"""LOT S2-S4, contenu des consignes : plus de `sys.path`, plus de chemins relatifs dans le code, `s9gm doctor` en premier geste,
tutoriel du terminal. Écrits AVANT les réécritures."""
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from . import parcours
from .conftest import RACINE

SEANCES = sorted((RACINE / "seances").glob("*/README.md"))
PHASES = [RACINE / "seances" / n / "README.md" for n in ("0a", "0b", "phase1", "phase2", "phase3", "phase4", "phase5", "phase6")]
LITTERAL = re.compile(r"""["'](?:results|rendus|data|modeles|seances|cas|annexes)/""")


def test_aucun_sys_path_dans_seances_ni_fiches():
    fautes = []
    for dossier in ("seances", "fiches"):
        for f in (RACINE / dossier).rglob("*"):
            if f.suffix in (".md", ".ipynb", ".py") and f.is_file() and "sys.path" in f.read_text(encoding="utf-8", errors="ignore"):
                fautes.append(str(f.relative_to(RACINE)))
    assert not fautes, fautes


@pytest.mark.parametrize("readme", PHASES, ids=lambda p: p.parent.name)
def test_le_code_python_des_consignes_n_utilise_aucun_chemin_relatif_du_depot(readme):
    for langue, code in parcours.blocs(readme.read_text(encoding="utf-8")):
        if langue != "python":
            continue
        for n, ligne in enumerate(code.split("\n"), start=1):
            assert not LITTERAL.search(ligne), f"{readme.parent.name} : chemin relatif dans le code : {ligne.strip()[:100]}"


@pytest.mark.parametrize("readme", SEANCES, ids=lambda p: p.parent.name)
def test_s9gm_doctor_est_le_premier_geste_de_chaque_seance(readme):
    t = readme.read_text(encoding="utf-8")
    if readme.parent.name == "atelier_tour":
        pytest.skip("l'atelier se fait dans le classeur : pas d'environnement")
    i = t.index("## 2. Avant de commencer")
    j = t.index("## 3.")
    assert "s9gm doctor" in t[i:j], "s9gm doctor absent de « Avant de commencer »"


def test_installation_se_termine_par_s9gm_doctor():
    t = (RACINE / "INSTALLATION.md").read_text(encoding="utf-8")
    assert "s9gm doctor" in t and "pip install -e ." in t


def test_les_tableaux_de_symptomes_ne_renvoient_plus_au_cd_et_expliquent_le_rechargement():
    p1 = (RACINE / "seances" / "phase1" / "README.md").read_text(encoding="utf-8")
    assert not re.search(r"ModuleNotFoundError: No module named 's9gm'.*(cd|sys\.path)", p1)
    assert "s9gm doctor" in p1
    for n in ("phase3", "phase4", "phase5"):
        t = (RACINE / "seances" / n / "README.md").read_text(encoding="utf-8")
        assert "rien ne change" in t and "ma_copie" in t, n


def test_les_copies_passent_par_ma_copie_et_les_tests_par_s9gm_tester():
    for n, nom in (("phase3", "fatigue"), ("phase4", "ancrage"), ("phase5", "structure")):
        t = (RACINE / "seances" / n / "README.md").read_text(encoding="utf-8")
        assert f"s9gm copie {nom}" in t and f"s9gm tester {nom}" in t, n
        assert f'ma_copie("{nom}")' in t, n
        assert "subprocess" not in "\n".join(c for _, c in parcours.blocs(t) if "pytest" in c), n


def test_tutoriel_terminal_une_page_lie_depuis_readme_installation_et_0a():
    f = RACINE / "annexes" / "TERMINAL.md"
    assert f.is_file()
    assert len(f.read_text(encoding="utf-8").splitlines()) <= 80, "une page : 80 lignes au plus"
    for lien in (RACINE / "README.md", RACINE / "INSTALLATION.md", RACINE / "seances" / "0a" / "README.md"):
        assert "TERMINAL.md" in lien.read_text(encoding="utf-8"), lien.name


def _commandes_du_tutoriel():
    t = (RACINE / "annexes" / "TERMINAL.md").read_text(encoding="utf-8")
    blocs = re.findall(r"^```bash\n(.*?)^```", t, re.S | re.M)
    return [[l[2:] for l in b.split("\n") if l.startswith("$ ")] for b in blocs]


@pytest.mark.skipif(not shutil.which("micromamba") and not (Path.home() / ".local/bin/micromamba").exists(), reason="micromamba absent")
def test_chaque_commande_du_tutoriel_est_executee_dans_un_dossier_temporaire(tmp_path):
    mm = shutil.which("micromamba") or str(Path.home() / ".local/bin/micromamba")
    prelude = f'eval "$({mm} shell hook -s bash --root-prefix ${{MAMBA_ROOT_PREFIX:-$HOME/micromamba}})"\n'
    blocs = _commandes_du_tutoriel()
    assert blocs and sum(len(b) for b in blocs) >= 8
    for k, commandes in enumerate(blocs):
        script = prelude + "set -e\n" + "\n".join(c.replace("~/S9-GM-FOWT-DeepCwind", str(RACINE)) for c in commandes) + "\n"
        r = subprocess.run(["bash", "-c", script], cwd=tmp_path, capture_output=True, text=True, timeout=300)
        assert r.returncode == 0, f"bloc {k} :\n{script}\n{r.stderr[-800:]}"


def _noms_de_chemin(arbre):
    """Noms liés à un chemin `pathlib` : importés de `s9gm.chemins` ou assignés d'une expression `X / "…"`."""
    import ast
    noms = set()
    for n in ast.walk(arbre):
        if isinstance(n, ast.ImportFrom) and n.module == "s9gm.chemins":
            noms.update(a.asname or a.name for a in n.names)
    for n in ast.walk(arbre):
        if isinstance(n, ast.Assign) and isinstance(n.value, ast.BinOp) and isinstance(n.value.op, ast.Div):
            noms.update(t.id for t in n.targets if isinstance(t, ast.Name))
    return noms


@pytest.mark.parametrize("readme", PHASES, ids=lambda p: p.parent.name)
def test_un_chemin_pathlib_ne_se_concatene_pas_a_une_chaine(readme):
    """Un `Path` plus une chaîne lève `TypeError` : le rejeu de la phase 5 l'a révélé (`MODELE + "….dat"`)."""
    import ast
    fautes = []
    for langue, code in parcours.blocs(readme.read_text(encoding="utf-8")):
        if langue != "python":
            continue
        try:
            arbre = ast.parse(re.sub(r"<votre[^>\n]*>", "0", code))
        except SyntaxError:        # bloc à trous : couvert par les autres tests
            continue
        chemins = _noms_de_chemin(arbre)
        for n in ast.walk(arbre):
            if (isinstance(n, ast.BinOp) and isinstance(n.op, ast.Add) and isinstance(n.left, ast.Name)
                    and n.left.id in chemins and isinstance(n.right, ast.Constant) and isinstance(n.right.value, str)):
                fautes.append(f"{n.left.id} + {n.right.value!r} (ligne {n.lineno} du bloc)")
    assert not fautes, fautes
