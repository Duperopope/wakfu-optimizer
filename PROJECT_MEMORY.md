# PROJECT MEMORY - wakfu-optimizer
> Derniere mise a jour : 2026-03-14 23:28:56
> CERVEAU du projet - A LIRE EN PREMIER par toute IA

## REGLES
1. LIRE CE FICHIER EN ENTIER avant toute modification
2. Lire le code sur GitHub (raw files) avant de proposer du code
3. Donner des blocs PowerShell complets, SANS placeholder
4. autopush.py synchronise local -> GitHub toutes les 5 secondes
5. Mettre a jour CE FICHIER a chaque etape significative
6. Verifier les URLs CDN avant de les utiliser

## FIN DE SESSION - OBLIGATOIRE
1. Executer : python scripts/session_end.py
2. Ou utiliser le bouton Fin de Session dans l'extension Chrome
3. Ce fichier = cerveau. Info absente ici = perdue.

## LIENS RAPIDES
- Repo : https://github.com/Duperopope/wakfu-optimizer
- Raw : https://raw.githubusercontent.com/Duperopope/wakfu-optimizer/main/{path}
- ARCHITECTURE.md | CHANGELOG.md | BRIEFING.md | SESSION_HANDOFF.md

## STACK (auto-detecte)
- Frontend : Next.js 16.1.6 / React 19.2.3 / Tailwind CSS 4 / TypeScript 5
- OS : Windows / PowerShell / VS Code
- Serveur dev : npm run dev (port 3000 ou 8090)
- Dev Server : python scripts/dev_server.py (port 8091)

## COMPOSANTS BUILDER (auto-detecte)
- BuilderLayout.tsx : 75 lignes
- ClassSelector.tsx : 115 lignes
- LeftPanel.tsx v5 : 396 lignes
- RightPanel.tsx : 470 lignes
- SaveButton.tsx : 33 lignes
- lib/BuildContext.tsx : 217 lignes
- lib/useWakfuData.ts : 40 lignes

## ASSETS (auto-detecte)
- icons/stats/ : 33 icones .webp
- icons/bonuses/ : 3 icones .png

## DONNEES WAKFULI (auto-detecte)
- all_items.json : 11.52 MB (7686 entrees) [OK]
- all_actions.json : 12.8 KB (68 entrees) [OK]
- all_builds.json : 38.39 MB (939 entrees) [OK]
- all_spells.json : 3.66 MB [OK]
- version.json : 71 B [OK]
- sync_report.json : 512 B [OK]
- spells_report.json : 2.2 KB [OK]

## VERSION JEU : 1.91.1.53

## CE QUI MARCHE
- Selection classe, level, nom du build
- 7686 items avec images + filtres + equip/unequip + modal anneau
- Stats recalculees dynamiquement (computeStats)
- 3 bonus toggle (Guilde/Havre-Monde/Monture) icones custom
- Barre priorite elementaire draggable
- Enchantements toggle + onglet runes
- Boutons Copier/Lien/Visibilite/Favori
- Couleurs rarete correctes
- Extension Chrome Wakfu Dev Assistant v2.1
- Dev Server local (localhost:8091)
- Pipeline : Genspark -> Extension -> Dev Server -> PowerShell -> Resultat

## TODO (priorite)
- [ ] Redesign LeftPanel bonus pour matcher Wakfuli
- [ ] Connecter priorite elementaire a computeStats
- [ ] Localiser icones classes (cdn -> local)
- [ ] Refaire gem.png en 64x64+
- [ ] Onglet Sorts (all_spells.json dispo)
- [ ] Enchantements dans BuildContext
- [ ] Onglets Aptitudes / Notes
- [ ] Sauvegarde builds localStorage

## CDN WAKFULI
- Stats : cdn.wakfuli.com/stats/{STAT_KEY}.webp
- Classes : cdn.wakfuli.com/breeds/{class}.webp
- Items : cdn.wakfuli.com/items/{image_id}.webp
- Raretes : cdn.wakfuli.com/rarity/{RARITY}.webp

## COMMITS RECENTS
- e963119 auto 20:15:46: RIEFING.md, dev_server.log
- de69725 auto 20:15:39: ANIFEST.json, PROJECT_MEMORY.md, dev_server.log +2
- 0cd53e0 auto 20:12:36: dev_server.log
- 7e6f540 auto 20:08:57: dev_server.log
- ac248dc auto 20:08:51: dev_server.log

## FICHIERS ACTIFS
- frontend/src/components/builder/LeftPanel.tsx
- frontend/src/components/builder/RightPanel.tsx
- frontend/src/components/builder/BuilderLayout.tsx
- frontend/src/components/builder/ClassSelector.tsx
- frontend/src/lib/BuildContext.tsx
- frontend/public/icons/
