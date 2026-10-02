# Provenance et licences

Ce dépôt assemble du code et des données de plusieurs origines. Voici, pour chaque dossier, d'où
il vient et sous quelle licence.

## `models/oc4_rtest/`
Origine : [OpenFAST/r-test](https://github.com/OpenFAST/r-test), tag `v5.0.0`
(SHA `dd5feaaaa500ba7283140107806300d551cff0a7`), cas `5MW_OC4Semi_WSt_WavesWN` et fichiers partagés
de `5MW_Baseline/`. **Licence Apache 2.0** (comme le dépôt [OpenFAST/openfast](
https://github.com/OpenFAST/openfast) dont il dépend). Repris tel quel, seuls les fichiers
effectivement lus par le cas de référence sont inclus (pas de BeamDyn, pas de champ de vent
turbulent pour ce cas précis).

## `tutorials/lheea/`
Origine : [openfast_quickstart](https://gitlab.in2p3.fr/lheea/oracle/tutorials/openfast_quickstart)
(LHEEA, Nantes Université — ORACLE), commit `6040b6430bba78d3906877f2ea4d3effe3a4eb5e`.
**Licence Apache 2.0** — voir `tutorials/lheea/LICENSE` et `tutorials/lheea/NOTICE` pour le détail
des modifications apportées (migration des fichiers d'entrée vers OpenFAST v5.0.0 ; voir les
commentaires `[migré : ...]` dans les fichiers concernés).

## `tutorials/prise_en_main/`
Construit pour ce cours, à partir des modèles ci-dessus (licence Apache 2.0 des sources) et d'une
progression inspirée d'un cours de Master Génie Maritime (2013) sur les outils de conception
éolien — adaptée ici en OpenFAST v5.0.0, pas une reproduction du document source.

## `env/`, `scripts/`, `outils/`, `README.md`, `data/`
Écrits pour ce dépôt.

## `fiches/`
Source de vérité : `Cours/DMO-S9_Fondations-Structures/Fiches/` du dépôt de cours (privé). Copiées
ici telles quelles pour que les étudiants y accèdent sans avoir accès à ce dépôt privé.

## DISCON (contrôleur)
Les fichiers `DISCON.F90` / `DISCON_OC3Hywind.F90` (sources du contrôleur) proviennent du dépôt
OpenFAST (tag v5.0.0, licence Apache 2.0). **Aucun binaire compilé (`.so`) n'est suivi dans ce
dépôt** : chacun compile le sien avec `scripts/build_discon.sh` (voir le README).
