"""Exporte les six cas IEA 15 MW a vent stationnaire (cases/iea15_stationnaire/_calculs/*/main.outb)
vers `data/iea15_openfast_stationnaire.csv.gz` : le jeu livre que lit le notebook de la seance 0b quand
les cas n'ont pas ete relances. Lecture par `s9gm.lire` (aucun traitement : memes valeurs que le .outb).

Usage (environnement s9gm-fowt, depuis la racine du depot) :
    python3 outils/exporter_iea15_stationnaire.py
"""
import sys
from pathlib import Path

import pandas as pd

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
from s9gm import lire  # noqa: E402

CANAUX = ["Wind1VelX", "RotSpeed", "BldPitch1", "GenPwr", "RotThrust", "RotTorq", "RootMyb1", "TwrBsMyt",
          "RtFldFxh", "RtFldCp", "RtFldCt", "RtVAvgxh", "RtArea"]

if __name__ == "__main__":
    morceaux = []
    for sortie in sorted((RACINE / "cases" / "iea15_stationnaire" / "_calculs").glob("*/main.outb")):
        df, _ = lire.lire(sortie)
        morceaux.append(df[["Time", *CANAUX]].assign(cas=sortie.parent.name)[["cas", "Time", *CANAUX]])
    if not morceaux:
        sys.exit("aucun main.outb trouve : lancez d'abord les cas (notebook, LANCER = True)")
    out = RACINE / "data" / "iea15_openfast_stationnaire.csv.gz"
    pd.concat(morceaux).to_csv(out, index=False, float_format="%.6g")
    print(f"OK : {out} ({len(morceaux)} cas)")
