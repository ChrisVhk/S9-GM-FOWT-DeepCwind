"""LOT E — en phase 6, un effet se mesure contre la ligne de référence de SA famille (même vent, même graine, même houle ; un seul paramètre change).
`D01` reste le point commun des trois groupes, mais ne sert que de contrôle de cohérence du modèle. Écrits AVANT les corrections de la consigne.

On exécute le vrai code de l'étape 2 de `seances/phase6/README.md`, sur des fichiers de synthèse SYNTHÉTIQUES où `D01` et la référence de famille diffèrent."""
import io
import contextlib
import re
from pathlib import Path

import pandas as pd
import pytest

from . import parcours
from .conftest import RACINE

PHASE6 = RACINE / "seances" / "phase6" / "README.md"
COLONNES = ["dommage_tour_par_heure", "DEL_tour_MPa", "DEL_ligne_max_N", "max_TwrBsMyt_kNm", "max_tension_N", "max_PtfmSurge", "max_PtfmHeave", "max_PtfmPitch"]
GROUPES = {"babord": "vent", "tribord": "mer", "centre": "ancrage"}


def _ligne(groupe, famille, type_, cas, facteur, variation=""):
    return {"groupe": groupe, "famille": famille, "type": type_, "cas": cas, "variation": variation, **{c: facteur * (i + 1) for i, c in enumerate(COLONNES)}}


def _fichiers(dossier, sans_reference=None, d01_ecart=None):
    dossier.mkdir(parents=True, exist_ok=True)
    for g, fam in GROUPES.items():
        lignes = [_ligne(g, fam, "point commun", "D01", 10.0 * (1 + (d01_ecart if (d01_ecart and g == "centre") else 0.0))),
                  _ligne(g, fam, "sensibilité", "S00", 6.0, "x = 1"), _ligne(g, fam, "sensibilité", "S01", 9.0, "x = 2")]
        if g != sans_reference:
            lignes.insert(1, _ligne(g, fam, "référence de famille", "SREF", 3.0))
        pd.DataFrame(lignes).to_csv(dossier / f"{g}.csv", index=False)


def _code_etape_2():
    blocs = parcours.blocs(PHASE6.read_text(encoding="utf-8"))
    code = [c for _, c in blocs if "tableau_synthese" in c][0]
    return parcours.substituer(code, {"<votre tolérance relative sur D01>": "0.01"})


def _executer(tmp_path, monkeypatch, **kw):
    from s9gm import chemins
    monkeypatch.setattr(chemins, "RENDUS", tmp_path / "rendus")
    _fichiers(tmp_path / "rendus" / "groupes", **kw)
    sortie = io.StringIO()
    with contextlib.redirect_stdout(sortie):
        exec(compile(_code_etape_2(), "etape2", "exec"), {})
    return sortie.getvalue(), pd.read_csv(tmp_path / "rendus" / "tableau_synthese.csv")


def test_a_chaque_effet_est_rapporte_a_la_reference_de_sa_famille_pas_a_d01(tmp_path, monkeypatch):
    _, tab = _executer(tmp_path, monkeypatch)
    assert len(tab) == 6 and set(tab["groupe"]) == set(GROUPES)
    s00 = tab[(tab["groupe"] == "babord") & (tab["cas"] == "S00")].iloc[0]
    assert s00["dommage_tour_relatif"] == pytest.approx(6.0 / 3.0)                 # S00 / SREF = 2 ; rapporté à D01 il aurait valu 0,6
    assert s00["max_tension_relatif"] == pytest.approx(6.0 * 5 / (3.0 * 5))
    assert not (tab["dommage_tour_relatif"] == pytest.approx(0.6)).any()
    s01 = tab[(tab["groupe"] == "centre") & (tab["cas"] == "S01")].iloc[0]
    assert s01["max_PtfmPitch_relatif"] == pytest.approx(3.0)


def test_b_une_famille_sans_reference_donne_une_erreur_qui_nomme_le_groupe_et_la_famille(tmp_path, monkeypatch):
    with pytest.raises(ValueError, match=r"groupe tribord.*famille mer|famille mer.*groupe tribord"):
        _executer(tmp_path, monkeypatch, sans_reference="tribord")


def test_c_le_controle_du_point_commun_sur_d01_est_conserve(tmp_path, monkeypatch):
    sortie, _ = _executer(tmp_path, monkeypatch)
    assert "point commun cohérent à la tolérance retenue ? True" in sortie
    sortie2, _ = _executer(tmp_path / "bis", monkeypatch, d01_ecart=0.05)
    assert "point commun cohérent à la tolérance retenue ? False" in sortie2


def test_le_texte_dit_pourquoi_on_ne_rapporte_pas_a_d01_sans_aucune_valeur():
    t = re.sub(r"\s+", " ", PHASE6.read_text(encoding="utf-8").replace("**", ""))
    assert "référence de famille" in t and "SREF" in t
    assert "contrôle de cohérence" in t
    assert re.search(r"deux causes|passage du stationnaire au turbulent", t)
    assert "rapportés au `D01` de leur groupe" not in t and "relatifs au `D01` de son groupe" not in t
    assert "IndexError` sur `ref`" not in t and "aucune ligne « référence de famille »" in t


def test_phase_2_ajoute_la_ligne_de_reference_de_famille():
    t = (RACINE / "seances" / "phase2" / "README.md").read_text(encoding="utf-8")
    assert 'cas="SREF"' in t
    code = "\n".join(c for l, c in parcours.blocs(t) if l == "python" and "variations" in c)
    assert "SREF" in code
