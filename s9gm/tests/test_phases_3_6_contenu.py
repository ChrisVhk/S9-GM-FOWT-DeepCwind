"""Falsificateurs de contenu des consignes des phases 3 à 6 (`seances/phase3` à `phase6`). Écrits AVANT les consignes.

Quatre familles :
1. Les trous restent des trous : aucune consigne ne contient le corps d'une fonction à trous de `s9gm.fatigue`, `s9gm.ancrage` ou
   `s9gm.structure`, ni une valeur de courbe S-N. Les consignes disent COMMENT compléter, tester (xfail -> réussi) puis appliquer.
2. Rien d'écrit par l'étudiant n'est suivi par git : tout vit sous `results/` ou `rendus/` (le squelette se copie sous `results/`).
3. Ce que l'énoncé ne fixe pas n'est pas décidé : aucune valeur de choix dans les commandes (exposant, DFF, courbe, période de retour).
4. Les renvois et les limites sont dits : atelier tour (renvoi seulement), niveau C sous réserve, D01 point commun de la phase 6.
Le rejeu des commandes depuis un clone neuf est dans `test_phases_3_6_rejeu.py` (opt-in : long)."""
import re

import pytest

from . import parcours
from .conftest import RACINE

PHASES = {n: RACINE / "seances" / f"phase{n}" / "README.md" for n in (3, 4, 5, 6)}
TROUS = {3: ("rainflow", "miner", "del_court_terme", "del_long_terme"),
         4: ("catenaire_elastique", "raideur_horizontale"),
         5: ("von_mises", "verifier_domaine_efthymiou", "scf_ty_axial_encastre", "scf_ty_flexion_plan", "scf_ty_flexion_hors_plan")}
VARIABLE = {3: "S9GM_FATIGUE_COMPLET", 4: "S9GM_ANCRAGE_COMPLET", 5: "S9GM_STRUCTURE_COMPLET"}


def texte(n):
    assert PHASES[n].is_file()
    return PHASES[n].read_text(encoding="utf-8")


def plat(t):
    return re.sub(r"\s+", " ", t.replace("**", ""))


def code(n):
    return "\n".join(c for _, c in parcours.blocs(texte(n)))


# ---- 1. les squelettes ne sont jamais dévoilés ------------------------------------------------------------------
@pytest.mark.parametrize("n", sorted(TROUS))
def test_aucune_fonction_a_trous_n_est_definie_ni_resolue_dans_la_consigne(n):
    c = code(n)
    for nom in TROUS[n]:
        assert not re.search(rf"def\s+{nom}\b", c), f"{nom} est défini dans une commande de la phase {n}"
    assert not re.search(r"\*\*\s*\(\s*1(?:\.0)?\s*/\s*m\s*\)", c), "formule du DEL écrite dans la consigne"
    assert not re.search(r"log_a[12]?\s*=\s*[-\d]", c), "valeur de courbe S-N écrite dans la consigne"
    assert not re.search(r"\bm[12]\s*=\s*\d", c), "pente de courbe S-N écrite dans la consigne"
    assert not re.search(r"np\.(?:sqrt|hypot)\(\s*sx", c), "Von Mises écrit dans la consigne"
    assert not re.search(r"raise\s+NotImplementedError", c)


@pytest.mark.parametrize("n", sorted(TROUS))
def test_la_consigne_dit_comment_completer_tester_puis_appliquer(n):
    t = texte(n)
    assert VARIABLE[n] in t and "results/mon_s9gm" in t                       # copie locale du squelette, test pointé dessus
    assert re.search(r"xfail", t, re.I) and re.search(r"passed|réussi", t, re.I)    # ce qu'on doit voir avant et après
    for nom in TROUS[n]:
        assert nom in t, f"{nom} non nommé dans la phase {n}"
    c = code(n)
    assert "shutil.copy" in c and "results/mon_s9gm" in c and "pytest" in c


@pytest.mark.parametrize("n", sorted(TROUS))
def test_le_squelette_public_n_est_pas_modifie_par_la_consigne(n):
    c = code(n)
    for ecriture in (r"open\(\s*[\"']s9gm/", r"write_text\(", r">\s*s9gm/", r"sed\s+-i\s+\S*\s*s9gm/"):
        for m in re.finditer(ecriture, c):
            assert "s9gm/" not in c[m.start():m.start() + 80] or "results/" in c[m.start():m.start() + 80], c[m.start():m.start() + 80]


# ---- 3. aucune valeur de choix dans les commandes -----------------------------------------------------------------
@pytest.mark.parametrize("n", sorted(PHASES))
def test_aucune_valeur_de_choix_n_est_ecrite_dans_les_commandes(n):
    c = code(n)
    assert not re.search(r"\bDFF\s*=\s*\d", c, re.I), "DFF écrit en dur"
    assert not re.search(r"\b(?:rho|masse_volumique)\w*\s*=\s*\d", c), "masse volumique écrite en dur"
    assert not re.search(r"\bperiode_retour\w*\s*=\s*[\"']?\d", c, re.I), "période de retour écrite en dur"
    assert not re.search(r"\bexposant_m\w*\s*=\s*\d|\bm_[a-z]+\s*=\s*\d", c), "exposant m écrit en dur"
    assert not re.search(r"RandSeed1[^\n]*\d{2,}|IECturbc\s*=\s*[\"']?(?:[ABC]|\d)", c)


@pytest.mark.parametrize("n", sorted(PHASES))
def test_aucune_commande_ne_modifie_un_fichier_suivi(n):
    c = code(n)
    for m in re.finditer(r"(?:to_csv|savefig|write_text|open)\(\s*f?[\"']([^\"']+)", c):
        chemin = m.group(1)
        assert chemin.startswith(("results/", "rendus/")) or not re.match(r"^[\w./-]+\.(?:csv|png|md|dat|fst|txt|json|xlsx)$", chemin), chemin


# ---- phase 3 -----------------------------------------------------------------------------------------------------------
def test_phase_3_etapes_de_l_enonce_et_renvoi_a_l_atelier():
    t = plat(texte(3))
    assert "seances/atelier_tour/" in texte(3) or "../atelier_tour/" in texte(3)
    for mot in ("rainflow", "TwrBsMyt", "FAIRTEN", "SCF = 2", "Miner", "DEL court terme", "DEL long terme", "DNV-RP-C203"):
        assert mot in t, mot
    assert "Long term DEL" in t                                                    # export au format du classeur (vérification à la main)
    assert "tolérance" in t.lower()                                                # nommée : l'étudiant dit à quelle précision les deux concordent
    c = code(3)
    assert "equivalent_load" in c                                                  # comparaison à l'outil d'openfast_toolbox (point 5)
    assert "<votre DFF>" in c and "<votre exposant m>" in c


def test_phase_3_point_7_confronte_a_un_del_de_reference_calcule_sur_les_classes_floatech_sans_valeur_dans_le_public():
    """Le DEL de référence est calculé sur les 251 classes de la feuille DLC12 (Papi et al., § 2.3.2) et communiqué en séance :
    la consigne le dit, ne contient aucune valeur de DEL, et ne parle ni de « 50 ans simulés » ni de simulations FLOATECH."""
    t = plat(texte(3))
    i = t.index("Point 7")
    pt7 = t[i:i + 2500]
    for mot in ("251 classes", "DLC12", "communiqué en séance", "binning", "lumping"):
        assert mot in pt7, mot
    assert not (RACINE / "data" / "del_reference_50ans.csv").exists()
    assert not re.search(r"\d+[.,]?\d*\s*(?:MPa|kN)", pt7), "valeur de DEL écrite"


def test_la_reference_de_50_ans_simules_n_existe_plus_nulle_part_dans_le_public():
    """Garde : la « référence de 50 ans » était une erreur (50 ans est la période de retour des états SSS et ESS, pas une durée simulée)."""
    import subprocess
    r = subprocess.run(["git", "grep", "-n", "-i", "-e", "450 000", "-e", "50 ans d'états", "-e", "référence fournie", "-e", "référence de 50 ans",
                        "--", ".", ":!s9gm/tests/test_phases_3_6_contenu.py"], cwd=RACINE, capture_output=True, text=True)
    assert r.stdout == "", r.stdout


@pytest.mark.parametrize("n,mots", [
    (3, ("DFF", "durée de service", "DNV", "justifiez")),
    (4, ("charge de rupture", "coefficient de sécurité", "norme", "justifiez")),
])
def test_dff_duree_de_service_charge_de_rupture_sont_des_parametres_a_justifier_avec_la_norme(n, mots):
    t = plat(texte(n))
    for mot in mots:
        assert mot in t, mot
    assert "il vous est donné en séance" not in t and "Vous la recevez de l'enseignant" not in t
    assert not re.search(r"\b(?:DFF|coefficient de sécurité)\s*(?:=|vaut|de)\s*\d", t)


def test_phase_5_niveau_d_cite_le_memoire_sans_le_redistribuer():
    t = plat(texte(5))
    assert "Fredheim" in t and "NTNU" in t and "2012" in t
    assert "https://hdl.handle.net/11250/238200" in t
    assert "redistribu" in t.lower()
    assert not list((RACINE / "annexes" / "papers").glob("*redheim*"))


def test_phase_6_l_echange_se_fait_par_depot_sur_vega_sous_un_nom_impose():
    t = plat(texte(6))
    assert "Vega" in t and "synthese_<groupe>.csv" in t
    assert "ne fixe pas comment" not in t


# ---- phase 4 -----------------------------------------------------------------------------------------------------------
def test_phase_4_correspondance_map_moordyn_est_ecrite_et_n_est_plus_a_etablir():
    t = plat(texte(4))
    assert re.search(r"T\[1\].{0,40}FAIRTEN1", t) and re.search(r"T\[2\].{0,40}FAIRTEN2", t) and re.search(r"T\[3\].{0,40}FAIRTEN3", t)
    assert "à établir" not in t.lower()
    assert "repeat 240 120" in t                                                   # la cause : le fichier MAP ne décrit qu'une ligne


def test_phase_4_charge_de_rupture_n_est_pas_inventee():
    t = plat(texte(4))
    assert "charge de rupture" in t.lower()
    assert not re.search(r"(?:MBL|charge de rupture)[^.]{0,60}\d[\d ,.]*\s*(?:kN|MN|N)\b", t, re.I), "valeur de charge de rupture écrite"
    assert re.search(r"pas (?:dans ce dépôt|fournie|donnée)|non (?:fournie|donnée)", t, re.I)


def test_phase_4_cas_extremes_ecrits_par_l_etudiant_pas_fixes():
    t = plat(texte(4))
    for mot in ("DLC 6.1", "DLC 1.6", "période de retour", "rotor à l'arrêt", "IEC_WindType"):
        assert mot in t, mot
    c = code(4)
    assert "<votre classe de la machine>" in c and "<votre catégorie (lettre)>" in c            # la classe et la catégorie sont ceux de l'étudiant
    assert "results/extremes_phase1.csv" in c                                                  # période de retour et classes de vent : déjà choisies en phase 1


# ---- phase 5 -----------------------------------------------------------------------------------------------------------
def test_phase_5_niveau_c_sous_reserve_et_sans_commande():
    t = plat(texte(5))
    assert re.search(r"sous réserve de faisabilité", t)
    c = code(5)
    assert "SubDyn" not in c and "subdyn" not in c.lower()


def test_phase_5_domaine_de_validite_avant_usage_et_renvois():
    t = plat(texte(5))
    for mot in ("β", "domaine de validité", "HorsDomaineError", "classeur d'architecture", "atelier"):
        assert mot in t, mot
    assert "seances/0b" in texte(5) or "../0b/" in texte(5)


# ---- phase 6 -----------------------------------------------------------------------------------------------------------
def test_phase_6_d01_point_commun_et_sensibilite_depuis_la_lct_du_groupe():
    t = plat(texte(6))
    assert "D01" in t and "point commun" in t
    assert re.search(r"LCT (?:de votre|de chaque|du) groupe", t)
    c = code(6)
    assert "lire." in c and "visu." in c
    assert "results/D01" in c or '"D01"' in c


def test_phase_6_question_finale_et_soutenance_conservees():
    t = plat(texte(6))
    assert "quelles études de sensibilité demanderiez-vous au bureau d'études" in t
    assert "15 min" in t and "10 min" in t
