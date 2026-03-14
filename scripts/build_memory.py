import json, os
from pathlib import Path
from datetime import datetime

PROJECT = Path(r"H:\Code\Ankama Dev\wakfu-optimizer")
DATA = PROJECT / "data" / "wakfuli"

lines = []
lines.append("# PROJECT MEMORY - Wakfu Optimizer")
lines.append("")
lines.append("> Derniere mise a jour : " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
lines.append("> Genere par scripts/build_memory.py")
lines.append("> Memoire persistante entre sessions Claude")
lines.append("")

lines.append("## Regles du projet")
lines.append("")
lines.append("- Tout fichier doit etre dans MANIFEST.json/allowed_files AVANT creation")
lines.append("- Les commandes passent TOUJOURS par PowerShell")
lines.append("- Les data generees vont dans data/wakfuli/")
lines.append("- Les logs vont dans logs/")
lines.append("- Pas de placeholder : le code doit etre complet et fonctionnel")
lines.append("- autopush.py lit allowed_files + protected + local_only")
lines.append("")

lines.append("## Etat des donnees Wakfuli")
lines.append("")
lines.append("| Fichier | Taille | Source | Statut |")
lines.append("|---------|--------|--------|--------|")
data_files = {
    "all_items.json": "api.wakfuli.com/api/v1/items",
    "all_actions.json": "api.wakfuli.com/api/v1/actions",
    "all_builds.json": "api.wakfuli.com/api/v1/builds",
    "all_spells.json": "frontend Wakfuli (console JS)",
    "spell_index_from_builds.json": "extrait des builds",
    "sync_report.json": "genere par sync_wakfuli.py",
    "spells_report.json": "genere par install_spells.py",
    "version.json": "wakfu.cdn.ankama.com",
}
for fname, source in data_files.items():
    fp = DATA / fname
    if fp.exists():
        size = fp.stat().st_size / (1024 * 1024)
        lines.append("| " + fname + " | " + str(round(size, 2)) + " MB | " + source + " | OK |")
    else:
        lines.append("| " + fname + " | - | " + source + " | ABSENT |")
lines.append("")

lines.append("## Etat des donnees CDN Ankama (ancien systeme)")
lines.append("")
lines.append("| Dossier | Fichiers | Role |")
lines.append("|---------|----------|------|")
old_dirs = {
    "data/raw": "JSON bruts du CDN Ankama",
    "data/extracted": "Donnees parsees (items, spells, states, breeds)",
    "data/parsed": "Donnees transformees (action_map, state_map)",
    "data/classes": "Classes de personnages (sram, common)",
    "data/profiles": "Profils de builds (limmortel)",
}
for dname, role in old_dirs.items():
    dp = PROJECT / dname.replace("/", os.sep)
    if dp.exists():
        count = len([f for f in dp.iterdir() if f.is_file()])
        lines.append("| " + dname + "/ | " + str(count) + " | " + role + " | ")
    else:
        lines.append("| " + dname + "/ | 0 | " + role + " |")
lines.append("")

lines.append("## Moteur de calcul (ancien systeme)")
lines.append("")
lines.append("| Module | Role |")
lines.append("|--------|------|")
engine_mods = {
    "engine/combat.py": "Boucle de combat",
    "engine/damage.py": "Calcul de degats",
    "engine/effect_bridge.py": "Pont entre effets et stats",
    "engine/equipment.py": "Gestion equipement",
    "engine/fighter.py": "Entite combattant",
}
for mod, role in engine_mods.items():
    mp = PROJECT / mod.replace("/", os.sep)
    status = "OK" if mp.exists() else "ABSENT"
    lines.append("| " + mod + " | " + role + " (" + status + ") |")
lines.append("")

ver_path = DATA / "version.json"
version = "inconnue"
if ver_path.exists():
    try:
        version = json.loads(ver_path.read_text("utf-8")).get("version", "inconnue")
    except:
        pass
lines.append("## Version du jeu : " + version)
lines.append("")

sync_path = DATA / "sync_report.json"
if sync_path.exists():
    try:
        sr = json.loads(sync_path.read_text("utf-8"))
        lines.append("## Derniere synchronisation Wakfuli")
        lines.append("")
        lines.append("- Date : " + sr.get("date", "?"))
        lines.append("- Items : " + str(sr.get("items_received", "?")))
        lines.append("- Actions : " + str(sr.get("actions_received", "?")))
        lines.append("- Builds : " + str(sr.get("builds_received", "?")))
        lines.append("- Duree : " + str(sr.get("duration_seconds", "?")) + "s")
        lines.append("- Classes : " + ", ".join(sr.get("classes_covered", [])))
        lines.append("")
    except:
        pass

spl_path = DATA / "spells_report.json"
if spl_path.exists():
    try:
        sp = json.loads(spl_path.read_text("utf-8"))
        lines.append("## Sorts installes")
        lines.append("")
        lines.append("- Total : " + str(sp.get("total_spells", "?")) + " sorts")
        lines.append("- Classes : " + str(sp.get("total_classes", "?")))
        lines.append("- Taille : " + str(sp.get("size_mb", "?")) + " MB")
        lines.append("")
    except:
        pass

lines.append("## API Wakfuli")
lines.append("")
lines.append("| Endpoint | Statut | Notes |")
lines.append("|----------|--------|-------|")
lines.append("| /api/v1/items | OK | Pagine, filtres: levelMin, levelMax, itemType, rarity, search |")
lines.append("| /api/v1/actions | OK | 68 effets avec types et descriptions |")
lines.append("| /api/v1/builds | OK | Builds publics pagines |")
lines.append("| /api/v1/spells | 404 | Pas d endpoint sorts |")
lines.append("| /api/v1/breeds | 404 | Pas d endpoint classes |")
lines.append("")

lines.append("## CDN Ankama")
lines.append("")
lines.append("| URL | Contenu |")
lines.append("|-----|---------|")
lines.append("| wakfu.cdn.ankama.com/gamedata/config.json | Version courante |")
lines.append("| wakfu.cdn.ankama.com/gamedata/{v}/actions.json | Effets multilingues |")
lines.append("| wakfu.cdn.ankama.com/gamedata/{v}/states.json | Etats/sublimations |")
lines.append("| wakfu.cdn.ankama.com/gamedata/{v}/items.json | Items bruts |")
lines.append("")

lines.append("## Scripts")
lines.append("")
lines.append("| Script | Role | Essentiel |")
lines.append("|--------|------|-----------|")
essentiels = {
    "sync_wakfuli.py": "Telecharge items, actions, builds depuis API Wakfuli",
    "install_spells.py": "Installe les sorts depuis le fichier navigateur",
    "build_memory.py": "Genere PROJECT_MEMORY.md",
    "diagnostic.py": "Diagnostic complet du projet",
    "autopush.py": "Auto-commit + nettoyage fichiers hors manifest",
}
sc_dir = PROJECT / "scripts"
if sc_dir.exists():
    for s in sorted(sc_dir.glob("*.py")):
        name = s.name
        if name in essentiels:
            lines.append("| " + name + " | " + essentiels[name] + " | OUI |")
        else:
            lines.append("| " + name + " | Legacy/debug | NON |")
lines.append("")

lines.append("## Architecture")
lines.append("")
lines.append("```")
lines.append("wakfu-optimizer/")
lines.append("  app.py                    # Application principale NiceGUI")
lines.append("  config.py                 # Configuration")
lines.append("  MANIFEST.json             # Fichiers proteges (allowed_files)")
lines.append("  PROJECT_MEMORY.md         # Ce fichier")
lines.append("  scripts/                  # Scripts utilitaires")
lines.append("  data/wakfuli/             # Source Wakfuli (API + frontend)")
lines.append("  data/raw/                 # Source CDN Ankama (brut)")
lines.append("  data/extracted/           # Source CDN Ankama (parse)")
lines.append("  data/parsed/              # Source CDN Ankama (transforme)")
lines.append("  engine/                   # Moteur de calcul combat")
lines.append("  logs/                     # Logs de sync et debug")
lines.append("```")
lines.append("")

lines.append("## Historique")
lines.append("")
lines.append("### 2026-03-14")
lines.append("")
lines.append("- Phase 1 : Sync items (7686), actions (68), builds (939) via API Wakfuli")
lines.append("- Phase 2 : Extraction sorts (908/18 classes) via console navigateur")
lines.append("- Correction autopush : ajout lecture allowed_files")
lines.append("- Unification MANIFEST : merge protected + local_only + allowed_files")
lines.append("- Conservation ancien systeme CDN pour verification croisee future")
lines.append("")

lines.append("## TODO")
lines.append("")
lines.append("- [ ] Phase 3 : Construire app.py (builder NiceGUI)")
lines.append("- [ ] Nettoyer scripts legacy (garder seulement les essentiels)")
lines.append("- [ ] Verification croisee Wakfuli vs CDN Ankama")
lines.append("- [ ] Premier push GitHub propre")
lines.append("")

content = "\n".join(lines)
out = PROJECT / "PROJECT_MEMORY.md"
out.write_text(content, "utf-8")
print("PROJECT_MEMORY.md genere (" + str(len(lines)) + " lignes)")
print("Version   : " + version)

if sync_path.exists():
    sr2 = json.loads(sync_path.read_text("utf-8"))
    print("Sync      : " + str(sr2.get("items_received", "?")) + " items, " + str(sr2.get("actions_received", "?")) + " actions, " + str(sr2.get("builds_received", "?")) + " builds")

if spl_path.exists():
    sp2 = json.loads(spl_path.read_text("utf-8"))
    print("Sorts     : " + str(sp2.get("total_spells", "?")) + " sorts / " + str(sp2.get("total_classes", "?")) + " classes")

data_count = len(list(DATA.iterdir())) if DATA.exists() else 0
print("Data      : " + str(data_count) + " fichiers")
print("TERMINE")
