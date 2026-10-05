#!/usr/bin/env python3
"""Exemple de chaîne complète de la toolbox `s9gm` : du site à un dommage équivalent, sans aucune valeur.

Ce script montre l'ENCHAÎNEMENT des modules ; les choix (nombre de classes, exposant du lumping, hauteur de vent, durée,
transitoire, exposant S-N, fréquence équivalente) sont des constantes à `None` à décider et justifier par vous — chacun est un
paramètre obligatoire des fonctions, jamais un défaut. Il ne produit aucune sortie : lancez-le morceau par morceau,
et regardez ce que chaque étape renvoie avant de passer à la suivante.

Étapes : site → LCT (`metocean`) → cas (`cas`) → calcul (`lancer`) → lecture (`lire`) → fatigue (`fatigue`).
Les trous de `fatigue` (rainflow, Miner, DEL) sont à compléter avant l'étape 5 ; voir `s9gm/CHAINE.md`.
"""
from pathlib import Path

from s9gm import cas, fatigue, lancer, lire, metocean

MODELE = Path("tutorials/lheea/05_FOWT/1_Configuration")       # modèle flottant du dépôt
SORTIE = Path("results/chaine")                                 # dossier des cas (non suivi par git)

# Choix à faire (None = non décidé : les fonctions refusent de calculer plutôt que d'inventer un défaut) ----------------
K_CLASSES = METHODE = M_LUMPING = Z_TABLE = Z_HUB = LOI = EXPOSANT = TMAX = GRAINE0 = COEURS = None
T_TRANSITOIRE = M_SN = N_EQ = None

# 1. Du site à la Load Case Table -------------------------------------------------------------------------------
table = metocean.lire()
table = metocean.binning(table, "U", K_CLASSES)                       # combien de classes de vent ? pourquoi ?
etats = metocean.lumper(table, methode=METHODE, axe_classes="U", m=M_LUMPING)
etats = metocean.occurrences(etats)                             # Σ Oⱼ = 100 % : la fonction échoue sinon
# hauteur de vent : <loi>, EXPOSANT, de Z_TABLE à Z_HUB   (metocean.hauteur_vent, explicite)
metocean.exporter_lct(etats, "lct.csv", "etats.csv", z_table=Z_TABLE, z_hub=Z_HUB, loi=LOI,
                      exposant=EXPOSANT, tmax=TMAX, graine0=GRAINE0)

# 2. Des cas : un dossier léger par ligne de la LCT (vent TurbSim, houle SeaState, durée) ------------------------
dossiers = cas.generer_serie("lct.csv", MODELE, SORTIE)

# 3. Le calcul : plusieurs cas à la fois, les cas terminés ne sont pas relancés ----------------------------------
lancer.lancer_serie(dossiers, coeurs=COEURS, journal=SORTIE / "journal_lancer.csv")

# 4. La lecture : le transitoire écarté est un choix, `lire` refuse de calculer sans lui ---------------------------
df, unites = lire.lire(SORTIE / "NOM_DU_CAS" / "main.outb")
print(lire.statistiques(df, ["TwrBsMyt"], t_transitoire=T_TRANSITOIRE))   # regardez aussi si la fenêtre est stationnaire

# 5. La fatigue : DEL court terme par cas, puis DEL long terme pondéré par les Oⱼ -------------------------------
serie = df.loc[df["Time"] >= T_TRANSITOIRE, "TwrBsMyt"].to_numpy()
cycles = fatigue.rainflow(serie)                                # étendues, pas amplitudes
del_cas = fatigue.del_court_terme(cycles["etendue"], cycles["compte"], M_SN, N_EQ)
# ... répétez pour chaque cas, puis :
# fatigue.del_long_terme(del_par_cas, occurrences, M_SN)
