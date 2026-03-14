# CHANGELOG - wakfu-optimizer
> Archive long terme de toutes les sessions de travail
> Chaque entree pointe vers les commits GitHub correspondants
> Repo : https://github.com/Duperopope/wakfu-optimizer

---

## [2026-03-14] Session LeftPanel v5 - Icones et design
> Mise a jour : 2026-03-14 18:33:58
> Commits : https://github.com/Duperopope/wakfu-optimizer/commits/main

### Ce qui a ete fait
- LeftPanel.tsx reecrit pour utiliser useBuild (fix runtime error)
- FEROCITY renomme en % Coup Critique
- Remplacement des icones SVG generiques par PNG custom pour les 3 bonus :
  - Guilde (tree.png 1735 bytes)
  - Havre-Monde (gem.png 805 bytes 37x39px)
  - Monture (mount.png)
- Telechargement des 28 icones stats depuis cdn.wakfuli.com/stats/ vers /icons/stats/
- Ajout barre priorite elementaire draggable (Feu/Eau/Terre/Air) avec drag-and-drop HTML5
- Implementation boutons : Copier JSON, Lien partageable (base64), Visibilite (cycle), Favori (localStorage)
- Bouton Enchantements toggle
- iconScale individuel par bonus pour gerer les tailles differentes
- Nombreuses iterations sur le sizing des icones bonus (conteneur CSS limitait la taille)

### Fichiers modifies
- frontend/src/components/builder/LeftPanel.tsx (reecrit v5)
- frontend/public/icons/bonuses/tree.png (cree)
- frontend/public/icons/bonuses/gem.png (cree)
- frontend/public/icons/bonuses/mount.png (cree)
- frontend/public/icons/stats/*.webp (28 fichiers crees)

### Problemes identifies non resolus
- gem.png pixelise (37x39px) compense par iconScale 2.0 mais idealement a recreer en 64x64+
- Icones classes toujours chargees depuis CDN distant
- Priorite elementaire pas connectee a computeStats

---

## [2026-03-14] Session initiale - Setup et corrections
> Commits : https://github.com/Duperopope/wakfu-optimizer/commits/main

### Ce qui a ete fait
- Mise en place du BuilderLayout (split 30/70 draggable)
- ClassSelector avec modal + LevelEditor
- RightPanel avec onglets items et enchantements fonctionnels
- BuildContext avec computeStats
- Correction couleurs raretes (classes CSS explicites pour Tailwind 4)
- Fix chevauchement niveau/classe (stopPropagation)
- Fix icone WP cassee (WAKFU_POINT -> WP)
- Fix images items (cdn.wakfuli.com/items/{image_id}.webp)
- Sync 7686 items, 908 sorts, 939 builds depuis API Wakfuli

### Fichiers modifies
- frontend/src/components/builder/BuilderLayout.tsx
- frontend/src/components/builder/LeftPanel.tsx
- frontend/src/components/builder/RightPanel.tsx
- frontend/src/components/builder/ClassSelector.tsx
- frontend/src/lib/BuildContext.tsx
- frontend/src/app/globals.css

---

> Pour ajouter une entree, copier le template ci-dessous en haut de la liste :
>
> ## [DATE] Titre de la session
> > Mise a jour : DATE HEURE (Get-Date)
> > Commits : https://github.com/Duperopope/wakfu-optimizer/commits/main
> ### Ce qui a ete fait
> ### Fichiers modifies
> ### Problemes identifies non resolus
