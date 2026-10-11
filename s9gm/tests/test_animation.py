"""Falsificateurs de s9gm.visu.animer (E-155, volet animation) — FA-1 à FA-7.

Écrits et committés AVANT le code (INV-25). Chaque falsificateur est doublé de sa falsification :
le détecteur doit échouer sur une entrée volontairement fausse.

Les tests marqués `slow` lancent OpenFAST et pvbatch pour de vrai (~ 2 à 5 min au total) ; les autres
n'ont besoin d'aucun calcul. Les cas vivent dans `tutorials/prise_en_main/_pytest_*` (ignoré par git,
supprimé en fin de module), comme ceux des autres tests."""
import json
import re
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from s9gm import cas, lancer, lire, visu

from .conftest import MODELE, PRISE_EN_MAIN, requiert_openfast
from .test_visu import _hors_charte_rgb

PROV = dict(cas="V10", modele="modele_fixe", etat="rejoué le 11/10")
TMAX, FPS = 10, 5
CLES_ANIMATION = ("WrVTK", "VTK_type", "VTK_fps")
requiert_rendu = pytest.mark.skipif(
    shutil.which("pvbatch") is None or shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None,
    reason="pvbatch, ffmpeg ou ffprobe absent du PATH (voir INSTALLATION.md)")
lent = [pytest.mark.slow, requiert_openfast, requiert_rendu]


# --------------------------------------------------------------------------------------------
# Détecteurs (écrits ici, indépendamment du code testé)
# --------------------------------------------------------------------------------------------
def lignes_differentes(avant, apres):
    """Numéros (0-based) des lignes qui diffèrent entre deux fichiers texte, comparaison ligne à ligne.
    Un nombre de lignes différent est lui-même une différence : on renvoie alors None."""
    a = Path(avant).read_text(encoding="utf-8").split("\n")
    b = Path(apres).read_text(encoding="utf-8").split("\n")
    if len(a) != len(b):
        return None
    return [i for i, (x, y) in enumerate(zip(a, b)) if x != y]


def cles_des_lignes(chemin, numeros):
    texte = Path(chemin).read_text(encoding="utf-8").split("\n")
    return {texte[i].split()[1] for i in numeros}


def compter_series_vtk(dossier_vtk):
    """{maillage: nombre de fichiers numérotés} pour les séries `<racine>.<maillage>.<NNN>.vtp`."""
    n = {}
    d = Path(dossier_vtk)
    if not d.is_dir():
        return n
    for f in d.glob("*.vtp"):
        m = re.fullmatch(r"(.+)\.(\d+)\.vtp", f.name)
        if m:
            n[m[1]] = n.get(m[1], 0) + 1
    return n


def verifier_nombre_vtk(dossier_vtk, tmax, fps):
    """Lève AssertionError si un maillage n'a pas tmax·fps + 1 fichiers (à un près) ou s'il n'y en a aucun."""
    n = compter_series_vtk(dossier_vtk)
    assert n, f"aucune série VTK dans {dossier_vtk}"
    attendu = round(tmax * fps) + 1
    for maillage, k in n.items():
        assert abs(k - attendu) <= 1, f"{maillage} : {k} fichiers, attendu {attendu} ± 1"
    return n


def sommet_tour_vtk(fichier, ref_idx=None):
    """Barycentre de l'anneau le plus haut du maillage de tour (VTP ASCII), lu sans ParaView. Renvoie
    (barycentre, indices de l'anneau) ; `ref_idx` impose les indices (ceux de l'image 0)."""
    t = Path(fichier).read_text()
    m = re.search(r"<Points>\s*<DataArray[^>]*>(.*?)</DataArray>", t, re.S)
    p = np.array(m[1].split(), float).reshape(-1, 3)
    if ref_idx is None:
        ref_idx = np.where(p[:, 2] > p[:, 2].max() - 1e-4)[0]
    return p[ref_idx].mean(axis=0), ref_idx


def deplacement_canaux(df, i, hauteur):
    """Déplacement axial (x) du sommet de tour déduit des canaux OutList, plateforme comprise :
    PtfmSurge + TTDspFA + hauteur · PtfmPitch (petits angles). Le canal TTDspFA seul est relatif au
    pied de tour, qui bouge et s'incline avec la plateforme : il ne suffit pas."""
    r = df.iloc[i]
    return r.PtfmSurge + r.TTDspFA + hauteur * np.radians(r.PtfmPitch)


def hauteur_tour():
    m = re.search(r"^\s*(\S+)\s+TowerHt\b", (MODELE / "config_elastodyn.dat").read_text(), re.M)
    return float(m[1])


def ecart_cinematique(deplacements_vtk, deplacements_canal, decalage=0, facteur=1.0):
    """Écart max (m) entre le déplacement lu dans le VTK (aux instants k = 0, 5, 10, …) et celui du canal,
    avec `decalage` images de décalage et un `facteur` d'amplification non déclaré. Tolérance de la
    consigne : 1 % de l'amplitude ou 1 mm, la plus grande."""
    k = np.arange(len(deplacements_vtk))
    ok = (k + decalage >= 0) & (k + decalage < len(deplacements_canal))
    ref = np.asarray(deplacements_canal)[k[ok] + decalage]
    return float(np.max(np.abs(facteur * np.asarray(deplacements_vtk)[ok] - ref)))


def tolerance(deplacements_canal):
    return max(0.01 * float(np.max(np.abs(deplacements_canal))), 1e-3)


def image_rgb(chemin):
    return np.asarray(Image.open(chemin).convert("RGB"))


# --------------------------------------------------------------------------------------------
# Fixtures : un cas court réel avec VTK, un cas sans VTK
# --------------------------------------------------------------------------------------------
LCT = ("cas,fst.TMax,inflow.WindType,inflow.HWindSpeed,inflow.PLExp\n"
       "{nom},{tmax},1,7.5,0.11\n")


def _fabriquer(nom, tmax, tmp_path_factory):
    lct = tmp_path_factory.mktemp("lct") / "lct.csv"
    lct.write_text(LCT.format(nom=nom, tmax=tmax), encoding="utf-8")
    return cas.generer_serie(lct, MODELE, PRISE_EN_MAIN, executer_turbsim=False)[0]


@pytest.fixture(scope="module")
def prefixe():
    p = f"_pytest_anim_{uuid.uuid4().hex[:6]}"
    yield p
    for d in PRISE_EN_MAIN.glob(p + "*"):
        shutil.rmtree(d, ignore_errors=True)


@pytest.fixture(scope="module")
def cas_vtk(prefixe, tmp_path_factory):
    """Cas de 10 s, fixe, VTK surfaces à 5 images/s, réellement lancé."""
    d = _fabriquer(f"{prefixe}_vtk", TMAX, tmp_path_factory)
    visu.preparer_animation(d, vtk_type=1, vtk_fps=FPS)
    res = lancer.lancer_cas(d)
    assert res["statut"] == "termine", res
    return d


@pytest.fixture(scope="module")
def cas_sans_vtk(prefixe, tmp_path_factory):
    """Même cas, 2 s, WrVTK = 0 (valeur du modèle) : sert à falsifier le détecteur de FA-2."""
    d = _fabriquer(f"{prefixe}_sans", 2, tmp_path_factory)
    res = lancer.lancer_cas(d)
    assert res["statut"] == "termine", res
    return d


@pytest.fixture(scope="module")
def rendu_complet(cas_vtk, tmp_path_factory):
    """Toutes les images du cas, amplification 1, éclairage plat."""
    sortie = tmp_path_factory.mktemp("png")
    pngs = visu.rendre(cas_vtk / "vtk", sortie, **PROV)
    return sortie, pngs


# --------------------------------------------------------------------------------------------
# FA-1 — préparation : seules WrVTK, VTK_type, VTK_fps changent
# --------------------------------------------------------------------------------------------
@pytest.fixture
def cas_prepare(tmp_path, pref):
    lct = tmp_path / "lct.csv"
    lct.write_text(LCT.format(nom=f"{pref}_prep", tmax=10), encoding="utf-8")
    d = cas.generer_serie(lct, MODELE, PRISE_EN_MAIN, executer_turbsim=False)[0]
    copie = tmp_path / "avant.fst"
    shutil.copy(d / "main.fst", copie)
    return d, copie


def test_fa1_preparation_ne_touche_que_trois_lignes(cas_prepare):
    d, avant = cas_prepare
    visu.preparer_animation(d, vtk_type=1, vtk_fps=5)
    diff = lignes_differentes(avant, d / "main.fst")
    assert diff, "la préparation n'a rien changé : le modèle a WrVTK = 0, au moins une ligne doit bouger"
    assert cles_des_lignes(d / "main.fst", diff) <= set(CLES_ANIMATION)
    f = cas.FASTInputFile(str(d / "main.fst"))
    assert (int(f["WrVTK"]), int(f["VTK_type"]), float(f["VTK_fps"])) == (2, 1, 5.0)


def test_fa1_preparation_repli_surfaces_vers_lignes(cas_prepare):
    d, avant = cas_prepare
    visu.preparer_animation(d, vtk_type=2, vtk_fps=10)
    assert int(cas.FASTInputFile(str(d / "main.fst"))["VTK_type"]) == 2
    assert cles_des_lignes(d / "main.fst", lignes_differentes(avant, d / "main.fst")) <= set(CLES_ANIMATION)


def test_fa1_falsification_une_autre_ligne_modifiee_est_detectee(cas_prepare):
    """Falsifie le falsificateur : si la préparation touchait aussi TMax, le test FA-1 doit échouer."""
    d, avant = cas_prepare
    visu.preparer_animation(d)
    lignes = (d / "main.fst").read_text(encoding="utf-8").split("\n")
    i = next(k for k, l in enumerate(lignes) if re.match(r"^\s*\S+\s+TMax\b", l))
    lignes[i] = lignes[i].replace(lignes[i].split()[0], "999", 1)
    (d / "main.fst").write_text("\n".join(lignes), encoding="utf-8")
    assert not cles_des_lignes(d / "main.fst", lignes_differentes(avant, d / "main.fst")) <= set(CLES_ANIMATION)


@pytest.mark.parametrize("kw", [dict(vtk_type=3), dict(vtk_type=0), dict(vtk_fps=0), dict(vtk_fps=-5)])
def test_fa1_valeurs_hors_domaine_refusees(cas_prepare, kw):
    d, avant = cas_prepare
    with pytest.raises(ValueError):
        visu.preparer_animation(d, **kw)
    assert lignes_differentes(avant, d / "main.fst") == []   # refus avant toute écriture


# --------------------------------------------------------------------------------------------
# FA-2 — sortie VTK : TMax·fps + 1 fichiers par maillage ; échoue à WrVTK = 0
# --------------------------------------------------------------------------------------------
@pytest.mark.slow
@requiert_openfast
def test_fa2_nombre_de_fichiers_vtk(cas_vtk):
    n = verifier_nombre_vtk(cas_vtk / "vtk", TMAX, FPS)
    assert n, "au moins un maillage"
    assert len(n) >= 5, f"surfaces attendues (pales, moyeu, nacelle, tour, …), trouvé {sorted(n)}"


@pytest.mark.slow
@requiert_openfast
def test_fa2_falsification_le_detecteur_echoue_a_wrvtk_zero(cas_sans_vtk):
    with pytest.raises(AssertionError):
        verifier_nombre_vtk(cas_sans_vtk / "vtk", 2, FPS)


@pytest.mark.slow
@requiert_openfast
def test_fa2_falsification_mauvaise_attente_echoue(cas_vtk):
    with pytest.raises(AssertionError):
        verifier_nombre_vtk(cas_vtk / "vtk", TMAX, 2 * FPS)   # on attendrait 101 fichiers


# --------------------------------------------------------------------------------------------
# FA-3 — fidélité cinématique : sommet de tour (VTK) = canaux OutList
# --------------------------------------------------------------------------------------------
@pytest.fixture(scope="module")
def deplacements(cas_vtk):
    df, _ = lire.lire(cas_vtk / "main.outb")
    h = hauteur_tour()
    nb = round(TMAX * FPS) + 1
    ref = None
    vtk, canal = [], []
    for k in range(nb):
        c, ref = sommet_tour_vtk(cas_vtk / "vtk" / f"main.TowerSurface1.{k:03d}.vtp", ref)
        if k == 0:
            c0 = c
        vtk.append(c[0] - c0[0])
        i = int(np.abs(df["Time"].to_numpy() - k / FPS).argmin())
        assert abs(df["Time"][i] - k / FPS) < 1e-6, "instant de l'image absent du fichier de sortie"
        canal.append(deplacement_canaux(df, i, h))
    return np.array(vtk), np.array(canal)


@pytest.mark.slow
@requiert_openfast
def test_fa3_vtk_egale_canaux_a_plus_de_trois_instants(deplacements):
    vtk, canal = deplacements
    assert len(vtk) >= 3
    assert np.max(np.abs(canal)) > 5e-3, "signal trop petit : le test ne discriminerait rien"
    ecart = ecart_cinematique(vtk, canal)
    assert ecart <= tolerance(canal), f"écart {ecart * 1e3:.3f} mm > {tolerance(canal) * 1e3:.3f} mm"


@pytest.mark.slow
@requiert_openfast
@pytest.mark.parametrize("decalage", [1, -1])
def test_fa3_falsification_decalage_d_un_pas_detecte(deplacements, decalage):
    vtk, canal = deplacements
    assert ecart_cinematique(vtk, canal, decalage=decalage) > tolerance(canal)


@pytest.mark.slow
@requiert_openfast
def test_fa3_falsification_facteur_deux_non_declare_detecte(deplacements):
    vtk, canal = deplacements
    assert ecart_cinematique(vtk, canal, facteur=2.0) > tolerance(canal)


@pytest.mark.slow
@requiert_openfast
@requiert_rendu
def test_fa3_chaine_de_rendu_amplification_declaree(cas_vtk, deplacements, tmp_path):
    """La géométrie réellement envoyée au rendu (après amplification ×3) : déplacement / 3 = canal.
    Sans diviser par le facteur déclaré, l'écart dépasse la tolérance (×N non déclaré détecté)."""
    _, canal = deplacements
    trace = tmp_path / "trace.json"
    pngs = visu.rendre(cas_vtk / "vtk", tmp_path / "png", **PROV, amplification=3, pas=5, trace=trace)
    assert len(pngs) >= 3
    t = json.loads(trace.read_text())
    k = np.array(t["images"])
    dx = np.array(t["sommet"])[:, 0] - np.array(t["sommet_ref"])[0]
    assert t["amplification"] == 3
    assert np.max(np.abs(dx)) > 2e-3
    assert np.max(np.abs(dx / 3 - canal[k])) <= tolerance(canal)
    assert np.max(np.abs(dx - canal[k])) > tolerance(canal)


@pytest.mark.slow
@requiert_openfast
@requiert_rendu
def test_fa3_chaine_de_rendu_amplification_unite(cas_vtk, deplacements, tmp_path):
    _, canal = deplacements
    trace = tmp_path / "trace.json"
    visu.rendre(cas_vtk / "vtk", tmp_path / "png", **PROV, pas=5, trace=trace)
    t = json.loads(trace.read_text())
    k = np.array(t["images"])
    dx = np.array(t["sommet"])[:, 0] - np.array(t["sommet_ref"])[0]
    assert t["amplification"] == 1
    assert np.max(np.abs(dx - canal[k])) <= tolerance(canal)


# --------------------------------------------------------------------------------------------
# FA-4 — rendu : une image par pas, aucune uniforme
# --------------------------------------------------------------------------------------------
def test_fa4_detecteur_refuse_une_image_blanche(tmp_path):
    Image.fromarray(np.full((720, 1280, 3), 255, np.uint8)).save(tmp_path / "image_0000.png")
    with pytest.raises(ValueError, match="uniforme"):
        visu.verifier_images(tmp_path, 1)


def test_fa4_detecteur_refuse_une_image_unie_non_blanche(tmp_path):
    Image.fromarray(np.full((720, 1280, 3), (26, 153, 136), np.uint8)).save(tmp_path / "image_0000.png")
    with pytest.raises(ValueError, match="uniforme"):
        visu.verifier_images(tmp_path, 1)


def test_fa4_detecteur_refuse_une_image_blanche_avec_seule_la_provenance(tmp_path):
    a = np.full((720, 1280, 3), 255, np.uint8)
    a[690:700, 300:900] = (89, 89, 89)   # bande de provenance seule, aucun objet dans la scène
    Image.fromarray(a).save(tmp_path / "image_0000.png")
    with pytest.raises(ValueError, match="uniforme"):
        visu.verifier_images(tmp_path, 1)


def test_fa4_detecteur_refuse_un_nombre_d_images_faux(tmp_path):
    a = np.full((720, 1280, 3), 255, np.uint8)
    a[200:400, 500:700] = (26, 153, 136)
    Image.fromarray(a).save(tmp_path / "image_0000.png")
    visu.verifier_images(tmp_path, 1)   # une image, un pas : accepté
    with pytest.raises(ValueError, match="nombre"):
        visu.verifier_images(tmp_path, 2)


@pytest.mark.slow
@requiert_openfast
@requiert_rendu
def test_fa4_une_image_par_pas_et_aucune_uniforme(cas_vtk, rendu_complet):
    sortie, pngs = rendu_complet
    n_vtk = verifier_nombre_vtk(cas_vtk / "vtk", TMAX, FPS)["main.TowerSurface1"]
    assert len(pngs) == n_vtk == len(list(Path(sortie).glob("*.png")))
    for p in pngs:
        a = image_rgb(p)
        assert a.shape[:2] == (720, 1280)
        scene = a[: int(0.9 * a.shape[0])]
        assert (scene != 255).any(axis=-1).mean() > 1e-3, f"{p.name} : scène vide"
    visu.verifier_images(sortie, n_vtk)


@pytest.mark.slow
@requiert_openfast
@requiert_rendu
def test_fa4_la_scene_bouge_entre_images(rendu_complet):
    """Deux images éloignées dans le temps ne sont pas identiques (pales en rotation)."""
    _, pngs = rendu_complet
    assert (image_rgb(pngs[0]) != image_rgb(pngs[len(pngs) // 2])).any()


@pytest.mark.slow
@requiert_openfast
@requiert_rendu
def test_fa4_provenance_dans_chaque_image(rendu_complet, cas_vtk, tmp_path):
    """La bande basse de chaque image porte du gris (couleur GREY de la provenance) ; avec une autre
    provenance, la bande change (le détecteur voit le texte, pas un liseré fixe)."""
    _, pngs = rendu_complet
    gris = np.array([0x59, 0x59, 0x59])
    for p in pngs:
        bande = image_rgb(p)[int(0.93 * 720):]
        assert (np.abs(bande.astype(int) - gris).sum(axis=-1) < 90).sum() > 50, f"{p.name} : provenance absente"
    autre = visu.rendre(cas_vtk / "vtk", tmp_path / "autre", cas="AUTRE", modele="modele_fixe",
                        etat="autre état", pas=50)
    assert (image_rgb(autre[0])[int(0.93 * 720):] != image_rgb(pngs[0])[int(0.93 * 720):]).any()


# --------------------------------------------------------------------------------------------
# FA-5 — charte : éclairage plat, chaque image est un mélange convexe de la palette
# --------------------------------------------------------------------------------------------
@pytest.mark.slow
@requiert_openfast
@requiert_rendu
def test_fa5_chaque_image_dans_la_charte(rendu_complet):
    _, pngs = rendu_complet
    cache = {}
    for p in pngs:
        n, ex = _hors_charte_rgb(image_rgb(p), cache)
        assert n == 0, f"{p.name} : {n} couleurs hors charte, par ex. {ex}"


@pytest.mark.slow
@requiert_openfast
@requiert_rendu
def test_fa5_falsification_l_eclairage_en_relief_est_refuse(cas_vtk, tmp_path):
    """Falsifie le falsificateur : avec ombrage, les teintes sortent de l'enveloppe de la palette."""
    pngs = visu.rendre(cas_vtk / "vtk", tmp_path, **PROV, eclairage="relief", pas=25)
    assert max(_hors_charte_rgb(image_rgb(p))[0] for p in pngs) > 0


# --------------------------------------------------------------------------------------------
# FA-6 — vidéo
# --------------------------------------------------------------------------------------------
def ffprobe(mp4):
    r = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
                        "-show_entries", "stream=nb_read_frames,codec_name,pix_fmt,duration,width,height",
                        "-of", "json", str(mp4)], capture_output=True, text=True, check=True)
    return json.loads(r.stdout)["streams"][0]


@pytest.mark.slow
@requiert_openfast
@requiert_rendu
def test_fa6_video_images_duree_codec_format(rendu_complet, tmp_path):
    sortie, pngs = rendu_complet
    mp4 = visu.monter(sortie, tmp_path / "anim.mp4", fps=FPS)
    s = ffprobe(mp4)
    assert int(s["nb_read_frames"]) == len(pngs)
    assert abs(float(s["duration"]) - len(pngs) / FPS) <= 1 / FPS
    assert s["codec_name"] == "h264"
    assert s["pix_fmt"] == "yuv420p"
    assert int(s["width"]) % 2 == 0 and int(s["height"]) % 2 == 0


@pytest.mark.slow
@requiert_openfast
@requiert_rendu
def test_fa6_falsification_le_detecteur_voit_un_mauvais_fps(rendu_complet, tmp_path):
    """Une vidéo montée à 2×fps dure moitié moins : le contrôle de durée doit l'attraper."""
    sortie, pngs = rendu_complet
    mp4 = visu.monter(sortie, tmp_path / "rapide.mp4", fps=2 * FPS)
    s = ffprobe(mp4)
    assert abs(float(s["duration"]) - len(pngs) / FPS) > 1 / FPS


# --------------------------------------------------------------------------------------------
# FA-7 — refus
# --------------------------------------------------------------------------------------------
def _registre_sans_porte(tmp_path):
    r = tmp_path / "REGISTRE.md"
    r.write_text("# vide\n\n**FIG:S9GM-VISU-001** — x\nCourte.\n", encoding="utf-8")
    return r


@pytest.mark.parametrize("manquant", ["cas", "modele", "etat"])
def test_fa7_provenance_obligatoire_typeerror(manquant, tmp_path):
    kw = dict(cas="V10", modele="m", etat="e", dossier_cas=tmp_path, sortie=tmp_path / "o.mp4")
    del kw[manquant]
    with pytest.raises(TypeError):
        visu.animer(**kw)


def test_fa7_rendre_et_monter_exigent_la_provenance(tmp_path):
    with pytest.raises(TypeError):
        visu.rendre(tmp_path, tmp_path / "png", cas="a", modele="b")
    with pytest.raises(ValueError, match="provenance incomplète"):
        visu.rendre(tmp_path, tmp_path / "png", cas="a", modele="", etat="c")


def test_fa7_sans_porte_pedagogique_la_livraison_est_refusee(tmp_path):
    """Refus avant tout calcul : le dossier de cas n'existe même pas."""
    with pytest.raises(PermissionError, match="porte pédagogique"):
        visu.animer(**PROV, dossier_cas=tmp_path / "inexistant", sortie=tmp_path / "o.mp4",
                    registre=_registre_sans_porte(tmp_path))
    assert not (tmp_path / "o.mp4").exists()


def test_fa7_monter_sans_porte_refuse(tmp_path):
    Image.fromarray(np.full((4, 4, 3), 255, np.uint8)).save(tmp_path / "image_0000.png")
    with pytest.raises(PermissionError, match="porte pédagogique"):
        visu.monter(tmp_path, tmp_path / "o.mp4", fps=5, registre=_registre_sans_porte(tmp_path))
    assert not (tmp_path / "o.mp4").exists()


@pytest.mark.parametrize("outil", ["pvbatch", "ffmpeg"])
def test_fa7_outil_absent_renvoie_a_installation(outil, tmp_path, monkeypatch):
    """PATH vide : le message nomme l'outil et renvoie à INSTALLATION.md (pas de FileNotFoundError brut)."""
    monkeypatch.setenv("PATH", str(tmp_path))
    appel = (lambda: visu.rendre(tmp_path, tmp_path / "png", **PROV)) if outil == "pvbatch" else \
            (lambda: visu.monter(tmp_path, tmp_path / "o.mp4", fps=5))
    if outil == "ffmpeg":
        Image.fromarray(np.full((4, 4, 3), 255, np.uint8)).save(tmp_path / "image_0000.png")
    with pytest.raises(visu.OutilAbsent) as e:
        appel()
    assert outil in str(e.value) and "INSTALLATION.md" in str(e.value)
    assert not isinstance(e.value, FileNotFoundError)


def test_fa7_animer_outil_absent_par_la_commande(tmp_path):
    """Par la ligne de commande, sans pvbatch dans le PATH : code de sortie non nul, message lisible,
    aucune trace Python."""
    env = {"PATH": str(tmp_path), "HOME": str(tmp_path)}
    r = subprocess.run([sys.executable, "-m", "s9gm.visu", "animer", str(tmp_path), str(tmp_path / "o.mp4"),
                        "--cas", "V10", "--modele", "m", "--etat", "e"],
                       capture_output=True, text=True, env=env, cwd=Path(__file__).resolve().parents[2])
    assert r.returncode != 0
    assert "INSTALLATION.md" in r.stderr
    assert "Traceback" not in r.stderr


def test_fa7_amplification_dans_la_provenance():
    assert "déplacements" not in visu.ligne_provenance(**PROV)
    assert "déplacements" not in visu.ligne_provenance(**PROV, amplification=1)
    assert visu.ligne_provenance(**PROV, amplification=5).endswith("déplacements ×5")
    with pytest.raises(ValueError):
        visu.ligne_provenance(**PROV, amplification=0)


def test_fa7_identifiant_et_porte_du_registre():
    assert visu.ID_ANIMATION == "FIG:S9GM-VISU-007"
    assert len(visu.porte_pedagogique(visu.ID_ANIMATION) or "") >= 40
    texte = visu.REGISTRE.read_text(encoding="utf-8")
    assert re.search(r"^\| FIG:S9GM-VISU-007 \|", texte, re.M)
