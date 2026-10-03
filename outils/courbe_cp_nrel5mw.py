#!/usr/bin/env python3
"""Courbe Cp(λ) de la NREL 5 MW à calage nul, calculée sur le modèle du dépôt.

POURQUOI : Jonkman 2009 ne donne que le point maximal (Cp = 0,482 à λ = 7,55, calage 0°, §7.2 p.19),
pas la courbe. Pour résoudre à la main l'équilibre des couples en Region 1½ (séance 0a, Q0.1), il faut
la courbe : on la calcule avec le modèle `modele_fixe` lui-même (AeroDyn v15, BEMT quasi-stationnaire,
`Wake_Mod = 1`), pour que la courbe et les cas F01/F02 parlent du même modèle.

MÉTHODE : le rotor est tenu à vitesse imposée (`GenDOF` faux, `RotSpeed` fixe), calage 0°, vent
stationnaire de 8 m/s au moyeu avec le même cisaillement que F01 (exposant 0,11), toutes les autres
dynamiques coupées (lames rigides, tour et plateforme fixes, ni contrôleur, ni hydro, ni SubDyn). On
relève `RtAeroCp` (rendement aérodynamique du rotor, défini par OpenFAST), moyenné sur un nombre ENTIER
de tours (le cisaillement et l'ombre de la tour font osciller le signal à 1P et 3P).
`λ = Ω·R/V` avec R = 63 m, V = vitesse au moyeu (définition de la fiche F1).

SORTIE : `data/cp_lambda_nrel5mw_pitch0.csv` (λ, Ω, Cp) — suivi par git, relu par la fiche F1.

Usage (environnement s9gm-fowt actif, depuis la racine du dépôt) :
    python outils/courbe_cp_nrel5mw.py
"""
import csv
import math
import shutil
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
from s9gm import cas, lancer, lire  # noqa: E402

MODELE = RACINE / "tutorials" / "prise_en_main" / "modele_fixe"
TRAVAIL = RACINE / "results" / "_cp"
SORTIE = RACINE / "data" / "cp_lambda_nrel5mw_pitch0.csv"
R, V = 63.0, 8.0
LAMBDAS = [1, 2, 3, 4, 5, 6, 7, 7.55, 8, 9, 10, 11, 12, 13, 14, 15, 16]
DOF_COUPES = ["FlapDOF1", "FlapDOF2", "EdgeDOF", "DrTrDOF", "GenDOF", "YawDOF", "TwFADOF1",
              "TwFADOF2", "TwSSDOF1", "TwSSDOF2", "PtfmSgDOF", "PtfmSwDOF", "PtfmHvDOF",
              "PtfmRDOF", "PtfmPDOF", "PtfmYDOF"]


def preparer(lam):
    d = TRAVAIL / f"lam_{lam:g}"
    if d.exists():
        shutil.rmtree(d)
    shutil.copytree(MODELE, d)
    rpm = lam * V / R * 60 / (2 * math.pi)

    def edite(nom, modifs):
        lignes, fin = cas._lire_lignes(d / nom)
        for k, v in modifs.items():
            cas.remplacer_valeur(lignes, k, v)
        cas._ecrire_lignes(d / nom, lignes, fin)

    edite("main.fst", {"TMax": "60", "CompServo": "0", "CompSeaSt": "0", "CompHydro": "0",
                       "CompSub": "0"})
    edite("config_inflow.dat", {"WindType": "1", "HWindSpeed": f"{V:g}", "PLExp": "0.11"})
    edite("config_elastodyn.dat", {**{k: "False" for k in DOF_COUPES}, "RotSpeed": f"{rpm:.6f}",
                                   "BlPitch(1)": "0", "BlPitch(2)": "0", "BlPitch(3)": "0"})
    return d, rpm


def cp_moyen(d):
    df, _ = lire.lire(d / "main.outb")
    t = df["Time"].to_numpy()
    m = t >= 20.0
    az = np.unwrap(np.radians(df.loc[m, "Azimuth"].to_numpy()))
    tours = int((az[-1] - az[0]) // (2 * math.pi))
    if tours < 1:  # rotor très lent : moins d'un tour dans la fenêtre -> on prend toute la fenêtre
        k = m.sum()
    else:
        fin = np.searchsorted(az - az[0], tours * 2 * math.pi)
        k = max(fin, 2)
    return float(df.loc[m, "RtAeroCp"].to_numpy()[:k].mean()), tours


def main():
    TRAVAIL.mkdir(parents=True, exist_ok=True)
    preps = [preparer(l) for l in LAMBDAS]
    res = lancer.lancer_serie([d for d, _ in preps], coeurs=4, reprise=False)
    mauvais = [r["cas"] for r in res if r["statut"] != "termine"]
    if mauvais:
        sys.exit(f"cas en échec : {mauvais}")
    SORTIE.parent.mkdir(exist_ok=True)
    with open(SORTIE, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["lambda", "omega_rpm", "Cp", "tours_moyennes"])
        for lam, (d, rpm) in zip(LAMBDAS, preps):
            cp, tours = cp_moyen(d)
            w.writerow([f"{lam:g}", f"{rpm:.3f}", f"{cp:.4f}", tours])
            print(f"lambda={lam:>5g}  Omega={rpm:6.2f} rpm  Cp={cp:7.4f}  ({tours} tours)")


if __name__ == "__main__":
    main()
