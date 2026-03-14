import json
from datetime import datetime
from pathlib import Path

P = Path(r"H:\Code\Ankama Dev\wakfu-optimizer")
W = P / "data" / "wakfuli"
now = datetime.now().strftime("%Y-%m-%d %H:%M")

# Scan data/wakfuli
files = {}
if W.exists():
    for f in sorted(W.iterdir()):
        if f.is_file():
            files[f.name] = round(f.stat().st_size / 1048576, 2)

# Version
ver = "inconnue"
if (W / "version.json").exists():
    ver = json.loads((W / "version.json").read_text("utf-8")).get("game_version", "inconnue")

# Sorts
sorts = "non installe"
if (W / "spells_report.json").exists():
    sr = json.loads((W / "spells_report.json").read_text("utf-8"))
    sorts = str(sr.get("total_sorts", 0)) + " sorts, " + str(sr.get("classes", 0)) + " classes"

# Sync
sync = "non execute"
if (W / "sync_report.json").exists():
    r = json.loads((W / "sync_report.json").read_text("utf-8"))
    d = r.get("datasets", {})
    sync = str(d.get("items",{}).get("total_received",0)) + " items, "
    sync += str(d.get("actions",{}).get("total_received",0)) + " actions, "
    sync += str(d.get("builds",{}).get("total_received",0)) + " builds"

# Scripts
scripts = []
sd = P / "scripts"
if sd.exists():
    for f in sorted(sd.iterdir()):
        if f.suffix == ".py":
            scripts.append(f.name)

# Fichiers racine
root = []
for f in sorted(P.iterdir()):
    if f.is_file():
        root.append(f.name)

# Construction du fichier
lines = []
lines.append("# PROJECT MEMORY - Wakfu Optimizer")
lines.append("")
lines.append("> Derniere mise a jour : " + now)
lines.append("> Ce fichier est la memoire persistante du projet.")
lines.append("> Il DOIT etre lu en debut de chaque session.")
lines.append("> Il DOIT etre mis a jour a la fin de chaque session.")
lines.append("")
lines.append("## Regles absolues")
lines.append("")
lines.append("1. JAMAIS de fichier cree manuellement - Tout passe par un script PowerShell (here-string)")
lines.append("2. MANIFEST.json mis a jour AVANT de creer un fichier - Sinon autopush le supprime")
lines.append("3. Pas de placeholder - L utilisateur ne code pas, tout doit etre fonctionnel")
lines.append("4. Pas de profil hardcode - Le builder est universel (toutes classes, tous niveaux)")
lines.append("5. Sources citees - Toute donnee vient d une source verifiable")
lines.append("6. Gros JSON dans .gitignore - all_items, all_builds, all_spells, all_actions sont regenerables")
lines.append("7. Fichiers legers commites - Scripts, rapports, config, MANIFEST, PROJECT_MEMORY.md")
lines.append("")
lines.append("## Etat des donnees (version " + ver + ")")
lines.append("")
lines.append("| Fichier | Taille | Source |")
lines.append("|---------|--------|--------|")
for name, mb in files.items():
    src = "frontend Wakfuli" if name == "all_spells.json" else "api.wakfuli.com"
    lines.append("| " + name + " | " + str(mb) + " MB | " + src + " |")
lines.append("")
lines.append("### Sync : " + sync)
lines.append("### Sorts : " + sorts)
lines.append("")
lines.append("## API Wakfuli - Endpoints")
lines.append("")
lines.append("| Endpoint | Status | Notes |")
lines.append("|----------|--------|-------|")
lines.append("| /items | OK sans auth | page, limit, levelMin, levelMax, itemType, rarity, search |")
lines.append("| /actions | OK sans auth | 68 total, 1 page |")
lines.append("| /builds | OK sans auth | 939 publics, contient spell IDs |")
lines.append("| /items/hidden | Auth requise | Token personnel |")
lines.append("| /spells | N EXISTE PAS | Donnees dans frontend JS uniquement |")
lines.append("| /breeds | N EXISTE PAS | - |")
lines.append("")
lines.append("## CDN Ankama")
lines.append("")
lines.append("- Config : https://wakfu.cdn.ankama.com/gamedata/config.json")
lines.append("- Actions : https://wakfu.cdn.ankama.com/gamedata/{version}/actions.json")
lines.append("- States : https://wakfu.cdn.ankama.com/gamedata/{version}/states.json")
lines.append("- Items : https://wakfu.cdn.ankama.com/gamedata/{version}/items.json")
lines.append("- PAS de spells.json sur le CDN")
lines.append("")
lines.append("## Scripts")
lines.append("")
for s in scripts:
    lines.append("- scripts/" + s)
lines.append("")
lines.append("## Fichiers racine")
lines.append("")
for f in root:
    lines.append("- " + f)
lines.append("")
lines.append("## Architecture cible")
lines.append("")
lines.append("```")
lines.append("wakfu-optimizer/")
lines.append("  PROJECT_MEMORY.md      <- CE FICHIER")
lines.append("  MANIFEST.json          <- Fichiers proteges")
lines.append("  .gitignore             <- Exclut gros JSON")
lines.append("  README.md              <- Doc publique")
lines.append("  config.py              <- Constantes du jeu")
lines.append("  app.py                 <- Application NiceGUI")
lines.append("  scripts/")
lines.append("    sync_wakfuli.py      <- DL items + actions + builds")
lines.append("    install_spells.py    <- Installe sorts extraits")
lines.append("    autopush.py          <- Git auto-commit + clean")
lines.append("  data/wakfuli/")
lines.append("    version.json         <- Version jeu (commitee)")
lines.append("    sync_report.json     <- Rapport sync (commite)")
lines.append("    spells_report.json   <- Rapport sorts (commite)")
lines.append("    spell_index.json     <- Index IDs (commite)")
lines.append("    all_items.json       <- 7686 items (gitignore)")
lines.append("    all_actions.json     <- 68 actions (gitignore)")
lines.append("    all_builds.json      <- 939 builds (gitignore)")
lines.append("    all_spells.json      <- 908 sorts (gitignore)")
lines.append("```")
lines.append("")
lines.append("## Historique des sessions")
lines.append("")
lines.append("### Session " + now)
lines.append("- Decouvert API Wakfuli (api.wakfuli.com/api/v1/)")
lines.append("- Cree sync_wakfuli.py : 7686 items, 68 actions, 939 builds")
lines.append("- Extrait 908 sorts (18 classes) via window.__SPELL_CACHE__")
lines.append("- Cree install_spells.py")
lines.append("- Lecon : PowerShell here-string obligatoire, MANIFEST avant tout fichier")
lines.append("")
lines.append("## TODO")
lines.append("")
lines.append("- [ ] .gitignore propre")
lines.append("- [ ] README.md")
lines.append("- [ ] Premier push GitHub propre")
lines.append("- [ ] Phase 3 : app.py builder universel")
lines.append("- [ ] Telecharger states.json depuis CDN Ankama")
lines.append("- [ ] UI style Wakfuli")

(P / "PROJECT_MEMORY.md").write_text("\n".join(lines), "utf-8")
print("PROJECT_MEMORY.md cree (" + str(len(lines)) + " lignes)")
print("Version : " + ver)
print("Sync    : " + sync)
print("Sorts   : " + sorts)
print("Scripts : " + ", ".join(scripts))
print("Data    : " + str(len(files)) + " fichiers")
