<!-- destinations: github -->
# La chaîne complète de `s9gm` — démarche, sans valeurs

Une étude de charges relie, dans l'ordre : **un site** (table conjointe vent/houle) → **une Load Case Table** (peu de
cas, chacun avec son poids `Oⱼ`) → **des calculs** (un par cas, sur le modèle flottant) → **des séries** (lues, transitoire
écarté) → **un dommage équivalent** (court terme par cas, long terme pondéré). Chaque flèche est un module de `s9gm`, chaque
module un bloc « Théorie » et des tests qui le mettent à l'épreuve ; le script `outils/exemple_chaine.py` montre
l'enchaînement avec tous les choix laissés à `None`.

| Étape | Module | Ce que vous décidez (et devez justifier) |
|---|---|---|
| Site → LCT | `metocean` | nombre de classes, exposant du lumping, loi et hauteur de vent, classes écartées et leur poids |
| LCT → cas | `cas` | graines (vent, houle), durée simulée, intensité de turbulence |
| Calcul | `lancer` | nombre de cœurs ; le temps réel par temps simulé se mesure, il ne se suppose pas |
| Lecture | `lire` | durée de transitoire, **vérifiée** par la stationnarité de la fenêtre |
| Fatigue | `fatigue` | exposant de la courbe S-N, fréquence équivalente, canal et composante |

Trois contrôles à toujours faire : (1) `Σ Oⱼ = 100 %` — si vous écartez des classes, **renormalisez explicitement** et dites que le
résultat est conditionnel aux états retenus ; (2) un résultat qui s'écarte d'une référence se **chiffre** puis s'**attribue** variable
par variable avant d'être expliqué ; (3) une seule réalisation par cas ne dit rien de la variabilité entre réalisations.
Les résultats chiffrés de la chaîne ne sont pas publiés ici : ils sont l'objet des phases 1 à 3 du projet.
