import time, subprocess, os, json
from pathlib import Path
from datetime import datetime

PROJECT = Path(r"H:\Code\Ankama Dev\wakfu-optimizer")
os.chdir(PROJECT)
MANIFEST = PROJECT / "MANIFEST.json"

def load_manifest():
    if not MANIFEST.exists():
        return set(), set()
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    files = set(m.get("protected", []) + m.get("local_only", []))
    dirs = set(m.get("protected_dirs", []))
    return files, dirs

def clean():
    allowed_files, allowed_dirs = load_manifest()
    if not allowed_files:
        return 0
    skip = {".venv", ".git", "__pycache__", "node_modules"}
    removed = 0
    for root, dirs, files in os.walk(PROJECT):
        dirs[:] = [d for d in dirs if d not in skip]
        for f in files:
            fp = Path(root) / f
            rel = str(fp.relative_to(PROJECT)).replace("\\", "/")
            # Skip si dans un dossier protege entierement (decompiled, logs)
            top = rel.split("/")[0]
            if top in allowed_dirs:
                continue
            # Skip gitignore patterns
            if rel.startswith(".git"):
                continue
            if rel not in allowed_files:
                fp.unlink()
                print(f"  [CLEAN] {rel}")
                removed += 1
    # Supprimer dossiers vides
    for root, dirs, files in os.walk(PROJECT, topdown=False):
        dirs[:] = [d for d in dirs if d not in skip]
        for d in dirs:
            dp = Path(root) / d
            if dp.name in skip:
                continue
            try:
                if not any(dp.iterdir()):
                    dp.rmdir()
                    print(f"  [CLEAN] dossier vide {dp.relative_to(PROJECT)}")
            except:
                pass
    return removed

print("AUTOPUSH + AUTOCLEAN actif")
print("Ctrl+C pour arreter")

cycle = 0
while True:
    try:
        # Nettoyage toutes les 30 secondes
        if cycle % 6 == 0:
            n = clean()
            if n > 0:
                print(f"  Nettoye {n} fichier(s) hors manifest")

        s = subprocess.run(["git","status","--porcelain"], capture_output=True, text=True)
        if s.stdout.strip():
            now = datetime.now().strftime("%H:%M:%S")
            n = len(s.stdout.strip().splitlines())
            subprocess.run(["git","add","-A"])
            subprocess.run(["git","commit","-m",f"auto {now} ({n} fichiers)"], capture_output=True)
            r = subprocess.run(["git","push"], capture_output=True, text=True)
            if r.returncode == 0:
                print(f"[{now}] Push OK - {n} fichier(s)")
            else:
                print(f"[{now}] ERREUR: {r.stderr.strip()[:100]}")
        time.sleep(5)
        cycle += 1
    except KeyboardInterrupt:
        print("Arrete.")
        break
