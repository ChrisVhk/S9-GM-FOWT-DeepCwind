"""s9gm.fatigue (SQUELETTE : quatre trous à compléter : `rainflow`, `miner`, `del_court_terme`, `del_long_terme`) — de la série temporelle de contrainte au dommage et au DEL.

Fonctions : `inversions`, `rainflow`, `CourbeSN` (+ `nombre_cycles`), `miner`, `dff_verif`, `del_court_terme`,
`del_long_terme`, `lire_serie`. **Toutes les grandeurs de contrainte de ce module sont des ÉTENDUES**
(`Δσ = σmax − σmin`, deux fois l'amplitude), jamais des amplitudes : les arguments s'appellent `etendues`.

Aucune valeur de courbe S-N n'est écrite ici : les paramètres `log ā`, `m`, le coude, la limite de fatigue et
l'exposant d'épaisseur `k` se lisent dans DNV-RP-C203 (Tab. 2-1 à 2-4 selon l'édition), et se passent à
`CourbeSN`. L'étudiant les lit dans la norme.

### Bloc Théorie

*`inversions` et `rainflow` — du signal aux cycles.*

1. **Question physique** — Un signal de contrainte irrégulier (vent turbulent, houle) n'est pas une suite de
   cycles : comment le découper en cycles d'étendue et de moyenne définies, pour pouvoir lui appliquer une courbe
   S-N établie sur des essais à amplitude constante ?
2. **Modèle** — on ne garde que les inversions (pics et creux), puis la méthode à trois points de la norme
   ASTM E1049 : on empile les inversions ; dès que l'étendue de la dernière variation X est au moins égale à celle
   de la précédente Y, Y est un cycle fermé — **complet** s'il ne contient pas le point de départ, **demi-cycle** sinon —
   et on retire les points concernés ; à la fin, la pile résiduelle donne des demi-cycles. Un cycle complet compte 1, un
   demi-cycle 0,5. **Domaine de validité** : un signal à une seule composante de contrainte, sans correction de
   contrainte moyenne ; l'étendue est la différence des deux extrema du cycle, pas l'amplitude.
3. **Ordre de grandeur attendu** — la méthode : sur un signal sinusoïdal régulier, tous les cycles ont l'étendue du
   signal et leur nombre est le nombre de périodes ; sur toute série, la somme des comptes est la moitié du nombre de
   variations entre inversions consécutives.
4. **Ce que le modèle ne permet pas de conclure** — que le comptage donne l'ordre des cycles (il le détruit) ni
   qu'il tienne compte de la contrainte moyenne ; et un signal court laisse une part importante de demi-cycles
   résiduels, dont le traitement change légèrement le résultat.
5. **Renvois** — fiche F8 (fatigue, rainflow) ; ASTM E1049 (méthode de comptage) ; DNV-RP-C203 §2.2 (cumul de dommage
   à partir des cycles comptés).

### Bloc Théorie

*`CourbeSN` et `nombre_cycles` — la courbe de résistance.*

1. **Question physique** — Combien de cycles d'une étendue donnée un détail soudé supporte-t-il avant la
   rupture, et comment cette résistance dépend-elle de l'épaisseur ?
2. **Modèle** — `log N = log ā − m·log(Δσ·(t/t_ref)^k)` (équation de la norme, section 2.4), avec deux pentes
   `m₁` puis `m₂` séparées par un coude (nombre de cycles du coude) ; pour `t ≤ t_ref` on prend `t = t_ref`.
   **Domaine de validité** : les paramètres sont ceux d'une classe de détail, d'un environnement et d'une édition
   de la norme donnés ; ce module ne les connaît pas, c'est à vous de les lire et de les citer.
3. **Ordre de grandeur attendu** — la méthode : à étendue fixée, calculer `N` sur chaque branche et vérifier que la
   courbe est continue au coude ; vérifier que doubler l'épaisseur multiplie le dommage par `2^(k·m)`.
4. **Ce que le modèle ne permet pas de conclure** — qu'une courbe soit valable hors de son domaine (détail,
   environnement, finition, protection) ni que les éditions de la norme soient interchangeables : certaines valeurs
   (exposant d'épaisseur de classes, courbe de joint tubulaire) ont changé entre éditions.
5. **Renvois** — fiche F8 (fatigue) ; DNV-RP-C203, section 2.4 (équations, tableaux de courbes, pages à citer) ;
   `ENONCE.md`, phase 3.

### Bloc Théorie

*`miner` et `dff_verif` — du comptage au dommage.*

1. **Question physique** — Combien de la vie du détail a-t-on consommé, et la marge est-elle suffisante ?
2. **Modèle** — règle de Palmgren-Miner : `D = Σ nᵢ / Nᵢ` (nᵢ cycles comptés d'étendue Δσᵢ, Nᵢ cycles à la rupture
   donnés par la courbe S-N) ; vérification `D · DFF ≤ 1` avec le facteur de sécurité de fatigue `DFF`.
   **Domaine de validité** : cumul linéaire, sans effet d'ordre ; les étendues sont celles du rainflow, avec leur
   comptage de demi-cycles.
3. **Ordre de grandeur attendu** — la méthode : pour un signal sinusoïdal, calculer à la main `n` et `N` et comparer
   le rapport ; vérifier que le dommage est multiplié par `2^m` si on double toutes les étendues.
4. **Ce que le modèle ne permet pas de conclure** — que `D < 1` garantisse l'absence de fissure : le dommage est un
   indicateur statistique, et le DFF couvre incertitude et conséquences d'une rupture, pas seulement le calcul.
5. **Renvois** — fiche F8 (fatigue) ; DNV-RP-C203 §2.2 (cumul de Palmgren-Miner ; le DFF y renvoie à DNV-OS-C101, section 6) ;
   `ENONCE.md`, phase 3.

### Bloc Théorie

*`del_court_terme` et `del_long_terme` — l'étendue équivalente.*

1. **Question physique** — Peut-on remplacer un signal irrégulier par une seule étendue constante qui produit le
   même dommage, pour comparer des cas et des composants sans refaire tout le calcul ?
2. **Modèle** — étendue équivalente à `n_eq` cycles : `Sₑ = (Σ nᵢ·Sᵢ^m / n_eq)^(1/m)` avec `n_eq = f_eq·T` ; long terme
   sur des états de mer d'occurrences `Oⱼ` : `Sₑₜ = (Σⱼ Oⱼ·Sₑ,ⱼ^m)^(1/m)`. **Domaine de validité** : `m` est la pente
   de la courbe S-N supposée unique (pas de coude) ; les `Oⱼ` somment à un, sauf demande explicite contraire ; le
   résultat dépend de `n_eq`, qu'il faut donner avec lui.
3. **Ordre de grandeur attendu** — la méthode : pour `n` cycles identiques d'étendue `S`, `Sₑ = S·(n/n_eq)^(1/m)` ;
   avec `n_eq = n`, le DEL est l'étendue elle-même ; changer `m` ne change pas ce cas particulier.
4. **Ce que le modèle ne permet pas de conclure** — que le DEL remplace une courbe S-N à deux pentes, ni que deux
   signaux de même DEL aient la même durée de vie pour une autre pente `m`.
5. **Renvois** — fiche F8 (fatigue) ; `s9gm.metocean` (les `Oⱼ`) ; DNV-RP-C203 (cumul de dommage) ;
   `ENONCE.md`, phase 3.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

TOLERANCE_SOMME_OCCURRENCES = 1e-6   # |Σ Oⱼ − 1| maximal accepté (sauf exiger_somme_un=False)


def inversions(serie):
    """Pics et creux d'une série (premier et dernier points inclus ; points consécutifs égaux fusionnés)."""
    x = np.asarray(serie, dtype=float)
    if x.ndim != 1 or x.size < 2:
        raise ValueError("série 1-D de deux points au moins attendue")
    x = x[np.concatenate([[True], np.diff(x) != 0])]            # fusionne les doublons consécutifs
    if x.size < 3:
        return x
    d = np.diff(x)
    garde = np.concatenate([[True], d[1:] * d[:-1] < 0, [True]])
    return x[garde]


def rainflow(serie):
    """Comptage rainflow (ASTM E1049, trois points) → DataFrame `etendue`, `moyenne`, `compte` (1 ou 0,5)."""
    raise NotImplementedError('trou : appliquez la méthode à trois points décrite dans le bloc Théorie à la liste `inversions(serie)` (pile, comparaison de X et Y, demi-cycle si Y contient le point de départ, résidu en demi-cycles) ; renvoyez un DataFrame `etendue`, `moyenne`, `compte`.')


@dataclass(frozen=True)
class CourbeSN:
    """Courbe S-N bilinéaire (ou à une pente) : `log N = log_a − m·log(Δσ·(t/t_ref)^k)`.

    `log_a1`, `m1` pour N ≤ `n_coude` ; `log_a2`, `m2` au-delà. Sans coude : `log_a2 = m2 = n_coude = None`.
    `k` : exposant d'épaisseur. Tous les paramètres sont à lire dans la norme (tableau et page à citer)."""
    log_a1: float
    m1: float
    log_a2: float | None = None
    m2: float | None = None
    n_coude: float | None = None
    k: float = 0.0
    source: str = ""

    def nombre_cycles(self, etendue, t=None, t_ref=None):
        """Nombre de cycles à la rupture pour une ÉTENDUE (pas une amplitude). `t` et `t_ref` (mm) : correction
        d'épaisseur ; `t ≤ t_ref` donne `t = t_ref`. Sans `t`, aucune correction."""
        s = np.asarray(etendue, dtype=float)
        if (s < 0).any():
            raise ValueError("étendue négative")
        if t is not None:
            if t_ref is None:
                raise ValueError("t_ref obligatoire avec t")
            s = s * (max(t, t_ref) / t_ref) ** self.k
        with np.errstate(divide="ignore"):
            logs = np.log10(s)
            n1 = 10.0 ** (self.log_a1 - self.m1 * logs)
            if self.log_a2 is None:
                return np.where(s > 0, n1, np.inf)
            n2 = 10.0 ** (self.log_a2 - self.m2 * logs)
        return np.where(s > 0, np.where(n1 <= self.n_coude, n1, n2), np.inf)


def miner(etendues, comptes, courbe, *, t=None, t_ref=None):
    """Dommage de Palmgren-Miner `D = Σ nᵢ / N(Δσᵢ)` ; `etendues` sont des ÉTENDUES."""
    raise NotImplementedError('trou : `D = Σ nᵢ / N(Δσᵢ)` avec `courbe.nombre_cycles` (déjà fournie) ; attention : `etendues` sont des ÉTENDUES.')


def dff_verif(dommage, dff):
    """Vérifie `D · DFF ≤ 1` ; renvoie le produit, la marge `1 − D·DFF` et le verdict."""
    prod = float(dommage) * float(dff)
    return {"dommage_x_dff": prod, "marge": 1.0 - prod, "ok": prod <= 1.0}


def del_court_terme(etendues, comptes, m, n_eq):
    """DEL court terme `Sₑ = (Σ nᵢ·Sᵢ^m / n_eq)^(1/m)` ; `n_eq = f_eq·T` ; `etendues` sont des ÉTENDUES."""
    raise NotImplementedError('trou : `Sₑ = (Σ nᵢ·Sᵢ^m / n_eq)^(1/m)` ; attention : `etendues` sont des ÉTENDUES, jamais des amplitudes.')


def del_long_terme(del_j, occurrences_j, m, *, exiger_somme_un=True, tolerance=TOLERANCE_SOMME_OCCURRENCES):
    """DEL long terme `Sₑₜ = (Σⱼ Oⱼ·Sₑ,ⱼ^m)^(1/m)`. Les `Oⱼ` doivent sommer à un (à `tolerance`) sauf
    `exiger_somme_un=False` (cas d'une densité non renormalisée, à dire)."""
    raise NotImplementedError('trou : `Sₑₜ = (Σⱼ Oⱼ·Sₑ,ⱼ^m)^(1/m)` ; refusez une somme des Oⱼ différente de un sauf `exiger_somme_un=False`.')


def lire_serie(chemin, canal, *, t_transitoire):
    """Série d'un canal d'une sortie OpenFAST, transitoire écarté (via `s9gm.lire`) → ndarray."""
    from s9gm import lire as _lire
    df, _ = _lire.lire(chemin)
    return df.loc[df["Time"] >= t_transitoire, canal].to_numpy(dtype=float)
