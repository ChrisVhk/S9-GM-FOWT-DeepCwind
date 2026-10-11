"""Falsificateurs de `s9gm.cas` pour ElastoDyn (AN-quater) : une condition initiale (`RotSpeed`) écrite
dans une COPIE ElastoDyn propre au cas, jamais dans le fichier partagé du tutoriel.

Écrits avant le code. Le strict nécessaire : le préfixe de colonne `elastodyn.Clé`, comme `seastate.Clé`."""
import hashlib
import re
from pathlib import Path

import pytest

from s9gm import cas

from .conftest import MODELE

ED = MODELE / "config_elastodyn.dat"
CLES_FICHIERS = ("BldFile(1)", "BldFile(2)", "BldFile(3)", "TwrFile")   # chemins relatifs réécrits


def _sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _cle(ligne):
    m = re.match(r'^\s*("[^"]*"|\S+)\s+(\S+)', ligne)
    return m[2] if m else None


@pytest.fixture
def cas_ed(tmp_path):
    avant = _sha(ED)
    d = cas.generer_cas({"cas": "ED1", "elastodyn.RotSpeed": "12.1"}, MODELE, tmp_path, executer_turbsim=False)
    return d, avant


def test_elastodyn_copie_propre_au_cas_seule_la_cle_demandee_et_les_chemins_changent(cas_ed):
    d, _ = cas_ed
    local = d / "config_elastodyn.dat"
    assert local.is_file(), "copie ElastoDyn locale au cas"
    a = ED.read_text(encoding="utf-8").split("\n")
    b = local.read_text(encoding="utf-8").split("\n")
    assert len(a) == len(b)
    diff = [_cle(y) for x, y in zip(a, b) if x != y]
    assert "RotSpeed" in diff
    assert set(diff) <= {"RotSpeed", *CLES_FICHIERS}, f"lignes modifiées inattendues : {diff}"
    f = cas.FASTInputFile(str(local))
    assert float(f["RotSpeed"]) == 12.1


def test_elastodyn_le_fichier_partage_du_tutoriel_n_est_pas_modifie(cas_ed):
    d, avant = cas_ed
    assert _sha(ED) == avant
    assert "RotSpeed" in ED.read_text(encoding="utf-8")
    assert float(cas.FASTInputFile(str(ED))["RotSpeed"]) == 0.0, "le modèle partagé démarre rotor à l'arrêt"


def test_elastodyn_le_main_fst_pointe_la_copie_locale_et_les_fichiers_internes_se_resolvent(cas_ed):
    d, _ = cas_ed
    f = cas.FASTInputFile(str(d / "main.fst"))
    assert str(f["EDFile"]).strip('"') == "config_elastodyn.dat"
    ed = cas.FASTInputFile(str(d / "config_elastodyn.dat"))
    for cle in CLES_FICHIERS:
        chemin = d / str(ed[cle]).strip('"')   # relatif au dossier de la copie
        assert chemin.is_file(), f"{cle} : {chemin} introuvable depuis la copie locale"
        assert chemin.resolve().parent == MODELE.resolve()


def test_elastodyn_journal_et_pas_de_copie_sans_colonne(tmp_path, cas_ed):
    d, _ = cas_ed
    import json
    j = json.loads((d / "journal_cas.json").read_text(encoding="utf-8"))
    assert {"fichier": "config_elastodyn.dat", "cle": "RotSpeed", "avant": "0", "apres": "12.1"} in j["modifications"]
    d2 = cas.generer_cas({"cas": "SANS"}, MODELE, tmp_path, executer_turbsim=False)
    assert not (d2 / "config_elastodyn.dat").exists()
    assert "../" in str(cas.FASTInputFile(str(d2 / "main.fst"))["EDFile"])   # comme avant : le modèle partagé


def test_elastodyn_colonne_acceptee_par_la_lct(tmp_path):
    p = tmp_path / "lct.csv"
    p.write_text("cas,elastodyn.RotSpeed\nA,12.1\n", encoding="utf-8")
    assert cas.lire_lct(p)[0]["elastodyn.RotSpeed"] == "12.1"


def test_elastodyn_cle_inconnue_refusee(tmp_path):
    with pytest.raises(KeyError, match="CleQuiNExistePas"):
        cas.generer_cas({"cas": "BAD", "elastodyn.CleQuiNExistePas": "1"}, MODELE, tmp_path, executer_turbsim=False)
