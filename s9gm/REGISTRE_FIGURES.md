# Registre des figures de `s9gm.visu`

Une figure n'est livrée (`visu.enregistrer`) que si son identifiant a ici une **porte pédagogique** :
la réponse écrite à « qu'est-ce que cette image apprend à un étudiant qui ne connaît pas le cas ? ».
Identifiants `FIG:S9GM-VISU-NNN`. Aucune valeur-réponse dans ce registre (dépôt public).

| ID | Fonction | Contenu | Provenance | Statut |
|---|---|---|---|---|
| FIG:S9GM-VISU-001 | `tracer_series` | Séries temporelles d'un ou plusieurs canaux d'un cas, zone de transitoire teintée | sorties d'un cas lancé par `s9gm.lancer`, lues par `s9gm.lire` ; ligne `cas · modèle · état` incrustée | ✅ prévue (modèle de figure) |
| FIG:S9GM-VISU-002 | `tracer_statistiques` | Moyenne, ± écart-type, min–max d'un canal pour plusieurs cas | `s9gm.lire.statistiques` sur chaque cas ; ligne `cas · modèle · état` incrustée | ✅ prévue (modèle de figure) |

## Portes pédagogiques

**FIG:S9GM-VISU-001** — *Qu'est-ce que cette image apprend à un étudiant qui ne connaît pas le cas ?*
Qu'un calcul ne démarre pas en régime établi : le début de la courbe (zone teintée) est une mise en
route à écarter des statistiques, et la forme de la courbe (plateau, oscillation, dépassement) dit si
le calcul est arrivé à son régime avant qu'on lise la moindre valeur. Avec `masquer_ordonnees=True`,
elle montre l'allure sans donner la valeur.

**FIG:S9GM-VISU-002** — *Qu'est-ce que cette image apprend à un étudiant qui ne connaît pas le cas ?*
Qu'une moyenne ne suffit pas : la dispersion (± écart-type) et l'étendue (min–max) d'un canal
changent d'un cas à l'autre même quand la moyenne varie peu, et qu'une statistique se lit toujours
avec son cas et sa durée de transitoire écartée.
