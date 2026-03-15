"""
conductor.py v1.0 - Agent Conductor pour le pipeline auto-codant
Analyse les resultats et decide la prochaine action.
Utilise qwen2.5-coder:7b via Ollama.
"""
import json, urllib.request, time
from pathlib import Path
from datetime import datetime

OLLAMA_URL = 'http://localhost:11434'
MODEL = 'qwen2.5-coder:7b'
PROJECT = Path(__file__).resolve().parent.parent
LOGS = PROJECT / 'logs'
LOGS.mkdir(exist_ok=True)
LOG_FILE = LOGS / 'conductor.log'

def log(msg):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    entry = '[' + ts + '] [CONDUCTOR] ' + msg
    print(entry)
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(entry + chr(10))
    except:
        pass

def load_context():
    ctx = {}
    briefing = PROJECT / 'BRIEFING.md'
    if briefing.exists():
        ctx['briefing'] = briefing.read_text('utf-8', errors='replace')[:2000]
    handoff = PROJECT / 'SESSION_HANDOFF.md'
    if handoff.exists():
        ctx['handoff'] = handoff.read_text('utf-8', errors='replace')[:2000]
    memory_ep = PROJECT / 'memory' / 'episodes.jsonl'
    if memory_ep.exists():
        ep_lines = memory_ep.read_text('utf-8', errors='replace').strip().split(chr(10))
        recent = ep_lines[-5:] if len(ep_lines) > 5 else ep_lines
        ctx['recent_episodes'] = [json.loads(l) for l in recent if l.strip()]
    return ctx

CONDUCTOR_PROMPT = (
    'Tu es le Conductor, un agent chef de projet IA. Reponds toujours en francais. '
    'Tu recois le resultat d une commande executee par Claude Opus. '
    'Analyse le resultat et decide la prochaine action. '
    'Contexte projet: {context} '
    'Commande executee: {command} '
    'Resultat (code retour: {returncode}): {output} '
    'Reponds en JSON strict: '
    '{{"action": "continue" ou "fix" ou "escalate" ou "done", "fix_command": "commande PowerShell de correction (si fix)", '
    '"message": "message a envoyer a Claude Opus", '
    '"analysis": "ton analyse en 1-2 phrases", '
    '"priority": "high" ou "medium" ou "low"}} '
    'Regles: continue=OK donne prochaine instruction, fix=erreur explique quoi corriger '
    '(ajoute fix_command avec la commande PowerShell pour corriger si possible), '
    'escalate=probleme critique pour humain, done=tache terminee. '
    'IMPORTANT: fix_command DOIT etre une vraie commande PowerShell executable, '
    'PAS du texte en francais. Exemple: python -c "print(2+2)" ou Write-Host "test". '
    'Si tu ne sais pas comment corriger, utilise action=escalate pour demander a Claude Opus. '
    'Sois concis.'
)

def ask_conductor(command, output, returncode, task_context=''):
    ctx = load_context()
    context_str = ''
    if 'briefing' in ctx:
        context_str += ctx['briefing'][:800]
    if 'recent_episodes' in ctx:
        for ep in ctx['recent_episodes']:
            status = 'OK' if ep.get('success') else 'FAIL'
            context_str += '[' + status + '] ' + ep.get('context', '')[:60] + ' '
    if task_context:
        context_str += ' TACHE: ' + task_context
    prompt = CONDUCTOR_PROMPT.format(
        context=context_str[:1500],
        command=command[:500],
        output=output[:1500],
        returncode=returncode
    )
    body = json.dumps({
        'model': MODEL, 'prompt': prompt, 'stream': False,
        'format': 'json', 'options': {'num_predict': 200, 'temperature': 0.1}
    }).encode('utf-8')
    try:
        start = time.time()
        req = urllib.request.Request(
            OLLAMA_URL + '/api/generate',
            data=body, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            response_text = result.get('response', '').strip()
            duration = round(time.time() - start, 1)
            try:
                decision = json.loads(response_text)
            except json.JSONDecodeError:
                decision = {'action': 'continue', 'message': 'Continue.', 'analysis': response_text[:200], 'priority': 'medium'}
            eval_dur = result.get('eval_duration', 0)
            tok_s = round(result.get('eval_count', 0) / (eval_dur / 1e9), 1) if eval_dur > 0 else 0
            log('Decision: ' + decision.get('action', '?') + ' | ' + str(tok_s) + ' tok/s | ' + str(duration) + 's')
            log('Message: ' + decision.get('message', '')[:100])
            decision['tokens_per_sec'] = tok_s
            # Enregistrer dans memoire procedurale si fix reussi
            if decision.get('action') == 'fix' and decision.get('fix_command'):
                try:
                    from memory_manager import get_manager
                    mm = get_manager()
                    mm.procedural.register(
                        'auto_fix_' + datetime.now().strftime('%H%M%S'),
                        [decision['fix_command']],
                        ['auto-repair', 'conductor']
                    )
                except: pass
            decision['duration'] = duration
            decision['model'] = MODEL
            return decision
    except Exception as e:
        log('Erreur Ollama: ' + str(e))
        if returncode == 0:
            return {'action': 'continue', 'message': 'Resultat OK. Continue.', 'analysis': 'Execution reussie (fallback)', 'priority': 'low'}
        else:
            return {'action': 'fix', 'message': 'Erreur: ' + output[:200], 'analysis': 'Echec (fallback)', 'priority': 'high'}

def format_message(decision):
    # Mini-contexte anti context-rot
    try:
        project = Path(__file__).resolve().parent.parent
        todo_file = project / 'PROJECT_MEMORY.md'
        if todo_file.exists():
            tc = todo_file.read_text('utf-8', errors='replace')
            idx = tc.find('- [ ]')
            if idx > 0:
                end = tc.find('\n', idx)
                current_task = tc[idx:end].strip() if end > 0 else tc[idx:idx+100].strip()
                decision['current_task'] = current_task
    except: pass
    # Mini-contexte anti context-rot
    try:
        project = Path(__file__).resolve().parent.parent
        todo_file = project / 'PROJECT_MEMORY.md'
        if todo_file.exists():
            tc = todo_file.read_text('utf-8', errors='replace')
            idx = tc.find('- [ ]')
            if idx > 0:
                end = tc.find('\n', idx)
                current_task = tc[idx:end].strip() if end > 0 else tc[idx:idx+100].strip()
                decision['current_task'] = current_task
    except: pass
    action = decision.get('action', 'continue')
    msg = decision.get('message', '')
    analysis = decision.get('analysis', '')
    if action == 'done': return 'Tache terminee. ' + analysis
    elif action == 'escalate': return '[ESCALADE] ' + msg
    elif action == 'fix': return 'Erreur a corriger: ' + msg
    else: return msg

if __name__ == '__main__':
    print('=== TEST CONDUCTOR ===')
    r = ask_conductor('Write-Host test', 'test', 0, 'Test pipeline')
    print('Decision:', json.dumps(r, indent=2, ensure_ascii=False))
    print('Message:', format_message(r))