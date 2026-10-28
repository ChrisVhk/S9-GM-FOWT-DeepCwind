"""Fiches F2, F3, F5, F9 (fatigue de structure) et F10 (structures tubulaires), tirées des masters : liens de « Théorie à lire », déclaration du master,
règles du public (R-8, R-9), formules lisibles sur GitHub. Écrits AVANT les fiches."""
import os
import re
from pathlib import Path

import pytest

from .conftest import RACINE

FICHES = {"F2": RACINE / "fiches" / "F2_Houle-lineaire.md", "F3": RACINE / "fiches" / "F3_Hydrostatique.md", "F5": RACINE / "fiches" / "F5_Hydrodynamique-potentielle.md",
          "F9": RACINE / "fiches" / "F9_Fatigue-de-structure.md", "F10": RACINE / "fiches" / "F10_Structures-tubulaires.md"}
PHASE = {"F2": RACINE / "seances" / "phase1" / "README.md", "F3": RACINE / "seances" / "0b" / "README.md", "F5": RACINE / "seances" / "phase2" / "README.md",
         "F9": RACINE / "seances" / "phase3" / "README.md", "F10": RACINE / "seances" / "phase5" / "README.md"}
MASTER = "Cours/OFFSHORE_Structures-Fondations/01_Houle-et-hydrodynamique-des-flotteurs.md"
MASTER2 = "Cours/OFFSHORE_Structures-Fondations/02_Fatigue-et-structures-tubulaires.md"
MASTER_DE = {"F2": MASTER, "F3": MASTER, "F5": MASTER, "F9": MASTER2, "F10": MASTER2}
# motifs scindés en deux littéraux : le test ne doit pas se déclarer lui-même fautif (R-9)
INTERDIT = re.compile(r"(?<![0-9A-Za-z.])E-\d{2,3}\b|_Cou" "lisses|\bcou" "lisses/|ENSM-Ensei" "gnement|_Rese" "rve/|dépôt d.ensei" "gnement|à comp" "léter", re.I)


@pytest.mark.parametrize("nom", FICHES)
def test_la_fiche_existe_et_declare_ses_destinations_et_son_master(nom):
    f = FICHES[nom]
    assert f.is_file(), f
    tete = "\n".join(f.read_text(encoding="utf-8").splitlines()[:40])
    assert re.search(r"<!--\s*destinations\s*:\s*github", tete), "destinations non déclarées"
    m = re.search(r"<!--\s*master\s*:\s*([^;>]+?)\s*(?:;[^>]*)?-->", tete)
    assert m and m.group(1).strip() == MASTER_DE[nom], "master non déclaré en tête de fiche (forme A)"


@pytest.mark.parametrize("nom", FICHES)
def test_le_master_declare_existe_si_les_masters_sont_disponibles(nom):
    racine = os.environ.get("S9GM_RACINE_MASTERS")
    if not racine:
        pytest.skip("S9GM_RACINE_MASTERS=<dossier contenant Cours/> non défini")
    assert (Path(racine) / MASTER_DE[nom]).is_file()


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
    assert "fiche F2" in form and "fiche F3" in form and "fiche F5" in form and "fiche F9" in form and "fiche F10" in form


def test_la_seance_0b_etape_3_3_renvoie_a_f3_et_l_index_la_donne_publiee():
    t = texte_0b = (RACINE / "seances" / "0b" / "README.md").read_text(encoding="utf-8")
    etape = t.split("### 3.3 Raideurs hydrostatiques", 1)[1].split("\n### 3.4", 1)[0]
    assert "F3_Hydrostatique.md" in etape and "à venir" not in etape.split("\n")[2], "l'étape 3.3 de la séance 0b renvoie toujours à une fiche « à venir »"
    index = (RACINE / "fiches" / "README.md").read_text(encoding="utf-8")
    ligne = next(l for l in index.split("\n") if l.startswith("| F3 "))
    assert "publiée" in ligne and "F3_Hydrostatique.md" in ligne, ligne


def test_f3_n_utilise_que_la_notation_c_ij_et_aucune_valeur_du_cas_oc4():
    t = FICHES["F3"].read_text(encoding="utf-8")
    assert "C_{33}" in t or "C33" in t
    assert not re.search(r"\bK\s*_?\{?(33|44|55)\}?\b", t.replace("`K_{ij}`", "").replace("K_{ij}", "")), "notation K_ij réservée à la mention de la correspondance avec Molin"
    for interdit in ("12 m³", "3,45", "OC4"):    # aucun nombre ni nom de cas du projet
        assert interdit not in t, interdit


def test_corrections_du_controle_independant_du_15_10_f2_et_f5():
    """Trois écarts relevés par un auditeur neuf (22/25) : critère de Stokes, sens de « premier ordre », contenu des fichiers de coefficients."""
    f2 = FICHES["F2"].read_text(encoding="utf-8")
    f5 = FICHES["F5"].read_text(encoding="utf-8")
    plat2 = re.sub(r"\s+", " ", f2)
    plat5 = re.sub(r"\s+", " ", f5)
    assert "fonction de courant" in plat2 and "quand la cambrure est modérée" not in plat2
    assert "Stokes d'ordre supérieur quand le nombre d'Ursell `U_R`" in plat2
    assert "approximation découplée" in plat5 and "au premier ordre `ω_j" not in plat5
    assert "ni le maillage ni la profondeur n'y figurent" in plat5
    assert "le master et Molin écrivent aussi la RAO `f_j" in plat5            # conflit de notation dit
    assert "`M` inclut la masse ajoutée" in plat5
    assert "adimensionnées" in plat5 and "amplitude de houle" in plat5.split("adimensionnées", 1)[1][:200]


PUBLIC_MD = [RACINE / "README.md", RACINE / "ENONCE.md", RACINE / "fiches" / "README.md"] + sorted((RACINE / "seances").glob("*/README.md"))


def test_f8_devient_ancrage_dynamique_partout_et_f9_f10_sont_publiees_a_l_index():
    """E-222 (28/10) : F8 = « Ancrage dynamique » seulement ; la fatigue de structure est F9, les structures tubulaires F10."""
    for f in PUBLIC_MD:
        assert "Ancrage dynamique et fatigue" not in f.read_text(encoding="utf-8"), f.relative_to(RACINE)
    index = (RACINE / "fiches" / "README.md").read_text(encoding="utf-8")
    lignes = {l.split("|")[1].strip(): l for l in index.split("\n") if l.startswith("| F")}
    assert "Ancrage dynamique" in lignes["F8"] and "fatigue" not in lignes["F8"].lower().split("|")[2], lignes["F8"]
    for nom in ("F9", "F10"):
        assert "publiée" in lignes[nom] and FICHES[nom].name in lignes[nom], lignes[nom]
    p3 = (RACINE / "seances" / "phase3" / "README.md").read_text(encoding="utf-8")
    assert "F8" not in p3.split("## 6. Théorie à lire", 1)[1].split("\n## ", 1)[0], "la phase 3 ne renvoie plus à F8"
    assert "**À lire avant la séance : F9" in p3, "en-tête de la phase 3"


def test_f9_expose_sans_recommander_ni_completer_le_rainflow():
    t = re.sub(r"\s+", " ", FICHES["F9"].read_text(encoding="utf-8"))
    assert "<!-- master:" in t and "sections 1 à 6" in t.split("-->", 2)[1]
    assert not re.search(r"\bDFF\s*(=|vaut|:)\s*\d", t), "aucun DFF recommandé (ARB-OSF-018)"
    assert "DFF" in t and "n'en recommande aucun" in t
    assert "algorithme détaillé : norme de référence, non fournie ici" in t, "lacune du rainflow dite sobrement"
    assert not re.search(r"E\s?1049", t), "aucune référence de registre ni de lacune interne dans la fiche publique"
    assert "source unique" not in t.lower() and "D4" not in t


def test_f10_ne_fixe_aucun_scf_et_n_emploie_que_la_rp_c203_pour_efthymiou():
    t = re.sub(r"\s+", " ", FICHES["F10"].read_text(encoding="utf-8"))
    assert "sections 7 à 12" in t.split("-->", 2)[1]
    assert not re.search(r"SCF\s*(=|vaut|:)\s*\d", t), "aucun SCF du projet fixé (ARB-OSF-046)"
    assert "appartient à l'enseignant" in t, "le choix du SCF de calcul"
    assert "Efthymiou" in t and "RP-C203" in t
    assert not re.search(r"\(3\.1[0-4]\d\)", t), "aucune équation d'El-Reedy (ARB-OSF-020)"
    assert "domaine de validité" in t


@pytest.mark.parametrize("nom", ["F9", "F10"])
def test_f9_f10_ne_citent_ni_conference_ni_intervenant_ni_valeur_du_classeur(nom):
    t = FICHES[nom].read_text(encoding="utf-8")
    assert not re.search(r"conf[ée]rence|intervenant|classeur d'atelier|WDZ", t, re.I)
    assert not re.search(r"\b(263|0,985|135,87|3\s?122,9)\b", t), "aucun nombre issu de la conférence ou du classeur (ARB-OSF-022)"
