"""Banc de rejeu des consignes : exécute les blocs de code d'une consigne, dans l'ordre, dans un CLONE NEUF du dépôt.

Ce qu'un étudiant fait en copiant les commandes d'une consigne, le test le refait. Un bloc ```python ou ```bash de la section
« 3. À faire » est exécuté tel quel, après substitution des marques `<votre …>` par des valeurs d'ESSAI NEUTRES données par le
test (jamais par la consigne : les choix de l'étudiant restent à l'étudiant). Une marque non prévue par le test, ou restée dans le
code, fait échouer le test.

Sorties : le code et la durée de chaque étape (`ETAPE <n> <secondes>`), pour que les temps mesurés citent leur source.
Variables d'environnement : `S9GM_PARCOURS_DEPOT=<dossier>` rejoue dans un dépôt existant (au lieu d'un clone neuf) : pratique pour
mettre au point, jamais suffisant pour clore."""
import re
import subprocess
import sys
import time
from pathlib import Path

BLOC = re.compile(r"^```(python|bash)[^\n]*\n(.*?)^```", re.S | re.M)
MARQUE = re.compile(r"<(?:votre|vos|indice|nombre|seuil|ligne|période|valeur|choix)[^<>\n]*>")


def section(texte, debut="## 3.", fin="## 4."):
    i = texte.index(debut)
    return texte[i:texte.index(fin, i)]


def blocs(texte):
    return [(m.group(1), m.group(2)) for m in BLOC.finditer(section(texte))]


def substituer(code, substitutions):
    for marque, valeur in substitutions.items():
        code = code.replace(marque, str(valeur))
    reste = MARQUE.findall(code)
    if reste:
        raise AssertionError(f"marque(s) sans valeur d'essai dans le test : {sorted(set(reste))}")
    return code


def cloner(racine, destination):
    """Clone local du dépôt (état COMMITÉ) + contrôleur compilé : l'état d'un étudiant après INSTALLATION.md."""
    subprocess.run(["git", "clone", "-q", "--local", str(racine), str(destination)], check=True, capture_output=True)
    r = subprocess.run(["bash", "scripts/build_discon.sh"], cwd=destination, capture_output=True, text=True)
    if r.returncode != 0:
        raise AssertionError(f"build_discon.sh a échoué dans le clone :\n{r.stdout}{r.stderr}")
    return Path(destination)


def rejouer(readme, depot, substitutions, delai=3600):
    """Exécute les blocs de `readme` dans `depot`. Renvoie (code de sortie, sortie, {étape : secondes})."""
    texte = Path(readme).read_text(encoding="utf-8")
    morceaux, n = [], 0
    for langue, code in blocs(texte):
        n += 1
        code = substituer(code, substitutions)
        if langue == "python":
            morceaux.append(f"_t0 = __import__('time').time()\n{code}\nprint('ETAPE {n}', round(__import__('time').time() - _t0, 1), flush=True)\n")
        else:
            raise AssertionError(f"bloc bash à l'étape {n} : le banc ne rejoue que le Python d'une phase")
    script = "import sys; sys.path.insert(0, '.')\n" + "\n".join(morceaux)
    debut = time.time()
    r = subprocess.run([sys.executable, "-I", "-c", script], cwd=depot, capture_output=True, text=True, timeout=delai)
    temps = {int(m[1]): float(m[2]) for m in re.finditer(r"^ETAPE (\d+) ([\d.]+)$", r.stdout, re.M)}
    temps["total"] = round(time.time() - debut, 1)
    return r.returncode, r.stdout + r.stderr, temps
