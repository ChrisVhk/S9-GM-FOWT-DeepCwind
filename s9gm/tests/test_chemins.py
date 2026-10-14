"""LOT S1 — le code de `s9gm` ne dépend pas du dossier courant. Écrits AVANT le code.

(a) depuis un dossier hors du dépôt, `import s9gm` et `metocean.lire()` réussissent (le paquet est installé) ;
(b) aucune fonction de `s9gm` n'utilise le dossier courant ni un chemin littéral du dépôt : tout passe par `s9gm.chemins` ;
(c) un chemin relatif donné par l'étudiant se lit à partir de la racine du dépôt, pas du dossier courant ; un chemin absolu ne change pas ;
(d) `results/` et `rendus/` se créent à la demande ;
(e) `env/install.sh` installe le paquet, reste idempotent, et ne contredit plus `INSTALLATION.md` sur `build_discon.sh`."""
import ast
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from .conftest import RACINE

S9GM = RACINE / "s9gm"


def _hors_du_depot(tmp_path, code):
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH",)}
    return subprocess.run([sys.executable, "-c", code], cwd=tmp_path, env=env, capture_output=True, text=True)


def test_a_import_et_lecture_de_la_table_depuis_un_dossier_hors_du_depot(tmp_path):
    r = _hors_du_depot(tmp_path, "import s9gm, s9gm.metocean as m; t = m.lire(); print(type(t).__name__)")
    assert r.returncode == 0, "s9gm n'est pas installé : `pip install -e .` depuis la racine du dépôt\n" + r.stderr[-800:]


def test_a_le_module_importe_est_celui_de_ce_clone(tmp_path):
    r = _hors_du_depot(tmp_path, "import s9gm.chemins as c; print(c.RACINE)")
    assert r.returncode == 0, r.stderr[-800:]
    assert Path(r.stdout.strip()).resolve() == RACINE.resolve()


def _constantes_hors_docstrings(arbre):
    docs = set()
    for noeud in ast.walk(arbre):
        if isinstance(noeud, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            corps = noeud.body
            if corps and isinstance(corps[0], ast.Expr) and isinstance(corps[0].value, ast.Constant) and isinstance(corps[0].value.value, str):
                docs.add(id(corps[0].value))
    return [n for n in ast.walk(arbre) if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in docs]


def test_b_aucun_dossier_courant_ni_chemin_litteral_du_depot_hors_de_chemins():
    motif = re.compile(r"^(results|rendus|data|cas|modeles|seances)/\S*$")
    fautes = []
    for f in sorted(S9GM.glob("*.py")):
        if f.name == "chemins.py":
            continue
        arbre = ast.parse(f.read_text(encoding="utf-8"))
        for n in ast.walk(arbre):
            if isinstance(n, ast.Attribute) and n.attr in ("getcwd", "cwd") and isinstance(n.value, (ast.Name, ast.Attribute)):
                fautes.append(f"{f.name}:{n.lineno} dossier courant ({n.attr})")
        for c in _constantes_hors_docstrings(arbre):
            if motif.match(c.value):
                fautes.append(f"{f.name}:{c.lineno} chemin littéral « {c.value} »")
    assert not fautes, fautes


def test_c_un_chemin_relatif_se_lit_depuis_la_racine_pas_depuis_le_dossier_courant(tmp_path, monkeypatch):
    from s9gm import cas, chemins, lire
    racine = tmp_path / "racine"
    (racine / "results").mkdir(parents=True)
    monkeypatch.setattr(chemins, "RACINE", racine)
    ailleurs = tmp_path / "ailleurs"
    ailleurs.mkdir()
    monkeypatch.chdir(ailleurs)                                    # on travaille depuis un autre dossier
    assert chemins.resoudre("results/x.csv") == racine / "results" / "x.csv"
    absolu = tmp_path / "a.csv"
    assert chemins.resoudre(absolu) == absolu
    (racine / "results" / "lct.csv").write_text("cas,fst.TMax\nA,10\n", encoding="utf-8")
    assert cas.lire_lct("results/lct.csv")[0]["cas"] == "A"
    vus = []

    class Faux:
        def __init__(self, chemin):
            vus.append(Path(chemin))

        def toDataFrame(self):
            import pandas as pd
            return pd.DataFrame({"Time_[s]": [0.0, 1.0]})

    monkeypatch.setattr(lire, "FASTOutputFile", Faux)
    lire.lire("results/phase1/EX00/main.outb")
    assert vus == [racine / "results" / "phase1" / "EX00" / "main.outb"]


def test_constantes_du_depot():
    from s9gm import chemins
    assert chemins.RACINE == S9GM.parent
    for nom, sous in (("RESULTS", "results"), ("RENDUS", "rendus"), ("DATA", "data"), ("CAS", "cas"), ("MODELES", "modeles"), ("SEANCES", "seances")):
        assert getattr(chemins, nom) == chemins.RACINE / sous, nom


def test_d_results_et_rendus_se_creent_a_la_demande(tmp_path, monkeypatch):
    from s9gm import chemins
    monkeypatch.setattr(chemins, "RESULTS", tmp_path / "results")
    monkeypatch.setattr(chemins, "RENDUS", tmp_path / "rendus")
    assert not (tmp_path / "results").exists()
    assert chemins.dossier_results("phase9", "x") == tmp_path / "results" / "phase9" / "x"
    assert (tmp_path / "results" / "phase9" / "x").is_dir()
    assert chemins.dossier_rendus() == tmp_path / "rendus" and (tmp_path / "rendus").is_dir()


def test_le_journal_de_lancer_se_cree_sous_results_meme_si_le_dossier_manque(tmp_path, monkeypatch):
    from s9gm import chemins, lancer
    monkeypatch.setattr(chemins, "RACINE", tmp_path)
    monkeypatch.setattr(chemins, "RESULTS", tmp_path / "results")
    lancer.lancer_serie([], coeurs=1, journal="results/sous/journal.csv")
    assert (tmp_path / "results" / "sous").is_dir()


def test_e_install_sh_installe_le_paquet_idempotent_et_ne_contredit_pas_installation_md():
    t = (RACINE / "env" / "install.sh").read_text(encoding="utf-8")
    assert re.search(r"pip install -e", t), "install.sh n'installe pas le paquet"
    assert "set -euo pipefail" in t
    assert "s9gm doctor" in t
    assert "chaque fois" not in t.lower().split("build_discon")[0].split("puis,")[-1]
    assert "une fois par clone" in t.lower()
    assert "une fois par clone" in (RACINE / "INSTALLATION.md").read_text(encoding="utf-8").lower()


def test_pyproject_declare_le_paquet_et_la_commande():
    t = (RACINE / "pyproject.toml").read_text(encoding="utf-8")
    assert re.search(r'^name\s*=\s*"s9gm"', t, re.M)
    assert 's9gm = "s9gm.__main__:main"' in t
    assert not re.search(r"^dependencies\s*=\s*\[\s*\"", t, re.M), "pas de dépendances déclarées : l'environnement les fournit"
