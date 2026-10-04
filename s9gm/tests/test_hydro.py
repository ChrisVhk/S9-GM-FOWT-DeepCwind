"""Falsificateurs de s9gm.hydro. Critères et tolérances écrits AVANT le code : `_Reserve/S9_T4_hydro/CRITERE_hydro.md`
du dépôt d'enseignement (commit 953a372). Les tests comparent à des fichiers de modèle publics (`marin_semi.hst`,
`marin_semi.1`, HydroDyn et ElastoDyn de `models/oc4_rtest`) et à deux publications (Coulling et al. 2013, Tab. XIII ;
DNV-RP-C205 §3.2.2.4) ; aucune valeur de corrigé n'est écrite ici.

Variables tenues égales : ρ, g, ULEN, la géométrie de `geometrie_deepcwind.md`. Variables qui bougent : membres pris
en compte à la flottaison, maillage WAMIT contre cylindre exact, simplification de masse de la tour et du rotor.
"""
import math
import re
from pathlib import Path

import numpy as np
import pytest

from s9gm import hydro

RACINE = Path(__file__).resolve().parents[2]
OC4 = RACINE / "models" / "oc4_rtest"
HST = OC4 / "5MW_Baseline" / "HydroData" / "marin_semi.hst"
ADDED = OC4 / "5MW_Baseline" / "HydroData" / "marin_semi.1"
HYDRODYN = OC4 / "5MW_OC4Semi_WSt_WavesWN" / "NRELOffshrBsline5MW_OC4DeepCwindSemi_HydroDyn.dat"
ELASTO = OC4 / "5MW_OC4Semi_WSt_WavesWN" / "NRELOffshrBsline5MW_OC4DeepCwindSemi_ElastoDyn.dat"
FST = OC4 / "5MW_OC4Semi_WSt_WavesWN" / "5MW_OC4Semi_WSt_WavesWN.fst"


def cle(chemin, nom):
    for l in Path(chemin).read_text().splitlines():
        p = l.split()
        if len(p) > 1 and p[1] == nom:
            return float(p[0])
    raise KeyError(nom)


RHO, G = cle(FST, "WtrDens"), cle(FST, "Gravity")
ULEN = cle(HYDRODYN, "WAMITULEN")


@pytest.fixture(scope="module")
def flot():
    return hydro.geometrie_flottaison(hydro.lire_membres())


@pytest.fixture(scope="module")
def K(flot):
    return hydro.raideurs_hydrostatiques(flot, RHO, G)


# ---- H1 : volume ----------------------------------------------------------------------------------------
def test_H1_volume_egal_PtfmVol0(flot):
    assert flot.V == pytest.approx(cle(HYDRODYN, "PtfmVol0"), rel=0.01)


# ---- H2 : K33 ------------------------------------------------------------------------------------------
def test_H2_K33_egal_hst(K):
    assert K["K33"] == pytest.approx(hydro.lire_hst(HST, RHO, G, ULEN)[2, 2], rel=0.01)


def test_H2_attribution_sans_les_croisillons_l_ecart_est_plus_grand(K):
    sans = hydro.geometrie_flottaison(hydro.lire_membres(), avec_membres_inclines=False)
    k33_hst = hydro.lire_hst(HST, RHO, G, ULEN)[2, 2]
    e_avec = abs(K["K33"] / k33_hst - 1)
    e_sans = abs(RHO * G * sans.A_wp / k33_hst - 1)
    assert e_sans > e_avec and e_sans > 0.01            # l'écart de 1 % n'est tenu qu'avec les membres inclinés


# ---- H3 : K44 et K55 de poussée --------------------------------------------------------------------------
def test_H3_K44_K55_egaux_hst_a_10_pour_cent(K):
    C = hydro.lire_hst(HST, RHO, G, ULEN)
    assert K["K44"] == pytest.approx(C[3, 3], rel=0.10)
    assert K["K55"] == pytest.approx(C[4, 4], rel=0.10)


# ---- H4 : dispersion -------------------------------------------------------------------------------------
@pytest.mark.parametrize("T,h", [(10, 2000), (10, 100), (15, 30), (200, 1), (3, 5), (25, 200)])
def test_H4_residu_de_newton(T, h):
    k = hydro.dispersion(T, h)
    w = 2 * math.pi / T
    assert abs(w * w - G * k * math.tanh(k * h)) / (w * w) <= 1e-12


def test_H4_profondeur_infinie():
    w = 2 * math.pi / 10.0
    assert hydro.dispersion(10.0, 2000.0) == pytest.approx(w * w / G, rel=1e-9)


def test_H4_eau_peu_profonde():
    w = 2 * math.pi / 200.0
    assert hydro.dispersion(200.0, 1.0) == pytest.approx(w / math.sqrt(G * 1.0), rel=1e-3)


@pytest.mark.parametrize("T,d", [(10, 100), (15, 30)])
def test_H4_approximation_de_DNV_RP_C205(T, d):
    """DNV-RP-C205 (avril 2014) §3.2.2.4, p. 36-37 (pages rendues) : coefficients α1…α4 de la page 37."""
    a = (0.666, 0.445, -0.105, 0.272)
    w_ = 4 * math.pi ** 2 * d / (G * T ** 2)
    f = 1 + sum(ai * w_ ** (n + 1) for n, ai in enumerate(a))
    lam = T * math.sqrt(G * d) * math.sqrt(f / (1 + w_ * f))
    assert hydro.longueur_onde(T, d) == pytest.approx(lam, rel=0.01)


def test_H4_refus_parametres_invalides():
    with pytest.raises(ValueError, match="profondeur"):
        hydro.dispersion(10.0, 0.0)
    with pytest.raises(ValueError, match="periode"):
        hydro.dispersion(-1.0, 100.0)


# ---- H5 : périodes propres (Coulling et al. 2013, Tab. XIII, p. 023116-15 : colonne « Data ») ---------------
PUBLIE = {"heave": 17.5, "pitch": 26.8, "roll": 26.9}
# Masses de tour et de rotor-nacelle : `.ED.sum` d'OpenFAST v5.0.0 sur models/oc4_rtest (fichier non versionné) :
# « Tower Mass 249718 kg », « Tower-top Mass 349389,844 kg ».
M_TOUR, M_RNA = 249718.0, 349389.844


def md_plateforme():
    t = hydro.GEOMETRIE_MD.read_text(encoding="utf-8")
    nb = lambda motif: float(re.search(motif + r"[^|]*\|\s*([\d,]+)", t)[1].replace(",", "."))
    ex = lambda motif: float(re.search(motif + r"[^|]*\|\s*([\d,]+)\s*×10([⁰¹²³⁴⁵⁶⁷⁸⁹]+)", t)[1].replace(",", ".")) * 10 ** int("".join(
        "0123456789"["⁰¹²³⁴⁵⁶⁷⁸⁹".index(c)] for c in re.search(motif + r"[^|]*\|\s*[\d,]+\s*×10([⁰¹²³⁴⁵⁶⁷⁸⁹]+)", t)[1]))
    return {"M": ex("Masse de la plateforme"), "zcm": -nb("Centre de masse sous la SWL"),
            "Iroll": ex("Inertie en roulis"), "Ipitch": ex("Inertie en tangage")}


def systeme(flot):
    p = md_plateforme()
    h_tour, z_tour = cle(ELASTO, "TowerHt"), None
    base = cle(ELASTO, "TowerBsHt")
    z_tour = base + (h_tour - base) / 2.0                          # tour : masse à mi-hauteur
    z_hub = h_tour + cle(ELASTO, "Twr2Shft")                       # rotor-nacelle : à la hauteur du moyeu
    M = p["M"] + M_TOUR + M_RNA
    zG = (p["M"] * p["zcm"] + M_TOUR * z_tour + M_RNA * z_hub) / M
    L = h_tour - base
    def inertie(I_cm):
        return I_cm + p["M"] * p["zcm"] ** 2 + M_TOUR * z_tour ** 2 + M_TOUR * L ** 2 / 12.0 + M_RNA * z_hub ** 2
    return M, zG, inertie(p["Ipitch"]), inertie(p["Iroll"])


def test_H5_periodes_propres_contre_coulling(flot, K):
    M, zG, I55, I44 = systeme(flot)
    a33 = hydro.lire_masse_ajoutee(ADDED, 3, 3, 0, RHO, ULEN)
    a55 = hydro.lire_masse_ajoutee(ADDED, 5, 5, 0, RHO, ULEN)
    a44 = hydro.lire_masse_ajoutee(ADDED, 4, 4, 0, RHO, ULEN)
    K55 = K["K55"] - M * G * zG                      # raideur de gravité ajoutée ; ancrage négligé
    K44 = K["K44"] - M * G * zG
    T = {"heave": hydro.periode_propre(K["K33"], M, a33), "pitch": hydro.periode_propre(K55, I55, a55),
         "roll": hydro.periode_propre(K44, I44, a44)}
    print("\npériodes calculées :", {k: round(v, 2) for k, v in T.items()})
    assert T["heave"] == pytest.approx(PUBLIE["heave"], rel=0.10)
    assert T["pitch"] == pytest.approx(PUBLIE["pitch"], rel=0.20)
    assert T["roll"] == pytest.approx(PUBLIE["roll"], rel=0.20)


def test_gm_et_raideur_totale_coherents(flot, K):
    M, zG, *_ = systeme(flot)
    gm = hydro.gm(flot, zG, axe="x")
    # raideur totale = ρ g V GM si la poussée équilibre le poids ; sinon l'écart est le déséquilibre poussée/poids
    K55 = K["K55"] - M * G * zG
    ecart_equilibre = abs(RHO * flot.V - M) / M
    assert K55 == pytest.approx(RHO * G * flot.V * gm, rel=2 * ecart_equilibre + 0.02)


def test_periode_propre_refuse_une_raideur_negative():
    with pytest.raises(ValueError, match="raideur"):
        hydro.periode_propre(-1.0, 1.0, 1.0)


# ---- H6 : KC et D/λ ---------------------------------------------------------------------------------------
def test_H6_KC_en_eau_profonde():
    H, T, D = 6.0, 10.0, 12.0
    assert hydro.kc(H / 2, T, 200.0, D) == pytest.approx(math.pi * H / D, rel=1e-3)


def test_H6_D_sur_lambda_en_eau_profonde():
    D, T = 12.0, 10.0
    assert hydro.d_sur_lambda(D, T, 200.0) == pytest.approx(D / (G * T ** 2 / (2 * math.pi)), rel=1e-3)


def test_regime_morison_exige_un_seuil():
    with pytest.raises(TypeError):
        hydro.regime_morison(0.1)
    assert hydro.regime_morison(0.1, seuil=0.2) == "morison" and hydro.regime_morison(0.3, seuil=0.2) == "diffraction"
