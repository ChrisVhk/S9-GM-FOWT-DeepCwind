"""s9gm — boîte à outils du projet DMO-S9 (OpenFAST, de la Load Case Table au résultat).

Trois modules pour la phase 0 : `cas` (fabriquer une série de cas depuis une Load Case Table),
`lancer` (les exécuter, en parallèle, en reprenant les cas non terminés), `lire` (lire les sorties
et en tirer des statistiques en écartant le transitoire). Phase 1 : `metocean` (de la table
conjointe vent/houle d'un site à une Load Case Table).

Chaque module commence par un bloc « Théorie » : la question physique avant le code. Rien ici
n'est une boîte noire — lisez le code, il est court.
"""
__version__ = "0.1.0"
