"""Lot Q1 : `annexes/outils/` ne garde que les deux scripts de PROVENANCE DES DONNÉES ; les deux scripts historiques sont archivés et plus cités ;
`s9gm/POST-TRAITER.md` § 6 décrit la procédure actuelle (`s9gm copie` / `ma_copie`) et plus l'ancienne. Écrits AVANT les retraits et réécritures."""
import re
import subprocess
from pathlib import Path

from .conftest import RACINE

RETIRES = ("lire_" "outb", "exemple_" "chaine")       # scindés : ce test ne doit pas se citer lui-même
GARDES = ("courbe_cp_nrel5mw.py", "exporter_iea15_stationnaire.py")


def suivis():
    return [f for f in subprocess.run(["git", "ls-files"], cwd=RACINE, capture_output=True, text=True, check=True).stdout.split("\n") if f]


def test_annexes_outils_ne_garde_que_les_scripts_de_provenance_des_donnees():
    presents = sorted(f.name for f in (RACINE / "annexes" / "outils").glob("*.py"))
    assert presents == sorted(GARDES), presents


def test_les_deux_scripts_historiques_ne_sont_plus_cites():
    fautes = []
    for f in suivis():
        if f == "TRANSITION.md" or f.startswith("s9gm/tests/") or not f.endswith((".md", ".py", ".ipynb", ".sh", ".txt")):
            continue
        t = (RACINE / f).read_text(encoding="utf-8", errors="ignore")
        if any(r in t for r in RETIRES):
            fautes.append(f)
    assert not fautes, fautes


def test_transition_dit_ou_sont_passes_les_deux_scripts():
    t = (RACINE / "TRANSITION.md").read_text(encoding="utf-8")
    assert all(r in t for r in RETIRES)


def test_la_carte_du_readme_decrit_annexes_outils_comme_provenance_des_donnees():
    t = (RACINE / "README.md").read_text(encoding="utf-8")
    ligne = next(l for l in t.split("\n") if l.startswith("| `annexes/`"))
    assert "provenance des données" in ligne and "non utilisés dans le parcours" in ligne, ligne
    assert "le seul outil" in t     # la phrase du README reste vraie


def test_plus_d_ancienne_procedure_dans_le_public():
    fautes = []
    for f in suivis():
        if f.startswith("s9gm/tests/") or not f.endswith(".md"):
            continue
        t = (RACINE / f).read_text(encoding="utf-8", errors="ignore")
        for motif in ("fatigue_" "maison", "S9GM_FATIGUE_" "COMPLET", "sys.path." "insert"):
            if motif in t:
                fautes.append(f"{f} : {motif}")
    assert not fautes, fautes


def test_post_traiter_decrit_la_procedure_actuelle_de_la_copie():
    t = (RACINE / "s9gm" / "POST-TRAITER.md").read_text(encoding="utf-8")
    sec = t.split("## 6. Fatigue", 1)[1].split("\n## 7.", 1)[0]
    for attendu in ("s9gm copie fatigue", "s9gm tester fatigue", 'ma_copie("fatigue")', "results/mon_s9gm/"):
        assert attendu in sec, attendu
    assert "results/cas_0b/F03" not in sec, "le fil rouge de la phase 3 n'est pas un cas de la séance 0b"
    assert "depuis la racine du dépôt" not in t, "les commandes se lancent de n'importe quel dossier"
    assert "s9gm doctor" in t
