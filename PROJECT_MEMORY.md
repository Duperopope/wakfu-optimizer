# PROJECT MEMORY - Wakfu Optimizer

> Derniere mise a jour : 2026-03-14 14:45:00
> Memoire persistante entre sessions Claude
> GitHub : https://github.com/Duperopope/wakfu-optimizer

## WORKFLOW CLAUDE - A LIRE EN PREMIER

### Protocole de travail
1. Toujours lire GitHub (raw files) avant de proposer du code
2. Ne jamais demander a Sam de copier-coller des resultats - lire le repo
3. Donner des blocs PowerShell complets a executer, sans placeholder
4. autopush.py pousse automatiquement sur GitHub toutes les 2min environ
5. Apres chaque bloc, verifier sur GitHub que les changements sont arrives
6. Mettre a jour ce fichier a chaque etape significative
7. Decouper les gros blocs en commandes separees (eviter les coupures)
8. Toujours verifier les URLs CDN avant de les utiliser dans le code

### URLs essentielles pour Claude
- Repo : https://github.com/Duperopope/wakfu-optimizer
- Raw files : https://raw.githubusercontent.com/Duperopope/wakfu-optimizer/main/{path}
- Commits : https://api.github.com/repos/Duperopope/wakfu-optimizer/commits?per_page=5
- API Wakfuli : https://api.wakfuli.com/api/v1/items?page=1&limit=1

### Stack technique
- Frontend : Next.js 16.1.6 / React 19.2.3 / Tailwind CSS 4 / TypeScript 5
- Backend data : Python (sync_wakfuli.py, install_spells.py, build_memory.py)
- Deploiement : Local (npm run dev sur port 3000)
- Autopush : scripts/autopush.py (auto-commit + push toutes les 2min)
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
