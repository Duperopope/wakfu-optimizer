"""
dev_server.py v1.3 - Serveur local pour workflow Genspark
Invoke-RestMethod autorise vers localhost uniquement.
Blacklist minimale : seulement les commandes reellement dangereuses.
"""
import json, subprocess, os, re, time
from pathlib import Path
try:
    from memory_manager import get_manager as get_memory
    HAS_MEMORY = True
except Exception as e:
    print(f"Memory Manager non disponible: {e}")
    HAS_MEMORY = False
from datetime import datetime
from http.server import HTTPServer, ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

PROJECT = Path(r"H:\Code\Ankama Dev\wakfu-optimizer")
FRONTEND = PROJECT / "frontend"
LOGS_DIR = PROJECT / "logs"
LOGS_DIR.mkdir(exist_ok=True)
LOG_FILE = LOGS_DIR / "dev_server.log"
VOICE_NOTES_FILE = LOGS_DIR / "voice_notes.log"
HOST = "127.0.0.1"
PORT = 8091
PROJECT_STR = str(PROJECT).lower().replace("/", "\\")

ALLOWED_LOCALHOST = ["localhost", "127.0.0.1", "0.0.0.0"]

# Blacklist minimale : uniquement des patterns de COMMANDES reelles
# Pas de mots isoles qui pourraient apparaitre dans du texte
BLOCKED_PATTERNS = [
    r"Remove-Item\s+.*-Recurse.*C:.*Windows",
    r"Remove-Item\s+.*-Recurse.*C:.*Program",
    r"Format-Volume",
    r"Format-Disk",
    r"Stop-Computer",
    r"Restart-Computer",
    r"del\s+/s.*C:.*Windows",
    r"rmdir\s+/s.*C:.*Windows",
]

def log(level, message):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{ts}] [{level}] {message}"
    print(entry)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(entry + "\n")
    except: pass

def log_voice_note(note):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(VOICE_NOTES_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] {note}\n")
    except: pass

def is_url_local(url_str):
    url_str = url_str.strip().strip('"').strip("'").lower()
    for local in ALLOWED_LOCALHOST:
        if local in url_str:
            return True
    return False

def check_web_commands(command):
    web_cmds = [
        (r'Invoke-RestMethod', r'Invoke-RestMethod\s+(?:-Uri\s+)?["\' ]?(https?://[^\s"\']+)["\' ]?'),
        (r'Invoke-WebRequest', r'Invoke-WebRequest\s+(?:-Uri\s+)?["\' ]?(https?://[^\s"\']+)["\' ]?'),
    ]
    for cmd_name, url_pattern in web_cmds:
        if re.search(cmd_name, command, re.IGNORECASE):
            urls_found = re.findall(url_pattern, command, re.IGNORECASE)
            if not urls_found:
                return False, f"{cmd_name} sans URL parsable - bloque"
            for url in urls_found:
                if not is_url_local(url):
                    return False, f"{cmd_name} vers URL externe bloque: {url}"
            log("SECURITY", f"{cmd_name} vers localhost autorise")
    return True, "OK"

def is_command_safe(command):
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return False, f"Commande bloquee par pattern: {pattern}"
    web_safe, web_reason = check_web_commands(command)
    if not web_safe:
        return False, web_reason
    quoted_paths = re.findall(r'"([A-Za-z]:\\[^"]+)"', command)
    quoted_paths += re.findall(r"'([A-Za-z]:\\[^']+)'", command)
    unquoted_paths = re.findall(r'(?<!["\'])([A-Za-z]:\\[^\s;|>]+)', command)
    for p in (quoted_paths + unquoted_paths):
        p_clean = p.strip().lower().replace("/", "\\")
        if p_clean.startswith(PROJECT_STR): continue
        if re.match(r'^[a-z]:\\', p_clean):
            if ("\\temp\\" in p_clean or "\\tmp\\" in p_clean or
                "\\.venv\\" in p_clean or "\\.ollama\\" in p_clean or
                "\\appdata\\" in p_clean or
                "\\wakfu-dev-extension\\" in p_clean): continue
            return False, f"Chemin hors projet: {p}"
    return True, "OK"

def execute_powershell(command, timeout=120):
    safe, reason = is_command_safe(command)
    if not safe:
        log("BLOCKED", f"{reason} | Cmd: {command[:200]}")
        return {"success": False, "error": f"Commande bloquee: {reason}", "stdout": "", "stderr": "", "duration": 0}
    log_cmd = command[:300] + "..." if len(command) > 300 else command
    log("EXEC", f"Commande ({len(command)} chars): {log_cmd}")
    start = time.time()
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", command],
            capture_output=True, text=True, timeout=timeout,
            cwd=str(PROJECT), encoding="utf-8", errors="replace")
        duration = round(time.time() - start, 2)
        # Memory hook
        if HAS_MEMORY:
            try:
                mm = get_memory()
                mm.on_command_executed(command[:300], result.stdout[:500], result.returncode == 0, duration)
            except: pass
        log("RESULT", f"Code: {result.returncode} | {duration}s | Out: {len(result.stdout)} chars")
        return {"success": result.returncode == 0, "stdout": result.stdout, "stderr": result.stderr,
                "returncode": result.returncode, "duration": duration}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": f"Timeout {timeout}s", "stdout": "", "stderr": "", "duration": round(time.time()-start,2)}
    except Exception as e:
        return {"success": False, "error": str(e), "stdout": "", "stderr": "", "duration": round(time.time()-start,2)}

def read_file(rel_path):
    full = PROJECT / rel_path.replace("/", os.sep)
    if not full.exists(): return {"success": False, "error": f"Non trouve: {rel_path}"}
    if not str(full.resolve()).startswith(str(PROJECT.resolve())): return {"success": False, "error": "Hors projet"}
    try:
        content = full.read_text("utf-8")
        return {"success": True, "content": content, "size": len(content), "path": rel_path}
    except Exception as e: return {"success": False, "error": str(e)}

def write_file(rel_path, content):
    full = PROJECT / rel_path.replace("/", os.sep)
    if not str(full.resolve()).startswith(str(PROJECT.resolve())): return {"success": False, "error": "Hors projet"}
    try:
        # Lire ancien contenu pour review de regression
        old_content = None
        if full.exists():
            try: old_content = full.read_text("utf-8")
            except: pass
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, "utf-8")
        log("WRITE", f"{rel_path} ({len(content)} chars)")
        # Memory + Reviewer hook (background)
        if HAS_MEMORY:
            try:
                from threading import Thread
                mm = get_memory()
                mm.on_file_modified(rel_path, old_content, content)
                mm.episodic.record(
                    "Ecriture fichier: " + rel_path,
                    "write_file " + rel_path,
                    str(len(content)) + " chars ecrit",
                    True,
                    ["write", rel_path.split("/")[-1]]
                )
            except: pass
        return {"success": True, "path": rel_path, "size": len(content)}
    except Exception as e: return {"success": False, "error": str(e)}

def get_system_info():
    ps = r'''
$r = @{}
$os = Get-CimInstance Win32_OperatingSystem
$r["ram_total_gb"] = [math]::Round($os.TotalVisibleMemorySize / 1MB, 1)
$r["ram_free_gb"] = [math]::Round($os.FreePhysicalMemory / 1MB, 1)
$r["ram_used_gb"] = [math]::Round(($os.TotalVisibleMemorySize - $os.FreePhysicalMemory) / 1MB, 1)
$cpu = Get-CimInstance Win32_Processor
$r["cpu_name"] = $cpu.Name.Trim()
$r["cpu_cores"] = $cpu.NumberOfCores
$r["cpu_threads"] = $cpu.NumberOfLogicalProcessors
$r["cpu_load"] = $cpu.LoadPercentage
$top = Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 8 | ForEach-Object {
    @{ name = $_.ProcessName; ram_mb = [math]::Round($_.WorkingSet64 / 1MB, 0); pid = $_.Id }
}
$r["top_processes"] = $top
$gameNames = @("Wakfu","wakfu","steam","steamwebhelper","EpicGamesLauncher","Battle.net","Dofus","dofus")
$gaming = @()
foreach ($g in $gameNames) {
    $f = Get-Process -Name $g -ErrorAction SilentlyContinue
    if ($f) { foreach ($p in $f) { $gaming += @{ name = $g; pid = $p.Id; ram_mb = [math]::Round($p.WorkingSet64 / 1MB, 0) } } }
}
$r["gaming_detected"] = $gaming
$r["is_gaming"] = $gaming.Count -gt 0
$ollamaCmd = Get-Command ollama -ErrorAction SilentlyContinue
$r["ollama_installed"] = $null -ne $ollamaCmd
if ($ollamaCmd) {
    $r["ollama_path"] = $ollamaCmd.Source
    try {
        $tags = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method GET -TimeoutSec 3
        $r["ollama_running"] = $true
        $models = @()
        foreach ($m in $tags.models) { $models += @{ name = $m.name; size_gb = [math]::Round($m.size / 1GB, 1) } }
        $r["ollama_models"] = $models
    } catch { $r["ollama_running"] = $false; $r["ollama_models"] = @() }
    try { $ps = & ollama ps 2>&1; $r["ollama_loaded"] = ($ps | Out-String).Trim() } catch { $r["ollama_loaded"] = "erreur" }
}
$freeGB = $r["ram_free_gb"]; $cpuLoad = $r["cpu_load"]; $isGaming = $r["is_gaming"]
if ($isGaming) { $r["mode"] = "ECO"; $r["mode_reason"] = "Gaming detecte" }
elseif ($cpuLoad -gt 70 -or $freeGB -lt 8) { $r["mode"] = "ECO"; $r["mode_reason"] = "Ressources limitees" }
elseif ($cpuLoad -gt 40 -or $freeGB -lt 12) { $r["mode"] = "NORMAL"; $r["mode_reason"] = "Charge moderee" }
else { $r["mode"] = "TURBO"; $r["mode_reason"] = "Ressources abondantes" }
$r | ConvertTo-Json -Depth 4
'''
    result = execute_powershell(ps, timeout=15)
    if result["success"] and result["stdout"].strip():
        try: return {"success": True, "system": json.loads(result["stdout"])}
        except: return {"success": True, "raw": result["stdout"]}
    return {"success": False, "error": result.get("error", result.get("stderr", "Erreur"))}

def get_project_status():
    s = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "project": str(PROJECT),
         "frontend_exists": FRONTEND.exists(), "server_version": "1.3"}
    try:
        r = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=str(PROJECT))
        changed = [l.strip() for l in r.stdout.strip().splitlines() if l.strip()]
        s["git_changed_files"] = len(changed); s["git_changes"] = changed[:10]
    except: s["git_changed_files"] = -1
    try:
        if LOG_FILE.exists():
            lines = LOG_FILE.read_text("utf-8").strip().splitlines()
            s["recent_logs"] = lines[-5:] if len(lines) >= 5 else lines
    except: s["recent_logs"] = []
    return s

def get_recent_logs(n=20):
    try:
        if LOG_FILE.exists():
            lines = LOG_FILE.read_text("utf-8").strip().splitlines()
            return lines[-n:]
        return []
    except: return []

def ollama_request(action, model=None, prompt=None, keep_alive=None):
    base = "http://localhost:11434"
    if action == "list":
        ps_cmd = f'Invoke-RestMethod -Uri "{base}/api/tags" -Method GET -TimeoutSec 5 | ConvertTo-Json -Depth 4'
    elif action == "ps":
        ps_cmd = '& ollama ps 2>&1 | Out-String'
    elif action == "unload":
        body = json.dumps({"model": model, "prompt": "", "stream": False, "keep_alive": 0}).replace('"', '\\"')
        ps_cmd = f'Invoke-RestMethod -Uri "{base}/api/generate" -Method POST -Body "{body}" -ContentType "application/json" -TimeoutSec 30 | ConvertTo-Json -Depth 4'
    elif action == "preload":
        body = json.dumps({"model": model, "keep_alive": keep_alive or "10m"}).replace('"', '\\"')
        ps_cmd = f'Invoke-RestMethod -Uri "{base}/api/generate" -Method POST -Body "{body}" -ContentType "application/json" -TimeoutSec 120 | ConvertTo-Json -Depth 4'
    elif action == "generate":
        body = json.dumps({"model": model, "prompt": prompt or "Reply OK", "stream": False, "keep_alive": keep_alive}).replace('"', '\\"')
        ps_cmd = f'Invoke-RestMethod -Uri "{base}/api/generate" -Method POST -Body "{body}" -ContentType "application/json" -TimeoutSec 60 | ConvertTo-Json -Depth 4'
    else:
        return {"success": False, "error": f"Action inconnue: {action}"}
    result = execute_powershell(ps_cmd, timeout=120)
    if result["success"] and result["stdout"].strip():
        try: return {"success": True, "data": json.loads(result["stdout"])}
        except: return {"success": True, "raw": result["stdout"]}
    return result

def restart_server():
    """Signal au launcher de redemarrer le serveur."""
    signal = LOGS_DIR / ".restart_signal"
    signal.write_text("restart", "utf-8")
    log("RESTART", "Signal envoye au launcher - arret dans 1s..."); os._exit(0)

class DevHandler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
    def _json(self, data, status=200):
        try:
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self._cors(); self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError, OSError):
            pass
    def _body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0: return {}
        body = self.rfile.read(length).decode("utf-8")
        try: return json.loads(body)
        except: return {"raw": body}
    def do_OPTIONS(self):
        self.send_response(204); self._cors(); self.end_headers()
    def do_GET(self):
        path = urlparse(self.path).path
        params = parse_qs(urlparse(self.path).query)
        if path == "/health": self._json({"status": "ok", "version": "1.3"})
        elif path == "/status": self._json(get_project_status())
        elif path == "/system": self._json(get_system_info())
        elif path == "/logs":
            n = int(params.get("n", [20])[0]); self._json({"logs": get_recent_logs(n)})
        elif path == "/read-file":
            fp = params.get("path", [None])[0]
            if not fp: self._json({"error": "'path' manquant"}, 400); return
            self._json(read_file(fp))
        else: self._json({"error": f"Route inconnue: {path}"}, 404)
    def do_POST(self):
        path = urlparse(self.path).path; body = self._body()
        if path == "/execute":
            cmd = body.get("command", "")
            if not cmd: self._json({"error": "'command' manquant"}, 400); return
            self._json(execute_powershell(cmd, body.get("timeout", 120)))
        elif path == "/write-file":
            fp = body.get("path", ""); ct = body.get("content", "")
            if not fp: self._json({"error": "'path' manquant"}, 400); return
            self._json(write_file(fp, ct))
        elif path == "/voice-note":
            note = body.get("note", "")
            if not note: self._json({"error": "'note' manquant"}, 400); return
            log_voice_note(note); log("VOICE", f"Note: {note[:100]}")
            self._json({"success": True, "note": note})
        elif path == "/build-memory":
            self._json(execute_powershell("python scripts/build_memory.py", timeout=30))
        elif path == "/session-end":
            self._json(run_session_end(body.get("title","Sans titre"), body.get("work_done",[]),
                                        body.get("files_modified",[]), body.get("issues",[])))
        elif path == "/classify":
            code = body.get("code", "")
            if not code: self._json({"error": "code manquant"}, 400); return
            try:
                import importlib, sys
                agent_path = str(PROJECT / "scripts")
                if agent_path not in sys.path: sys.path.insert(0, agent_path)
                import local_agent
                importlib.reload(local_agent)
                result = local_agent.handle_classify(code)
                self._json({"success": True, "classification": result})
            except Exception as e:
                log("CLASSIFY", f"Erreur: {e}")
                self._json({"success": False, "error": str(e)})
        elif path == "/ext-log":
            message = body.get("message", "")
            if HAS_MEMORY:
                try:
                    mm = get_memory()
                    mm.on_ext_log(message)
                except: pass
            self._json({"success": True})
        elif path == "/memory-status":
            if HAS_MEMORY:
                mm = get_memory()
                self._json({
                    "success": True,
                    "episodes": len(mm.episodic.episodes),
                    "procedures": len(mm.procedural.procedures),
                    "session": mm.session.get_summary(),
                    "working": mm.working.summarize()
                })
            else:
                self._json({"success": False, "error": "Memory Manager non disponible"})
        elif path == "/ollama":
            action = body.get("action", "")
            if not action: self._json({"error": "'action' manquant"}, 400); return
            self._json(ollama_request(action, body.get("model",""), body.get("prompt",""), body.get("keep_alive")))
        elif path == "/restart":
            self._json({"success": True, "message": "Restart en cours..."})
            import threading; threading.Timer(1.0, restart_server).start()
        else: self._json({"error": f"Route inconnue: {path}"}, 404)
    def log_message(self, format, *args): pass

def run_session_end(title, work_done, files_modified, issues):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_str = datetime.now().strftime("%Y-%m-%d")
    handoff = ["# SESSION HANDOFF - wakfu-optimizer", f"> Derniere session : {ts}", f"> Titre : {title}", "",
               "## CE QUI A ETE FAIT"] + [f"- {w}" for w in work_done] + ["", "## FICHIERS MODIFIES"] + \
              [f"- {f}" for f in files_modified] + ["", "## PROBLEMES NON RESOLUS"] + [f"- {i}" for i in issues] + \
              ["", "## PROCHAINE ETAPE", "- Lire BRIEFING.md en debut de session", ""]
    (PROJECT / "SESSION_HANDOFF.md").write_text("\n".join(handoff), "utf-8")
    log("SESSION", f"SESSION_HANDOFF.md ({len(handoff)} lignes)")
    # Consolider la memoire
    if HAS_MEMORY:
        try:
            mm = get_memory()
            mm.end_session()
            log("SESSION", "Memoire consolidee (episodique + procedurale + briefing)")
        except Exception as e:
            log("SESSION", "Erreur consolidation memoire: " + str(e))
    cl_path = PROJECT / "CHANGELOG.md"
    entry = ["", f"## [{date_str}] {title}", f"> {ts}", "> https://github.com/Duperopope/wakfu-optimizer/commits/main",
             "", "### Fait"] + [f"- {w}" for w in work_done] + ["", "### Fichiers"] + [f"- {f}" for f in files_modified] + [""]
    if issues: entry += ["### Non resolus"] + [f"- {i}" for i in issues] + [""]
    if cl_path.exists():
        existing = cl_path.read_text("utf-8")
        if "---" in existing:
            parts = existing.split("---", 1)
            cl_path.write_text(parts[0] + "---" + "\n".join(entry) + "\n" + parts[1], "utf-8")
        else: cl_path.write_text(existing + "\n".join(entry), "utf-8")
    else: cl_path.write_text("# CHANGELOG\n\n---\n" + "\n".join(entry), "utf-8")
    log("SESSION", "CHANGELOG.md maj")
    br = execute_powershell("python scripts/build_memory.py", timeout=30)
    return {"success": True, "handoff_written": True, "changelog_updated": True,
            "memory_rebuilt": br.get("success",False), "timestamp": ts}

if __name__ == "__main__":
    os.chdir(PROJECT)
    log("START", f"Dev Server v1.3 sur {HOST}:{PORT}")
    print("=" * 60)
    print(f"  WAKFU DEV SERVER v1.3")
    print(f"  http://{HOST}:{PORT}")
    print(f"  Projet : {PROJECT}")
    print(f"  Invoke-RestMethod: localhost SEULEMENT")
    print(f"  Routes: /health /status /system /logs /read-file")
    print(f"          /execute /write-file /voice-note")
    print(f"          /build-memory /session-end /ollama /restart")
    print(f"  {len(BLOCKED_PATTERNS)} patterns bloques | Ctrl+C pour arreter")
    print("=" * 60)
    server = HTTPServer((HOST, PORT), DevHandler)
    try: server.serve_forever()
    except KeyboardInterrupt:
        log("STOP", "Arrete"); server.server_close(); print("\nArrete.")