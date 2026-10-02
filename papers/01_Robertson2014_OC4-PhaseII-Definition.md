# Robertson et al. (2014) — Definition of the Semisubmersible Floating System for Phase II of OC4

**Référence complète** : Robertson, A.; Jonkman, J.; Masciola, M.; Song, H.; Goupee, A.; Coulling, A.;
Luan, C. *Definition of the Semisubmersible Floating System for Phase II of OC4*. NREL/TP-5000-60601,
National Renewable Energy Laboratory, septembre 2014, 43 p. DOI: 10.2172/1155123. OSTI ID 1155123.

**Accès** : métadonnées et résumé obtenus via la fiche OSTI (osti.gov/biblio/1155123). Le PDF complet
est hébergé sur `nrel.gov`/`docs.nrel.gov`, domaines **inaccessibles depuis cette session** (échec DNS
répété, `ENOTFOUND`). Une tentative de récupération du lien de téléchargement OSTI a renvoyé une
redirection vers un domaine `nlr.gov` qui n'est PAS le domaine officiel (`nrel.gov`) — anomalie notée,
non suivie par prudence. **Texte intégral non lu** ; cette fiche ne porte donc que ce que l'abstract
et les documents dérivés (OC5 definition, ci-dessous) rapportent explicitement.

## Question posée
Documenter les spécifications du système flottant semi-submersible (conception DeepCwind) nécessaires
aux participants du projet OC4 Phase II pour construire des modèles aéro-hydro-servo-élastiques
cohérents entre eux (étude de comparaison de codes, pas de validation contre essai à ce stade).

## Système modélisé
Plateforme semi-submersible DeepCwind + éolienne NREL 5 MW. C'est la plateforme reprise telle quelle
par le cas r-test `5MW_OC4Semi_WSt_WavesWN` de ce dépôt (`models/oc4_rtest/`) : géométrie (colonnes,
pontons), masses et ancrage identiques (à confirmer précisément une fois le texte intégral
accessible — voir `data/geometrie_deepcwind.md` pour les valeurs sourcées sur la fiche 02, et
`models/oc4_rtest/5MW_Baseline/HydroData/marin_semi.*` pour les données hydro WAMIT elles-mêmes,
dont ce rapport est probablement la source documentaire).

## Outil et version
Non applicable (rapport de définition, pas de résultat de simulation).

## Réglages hydro / ancrage / cas de charge
**Non lus** (texte intégral inaccessible). D'après le document OC5 (fiche 02, qui cite ce rapport comme
antécédent direct) : ancrage à 3 lignes caténaires, mêmes géométrie/matériau repris en OC5 avec mise à
jour mineure de la longueur non tendue (835.5 m en OC5 contre une valeur proche en OC4, à vérifier).

## Résultats chiffrés clés
Aucun (rapport de définition, pas de résultat de simulation ou d'essai).

## Ce que le rapport ne couvre pas
D'après le document OC5 (fiche 02) qui le prolonge explicitement : OC4 n'a jamais été confronté à des
données d'essai — c'est précisément l'objet d'OC5 Phase II. La turbine utilisée dans les essais en
bassin (2011 et 2013) était une version mise à l'échelle géométrique du NREL 5 MW qui ne reproduisait
pas sa poussée/puissance réelles, contrairement à la turbine utilisée dans les essais OC5 2013.

## Reproductible avec nos moyens ?
**Partiel.** Le système décrit est déjà notre cas de référence (`models/oc4_rtest/`), validé par le
LOT 6. Mais faute d'accès au texte intégral de CE rapport, on ne peut pas vérifier page par page que
notre copie r-test correspond exactement aux cotes d'origine — on s'appuie sur la cohérence déjà
établie (sha256, LOT 3a partiel) entre r-test et le tutoriel LHEEA, pas sur ce rapport lui-même.
