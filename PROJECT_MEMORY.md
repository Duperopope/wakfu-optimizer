# PROJECT MEMORY - Wakfu Optimizer

> Derniere mise a jour : 2026-03-14 14:30:00
> Memoire persistante entre sessions Claude
> GitHub : https://github.com/Duperopope/wakfu-optimizer

## WORKFLOW CLAUDE - A LIRE EN PREMIER

### Protocole de travail
1. Toujours lire GitHub avant de proposer du code (crawler les raw files)
2. Ne jamais demander a Sam de copier-coller des resultats - lire le repo
3. Donner des blocs PowerShell complets a executer, sans placeholder
4. autopush.py pousse automatiquement sur GitHub toutes les 2min environ
5. Apres chaque bloc, verifier sur GitHub que les changements sont arrives
6. Mettre a jour ce fichier a chaque etape significative
7. Decouper les gros blocs en commandes separees (eviter les coupures)

### URLs essentielles pour Claude
- Repo : https://github.com/Duperopope/wakfu-optimizer
- Tree API : https://api.github.com/repos/Duperopope/wakfu-optimizer/git/trees/main?recursive=1
- Raw files : https://raw.githubusercontent.com/Duperopope/wakfu-optimizer/main/{path}
- Commits : https://api.github.com/repos/Duperopope/wakfu-optimizer/commits?per_page=5
- Frontend raw : https://raw.githubusercontent.com/Duperopope/wakfu-optimizer/main/frontend/src/{path}

### Stack technique
- Frontend : Next.js 16.1.6 / React 19.2.3 / Tailwind CSS 4 / TypeScript 5
- Backend data : Python (sync_wakfuli.py, install_spells.py, build_memory.py)
- Deploiement : Local (npm run dev sur port 3000)
- Autopush : scripts/autopush.py (auto-commit + push toutes les 2min)
- OS : Windows / PowerShell / VS Code
- Machine : AMD 5700 X3D, 32GB RAM, 1TB dispo

## Regles du projet

- Tout fichier backend doit etre dans MANIFEST.json/allowed_files AVANT creation
- frontend/ est dans protected_dirs donc tous les fichiers frontend sont proteges
- Les commandes passent TOUJOURS par PowerShell
- Les data generees vont dans data/wakfuli/
- Les logs vont dans logs/
- Pas de placeholder : le code doit etre complet et fonctionnel
- autopush.py lit allowed_files + protected_dirs
- Les fichiers data/wakfuli/*.json sont en local only (trop gros pour git)

## Architecture frontend

### Arborescence
- frontend/package.json : Next.js 16, React 19, Tailwind 4
- frontend/src/app/globals.css : Design tokens Wakfuli (couleurs, fonts, rarity)
- frontend/src/app/layout.tsx : RootLayout + ThemeProvider + IBM Plex Sans
- frontend/src/app/page.tsx : BuildProvider + BuilderLayout
- frontend/src/app/api/data/route.ts : GET /api/data?file=xxx lit data/wakfuli/xxx
- frontend/src/components/builder/BuilderLayout.tsx : Layout 30/70 resizable custom
- frontend/src/components/builder/ClassSelector.tsx : Modal selection classe + LevelEditor
- frontend/src/components/builder/LeftPanel.tsx : Stats connecte a BuildContext
- frontend/src/components/builder/RightPanel.tsx : Equipment + items reels + filtres + ItemCard
- frontend/src/components/shared/Navbar.tsx : Logo SVG + nav + Discord + user
- frontend/src/components/ui/ : (futur) composants UI reutilisables
- frontend/src/lib/BuildContext.tsx : State global nom, classe, level, equipment
- frontend/src/lib/useWakfuData.ts : Hook fetch /api/data?file=xxx
- frontend/src/types/wakfu.ts : Types, constantes, CLASSES, SLOT_ORDER, RARITY

### Etat des composants (2026-03-14 14:30)
- layout.tsx : COMPLET
- page.tsx : COMPLET
- api/data/route.ts : COMPLET (lit ../data/wakfuli/)
- BuilderLayout.tsx : COMPLET (flexbox custom, drag resize 18-50%)
- ClassSelector.tsx : COMPLET (modal 6 colonnes, LevelEditor inline)
- LeftPanel.tsx : COMPLET (useBuild, ClassSelector, bonus checkboxes, toutes stats)
- RightPanel.tsx : COMPLET (useWakfuData, filtres niveau/type/rarete, ItemCard, loading/error)
- Navbar.tsx : COMPLET (logo SVG, Discord SVG, liens)
- BuildContext.tsx : COMPLET (name, class, level, equip, unequip)
- useWakfuData.ts : COMPLET (fetch generique avec loading/error)
- wakfu.ts : COMPLET (18 classes, 7 raretes, 13 slots, types Item/Effect/StatLine)

### Dependencies npm installees
- react-resizable-panels 4.7.2 (installe mais non utilise, layout custom a la place)
- lucide-react (icones)
- next-themes (dark mode)
- @radix-ui/react-checkbox, dialog, dropdown-menu, toggle-group, tooltip
- clsx

## Design system Wakfuli

- Backgrounds: #0a0d13, #101319, #1a1e27, #22262f, #383e4d
- Primary text: #e1ffff
- Accent: #71f2ff (cyan-wakfuli)
- Elements: Fire #ff9333, Water #99f9f9, Earth #c4dd1e, Air #ed99ff
- Stats: HP #ff515b, AP #19c1ef, MP #afd34c, WP #e1b900
- Rarity: Common #b0b0b0, Rare #36e376, Mythical #f28c28, Legendary #ffd700, Memory #e84dff, Epic #ff6b9d, Relic #ff4444
- Fonts: Bagnard (titres via /fonts/Bagnard.otf), IBM Plex Sans (body via next/font)
- Icons: Lucide React
- CDN images: cdn.wakfuli.com/breeds/, /stats/, /placeholders/, /itemTypes/, /rarity/
- Item images: static.ankama.com/wakfu/portal/game/item/115/{imageId}.png

## Etat des donnees Wakfuli (local only)

| Fichier | Taille | Source | Statut |
|---------|--------|--------|--------|
| all_items.json | 11.52 MB | api.wakfuli.com/api/v1/items | OK |
| all_actions.json | 0.01 MB | api.wakfuli.com/api/v1/actions | OK |
| all_builds.json | 38.39 MB | api.wakfuli.com/api/v1/builds | OK |
| all_spells.json | 3.66 MB | frontend Wakfuli (console JS) | OK |
| spell_index_from_builds.json | < 0.01 MB | extrait des builds | OK |
| sync_report.json | < 0.01 MB | genere par sync_wakfuli.py | OK |
| spells_report.json | < 0.01 MB | genere par install_spells.py | OK |
| version.json | < 0.01 MB | wakfu.cdn.ankama.com | OK |

## Derniere synchronisation Wakfuli

- Date : 2026-03-14T11:13:26
- Items : 7686
- Actions : 68
- Builds : 939
- Sorts : 908 (18 classes)
- Version jeu : 1.91.1.53

## API Wakfuli

| Endpoint | Statut |
|----------|--------|
| /api/v1/items | OK (pagine, filtres levelMin/Max, itemType, rarity, search) |
| /api/v1/actions | OK (68 effets) |
| /api/v1/builds | OK (builds publics pagines) |
| /api/v1/spells | 404 |
| /api/v1/breeds | 404 |

## Scripts essentiels

| Script | Role |
|--------|------|
| autopush.py | Auto-commit + push fichiers manifest + protected_dirs |
| build_memory.py | Genere PROJECT_MEMORY.md |
| sync_wakfuli.py | Telecharge items, actions, builds depuis API Wakfuli |
| install_spells.py | Installe les sorts depuis fichier navigateur |

## Historique

### 2026-03-14
- Phase 1 : Sync items (7686), actions (68), builds (939) via API Wakfuli
- Phase 2 : Extraction sorts (908/18 classes) via console navigateur
- Phase 3 : Frontend Next.js 16 cree (layout, page, api route, types)
- Phase 4 : Navbar, BuilderLayout 30/70 resizable, ClassSelector, LeftPanel statique
- Phase 5 : Fix react-resizable-panels v4 (Group/Panel/Separator), puis remplacement par custom flexbox
- Phase 6 : BuildContext (state global), useWakfuData (hook fetch)
- Phase 7 : LeftPanel connecte au BuildContext + ClassSelector + bonus checkboxes
- Phase 8 : RightPanel charge les vrais items (useWakfuData) + filtres + ItemCard

## TODO

- [ ] Verifier que les items s affichent (npm run dev + tester filtres)
- [ ] Implementer equip/unequip (clic sur + dans ItemCard -> slot dans EquipmentBar)
- [ ] Calculer les stats reelles depuis les items equipes (somme des effets)
- [ ] Onglet Sorts (charger all_spells.json)
- [ ] Onglet Enchantements
- [ ] Onglet Aptitudes
- [ ] Onglet Notes
- [ ] Slider de niveau double-range propre (remplacer les 2 inputs range)
- [ ] Recherche avancee (filtres par effet specifique)
- [ ] Sauvegarde/chargement de builds (localStorage puis API)
- [ ] Nettoyer scripts legacy
- [ ] Verification croisee Wakfuli vs CDN Ankama
