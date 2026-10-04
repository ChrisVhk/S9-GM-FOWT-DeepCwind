"""Falsificateurs de s9gm.metocean.

Critère d'énergie de houle écrit AVANT l'essai : `_Reserve/S9_T2_metocean/CRITERE_energie_houle.md` du dépôt
d'enseignement (commit e46f86d), reproduit ici. Aucune tolérance n'est ajustée après coup.

Variables tenues égales : la table FLOATECH lue (mêmes P, mêmes classes), le pas du binning de départ, la
formule E = Σ P·Hs², la hauteur de vent (100 m), la normalisation Σ P = 1.
Variables qui bougent : la règle de lumping (identité, moyenne, maximum, dommage m = 2), le regroupement en
classes de vent, le nombre d'états de mer retenus.
"""
import numpy as np
import pandas as pd
import pytest

from s9gm import cas, metocean as mo

from .conftest import PRISE_EN_MAIN, MODELE  # noqa: F401

TOL_IDENTITE = 1e-12          # critère 1 et 4 : identités algébriques
TOL_MOYENNE = 0.25            # critère 2 : écart relatif maximal de la moyenne (par défaut, écrit avant l'essai)


@pytest.fixture(scope="module")
def t():
    return mo.lire()


def test_somme_des_probabilites_est_un(t):
    assert abs(t.P.sum() - 1.0) <= mo.TOLERANCE_SOMME


def test_lecture_echoue_si_la_somme_n_est_pas_un(tmp_path, t):
    f = tmp_path / "abime.bin"
    (t.P * 1.01).astype("<f8").tofile(f)
    with pytest.raises(ValueError, match="TOLERANCE_SOMME"):
        mo.lire(f)


def test_lecture_echoue_si_la_forme_ne_correspond_pas(tmp_path):
    f = tmp_path / "court.bin"
    np.zeros(10).astype("<f8").tofile(f)
    with pytest.raises(ValueError, match="forme"):
        mo.lire(f)


def test_marginales_somment_a_un(t):
    for axe in mo.AXES:
        assert abs(mo.marginales(t, axe).sum() - 1.0) < 1e-12


def test_binning_conserve_la_somme_et_somme_les_marginales(t):
    b = mo.binning(t, "U", 3)
    assert b.P.shape[0] == t.P.shape[0] // 3
    assert abs(b.P.sum() - 1.0) < 1e-12
    np.testing.assert_allclose(mo.marginales(b, "U").to_numpy(),
                               mo.marginales(t, "U").to_numpy().reshape(-1, 3).sum(axis=1), atol=1e-14)
    assert b.bords["U"][0] == t.bords["U"][0] and b.bords["U"][-1] == t.bords["U"][-1]


def test_binning_refuse_k_qui_ne_divise_pas(t):
    with pytest.raises(ValueError, match="divise"):
        mo.binning(t, "U", 4)


def test_somme_des_occurrences_est_cent_pour_cent(t):
    for methode, kw in [("identite", {}), ("moyenne", {}), ("maximum", {}), ("dommage", {"m": 2})]:
        df = mo.lumper(t, methode=methode, **kw)
        assert abs(mo.occurrences(df)["O_pct"].sum() - 100.0) <= 100.0 * mo.TOLERANCE_OCCURRENCES


def test_occurrences_refuse_une_somme_incomplete(t):
    df = mo.lumper(t, methode="identite")
    with pytest.raises(ValueError, match="TOLERANCE_OCCURRENCES"):
        mo.occurrences(df.iloc[: len(df) // 2])


def test_lumping_identite_restitue_la_table_d_origine(t):
    df = mo.lumper(t, methode="identite")
    assert len(df) == int((t.P > 0).sum())
    np.testing.assert_array_equal(mo.reconstruire(t, df), t.P)       # cellule à cellule, exactement


def test_energie_identite_egale_celle_du_site(t):
    r = mo.representativite(t, mo.lumper(t, methode="identite"))["energie"]
    assert abs(r["ecart_relatif"]) <= TOL_IDENTITE


def test_energie_dommage_m2_egale_celle_du_site(t):                  # critère 1
    r = mo.representativite(t, mo.lumper(t, methode="dommage", m=2))["energie"]
    assert abs(r["ecart_relatif"]) <= TOL_IDENTITE


def test_energie_moyenne_sous_le_site_dans_la_tolerance(t):          # critère 2
    r = mo.representativite(t, mo.lumper(t, methode="moyenne"))["energie"]
    assert r["E_lct"] <= r["E_site"]
    assert abs(r["ecart_relatif"]) <= TOL_MOYENNE, f"écart relatif {r['ecart_relatif']:.3f}"


def test_energie_maximum_au_dessus_du_site(t):                       # critère 3 : pas de borne supérieure
    r = mo.representativite(t, mo.lumper(t, methode="maximum"))["energie"]
    assert r["E_lct"] >= r["E_site"]


def test_ordre_moyenne_dommage_maximum(t):
    h = {m: mo.lumper(t, methode=m, **({"m": 2} if m == "dommage" else {}))["Hs"].to_numpy()
         for m in ("moyenne", "dommage", "maximum")}
    assert (h["moyenne"] <= h["dommage"] + 1e-12).all() and (h["dommage"] <= h["maximum"] + 1e-12).all()


def test_dommage_exige_m(t):
    with pytest.raises(ValueError, match="exposant"):
        mo.lumper(t, methode="dommage")


def test_hauteur_vent_est_explicite():
    with pytest.raises(TypeError):
        mo.hauteur_vent(10.0, 100.0, 90.0)                      # loi absente : refusé
    with pytest.raises(ValueError, match="exposant"):
        mo.hauteur_vent(10.0, 100.0, 90.0, loi="puissance")
    with pytest.raises(ValueError, match="z0"):
        mo.hauteur_vent(10.0, 100.0, 90.0, loi="logarithmique")
    assert mo.hauteur_vent(10.0, 100.0, 100.0, loi="puissance", exposant=0.12) == pytest.approx(10.0)
    assert mo.hauteur_vent(10.0, 100.0, 50.0, loi="puissance", exposant=0.12) < 10.0


def test_la_lct_exportee_est_relue_par_cas(tmp_path, t, pref):
    import shutil
    df = mo.lumper(t, methode="moyenne")
    lct, etats = mo.exporter_lct(df, tmp_path / "lct.csv", tmp_path / "etats.csv", z_table=100.0, z_hub=90.0,
                                 loi="puissance", exposant=0.12, tmax=300, graine0=1000, prefixe=f"{pref}_M")
    lignes = cas.lire_lct(lct)
    assert len(lignes) == len(df) and lignes[0]["turbsim.RandSeed1"] == "1000"
    et = pd.read_csv(etats)
    assert abs(et["O_pct"].sum() - 100.0) < 1e-6 and (et["U_hub"] < et["U_table"]).all()   # moyeu plus bas
    # relecture par cas.generer_cas : le gabarit à un trou, la graine vient de la LCT
    from .conftest import PRISE_EN_MAIN
    from .test_cas import GABARIT
    m = PRISE_EN_MAIN / f"{pref}_modele"
    shutil.copytree(MODELE, m)
    shutil.copy(GABARIT, m / "turbsim.inp")
    dossiers = cas.generer_serie(lct, m, PRISE_EN_MAIN, executer_turbsim=False)
    assert len(dossiers) == len(df)
