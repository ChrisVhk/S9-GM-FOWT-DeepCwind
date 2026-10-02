# S9-GM-FOWT-DeepCwind

Dépôt du cours **DMO-S9 — Fondations et structures** (ENSM, Génie Maritime, I5). Vous allez
simuler une éolienne flottante (NREL 5 MW sur plateforme semi-submersible OC4-DeepCwind) avec
**OpenFAST v5.0.0**, du modèle le plus simple (tour seule) jusqu'au modèle complet couplé, avant
de qualifier sa tenue en fatigue et aux états limites.

## Lundi — séance 0a : commencez ici → [`seances/0a/`](seances/0a/README.md)

L'énoncé complet du projet est dans [`ENONCE.md`](ENONCE.md). L'installation (pas à pas, avec
dépannage) est dans [`INSTALLATION.md`](INSTALLATION.md).

## Le projet en bref

| Phase | Contenu | Volume | Rendu |
|---|---|---|---|
| 0 | Tutoriel de prise en main : installation, éolienne fixe puis flottante, vérifications à la main | 6 h — 0a lundi, 0b séance suivante | R0 |
| 1 | Du site à la Load Case Table (scatter diagram, DLC, binning/lumping) | 3 h | R1 |
| 2 | Simulations de référence, lâchers, étude de sensibilité par groupe | 5 h | R2 |
| 3 | Fatigue : rainflow, S-N, Miner, DEL court et long terme | 8 h | R3 |
| 4 | Extrêmes (ULS) et ancrage | 12 h | R4 |
| 5 | Structures tubulaires : section de tour, entretoise, SCF | 8 h | R5 |
| 6 | Synthèse commune des trois groupes et soutenance | 4 h | Soutenance |
| | | **46 h** | |

Détail phase par phase, compétences visées, méthode de travail et règles d'évaluation :
[`ENONCE.md`](ENONCE.md).

## Carte du dépôt

| Dossier | Contenu | Sert en |
|---|---|---|
| `env/` | Environnement épinglé (`environment.yml`) et script d'installation | phase 0 |
| `scripts/build_discon.sh` | Compile le contrôleur (jamais suivi compilé) | phase 0, toute séance |
| `scripts/generer_vent_turbulent_05.sh` | Génère le vent turbulent du cas LHEEA 05 (fichier trop gros pour git) | phase 0b, phase 2 |
| `models/oc4_rtest/` | Modèle de référence OC4-DeepCwind (cas r-test OpenFAST, Apache-2.0) : géométrie, contrôleur et données hydro partagés par les tutoriels ci-dessous | toutes phases (référence partagée) |
| `tutorials/lheea/01-02` | Tutoriel OpenFAST Quickstart (LHEEA), Apache-2.0 : tour seule, rotor libre — récit dans `seances/0a/` | phase 0a |
| `tutorials/lheea/03-04` | Suite du même tutoriel (éolienne pilotée, monopieu) — récit dans `seances/0b/` | phase 0b |
| `tutorials/lheea/05` | Cas flottant complet du même tutoriel — récit dans `seances/0b/`, puis cas de **référence commune** | phase 0b, phase 2 |
| `tutorials/prise_en_main/` | Tutoriel du cours : éolienne fixe (F0x) puis flottante (D0x) | phase 0 |
| `fiches/` | Fiches « minimum vital » (théorie prérequise par phase) — une seule à ce jour (F1) | toutes phases |
| `papers/` | Fiches de lecture sourcées sur les systèmes OC4/OC5/OC6 (documents publics) | phases 1-2 |
| `data/` | Données du projet (dimensions, propriétés, références) — *en construction* | phases 0b-2 |
| `outils/` | Scripts de post-traitement de base (lecture `.outb`, tracés) | toutes phases |
| `rendus/` | Déposez vos rendus ici (jamais suivi par git) | tous rendus |

## Licences et attributions

Voir `PROVENANCE.md`. En résumé : modèle de référence et contrôleur sous licence Apache 2.0
(projet [OpenFAST](https://github.com/OpenFAST/openfast)) ; tutoriel LHEEA sous licence Apache 2.0
([openfast_quickstart](https://gitlab.in2p3.fr/lheea/oracle/tutorials/openfast_quickstart)), avec
attribution dans `tutorials/lheea/NOTICE`.
