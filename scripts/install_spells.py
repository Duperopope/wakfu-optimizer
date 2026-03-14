import json, shutil, sys
from datetime import datetime
from pathlib import Path

PROJECT = Path(r"H:\Code\Ankama Dev\wakfu-optimizer")
DATA = PROJECT / "data" / "wakfuli"
MANIFEST = PROJECT / "MANIFEST.json"

DATA.mkdir(parents=True, exist_ok=True)

m = json.loads(MANIFEST.read_text("utf-8"))
allowed = m.get("allowed_files", [])
if "scripts/install_spells.py" not in allowed:
    m["allowed_files"] = allowed + ["scripts/install_spells.py"]
    MANIFEST.write_text(json.dumps(m, ensure_ascii=False, indent=2), "utf-8")
    print("MANIFEST mis a jour")

candidates = [
    Path(r"H:\Downloads\wakfuli_all_spells.json"),
    Path.home() / "Downloads" / "wakfuli_all_spells.json",
    PROJECT / "wakfuli_all_spells.json",
]

source = None
for c in candidates:
    if c.exists():
        source = c
        print("Trouve : " + str(c))
        break

if not source:
    print("ERREUR: fichier introuvable")
    sys.exit(1)

data = json.loads(source.read_text("utf-8"))
print("Classes : " + str(len(data)))

total_all = 0
for name in sorted(data):
    d = data[name]
    e = len(d.get("elementary", []))
    a = len(d.get("active", []))
    p = len(d.get("passive", []))
    t = e + a + p
    total_all += t
    print("  " + name.ljust(15) + ": " + str(e) + " elem, " + str(a) + " actifs, " + str(p) + " passifs = " + str(t))

dest = DATA / "all_spells.json"
shutil.copy2(source, dest)
mb = round(dest.stat().st_size / 1048576, 2)
print("Copie : " + str(dest) + " (" + str(mb) + " MB)")
print("Total sorts : " + str(total_all))

report = {"classes": len(data), "total_sorts": total_all, "size_mb": mb, "date": datetime.now().isoformat()}
(DATA / "spells_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), "utf-8")
print("TERMINE")
