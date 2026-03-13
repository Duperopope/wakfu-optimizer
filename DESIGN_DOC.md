# WAKFU THEORYCRAFTER V5 - DESIGN DOCUMENT
# Mecanique de combat complete
# Date: 2026-03-13
# Statut: VALIDE - Sources officielles integrees
#
# Sources:
#   MethodWakfu: https://methodwakfu.com/bien-debuter/informations-generales/
#   WakfuCalc (Ectawem): https://sites.google.com/view/wakfucalc/en/guides/formulas
#   Patch 1.91: https://www.wakfu.com/en/mmorpg/news/patch-notes/1767730-update-1-91/details
#   Wiki Damage: https://wakfu.fandom.com/wiki/Damage


# ============================================================
# PARTIE 1 - GRILLE ET POSITIONNEMENT
# ============================================================

## 1.1 Terrain
# Grille 2D de cases (taille variable selon le donjon)
# Types de cases: vide, occupee, obstacle, trou, glyphe, piege, mecanisme
# Obstacles: bloquent mouvement ET ligne de vue
# Trous: infranchissables sauf teleportation
# Cases speciales de donjon: bonus/malus/buffs/debuffs specifiques

## 1.2 Ligne de vue (LdV)
# Necessaire sauf sorts marques "sans LdV" (oeil barre)
# Bloquee par: obstacles, combattants
# Invisible NE bloque PAS la LdV
# Calcul: tracage de ligne entre lanceur et cible

## 1.3 Portee
# Portee de base du sort (min-max)
# Proprietes independantes:
#   - Modifiable ou non par bonus/malus de PO
#   - En ligne obligatoire ou non
#   - Necessite LdV ou non
#   - Lancable sur soi (DISTINCT de portee min 0)
#     -> portee 1-4 + lancable sur soi: retrait 5 PO => portee 1 + sur soi
#     -> portee 0-4: retrait 5 PO => portee 0 seulement
# Source: MethodWakfu section 2.1

## 1.4 Orientation (Face / Cote / Dos)
# Chaque combattant regarde N/S/E/W
# Multiplicateurs de degats (ce sont des %df, pas des %di):
#   Face = x1.0
#   Cote = x1.1
#   Dos  = x1.25
# Impact sur le tacle (voir section 5)
# Sorts modifiant l'orientation: Effroi, Diversion, pieges


# ============================================================
# PARTIE 2 - ORDRE DES TOURS ET TEMPS
# ============================================================

## 2.1 Initiative
# Equipe avec la moyenne d'initiative la plus haute joue en premier
# Au sein d'une equipe: ordre decroissant d'initiative
# Alternance: A1 > B1 > A2 > B2 > A3 > B3 > ...
# Si equipe A a moins de combattants: les restants de B jouent a la suite
# Ordre FIXE pour tout le combat
#   Mort = retire de la chaine
#   Resurrection = retour a sa place initiale
# Invocations jouent juste apres l'invocateur
# Source: MethodWakfu section 1.3

## 2.2 Temps de tour
# Base: 30s + 0.5s par PA/PM possede en debut de tour
# Premier tour: +30s bonus
# Tour avec bonus velocite: +30s
# Temps non utilise reporte au tour suivant (max 90s)
# Formule max: personnage 12PA 6PM = 30 + 0.5*(12+6) = 39s base
#   Max report: 39 + 90 = 129s normal, 159s avec velocite
# Source: MethodWakfu section 1.2

## 2.3 Bonus de velocite (CONFIRME - captures d'ecran Sam)
# Apparait tous les 3 tours
# Le joueur dont c'est le tour CHOISIT 1 bonus parmi 6 OU passe
# Bonus choisi = GRISE pour les coequipiers jusqu'a prochaine apparition
# UNIQUEMENT joueurs, monstres n'y ont PAS acces
# En PvP chaque equipe a son propre set
# Actions automatiques des monstres en debut de tour: AVANT le bonus velocite
#
# Les 6 bonus (CONFIRMES):
#   1. Prevention: +20% PV max en Armure
#   2. Ancrage: Stabilise + ennemis au contact: -2 PM max
#   3. Meditation: +1 PW
#   4. Brasier: Applique Embrasement aux ennemis (degats feu)
#   5. Liberation: Repousse de 2 cases allies et ennemis au contact
#   6. Engouement: +2 PA pour le tour
#
# NOTE SRAM: Solo = acces aux 6. Engouement pour burst, Prevention pour
# synergie Rupture PA/Temerite, Ancrage pour verrouiller au contact.


# ============================================================
# PARTIE 3 - FORMULE DE DEGATS COMPLETE
# ============================================================

## 3.1 Degats directs (Source: WakfuCalc + MethodWakfu 2.2)
#
# Degats = (((Base * (1 + Sigma_Mastery/100) * Orientation * Crit
#            * (1 + Sigma_DI/100) * (1 - %Res/100))
#            + Degats_fixes)
#            - Barriere)
#            * Coeff_Blocage
#            * Produit(%df)
#
# NOTE: les %df sont des multiplicateurs SEPARES, pas additifs aux %di.
# L'orientation et le crit sont techniquement des %df.

## 3.2 Sigma_Mastery (somme additive)
# + Maitrise elementaire correspondant a l'element du sort
#   (ou la plus haute pour Lumiere/Stasis)
# + Maitrise melee si cible a 1-2 cases OU Maitrise distance si >= 3 cases
# + Maitrise berserk si lanceur <= 50% PV max
# + Maitrise dos si lanceur regarde le dos de la cible
# + Maitrise critique si coup critique
# Source: WakfuCalc "Sum of relevant masteries"

## 3.3 Sigma_DI (somme additive des %di)
# + %di du personnage (fiche)
# + %di conditionnels (distance, melee, zone, monocible, etc.)
# + %dommages recus de la cible (additif avec %di du lanceur!)
# + %di indirects si degats indirects
# + Echauffe de la cible (+30% dommages indirects recus) si indirect
# Plancher: %di totaux ne peuvent pas descendre sous -50%
#   (sauf Theorie de la Matiere: -100%)
#   Les %di conditionnels s'ajoutent APRES le plancher
# Source: MethodWakfu section 2.2

## 3.4 Resistance
# %Res = 1 - 0.8^(Res_flat / 100)  (arrondi vers le bas)
# Res_flat = Res_elementaire + Res_critique(si crit) + Res_dos(si dos)
# Cap joueurs/invocations: 90% (atteint a 1032 flat)
# Monstres: PAS de cap
# Retrait de resistances par joueurs: max -200
# Les pertes de res dues aux mecaniques de monstres ne comptent pas
# Source: MethodWakfu section 1.1, WakfuCalc "Resistances"

## 3.5 Blocage
# Non bloque: x1.0
# Bloque: x0.80
# Bloque + sublimation Expert du Blocage: x0.68
# Le % blocage est une stat du personnage
# Certains degats (indirects, non-reductibles) ne peuvent pas etre bloques
# Source: WakfuCalc "Block coefficient"

## 3.6 %df (dommages finaux) - multiplicateurs SEPARES
# Chaque source est un multiplicateur independant: Produit(%df) = (1+df1/100) * (1+df2/100) * ...
# Sources connues pour le Sram:
#   - Orientation (x1.0 / x1.1 / x1.25)
#   - Coup critique (x1.25)
#   - Traumatisme: +% selon PF consommes
#   - Mise a Mort: +% selon PF consommes
#   - Isole: +50% (x1.5)
#   - Multiplicateur de difficulte du donjon
# Source: MethodWakfu section 2.2

## 3.7 Degats indirects (poisons, pieges, glyphes)
# Meme formule generale MAIS:
#   - Calcul base sur les stats AU MOMENT du proc (pas du lancer)
#   - La plupart ignorent l'orientation (pas de Maitrise Dos, pas de Res Dos)
#   - %di indirects s'ajoutent aux %di
#   - Ne peuvent generalement pas etre bloques ni reduits par la barriere
#   - Peuvent traverser les armures et les invulnerabilites
# Source: WakfuCalc "Indirect damage"

## 3.8 Sequencement des effets
# Les effets d'un sort sont appliques DANS L'ORDRE DE LA DESCRIPTION
# Exemple: poussee avant degats peut casser la melee
# Exemple: gain d'armure apres degats = pas de protection contre riposte
# CRUCIAL pour le simulateur: on doit respecter l'ordre des effets
# Source: MethodWakfu section 2.1


# ============================================================
# PARTIE 4 - RESSOURCES
# ============================================================

## 4.1 Points d'Action (PA)
# Max hors combat: 16
# Depassable en combat via buffs, passifs, sublimations, velocite
# Recuperables via kills, passifs, sublimations

## 4.2 Points de Mouvement (PM)
# Max hors combat: 8
# 1 PM = 1 case de deplacement
# Depassable via buffs (Galopade +3 PM max)

## 4.3 Points de Wakfu (PW)
# Max hors combat: 20
# Utilises pour sorts speciaux

## 4.4 Point Faible (PF) - Specifique Sram
# Jauge 0-100
# +5 par PA de sort elementaire lance
# Consomme par: Mise a Mort, Traumatisme, Arnaque, Effroi
# Tous les 25 PF consommes: +1 AP, +1 MP, +1 WP, +10 Hemorrhagie

## 4.5 Points de Vie (PV)
# Formule: (50 + Niveau * 10 + PV_flat) * (1 + %PV/100)
# Tous les %PV sont additifs entre eux
# Tous les PV flat sont affectes par les %PV
# Source: WakfuCalc "HP", MethodWakfu section 2.2

## 4.6 Armure
# Cap joueur: 50% PV max
# Cap invocations: 100% PV max
# Monstres ennemis: PAS de cap
# Non affectee par les Maitrises
# Affectee par: % Armure Donnee (aux autres) + % Armure Recue (de tous)
# Crit x1.25 s'applique a l'armure
# Friable: multiplicateur separe (10% par niveau, remplace si superieur)
# Source: MethodWakfu section 2.3, WakfuCalc "Armors"


# ============================================================
# PARTIE 5 - TACLE, ESQUIVE, RETRAITS
# ============================================================

## 5.1 Tacle/Esquive - Mecanique
# Declenche quand un combattant quitte une case adjacente a un ennemi
# Max pertes selon niveau de l'esquiveur:
#   Niv 1-49:   2 PM, 2 PA
#   Niv 50-99:  3 PM, 3 PA
#   Niv 100+:   4 PM, 4 PA
# Echelle de pertes: 0 > 1PM > 1PM1PA > 2PM1PA > 2PM2PA > 3PM2PA > 3PM3PA > 4PM3PA > 4PM4PA

## 5.2 Formule exacte (WakfuCalc)
# L = La + Lb/2 + Lc/3 + Ld/4 (tacles adjacents, poids decroissant)
# Si L < 0: L = 0  ;  Si Dodge < 0: Dodge = 0
# X = (7/3) * (L - Dodge) / (L + Dodge)
# Y = floor((X + 1) * 4 * FacteurOrientation)  [borne 0 a 8 pour niv 100+]
# FacteurOrientation:
#   2 si TOUS les tacleurs montrent leur dos
#   1 si au moins un tacleur montre son cote
#   0 si au moins un tacleur fait face
# Perte PM = ceil(Y / 2)
# Perte PA = floor(Y / 2)
# Source: WakfuCalc "MP/AP losses based on Lock and Dodge"

## 5.3 Orientation du tacleur (reduction du max)
# Face: pleine efficacite
# Cote: max reduit de 1 PA
# Dos: max reduit de 1 PM et 1 PA
# Niv 100+ de face: max 4PM 4PA ; de cote: 4PM 3PA ; de dos: 3PM 3PA

## 5.4 Seuils (face)
# Esquive >= 1.95x Tacle: aucune perte
# Tacle >= 1.95x Esquive: 4 PM 3 PA
# Tacle >= 2.5x Esquive: 4 PM 4 PA (max)

## 5.5 Retraits PA/PM (Volonte)
# FF = (1 + Vol_lanceur/100) * (Vol_cible/100)  ;  borne [0, 2]
# Retrait effectif = Base_retrait * 0.5 * FF
# Partie decimale = % chance d'arrondir au superieur
# A Volonte egale: 50% du retrait
# +100 Vol lanceur: 100% du retrait
# -100 Vol lanceur: 0% du retrait
# Chaque PA/PM retire donne +10 Volonte a la cible (reset fin de son tour)
# Collision: tente de retirer 1 PA (affecte par Volonte)
# Retraits PA max / PM max / PO: PAS affectes par Volonte
# Source: MethodWakfu section 2.7, WakfuCalc "AP/MP removals"


# ============================================================
# PARTIE 6 - SOINS ET RESISTANCE SOIN
# ============================================================

## 6.1 Formule de soin (WakfuCalc)
# Soin = Base * (1 + Sigma_Mastery_Soin/100) * Crit
#        * (1 + (% Soins Realises + % Soins Recus)/100)
#        * (1 - % Resistance Soin/100)
#        * (1 - Incurable*10%/100)
#
# Sigma_Mastery_Soin: comme degats SAUF Maitrise Dos exclue + Maitrise Soin incluse
# Vol de Vie: ignore % Soins et Maitrise Soin
# Soins en % de PV: ignorent Maitrises et % Soins

## 6.2 Resistance Soin
# +1% par 5% PV max soignes (ou proportionnel pour petits soins)
# Multiplicateur separe (pas additif aux % Soins)
# 100% resistance soin = soins reduits a 0
# Seulement joueurs, PAS les monstres
# Source: MethodWakfu section 2.4, WakfuCalc "Heal Resistance"

## 6.3 Incurable / Friable
# Incurable N: reduit soins de N*10% (multiplicateur separe)
# Friable N: reduit armure de N*10% (multiplicateur separe)
# Ne s'empilent PAS: si nouveau > existant, REMPLACE; sinon rien
# Source: MethodWakfu section 2.5


# ============================================================
# PARTIE 7 - ETATS ET BUFFS/DEBUFFS
# ============================================================

## 7.1 Stabilise / Destabilise
# Stabilise empeche: poussee, attirance, charge, teleportation, swap, changement d'orientation
# Autorise: la marche uniquement
# Certains sorts deviennent inutilisables (ex: teleport sur case vide)
# Destabilise: immunite a Stabilise par la meme equipe pendant 3 tours
# Les deux equipes ont des compteurs independants
# Source: MethodWakfu section 2.8

## 7.2 Invisible
# Non ciblable
# +1 Esquive
# Ne bloque PAS la LdV
# Brise par: degats directs, sorts >= 4 PA (avec Retenue), lancer, KO

## 7.3 Echauffe
# +30% dommages indirects recus (additif avec %di indirects)

## 7.4 Etats Sram specifiques
# Meurtrier: le Sram a tue ce tour (1 tour)
# Point Faible: jauge 0-100
# Hemorrhagie: +1% degats par niveau (max 40, dure 2 tours)
# Hemophilie: poison debut de tour converti depuis Hemorrhagie
# Maitre des Ombres: +100% DI au prochain sort de degats directs
# Apparent: ne peut plus etre Invisible (3 tours)
# Marque Letale: sur kill -> +2 PA + transfert Hemorrhagie
# Saignee Mortelle: replique du sort au prochain tour


# ============================================================
# PARTIE 8 - IA DES MONSTRES
# ============================================================

## 8.1 Comportement general (Source: MethodWakfu section 1.4)
# Preferent taper les joueurs les plus fragiles (resistances basses)
# Preferent taper de dos > cote > face
# Preferent zone multi-cibles plutot que cible isolee
# Pas 100% previsible (parfois aller-retour inutiles, ou tour passe)
# Actions automatiques debut de tour: AVANT le bonus de velocite


# ============================================================
# PARTIE 9 - MECANIQUES DE BOSS
# ============================================================

## 9.1 Patterns communs
# Phases d'invulnerabilite (1 tour tous les X tours)
# Changement de resistances selon phases
# Mecaniques d'orientation obligatoire
# Invocations supplementaires
# Zones dangereuses (glyphes, cases piege)
# Bonus/malus conditionnels

## 9.2 Mecaniques specifiques
# Invulnerabilite conditionnelle (ex: sauf de dos)
# Riposte sur coup recu
# Teleportation sur coup recu (contrable avec Stabilise!)
# Armure regenerable
# Resurrection de mobs
# Enrage progressif
# Cap de degats par tour
# Multiplicateur de difficulte du donjon (%df)


# ============================================================
# PARTIE 10 - SUBLIMATIONS ET EQUIPEMENT (universel)
# ============================================================

## 10.1 Sublimations pertinentes (L'Immortel)
# Rupture PA (Niv.4): perte Armure ennemi -> +2 PA (2 activations/tour)
# Rupture Violente (Niv.4): perte Armure -> degats lumiere 40% niveau (2 act/tour)
# Temerite (Niv.4): retirer toute l'armure -> +12% DI reste du tour (max 30%)
# Influence Lente (Niv.2): +2% CC par tour (max 30%)

## 10.2 Reliques
# Dofus Ivoire: +200% du niveau en mastery au 1er coup par element/tour
# Par-dela la barriere: +15% DI crit si sort >= 4 PA, +15% DI crit si sort >= 1 PW

## 10.3 Statistiques d'equipement a condition
# Equipement RESTE equipe si condition invalidee EN COMBAT
# Condition negative %cc: plancher -9%cc hors combat
# Familiers/montures: doivent etre en vie pour donner les stats


# ============================================================
# PARTIE 11 - FORMULES UTILITAIRES
# ============================================================

## 11.1 EHP (Effective Hit Points)
# EHP = (HP * 10000) / ((100 - %Res) * (100 - (1 - Coeff_Blocage) * %Blocage))
# Source: WakfuCalc "EHP"

## 11.2 EM (Effective Masteries)
# EM = ((Sigma_Mastery + 100) * (Sigma_%DI + 100) / 10000) - 100
# EMcrit = (((Sigma_Mastery_avec_crit + 100) * (Sigma_%DI_avec_crit_di + 100) / 10000) * 1.25) - 100
# EM_moyen = EM + ((EMcrit - EM) * %CC)
# Source: WakfuCalc "EM"

## 11.3 Conversion resistance
# %Res = 1 - 0.8^(flat/100)  (arrondi inf)
# flat = 100 * log(1 - %Res/100) / log(0.8)  (arrondi sup)


# ============================================================
# PARTIE 12 - PRIORITE D'IMPLEMENTATION
# ============================================================

## Phase 1 - Moteur de base (EN COURS)
# [x] Formule de degats officielle (engine/damage.py) - TESTE OK
# [x] Donnees de classe Sram completes (data/classes/sram.py)
# [x] Passifs et sorts communs (data/classes/common.py)
# [x] Profil joueur L'Immortel (data/profiles/limmortel.py)
# [x] Logging automatique (utils/changelog.py + scripts/auto_log.py)
# [x] DESIGN_DOC.md complet et source
# [ ] Mise a jour engine/damage.py avec: res critique, res dos, blocage,
#     degats fixes, barriere, %dommages recus cible
# [ ] Combattant en combat (engine/fighter.py)
# [ ] Grille simplifiee (engine/grid.py)
# [ ] Boucle de combat (engine/combat.py)

## Phase 2 - Combat realiste
# [ ] Initiative et ordre des tours (section 2.1)
# [ ] Tacle/Esquive avec formule exacte (section 5.2)
# [ ] Ligne de vue
# [ ] Portee, contraintes de sorts, lancable sur soi
# [ ] Retraits PA/PM/PO avec Volonte (section 5.5)
# [ ] Bonus de velocite (section 2.3)
# [ ] Blocage (section 3.5)
# [ ] Sequencement des effets de sort (section 3.8)

## Phase 3 - Mecaniques avancees
# [ ] Invisibilite + Maitre des Ombres
# [ ] Double complet (sous-tour, sorts, interaction Isole)
# [ ] Pieges (placement, declenchement, refund)
# [ ] Hemorrhagie complete + Hemophilie
# [ ] Sublimations (Rupture PA, Rupture Violente, Temerite, Influence Lente)
# [ ] Soins + Resistance Soin (section 6)
# [ ] Armure complete avec Friable (section 4.6)
# [ ] Degats indirects (section 3.7)

## Phase 4 - Donjons et boss
# [ ] Mecaniques de boss specifiques
# [ ] Terrain avec obstacles
# [ ] Cases speciales
# [ ] IA des monstres (section 8)

## Phase 5 - Optimiseur
# [ ] Generateur de loadouts (sorts + passifs)
# [ ] Simulation parallele (~15 workers)
# [ ] Scoring multi-combat (EHP + EM)
# [ ] Export des resultats
# [ ] Recuperation objets/sorts depuis fichiers du jeu ou API
