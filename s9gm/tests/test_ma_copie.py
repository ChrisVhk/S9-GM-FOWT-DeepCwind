"""LOT S2 — copies d'étudiant sans `sys.path` : `ma_copie` (chargement rechargé à chaque appel), `copie`, `tester`. Écrits AVANT le code."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from .conftest import RACINE

SOLUTIONS = os.environ.get("S9GM_SOLUTIONS_ENSEIGNANT")


@pytest.fixture
def copies(tmp_path, monkeypatch):
    """Les copies vont sous un dossier temporaire : on ne touche jamais `results/mon_s9gm/` de l'arbre de travail."""
    from s9gm import chemins, copies as c
    monkeypatch.setattr(chemins, "RESULTS", tmp_path / "results")
    monkeypatch.setattr(c, "DOSSIER_COPIES", tmp_path / "results" / "mon_s9gm")
    return c


def test_ma_copie_cree_la_copie_depuis_le_squelette_et_renvoie_un_module(copies):
    m = copies.ma_copie("fatigue")
    f = copies.DOSSIER_COPIES / "fatigue.py"
    assert f.is_file()
    assert f.read_text(encoding="utf-8") == (RACINE / "s9gm" / "fatigue.py").read_text(encoding="utf-8")
    assert hasattr(m, "rainflow") and m.__name__ != "s9gm.fatigue"          # nom distinct : pas d'ambiguïté avec le squelette du dépôt
    with pytest.raises(NotImplementedError):
        m.rainflow([0.0, 1.0, 0.0])


def test_ma_copie_n_ecrase_jamais_une_copie_existante(copies, capsys):
    copies.ma_copie("fatigue")
    f = copies.DOSSIER_COPIES / "fatigue.py"
    f.write_text(f.read_text(encoding="utf-8") + "\nMARQUE_ETUDIANT = 42\n", encoding="utf-8")
    avant = f.read_bytes()
    m = copies.ma_copie("fatigue")
    assert f.read_bytes() == avant
    assert m.MARQUE_ETUDIANT == 42
    assert "existe déjà" in capsys.readouterr().out


def test_ma_copie_recharge_le_fichier_sans_redemarrer_la_session(copies):
    m1 = copies.ma_copie("fatigue")
    f = copies.DOSSIER_COPIES / "fatigue.py"
    texte = f.read_text(encoding="utf-8")
    f.write_text(texte + "\n\ndef nouvelle_fonction():\n    return 'corrigée'\n", encoding="utf-8")
    m2 = copies.ma_copie("fatigue")
    assert not hasattr(m1, "nouvelle_fonction")
    assert m2.nouvelle_fonction() == "corrigée"


def test_nom_inconnu_refuse_avec_la_liste(copies):
    with pytest.raises(ValueError, match="fatigue.*ancrage.*structure"):
        copies.ma_copie("hydro")


def test_tester_sur_le_squelette_nomme_les_trous(copies):
    copies.ma_copie("fatigue")
    code, sortie = copies.tester("fatigue")
    assert code != 0
    assert "NotImplementedError" in sortie and "rainflow" in sortie


def test_tester_avec_l_option_squelette_compte_les_xfail(copies):
    code, sortie = copies.tester("fatigue", squelette=True)
    assert code == 0 and "xfailed" in sortie


@pytest.mark.skipif(not SOLUTIONS, reason="versions complètes de l'enseignant : S9GM_SOLUTIONS_ENSEIGNANT=<dossier>")
@pytest.mark.parametrize("nom", ["fatigue", "ancrage", "structure"])
def test_tester_sur_une_copie_complete_ne_donne_aucun_echec(copies, nom):
    copies.ma_copie(nom)
    for f in (f"{nom}.py", "efthymiou_c203.json") if nom == "structure" else (f"{nom}.py",):
        shutil.copy(Path(SOLUTIONS) / f, copies.DOSSIER_COPIES / f)
    code, sortie = copies.tester(nom)
    assert code == 0 and "failed" not in sortie and "xfailed" not in sortie, sortie[-1500:]


def test_la_commande_s9gm_copie_et_tester_existent(tmp_path):
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    r = subprocess.run([sys.executable, "-m", "s9gm", "--aide"], cwd=tmp_path, env=env, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-600:]
    for mot in ("copie", "tester", "doctor"):
        assert mot in r.stdout
