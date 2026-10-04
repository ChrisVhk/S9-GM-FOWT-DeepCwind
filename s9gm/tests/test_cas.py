"""Falsificateurs de s9gm.cas : un cas généré doit être identique, octet pour octet, à F01 fait à
la main ; une clé absente ou ambiguë doit échouer, pas passer en silence."""
import json
import subprocess

import pytest

from s9gm import cas

from .conftest import PRISE_EN_MAIN, MODELE


def test_fst_et_inflow_identiques_a_F01_fait_main(pref, lct_f01):
    (dossier,) = cas.generer_serie(lct_f01, MODELE, PRISE_EN_MAIN)
    for nom in ("main.fst", "config_inflow.dat"):
        genere = (dossier / nom).read_bytes()
        main = (PRISE_EN_MAIN / "F01" / nom).read_bytes()
        assert genere == main, f"{nom} généré diffère de F01/{nom} fait à la main"


def test_journal_des_parametres(pref, lct_f01):
    (dossier,) = cas.generer_serie(lct_f01, MODELE, PRISE_EN_MAIN)
    j = json.loads((dossier / "journal_cas.json").read_text(encoding="utf-8"))
    mods = {(m["cle"]): (m["avant"], m["apres"]) for m in j["modifications"]}
    assert mods["TMax"] == ("600", "200")
    assert mods["HWindSpeed"] == ("8", "7.5")
    assert j["modele"] == "../modele_fixe"


def test_modele_partage_non_modifie(pref, lct_f01):
    avant = (MODELE / "main.fst").read_bytes()
    cas.generer_serie(lct_f01, MODELE, PRISE_EN_MAIN)
    assert (MODELE / "main.fst").read_bytes() == avant


def test_cle_inconnue_echoue(pref):
    l = {"cas": pref + "_X", "fst.PasUneCle": "1"}
    with pytest.raises(KeyError, match="PasUneCle"):
        cas.generer_cas(l, MODELE, PRISE_EN_MAIN)


def test_prefixe_de_colonne_invalide(tmp_path):
    p = tmp_path / "lct.csv"
    p.write_text("cas,elastodyn.Foo\nX,1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="préfixe"):
        cas.lire_lct(p)


def test_cas_en_double(tmp_path):
    p = tmp_path / "lct.csv"
    p.write_text("cas,fst.TMax\nX,1\nX,2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="double"):
        cas.lire_lct(p)


def test_separateur_point_virgule(tmp_path):
    p = tmp_path / "lct.csv"
    p.write_text("cas;fst.TMax\nX;50\n", encoding="utf-8")
    assert cas.lire_lct(p) == [{"cas": "X", "fst.TMax": "50"}]


def test_remplacer_valeur_exige_une_seule_occurrence():
    with pytest.raises(KeyError):
        cas.remplacer_valeur(["1  A", "2  A"], "A", "3")


def test_champ_texte_garde_ses_guillemets():
    lignes = ['"unused"      FileName_BTS   - Name of the Full field wind file (.bts)']
    cas.remplacer_valeur(lignes, "FileName_BTS", "Wind/F03.bts")
    assert lignes[0].startswith('"Wind/F03.bts"      FileName_BTS')


def test_regenerer_un_cas_supprime_ses_anciennes_sorties(pref):
    d = cas.generer_cas({"cas": pref + "_Z", "fst.TMax": "5"}, MODELE, PRISE_EN_MAIN)
    (d / "main.outb").write_bytes(b"x")
    (d / "run.log").write_text("OpenFAST terminated normally", encoding="utf-8")
    cas.generer_cas({"cas": pref + "_Z", "fst.TMax": "6"}, MODELE, PRISE_EN_MAIN)
    assert not (d / "main.outb").exists() and not (d / "run.log").exists()


# ---- TurbSim branché dans `cas` --------------------------------------------------
import re
import shutil

TURBSIM_INP = (RACINE_TESTS := __import__("pathlib").Path(__file__).resolve().parents[2]) \
    / "tutorials" / "lheea" / "05_FOWT" / "1_Configuration" / "Wind" / "turb12mps.inp"
# grille minuscule : l'essai vérifie la chaîne, pas la turbulence
PETITE_GRILLE = {"NumGrid_Z": "5", "NumGrid_Y": "5", "TimeStep": "0.5", "AnalysisTime": "30",
                 "UsableTime": "20"}
requiert_turbsim = pytest.mark.skipif(shutil.which("turbsim") is None,
                                      reason="turbsim absent du PATH (environnement s9gm-fowt)")


@pytest.fixture
def modele_turbsim(pref):
    """Copie de modele_fixe/ (sœur, même profondeur : les chemins relatifs restent valables) + turbsim.inp."""
    m = PRISE_EN_MAIN / f"{pref}_modele"
    shutil.copytree(MODELE, m)
    shutil.copy(TURBSIM_INP, m / "turbsim.inp")
    return m


def _lct_turbsim(tmp_path, pref, graine="4242", uref="9"):
    cols = {f"turbsim.{k}": v for k, v in PETITE_GRILLE.items()}
    cols |= {"turbsim.RandSeed1": graine, "turbsim.URef": uref}
    p = tmp_path / "lct_ts.csv"
    p.write_text("cas,fst.TMax," + ",".join(cols) + f"\n{pref}_F03,20," + ",".join(cols.values()) + "\n",
                 encoding="utf-8")
    return p


def test_turbsim_entree_identique_a_celle_faite_a_la_main(tmp_path, pref, modele_turbsim):
    """Falsificateur 1 : le .inp écrit par `cas` est, octet pour octet, le modèle dont on a changé à la
    main les seules lignes demandées. Pas besoin de TurbSim : `executer_turbsim=False`."""
    (dossier,) = cas.generer_serie(_lct_turbsim(tmp_path, pref), modele_turbsim, PRISE_EN_MAIN,
                                   executer_turbsim=False)
    lignes = (modele_turbsim / "turbsim.inp").read_text(encoding="utf-8").split("\n")
    voulu = dict(PETITE_GRILLE, RandSeed1="4242", URef="9")
    main = []
    for l in lignes:
        for cle, val in voulu.items():
            m = cas._motif_cle(cle).match(l)
            if m:
                l = m["pre"] + val + m["mid"] + m["cle"] + m["reste"]
        main.append(l)
    assert (dossier / "Wind" / f"{pref}_F03.inp").read_bytes() == "\n".join(main).encode("utf-8")
    j = json.loads((dossier / "journal_cas.json").read_text(encoding="utf-8"))
    assert j["turbsim"]["bts"] is None and j["turbsim"]["parametres"]["RandSeed1"] == "4242"


def test_turbsim_pointe_le_vent_du_cas(tmp_path, pref, modele_turbsim):
    (dossier,) = cas.generer_serie(_lct_turbsim(tmp_path, pref), modele_turbsim, PRISE_EN_MAIN,
                                   executer_turbsim=False)
    inflow = (dossier / "config_inflow.dat").read_text(encoding="utf-8")
    assert f'"Wind/{pref}_F03.bts"' in inflow
    assert any(l.split()[:2] == ["3", "WindType"] for l in inflow.splitlines())


@requiert_turbsim
def test_turbsim_meme_graine_meme_champ_que_a_la_main(tmp_path, pref, modele_turbsim):
    """Falsificateur 2 : même graine → même .bts qu'un TurbSim lancé à la main sur le même .inp ;
    une autre graine donne un autre champ."""
    lct = _lct_turbsim(tmp_path, pref)
    (dossier,) = cas.generer_serie(lct, modele_turbsim, PRISE_EN_MAIN)
    genere = (dossier / "Wind" / f"{pref}_F03.bts").read_bytes()
    main = tmp_path / "main"
    main.mkdir()
    shutil.copy(dossier / "Wind" / f"{pref}_F03.inp", main / "x.inp")
    subprocess.run(["turbsim", "x.inp"], cwd=main, check=True, capture_output=True)
    assert (main / "x.bts").read_bytes() == genere
    (autre,) = cas.generer_serie(_lct_turbsim(tmp_path, pref, graine="999"), modele_turbsim, PRISE_EN_MAIN)
    assert (autre / "Wind" / f"{pref}_F03.bts").read_bytes() != genere


def test_turbsim_sans_modele_echoue(tmp_path, pref):
    cols = "turbsim.RandSeed1\n"
    p = tmp_path / "lct.csv"
    p.write_text(f"cas,{cols}{pref}_F03,1\n", encoding="utf-8")
    with pytest.raises(FileNotFoundError, match="turbsim.inp"):
        cas.generer_serie(p, MODELE, PRISE_EN_MAIN, executer_turbsim=False)


# ---- gabarit à trous seances/0b/turbsim_gabarit.inp (LOT A2) --------------------------------------
GABARIT = (RACINE_TESTS / "seances" / "0b" / "turbsim_gabarit.inp")
TROUS = {"URef": "9", "IECturbc": '"B"', "RandSeed1": "4242"}


@pytest.fixture
def modele_gabarit(pref):
    m = PRISE_EN_MAIN / f"{pref}_modele"
    shutil.copytree(MODELE, m)
    shutil.copy(GABARIT, m / "turbsim.inp")
    return m


def _lct_gabarit(tmp_path, pref, trous):
    cols = {f"turbsim.{k}": v for k, v in PETITE_GRILLE.items()} | {f"turbsim.{k}": v for k, v in trous.items()}
    p = tmp_path / "lct_g.csv"
    p.write_text("cas,fst.TMax," + ",".join(f'"{c}"' for c in cols) + f"\n{pref}_G,20," +
                 ",".join('"' + v.replace('"', '""') + '"' for v in cols.values()) + "\n", encoding="utf-8")
    return p


def test_gabarit_non_rempli_refuse_et_nomme_les_champs(tmp_path, pref, modele_gabarit):
    """Falsificateur : aucun trou rempli -> refus, et le message nomme chaque champ manquant."""
    p = _lct_gabarit(tmp_path, pref, {"URef": "9"})  # IECturbc et RandSeed1 restent à compléter
    with pytest.raises(ValueError, match=r"RandSeed1, IECturbc"):
        cas.generer_serie(p, modele_gabarit, PRISE_EN_MAIN, executer_turbsim=False)


def test_gabarit_les_trous_sont_exactement_trois():
    import re
    trous = [m[1] for l in GABARIT.read_text(encoding="utf-8").split("\n") if (m := re.match(r"^\s*A_COMPLETER\s+(\w+)", l))]
    assert sorted(trous) == sorted(TROUS)


@requiert_turbsim
def test_gabarit_rempli_a_la_main_meme_champ_que_via_cas(tmp_path, pref, modele_gabarit):
    """Falsificateur : le gabarit rempli À LA MAIN (éditeur de texte) donne, par TurbSim, le même .bts
    que le même gabarit rempli par les colonnes turbsim.* de la LCT et lancé par `cas`."""
    (dossier,) = cas.generer_serie(_lct_gabarit(tmp_path, pref, TROUS), modele_gabarit, PRISE_EN_MAIN)
    genere = (dossier / "Wind" / f"{pref}_G.bts").read_bytes()
    texte = GABARIT.read_text(encoding="utf-8")
    for k, v in (PETITE_GRILLE | TROUS).items():
        texte = re.sub(rf"^(\s*)(A_COMPLETER|\S+)(\s+){k}(\s)", lambda m: f"{m[1]}{v}{m[3]}{k}{m[4]}", texte, flags=re.M)
    main = tmp_path / "main"
    main.mkdir()
    (main / "x.inp").write_text(texte, encoding="utf-8")
    subprocess.run(["turbsim", "x.inp"], cwd=main, check=True, capture_output=True)
    assert (main / "x.bts").read_bytes() == genere
