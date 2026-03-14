# PROJECT MEMORY - wakfu-optimizer
> Derniere mise a jour : 2026-03-14 18:48:56
> CERVEAU du projet - A LIRE EN PREMIER par toute IA

## REGLES
1. LIRE CE FICHIER EN ENTIER avant toute modification
2. Lire le code sur GitHub (raw files) avant de proposer du code
3. Donner des blocs PowerShell complets, SANS placeholder
4. autopush.py synchronise local -> GitHub toutes les 5 secondes
5. Mettre a jour CE FICHIER a chaque etape significative
6. Verifier les URLs CDN avant de les utiliser

## FIN DE SESSION - OBLIGATOIRE
1. Mettre a jour ce fichier avec tout ce qui a ete fait
2. Date/heure avec Get-Date (JAMAIS en dur)
3. Mettre a jour CHANGELOG.md (nouvelle entree)
4. Ce fichier = cerveau. Info absente ici = perdue.

## LIENS RAPIDES
- Repo : https://github.com/Duperopope/wakfu-optimizer
- Raw : https://raw.githubusercontent.com/Duperopope/wakfu-optimizer/main/{path}
- Commits : https://api.github.com/repos/Duperopope/wakfu-optimizer/commits?per_page=5
- Inventaire detaille : ARCHITECTURE.md
- Historique sessions : CHANGELOG.md

## STACK
- Frontend : Next.js 16.1.6 / React 19.2.3 / Tailwind CSS 4 / TypeScript 5
- OS : Windows / PowerShell / VS Code
- Serveur dev : npm run dev (port 3000 ou 8090)

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
- [ ] Connecter priorite elementaire a computeStats
- [ ] Localiser icones classes (cdn -> local)
- [ ] Refaire gem.png en 64x64+ (pixelise)
- [ ] Onglet Sorts (all_spells.json dispo)
- [ ] Enchantements dans BuildContext
- [ ] Onglets Aptitudes / Notes
- [ ] Sauvegarde builds localStorage

## CDN WAKFULI
- Stats : cdn.wakfuli.com/stats/{STAT_KEY}.webp
- Classes : cdn.wakfuli.com/breeds/{class}.webp
- Items : cdn.wakfuli.com/items/{image_id}.webp
- Raretes : cdn.wakfuli.com/rarity/{RARITY}.webp

## FICHIERS ACTIFS (ou on travaille)
- frontend/src/components/builder/LeftPanel.tsx (v5 - dernier modifie)
- frontend/src/components/builder/RightPanel.tsx
- frontend/src/components/builder/BuilderLayout.tsx
- frontend/src/components/builder/ClassSelector.tsx
- frontend/src/lib/BuildContext.tsx
- frontend/public/icons/ (stats/*.webp + bonuses/*.png)

## CONTEXTE LEGACY (lire ARCHITECTURE.md si besoin)
engine/ = moteur combat Python (formules de degats de reference)
decompiled/ = 332 fichiers Java du client Wakfu
data/raw/ + data/extracted/ = ancien systeme CDN Ankama
scripts/ = 41 scripts legacy dans archive/
