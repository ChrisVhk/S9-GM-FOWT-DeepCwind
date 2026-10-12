"""Falsificateurs du classeur d'architecture du flotteur (séance 0b, point 7) et de `scripts/verifier_architecture.py`.

Le classeur a deux versions : la COMPLÈTE (coulisses, chaque valeur sourcée) et l'ÉTUDIANTE (publique,
`seances/0b/DeepCwind_ARCHITECTURE.xlsx`, colonne centrale résolue en exemple, le reste « à remplir »). Le contrôle compare un classeur rempli,
membre par membre, au fichier HydroDyn de `modeles/flottant`.

- A-1 : la version complète passe le contrôle à 100 %.
- A-2 : une copie altérée sur 3 cellules donne exactement 3 écarts, nommés.
- A-3 : la version étudiante vide donne « manquant » partout, sauf pour la colonne centrale.
- A-4 : aucune cellule de la version étudiante, hors exemple et hors `Donnees`, ne contient de nombre égal à une valeur de la version complète.

Public / coulisses : ce dépôt public ne contient AUCUN générateur de classeur complet depuis le vrai fichier HydroDyn (il vit en coulisses,
avec le classeur complet). Les tests publics éprouvent le contrôle sur une FIXTURE SYNTHÉTIQUE (trois membres inventés) ; A-1 et A-4 sur le VRAI
classeur complet se lancent avec `S9GM_ARCHITECTURE_COMPLET=<chemin>` (sinon ils sont ignorés). Le contrôle ne dit jamais la valeur attendue :
il nomme le champ fautif et la valeur saisie.
Convention des étiquettes (texte, jamais des nombres, pour que A-4 ait un sens) : membres `M1`…, nœuds `N1`…, jeux de propriétés `P1`…
"""
import importlib.util
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import openpyxl
import pytest

from .conftest import MODELES, RACINE

SCRIPT = RACINE / "scripts" / "verifier_architecture.py"
ETUDIANT = RACINE / "seances" / "0b" / "DeepCwind_ARCHITECTURE.xlsx"
HYDRODYN = MODELES / "oc4_rtest" / "5MW_OC4Semi_WSt_WavesWN" / "NRELOffshrBsline5MW_OC4DeepCwindSemi_HydroDyn.dat"
COMPLET = os.environ.get("S9GM_ARCHITECTURE_COMPLET")
A_REMPLIR = "à remplir"

# Groupes de coefficients (étiquettes de la feuille Coefficients) : identiques dans les deux versions.
GROUPES = ["Colonne centrale", "Colonnes déportées", "Bases", "Pontons", "Entretoises"]
GROUPE_DU_MEMBRE = {**{1: GROUPES[0]}, **{i: GROUPES[1] for i in (2, 3, 4)}, **{i: GROUPES[2] for i in (5, 6, 7, 23, 24, 25)},
                    **{i: GROUPES[3] for i in range(8, 20)}, **{i: GROUPES[4] for i in (20, 21, 22)}}
EXEMPLE_MEMBRE = 1                         # la colonne centrale


def _charger_script():
    if not SCRIPT.is_file():
        pytest.fail(f"{SCRIPT.relative_to(RACINE)} n'existe pas encore")
    spec = importlib.util.spec_from_file_location("verifier_architecture", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["verifier_architecture"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def va():
    return _charger_script()


HYDRODYN_SYNTHETIQUE = """------- HydroDyn Input File ---------------------------------------
fixture de test : trois membres inventés (aucun lien avec la DeepCwind)
---------------------- MEMBER JOINTS -------------------------------------------
             6   NJoints        - Number of joints (-)
JointID   Jointxi     Jointyi     Jointzi  JointAxID   JointOvrlp
   (-)     (m)         (m)         (m)        (-)       (switch)
    1     0.00000     0.00000   -10.00000      1            0
    2     0.00000     0.00000     5.00000      1            0
    3     8.00000     0.00000    -9.94000      1            0
    4     8.00000     0.00000     3.00000      1            0
    5     2.00000     1.00000     1.00000      1            0
    6     6.00000     3.00000     1.00000      1            0
---------------- CYLINDRICAL MEMBER CROSS-SECTION PROPERTIES -------------------
             3   NPropSetsCyl    - Number of cylindrical member property sets (-)
PropSetID    PropD         PropThck
   (-)        (m)            (m)
    1        5.00000        0.02000          ! A
    2       10.00000        0.04000          ! B
    3        1.00000        0.01000          ! C
------ MEMBER-BASED CYLINDRICAL-MEMBER HYDRODYNAMIC COEFFICIENTS (model 3) ------
            3   NCoefMembersCyl - Number of member-based cylindrical member coefficients (-)
MemberID    MemberCd1     MemberCd2    MemberCdMG1   MemberCdMG2    MemberCa1     MemberCa2
   (-)         (-)           (-)           (-)           (-)           (-)           (-)
    1          0.50          0.50          0.00          0.00          0.10          0.10
    2          0.60          0.60          0.00          0.00          0.20          0.20
    3          0.70          0.70          0.00          0.00          0.30          0.30
-------------------- MEMBERS -------------------------------------------------
             3   NMembers       - Number of members (-)
MemberID  MJointID1  MJointID2  MPropSetID1  MPropSetID2  MSecGeom    MSpinOrient   MDivSize   MCoefMod
  (-)        (-)        (-)         (-)          (-)      (switch)       (deg)        (m)      (switch)
   1          1          2           1            1           1            0         1.0000        3          ! Colonne synthetique
   2          3          4           2            2           1            0         2.0000        3          ! Base synthetique
   3          5          6           3            3           1            0         0.5000        3          ! Tube synthetique
---------------------- FILLED MEMBERS ------------------------------------------
"""
# membre -> (noeud1, noeud2, jeu, discrétisation, groupe) ; coordonnées lues de la fixture
GROUPES_SYNTH = {1: "Colonne centrale", 2: "Bases", 3: "Pontons"}


def _hydrodyn_synthetique(tmp_path):
    chemin = tmp_path / "HydroDyn_synthetique.dat"
    chemin.write_text(HYDRODYN_SYNTHETIQUE, encoding="utf-8")
    return chemin


def _classeur_synthetique(chemin, noms=True):
    """Classeur complet de la FIXTURE SYNTHÉTIQUE (3 membres, jamais la DeepCwind) dans la mise en page des deux versions."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Noeuds"
    ws.append(["Noeud", "x (m)", "y (m)", "z (m)"])
    for etiquette, xyz in (("N1", (0, 0, -10)), ("N2", (0, 0, 5)), ("N3", (8, 0, -9.94)), ("N4", (8, 0, 3)), ("N5", (2, 1, 1)), ("N6", (6, 3, 1))):
        ws.append([etiquette, *xyz])
    ws = wb.create_sheet("Membres")
    ws.append(["Membre", "Nom", "Groupe", "Noeud 1", "Noeud 2", "Jeu de propriétés", "Discrétisation (m)"])
    for i, (n1, n2, jeu, div) in {1: ("N1", "N2", "P1", 1.0), 2: ("N3", "N4", "P2", 2.0), 3: ("N5", "N6", "P3", 0.5)}.items():
        ws.append([f"M{i}", f"membre {i}" if noms else None, GROUPES_SYNTH[i], n1, n2, jeu, div])
    ws = wb.create_sheet("Proprietes")
    ws.append(["Jeu", "Diamètre (m)", "Épaisseur (m)"])
    for e, d, t in (("P1", 5.0, 0.02), ("P2", 10.0, 0.04), ("P3", 1.0, 0.01)):
        ws.append([e, d, t])
    ws = wb.create_sheet("Coefficients")
    ws.append(["Groupe", "Cd", "Ca"])
    for g, cd, ca in (("Colonne centrale", 0.5, 0.1), ("Bases", 0.6, 0.2), ("Pontons", 0.7, 0.3)):
        ws.append([g, cd, ca])
    wb.save(chemin)
    return chemin


def _lignes_sorties(texte):
    """`Membre M5 (Base Column 1) : juste` -> {5: ('juste', détail)}"""
    res = {}
    for l in texte.splitlines():
        m = re.match(r"^Membre M(\d+) \(.*?\) : (juste|écart|manquant)(.*)$", l)
        if m:
            res[int(m[1])] = (m[2], m[3])
    return res


def _lancer(classeur, hydrodyn=None):
    cmd = [sys.executable, "-I", str(SCRIPT), str(classeur)] + (["--hydrodyn", str(hydrodyn)] if hydrodyn else [])
    return subprocess.run(cmd, cwd=RACINE, capture_output=True, text=True)


# ---------------------------------------------------------------------------------------- le contrôle lui-même (fixture synthétique)
def _modifier(chemin, feuille, etiquette, colonne, valeur=None, delta=None):
    wb = openpyxl.load_workbook(chemin)
    ligne = next(r for r in wb[feuille].iter_rows(min_row=2) if r[0].value == etiquette)
    ligne[colonne].value = (ligne[colonne].value + delta) if delta is not None else valeur
    wb.save(chemin)


def test_a1_un_classeur_complet_passe_a_100_pour_cent(tmp_path, va):
    hyd = _hydrodyn_synthetique(tmp_path)
    r = _lancer(_classeur_synthetique(tmp_path / "complet.xlsx"), hyd)
    v = _lignes_sorties(r.stdout)
    assert len(v) == 3 and all(s == "juste" for s, _ in v.values()), r.stdout
    assert r.returncode == 0


def test_a2_trois_cellules_alterees_donnent_exactement_trois_ecarts_nommes(tmp_path, va):
    hyd = _hydrodyn_synthetique(tmp_path)
    chemin = _classeur_synthetique(tmp_path / "altere.xlsx")
    _modifier(chemin, "Noeuds", "N2", 3, delta=0.5)                 # z de N2 : seul le membre 1 l'utilise
    _modifier(chemin, "Membres", "M2", 6, valeur=3.0)               # discrétisation de M2
    _modifier(chemin, "Membres", "M3", 5, valeur="P1")              # M3 rattaché au mauvais jeu de propriétés
    r = _lancer(chemin, hyd)
    v = _lignes_sorties(r.stdout)
    assert {i for i, (s, _) in v.items() if s == "écart"} == {1, 2, 3}, r.stdout
    assert "N2" in v[1][1] and "z" in v[1][1], r.stdout
    assert "discrétisation" in v[2][1], r.stdout
    assert "jeu" in v[3][1].lower(), r.stdout
    assert r.returncode != 0


def test_un_ecart_nomme_le_champ_sans_donner_la_valeur_attendue(tmp_path, va):
    """Le contrôle n'est pas un oracle : il dit OÙ est l'écart et ce que l'étudiant a saisi, jamais ce que contient le fichier."""
    hyd = _hydrodyn_synthetique(tmp_path)
    chemin = _classeur_synthetique(tmp_path / "ecart.xlsx")
    _modifier(chemin, "Noeuds", "N2", 3, valeur=0.0)                # z de N2 saisi à 0 (le fichier : 5)
    _modifier(chemin, "Proprietes", "P2", 1, valeur=7.0)            # diamètre de P2 saisi à 7 (le fichier : 10)
    _modifier(chemin, "Coefficients", "Pontons", 1, valeur=0.1)     # Cd des pontons saisi à 0,1 (le fichier : 0,7)
    sortie = _lancer(chemin, hyd).stdout
    assert "écart" in sortie
    assert "fichier :" not in sortie and "(fichier" not in sortie
    for attendu in ("5", "10", "0.7"):
        assert not re.search(rf"(?<![\d.]){re.escape(attendu)}(?![\d.])", re.sub(r"Membre M\d+", "", re.sub(r"[NP]\d+", "", sortie))), \
            f"la valeur attendue {attendu} apparaît dans le message"
    assert "N2" in sortie and "diamètre" in sortie and "Cd" in sortie        # le champ est nommé


def test_la_tolerance_accepte_les_valeurs_arrondies_des_documents_sources(tmp_path, va):
    """Un document arrondit à 0,01 m et ses tableaux s'écartent du fichier jusqu'à 6 cm (la base d'une colonne : -20 m dans le document, -19,94 m dans
    le fichier) : saisir la valeur du document n'est PAS un écart. Une erreur de 15 cm l'est."""
    hyd = _hydrodyn_synthetique(tmp_path)
    chemin = _classeur_synthetique(tmp_path / "doc.xlsx")
    _modifier(chemin, "Noeuds", "N3", 3, valeur=-10.0)               # fichier : -9,94 ; document : -10
    assert _lignes_sorties(_lancer(chemin, hyd).stdout)[2][0] == "juste"
    _modifier(chemin, "Noeuds", "N3", 3, valeur=-9.79)               # 15 cm d'écart
    assert _lignes_sorties(_lancer(chemin, hyd).stdout)[2][0] == "écart"


def test_la_tolerance_est_justifiee_dans_le_script():
    code = SCRIPT.read_text(encoding="utf-8")
    ligne = next(l for l in code.splitlines() if l.startswith("TOL_COORD"))
    assert "0.07" in ligne
    assert "arrondi" in code and "6 cm" in code                    # justification d'après l'arrondi des documents sources


def test_les_noms_des_membres_viennent_du_classeur_pas_du_fichier(tmp_path, va):
    """Un membre sans nom dans le classeur s'affiche « sans nom » : le contrôle ne révèle pas les noms du fichier HydroDyn."""
    hyd = _hydrodyn_synthetique(tmp_path)
    sortie = _lancer(_classeur_synthetique(tmp_path / "anonyme.xlsx", noms=False), hyd).stdout
    assert "sans nom" in sortie
    assert "synthetique" not in sortie.lower()


def test_une_cellule_vide_ou_a_remplir_est_manquante_pas_fausse(tmp_path, va):
    hyd = _hydrodyn_synthetique(tmp_path)
    chemin = _classeur_synthetique(tmp_path / "trou.xlsx")
    _modifier(chemin, "Membres", "M2", 4, valeur=A_REMPLIR)
    _modifier(chemin, "Coefficients", "Pontons", 1, valeur=None)
    v = _lignes_sorties(_lancer(chemin, hyd).stdout)
    assert v[2][0] == "manquant" and v[3][0] == "manquant" and v[1][0] == "juste"


def test_le_sens_des_noeuds_compte(tmp_path, va):
    hyd = _hydrodyn_synthetique(tmp_path)
    chemin = _classeur_synthetique(tmp_path / "sens.xlsx")
    wb = openpyxl.load_workbook(chemin)
    ligne = next(r for r in wb["Membres"].iter_rows(min_row=2) if r[0].value == "M1")
    ligne[3].value, ligne[4].value = ligne[4].value, ligne[3].value
    wb.save(chemin)
    assert _lignes_sorties(_lancer(chemin, hyd).stdout)[1][0] == "écart"


def test_un_classeur_illisible_est_refuse(tmp_path, va):
    faux = tmp_path / "faux.xlsx"
    faux.write_text("pas un classeur", encoding="utf-8")
    r = _lancer(faux)
    assert r.returncode != 0 and "Traceback" not in r.stderr


# ------------------------------------------------------------------------------ la version étudiante (publique)
@pytest.fixture(scope="module")
def etudiant():
    assert ETUDIANT.is_file(), f"{ETUDIANT.relative_to(RACINE)} n'existe pas encore"
    return ETUDIANT


def test_a3_la_version_etudiante_vide_est_manquante_partout_sauf_la_colonne_centrale(etudiant, va):
    r = _lancer(etudiant)
    v = _lignes_sorties(r.stdout)
    assert len(v) == 25, r.stdout
    assert v[EXEMPLE_MEMBRE][0] == "juste", r.stdout
    assert all(s == "manquant" for i, (s, _) in v.items() if i != EXEMPLE_MEMBRE), r.stdout
    assert r.returncode != 0


def _nombres(wb, feuilles_exclues=("Donnees", "Sources")):
    sortie = []
    for ws in wb.worksheets:
        if ws.title in feuilles_exclues:
            continue
        for ligne in ws.iter_rows():
            for c in ligne:
                if isinstance(c.value, (int, float)) and not isinstance(c.value, bool):
                    sortie.append((ws.title, c.coordinate, float(c.value)))
    return sortie


def _cellules_exemple(wb):
    """Cellules de l'exemple résolu (colonne centrale) : ligne M1, nœuds et jeu qu'elle utilise, groupe central."""
    ex = set()
    lm = next(r for r in wb["Membres"].iter_rows(min_row=2) if r[0].value == f"M{EXEMPLE_MEMBRE}")
    ex |= {("Membres", c.coordinate) for c in lm}
    noeuds, jeu = {lm[3].value, lm[4].value}, lm[5].value
    ex |= {("Noeuds", c.coordinate) for r in wb["Noeuds"].iter_rows(min_row=2) if r[0].value in noeuds for c in r}
    ex |= {("Proprietes", c.coordinate) for r in wb["Proprietes"].iter_rows(min_row=2) if r[0].value == jeu for c in r}
    ex |= {("Coefficients", c.coordinate) for r in wb["Coefficients"].iter_rows(min_row=2) if r[0].value == GROUPES[0] for c in r}
    return ex


@pytest.mark.skipif(not COMPLET, reason="version complète en coulisses : S9GM_ARCHITECTURE_COMPLET=<chemin>")
def test_a1_reel_la_version_complete_des_coulisses_passe_a_100_pour_cent(va):
    r = _lancer(COMPLET)
    v = _lignes_sorties(r.stdout)
    assert len(v) == 25 and all(s == "juste" for s, _ in v.values()), r.stdout
    assert r.returncode == 0


@pytest.mark.skipif(not COMPLET, reason="version complète en coulisses : S9GM_ARCHITECTURE_COMPLET=<chemin>")
def test_a4_aucune_cellule_etudiante_hors_exemple_ne_livre_une_valeur_de_la_version_complete(etudiant):
    complet = {round(v, 9) for _, _, v in _nombres(openpyxl.load_workbook(COMPLET))}
    wb = openpyxl.load_workbook(etudiant)
    exemple = _cellules_exemple(wb)
    fuites = [(f, c, v) for f, c, v in _nombres(wb) if (f, c) not in exemple and round(v, 9) in complet]
    assert not fuites, fuites


def test_a4_bis_la_version_etudiante_ne_contient_aucun_nombre_hors_exemple_et_donnees(etudiant):
    """Sans la version complète sous la main : la version étudiante n'a aucun nombre en dehors de l'exemple et de `Donnees`."""
    wb = openpyxl.load_workbook(etudiant)
    exemple = _cellules_exemple(wb)
    reste = [(f, c, v) for f, c, v in _nombres(wb) if (f, c) not in exemple]
    assert not reste, reste


def test_la_version_etudiante_a_les_feuilles_attendues_et_pas_de_sources(etudiant):
    wb = openpyxl.load_workbook(etudiant)
    assert wb.sheetnames == ["Donnees", "Noeuds", "Membres", "Proprietes", "Coefficients"]
    assert not any(isinstance(c.value, str) and c.value.startswith("=") for ws in wb for r in ws.iter_rows() for c in r), "aucune formule"


def test_la_consigne_de_la_0b_donne_la_commande_et_n_a_plus_de_a_completer_sur_le_classeur():
    texte = (RACINE / "seances" / "0b" / "README.md").read_text(encoding="utf-8")
    assert "scripts/verifier_architecture.py" in texte
    assert "DeepCwind_ARCHITECTURE.xlsx" in texte
    bloc = texte[texte.index("### 3.2"):texte.index("### 3.3")]
    assert "à compléter" not in bloc.lower()


def test_cd_et_ca_du_groupe_sont_controles_pour_tous_ses_membres(tmp_path, va):
    hyd = _hydrodyn_synthetique(tmp_path)
    chemin = _classeur_synthetique(tmp_path / "coef.xlsx")
    wb = openpyxl.load_workbook(chemin)
    # un second membre dans le même groupe « Bases » : même Cd et Ca
    ws = wb["Membres"]
    ligne = next(r for r in ws.iter_rows(min_row=2) if r[0].value == "M3")
    ligne[2].value = "Bases"
    wb["Coefficients"]["B3"].value = 0.7        # Cd de « Bases » (fichier : 0,6 pour M2 et 0,7 pour M3)
    wb.save(chemin)
    v = _lignes_sorties(_lancer(chemin, hyd).stdout)
    assert v[2][0] == "écart" and "Cd" in v[2][1]
    assert v[3][0] == "écart" and "Ca" in v[3][1]


def test_les_membres_que_le_document_ne_contient_pas_ne_sont_pas_nommes_dans_la_version_etudiante(etudiant, va):
    """M23 à M25 existent dans le fichier HydroDyn mais pas dans le tableau du document OC5 : la version étudiante ne les nomme pas."""
    wb = openpyxl.load_workbook(etudiant)
    lignes = {r[0].value: r for r in wb["Membres"].iter_rows(min_row=2)}
    for m in ("M23", "M24", "M25"):
        assert lignes[m][1].value in (None, ""), f"{m} est nommé dans la version étudiante"
    sortie = _lancer(etudiant).stdout
    for i in (23, 24, 25):
        assert f"Membre M{i} (sans nom) : manquant" in sortie
    assert "cap" not in sortie.lower()
