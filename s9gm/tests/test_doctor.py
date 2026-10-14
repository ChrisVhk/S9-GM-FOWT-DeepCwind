"""LOT S3 — `s9gm doctor`. Écrits AVANT le code. Chaque point rend OK ou À CORRIGER avec la commande exacte."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from .conftest import RACINE


def _par_id(resultats):
    return {r.id: r for r in resultats}


def test_environnement_non_actif_donne_la_commande_d_activation():
    from s9gm import doctor
    res = _par_id(doctor.verifier(env={}, prefixe_python="/usr", executable="/usr/bin/python3"))
    r = res["environnement"]
    assert not r.ok and "micromamba activate s9gm-fowt" in r.commande


def test_s9gm_importe_d_un_autre_clone_est_detecte():
    from s9gm import doctor
    res = _par_id(doctor.verifier(fichier_s9gm="/home/autre/S9-GM-FOWT-DeepCwind/s9gm/__init__.py"))
    r = res["clone"]
    assert not r.ok and "deux clones" in r.message and "pip install -e" in r.commande


def test_clone_sous_mnt_c_est_signale():
    from s9gm import doctor
    res = _par_id(doctor.verifier(racine=Path("/mnt/c/Users/x/S9-GM-FOWT-DeepCwind"), fichier_s9gm="/mnt/c/Users/x/S9-GM-FOWT-DeepCwind/s9gm/__init__.py"))
    assert not res["emplacement"].ok and "/mnt/c" in res["emplacement"].message


def test_les_points_facultatifs_ne_font_pas_echouer(monkeypatch):
    from s9gm import doctor
    res = doctor.verifier()
    facultatifs = [r for r in res if not r.obligatoire]
    assert {r.id for r in facultatifs} >= {"pvbatch", "ffmpeg"}
    assert doctor.code_de_sortie([r for r in res if not r.obligatoire and not r.ok] + [r for r in res if r.obligatoire and r.ok]) == 0


def test_une_copie_a_trous_est_une_information_pas_une_erreur(tmp_path, monkeypatch):
    from s9gm import chemins, copies, doctor
    monkeypatch.setattr(chemins, "RESULTS", tmp_path / "results")
    monkeypatch.setattr(copies, "DOSSIER_COPIES", tmp_path / "results" / "mon_s9gm")
    copies.ma_copie("fatigue")
    r = _par_id(doctor.verifier())["copies"]
    assert r.ok and "fatigue" in r.message and "NotImplementedError" in r.message or "trou" in r.message


@pytest.mark.skipif(not shutil.which("openfast") or not (RACINE / "modeles/oc4_rtest/5MW_Baseline/ServoData/DISCON.so").is_file(),
                    reason="machine sans OpenFAST ni contrôleur compilé")
def test_tout_est_ok_sur_la_machine_de_developpement(tmp_path):
    env = dict(os.environ)
    r = subprocess.run([sys.executable, "-m", "s9gm", "doctor"], cwd=tmp_path, env=env, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout[-1500:]
    assert "À CORRIGER" not in r.stdout and "OK" in r.stdout


def test_la_sortie_est_en_francais_sans_couleur(tmp_path):
    r = subprocess.run([sys.executable, "-m", "s9gm", "doctor"], cwd=tmp_path, capture_output=True, text=True)
    assert "\x1b[" not in r.stdout
    assert "OK" in r.stdout or "À CORRIGER" in r.stdout
