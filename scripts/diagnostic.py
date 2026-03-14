import os
from pathlib import Path

P = Path(r"H:\Code\Ankama Dev\wakfu-optimizer")

print("=" * 60)
print("DIAGNOSTIC COMPLET DU PROJET")
print("=" * 60)

# 1. Verifier data/wakfuli
dw = P / "data" / "wakfuli"
print(f"\n[1] Dossier data/wakfuli : {'EXISTE' if dw.exists() else 'ABSENT'}")
if dw.exists():
    files = list(dw.iterdir())
    print(f"    Fichiers : {len(files)}")
    for f in sorted(files):
        size = f.stat().st_size / (1024*1024)
        print(f"    - {f.name} ({size:.2f} MB)")
else:
    print("    -> Il faudra relancer sync_wakfuli.py")

# 2. Verifier scripts essentiels
print(f"\n[2] Scripts essentiels :")
essentiels = ["sync_wakfuli.py", "install_spells.py", "build_memory.py", "autopush.py"]
sc = P / "scripts"
for s in essentiels:
    sp = sc / s
    print(f"    - {s} : {'OK' if sp.exists() else 'ABSENT'}")

# 3. Compter tous les scripts
all_scripts = list(sc.glob("*.py")) if sc.exists() else []
print(f"    Total scripts : {len(all_scripts)}")

# 4. Fichiers racine
print(f"\n[3] Fichiers racine :")
racine = ["MANIFEST.json", "PROJECT_MEMORY.md", "app.py", "config.py", ".gitignore", "README.md"]
for r in racine:
    rp = P / r
    if rp.exists():
        size = rp.stat().st_size / 1024
        print(f"    - {r} ({size:.1f} KB)")
    else:
        print(f"    - {r} : ABSENT")

# 5. MANIFEST contenu
print(f"\n[4] MANIFEST.json contenu :")
mp = P / "MANIFEST.json"
if mp.exists():
    import json
    m = json.loads(mp.read_text("utf-8"))
    af = m.get("allowed_files", [])
    print(f"    allowed_files : {len(af)} entrees")
    for a in sorted(af):
        exists = (P / a.replace("/", os.sep)).exists()
        status = "OK" if exists else "MANQUANT"
        print(f"      [{status}] {a}")

# 6. Downloads check
print(f"\n[5] Fichier spells dans Downloads :")
dl = Path(r"H:\Downloads\wakfuli_all_spells.json")
if dl.exists():
    size = dl.stat().st_size / (1024*1024)
    print(f"    wakfuli_all_spells.json : {size:.2f} MB")
else:
    print("    ABSENT dans H:\\Downloads")

print("\n" + "=" * 60)
print("FIN DU DIAGNOSTIC")
print("=" * 60)
