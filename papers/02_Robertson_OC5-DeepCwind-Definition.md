# Robertson, Jonkman, Wendt, Goupee, Dagher — Definition of the OC5 DeepCwind Semisubmersible Floating System

**Référence complète** : Robertson, A.; Jonkman, J.; Wendt, F. (NREL) ; Goupee, A.; Dagher, H.
(University of Maine). *Definition of the OC5 DeepCwind Semisubmersible Floating System*, version 1.5.
Document de définition du projet OC5 Phase II, IEA Wind Task 30. Hébergé sur le Wind Data Hub (WDH) :
`wdh.energy.gov/api/datasets/oc5/oc5.phase2/files/oc5.phase2.model.definition-semisubmersible-floating-
system-phase2-oc5-ver15.pdf`.

**Accès** : **texte intégral lu** (34 pages, PDF récupéré et rendu page par page). Toutes les valeurs
ci-dessous portent leur tableau/page source.

## Question posée
Fournir aux participants du projet OC5 Phase II les données nécessaires pour modéliser le système
semi-submersible DeepCwind tel que testé au bassin MARIN en 2013 (campagne utilisée pour OC5, distincte
de la campagne 2011 utilisée pour OC4) : géométrie, masses, ancrage, cas de charge.

## Système modélisé
Plateforme semi-submersible DeepCwind + éolienne « proche mais non identique » au NREL 5 MW (p.5) :
la turbine des essais 2013 (OC5) reproduit la poussée/couple/puissance du NREL 5 MW à l'échelle 1/50,
contrairement à la turbine des essais 2011 (OC4) qui n'était qu'une mise à l'échelle géométrique.
**Point de vigilance pour toute comparaison OC4 ↔ OC5** : ce n'est pas rigoureusement le même système.

## Outil et version
Non applicable (document de définition).

## Réglages hydro
Non traités dans ce document (purement géométrie/masse/ancrage/cas de charge ; les coefficients
hydrodynamiques/QTF sont dans les fichiers WAMIT associés, hors périmètre de cette fiche).

## Modèle d'ancrage
**Tableau 3-13, p.26** : 3 lignes caténaires (chaîne laiton), 120° entre lignes, profondeur 200 m,
rayon aux ancrages 837.6 m, rayon aux chaumards 40.868 m (profondeur chaumards 14 m), longueur non
tendue **835.5 m** (r-test : 835.35 m — écart de 0.15 m, négligeable, probablement un arrondi).
Diamètre équivalent-volume ≈ 0.137–0.140 m selon la ligne, masse linéique ≈ 125.4–125.8 kg/m, raideur
axiale équivalente EA ≈ 7.46–7.52×10⁸ N, prétension 1.107–1.148×10⁶ N (**Tableau 3-13, p.27**).
**Tableau 3-14/3-15, p.27-28** : essais statiques d'offset (surge et sway) comparant force mesurée au
bassin MARIN vs valeur « théorique » (modèle analytique) — directement réutilisable comme référence
de comparabilité pour notre transposition d'ancrage (LOT 3, une fois `/mnt/e` accessible).

## Géométrie et masse de la plateforme
**Tableau 3-9, p.23** : masse (avec ballast) 1.2919×10⁷ kg, CM à 14.09 m sous la SWL, inerties roll
7.5534×10⁹, pitch 8.2236×10⁹, yaw 1.3612×10¹⁰ kg·m². **Tableau 3-10/3-11, p.24-25** : tirant d'eau
20 m, colonne principale Ø6.5 m, colonnes latérales Ø12 m (longueur 26 m), colonnes de base Ø24 m
(longueur 6 m), pontons/croisillons Ø1.6 m — coordonnées complètes des 19 membres (Tableau 3-11).

## Cas de charge
**§4.2, p.30-33** : LC1.X (identification système/calibration), LC2.X (vent seul), LC3.X (houle seule),
LC4.X (vent+houle combinés). Pas de contrôle actif testé (**§3.6, p.29** : « no control applied »,
vitesse/pas/lacet constants) — important pour toute comparaison avec nos cas incluant un contrôleur.

## Résultats chiffrés clés
Essais statiques d'offset (Tableaux 3-14/3-15) donnant force vs déplacement en surge et en sway,
comparés à la théorie — base quantifiée directement réutilisable.

## Ce que le rapport dit explicitement ne pas couvrir
- p.5 : le système OC5 n'est PAS identique au système OC4 (turbine différente) — toute comparaison
  OC4/OC5 doit en tenir compte, ce n'est pas un simple raffinement du même modèle.
- p.26 : un faisceau de câbles de mesure suspendu à la tour crée une raideur/précharge additionnelle
  non mesurée par MARIN ; NREL l'approxime (ancrage homogène + raideur/précharge artificielle en surge).
- p.26 : hystérésis constatée dans le système d'ancrage pendant les essais — incertitude sur la
  position d'équilibre exacte.

## Reproductible avec nos moyens ?
**Oui pour l'ancrage** (LOT 3f/3h) : toutes les données nécessaires à une transposition MoorDyn/MAP++
sont ici, avec une référence quantifiée (Tableaux 3-14/3-15) pour juger l'écart. **Partiel pour le
système complet** : nécessiterait la turbine « proche du NREL 5MW » spécifique à OC5 (non modélisée
dans ce dépôt, qui utilise le NREL 5MW standard du cas r-test) — à signaler dans `models/oc5/NOTE.md`.
