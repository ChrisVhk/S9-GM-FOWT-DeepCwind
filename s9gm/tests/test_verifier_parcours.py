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
