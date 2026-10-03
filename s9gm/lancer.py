"""s9gm.lancer — exécuter une série de cas OpenFAST, en parallèle, en reprenant ce qui n'est pas fini.

### Bloc Théorie

1. **Question physique** — Une étude de charges, c'est des dizaines de calculs de plusieurs minutes
   chacun. Combien de temps faut-il réserver, que faire quand la machine s'arrête au milieu, et
   comment sait-on qu'un cas est *terminé* et pas seulement *arrêté* ?
2. **Modèle** — le temps de calcul d'un cas est proportionnel à la durée simulée :
   `t_réel ≈ t_simulé / r`, où le rapport `r` (simulé/réel, colonne « Ratio sim/CPU » du tutoriel) est
   mesuré, pas supposé : il dépend du
   modèle (BEM, SubDyn, hydro…) et de la machine. Les cas sont indépendants : on peut en lancer
   autant que de cœurs en parallèle, `t_total ≈ Σ t_réel / n_cœurs` tant que la mémoire suffit.
   Un cas est *terminé* si et seulement si son journal contient la phrase finale d'OpenFAST
   (`OpenFAST terminated normally.`) **et** que son fichier de sortie existe. **Domaine de
   validité** : un cas = un processus mono-cœur (OpenFAST compilé sans OpenMP) ; la reprise relance
   depuis t = 0 tout cas interrompu ou en échec (les points de reprise `ChkptTime` d'OpenFAST ne
   sont pas utilisés). La reprise juge sur la présence des fichiers de sortie, non sur les entrées :
   `cas` supprime donc les sorties d'un cas qu'il régénère.
3. **Ordre de grandeur attendu** — la méthode : lancer un cas court, relever `r` dans le journal
   de `lancer`, puis estimer la durée d'une série entière avant de la lancer (durée simulée totale
   ÷ `r` ÷ nombre de cœurs). Le tutoriel donne un `r` mesuré pour un cas fixe.
4. **Ce que le modèle ne permet pas de conclure** — `r` d'un cas ne se transpose pas à un autre
   modèle (flottant, houle irrégulière) ; et « terminé normalement » ne dit pas que le résultat est
   *bon* (un calcul peut finir avec une mauvaise configuration) : c'est le rôle de `lire`.
5. **Renvois** — fiche F1 (ce que vaut un résultat plausible) ; `tutorials/prise_en_main/README.md`
   (temps de calcul mesurés) ; `ENONCE.md`, phase 2 (série de référence) ; manuel OpenFAST v5.0.0.
"""
import csv
import os
import re
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

MARQUEUR_FIN = "OpenFAST terminated normally"
COLONNES_JOURNAL = ["cas", "statut", "temps_reel_s", "temps_simule_s", "rapport_simule_sur_reel"]


def duree_simulee(dossier, fst="main.fst"):
    """TMax lu dans le .fst du cas (s)."""
    for ligne in Path(dossier, fst).read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\s*(\S+)\s+TMax\b", ligne)
        if m:
            return float(m.group(1))
    raise KeyError(f"TMax introuvable dans {dossier}/{fst}")


def est_termine(dossier, fst="main.fst"):
    """Terminé = phrase finale dans run.log ET fichier .outb présent."""
    d = Path(dossier)
    log, sortie = d / "run.log", d / (Path(fst).stem + ".outb")
    if not (log.is_file() and sortie.is_file()):
        return False
    return MARQUEUR_FIN in log.read_text(encoding="utf-8", errors="replace")


def lancer_cas(dossier, executable="openfast", fst="main.fst", delai_max=None):
    """Lance un cas dans son dossier. Renvoie un dict (cas, statut, temps_reel_s, ...).
    statut ∈ {termine, echec, interrompu}. `delai_max` (s) tue le calcul : statut `interrompu`."""
    d = Path(dossier)
    sortie = d / (Path(fst).stem + ".outb")
    if sortie.exists():
        sortie.unlink()  # une sortie d'un calcul précédent ne doit pas passer pour la nouvelle
    t0 = time.monotonic()
    with open(d / "run.log", "w", encoding="utf-8") as log:
        try:
            r = subprocess.run([executable, fst], cwd=d, stdout=log, stderr=subprocess.STDOUT,
                               timeout=delai_max)
            statut = "termine" if (r.returncode == 0 and est_termine(d, fst)) else "echec"
        except subprocess.TimeoutExpired:
            statut = "interrompu"
    reel = time.monotonic() - t0
    simule = duree_simulee(d, fst)
    return {"cas": d.name, "statut": statut, "temps_reel_s": round(reel, 1),
            "temps_simule_s": simule,
            "rapport_simule_sur_reel": round(simule / reel, 3) if reel else None}


def lancer_serie(dossiers, coeurs=1, executable="openfast", reprise=True, delai_max=None,
                 journal=None, afficher=print):
    """Lance les cas de `dossiers`, `coeurs` à la fois. Avec `reprise=True`, un cas déjà terminé
    (voir `est_termine`) est sauté, un cas interrompu ou en échec est relancé depuis t = 0.

    `journal` : chemin d'un CSV (ajout, une ligne dès qu'un cas finit) — temps réel et temps simulé
    de chaque cas lancé.
    Renvoie la liste des résultats, dans l'ordre de `dossiers`."""
    if coeurs < 1:
        raise ValueError("coeurs doit être >= 1")

    def un(dossier):
        d = Path(dossier)
        if reprise and est_termine(d):
            res = {"cas": d.name, "statut": "deja_termine", "temps_reel_s": 0.0,
                   "temps_simule_s": duree_simulee(d), "rapport_simule_sur_reel": None}
        else:
            res = lancer_cas(d, executable=executable, delai_max=delai_max)
        if afficher:
            afficher(f"{res['cas']:>10} : {res['statut']:<12} réel {res['temps_reel_s']:>7.1f} s"
                     f" / simulé {res['temps_simule_s']:g} s")
        return res

    verrou = threading.Lock()

    def consigner(res):
        # écrit au fil de l'eau : un arrêt de la machine ne fait pas perdre les cas déjà finis
        if not journal or res["statut"] == "deja_termine":
            return
        with verrou:
            neuf = not os.path.exists(journal)
            with open(journal, "a", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=COLONNES_JOURNAL)
                if neuf:
                    w.writeheader()
                w.writerow(res)

    def un_et_consigner(dossier):
        res = un(dossier)
        consigner(res)
        return res

    with ThreadPoolExecutor(max_workers=coeurs) as pool:
        resultats = list(pool.map(un_et_consigner, dossiers))
    return resultats
