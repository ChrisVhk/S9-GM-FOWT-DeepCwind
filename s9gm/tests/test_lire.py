"""Falsificateurs de s9gm.lire : mêmes statistiques qu'openfast_toolbox sur F01 ; transitoire
jamais écarté par défaut."""
import numpy as np
import pytest
from openfast_toolbox.io import FASTOutputFile
from openfast_toolbox.io.fast_output_file import load_binary_output

from s9gm import cas, lancer, lire

from .conftest import MODELE, PRISE_EN_MAIN, requiert_openfast


@pytest.fixture(scope="module")
def sortie_F01():
    """F01 court (TMax = 20 s) fabriqué par cas, lancé par lancer."""
    import shutil
    import uuid
    nom = f"_pytest_{uuid.uuid4().hex[:8]}_F01"
    try:
        d = cas.generer_cas({"cas": nom, "fst.TMax": "20", "inflow.WindType": "1",
                             "inflow.HWindSpeed": "7.5", "inflow.PLExp": "0.11"}, MODELE, PRISE_EN_MAIN)
        (res,) = lancer.lancer_serie([d], afficher=None)
        assert res["statut"] == "termine"
        yield d / "main.outb"
    finally:
        shutil.rmtree(PRISE_EN_MAIN / nom, ignore_errors=True)


@requiert_openfast
@pytest.mark.parametrize("t0", [0.0, 5.0, 12.5])
def test_statistiques_egales_a_openfast_toolbox(sortie_F01, t0):
    df, _ = lire.lire(sortie_F01)
    canaux = ["RotSpeed", "TwrBsMyt", "GenPwr"]
    stats = lire.statistiques(df, canaux, t_transitoire=t0)
    # chemin indépendant : tableau brut de la lecture binaire d'openfast_toolbox + numpy
    data, info = load_binary_output(str(sortie_F01))
    noms = info["attribute_names"]
    t = data[:, noms.index("Time")]
    for c in canaux:
        y = data[t >= t0, noms.index(c)]
        ref = {"moyenne": y.mean(), "ecart_type": y.std(), "min": y.min(), "max": y.max()}
        for k, v in ref.items():
            assert stats.loc[c, k] == pytest.approx(v, rel=1e-12), (c, k)
    # et via la conversion pandas de l'outil
    pdf = FASTOutputFile(str(sortie_F01)).toDataFrame()
    m = pdf.iloc[:, 0] >= t0
    assert stats.loc["RotSpeed", "moyenne"] == pytest.approx(
        pdf.loc[m, "RotSpeed_[rpm]"].mean(), rel=1e-12)


@requiert_openfast
def test_ecarter_le_transitoire_change_la_moyenne(sortie_F01):
    df, _ = lire.lire(sortie_F01)
    a = lire.statistiques(df, ["RotSpeed"], t_transitoire=0.0).loc["RotSpeed", "moyenne"]
    b = lire.statistiques(df, ["RotSpeed"], t_transitoire=10.0).loc["RotSpeed", "moyenne"]
    assert a != b  # le rotor part de l'arrêt : le début tire la moyenne vers zéro


def test_transitoire_jamais_zero_par_defaut():
    import pandas as pd
    df = pd.DataFrame({"Time": [0.0, 1.0, 2.0], "Y": [1.0, 2.0, 3.0]})
    with pytest.raises(TypeError):  # argument obligatoire, pas de valeur par défaut
        lire.statistiques(df, ["Y"])
    with pytest.raises(ValueError, match="obligatoire"):
        lire.statistiques(df, ["Y"], t_transitoire=None)
    with pytest.raises(ValueError, match="dépasse"):
        lire.statistiques(df, ["Y"], t_transitoire=10.0)
    with pytest.raises(KeyError):
        lire.statistiques(df, ["Z"], t_transitoire=0.0)


def test_statistiques_main():
    import pandas as pd
    df = pd.DataFrame({"Time": [0.0, 1.0, 2.0, 3.0], "Y": [10.0, 2.0, 4.0, 6.0]})
    s = lire.statistiques(df, ["Y"], t_transitoire=1.0)
    assert s.loc["Y", "moyenne"] == pytest.approx(4.0)
    assert s.loc["Y", "ecart_type"] == pytest.approx(np.sqrt(8 / 3))
    assert (s.loc["Y", "min"], s.loc["Y", "max"], s.loc["Y", "n"]) == (2.0, 6.0, 3)
