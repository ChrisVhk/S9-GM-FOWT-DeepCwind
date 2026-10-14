"""Falsificateurs de la consigne de la phase 2 « Simulations de référence et sensibilité » (`seances/phase2/README.md`).

Écrits AVANT la consigne. Même principe que la phase 1 (`test_phase1_parcours.py`) :
1. Le CONTENU : les trois familles de paramètres de l'ENONCE sont chacune reliées à des colonnes de LCT ; aucune valeur de choix
   n'est écrite dans les commandes ; le cas de référence commun est D01 ; la
   direction de houle est dite limitée à 0° ; les périodes publiées sont dans data/periodes_lacher_reference.md ; l'écart 300 s / 600 s est une QUESTION.
2. Le REJEU : les blocs de code s'exécutent dans un clone neuf, après la phase 1, avec des valeurs d'essai neutres définies ICI.
   Chaque famille de sensibilité (bâbord : vent ; tribord : mer et courant ; centre : modèle et ancrage) est rejouée séparément.
"""
import json
import os
import re
from pathlib import Path

import pytest

from . import parcours
from .conftest import RACINE, requiert_openfast
from .test_phase1_parcours import ESSAI as ESSAI_PHASE1

REJEU_OPTIONNEL = pytest.mark.skipif(
    not (os.environ.get("S9GM_PARCOURS_REJEU") or os.environ.get("S9GM_PARCOURS_DEPOT")),
    reason="rejeu long (clone neuf, TurbSim, OpenFAST : plus d'une heure) : S9GM_PARCOURS_REJEU=1, ou S9GM_PARCOURS_DEPOT=<dépôt>")

PHASE2 = RACINE / "seances" / "phase2" / "README.md"

CHAUMARD = "../../../modeles/oc4_rtest/5MW_OC4Semi_WSt_WavesWN/NRELOffshrBsline5MW_OC4DeepCwindSemi_"
ESSAI = {
    "<votre valeur>": "60",
    "<votre durée de lâcher (s)>": "60",
    "<votre déplacement de surge (m)>": "5",
    "<votre déplacement de heave (m)>": "1",
    "<votre rotation de pitch (°)>": "3",
    "<indice du cas de base>": "5",
    "<votre durée de simulation (s)>": "90",     # plus longue que le transitoire d essai (60 s)
    "<vos coeurs>": "3",
    # famille bâbord (vent) : par défaut du rejeu complet
    "<vos variations>": '{"turbsim.URef": [9, 14]}',
}
FAMILLES = {
    "babord_vent": '{"turbsim.URef": [9, 14]}',
    "babord_graines": '{"turbsim.RandSeed1": [4242, 4243]}',
    "tribord_mer": '{"seastate.WaveHs": [3, 5], "seastate.WavePkShp": [2.0, 5.0]}',
    "tribord_courant": '{"seastate.CurrMod": [0, 1], "seastate.CurrDIV": [0, 0.3]}',
    "centre_ancrage": '{"fst.CompMooring": [3, 1], "fst.MooringFile": ["' + CHAUMARD + 'MoorDyn.dat", "' + CHAUMARD + 'MAP.dat"]}',
}


def _texte():
    assert PHASE2.is_file()
    return PHASE2.read_text(encoding="utf-8")


def _plat(t):
    return re.sub(r"\s+", " ", t.replace("**", ""))


def test_chaque_famille_de_l_enonce_a_ses_colonnes_de_lct():
    t = _texte()
    for famille in ("Bâbord", "Tribord", "Centre"):
        assert famille in t, famille
    for colonne in ("turbsim.URef", "turbsim.IECturbc", "turbsim.RandSeed1",
                    "seastate.WaveHs", "seastate.WaveTp", "seastate.WavePkShp", "seastate.CurrMod",
                    "fst.CompMooring", "fst.MooringFile", "fst.HydroFile"):
        assert f"`{colonne}`" in t, colonne


def test_les_limites_du_modele_sont_dites():
    t = _plat(_texte()).lower()
    assert "direction de houle" in t and "0°" in t                           # WaveDir : cap 0° seulement (WAMIT du second ordre)
    assert "hydrodyn" in t and ("copie" in t or "copiez" in t)               # théorie potentielle vs Morison : copie locale du fichier
    assert "data/periodes_lacher_reference.md" in t and "valeurs de référence" in t   # périodes publiées : données dans le dépôt, sourcées
    assert "désalignement" in t and "question de discussion" in t               # limite du modèle, pas un oubli


def test_le_cas_de_reference_commun_est_d01_et_sert_de_point_commun_a_la_synthese():
    """REF = D01 écrit dans la consigne ; la sensibilité part de la LCT du groupe ; D01 entre dans la comparaison."""
    t = _plat(_texte())
    assert 'REF = "D01"' in t
    assert "<cas de référence désigné par l'enseignant>" not in t and "désigné par l'enseignant" not in t
    assert "point commun" in t and "phase 6" in t
    code = "\n".join(c for _, c in parcours.blocs(_texte()))
    assert 'RESULTS / "D01"' in code             # D01 est dans la comparaison de l'étape 4


def test_les_commandes_300_s_et_600_s_et_la_question_d_analyse_sans_valeur():
    t = _plat(_texte())
    assert "300" in t and "600" in t
    assert re.search(r"dans le bruit", t) or re.search(r"significatif", t)
    code = "\n".join(c for _, c in parcours.blocs(_texte()))
    assert re.search(r'\["fst\.TMax"\]\s*=\s*\[300,\s*600\]', code)       # les deux durées, dans la même commande


def test_aucune_valeur_de_choix_n_est_ecrite_dans_les_commandes():
    for langue, code in parcours.blocs(_texte()):
        assert not re.search(r"RandSeed1[^\n]*\d{3,}", code), "graine écrite en dur"
        assert not re.search(r"iecturbc\s*[=:]\s*[\"']?(?:[ABC]|\d)", code, re.I), "catégorie IEC écrite en dur"
        assert not re.search(r"(URef|WaveHs|WaveTp|PkShp|CurrDIV)\"?\s*[:=]\s*\[?\s*\d", code), "valeur de sensibilité écrite en dur"


def test_r8_la_phase_2_n_a_plus_de_trou_annonce():
    import importlib.util
    spec = importlib.util.spec_from_file_location("vp", RACINE / "scripts" / "verifier_parcours.py")
    vp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vp)
    assert not vp.MARQUEUR_TROU.search(_texte())


def _depot(tmp_path_factory):
    depot = os.environ.get("S9GM_PARCOURS_DEPOT")
    if depot:
        return Path(depot)
    depot = parcours.cloner(RACINE, tmp_path_factory.mktemp("clone2") / "clone")
    code, sortie, _ = parcours.rejouer(RACINE / "seances" / "phase1" / "README.md", depot, ESSAI_PHASE1)
    assert code == 0, "la phase 1 doit passer avant la phase 2 :\n" + sortie[-2000:]
    return depot


@pytest.fixture(scope="module")
def depot(tmp_path_factory):
    return _depot(tmp_path_factory)


@pytest.mark.slow
@REJEU_OPTIONNEL
@requiert_openfast
def test_rejeu_complet_phase_2_apres_la_phase_1(depot):
    code, sortie, temps = parcours.rejouer(PHASE2, depot, ESSAI, delai=7200)
    assert code == 0, sortie[-4000:]
    res = depot / "results"
    assert (res / "phase2_lachers").is_dir() and len(list((res / "phase2_lachers").glob("*/main.outb"))) == 3
    assert len(list((res / "phase2").glob("*/main.outb"))) >= 2
    assert (res / "phase2_300_600").is_dir()
    (res / "parcours_phase2_temps.json").write_text(json.dumps(temps), encoding="utf-8")
    print("TEMPS_PHASE2", json.dumps(temps))


@pytest.mark.slow
@REJEU_OPTIONNEL
@requiert_openfast
@pytest.mark.parametrize("famille", [f for f in FAMILLES if f != "babord_vent"])
def test_chaque_famille_de_sensibilite_tourne(depot, famille):
    """Rejoue seulement l'étape de sensibilité, avec la variation propre à la famille (durée d'essai courte)."""
    essai = {**ESSAI, "<vos variations>": FAMILLES[famille]}
    n = _numero_bloc_sensibilite()
    code, sortie, _ = parcours.rejouer(PHASE2, depot, essai, delai=3600, etapes=[n])
    assert code == 0, f"{famille} :\n" + sortie[-3000:]
    assert len(list((depot / "results" / "phase2").glob("*/main.outb"))) == 2


def _numero_bloc_sensibilite():
    for i, (_, code) in enumerate(parcours.blocs(_texte()), start=1):
        if "<vos variations>" in code:
            return i
    raise AssertionError("aucun bloc de sensibilité (<vos variations>) dans la consigne")


@pytest.mark.slow
@REJEU_OPTIONNEL
@requiert_openfast
def test_les_300_premieres_secondes_du_calcul_de_600_s_sont_celles_du_calcul_de_300_s(depot):
    """Affirmation de la consigne (étape 5) : même graine, même champ de vent, même houle -> mêmes 300 premières secondes. Lit les sorties
    du rejeu complet (à lancer après `test_rejeu_complet_phase_2_apres_la_phase_1`, dans le même dépôt)."""
    import numpy as np
    from s9gm import lire
    a, _ = lire.lire(depot / "results" / "phase2_300_600" / "T300" / "main.outb")
    b, _ = lire.lire(depot / "results" / "phase2_300_600" / "T600" / "main.outb")
    n = len(a)
    for canal in ("TwrBsMyt", "FAIRTEN1", "PtfmSurge", "PtfmHeave", "PtfmPitch"):
        ecart = float(np.abs(a[canal].to_numpy() - b[canal].to_numpy()[:n]).max())
        assert ecart < 1e-2 * max(1.0, float(np.ptp(a[canal].to_numpy()))), (canal, ecart)
