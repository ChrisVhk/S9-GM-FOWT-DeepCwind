"""Falsificateurs du classeur d'architecture du flotteur (séance 0b, point 7) et de `scripts/verifier_architecture.py`.

Écrits AVANT le classeur et AVANT le script (les tests échouent tant qu'ils n'existent pas).

Le classeur a deux versions : la version COMPLÈTE (en coulisses, chaque valeur sourcée) et la version ÉTUDIANTE (publique,
`seances/0b/DeepCwind_ARCHITECTURE.xlsx`, colonne centrale résolue en exemple, le reste « à remplir »). Le contrôle compare un
classeur rempli, membre par membre, au fichier HydroDyn de `modeles/flottant` (les 25 membres du fichier).

- A-1 : la version complète passe le contrôle à 100 %.
- A-2 : une copie altérée sur 3 cellules donne exactement 3 écarts, nommés.
- A-3 : la version étudiante vide donne « manquant » partout, sauf pour la colonne centrale.
- A-4 : aucune cellule de la version étudiante, hors exemple et hors `Donnees`, ne contient de nombre égal à une valeur de la
  version complète.

La version complète n'est pas dans le dépôt public : A-1 et A-4 sur le VRAI fichier se lancent avec
`S9GM_ARCHITECTURE_COMPLET=<chemin du classeur complet>` (sinon ils sont ignorés). A-1 et A-2 sont aussi éprouvés sur un classeur
complet FABRIQUÉ ICI à partir du fichier HydroDyn : ils prouvent le contrôle, sans dépendre des coulisses.
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


def _hydrodyn_brut():
    """Lecture indépendante du fichier HydroDyn (pas celle du script testé) : joints, jeux, membres, coefficients."""
    lignes = HYDRODYN.read_text(encoding="utf-8").splitlines()

    def table(titre, n_champs):
        i = next(k for k, l in enumerate(lignes) if titre in l)
        i += 4                                             # titre, compte, en-tête, unités -> données
        sortie = []
        while len(sortie) < 10_000:
            cols = lignes[i].split("!")[0].split()
            if len(cols) < n_champs or not re.match(r"^-?\d", cols[0]):
                break
            sortie.append((cols, lignes[i].split("!")[1].strip() if "!" in lignes[i] else ""))
            i += 1
        return sortie

    joints = {int(c[0]): tuple(map(float, c[1:4])) for c, _ in table("MEMBER JOINTS", 4)}
    jeux = {int(c[0]): (float(c[1]), float(c[2])) for c, _ in table("CYLINDRICAL MEMBER CROSS-SECTION PROPERTIES", 3)}
    coefs = {int(c[0]): (float(c[1]), float(c[5])) for c, _ in table("MEMBER-BASED CYLINDRICAL-MEMBER HYDRODYNAMIC COEFFICIENTS (model 3)", 6)}
    membres = {}
    for c, nom in table("-------------------- MEMBERS", 8):
        membres[int(c[0])] = dict(j1=int(c[1]), j2=int(c[2]), jeu=int(c[3]), div=float(c[7]), nom=nom)
    return joints, jeux, coefs, membres


def _classeur_complet(chemin):
    """Fabrique, depuis HydroDyn, un classeur COMPLET dans la mise en page des deux versions (aide de test)."""
    joints, jeux, coefs, membres = _hydrodyn_brut()
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Noeuds"
    ws.append(["Noeud", "x (m)", "y (m)", "z (m)"])
    for j in sorted(joints):
        ws.append([f"N{j}", *joints[j]])
    ws = wb.create_sheet("Membres")
    ws.append(["Membre", "Nom", "Groupe", "Noeud 1", "Noeud 2", "Jeu de propriétés", "Discrétisation (m)"])
    for i in sorted(membres):
        m = membres[i]
        ws.append([f"M{i}", m["nom"], GROUPE_DU_MEMBRE[i], f"N{m['j1']}", f"N{m['j2']}", f"P{m['jeu']}", m["div"]])
    ws = wb.create_sheet("Proprietes")
    ws.append(["Jeu", "Diamètre (m)", "Épaisseur (m)"])
    for p in sorted(jeux):
        ws.append([f"P{p}", *jeux[p]])
    ws = wb.create_sheet("Coefficients")
    ws.append(["Groupe", "Cd", "Ca"])
    for g in GROUPES:
        i = next(k for k, v in GROUPE_DU_MEMBRE.items() if v == g)
        ws.append([g, *coefs[i]])
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


def _lancer(classeur):
    return subprocess.run([sys.executable, "-I", str(SCRIPT), str(classeur)], cwd=RACINE, capture_output=True, text=True)


# ---------------------------------------------------------------------------------------- le contrôle lui-même
def test_a1_un_classeur_complet_passe_a_100_pour_cent(tmp_path, va):
    chemin = _classeur_complet(tmp_path / "complet.xlsx")
    r = _lancer(chemin)
    verdicts = _lignes_sorties(r.stdout)
    assert len(verdicts) == 25, r.stdout
    assert all(v[0] == "juste" for v in verdicts.values()), r.stdout
    assert r.returncode == 0


def test_a2_trois_cellules_alterees_donnent_exactement_trois_ecarts_nommes(tmp_path, va):
    chemin = _classeur_complet(tmp_path / "altere.xlsx")
    wb = openpyxl.load_workbook(chemin)
    # trois cellules dont l'effet est limité à UN membre chacune
    ligne_noeud = next(r for r in wb["Noeuds"].iter_rows(min_row=2) if r[0].value == "N36")   # extrémité de la seule entretoise 20
    ligne_noeud[3].value += 0.5                                                                  # z de N36
    ligne_m10 = next(r for r in wb["Membres"].iter_rows(min_row=2) if r[0].value == "M10")
    ligne_m10[6].value = 2.0                                                                     # discrétisation de M10
    ligne_m5 = next(r for r in wb["Membres"].iter_rows(min_row=2) if r[0].value == "M5")
    ligne_m5[5].value = "P4"                                                                     # M5 rattaché au mauvais jeu de propriétés
    wb.save(chemin)
    r = _lancer(chemin)
    v = _lignes_sorties(r.stdout)
    ecarts = {i for i, (s, _) in v.items() if s == "écart"}
    assert ecarts == {20, 10, 5}, r.stdout
    assert all(s == "juste" for i, (s, _) in v.items() if i not in ecarts), r.stdout
    assert "discrétisation" in v[10][1], r.stdout
    assert "jeu" in v[5][1].lower(), r.stdout
    assert "N36" in v[20][1], r.stdout
    assert r.returncode != 0


def test_une_cellule_vide_ou_a_remplir_est_manquante_pas_fausse(tmp_path, va):
    chemin = _classeur_complet(tmp_path / "trou.xlsx")
    wb = openpyxl.load_workbook(chemin)
    next(r for r in wb["Membres"].iter_rows(min_row=2) if r[0].value == "M12")[4].value = A_REMPLIR
    next(r for r in wb["Coefficients"].iter_rows(min_row=2) if r[0].value == GROUPES[3])[1].value = None
    wb.save(chemin)
    v = _lignes_sorties(_lancer(chemin).stdout)
    manquants = {i for i, (s, _) in v.items() if s == "manquant"}
    assert 12 in manquants and set(range(8, 20)) <= manquants     # Cd des pontons vide : tous les pontons manquent
    assert not any(s == "écart" for s, _ in v.values())


def test_le_sens_des_noeuds_compte(tmp_path, va):
    chemin = _classeur_complet(tmp_path / "sens.xlsx")
    wb = openpyxl.load_workbook(chemin)
    ligne = next(r for r in wb["Membres"].iter_rows(min_row=2) if r[0].value == "M2")
    ligne[3].value, ligne[4].value = ligne[4].value, ligne[3].value
    wb.save(chemin)
    v = _lignes_sorties(_lancer(chemin).stdout)
    assert v[2][0] == "écart"


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
    chemin = _classeur_complet(tmp_path / "coef.xlsx")
    wb = openpyxl.load_workbook(chemin)
    ligne = next(r for r in wb["Coefficients"].iter_rows(min_row=2) if r[0].value == GROUPES[1])
    ligne[1].value += 0.1                      # Cd des colonnes déportées
    ligne[2].value = 0.5                       # Ca des colonnes déportées
    wb.save(chemin)
    v = _lignes_sorties(_lancer(chemin).stdout)
    assert {i for i, (s, _) in v.items() if s == "écart"} == {2, 3, 4}
    assert all("Cd" in v[i][1] and "Ca" in v[i][1] for i in (2, 3, 4))
