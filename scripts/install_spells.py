import json, shutil
from pathlib import Path
from datetime import datetime

PROJECT = Path(r"H:\Code\Ankama Dev\wakfu-optimizer")
DATA = PROJECT / "data" / "wakfuli"
DATA.mkdir(parents=True, exist_ok=True)

SEARCH_PATHS = [
    Path(r"H:\Downloads\wakfuli_all_spells.json"),
    Path.home() / "Downloads" / "wakfuli_all_spells.json",
    PROJECT / "wakfuli_all_spells.json",
]

source = None
for p in SEARCH_PATHS:
    if p.exists():
        source = p
        break

if not source:
    print("ERREUR : wakfuli_all_spells.json introuvable")
    for p in SEARCH_PATHS:
        print("  - " + str(p))
    exit(1)

print("Trouve : " + str(source))
data = json.loads(source.read_text("utf-8"))
classes = list(data.keys())
print("Classes : " + str(len(classes)))

total_all = 0
report_classes = {}
for cls in sorted(classes):
    info = data[cls]
    n_elem = len(info.get("elementaries", []))
    n_act = len(info.get("actives", []))
    n_pas = len(info.get("passives", []))
    n_tot = n_elem + n_act + n_pas
    total_all += n_tot
    report_classes[cls] = {
        "elementary": n_elem,
        "active": n_act,
        "passive": n_pas,
        "total": n_tot,
    }
    label = cls.ljust(15)
    print("  " + label + ": " + str(n_elem) + " elem, " + str(n_act) + " actifs, " + str(n_pas) + " passifs = " + str(n_tot))

dest = DATA / "all_spells.json"
shutil.copy2(source, dest)
size_mb = dest.stat().st_size / (1024 * 1024)
print("Copie : " + str(dest) + " (" + str(round(size_mb, 2)) + " MB)")
print("Total sorts : " + str(total_all))

report = {
    "date": datetime.now().isoformat(),
    "source": str(source),
    "destination": str(dest),
    "size_mb": round(size_mb, 2),
    "total_classes": len(classes),
    "total_spells": total_all,
    "per_class": report_classes,
}
rpt = DATA / "spells_report.json"
rpt.write_text(json.dumps(report, ensure_ascii=False, indent=2), "utf-8")
print("Rapport : " + str(rpt))
print("TERMINE")
