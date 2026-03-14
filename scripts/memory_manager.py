"""
memory_manager.py v1.0 - Systeme de memoire unifiee pour Wakfu Dev Orchestra
Gere 5 types de memoire en parallele pendant le developpement.
Sources:
  - IBM: https://www.ibm.com/think/topics/ai-agent-memory
  - ML Mastery: https://machinelearningmastery.com/beyond-short-term-memory-the-3-types-of-long-term-memory-ai-agents-need/
  - Anthropic: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
"""

import json, time, os, re, subprocess
from pathlib import Path
from datetime import datetime
from threading import Thread, Lock

PROJECT = Path(r"H:\Code\Ankama Dev\wakfu-optimizer")
MEMORY_DIR = PROJECT / "memory"
MEMORY_DIR.mkdir(exist_ok=True)
LOGS_DIR = PROJECT / "logs"

# Fichiers memoire
EPISODIC_FILE = MEMORY_DIR / "episodes.jsonl"
PROCEDURAL_FILE = MEMORY_DIR / "procedures.json"
WORKING_FILE = MEMORY_DIR / "working_notes.md"
SEMANTIC_FILE = PROJECT / "PROJECT_MEMORY.md"
BRIEFING_FILE = PROJECT / "BRIEFING.md"
SESSION_LOG = MEMORY_DIR / "current_session.jsonl"

_lock = Lock()
def log(level, msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{ts}] [MEMORY/{level}] {msg}"
    print(entry)
    try:
        with open(LOGS_DIR / "memory_manager.log", "a", encoding="utf-8") as f:
            f.write(entry + "\n")
    except: pass

class EpisodicMemory:
    """Stocke les episodes: contexte -> action -> resultat."""
    def __init__(self):
        self.episodes = []
        self._load()

    def _load(self):
        if EPISODIC_FILE.exists():
            try:
                for line in EPISODIC_FILE.read_text("utf-8").strip().split("\n"):
                    if line.strip():
                        self.episodes.append(json.loads(line))
                log("EPISODIC", f"Charge {len(self.episodes)} episodes")
            except: pass

    def record(self, context, action, result, success, tags=None):
        """Enregistre un episode."""
        episode = {
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "action": action,
            "result": result[:500] if isinstance(result, str) else str(result)[:500],
            "success": success,
            "tags": tags or []
        }
        self.episodes.append(episode)
        with _lock:
            with open(EPISODIC_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(episode, ensure_ascii=False) + "\n")
        log("EPISODIC", "Episode enregistre: " + context[:60] + " -> " + ("OK" if success else "FAIL"))

    def search(self, query, limit=5):
        """Recherche les episodes similaires (par mots-cles)."""
        words = set(query.lower().split())
        scored = []
        for ep in self.episodes:
            text = (ep['context'] + ' ' + ep['action'] + ' ' + ' '.join(ep.get('tags', []))).lower()
            score = len(words & set(text.split()))
            if score > 0:
                scored.append((score, ep))
        scored.sort(key=lambda x: -x[0])
        return [ep for _, ep in scored[:limit]]

    def get_recent(self, n=10):
        return self.episodes[-n:]

    def get_failures(self, n=10):
        fails = [e for e in self.episodes if not e["success"]]
        return fails[-n:]

    def summarize_for_briefing(self, n=5):
        """Resume les derniers episodes pour injection dans le BRIEFING."""
        recent = self.get_recent(n)
        if not recent: return "Aucun episode enregistre."
        lines = []
        for ep in recent:
            status = "OK" if ep["success"] else "FAIL"
            ts = ep["timestamp"][11:19]
            lines.append('- [' + status + '] ' + ts + ' ' + ep['context'][:80])
        return "\n".join(lines)

class ProceduralMemory:
    """Stocke les procedures: recettes reutilisables."""
    def __init__(self):
        self.procedures = {}
        self._load()

    def _load(self):
        if PROCEDURAL_FILE.exists():
            try:
                self.procedures = json.loads(PROCEDURAL_FILE.read_text("utf-8"))
                log("PROCEDURAL", f"Charge {len(self.procedures)} procedures")
            except: pass

    def _save(self):
        with _lock:
            PROCEDURAL_FILE.write_text(json.dumps(self.procedures, indent=2, ensure_ascii=False), "utf-8")

    def record(self, name, steps, tags=None, source_episode=None):
        """Enregistre ou met a jour une procedure."""
        self.procedures[name] = {
            "steps": steps,
            "tags": tags or [],
            "last_used": datetime.now().isoformat(),
            "use_count": self.procedures.get(name, {}).get("use_count", 0) + 1,
            "source_episode": source_episode
        }
        self._save()
        log("PROCEDURAL", f"Procedure enregistree: {name}")

    def get(self, name):
        return self.procedures.get(name)

    def search(self, query):
        """Recherche par mots-cles dans noms et tags."""
        words = set(query.lower().split())
        results = []
        for name, proc in self.procedures.items():
            text = (name + ' ' + ' '.join(proc.get('tags', []))).lower()
            score = len(words & set(text.split()))
            if score > 0:
                results.append((score, name, proc))
        results.sort(key=lambda x: -x[0])
        return [(n, p) for _, n, p in results]

    def summarize_for_briefing(self):
        """Resume les procedures les plus utilisees."""
        if not self.procedures: return "Aucune procedure enregistree."
        sorted_procs = sorted(self.procedures.items(), key=lambda x: -x[1].get("use_count", 0))
        lines = []
        for name, proc in sorted_procs[:8]:
            count = proc.get("use_count", 0)
            lines.append('- ' + name + ' (x' + str(count) + '): ' + str(len(proc['steps'])) + ' etapes')
        return "\n".join(lines)

class WorkingMemory:
    """Notes de travail pour la session en cours."""
    def __init__(self):
        self.notes = []
        self.task_stack = []

    def add_note(self, note):
        entry = {"time": datetime.now().isoformat(), "note": note}
        self.notes.append(entry)
        self._save()

    def push_task(self, task):
        self.task_stack.append({"task": task, "started": datetime.now().isoformat()})
        log("WORKING", f"Tache empilee: {task}")

    def pop_task(self):
        if self.task_stack:
            done = self.task_stack.pop()
            log("WORKING", f"Tache terminee: {done['task']}")
            return done
        return None

    def current_task(self):
        return self.task_stack[-1]["task"] if self.task_stack else None

    def _save(self):
        lines = ["# Working Notes - " + datetime.now().strftime("%Y-%m-%d %H:%M"), ""]
        if self.task_stack:
            lines.append("## Taches en cours")
            for t in self.task_stack:
                lines.append('- [ ] ' + t['task'] + ' (depuis ' + t['started'][11:19] + ')')
            lines.append("")
        if self.notes:
            lines.append("## Notes")
            for n in self.notes[-20:]:
                lines.append('- ' + n['time'][11:19] + ' ' + n['note'])
        with _lock:
            WORKING_FILE.write_text("\n".join(lines), "utf-8")

    def summarize(self):
        task = self.current_task() or "Aucune"
        return f"Tache: {task} | Notes: {len(self.notes)}"

class SessionTracker:
    """Suit les evenements de la session pour nourrir les autres memoires."""
    def __init__(self):
        self.events = []
        self.session_start = datetime.now().isoformat()
        self.files_modified = set()
        self.commands_run = 0
        self.errors = 0

    def track_command(self, command, result, success, duration=0):
        """Enregistre une commande executee."""
        event = {
            "type": "command",
            "time": datetime.now().isoformat(),
            "command": command[:200],
            "success": success,
            "duration": duration
        }
        self.events.append(event)
        self.commands_run += 1
        if not success: self.errors += 1
        with _lock:
            with open(SESSION_LOG, "a", encoding="utf-8") as f:
                f.write(json.dumps(event, ensure_ascii=False) + "\n")

    def track_file_change(self, filepath):
        self.files_modified.add(filepath)

    def track_ext_log(self, log_entry):
        """Enregistre un log de l extension Chrome."""
        event = {
            "type": "ext_log",
            "time": datetime.now().isoformat(),
            "message": log_entry[:300]
        }
        self.events.append(event)

    def get_summary(self):
        return {
            "session_start": self.session_start,
            "duration_min": round((datetime.now() - datetime.fromisoformat(self.session_start)).total_seconds() / 60, 1),
            "commands_run": self.commands_run,
            "errors": self.errors,
            "files_modified": list(self.files_modified),
            "events_count": len(self.events)
        }

class DocBot:
    """Agent local qui met a jour la documentation via llama3.2:3b."""
    MODEL = "llama3.2:3b"
    OLLAMA_URL = "http://localhost:11434"

    def _ask(self, prompt, max_tokens=300):
        import urllib.request
        body = json.dumps({
            "model": self.MODEL, "prompt": prompt, "stream": False,
            "options": {"num_predict": max_tokens, "temperature": 0.3}
        }).encode("utf-8")
        try:
            req = urllib.request.Request(
                f"{self.OLLAMA_URL}/api/generate", data=body,
                headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8")).get("response", "").strip()
        except Exception as e:
            log("DOCBOT", f"Erreur Ollama: {e}")
            return None

    def generate_episode_tags(self, context, action, result):
        """Genere des tags pour un episode."""
        prompt = f"Generate 3-5 short tags for this development event. Reply with ONLY comma-separated tags.\nContext: {context[:200]}\nAction: {action[:200]}\nResult: {result[:100]}"
        resp = self._ask(prompt, 50)
        if resp:
            return [t.strip().lower() for t in resp.split(",") if t.strip()]
        return []

    def extract_procedure(self, episodes):
        """Detecte une procedure recurrente dans les episodes."""
        if len(episodes) < 2: return None
        recent = episodes[-5:]
        context_text = "\n".join(['- ' + e['context'][:80] + ': ' + e['action'][:80] for e in recent])
        prompt = f"These are recent development actions. If there is a repeated pattern, describe it as a reusable procedure with numbered steps. If no pattern, reply NONE.\n{context_text}"
        resp = self._ask(prompt, 200)
        if resp and "NONE" not in resp.upper():
            return resp
        return None

    def generate_changelog_entry(self, files_modified, commands_summary):
        """Genere une entree de changelog."""
        prompt = f"Write a brief changelog entry (1-2 lines) for these changes:\nFiles: {files_modified[:300]}\nActions: {commands_summary[:300]}"
        return self._ask(prompt, 100)

class Reviewer:
    """Agent local qui review le code ecrit via deepseek-coder-v2."""
    MODEL = "qwen2.5-coder:7b"
    OLLAMA_URL = "http://localhost:11434"

    def _ask(self, prompt, max_tokens=500):
        import urllib.request
        body = json.dumps({
            "model": self.MODEL, "prompt": prompt, "stream": False,
            "options": {"num_predict": max_tokens, "temperature": 0.1}
        }).encode("utf-8")
        try:
            req = urllib.request.Request(
                f"{self.OLLAMA_URL}/api/generate", data=body,
                headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                return json.loads(resp.read().decode("utf-8")).get("response", "").strip()
        except Exception as e:
            log("REVIEWER", f"Erreur Ollama: {e}")
            return None

    def review_file(self, filepath, content):
        """Review un fichier modifie."""
        prompt = f"Review this code file for bugs, missing imports, or regressions. Be brief. File: {filepath}\n```\n{content[:3000]}\n```"
        resp = self._ask(prompt)
        if resp:
            log("REVIEWER", f"Review {filepath}: {resp[:100]}")
        return resp

    def check_regression(self, filepath, old_content, new_content):
        """Verifie si une modification introduit une regression."""
        prompt = f"Compare old and new versions of {filepath}. Are there any regressions or lost features? Reply SAFE if OK, or describe the regression.\nOLD (last 50 lines):\n{old_content[-2000:]}\nNEW (last 50 lines):\n{new_content[-2000:]}"
        resp = self._ask(prompt)
        if resp:
            is_safe = "SAFE" in resp.upper()[:20]
            log("REVIEWER", "Regression check " + filepath + ": " + ("SAFE" if is_safe else "ISSUE: " + resp[:80]))
            return {"safe": is_safe, "details": resp}
        return {"safe": True, "details": "Review unavailable"}

class MemoryManager:
    """Orchestrateur central des 5 memoires."""
    def __init__(self):
        self.episodic = EpisodicMemory()
        self.procedural = ProceduralMemory()
        self.working = WorkingMemory()
        self.session = SessionTracker()
        self.docbot = DocBot()
        self.reviewer = Reviewer()
        log("MANAGER", "Memory Manager v1.0 initialise")
        log("MANAGER", f"Episodes: {len(self.episodic.episodes)} | Procedures: {len(self.procedural.procedures)}")

    def on_command_executed(self, command, result, success, duration=0):
        """Appele apres chaque execution de commande."""
        # 1. Session tracking
        self.session.track_command(command, result, success, duration)

        # 2. Episode recording (async via thread)
        def _record():
            context = self._extract_context(command)
            tags = self.docbot.generate_episode_tags(context, command[:200], result[:200])
            self.episodic.record(context, command[:300], result[:300], success, tags)
        Thread(target=_record, daemon=True).start()

    def on_file_modified(self, filepath, old_content=None, new_content=None):
        """Appele quand un fichier est modifie."""
        self.session.track_file_change(filepath)

        # Review en background si c est du code
        if new_content and filepath.endswith((".tsx", ".ts", ".py", ".js")):
            def _review():
                if old_content:
                    result = self.reviewer.check_regression(filepath, old_content, new_content)
                    if not result["safe"]:
                        self.working.add_note("REGRESSION DETECTEE dans " + filepath + ": " + result['details'][:100])
                        self.episodic.record(f"Regression dans {filepath}", "modification fichier", result['details'][:200], False, ["regression", filepath.split("/")[-1]])
                else:
                    self.reviewer.review_file(filepath, new_content)
            Thread(target=_review, daemon=True).start()

    def on_ext_log(self, message):
        """Appele quand l extension envoie un log."""
        self.session.track_ext_log(message)

    def get_briefing_context(self):
        """Genere le contexte a injecter dans le BRIEFING pour la prochaine session."""
        parts = []
        parts.append("## MEMOIRE EPISODIQUE (derniers evenements)")
        parts.append(self.episodic.summarize_for_briefing(8))
        parts.append("")
        parts.append("## MEMOIRE PROCEDURALE (savoir-faire)")
        parts.append(self.procedural.summarize_for_briefing())
        parts.append("")
        parts.append("## SESSION PRECEDENTE")
        summary = self.session.get_summary()
        parts.append("Duree: " + str(summary['duration_min']) + "min | Commandes: " + str(summary['commands_run']) + " | Erreurs: " + str(summary['errors']))
        parts.append("Fichiers modifies: " + ", ".join(summary['files_modified'][:10]))
        parts.append("")
        failures = self.episodic.get_failures(3)
        if failures:
            parts.append("## ERREURS RECENTES (ne pas repeter)")
            for f in failures:
                parts.append("- " + f['context'][:80] + ": " + f['result'][:100])
        return "\n".join(parts)

    def check_procedures(self):
        """Detecte de nouvelles procedures depuis les episodes recents."""
        recent = self.episodic.get_recent(10)
        result = self.docbot.extract_procedure(recent)
        if result:
            name = "auto_" + datetime.now().strftime("%Y%m%d_%H%M")
            self.procedural.record(name, result.split("\n"), ["auto-detected"])
            log("MANAGER", f"Nouvelle procedure detectee: {name}")

    def end_session(self):
        """Finalise la session: met a jour BRIEFING, detecte les procedures."""
        log("MANAGER", "Fin de session - consolidation memoire...")

        # Detecter procedures
        self.check_procedures()

        # Generer contexte briefing
        memory_context = self.get_briefing_context()

        # Mettre a jour BRIEFING.md
        try:
            briefing = BRIEFING_FILE.read_text("utf-8") if BRIEFING_FILE.exists() else ""
            marker = "## MEMOIRE EPISODIQUE"
            if marker in briefing:
                briefing = briefing[:briefing.index(marker)]
            briefing = briefing.rstrip() + "\n\n" + memory_context
            BRIEFING_FILE.write_text(briefing, "utf-8")
            log("MANAGER", "BRIEFING.md mis a jour avec memoire")
        except Exception as e:
            log("MANAGER", f"Erreur MAJ briefing: {e}")

        # Reset session
        summary = self.session.get_summary()
        log("MANAGER", f"Session terminee: {summary['commands_run']} commandes, {summary['errors']} erreurs, {len(summary['files_modified'])} fichiers modifies")
        return summary

    def _extract_context(self, command):
        """Extrait le contexte lisible d une commande."""
        cmd = command[:200]
        if "Write-Host" in cmd:
            return "Affichage/diagnostic PowerShell"
        elif "Set-Content" in cmd or "write_text" in cmd:
            return "Ecriture de fichier"
        elif "Get-Content" in cmd or "read_text" in cmd:
            return "Lecture de fichier"
        elif "pip install" in cmd:
            return "Installation de package Python"
        elif "npm" in cmd:
            return "Commande npm"
        elif "git" in cmd:
            return "Operation git"
        elif "Invoke-RestMethod" in cmd:
            return "Appel API/serveur"
        elif "python" in cmd:
            return "Execution script Python"
        else:
            return f"Commande: {cmd[:80]}"

# Instance globale
_manager = None

def get_manager():
    global _manager
    if _manager is None:
        _manager = MemoryManager()
    return _manager

if __name__ == "__main__":
    print("=== MEMORY MANAGER v1.0 - Test ===")
    mm = get_manager()
    print()
    print("--- Test Episodic ---")
    mm.on_command_executed("Write-Host Hello", "Hello", True, 0.3)
    time.sleep(2)
    print(f"Episodes: {len(mm.episodic.episodes)}")
    print()
    print("--- Test Procedural ---")
    mm.procedural.record("deploy_frontend", ["npm run build", "git push", "vercel deploy"], ["deploy", "frontend"])
    print(f"Procedures: {len(mm.procedural.procedures)}")
    print()
    print("--- Test Briefing Context ---")
    ctx = mm.get_briefing_context()
    print(ctx[:500])
    print()
    print("=== FIN TEST ===")