"""Rejeu des commandes des phases 3 à 6, dans l'ordre, comme un étudiant (opt-in : TurbSim et OpenFAST, plus d'une heure).

Principe (même banc que les phases 1 et 2, `parcours.py`) :
- un CLONE NEUF du dépôt (ou `S9GM_PARCOURS_DEPOT=<dépôt>` pour mettre au point), la phase 1 rejouée pour obtenir la LCT ;
- les choix de l'étudiant sont remplacés par des valeurs d'essai NEUTRES définies ici, jamais dans les consignes ;
- les squelettes (`fatigue`, `ancrage`, `structure`) : le test rejoue d'abord le bloc qui COPIE le squelette sous `results/mon_s9gm/`,
  vérifie que les tests de la consigne donnent des `xfailed`, puis dépose dans cette copie la version complète de l'enseignant
  (dossier donné par `S9GM_SOLUTIONS_ENSEIGNANT=<dossier>`, test ignoré sans lui) et rejoue le reste. La version complète ne touche
  jamais un fichier suivi du dépôt : elle n'existe que dans `results/` du clone.
Les temps mesurés sont écrits dans `results/parcours_phases_3_6_temps.json` du dépôt rejoué."""
import json
import os
import shutil
from pathlib import Path

import pytest

from . import parcours
from .conftest import RACINE, requiert_openfast
from .test_phase1_parcours import ESSAI as ESSAI_PHASE1

REJEU = pytest.mark.skipif(
    not (os.environ.get("S9GM_PARCOURS_REJEU") or os.environ.get("S9GM_PARCOURS_DEPOT")),
    reason="rejeu long : S9GM_PARCOURS_REJEU=1, ou S9GM_PARCOURS_DEPOT=<dépôt>")
SOLUTIONS = os.environ.get("S9GM_SOLUTIONS_ENSEIGNANT")
AVEC_SOLUTIONS = pytest.mark.skipif(not SOLUTIONS, reason="versions complètes de l'enseignant : S9GM_SOLUTIONS_ENSEIGNANT=<dossier>")
COMPAGNONS = {"structure.py": ("efthymiou_c203.json",)}       # données lues par la version complète de l'enseignant (bornes de la norme, jamais dans le dépôt)
PHASE = {n: RACINE / "seances" / f"phase{n}" / "README.md" for n in (3, 4, 5, 6)}

# Valeurs d'essai : propres au TEST, choisies pour ne reproduire aucune valeur de norme ni du modèle (le test ne vérifie aucun nombre).
ESSAI = {
    "<votre durée>": "300",
    "<votre nombre de coeurs>": "12",
    "<votre valeur>": "60",
    "<votre épaisseur de paroi (m)>": "0.06",
    "<votre exposant m>": "3.5",
    "<votre exposant m de la ligne>": "3.7",
    "<votre f_eq (Hz)>": "1.0",
    "<votre épaisseur de référence (mm)>": "30",
    "<votre log ā1>": "12.0",
    "<votre pente m1>": "3.0",
    "<votre log ā2>": "14.2",
    "<votre pente m2>": "4.6",
    "<votre nombre de cycles au coude>": "5e6",
    "<votre exposant d'épaisseur k>": "0.1",
    "<votre source S-N (norme, tableau, page)>": "courbe d'école, non DNV",
    "<votre DFF>": "2.5",
    "<votre durée de service (ans)>": "30",
    "<votre fréquence de coupure (Hz)>": "0.2",
}


@pytest.fixture(scope="module")
def depot(tmp_path_factory):
    d = os.environ.get("S9GM_PARCOURS_DEPOT")
    if d:
        return Path(d)
    d = parcours.cloner(RACINE, tmp_path_factory.mktemp("clone36") / "clone")
    code, sortie, _ = parcours.rejouer(RACINE / "seances" / "phase1" / "README.md", d, ESSAI_PHASE1)
    assert code == 0, "la phase 1 doit passer avant les phases 3 à 6 :\n" + sortie[-2000:]
    return d


def _noter(depot, phase, temps):
    f = Path(depot) / "results" / "parcours_phases_3_6_temps.json"
    f.parent.mkdir(exist_ok=True)
    cumul = json.loads(f.read_text(encoding="utf-8")) if f.is_file() else {}
    cumul[f"phase{phase}"] = temps
    f.write_text(json.dumps(cumul, indent=1), encoding="utf-8")
    print(f"TEMPS_PHASE{phase}", json.dumps(temps))


def _avec_squelette(phase, depot, module, essai, apres):
    """Étape 1 (copie du squelette) ; tests sur le squelette (xfailed) ; version complète déposée dans la copie ; tests sur la copie ;
    puis les blocs `apres`. Renvoie les temps."""
    readme = PHASE[phase]
    code, sortie, t1 = parcours.rejouer(readme, depot, essai, etapes=[1])
    assert code == 0, sortie[-2000:]
    code, sortie, _ = parcours.rejouer(readme, depot, essai, etapes=[2])
    assert code == 0 and "xfailed" in sortie.split("== votre copie")[0], "sur le squelette, des tests doivent être xfailed :\n" + sortie[-2000:]
    for fichier in (module, *COMPAGNONS.get(module, ())):
        shutil.copy(Path(SOLUTIONS) / fichier, Path(depot) / "results" / "mon_s9gm" / fichier)
    code, sortie, t2 = parcours.rejouer(readme, depot, essai, etapes=[2])
    copie = sortie.split("== votre copie")[1]
    assert code == 0 and "passed" in copie and "xfailed" not in copie and "failed" not in copie, "sur la copie complétée :\n" + sortie[-2500:]
    code, sortie, t3 = parcours.rejouer(readme, depot, essai, delai=7200, etapes=apres)
    assert code == 0, sortie[-4000:]
    return {**t1, **t2, **t3}, sortie


@pytest.mark.slow
@REJEU
@AVEC_SOLUTIONS
@requiert_openfast
def test_rejeu_phase_3(depot):
    essai = dict(ESSAI)
    # un cas tiré de ce que l'étape 2 a produit : le test ne le connaît qu'après la campagne, donc deux temps
    readme = PHASE[3]
    code, sortie, t1 = parcours.rejouer(readme, depot, essai, etapes=[1])
    assert code == 0, sortie[-2000:]
    code, sortie, _ = parcours.rejouer(readme, depot, essai, etapes=[2])
    assert code == 0 and "xfailed" in sortie.split("== votre copie")[0], "sur le squelette, des tests doivent être xfailed :\n" + sortie[-2000:]
    shutil.copy(Path(SOLUTIONS) / "fatigue.py", Path(depot) / "results" / "mon_s9gm" / "fatigue.py")
    code, sortie, _ = parcours.rejouer(readme, depot, essai, etapes=[2])
    copie = sortie.split("== votre copie")[1]
    assert code == 0 and "passed" in copie and "xfailed" not in copie and "failed" not in copie, "sur la copie complétée :\n" + sortie[-2500:]
    code, sortie, t3 = parcours.rejouer(readme, depot, essai, delai=7200, etapes=[3, 4])
    assert code == 0, sortie[-4000:]
    cas = sorted(p.name for p in (Path(depot) / "results" / "phase3").glob("*/main.outb") for p in [p.parent])
    assert len(cas) >= 2
    essai["<votre cas>"] = cas[len(cas) // 2]
    code, sortie, t5 = parcours.rejouer(readme, depot, essai, delai=3600, etapes=[5, 6, 7])
    assert code == 0, sortie[-4000:]
    res = Path(depot) / "results"
    for f in ("phase3_del_par_cas.csv", "phase3_bilan.csv", "phase3_export_long_terme.csv", "phase3_parametres.json"):
        assert (res / f).is_file(), f
    _noter(depot, 3, {**t1, **t3, **t5})


ESSAI_4 = {
    **ESSAI,
    "<votre graine>": "5000",
    "<votre classe de la machine>": "3",
    "<votre catégorie (lettre)>": "C",
    "<votre colonne de variation>": "seastate.WavePkShp",
    "<votre valeur de variation>": "5.0",
    "<votre charge de rupture (N)>": "1.0e7",              # valeur d'essai du TEST, sans rapport avec la ligne réelle
    "<votre coefficient de sécurité>": "1.5",
}


@pytest.mark.slow
@REJEU
@AVEC_SOLUTIONS
@requiert_openfast
def test_rejeu_phase_4(depot):
    temps, sortie = _avec_squelette(4, depot, "ancrage.py", ESSAI_4, apres=[3, 4, 5, 6])
    assert "{'cavalement': True, 'embardee': True}" in sortie, sortie[-1500:]      # la correspondance MAP++ / MoorDyn
    res = Path(depot) / "results"
    for f in ("lct_phase4.csv", "phase4_uls.csv", "phase4_quasi_statique.csv"):
        assert (res / f).is_file(), f
    assert len(list((res / "phase4").glob("*/main.outb"))) >= 4
    _noter(depot, 4, temps)


ESSAI_5 = {
    **ESSAI_4,
    "<votre épaisseur minimale (m)>": "0.02", "<votre épaisseur maximale (m)>": "0.12", "<votre pas d'épaisseur (m)>": "0.02",
    "<votre limite d'élasticité (MPa)>": "300", "<votre coefficient partiel>": "1.0",
    "<votre épaisseur retenue au pied (m)>": "0.05",
    "<votre masse en tête (kg)>": "300000", "<votre vitesse minimale (rpm)>": "5.0", "<votre vitesse nominale (rpm)>": "10.0",
    "<votre effort d'écartement ΔF (N)>": "1.0e6", "<votre angle φ (°)>": "30", "<votre partage>": "0.5",
    "<votre diamètre d'entretoise (m)>": "1.6", "<votre épaisseur d'entretoise (m)>": "0.03", "<votre contrainte admissible (MPa)>": "200",
    "<votre d (m)>": "6.0", "<votre D (m)>": "12.0", "<votre τ>": "0.5", "<votre γ>": "12", "<votre α>": "8", "<votre θ (°)>": "60",
}


@pytest.mark.slow
@REJEU
@AVEC_SOLUTIONS
@requiert_openfast
def test_rejeu_phase_5(depot):
    res = Path(depot) / "results"
    cas3 = sorted(p.parent.name for p in (res / "phase3").glob("*/main.outb"))
    assert cas3 and (res / "phase4").is_dir(), "les phases 3 et 4 doivent avoir été rejouées dans ce dépôt"
    essai = {**ESSAI_5, "<votre cas de fatigue>": cas3[len(cas3) // 2], "<votre cas ULS>": "X61"}
    # étape 1 (copie, tests), puis blocs 3 à 9 (le bloc 5 relance deux cas)
    temps, _ = _avec_squelette(5, depot, "structure.py", essai, apres=[3, 4, 5, 6, 7, 8, 9])
    for f in ("phase5_tour_epaisseurs.csv", "phase5_somme_des_DEL.csv", "phase5_boucle.csv"):
        assert (res / f).is_file(), f
    assert (res / "tour_dimensionnee.dat").is_file() and len(list((res / "phase5").glob("*/main.outb"))) == 2
    _noter(depot, 5, temps)


@pytest.mark.slow
@REJEU
@requiert_openfast
def test_rejeu_phase_6(depot):
    if not (Path(depot) / "results" / "phase3_parametres.json").is_file():
        pytest.skip("la phase 3 doit avoir été rejouée dans ce dépôt (results/phase3_parametres.json)")
    import subprocess
    import pandas as pd
    from .test_phase2_parcours import ESSAI as ESSAI_2, FAMILLES, _numero_bloc_sensibilite
    res = Path(depot) / "results"
    if not (res / "D01" / "main.outb").is_file():
        r = subprocess.run(["bash", "cas/run_cas.sh", "D01"], cwd=depot, capture_output=True, text=True)
        assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-1500:]
    if not list((res / "phase2").glob("S*/main.outb")):
        code, sortie, _ = parcours.rejouer(RACINE / "seances" / "phase2" / "README.md", depot,
                                           {**ESSAI_2, "<vos variations>": FAMILLES["babord_vent"]}, etapes=[_numero_bloc_sensibilite()])
        assert code == 0, sortie[-2000:]
    essai = {**ESSAI_4, "<votre groupe>": "babord", "<votre famille de paramètres>": "vent",
             "<votre tolérance relative sur D01>": "0.01", "<votre date de rejeu>": "13/10"}
    code, sortie, t1 = parcours.rejouer(PHASE[6], depot, essai, delai=1800, etapes=[1])
    assert code == 0, sortie[-3000:]
    # les deux autres groupes : le test fabrique leurs fichiers (même format), à partir de celui du premier
    dossier = Path(depot) / "rendus" / "groupes"
    dossier.mkdir(parents=True, exist_ok=True)
    base = pd.read_csv(Path(depot) / "rendus" / "synthese_babord.csv")
    for facteur, (g, fam) in zip((1.0, 1.3, 0.8), (("babord", "vent"), ("tribord", "mer"), ("centre", "ancrage"))):
        d = base.copy()
        d["groupe"], d["famille"] = g, fam
        sens = d["type"] == "sensibilité"
        for c in ("dommage_tour_par_heure", "DEL_ligne_max_N", "max_TwrBsMyt_kNm", "max_tension_N"):
            d.loc[sens, c] = d.loc[sens, c] * facteur
        d.to_csv(dossier / f"{g}.csv", index=False)
    code, sortie, t2 = parcours.rejouer(PHASE[6], depot, essai, delai=1800, etapes=[2, 3])
    assert code == 0, sortie[-3000:]
    assert "point commun cohérent à la tolérance retenue ? True" in sortie
    assert (Path(depot) / "rendus" / "tableau_synthese.csv").is_file() and (Path(depot) / "rendus" / "synthese_sensibilite.png").is_file()
    _noter(depot, 6, {**t1, **t2})
