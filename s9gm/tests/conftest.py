"""Fixtures communes. Les cas de test sont fabriqués dans `cas/` (même profondeur que F01, F02 : le chemin
relatif `../../modeles/fixe` est celui du tutoriel), dans un dossier `_pytest_*` ignoré par git et supprimé
après le test."""
import shutil
import uuid
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[2]
CAS = RACINE / "cas"
MODELES = RACINE / "modeles"
MODELE = MODELES / "fixe"
DISCON = RACINE / "modeles" / "oc4_rtest" / "5MW_Baseline" / "ServoData" / "DISCON.so"

LCT_F01 = ("cas,fst.TMax,inflow.WindType,inflow.HWindSpeed,inflow.PLExp\n"
           "F01,200,1,7.5,0.11\n")


@pytest.fixture
def pref():
    """Préfixe unique des cas de test. Les cas sont fabriqués dans `cas/`, puis supprimés."""
    p = f"_pytest_{uuid.uuid4().hex[:8]}"
    yield p
    for d in [*CAS.glob(p + "*"), *MODELES.glob(p + "*")]:   # cas fabriqués, et copies de modèle des tests
        shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def lct_f01(tmp_path, pref):
    p = tmp_path / "lct.csv"
    p.write_text(LCT_F01.replace("F01,", f"{pref}_F01,"), encoding="utf-8")
    return p


def openfast_disponible():
    return shutil.which("openfast") is not None and DISCON.is_file()


requiert_openfast = pytest.mark.skipif(
    not openfast_disponible(),
    reason="openfast absent du PATH ou DISCON.so non compilé (bash scripts/build_discon.sh)")


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: calcul OpenFAST ou rendu pvbatch réel (minutes)")
