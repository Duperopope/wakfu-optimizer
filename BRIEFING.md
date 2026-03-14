# BRIEFING - wakfu-optimizer
> Auto-genere le 2026-03-14 19:45:31
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

## LE PROJET
Un optimiseur de builds pour le MMORPG Wakfu, inspire du site Wakfuli (https://wakfuli.com).
L'application permet de creer des builds : choisir une classe, un level, equiper des items, voir les stats calculees en temps reel.

## STACK TECHNIQUE
- **Framework** : Next.js 16.1.6 / React 19.2.3 / TypeScript 5
- **CSS** : Tailwind CSS 4
- **OS** : Windows 11 / PowerShell / VS Code
- **Serveur dev** : npm run dev (port 3000 ou 8090)
- **Repo** : https://github.com/Duperopope/wakfu-optimizer
- **Sync** : autopush.py (git add/commit/push toutes les 5s)

## ARCHITECTURE FRONTEND (ou on travaille)
Tous les fichiers actifs sont dans frontend/src/ :

### Composants builder (frontend/src/components/builder/)
- **BuilderLayout.tsx** : layout 2 panneaux avec split draggable 30/70
- **LeftPanel.tsx (v5)** : panneau gauche - stats, bonus, priorite elementaire, enchantements
- **RightPanel.tsx** : panneau droit - onglets items (filtre/equip) et enchantements (runes)
- **ClassSelector.tsx** : modal selection classe + editeur de niveau

### Contexte et logique (frontend/src/lib/)
- **BuildContext.tsx** : etat global du build via React Context + useBuild() hook
  - computeStats() : calcule les stats a partir des items equipes
  - BASE_STATS : HP=50, AP=6, MP=3, WP=6, FEROCITY=3
  - baseHpForLevel(level) = 50 + level*10
  - Expose : build, stats, setName, setClass, setLevel, equipItem, unequipItem, pendingRingItem
- **useWakfuData.ts** : hook de chargement des JSON
- **wakfu.ts** : types TypeScript et constantes (CLASSES, etc.)

### Assets (frontend/public/)
- icons/stats/*.webp : 28 icones de stats (telechargees depuis cdn.wakfuli.com)
- icons/bonuses/*.png : 3 icones custom (tree.png, gem.png, mount.png)
- data/*.json : copies locales des donnees Wakfuli

## CE QUI FONCTIONNE ACTUELLEMENT
- Selection classe + level + nom du build
- 7686 items avec images, filtres, equip/unequip, modal double anneau
- Stats recalculees dynamiquement via computeStats
- 3 bonus toggles (Guilde/Havre-Monde/Monture) avec icones PNG custom
- Barre de priorite elementaire draggable (Feu/Eau/Terre/Air) via HTML5 drag-and-drop
- Toggle enchantements + onglet runes
- Boutons : Copier JSON, Lien partageable base64, Visibilite (public/lien/prive), Favori localStorage
- Couleurs de rarete correctes (CSS explicite pour Tailwind 4)
- Section debug en mode developpement

## DONNEES CDN WAKFULI
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
9. Connecter le moteur de combat Python (engine/) au frontend

## PROBLEMES CONNUS
- gem.png pixelise (37x39px), compense par iconScale 2.0
- Icones de classes chargees depuis CDN distant (pas local)
- Priorite elementaire non connectee a computeStats
- Enchantements pas encore dans BuildContext

## FICHIERS LEGACY (ne pas toucher sauf besoin specifique)
- engine/ : moteur combat Python pour Sram (formules de degats reference)
- decompiled/ : 332 fichiers Java decompiles du client Wakfu
- data/raw/ + data/extracted/ : ancien systeme CDN Ankama
- scripts/ : 41 scripts legacy dans archive/scripts_legacy/
- reference/ : 758 fichiers scrapes de wakfuli.com

## SCRIPTS ACTIFS
- **autopush.py** : sync git toutes les 5s, nettoie fichiers hors MANIFEST.json
- **sync_wakfuli.py** : telecharge items/builds/spells depuis l'API Wakfuli
- **install_spells.py** : installe les donnees de sorts
- **build_memory.py** : regenere PROJECT_MEMORY.md depuis l'etat du repo

## DOCUMENTATION COMPLEMENTAIRE
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
