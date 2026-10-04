"""s9gm.hydro — hydrostatique, dispersion et périodes propres d'un flotteur à membres cylindriques.

Fonctions : `dispersion`, `longueur_onde`, `vitesse_orbitale`, `kc`, `d_sur_lambda`, `regime_morison`,
`lire_membres`, `geometrie_flottaison`, `raideurs_hydrostatiques`, `gm`, `periode_propre`, `lire_hst`,
`lire_masse_ajoutee`. Toutes les grandeurs sont en unités SI ; l'axe `z` est vertical vers le haut, origine à la
surface libre au repos (SWL) ; la masse ajoutée est un **paramètre explicite** de `periode_propre`.

Une seule source par grandeur : la géométrie (coordonnées et diamètres) vient de `data/geometrie_deepcwind.md`, lue
par `lire_membres`, jamais d'une saisie à la main.

### Bloc Théorie

*`dispersion`, `longueur_onde` — la relation entre fréquence et nombre d'onde.*

1. **Question physique** — Une houle de période donnée, en profondeur donnée, a quelle longueur d'onde ? C'est
   la première chose à savoir avant de dire si un flotteur « voit » la houle comme une onde longue ou courte devant
   lui.
2. **Modèle** — houle linéaire d'Airy en profondeur finie `h` : `ω² = g·k·tanh(k·h)` avec `ω = 2π/T`, `k = 2π/λ`.
   On résout pour `k` par la méthode de Newton à partir de la solution en profondeur infinie, jusqu'à un résidu
   relatif inférieur à une tolérance nommée. **Domaine de validité** : houle de faible cambrure (théorie linéaire),
   fond horizontal ; la fonction refuse `h ≤ 0` et `T ≤ 0` par une erreur qui nomme le paramètre.
3. **Ordre de grandeur attendu** — la méthode : vérifier les deux limites — profondeur infinie, où `k = ω²/g`, et
   eau peu profonde, où `k = ω/√(g·h)` — puis constater qu'entre les deux la longueur d'onde est toujours plus courte
   que celle de l'eau peu profonde et plus longue que celle de l'eau profonde.
4. **Ce que le modèle ne permet pas de conclure** — que la houle réelle soit sinusoïdale (c'est un spectre) ni que le
   comportement en cambrure forte, près du déferlement, soit linéaire.
5. **Renvois** — fiche F2 (houle linéaire) ; DNV-RP-C205, §3.2.2 (relation de dispersion et approximation
   explicite de la longueur d'onde) ; `ENONCE.md`, phase 0, séance 0b.

### Bloc Théorie

*`lire_membres`, `geometrie_flottaison`, `raideurs_hydrostatiques`, `lire_hst` — la raideur de rappel.*

1. **Question physique** — Quand le flotteur s'enfonce, s'incline, quelle force et quel moment de rappel la
   poussée d'Archimède exerce-t-elle, d'où viennent-ils, et comment les retrouver depuis la seule géométrie ?
2. **Modèle** — pour des membres cylindriques coupés par la surface libre : volume immergé `V`, centre de poussée
   `z_B`, aire de flottaison `A_wp` (un membre incliné coupe le plan en une ellipse de section `π D²/(4 cos θ)`) et ses
   moments d'inertie `I = ∫ x² dA`, `∫ y² dA`. Raideurs de poussée autour de l'origine (surface libre) :
   `K33 = ρ g A_wp`, `K44 = ρ g (∫y² dA + V z_B)`, `K55 = ρ g (∫x² dA + V z_B)`. **Domaine de validité** : petits
   mouvements autour de la flottaison au repos ; la raideur de gravité du poids du système n'y est pas incluse (elle
   se rajoute : voir `gm`) ; les extrémités inclinées des membres coupées par le plan horizontal sont négligées.
3. **Ordre de grandeur attendu** — la méthode : le volume immergé calculé doit redonner la poussée du poids du
   système ; `K33` doit se comparer à l'aire de flottaison des seules colonnes, puis à celle qui inclut les membres
   inclinés qui coupent le plan ; `K44` et `K55` sont des différences de deux grands termes — leur erreur relative
   est bien plus grande que celle de `K33`.
4. **Ce que le modèle ne permet pas de conclure** — que le maillage d'un code de diffraction (facettes) donne
   exactement la même aire que le cylindre idéal, ni que les raideurs hydrostatiques seules donnent la période
   propre : il faut le poids et la masse ajoutée.
5. **Renvois** — fiche F3 (hydrostatique) ; `data/geometrie_deepcwind.md` (membres) ; fichiers `.hst` du modèle
   (raideurs adimensionnelles, mise à l'échelle par `ρ g L^n`).

### Bloc Théorie

*`gm` — la hauteur métacentrique.*

1. **Question physique** — Un flotteur flottant droit est-il stable en inclinaison, et de combien ?
2. **Modèle** — `GM = I/V + z_B − z_G` (z vers le haut) avec `I` moment d'inertie de la surface de flottaison autour
   de l'axe de rotation passant par son centre, `V` le volume immergé, `z_B` le centre de poussée, `z_G` le centre de
   gravité du **système entier** (flotteur, ballast, tour, rotor). La raideur totale en inclinaison vaut
   `ρ g (I + V z_B) − M g z_G`. **Domaine de validité** : flottaison à l'équilibre (poussée égale au poids) ; sinon la
   formule donne une raideur et non un `GM`.
3. **Ordre de grandeur attendu** — la méthode : repérer le terme stabilisant (inertie de la flottaison) et le
   terme déstabilisant (centre de gravité au-dessus du centre de poussée) et vérifier leur signe avant tout calcul.
4. **Ce que le modèle ne permet pas de conclure** — que la stabilité statique suffise : poussée du vent sur le rotor,
   ancrage et dynamique la modifient.
5. **Renvois** — fiche F3 (hydrostatique) ; fiche F1 (poussée du rotor) ; `ENONCE.md`, phase 0, séance 0b.

### Bloc Théorie

*`periode_propre`, `lire_masse_ajoutee` — la fréquence où le flotteur résonne.*

1. **Question physique** — À quelle période un flotteur, déplacé puis lâché, oscille-t-il, et cette période est-elle
   proche de celles de la houle ?
2. **Modèle** — système à un degré de liberté : `T = 2π √((m + a)/K)` avec `m` masse (ou inertie) du système, `a`
   masse (ou inertie) **ajoutée** de l'eau entraînée, `K` raideur totale du degré de liberté. La masse ajoutée se lit
   dans la sortie d'un code de diffraction (`.1`, normalisée par `ρ L³` ou `ρ L⁵`). **Domaine de validité** : la
   masse ajoutée dépend de la fréquence ; la valeur à fréquence nulle n'est qu'une approximation à la résonance ;
   les lignes d'ancrage, ignorées ici, ajoutent de la raideur en dérive et peu en pilonnement.
3. **Ordre de grandeur attendu** — la méthode : pour le pilonnement, comparer la masse ajoutée lue à la masse du
   flotteur, en déduire la période, et la comparer à la période de houle dominante du site avant d'accepter le
   dimensionnement.
4. **Ce que le modèle ne permet pas de conclure** — que la période calculée soit la période mesurée : l'amortissement,
   le couplage entre degrés de liberté et l'ancrage la déplacent.
5. **Renvois** — fiche F5 (hydrodynamique potentielle, masse ajoutée) ; fiche F3 (hydrostatique) ;
   `seances/0b/README.md` (modèle flottant).

### Bloc Théorie

*`vitesse_orbitale`, `kc`, `d_sur_lambda`, `regime_morison` — quel modèle de force pour un membre ?*

1. **Question physique** — Un membre cylindrique dans la houle subit-il surtout une force de traînée, d'inertie, ou
   diffracte-t-il la houle (modèle potentiel) ? Les deux nombres sans dimension qui décident : `KC` et `D/λ`.
2. **Modèle** — vitesse orbitale linéaire au niveau `z` : `u = ω a cosh(k(z+h))/sinh(kh)` ; nombre de Keulegan-Carpenter
   `KC = u_max T / D` (rapport du déplacement de la particule au diamètre) ; `D/λ` (diamètre sur longueur d'onde).
   Le seuil de `D/λ` au-dessous duquel la théorie de Morison s'applique est un **paramètre obligatoire** de
   `regime_morison`, à lire dans la norme (page à citer). **Domaine de validité** : houle linéaire régulière, membre
   vertical isolé ; l'interaction entre membres n'est pas prise en compte.
3. **Ordre de grandeur attendu** — la méthode : en eau profonde à la surface, `u = π H/T` et `λ = g T²/(2π)` ;
   calculer `KC` et `D/λ` à la main avant de lancer la fonction.
4. **Ce que le modèle ne permet pas de conclure** — que les coefficients de traînée et d'inertie se déduisent de
   `KC` et de `D/λ` seuls (ils dépendent aussi du nombre de Reynolds et de la rugosité).
5. **Renvois** — fiche F4 (Morison) ; fiche F2 (cinématique de la houle) ; DNV-RP-C205 (domaine de validité du
   modèle de Morison).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[1]
GEOMETRIE_MD = RACINE / "data" / "geometrie_deepcwind.md"
TOLERANCE_NEWTON = 1e-13       # résidu relatif |ω² − g k tanh(kh)| / ω² visé
NITER_MAX = 60
# libellés (Tab. 3-10 de geometrie_deepcwind.md) dont on lit le diamètre ; préfixes d'abréviation des membres associés
_LIBELLES_DIAMETRES = {"Diamètre de la colonne centrale": ("MC",), "Diamètre des colonnes déportées": ("UC",),
                       "Diamètre des colonnes de base": ("BC",),
                       "Diamètre des pontons et croisillons": ("DU", "DL", "YU", "YL", "CB")}


def _lire_diametres(texte):
    d = {}
    for ligne in texte.splitlines():
        for lib, prefs in _LIBELLES_DIAMETRES.items():
            if ligne.startswith(f"| {lib}"):
                v = float(re.search(r"\|\s*([\d,]+)\s*m\s*\|?\s*$", ligne)[1].replace(",", "."))
                d.update({p: v for p in prefs})
    manquants = {p for ps in _LIBELLES_DIAMETRES.values() for p in ps} - set(d)
    if manquants:
        raise ValueError(f"diamètres introuvables dans la géométrie : {sorted(manquants)}")
    return d


# ---------------------------------------------------------------- houle -------------------------------------
def dispersion(periode, profondeur, g=9.80665):
    """Nombre d'onde `k` de ω² = g k tanh(k h) par Newton ; refuse T ≤ 0 et h ≤ 0 (erreur nommée)."""
    if periode <= 0:
        raise ValueError(f"periode = {periode} : doit être > 0")
    if profondeur <= 0:
        raise ValueError(f"profondeur = {profondeur} : doit être > 0")
    w = 2 * np.pi / periode
    k = max(w * w / g, w / np.sqrt(g * profondeur))                  # départ du côté sûr de la convexité
    for _ in range(NITER_MAX):
        th = np.tanh(k * profondeur)
        f = g * k * th - w * w
        df = g * th + g * k * profondeur * (1.0 - th * th)
        k_new = k - f / df
        if abs(g * k_new * np.tanh(k_new * profondeur) - w * w) <= TOLERANCE_NEWTON * w * w:
            return float(k_new)
        k = k_new
    raise RuntimeError(f"Newton n'a pas convergé en {NITER_MAX} itérations (T = {periode}, h = {profondeur})")


def longueur_onde(periode, profondeur, g=9.80665):
    return 2 * np.pi / dispersion(periode, profondeur, g)


def vitesse_orbitale(amplitude, periode, profondeur, z=0.0, g=9.80665):
    """Amplitude de la vitesse horizontale des particules à la cote `z` (≤ 0) : ω a cosh(k(z+h))/sinh(kh)."""
    k = dispersion(periode, profondeur, g)
    w = 2 * np.pi / periode
    return float(w * amplitude * np.cosh(k * (z + profondeur)) / np.sinh(k * profondeur))


def kc(amplitude, periode, profondeur, diametre, z=0.0, g=9.80665):
    """Nombre de Keulegan-Carpenter `u_max T / D`."""
    return vitesse_orbitale(amplitude, periode, profondeur, z, g) * periode / diametre


def d_sur_lambda(diametre, periode, profondeur, g=9.80665):
    return diametre / longueur_onde(periode, profondeur, g)


def regime_morison(d_sur_lam, *, seuil):
    """« morison » si D/λ < seuil, « diffraction » sinon. Le seuil est **obligatoire** : à lire dans la norme."""
    return "morison" if d_sur_lam < seuil else "diffraction"


# ---------------------------------------------------------------- géométrie ---------------------------------
def lire_membres(chemin=GEOMETRIE_MD):
    """Membres du tableau « Membres et coordonnées » de `geometrie_deepcwind.md` : liste de dicts `nom`,
    `abrev`, `p1`, `p2`, `diametre` (virgule décimale française lue). Une seule source de géométrie."""
    membres, dans = [], False
    texte = Path(chemin).read_text(encoding="utf-8")
    DIAMETRES = _lire_diametres(texte)                              # lus dans le même fichier : une seule source
    for ligne in texte.splitlines():
        if ligne.startswith("## Membres et coordonnées"):
            dans = True
            continue
        if dans and ligne.startswith("## "):
            break
        if dans and ligne.startswith("|"):
            cel = [c.strip() for c in ligne.strip("|").split("|")]
            if len(cel) < 5 or not cel[2].startswith("(") or not re.match(r"^\(-?[\d]", cel[2]):
                continue                                           # en-tête ou ligne de séparation
            pts = []
            for c in (cel[2], cel[3]):
                v = re.sub(r"[()]", "", c).split(", ")
                pts.append(np.array([float(x.replace(",", ".")) for x in v]))
            pref = cel[1][:2]
            if pref not in DIAMETRES:
                raise ValueError(f"préfixe de membre inconnu : {cel[1]}")
            membres.append({"nom": cel[0], "abrev": cel[1], "p1": pts[0], "p2": pts[1], "diametre": DIAMETRES[pref]})
    if not membres:
        raise ValueError(f"aucun membre lu dans {chemin}")
    return membres


@dataclass(frozen=True)
class Flottaison:
    V: float            # volume immergé (m³)
    z_B: float          # cote du centre de poussée (m, vers le haut, 0 = SWL)
    A_wp: float         # aire de flottaison (m²)
    x_wp: float         # abscisse du centre de la flottaison (m)
    y_wp: float
    Ix2: float          # ∫ x² dA autour de x = 0 (m⁴)
    Iy2: float          # ∫ y² dA autour de y = 0 (m⁴)


def geometrie_flottaison(membres, *, avec_membres_inclines=True):
    """Volume immergé, centre de poussée et propriétés de la section à la flottaison (SWL, z = 0) de cylindres.
    `avec_membres_inclines=False` ignore la section des membres inclinés qui coupent la SWL (essai d'attribution)."""
    V = Vz = A = Ax = Ay = Ix = Iy = 0.0
    for m in membres:
        p1, p2, D = m["p1"], m["p2"], m["diametre"]
        lo, hi = (p1, p2) if p1[2] <= p2[2] else (p2, p1)
        if lo[2] >= 0.0:
            continue
        L = float(np.linalg.norm(hi - lo))
        aire = np.pi * D * D / 4.0
        if hi[2] <= 0.0:                                            # entièrement immergé
            ell = L
            c = (lo + hi) / 2.0
        else:                                                       # coupé par la SWL
            t = (0.0 - lo[2]) / (hi[2] - lo[2])
            ell = t * L
            c = lo + (t / 2.0) * (hi - lo)
            f = lo + t * (hi - lo)                                  # centre de la section à la flottaison
            cos_t = (hi[2] - lo[2]) / L
            if abs(cos_t - 1.0) < 1e-12 or avec_membres_inclines:
                a_maj, b_min = D / (2.0 * cos_t), D / 2.0
                s = np.pi * a_maj * b_min
                phi = np.arctan2(hi[1] - lo[1], hi[0] - lo[0]) if cos_t < 1 - 1e-12 else 0.0
                I_a, I_b = np.pi * a_maj ** 3 * b_min / 4.0, np.pi * a_maj * b_min ** 3 / 4.0
                ix_own = I_a * np.cos(phi) ** 2 + I_b * np.sin(phi) ** 2     # ∫ x'² dA
                iy_own = I_a * np.sin(phi) ** 2 + I_b * np.cos(phi) ** 2
                A += s; Ax += s * f[0]; Ay += s * f[1]
                Ix += ix_own + s * f[0] ** 2
                Iy += iy_own + s * f[1] ** 2
        vol = aire * ell
        V += vol
        Vz += vol * c[2]
    if V <= 0:
        raise ValueError("aucun volume immergé")
    return Flottaison(V, Vz / V, A, Ax / A if A else 0.0, Ay / A if A else 0.0, Ix, Iy)


def raideurs_hydrostatiques(flot, rho, g=9.80665):
    """K33, K44, K55 (poussée seule, autour de l'origine à la SWL, comme un `.hst`) ; N/m et N·m/rad."""
    return {"K33": rho * g * flot.A_wp,
            "K44": rho * g * (flot.Iy2 + flot.V * flot.z_B),
            "K55": rho * g * (flot.Ix2 + flot.V * flot.z_B)}


def gm(flot, z_G, *, axe="x"):
    """`GM = I/V + z_B − z_G` (I autour de l'axe passant par le centre de la flottaison ; axe « x » : tangage,
    ∫x²dA ; « y » : roulis). `z_G` : cote du centre de gravité du système entier (m, vers le haut)."""
    if axe == "x":
        I = flot.Ix2 - flot.A_wp * flot.x_wp ** 2
    elif axe == "y":
        I = flot.Iy2 - flot.A_wp * flot.y_wp ** 2
    else:
        raise ValueError("axe : « x » (tangage) ou « y » (roulis)")
    return I / flot.V + flot.z_B - z_G


def periode_propre(raideur, masse, masse_ajoutee):
    """`T = 2π √((m + a)/K)`. Refuse une raideur ≤ 0 (instable) et une masse totale ≤ 0."""
    if raideur <= 0:
        raise ValueError(f"raideur = {raideur:g} : doit être > 0 (système instable)")
    if masse + masse_ajoutee <= 0:
        raise ValueError("masse + masse ajoutée doit être > 0")
    return float(2 * np.pi * np.sqrt((masse + masse_ajoutee) / raideur))


# ---------------------------------------------------------------- fichiers WAMIT ------------------------------
def lire_hst(chemin, rho, g=9.80665, ulen=1.0):
    """Matrice 6×6 dimensionnelle d'un `.hst` WAMIT : `C_ij × ρ g L^(2 + [i>3] + [j>3])`."""
    C = np.zeros((6, 6))
    for ligne in Path(chemin).read_text().splitlines():
        p = ligne.split()
        if len(p) == 3:
            i, j, v = int(p[0]), int(p[1]), float(p[2])
            C[i - 1, j - 1] = v * rho * g * ulen ** (2 + (i > 3) + (j > 3))
    return C


def lire_masse_ajoutee(chemin, i, j, periode, rho, ulen=1.0):
    """Masse ajoutée A_ij d'un `.1` WAMIT à la période `periode` (convention WAMIT : −1 = fréquence nulle, 0 = fréquence infinie),
    redimensionnée par ρ L^(3 + [i>3] + [j>3]). Échoue si la période n'est pas dans le fichier."""
    for ligne in Path(chemin).read_text().splitlines():
        p = ligne.split()
        if len(p) >= 4 and int(p[1]) == i and int(p[2]) == j and abs(float(p[0]) - periode) < 1e-9:
            return float(p[3]) * rho * ulen ** (3 + (i > 3) + (j > 3))
    raise KeyError(f"A({i},{j}) à la période {periode} absente de {chemin}")
