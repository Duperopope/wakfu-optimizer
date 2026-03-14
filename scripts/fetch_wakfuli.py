import urllib.request, re, os, json

PROJECT = r"H:\Code\Ankama Dev\wakfu-optimizer"
base = "https://wakfuli.com"
ref_dir = os.path.join(PROJECT, "reference")
os.makedirs(ref_dir, exist_ok=True)

# Ajouter reference/ au manifest comme dossier protege
mpath = os.path.join(PROJECT, "MANIFEST.json")
with open(mpath, "r", encoding="utf-8") as f:
    manifest = json.load(f)
if "reference" not in manifest["protected_dirs"]:
    manifest["protected_dirs"].append("reference")
    with open(mpath, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print("Manifest mis a jour: reference/ protege")

# Telecharger le HTML
print("\nTelechargement HTML...")
url = "https://wakfuli.com/builder/public"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
html = urllib.request.urlopen(req).read().decode("utf-8")
html_path = os.path.join(ref_dir, "wakfuli.html")
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)
print(f"HTML: {len(html)} chars")

# Telecharger les CSS
css_files = re.findall(r'href="([^"]*\.css[^"]*)"', html)
all_css = ""
for i, u in enumerate(css_files):
    full = base + u if u.startswith("/") else u
    print(f"CSS {i+1}/{len(css_files)}: {full}")
    try:
        req = urllib.request.Request(full, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req).read().decode("utf-8")
        all_css += data + "\n"
        print(f"  {len(data)} chars")
    except Exception as e:
        print(f"  ERREUR: {e}")
with open(os.path.join(ref_dir, "wakfuli_all.css"), "w", encoding="utf-8") as f:
    f.write(all_css)

# Analyser les JS
js_files = re.findall(r'src="([^"]*\.js[^"]*)"', html)
report = ""
for i, u in enumerate(js_files):
    full = base + u if u.startswith("/") else u
    print(f"JS {i+1}/{len(js_files)}: {full[:60]}...")
    try:
        req = urllib.request.Request(full, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req).read().decode("utf-8", errors="replace")
        classes = set(re.findall(r'className:"([^"]{5,80})"', data))
        labels = set(re.findall(r'"(Statistiques|Sorts|Items|[EÉ]quipement|Enchantement|Caract|[RÉ]sistances|Ma[iî]trises|Combat|Familier|Monture|Amulette|Casque|Plastron|Cape|Ceinture|Bottes|Anneau|Arme|Bouclier|[EÉ]paulettes|Embl[eè]me|Passi[fv]|Actif|Deck|Niveau|Raret|Sort|Spell|Level|Rarity|slot|equipment)"', data, re.IGNORECASE))
        if labels or len(classes) > 5:
            report += f"\n=== {u} ===\n"
            if labels:
                report += f"Labels: {sorted(labels)}\n"
            if classes:
                report += f"Classes ({len(classes)}):\n"
                for c in sorted(classes)[:40]:
                    report += f"  {c}\n"
            print(f"  {len(data)} chars, {len(labels)} labels, {len(classes)} classes")
        else:
            print(f"  {len(data)} chars (framework)")
    except Exception as e:
        print(f"  ERREUR: {e}")

with open(os.path.join(ref_dir, "wakfuli_analysis.txt"), "w", encoding="utf-8") as f:
    f.write(report)
print(f"\nAnalyse sauvegardee: {len(report)} chars")
print("DONE - fichiers dans reference/")
