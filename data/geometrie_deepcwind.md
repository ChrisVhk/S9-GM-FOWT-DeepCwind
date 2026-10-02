# Géométrie de la plateforme OC4-DeepCwind

Source : `papers/02_...` (document de définition OC5, Tableaux 3-10 et 3-11 — la géométrie du
flotteur n'a pas changé entre OC4 et OC5, seule la turbine diffère, cf la même fiche p.5).

## Dimensions principales (Tableau 3-10)

| Grandeur | Valeur |
|---|---|
| Tirant d'eau (profondeur du bas de la plateforme sous la SWL) | 20 m |
| Élévation de la colonne centrale (base de la tour) au-dessus de la SWL | 10 m |
| Élévation des colonnes déportées au-dessus de la SWL | 12 m |
| Entraxe entre colonnes déportées | 50 m |
| Longueur des colonnes supérieures (déportées) | 26 m |
| Longueur des colonnes de base | 6 m |
| Diamètre de la colonne centrale | 6,5 m |
| Diamètre des colonnes déportées (partie supérieure) | 12 m |
| Diamètre des colonnes de base | 24 m |
| Diamètre des pontons et croisillons (entretoises) | 1,6 m |

## Membres et coordonnées (Tableau 3-11, repère inertiel, origine au centre de la plateforme)

| Membre | Abrév. | Début (X,Y,Z) | Fin (X,Y,Z) | Longueur (m) |
|---|---|---|---|---|
| Colonne centrale | MC | (0, 0, -20) | (0, 0, 10) | 30 |
| Colonne déportée 1 | UC1 | (14,43, 25, -14) | (14,43, 25, 12) | 26 |
| Colonne déportée 2 | UC2 | (-28,87, 0, -14) | (-28,87, 0, 12) | 26 |
| Colonne déportée 3 | UC3 | (14,43, -25, -14) | (14,43, -25, 12) | 26 |
| Colonne de base 1 | BC1 | (14,43, 25, -20) | (14,43, 25, -14) | 6 |
| Colonne de base 2 | BC2 | (-28,87, 0, -20) | (-28,87, 0, -14) | 6 |
| Colonne de base 3 | BC3 | (14,43, -25, -20) | (14,43, -25, -14) | 6 |
| Ponton delta sup. 1 | DU1 | (9,20, 22, 10) | (-23,67, 3, 10) | 38 |
| Ponton delta sup. 2 | DU2 | (-23,67, -3, 10) | (9,20, -22, 10) | 38 |
| Ponton delta sup. 3 | DU3 | (14,43, -19, 10) | (14,43, 19, 10) | 38 |
| Ponton delta inf. 1 | DL1 | (4, 19, -17) | (-18,47, 6, -17) | 26 |
| Ponton delta inf. 2 | DL2 | (-18,47, -6, -17) | (4, -19, -17) | 26 |
| Ponton delta inf. 3 | DL3 | (14,43, -13, -17) | (14,43, 13, -17) | 26 |
| Entretoise (Y) sup. 1 | YU1 | (1,625, 2,815, 10) | (11,43, 19,81, 10) | 19,62 |
| Entretoise (Y) sup. 2 | YU2 | (-3,25, 0, 10) | (-22,87, 0, 10) | 19,62 |
| Entretoise (Y) sup. 3 | YU3 | (1,625, -2,815, 10) | (11,43, -19,81, 10) | 19,62 |
| Entretoise (Y) inf. 1 | YL1 | (1,625, 2,815, -17) | (8,4, 14,6, -17) | 13,62 |
| Entretoise (Y) inf. 2 | YL2 | (-3,25, 0, -17) | (-16,87, 0, -17) | 13,62 |
| Entretoise (Y) inf. 3 | YL3 | (1,625, -2,815, -17) | (8,4, -14,6, -17) | 13,62 |
| Croisillon (cross brace) 1 | CB1 | (1,625, 2,815, -16,2) | (11,43, 19,81, 9,13) | 32,04 |
| Croisillon 2 | CB2 | (-3,25, 0, -16,2) | (-22,87, 0, 9,13) | 32,04 |
| Croisillon 3 | CB3 | (1,625, -2,815, -16,2) | (11,43, -19,81, 9,13) | 32,04 |

## Masse et inerties (Tableau 3-9)

| Grandeur | Valeur |
|---|---|
| Masse de la plateforme, avec lest | 1,2919×10⁷ kg |
| Centre de masse sous la SWL | 14,09 m |
| Inertie en roulis (autour du CM) | 7,5534×10⁹ kg·m² |
| Inertie en tangage (autour du CM) | 8,2236×10⁹ kg·m² |
| Inertie en lacet (autour du CM) | 1,3612×10¹⁰ kg·m² |

## Ancrage (Tableau 3-13)

| Grandeur | Valeur |
|---|---|
| Nombre de lignes | 3, à 120° |
| Profondeur (ancrages) | 200 m |
| Profondeur des chaumards | 14 m |
| Rayon des ancrages depuis le centre | 837,6 m |
| Rayon des chaumards depuis le centre | 40,868 m |
| Longueur non tendue de chaque ligne | 835,5 m |
| Diamètre équivalent-volume | 0,137-0,140 m (selon la ligne) |
| Masse linéique | 125,4-125,8 kg/m (selon la ligne) |
| Raideur axiale équivalente (EA) | 7,46-7,52×10⁸ N (selon la ligne) |
| Prétension (à l'équilibre, position non déplacée) | 1,107-1,148×10⁶ N (selon la ligne) |

**Charge de rupture de la ligne : OUVERT.** Aucune des sources actuellement en main ne la donne
directement — à compléter (LOT H si le document FEAMooring ou un manuel de ligne de mouillage est
déposé), ou à calculer par une formule usuelle (ex. contrainte de rupture de la chaîne × section),
**marquée explicitement « hypothèse »** si aucune source directe n'est trouvée.

## Vérifier dans le modèle du dépôt

Ces mêmes valeurs sont dans `models/oc4_rtest/5MW_OC4Semi_WSt_WavesWN/
NRELOffshrBsline5MW_OC4DeepCwindSemi_HydroDyn.dat` (section MEMBER JOINTS / MEMBER CROSS-SECTION
PROPERTIES) et `.../NRELOffshrBsline5MW_OC4DeepCwindSemi_MoorDyn.dat` (section POINTS / LINES) —
c'est l'exercice du classeur d'architecture (phase 0, séance 0b).
