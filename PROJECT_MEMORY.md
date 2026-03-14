# PROJECT MEMORY - wakfu-optimizer
> Derniere mise a jour : 2026-03-14 20:05:16
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
2. Ou mettre a jour manuellement PROJECT_MEMORY.md + CHANGELOG.md
3. Ce fichier = cerveau. Info absente ici = perdue.

## LIENS RAPIDES
- Repo : https://github.com/Duperopope/wakfu-optimizer
- Raw : https://raw.githubusercontent.com/Duperopope/wakfu-optimizer/main/{path}
- Commits : https://api.github.com/repos/Duperopope/wakfu-optimizer/commits?per_page=5
- ARCHITECTURE.md | CHANGELOG.md | BRIEFING.md | SESSION_HANDOFF.md

## STACK (auto-detecte)
- Frontend : Next.js 16.1.6 / React 19.2.3 / Tailwind CSS 4 / TypeScript 5
- OS : Windows / PowerShell / VS Code
- Serveur dev : npm run dev (port 3000 ou 8090)

## COMPOSANTS BUILDER (auto-detecte)
- BuilderLayout.tsx : 75 lignes
- ClassSelector.tsx : 115 lignes
- LeftPanel.tsx v5 : 396 lignes
- RightPanel.tsx : 470 lignes
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

## DERNIERE SYNC : 2026-03-14T11:13:26.199179
- 7686 items, 68 actions, 939 builds

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
- 77685c6 auto 20:00:09: dev_server.log
- 4add6c4 auto 19:59:32: ANIFEST.json, dev_server.py
- b8bfd4f auto 19:54:37: build_memory.py
- 766238b auto 19:47:05: BRIEFING.md
- d5e7eb7 auto 19:46:44: ANIFEST.json

## FICHIERS ACTIFS
- frontend/src/components/builder/LeftPanel.tsx (dernier modifie)
- frontend/src/components/builder/RightPanel.tsx
- frontend/src/components/builder/BuilderLayout.tsx
- frontend/src/components/builder/ClassSelector.tsx
- frontend/src/lib/BuildContext.tsx
- frontend/public/icons/ (stats/*.webp + bonuses/*.png)
