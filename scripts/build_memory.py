"""
build_memory.py v3 - Generateur automatique de memoire projet
Genere PROJECT_MEMORY.md et BRIEFING.md depuis l'etat reel du repo.
Usage : python scripts/build_memory.py
"""

import json, os, subprocess, re
from pathlib import Path
from datetime import datetime

PROJECT = Path(r"H:\Code\Ankama Dev\wakfu-optimizer")
FRONTEND = PROJECT / "frontend"
DATA = PROJECT / "data" / "wakfuli"
ICONS_STATS = FRONTEND / "public" / "icons" / "stats"
ICONS_BONUSES = FRONTEND / "public" / "icons" / "bonuses"
COMPONENTS = FRONTEND / "src" / "components" / "builder"
LIB = FRONTEND / "src" / "lib"

NOW = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def file_size_str(path):
    if not path.exists():
        return "ABSENT"
    size = path.stat().st_size
    if size > 1024 * 1024:
        return f"{size / (1024*1024):.2f} MB"
    elif size > 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size} B"


def count_files(directory, pattern="*"):
    if not directory.exists():
        return 0
    return len(list(directory.glob(pattern)))


def get_recent_commits(n=5):
    try:
        r = subprocess.run(
            ["git", "log", "--oneline", f"-{n}"],
            capture_output=True, text=True, cwd=str(PROJECT)
        )
        return r.stdout.strip().splitlines() if r.returncode == 0 else []
    except Exception:
        return []


def get_package_version(package_name):
    pkg = FRONTEND / "package.json"
    if not pkg.exists():
        return "?"
    try:
        data = json.loads(pkg.read_text("utf-8"))
        deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
        ver = deps.get(package_name, "?")
        return ver.lstrip("^~")
    except Exception:
        return "?"


def count_lines(filepath):
    if not filepath.exists():
        return 0
    try:
        return len(filepath.read_text("utf-8").splitlines())
    except Exception:
        return 0


def detect_todos_from_code():
    todos = []
    if not FRONTEND.exists():
        return todos
    for ext in ["*.tsx", "*.ts"]:
        for f in FRONTEND.rglob(ext):
            if "node_modules" in str(f):
                continue
            try:
                for i, line in enumerate(f.read_text("utf-8").splitlines(), 1):
                    if "TODO" in line or "FIXME" in line or "HACK" in line:
                        clean = line.strip().lstrip("/ ").strip()
                        rel = str(f.relative_to(PROJECT)).replace("\\", "/")
                        todos.append(f"{rel}:{i} - {clean}")
            except Exception:
                continue
    return todos


def get_component_info():
    components = {}
    if not COMPONENTS.exists():
        return components
    for f in sorted(COMPONENTS.glob("*.tsx")):
        name = f.name
        lines = count_lines(f)
        version = ""
        try:
            head = f.read_text("utf-8")[:500]
            m = re.search(r"v(\d+)", head)
            if m:
                version = f" v{m.group(1)}"
        except Exception:
            pass
        components[name] = {"lines": lines, "version": version}
    return components


def get_data_stats():
    stats = {}
    data_files = {
        "all_items.json": "Items (API Wakfuli)",
        "all_actions.json": "Actions/effets",
        "all_builds.json": "Builds publics",
        "all_spells.json": "Sorts (console navigateur)",
        "version.json": "Version du jeu",
        "sync_report.json": "Rapport de sync",
        "spells_report.json": "Rapport des sorts",
    }
    for fname, desc in data_files.items():
        fp = DATA / fname
        if fp.exists():
            size = file_size_str(fp)
            count = ""
            try:
                d = json.loads(fp.read_text("utf-8"))
                if isinstance(d, list):
                    count = f" ({len(d)} entrees)"
            except Exception:
                pass
            stats[fname] = {"desc": desc, "size": size, "count": count, "status": "OK"}
        else:
            stats[fname] = {"desc": desc, "size": "-", "count": "", "status": "ABSENT"}
    return stats


# ============================================================
# GENERATION DE PROJECT_MEMORY.md
# ============================================================

def generate_project_memory():
    L = []
    L.append("# PROJECT MEMORY - wakfu-optimizer")
    L.append(f"> Derniere mise a jour : {NOW}")
    L.append("> CERVEAU du projet - A LIRE EN PREMIER par toute IA")
    L.append("")
    L.append("## REGLES")
    L.append("1. LIRE CE FICHIER EN ENTIER avant toute modification")
    L.append("2. Lire le code sur GitHub (raw files) avant de proposer du code")
    L.append("3. Donner des blocs PowerShell complets, SANS placeholder")
    L.append("4. autopush.py synchronise local -> GitHub toutes les 5 secondes")
    L.append("5. Mettre a jour CE FICHIER a chaque etape significative")
    L.append("6. Verifier les URLs CDN avant de les utiliser")
    L.append("")
    L.append("## FIN DE SESSION - OBLIGATOIRE")
    L.append("1. Executer : python scripts/session_end.py")
    L.append("2. Ou utiliser le bouton Fin de Session dans l'extension Chrome")
    L.append("3. Ce fichier = cerveau. Info absente ici = perdue.")
    L.append("")
    L.append("## LIENS RAPIDES")
    L.append("- Repo : https://github.com/Duperopope/wakfu-optimizer")
    L.append("- Raw : https://raw.githubusercontent.com/Duperopope/wakfu-optimizer/main/{path}")
    L.append("- ARCHITECTURE.md | CHANGELOG.md | BRIEFING.md | SESSION_HANDOFF.md")
    L.append("")

    next_ver = get_package_version("next")
    react_ver = get_package_version("react")
    tw_ver = get_package_version("tailwindcss")
    L.append("## STACK (auto-detecte)")
    L.append(f"- Frontend : Next.js {next_ver} / React {react_ver} / Tailwind CSS {tw_ver} / TypeScript 5")
    L.append("- OS : Windows / PowerShell / VS Code")
    L.append("- Serveur dev : npm run dev (port 3000 ou 8090)")
    L.append("- Dev Server : python scripts/dev_server.py (port 8091)")
    L.append("")

    comps = get_component_info()
    L.append("## COMPOSANTS BUILDER (auto-detecte)")
    for name, info in comps.items():
        L.append(f"- {name}{info['version']} : {info['lines']} lignes")
    lib_files = sorted(list(LIB.glob("*.ts")) + list(LIB.glob("*.tsx"))) if LIB.exists() else []
    for f in lib_files:
        L.append(f"- lib/{f.name} : {count_lines(f)} lignes")
    L.append("")

    n_stats = count_files(ICONS_STATS, "*.webp")
    n_bonuses = count_files(ICONS_BONUSES, "*.png")
    L.append("## ASSETS (auto-detecte)")
    L.append(f"- icons/stats/ : {n_stats} icones .webp")
    L.append(f"- icons/bonuses/ : {n_bonuses} icones .png")
    L.append("")

    data_stats = get_data_stats()
    L.append("## DONNEES WAKFULI (auto-detecte)")
    for fname, info in data_stats.items():
        L.append(f"- {fname} : {info['size']}{info['count']} [{info['status']}]")
    L.append("")

    ver_path = DATA / "version.json"
    if ver_path.exists():
        try:
            ver = json.loads(ver_path.read_text("utf-8")).get("version", "?")
            L.append(f"## VERSION JEU : {ver}")
            L.append("")
        except Exception:
            pass

    L.append("## CE QUI MARCHE")
    L.append("- Selection classe, level, nom du build")
    L.append("- 7686 items avec images + filtres + equip/unequip + modal anneau")
    L.append("- Stats recalculees dynamiquement (computeStats)")
    L.append("- 3 bonus toggle (Guilde/Havre-Monde/Monture) icones custom")
    L.append("- Barre priorite elementaire draggable")
    L.append("- Enchantements toggle + onglet runes")
    L.append("- Boutons Copier/Lien/Visibilite/Favori")
    L.append("- Couleurs rarete correctes")
    L.append("- Extension Chrome Wakfu Dev Assistant v2.1")
    L.append("- Dev Server local (localhost:8091)")
    L.append("- Pipeline : Genspark -> Extension -> Dev Server -> PowerShell -> Resultat")
    L.append("")

    L.append("## TODO (priorite)")
    L.append("- [ ] Redesign LeftPanel bonus pour matcher Wakfuli")
    L.append("- [ ] Connecter priorite elementaire a computeStats")
    L.append("- [ ] Localiser icones classes (cdn -> local)")
    L.append("- [ ] Refaire gem.png en 64x64+")
    L.append("- [ ] Onglet Sorts (all_spells.json dispo)")
    L.append("- [ ] Enchantements dans BuildContext")
    L.append("- [ ] Onglets Aptitudes / Notes")
    L.append("- [ ] Sauvegarde builds localStorage")
    L.append("")

    code_todos = detect_todos_from_code()
    if code_todos:
        L.append("## TODO DETECTES DANS LE CODE")
        for t in code_todos[:10]:
            L.append(f"- {t}")
        L.append("")

    L.append("## CDN WAKFULI")
    L.append("- Stats : cdn.wakfuli.com/stats/{STAT_KEY}.webp")
    L.append("- Classes : cdn.wakfuli.com/breeds/{class}.webp")
    L.append("- Items : cdn.wakfuli.com/items/{image_id}.webp")
    L.append("- Raretes : cdn.wakfuli.com/rarity/{RARITY}.webp")
    L.append("")

    commits = get_recent_commits(5)
    if commits:
        L.append("## COMMITS RECENTS")
        for c in commits:
            L.append(f"- {c}")
        L.append("")

    L.append("## FICHIERS ACTIFS")
    L.append("- frontend/src/components/builder/LeftPanel.tsx")
    L.append("- frontend/src/components/builder/RightPanel.tsx")
    L.append("- frontend/src/components/builder/BuilderLayout.tsx")
    L.append("- frontend/src/components/builder/ClassSelector.tsx")
    L.append("- frontend/src/lib/BuildContext.tsx")
    L.append("- frontend/public/icons/")
    L.append("")

    return "\n".join(L)


# ============================================================
# GENERATION DE BRIEFING.md
# ============================================================

def generate_briefing():
    next_ver = get_package_version("next")
    react_ver = get_package_version("react")
    tw_ver = get_package_version("tailwindcss")
    n_stats = count_files(ICONS_STATS, "*.webp")
    n_bonuses = count_files(ICONS_BONUSES, "*.png")
    comps = get_component_info()
    data_stats = get_data_stats()
    commits = get_recent_commits(3)
    code_todos = detect_todos_from_code()

    L = []
    L.append("# BRIEFING - wakfu-optimizer")
    L.append(f"> Auto-genere le {NOW} par build_memory.py v3")
    L.append("> INJECTE AUTOMATIQUEMENT PAR L'EXTENSION CHROME WAKFU DEV ASSISTANT")
    L.append("")
    L.append("---")
    L.append("")
    L.append("## QUI EST L'UTILISATEUR")
    L.append("Sam est un Product Owner no-code. Il ne code PAS lui-meme.")
    L.append("L'IA fournit des blocs PowerShell complets copiables-collables.")
    L.append("JAMAIS de placeholder, JAMAIS de 'remplace par ton code'.")
    L.append("")
    L.append("## REGLES ABSOLUES")
    L.append("1. Lire le code sur GitHub AVANT de coder : https://raw.githubusercontent.com/Duperopope/wakfu-optimizer/main/{path}")
    L.append("2. Blocs PowerShell complets et fonctionnels")
    L.append("3. ZERO placeholder")
    L.append("4. Travailler bout par bout (un fichier a la fois)")
    L.append("5. Ne JAMAIS modifier un fichier non lu")
    L.append("6. autopush.py sync vers GitHub toutes les 5s")
    L.append("7. MAJ PROJECT_MEMORY.md et CHANGELOG.md a chaque etape")
    L.append("8. Verifier les URLs CDN avant utilisation")
    L.append("9. Fin de session : bouton dans l'extension ou python scripts/session_end.py")
    L.append("")
    L.append("## LE PROJET")
    L.append("Optimiseur de builds pour Wakfu (MMORPG), inspire de Wakfuli (https://wakfuli.com).")
    L.append("Creer des builds : classe, level, items, stats en temps reel.")
    L.append("")
    L.append(f"## STACK (auto-detecte)")
    L.append(f"- Next.js {next_ver} / React {react_ver} / Tailwind {tw_ver} / TypeScript 5")
    L.append("- Windows 11 / PowerShell / VS Code")
    L.append("- npm run dev (port 3000 ou 8090)")
    L.append("- Repo : https://github.com/Duperopope/wakfu-optimizer")
    L.append("- autopush.py (sync 5s) + dev_server.py (localhost:8091)")
    L.append("")
    L.append("## COMPOSANTS (auto-detecte)")
    for name, info in comps.items():
        L.append(f"- {name}{info['version']} ({info['lines']} lignes)")
    L.append("- BuildContext.tsx : useBuild(), computeStats(), BASE_STATS (HP=50,AP=6,MP=3,WP=6,FEROCITY=3)")
    L.append("- useWakfuData.ts : chargement JSON")
    L.append("- wakfu.ts : types et constantes")
    L.append("")
    L.append(f"## ASSETS : {n_stats} icones stats .webp, {n_bonuses} icones bonus .png")
    L.append("")
    L.append("## FONCTIONNE")
    L.append("- Classe + level + nom du build")
    L.append("- 7686 items avec images, filtres, equip/unequip")
    L.append("- Stats dynamiques via computeStats")
    L.append("- 3 bonus toggles (Guilde/Havre-Monde/Monture)")
    L.append("- Priorite elementaire draggable")
    L.append("- Enchantements toggle + runes")
    L.append("- Copier/Lien/Visibilite/Favori")
    L.append("- Pipeline automatise : Genspark -> Extension Chrome -> Dev Server -> PowerShell")
    L.append("")
    L.append("## TODO")
    L.append("1. Redesign LeftPanel bonus (matcher Wakfuli)")
    L.append("2. Connecter priorite elementaire a computeStats")
    L.append("3. Localiser icones classes")
    L.append("4. Refaire gem.png 64x64+")
    L.append("5. Onglet Sorts")
    L.append("6. Enchantements dans BuildContext")
    L.append("7. Onglets Aptitudes / Notes")
    L.append("8. Sauvegarde localStorage")
    L.append("")
    L.append("## PROBLEMES CONNUS")
    L.append("- gem.png pixelise (37x39px)")
    L.append("- Icones classes depuis CDN distant")
    L.append("- Priorite elementaire non connectee")
    L.append("- Enchantements pas dans BuildContext")
    L.append("")

    if code_todos:
        L.append("## TODO DANS LE CODE")
        for t in code_todos[:5]:
            L.append(f"- {t}")
        L.append("")

    L.append("## CDN : cdn.wakfuli.com/stats|breeds|items|rarity/{KEY}.webp")
    L.append("")

    if commits:
        L.append("## COMMITS RECENTS")
        for c in commits:
            L.append(f"- {c}")
        L.append("")

    L.append("## SCRIPTS : autopush.py, build_memory.py, session_end.py, dev_server.py, sync_wakfuli.py")
    L.append("## DOCS : PROJECT_MEMORY.md, ARCHITECTURE.md, CHANGELOG.md, SESSION_HANDOFF.md")
    L.append("")
    L.append("## FORMAT REPONSE")
    L.append("1. Explication claire")
    L.append("2. Bloc PowerShell complet")
    L.append("3. Ce qui a change et pourquoi")

    return "\n".join(L)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print(f"build_memory.py v3 - {NOW}")
    print("=" * 50)

    pm_content = generate_project_memory()
    pm_path = PROJECT / "PROJECT_MEMORY.md"
    pm_path.write_text(pm_content, "utf-8")
    pm_lines = len(pm_content.splitlines())
    print(f"PROJECT_MEMORY.md : {pm_lines} lignes")

    br_content = generate_briefing()
    br_path = PROJECT / "BRIEFING.md"
    br_path.write_text(br_content, "utf-8")
    br_lines = len(br_content.splitlines())
    print(f"BRIEFING.md       : {br_lines} lignes")

    print()
    print(f"Composants : {len(get_component_info())}")
    print(f"Icones     : {count_files(ICONS_STATS, '*.webp')} stats + {count_files(ICONS_BONUSES, '*.png')} bonus")
    print(f"TODOs code : {len(detect_todos_from_code())}")
    print(f"Commits    : {len(get_recent_commits(5))}")
    print()
    print("TERMINE - autopush.py va pousser les fichiers.")
