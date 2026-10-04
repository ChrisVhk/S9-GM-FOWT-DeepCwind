"""Tests de s9gm.structure (squelette public). Critères écrits AVANT le code : `_Reserve/S9_T4_structure/CRITERE_structure.md`
du dépôt d'enseignement (commit 37e746c).

Les trous (`von_mises`, `verifier_domaine_efthymiou`, `scf_ty_*`) font échouer (xfail, NotImplementedError) les tests
qui les appellent tant qu'ils ne sont pas complétés ; contre la version complète de l'enseignant
(`S9GM_STRUCTURE_COMPLET=<dossier>`), tous passent. Aucune valeur de norme n'est écrite ici : les bornes se lisent dans
DNV-RP-C203 (annexe B), page à citer ; les tests de domaine n'emploient que des valeurs absurdes (très hors domaine).

Variables tenues égales : la formule de Von Mises, la géométrie de la section d'essai. Variables qui bougent :
l'implémentation (squelette complété ou version complète).
"""
import importlib.util
import math
import os
import sys
from pathlib import Path

import numpy as np
import pytest

COMPLET = os.environ.get("S9GM_STRUCTURE_COMPLET")


def _charger():
    if COMPLET:
        sys.path.insert(0, str(COMPLET))
        spec = importlib.util.spec_from_file_location("structure_complet", Path(COMPLET) / "structure.py")
        mod = importlib.util.module_from_spec(spec)
        sys.modules["structure_complet"] = mod
        spec.loader.exec_module(mod)
        return mod
    from s9gm import structure
    return structure


st = _charger()
trou = pytest.mark.xfail(condition=not COMPLET, raises=NotImplementedError, strict=False,
                         reason="attendu en échec tant que le trou n'est pas complété")


# ---- parties complètes ---------------------------------------------------------------------------------------
def test_section_tubulaire_a_la_main():
    A, I, W = st.section_tubulaire(1.0, 0.02)
    d = 1.0 - 0.04
    assert A == pytest.approx(math.pi / 4 * (1 - d * d), rel=1e-12)
    assert I == pytest.approx(math.pi / 64 * (1 - d ** 4), rel=1e-12)
    assert W == pytest.approx(I / 0.5, rel=1e-12)


def test_contrainte_de_flexion_et_section_mince():
    A, I, W = st.section_tubulaire(1.0, 0.02)
    sigma = st.contrainte_flexion(1000.0, 1.0, I)                       # M = 1000 (unité de force·longueur quelconque)
    assert sigma == pytest.approx(1000.0 * 0.5 / I, rel=1e-9)
    # paroi mince : critère S5 « ≤ 5 % » avec le diamètre extérieur ; mesuré ≈ 6 % pour t/D = 0,02 (l'erreur de la formule
    # mince à diamètre extérieur est ≈ 3 t/D) → avertissement + valeur consignée ; avec le diamètre moyen D − t : ≤ 1 %.
    mince_ext = 4 * 1000.0 / (math.pi * 1.0 ** 2 * 0.02)
    if abs(mince_ext / sigma - 1) > 0.05:
        import warnings
        warnings.warn(f"section mince à diamètre extérieur : écart {mince_ext / sigma - 1:+.3f} > 5 % (critère S5)")
    assert sigma == pytest.approx(4 * 1000.0 * 1.0 / (math.pi * 0.98 ** 3 * 0.02), rel=0.01)   # I ≈ π d_m³ t/8, d_m = D − t, fibre extérieure


def test_effort_axial_entretoise_a_la_main():
    assert st.effort_axial_entretoise(1000.0, 0.0, partage=0.5) == pytest.approx(500.0, rel=1e-12)
    assert st.effort_axial_entretoise(1000.0, 60.0, partage=0.5) == pytest.approx(250.0, rel=1e-12)
    with pytest.raises(TypeError):
        st.effort_axial_entretoise(1000.0, 0.0)                         # partage obligatoire


# ---- S1 : Von Mises (trou) -----------------------------------------------------------------------------------------
@trou
def test_von_mises_uniaxial_redonne_la_contrainte_appliquee():
    assert st.von_mises(123.4) == pytest.approx(123.4, rel=1e-12)
    assert st.von_mises(-77.0) == pytest.approx(77.0, rel=1e-12)


@trou
def test_von_mises_cisaillement_pur_racine_de_trois():
    assert st.von_mises(0.0, txy=10.0) == pytest.approx(10.0 * math.sqrt(3.0), rel=1e-12)


@trou
def test_von_mises_biaxial_egal_et_hydrostatique():
    assert st.von_mises(50.0, 50.0) == pytest.approx(50.0, rel=1e-12)
    assert st.von_mises(80.0, 80.0, 80.0) == pytest.approx(0.0, abs=1e-12)


@trou
def test_von_mises_normale_plus_cisaillement():                       # forme utilisée pour une section : √(σ² + 3τ²)
    assert st.von_mises(60.0, txy=20.0) == pytest.approx(math.sqrt(60.0 ** 2 + 3 * 20.0 ** 2), rel=1e-12)


# ---- S2 : domaine (trou) : valeurs très hors domaine seulement ---------------------------------------------------
@trou
def test_appel_dans_un_domaine_courant_ne_leve_rien():
    st.verifier_domaine_efthymiou(0.5, 0.5, 15.0, 12.0, 90.0)


@trou
@pytest.mark.parametrize("nom,kw", [("beta", dict(beta=50.0)), ("tau", dict(tau=50.0)), ("gamma", dict(gamma=5000.0)),
                                    ("alpha", dict(alpha=5000.0)), ("theta_deg", dict(theta_deg=500.0))])
def test_hors_domaine_leve_une_erreur_qui_nomme_le_parametre(nom, kw):
    args = dict(beta=0.5, tau=0.5, gamma=15.0, alpha=12.0, theta_deg=90.0) | kw
    with pytest.raises(st.HorsDomaineError, match=nom):
        st.verifier_domaine_efthymiou(**args)


@trou
def test_hors_domaine_est_aussi_refuse_par_les_scf():
    with pytest.raises(st.HorsDomaineError):
        st.scf_ty_axial_encastre(50.0, 0.5, 15.0, 12.0, 90.0)
    with pytest.raises(st.HorsDomaineError):
        st.scf_ty_flexion_plan(0.5, 50.0, 15.0, 12.0, 90.0)


@trou
def test_scf_domaine_courant_superieur_a_un():
    for v in st.scf_ty_axial_encastre(0.5, 0.5, 15.0, 12.0, 90.0).values():
        assert v > 1.0
    for v in st.scf_ty_flexion_plan(0.5, 0.5, 15.0, 12.0, 90.0).values():
        assert v > 1.0
