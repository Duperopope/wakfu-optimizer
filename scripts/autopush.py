import time, subprocess, os
from pathlib import Path
from datetime import datetime

PROJECT = Path(r"H:\Code\Ankama Dev\wakfu-optimizer")
os.chdir(PROJECT)

print("AUTOPUSH actif")
print("Ctrl+C pour arreter")

while True:
    try:
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
    except KeyboardInterrupt:
        print("Arrete.")
        break
