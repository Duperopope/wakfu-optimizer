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

# ============================================================
# UTILITAIRES
# ============================================================

def file_size_str(path):
    """Retourne la taille lisible d'un fichier."""
    if not path.exists():
        return "ABSENT"
    size = path.stat().st_size
    if size > 1024 * 1024:
        return f"{size / (1024*1024):.2f} MB"
    elif size > 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size} B"

def count_files(directory, pattern="*"):
    """Compte les fichiers dans un dossier."""
    if not directory.exists():
        return 0
    return len(list(directory.glob(pattern)))

def get_recent_commits(n=5):
    """Recupere les N derniers commits."""
    try:
        r = subprocess.run(
            ["git", "log", f"--oneline", f"-{n}"],
            capture_output=True, text=True, cwd=PROJECT
        )
        return r.stdout.strip().splitlines() if r.returncode == 0 else []
    except Exception:
        return []

def get_package_version(package_name):
    """Lit la version d'un package depuis package.json."""
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
    """Compte les lignes d'un fichier."""
    if not filepath.exists():
        return 0
    try:
        return len(filepath.read_text("utf-8").splitlines())
    except Exception:
        return 0

def detect_todos_from_code():
    """Scanne les fichiers TSX/TS pour trouver les TODO dans les commentaires."""
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

def get_data_stats():
    """Recupere les stats des fichiers de donnees Wakfuli."""
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
            # Compter les entrees pour les gros fichiers
            count = ""
            try:
                d = json.loads(fp.read_text("utf-8"))
                if isinstance(d, list):
                    count = f" ({len(d)} entrees)"
                elif isinstance(d, dict) and "items" in str(fname):
                    count = f" ({len(d)} entrees)"
            except Exception:
                pass
            stats[fname] = {"desc": desc, "size": size, "count": count, "status": "OK"}
        else:
            stats[fname] = {"desc": desc, "size": "-", "count": "", "status": "ABSENT"}
    return stats

def get_component_info():
    """Analyse les composants builder."""
    components = {}
    if not COMPONENTS.exists():
        return components
    for f in sorted(COMPONENTS.glob("*.tsx")):
        name = f.name
        lines = count_lines(f)
        # Detecter la version dans les commentaires
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

# ============================================================
# GENERATION DE PROJECT_MEMORY.md
# ============================================================

def generate_project_memory():
    """Genere le fichier PROJECT_MEMORY.md compact (<150 lignes)."""
    L = []
    L.append("# PROJECT MEMORY - wakfu-optimizer")
    L.append(f"> Derniere mise a jour : {NOW}")
    L.append("> CERVEAU du projet - A LIRE EN PREMIER par toute IA")
    L.append("")

    # Regles
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
    L.append("2. Ou mettre a jour manuellement PROJECT_MEMORY.md + CHANGELOG.md")
    L.append("3. Ce fichier = cerveau. Info absente ici = perdue.")
    L.append("")

    # Liens
    L.append("## LIENS RAPIDES")
    L.append("- Repo : https://github.com/Duperopope/wakfu-optimizer")
    L.append("- Raw : https://raw.githubusercontent.com/Duperopope/wakfu-optimizer/main/{path}")
    L.append("- Commits : https://api.github.com/repos/Duperopope/wakfu-optimizer/commits?per_page=5")
    L.append("- ARCHITECTURE.md | CHANGELOG.md | BRIEFING.md | SESSION_HANDOFF.md")
    L.append("")

    # Stack (detecte automatiquement)
    next_ver = get_package_version("next")
    react_ver = get_package_version("react")
    tw_ver = get_package_version("tailwindcss")
    L.append("## STACK (auto-detecte)")
    L.append(f"- Frontend : Next.js {next_ver} / React {react_ver} / Tailwind CSS {tw_ver} / TypeScript 5")
    L.append("- OS : Windows / PowerShell / VS Code")
    L.append("- Serveur dev : npm run dev (port 3000 ou 8090)")
    L.append("")

    # Composants
    comps = get_component_info()
    L.append("## COMPOSANTS BUILDER (auto-detecte)")
    for name, info in comps.items():
        L.append(f"- {name}{info['version']} : {info['lines']} lignes")
    lib_files = list(LIB.glob("*.ts")) + list(LIB.glob("*.tsx")) if LIB.exists() else []
    for f in sorted(lib_files):
        L.append(f"- lib/{f.name} : {count_lines(f)} lignes")
    L.append("")

    # Assets
    n_stats = count_files(ICONS_STATS, "*.webp")
    n_bonuses = count_files(ICONS_BONUSES, "*.png")
    L.append("## ASSETS (auto-detecte)")
    L.append(f"- icons/stats/ : {n_stats} icones .webp")
    L.append(f"- icons/bonuses/ : {n_bonuses} icones .png")
    L.append("")

    # Donnees
    data_stats = get_data_stats()
    L.append("## DONNEES WAKFULI (auto-detecte)")
    for fname, info in data_stats.items():
        L.append(f"- {fname} : {info['size']}{info['count']} [{info['status']}]")
    L.append("")

    # Sync report
    sync_path = DATA / "sync_report.json"
    if sync_path.exists():
        try:
            sr = json.loads(sync_path.read_text("utf-8"))
            L.append(f"## DERNIERE SYNC : {sr.get('date', '?')}")
            L.append(f"- {sr.get('items_received', '?')} items, {sr.get('actions_received', '?')} actions, {sr.get('builds_received', '?')} builds")
            L.append("")
        except Exception:
            pass

    # Version jeu
    ver_path = DATA / "version.json"
    if ver_path.exists():
        try:
            ver = json.loads(ver_path.read_text("utf-8")).get("version", "?")
            L.append(f"## VERSION JEU : {ver}")
            L.append("")
        except Exception:
            pass

    # CE QUI MARCHE
    L.append("## CE QUI MARCHE")
    L.append("- Selection classe, level, nom du build")
    L.append("- 7686 items avec images + filtres + equip/unequip + modal anneau")
    L.append("- Stats recalculees dynamiquement (computeStats)")
    L.append("- 3 bonus toggle (Guilde/Havre-Monde/Monture) icones custom")
    L.append("- Barre priorite elementaire draggable")
    L.append("- Enchantements toggle + onglet runes")
    L.append("- Boutons Copier/Lien/Visibilite/Favori")
    L.append("- Couleurs rarete correctes")
    L.append("")

    # TODO (detecte depuis le code + liste manuelle)
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

    # TODOs detectes dans le code
    code_todos = detect_todos_from_code()
    if code_todos:
        L.append("## TODO DETECTES DANS LE CODE")
        for t in code_todos[:10]:
            L.append(f"- {t}")
        if len(code_todos) > 10:
            L.append(f"- ... et {len(code_todos) - 10} autres")
        L.append("")

    # CDN
    L.append("## CDN WAKFULI")
    L.append("- Stats : cdn.wakfuli.com/stats/{STAT_KEY}.webp")
    L.append("- Classes : cdn.wakfuli.com/breeds/{class}.webp")
    L.append("- Items : cdn.wakfuli.com/items/{image_id}.webp")
    L.append("- Raretes : cdn.wakfuli.com/rarity/{RARITY}.webp")
    L.append("")

    # Commits recents
    commits = get_recent_commits(5)
    if commits:
        L.append("## COMMITS RECENTS")
        for c in commits:
            L.append(f"- {c}")
        L.append("")

    # Fichiers actifs
    L.append("## FICHIERS ACTIFS")
    L.append("- frontend/src/components/builder/LeftPanel.tsx (dernier modifie)")
    L.append("- frontend/src/components/builder/RightPanel.tsx")
    L.append("- frontend/src/components/builder/BuilderLayout.tsx")
    L.append("- frontend/src/components/builder/ClassSelector.tsx")
    L.append("- frontend/src/lib/BuildContext.tsx")
    L.append("- frontend/public/icons/ (stats/*.webp + bonuses/*.png)")
    L.append("")

    return "\n".join(L)


# ============================================================
# GENERATION DE BRIEFING.md
# ============================================================

def generate_briefing():
    """Genere le BRIEFING.md pour l'extension Chrome."""
    # Stack auto-detecte
    next_ver = get_package_version("next")
    react_ver = get_package_version("react")
    tw_ver = get_package_version("tailwindcss")

    # Assets auto-detectes
    n_stats = count_files(ICONS_STATS, "*.webp")
    n_bonuses = count_files(ICONS_BONUSES, "*.png")

    # Composants
    comps = get_component_info()
    comp_lines = []
    for name, info in comps.items():
        comp_lines.append(f"- **{name}**{info['version']} ({info['lines']} lignes)")

    # Donnees
    data_stats = get_data_stats()
    data_summary = []
    for fname, info in data_stats.items():
        if info["status"] == "OK":
            data_summary.append(f"{fname}: {info['size']}{info['count']}")

    # Commits
    commits = get_recent_commits(3)
    commits_str = "\n".join([f"- {c}" for c in commits]) if commits else "- Aucun commit recent"

    # Code TODOs
    code_todos = detect_todos_from_code()
    code_todos_str = ""
    if code_todos:
        code_todos_str = "\n## TODO DETECTES DANS LE CODE\n"
        for t in code_todos[:8]:
            code_todos_str += f"- {t}\n"

    L = []
    L.append("# BRIEFING - wakfu-optimizer")
    L.append(f"> Auto-genere le {NOW} par build_memory.py v3")
    L.append("> CE FICHIER EST INJECTE AUTOMATIQUEMENT EN DEBUT DE SESSION PAR L'EXTENSION CHROME")
    L.append("> Il resume TOUT ce qu'une IA doit savoir pour travailler sur ce projet")
    L.append("")
    L.append("---")
    L.append("")
    L.append("## QUI EST L'UTILISATEUR")
    L.append("Sam est un Product Owner no-code. Il ne code PAS lui-meme. L'IA doit fournir des blocs PowerShell complets copiables-collables, JAMAIS de placeholder, JAMAIS de \"remplace par ton code\". Sam coordonne, l'IA execute.")
    L.append("")
    L.append("## REGLES ABSOLUES")
    L.append("1. Lire le code source sur GitHub AVANT de proposer du code : https://raw.githubusercontent.com/Duperopope/wakfu-optimizer/main/{path}")
    L.append("2. Donner des blocs PowerShell complets et fonctionnels")
    L.append("3. ZERO placeholder - tout le code doit etre fonctionnel tel quel")
    L.append("4. Travailler bout par bout (petit scope, un fichier a la fois)")
    L.append("5. Ne JAMAIS modifier un fichier qu'on n'a pas lu d'abord")
    L.append("6. autopush.py tourne en fond et synchronise vers GitHub toutes les 5s")
    L.append("7. Mettre a jour PROJECT_MEMORY.md et CHANGELOG.md a chaque etape importante")
    L.append("8. Verifier les URLs CDN avant de les utiliser dans le code")
    L.append("9. En fin de session : executer python scripts/session_end.py")
    L.append("")
    L.append("## LE PROJET")
    L.append("Un optimiseur de builds pour le MMORPG Wakfu, inspire du site Wakfuli (https://wakfuli.com).")
    L.append("L'application permet de creer des builds : choisir une classe, un level, equiper des items, voir les stats calculees en temps reel.")
    L.append("")
    L.append("## STACK TECHNIQUE (auto-detecte)")
    L.append(f"- **Framework** : Next.js {next_ver} / React {react_ver} / TypeScript 5")
    L.append(f"- **CSS** : Tailwind CSS {tw_ver}")
    L.append("- **OS** : Windows 11 / PowerShell / VS Code")
    L.append("- **Serveur dev** : npm run dev (port 3000 ou 8090)")
    L.append("- **Repo** : https://github.com/Duperopope/wakfu-optimizer")
    L.append("- **Sync** : autopush.py (git add/commit/push toutes les 5s)")
    L.append("")
    L.append("## COMPOSANTS BUILDER (auto-detecte)")
    for line in comp_lines:
        L.append(line)
    L.append("")
    L.append("### Contexte et logique (frontend/src/lib/)")
    L.append("- **BuildContext.tsx** : etat global du build via React Context + useBuild() hook")
    L.append("  - computeStats() : calcule les stats a partir des items equipes")
    L.append("  - BASE_STATS : HP=50, AP=6, MP=3, WP=6, FEROCITY=3")
    L.append("  - baseHpForLevel(level) = 50 + level*10")
    L.append("  - Expose : build, stats, setName, setClass, setLevel, equipItem, unequipItem, pendingRingItem")
    L.append("- **useWakfuData.ts** : hook de chargement des JSON")
    L.append("- **wakfu.ts** : types TypeScript et constantes (CLASSES, etc.)")
    L.append("")
    L.append(f"### Assets (auto-detecte)")
    L.append(f"- icons/stats/ : {n_stats} icones .webp")
    L.append(f"- icons/bonuses/ : {n_bonuses} icones .png (tree.png, gem.png, mount.png)")
    L.append("- data/*.json : copies locales des donnees Wakfuli")
    L.append("")
    L.append("## CE QUI FONCTIONNE ACTUELLEMENT")
    L.append("- Selection classe + level + nom du build")
    L.append("- 7686 items avec images, filtres, equip/unequip, modal double anneau")
    L.append("- Stats recalculees dynamiquement via computeStats")
    L.append("- 3 bonus toggles (Guilde/Havre-Monde/Monture) avec icones PNG custom")
    L.append("- Barre de priorite elementaire draggable (Feu/Eau/Terre/Air)")
    L.append("- Toggle enchantements + onglet runes")
    L.append("- Boutons : Copier JSON, Lien partageable base64, Visibilite, Favori localStorage")
    L.append("- Couleurs de rarete correctes")
    L.append("")
    L.append("## DONNEES (auto-detecte)")
    for d in data_summary:
        L.append(f"- {d}")
    L.append("")
    L.append("## CDN WAKFULI")
    L.append("- Stats : https://cdn.wakfuli.com/stats/{STAT_KEY}.webp")
    L.append("- Classes : https://cdn.wakfuli.com/breeds/{class}.webp")
    L.append("- Items : https://cdn.wakfuli.com/items/{image_id}.webp")
    L.append("- Raretes : https://cdn.wakfuli.com/rarity/{RARITY}.webp")
    L.append("")
    L.append("## TODO (par priorite)")
    L.append("1. Redesign LeftPanel section bonus pour matcher le style Wakfuli")
    L.append("2. Connecter priorite elementaire a computeStats (impact tri items)")
    L.append("3. Localiser icones classes (CDN distant -> fichiers locaux)")
    L.append("4. Refaire gem.png en 64x64+ (actuellement 37x39px, pixelise)")
    L.append("5. Onglet Sorts (all_spells.json disponible dans data/wakfuli/)")
    L.append("6. Integrer enchantements dans BuildContext")
    L.append("7. Onglets Aptitudes et Notes")
    L.append("8. Sauvegarde builds dans localStorage")
    L.append("")
    L.append("## PROBLEMES CONNUS")
    L.append("- gem.png pixelise (37x39px), compense par iconScale 2.0")
    L.append("- Icones de classes chargees depuis CDN distant (pas local)")
    L.append("- Priorite elementaire non connectee a computeStats")
    L.append("- Enchantements pas encore dans BuildContext")
    L.append("")
    if code_todos_str:
        L.append(code_todos_str)
    L.append("## COMMITS RECENTS")
    L.append(commits_str)
    L.append("")
    L.append("## SCRIPTS ACTIFS")
    L.append("- **autopush.py** : sync git toutes les 5s, nettoie fichiers hors MANIFEST.json")
    L.append("- **build_memory.py** : regenere PROJECT_MEMORY.md + BRIEFING.md (CE SCRIPT)")
    L.append("- **session_end.py** : fin de session (CHANGELOG + SESSION_HANDOFF + build_memory)")
    L.append("- **sync_wakfuli.py** : telecharge items/builds/spells depuis l'API Wakfuli")
    L.append("- **install_spells.py** : installe les donnees de sorts")
    L.append("")
    L.append("## DOCUMENTATION")
    L.append("- **PROJECT_MEMORY.md** : cerveau du projet (etat actuel, todo, regles)")
    L.append("- **ARCHITECTURE.md** : inventaire detaille de tous les dossiers et fichiers")
    L.append("- **CHANGELOG.md** : historique chronologique de toutes les sessions")
    L.append("- **SESSION_HANDOFF.md** : contexte de la derniere session (si existe)")
    L.append("")
    L.append("## FORMAT DE REPONSE ATTENDU")
    L.append("L'IA doit toujours repondre avec :")
    L.append("1. Ce qu'elle va faire (explication claire)")
    L.append("2. Le bloc PowerShell complet a copier-coller")
    L.append("3. Ce qui a change et pourquoi")
    L.append("4. La mise a jour de PROJECT_MEMORY.md si necessaire")

    return "\n".join(L)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print(f"build_memory.py v3 - {NOW}")
    print("=" * 50)

    # Generer PROJECT_MEMORY.md
    pm_content = generate_project_memory()
    pm_path = PROJECT / "PROJECT_MEMORY.md"
    pm_path.write_text(pm_content, "utf-8")
    pm_lines = len(pm_content.splitlines())
    print(f"PROJECT_MEMORY.md : {pm_lines} lignes")

    # Generer BRIEFING.md
    br_content = generate_briefing()
    br_path = PROJECT / "BRIEFING.md"
    br_path.write_text(br_content, "utf-8")
    br_lines = len(br_content.splitlines())
    print(f"BRIEFING.md       : {br_lines} lignes")

    # Stats
    print(f"")
    print(f"Composants detectes : {len(get_component_info())}")
    print(f"Icones stats        : {count_files(ICONS_STATS, '*.webp')}")
    print(f"Icones bonuses      : {count_files(ICONS_BONUSES, '*.png')}")
    print(f"TODOs dans le code  : {len(detect_todos_from_code())}")
    print(f"Commits recents     : {len(get_recent_commits(5))}")
    print(f"")
    print(f"TERMINE - Les deux fichiers sont a jour.")
    print(f"autopush.py va les pousser vers GitHub automatiquement.")
