# PROJECT MEMORY - Wakfu Optimizer

> Derniere mise a jour : 2026-03-14 18:46:28
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

## INVENTAIRE COMPLET DU PROJET (mis a jour 2026-03-14 18:46:28)

### frontend/ (25469 fichiers, app Next.js active)
- globals.css : couleurs raretes + classes CSS explicites
- layout.tsx : RootLayout + ThemeProvider + IBM Plex Sans
- page.tsx : BuildProvider + BuilderLayout
- api/data/route.ts : GET lit ../data/wakfuli/
- BuilderLayout.tsx : split 30/70 draggable
- ClassSelector.tsx : selecteur classe + modal + LevelEditor
- LeftPanel.tsx v5 : icones locales, priorite elementaire, bonus toggle, enchantements
- RightPanel.tsx : onglets items + enchants fonctionnels
- Navbar.tsx : barre de navigation
- BuildContext.tsx : contexte React, types, computeStats
- useWakfuData.ts : hook chargement donnees
- wakfu.ts : types, POSITION_TO_SLOT, RARITY_CSS
- public/icons/stats/*.webp : 28 icones stats (depuis CDN Wakfuli)
- public/icons/bonuses/*.png : 3 icones bonus custom (tree, gem, mount)
- public/data/*.json : items, builds, spells, actions copies depuis data/wakfuli/

### engine/ (10 fichiers, 263 Ko - moteur de combat Python legacy)
- combat.py (23 Ko) : boucle de combat tour par tour
- damage.py (23 Ko) : calcul de degats (formules Wakfu)
- double.py (41 Ko) : gestion du Double Sram (invocation controlable)
- effect_bridge.py (41 Ko) : pont entre effets de sorts et modifications de stats
- equipment.py (19 Ko) : gestion equipement et slots
- fighter.py (25 Ko) : entite combattant (PV, PA, PM, stats, etats)
- grid.py (19 Ko) : grille de combat hexagonale
- invisibility.py (33 Ko) : systeme invisibilite Sram
- orientation.py (41 Ko) : gestion orientation et dos/face
- __init__.py : module init
> Ce moteur simulait des combats Sram complets. Non utilise par le frontend Next.js
> mais contient les formules de degats et la logique de combat de reference.

### scripts/ (45 fichiers - 4 actifs, 41 legacy)
Actifs :
- autopush.py v2 : auto-commit + push temps reel (5s) + nettoyage MANIFEST
- sync_wakfuli.py : telecharge items/actions/builds depuis api.wakfuli.com
- install_spells.py : installe les sorts extraits du navigateur Wakfuli
- build_memory.py : ancien generateur de PROJECT_MEMORY (fonctionnel mais remplace)
Legacy (voir archive/scripts_legacy/ pour copies + archive/README.md) :
- analyse_effects*.py : analyse effets sorts Sram depuis CDN Ankama
- parse_*.py : parsing formats binaires, effets, etats, breeds, kanjedo
- calibrate_v2.py + inject_calibration.py : calibration moteur degats in-game
- decompile_client.py : decompilation wakfu-client.jar avec CFR
- bootstrap.py : ancien setup UI NiceGUI (abandonne pour Next.js)
- bdata_*.py : lecture format binaire donnees Wakfu
- data_sync.py : ancien sync CDN Ankama (remplace par sync_wakfuli.py)
- combat_validator.py : validation calculs combat
- rapport_mannequin3.py : tests sur mannequin entrainement in-game
- test_*.py : tests end-to-end

### data/ (54 fichiers)
- data/wakfuli/ (8 fichiers) : source API Wakfuli (items, builds, spells, actions)
  all_items.json 11.52 MB (7686 items)
  all_builds.json 38.39 MB (939 builds)
  all_spells.json 3.66 MB (908 sorts, 18 classes)
  all_actions.json 0.01 MB (68 actions)
  + version.json, sync_report.json, spells_report.json, spell_index_from_builds.json
- data/raw/ (16 fichiers) : JSON bruts CDN Ankama (items, states, actions, recipes, etc.)
- data/extracted/ (11 fichiers) : donnees parsees (all_items, all_spells, breeds, states, etc.)
- data/parsed/ (4 fichiers) : donnees transformees (action_map, state_map, equipment_types)
- data/classes/ (7 fichiers) : classes Python (Sram, common, base_class)
- data/profiles/ (4 fichiers) : profils de builds (L Immortel)
> data/raw/ et data/extracted/ = ancien systeme CDN Ankama, conserve pour verification croisee
> data/wakfuli/ = source actuelle utilisee par le frontend

### decompiled/ (332 fichiers - code Java decompile du client Wakfu)
- racine : ~230 classes Java decompilees (aKP.java a nB.java)
- key_classes/ : classes cles identifiees (aOC effets, fwH items, aNn sorts, etc.)
- items/ : classes liees aux items (.java + .class)
- states/ : classes liees aux etats/sublimations (.java + .class)
- effects_real/ : classes d effets reels (aOC, aZy, fyb)
> Fichiers les plus importants : aTN.java (544 Ko!), cKV.java (1 Mo), eHr.java (236 Ko)
> Ces gros fichiers contiennent probablement les tables de donnees du jeu.
> Source : wakfu-client.jar decompile avec CFR (tools/cfr.jar)

### reference/ (758 fichiers - assets scrapes de Wakfuli)
- reference/wakfuli/assets/js/ : JavaScript source Wakfuli (25c3dbf546a727d1.js)
- reference/wakfuli/assets/css/ : 5 fichiers CSS Wakfuli
- reference/wakfuli/assets/images/ : icones items numeriques .webp
- reference/wakfuli/assets/fonts/ : polices
- reference/wakfuli/assets/other/ : autres assets

### logs/ (20 fichiers)
- sync_wakfuli_*.log : logs de synchronisation API Wakfuli
- app_*.log / app.log : logs application NiceGUI
- wakfu_optimizer.log (143 Ko) : log principal
- file_hashes.json : hashes pour detection changements
- modifications.jsonl : journal des modifications fichiers
- module_registry.json : registre des modules Python

### archive/ (40 fichiers)
- archive/scripts_legacy/ : copies des scripts legacy
- archive/README.md : contexte et explication de l archivage

### Racine
- app.py (20 Ko) : ancienne UI NiceGUI (abandonnee pour Next.js)
- config.py (2 Ko) : configuration projet
- MANIFEST.json (4 Ko) : 117 allowed_files + 5 protected_dirs
- PROJECT_MEMORY.md : ce fichier (cerveau)
- CHANGELOG.md : archive long terme des sessions
- .gitignore : exclusions git

### tools/
- cfr.jar (2.1 Mo) : decompilateur Java CFR (utilise par decompile_client.py)

### tests/
- test_sram_load.py : test chargement donnees Sram
- __init__.py

### utils/
- changelog.py (4 Ko) : utilitaire changelog
- logger.py (1 Ko) : configuration logging
- __init__.py

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






