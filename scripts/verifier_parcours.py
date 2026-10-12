#!/usr/bin/env python3
"""Contrôles de structure du dépôt : liens, anciens chemins, format des consignes, porte unique, transition.

  liens       R-1  tout lien relatif de tout .md et .ipynb suivi pointe vers un fichier suivi (ou un dossier qui en contient)
  chemins     R-1b chemins entre guillemets des fichiers d'entrée OpenFAST (.dat .fst .inp) : relatifs au fichier qui les cite, comme
               OpenFAST les lit ; un binaire généré localement (.so, .bts) n'a besoin que de son dossier ; les fixtures
               s9gm/tests/data/ sont exemptées. Les non-résolus restants sont une LISTE DE RÉFÉRENCE (voir CARTE) : elle ne doit pas grandir
  edition     R-7  aucune consigne (seances/**/*.md, cas/README.md, INSTALLATION.md) ne demande d'éditer un fichier SUIVI par git :
               pas de verbe d'édition à côté d'un chemin suivi (sauf copie sous results/ ou mention « lecture seule »), pas d'éditeur
               ni de `sed -i` lancé sur un fichier suivi. L'étudiant ne modifie que des dossiers ignorés par git.
  anciens     R-2  aucun ancien chemin cité hors annexes/, hors TRANSITION.md et CHANGELOG, hors ce script et son test
  format      R-4  chaque seances/*/README.md porte les 6 titres « ## » du format commun, dans l'ordre, et eux seuls
  porte       R-5  le README.md racine renvoie à chaque séance et à la page de post-traitement ; aucun autre fichier ne se
               présente comme point d'entrée
  transition  R-6  clone de l'état ANCIEN (par défaut origin/main), travail d'étudiant simulé, `git pull` de l'état NOUVEAU
               (par défaut HEAD) : aucun conflit, aucun fichier d'étudiant perdu, anciens emplacements nommés dans TRANSITION.md

Usage : python scripts/verifier_parcours.py {liens|chemins|edition|anciens|format|porte|transition|tout} [--racine DOSSIER]
        python scripts/verifier_parcours.py --autotest      (chaque contrôle doit voir une faute plantée)
Sortie : une ligne par écart, code 1 s'il y en a, 0 sinon. `tout` enchaîne R-1, R-1b, R-2, R-4, R-5, R-7 (R-6 se lance à part).
"""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote

# ---- R-4 : le format commun d'une consigne de séance (titres identiques partout, dans cet ordre) ----------------------
TITRES = ["Objectif", "Avant de commencer", "À faire, étape par étape", "Post-traiter", "Ce qu'on rend", "Théorie à lire"]
PAGE_POST_TRAITEMENT = "s9gm/POST-TRAITER.md"

# ---- R-2 : anciens chemins (table de CARTE_RESTRUCTURATION.md). `papers/` et `outils/` ne sont anciens que s'ils ne
# sont pas précédés de `annexes/` ; `models/` ne doit pas attraper `modeles/`.
ANCIENS = [
    r"(?<!oracle/)\btutorials/", r"\bprise_en_main\b", r"\bmodele_fixe\b", r"\bmodels/", r"\bcases/",
    r"(?<!annexes/)\bpapers/", r"(?<!annexes/)\boutils/",
]
EXCLUS_ANCIENS = ("annexes/", "scripts/verifier_parcours.py", "s9gm/tests/test_verifier_parcours.py", "TRANSITION.md", "CHANGELOG")
TEXTES = {".md", ".py", ".sh", ".ipynb", ".txt", ".csv", ".yml", ".yaml", ".json", ".dat", ".fst", ".inp", ".gitignore", ""}

LIEN_MD = re.compile(r"\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")


def git(racine, *args):
    return subprocess.run(["git", *args], cwd=racine, capture_output=True, text=True, check=True).stdout


def suivis(racine):
    return [f for f in git(racine, "ls-files").split("\n") if f]


def sans_code(texte):
    """Retire les blocs ``` et les spans `...` (un lien écrit comme exemple n'est pas un lien)."""
    sortie, dedans = [], False
    for ligne in texte.split("\n"):
        if ligne.lstrip().startswith("```"):
            dedans = not dedans
            continue
        sortie.append("" if dedans else re.sub(r"`[^`]*`", "", ligne))
    return sortie


def lignes_markdown(chemin):
    """Lignes de texte Markdown d'un .md ou des cellules markdown d'un .ipynb (code retiré)."""
    brut = chemin.read_text(encoding="utf-8", errors="replace")
    if chemin.suffix == ".ipynb":
        cellules = json.loads(brut).get("cells", [])
        brut = "\n".join("".join(c.get("source", [])) for c in cellules if c.get("cell_type") == "markdown")
    return sans_code(brut)


def liens(racine):
    racine = Path(racine).resolve()
    f_suivis = set(suivis(racine))
    dossiers = {str(p) for f in f_suivis for p in Path(f).parents if str(p) != "."}
    ecarts = []
    liens.verifies = liens.fichiers = 0
    for f in sorted(f_suivis):
        if not f.endswith((".md", ".ipynb")):
            continue
        liens.fichiers += 1
        for n, ligne in enumerate(lignes_markdown(racine / f), start=1):
            for m in LIEN_MD.finditer(ligne):
                cible = m.group(1)
                if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", cible) or cible.startswith("#"):
                    continue
                chemin = unquote(cible.split("#")[0].split("?")[0])
                if not chemin:
                    continue
                liens.verifies += 1
                voulu = (racine / f).parent / chemin
                try:
                    rel = str(voulu.resolve().relative_to(racine))
                except ValueError:
                    ecarts.append(f"{f}:{n}: lien hors du dépôt : {cible}")
                    continue
                if rel not in f_suivis and rel not in dossiers:
                    ecarts.append(f"{f}:{n}: lien vers un fichier absent ou non suivi : {cible}")
    return ecarts


CHEMIN_OPENFAST = re.compile(r'^\s*"([^"]+)"\s+\S')
EXT_FICHIER = re.compile(r"\.(dat|so|bts|txt|csv|fst|inp|dll|1|3|hst|12d|ipt|yaml)$")
# Références préexistantes à des fichiers que les cas concernés ne lisent pas (module éteint, vent non lu) : tolérées, le reste échoue.
TOLERES = {"config_moordyn.dat", "NRELOffshrBsline5MW_BeamDyn.dat", "SWRT_Furl.dat", "TailPlate.dat", "ramp_wind.dat", "libdiscon.so"}
STRICTS = {("cas/F02/config_inflow.dat", "ramp_wind.dat"), ("cas/D02/config_inflow.dat", "ramp_wind.dat")}   # ces cas LISENT la rampe
GENERES = (".so", ".bts")   # produits par scripts/build_discon.sh, installer_rosco.sh, TurbSim : jamais suivis


def chemins(racine):
    """R-1b. Renvoie les chemins d'entrée OpenFAST qui ne se résolvent pas (hors binaires générés dont le dossier existe)."""
    racine = Path(racine).resolve()
    f_suivis = set(suivis(racine))
    dossiers = {str(p) for f in f_suivis for p in Path(f).parents if str(p) != "."}
    ecarts = []
    chemins.verifies = chemins.toleres = 0
    for f in sorted(f_suivis):
        if not f.endswith((".dat", ".fst", ".inp")) or f.startswith("s9gm/tests/data/") or "/Documentation/" in f:
            continue
        try:
            lignes = (racine / f).read_text(encoding="utf-8").split("\n")
        except (UnicodeDecodeError, OSError):
            continue
        for n, ligne in enumerate(lignes, start=1):
            m = CHEMIN_OPENFAST.match(ligne)
            if not m:
                continue
            c = m.group(1)
            if c.lower() in ("unused", "default", "none") or " " in c or not EXT_FICHIER.search(c):
                continue
            chemins.verifies += 1
            voulu = ((racine / f).parent / c).resolve()
            try:
                rel = str(voulu.relative_to(racine))
            except ValueError:
                ecarts.append(f"{f}:{n}: chemin hors du dépôt : {c}")
                continue
            if c.endswith(GENERES):
                rel = str(Path(rel).parent)   # le binaire n'est pas suivi : son dossier doit l'être
            if rel not in f_suivis and rel not in dossiers:
                base = Path(c).name
                if base in TOLERES and (f, base) not in STRICTS:
                    chemins.toleres += 1
                    continue
                ecarts.append(f"{f}:{n}: chemin non résolu : {c}")
    return ecarts


VERBES_EDITION = re.compile(r"\b(édit\w+|modifi\w+|chang(?:ez|er|ez-le|ez-les)|remplac\w+|compl[ée]t\w+|renseign\w+|corrig\w+|enregistr\w+|ajout\w+|réécri\w+)\b", re.IGNORECASE)
GARDE_FOUS = re.compile(r"results/|rendus/|\bcopi\w+|lecture seule|sans (?:le |les |l')?(?:modifi|enregistr)\w*|ne (?:le |les |l')?(?:modifi|enregistr)\w*|jamais|n'(?:est|a) pas|à compléter", re.IGNORECASE)
EDITEUR = re.compile(r"^\s*(?:nano|vim?|code|gedit|emacs|sed\s+-i|tee|cat\s*>)\s+(?:-\S+\s+)*(\S+)")


def edition(racine):
    """R-7 : une consigne ne demande jamais d'éditer un fichier suivi par git."""
    racine = Path(racine).resolve()
    f_suivis = set(suivis(racine))
    noms = {}
    for f in f_suivis:
        noms.setdefault(Path(f).name, []).append(f)
    cibles = [f for f in sorted(f_suivis) if f.endswith(".md") and (f.startswith("seances/") or f in ("cas/README.md", "INSTALLATION.md"))]
    ecarts = []
    for f in cibles:
        dedans = False
        for n, ligne in enumerate((racine / f).read_text(encoding="utf-8").split("\n"), start=1):
            if ligne.lstrip().startswith("```"):
                dedans = not dedans
                continue
            if dedans:
                if EDITEUR.match(ligne):
                    for jeton in ligne.split():
                        if _est_suivi(jeton, racine, f, f_suivis):
                            ecarts.append(f"{f}:{n}: éditeur ou sed -i lancé sur un fichier suivi : {jeton}")
                            break
                continue
            if not VERBES_EDITION.search(ligne) or GARDE_FOUS.search(ligne):
                continue
            for jeton in re.findall(r"`([^`\s]+)`", ligne):
                if _est_suivi(jeton, racine, f, f_suivis):
                    ecarts.append(f"{f}:{n}: demande d'éditer un fichier suivi ({jeton}) : « {ligne.strip()[:90]} »")
                    break
    return ecarts


def _est_suivi(jeton, racine, depuis, f_suivis):
    """Le jeton désigne-t-il un fichier suivi (chemin depuis la racine, ou depuis le .md qui le cite) ?"""
    jeton = jeton.strip("`'\".,;:()")
    if not jeton or jeton.endswith("/") or "*" in jeton or "<" in jeton:
        return False
    for base in (Path("."), Path(depuis).parent):
        try:
            rel = str((racine / base / jeton).resolve().relative_to(racine))
        except ValueError:
            continue
        if rel in f_suivis:
            return True
    return False


def anciens(racine):
    racine = Path(racine).resolve()
    motifs = [re.compile(p) for p in ANCIENS]
    ecarts = []
    for f in suivis(racine):
        if f.startswith(EXCLUS_ANCIENS) or Path(f).name.startswith(("TRANSITION", "CHANGELOG")):
            continue
        if Path(f).suffix not in TEXTES and Path(f).name not in TEXTES:
            continue
        try:
            texte = (racine / f).read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for n, ligne in enumerate(texte.split("\n"), start=1):
            for m in motifs:
                t = m.search(ligne)
                if t:
                    ecarts.append(f"{f}:{n}: ancien chemin « {t.group(0)} »")
    return ecarts


def format_seances(racine):
    racine = Path(racine).resolve()
    ecarts = []
    seances = racine / "seances"
    for d in sorted(p for p in seances.iterdir() if p.is_dir()) if seances.is_dir() else []:
        readme = d / "README.md"
        if not readme.is_file():
            ecarts.append(f"seances/{d.name}/README.md : absent")
            continue
        trouves = [(m.group(1), m.group(2).strip()) for ligne in sans_code(readme.read_text(encoding="utf-8"))
                   if (m := re.match(r"^## (\d+)\.\s+(.*)$", ligne))]
        voulus = [(str(i), t) for i, t in enumerate(TITRES, start=1)]
        if trouves != voulus:
            manquants = [t for t in TITRES if t not in [x[1] for x in trouves]]
            en_trop = [x[1] for x in trouves if x[1] not in TITRES]
            detail = (f"manque {manquants}" if manquants else "") + (f" ; en trop {en_trop}" if en_trop else "")
            if not detail:
                detail = f"ordre ou numérotation faux : {[f'{a}. {b}' for a, b in trouves]}"
            ecarts.append(f"seances/{d.name}/README.md : format commun non respecté ({detail.strip(' ;')})")
    return ecarts


def porte_unique(racine):
    racine = Path(racine).resolve()
    ecarts = []
    readme = racine / "README.md"
    texte = readme.read_text(encoding="utf-8") if readme.is_file() else ""
    cibles = {unquote(m.group(1).split("#")[0]) for l in sans_code(texte) for m in LIEN_MD.finditer(l)}
    seances = racine / "seances"
    for d in sorted(p.name for p in seances.iterdir() if p.is_dir()) if seances.is_dir() else []:
        if f"seances/{d}/README.md" not in cibles and f"seances/{d}/" not in cibles:
            ecarts.append(f"README.md : ne renvoie pas à seances/{d}/")
    if PAGE_POST_TRAITEMENT not in cibles:
        ecarts.append(f"README.md : ne renvoie pas à {PAGE_POST_TRAITEMENT}")
    pretendant = re.compile(r"commencez ici|point d'entrée|porte d'entrée", re.IGNORECASE)
    for f in suivis(racine):
        if f in ("README.md", "scripts/verifier_parcours.py", "s9gm/tests/test_verifier_parcours.py") or f.startswith("annexes/"):
            continue
        if f.endswith((".md", ".ipynb")):
            for n, ligne in enumerate(lignes_markdown(racine / f), start=1):
                if pretendant.search(ligne):
                    ecarts.append(f"{f}:{n}: se présente comme point d'entrée : « {ligne.strip()[:80]} »")
    return ecarts


# ---- R-6 : transition d'un clone d'étudiant -----------------------------------------------------------------------
def empreintes(dossier, fichiers):
    return {f: hashlib.sha256((dossier / f).read_bytes()).hexdigest() for f in fichiers}


def recuperer(racine, distant_nu, ref):
    """Met `ref` du dépôt `racine` en tête de `main` du dépôt nu temporaire, par `fetch` DEPUIS le temporaire : rien n'est
    écrit dans `racine` ni dans son vrai `origin` (et le hook pre-push du poste n'a pas à être contourné)."""
    complet = git(racine, "rev-parse", "--symbolic-full-name", ref).strip() or git(racine, "rev-parse", ref).strip()
    subprocess.run(["git", "--git-dir", str(distant_nu), "fetch", "-q", str(racine), f"+{complet}:refs/heads/main"],
                   check=True, capture_output=True, text=True)


def transition(racine, ancien="origin/main", nouveau="HEAD", fichiers_etudiant=None, note="TRANSITION.md",
               fichier_suivi="tutorials/prise_en_main/F01/main.fst"):
    """Rejoue le geste d'un étudiant, deux fois. N'écrit jamais dans le vrai `origin` (le dépôt « distant » est un dépôt nu
    temporaire, alimenté par `fetch`).

    Scénario A : l'étudiant n'a créé que des fichiers NON suivis (sorties, tables de cas, brouillons) : `git pull` doit passer, sans rien
    perdre. Scénario B : il a de plus MODIFIÉ un fichier suivi que la restructuration déplace (`fichier_suivi`) : le `git pull` simple peut
    refuser ; la recette de la note (`git stash`, `git pull`, `git stash pop`) doit alors passer sans perdre sa modification, et la note doit
    la donner."""
    racine = Path(racine).resolve()
    if fichiers_etudiant is None:
        fichiers_etudiant = {
            "results/essai/F01_stats.csv": "cas,moyenne\nF01,0\n",
            "rendus/R0_brouillon.md": "brouillon d'étudiant\n",
            "lct_0b.csv": "cas,fst.TMax\nF03,300\n",
            "tutorials/prise_en_main/F03/main.outb": "sortie d'un calcul d'étudiant (ignorée par git)\n",
        }
    ecarts = []
    tmp = Path(tempfile.mkdtemp(prefix="transition_"))
    marque = "! modification d'etudiant (R-6)"

    def cloner(nom):
        nu = tmp / f"{nom}.git"
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(nu)], check=True)
        recuperer(racine, nu, ancien)
        etu = tmp / nom
        subprocess.run(["git", "clone", "-q", str(nu), str(etu)], check=True, capture_output=True)
        git(etu, "config", "user.email", "etudiant@exemple.invalid")
        git(etu, "config", "user.name", "etudiant")
        for f, c in fichiers_etudiant.items():
            (etu / f).parent.mkdir(parents=True, exist_ok=True)
            (etu / f).write_text(c, encoding="utf-8")
        recuperer(racine, nu, nouveau)
        return etu

    def verifier_fichiers(etu, etiquette):
        avant = {f: hashlib.sha256(c.encode("utf-8")).hexdigest() for f, c in fichiers_etudiant.items()}
        perdus = [f for f in fichiers_etudiant if not (etu / f).is_file()]
        ecarts.extend(f"{etiquette} : fichier d'étudiant perdu : {f}" for f in perdus)
        ecarts.extend(f"{etiquette} : fichier d'étudiant modifié : {f}" for f, h in
                      empreintes(etu, [f for f in fichiers_etudiant if f not in perdus]).items() if h != avant[f])

    def modification_presente(etu):
        return any(marque in f.read_text(encoding="utf-8", errors="replace")
                   for f in etu.rglob("*.fst") if f.is_file() and ".git" not in f.parts)

    try:
        # --- scénario A : fichiers non suivis seulement
        etu = cloner("etudiant_a")
        r = subprocess.run(["git", "pull", "-q", "--no-rebase", "--no-edit"], cwd=etu, capture_output=True, text=True)
        if r.returncode != 0:
            ecarts.append(f"A : git pull a échoué : {(r.stderr or r.stdout).strip()[:300]}")
        else:
            verifier_fichiers(etu, "A")
            texte_note = (etu / note).read_text(encoding="utf-8") if (etu / note).is_file() else None
            restes = sorted({f.split("/")[0] + "/" for f in fichiers_etudiant
                             if f.split("/")[0] not in ("results", "rendus") and "/" in f})
            if texte_note is None:
                if restes:
                    ecarts.append(f"{note} absente alors que des fichiers d'étudiant restent à d'anciens emplacements : {restes}")
            else:
                ecarts += [f"{note} ne nomme pas l'ancien emplacement {d}" for d in restes if d not in texte_note]
        # --- scénario B : un fichier suivi modifié par l'étudiant
        etu = cloner("etudiant_b")
        suivi = etu / fichier_suivi
        if suivi.is_file():
            suivi.write_text(suivi.read_text(encoding="utf-8") + marque + "\n", encoding="utf-8")
            r = subprocess.run(["git", "pull", "-q", "--no-rebase", "--no-edit"], cwd=etu, capture_output=True, text=True)
            if r.returncode != 0:
                # refus attendu : la recette de la note doit passer, et la note doit la donner
                for cmd in (["git", "stash", "-q"], ["git", "pull", "-q", "--no-rebase", "--no-edit"], ["git", "stash", "pop", "-q"]):
                    r2 = subprocess.run(cmd, cwd=etu, capture_output=True, text=True)
                    if r2.returncode != 0:
                        ecarts.append(f"B : « {' '.join(cmd)} » a échoué : {(r2.stderr or r2.stdout).strip()[:300]}")
                        break
                texte_note = (etu / note).read_text(encoding="utf-8") if (etu / note).is_file() else ""
                if "git stash pop" not in texte_note or "git stash" not in texte_note:
                    ecarts.append(f"B : le git pull simple refuse, et {note} ne donne pas la recette git stash / git pull / git stash pop")
            if not modification_presente(etu):
                ecarts.append("B : la modification d'étudiant sur un fichier suivi a été perdue")
            verifier_fichiers(etu, "B")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return ecarts


CONTROLES = {"liens": liens, "chemins": chemins, "edition": edition, "anciens": anciens, "format": format_seances, "porte": porte_unique}


# ---- autotest : chaque contrôle doit voir une faute plantée ------------------------------------------------------------
def _depot_jouet(base, fichiers):
    base.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=base, check=True)
    git(base, "config", "user.email", "t@exemple.invalid")
    git(base, "config", "user.name", "t")
    for f, c in fichiers.items():
        (base / f).parent.mkdir(parents=True, exist_ok=True)
        (base / f).write_text(c, encoding="utf-8")
    git(base, "add", *fichiers)
    git(base, "commit", "-q", "-m", "jouet")
    return base


def _six_titres(sauf=None, permuter=False):
    t = [x for x in TITRES if x != sauf]
    if permuter:
        t[0], t[1] = t[1], t[0]
    return "# Séance\n\n" + "".join(f"## {i}. {x}\n\ntexte\n\n" for i, x in enumerate(t, start=1))


def autotest():
    echecs = []

    def attendre(nom, ecarts, vide):
        if bool(ecarts) == vide:
            echecs.append(f"{nom} : {'écart attendu non vu' if not vide else 'faux positif ' + str(ecarts)}")

    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        # R-1
        bon = _depot_jouet(d / "l_bon", {"README.md": "[a](docs/a.md) [b](https://x.invalid) [c](#t)\n", "docs/a.md": "ok\n"})
        attendre("liens (sain)", liens(bon), vide=True)
        mauvais = _depot_jouet(d / "l_mauvais", {"README.md": "[a](docs/absent.md)\n"})
        attendre("liens (lien cassé)", liens(mauvais), vide=False)
        nb = json.dumps({"cells": [{"cell_type": "markdown", "source": ["[x](absent.md)"]}]})
        ipynb = _depot_jouet(d / "l_nb", {"n.ipynb": nb})
        attendre("liens (notebook)", liens(ipynb), vide=False)
        ex = _depot_jouet(d / "l_code", {"README.md": "`[x](absent.md)`\n```\n[y](absent.md)\n```\n"})
        attendre("liens (exemple en code, non compté)", liens(ex), vide=True)
        # R-1b : dossier de binaire présent / absent, fichier .dat présent / absent
        ok_c = _depot_jouet(d / "c_ok", {"m/a.dat": '"../b/x.dat"   Fichier - x\n"../b/DISCON.so"   DLL - x\n', "b/x.dat": "x\n", "b/lisez.txt": "x\n"})
        attendre("chemins (sain, .so généré non suivi)", chemins(ok_c), vide=True)
        ko_c = _depot_jouet(d / "c_ko", {"m/a.dat": '"../b/absent.dat"   Fichier - x\n', "b/x.dat": "x\n"})
        attendre("chemins (fichier absent)", chemins(ko_c), vide=False)
        ko_so = _depot_jouet(d / "c_so", {"m/a.dat": '"../ancien/DISCON.so"   DLL - x\n', "b/x.dat": "x\n"})
        attendre("chemins (dossier du .so absent)", chemins(ko_so), vide=False)
        # R-7 : édition d'un fichier suivi
        base7 = {"modeles/fixe/main.fst": "x\n", "results/.gitkeep": ""}
        for nom, texte, vide in [("modifiez un fichier suivi", "Modifiez `modeles/fixe/main.fst` puis relancez.\n", False),
                                 ("éditeur sur un fichier suivi", "```bash\nnano modeles/fixe/main.fst\n```\n", False),
                                 ("sed -i sur un fichier suivi", "```bash\nsed -i 's/a/b/' modeles/fixe/main.fst\n```\n", False),
                                 ("copie sous results", "Copiez `modeles/fixe/main.fst` sous `results/` puis modifiez la copie.\n", True),
                                 ("lecture seule", "Ouvrez `modeles/fixe/main.fst` (lecture seule) : ne le modifiez pas.\n", True),
                                 ("éditer un fichier non suivi", "Éditez `results/lct_0b.csv`.\n", True)]:
            attendre(f"edition ({nom})", edition(_depot_jouet(d / ("e_" + str(abs(hash(nom)))), {**base7, "seances/0a/README.md": texte})), vide)
        # R-2
        for nom, texte, vide in [("tutorials/ cité", "voir tutorials/lheea/\n", False), ("models/ cité", "models/oc4_rtest\n", False),
                                 ("modeles/ nouveau", "modeles/oc4_rtest\n", True), ("annexes/papers nouveau", "annexes/papers/x.md\n", True),
                                 ("papers/ ancien", "voir papers/x.md\n", False), ("annexes/outils nouveau", "annexes/outils/y.py\n", True),
                                 ("URL gitlab LHEEA", "https://gitlab.in2p3.fr/lheea/oracle/tutorials/openfast_quickstart\n", True)]:
            attendre(f"anciens ({nom})", anciens(_depot_jouet(d / ("a_" + str(abs(hash(nom)))), {"R.md": texte})), vide)
        ann = _depot_jouet(d / "a_annexes", {"annexes/lheea/R.md": "tutorials/lheea/\n"})
        attendre("anciens (annexes exemptées)", anciens(ann), vide=True)
        # R-4
        for nom, contenu, vide in [("six titres", _six_titres(), True), ("titre manquant", _six_titres(sauf="Post-traiter"), False),
                                   ("ordre faux", _six_titres(permuter=True), False), ("titre en trop", _six_titres() + "## 7. Divers\n", False)]:
            attendre(f"format ({nom})", format_seances(_depot_jouet(d / ("f_" + str(abs(hash(nom)))), {"seances/0a/README.md": contenu})), vide)
        attendre("format (README absent)", format_seances(_depot_jouet(d / "f_absent", {"seances/0a/x.md": "x\n"})), vide=False)
        # R-5
        porte_ok = _depot_jouet(d / "p_ok", {"README.md": "[0a](seances/0a/README.md) [pt](s9gm/POST-TRAITER.md)\n",
                                             "seances/0a/README.md": "x\n", "s9gm/POST-TRAITER.md": "x\n"})
        attendre("porte (sain)", porte_unique(porte_ok), vide=True)
        sans = _depot_jouet(d / "p_sans", {"README.md": "[pt](s9gm/POST-TRAITER.md)\n", "seances/0a/README.md": "x\n", "s9gm/POST-TRAITER.md": "x\n"})
        attendre("porte (séance non citée)", porte_unique(sans), vide=False)
        concur = _depot_jouet(d / "p_conc", {"README.md": "[0a](seances/0a/README.md) [pt](s9gm/POST-TRAITER.md)\n",
                                             "seances/0a/README.md": "Commencez ici.\n", "s9gm/POST-TRAITER.md": "x\n"})
        attendre("porte (second point d'entrée)", porte_unique(concur), vide=False)
        # R-6 : nouvel état qui range un fichier SUIVI à l'emplacement d'un fichier d'étudiant => conflit à voir
        base = _depot_jouet(d / "t_base", {"a.txt": "a\n"})
        git(base, "update-ref", "refs/remotes/origin/main", "HEAD")
        (base / "lct_0b.csv").write_text("suivi côté cours\n", encoding="utf-8")
        git(base, "add", "lct_0b.csv")
        git(base, "commit", "-q", "-m", "nouveau")
        attendre("transition (collision)", transition(base, fichiers_etudiant={"lct_0b.csv": "étudiant\n"}), vide=False)
        sain = _depot_jouet(d / "t_sain", {"a.txt": "a\n"})
        git(sain, "update-ref", "refs/remotes/origin/main", "HEAD")
        (sain / "b.txt").write_text("b\n", encoding="utf-8")
        git(sain, "add", "b.txt")
        git(sain, "commit", "-q", "-m", "nouveau")
        attendre("transition (sain)", transition(sain, fichiers_etudiant={"results/x.csv": "x\n", "lct_0b.csv": "y\n"}), vide=True)
        # scénario B : fichier suivi modifié par l'étudiant et déplacé par la restructuration
        for nom, avec_note, vide in [("fichier suivi déplacé, note sans recette", "Rien à signaler.\n", False),
                                     ("fichier suivi déplacé, note avec recette", "git stash\ngit pull\ngit stash pop\n", True)]:
            ancien = _depot_jouet(d / ("b_" + str(abs(hash(nom)))), {"tutorials/prise_en_main/F01/main.fst": "a\nb\nc\n"})
            git(ancien, "update-ref", "refs/remotes/origin/main", "HEAD")
            git(ancien, "mv", "tutorials/prise_en_main/F01/main.fst", "cas_F01_main.fst")
            (ancien / "TRANSITION.md").write_text(avec_note, encoding="utf-8")
            git(ancien, "add", "TRANSITION.md")
            git(ancien, "commit", "-q", "-m", "déplacement")
            attendre(f"transition ({nom})", transition(ancien, fichiers_etudiant={"results/x.csv": "x\n"}), vide)
        attendre("transition (reste sans note)", transition(sain, fichiers_etudiant={"vieux/F03.outb": "z\n"}), vide=False)
    for e in echecs:
        print("AUTOTEST ÉCHEC :", e)
    print("autotest :", "ÉCHEC" if echecs else "ok (chaque contrôle voit sa faute plantée et ne crie pas au loup)")
    return 1 if echecs else 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("controle", nargs="?", choices=[*CONTROLES, "transition", "tout"])
    p.add_argument("--racine", default=str(Path(__file__).resolve().parents[1]))
    p.add_argument("--ancien", default="origin/main")
    p.add_argument("--nouveau", default="HEAD")
    p.add_argument("--autotest", action="store_true")
    a = p.parse_args(argv)
    if a.autotest:
        return autotest()
    if not a.controle:
        p.error("un contrôle ou --autotest")
    noms = list(CONTROLES) if a.controle == "tout" else [a.controle]
    code = 0
    for nom in noms:
        ecarts = transition(a.racine, a.ancien, a.nouveau) if nom == "transition" else CONTROLES[nom](a.racine)
        for e in ecarts:
            print(f"[{nom}] {e}")
        if nom == "chemins":
            print(f"[chemins] {chemins.verifies} chemins d'entrée OpenFAST examinés, {chemins.toleres} références préexistantes tolérées")
        if nom == "liens":
            print(f"[liens] {liens.verifies} liens relatifs vérifiés dans {liens.fichiers} fichiers .md/.ipynb")
        print(f"[{nom}] {len(ecarts)} écart(s)")
        code |= 1 if ecarts else 0
    return code


if __name__ == "__main__":
    sys.exit(main())
