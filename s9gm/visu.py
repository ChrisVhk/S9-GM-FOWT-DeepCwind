"""s9gm.visu — tracer des séries et des statistiques à la charte ENSM, avec leur provenance ; animer.

### Bloc Théorie

1. **Question physique** — Une courbe est un argument : que doit-elle montrer, et à qui ? Un
   graphique d'ingénieur qu'on ne peut pas rattacher à un cas, un modèle et un état de calcul n'est
   pas une preuve — c'est une illustration. Et certains graphiques répondraient à une question
   notée avant que l'étudiant l'ait traitée.
2. **Modèle** — chaque figure porte une **ligne de provenance incrustée** (`cas · … · modèle · … ·
   état · …`) : sans elle, le tracé est refusé (les trois champs sont des arguments obligatoires).
   Les couleurs sont celles de la charte ENSM, rien d'autre : MARINE, TEALD, TEAL pour les
   données, GREY pour la provenance, LIGHT/PALE en fond. L'option `masquer_ordonnees` retire les
   graduations de l'axe vertical : on voit l'**allure** (établi, transitoire, dépassement), pas la
   **valeur**. Une figure n'est livrée (`enregistrer`) que si le registre
   `s9gm/REGISTRE_FIGURES.md` porte, pour son identifiant, la réponse écrite à « qu'apprend cette
   image à un étudiant qui ne connaît pas le cas ? ». **Domaine de validité** : séries issues de
   `s9gm.lire` (colonne `Time` en secondes) ; au plus six canaux par figure. `tracer_courbes` :
   comparaisons y(x) (main / calcul / valeurs publiées), la forme du trait distinguant les sources.
   **Volet animation** (`animer`, détails dans `_rendu_vtk.py`) : trois étapes appelables seules —
   `preparer_animation` (3 clés du `.fst`), `rendre` (`pvbatch` en sous-processus, une image par pas),
   `monter` (`ffmpeg`, H.264 `yuv420p`). La provenance est incrustée dans **chaque image** ; éclairage
   plat, couleurs de la charte, fond blanc ; amplification des déplacements ×1 par défaut, écrite dans
   la provenance dès qu'elle diffère de 1 (« déplacements ×N ») ; `fenetre=(t_debut, t_fin)` n'anime que cet
   intervalle du temps de calcul (voir `lire.debut_regime`) ; vidéo livrée seulement si
   `FIG:S9GM-VISU-007` a sa porte pédagogique.
3. **Ordre de grandeur attendu** — la méthode : avant de tracer, écrire la question à laquelle le
   graphique répond ; après, vérifier qu'un lecteur qui n'a jamais vu le cas peut la retrouver sans
   la légende orale. Pour un graphique qui répond à une question notée, demander
   `masquer_ordonnees=True` et vérifier qu'aucune valeur n'est lisible. Pour une animation : prévoir
   le volume avant de lancer (maillages × images × taille d'un fichier, à mesurer sur un cas court) et
   l'angle tourné par le rotor entre deux images (`Ω / VTK_fps`, `Ω` lu dans `RotSpeed` ou prévu par
   la fiche F1), à comparer à 60° (trois pales identiques : repli de Shannon au-delà).
4. **Ce que le modèle ne permet pas de conclure** — qu'une figure soit juste parce qu'elle est
   jolie ou conforme à la charte : la charte garantit la lisibilité, pas l'exactitude des données ;
   et masquer les ordonnées cache la valeur, pas le fait que la courbe existe. Une animation montre
   une **cinématique calculée**, non une validation ; l'amplification des déplacements déforme la
   perception (d'où la mention sur chaque image) ; le pas `VTK_fps` échantillonne le mouvement et peut
   replier une oscillation plus rapide que `VTK_fps / 2` (Shannon), jusqu'à faire paraître un rotor
   immobile ou à l'envers.
5. **Renvois** — fiche F1 (lire une courbe de régulation sans en connaître la valeur) ;
   la charte graphique du cours (tableau de charte) ; `seances/0a/README.md`
   (vérifications à la main avant de regarder la valeur). Animation : fiche F1 aussi, seule fiche
   existante, qui donne `Ω = λ·V/R` pour prévoir l'angle par image ; voir le bloc de `_rendu_vtk.py`.
"""
import argparse
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Palette de la charte (tableau « Charte appliquée » de NOTE_GABARIT_PPTX.md) + blanc de fond.
CHARTE = {"MARINE": "#1A346D", "TEALD": "#147A6D", "TEAL": "#1A9988", "GREY": "#595959",
          "LIGHT": "#A9D5E2", "PALE": "#E8F4F2", "BLANC": "#FFFFFF"}
COULEURS_DONNEES = [CHARTE["MARINE"], CHARTE["TEALD"], CHARTE["TEAL"]]
REGISTRE = Path(__file__).with_name("REGISTRE_FIGURES.md")
ID_ANIMATION = "FIG:S9GM-VISU-007"
RENDU_VTK = Path(__file__).with_name("_rendu_vtk.py")

_RC = {"font.family": "DejaVu Sans", "font.size": 10, "text.color": CHARTE["MARINE"],
       "axes.edgecolor": CHARTE["MARINE"], "axes.labelcolor": CHARTE["MARINE"],
       "xtick.color": CHARTE["MARINE"], "ytick.color": CHARTE["MARINE"],
       "figure.facecolor": CHARTE["BLANC"], "axes.facecolor": CHARTE["BLANC"],
       "savefig.facecolor": CHARTE["BLANC"], "grid.color": CHARTE["LIGHT"], "grid.linewidth": 0.5, "grid.alpha": 0.6, "axes.grid": True,
       "svg.fonttype": "none"}


def ligne_provenance(cas, modele, etat, amplification=1):
    """`cas · X  ·  modèle · Y  ·  état · Z` — même format que FIG-DMO-S9-001/002. Si `amplification`
    (facteur sur les déplacements d'une animation) diffère de 1, la ligne finit par `déplacements ×N`."""
    for nom, v in (("cas", cas), ("modèle", modele), ("état", etat)):
        if not str(v).strip():
            raise ValueError(f"provenance incomplète : {nom} vide")
    if not amplification > 0:
        raise ValueError("amplification : un facteur strictement positif est attendu")
    ligne = f"cas · {cas}  ·  modèle · {modele}  ·  état · {etat}"
    return ligne if amplification == 1 else f"{ligne}  ·  déplacements ×{amplification:g}"


def _habiller(fig, axes, provenance, masquer_ordonnees):
    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
        if masquer_ordonnees:
            ax.set_yticks([])
    fig.text(0.5, 0.012, provenance, ha="center", va="bottom", fontsize=7, color=CHARTE["GREY"])
    fig.tight_layout(rect=(0, 0.04, 1, 1))


def tracer_series(df, canaux, *, cas, modele, etat, t_transitoire=None, masquer_ordonnees=False,
                  titre=None):
    """Un panneau par canal, partagé en temps. `df` vient de `s9gm.lire.lire`.

    `cas`, `modele`, `etat` sont obligatoires : ils composent la ligne de provenance incrustée.
    Si `t_transitoire` est donné, la zone écartée est teintée (fond LIGHT) : on *voit* ce que les
    statistiques ignorent. Renvoie la figure matplotlib."""
    provenance = ligne_provenance(cas, modele, etat)
    if not 1 <= len(canaux) <= 6:
        raise ValueError("entre 1 et 6 canaux par figure")
    with plt.rc_context(_RC):
        fig, axes = plt.subplots(len(canaux), 1, sharex=True, squeeze=False,
                                 figsize=(8, 1.9 * len(canaux) + 0.9))
        axes = axes[:, 0]
        t = df["Time"].to_numpy()
        for i, (ax, c) in enumerate(zip(axes, canaux)):
            ax.plot(t, df[c].to_numpy(), color=COULEURS_DONNEES[i % 3], lw=1.1)
            ax.set_ylabel(c)
            if t_transitoire:
                ax.axvspan(t[0], t_transitoire, color=CHARTE["LIGHT"], alpha=0.5, lw=0)
        axes[-1].set_xlabel("temps (s)")
        if titre:
            axes[0].set_title(titre, fontsize=10.5)
        _habiller(fig, axes, provenance, masquer_ordonnees)
    return fig


def tracer_statistiques(stats_par_cas, canal, *, modele, etat, masquer_ordonnees=False,
                        titre=None):
    """Moyenne (barre), ± écart-type (trait) et min–max (traits fins) d'un canal, un cas par barre.

    `stats_par_cas` : dict `nom du cas -> DataFrame de s9gm.lire.statistiques`. La provenance
    liste les cas tracés."""
    provenance = ligne_provenance(", ".join(stats_par_cas), modele, etat)
    with plt.rc_context(_RC):
        fig, ax = plt.subplots(figsize=(6.5, 3.8))
        for i, (nom, st) in enumerate(stats_par_cas.items()):
            m, s = st.loc[canal, "moyenne"], st.loc[canal, "ecart_type"]
            ax.bar(i, m, color=CHARTE["TEAL"], width=0.55)
            ax.errorbar(i, m, yerr=s, color=CHARTE["MARINE"], capsize=5, lw=1.4)
            ax.vlines(i, st.loc[canal, "min"], st.loc[canal, "max"], color=CHARTE["MARINE"],
                      lw=0.6, linestyles="dotted")
        ax.set_xticks(range(len(stats_par_cas)), list(stats_par_cas))
        ax.set_ylabel(f"{canal} : moyenne, ± σ, min–max")
        if titre:
            ax.set_title(titre, fontsize=10.5)
        _habiller(fig, [ax], provenance, masquer_ordonnees)
    return fig


_STYLES = {"ligne": dict(ls="-", lw=1.4), "tirets": dict(ls="--", lw=1.4),
           "points": dict(ls="none", marker="o", ms=4.5)}


def tracer_courbes(panneaux, *, xlabel, cas, modele, etat, titre=None, masquer_ordonnees=False):
    """Courbes y(x) superposées (un panneau par grandeur, abscisse partagée) : la comparaison
    main / OpenFAST / valeurs publiées du notebook de la séance 0b, hors série temporelle.

    `panneaux` : liste de dicts `{"ylabel": str, "courbes": [{"label", "x", "y", "style"}, ...],
    "reperes": {nom: x}}` ; `style` ∈ {"ligne", "tirets", "points"} (la forme, pas seulement la
    couleur, distingue les courbes) ; `reperes` (optionnel) trace un trait vertical nommé.
    Provenance obligatoire, charte seule, au plus six panneaux. Renvoie la figure."""
    provenance = ligne_provenance(cas, modele, etat)
    if not 1 <= len(panneaux) <= 6:
        raise ValueError("entre 1 et 6 panneaux par figure")
    with plt.rc_context(_RC):
        fig, axes = plt.subplots(len(panneaux), 1, sharex=True, squeeze=False,
                                 figsize=(8, 2.6 * len(panneaux) + 0.9))
        axes = axes[:, 0]
        for ax, pan in zip(axes, panneaux):
            for i, c in enumerate(pan["courbes"]):
                ax.plot(c["x"], c["y"], color=COULEURS_DONNEES[i % 3], label=c["label"],
                        **_STYLES[c.get("style", "ligne")])
            for nom, x in pan.get("reperes", {}).items():
                ax.axvline(x, color=CHARTE["GREY"], lw=0.8, ls=":")
                ax.text(x, 1.0, nom, transform=ax.get_xaxis_transform(), fontsize=7.5,
                        color=CHARTE["GREY"], ha="center", va="bottom")
            ax.set_ylabel(pan["ylabel"])
            ax.legend(fontsize=8, frameon=False)
        axes[-1].set_xlabel(xlabel)
        if titre:
            axes[0].set_title(titre, fontsize=10.5, pad=14)
        _habiller(fig, axes, provenance, masquer_ordonnees)
    return fig


def porte_pedagogique(id_figure, registre=REGISTRE):
    """Texte de la porte pédagogique de `id_figure` dans le registre, ou None."""
    if not Path(registre).is_file():
        return None
    texte = Path(registre).read_text(encoding="utf-8")
    m = re.search(r"^\*\*" + re.escape(id_figure) + r"\*\*[^\n]*\n(?P<rep>(?:[^\n]+\n?)+)", texte,
                  re.MULTILINE)
    return m["rep"].strip() if m else None


def _exiger_porte(id_figure, registre):
    porte = porte_pedagogique(id_figure, registre)
    if not porte or len(porte) < 40:
        raise PermissionError(
            f"{id_figure} : pas de porte pédagogique dans {Path(registre).name} — "
            "figure non livrée (écrivez la réponse à « qu'apprend cette image à un étudiant "
            "qui ne connaît pas le cas ? » d'abord)")


def enregistrer(fig, chemin, id_figure, registre=REGISTRE):
    """Écrit la figure — seulement si le registre porte sa porte pédagogique (≥ 40 caractères)."""
    _exiger_porte(id_figure, registre)
    from . import chemins as _ch
    chemin = _ch.assurer_parent(chemin)               # relatif : à partir de la racine du dépôt ; le dossier se crée
    with plt.rc_context(_RC):
        fig.savefig(chemin, dpi=150)
    return chemin


# ---------------------------------------------------------------------------------------------
# Animation : préparer (.fst) → rendre (pvbatch) → monter (ffmpeg)
# ---------------------------------------------------------------------------------------------
class OutilAbsent(RuntimeError):
    """Un outil externe (pvbatch, ffmpeg) manque : le message dit quoi faire, sans trace illisible."""


def _outil(nom, paquet):
    chemin = shutil.which(nom)
    if chemin is None:
        raise OutilAbsent(f"{nom} introuvable dans le PATH. Installation : `sudo apt install {paquet}` "
                          "(geste de l'administrateur de la machine) — voir INSTALLATION.md, "
                          "section 5 « Animation (facultatif) : ParaView et ffmpeg ».")
    return chemin


def preparer_animation(dossier_cas, *, vtk_type=1, vtk_fps=5, fst="main.fst"):
    """Règle `WrVTK = 2`, `VTK_type` (1 = surfaces ; 2 = lignes et points, en repli) et `VTK_fps` dans le
    `.fst` du cas, et rien d'autre. Relecture indépendante par `openfast_toolbox` (comme `s9gm.cas`).
    Renvoie `{clé: ancienne valeur}`. Attention : OpenFAST arrondit l'intervalle entre images au multiple
    entier du pas `DT` le plus proche de `1 / VTK_fps` ; si `1 / (VTK_fps·DT)` n'est pas entier, la
    cadence réelle diffère de `VTK_fps` (jusqu'à plusieurs %) et l'erreur sur l'instant de l'image `k`
    croît avec `k`. Choisir `VTK_fps` tel que `1 / (VTK_fps·DT)` soit entier ; ce n'est pas contrôlé ici."""
    from . import cas as _cas
    if int(vtk_type) != vtk_type or vtk_type not in (1, 2):
        raise ValueError("vtk_type : 1 (surfaces) ou 2 (lignes et points, repli)")
    if not vtk_fps > 0:
        raise ValueError("vtk_fps : un nombre d'images par seconde strictement positif est attendu")
    voulu = {"WrVTK": "2", "VTK_type": str(int(vtk_type)), "VTK_fps": f"{vtk_fps:g}"}
    from . import chemins as _ch
    chemin = _ch.resoudre(dossier_cas) / fst
    lignes, fin = _cas._lire_lignes(chemin)
    anciennes = {cle: _cas._sans_guillemets(_cas.remplacer_valeur(lignes, cle, val))
                 for cle, val in voulu.items()}
    _cas._ecrire_lignes(chemin, lignes, fin)
    _cas._controler_relecture(chemin, voulu)
    return anciennes


def _fps_du_cas(dossier_cas, fst="main.fst"):
    from . import cas as _cas
    lignes, _ = _cas._lire_lignes(Path(dossier_cas) / fst)
    return float(_cas._sans_guillemets(_cas._valeur_de(lignes, "VTK_fps")))


# Maillages vus et vérifiés sur `modeles/fixe` (VTK_type = 1) : seuls ceux-là peuvent être amplifiés.
# Noms exacts, sans sous-chaîne : « TowerSurface2 » n'est pas « TowerSurface1 ».
MAILLAGES_VERIFIES = (r"Blade_R1B[123]Surface", r"HubSurface1", r"NacelleSurface1", r"TowerSurface1",
                      r"MorisonSurface", r"WaveSurface", r"SeabedSurface", r"StillWaterSurface")


def verifier_amplification(dossier_vtk, amplification):
    """À `amplification` ≠ 1, refuse (ValueError) toute série où un maillage n'est pas dans
    `MAILLAGES_VERIFIES` : un maillage inconnu (ancrage, plateforme flottante…) serait translaté comme un
    rotor, ce qui est faux. À `amplification` = 1, ne contrôle rien. Ne lit que les noms de fichiers."""
    if amplification == 1:
        return
    noms = {m[1] for f in Path(dossier_vtk).glob("*.vtp")
            if (m := re.fullmatch(r"[^.]+\.(.+?)(?:\.\d+)?\.vtp", f.name))}
    if not noms:
        raise ValueError(f"{dossier_vtk} : aucune série VTK reconnue, amplification ×{amplification:g} refusée "
                         "(N = 1 reste possible)")
    inconnus = sorted(n for n in noms if not any(re.fullmatch(p, n) for p in MAILLAGES_VERIFIES))
    if inconnus:
        raise ValueError(
            f"amplification ×{amplification:g} refusée : maillage(s) non vérifié(s) {', '.join(inconnus)} "
            "(ancrage, plateforme, ou autre : l'amplification de leur mouvement n'est validée que pour les "
            "pales, le moyeu, la nacelle, la tour, Morison et la surface libre de modeles/fixe). "
            "N = 1 reste possible.")


def _nb_pas_vtk(dossier_vtk):
    """Nombre d'images VTK de la série : le plus petit nombre de fichiers numérotés d'un maillage."""
    n = {}
    for f in Path(dossier_vtk).glob("*.vtp"):
        m = re.fullmatch(r"[^.]+\.(.+?)\.\d+\.vtp", f.name)
        if m and not m[1].endswith("_Reference"):
            n[m[1]] = n.get(m[1], 0) + 1
    return min(n.values()) if n else 0


def _indices_fenetre(dossier_vtk, fenetre, fps):
    """`(k_debut, k_fin)` : indices des images VTK dont l'instant `k / fps` est dans `fenetre` = `(t_debut,
    t_fin)` en secondes de TEMPS DE CALCUL. Refuse une fenêtre mal formée, vide ou hors de la série."""
    if not (isinstance(fenetre, (tuple, list)) and len(fenetre) == 2):
        raise ValueError("fenêtre : un couple (t_debut, t_fin) en secondes est attendu")
    t0, t1 = fenetre
    if not t1 >= t0:
        raise ValueError(f"fenêtre ({t0:g}, {t1:g}) : t_fin doit être >= t_debut")
    if not fps or fps <= 0:
        raise ValueError("fenêtre : la cadence VTK_fps du cas est nécessaire (argument fps, ou main.fst à côté de vtk/)")
    nb = _nb_pas_vtk(dossier_vtk)
    if nb == 0:
        raise ValueError(f"fenêtre : aucune série VTK dans {dossier_vtk}")
    k0, k1 = math.ceil(t0 * fps - 1e-9), math.floor(t1 * fps + 1e-9)
    if t0 < 0 or k1 > nb - 1 or k1 < k0:
        raise ValueError(f"fenêtre ({t0:g}, {t1:g}) s hors de la série ({0:g} à {(nb - 1) / fps:g} s, "
                         f"{nb} images à {fps:g} images/s)")
    return k0, k1


def rendre(dossier_vtk, dossier_png, *, cas, modele, etat, amplification=1, eclairage="plat",
           resolution=(1280, 720), pas=1, trace=None, fps=None, fenetre=None):
    """`pvbatch` lit la série VTK de `dossier_vtk` et écrit `dossier_png/image_NNNN.png`, une image par
    pas (`pas > 1` : une image sur `pas`, pour un essai). `cas`, `modele`, `etat` sont obligatoires : la
    ligne de provenance est incrustée dans chaque image. `eclairage` : "plat" (charte) ou "relief"
    (ombrage, réservé au falsificateur de charte). `trace` : chemin d'un JSON qui reçoit la position du
    sommet de tour réellement dessinée, image par image. `fenetre=(t_debut, t_fin)` (s, temps de calcul) ne rend
    que les images VTK dans cet intervalle ; absente, toute la série (comportement inchangé). L'horloge
    incrustée est le temps du calcul, jamais le temps depuis le début de la fenêtre. `amplification` ≠ 1 : voir
    `verifier_amplification`. `fps` : cadence VTK du cas (horloge `t = k/fps`
    incrustée) ; par défaut lue dans le `.fst`. Renvoie la liste des PNG."""
    provenance = ligne_provenance(cas, modele, etat, amplification)
    if eclairage not in ("plat", "relief"):
        raise ValueError("eclairage : 'plat' ou 'relief'")
    if pas < 1:
        raise ValueError("pas >= 1")
    verifier_amplification(dossier_vtk, amplification)   # avant tout outil, tout dossier, tout rendu
    dossier_vtk, dossier_png = Path(dossier_vtk), Path(dossier_png)
    if fps is None:
        try:
            fps = _fps_du_cas(dossier_vtk.parent)
        except (OSError, KeyError):
            fps = 0.0
    indices = _indices_fenetre(dossier_vtk, fenetre, fps) if fenetre is not None else None
    pvbatch = _outil("pvbatch", "paraview")
    if not dossier_vtk.is_dir():
        raise FileNotFoundError(f"{dossier_vtk} : pas de série VTK (WrVTK = 2 dans le .fst, calcul lancé ?)")
    dossier_png.mkdir(parents=True, exist_ok=True)
    for ancien in dossier_png.glob("image_*.png"):   # pas d'image d'un rendu précédent dans la série
        ancien.unlink()
    cmd = [pvbatch, str(RENDU_VTK), "--vtk", str(dossier_vtk), "--sortie", str(dossier_png),
           "--provenance", provenance, "--fps", f"{fps:g}", "--amplification", f"{amplification:g}",
           "--eclairage", eclairage, "--resolution", f"{resolution[0]}x{resolution[1]}",
           "--pas", str(pas)] + (["--trace", str(trace)] if trace else []) \
          + (["--k-debut", str(indices[0]), "--k-fin", str(indices[1])] if indices else [])
    r = subprocess.run(cmd, capture_output=True, text=True)
    pngs = sorted(dossier_png.glob("image_*.png"))
    if r.returncode != 0 or not pngs:
        raise RuntimeError(f"pvbatch a échoué (code {r.returncode}) :\n{(r.stdout + r.stderr)[-800:]}")
    return pngs


def verifier_images(dossier_png, n_attendu=None, fond=(255, 255, 255)):
    """Refuse une série d'images inutilisable : nombre différent de `n_attendu` (si donné), ou image
    **uniforme** — une seule couleur, ou scène vide (moins de 0,1 % de pixels différents du fond, l'horloge,
    en haut, et la bande de provenance, en bas, étant exclues). Lève ValueError ; renvoie le nombre d'images."""
    import numpy as np
    from PIL import Image
    pngs = sorted(Path(dossier_png).glob("*.png"))
    if n_attendu is not None and len(pngs) != n_attendu:
        raise ValueError(f"nombre d'images : {len(pngs)} PNG pour {n_attendu} pas VTK")
    if not pngs:
        raise ValueError(f"aucune image dans {dossier_png}")
    for p in pngs:
        a = np.asarray(Image.open(p).convert("RGB"))
        h = a.shape[0]
        scene = a[int(0.08 * h): int(0.9 * h)]   # hors horloge (haut) et provenance (bas)
        if len(np.unique(scene.reshape(-1, 3), axis=0)) < 2 or \
                (scene != np.array(fond)).any(axis=-1).mean() < 1e-3:
            raise ValueError(f"{p.name} : image uniforme (scène vide) — rendu refusé")
    return len(pngs)


def monter(dossier_png, mp4, *, fps, id_figure=ID_ANIMATION, registre=REGISTRE):
    """`ffmpeg` assemble les `*.png` de `dossier_png` en un mp4 H.264 `yuv420p` (lisible par PowerPoint et
    VLC), à `fps` images par seconde. Refusé sans porte pédagogique pour `id_figure`, et si une image est
    uniforme. Renvoie le chemin du mp4."""
    _exiger_porte(id_figure, registre)
    ffmpeg = _outil("ffmpeg", "ffmpeg")
    from . import chemins as _ch
    dossier_png = _ch.resoudre(dossier_png)
    verifier_images(dossier_png)
    mp4 = _ch.resoudre(mp4)
    mp4.parent.mkdir(parents=True, exist_ok=True)
    cmd = [ffmpeg, "-y", "-loglevel", "error", "-framerate", f"{fps:g}", "-pattern_type", "glob",
           "-i", str(Path(dossier_png) / "*.png"), "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-movflags", "+faststart", str(mp4)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not mp4.is_file():
        raise RuntimeError(f"ffmpeg a échoué (code {r.returncode}) :\n{r.stderr[-800:]}")
    return mp4


def animer(*, cas, modele, etat, dossier_cas, sortie, amplification=1, fps=None, eclairage="plat",
           resolution=(1280, 720), id_figure=ID_ANIMATION, registre=REGISTRE, fenetre=None):
    """Rendre puis monter l'animation d'un cas déjà calculé avec `WrVTK = 2` (voir `preparer_animation`) :
    `dossier_cas/vtk/` → images dans `<sortie sans suffixe>_images/` → mp4 `sortie`, lu à `VTK_fps`
    images par seconde (temps réel, si la cadence VTK est bien `VTK_fps`) sauf `fps` donné, qui ne
    change que la vitesse de lecture : l'horloge incrustée reste celle du calcul. `fenetre=(t_debut, t_fin)` :
    n'animer que cet intervalle du temps de calcul (par exemple après le transitoire, voir
    `lire.debut_regime`). Les gardes passent avant tout calcul : provenance
    complète, porte pédagogique de `id_figure`, outils présents. Renvoie le chemin du mp4."""
    ligne_provenance(cas, modele, etat, amplification)
    _exiger_porte(id_figure, registre)
    _outil("pvbatch", "paraview")
    _outil("ffmpeg", "ffmpeg")
    from . import chemins as _ch
    dossier_cas, sortie = _ch.resoudre(dossier_cas), _ch.resoudre(sortie)
    fps_vtk = _fps_du_cas(dossier_cas)
    fps = fps_vtk if fps is None else fps
    images = sortie.with_name(sortie.stem + "_images")
    pngs = rendre(dossier_cas / "vtk", images, cas=cas, modele=modele, etat=etat,
                  amplification=amplification, eclairage=eclairage, resolution=resolution, fps=fps_vtk,
                  fenetre=fenetre)
    if fenetre is None:
        n_vtk = len([f for f in (dossier_cas / "vtk").glob("*.vtp")
                     if re.fullmatch(r".+Tower[^.]*\.\d+\.vtp", f.name)])
    else:
        k0, k1 = _indices_fenetre(dossier_cas / "vtk", fenetre, fps_vtk)
        n_vtk = k1 - k0 + 1
    verifier_images(images, n_vtk)
    return monter(images, sortie, fps=fps, id_figure=id_figure, registre=registre)


def _commande(argv=None):
    ap = argparse.ArgumentParser(prog="python -m s9gm.visu",
                                 description="Animation VTK d'un cas OpenFAST (rendre puis monter).")
    sp = ap.add_subparsers(dest="action", required=True)
    a = sp.add_parser("animer", help="dossier du cas -> mp4")
    a.add_argument("dossier_cas")
    a.add_argument("sortie")
    for o in ("cas", "modele", "etat"):
        a.add_argument(f"--{o}", required=True)
    a.add_argument("--amplification", type=float, default=1.0)
    a.add_argument("--fps", type=float)
    a.add_argument("--fenetre", type=float, nargs=2, metavar=("T_DEBUT", "T_FIN"),
                   help="n'animer que cet intervalle du temps de calcul (s)")
    args = ap.parse_args(argv)
    try:
        mp4 = animer(cas=args.cas, modele=args.modele, etat=args.etat, dossier_cas=args.dossier_cas,
                     sortie=args.sortie, amplification=args.amplification, fps=args.fps,
                     fenetre=tuple(args.fenetre) if args.fenetre else None)
    except (OutilAbsent, PermissionError, ValueError, FileNotFoundError, KeyError, RuntimeError) as e:
        print(f"ERREUR : {e}", file=sys.stderr)
        return 2
    print(mp4)
    return 0


if __name__ == "__main__":
    sys.exit(_commande())
