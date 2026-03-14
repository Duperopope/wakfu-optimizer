# Archive Scripts Legacy
> Deplace le 2026-03-14 18:43:58
> Ces scripts ont servi a la phase de reverse-engineering du client Wakfu

## Contexte
Avant d'utiliser l'API Wakfuli, le projet a necessite :
- Decompilation du client Java Wakfu (decompile_client.py)
- Parsing des formats binaires (bdata_reader_final.py, bdata_diagnostic_v5.py)
- Extraction des donnees CDN Ankama (download_and_parse_items.py, data_sync.py)
- Analyse des effets et sorts (analyse_effects.py, parse_effects_*.py)
- Calibration du moteur de degats avec tests in-game (calibrate_v2.py)
- Bootstrap d'une UI NiceGUI (bootstrap.py) - remplace par Next.js

## Pourquoi archives
L'API Wakfuli (api.wakfuli.com) fournit desormais toutes les donnees necessaires.
Ces scripts restent disponibles pour reference ou verification croisee.

## Scripts actifs (restes dans scripts/)
- autopush.py : auto-commit + push + nettoyage
- sync_wakfuli.py : sync items/actions/builds depuis API Wakfuli
- install_spells.py : installation des sorts
- build_memory.py : generateur PROJECT_MEMORY (legacy mais fonctionnel)
