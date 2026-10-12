# Périodes propres de la DeepCwind : valeurs publiées de référence

Valeurs **mesurées** lors d'essais de lâcher (décay tests) de la maquette de la semi-submersible DeepCwind, à comparer aux périodes
que vous tirez de vos propres lâchers (phase 2). Ce sont des valeurs publiées, pas des valeurs calculées par ce dépôt.

**Source** : Coulling A. J., Goupee A. J., Robertson A. N., Jonkman J. M., Dagher H. J., « Validation of a FAST semi-submersible
floating wind turbine numerical model with DeepCwind test data », *Journal of Renewable and Sustainable Energy* 5, 023116 (2013),
doi : [10.1063/1.4796197](https://doi.org/10.1063/1.4796197). **Table XIII**, page 023116-15 de l'article (page 16 du PDF), colonne
« Data (s) » (mesures), colonne « FAST » (modèle de l'article, donnée à titre de comparaison).

| Mouvement | Période mesurée (s) | Période du modèle FAST de l'article (s) |
|---|---|---|
| surge | 107 | 107 |
| sway | 112 | 113 |
| heave | 17.5 | 17.3 |
| roll | 26.9 | 26.7 |
| pitch | 26.8 | 26.8 |
| yaw | 82.3 | 82.7 |

**Portée.** Ces périodes valent pour la maquette et l'ancrage de l'article ; le modèle `modeles/flottant/` en est une
représentation (dérivée du cas r-test OC4), pas la maquette : un écart de quelques pour cent entre vos périodes et ces valeurs est
attendu et se discute (masse ajoutée, raideur d'ancrage, amortissement), il ne prouve pas à lui seul une erreur de votre lâcher.
Les périodes de surge, sway et yaw sont longues devant une fenêtre de lâcher de quelques centaines de secondes : citez le nombre
de périodes que contient votre fenêtre avant de comparer.
