"""Falsificateur du notebook de la séance 0b : il s'exécute de bout en bout sans erreur, et ne contient
aucune valeur du rendu R0 (NREL 5 MW). Exécuté depuis le dossier du notebook, sur le jeu de résultats livré
(`LANCER = False`) : aucun calcul OpenFAST n'est lancé."""
import json
import re
from pathlib import Path

import pytest

NB = Path(__file__).resolve().parents[2] / "seances" / "0b" / "theorie_par_les_chiffres.ipynb"


@pytest.mark.parametrize("jeu_livre", [False, True], ids=["calculs_locaux", "jeu_livre_apres_clone"])
def test_le_notebook_s_execute_de_bout_en_bout(monkeypatch, jeu_livre):
    if jeu_livre:
        monkeypatch.setenv("S9GM_JEU_LIVRE", "1")  # ignore results/0b/iea15_calculs : lit data/*.csv.gz comme après un clone
    nbformat = pytest.importorskip("nbformat")
    nbclient = pytest.importorskip("nbclient")
    nb = nbformat.read(NB, as_version=4)
    client = nbclient.NotebookClient(nb, timeout=300, resources={"metadata": {"path": str(NB.parent)}})
    client.execute()  # lève CellExecutionError à la première cellule en erreur
    erreurs = [o for c in nb.cells if c.cell_type == "code" for o in c.outputs if o.output_type == "error"]
    assert not erreurs
    if jeu_livre:
        sources = "".join("".join(o.get("text", "")) for c in nb.cells if c.cell_type == "code" for o in c.outputs)
        assert "jeu livré" in sources


def test_aucune_valeur_de_reponse_R0():
    """La NREL 5 MW (machine du rendu R0) ne doit pas apparaître dans le notebook : ni son nom, ni ses
    grandeurs caractéristiques (R = 63 m, 12,1 tr/min, 7,55 de TSR, 11,4 m/s)."""
    texte = "\n".join("".join(c["source"]) for c in json.loads(NB.read_text(encoding="utf-8"))["cells"])
    for motif in (r"NREL\s*5", r"\b63\s*m\b", r"12[.,]1\s*tr", r"7[.,]55\b", r"11[.,]4\s*m/s"):
        assert not re.search(motif, texte), f"motif R0 trouvé dans le notebook : {motif}"


def test_le_notebook_ne_modifie_aucun_fichier_suivi(monkeypatch):
    """Règle du parcours : l'étudiant ne modifie aucun fichier suivi par git. Exécuté tel quel, le carnet écrit ses
    figures sous `results/` (ignoré) et laisse intactes les figures de référence de `seances/0b/figures/`."""
    import hashlib
    monkeypatch.delenv("S9GM_ENSEIGNANT", raising=False)
    monkeypatch.setenv("S9GM_JEU_LIVRE", "1")
    nbformat = pytest.importorskip("nbformat")
    nbclient = pytest.importorskip("nbclient")
    ref = sorted((NB.parent / "figures").glob("*.png"))
    assert ref, "figures de référence absentes"
    avant = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in ref}
    nb = nbformat.read(NB, as_version=4)
    nbclient.NotebookClient(nb, timeout=300, resources={"metadata": {"path": str(NB.parent)}}).execute()
    assert {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in ref} == avant
    ecrites = sorted((NB.parents[2] / "results" / "0b" / "figures").glob("FIG-S9GM-VISU-00*.png"))
    assert len(ecrites) == len(ref)
