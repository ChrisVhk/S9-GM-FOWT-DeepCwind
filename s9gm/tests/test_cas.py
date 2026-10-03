"""Falsificateurs de s9gm.cas : un cas généré doit être identique, octet pour octet, à F01 fait à
la main ; une clé absente ou ambiguë doit échouer, pas passer en silence."""
import json

import pytest

from s9gm import cas

from .conftest import PRISE_EN_MAIN, MODELE


def test_fst_et_inflow_identiques_a_F01_fait_main(pref, lct_f01):
    (dossier,) = cas.generer_serie(lct_f01, MODELE, PRISE_EN_MAIN)
    for nom in ("main.fst", "config_inflow.dat"):
        genere = (dossier / nom).read_bytes()
        main = (PRISE_EN_MAIN / "F01" / nom).read_bytes()
        assert genere == main, f"{nom} généré diffère de F01/{nom} fait à la main"


def test_journal_des_parametres(pref, lct_f01):
    (dossier,) = cas.generer_serie(lct_f01, MODELE, PRISE_EN_MAIN)
    j = json.loads((dossier / "journal_cas.json").read_text(encoding="utf-8"))
    mods = {(m["cle"]): (m["avant"], m["apres"]) for m in j["modifications"]}
    assert mods["TMax"] == ("600", "200")
    assert mods["HWindSpeed"] == ("8", "7.5")
    assert j["modele"] == "../modele_fixe"


def test_modele_partage_non_modifie(pref, lct_f01):
    avant = (MODELE / "main.fst").read_bytes()
    cas.generer_serie(lct_f01, MODELE, PRISE_EN_MAIN)
    assert (MODELE / "main.fst").read_bytes() == avant


def test_cle_inconnue_echoue(pref):
    l = {"cas": pref + "_X", "fst.PasUneCle": "1"}
    with pytest.raises(KeyError, match="PasUneCle"):
        cas.generer_cas(l, MODELE, PRISE_EN_MAIN)


def test_prefixe_de_colonne_invalide(tmp_path):
    p = tmp_path / "lct.csv"
    p.write_text("cas,elastodyn.Foo\nX,1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="préfixe"):
        cas.lire_lct(p)


def test_cas_en_double(tmp_path):
    p = tmp_path / "lct.csv"
    p.write_text("cas,fst.TMax\nX,1\nX,2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="double"):
        cas.lire_lct(p)


def test_separateur_point_virgule(tmp_path):
    p = tmp_path / "lct.csv"
    p.write_text("cas;fst.TMax\nX;50\n", encoding="utf-8")
    assert cas.lire_lct(p) == [{"cas": "X", "fst.TMax": "50"}]


def test_remplacer_valeur_exige_une_seule_occurrence():
    with pytest.raises(KeyError):
        cas.remplacer_valeur(["1  A", "2  A"], "A", "3")
