"""s9gm.visu — tracer des séries et des statistiques à la charte ENSM, avec leur provenance.

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
   `s9gm.lire` (colonne `Time` en secondes) ; au plus six canaux par figure.
3. **Ordre de grandeur attendu** — la méthode : avant de tracer, écrire la question à laquelle le
   graphique répond ; après, vérifier qu'un lecteur qui n'a jamais vu le cas peut la retrouver sans
   la légende orale. Pour un graphique qui répond à une question notée, demander
   `masquer_ordonnees=True` et vérifier qu'aucune valeur n'est lisible.
4. **Ce que le modèle ne permet pas de conclure** — qu'une figure soit juste parce qu'elle est
   jolie ou conforme à la charte : la charte garantit la lisibilité, pas l'exactitude des données ;
   et masquer les ordonnées cache la valeur, pas le fait que la courbe existe.
5. **Renvois** — fiche F1 (lire une courbe de régulation sans en connaître la valeur) ;
   `NOTE_GABARIT_PPTX.md` du dépôt d'enseignement (tableau de charte) ; `ENONCE.md`, phase 0
   (vérifications à la main avant de regarder la valeur).
"""
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Palette de la charte (tableau « Charte appliquée » de NOTE_GABARIT_PPTX.md) + blanc de fond.
CHARTE = {"MARINE": "#1A346D", "TEALD": "#147A6D", "TEAL": "#1A9988", "GREY": "#595959",
          "LIGHT": "#A9D5E2", "PALE": "#E8F4F2", "BLANC": "#FFFFFF"}
COULEURS_DONNEES = [CHARTE["MARINE"], CHARTE["TEALD"], CHARTE["TEAL"]]
REGISTRE = Path(__file__).with_name("REGISTRE_FIGURES.md")

_RC = {"font.family": "DejaVu Sans", "font.size": 10, "text.color": CHARTE["MARINE"],
       "axes.edgecolor": CHARTE["MARINE"], "axes.labelcolor": CHARTE["MARINE"],
       "xtick.color": CHARTE["MARINE"], "ytick.color": CHARTE["MARINE"],
       "figure.facecolor": CHARTE["BLANC"], "axes.facecolor": CHARTE["BLANC"],
       "savefig.facecolor": CHARTE["BLANC"], "grid.color": CHARTE["LIGHT"], "grid.linewidth": 0.5, "grid.alpha": 0.6, "axes.grid": True,
       "svg.fonttype": "none"}


def ligne_provenance(cas, modele, etat):
    """`cas · X  ·  modèle · Y  ·  état · Z` — même format que FIG-DMO-S9-001/002."""
    for nom, v in (("cas", cas), ("modèle", modele), ("état", etat)):
        if not str(v).strip():
            raise ValueError(f"provenance incomplète : {nom} vide")
    return f"cas · {cas}  ·  modèle · {modele}  ·  état · {etat}"


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


def porte_pedagogique(id_figure, registre=REGISTRE):
    """Texte de la porte pédagogique de `id_figure` dans le registre, ou None."""
    if not Path(registre).is_file():
        return None
    texte = Path(registre).read_text(encoding="utf-8")
    m = re.search(r"^\*\*" + re.escape(id_figure) + r"\*\*[^\n]*\n(?P<rep>(?:[^\n]+\n?)+)", texte,
                  re.MULTILINE)
    return m["rep"].strip() if m else None


def enregistrer(fig, chemin, id_figure, registre=REGISTRE):
    """Écrit la figure — seulement si le registre porte sa porte pédagogique (≥ 40 caractères)."""
    porte = porte_pedagogique(id_figure, registre)
    if not porte or len(porte) < 40:
        raise PermissionError(
            f"{id_figure} : pas de porte pédagogique dans {Path(registre).name} — "
            "figure non livrée (écrivez la réponse à « qu'apprend cette image à un étudiant "
            "qui ne connaît pas le cas ? » d'abord)")
    with plt.rc_context(_RC):
        fig.savefig(chemin, dpi=150)
    return chemin
