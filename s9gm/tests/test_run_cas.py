"""Falsificateurs de `cas/run_cas.sh` : un cas de référence se lance SUR UNE COPIE sous `results/` ; `cas/` (suivi par git)
n'est jamais modifié ; un cas inconnu ou un dossier sans main.fst fait échouer le script (code ≠ 0)."""
import hashlib
import shutil
import subprocess
import uuid

import pytest

from .conftest import CAS, RACINE, requiert_openfast

SCRIPT = CAS / "run_cas.sh"


def _lancer(*args):
    return subprocess.run(["bash", str(SCRIPT), *args], cwd=RACINE, capture_output=True, text=True)


def _empreinte(dossier):
    return {str(p.relative_to(dossier)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(dossier.rglob("*")) if p.is_file()}


@requiert_openfast
def test_cas_inconnu_fait_echouer_le_script():
    r = _lancer("Z99")
    assert r.returncode != 0 and "inconnu" in r.stderr


@requiert_openfast
def test_dossier_sans_main_fst_fait_echouer_le_script(tmp_path):
    r = _lancer(str(tmp_path))
    assert r.returncode != 0 and "main.fst" in r.stderr


@requiert_openfast
def test_dossier_a_soi_sous_results_est_lance_sur_place():
    nom = f"_pytest_{uuid.uuid4().hex[:8]}"
    dest = RACINE / "results" / nom
    try:
        shutil.copytree(CAS / "F01", dest, ignore=shutil.ignore_patterns("*.outb", "*.log", "*.sum*"))
        main = dest / "main.fst"
        main.write_text(main.read_text(encoding="utf-8").replace("\t\t200   TMax", "\t\t  3   TMax"), encoding="utf-8")
        r = _lancer(f"results/{nom}")
        assert r.returncode == 0, r.stdout + r.stderr
        assert (dest / "main.outb").is_file()
    finally:
        shutil.rmtree(dest, ignore_errors=True)


@pytest.mark.slow
@requiert_openfast
def test_cas_de_reference_lance_sur_une_copie_et_cas_reste_intact():
    avant = _empreinte(CAS / "F01")
    r = _lancer("F01")
    assert r.returncode == 0, r.stdout + r.stderr
    assert (RACINE / "results" / "F01" / "main.outb").is_file()
    assert _empreinte(CAS / "F01") == avant          # aucun fichier créé ni modifié sous cas/F01


@requiert_openfast
def test_un_dossier_de_reference_n_est_jamais_lance_sur_place():
    r = _lancer("cas/F01")
    assert r.returncode != 0 and "Refus" in r.stderr
