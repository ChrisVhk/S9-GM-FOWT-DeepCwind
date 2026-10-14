"""Les dossiers du dépôt, définis UNE fois, indépendamment du dossier courant du terminal.

`RACINE` est le dossier qui contient `s9gm/` : le clone dont ce paquet est importé. Tout le reste s'en déduit.
Un chemin **relatif** donné à une fonction de `s9gm` (par exemple `"results/lct.csv"`) se lit à partir de `RACINE`, pas du
dossier où vous avez lancé Python ; un chemin **absolu** n'est jamais modifié. `results/` et `rendus/` (ignorés par git)
se créent à la demande : plus de `mkdir` à taper."""
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
RESULTS = RACINE / "results"
RENDUS = RACINE / "rendus"
DATA = RACINE / "data"
CAS = RACINE / "cas"
MODELES = RACINE / "modeles"
SEANCES = RACINE / "seances"


def assurer_dossiers():
    """Crée `results/` et `rendus/` s'ils manquent (ignorés par git, donc absents d'un clone neuf). Silencieux si le dépôt est en lecture seule."""
    for d in (RESULTS, RENDUS):
        try:
            d.mkdir(exist_ok=True)
        except OSError:
            pass


assurer_dossiers()


def resoudre(chemin):
    """Chemin absolu : inchangé. Chemin relatif : relatif à `RACINE` (jamais au dossier courant)."""
    p = Path(chemin)
    return p if p.is_absolute() else RACINE / p


def dossier_results(*parties):
    """`results/<parties>` : créé s'il manque, renvoyé."""
    d = Path(RESULTS, *parties)
    d.mkdir(parents=True, exist_ok=True)
    return d


def dossier_rendus(*parties):
    """`rendus/<parties>` : créé s'il manque, renvoyé."""
    d = Path(RENDUS, *parties)
    d.mkdir(parents=True, exist_ok=True)
    return d


def assurer_parent(chemin):
    """Crée le dossier parent d'un fichier à écrire (et renvoie le chemin résolu)."""
    p = resoudre(chemin)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p
