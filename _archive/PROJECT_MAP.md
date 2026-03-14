# WAKFU VISION AUTOMATOR — PROJECT MAP
Mis à jour : 2026-03-07

## Ce que fait le projet
Outil d'automatisation visuelle pour WAKFU (jeu isométrique tour par tour).
Capture l'écran → reconnaît des éléments visuels (plantes, minerais) → clique automatiquement.
C'est un programme Windows externe, pas une modification du jeu.

## Stack technique
- Python 3.10
- DearPyGui (UI principale)
- OpenCV (template matching / détection)
- windows_capture (capture écran Windows Graphics Capture)
- mss + Pillow (screenshot secondaire)
- Architecture : ModuleBase + Hub (hub.py)

## Structure des fichiers
H:\Code\Ankama Dev\wakfu-optimizer\
  wakfu_vision.py              → V4 monolithique Tkinter (ABANDONNÉ, ne pas toucher)
  Vision\
    vision_automator_v5\
      hub.py                   → Point d'entrée : python -m vision_automator_v5.hub
      module_base.py           → Classe de base abstraite pour tous les modules
      module_registry.py       → Découverte automatique des modules
      shared\
        bus.py                 → EventBus (communication inter-modules)
        types.py
        constants.py
        logger.py
      modules\
        m01_capture\module.py  → Capture vidéo Windows Graphics Capture ✅ FONCTIONNEL
        m02_detection\module.py→ Template matching OpenCV ✅ FONCTIONNEL
        m08_sequencer\         → Séquenceur d'actions ✅ FONCTIONNEL
        m10_tagger\module.py   → Tagger templates v1.2.0 ✅ FONCTIONNEL
        m03_grid\ à m09_ai_brain\ → Stubs vides ❌ PAS DE MODULEBASE
    app\
      templates\               → Fichiers PNG des templates de détection
      config.json              → Dossiers/catégories/types persistés

## Contrat ModuleBase (à respecter pour tout nouveau module)
Méthodes abstraites obligatoires :
  - name (property) → str
  - version (property) → str
  - initialize(hub, config) → None
  - build_ui(parent) → None
Méthodes optionnelles :
  - description, icon, on_show, on_hide, cleanup
La classe doit s'appeler Module (ou exporter Module = MaClasse)

## Connexions importantes
- hub.py charge tous les modules via module_registry.py
- m01_capture émet → "frame.new" sur le bus
- m02_detection écoute → "frame.new", émet → "detection.results"
- m10_tagger émet → "detection.reload_templates" après sauvegarde d'un template
- m02_detection écoute → "detection.reload_templates" pour recharger les PNG

## Lancer l'application
cd "H:\Code\Ankama Dev\wakfu-optimizer\Vision"
python -m vision_automator_v5.hub

## GitHub
- Remote : https://github.com/Duperopope/wakfu-vision-automator.git
- Branche active : refactor/surface-tuner-v3
- Dernier commit : feat(m10_tagger) v1.2.0

## État actuel (2026-03-07)
- Hub ✅
- m01_capture ✅
- m02_detection ✅
- m08_sequencer ✅
- m10_tagger v1.2.0 ✅ : aperçu image, formulaire complet, historique, sauvegarde PNG
- m03 à m09 (sauf m08) ❌ stubs sans ModuleBase

## Prochaines étapes possibles
1. Module m11_library : naviguer et gérer les templates existants (affichage, suppression, renommage)
2. Améliorer m02_detection : affichage des résultats dans l'UI
3. Améliorer m08_sequencer : intégration avec m02_detection pour clics automatiques

## Règles de développement
- Pas de placeholders
- Toujours du code complet et fonctionnel
- Commandes terminal complètes
- Un seul fichier modifié à la fois
- Tester après chaque modification
- La classe module s'appelle toujours Module (exigé par module_registry.py)
