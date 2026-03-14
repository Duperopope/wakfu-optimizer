# PROJECT MEMORY - Wakfu Optimizer

> Derniere mise a jour : 2026-03-14 11:16:30
> Genere par scripts/build_memory.py
> Memoire persistante entre sessions Claude

## Regles du projet

- Tout fichier doit etre dans MANIFEST.json/allowed_files AVANT creation
- Les commandes passent TOUJOURS par PowerShell
- Les data generees vont dans data/wakfuli/
- Les logs vont dans logs/
- Pas de placeholder : le code doit etre complet et fonctionnel
- autopush.py lit allowed_files + protected + local_only

## Etat des donnees Wakfuli

| Fichier | Taille | Source | Statut |
|---------|--------|--------|--------|
| all_items.json | 11.52 MB | api.wakfuli.com/api/v1/items | OK |
| all_actions.json | 0.01 MB | api.wakfuli.com/api/v1/actions | OK |
| all_builds.json | 38.39 MB | api.wakfuli.com/api/v1/builds | OK |
| all_spells.json | 3.66 MB | frontend Wakfuli (console JS) | OK |
| spell_index_from_builds.json | 0.0 MB | extrait des builds | OK |
| sync_report.json | 0.0 MB | genere par sync_wakfuli.py | OK |
| spells_report.json | 0.0 MB | genere par install_spells.py | OK |
| version.json | 0.0 MB | wakfu.cdn.ankama.com | OK |

## Etat des donnees CDN Ankama (ancien systeme)

| Dossier | Fichiers | Role |
|---------|----------|------|
| data/raw/ | 16 | JSON bruts du CDN Ankama | 
| data/extracted/ | 11 | Donnees parsees (items, spells, states, breeds) | 
| data/parsed/ | 4 | Donnees transformees (action_map, state_map) | 
| data/classes/ | 4 | Classes de personnages (sram, common) | 
| data/profiles/ | 2 | Profils de builds (limmortel) | 

## Moteur de calcul (ancien systeme)

| Module | Role |
|--------|------|
| engine/combat.py | Boucle de combat (OK) |
| engine/damage.py | Calcul de degats (OK) |
| engine/effect_bridge.py | Pont entre effets et stats (OK) |
| engine/equipment.py | Gestion equipement (OK) |
| engine/fighter.py | Entite combattant (OK) |

## Version du jeu : 1.91.1.53

## Derniere synchronisation Wakfuli

- Date : 2026-03-14T11:13:26.199179
- Items : 7686
- Actions : 68
- Builds : 939
- Duree : 113.4s
- Classes : cra, ecaflip, eliotrope, eniripsa, enutrof, feca, huppermage, iop, osamodas, ouginak, pandawa, roublard, sacrieur, sadida, sram, steamer, xelor, zobal

## Sorts installes

- Total : 908 sorts
- Classes : 18
- Taille : 3.66 MB

## API Wakfuli

| Endpoint | Statut | Notes |
|----------|--------|-------|
| /api/v1/items | OK | Pagine, filtres: levelMin, levelMax, itemType, rarity, search |
| /api/v1/actions | OK | 68 effets avec types et descriptions |
| /api/v1/builds | OK | Builds publics pagines |
| /api/v1/spells | 404 | Pas d endpoint sorts |
| /api/v1/breeds | 404 | Pas d endpoint classes |

## CDN Ankama

| URL | Contenu |
|-----|---------|
| wakfu.cdn.ankama.com/gamedata/config.json | Version courante |
| wakfu.cdn.ankama.com/gamedata/{v}/actions.json | Effets multilingues |
| wakfu.cdn.ankama.com/gamedata/{v}/states.json | Etats/sublimations |
| wakfu.cdn.ankama.com/gamedata/{v}/items.json | Items bruts |

## Scripts

| Script | Role | Essentiel |
|--------|------|-----------|
| __init__.py | Legacy/debug | NON |
| analyse_effects.py | Legacy/debug | NON |
| analyse_effects2.py | Legacy/debug | NON |
| analyze_spells.py | Legacy/debug | NON |
| audit_v2.py | Legacy/debug | NON |
| auto_log.py | Legacy/debug | NON |
| autopush.py | Auto-commit + nettoyage fichiers hors manifest | OUI |
| bdata_diagnostic_v5.py | Legacy/debug | NON |
| bdata_reader_final.py | Legacy/debug | NON |
| bootstrap.py | Legacy/debug | NON |
| build_equipment_system.py | Legacy/debug | NON |
| build_memory.py | Genere PROJECT_MEMORY.md | OUI |
| calibrate_v2.py | Legacy/debug | NON |
| check_effects.py | Legacy/debug | NON |
| check_effects_data.py | Legacy/debug | NON |
| combat_validator.py | Legacy/debug | NON |
| data_sync.py | Legacy/debug | NON |
| decompile_client.py | Legacy/debug | NON |
| diagnose_v3.py | Legacy/debug | NON |
| download_and_parse_items.py | Legacy/debug | NON |
| find_state_v4.py | Legacy/debug | NON |
| fix_slot_mapping.py | Legacy/debug | NON |
| gen_spell_names.py | Legacy/debug | NON |
| inject_calibration.py | Legacy/debug | NON |
| inspect_items_structure.py | Legacy/debug | NON |
| install_spells.py | Installe les sorts depuis le fichier navigateur | OUI |
| parse_breeds.py | Legacy/debug | NON |
| parse_breeds_real.py | Legacy/debug | NON |
| parse_effects_final.py | Legacy/debug | NON |
| parse_effects_states.py | Legacy/debug | NON |
| parse_effects_v2.py | Legacy/debug | NON |
| parse_kanjedo.py | Legacy/debug | NON |
| parse_log.py | Legacy/debug | NON |
| parse_session.py | Legacy/debug | NON |
| parse_states_final.py | Legacy/debug | NON |
| parse_static_effects.py | Legacy/debug | NON |
| rapport_mannequin3.py | Legacy/debug | NON |
| rebuild_equipment_fixed.py | Legacy/debug | NON |
| rebuild_items_fixed.py | Legacy/debug | NON |
| sync_wakfuli.py | Telecharge items, actions, builds depuis API Wakfuli | OUI |
| test_e2e_states.py | Legacy/debug | NON |
| test_integral_v3.py | Legacy/debug | NON |
| upgrade_bridge_v2.py | Legacy/debug | NON |
| verify_effects.py | Legacy/debug | NON |

## Architecture

```
wakfu-optimizer/
  app.py                    # Application principale NiceGUI
  config.py                 # Configuration
  MANIFEST.json             # Fichiers proteges (allowed_files)
  PROJECT_MEMORY.md         # Ce fichier
  scripts/                  # Scripts utilitaires
  data/wakfuli/             # Source Wakfuli (API + frontend)
  data/raw/                 # Source CDN Ankama (brut)
  data/extracted/           # Source CDN Ankama (parse)
  data/parsed/              # Source CDN Ankama (transforme)
  engine/                   # Moteur de calcul combat
  logs/                     # Logs de sync et debug
```

## Historique

### 2026-03-14

- Phase 1 : Sync items (7686), actions (68), builds (939) via API Wakfuli
- Phase 2 : Extraction sorts (908/18 classes) via console navigateur
- Correction autopush : ajout lecture allowed_files
- Unification MANIFEST : merge protected + local_only + allowed_files
- Conservation ancien systeme CDN pour verification croisee future

## TODO

- [ ] Phase 3 : Construire app.py (builder NiceGUI)
- [ ] Nettoyer scripts legacy (garder seulement les essentiels)
- [ ] Verification croisee Wakfuli vs CDN Ankama
- [ ] Premier push GitHub propre
