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
CORAIL = "#EB5600"   # maillage non répertorié (AN-ter) ; GREY #595959 est réservé à la provenance
PALETTE_ANIMATION = [*visu.CHARTE.values(), CORAIL]   # la charte des graphiques + l'accent, animations seulement
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


def pixels_provenance(a):
    """Nombre de pixels de la bande basse (7 %) qui sont du texte gris de provenance : sans teinte (écart
    entre canaux < 10) et plus sombres que 200. Le test FA-4 exige plus de 50."""
    bande = np.asarray(a)[int(0.93 * a.shape[0]):].astype(int)
    return int((((bande.max(axis=-1) - bande.min(axis=-1)) < 10) & (bande.max(axis=-1) < 200)).sum())


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
    for p in pngs:
        assert pixels_provenance(image_rgb(p)) > 50, f"{p.name} : provenance absente"
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
        n, ex = _hors_charte_rgb(image_rgb(p), cache, PALETTE_ANIMATION)
        assert n == 0, f"{p.name} : {n} couleurs hors charte, par ex. {ex}"


@pytest.mark.slow
@requiert_openfast
@requiert_rendu
def test_fa5_falsification_l_eclairage_en_relief_est_refuse(cas_vtk, tmp_path):
    """Falsifie le falsificateur : avec ombrage, les teintes sortent de l'enveloppe de la palette."""
    pngs = visu.rendre(cas_vtk / "vtk", tmp_path, **PROV, eclairage="relief", pas=25)
    assert max(_hors_charte_rgb(image_rgb(p), None, PALETTE_ANIMATION)[0] for p in pngs) > 0


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


# --------------------------------------------------------------------------------------------
# Ajouts après la relecture (relecteur-invariants, 11/10) : repli VTK_type = 2, horloge, scène vide
# --------------------------------------------------------------------------------------------
@pytest.mark.slow
@requiert_openfast
@requiert_rendu
def test_repli_vtk_type_2_se_rend(prefixe, tmp_path_factory, tmp_path):
    """Le repli annoncé (lignes et points, maillages `ED_Tower…`) doit produire une image par pas."""
    d = _fabriquer(f"{prefixe}_ln2", 2, tmp_path_factory)
    visu.preparer_animation(d, vtk_type=2, vtk_fps=FPS)
    assert lancer.lancer_cas(d)["statut"] == "termine"
    pngs = visu.rendre(d / "vtk", tmp_path / "png", **PROV)
    n = max(compter_series_vtk(d / "vtk").values())
    assert len(pngs) == n == 2 * FPS + 1
    visu.verifier_images(tmp_path / "png", n)


def test_fa4_scene_vide_avec_seule_l_horloge_refusee(tmp_path):
    a = np.full((720, 1280, 3), 255, np.uint8)
    a[10:40, 10:140] = (26, 52, 109)   # « t = … s » en haut à gauche, rien d'autre
    Image.fromarray(a).save(tmp_path / "image_0000.png")
    with pytest.raises(ValueError, match="uniforme"):
        visu.verifier_images(tmp_path, 1)


def test_l_horloge_suit_la_cadence_vtk_pas_la_lecture(tmp_path, monkeypatch):
    """`animer(fps=10)` sur un cas à VTK_fps = 5 : la vidéo est lue à 10, l'horloge reste à 5."""
    vus = {}
    (tmp_path / "vtk").mkdir()
    (tmp_path / "vtk" / "main.TowerSurface1.000.vtp").write_text("x")
    (tmp_path / "main.fst").write_text("         5    VTK_fps - x\n")
    monkeypatch.setattr(visu, "_outil", lambda *a: "/bin/true")
    monkeypatch.setattr(visu, "rendre", lambda *a, fps=None, **k: vus.update(horloge=fps) or [])
    monkeypatch.setattr(visu, "verifier_images", lambda *a, **k: 1)
    monkeypatch.setattr(visu, "monter", lambda *a, fps=None, **k: vus.update(lecture=fps))
    visu.animer(**PROV, dossier_cas=tmp_path, sortie=tmp_path / "o.mp4", fps=10)
    assert vus == {"horloge": 5.0, "lecture": 10}


@pytest.mark.slow
@requiert_openfast
@requiert_rendu
def test_fa4bis_le_detecteur_de_provenance_refuse_un_rendu_sans_provenance(cas_vtk, tmp_path):
    """FA-4bis : même scène, même caméra, même pvbatch, mais le texte de provenance est vide
    (`_rendu_vtk.py --provenance " "`, aucune incrustation) : le détecteur doit échouer sur ces images
    et passer sur les mêmes images rendues avec leur provenance. Le contrôle ne recouvre rien après coup :
    c'est le rendu qui diffère, donc ce que le détecteur compte vient bien de la ligne de provenance
    (et non d'une arête ou d'un objet gris de la scène)."""
    def rendre_avec(provenance, sortie):
        cmd = [shutil.which("pvbatch"), str(visu.RENDU_VTK), "--vtk", str(cas_vtk / "vtk"), "--sortie",
               str(sortie), "--provenance", provenance, "--fps", str(FPS), "--pas", "25"]
        r = subprocess.run(cmd, capture_output=True, text=True)
        assert r.returncode == 0, r.stderr[-400:]
        return sorted(Path(sortie).glob("image_*.png"))

    avec = rendre_avec(visu.ligne_provenance(**PROV), tmp_path / "avec")
    sans = rendre_avec(" ", tmp_path / "sans")
    assert len(avec) == len(sans) >= 3
    for pa, ps in zip(avec, sans):
        n_avec, n_sans = pixels_provenance(image_rgb(pa)), pixels_provenance(image_rgb(ps))
        print(f"FA-4bis {pa.name} : avec provenance {n_avec} px, rendu sans provenance {n_sans} px")
        assert n_avec > 50, f"{pa.name} : l'image avec provenance doit passer ({n_avec} px)"
        assert not n_sans > 50, f"{ps.name} : image sans provenance acceptée ({n_sans} px comptés)"
        # le reste de la scène est identique : seule la bande de provenance change
        h = image_rgb(pa).shape[0]
        assert (image_rgb(pa)[: int(0.93 * h)] == image_rgb(ps)[: int(0.93 * h)]).all()


# --------------------------------------------------------------------------------------------
# AN-bis point 2 — garde-fou sur l'amplification : N ≠ 1 seulement si tous les maillages sont connus
# --------------------------------------------------------------------------------------------
MAILLAGES_MODELE_FIXE = ["Blade_R1B1Surface", "Blade_R1B2Surface", "Blade_R1B3Surface", "HubSurface1",
                         "NacelleSurface1", "TowerSurface1", "MorisonSurface", "WaveSurface"]
STATIQUES_MODELE_FIXE = ["SeabedSurface", "StillWaterSurface"]


def _serie_factice(dossier, supplementaires=()):
    """Dossier VTK factice : noms de `modele_fixe` (+ éventuellement d'autres), contenu vide — le garde-fou
    ne lit que les noms, et doit refuser avant que pvbatch ne lise quoi que ce soit."""
    dossier.mkdir(parents=True, exist_ok=True)
    for m in MAILLAGES_MODELE_FIXE + list(supplementaires):
        for k in range(3):
            (dossier / f"main.{m}.{k:03d}.vtp").write_text("")
    for m in STATIQUES_MODELE_FIXE:
        (dossier / f"main.{m}.vtp").write_text("")
    return dossier


@pytest.mark.parametrize("intrus", [["MD_Line1", "MD_Line2"], ["PlatformSurface"], ["ED_Platform_motion_R1"]])
def test_garde_fou_refuse_un_maillage_inconnu_avec_amplification(tmp_path, intrus):
    vtk = _serie_factice(tmp_path / "vtk", intrus)
    avant = sorted(p.name for p in tmp_path.rglob("*"))
    with pytest.raises(ValueError) as e:
        visu.rendre(vtk, tmp_path / "png", **PROV, amplification=3)
    for m in intrus:
        assert m in str(e.value), "le message doit nommer chaque maillage en cause"
    assert "N = 1" in str(e.value), "le message doit dire que N = 1 reste possible"
    assert sorted(p.name for p in tmp_path.rglob("*")) == avant, "aucun fichier écrit, aucun dossier créé"
    assert not (tmp_path / "png").exists()


def test_garde_fou_refuse_avant_de_chercher_pvbatch(tmp_path, monkeypatch):
    """Le refus ne dépend pas des outils : PATH vide, c'est bien le ValueError qui sort, pas OutilAbsent."""
    monkeypatch.setenv("PATH", str(tmp_path))
    vtk = _serie_factice(tmp_path / "vtk", ["MD_Line1"])
    with pytest.raises(ValueError, match="MD_Line1"):
        visu.rendre(vtk, tmp_path / "png", **PROV, amplification=3)


def test_garde_fou_n_egal_un_rien_ne_change(tmp_path, monkeypatch):
    """Même série avec ancrage, N = 1 : acceptée, pvbatch est bien lancé (ici simulé)."""
    vtk = _serie_factice(tmp_path / "vtk", ["MD_Line1", "PlatformSurface"])
    appels = []

    def faux(cmd, **kw):
        appels.append(cmd)
        Path(cmd[cmd.index("--sortie") + 1], "image_0000.png").write_bytes(b"x")
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(visu, "_outil", lambda nom, paquet: f"/bin/{nom}")
    monkeypatch.setattr(visu.subprocess, "run", faux)
    assert len(visu.rendre(vtk, tmp_path / "png", **PROV, amplification=1)) == 1
    assert len(appels) == 1


def test_garde_fou_accepte_les_maillages_de_modele_fixe(tmp_path):
    vtk = _serie_factice(tmp_path / "vtk")
    visu.verifier_amplification(vtk, 3)   # ne lève pas
    visu.verifier_amplification(vtk, 1)


def test_garde_fou_liste_blanche_exacte_pas_de_sous_chaine(tmp_path):
    """« TowerSurface2 » ou « WaveSurfaceX » contiennent un nom connu mais n'en sont pas : refusés."""
    for nom in ("TowerSurface2", "WaveSurfaceX", "Blade_R1B4Surface"):
        vtk = _serie_factice(tmp_path / nom / "vtk", [nom])
        with pytest.raises(ValueError, match=nom):
            visu.verifier_amplification(vtk, 2)


def test_garde_fou_dossier_vide_ou_sans_serie_refuse_n_different_de_un(tmp_path):
    (tmp_path / "vtk").mkdir()
    with pytest.raises(ValueError):
        visu.verifier_amplification(tmp_path / "vtk", 3)


@pytest.mark.slow
@requiert_openfast
def test_garde_fou_serie_reelle_de_modele_fixe_acceptee(cas_vtk):
    """La série réelle (surfaces) passe à N = 3 ; le test FA-3 de la chaîne de rendu (×3) reste vert."""
    visu.verifier_amplification(cas_vtk / "vtk", 3)
    noms = {re.sub(r"^[^.]+\.|(\.\d+)?\.vtp$", "", f.name) for f in (cas_vtk / "vtk").glob("*.vtp")}
    assert noms == set(MAILLAGES_MODELE_FIXE + STATIQUES_MODELE_FIXE)


# --------------------------------------------------------------------------------------------
# AN-ter — maillage inconnu : CORAIL (pas GREY, réservé à la provenance)
# --------------------------------------------------------------------------------------------
def _vtp(chemin, pts, tris):
    """Maillage de surface VTP ASCII minimal (triangles)."""
    p = "\n".join(" ".join(f"{c:.4f}" for c in q) for q in pts)
    c = " ".join(str(i) for t in tris for i in t)
    o = " ".join(str(3 * (k + 1)) for k in range(len(tris)))
    Path(chemin).write_text(
        '<?xml version="1.0"?>\n<VTKFile type="PolyData" version="1.0" byte_order="LittleEndian" '
        f'header_type="UInt64"><PolyData><Piece NumberOfPoints="{len(pts)}" NumberOfVerts="0" '
        f'NumberOfLines="0" NumberOfStrips="0" NumberOfPolys="{len(tris)}"><Points>'
        f'<DataArray type="Float32" NumberOfComponents="3" format="ascii">{p}</DataArray></Points><Polys>'
        f'<DataArray type="Int64" Name="connectivity" format="ascii">{c}</DataArray>'
        f'<DataArray type="Int64" Name="offsets" format="ascii">{o}</DataArray></Polys></Piece>'
        '</PolyData></VTKFile>')


def _rectangle(x0, x1, z0, z1, y=0.0):
    return [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)], [(0, 1, 2), (0, 2, 3)]


def serie_avec_maillage_inconnu(dest, vtk_reel, images):
    """Série à 2 images : les maillages réels de `modele_fixe` (image 0 du calcul, répétée) + un maillage
    de nom inconnu de type MoorDyn (`MD_Line1`) dont la géométrie est `images` = [image 0, image 1]. La
    caméra étant calée sur l'image 0, un maillage qui bouge peut sortir du cadrage : c'est le mécanisme
    qui, sur un calcul réel, fait sortir un ancrage ou une plateforme du cadrage (ici de façon extrême)."""
    dest = Path(dest)
    dest.mkdir(parents=True)
    for f in Path(vtk_reel).glob("*.000.vtp"):
        (dest / f.name).symlink_to(f.resolve())
        (dest / f.name.replace(".000.", ".001.")).symlink_to(f.resolve())
    for k, geo in enumerate(images):
        _vtp(dest / f"main.MD_Line1.{k:03d}.vtp", *geo)
    return dest


def rendre_direct(vtk, sortie, provenance, fps=0):
    """pvbatch sur `_rendu_vtk.py`, provenance au choix (`" "` : aucune), sans horloge si fps = 0."""
    r = subprocess.run([shutil.which("pvbatch"), str(visu.RENDU_VTK), "--vtk", str(vtk), "--sortie", str(sortie),
                        "--provenance", provenance, "--fps", str(fps)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-400:]
    return [image_rgb(p) for p in sorted(Path(sortie).glob("image_*.png"))]


def compter(a, couleur):
    return int((np.asarray(a) == np.array(couleur)).all(axis=-1).sum())


GREY_RVB, CORAIL_RVB = (0x59, 0x59, 0x59), (0xEB, 0x56, 0x00)
VISIBLE = _rectangle(-130, -80, 20, 120)          # à gauche de la tour, dans le cadrage de l'image 0
LIGNE_LONGUE = _rectangle(-130, -80, -600, 120)   # même ancrage, plongeant sous le cadre à l'image 1


@pytest.fixture(scope="module")
def rendu_inconnu(cas_vtk, tmp_path_factory):
    """Maillage inconnu visible, N = 1, sans provenance ni horloge : tout pixel GREY serait le maillage."""
    d = tmp_path_factory.mktemp("inconnu")
    vtk = serie_avec_maillage_inconnu(d / "vtk", cas_vtk / "vtk", [VISIBLE, VISIBLE])
    return rendre_direct(vtk, d / "png", " ")


@pytest.mark.slow
@requiert_openfast
@requiert_rendu
def test_ft1_le_maillage_inconnu_est_corail_et_jamais_grey(rendu_inconnu):
    for a in rendu_inconnu:
        n_corail, n_grey = compter(a, CORAIL_RVB), compter(a, GREY_RVB)
        print(f"FT-1 : {n_corail} px CORAIL, {n_grey} px GREY")
        assert n_corail > 500, f"maillage inconnu pas en CORAIL ({n_corail} px)"
        assert n_grey == 0, f"{n_grey} px GREY : GREY est réservé à la provenance"


@pytest.mark.slow
@requiert_openfast
@requiert_rendu
def test_ft2_un_maillage_inconnu_dans_la_bande_ne_trompe_pas_le_detecteur_de_provenance(cas_vtk, tmp_path):
    """Le maillage inconnu, immobile à l'image 0, plonge à l'image 1 sous le cadrage (calé sur l'image 0) :
    il traverse la bande basse où s'écrit la provenance. Sans provenance, le détecteur doit compter 0 pixel ;
    avec, plus de 0."""
    vtk = serie_avec_maillage_inconnu(tmp_path / "vtk", cas_vtk / "vtk", [VISIBLE, LIGNE_LONGUE])
    sans = rendre_direct(vtk, tmp_path / "sans", " ")
    avec = rendre_direct(vtk, tmp_path / "avec", visu.ligne_provenance(**PROV))
    h = sans[1].shape[0]
    # le maillage est-il bien dans la bande ? différence avec la même série sans lui (indépendant de sa couleur
    # et de la surface libre, qui remplit peut-être le bas de l'image dans les deux rendus)
    vide = serie_avec_maillage_inconnu(tmp_path / "vtk_sans_maillage", cas_vtk / "vtk", [])
    sans_maillage = rendre_direct(vide, tmp_path / "sans_maillage", " ")
    dans_la_bande = int((sans[1][int(0.93 * h):] != sans_maillage[1][int(0.93 * h):]).any(axis=-1).sum())
    print(f"FT-2 : {dans_la_bande} px non blancs du maillage dans la bande ; détecteur sans provenance "
          f"{[pixels_provenance(a) for a in sans]}, avec {[pixels_provenance(a) for a in avec]}")
    assert dans_la_bande > 1000, "scénario non reproduit : le maillage ne traverse pas la bande"
    assert [pixels_provenance(a) for a in sans] == [0, 0], "le maillage inconnu a été pris pour de la provenance"
    assert all(pixels_provenance(a) > 0 for a in avec), "la provenance doit être comptée"


@pytest.mark.slow
@requiert_openfast
@requiert_rendu
def test_ft3_charte_corail_accepte_rouge_pur_refuse(rendu_inconnu):
    """Palette des animations = charte + CORAIL. Le rendu au maillage CORAIL y est accepté mais pas dans la
    charte des graphiques (on a bien élargi l'enveloppe, seulement ici) ; un rendu où l'on peint du rouge
    pur #FF0000 reste refusé, même avec la palette élargie."""
    a = rendu_inconnu[0]
    assert _hors_charte_rgb(a, None, PALETTE_ANIMATION)[0] == 0
    assert _hors_charte_rgb(a)[0] > 0, "la charte des graphiques ne doit pas accepter CORAIL"
    rouge = np.array(a)
    rouge[100:200, 100:300] = (255, 0, 0)
    n, ex = _hors_charte_rgb(rouge, None, PALETTE_ANIMATION)
    print(f"FT-3 : rouge pur, {n} couleurs hors charte (exemple {ex})")
    assert n > 0
