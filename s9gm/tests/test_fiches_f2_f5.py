"""Fiches F2 (houle linéaire) et F5 (hydrodynamique potentielle), tirées du master : liens de « Théorie à lire », déclaration du master,
règles du public (R-8, R-9), formules lisibles sur GitHub. Écrits AVANT les fiches."""
import os
import re
from pathlib import Path

import pytest

from .conftest import RACINE

FICHES = {"F2": RACINE / "fiches" / "F2_Houle-lineaire.md", "F5": RACINE / "fiches" / "F5_Hydrodynamique-potentielle.md"}
PHASE = {"F2": RACINE / "seances" / "phase1" / "README.md", "F5": RACINE / "seances" / "phase2" / "README.md"}
MASTER = "Cours/OFFSHORE_Structures-Fondations/01_Houle-et-hydrodynamique-des-flotteurs.md"
INTERDIT = re.compile(r"(?<![0-9A-Za-z.])E-\d{2,3}\b|_Coulisses|\bcoulisses/|ENSM-Enseignement|_Reserve/|dépôt d.enseignement|à compléter", re.I)


@pytest.mark.parametrize("nom", FICHES)
def test_la_fiche_existe_et_declare_ses_destinations_et_son_master(nom):
    f = FICHES[nom]
    assert f.is_file(), f
    tete = "\n".join(f.read_text(encoding="utf-8").splitlines()[:40])
    assert re.search(r"<!--\s*destinations\s*:\s*github", tete), "destinations non déclarées"
    m = re.search(r"<!--\s*master\s*:\s*([^;>]+?)\s*(?:;[^>]*)?-->", tete)
    assert m and m.group(1).strip() == MASTER, "master non déclaré en tête de fiche (forme A)"


@pytest.mark.parametrize("nom", FICHES)
def test_le_master_declare_existe_si_les_masters_sont_disponibles(nom):
    racine = os.environ.get("S9GM_RACINE_MASTERS")
    if not racine:
        pytest.skip("S9GM_RACINE_MASTERS=<dossier contenant Cours/> non défini")
    assert (Path(racine) / MASTER).is_file()


@pytest.mark.parametrize("nom", FICHES)
def test_la_fiche_respecte_les_regles_du_public(nom):
    f = FICHES[nom]
    assert f.is_file(), f
    texte = f.read_text(encoding="utf-8")
    assert not INTERDIT.findall(texte), INTERDIT.findall(texte)
    assert "$$" not in texte, "formules d'affichage : bloc ```math, pas $$"
    for section in ("## Pourquoi", "## Minimum vital", "## Ordres de grandeur", "## Ce que le modèle ne permet pas de conclure", "## Pour aller plus loin"):
        assert section in texte, section
    assert "**À lire avant**" in texte


@pytest.mark.parametrize("nom", FICHES)
def test_la_theorie_a_lire_pointe_vers_la_fiche(nom):
    texte = PHASE[nom].read_text(encoding="utf-8")
    section = texte.split("## 6. Théorie à lire", 1)[1].split("\n## ", 1)[0]
    cible = FICHES[nom].name
    assert f"(../../fiches/{cible})" in section, section
    assert f"{nom} (" not in section.replace(f"[{nom}", "") or "fiche à venir" not in section.split(nom, 1)[1].split("\n", 1)[0]
    assert (PHASE[nom].parent / "../../fiches" / cible).resolve().is_file()


def test_les_autres_fiches_restent_annoncees():
    section = PHASE["F5"].read_text(encoding="utf-8").split("## 6. Théorie à lire", 1)[1]
    assert "F6" in section and "fiche à venir" in section, "F6 reste « à venir »"


def test_enonce_et_formulaire_connaissent_les_fiches():
    enonce = (RACINE / "ENONCE.md").read_text(encoding="utf-8")
    for nom, f in FICHES.items():
        assert f"fiches/{f.name}" in enonce, nom
    assert "Une seule existe à ce jour" not in enonce
    form = (RACINE / "fiches" / "FORMULAIRE.md").read_text(encoding="utf-8")
    assert "fiche F2" in form and "fiche F5" in form
