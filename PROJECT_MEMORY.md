# PROJECT MEMORY - Wakfu Optimizer

> Derniere mise a jour : 2026-03-14 18:43:58
> Memoire persistante entre sessions - CERVEAU (court terme)
> GitHub : https://github.com/Duperopope/wakfu-optimizer
> Archive long terme : voir CHANGELOG.md (historique complet avec liens commits)
> Raw : https://raw.githubusercontent.com/Duperopope/wakfu-optimizer/main/CHANGELOG.md

## WORKFLOW CLAUDE - A LIRE EN PREMIER

### Protocole de travail
1. LIRE CE FICHIER EN ENTIER avant toute modification sur le projet
2. Toujours lire GitHub (raw files) avant de proposer du code
3. Ne jamais demander a Sam de copier-coller des resultats - lire le repo
4. Donner des blocs PowerShell complets a executer, sans placeholder
5. autopush.py pousse automatiquement sur GitHub toutes les 2min environ
6. Apres chaque bloc, verifier sur GitHub que les changements sont arrives
7. Mettre a jour ce fichier a chaque etape significative
8. Decouper les gros blocs en commandes separees (eviter les coupures)
9. Toujours verifier les URLs CDN avant de les utiliser dans le code

### Protocole de fin de session - OBLIGATOIRE
A la fin de chaque session de travail, toute IA doit :
1. Mettre a jour ce PROJECT_MEMORY.md avec tout ce qui a ete fait
2. Inscrire la date et heure REELLE du systeme avec $now = Get-Date -Format "yyyy-MM-dd HH:mm:ss" (ne JAMAIS ecrire en dur)
3. Mettre a jour les sections : Bugs corriges, Ce qui fonctionne, TODO, Assets
4. Le repo se synchronise en temps reel via autopush.py, le fichier sera visible par les autres IA immediatement
5. Ce fichier est le CERVEAU du projet : si une info manque ici, elle est perdue pour les prochaines sessions

### URLs essentielles pour Claude
- Repo : https://github.com/Duperopope/wakfu-optimizer
- Raw files : https://raw.githubusercontent.com/Duperopope/wakfu-optimizer/main/{path}
- Commits : https://api.github.com/repos/Duperopope/wakfu-optimizer/commits?per_page=5
- API Wakfuli : https://api.wakfuli.com/api/v1/items?page=1&limit=1

### Stack technique
- Frontend : Next.js 16.1.6 / React 19.2.3 / Tailwind CSS 4 / TypeScript 5
- Backend data : Python (sync_wakfuli.py, install_spells.py, build_memory.py)
- Deploiement : Local (npm run dev sur port 3000)
- Autopush : scripts/autopush.py (auto-commit + push toutes les 5s)
- Scripts actifs : autopush.py, sync_wakfuli.py, install_spells.py, build_memory.py
- Scripts legacy : archives dans archive/scripts_legacy/ (voir archive/README.md)
- OS : Windows / PowerShell / VS Code
- Machine : AMD 5700 X3D, 32GB RAM, 1TB dispo

### CDN Wakfuli - URLs verifiees
- Classes : cdn.wakfuli.com/breeds/{classname}.webp
- Stats : cdn.wakfuli.com/stats/{STAT_NAME}.webp (WP pas WAKFU_POINT)
- Items : cdn.wakfuli.com/items/{image_id}.webp
- Placeholders : cdn.wakfuli.com/placeholders/{slot}.webp
- Types : cdn.wakfuli.com/itemTypes/{typeId}.webp
- Raretes : cdn.wakfuli.com/rarity/{RARITY}.webp

### Types effets API connus
- HP, AP, MP, WP, RANGE, FEROCITY, BLOCK, INIT, DODGE, TACKLE
- WISDOM, PROSPECTION, WILLPOWER
- DMG_IN_PERCENT (maitrise elem, avec elementCount)
- RES_IN_PERCENT (resistance elem, distribue sur 4)
- CRITICAL_BONUS, CRITICAL_RES, BACKSTAB_BONUS, RES_BACKSTAB
- MELEE_DMG, RANGED_DMG, HEAL_IN_PERCENT, BERSERK_DMG
- ARMOR_GIVEN, ARMOR_RECEIVED, INDIRECT_DMG
- type null + states[] = effet passif special

## Regles du projet
- Fichiers backend dans MANIFEST.json/allowed_files AVANT creation
- frontend/ dans protected_dirs (tous fichiers proteges)
- Commandes via PowerShell uniquement
- Data dans data/wakfuli/, logs dans logs/
- Pas de placeholder, code complet et fonctionnel
- data/wakfuli/*.json en local only (trop gros pour git)

## Fichiers frontend (2026-03-14 14:45)
- globals.css : OK (couleurs raretes + classes CSS explicites)
- layout.tsx : OK (RootLayout + ThemeProvider + IBM Plex Sans)
- page.tsx : OK (BuildProvider + BuilderLayout)
- api/data/route.ts : OK (GET lit ../data/wakfuli/)
- BuilderLayout.tsx : OK (split 30/70 draggable)
- ClassSelector.tsx : OK (FIX stopPropagation niveau)
- LeftPanel.tsx : OK v5 (icones locales stats+bonus, barre priorite elementaire draggable, bonus toggle iconScale, enchantements toggle, boutons copier/lien/visibilite/favori)
- RightPanel.tsx : OK (items, filtres, ItemCard, modal anneau)
- Navbar.tsx : OK
- BuildContext.tsx : OK (computeStats + pendingRingItem)
- useWakfuData.ts : OK
- wakfu.ts : OK (types, POSITION_TO_SLOT, RARITY_CSS)

## Donnees locales
- all_items.json 11.52 MB (7686 items)
- all_actions.json 0.01 MB (68)
- all_builds.json 38.39 MB (939)
- all_spells.json 3.66 MB (908 sorts, 18 classes)
- Version jeu : 1.91.1.53

## Bugs corriges cette session
1. Couleurs raretes (classes CSS explicites pour Tailwind 4)
2. Chevauchement niveau/classe (stopPropagation)
3. Icone WP cassee (WAKFU_POINT -> WP)
4. Images items (cdn.wakfuli.com/items/{image_id}.webp)
5. LeftPanel reecrit avec useBuild (runtime error fix)
6. FEROCITY renomme en % Coup Critique
7. Icones bonus CDN cassees remplacees par PNG custom locaux (tree/gem/mount)
8. Icones stats CDN telechargees en local /icons/stats/*.webp
9. Ajout barre priorite elementaire draggable (Feu/Eau/Terre/Air)
10. iconScale individuel par bonus (gem.png 37x39px compense par scale 2.0)

## Ce qui fonctionne
- Selection classe, edition niveau, nom du build
- 7686 items avec images + filtres (recherche, niveau, type, rarete)
- Equip/unequip + modal anneau + stats recalculees
- Couleurs rarete correctes (Memory bleu, Relic violet, Epic rose)
- 3 bonus toggle avec icones PNG custom (Guilde/Havre-Monde/Monture)
- Bouton Enchantements toggle
- Barre priorite elementaire draggable (4 elements)
- Stats primaires + secondaires avec icones locales .webp
- Boutons Copier JSON, Lien partageable, Visibilite, Favori

## TODO
- [x] Boutons action LeftPanel (Copier, Lien, Visibilite, Favori) - DONE 2026-03-14
- [x] Checkboxes bonus (Arbre, Gemme, Monture) - DONE avec icones custom
- [x] Barre priorite elementaire draggable - DONE
- [x] Icones stats locales /icons/stats/*.webp - DONE
- [ ] Connecter priorite elementaire a computeStats
- [ ] Localiser icones classes (cdn -> public/icons/breeds/)
- [ ] gem.png a recreer en 64x64+ (actuellement 37x39px pixelise)
- [ ] Onglet Sorts (all_spells.json)
- [ ] Onglet Enchantements (logique dans BuildContext)
- [ ] Onglet Aptitudes
- [ ] Onglet Notes
- [ ] Sauvegarde/chargement builds (localStorage)

## Assets locaux ajoutes (2026-03-14)
- frontend/public/icons/bonuses/tree.png (1735 bytes - Guilde)
- frontend/public/icons/bonuses/gem.png (805 bytes - Havre-Monde, pixelise)
- frontend/public/icons/bonuses/mount.png (Monture)
- frontend/public/icons/stats/*.webp (28 fichiers telecharges depuis cdn.wakfuli.com/stats/)





