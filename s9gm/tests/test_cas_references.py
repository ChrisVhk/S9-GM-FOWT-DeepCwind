"""Falsificateurs des cas de référence E01, E02 (échauffement, modèle fixe) et D00, D01, D02 (flottant, `modeles/flottant/`).

1. Chaque dossier de `cas/` est, fichier pour fichier, ce que `s9gm.cas` fabrique depuis la table de cas versionnée
   (`cas/lct_echauffement.csv`, `cas/lct_flottant.csv`) : on ne peut pas modifier un cas à la main sans que ce test le voie.
2. Le contenu physique de chaque cas est celui du tableau de la consigne (vent, houle, modules actifs), lu dans les fichiers.
3. Les cas tournent (OpenFAST) : E01 en entier, D00 sur quelques secondes (le calcul complet dure plusieurs minutes).
D03 à D05 ne sont pas des cas de référence (leurs champs de vent dépendent de choix de l'étudiant) : on teste leur fabrication."""
import hashlib
import shutil
import subprocess
import uuid

import pytest
from openfast_toolbox.io import FASTInputFile

from s9gm import cas

from .conftest import CAS, MODELES, RACINE, requiert_openfast

LCT_E = CAS / "lct_echauffement.csv"
LCT_D = CAS / "lct_flottant.csv"
FIXE, FLOTTANT = MODELES / "fixe", MODELES / "flottant"


def _fichiers(dossier):
    return {str(p.relative_to(dossier)): p.read_bytes() for p in sorted(dossier.rglob("*"))
            if p.is_file() and p.name not in ("journal_cas.json",) and not p.name.endswith((".outb", ".log", ".sum", ".yaml"))}


def _regenere(lct, modele, noms, pref, tmp_path):
    """Fabrique les cas de `lct` sous `cas/<pref>_<nom>` (même profondeur que cas/ : mêmes chemins relatifs)."""
    p = tmp_path / "lct.csv"
    lignes = lct.read_text(encoding="utf-8").splitlines()
    p.write_text("\n".join([lignes[0], *[f"{pref}_{l}" for l in lignes[1:]]]) + "\n", encoding="utf-8")
    return cas.generer_serie(p, modele, CAS)


@pytest.mark.parametrize("lct,modele,noms", [(LCT_E, FIXE, ["E01", "E02"]), (LCT_D, FLOTTANT, ["D00", "D01", "D02"])])
def test_les_cas_de_reference_sont_ceux_que_fabrique_s9gm(lct, modele, noms, pref, tmp_path):
    for dossier, nom in zip(_regenere(lct, modele, noms, pref, tmp_path), noms):
        voulu = _fichiers(dossier)
        present = _fichiers(CAS / nom)
        present.pop("Wind/ramp_wind.dat", None)      # rampe copiée à la main depuis F02 (testée à part)
        assert present == voulu, f"{nom} ne correspond plus à sa table de cas"


def test_la_rampe_de_d02_est_celle_de_f02():
    assert (CAS / "D02/Wind/ramp_wind.dat").read_bytes() == (CAS / "F02/Wind/ramp_wind.dat").read_bytes()


def _lire(chemin, cle):
    return FASTInputFile(str(chemin))[cle]


def test_e01_tour_seule_un_seul_module_et_plateforme_bloquee():
    fst = CAS / "E01" / "main.fst"
    assert [_lire(fst, k) for k in ("CompElast", "CompInflow", "CompAero", "CompServo", "CompSeaSt", "CompHydro", "CompSub")] == [1, 0, 0, 0, 0, 0, 0]
    ed = CAS / "E01" / "config_elastodyn.dat"
    assert not any(_lire(ed, k) for k in ("PtfmSgDOF", "PtfmSwDOF", "PtfmHvDOF", "PtfmRDOF", "PtfmPDOF", "PtfmYDOF", "PitchDOF"))
    assert _lire(ed, "TTDspFA") != 0 and _lire(ed, "RotSpeed") == 0     # tour lâchée depuis un déplacement initial


def test_e02_rotor_libre_sans_controleur_en_vent_constant():
    fst = CAS / "E02" / "main.fst"
    assert [_lire(fst, k) for k in ("CompElast", "CompInflow", "CompAero", "CompServo", "CompHydro", "CompSub")] == [1, 1, 2, 0, 0, 0]
    assert _lire(CAS / "E02" / "config_inflow.dat", "WindType") == 1


def test_d00_aucun_vent_houle_reguliere():
    fst = CAS / "D00" / "main.fst"
    assert (_lire(fst, "CompInflow"), _lire(fst, "CompAero"), _lire(fst, "TMax")) == (0, 0, 300)
    sea = CAS / "D00" / "SeaState.dat"
    assert (_lire(sea, "WaveMod"), _lire(sea, "WaveHs"), _lire(sea, "WaveTp")) == (1, 6, 10)


def test_d01_vent_constant_houle_reguliere():
    inflow = CAS / "D01" / "config_inflow.dat"
    assert (_lire(inflow, "WindType"), float(_lire(inflow, "HWindSpeed"))) == (1, 7.5)
    sea = CAS / "D01" / "SeaState.dat"
    assert (_lire(sea, "WaveMod"), _lire(sea, "WaveHs"), _lire(sea, "WaveTp")) == (1, 6, 10)


def test_d02_echelon_lu_dans_la_rampe_houle_reguliere():
    assert _lire(CAS / "D02" / "config_inflow.dat", "WindType") == 2
    assert (_lire(CAS / "D02" / "SeaState.dat", "WaveMod"), _lire(CAS / "D02" / "SeaState.dat", "WaveHs")) == (1, 6)


def test_le_modele_flottant_demarre_au_repos_comme_le_modele_fixe():
    ed = FLOTTANT / "config_elastodyn.dat"
    assert (_lire(ed, "RotSpeed"), _lire(ed, "PtfmSurge"), _lire(ed, "PtfmPitch")) == (0, 0, 0)
    assert _lire(FLOTTANT / "main.fst", "WtrDpth") == 200 and _lire(FLOTTANT / "main.fst", "CompMooring") == 3


def test_d03_a_d05_se_fabriquent_avec_houle_jonswap_et_champs_de_vent_de_l_etudiant(tmp_path, pref):
    """Fabrication sans lancer TurbSim ni OpenFAST. Les deux trous du gabarit (catégorie IEC, graine) sont remplis ici par des
    valeurs d'essai neutres, uniquement pour le test."""
    lct = tmp_path / "lct.csv"
    lct.write_text("cas,fst.TMax,turbsim.URef,turbsim.IECturbc,turbsim.RandSeed1,seastate.WaveMod,seastate.WaveHs,seastate.WaveTp\n"
                   + "".join(f"{pref}_D0{i},300,{u},12,{4240 + i},2,6,10\n" for i, u in ((3, 7.5), (4, 12), (5, 16))), encoding="utf-8")
    dossiers = cas.generer_serie(lct, FLOTTANT, CAS, executer_turbsim=False,
                                 turbsim_inp=RACINE / "seances" / "0b" / "turbsim_gabarit.inp")
    assert len(dossiers) == 3
    for d, u in zip(dossiers, (7.5, 12, 16)):
        assert _lire(d / "SeaState.dat", "WaveMod") == 2 and float(_lire(d / "SeaState.dat", "WaveHs")) == 6
        assert _lire(d / "config_inflow.dat", "WindType") == 3
        assert float(_lire(next((d / "Wind").glob("*.inp")), "URef")) == u


def test_d03_peut_reutiliser_le_champ_de_vent_de_f03(tmp_path, pref):
    """« Mêmes champs que F03-F05 » : un cas D pointe le .bts d'un cas F voisin, par chemin relatif (même dossier de sortie)."""
    lct = tmp_path / "lct.csv"
    lct.write_text(f"cas,fst.TMax,inflow.WindType,inflow.FileName_BTS,seastate.WaveMod,seastate.WaveHs,seastate.WaveTp\n"
                   f"{pref}_D03,300,3,../{pref}_F03/Wind/{pref}_F03.bts,2,6,10\n", encoding="utf-8")
    (d,) = cas.generer_serie(lct, FLOTTANT, CAS, executer_turbsim=False)
    assert _lire(d / "config_inflow.dat", "FileName_BTS").strip('"') == f"../{pref}_F03/Wind/{pref}_F03.bts"


@requiert_openfast
def test_e01_tourne_en_entier():
    r = subprocess.run(["bash", str(CAS / "run_cas.sh"), "E01"], cwd=RACINE, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "OpenFAST terminated normally" in (RACINE / "results" / "E01" / "run.log").read_text(errors="replace")


@pytest.mark.slow
@requiert_openfast
def test_d00_tourne_sur_quelques_secondes():
    nom = f"_pytest_{uuid.uuid4().hex[:8]}"
    dest = RACINE / "results" / nom
    try:
        shutil.copytree(CAS / "D00", dest)
        main = dest / "main.fst"
        main.write_text(main.read_text(encoding="utf-8").replace("        300   TMax", "          4   TMax"), encoding="utf-8")
        r = subprocess.run(["bash", str(CAS / "run_cas.sh"), f"results/{nom}"], cwd=RACINE, capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr
        assert "OpenFAST terminated normally" in (dest / "run.log").read_text(errors="replace")
    finally:
        shutil.rmtree(dest, ignore_errors=True)
