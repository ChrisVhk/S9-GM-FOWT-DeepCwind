"""Falsificateurs de la consigne de la phase 1 « Du site à la Load Case Table » (`seances/phase1/README.md`).

Écrits AVANT la consigne. Deux familles :
1. Le CONTENU : les promesses de l'ENONCE sont tenues (données non fournies dites « non fournies »), le trou `IECturbc` est
   à justifier avec sa source et non imposé, aucune valeur de choix (catégorie, graine, seuils) n'est écrite dans les commandes.
2. Le REJEU : les blocs de code de la section 3 s'exécutent, dans l'ordre, dans un clone NEUF du dépôt, comme le ferait un
   étudiant. Les choix de l'étudiant (seuils, loi de vent, graine, catégorie) sont remplacés par des valeurs d'essai neutres
   définies ICI, jamais dans la consigne. Test lent (TurbSim, OpenFAST).
"""
import json
import os
import re
from pathlib import Path

import pytest

from . import parcours
from .conftest import RACINE, requiert_openfast

PHASE1 = RACINE / "seances" / "phase1" / "README.md"

# Valeurs d'essai neutres, propres au TEST (pas à la consigne) : une marque par choix de l'étudiant.
ESSAI = {
    "<votre k (diviseur de 18)>": "1",
    "<votre exposant m>": "3",
    "<votre méthode de lumping>": "dommage",
    "<votre z0>": "0.001",
    "<votre seuil de probabilité>": "0.005",
    "<votre loi>": "puissance",
    "<votre exposant de vent>": "0.14",
    "<votre graine>": "4242",
    "<votre catégorie ou intensité>": "12",
    "<votre période de retour>": "50 yrs",
    "<vos classes de vent>": "[11, 25]",
    "<indice du cas à lancer>": "5",
    "<votre valeur>": "60",
}


def _texte():
    assert PHASE1.is_file()
    return PHASE1.read_text(encoding="utf-8")


def _plat(texte):
    """Texte sans gras ni retours à la ligne : pour chercher une phrase coupée par la mise en page."""
    return re.sub(r"\s+", " ", texte.replace("**", ""))


def test_les_donnees_de_courant_et_de_niveaux_d_eau_sont_dites_non_fournies():
    """E-164 (b) : la consigne dit « à consulter, non fourni » pour le courant et les niveaux d'eau (LIFES50+ D1.1)."""
    t = _texte()
    i = t.index("LIFES50+")
    voisinage = t[max(0, i - 400): i + 600].lower()
    assert "non fourni" in voisinage or "ne sont pas fournies" in voisinage or "pas redistribu" in voisinage
    assert "fournies par" not in voisinage.replace("non fournies", "")


def test_iecturbc_est_un_trou_a_justifier_avec_sa_source_pas_une_valeur_imposee():
    """Avenant 13 h 23 : la consigne demande de JUSTIFIER (Iref, classe de conception de la machine, source citée), pas de donner."""
    t = _texte()
    assert "IECturbc" in t
    i = t.index("IECturbc")
    bloc = t[i - 800: i + 1800].lower()
    for mot in ("justif", "iref", "classe de conception", "source"):
        assert mot in bloc, f"« {mot} » absent de la demande de justification de IECturbc"
    assert not re.search(r"(?<!pas )impos[ée]", bloc), "IECturbc présenté comme imposé"   # « pas imposés » est permis
    assert "la lettre" in bloc or "pas la lettre" in bloc or "lettre seule" in bloc    # le barème : la justification, pas la lettre


def test_aucune_valeur_de_choix_n_est_ecrite_dans_les_commandes():
    """Ni catégorie IEC, ni graine, ni seuil, ni exposant, ni indice de cas en dur dans les blocs de code."""
    for langue, code in parcours.blocs(_texte()):
        assert not re.search(r"graine0?\s*=\s*\d", code), "graine écrite en dur"
        assert not re.search(r"RandSeed1[^\n]*\d{3,}", code), "graine écrite en dur"
        assert not re.search(r"iecturbc\s*=\s*[\"']?(?:[ABC]|\d)", code, re.I), "catégorie IEC écrite en dur"
        assert not re.search(r"seuil\w*\s*=\s*0?\.\d", code), "seuil écrit en dur"
        assert not re.search(r"exposant\s*=\s*0?\.\d", code), "exposant écrit en dur"


def test_la_lct_est_validee_avant_la_campagne_et_les_extremes_ne_sont_pas_lances():
    t = _plat(_texte()).lower()
    assert "validée par l'enseignant" in t or "validee par l'enseignant" in t
    assert "somme des occurrences" in t and "100 %" in t


def test_les_commandes_n_utilisent_que_les_modules_prevus():
    """Chaîne attendue : s9gm.metocean, s9gm.cas, s9gm.lancer, s9gm.lire (+ pandas pour les feuilles Excel des extrêmes)."""
    code = "\n".join(c for _, c in parcours.blocs(_texte()))
    for module in re.findall(r"from s9gm import ([^\n]+)", code):
        for nom in [m.strip() for m in module.split(",")]:
            assert nom in {"metocean", "cas", "lancer", "lire", "visu"}, nom
    assert "metocean.lire()" in code and "cas.generer_serie" in code and "lancer.lancer_serie" in code and "lire.statistiques" in code
    assert "pandas" in code or "pd." in code


def test_r8_la_phase_1_n_a_plus_de_trou_annonce():
    import importlib.util
    spec = importlib.util.spec_from_file_location("vp", RACINE / "scripts" / "verifier_parcours.py")
    vp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vp)
    texte = _texte()
    assert not vp.MARQUEUR_TROU.search(texte), vp.MARQUEUR_TROU.search(texte)


@pytest.mark.slow
@requiert_openfast
def test_rejeu_depuis_un_clone_neuf(tmp_path):
    depot = os.environ.get("S9GM_PARCOURS_DEPOT")
    depot = Path(depot) if depot else parcours.cloner(RACINE, tmp_path / "clone")
    code, sortie, temps = parcours.rejouer(PHASE1, depot, ESSAI)
    assert code == 0, sortie[-3000:]
    # artefacts attendus d'un étudiant qui a suivi la consigne
    assert (depot / "results" / "lct_phase1.csv").is_file()
    assert (depot / "results" / "etats_phase1.csv").is_file()
    sorties = list((depot / "results" / "phase1").glob("*/main.outb"))
    assert len(sorties) == 1, sorties
    # la somme des occurrences est 100 % (point de contrôle de l'ENONCE)
    import pandas as pd
    etats = pd.read_csv(depot / "results" / "etats_phase1.csv")
    assert abs(etats["O_pct"].sum() - 100.0) < 1e-6
    assert 10 <= len(etats) <= 15          # 10 à 15 cas de fatigue (ENONCE, phase 1) ; les cas extrêmes sont dans un autre fichier
    (depot / "results" / "parcours_phase1_temps.json").write_text(json.dumps(temps), encoding="utf-8")
    print("TEMPS_PHASE1", json.dumps(temps))
