"""Falsificateurs de s9gm.visu : aucune couleur hors charte dans la figure produite ; la ligne de
provenance est présente ; une figure sans porte pédagogique n'est pas livrée."""
import re

import numpy as np
import pandas as pd
import pytest
from matplotlib import pyplot as plt

from s9gm import visu

PROV = dict(cas="F01", modele="modele_fixe", etat="rejoué le 04/10")
TOL = 8  # tolérance (niveaux sur 255) pour le crénelage ; voir _hors_charte


def _rgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], dtype=float)


def _hors_charte(fig):
    """Pixels de la figure qui ne sont pas un mélange convexe de couleurs de la charte (le crénelage
    et le chevauchement de deux traits produisent des mélanges, jamais une teinte nouvelle).
    Distance de chaque pixel à l'enveloppe convexe de la palette, par moindres carrés non négatifs
    avec somme des poids = 1 ; fautif si distance > TOL. Renvoie (nb de pixels fautifs, exemple)."""
    from scipy.optimize import nnls
    fig.canvas.draw()
    px = np.unique(np.asarray(fig.canvas.buffer_rgba())[..., :3].reshape(-1, 3).astype(float),
                   axis=0)
    pal = np.array([_rgb(h) for h in visu.CHARTE.values()])
    A = np.vstack([pal.T, 1000 * np.ones(len(pal))])  # dernière ligne : somme des poids = 1
    fautifs = []
    for c in px:
        w, _ = nnls(A, np.append(c, 1000.0))
        if np.linalg.norm(pal.T @ w - c) > TOL:
            fautifs.append(c)
    return len(fautifs), (fautifs[0] if fautifs else None)


@pytest.fixture
def df():
    t = np.linspace(0, 100, 400)
    return pd.DataFrame({"Time": t, "A": 5 * (1 - np.exp(-t / 20)), "B": np.sin(t / 5),
                         "C": t / 100})


def test_series_aucune_couleur_hors_charte(df):
    fig = visu.tracer_series(df, ["A", "B", "C"], t_transitoire=30, titre="essai", **PROV)
    n, ex = _hors_charte(fig)
    assert n == 0, f"{n} couleurs hors charte, par ex. {ex}"


def test_statistiques_aucune_couleur_hors_charte():
    st = pd.DataFrame({"moyenne": [3.0], "ecart_type": [0.5], "min": [2.0], "max": [4.5]},
                      index=["Y"])
    fig = visu.tracer_statistiques({"F03": st, "F04": st * 1.2}, "Y", modele="modele_fixe",
                                   etat="test")
    n, ex = _hors_charte(fig)
    assert n == 0, f"{n} couleurs hors charte, par ex. {ex}"


def test_le_detecteur_attrape_une_couleur_hors_charte(df):
    """Falsifie le falsificateur : un tracé rouge doit être refusé."""
    fig = visu.tracer_series(df, ["A"], **PROV)
    fig.axes[0].plot(df["Time"], df["B"], color="#FF0000", lw=3)
    assert _hors_charte(fig)[0] > 0


def test_provenance_incrustee(df, tmp_path):
    fig = visu.tracer_series(df, ["A"], **PROV)
    attendu = "cas · F01  ·  modèle · modele_fixe  ·  état · rejoué le 04/10"
    assert attendu in [t.get_text() for t in fig.texts]
    with plt.rc_context(visu._RC):
        fig.savefig(tmp_path / "f.svg")  # texte conservé dans le SVG (fonttype none)
    assert attendu in (tmp_path / "f.svg").read_text(encoding="utf-8")


def test_provenance_obligatoire(df):
    with pytest.raises(TypeError):
        visu.tracer_series(df, ["A"])
    with pytest.raises(ValueError, match="provenance incomplète"):
        visu.tracer_series(df, ["A"], cas="F01", modele="", etat="x")


def test_masquer_ordonnees(df):
    fig = visu.tracer_series(df, ["A", "B"], masquer_ordonnees=True, **PROV)
    assert all(len(ax.get_yticks()) == 0 for ax in fig.axes)
    fig2 = visu.tracer_series(df, ["A", "B"], **PROV)
    assert all(len(ax.get_yticks()) > 0 for ax in fig2.axes)


def test_figure_sans_porte_pedagogique_refusee(df, tmp_path):
    fig = visu.tracer_series(df, ["A"], **PROV)
    with pytest.raises(PermissionError, match="porte pédagogique"):
        visu.enregistrer(fig, tmp_path / "f.png", "FIG:S9GM-VISU-999")


def test_figure_avec_porte_pedagogique_livree(df, tmp_path):
    fig = visu.tracer_series(df, ["A"], **PROV)
    sortie = visu.enregistrer(fig, tmp_path / "f.png", "FIG:S9GM-VISU-001")
    assert sortie.exists() and sortie.stat().st_size > 1000


def test_registre_sans_valeur_reponse():
    texte = visu.REGISTRE.read_text(encoding="utf-8")
    assert not re.search(r"\b\d+[.,]?\d*\s*(tr/min|rad/s|m/s|kN|MN|kW|MW)\b", texte)
