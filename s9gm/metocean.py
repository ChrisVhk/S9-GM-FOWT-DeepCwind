"""s9gm.metocean — de la table conjointe vent/houle d'un site à une Load Case Table.

Sept fonctions, chacune précédée de son bloc « Théorie » : `lire`, `marginales`, `binning`,
`lumper`, `occurrences`, `representativite`, `exporter_lct` (plus `hauteur_vent`, le changement de
hauteur du vent, qui est un **paramètre explicite**, jamais un défaut caché).

Table de travail : FLOATECH (Papi et al., Zenodo 10.5281/zenodo.10102696, CC BY 4.0) — probabilités
d'un tableau 4-D vent à 100 m × Hs × Tp × désalignement vent/houle, site West of Barra, réanalyse ERA5,
voir `data/metocean/floatech_wob.metadata.json` et `PROVENANCE.md`.

### Bloc Théorie

*`lire` — lecture de la table conjointe.*

1. **Question physique** — Un site se décrit par la fréquence à laquelle se présentent ensemble un vent, une
   hauteur de houle, une période et un désalignement. Que contient exactement le fichier, et comment savoir qu'on
   l'a lu correctement avant de s'en servir ?
2. **Modèle** — un tableau `P[i, j, k, l]` de probabilités, une case par classe de vent `i`, de hauteur
   significative `j`, de période de pic `k` et de désalignement `l`, issu du comptage d'observations horaires d'une
   réanalyse : `P = n(case) / N`. **Domaine de validité** : les classes sont celles du fichier (largeur
   constante par axe) ; une probabilité n'est pas une occurrence tant qu'on ne l'a pas multipliée par une durée.
3. **Ordre de grandeur attendu** — la méthode : avant de lire, écrire la forme attendue du tableau d'après la
   description du fichier (nombre de classes par axe), puis vérifier que la somme vaut un à la tolérance nommée
   `TOLERANCE_SOMME`. Une somme qui n'est pas un à cette tolérance est un fichier abîmé ou mal lu : la fonction
   échoue plutôt que de renormaliser en silence.
4. **Ce que le modèle ne permet pas de conclure** — que le tableau soit le site réel : c'est une réanalyse,
   sur une période finie, à une hauteur de vent donnée ; il ne dit rien des extrêmes au-delà de sa période ni de
   la variabilité d'une année à l'autre.
5. **Renvois** — fiche F2 (houle linéaire : Hs, Tp) ; `data/metocean/floatech_wob.metadata.json` ;
   `PROVENANCE.md` (source, licence, période, hauteur de vent) ; `ENONCE.md`, phase 1 (occurrences).

### Bloc Théorie

*`marginales` — ce que le tableau dit d'un seul paramètre.*

1. **Question physique** — Sur quelles classes de vent, de houle, de période se concentre le temps passé ?
   Un paramètre pris seul suffit-il à décrire le site ?
2. **Modèle** — la marginale d'un axe est la somme du tableau sur les trois autres :
   `P_i = Σ_{j,k,l} P[i, j, k, l]` (et de même pour les autres axes). **Domaine de validité** : exacte pour le
   tableau lu ; elle perd la corrélation entre paramètres (un vent fort s'accompagne de houle forte).
3. **Ordre de grandeur attendu** — la méthode : repérer la classe la plus probable de chaque marginale et
   vérifier que les probabilités de classes sommées redonnent un ; comparer ensuite l'étalement des marginales
   (queue du vent, queue de Hs) avant d'en tirer des cas de charge.
4. **Ce que le modèle ne permet pas de conclure** — que les paramètres soient indépendants : le produit des
   marginales n'est pas le tableau conjoint, et choisir « le vent le plus probable avec la houle la plus
   probable » ne donne pas l'état de mer le plus probable.
5. **Renvois** — fiche F2 (houle) ; fiche F1 (zones de fonctionnement selon le vent) ; phase 1 de l'énoncé.

### Bloc Théorie

*`binning` — changer la finesse des classes.*

1. **Question physique** — Un calcul coûte cher : combien de classes garde-t-on, et que perd-on en fusionnant
   des cases voisines ?
2. **Modèle** — fusionner `k` classes consécutives d'un axe en une seule : les probabilités s'additionnent,
   les bornes se regroupent ; la somme est conservée. **Domaine de validité** : `k` doit diviser le nombre de
   classes de l'axe ; on ne coupe jamais une classe en deux (aucune information de sous-classe n'existe).
3. **Ordre de grandeur attendu** — la méthode : compter le nombre de classes avant et après, vérifier que la
   somme est inchangée, et que la marginale de l'axe fusionné est la somme des marginales fusionnées.
4. **Ce que le modèle ne permet pas de conclure** — que fusionner soit gratuit : une classe plus large mélange
   des états de mer de nature différente, et la valeur qu'on lui attribue ensuite (voir `lumper`) devient une
   moyenne de choses hétérogènes.
5. **Renvois** — fiche F2 (houle) ; `lumper` ; phase 1 de l'énoncé (choix des classes).

### Bloc Théorie

*`lumper` — passer des classes à des cas de charge.*

1. **Question physique** — On ne peut pas simuler chaque case du tableau : comment choisir peu d'états de mer
   qui représentent le site, et quelle valeur de Hs, de Tp attribuer à une classe qui en regroupe beaucoup ?
2. **Modèle** — on regroupe les cases par classe d'un axe (par défaut le vent) puis, pour chaque classe de
   probabilité `P_c = Σ p`, on choisit une valeur représentative de Hs : **moyenne** `Σ p·Hs / P_c`, **maximum**
   (valeur de la plus haute classe de probabilité non nulle), ou **pondérée dommage** `(Σ p·Hs^m / P_c)^{1/m}`
   avec l'exposant `m` donné par l'appelant. `m = 1` redonne la moyenne ; le maximum est le cas limite
   `m → ∞`. La période est la moyenne pondérée, le désalignement est une moyenne circulaire (moyenne, dommage) ou celui de la case la plus
   probable de la classe (maximum). **Domaine de validité** : la valeur représentative d'une classe n'est un
   bon substitut que si la quantité visée varie comme la puissance `m` de Hs ; `lumper` ne choisit pas `m` pour vous. « Maximum » est la plus haute classe de Hs de probabilité non nulle
   (milieu de classe), conservateur au regard de l'énergie calculée sur les milieux de classe, pas d'un Hs réel.
3. **Ordre de grandeur attendu** — la méthode : pour une classe, calculer les trois valeurs et les ranger :
   moyenne, pondérée dommage (pour un exposant au moins égal à un) et maximum sont dans cet ordre ; l'identité `m = 2` conserve exactement
   `Σ p·Hs²` (énergie de houle) et rien d'autre.
4. **Ce que le modèle ne permet pas de conclure** — qu'une LCT lumpée donne le même dommage que le tableau : la
   conservation d'une grandeur (ici `Hs^m`) ne conserve pas les autres, et la réponse d'une structure dépend de
   la période et de la direction autant que de Hs.
5. **Renvois** — fiche F2 (énergie de la houle linéaire) ; fiche F4 (forces de Morison, effet de Hs et de Tp) ;
   phase 1 de l'énoncé (Load Case Table).

### Bloc Théorie

*`occurrences` — de la probabilité au temps passé.*

1. **Question physique** — Combien d'heures par an le site passe-t-il dans chacun des états de mer retenus,
   et la somme redonne-t-elle bien la totalité du temps ?
2. **Modèle** — `O_j = P_j × T` avec `T` la durée d'une année en heures (`HEURES_PAR_AN`) ; en pourcentage
   `O_j % = 100·P_j`. **Domaine de validité** : vaut pour des probabilités qui somment à un ; si on a écarté
   des classes (peu probables), la somme est inférieure à cent pour cent et la fonction **le dit** au lieu de
   renormaliser.
3. **Ordre de grandeur attendu** — la méthode : sommer les `O_j` et vérifier cent pour cent à la tolérance
   nommée `TOLERANCE_OCCURRENCES` ; si on a retiré des classes, calculer la part de temps non représentée.
4. **Ce que le modèle ne permet pas de conclure** — qu'un état de mer rare soit négligeable pour la fatigue :
   une occurrence faible pondère le dommage par la puissance de la contrainte, et un état extrême rare peut
   dominer.
5. **Renvois** — fiche F8 (fatigue : DEL long terme `Σ_j O_j S_{e,j}^m`, FAIRTEN et rainflow) ; phase 1 de l'énoncé
   (occurrences) ; phase 3 (DEL long terme).

### Bloc Théorie

*`representativite` — la LCT ressemble-t-elle au site ?*

1. **Question physique** — Après avoir choisi des cas, que garde-t-on du site ? Sur quels paramètres la LCT
   est-elle fidèle, et sur lesquels s'écarte-t-elle ?
2. **Modèle** — on compare, paramètre par paramètre, la marginale du site à celle de la LCT (chaque état de mer
   rangé dans la classe qui le contient), et on compare l'**énergie de houle** `E = Σ P·Hs²` (proportionnelle
   à l'énergie par unité de surface, à un facteur près et sans la période). **Domaine de validité** : un critère
   de comparabilité, pas de justesse : il dit de combien la LCT s'écarte, pas si l'écart est acceptable pour votre
   étude.
3. **Ordre de grandeur attendu** — la méthode : écrire avant l'essai la tolérance sur l'énergie et les
   variables tenues égales et celles qui bougent ; classer ensuite les règles de lumping selon l'énergie
   restituée (moyenne sous le site, maximum au-dessus, pondération `m = 2` à égalité).
4. **Ce que le modèle ne permet pas de conclure** — qu'une énergie conservée suffise : la période, la direction
   et la corrélation vent/houle peuvent être déformées sans que `E` le montre.
5. **Renvois** — fiche F2 (énergie de la houle) ; `CRITERE_energie_houle.md` du dépôt d'enseignement (écrit avant
   l'essai) ; phase 1 de l'énoncé.

### Bloc Théorie

*`exporter_lct` — de la table à la Load Case Table lue par `s9gm.cas`.*

1. **Question physique** — Comment transformer les états de mer retenus en cas OpenFAST, sans rien changer à la
   main et sans oublier que le vent du tableau n'est pas le vent au moyeu ?
2. **Modèle** — une ligne de LCT par état de mer : numéro de cas, durée, vent moyen **à la hauteur du moyeu**
   (conversion explicite depuis la hauteur de la table, par une loi nommée : puissance avec exposant, ou
   logarithmique avec longueur de rugosité), graine. Hs, Tp, direction et occurrence vont dans un fichier
   compagnon, parce que `s9gm.cas` n'édite pas le fichier de houle. **Domaine de validité** : la conversion de
   hauteur est une loi de profil moyen, valable en atmosphère neutre ; le choix de la loi et de son exposant est un
   choix de modélisation que vous devez justifier.
3. **Ordre de grandeur attendu** — la méthode : vérifier que la vitesse au moyeu dépasse la vitesse à la hauteur
   de la table si le moyeu est plus haut, et l'inverse sinon ; relire la LCT exportée avec `s9gm.cas` avant de
   lancer quoi que ce soit.
4. **Ce que le modèle ne permet pas de conclure** — que la graine fixée suffise : une seule réalisation par état
   de mer ne dit rien de la variabilité entre réalisations (voir `lire`, point 4).
5. **Renvois** — `s9gm/cas.py` (format de la LCT, colonnes `turbsim.*`) ; fiche F1 (vent à la hauteur du moyeu) ;
   `seances/0b/README.md` (graine, TurbSim) ; phase 1 de l'énoncé.
"""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

RACINE = Path(__file__).resolve().parents[1]
DONNEES = RACINE / "data" / "metocean"
FICHIER = DONNEES / "floatech_wob_pdf_array.bin"
METADONNEES = DONNEES / "floatech_wob.metadata.json"

TOLERANCE_SOMME = 1e-9          # |Σ P − 1| maximal accepté à la lecture (écart flottant du fichier de départ)
TOLERANCE_OCCURRENCES = 1e-9    # |Σ O_j (%) − 100| / 100 maximal accepté
HEURES_PAR_AN = 8766.0          # 365,25 jours
AXES = ("U", "Hs", "Tp", "mis")
METHODES = ("identite", "moyenne", "maximum", "dommage")


@dataclass(frozen=True)
class Table:
    """Tableau 4-D de probabilités `P[U, Hs, Tp, mis]`, avec les bornes de classes de chaque axe."""
    P: np.ndarray
    bords: dict
    meta: dict

    def milieux(self, axe):
        b = self.bords[axe]
        return (b[:-1] + b[1:]) / 2


def lire(chemin=None, metadonnees=None, tolerance=TOLERANCE_SOMME):
    """Lit la table conjointe. Échoue si la forme ne correspond pas aux métadonnées ou si
    `|Σ P − 1| > tolerance` (jamais de renormalisation silencieuse)."""
    chemin = Path(chemin or FICHIER)
    meta = json.loads(Path(metadonnees or METADONNEES).read_text(encoding="utf-8"))
    forme = tuple(meta["forme"])
    P = np.fromfile(chemin, dtype="<f8")
    if P.size != int(np.prod(forme)):
        raise ValueError(f"{chemin.name} : {P.size} valeurs, la forme {forme} en attend {int(np.prod(forme))}")
    P = P.reshape(forme)
    if (P < 0).any():
        raise ValueError(f"{chemin.name} : probabilité négative")
    ecart = abs(P.sum() - 1.0)
    if ecart > tolerance:
        raise ValueError(f"{chemin.name} : Σ P = {P.sum():.12g}, écart à 1 de {ecart:.3g} > tolérance "
                         f"{tolerance:g} (TOLERANCE_SOMME)")
    nb = meta["bornes"]
    bords = {axe: np.linspace(*nb[cle][:2], nb[cle][2] + 1)
             for axe, cle in zip(AXES, ("U100", "Hs", "Tp", "desalignement"))}
    for axe, n in zip(AXES, forme):
        assert len(bords[axe]) == n + 1, axe
    return Table(P, bords, meta)


def marginales(t, axe):
    """Marginale d'un axe : Série indexée par le milieu de classe."""
    i = AXES.index(axe)
    autres = tuple(k for k in range(4) if k != i)
    return pd.Series(t.P.sum(axis=autres), index=t.milieux(axe), name=f"P_{axe}")


def binning(t, axe, k):
    """Fusionne `k` classes consécutives de `axe` ; la somme est conservée."""
    i = AXES.index(axe)
    n = t.P.shape[i]
    if k < 1 or n % k:
        raise ValueError(f"k = {k} ne divise pas le nombre de classes de {axe} ({n})")
    forme = list(t.P.shape)
    forme[i:i + 1] = [n // k, k]
    P = t.P.reshape(forme).sum(axis=i + 1)
    bords = dict(t.bords)
    bords[axe] = np.append(t.bords[axe][:-1:k], t.bords[axe][-1])
    return Table(P, bords, t.meta)


def hauteur_vent(u_ref, z_ref, z_cible, *, loi, exposant=None, z0=None):
    """Vitesse à `z_cible` d'un vent connu à `z_ref`. `loi` ∈ {"puissance", "logarithmique"} est
    **obligatoire** ; la loi puissance exige `exposant`, la loi logarithmique exige `z0` (m). Aucune valeur par
    défaut : le choix de la loi et de son paramètre est un choix de modélisation à justifier."""
    u_ref = np.asarray(u_ref, dtype=float)
    if loi == "puissance":
        if exposant is None:
            raise ValueError("loi « puissance » : exposant obligatoire")
        return u_ref * (z_cible / z_ref) ** exposant
    if loi == "logarithmique":
        if z0 is None:
            raise ValueError("loi « logarithmique » : z0 obligatoire")
        return u_ref * np.log(z_cible / z0) / np.log(z_ref / z0)
    raise ValueError(f"loi inconnue : {loi!r} (attendu : « puissance » ou « logarithmique »)")


def _moyenne_circulaire(angles_deg, poids):
    a = np.radians(angles_deg)
    return float(np.degrees(np.arctan2((poids * np.sin(a)).sum(), (poids * np.cos(a)).sum())))


def lumper(t, *, methode, axe_classes="U", m=None):
    """États de mer représentatifs. `identite` : une classe par case de probabilité non nulle.
    Sinon : une classe par classe de `axe_classes`, valeur de Hs par `methode` ∈ {moyenne, maximum, dommage}
    (`dommage` exige l'exposant `m`). Renvoie un DataFrame (U, Hs, Tp, mis, P) ; U est le milieu de classe."""
    if methode not in METHODES:
        raise ValueError(f"méthode inconnue : {methode!r} (attendu : {METHODES})")
    mid = {a: t.milieux(a) for a in AXES}
    U, H, T, D = np.meshgrid(mid["U"], mid["Hs"], mid["Tp"], mid["mis"], indexing="ij")
    if methode == "identite":
        masque = t.P > 0
        return pd.DataFrame({"U": U[masque], "Hs": H[masque], "Tp": T[masque], "mis": D[masque],
                             "P": t.P[masque]})
    if methode == "dommage" and (m is None or m <= 0):
        raise ValueError("lumping « dommage » : exposant m > 0 obligatoire")
    ia = AXES.index(axe_classes)
    lignes = []
    for c in range(t.P.shape[ia]):
        sel = np.take(t.P, c, axis=ia)
        grilles = [np.take(g, c, axis=ia) for g in (U, H, T, D)]
        Pc = sel.sum()
        if Pc <= 0:
            continue
        u, h, tp, d = grilles
        w = sel / Pc
        if methode == "moyenne":
            hr = float((w * h).sum()); dr = _moyenne_circulaire(d, w)
        elif methode == "dommage":
            hr = float(((w * h ** m).sum()) ** (1.0 / m)); dr = _moyenne_circulaire(d, w)
        else:  # maximum
            hr = float(h[sel > 0].max()); dr = float(d.flat[np.argmax(sel)])
        valeur_axe = float(np.take(mid[axe_classes], c))
        ligne = {"U": float((w * u).sum()), "Hs": hr, "Tp": float((w * tp).sum()), "mis": dr, "P": float(Pc)}
        if axe_classes == "U":
            ligne["U"] = valeur_axe
        lignes.append(ligne)
    return pd.DataFrame(lignes)


def occurrences(df, heures=HEURES_PAR_AN, tolerance=TOLERANCE_OCCURRENCES):
    """Ajoute `O_h` (heures par an) et `O_pct` ; échoue si Σ O_pct ≠ 100 à `tolerance`. Si des classes ont
    été écartées en amont (Σ P < 1), l'appelant doit renormaliser **explicitement** : pas de silence."""
    out = df.copy()
    out["O_h"] = out["P"] * heures
    out["O_pct"] = 100.0 * out["P"]
    ecart = abs(out["O_pct"].sum() - 100.0) / 100.0
    if ecart > tolerance:
        raise ValueError(f"Σ O_j = {out['O_pct'].sum():.12g} % ≠ 100 % (écart relatif {ecart:.3g} > "
                         f"tolérance {tolerance:g} : TOLERANCE_OCCURRENCES) ; classes écartées ?")
    return out


def _classe(valeurs, bords):
    return np.clip(np.digitize(valeurs, bords) - 1, 0, len(bords) - 2)


def representativite(t, df):
    """Compare la LCT `df` au site `t` : marginales par paramètre (site contre LCT) et énergie de houle
    `E = Σ P·Hs²`. Renvoie `{"marginales": {axe: DataFrame}, "energie": {...}}`."""
    marg = {}
    for axe, col in zip(AXES, ("U", "Hs", "Tp", "mis")):
        site = marginales(t, axe)
        idx = _classe(df[col].to_numpy(), t.bords[axe])
        lct = np.bincount(idx, weights=df["P"].to_numpy(), minlength=len(site))
        marg[axe] = pd.DataFrame({"site": site.to_numpy(), "lct": lct}, index=site.index)
    h2 = t.milieux("Hs") ** 2
    e_site = float((t.P.sum(axis=(0, 2, 3)) * h2).sum())
    e_lct = float((df["P"] * df["Hs"] ** 2).sum())
    return {"marginales": marg,
            "energie": {"E_site": e_site, "E_lct": e_lct, "ecart_relatif": (e_lct - e_site) / e_site,
                        "P_lct": float(df["P"].sum())}}


def reconstruire(t, df):
    """Remet les états de mer `df` (U, Hs, Tp, mis, P) dans un tableau de la forme de `t` — l'inverse du
    lumping « identité » ; sert à vérifier qu'il restitue la table."""
    P = np.zeros_like(t.P)
    ix = [_classe(df[c].to_numpy(), t.bords[a]) for a, c in zip(AXES, ("U", "Hs", "Tp", "mis"))]
    np.add.at(P, tuple(ix), df["P"].to_numpy())
    return P


def exporter_lct(df, chemin_lct, chemin_etats, *, z_table, z_hub, loi, exposant=None, z0=None, tmax,
                 graine0, prefixe="M"):
    """Écrit une LCT lisible par `s9gm.cas` (colonnes `cas`, `fst.TMax`, `turbsim.URef`,
    `turbsim.RandSeed1`) et un fichier compagnon (états de mer : U à la table et au moyeu, Hs, Tp, mis, P,
    O_h, O_pct), car `cas` n'édite pas le fichier de houle. `z_table`, `z_hub`, `loi` (et `exposant` ou `z0`)
    sont **obligatoires** : le changement de hauteur du vent est un choix, jamais un défaut."""
    d = occurrences(df)
    d = d.reset_index(drop=True)
    d["cas"] = [f"{prefixe}{j:03d}" for j in range(len(d))]
    d["U_hub"] = hauteur_vent(d["U"], z_table, z_hub, loi=loi, exposant=exposant, z0=z0)
    with open(chemin_lct, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["cas", "fst.TMax", "turbsim.URef", "turbsim.RandSeed1"])
        for j, r in d.iterrows():
            w.writerow([r["cas"], tmax, f"{r['U_hub']:.4f}", graine0 + j])
    d[["cas", "U", "U_hub", "Hs", "Tp", "mis", "P", "O_h", "O_pct"]].rename(columns={"U": "U_table"}).to_csv(
        chemin_etats, index=False, float_format="%.10g")
    return Path(chemin_lct), Path(chemin_etats)
