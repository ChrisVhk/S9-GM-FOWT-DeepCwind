#!/usr/bin/env python3
"""Squelette de post-traitement OpenFAST : lecture d'un .outb, statistiques simples,
trace d'un ou plusieurs canaux.

Ne fait PAS de rainflow ni de DEL : c'est a vous de les programmer (phase 3 du projet),
precisement pour que vous compreniez ce que fait l'outil avant de vous en servir.

Usage :
    python outils/lire_outb.py chemin/vers/main.outb                 # liste les canaux
    python outils/lire_outb.py chemin/vers/main.outb TwrBsMyt         # stats + trace
    python outils/lire_outb.py chemin/vers/main.outb TwrBsMyt RotSpeed  # plusieurs canaux
"""
import sys
import numpy as np
import matplotlib.pyplot as plt
from openfast_toolbox.io.fast_output_file import load_binary_output


def lire(chemin):
    """Renvoie (t, donnees, noms_colonnes). donnees[:,0] == t."""
    data, info = load_binary_output(chemin, use_buffer=True)
    colonnes = ["Time"] + info["attribute_names"][1:]
    return data[:, 0], data, colonnes


def statistiques(t, data, colonnes, canal, t_min=None):
    """Moyenne, ecart-type, max, min d'un canal, optionnellement apres t_min
    (pour ignorer le transitoire de demarrage -- piege classique signale dans l'enonce)."""
    i = colonnes.index(canal)
    mask = t >= t_min if t_min is not None else np.ones_like(t, dtype=bool)
    y = data[mask, i]
    return {
        "moyenne": float(np.mean(y)),
        "ecart_type": float(np.std(y)),
        "max": float(np.max(y)),
        "min": float(np.min(y)),
    }


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    chemin = sys.argv[1]
    canaux_demandes = sys.argv[2:]

    t, data, colonnes = lire(chemin)
    print(f"Fichier : {chemin}")
    print(f"Duree simulee : {t[-1]:.1f} s, {len(t)} pas de temps")

    if not canaux_demandes:
        print("\nCanaux disponibles :")
        for c in colonnes:
            print(f"  {c}")
        return

    for canal in canaux_demandes:
        if canal not in colonnes:
            print(f"ATTENTION : canal '{canal}' absent de ce fichier, ignore.")
            continue
        s = statistiques(t, data, colonnes, canal)
        print(f"\n{canal} :")
        for k, v in s.items():
            print(f"  {k:12s} = {v:.4g}")

    fig, axes = plt.subplots(len(canaux_demandes), 1, sharex=True, figsize=(9, 3 * len(canaux_demandes)))
    if len(canaux_demandes) == 1:
        axes = [axes]
    for ax, canal in zip(axes, canaux_demandes):
        if canal not in colonnes:
            continue
        i = colonnes.index(canal)
        ax.plot(t, data[:, i])
        ax.set_ylabel(canal)
        ax.grid(True)
    axes[-1].set_xlabel("Temps (s)")
    fig.tight_layout()
    out_png = chemin.rsplit(".", 1)[0] + "_trace.png"
    fig.savefig(out_png, dpi=120)
    print(f"\nFigure enregistree : {out_png}")


if __name__ == "__main__":
    main()
