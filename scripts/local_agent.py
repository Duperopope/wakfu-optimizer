"""
local_agent.py v1.0 - Agent local pour le consortium IA
Orchestre SENTINEL (classification), ResourceGovernor (RAM/CPU), et Ollama.
"""
import json, time, subprocess, os, re
from pathlib import Path
from datetime import datetime

PROJECT = Path(r'H:\Code\Ankama Dev\wakfu-optimizer')
LOGS_DIR = PROJECT / 'logs'
LOGS_DIR.mkdir(exist_ok=True)
AGENT_LOG = LOGS_DIR / 'local_agent.log'
OLLAMA_URL = 'http://localhost:11434'

def log(level, message):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    entry = f'[{ts}] [AGENT/{level}] {message}'
    print(entry)
    try:
        with open(AGENT_LOG, 'a', encoding='utf-8') as f:
            f.write(entry + '\n')
    except: pass

class ResourceGovernor:
    GAME_PROCESSES = ['Wakfu','wakfu','Dofus','dofus','steam','steamwebhelper','EpicGamesLauncher','Battle.net']

    def __init__(self):
        self.current_mode = 'NORMAL'
        self.last_check = None
        self.system_info = {}

    def check(self):
        try:
            ps_script = '$r=@{};$os=Get-CimInstance Win32_OperatingSystem;$r[\"ram_free_gb\"]=[math]::Round($os.FreePhysicalMemory/1MB, 1);$r[\"ram_total_gb\"]=[math]::Round($os.TotalVisibleMemorySize/1MB, 1);$cpu=Get-CimInstance Win32_Processor;$r[\"cpu_load\"]=$cpu.LoadPercentage;$gaming=@();foreach($g in @(\"Wakfu\",\"wakfu\",\"Dofus\",\"dofus\",\"steam\")){$f=Get-Process -Name $g -ErrorAction SilentlyContinue;if($f){$gaming+=$g}};$r[\"gaming\"]=$gaming;$r[\"is_gaming\"]=$gaming.Count -gt 0;$r|ConvertTo-Json -Depth 2'
            result = subprocess.run(
                ['powershell', '-NoProfile', '-NonInteractive', '-Command', ps_script],
                capture_output=True, text=True, timeout=10,
                encoding='utf-8', errors='replace')
            if result.returncode == 0 and result.stdout.strip():
                self.system_info = json.loads(result.stdout)
                self.last_check = datetime.now().isoformat()
                self._determine_mode()
            return self.get_status()
        except Exception as e:
            log('GOVERNOR', f'Erreur check: {e}')
            return self.get_status()

    def _determine_mode(self):
        info = self.system_info
        is_gaming = info.get('is_gaming', False)
        cpu = info.get('cpu_load', 50) or 50
        ram_free = info.get('ram_free_gb', 10)
        if is_gaming: self.current_mode = 'ECO'
        elif cpu > 70 or ram_free < 6: self.current_mode = 'ECO'
        elif cpu > 40 or ram_free < 9: self.current_mode = 'NORMAL'
        else: self.current_mode = 'TURBO'
        log('GOVERNOR', f'Mode: {self.current_mode} (CPU {cpu}% | RAM libre {ram_free} GB | Gaming: {is_gaming})')

    def get_status(self):
        return {'mode': self.current_mode, 'system': self.system_info, 'last_check': self.last_check}

    def can_load_model(self, model_size_gb=5):
        ram_free = self.system_info.get('ram_free_gb', 0)
        if self.current_mode == 'ECO': return False
        if ram_free < model_size_gb + 1: return False
        return True

SENTINEL_MODEL = 'qwen2.5-coder:7b'

SENTINEL_PROMPT = '''You are SENTINEL, a code block classifier. Analyze the code and reply with ONLY one JSON object:
{"verdict": "EXEC_SAFE" or "NO_EXEC" or "EXEC_DANGER", "reason": "brief reason", "type": "powershell" or "tsx" or "python" or "javascript" or "other"}

Rules:
- EXEC_SAFE: PowerShell scripts meant to run on the developer machine (file ops, git, npm, diagnostics)
- NO_EXEC: Code examples, React/TSX components, Python classes, config samples
- EXEC_DANGER: Destructive commands (mass delete, kill all processes)

Code block:
'''

def sentinel_classify(code_block):
    import urllib.request
    prompt = SENTINEL_PROMPT + code_block
    body = json.dumps({
        'model': SENTINEL_MODEL, 'prompt': prompt, 'stream': False,
        'format': 'json', 'options': {'num_predict': 80, 'temperature': 0}
    }).encode('utf-8')
    try:
        req = urllib.request.Request(
            f'{OLLAMA_URL}/api/generate', data=body,
            headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            response_text = result.get('response', '').strip()
            try:
                classification = json.loads(response_text)
                verdict = classification.get('verdict', 'NO_EXEC')
                reason = classification.get('reason', '')
                code_type = classification.get('type', 'other')
            except json.JSONDecodeError:
                if 'EXEC_SAFE' in response_text: verdict = 'EXEC_SAFE'
                elif 'EXEC_DANGER' in response_text: verdict = 'EXEC_DANGER'
                else: verdict = 'NO_EXEC'
                reason = response_text[:100]; code_type = 'other'
            eval_dur = result.get('eval_duration', 0)
            tok_s = round(result.get('eval_count', 0) / (eval_dur / 1e9), 1) if eval_dur > 0 else 0
            log('SENTINEL', f'{verdict} | {code_type} | {tok_s} tok/s | {reason[:60]}')
            return {'verdict': verdict, 'reason': reason, 'type': code_type,
                    'tokens_per_sec': tok_s, 'model': SENTINEL_MODEL}
    except Exception as e:
        log('SENTINEL', f'Erreur: {e}')
        return sentinel_heuristic(code_block)

def sentinel_heuristic(code_block):
    code = code_block.strip()
    ps_markers = ['Write-Host','Get-Content','Set-Content','Get-ChildItem',
                  'Get-CimInstance','ConvertTo-Json','ForEach-Object',
                  '-ForegroundColor','New-Item','Test-Path','Invoke-RestMethod']
    ps_score = sum(1 for m in ps_markers if m in code)
    danger_patterns = [r'Remove-Item.*-Recurse.*-Force', r'Stop-Process.*-Force']
    danger_score = sum(1 for m in danger_patterns if re.search(m, code))
    noexec_patterns = [r'export default', r'import React', r'function.*return.*<',
                        r'class.*extends', r'def __init__', r'from.*import']
    noexec_score = sum(1 for m in noexec_patterns if re.search(m, code))
    if danger_score > 0:
        verdict, reason, code_type = 'EXEC_DANGER', 'Destructive command (heuristic)', 'powershell'
    elif ps_score >= 2:
        verdict, reason, code_type = 'EXEC_SAFE', f'{ps_score} PS markers (heuristic)', 'powershell'
    elif noexec_score >= 1:
        verdict, reason = 'NO_EXEC', 'Source code (heuristic)'
        code_type = 'tsx' if 'React' in code or '<' in code else 'python'
    else:
        verdict, reason, code_type = 'NO_EXEC', 'Unknown - blocked (heuristic)', 'other'
    log('SENTINEL', f'{verdict} (heuristic) | {code_type} | {reason[:60]}')
    return {'verdict': verdict, 'reason': reason, 'type': code_type,
            'tokens_per_sec': 0, 'model': 'heuristic'}

governor = ResourceGovernor()

def handle_classify(code_block):
    status = governor.check()
    mode = status['mode']
    if mode == 'ECO' or not governor.can_load_model():
        log('AGENT', 'Mode ECO ou RAM insuffisante - heuristique')
        result = sentinel_heuristic(code_block)
    else:
        result = sentinel_classify(code_block)
    result['resource_mode'] = mode
    return result

def handle_system_check():
    return governor.check()

if __name__ == '__main__':
    print('=== LOCAL AGENT v1.0 - Test ===')
    print()
    print('--- ResourceGovernor ---')
    status = governor.check()
    print(f'Mode: {status["mode"]}')
    print(f'RAM libre: {status["system"].get("ram_free_gb", "?")} GB')
    print(f'CPU: {status["system"].get("cpu_load", "?")}%')
    print(f'Gaming: {status["system"].get("is_gaming", "?")}')
    print(f'Peut charger 7B: {governor.can_load_model(5)}')
    print()
    print('--- SENTINEL ---')
    tests = [
        'Write-Host "Hello" ; Get-Content "MANIFEST.json" -Raw',
        'export default function Panel() { return <div>test</div>; }',
        'Get-Process | Stop-Process -Force',
    ]
    for t in tests:
        r = handle_classify(t)
        print(f'  [{r["verdict"]}] ({r["type"]}, {r["model"]}) {t[:50]}...')
    print()
    print('=== FIN TEST ===')


