"""Vos copies des squelettes (`fatigue`, `ancrage`, `structure`) : créer, charger, tester — sans toucher au chemin d'import.

Les squelettes du dépôt (`s9gm/fatigue.py` …) ne se modifient pas : vous travaillez sur **une copie** sous
`results/mon_s9gm/`, que ce module crée **sans jamais écraser** une copie existante. `ma_copie("fatigue")` renvoie le module
chargé **depuis le fichier de la copie, rechargé à chaque appel** : après avoir corrigé votre fonction, relancez `ma_copie`
et vous obtenez la nouvelle version, sans redémarrer Python. Le module porte un nom distinct (`mon_s9gm.fatigue`) : il ne se confond
jamais avec le squelette `s9gm.fatigue`. `tester` lance les tests du dépôt sur la copie (ligne de commande : `s9gm tester fatigue`)."""
import importlib.util
import os
import subprocess
import sys

from . import chemins

NOMS = ("fatigue", "ancrage", "structure")
TESTS = {"fatigue": "test_fatigue.py", "ancrage": "test_ancrage.py", "structure": "test_structure.py"}
VARIABLE = {"fatigue": "S9GM_FATIGUE_COMPLET", "ancrage": "S9GM_ANCRAGE_COMPLET", "structure": "S9GM_STRUCTURE_COMPLET"}
DOSSIER_COPIES = chemins.RESULTS / "mon_s9gm"        # surchargeable (tests)


def _verifier(nom):
    if nom not in NOMS:
        raise ValueError(f"squelette inconnu : « {nom} » ; attendu : {', '.join(NOMS)}")


def creer_copie(nom):
    """Crée `results/mon_s9gm/<nom>.py` depuis le squelette, **seulement s'il n'existe pas**. Renvoie son chemin."""
    _verifier(nom)
    cible = DOSSIER_COPIES / f"{nom}.py"
    if cible.exists():
        print(f"{cible} existe déjà : conservée telle quelle (votre travail n'est jamais écrasé).")
        return cible
    cible.parent.mkdir(parents=True, exist_ok=True)
    cible.write_text((chemins.RACINE / "s9gm" / f"{nom}.py").read_text(encoding="utf-8"), encoding="utf-8")
    print(f"copie créée : {cible}")
    return cible


def trous(nom):
    """Nombre de `NotImplementedError` encore présents dans la copie (information, pas une erreur)."""
    f = DOSSIER_COPIES / f"{nom}.py"
    return f.read_text(encoding="utf-8").count("raise NotImplementedError") if f.is_file() else None


def ma_copie(nom):
    """Crée la copie si elle manque, puis renvoie le module chargé depuis le fichier, **rechargé à chaque appel**."""
    cible = creer_copie(nom)
    spec = importlib.util.spec_from_file_location(f"mon_s9gm.{nom}", cible)
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"mon_s9gm.{nom}"] = module                # requis par les dataclasses
    spec.loader.exec_module(module)
    return module


def tester(nom, squelette=False):
    """Lance les tests du dépôt sur votre copie (ou, avec `squelette=True`, sur le squelette du dépôt).
    Renvoie `(code de sortie, sortie)`. Sur une copie à trous, les tests échouent et nomment la fonction à programmer."""
    _verifier(nom)
    env = dict(os.environ)
    for v in VARIABLE.values():
        env.pop(v, None)
    if not squelette:
        creer_copie(nom)
        env[VARIABLE[nom]] = str(DOSSIER_COPIES)
    test = chemins.RACINE / "s9gm" / "tests" / TESTS[nom]
    r = subprocess.run([sys.executable, "-m", "pytest", str(test), "-q", "-p", "no:cacheprovider", "--tb=short", "-rx"],
                       cwd=chemins.RACINE, env=env, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr
