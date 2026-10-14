"""Les contrôles de structure du dépôt (scripts/verifier_parcours.py) voient chacun une faute plantée.

Un contrôle qui ne sait pas échouer ne prouve rien : l'autotest du script plante une faute par contrôle (lien cassé,
ancien chemin, titre manquant, séance non citée, collision de fichier d'étudiant) et exige que le contrôle la voie, sans
fausse alerte sur le cas sain."""
import importlib.util
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("verifier_parcours", RACINE / "scripts" / "verifier_parcours.py")
vp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vp)


def test_autotest_du_script(capsys):
    assert vp.autotest() == 0, capsys.readouterr().out


def test_les_six_titres_du_format_commun_sont_ceux_de_la_consigne():
    assert vp.TITRES == ["Objectif", "Avant de commencer", "À faire, étape par étape", "Post-traiter",
                         "Ce qu'on rend", "Théorie à lire"]


def test_le_depot_courant_n_a_aucun_lien_relatif_casse():
    assert vp.liens(RACINE) == []
    assert vp.liens.verifies > 0   # un « 0 écart » sur 0 lien ne prouverait rien


# ---- R-8 étendu : les six phases ----------------------------------------------------------------------------------------
def test_r8_couvre_les_six_phases():
    assert vp.PHASES_COMPLETES == tuple(f"seances/phase{i}/README.md" for i in range(1, 7))
    assert vp.completer(RACINE) == []


# ---- R-9 : aucune référence à un registre interne ni aux coulisses dans le public -----------------------------------------
def _depot(tmp_path, fichiers):
    return vp._depot_jouet(tmp_path / "r9", fichiers)


def test_r9_voit_un_numero_de_registre_un_chemin_de_coulisses_et_le_nom_du_depot_prive(tmp_path):
    for i, texte in enumerate(("voir E-164 (c)\n", "dossier _Coulisses" "-depots-publics/x\n", "dans coulisses/ à part\n", "ENSM-Enseignement\n", "voir _Reserve/S9/CRITERE.md\n", "du dépôt d'enseignement\n")):
        d = vp._depot_jouet(tmp_path / f"v{i}", {"s9gm/a.py": "# " + texte})
        assert vp.registre(d), texte


def test_r9_ne_crie_pas_au_loup_sur_les_flottants_les_hexadecimaux_et_le_texte_neutre(tmp_path):
    d = _depot(tmp_path, {"data/x.dat": "1.2E-05 3E-100 -4.5E-10\n", "s9gm/a.py": "# les « coulisses » du cours : mot ordinaire\nx = 'ARE-123'\n"})
    assert vp.registre(d) == []


def test_r9_exempte_les_fichiers_listes_et_dit_pourquoi(tmp_path):
    d = _depot(tmp_path, {"LICENSE": "ENSM-Enseignement\n", "PROVENANCE.md": "E-123\n", "CHANGELOG.md": "E-124\n"})
    assert vp.registre(d) == []
    assert all(isinstance(v, str) and len(v) > 15 for v in vp.EXCEPTIONS_REGISTRE.values())   # chaque exception est justifiée


def test_r9_le_depot_courant_est_propre():
    assert vp.registre(RACINE) == []
