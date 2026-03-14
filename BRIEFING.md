# BRIEFING - wakfu-optimizer
> Auto-genere le 2026-03-14 20:05:16 par build_memory.py v3
> CE FICHIER EST INJECTE AUTOMATIQUEMENT EN DEBUT DE SESSION PAR L'EXTENSION CHROME
> Il resume TOUT ce qu'une IA doit savoir pour travailler sur ce projet

---

## QUI EST L'UTILISATEUR
Sam est un Product Owner no-code. Il ne code PAS lui-meme. L'IA doit fournir des blocs PowerShell complets copiables-collables, JAMAIS de placeholder, JAMAIS de "remplace par ton code". Sam coordonne, l'IA execute.

## REGLES ABSOLUES
1. Lire le code source sur GitHub AVANT de proposer du code : https://raw.githubusercontent.com/Duperopope/wakfu-optimizer/main/{path}
2. Donner des blocs PowerShell complets et fonctionnels
3. ZERO placeholder - tout le code doit etre fonctionnel tel quel
4. Travailler bout par bout (petit scope, un fichier a la fois)
5. Ne JAMAIS modifier un fichier qu'on n'a pas lu d'abord
6. autopush.py tourne en fond et synchronise vers GitHub toutes les 5s
7. Mettre a jour PROJECT_MEMORY.md et CHANGELOG.md a chaque etape importante
8. Verifier les URLs CDN avant de les utiliser dans le code
9. En fin de session : executer python scripts/session_end.py

## LE PROJET
Un optimiseur de builds pour le MMORPG Wakfu, inspire du site Wakfuli (https://wakfuli.com).
L'application permet de creer des builds : choisir une classe, un level, equiper des items, voir les stats calculees en temps reel.

## STACK TECHNIQUE (auto-detecte)
- **Framework** : Next.js 16.1.6 / React 19.2.3 / TypeScript 5
- **CSS** : Tailwind CSS 4
- **OS** : Windows 11 / PowerShell / VS Code
- **Serveur dev** : npm run dev (port 3000 ou 8090)
- **Repo** : https://github.com/Duperopope/wakfu-optimizer
- **Sync** : autopush.py (git add/commit/push toutes les 5s)

## COMPOSANTS BUILDER (auto-detecte)
- **BuilderLayout.tsx** (75 lignes)
- **ClassSelector.tsx** (115 lignes)
- **LeftPanel.tsx** v5 (396 lignes)
- **RightPanel.tsx** (470 lignes)

### Contexte et logique (frontend/src/lib/)
- **BuildContext.tsx** : etat global du build via React Context + useBuild() hook
  - computeStats() : calcule les stats a partir des items equipes
  - BASE_STATS : HP=50, AP=6, MP=3, WP=6, FEROCITY=3
  - baseHpForLevel(level) = 50 + level*10
  - Expose : build, stats, setName, setClass, setLevel, equipItem, unequipItem, pendingRingItem
- **useWakfuData.ts** : hook de chargement des JSON
- **wakfu.ts** : types TypeScript et constantes (CLASSES, etc.)

### Assets (auto-detecte)
- icons/stats/ : 33 icones .webp
- icons/bonuses/ : 3 icones .png (tree.png, gem.png, mount.png)
- data/*.json : copies locales des donnees Wakfuli

## CE QUI FONCTIONNE ACTUELLEMENT
- Selection classe + level + nom du build
- 7686 items avec images, filtres, equip/unequip, modal double anneau
- Stats recalculees dynamiquement via computeStats
- 3 bonus toggles (Guilde/Havre-Monde/Monture) avec icones PNG custom
- Barre de priorite elementaire draggable (Feu/Eau/Terre/Air)
- Toggle enchantements + onglet runes
- Boutons : Copier JSON, Lien partageable base64, Visibilite, Favori localStorage
- Couleurs de rarete correctes

## DONNEES (auto-detecte)
- all_items.json: 11.52 MB (7686 entrees)
- all_actions.json: 12.8 KB (68 entrees)
- all_builds.json: 38.39 MB (939 entrees)
- all_spells.json: 3.66 MB
- version.json: 71 B
- sync_report.json: 512 B
- spells_report.json: 2.2 KB

## CDN WAKFULI
- Stats : https://cdn.wakfuli.com/stats/{STAT_KEY}.webp
- Classes : https://cdn.wakfuli.com/breeds/{class}.webp
- Items : https://cdn.wakfuli.com/items/{image_id}.webp
- Raretes : https://cdn.wakfuli.com/rarity/{RARITY}.webp

## TODO (par priorite)
1. Redesign LeftPanel section bonus pour matcher le style Wakfuli
2. Connecter priorite elementaire a computeStats (impact tri items)
3. Localiser icones classes (CDN distant -> fichiers locaux)
4. Refaire gem.png en 64x64+ (actuellement 37x39px, pixelise)
5. Onglet Sorts (all_spells.json disponible dans data/wakfuli/)
6. Integrer enchantements dans BuildContext
7. Onglets Aptitudes et Notes
8. Sauvegarde builds dans localStorage

## PROBLEMES CONNUS
- gem.png pixelise (37x39px), compense par iconScale 2.0
- Icones de classes chargees depuis CDN distant (pas local)
- Priorite elementaire non connectee a computeStats
- Enchantements pas encore dans BuildContext

## COMMITS RECENTS
- 4d6e34b auto 20:05:19: ROJECT_MEMORY.md, dev_server.log
- 77685c6 auto 20:00:09: dev_server.log
- 4add6c4 auto 19:59:32: ANIFEST.json, dev_server.py

## SCRIPTS ACTIFS
- **autopush.py** : sync git toutes les 5s, nettoie fichiers hors MANIFEST.json
- **build_memory.py** : regenere PROJECT_MEMORY.md + BRIEFING.md (CE SCRIPT)
- **session_end.py** : fin de session (CHANGELOG + SESSION_HANDOFF + build_memory)
- **sync_wakfuli.py** : telecharge items/builds/spells depuis l'API Wakfuli
- **install_spells.py** : installe les donnees de sorts

## DOCUMENTATION
- **PROJECT_MEMORY.md** : cerveau du projet (etat actuel, todo, regles)
- **ARCHITECTURE.md** : inventaire detaille de tous les dossiers et fichiers
- **CHANGELOG.md** : historique chronologique de toutes les sessions
- **SESSION_HANDOFF.md** : contexte de la derniere session (si existe)

## FORMAT DE REPONSE ATTENDU
L'IA doit toujours repondre avec :
1. Ce qu'elle va faire (explication claire)
2. Le bloc PowerShell complet a copier-coller
3. Ce qui a change et pourquoi
4. La mise a jour de PROJECT_MEMORY.md si necessaire