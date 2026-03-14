# ARCHITECTURE - wakfu-optimizer
> Inventaire detaille du projet - consulter uniquement si necessaire
> Mis a jour : 2026-03-14 18:48:56

## Structure des dossiers

### frontend/ (app Next.js ACTIVE - c est la qu on travaille)
Composants builder dans frontend/src/components/builder/ :
- BuilderLayout.tsx : layout 2 panneaux draggable (30/70)
- LeftPanel.tsx v5 : stats, bonus, priorite elementaire, enchantements
- RightPanel.tsx : items (filtre/equip), enchants (runes)
- ClassSelector.tsx : selection classe + level
Contexte dans frontend/src/lib/ :
- BuildContext.tsx : etat du build, computeStats
- useWakfuData.ts : hook chargement JSON
- wakfu.ts : types, constantes
Assets dans frontend/public/ :
- icons/stats/*.webp (28 icones)
- icons/bonuses/*.png (3 icones custom)
- data/*.json (copies de data/wakfuli/)

### engine/ (moteur combat Python LEGACY - non utilise par le frontend)
Simulateur de combat Sram complet : degats, double, invisibilite, grille hex.
Contient les FORMULES DE REFERENCE pour les calculs de degats Wakfu.
10 fichiers, 263 Ko total. Lire si besoin de comprendre les mecaniques de combat.

### scripts/ (4 actifs sur 45)
ACTIFS : autopush.py, sync_wakfuli.py, install_spells.py, build_memory.py
LEGACY : 41 scripts de reverse-engineering (copies dans archive/scripts_legacy/)

### data/
- data/wakfuli/ : SOURCE ACTIVE (API Wakfuli) - items, builds, spells, actions
- data/raw/ + data/extracted/ + data/parsed/ : ANCIEN systeme CDN Ankama
- data/classes/ + data/profiles/ : classes Python legacy (Sram, L Immortel)

### decompiled/ (332 fichiers Java decompiles du client Wakfu)
Code source du wakfu-client.jar obtenu par decompilation avec CFR.
Organise en : key_classes/, items/, states/, effects_real/
Gros fichiers de reference : aTN.java (544Ko), cKV.java (1Mo), eHr.java (236Ko)

### reference/ (758 fichiers scrapes de wakfuli.com)
JS source, CSS, images items, fonts. Fichier cle : assets/js/25c3dbf546a727d1.js

### Autres
- app.py : ancienne UI NiceGUI (abandonnee)
- logs/ : logs de sync et debug
- tools/cfr.jar : decompilateur Java
- archive/ : scripts legacy copies
- tests/ + utils/ : tests et utilitaires
