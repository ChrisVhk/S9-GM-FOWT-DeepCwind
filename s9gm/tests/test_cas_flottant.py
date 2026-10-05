"""Falsificateurs de s9gm.cas sur le modèle FLOTTANT du dépôt (`tutorials/lheea/05_FOWT/1_Configuration`) : un cas
généré (état de mer `seastate.*`, vent TurbSim `turbsim.*`, durée `fst.*`) doit être **identique octet pour octet** aux
fichiers faits à la main (`tests/data/`, éditions `sed` du modèle avec des valeurs distinctes des siennes)."""
import shutil
import uuid
from pathlib import Path

import pytest

from s9gm import cas

RACINE = Path(__file__).resolve().parents[2]
FLOTTANT = RACINE / "tutorials" / "lheea" / "05_FOWT" / "1_Configuration"
DONNEES = Path(__file__).parent / "data"
PARENT = FLOTTANT.parent       # les cas sont les sœurs du modèle : `../1_Configuration` reste valable


@pytest.fixture
def nom_cas():
    n = f"_pytest_{uuid.uuid4().hex[:8]}"
    yield n
    for d in PARENT.glob(n + "*"):
        shutil.rmtree(d, ignore_errors=True)


def _lct(tmp_path, nom):
    p = tmp_path / "lct.csv"
    p.write_text("cas,fst.TMax,seastate.WaveHs,seastate.WaveTp,seastate.WaveSeed(1),seastate.WaveTMax,"
                 "turbsim.URef,turbsim.RandSeed1,turbsim.AnalysisTime,turbsim.UsableTime\n"
                 f"{nom},120,6.5,9.5,987654321,120,15,777,90,60\n", encoding="utf-8")
    return p


def test_seastate_turbsim_fst_inflow_identiques_aux_fichiers_faits_a_la_main(tmp_path, nom_cas):
    (d,) = cas.generer_serie(_lct(tmp_path, nom_cas), FLOTTANT, PARENT, executer_turbsim=False)
    attendus = {"SeaState.dat": "SeaState_fait_main.dat", "main.fst": "main_flottant_fait_main.fst",
                f"Wind/{nom_cas}.inp": "turbsim_fait_main.inp"}
    for genere, ref in attendus.items():
        assert (d / genere).read_bytes() == (DONNEES / ref).read_bytes(), f"{genere} diffère de {ref}"
    inflow = (DONNEES / "config_inflow_flottant_fait_main.dat").read_text(encoding="utf-8").replace("CASX", nom_cas)
    assert (d / "config_inflow.dat").read_text(encoding="utf-8") == inflow


def test_seastate_est_local_au_cas_et_modele_inchange(tmp_path, nom_cas):
    avant = (FLOTTANT / "SeaState.dat").read_bytes()
    (d,) = cas.generer_serie(_lct(tmp_path, nom_cas), FLOTTANT, PARENT, executer_turbsim=False)
    assert (d / "SeaState.dat").is_file() and (FLOTTANT / "SeaState.dat").read_bytes() == avant
    j = (d / "journal_cas.json").read_text(encoding="utf-8")
    assert "SeaStFile (local)" in j and "WaveSeed(1)" in j


def test_seastate_cle_inconnue_echoue(tmp_path, nom_cas):
    p = tmp_path / "lct.csv"
    p.write_text(f"cas,seastate.PasUneCle\n{nom_cas},1\n", encoding="utf-8")
    with pytest.raises(KeyError, match="PasUneCle"):
        cas.generer_serie(p, FLOTTANT, PARENT, executer_turbsim=False)
