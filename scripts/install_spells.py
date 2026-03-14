import json, shutil, sys
from datetime import datetime
from pathlib import Path

PROJECT = Path(r"H:\Code\Ankama Dev\wakfu-optimizer")
DATA = PROJECT / "data" / "wakfuli"
MANIFEST = PROJECT / "MANIFEST.json"
SCRIPTS = PROJECT / "scripts"

DATA.mkdir(parents=True, exist_ok=True)
SCRIPTS.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("ETAPE 1 - MANIFEST")
print("=" * 60)

entries = [
    "scripts/install_spells.py",
    "scripts/sync_wakfuli.py",
    "data/wakfuli/all_spells.json",
    "data/wakfuli/spells_report.json",
    "data/wakfuli/all_items.json",
    "data/wakfuli/all_actions.json",
    "data/wakfuli/all_builds.json",
    "data/wakfuli/spell_index_from_builds.json",
    "data/wakfuli/sync_report.json",
    "data/wakfuli/version.json",
]

m = json.loads(MANIFEST.read_text("utf-8"))
allowed = m.get("allowed_files", [])
added = [e for e in entries if e not in allowed]
if added:
    m["allowed_files"] = allowed + added
    MANIFEST.write_text(json.dumps(m, ensure_ascii=False, indent=2), "utf-8")
    for a in added:
        print("  + " + a)
    print(str(len(added)) + " entrees ajoutees")
else:
    print("Deja a jour")

print()
print("=" * 60)
print("ETAPE 2 - RECHERCHE DU FICHIER")
print("=" * 60)

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
    print("ERREUR: fichier introuvable dans :")
    for c in candidates:
        print("  - " + str(c))
    sys.exit(1)

print()
print("=" * 60)
print("ETAPE 3 - ANALYSE")
print("=" * 60)

data = json.loads(source.read_text("utf-8"))
print("Classes : " + str(len(data)))
print()

total_all = 0
for name in sorted(data):
    d = data[name]
    e = len(d.get("elementary", []))
    a = len(d.get("active", []))
    p = len(d.get("passive", []))
    t = e + a + p
    total_all += t
    line = "  " + name.ljust(15) + ": " + str(e) + " elem, " + str(a) + " actifs, " + str(p) + " passifs = " + str(t)
    print(line)

print()
print("=" * 60)
print("ETAPE 4 - COPIE ET RAPPORT")
print("=" * 60)

dest = DATA / "all_spells.json"
shutil.copy2(source, dest)
mb = round(dest.stat().st_size / 1048576, 2)
print("Copie : " + str(dest))
print("Taille : " + str(mb) + " MB")
print("Total sorts : " + str(total_all))

report = {
    "classes": len(data),
    "total_sorts": total_all,
    "size_mb": mb,
    "date": datetime.now().isoformat(),
}
rp = DATA / "spells_report.json"
rp.write_text(json.dumps(report, ensure_ascii=False, indent=2), "utf-8")
print("Rapport : " + str(rp))
print()
print("TERMINE")
print("=" * 60)
