"""Tests de s9gm.fatigue (squelette public). Critères écrits AVANT le code : `_Reserve/S9_T3_fatigue/CRITERE_fatigue.md`
du dépôt d'enseignement (commit 883eae1). Courbe S-N d'école (log ā = 12, m = 3), **valeurs non DNV**.

Tant que les trous de `s9gm/fatigue.py` (`rainflow`, `del_court_terme`, `del_long_terme`, `miner`) ne sont pas
complétés, les tests qui les appellent sont « attendus en échec » (xfail, NotImplementedError). Contre la version
complète de l'enseignant (`S9GM_FATIGUE_COMPLET=<dossier>`), ils passent tous.

Variables tenues égales : la série (sinusoïde), l'étendue (100), la courbe d'école, m = 3, n_eq = 600.
Variables qui bougent : l'implémentation (squelette complété ou version complète).
"""
import importlib.util
import math
import os
import sys
from pathlib import Path

import numpy as np
import pytest

COMPLET = os.environ.get("S9GM_FATIGUE_COMPLET")


def _charger():
    if COMPLET:
        spec = importlib.util.spec_from_file_location("fatigue_complet", Path(COMPLET) / "fatigue.py")
        mod = importlib.util.module_from_spec(spec)
        sys.modules["fatigue_complet"] = mod              # requis par dataclasses
        spec.loader.exec_module(mod)
        return mod
    from s9gm import fatigue
    return fatigue


fat = _charger()
trou = pytest.mark.xfail(condition=not COMPLET, raises=NotImplementedError, strict=False,
                         reason="attendu en échec tant que le trou n'est pas complété")

M, N_EQ = 3.0, 600.0
COURBE = fat.CourbeSN(log_a1=12.0, m1=3.0, k=0.2, source="courbe d'école, non DNV")


def sinus(amplitude=50.0, periodes=300, pts=40):
    k = np.arange(periodes * pts + 1)
    return amplitude * np.cos(2 * np.pi * k / pts)             # commence et finit sur un pic


# ---- parties complètes (pas des trous) ---------------------------------------------------------------
def test_inversions_gardent_pics_et_creux():
    np.testing.assert_array_equal(fat.inversions([0, 1, 2, 1, 0, 0, -1, 3]), [0, 2, -1, 3])


def test_courbe_sn_nombre_de_cycles_a_la_main():
    assert fat.CourbeSN(12.0, 3.0).nombre_cycles(100.0) == pytest.approx(10 ** (12 - 3 * math.log10(100)), rel=1e-12)  # 1e6


def test_courbe_sn_correction_d_epaisseur():
    n25, n50 = COURBE.nombre_cycles(100.0, t=25, t_ref=25), COURBE.nombre_cycles(100.0, t=50, t_ref=25)
    assert n25 / n50 == pytest.approx(2 ** (0.2 * 3.0), rel=1e-12)
    assert COURBE.nombre_cycles(100.0, t=10, t_ref=25) == pytest.approx(n25, rel=1e-12)   # t <= t_ref : pas de correction


def test_courbe_bilineaire_continue_au_coude():
    s0 = 10 ** ((12.0 - 7.0) / 3.0)                            # étendue au coude de 1e7 cycles
    c = fat.CourbeSN(12.0, 3.0, 7.0 + 5.0 * math.log10(s0), 5.0, 1e7)
    assert c.nombre_cycles(s0 * 1.0000001) == pytest.approx(1e7, rel=1e-5)
    assert c.nombre_cycles(s0 * 0.99999) == pytest.approx(1e7, rel=1e-3)
    assert c.nombre_cycles(0.5 * s0) == pytest.approx(10 ** (7.0 + 5.0 * math.log10(s0) - 5.0 * math.log10(0.5 * s0)), rel=1e-12)


def test_dff_verif():
    assert fat.dff_verif(0.05, 10)["ok"] and not fat.dff_verif(0.2, 10)["ok"]


# ---- C1 : sinusoïde, calcul à la main (trous) ----------------------------------------------------------
@trou
def test_rainflow_sinusoide_cycles_complets():
    r = fat.rainflow(sinus())
    assert r["compte"].sum() == pytest.approx(300.0, abs=1e-9)
    np.testing.assert_allclose(r["etendue"], 100.0, rtol=1e-9)


@trou
def test_del_court_terme_sinusoide_a_la_main():
    attendu = 100.0 * 0.5 ** (1.0 / 3.0)                       # (300·100³/600)^(1/3) = 79,3701
    assert fat.del_court_terme([100.0], [300.0], M, N_EQ) == pytest.approx(attendu, rel=1e-9)
    r = fat.rainflow(sinus())
    assert fat.del_court_terme(r["etendue"], r["compte"], M, N_EQ) == pytest.approx(attendu, rel=1e-9)


@trou
def test_dommage_sinusoide_courbe_d_ecole():
    assert fat.miner([100.0], [300.0], COURBE) == pytest.approx(300.0 / 1e6, rel=1e-9)     # 3,0e-4
    r = fat.rainflow(sinus())
    assert fat.miner(r["etendue"], r["compte"], COURBE) == pytest.approx(3.0e-4, rel=1e-9)


@trou
def test_dommage_epaisseur_double():
    d25 = fat.miner([100.0], [300.0], COURBE, t=25, t_ref=25)
    d50 = fat.miner([100.0], [300.0], COURBE, t=50, t_ref=25)
    assert d50 / d25 == pytest.approx(2 ** 0.6, rel=1e-9)


# ---- C2 : étendue contre amplitude -----------------------------------------------------------------------
@trou
def test_amplitude_a_la_place_de_l_etendue_donne_un_autre_resultat():
    attendu = 100.0 * 0.5 ** (1.0 / 3.0)
    mauvais = fat.del_court_terme([50.0], [300.0], M, N_EQ)             # amplitude passée à la place de l'étendue
    assert not math.isclose(mauvais, attendu, rel_tol=1e-6)             # le calcul à la main ne passe plus
    assert mauvais == pytest.approx(attendu / 2.0, rel=1e-9)            # DEL divisé par 2
    d_ok, d_mauvais = fat.miner([100.0], [300.0], COURBE), fat.miner([50.0], [300.0], COURBE)
    assert d_ok / d_mauvais == pytest.approx(2.0 ** M, rel=1e-9)        # dommage divisé par 2^m = 8


# ---- C3 : séquence d'exemple ASTM E1049, dérivation à la main -----------------------------------------------
@trou
def test_rainflow_sequence_exemple_e1049():
    # Méthode à trois points, à la main : demi-cycles 3, 4, 8, 9, 8, 6 et un cycle complet 4.
    r = fat.rainflow([-2, 1, -3, 5, -1, 3, -4, 4, -2])
    comptes = r.groupby("etendue")["compte"].sum().to_dict()
    assert comptes == {3.0: 0.5, 4.0: 1.5, 6.0: 0.5, 8.0: 1.0, 9.0: 0.5}
    assert r["compte"].sum() == 4.0


# ---- DEL long terme ----------------------------------------------------------------------------------------
@trou
def test_del_long_terme_a_la_main():
    # deux états : Oj = 0,25 et 0,75, DEL court terme 10 et 20, m = 3 : (0,25·10³ + 0,75·20³)^(1/3)
    assert fat.del_long_terme([10.0, 20.0], [0.25, 0.75], 3.0) == pytest.approx((0.25 * 1e3 + 0.75 * 8e3) ** (1 / 3), rel=1e-12)


@trou
def test_del_long_terme_refuse_une_somme_differente_de_un():
    with pytest.raises(ValueError):
        fat.del_long_terme([10.0, 20.0], [0.25, 0.5], 3.0)
    assert fat.del_long_terme([10.0, 20.0], [0.25, 0.5], 3.0, exiger_somme_un=False) > 0
