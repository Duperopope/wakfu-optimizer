import os
import sys
import json
import ast
from datetime import datetime
from pathlib import Path

# === Configuration ===
PROJECT_ROOT = Path(r"H:\Code\Ankama Dev\wakfu-optimizer")
AUDIT_DIR = PROJECT_ROOT / "logs" / "audit"
AUDIT_DIR.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

def write_report(filename, content):
    """Ecrit un rapport dans le dossier audit"""
    filepath = AUDIT_DIR / f"{timestamp}_{filename}"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] {filepath.name} ({len(content):,} caracteres)")
    return filepath

# === 1. INVENTAIRE COMPLET ===
print("=" * 60)
print("AUDIT WAKFU-OPTIMIZER v2")
print(f"Date : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Racine : {PROJECT_ROOT}")
print("=" * 60)

all_files = []
for root, dirs, files in os.walk(PROJECT_ROOT):
    # On skip .venv et .git pour pas polluer
    dirs[:] = [d for d in dirs if d not in ('.venv', '.git', '__pycache__', 'node_modules')]
    for f in files:
        filepath = Path(root) / f
        try:
            stat = filepath.stat()
            all_files.append({
                "path": str(filepath.relative_to(PROJECT_ROOT)),
                "abs_path": str(filepath),
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                "ext": filepath.suffix.lower(),
                "name": filepath.name,
                "parent": str(filepath.parent.relative_to(PROJECT_ROOT)),
            })
        except Exception as e:
            all_files.append({
                "path": str(filepath.relative_to(PROJECT_ROOT)),
                "abs_path": str(filepath),
                "size": 0,
                "modified": "ERREUR",
                "ext": filepath.suffix.lower(),
                "name": filepath.name,
                "parent": "ERREUR",
                "error": str(e),
            })

print(f"\nTotal fichiers trouves : {len(all_files)}")

# === 2. RAPPORT ARBORESCENCE ===
print("\n[1/6] Arborescence...")
tree_lines = []
tree_lines.append(f"ARBORESCENCE WAKFU-OPTIMIZER")
tree_lines.append(f"{'=' * 60}")
tree_lines.append(f"Total : {len(all_files)} fichiers")
tree_lines.append("")

# Grouper par dossier parent
from collections import defaultdict
by_folder = defaultdict(list)
for f in all_files:
    by_folder[f["parent"]].append(f)

for folder in sorted(by_folder.keys()):
    files_in_folder = by_folder[folder]
    total_size = sum(f["size"] for f in files_in_folder)
    tree_lines.append(f"\n{'─' * 40}")
    tree_lines.append(f"📁 {folder}/ ({len(files_in_folder)} fichiers, {total_size:,} octets)")
    tree_lines.append(f"{'─' * 40}")
    for f in sorted(files_in_folder, key=lambda x: x["name"]):
        size_kb = f["size"] / 1024
        tree_lines.append(f"  {f['name']:<50} {size_kb:>8.1f} KB  {f['modified']}")

write_report("01_arborescence.txt", "\n".join(tree_lines))

# === 3. RAPPORT PYTHON ===
print("[2/6] Analyse fichiers Python...")
py_files = [f for f in all_files if f["ext"] == ".py"]
py_lines = []
py_lines.append(f"ANALYSE FICHIERS PYTHON ({len(py_files)} fichiers)")
py_lines.append(f"{'=' * 60}")

for pf in sorted(py_files, key=lambda x: x["path"]):
    py_lines.append(f"\n{'━' * 60}")
    py_lines.append(f"📄 {pf['path']}")
    py_lines.append(f"   Taille: {pf['size']:,} octets | Modifie: {pf['modified']}")
    
    try:
        with open(pf["abs_path"], "r", encoding="utf-8", errors="replace") as f:
            source = f.read()
        
        lines = source.split("\n")
        py_lines.append(f"   Lignes: {len(lines)}")
        
        # Syntaxe valide ?
        try:
            tree = ast.parse(source)
            py_lines.append(f"   Syntaxe: OK")
            
            # Extraire classes, fonctions, imports
            classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
            functions = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(f"from {node.module}")
            
            if classes:
                py_lines.append(f"   Classes: {', '.join(classes)}")
            if functions:
                py_lines.append(f"   Fonctions: {', '.join(functions)}")
            if imports:
                unique_imports = sorted(set(imports))
                py_lines.append(f"   Imports: {', '.join(unique_imports)}")
                
        except SyntaxError as se:
            py_lines.append(f"   Syntaxe: ERREUR ligne {se.lineno} - {se.msg}")
        
        # Chemins en dur
        hardcoded = []
        for i, line in enumerate(lines, 1):
            if any(p in line.lower() for p in ["c:\\users", "h:\\code", "c:/users", "h:/code"]):
                if not line.strip().startswith("#"):
                    hardcoded.append(f"     L{i}: {line.strip()[:100]}")
        if hardcoded:
            py_lines.append(f"   Chemins en dur ({len(hardcoded)}):")
            for h in hardcoded[:5]:  # Max 5
                py_lines.append(h)
            if len(hardcoded) > 5:
                py_lines.append(f"     ... et {len(hardcoded)-5} autres")
        
        # Premiere ligne (description)
        first_meaningful = ""
        for line in lines[:10]:
            stripped = line.strip()
            if stripped and not stripped.startswith("#!"):
                first_meaningful = stripped[:120]
                break
        if first_meaningful:
            py_lines.append(f"   Debut: {first_meaningful}")
            
    except Exception as e:
        py_lines.append(f"   ERREUR lecture: {e}")

write_report("02_python_analyse.txt", "\n".join(py_lines))

# === 4. RAPPORT JSON/DATA ===
print("[3/6] Analyse fichiers JSON/data...")
json_files = [f for f in all_files if f["ext"] == ".json"]
json_lines = []
json_lines.append(f"ANALYSE FICHIERS JSON ({len(json_files)} fichiers)")
json_lines.append(f"{'=' * 60}")

for jf in sorted(json_files, key=lambda x: x["path"]):
    json_lines.append(f"\n{'━' * 60}")
    json_lines.append(f"📄 {jf['path']}")
    json_lines.append(f"   Taille: {jf['size']:,} octets | Modifie: {jf['modified']}")
    
    try:
        with open(jf["abs_path"], "r", encoding="utf-8", errors="replace") as f:
            raw = f.read()
        
        data = json.loads(raw)
        
        if isinstance(data, list):
            json_lines.append(f"   Type: Liste de {len(data)} elements")
            if len(data) > 0:
                first = data[0]
                if isinstance(first, dict):
                    keys = list(first.keys())[:10]
                    json_lines.append(f"   Cles (1er element): {', '.join(str(k) for k in keys)}")
                    # Echantillon de valeurs
                    for k in keys[:3]:
                        val = first[k]
                        val_str = str(val)[:80]
                        json_lines.append(f"     {k}: {val_str}")
                else:
                    json_lines.append(f"   Type element: {type(first).__name__} - {str(first)[:80]}")
                    
        elif isinstance(data, dict):
            keys = list(data.keys())[:15]
            json_lines.append(f"   Type: Dictionnaire ({len(data)} cles)")
            json_lines.append(f"   Cles: {', '.join(str(k) for k in keys)}")
            for k in keys[:5]:
                val = data[k]
                if isinstance(val, (list, dict)):
                    val_str = f"{type(val).__name__}({len(val)} elements)"
                else:
                    val_str = str(val)[:80]
                json_lines.append(f"     {k}: {val_str}")
        else:
            json_lines.append(f"   Type: {type(data).__name__} - {str(data)[:80]}")
            
    except json.JSONDecodeError as je:
        json_lines.append(f"   JSON INVALIDE: {je}")
    except Exception as e:
        json_lines.append(f"   ERREUR lecture: {e}")

write_report("03_json_analyse.txt", "\n".join(json_lines))

# === 5. RAPPORT LOGS ===
print("[4/6] Analyse fichiers logs...")
log_files = [f for f in all_files if f["ext"] in (".log", ".txt") and "log" in f["parent"].lower()]
log_lines = []
log_lines.append(f"ANALYSE FICHIERS LOGS ({len(log_files)} fichiers)")
log_lines.append(f"{'=' * 60}")

for lf in sorted(log_files, key=lambda x: x["modified"], reverse=True):
    log_lines.append(f"\n{'━' * 60}")
    log_lines.append(f"📄 {lf['path']}")
    log_lines.append(f"   Taille: {lf['size']:,} octets | Modifie: {lf['modified']}")
    
    try:
        with open(lf["abs_path"], "r", encoding="utf-8", errors="replace") as f:
            content = f.readlines()
        
        log_lines.append(f"   Lignes: {len(content)}")
        
        if content:
            log_lines.append(f"   Premiere ligne: {content[0].strip()[:120]}")
            log_lines.append(f"   Derniere ligne: {content[-1].strip()[:120]}")
            
            # Compter les niveaux de log
            counts = {"ERROR": 0, "WARNING": 0, "INFO": 0, "DEBUG": 0}
            for line in content:
                for level in counts:
                    if level in line.upper():
                        counts[level] += 1
            if any(v > 0 for v in counts.values()):
                log_lines.append(f"   Niveaux: ERROR={counts['ERROR']}, WARNING={counts['WARNING']}, INFO={counts['INFO']}, DEBUG={counts['DEBUG']}")
                
    except Exception as e:
        log_lines.append(f"   ERREUR lecture: {e}")

write_report("04_logs_analyse.txt", "\n".join(log_lines))

# === 6. RAPPORT DOUBLONS ET ARCHIVES ===
print("[5/6] Detection doublons et archives...")
dup_lines = []
dup_lines.append(f"DETECTION DOUBLONS ET FICHIERS SUSPECTS")
dup_lines.append(f"{'=' * 60}")

# Fichiers avec _archive, _old, _backup, _v dans le chemin
archive_files = [f for f in all_files if any(tag in f["path"].lower() for tag in ["_archive", "_old", "_backup", "archive/", "old/"])]
dup_lines.append(f"\n--- FICHIERS ARCHIVES ({len(archive_files)}) ---")
for af in sorted(archive_files, key=lambda x: x["path"]):
    dup_lines.append(f"  {af['path']} ({af['size']:,} octets, {af['modified']})")

# Fichiers Python avec des noms similaires (potentiels doublons)
py_names = defaultdict(list)
for pf in py_files:
    base = pf["name"].lower().replace("_v2", "").replace("_v3", "").replace("_v4", "").replace("_v5", "").replace("_old", "").replace("_backup", "").replace("_new", "")
    py_names[base].append(pf)

dup_lines.append(f"\n--- SCRIPTS PYTHON POTENTIELLEMENT DUPLIQUES ---")
for base, variants in sorted(py_names.items()):
    if len(variants) > 1:
        dup_lines.append(f"\n  Groupe '{base}':")
        for v in variants:
            dup_lines.append(f"    {v['path']} ({v['size']:,} octets, {v['modified']})")

# Fichiers JSON en double (meme nom, dossiers differents)
json_names = defaultdict(list)
for jf in json_files:
    json_names[jf["name"].lower()].append(jf)

dup_lines.append(f"\n--- FICHIERS JSON POTENTIELLEMENT DUPLIQUES ---")
for name, variants in sorted(json_names.items()):
    if len(variants) > 1:
        dup_lines.append(f"\n  '{name}':")
        for v in variants:
            dup_lines.append(f"    {v['path']} ({v['size']:,} octets, {v['modified']})")

write_report("05_doublons_archives.txt", "\n".join(dup_lines))

# === 7. RESUME FINAL ===
print("[6/6] Resume...")
summary_lines = []
summary_lines.append(f"RESUME AUDIT WAKFU-OPTIMIZER")
summary_lines.append(f"{'=' * 60}")
summary_lines.append(f"Date : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
summary_lines.append(f"Racine : {PROJECT_ROOT}")
summary_lines.append(f"")

# Stats par extension
ext_stats = defaultdict(lambda: {"count": 0, "size": 0})
for f in all_files:
    ext_stats[f["ext"]]["count"] += 1
    ext_stats[f["ext"]]["size"] += f["size"]

summary_lines.append(f"--- PAR EXTENSION ---")
for ext, stats in sorted(ext_stats.items(), key=lambda x: x[1]["size"], reverse=True):
    summary_lines.append(f"  {ext or '(sans ext)':<12} {stats['count']:>5} fichiers  {stats['size']/1024/1024:>8.2f} MB")

total_size = sum(f["size"] for f in all_files)
summary_lines.append(f"\n  {'TOTAL':<12} {len(all_files):>5} fichiers  {total_size/1024/1024:>8.2f} MB")

# Stats par dossier racine
summary_lines.append(f"\n--- PAR DOSSIER RACINE ---")
root_folders = defaultdict(lambda: {"count": 0, "size": 0})
for f in all_files:
    parts = f["path"].split(os.sep)
    root_folder = parts[0] if len(parts) > 1 else "(racine)"
    root_folders[root_folder]["count"] += 1
    root_folders[root_folder]["size"] += f["size"]

for folder, stats in sorted(root_folders.items(), key=lambda x: x[1]["size"], reverse=True):
    summary_lines.append(f"  {folder:<30} {stats['count']:>5} fichiers  {stats['size']/1024/1024:>8.2f} MB")

# Fichiers les plus gros
summary_lines.append(f"\n--- TOP 20 PLUS GROS FICHIERS ---")
biggest = sorted(all_files, key=lambda x: x["size"], reverse=True)[:20]
for f in biggest:
    summary_lines.append(f"  {f['size']/1024/1024:>8.2f} MB  {f['path']}")

# Fichiers les plus recents
summary_lines.append(f"\n--- 20 FICHIERS LES PLUS RECENTS ---")
newest = sorted(all_files, key=lambda x: x["modified"], reverse=True)[:20]
for f in newest:
    summary_lines.append(f"  {f['modified']}  {f['path']}")

summary_lines.append(f"\n--- FICHIERS RAPPORTS GENERES ---")
for report_file in sorted(AUDIT_DIR.glob(f"{timestamp}_*")):
    summary_lines.append(f"  {report_file.name}")

write_report("06_resume.txt", "\n".join(summary_lines))

print(f"\n{'=' * 60}")
print(f"AUDIT TERMINE")
print(f"Tous les rapports sont dans : {AUDIT_DIR}")
print(f"{'=' * 60}")
print(f"\nPour les consulter :")
print(f'  dir "{AUDIT_DIR}"')
print(f"Ou ouvre-les dans VS Code :")
print(f'  code "{AUDIT_DIR}"')
