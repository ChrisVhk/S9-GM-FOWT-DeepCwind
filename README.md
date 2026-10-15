# S9-GM-FOWT-DeepCwind

Dépôt du cours **DMO-S9 — Fondations et structures** (ENSM, Génie Maritime, I5). Vous allez
simuler une éolienne flottante (NREL 5 MW sur plateforme semi-submersible OC4-DeepCwind) avec
**OpenFAST v5.0.0**, du modèle le plus simple (tour seule) jusqu'au modèle complet couplé, avant
de qualifier sa tenue en fatigue et aux états limites.

Droits : ENSM, publié avec l'accord de l'École.

Licences : code Apache 2.0 ([LICENSE](LICENSE)), documentation CC BY 4.0 ([LICENSE-docs](LICENSE-docs)) ; les composants tiers gardent leur propre licence, notamment [modeles/iea15_monopile/LICENSE](modeles/iea15_monopile/LICENSE) et [annexes/lheea/LICENSE](annexes/lheea/LICENSE) (exceptions, non modifiées).

> **Vous aviez déjà cloné ce dépôt avant le 12/10/2026 ?** Il a été réorganisé : lisez d'abord [`TRANSITION.md`](TRANSITION.md).

## Commencez ici

1. **Installer** : [`INSTALLATION.md`](INSTALLATION.md) (pas à pas, avec dépannage), puis `s9gm doctor` pour vérifier le poste. Le terminal en une page : [`annexes/TERMINAL.md`](annexes/TERMINAL.md).
2. **Suivre les séances dans l'ordre** : chacune a sa consigne autonome, au même format (objectif, avant de commencer, à
   faire étape par étape, post-traiter, ce qu'on rend, théorie à lire).
3. **Post-traiter toujours de la même façon** : [`s9gm/POST-TRAITER.md`](s9gm/POST-TRAITER.md), du `.outb` aux
   statistiques, aux figures et au DEL.
4. **La théorie** : [`fiches/README.md`](fiches/README.md), l'index de tout ce qu'il faut lire, par phase.

Le cadre du projet (compétences visées, organisation, évaluation, règles) est dans [`ENONCE.md`](ENONCE.md).

## Le parcours, phase par phase

| Phase / séance | Contenu | Séances | Volume | Consigne | Rendu |
|---|---|---|---|---|---|
| 0a | Installation, anatomie d'un cas, régulation à la main, éolienne fixe F01-F02 | 1 séance (lundi) | 3 h | [`seances/0a/`](seances/0a/README.md) | R0 (Q0.1, Q0.2) |
| 0b | Vent turbulent F03-F05, architecture et hydrostatique du flotteur, flottant D00-D05, comparaison fixe / flottant | 1 séance (la suivante) | 3 h | [`seances/0b/`](seances/0b/README.md) | R0 (Q0.3 à Q0.6) |
| 1 | Du site à la Load Case Table (scatter diagram, DLC, binning/lumping) | créneaux au planning de la promotion | 3 h | [`seances/phase1/`](seances/phase1/README.md) | R1 |
| 2 | Simulations de référence, lâchers, étude de sensibilité | créneaux au planning de la promotion | 5 h | [`seances/phase2/`](seances/phase2/README.md) | R2 |
| 3 | Fatigue : rainflow, S-N, Miner, DEL court et long terme | créneaux au planning de la promotion | 8 h (+ ≈ 3 h) | [`seances/phase3/`](seances/phase3/README.md) | R3 |
| 4 | Extrêmes (ULS) et ancrage | créneaux au planning de la promotion | 12 h | [`seances/phase4/`](seances/phase4/README.md) | R4 |
| 5 | Structures tubulaires : section de tour, entretoise, SCF | créneaux au planning de la promotion | 8 h (+ ≈ 5 h) | [`seances/phase5/`](seances/phase5/README.md) | R5 |
| 6 | Synthèse commune des trois groupes et soutenance | créneaux au planning de la promotion | 4 h | [`seances/phase6/`](seances/phase6/README.md) | Soutenance |
| | | | **46 h** | | |

**Vocabulaire.** Une **séance** est un créneau de cours ; une **phase** est une étape du projet, d'une ou de plusieurs séances. Les lignes 0a et 0b sont les deux séances de la phase 0 ; les dates des créneaux sont au planning de la promotion.

Les phases 3 et 5 se poursuivent à la maison : les heures entre parenthèses s'ajoutent au volume de séance ; le total de 46 h ne les compte pas. Elles s'appuient sur le [guide du classeur de l'atelier](annexes/atelier_tour/README.md), une ressource qu'on ouvre à l'étape 0 de la phase 3 et au point 1 de la phase 5 (ce n'est pas une séance).

## Carte du dépôt

| Dossier | Contenu | Vous le… |
|---|---|---|
| `seances/` | Une consigne autonome par séance ou par phase | **lisez et suivez** |
| `modeles/` | Tous les modèles : `fixe/` (monopieu OC3 du tutoriel), `flottant/` (OC4-DeepCwind du tutoriel), `oc4_rtest/` (OC4-DeepCwind, r-test OpenFAST, Apache-2.0), `iea15_monopile/`, `oc5/` (note) | lisez, sans le modifier |
| `cas/` | Cas de référence (F01, F02…) et leur lanceur `run_cas.sh` | lancez, sans le modifier |
| `s9gm/` | Le seul outil de calcul et de post-traitement (Python) | utilisez, sans le modifier (aux phases 3 à 5, vous complétez **une copie** sous `results/mon_s9gm/`, jamais le fichier suivi) |
| `fiches/` | Fiches « minimum vital » et leur index (théorie prérequise par phase) | lisez |
| `data/` | Données du projet (dimensions, propriétés, références, site) | lisez |
| `env/`, `scripts/` | Environnement épinglé ; compilation du contrôleur, contrôles du dépôt | lancez |
| `annexes/` | Guide du classeur de l'atelier, tutoriel LHEEA d'origine, notes de lecture, et `annexes/outils/` (scripts de provenance des données, non utilisés dans le parcours) | consultez |
| `results/` | **Vos** sorties, copies de cas, tables de cas, figures (ignoré par git) | écrivez ici |
| `rendus/` | **Vos** rendus (ignoré par git) | déposez ici |

**Règle du dépôt** : vous ne modifiez aucun fichier suivi par git. Tout ce que vous créez ou modifiez vit sous `results/`
ou `rendus/`, ce qui rend `git pull` toujours sans conflit.

## Licences et attributions

Voir `PROVENANCE.md`. En résumé : modèle de référence et contrôleur sous licence Apache 2.0
(projet [OpenFAST](https://github.com/OpenFAST/openfast)) ; tutoriel LHEEA sous licence Apache 2.0
([openfast_quickstart](https://gitlab.in2p3.fr/lheea/oracle/tutorials/openfast_quickstart)), avec
attribution dans `annexes/lheea/NOTICE`.
