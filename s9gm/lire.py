"""s9gm.lire — lire les sorties OpenFAST, en tirer des statistiques, écarter le transitoire.

### Bloc Théorie

1. **Question physique** — Un calcul rend des milliers de valeurs par canal. Quelles statistiques
   (moyenne, dispersion, extrêmes) en retenir — et sur quelle partie du signal ? Le début d'une
   simulation n'est pas de la physique : la machine part de conditions initiales arbitraires
   (rotor à l'arrêt) et met du temps à atteindre son régime.
2. **Modèle** — pour un canal échantillonné `y(tᵢ)`, avec `t₀` la durée de transitoire écartée :
   moyenne `ȳ = (1/N) Σ yᵢ`, écart-type `σ = √((1/N) Σ (yᵢ − ȳ)²)` (population, dénominateur N),
   minimum et maximum, calculés sur les `N` points tels que `tᵢ ≥ t₀`. Garder le transitoire
   biaise la moyenne vers les conditions initiales et gonfle `σ` et les extrêmes. **Domaine de
   validité** : signal quasi stationnaire après `t₀` ; `t₀` se *choisit en regardant la courbe*,
   c'est pourquoi `lire` n'en propose aucun par défaut et refuse `None`.
3. **Ordre de grandeur attendu** — la méthode : tracer le canal, repérer l'instant où il cesse
   d'évoluer systématiquement, puis comparer la statistique avec et sans le transitoire — l'écart
   est la mesure de ce que vous évitez en l'écartant.
4. **Ce que le modèle ne permet pas de conclure** — qu'une moyenne sur une seule simulation soit
   la moyenne du processus : une seule réalisation de vent turbulent ne dit rien de la variabilité
   entre réalisations (phases 1-2). Et un maximum est un maximum *de cette réalisation*, pas un
   extrême de dimensionnement.
5. **Renvois** — fiche F1 (écarter le transitoire, `RotSpeed`) ; `outils/lire_outb.py` (version
   pas à pas du même calcul) ; `ENONCE.md`, phase 0 (piège « analyser le début de simulation ») et
   phase 3 (DEL, qui exige la même discipline).
"""
import re

import numpy as np
import pandas as pd
from openfast_toolbox.io import FASTOutputFile

_UNITE = re.compile(r"^(?P<nom>.*?)_\[(?P<unite>.*)\]$")


def lire(chemin):
    """Lit un `.outb` ou `.out`. Renvoie `(df, unites)` : `df` indexé par les noms de canaux
    (sans unité) avec la colonne `Time` ; `unites` : dict canal → unité."""
    df = FASTOutputFile(str(chemin)).toDataFrame()
    unites, noms = {}, {}
    for col in df.columns:
        m = _UNITE.match(col)
        nom = m["nom"] if m else col
        noms[col], unites[nom] = nom, (m["unite"] if m else "")
    df = df.rename(columns=noms)
    if "Time" not in df.columns:
        raise ValueError(f"{chemin} : pas de colonne Time")
    return df, unites


def statistiques(df, canaux, *, t_transitoire):
    """Moyenne, écart-type (population), min, max de `canaux` pour `Time >= t_transitoire`.

    `t_transitoire` (s) est **obligatoire**, sans valeur par défaut : choisir 0, c'est affirmer
    que le début du signal est déjà du régime établi — à faire en connaissance de cause."""
    if t_transitoire is None:
        raise ValueError("t_transitoire est obligatoire : regardez la courbe et choisissez une "
                         "durée de transitoire à écarter (0 seulement si vous l'assumez)")
    if t_transitoire < 0:
        raise ValueError("t_transitoire doit être >= 0")
    t = df["Time"].to_numpy()
    masque = t >= t_transitoire
    if not masque.any():
        raise ValueError(f"t_transitoire = {t_transitoire} s dépasse la fin du signal ({t[-1]} s)")
    lignes = {}
    for c in canaux:
        if c not in df.columns:
            raise KeyError(f"canal inconnu : {c}")
        y = df.loc[masque, c].to_numpy(dtype=float)
        lignes[c] = {"moyenne": y.mean(), "ecart_type": y.std(), "min": y.min(), "max": y.max(),
                     "n": int(y.size)}
    return pd.DataFrame(lignes).T
