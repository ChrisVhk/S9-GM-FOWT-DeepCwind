"""Fixtures communes. Les cas de test sont fabriqués à côté de `modele_fixe/` (même profondeur que
F01, F02 : le chemin relatif `../modele_fixe` est celui du tutoriel) dans un dossier `_pytest_*`
ignoré par git et supprimé après le test."""
import shutil
import uuid
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[2]
PRISE_EN_MAIN = RACINE / "tutorials" / "prise_en_main"
MODELE = PRISE_EN_MAIN / "modele_fixe"
DISCON = RACINE / "models" / "oc4_rtest" / "5MW_Baseline" / "ServoData" / "DISCON.so"

LCT_F01 = ("cas,fst.TMax,inflow.WindType,inflow.HWindSpeed,inflow.PLExp\n"
           "F01,200,1,7.5,0.11\n")


@pytest.fixture
def pref():
    """Préfixe unique des cas de test. Les cas sont fabriqués dans `prise_en_main/` (frères de
    `modele_fixe/`), puis supprimés."""
    p = f"_pytest_{uuid.uuid4().hex[:8]}"
    yield p
    for d in PRISE_EN_MAIN.glob(p + "*"):
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
