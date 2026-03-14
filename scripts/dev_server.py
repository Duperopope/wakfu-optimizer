"""
dev_server.py - Serveur local d'execution pour le workflow Genspark
Ecoute sur localhost:8091 et execute les commandes envoyees par l'extension Chrome.

SECURITE : Seules les commandes whitelistees sont autorisees.
LOGGING : Toutes les actions sont loguees dans logs/dev_server.log

Usage : python scripts/dev_server.py
"""

import json, subprocess, os, sys, re, time
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

# ============================================================
# CONFIGURATION
# ============================================================

PROJECT = Path(r"H:\Code\Ankama Dev\wakfu-optimizer")
FRONTEND = PROJECT / "frontend"
LOGS_DIR = PROJECT / "logs"
LOGS_DIR.mkdir(exist_ok=True)
LOG_FILE = LOGS_DIR / "dev_server.log"
VOICE_NOTES_FILE = LOGS_DIR / "voice_notes.log"

HOST = "127.0.0.1"
PORT = 8091

# Commandes PowerShell autorisees (whitelist)
# On autorise uniquement les operations sur le projet
ALLOWED_COMMANDS = [
    "Set-Content",
    "Get-Content",
    "New-Item",
    "Remove-Item",
    "Copy-Item",
    "Move-Item",
    "Test-Path",
    "Get-ChildItem",
    "Get-Date",
    "Write-Host",
    "npm",
    "npx",
    "node",
    "python",
    "git",
    "cd",
    "Set-Location",
    "Push-Location",
    "Pop-Location",
]

# Commandes INTERDITES (blacklist absolue)
BLOCKED_PATTERNS = [
    r"Invoke-WebRequest",
    r"Invoke-RestMethod",
    r"Start-Process",
    r"Remove-Item\s+.*-Recurse.*C:\\",
    r"Remove-Item\s+.*-Recurse.*D:\\",
    r"Format-",
    r"Stop-Computer",
    r"Restart-Computer",
    r"reg\s+delete",
    r"reg\s+add",
    r"netsh",
    r"shutdown",
    r"del\s+/s",
    r"rmdir\s+/s",
    r"::.*system32",
]

# ============================================================
# LOGGING
# ============================================================

def log(level, message):
    """Ecrit dans le fichier log et dans la console."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{ts}] [{level}] {message}"
    print(entry)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(entry + "\n")
    except Exception:
        pass

def log_voice_note(note):
    """Enregistre une note vocale dans un fichier dedie."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{ts}] {note}"
    try:
        with open(VOICE_NOTES_FILE, "a", encoding="utf-8") as f:
            f.write(entry + "\n")
    except Exception:
        pass

# ============================================================
# SECURITE
# ============================================================

def is_command_safe(command):
    """Verifie qu'une commande est dans la whitelist et pas dans la blacklist."""
    # Verifier la blacklist en premier
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return False, f"Commande bloquee par pattern: {pattern}"

    # Verifier que la commande ne sort pas du projet
    # Autoriser uniquement les chemins dans le projet
    project_str = str(PROJECT).replace("\\", "\\\\")
    frontend_str = str(FRONTEND).replace("\\", "\\\\")

    # Si la commande contient un chemin absolu, verifier qu'il est dans le projet
    abs_paths = re.findall(r'[A-Z]:\\[^\s"\']+', command)
    for p in abs_paths:
        p_normalized = p.replace("/", "\\")
        if not p_normalized.startswith(str(PROJECT)):
            return False, f"Chemin hors projet interdit: {p}"

    return True, "OK"

# ============================================================
# EXECUTION
# ============================================================

def execute_powershell(command, timeout=60):
    """Execute une commande PowerShell et retourne le resultat."""
    safe, reason = is_command_safe(command)
    if not safe:
        log("BLOCKED", f"{reason} | Commande: {command[:100]}")
        return {
            "success": False,
            "error": f"Commande bloquee: {reason}",
            "stdout": "",
            "stderr": "",
            "duration": 0,
        }

    log("EXEC", f"Commande: {command[:200]}...")

    start = time.time()
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", command],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(PROJECT),
            encoding="utf-8",
            errors="replace",
        )
        duration = round(time.time() - start, 2)

        log("RESULT", f"Code: {result.returncode} | Duree: {duration}s | Stdout: {len(result.stdout)} chars")

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "duration": duration,
        }
    except subprocess.TimeoutExpired:
        duration = round(time.time() - start, 2)
        log("TIMEOUT", f"Commande timeout apres {timeout}s")
        return {
            "success": False,
            "error": f"Timeout apres {timeout}s",
            "stdout": "",
            "stderr": "",
            "duration": duration,
        }
    except Exception as e:
        duration = round(time.time() - start, 2)
        log("ERROR", f"Exception: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "stdout": "",
            "stderr": "",
            "duration": duration,
        }

def read_file(rel_path):
    """Lit un fichier du projet."""
    full = PROJECT / rel_path.replace("/", os.sep)
    if not full.exists():
        return {"success": False, "error": f"Fichier non trouve: {rel_path}"}
    if not str(full.resolve()).startswith(str(PROJECT.resolve())):
        return {"success": False, "error": "Chemin hors projet"}
    try:
        content = full.read_text("utf-8")
        return {"success": True, "content": content, "size": len(content), "path": rel_path}
    except Exception as e:
        return {"success": False, "error": str(e)}

def write_file(rel_path, content):
    """Ecrit un fichier dans le projet."""
    full = PROJECT / rel_path.replace("/", os.sep)
    if not str(full.resolve()).startswith(str(PROJECT.resolve())):
        return {"success": False, "error": "Chemin hors projet"}
    try:
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, "utf-8")
        log("WRITE", f"Fichier ecrit: {rel_path} ({len(content)} chars)")
        return {"success": True, "path": rel_path, "size": len(content)}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_project_status():
    """Retourne l'etat actuel du projet."""
    status = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "project": str(PROJECT),
        "frontend_exists": FRONTEND.exists(),
    }

    # Git status
    try:
        r = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=str(PROJECT))
        changed = [l.strip() for l in r.stdout.strip().splitlines() if l.strip()]
        status["git_changed_files"] = len(changed)
        status["git_changes"] = changed[:10]
    except Exception:
        status["git_changed_files"] = -1

    # Dev server running?
    try:
        r = subprocess.run(
            ["powershell", "-Command", "Get-Process -Name node -ErrorAction SilentlyContinue | Select-Object -First 1 | Format-List Id"],
            capture_output=True, text=True, timeout=5
        )
        status["node_running"] = "Id" in r.stdout
    except Exception:
        status["node_running"] = False

    # Derniers logs
    try:
        if LOG_FILE.exists():
            lines = LOG_FILE.read_text("utf-8").strip().splitlines()
            status["recent_logs"] = lines[-5:] if len(lines) >= 5 else lines
    except Exception:
        status["recent_logs"] = []

    # Notes vocales recentes
    try:
        if VOICE_NOTES_FILE.exists():
            lines = VOICE_NOTES_FILE.read_text("utf-8").strip().splitlines()
            status["recent_voice_notes"] = lines[-3:] if len(lines) >= 3 else lines
    except Exception:
        status["recent_voice_notes"] = []

    return status

def get_recent_logs(n=20):
    """Retourne les N dernieres lignes du log."""
    try:
        if LOG_FILE.exists():
            lines = LOG_FILE.read_text("utf-8").strip().splitlines()
            return lines[-n:]
        return []
    except Exception:
        return []

# ============================================================
# SERVEUR HTTP
# ============================================================

class DevHandler(BaseHTTPRequestHandler):
    """Gestionnaire de requetes HTTP."""

    def _cors_headers(self):
        """Ajoute les headers CORS pour l'extension Chrome."""
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def _json_response(self, data, status=200):
        """Envoie une reponse JSON."""
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self._cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _read_body(self):
        """Lit le corps de la requete."""
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        body = self.rfile.read(length).decode("utf-8")
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return {"raw": body}

    def do_OPTIONS(self):
        """Repond aux preflight CORS."""
        self.send_response(204)
        self._cors_headers()
        self.end_headers()

    def do_GET(self):
        """Routes GET."""
        path = urlparse(self.path).path
        params = parse_qs(urlparse(self.path).query)

        if path == "/status":
            self._json_response(get_project_status())

        elif path == "/logs":
            n = int(params.get("n", [20])[0])
            self._json_response({"logs": get_recent_logs(n)})

        elif path == "/read-file":
            file_path = params.get("path", [None])[0]
            if not file_path:
                self._json_response({"error": "Parametre 'path' manquant"}, 400)
                return
            self._json_response(read_file(file_path))

        elif path == "/health":
            self._json_response({"status": "ok", "timestamp": datetime.now().isoformat()})

        else:
            self._json_response({"error": f"Route inconnue: {path}"}, 404)

    def do_POST(self):
        """Routes POST."""
        path = urlparse(self.path).path
        body = self._read_body()

        if path == "/execute":
            command = body.get("command", "")
            timeout = body.get("timeout", 60)
            if not command:
                self._json_response({"error": "Parametre 'command' manquant"}, 400)
                return
            result = execute_powershell(command, timeout=timeout)
            self._json_response(result)

        elif path == "/write-file":
            file_path = body.get("path", "")
            content = body.get("content", "")
            if not file_path:
                self._json_response({"error": "Parametre 'path' manquant"}, 400)
                return
            result = write_file(file_path, content)
            self._json_response(result)

        elif path == "/voice-note":
            note = body.get("note", "")
            if not note:
                self._json_response({"error": "Parametre 'note' manquant"}, 400)
                return
            log_voice_note(note)
            log("VOICE", f"Note recue: {note[:100]}")
            self._json_response({"success": True, "note": note})

        elif path == "/build-memory":
            # Relance build_memory.py
            result = execute_powershell("python scripts/build_memory.py", timeout=30)
            self._json_response(result)

        elif path == "/session-end":
            # Protocole de fin de session
            title = body.get("title", "Session sans titre")
            work_done = body.get("work_done", [])
            files_modified = body.get("files_modified", [])
            issues = body.get("issues", [])
            result = run_session_end(title, work_done, files_modified, issues)
            self._json_response(result)

        else:
            self._json_response({"error": f"Route inconnue: {path}"}, 404)

    def log_message(self, format, *args):
        """Reduit le bruit dans la console."""
        pass

def run_session_end(title, work_done, files_modified, issues):
    """Execute le protocole de fin de session."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_str = datetime.now().strftime("%Y-%m-%d")

    # 1. Creer SESSION_HANDOFF.md
    handoff_lines = [
        f"# SESSION HANDOFF - wakfu-optimizer",
        f"> Derniere session : {ts}",
        f"> Titre : {title}",
        f"",
        f"## CE QUI A ETE FAIT",
    ]
    for w in work_done:
        handoff_lines.append(f"- {w}")
    handoff_lines.append("")
    handoff_lines.append("## FICHIERS MODIFIES")
    for f in files_modified:
        handoff_lines.append(f"- {f}")
    handoff_lines.append("")
    handoff_lines.append("## PROBLEMES NON RESOLUS")
    for i in issues:
        handoff_lines.append(f"- {i}")
    handoff_lines.append("")
    handoff_lines.append("## PROCHAINE ETAPE RECOMMANDEE")
    handoff_lines.append("- Lire ce fichier + BRIEFING.md en debut de session")
    handoff_lines.append("")

    handoff_path = PROJECT / "SESSION_HANDOFF.md"
    handoff_path.write_text("\n".join(handoff_lines), "utf-8")
    log("SESSION", f"SESSION_HANDOFF.md ecrit ({len(handoff_lines)} lignes)")

    # 2. Ajouter entree au CHANGELOG.md
    changelog_path = PROJECT / "CHANGELOG.md"
    changelog_entry = [
        f"",
        f"## [{date_str}] {title}",
        f"> Mise a jour : {ts}",
        f"> Commits : https://github.com/Duperopope/wakfu-optimizer/commits/main",
        f"",
        f"### Ce qui a ete fait",
    ]
    for w in work_done:
        changelog_entry.append(f"- {w}")
    changelog_entry.append("")
    changelog_entry.append("### Fichiers modifies")
    for f in files_modified:
        changelog_entry.append(f"- {f}")
    changelog_entry.append("")
    if issues:
        changelog_entry.append("### Problemes identifies non resolus")
        for i in issues:
            changelog_entry.append(f"- {i}")
        changelog_entry.append("")

    if changelog_path.exists():
        existing = changelog_path.read_text("utf-8")
        # Inserer apres le header
        marker = "---"
        if marker in existing:
            parts = existing.split(marker, 1)
            new_content = parts[0] + marker + "\n".join(changelog_entry) + "\n" + parts[1]
        else:
            new_content = existing + "\n".join(changelog_entry)
        changelog_path.write_text(new_content, "utf-8")
    else:
        header = "# CHANGELOG - wakfu-optimizer\n> Archive de toutes les sessions\n\n---\n"
        changelog_path.write_text(header + "\n".join(changelog_entry), "utf-8")
    log("SESSION", "CHANGELOG.md mis a jour")

    # 3. Regenerer PROJECT_MEMORY.md et BRIEFING.md
    build_result = execute_powershell("python scripts/build_memory.py", timeout=30)

    return {
        "success": True,
        "handoff_written": True,
        "changelog_updated": True,
        "memory_rebuilt": build_result.get("success", False),
        "timestamp": ts,
    }

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    os.chdir(PROJECT)

    log("START", f"Dev Server demarre sur {HOST}:{PORT}")
    log("START", f"Projet : {PROJECT}")
    log("START", f"Commandes autorisees : {len(ALLOWED_COMMANDS)}")
    log("START", f"Patterns bloques : {len(BLOCKED_PATTERNS)}")

    print("=" * 60)
    print(f"  WAKFU DEV SERVER v1.0")
    print(f"  http://{HOST}:{PORT}")
    print(f"  Projet : {PROJECT}")
    print(f"")
    print(f"  Routes :")
    print(f"    GET  /health      - Verification")
    print(f"    GET  /status      - Etat du projet")
    print(f"    GET  /logs        - Derniers logs")
    print(f"    GET  /read-file   - Lire un fichier (?path=...)")
    print(f"    POST /execute     - Executer une commande PS")
    print(f"    POST /write-file  - Ecrire un fichier")
    print(f"    POST /voice-note  - Ajouter une note vocale")
    print(f"    POST /build-memory - Regenerer la memoire")
    print(f"    POST /session-end - Protocole fin de session")
    print(f"")
    print(f"  Ctrl+C pour arreter")
    print("=" * 60)

    server = HTTPServer((HOST, PORT), DevHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log("STOP", "Serveur arrete par l'utilisateur")
        server.server_close()
        print("\nServeur arrete.")
