# BRIEFING - wakfu-optimizer
> Auto-genere le 2026-03-14 20:15:37 par build_memory.py v3
> INJECTE AUTOMATIQUEMENT PAR L'EXTENSION CHROME WAKFU DEV ASSISTANT

---

## QUI EST L'UTILISATEUR
Sam est un Product Owner no-code. Il ne code PAS lui-meme.
L'IA fournit des blocs PowerShell complets copiables-collables.
JAMAIS de placeholder, JAMAIS de 'remplace par ton code'.

## REGLES ABSOLUES
1. Lire le code sur GitHub AVANT de coder : https://raw.githubusercontent.com/Duperopope/wakfu-optimizer/main/{path}
2. Blocs PowerShell complets et fonctionnels
3. ZERO placeholder
4. Travailler bout par bout (un fichier a la fois)
5. Ne JAMAIS modifier un fichier non lu
6. autopush.py sync vers GitHub toutes les 5s
7. MAJ PROJECT_MEMORY.md et CHANGELOG.md a chaque etape
8. Verifier les URLs CDN avant utilisation
9. Fin de session : bouton dans l'extension ou python scripts/session_end.py

## LE PROJET
Optimiseur de builds pour Wakfu (MMORPG), inspire de Wakfuli (https://wakfuli.com).
Creer des builds : classe, level, items, stats en temps reel.

## STACK (auto-detecte)
- Next.js 16.1.6 / React 19.2.3 / Tailwind 4 / TypeScript 5
- Windows 11 / PowerShell / VS Code
- npm run dev (port 3000 ou 8090)
- Repo : https://github.com/Duperopope/wakfu-optimizer
- autopush.py (sync 5s) + dev_server.py (localhost:8091)

## COMPOSANTS (auto-detecte)
- BuilderLayout.tsx (75 lignes)
- ClassSelector.tsx (115 lignes)
- LeftPanel.tsx v5 (396 lignes)
- RightPanel.tsx (470 lignes)
- BuildContext.tsx : useBuild(), computeStats(), BASE_STATS (HP=50,AP=6,MP=3,WP=6,FEROCITY=3)
- useWakfuData.ts : chargement JSON
- wakfu.ts : types et constantes

## ASSETS : 33 icones stats .webp, 3 icones bonus .png

## FONCTIONNE
- Classe + level + nom du build
- 7686 items avec images, filtres, equip/unequip
- Stats dynamiques via computeStats
- 3 bonus toggles (Guilde/Havre-Monde/Monture)
- Priorite elementaire draggable
- Enchantements toggle + runes
- Copier/Lien/Visibilite/Favori
- Pipeline automatise : Genspark -> Extension Chrome -> Dev Server -> PowerShell

## TODO
1. Redesign LeftPanel bonus (matcher Wakfuli)
2. Connecter priorite elementaire a computeStats
3. Localiser icones classes
4. Refaire gem.png 64x64+
5. Onglet Sorts
6. Enchantements dans BuildContext
7. Onglets Aptitudes / Notes
8. Sauvegarde localStorage

## PROBLEMES CONNUS
- gem.png pixelise (37x39px)
- Icones classes depuis CDN distant
- Priorite elementaire non connectee
- Enchantements pas dans BuildContext

## CDN : cdn.wakfuli.com/stats|breeds|items|rarity/{KEY}.webp

## COMMITS RECENTS
- de69725 auto 20:15:39: ANIFEST.json, PROJECT_MEMORY.md, dev_server.log +2
- 0cd53e0 auto 20:12:36: dev_server.log
- 7e6f540 auto 20:08:57: dev_server.log

## SCRIPTS : autopush.py, build_memory.py, session_end.py, dev_server.py, sync_wakfuli.py
## DOCS : PROJECT_MEMORY.md, ARCHITECTURE.md, CHANGELOG.md, SESSION_HANDOFF.md

## FORMAT REPONSE
1. Explication claire
2. Bloc PowerShell complet
3. Ce qui a change et pourquoi