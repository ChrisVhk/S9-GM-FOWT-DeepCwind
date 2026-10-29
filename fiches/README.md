<!-- destinations: github -->
# Index de la théorie : où lire quoi, phase par phase

Cet index **pointe, il n'explique pas** : chaque ligne dit où se trouve aujourd'hui la théorie d'une notion. Les fiches sont le « minimum vital » de chaque phase ; tant qu'une fiche n'est pas publiée, la ligne dit où la notion se lit en attendant. Le projet complet est présenté dans le [`README.md`](../README.md) du dépôt ; le post-traitement se lit toujours dans [`s9gm/POST-TRAITER.md`](../s9gm/POST-TRAITER.md).

## Les fiches

| Fiche | Sujet | État | Fichier |
|---|---|---|---|
| F1 | Aérodynamique et régulation | publiée | [`F1_Aero-regulation.md`](F1_Aero-regulation.md) ; exercices gradués corrigés : [`F1_exercices_IEA15_corriges.md`](F1_exercices_IEA15_corriges.md) |
| F2 | Houle linéaire, spectre, états de mer | publiée | [`F2_Houle-lineaire.md`](F2_Houle-lineaire.md) |
| F3 | Hydrostatique | publiée | [`F3_Hydrostatique.md`](F3_Hydrostatique.md) |
| F4 | Morison | publiée | [`F4_Morison.md`](F4_Morison.md) |
| F5 | Hydrodynamique potentielle | publiée | [`F5_Hydrodynamique-potentielle.md`](F5_Hydrodynamique-potentielle.md) |
| F6 | Aérodynamique et amortissement négatif | à venir | en attendant : voir la phase 2 ci-dessous |
| F7 | Caténaire statique | à venir | en attendant : voir la phase 4 ci-dessous |
| F8 | Ancrage dynamique | à venir | en attendant : voir la phase 4 ci-dessous |
| F9 | Fatigue de structure | publiée | [`F9_Fatigue-de-structure.md`](F9_Fatigue-de-structure.md) |
| F10 | Structures tubulaires | publiée | [`F10_Structures-tubulaires.md`](F10_Structures-tubulaires.md) |
| Formulaire | Relations par phase (rappel, sans valeurs) | publié | [`FORMULAIRE.md`](FORMULAIRE.md) |

## Phase 0a

| Notion | Où la lire |
|---|---|
| Aérodynamique, régions de régulation, poussée, fréquence 1P | [F1](F1_Aero-regulation.md) |
| Tour seule | [séance 0a, 6.1](../seances/0a/README.md#61-tour-seule-e01) |
| Rotor libre en vent constant | [séance 0a, 6.2](../seances/0a/README.md#62-éolienne-libre-en-vent-constant-e02) |
| Régulation de la NREL 5 MW | [séance 0a, 6.3](../seances/0a/README.md#63-régulation-de-la-nrel-5-mw) |
| Plausibilité des sorties | [séance 0a, 6.4](../seances/0a/README.md#64-plausibilité-des-sorties-f01-et-f02) |
| Fréquence 1P et 3P | [séance 0a, 6.5](../seances/0a/README.md#65-fréquence-1p) |
| Statistiques d'un canal, transitoire | [`s9gm/lire.py`](../s9gm/lire.py) (bloc Théorie du module) ; [`s9gm/POST-TRAITER.md`](../s9gm/POST-TRAITER.md) |
| Relations utiles | [Formulaire, phase 0](FORMULAIRE.md) |

## Phase 0b

| Notion | Où la lire |
|---|---|
| Vent turbulent et durée de simulation | [séance 0b, 6.1](../seances/0b/README.md#61-vent-turbulent-et-durée-de-simulation) |
| Champ de vent, gabarit TurbSim | [séance 0b, 6.2](../seances/0b/README.md#62-le-champ-de-vent--gabarit-turbsim) |
| Contrôleur complet en vent variable | [séance 0b, 6.3](../seances/0b/README.md#63-contrôleur-complet-en-vent-variable-cas-lheea-03) |
| Éolienne sur monopieu | [séance 0b, 6.4](../seances/0b/README.md#64-éolienne-sur-monopieu-cas-lheea-04) |
| Éolienne flottante | [séance 0b, 6.5](../seances/0b/README.md#65-éolienne-flottante-cas-lheea-05) |
| Houle linéaire, états de mer | [F2](F2_Houle-lineaire.md) |
| Hydrostatique du flotteur : raideurs, GM, ancrage à part | [F3](F3_Hydrostatique.md) ; l'exercice : [séance 0b, étape 3.3](../seances/0b/README.md#33-raideurs-hydrostatiques-à-la-main-environ-30-min) ; [`s9gm/hydro.py`](../s9gm/hydro.py) (bloc Théorie du module) |
| Morison : coefficients, domaine de validité, efforts sur un membre | [F4](F4_Morison.md) ; [`s9gm/hydro.py`](../s9gm/hydro.py) (régime de Morison, nombre de Keulegan-Carpenter) ; [Formulaire, phase 2](FORMULAIRE.md) |

## Phase 1

| Notion | Où la lire |
|---|---|
| Houle linéaire, spectre, `Hs`, `Tz`, `Tp`, énergie, états de mer | [F2](F2_Houle-lineaire.md) |
| Du site à la table de cas : marginales, regroupement, occurrences, représentativité | [`s9gm/metocean.py`](../s9gm/metocean.py) (un bloc Théorie par fonction) |
| Relations utiles | [Formulaire, phase 1](FORMULAIRE.md) |

## Phase 2

| Notion | Où la lire |
|---|---|
| Excitation, masse ajoutée, amortissement de rayonnement, RAO, périodes propres | [F5](F5_Hydrodynamique-potentielle.md) |
| Aérodynamique et amortissement négatif (F6, à venir) | en attendant : la rubrique « Théorie à lire » de la [phase 2](../seances/phase2/README.md#6-théorie-à-lire) |
| Hydrostatique et périodes propres | [F3](F3_Hydrostatique.md) ; [`s9gm/hydro.py`](../s9gm/hydro.py) (bloc Théorie du module) ; [Formulaire, phase 2](FORMULAIRE.md) |
| Morison : coefficients, domaine de validité, efforts sur un membre | [F4](F4_Morison.md) ; [Formulaire, phase 2](FORMULAIRE.md) |

## Phase 3

| Notion | Où la lire |
|---|---|
| Fatigue : rainflow, courbe S-N, Miner, DEL court et long terme, DFF, effet d'épaisseur | [F9](F9_Fatigue-de-structure.md) ; [`s9gm/fatigue.py`](../s9gm/fatigue.py) (blocs Théorie du module) ; [Formulaire, phase 3](FORMULAIRE.md) |
| Section tubulaire, DEL, courbe S-N, somme de DEL, Von Mises, dimensionnement | [guide du classeur de l'atelier, section 6](../annexes/atelier_tour/README.md#a-theorie) (une rubrique par étape du classeur) |
| Post-traitement de la chaîne | [`s9gm/CHAINE.md`](../s9gm/CHAINE.md) ; [`s9gm/POST-TRAITER.md`](../s9gm/POST-TRAITER.md) |

## Phase 4

| Notion | Où la lire |
|---|---|
| Caténaire statique, raideur de ligne (F7, à venir) | en attendant : [`s9gm/ancrage.py`](../s9gm/ancrage.py) (bloc Théorie du module) ; [Formulaire, phase 4](FORMULAIRE.md) |
| Ancrage dynamique, tension de chaumard (F8, à venir) | en attendant : la rubrique « Théorie à lire » de la [phase 4](../seances/phase4/README.md#6-théorie-à-lire) |
| Rainflow, Miner et DEL appliqués à la tension de chaumard `FAIRTEN` | [F9](F9_Fatigue-de-structure.md) ; [`s9gm/fatigue.py`](../s9gm/fatigue.py) |

## Phase 5

| Notion | Où la lire |
|---|---|
| Nœuds tubulaires, point chaud, facteurs de concentration de contrainte (SCF), domaine de validité | [F10](F10_Structures-tubulaires.md) ; [Formulaire, phase 5](FORMULAIRE.md) |
| Section tubulaire, contraintes, Von Mises, dimensionnement de la tour | [guide du classeur de l'atelier, section 6](../annexes/atelier_tour/README.md#a-theorie) ; [`s9gm/structure.py`](../s9gm/structure.py) (bloc Théorie du module) ; [Formulaire, phase 5](FORMULAIRE.md) |
| Fréquence de la tour et bandes 1P et 3P | [F1](F1_Aero-regulation.md) ; [guide de l'atelier, section 6.7](../annexes/atelier_tour/README.md#a-theorie-6-7) |
| Morison : coefficients, domaine de validité, efforts sur un membre | [F4](F4_Morison.md) ; [Formulaire, phase 2](FORMULAIRE.md) |

## Phase 6

Aucune fiche n'est prévue pour cette phase. La démarche d'ensemble (du site au dommage équivalent) se lit dans [`s9gm/CHAINE.md`](../s9gm/CHAINE.md).
