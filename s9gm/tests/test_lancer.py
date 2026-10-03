"""Falsificateurs de s9gm.lancer : un cas interrompu est repris ; un cas terminé n'est pas relancé."""
import stat

import pytest

from s9gm import cas, lancer

from .conftest import MODELE, PRISE_EN_MAIN, requiert_openfast


def _faux_openfast(chemin, corps):
    chemin.write_text("#!/bin/sh\n" + corps + "\n", encoding="utf-8")
    chemin.chmod(chemin.stat().st_mode | stat.S_IEXEC)
    return str(chemin)


def _cas_court(pref, nom="C1", tmax="5"):
    return cas.generer_cas({"cas": f"{pref}_{nom}", "fst.TMax": tmax, "inflow.WindType": "1",
                             "inflow.HWindSpeed": "7.5", "inflow.PLExp": "0.11"}, MODELE, PRISE_EN_MAIN)


def test_reprise_avec_faux_executable(pref, tmp_path):
    d = _cas_court(pref)
    # un faux calcul interrompu : journal sans phrase finale, sortie tronquée
    (d / "run.log").write_text("Time: 1 of 5 seconds\n", encoding="utf-8")
    (d / "main.outb").write_bytes(b"\x00\x01")
    assert not lancer.est_termine(d)
    ok = _faux_openfast(tmp_path / "fake_ok", 'echo "OpenFAST terminated normally."; : > main.outb')
    (res,) = lancer.lancer_serie([d], executable=ok, afficher=None)
    assert res["statut"] == "termine" and lancer.est_termine(d)
    # relance : le cas terminé n'est pas relancé
    (res2,) = lancer.lancer_serie([d], executable=str(tmp_path / "n_existe_pas"), afficher=None)
    assert res2["statut"] == "deja_termine"


def test_echec_si_pas_de_phrase_finale(pref, tmp_path):
    d = _cas_court(pref)
    ko = _faux_openfast(tmp_path / "fake_ko", 'echo "ERREUR"; : > main.outb')
    (res,) = lancer.lancer_serie([d], executable=ko, afficher=None)
    assert res["statut"] == "echec"


def test_delai_max_interrompt(pref, tmp_path):
    d = _cas_court(pref)
    lent = _faux_openfast(tmp_path / "fake_lent", "sleep 30")
    (res,) = lancer.lancer_serie([d], executable=lent, delai_max=1, afficher=None)
    assert res["statut"] == "interrompu"


def test_parallele_et_journal(pref, tmp_path):
    ds = [_cas_court(pref, f"C{i}") for i in range(3)]
    ok = _faux_openfast(tmp_path / "fake_ok", 'echo "OpenFAST terminated normally."; : > main.outb')
    journal = tmp_path / "journal.csv"
    res = lancer.lancer_serie(ds, coeurs=2, executable=ok, journal=journal, afficher=None)
    assert [r["cas"] for r in res] == [d.name for d in ds]
    assert len(journal.read_text(encoding="utf-8").splitlines()) == 4  # entête + 3 cas


def test_coeurs_invalide(pref, tmp_path):
    with pytest.raises(ValueError):
        lancer.lancer_serie([], coeurs=0)


@requiert_openfast
def test_reprise_reelle_openfast(pref, tmp_path):
    d = _cas_court(pref, "R1", tmax="10")
    (r1,) = lancer.lancer_serie([d], delai_max=2, afficher=None)  # tué en cours de calcul
    assert r1["statut"] == "interrompu" and not lancer.est_termine(d)
    (r2,) = lancer.lancer_serie([d], afficher=None)  # reprise
    assert r2["statut"] == "termine" and lancer.est_termine(d)
    mtime = (d / "main.outb").stat().st_mtime
    (r3,) = lancer.lancer_serie([d], afficher=None)
    assert r3["statut"] == "deja_termine" and (d / "main.outb").stat().st_mtime == mtime
