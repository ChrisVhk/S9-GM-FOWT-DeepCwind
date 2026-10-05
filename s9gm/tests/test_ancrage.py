"""Tests de s9gm.ancrage (squelette public). Critères écrits AVANT le code : `_Reserve/S9_T4_ancrage/CRITERE_ancrage.md`
du dépôt d'enseignement (commit ecb0ca8). Aucune valeur d'essai ni de document de définition ici : seulement des contrôles
indépendants que vous pouvez refaire à la main (intégration de la ligne, limite inextensible, symétrie, raideur).

Tant que les trous de `s9gm/ancrage.py` (`catenaire_elastique`, `raideur_horizontale`) ne sont pas complétés, les tests qui
les appellent sont « attendus en échec » (xfail, NotImplementedError). Contre la version complète de l'enseignant
(`S9GM_ANCRAGE_COMPLET=<dossier>`), ils passent tous.

Variables tenues égales : géométrie et lignes du fichier MoorDyn du modèle public, ρ = 1025, g = 9,80665.
Variables qui bougent : l'implémentation (squelette complété ou version complète).
"""
import importlib.util
import math
import os
import sys
from pathlib import Path

import pytest
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

COMPLET = os.environ.get("S9GM_ANCRAGE_COMPLET")
RACINE = Path(__file__).parents[2]
MOORDYN = RACINE / "models/oc4_rtest/5MW_OC4Semi_WSt_WavesWN/NRELOffshrBsline5MW_OC4DeepCwindSemi_MoorDyn.dat"


def _charger():
    if COMPLET:
        spec = importlib.util.spec_from_file_location("ancrage_complet", Path(COMPLET) / "ancrage.py")
        mod = importlib.util.module_from_spec(spec)
        sys.modules["ancrage_complet"] = mod
        spec.loader.exec_module(mod)
        return mod
    from s9gm import ancrage
    return ancrage


an = _charger()
trou = pytest.mark.xfail(condition=not COMPLET, raises=NotImplementedError, strict=False,
                         reason="attendu en échec tant que le trou n'est pas complété")
RHO, G = 1025.0, 9.80665
LIGNES = an.lire_moordyn(MOORDYN, RHO, G)


# ---- parties complètes (pas des trous) -------------------------------------------------------------
def test_poids_immerge_a_la_main():
    assert an.poids_immerge(100.0, 0.1, 1000.0, 10.0) == pytest.approx((100.0 - 1000.0 * math.pi * 0.01 / 4) * 10.0, rel=1e-12)


def test_poids_immerge_ligne_qui_flotte_refusee():
    with pytest.raises(ValueError, match="flotte"):
        an.poids_immerge(1.0, 0.5, 1025.0)


def test_lecture_moordyn_trois_lignes_a_120_degres():
    assert len(LIGNES) == 3
    angles = sorted(math.degrees(math.atan2(li.ancre[1], li.ancre[0])) for li in LIGNES)
    ecarts = [angles[1] - angles[0], angles[2] - angles[1]]
    assert ecarts == pytest.approx([120.0, 120.0], abs=1e-4)  # coordonnées du fichier arrondies : 8e-6° d'écart observé
    for li in LIGNES:
        assert li.w > 0 and li.EA > 0 and li.L > 0 and li.ancre[2] < li.chaumard[2] < 0


# ---- trous : ce que votre implémentation doit satisfaire -----------------------------------------------
CAS = [("posée puis suspendue", 700.0, 186.0, 835.5, 7.5e8, 1100.0),
       ("entièrement suspendue", 500.0, 186.0, 535.0, 7.5e8, 300.0)]


@trou
@pytest.mark.parametrize("nom,xF,zF,L,EA,w", CAS)
def test_fermeture_par_integration_de_la_ligne(nom, xF, zF, L, EA, w):
    """Intégrer la ligne avec les efforts trouvés doit retomber sur le chaumard demandé."""
    e = an.catenaire_elastique(xF, zF, L, EA, w)
    s0 = max(L - e.V / w, 0.0)                    # longueur posée sur le fond (z = 0, T = H)

    def f(s, y):
        Vs = w * (s - s0) if s0 > 0 else e.V - w * s
        T = math.hypot(e.H, Vs)
        k = 1.0 + T / EA
        return [e.H / T * k, Vs / T * k]
    sol = solve_ivp(f, [s0, L] if s0 > 0 else [0.0, L], [s0 * (1.0 + e.H / EA), 0.0], rtol=1e-12, atol=1e-12)
    assert sol.y[0, -1] == pytest.approx(xF, rel=1e-6)
    assert sol.y[1, -1] == pytest.approx(zF, rel=1e-6)


@trou
def test_limite_inextensible_caténaire_classique():
    xF, zF, L, w = 780.0, 186.0, 835.5, 1100.0
    e = an.catenaire_elastique(xF, zF, L, 1e15, w)

    def reste(H):
        ell = math.sqrt(zF ** 2 + 2.0 * zF * H / w)
        return L - ell + (H / w) * math.asinh(w * ell / H) - xF
    H = brentq(reste, 1e3, 5e7, xtol=1e-12, rtol=1e-14)
    assert e.H == pytest.approx(H, rel=1e-6)
    assert e.V == pytest.approx(w * math.sqrt(zF ** 2 + 2.0 * zF * H / w), rel=1e-6)


@trou
def test_symetrie_decalage_nul():
    fx, fy, efforts = an.systeme_lignes(LIGNES)
    assert abs(fx) < 2e4 and abs(fy) < 2e4          # N ; somme nulle (trois lignes à 120° identiques à ~1 % près)
    assert all(e.tension > 0 for e in efforts)


@trou
def test_force_de_rappel_croit_avec_le_decalage_et_s_oppose_a_lui():
    courbe = an.courbe_deport(LIGNES, [2.0, 6.0, 10.0])
    fx = [c[0] for c in courbe]
    assert all(f < 0 for f in fx) and fx[0] > fx[1] > fx[2]       # force vers l'ancrage, croissante en module


@trou
@pytest.mark.parametrize("nom,xF,zF,L,EA,w", CAS)
def test_raideur_analytique_et_difference_finie_concordent(nom, xF, zF, L, EA, w):
    a = an.raideur_horizontale(xF, zF, L, EA, w)
    b = an.raideur_horizontale(xF, zF, L, EA, w, methode="difference_finie", pas=0.01)
    assert a == pytest.approx(b, rel=1e-4)
    assert a > 0


@trou
@pytest.mark.parametrize("args", [(800.0, 186.0, 835.5, 7.5e8, 0.0), (800.0, 186.0, 835.5, 0.0, 1100.0),
                                  (800.0, 186.0, 0.0, 7.5e8, 1100.0), (800.0, 0.0, 835.5, 7.5e8, 1100.0)])
def test_donnees_invalides_refusees(args):
    with pytest.raises(ValueError):
        an.catenaire_elastique(*args)
