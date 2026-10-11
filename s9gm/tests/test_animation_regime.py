"""Falsificateurs d'AN-quater : un exemple d'animation où le rotor tourne (Region 3, vent uniforme, rotor lancé
au régime nominal), animé sur une fenêtre prise après le transitoire. FA-8a (le rotor tourne), FA-8b (le pas se
voit), FA-8c (la fenêtre) et `lire.debut_regime`. Écrits avant le code.

Cas réel : `modele_fixe`, vent uniforme de 15,4 m/s, `RotSpeed` initial 12,1 tr/min (donnée publiée, ENONCE §4),
pas initial 0 (le régulateur le trouve seul), TMax = 31,2 s, VTK à 5 images/s. Fenêtre animée : de 19,2 s à
31,2 s, début fixé par le critère écrit AVANT le calcul : |RotSpeed − 12,1| ≤ 2 % et amplitude de BldPitch1 ≤ 0,5°
sur les 5 s suivantes (arrondi à l'image VTK supérieure). Aucune valeur de pas, de puissance ni de flèche n'est
écrite dans ce fichier : les tests comparent le VTK aux canaux du même calcul.

Mesures dans le VTK (ASCII), sans ParaView :
- maillage de pale : 19 sections de 399 points ; la section 0 est la bague de racine, circulaire ;
- axe du rotor, à chaque image : normale au plan des trois racines de pale ;
- azimut : angle du barycentre de la section 2 de la pale 1 autour de l'axe, `0` = dans le plan de l'axe et de la
  verticale. Les nœuds du maillage sont sur la ligne du centre aérodynamique, décalée de l'axe de pas : l'angle
  absolu est décalé d'environ 7° ; on compare donc la VARIATION depuis l'image 0 (comme FA-3 pour les flèches) ;
- calage : angle de la corde (axe principal des 399 points) de la section 6 de la pale 1 dans le plan normal à
  l'axe de pale, mesuré depuis l'image 0 (pas nul). Convention de signe : un pas positif fait tourner la corde
  dans le sens négatif de ce repère (fixé une fois, vérifié par la falsification en signe opposé)."""
import json
import math
import re
import shutil
import subprocess
import uuid
from pathlib import Path

import numpy as np
import pytest

from s9gm import cas, lancer, lire, visu

from .conftest import MODELE, PRISE_EN_MAIN, requiert_openfast
from .test_animation import (PROV, FPS, cas_vtk, ffprobe, image_rgb, lent, prefixe,  # noqa: F401 (fixtures)
                             requiert_rendu)

T_DEBUT, T_FIN, TMAX_R3 = 19.2, 31.2, 31.2
VENT, ROT_NOMINAL = 15.4, 12.1
NPTS = 399
STATION_AZIMUT, STATION_CALAGE = 2, 6


# --------------------------------------------------------------------------------------------
# Lecture du VTK (indépendante de ParaView et de s9gm.visu)
# --------------------------------------------------------------------------------------------
def fichier_vtk(dossier, maillage, k):
    """k-ième fichier (ordre trié) de la série `main.<maillage>.*.vtp` : 3 chiffres jusqu'à 100 images,
    4 au-delà (OpenFAST élargit l'indice)."""
    return sorted(Path(dossier).glob(f"main.{maillage}.*.vtp"))[k]


def points(fichier):
    m = re.search(r"<Points>\s*<DataArray[^>]*>(.*?)</DataArray>", Path(fichier).read_text(), re.S)
    return np.array(m[1].split(), float).reshape(-1, 3)


def geometrie(dossier, k):
    """(centre du moyeu, axe du rotor, barycentres de racine des 3 pales, points de la pale 1)."""
    c = points(fichier_vtk(dossier, "HubSurface1", k)).mean(axis=0)
    pales = [points(fichier_vtk(dossier, f"Blade_R1B{i}Surface", k)) for i in (1, 2, 3)]
    assert len(pales[0]) % NPTS == 0, "maillage de pale : sections de 399 points attendues"
    racines = np.array([p[:NPTS].mean(axis=0) for p in pales])
    a = np.cross(racines[1] - racines[0], racines[2] - racines[0])
    a /= np.linalg.norm(a)
    return c, (a if a[0] > 0 else -a), racines, pales[0]


def azimut_vtk(dossier, k):
    c, a, _, p = geometrie(dossier, k)
    z = np.array([0.0, 0.0, 1.0])
    haut = z - (z @ a) * a
    haut /= np.linalg.norm(haut)
    cote = np.cross(a, haut)
    r = p[STATION_AZIMUT * NPTS:(STATION_AZIMUT + 1) * NPTS].mean(axis=0) - c
    return math.degrees(math.atan2(r @ cote, r @ haut))


def angle_corde_vtk(dossier, k):
    c, a, racines, p = geometrie(dossier, k)
    b = racines[0] - c
    b /= np.linalg.norm(b)
    t = np.cross(a, b)
    t /= np.linalg.norm(t)
    n = np.cross(b, t)
    s = p[STATION_CALAGE * NPTS:(STATION_CALAGE + 1) * NPTS]
    s = s - s.mean(axis=0)
    e = np.linalg.svd(np.c_[s @ t, s @ n], full_matrices=False)[2][0]
    e = e if e[0] > 0 else -e
    return math.degrees(math.atan2(e[1], e[0]))


def canal_a(df, k, fps=FPS):
    i = int(np.abs(df["Time"].to_numpy() - k / fps).argmin())
    assert abs(df["Time"][i] - k / fps) < 1e-6
    return i


def difference_angulaire(x, y):
    return (np.asarray(x) - np.asarray(y) + 180) % 360 - 180


def assert_au_moins_un_tour(azimuts_deg):
    """Détecteur de FA-8a : la fenêtre contient au moins un tour complet du rotor."""
    tours = abs(np.unwrap(np.radians(azimuts_deg))[-1] - np.unwrap(np.radians(azimuts_deg))[0]) / (2 * math.pi)
    assert tours >= 1.0, f"{tours:.2f} tour dans la fenêtre"
    return tours


# --------------------------------------------------------------------------------------------
# Fixture : le cas réel Region 3
# --------------------------------------------------------------------------------------------
@pytest.fixture(scope="module")
def cas_r3(prefixe, tmp_path_factory):
    lct = tmp_path_factory.mktemp("lct_r3") / "lct.csv"
    lct.write_text("cas,fst.TMax,inflow.WindType,inflow.HWindSpeed,inflow.PLExp,elastodyn.RotSpeed\n"
                   f"{prefixe}_r3,{TMAX_R3},1,{VENT},0,{ROT_NOMINAL}\n", encoding="utf-8")
    d = cas.generer_serie(lct, MODELE, PRISE_EN_MAIN, executer_turbsim=False)[0]
    visu.preparer_animation(d, vtk_type=1, vtk_fps=FPS)
    res = lancer.lancer_cas(d)
    assert res["statut"] == "termine", res
    df, _ = lire.lire(d / "main.outb")
    return d, df


# --------------------------------------------------------------------------------------------
# Début du régime : lire.debut_regime (critère écrit avant le calcul)
# --------------------------------------------------------------------------------------------
def _serie(t, vitesse, pas):
    import pandas as pd
    return pd.DataFrame({"Time": t, "RotSpeed": vitesse, "BldPitch1": pas})


def test_debut_regime_critere_sur_serie_synthetique():
    t = np.arange(0, 60, 0.1)
    vitesse = np.where(t < 10, 5.0, 12.1)           # le rotor atteint le nominal à 10 s
    pas = np.where(t < 20, 0.0 + 0.2 * t, 4.0)      # le pas se stabilise à 20 s
    d = lire.debut_regime(_serie(t, vitesse, pas), nominal=12.1, tol_rel=0.02, stab_pas=0.5, duree=5.0)
    assert 15.0 <= d <= 20.0, f"début attendu quand le pas devient stable à ±0,5° sur 5 s, trouvé {d}"


def test_debut_regime_jamais_atteint_renvoie_none():
    t = np.arange(0, 30, 0.1)
    assert lire.debut_regime(_serie(t, 0.3 * np.ones_like(t), np.zeros_like(t)), nominal=12.1, tol_rel=0.02,
                             stab_pas=0.5, duree=5.0) is None
    # régime nominal, mais pas qui dérive sans cesse : jamais stable
    assert lire.debut_regime(_serie(t, 12.1 * np.ones_like(t), 2.0 * t), nominal=12.1, tol_rel=0.02,
                             stab_pas=0.5, duree=5.0) is None


def test_debut_regime_demande_la_duree_complete():
    t = np.arange(0, 6, 0.1)   # moins de 5 s après tout instant utile : refusé plutôt que deviné
    assert lire.debut_regime(_serie(t, 12.1 * np.ones_like(t), np.zeros_like(t)), nominal=12.1, tol_rel=0.02,
                             stab_pas=0.5, duree=10.0) is None


@pytest.mark.slow
@requiert_openfast
def test_debut_regime_sur_le_cas_reel_la_fenetre_commence_apres_le_critere(cas_r3):
    _, df = cas_r3
    debut = lire.debut_regime(df, nominal=ROT_NOMINAL, tol_rel=0.02, stab_pas=0.5, duree=5.0)
    assert debut is not None
    assert 10.0 < debut <= T_DEBUT, f"critère satisfait à {debut:.2f} s : la fenêtre retenue ({T_DEBUT} s) est après"
    assert abs(math.ceil(debut * FPS) / FPS - T_DEBUT) < 1e-9, "T_DEBUT = début du critère arrondi à l'image VTK"
    assert df["Time"].iloc[-1] >= T_FIN - 1e-6


@pytest.mark.slow
@requiert_openfast
def test_debut_regime_falsification_l_ancien_cas_n_atteint_jamais_le_regime(cas_vtk):
    df, _ = lire.lire(cas_vtk / "main.outb")   # modèle partagé : rotor à l'arrêt, vent de 7,5 m/s
    assert lire.debut_regime(df, nominal=ROT_NOMINAL, tol_rel=0.02, stab_pas=0.5, duree=5.0) is None


# --------------------------------------------------------------------------------------------
# FA-8a — le rotor tourne : azimut VTK = canal Azimuth, à 1° près, à chaque image de la fenêtre
# --------------------------------------------------------------------------------------------
def _fenetre_k():
    return range(round(T_DEBUT * FPS), round(T_FIN * FPS) + 1)


@pytest.fixture(scope="module")
def azimuts(cas_r3):
    d, df = cas_r3
    v = d / "vtk"
    psi0 = azimut_vtk(v, 0)
    ks = list(_fenetre_k())
    vtk = np.array([azimut_vtk(v, k) - psi0 for k in ks])
    canal = np.array([df["Azimuth"][canal_a(df, k)] - df["Azimuth"][0] for k in ks])
    return ks, vtk, canal


@pytest.mark.slow
@requiert_openfast
def test_fa8a_l_azimut_du_vtk_egale_le_canal_a_chaque_image(azimuts):
    ks, vtk, canal = azimuts
    assert len(ks) >= 60
    ecart = np.abs(difference_angulaire(vtk, canal))
    print(f"FA-8a : {len(ks)} images, écart max {ecart.max():.3f}°, tolérance 1°")
    assert ecart.max() <= 1.0


@pytest.mark.slow
@requiert_openfast
def test_fa8a_la_fenetre_contient_au_moins_un_tour(azimuts):
    _, vtk, _ = azimuts
    tours = assert_au_moins_un_tour(vtk)
    print(f"FA-8a : {tours:.2f} tours dans la fenêtre")


@pytest.mark.slow
@requiert_openfast
def test_fa8a_falsification_l_ancien_cas_ne_fait_pas_un_tour(cas_vtk):
    """Le détecteur « au moins un tour » doit échouer sur l'ancien cas (rotor à l'arrêt au départ, 10 s)."""
    v = cas_vtk / "vtk"
    n = len(sorted(v.glob("main.HubSurface1.*.vtp")))
    psi = [azimut_vtk(v, k) for k in range(n)]
    with pytest.raises(AssertionError, match="tour"):
        assert_au_moins_un_tour(psi)


@pytest.mark.slow
@requiert_openfast
@pytest.mark.parametrize("decalage", [1, -1])
def test_fa8a_falsification_decalage_d_une_image_detecte(cas_r3, azimuts, decalage):
    ks, vtk, _ = azimuts
    _, df = cas_r3
    decale = np.array([df["Azimuth"][canal_a(df, k + decalage)] - df["Azimuth"][0] for k in ks])
    assert np.abs(difference_angulaire(vtk, decale)).max() > 1.0


# --------------------------------------------------------------------------------------------
# FA-8b — le pas se voit : calage de la pale 1 dans le VTK = BldPitch1, à 0,5° près
# --------------------------------------------------------------------------------------------
@pytest.fixture(scope="module")
def calages(cas_r3):
    d, df = cas_r3
    v = d / "vtk"
    assert abs(df["BldPitch1"][0]) < 1e-9, "image de référence : pas nul"
    phi0 = angle_corde_vtk(v, 0)
    ks = list(_fenetre_k())
    vtk = np.array([-(angle_corde_vtk(v, k) - phi0) for k in ks])   # signe : voir l'en-tête du fichier
    canal = np.array([df["BldPitch1"][canal_a(df, k)] for k in ks])
    return ks, vtk, canal


@pytest.mark.slow
@requiert_openfast
def test_fa8b_le_calage_du_vtk_egale_bldpitch1(calages):
    ks, vtk, canal = calages
    assert len(ks) >= 3
    print(f"FA-8b : {len(ks)} images, écart max {np.abs(vtk - canal).max():.3f}°, tolérance 0,5°")
    assert np.abs(vtk - canal).max() <= 0.5
    assert canal.max() > 1.0, "le pas doit être loin de zéro : sinon le test ne discriminerait pas"


@pytest.mark.slow
@requiert_openfast
def test_fa8b_falsification_signe_oppose_pas_nul_et_pas_constant_detectes(calages):
    ks, vtk, canal = calages
    assert np.abs(-vtk - canal).max() > 0.5, "signe opposé"
    assert np.abs(vtk - 0.0).max() > 0.5, "pas constant nul (pas de pivotement)"
    assert np.abs(vtk - canal[0]).max() > 0.5, "pas constant égal à sa valeur au début de la fenêtre"


@pytest.mark.slow
@requiert_openfast
def test_fa8b_limite_connue_un_decalage_d_une_image_n_est_pas_detectable_a_0_5_degre(cas_r3, calages):
    """Documente une limite, ne l'affaiblit pas : en régime, le pas varie de moins de 0,5° d'une image à l'autre,
    donc comparer le VTK à BldPitch1 décalé d'UNE image reste dans la tolérance. Un décalage assez grand
    (plusieurs secondes) est, lui, détecté. `BldPitch2` n'est pas un canal de ce modèle."""
    _, df = cas_r3
    ks, vtk, canal = calages
    un = np.array([df["BldPitch1"][canal_a(df, k + 1)] for k in ks])
    assert np.abs(un - canal).max() < 0.5, "décalage d'une image : indétectable à cette tolérance"
    loin = np.array([df["BldPitch1"][canal_a(df, k - 40)] for k in ks])   # 8 s plus tôt
    assert np.abs(vtk - loin).max() > 0.5, "décalage de 8 s : détecté"


# --------------------------------------------------------------------------------------------
# FA-8c — la fenêtre
# --------------------------------------------------------------------------------------------
def _vtk_factice(dossier, n=10):
    dossier.mkdir(parents=True)
    for m in ("TowerSurface1", "HubSurface1"):
        for k in range(n):
            (dossier / f"main.{m}.{k:03d}.vtp").write_text("")
    return dossier


@pytest.mark.parametrize("fenetre,motif", [((5.0, 6.0), "hors"), ((1.0, 0.5), "fenêtre"), ((-1.0, 1.0), "hors"),
                                           ((1.0,), "fenêtre"), ((0.0, 1.0, 2.0), "fenêtre")])
def test_fa8c_fenetre_invalide_refusee_avant_tout_rendu(tmp_path, fenetre, motif):
    vtk = _vtk_factice(tmp_path / "vtk")   # 10 images à 5 images/s : 0 à 1,8 s
    with pytest.raises(ValueError, match=motif):
        visu.rendre(vtk, tmp_path / "png", **PROV, fps=5, fenetre=fenetre)
    assert not (tmp_path / "png").exists()


def test_fa8c_fenetre_choisit_les_pas_vtk_passes_a_pvbatch(tmp_path, monkeypatch):
    vtk = _vtk_factice(tmp_path / "vtk", n=60)
    vus = []

    def faux(cmd, **kw):
        vus.append(cmd)
        Path(cmd[cmd.index("--sortie") + 1], "image_0000.png").write_bytes(b"x")
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(visu, "_outil", lambda nom, paquet: f"/bin/{nom}")
    monkeypatch.setattr(visu.subprocess, "run", faux)
    visu.rendre(vtk, tmp_path / "png", **PROV, fps=5, fenetre=(2.0, 4.0))
    cmd = vus[-1]
    assert cmd[cmd.index("--k-debut") + 1] == "10" and cmd[cmd.index("--k-fin") + 1] == "20"
    visu.rendre(vtk, tmp_path / "png2", **PROV, fps=5)   # sans fenêtre : aucune option de fenêtre
    assert "--k-debut" not in vus[-1] and "--k-fin" not in vus[-1]


@pytest.mark.slow
@requiert_openfast
@requiert_rendu
def test_fa8c_sans_fenetre_le_resultat_ne_change_pas_et_fenetre_pleine_est_identique(cas_r3, tmp_path):
    d, _ = cas_r3
    a = visu.rendre(d / "vtk", tmp_path / "a", **PROV, pas=60)
    b = visu.rendre(d / "vtk", tmp_path / "b", **PROV, pas=60, fenetre=(0.0, TMAX_R3))
    assert [p.name for p in a] == [p.name for p in b]
    assert all(pa.read_bytes() == pb.read_bytes() for pa, pb in zip(a, b))
    assert len(sorted((d / "vtk").glob("main.TowerSurface1.*.vtp"))) == round(TMAX_R3 * FPS) + 1


@pytest.mark.slow
@requiert_openfast
@requiert_rendu
def test_fa8c_fenetre_donnee_nombre_d_images_et_horloge_du_temps_reel(cas_r3, tmp_path):
    d, _ = cas_r3
    trace = tmp_path / "trace.json"
    pngs = visu.rendre(d / "vtk", tmp_path / "png", **PROV, fenetre=(T_DEBUT, T_DEBUT + 2.0), trace=trace)
    attendu = round(2.0 * FPS) + 1
    assert abs(len(pngs) - attendu) <= 1 and len(pngs) == attendu
    t = json.loads(trace.read_text())
    print(f"FA-8c : {len(pngs)} images, première horloge « {t['horloges'][0]} », dernière « {t['horloges'][-1]} »")
    assert t["horloges"][0] == f"t = {T_DEBUT:.2f} s", "l'horloge affiche le temps du calcul, non le temps depuis le début de la fenêtre"
    assert t["horloges"][-1] == f"t = {T_DEBUT + 2.0:.2f} s"
    assert t["images"][0] == round(T_DEBUT * FPS)
    assert pngs[0].name == f"image_{round(T_DEBUT * FPS):04d}.png"


@pytest.mark.slow
@requiert_openfast
@requiert_rendu
def test_fa8c_animer_avec_fenetre_de_bout_en_bout(cas_r3, tmp_path):
    d, _ = cas_r3
    mp4 = visu.animer(**PROV, dossier_cas=d, sortie=tmp_path / "w.mp4", fenetre=(T_DEBUT, T_DEBUT + 2.0))
    s = ffprobe(mp4)
    assert int(s["nb_read_frames"]) == round(2.0 * FPS) + 1
    assert s["codec_name"] == "h264" and s["pix_fmt"] == "yuv420p"
