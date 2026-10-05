"""s9gm.ancrage (SQUELETTE : trous à compléter : `catenaire_elastique`, `raideur_horizontale`) — caténaire élastique, prétension, raideur horizontale et courbe effort/déport d'un ancrage à lignes.

Fonctions : `poids_immerge`, `catenaire_elastique`, `raideur_horizontale`, `lire_moordyn`, `systeme_lignes`,
`courbe_deport`. Unités SI (N, m, kg).

Hypothèses (domaine de validité) : ligne **sans raideur de flexion**, **sans frottement de fond**, quasi-statique,
dans un plan vertical ; ligne posée sur le fond puis suspendue, ou entièrement suspendue ; plateforme sans mouvement
vertical ni rotation. Les données de ligne (masse linéique, diamètre, EA, longueur) viennent du fichier MoorDyn du
modèle public (`lire_moordyn`) : une seule source par grandeur.

### Bloc Théorie

*`catenaire_elastique` — l'effort d'une ligne d'ancrage.*

1. **Question physique** — Une ligne lourde et élastique relie un point fixe du fond à un chaumard de la plateforme : quel effort
   exerce-t-elle sur la plateforme, composante horizontale et composante verticale, pour une position donnée du chaumard ?
2. **Modèle** — caténaire élastique : pour une ligne de longueur non tendue `L`, de poids immergé linéique `w` et de
   raideur axiale `EA`, la position du chaumard `(x_F, z_F)` par rapport à l'ancre est une fonction de l'effort au
   chaumard `(H, V)` ; selon que `V` est inférieur ou supérieur à `w·L`, une longueur de ligne repose sur le fond ou toute
   la ligne est suspendue. On inverse ces relations par la méthode de Newton. **Domaine de validité** : sans
   raideur de flexion, sans frottement de fond, quasi-statique ; une ligne plus courte que la distance droite
   entre l'ancre et le chaumard reste calculable (élastique : elle est tendue et s'allonge), avec une tension très élevée.
3. **Ordre de grandeur attendu** — la méthode : comparer d'abord `L` à la distance droite (si elle la dépasse, la ligne est détendue) ; calculer la
   limite de la ligne inextensible (caténaire classique) et vérifier que l'effort élastique en est très proche pour
   une raideur grande ; l'effort vertical au chaumard est de l'ordre du poids de la partie suspendue.
4. **Ce que le modèle ne permet pas de conclure** — la réponse dynamique d'une ligne (masse ajoutée, amortissement,
   frottement de fond, ondes de tension) : un ancrage chargé vite se comporte autrement que la courbe quasi-statique.
5. **Renvois** — fiche F7 (caténaire statique) ; `data/geometrie_deepcwind.md` (ancrage) ; MoorDyn et MAP++ (modèles
   de référence) ; `ENONCE.md`, phase 4.

### Bloc Théorie

*`raideur_horizontale`, `systeme_lignes`, `courbe_deport` — la raideur du système d'ancrage.*

1. **Question physique** — Quand la plateforme se déplace d'un décalage donné, quelle force de rappel les trois lignes lui
   appliquent-elles, et quelle est la raideur de l'ancrage autour de la position d'équilibre ?
2. **Modèle** — la raideur horizontale d'une ligne est `∂H/∂x_F` à altitude de chaumard constante ; on la calcule de
   deux façons : analytiquement (inversion de la matrice jacobienne des relations de la caténaire) et par différence finie
   centrée. Les forces horizontales des trois lignes, projetées vers leurs ancres, se somment en une force de rappel
   en fonction du décalage. **Domaine de validité** : petits mouvements pour la raideur (linéarisation) ; la courbe effort/déport
   est non linéaire mais statique, sans effet du déport sur la hauteur du chaumard.
3. **Ordre de grandeur attendu** — la méthode : au décalage nul, la somme des efforts horizontaux est nulle (symétrie) ;
   un décalage vers une ligne la tend et détend les autres ; la raideur de la courbe croît avec le décalage.
4. **Ce que le modèle ne permet pas de conclure** — que la raideur statique soit celle qui s'applique aux mouvements de
   houle (dynamique de la ligne) ni que la plateforme n'oscille pas verticalement ou en tangage.
5. **Renvois** — fiche F7 (caténaire statique) ; fiche F8 (ancrage dynamique : MoorDyn contre quasi-statique) ;
   `ENONCE.md`, phase 4.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np


def poids_immerge(masse_air, diametre, rho, g=9.80665):
    """Poids immergé linéique `w = (m_air − ρ π d²/4) g` (le diamètre sert à la poussée)."""
    w = (masse_air - rho * math.pi * diametre ** 2 / 4.0) * g
    if w <= 0:
        raise ValueError(f"poids immergé linéique {w:.4g} N/m ≤ 0 : la ligne flotte")
    return w


@dataclass(frozen=True)
class EffortLigne:
    H: float            # effort horizontal au chaumard (N)
    V: float            # effort vertical au chaumard (N)
    suspendue: bool     # vrai si toute la ligne est suspendue
    L_fond: float       # longueur posée sur le fond (m)

    @property
    def tension(self):
        return math.hypot(self.H, self.V)


def catenaire_elastique(x_F, z_F, L, EA, w):
    """Effort (H, V) au chaumard d'une caténaire élastique sans frottement de fond. `x_F`, `z_F` : position du chaumard
    par rapport à l'ancre (m, z vers le haut). Refuse w, EA ou L ≤ 0, z_F ≤ 0 ou x_F < 0. Une ligne plus courte que la
    distance droite est acceptée (ligne élastique tendue : la tension l'allonge)."""
    raise NotImplementedError('trou : voir la rubrique « Modèle » du bloc Théorie ; exprimez la position du chaumard en fonction de (H, V) pour les deux branches (posée puis suspendue ; entièrement suspendue), puis inversez par Newton ; refusez w, EA, L ≤ 0 et z_F ≤ 0 par une erreur qui nomme le paramètre ; renvoyez un `EffortLigne`.')


def raideur_horizontale(x_F, z_F, L, EA, w, *, methode="analytique", pas=0.01):
    """Raideur horizontale `∂H/∂x_F` (z_F fixe), en N/m : `methode` « analytique » (jacobienne) ou « difference_finie »
    (centrée, pas en m)."""
    raise NotImplementedError('trou : `∂H/∂x_F` à z_F constant ; deux méthodes (« analytique » par la jacobienne de la caténaire, « difference_finie » centrée) qui doivent concorder ; appuyez-vous sur `catenaire_elastique`.')


# ------------------------------------------------------------------------ système de lignes -------------------
@dataclass(frozen=True)
class Ligne:
    ancre: tuple          # (x, y, z) de l'ancre (m)
    chaumard: tuple       # (x, y, z) du chaumard par rapport au centre de la plateforme au repos (m)
    L: float
    EA: float
    w: float


def lire_moordyn(chemin, rho, g=9.80665):
    """Lignes du fichier MoorDyn (blocs LINE TYPES, POINTS, LINES) : points « Fixed » = ancres, « Vessel » = chaumards."""
    txt = Path(chemin).read_text().splitlines()
    sect = None
    types, points, lignes = {}, {}, []
    for l in txt:
        if l.startswith("-") and "LINE TYPES" in l.upper():
            sect = "types"; continue
        if l.startswith("-") and "POINTS" in l.upper() and "NODE" not in l.upper():
            sect = "points"; continue
        if l.startswith("-") and re.search(r"\bLINES\b", l.upper()):
            sect = "lignes"; continue
        if l.startswith("-"):
            sect = None; continue
        p = l.split()
        if not p or p[0].startswith("(") or p[0] in ("Name", "ID"):
            continue
        if sect == "types" and len(p) >= 4:
            types[p[0]] = {"d": float(p[1]), "m": float(p[2]), "EA": float(p[3])}
        elif sect == "points" and len(p) >= 5 and p[1] in ("Fixed", "Vessel", "Body1"):
            points[int(p[0])] = (p[1], float(p[2]), float(p[3]), float(p[4]))
        elif sect == "lignes" and len(p) >= 5:
            lignes.append((p[1], int(p[2]), int(p[3]), float(p[4])))
    out = []
    for tn, a, b, L in lignes:
        t = types[tn]
        pa, pb = points[a], points[b]
        anc, cha = (pa, pb) if pa[0] == "Fixed" else (pb, pa)
        out.append(Ligne(anc[1:], cha[1:], L, t["EA"], poids_immerge(t["m"], t["d"], rho, g)))
    return out


def systeme_lignes(lignes, deport_xy=(0.0, 0.0)):
    """Force horizontale (FX, FY) exercée sur la plateforme par les lignes pour un décalage `deport_xy` (m), plateforme
    sans mouvement vertical ni rotation ; renvoie `(FX, FY, efforts)` avec `efforts` la liste des `EffortLigne`."""
    FX = FY = 0.0
    efforts = []
    for li in lignes:
        fx, fy, fz = li.chaumard[0] + deport_xy[0], li.chaumard[1] + deport_xy[1], li.chaumard[2]
        dx, dy = li.ancre[0] - fx, li.ancre[1] - fy
        d = math.hypot(dx, dy)
        e = catenaire_elastique(d, fz - li.ancre[2], li.L, li.EA, li.w)
        efforts.append(e)
        FX += e.H * dx / d
        FY += e.H * dy / d
    return FX, FY, efforts


def courbe_deport(lignes, deports, direction="x"):
    """Force de rappel `(FX, FY)` pour chaque décalage de `deports` (m) le long de `direction` ∈ {« x », « y »}."""
    out = []
    for u in deports:
        fx, fy, _ = systeme_lignes(lignes, (u, 0.0) if direction == "x" else (0.0, u))
        out.append((fx, fy))
    return np.array(out)
