import time, subprocess, os, json
from pathlib import Path
from datetime import datetime

PROJECT = Path(r"H:\Code\Ankama Dev\wakfu-optimizer")
os.chdir(PROJECT)
MANIFEST = PROJECT / "MANIFEST.json"
SKIP = {".venv", ".git", "__pycache__", "node_modules"}

# Fix CRLF warnings
subprocess.run(["git", "config", "core.autocrlf", "true"], capture_output=True)

def load_manifest():
    if not MANIFEST.exists():
        return set(), set()
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    files = set(m.get("protected", []) + m.get("local_only", []) + m.get("allowed_files", []))
    dirs = set(m.get("protected_dirs", []))
    return files, dirs

def clean():
    allowed_files, allowed_dirs = load_manifest()
    if not allowed_files:
        return 0
    removed = 0
    for root, dirs, files in os.walk(PROJECT):
        dirs[:] = [d for d in dirs if d not in SKIP]
        rel_root = Path(root).relative_to(PROJECT)
        top = str(rel_root).replace("\\", "/").split("/")[0]
        if top in allowed_dirs or top == ".":
            if str(rel_root) != ".":
                continue
        for f in files:
            fp = Path(root) / f
            rel = str(fp.relative_to(PROJECT)).replace("\\", "/")
            if rel not in allowed_files:
                fp.unlink()
                print(f"  [CLEAN] {rel}")
                removed += 1
    return removed

def get_changed_files():
    s = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    lines = [l for l in s.stdout.strip().splitlines() if l.strip()]
    return [l[3:] for l in lines if len(l) > 3]

print("AUTOPUSH v2 actif (temps reel + fix CRLF)")
print("Ctrl+C pour arreter")

cycle = 0
while True:
    try:
        if cycle % 6 == 0 and cycle > 0:
            n = clean()
            if n > 0:
                print(f"  Nettoye {n} fichier(s) hors manifest")

        files = get_changed_files()
        if files:
            now = datetime.now().strftime("%H:%M:%S")
            names = ", ".join([f.split("/")[-1] for f in files[:3]])
            if len(files) > 3:
                names += f" +{len(files)-3}"
            subprocess.run(["git", "add", "-A"], capture_output=True)
            subprocess.run(["git", "commit", "-m", f"auto {now}: {names}"], capture_output=True)
            r = subprocess.run(["git", "push"], capture_output=True, text=True)
            if r.returncode == 0:
                print(f"[{now}] Push OK - {len(files)} fichier(s): {names}")
            else:
                print(f"[{now}] ERREUR: {r.stderr.strip()[:100]}")

        time.sleep(5)
        cycle += 1
    except KeyboardInterrupt:
        files = get_changed_files()
        if files:
            subprocess.run(["git", "add", "-A"], capture_output=True)
            subprocess.run(["git", "commit", "-m", "auto: push final"], capture_output=True)
            subprocess.run(["git", "push"], capture_output=True)
            print("Push final OK")
        print("Arrete.")
        break
