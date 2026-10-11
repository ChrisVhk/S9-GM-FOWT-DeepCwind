"""s9gm._rendu_vtk — rendre la série VTK d'un calcul OpenFAST en une image PNG par pas (script de `pvbatch`).

Ce fichier n'est PAS importé par `s9gm` : `s9gm.visu.rendre` le lance en sous-processus avec
`pvbatch`, qui embarque son propre Python (celui de ParaView), distinct de celui du venv `s9gm`.
Il n'utilise que `paraview.simple` (et `vtkmodules` dans un filtre programmable), API que l'on
attend commune à ParaView 5.11 et 6.0 (seul 6.0.1 a été exécuté).

### Bloc Théorie

1. **Question physique** — Que *fait* la structure pendant le calcul ? Une courbe donne un canal à
   la fois ; une animation montre ensemble le rotor qui tourne, la tour qui fléchit, la plateforme qui
   bouge et la surface libre, c'est-à-dire la **cinématique** : qui bouge, dans quel sens, avec quel
   déphasage. Elle sert à repérer un mouvement incohérent (une pale qui traverse la tour, une
   plateforme qui dérive) avant de lire le moindre canal.
2. **Modèle** — OpenFAST (`WrVTK = 2`) écrit, tous les `1/VTK_fps` secondes de temps simulé, la
   position des nœuds de chaque maillage (pales, moyeu, nacelle, tour, sous-structure, surface libre) :
   un fichier `.vtp` par maillage et par image. Le rendu ne calcule rien de physique : il lit ces
   positions et les dessine, caméra fixe (calée sur l'image 0), **éclairage plat** (ambiant 1, diffus 0, pas de spéculaire)
   pour que chaque objet garde exactement sa couleur de la charte, sur fond blanc ; une pièce en
   **CORAIL** (l'accent de la charte) est un maillage non répertorié, à regarder avec prudence (le
   gris est réservé à la provenance). Facteur
   d'amplification `N` : la structure (tour, sous-structure) est dessinée à `p₀ + N·(p − p₀)` où `p₀`
   est sa position à l'image 0 — seul le déplacement **depuis l'image 0** est amplifié, un décalage
   déjà présent à l'image 0 ne l'est pas, et une rotation de corps rigide (plateforme) est étirée
   au lieu d'être tournée ; rotor et nacelle sont translatés de `(N − 1)` fois le déplacement du
   sommet de tour (leur rotation propre n'est pas amplifiée) ; la surface libre ne l'est pas. Un maillage
   de nom inconnu serait traité comme rotor (translaté), ce qui est faux pour une ligne d'ancrage ou
   une plateforme flottante : `N ≠ 1` est donc **refusé** (`ValueError`, avant tout rendu) si un maillage
   de la série n'est pas dans la liste vérifiée sur `modele_fixe` (`visu.MAILLAGES_VERIFIES` : pales,
   moyeu, nacelle, tour, Morison, surface libre, plans statiques). Avec `N = 1` (défaut), rien n'est
   modifié ni contrôlé. **Domaine de validité** : maillages `.vtp` d'OpenFAST, surfaces (`VTK_type = 1`) ou
   lignes (`VTK_type = 2`, repli, noms `ED_Tower…` ; rendus à `N = 1` seulement, ces noms
   n'étant pas dans la liste vérifiée), nommés `<racine>.<maillage>.<NNN>.vtp` ; un seul rotor ; le maillage de
   tour sert de référence cinématique (son anneau le plus haut).
3. **Ordre de grandeur attendu** — la méthode : avant de lancer, calculer l'angle que le rotor
   parcourt entre deux images, `Ω / VTK_fps` (Ω en rad/s, lu dans `RotSpeed` du cas ou prévu par
   `λ·V/R`, fiche F1), et le comparer à **60°** : trois pales identiques redonnent la même image tous
   les 120°, donc la limite de Shannon est 120°/2 ; au-delà de 60° par image le rotor paraît déjà
   tourner à l'envers, et il paraît immobile à 120° ; puis estimer le volume : (nombre de
   maillages) × (images) × (taille d'un fichier), et le mesurer sur 10 s avant de lancer plus long.
   Après le rendu, vérifier à quelques instants que le déplacement du sommet de tour, relevé dans
   la série VTK par rapport à l'image 0, est du même ordre que celui des canaux (`TTDspFA` plus
   le mouvement de la plateforme), pas un multiple.
4. **Ce que le modèle ne permet pas de conclure** — (a) Une animation montre une **cinématique
   calculée**, pas un mouvement mesuré : elle ne valide pas le modèle, elle montre ce que le modèle
   fait ; qu'elle « ait l'air juste » ne dit rien de l'exactitude des efforts ni des fréquences.
   (b) L'**amplification déforme la perception** : à `N > 1`, des flèches de quelques millimètres
   paraissent des centimètres, la tour semble flexible, et les rapports entre déplacement et
   dimensions de l'objet sont faux ; le facteur doit être lu dans la ligne de provenance, sur chaque
   image. (c) Le pas `VTK_fps` **échantillonne** le mouvement : une oscillation de fréquence
   supérieure à `VTK_fps / 2` est repliée (Shannon) et paraît lente, voire immobile ou inversée —
   l'effet « roue de chariot » : pour un rotor à trois pales identiques, dès que la rotation par
   image dépasse 60°.
   Une animation lisse n'est donc pas la preuve qu'il n'y a pas de mouvement rapide. (d) Une image
   unique ne dit ni l'amplitude ni la fréquence : on lit les courbes pour cela.
5. **Renvois** — fiche F1 (seule fiche existante à ce jour ; choisie parce qu'elle donne `Ω = λ·V/R`
   et la lecture de `RotSpeed`, qui permettent de prévoir l'angle tourné par image et de détecter le
   repliement avant de regarder la vidéo ; les fiches de dynamique de structure, quand elles existeront,
   seront à ajouter pour la lecture de `TTDspFA` et de la plateforme) ; `s9gm/visu.py` (bloc Théorie :
   provenance, charte, porte pédagogique) ; `s9gm/REGISTRE_FIGURES.md` (`FIG:S9GM-VISU-007`) ; manuel
   OpenFAST v5.0.0, section « Visualization » ; `INSTALLATION.md` (ParaView, ffmpeg).
"""
import argparse
import glob
import json
import os
import re

from paraview.simple import (CreateView, Delete, Render, SaveScreenshot, Show, Text, XMLPolyDataReader,
                             ProgrammableFilter)
from paraview import servermanager

# Palette de la charte (voir `s9gm.visu.CHARTE`) en RVB 0-1. Recopiée, car ce script ne peut pas
# importer `s9gm` ; un test (`test_animation`) vérifie que les images restent dans l'enveloppe de la charte.
def _rgb(h):
    return [int(h[i:i + 2], 16) / 255.0 for i in (1, 3, 5)]


MARINE, TEALD, TEAL = _rgb("#1A346D"), _rgb("#147A6D"), _rgb("#1A9988")
GREY, LIGHT, BLANC = _rgb("#595959"), _rgb("#A9D5E2"), _rgb("#FFFFFF")
CORAIL = _rgb("#EB5600")   # accent unique de la charte : ici, « maillage non répertorié »

# Maillage → (couleur, rôle). Rôles : "structure" (amplifiée par p0 + N(p - p0)), "rotor" (translaté),
# "eau" (jamais amplifié). Un maillage inconnu est dessiné en CORAIL, comme « rotor » (GREY est réservé
# à la provenance et aux crédits : un maillage gris serait pris pour du texte de provenance).
COULEURS = {"Blade": (TEAL, "rotor"), "Hub": (MARINE, "rotor"), "Nacelle": (TEALD, "rotor"),
            "Tower": (MARINE, "structure"), "Morison": (TEALD, "structure"),
            "Wave": (LIGHT, "eau")}
IGNORES = ("Seabed", "StillWater")   # plans statiques sans numéro : hors cadre, inutiles à la lecture

SCRIPT_STRUCTURE = """
from vtkmodules.vtkCommonCore import vtkPoints
inp = self.GetInputDataObject(0, 0)
ref = self.GetInputDataObject(0, 1)
out = self.GetPolyDataOutput()
out.ShallowCopy(inp)
pts = vtkPoints()
n = inp.GetNumberOfPoints()
pts.SetNumberOfPoints(n)
for i in range(n):
    p = inp.GetPoint(i); r = ref.GetPoint(i)
    pts.SetPoint(i, r[0] + %(N)r * (p[0] - r[0]), r[1] + %(N)r * (p[1] - r[1]), r[2] + %(N)r * (p[2] - r[2]))
out.SetPoints(pts)
"""
SCRIPT_TRANSLATION = """
from vtkmodules.vtkCommonCore import vtkPoints
inp = self.GetInputDataObject(0, 0)
out = self.GetPolyDataOutput()
out.ShallowCopy(inp)
pts = vtkPoints()
n = inp.GetNumberOfPoints()
pts.SetNumberOfPoints(n)
for i in range(n):
    p = inp.GetPoint(i)
    pts.SetPoint(i, p[0] + %(dx)r, p[1] + %(dy)r, p[2] + %(dz)r)
out.SetPoints(pts)
"""


def trouver_series(dossier):
    """{maillage: [fichiers triés]} pour les séries numérotées ; les plans statiques sont ignorés."""
    series = {}
    for f in sorted(glob.glob(os.path.join(dossier, "*.vtp"))):
        m = re.fullmatch(r"(.+)\.(\d+)\.vtp", os.path.basename(f))
        if m:
            series.setdefault(m[1].split(".", 1)[-1], []).append(f)
    return {k: v for k, v in series.items() if not k.startswith(IGNORES) and not k.endswith("_Reference")}


def style(nom):
    """Couleur et rôle d'un maillage d'après son nom : « TowerSurface1 » (VTK_type 1) comme
    « ED_TowerLn2Mesh_motion_R1 » (VTK_type 2) contiennent « Tower »."""
    for motif, (couleur, role) in COULEURS.items():
        if motif in nom:
            return couleur, role
    return CORAIL, "rotor"


def lire_points(proxy, indices):
    """Barycentre des points `indices` d'un maillage lu (coordonnées VTK, en m)."""
    proxy.UpdatePipeline()
    d = servermanager.Fetch(proxy)
    s = [0.0, 0.0, 0.0]
    for i in indices:
        p = d.GetPoint(i)
        s = [s[0] + p[0], s[1] + p[1], s[2] + p[2]]
    return [c / len(indices) for c in s]


def anneau_haut(fichier):
    """Indices des points du maillage de tour à la cote maximale (anneau de sommet), à 0,1 mm près."""
    r = XMLPolyDataReader(FileName=[fichier])
    r.UpdatePipeline()
    d = servermanager.Fetch(r)
    z = [d.GetPoint(i)[2] for i in range(d.GetNumberOfPoints())]
    Delete(r)
    zmax = max(z)
    return [i for i, v in enumerate(z) if v > zmax - 1e-4]


def fixer_eclairage(rep, mode):
    if mode == "plat":
        rep.Ambient, rep.Diffuse, rep.Specular = 1.0, 0.0, 0.0
    else:   # "relief" : sert uniquement à falsifier le test de charte
        rep.Ambient, rep.Diffuse, rep.Specular = 0.2, 1.0, 0.6


def colorer(rep, couleur):
    rep.LineWidth = 3.0     # maillages de lignes (VTK_type 2) : trait lisible ; sans effet sur les surfaces
    rep.PointSize = 5.0
    rep.ColorArrayName = [None, ""]
    rep.AmbientColor = couleur
    rep.DiffuseColor = couleur


def texte(vue, contenu, couleur, taille, lieu):
    t = Text(Text=contenu)
    rep = Show(t, vue)
    rep.Color = couleur
    rep.FontSize = taille
    try:
        rep.WindowLocation = lieu
    except Exception:   # graphie sans espace, par prudence (non vérifiée sur 5.11)
        rep.WindowLocation = lieu.replace(" ", "")
    return t


def principal():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vtk", required=True)
    ap.add_argument("--sortie", required=True)
    ap.add_argument("--provenance", required=True)
    ap.add_argument("--fps", type=float, default=0.0)   # 0 : pas d'horloge incrustée
    ap.add_argument("--amplification", type=float, default=1.0)
    ap.add_argument("--eclairage", choices=("plat", "relief"), default="plat")
    ap.add_argument("--resolution", default="1280x720")
    ap.add_argument("--pas", type=int, default=1)
    ap.add_argument("--trace")
    ap.add_argument("--k-debut", type=int, default=0)     # fenêtre : indices des images VTK (inclus)
    ap.add_argument("--k-fin", type=int)
    a = ap.parse_args()
    largeur, hauteur = (int(v) for v in a.resolution.split("x"))
    N = a.amplification

    series = trouver_series(a.vtk)
    tours = [k for k in series if style(k)[1] == "structure" and "Tower" in k]
    if not series or not tours:
        raise SystemExit(f"ERREUR : pas de série VTK de tour dans {a.vtk} (WrVTK = 2 ? VTK_type = 1 ?)")
    nb = min(len(v) for v in series.values())
    anneau = anneau_haut(series[tours[0]][0])
    r0 = XMLPolyDataReader(FileName=[series[tours[0]][0]])
    c0 = lire_points(r0, anneau)
    Delete(r0)

    vue = CreateView("RenderView")
    vue.ViewSize = [largeur, hauteur]
    vue.Background = BLANC
    for attr, val in (("UseColorPaletteForBackground", 0), ("OrientationAxesVisibility", 0)):
        try:
            setattr(vue, attr, val)
        except Exception:
            pass

    # Caméra fixe, calée sur l'image 0 hors surface libre (qui peut être très étendue).
    bornes = None
    for nom, fichiers in series.items():
        if style(nom)[1] == "eau":
            continue
        r = XMLPolyDataReader(FileName=[fichiers[0]])
        r.UpdatePipeline()
        b = r.GetDataInformation().GetBounds()
        bornes = list(b) if bornes is None else [min(bornes[0], b[0]), max(bornes[1], b[1]),
                                                  min(bornes[2], b[2]), max(bornes[3], b[3]),
                                                  min(bornes[4], b[4]), max(bornes[5], b[5])]
        Delete(r)
    centre = [(bornes[0] + bornes[1]) / 2, (bornes[2] + bornes[3]) / 2, (bornes[4] + bornes[5]) / 2]
    rayon = 0.5 * ((bornes[1] - bornes[0]) ** 2 + (bornes[3] - bornes[2]) ** 2
                   + (bornes[5] - bornes[4]) ** 2) ** 0.5
    d = 1.15 * rayon / 0.2588   # sin(15°) : demi-angle de vue de 30°
    direction = [-0.55, -0.75, 0.30]
    n = sum(v * v for v in direction) ** 0.5
    vue.CameraFocalPoint = centre
    vue.CameraPosition = [centre[i] + d * direction[i] / n for i in range(3)]
    vue.CameraViewUp = [0, 0, 1]
    vue.CameraViewAngle = 30

    os.makedirs(a.sortie, exist_ok=True)
    trace = {"images": [], "sommet": [], "sommet_ref": c0, "amplification": N, "fps": a.fps, "horloges": []}
    k_fin = nb - 1 if a.k_fin is None else min(a.k_fin, nb - 1)
    for k in range(a.k_debut, k_fin + 1, a.pas):
        sources = []
        # déplacement du sommet de tour à l'image k, lu dans le VTK (avant toute amplification)
        rt = XMLPolyDataReader(FileName=[series[tours[0]][k]])
        ck = lire_points(rt, anneau)
        Delete(rt)
        dk = [ck[i] - c0[i] for i in range(3)]
        for nom, fichiers in series.items():
            couleur, role = style(nom)
            lec = XMLPolyDataReader(FileName=[fichiers[k]])
            amont = lec
            if N != 1 and role == "structure":
                ref = XMLPolyDataReader(FileName=[fichiers[0]])
                amont = ProgrammableFilter(Input=[lec, ref])
                amont.OutputDataSetType = "vtkPolyData"
                amont.Script = SCRIPT_STRUCTURE % {"N": N}
                sources += [ref]
            elif N != 1 and role == "rotor":
                amont = ProgrammableFilter(Input=[lec])
                amont.OutputDataSetType = "vtkPolyData"
                amont.Script = SCRIPT_TRANSLATION % {"dx": (N - 1) * dk[0], "dy": (N - 1) * dk[1],
                                                     "dz": (N - 1) * dk[2]}
            rep = Show(amont, vue)
            colorer(rep, couleur)
            fixer_eclairage(rep, a.eclairage)
            sources += [lec] + ([amont] if amont is not lec else [])
            if nom == tours[0]:
                trace["images"].append(k)
                trace["sommet"].append(lire_points(amont, anneau))
        textes = [texte(vue, a.provenance, GREY, 11, "Lower Center")]
        horloge = f"t = {k / a.fps:.2f} s" if a.fps > 0 else ""   # temps de CALCUL, pas depuis la fenêtre
        trace["horloges"].append(horloge)
        if a.fps > 0:
            textes.append(texte(vue, horloge, MARINE, 14, "Upper Left Corner"))
        Render(vue)
        SaveScreenshot(os.path.join(a.sortie, f"image_{k:04d}.png"), vue,
                       ImageResolution=[largeur, hauteur], TransparentBackground=0)
        for s in textes:
            Delete(s)
        for s in reversed(sources):
            Delete(s)
    if a.trace:
        with open(a.trace, "w", encoding="utf-8") as f:
            json.dump(trace, f)
    print(f"IMAGES {len(trace['images'])}")


if __name__ == "__main__":
    principal()
