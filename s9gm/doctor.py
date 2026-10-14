"""`s9gm doctor` : vérifie, dans l'ordre, que votre poste est prêt, et dit pour chaque point **OK** ou **À CORRIGER** avec la commande exacte.

Rien n'est modifié par cette commande (aucune écriture, aucun réseau). Code de sortie 0 si tous les points obligatoires sont OK.
Sortie en français, sans couleur."""
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from . import chemins, copies

ENV_NOM = "s9gm-fowt"


@dataclass(frozen=True)
class Resultat:
    id: str
    titre: str
    ok: bool
    message: str = ""
    commande: str = ""
    obligatoire: bool = True


def _version_openfast_epinglee(racine):
    f = Path(racine) / "env" / "environment.yml"
    if f.is_file():
        m = re.search(r"openfast=(\d+\.\d+\.\d+)", f.read_text(encoding="utf-8"))
        if m:
            return m.group(1)
    return None


def verifier(env=None, prefixe_python=None, executable=None, fichier_s9gm=None, racine=None):
    """Liste de `Resultat`. Les paramètres permettent de simuler un poste défaillant (tests)."""
    env = os.environ if env is None else env
    racine = Path(racine) if racine else chemins.RACINE
    prefixe_python = prefixe_python or sys.prefix
    executable = executable or sys.executable
    fichier = Path(fichier_s9gm) if fichier_s9gm else Path(sys.modules["s9gm"].__file__)
    r = []

    r.append(Resultat("systeme", "Linux (WSL ou natif)", sys.platform.startswith("linux"),
                      "" if sys.platform.startswith("linux") else f"système : {sys.platform}",
                      "installez WSL (Ubuntu) puis refaites l'installation dans WSL"))
    sous_windows = re.match(r"^/mnt/[a-z]/", racine.as_posix()) is not None
    r.append(Resultat("emplacement", "clone hors de /mnt/c", not sous_windows,
                      f"le clone est sous {racine} (disque Windows : lent, droits de fichiers faux)" if sous_windows else str(racine),
                      "git clone <adresse> ~/S9-GM-FOWT-DeepCwind   (dans votre dossier personnel Linux)"))
    prefixe_env = env.get("CONDA_PREFIX", "")
    actif = bool(prefixe_env) and Path(prefixe_env).name == ENV_NOM and Path(prefixe_python).resolve() == Path(prefixe_env).resolve()
    if actif:
        msg = f"python : {executable}"
    elif prefixe_env and Path(prefixe_env).name != ENV_NOM:
        msg = f"environnement actif : {Path(prefixe_env).name} (attendu : {ENV_NOM})"
    elif prefixe_env:
        msg = f"le python en cours ({executable}) n'est pas celui de l'environnement {ENV_NOM}"
    else:
        msg = f"aucun environnement actif ; python : {executable}"
    r.append(Resultat("environnement", f"environnement {ENV_NOM} actif et python en cours = le sien", actif, msg,
                      f"micromamba activate {ENV_NOM}"))

    attendu = _version_openfast_epinglee(racine)
    of = shutil.which("openfast", path=env.get("PATH") if "PATH" in env else None)
    version = ""
    if of:
        try:
            version = subprocess.run([of, "-v"], capture_output=True, text=True, timeout=30).stdout
        except (OSError, subprocess.TimeoutExpired):
            version = ""
    ok_of = bool(of) and (attendu is None or f"OpenFAST-v{attendu}" in version)
    r.append(Resultat("openfast", f"openfast -v = v{attendu}", ok_of,
                      (re.search(r"OpenFAST-v\S+", version).group(0) if re.search(r"OpenFAST-v\S+", version) else "openfast introuvable") if of or version else "openfast introuvable",
                      f"micromamba activate {ENV_NOM}   (puis : openfast -v)"))
    r.append(Resultat("turbsim", "turbsim présent", shutil.which("turbsim", path=env.get("PATH") if "PATH" in env else None) is not None,
                      "", f"micromamba activate {ENV_NOM}"))

    meme_clone = fichier.resolve().parent.parent == racine.resolve()
    r.append(Resultat("clone", "s9gm importé depuis CE clone", meme_clone,
                      "" if meme_clone else f"s9gm vient de {fichier.resolve().parent.parent} et non de {racine} : vous avez deux clones",
                      f"cd {racine} && pip install -e ."))

    controleurs = [racine / "modeles" / "oc4_rtest" / "5MW_Baseline" / "ServoData" / n for n in ("DISCON.so", "DISCON_OC3Hywind.so")]
    manque = [c.name for c in controleurs if not c.is_file()]
    r.append(Resultat("controleur", "contrôleur compilé", not manque, ("manque : " + ", ".join(manque)) if manque else "",
                      f"cd {racine} && bash scripts/build_discon.sh"))

    probleme = []
    for nom in ("results", "rendus"):
        d = racine / nom
        if not d.is_dir() and not os.access(racine, os.W_OK):
            probleme.append(f"{nom}/ ne peut pas être créé")
    if shutil.which("git") and (racine / ".git").exists():
        sale = subprocess.run(["git", "status", "--porcelain", "--", "data"], cwd=racine, capture_output=True, text=True).stdout.strip()
        if sale:
            probleme.append("data/ est modifié (il ne doit jamais l'être) : " + sale.splitlines()[0])
    r.append(Resultat("dossiers", "results/ et rendus/ utilisables, data/ intact", not probleme, "; ".join(probleme),
                      f"cd {racine} && git checkout -- data/   (si data/ est modifié)"))

    infos = []
    for nom in copies.NOMS:
        n = copies.trous(nom)
        if n is not None:
            infos.append(f"{nom} : {n} trou(s) `NotImplementedError` restant(s)" if n else f"{nom} : aucun trou restant")
    r.append(Resultat("copies", "vos copies results/mon_s9gm/*.py (information)", True,
                      "; ".join(infos) if infos else "aucune copie encore (normal avant la phase 3)", "", obligatoire=False))
    for outil, role in (("pvbatch", "animations (ParaView)"), ("ffmpeg", "montage vidéo")):
        r.append(Resultat(outil, f"{outil} ({role}, facultatif)", shutil.which(outil) is not None, "", f"micromamba install -n {ENV_NOM} -c conda-forge {outil}" if outil == "ffmpeg" else "voir seances/atelier_tour ou ANIMER.md",
                          obligatoire=False))
    return r


def code_de_sortie(resultats):
    return 0 if all(x.ok for x in resultats if x.obligatoire) else 1


def afficher(resultats, sortie=print):
    sortie("s9gm doctor — votre poste")
    for x in resultats:
        etat = "OK" if x.ok else ("À CORRIGER" if x.obligatoire else "absent (facultatif)")
        sortie(f"  [{etat}] {x.titre}" + (f" — {x.message}" if x.message else ""))
        if not x.ok and x.commande:
            sortie(f"      commande : {x.commande}")
    obligatoires_ko = [x for x in resultats if x.obligatoire and not x.ok]
    sortie("")
    sortie("Tout est prêt." if not obligatoires_ko else f"{len(obligatoires_ko)} point(s) à corriger avant de continuer (dans l'ordre ci-dessus).")


def main():
    res = verifier()
    afficher(res)
    return code_de_sortie(res)
