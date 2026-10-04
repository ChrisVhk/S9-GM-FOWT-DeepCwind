# Registre des figures de `s9gm.visu`

Une figure n'est livrée (`visu.enregistrer`) que si son identifiant a ici une **porte pédagogique** :
la réponse écrite à « qu'est-ce que cette image apprend à un étudiant qui ne connaît pas le cas ? ».
Identifiants `FIG:S9GM-VISU-NNN`. Aucune valeur-réponse dans ce registre (dépôt public).

| ID | Fonction | Contenu | Provenance | Statut |
|---|---|---|---|---|
| FIG:S9GM-VISU-001 | `tracer_series` | Séries temporelles d'un ou plusieurs canaux d'un cas, zone de transitoire teintée | sorties d'un cas lancé par `s9gm.lancer`, lues par `s9gm.lire` ; ligne `cas · modèle · état` incrustée | ✅ prévue (modèle de figure) |
| FIG:S9GM-VISU-002 | `tracer_statistiques` | Moyenne, ± écart-type, min–max d'un canal pour plusieurs cas | `s9gm.lire.statistiques` sur chaque cas ; ligne `cas · modèle · état` incrustée | ✅ prévue (modèle de figure) |
| FIG:S9GM-VISU-003 | `tracer_courbes` | Famille de courbes Cp(λ) pour plusieurs calages (notebook 0b, §2) | tableau de pales rigides `Cp_Ct_Cq.IEA15MW.txt` ; ligne `cas · modèle · état` incrustée | ✅ livrée |
| FIG:S9GM-VISU-004 | `tracer_series` | Mise en régime de Ω, β, P à vent stationnaire, transitoire teinté (notebook 0b, §5) | sortie OpenFAST lue par `s9gm.lire` ; ligne `cas · modèle · état` incrustée | ✅ livrée |
| FIG:S9GM-VISU-005 | `tracer_courbes` | Ω, β, P, T en fonction du vent : à la main, publié, OpenFAST (notebook 0b, §5) | §4 du notebook, classeur publié, `s9gm.lire` ; ligne `cas · modèle · état` incrustée | ✅ livrée |
| FIG:S9GM-VISU-006 | `tracer_courbes` | Spectre d'une sortie OpenFAST avec repères 1P et 3P (notebook 0b, §6) | `s9gm.lire`, FFT du régime établi ; ligne `cas · modèle · état` incrustée | ✅ livrée |

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

**FIG:S9GM-VISU-003** — *Qu'est-ce que cette image apprend à un étudiant qui ne connaît pas le cas ?*
Qu'un rotor n'a pas « un » coefficient de puissance mais une famille de courbes `Cp(λ)`, une par angle de
calage : à calage donné la courbe a un maximum unique, et changer le calage déplace et abaisse ce maximum.
C'est ce qui permet au contrôleur de réduire la puissance captée quand le vent dépasse le nominal, et ce qui
rend faux tout `Cp` pris comme une constante.

**FIG:S9GM-VISU-004** — *Qu'est-ce que cette image apprend à un étudiant qui ne connaît pas le cas ?*
Que la vitesse de rotation, le calage et la puissance d'un calcul à vent stationnaire ne sont pas stationnaires
au début : le contrôleur amène la machine vers son équilibre en plusieurs dizaines de secondes, et la zone
teintée montre ce qu'une moyenne ne doit pas contenir. On choisit le temps à écarter en regardant la courbe.

**FIG:S9GM-VISU-005** — *Qu'est-ce que cette image apprend à un étudiant qui ne connaît pas le cas ?*
Qu'une même grandeur obtenue par trois voies (calcul à la main, valeurs publiées, calcul complet) ne coïncide
jamais exactement, que l'écart n'est pas le même dans chaque région de fonctionnement, et que cet écart est une
information : il s'attribue à des variables nommées (définition du rayon, calage imposé, élasticité des
pales…) plutôt qu'il ne se constate.

**FIG:S9GM-VISU-006** — *Qu'est-ce que cette image apprend à un étudiant qui ne connaît pas le cas ?*
Que les fréquences 1P et 3P, calculées avec la seule vitesse de rotation, sont bien celles où le calcul complet
excite la structure : le spectre d'une charge de rotor a des pics aux repères tracés. Une fréquence propre qui
tomberait sur l'un d'eux serait à craindre ; c'est pourquoi on les calcule avant de dimensionner.
