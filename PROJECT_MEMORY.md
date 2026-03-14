# PROJECT MEMORY - Wakfu Optimizer

> Derniere mise a jour : 2026-03-14 10:55
> Ce fichier est la memoire persistante du projet.
> Il DOIT etre lu en debut de chaque session.
> Il DOIT etre mis a jour a la fin de chaque session.

## Regles absolues

1. JAMAIS de fichier cree manuellement - Tout passe par un script PowerShell (here-string)
2. MANIFEST.json mis a jour AVANT de creer un fichier - Sinon autopush le supprime
3. Pas de placeholder - L utilisateur ne code pas, tout doit etre fonctionnel
4. Pas de profil hardcode - Le builder est universel (toutes classes, tous niveaux)
5. Sources citees - Toute donnee vient d une source verifiable
6. Gros JSON dans .gitignore - all_items, all_builds, all_spells, all_actions sont regenerables
7. Fichiers legers commites - Scripts, rapports, config, MANIFEST, PROJECT_MEMORY.md

## Etat des donnees (version inconnue)

| Fichier | Taille | Source |
|---------|--------|--------|

### Sync : non execute
### Sorts : non installe

## API Wakfuli - Endpoints

| Endpoint | Status | Notes |
|----------|--------|-------|
| /items | OK sans auth | page, limit, levelMin, levelMax, itemType, rarity, search |
| /actions | OK sans auth | 68 total, 1 page |
| /builds | OK sans auth | 939 publics, contient spell IDs |
| /items/hidden | Auth requise | Token personnel |
| /spells | N EXISTE PAS | Donnees dans frontend JS uniquement |
| /breeds | N EXISTE PAS | - |

## CDN Ankama

- Config : https://wakfu.cdn.ankama.com/gamedata/config.json
- Actions : https://wakfu.cdn.ankama.com/gamedata/{version}/actions.json
- States : https://wakfu.cdn.ankama.com/gamedata/{version}/states.json
- Items : https://wakfu.cdn.ankama.com/gamedata/{version}/items.json
- PAS de spells.json sur le CDN

## Scripts

- scripts/__init__.py
- scripts/analyse_effects.py
- scripts/analyse_effects2.py
- scripts/analyze_spells.py
- scripts/audit_v2.py
- scripts/auto_log.py
- scripts/autopush.py
- scripts/bdata_diagnostic_v5.py
- scripts/bdata_reader_final.py
- scripts/bootstrap.py
- scripts/build_equipment_system.py
- scripts/build_memory.py
- scripts/calibrate_v2.py
- scripts/check_effects.py
- scripts/check_effects_data.py
- scripts/combat_validator.py
- scripts/data_sync.py
- scripts/decompile_client.py
- scripts/diagnose_v3.py
- scripts/download_and_parse_items.py
- scripts/find_state_v4.py
- scripts/fix_slot_mapping.py
- scripts/gen_spell_names.py
- scripts/inject_calibration.py
- scripts/inspect_items_structure.py
- scripts/parse_breeds.py
- scripts/parse_breeds_real.py
- scripts/parse_effects_final.py
- scripts/parse_effects_states.py
- scripts/parse_effects_v2.py
- scripts/parse_kanjedo.py
- scripts/parse_log.py
- scripts/parse_session.py
- scripts/parse_states_final.py
- scripts/parse_static_effects.py
- scripts/rapport_mannequin3.py
- scripts/rebuild_equipment_fixed.py
- scripts/rebuild_items_fixed.py
- scripts/test_e2e_states.py
- scripts/test_integral_v3.py
- scripts/upgrade_bridge_v2.py
- scripts/verify_effects.py

## Fichiers racine

- .gitignore
- app.py
- config.py
- MANIFEST.json

## Architecture cible

```
wakfu-optimizer/
  PROJECT_MEMORY.md      <- CE FICHIER
  MANIFEST.json          <- Fichiers proteges
  .gitignore             <- Exclut gros JSON
  README.md              <- Doc publique
  config.py              <- Constantes du jeu
  app.py                 <- Application NiceGUI
  scripts/
    sync_wakfuli.py      <- DL items + actions + builds
    install_spells.py    <- Installe sorts extraits
    autopush.py          <- Git auto-commit + clean
  data/wakfuli/
    version.json         <- Version jeu (commitee)
    sync_report.json     <- Rapport sync (commite)
    spells_report.json   <- Rapport sorts (commite)
    spell_index.json     <- Index IDs (commite)
    all_items.json       <- 7686 items (gitignore)
    all_actions.json     <- 68 actions (gitignore)
    all_builds.json      <- 939 builds (gitignore)
    all_spells.json      <- 908 sorts (gitignore)
```

## Historique des sessions

### Session 2026-03-14 10:55
- Decouvert API Wakfuli (api.wakfuli.com/api/v1/)
- Cree sync_wakfuli.py : 7686 items, 68 actions, 939 builds
- Extrait 908 sorts (18 classes) via window.__SPELL_CACHE__
- Cree install_spells.py
- Lecon : PowerShell here-string obligatoire, MANIFEST avant tout fichier

## TODO

- [ ] .gitignore propre
- [ ] README.md
- [ ] Premier push GitHub propre
- [ ] Phase 3 : app.py builder universel
- [ ] Telecharger states.json depuis CDN Ankama
- [ ] UI style Wakfuli