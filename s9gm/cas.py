"""s9gm.cas — fabriquer une série de cas OpenFAST depuis une Load Case Table (LCT).

### Bloc Théorie

1. **Question physique** — Un dimensionnement ne repose pas sur un calcul mais sur une liste de
   cas de charge (vent, houle, durée…) tirée des données du site. Comment fabriquer cette liste de
   calculs sans changer à la main, cas après cas, des paramètres dans des fichiers de plusieurs
   centaines de lignes — et sans rien changer *d'autre* par erreur ? Et, pour un vent turbulent,
   comment obtenir le champ de vent d'un cas *depuis sa ligne de LCT* — même graine, même champ ?
2. **Modèle** — une LCT est un tableau : une ligne = un cas, une colonne = un paramètre. Un cas
   OpenFAST = un modèle partagé (la machine, identique pour tous les cas) + un dossier léger par
   cas (`main.fst`, `config_inflow.dat`) qui ne contient que ce qui change. Un paramètre est
   désigné par `fichier.Clé` (ex. `fst.TMax`, `inflow.HWindSpeed`) : la clé est le nom écrit dans le
   fichier OpenFAST à droite de la valeur. **Domaine de validité** : paramètres scalaires d'une
   seule ligne (nombre, texte) dans `main.fst` et `config_inflow.dat` ; pas de listes
   (`LinTimes`…), pas d'autre module (ElastoDyn, HydroDyn : à ajouter par la même méthode). Une
   clé absente ou présente deux fois dans le fichier est une erreur. Une *cellule vide* de la LCT
   est lue comme « garder la valeur du modèle » : c'est voulu, mais c'est un choix à connaître.
   Un préfixe de plus, `turbsim.Clé`, édite de la même façon une copie de `turbsim.inp` du modèle
   (graine, vitesse de référence, intensité de turbulence…) et lance TurbSim : le champ `.bts` du cas est
   produit dans `Wind/<cas>.bts` et `inflow.WindType`/`inflow.FileName_BTS` y sont pointés, sauf si la
   LCT les fixe elle-même. TurbSim est déterministe : même graine, même entrée → même `.bts`.
3. **Ordre de grandeur attendu** — la méthode : un cas que vous fabriquez à la main (F01 du
   tutoriel) doit être reproduit *à l'identique* (comparaison `diff`) par une ligne de LCT. Si la
   machine et les sorties ne diffèrent d'aucune ligne, le générateur ne fait que ce que vous lui
   dites.
4. **Ce que le modèle ne permet pas de conclure** — qu'une LCT bien fabriquée soit une bonne LCT :
   `cas` ne dit rien de la représentativité des cas choisis (phase 1), ni de leur nombre suffisant.
5. **Renvois** — fiche F1 (cas F01/F02 du tutoriel) ; `tutorials/prise_en_main/README.md`
   (modèle partagé + dossier léger, règle de résolution des chemins) ; manuel OpenFAST v5.0.0,
   format des fichiers d'entrée ; `ENONCE.md`, phase 1 (Load Case Table).

Méthode d'édition : `openfast_toolbox` relit chaque fichier produit et confirme que la valeur est
bien celle demandée (contrôle indépendant). L'écriture, elle, remplace *uniquement* le champ valeur
de la ligne portant la clé (en remettant les guillemets d'un champ texte et en retirant une
annotation `[migre …]` devenue fausse) : `FASTInputFile.write` de l'outil reformate les titres et les
espaces, ce qui rendrait la comparaison `diff` avec un cas fait à la main impossible.
"""
import csv
import json
import os
import re
import subprocess
from pathlib import Path

from openfast_toolbox.io import FASTInputFile

from . import __version__

# Clés de main.fst qui désignent un fichier d'entrée de module : réécrites vers le modèle partagé.
# InflowFile reste local au cas (c'est lui qui change d'un cas à l'autre).
CLES_FICHIERS_PARTAGES = ("EDFile", "AeroFile", "ServoFile", "SeaStFile", "HydroFile", "SubFile",
                          "MooringFile")
FICHIERS = {"fst": "main.fst", "inflow": "config_inflow.dat"}
TURBSIM = "turbsim"   # préfixe de colonne : édite `turbsim.inp` du modèle, voir `generer_vent`
_COMMENTAIRE_MIGRE = re.compile(r"\s*\[migre[^\]]*\]\s*$")


def lire_lct(chemin_csv):
    """Lit une LCT au format CSV (séparateur « , » ou « ; »). Colonne `cas` obligatoire ; les autres
    colonnes sont `fichier.Clé` avec fichier ∈ {fst, inflow, turbsim}. Renvoie une liste de dicts.

    Un tableur s'exporte en CSV (« enregistrer sous… ») : on évite ainsi une dépendance de plus."""
    with open(chemin_csv, encoding="utf-8-sig", newline="") as f:
        echantillon = f.read(2048)
        f.seek(0)
        delim = ";" if echantillon.count(";") > echantillon.count(",") else ","
        lignes = list(csv.DictReader(f, delimiter=delim))
    if not lignes or "cas" not in lignes[0]:
        raise ValueError(f"{chemin_csv} : colonne « cas » obligatoire")
    noms = [l["cas"].strip() for l in lignes]
    if len(set(noms)) != len(noms):
        raise ValueError("noms de cas en double dans la LCT")
    for col in lignes[0]:
        if col != "cas" and col.split(".", 1)[0] not in (*FICHIERS, TURBSIM):
            raise ValueError(f"colonne « {col} » : le préfixe doit être l'un de "
                             f"{sorted((*FICHIERS, TURBSIM))}")
    return [{k.strip(): v.strip() for k, v in l.items()} for l in lignes]


def _motif_cle(cle):
    # valeur (entre guillemets ou non) puis séparateur puis la clé exacte, seule sur son champ
    return re.compile(r'^(?P<pre>\s*)(?P<val>"[^"]*"|\S+)(?P<mid>\s+)(?P<cle>' + re.escape(cle)
                      + r')(?P<reste>(\s.*)?)$')


def remplacer_valeur(lignes, cle, valeur):
    """Remplace la valeur de `cle` dans `lignes` (liste de str, sans saut de ligne). Renvoie
    l'ancienne valeur. Échoue si la clé n'apparaît pas exactement une fois."""
    motif = _motif_cle(cle)
    trouves = [i for i, l in enumerate(lignes) if motif.match(l)]
    if len(trouves) != 1:
        raise KeyError(f"clé « {cle} » trouvée {len(trouves)} fois (attendu : 1)")
    i = trouves[0]
    m = motif.match(lignes[i])
    ancien = m["val"]
    if ancien.startswith('"') and not valeur.startswith('"'):
        valeur = f'"{valeur}"'  # champ texte : OpenFAST attend des guillemets, la LCT n'en porte pas
    reste = _COMMENTAIRE_MIGRE.sub("", m["reste"]) if ancien != valeur else m["reste"]
    lignes[i] = m["pre"] + valeur + m["mid"] + m["cle"] + reste
    return ancien


def _valeur_de(lignes, cle):
    motif = _motif_cle(cle)
    trouves = [motif.match(l) for l in lignes if motif.match(l)]
    if len(trouves) != 1:
        raise KeyError(f"clé « {cle} » trouvée {len(trouves)} fois (attendu : 1)")
    return trouves[0]["val"]


def _lire_lignes(chemin):
    with open(chemin, encoding="utf-8", newline="") as f:
        texte = f.read()
    fin = "\r\n" if "\r\n" in texte else "\n"
    return texte.split(fin), fin


def _ecrire_lignes(chemin, lignes, fin):
    with open(chemin, "w", encoding="utf-8", newline="") as f:
        f.write(fin.join(lignes))


def _sans_guillemets(v):
    return str(v).strip().strip('"')


def _egales(a, b):
    a, b = _sans_guillemets(a), _sans_guillemets(b)
    try:
        return float(a) == float(b)
    except ValueError:
        return a == b


def _controler_relecture(chemin, attendu):
    """Contrôle indépendant : openfast_toolbox relit le fichier produit et doit y trouver les
    valeurs demandées."""
    f = FASTInputFile(str(chemin))
    for cle, valeur in attendu.items():
        if not _egales(f[cle], valeur):
            raise AssertionError(f"{chemin} : relu {cle} = {f[cle]!r}, demandé {valeur!r}")


def generer_vent(dossier, modele, modifs, executable="turbsim", executer=True):
    """Fabrique `dossier/Wind/<cas>.inp` depuis `modele/turbsim.inp` (clés de `modifs` remplacées, comme
    pour `main.fst`) et, si `executer`, lance TurbSim pour produire `dossier/Wind/<cas>.bts`.
    Renvoie `{"entree": chemin du .inp, "bts": chemin du .bts ou None}`.

    Le champ de vent d'un cas ne dépend que de son fichier d'entrée (graine comprise) : relancer donne
    le même `.bts`. `RandSeed1` est donc à fixer explicitement dans la LCT pour qu'un cas se reproduise."""
    dossier, modele = Path(dossier), Path(modele)
    modele_inp = modele / "turbsim.inp"
    if not modele_inp.is_file():
        raise FileNotFoundError(f"{modele_inp} : colonnes turbsim.* dans la LCT mais pas de turbsim.inp "
                                "dans le modèle")
    vent = dossier / "Wind"
    vent.mkdir(exist_ok=True)
    lignes, fin = _lire_lignes(modele_inp)
    for cle, val in modifs.items():
        remplacer_valeur(lignes, cle, val)
    # gabarit à trous (seances/0b/turbsim_gabarit.inp) : un champ resté « A_COMPLETER » est refusé, nommé
    trous = [m[1] for l in lignes if (m := re.match(r"^\s*A_COMPLETER\s+(\w+)", l))]
    if trous:
        raise ValueError(f"{modele_inp.name} : champ(s) à compléter, à choisir et justifier : "
                         f"{', '.join(trous)} (colonnes turbsim.<Clé> de la LCT, ou éditez le fichier)")
    entree = vent / f"{dossier.name}.inp"
    _ecrire_lignes(entree, lignes, fin)
    _controler_relecture_turbsim(entree, modifs)
    bts = vent / f"{dossier.name}.bts"
    bts.unlink(missing_ok=True)  # un champ d'un calcul précédent ne doit pas passer pour le nouveau
    if executer:
        r = subprocess.run([executable, entree.name], cwd=vent, capture_output=True, text=True)
        if r.returncode != 0 or not bts.is_file():
            raise RuntimeError(f"TurbSim n'a pas produit {bts.name} (code {r.returncode}) :\n"
                               f"{(r.stdout + r.stderr)[-600:]}")
    return {"entree": entree, "bts": bts if executer else None}


def _controler_relecture_turbsim(chemin, attendu):
    """Relecture indépendante du .inp produit (même contrôle que pour main.fst)."""
    f = FASTInputFile(str(chemin))
    for cle, valeur in attendu.items():
        if not _egales(f[cle], valeur):
            raise AssertionError(f"{chemin} : relu {cle} = {f[cle]!r}, demandé {valeur!r}")


def generer_cas(ligne_lct, modele, sortie, executer_turbsim=True):
    """Fabrique le dossier `sortie/<cas>/` depuis le modèle partagé `modele` (dossier contenant
    `main.fst` et `config_inflow.dat`). Renvoie le dossier du cas.

    Pourquoi un dossier léger : la machine (`modele`) est écrite une seule fois ; chaque cas ne
    porte que ce qui change, donc ce qu'on relit en revue est exactement ce qu'on a voulu changer.
    Écrit aussi `journal_cas.json` : valeurs avant/après de chaque paramètre modifié. Avec des colonnes
    `turbsim.*`, fabrique aussi le champ de vent (`generer_vent`) ; `executer_turbsim=False` n'écrit que
    le `.inp`."""
    modele, sortie = Path(modele), Path(sortie)
    dossier = sortie / ligne_lct["cas"]
    dossier.mkdir(parents=True, exist_ok=True)
    # Les entrées vont changer : d'anciennes sorties ne correspondraient plus au cas. Sans cette
    # purge, `lancer` croirait le cas terminé et rendrait un résultat périmé.
    for ancien in [dossier / "run.log", *dossier.glob("*.outb"), *dossier.glob("*.out")]:
        ancien.unlink(missing_ok=True)
    rel = Path(os.path.relpath(modele.resolve(), dossier.resolve())).as_posix()

    modifs = {fich: {} for fich in (*FICHIERS, TURBSIM)}
    for col, val in ligne_lct.items():
        if col == "cas" or val == "":
            continue
        fich, cle = col.split(".", 1)
        modifs[fich][cle] = val
    if modifs[TURBSIM]:  # le champ de vent produit par TurbSim est le vent du cas, sauf avis contraire
        modifs["inflow"].setdefault("WindType", "3")
        modifs["inflow"].setdefault("FileName_BTS", f"Wind/{ligne_lct['cas']}.bts")

    journal = {"cas": ligne_lct["cas"], "s9gm": __version__, "modele": rel, "modifications": [],
               "chemins_reecrits": []}
    for fich, nom in FICHIERS.items():
        lignes, fin = _lire_lignes(modele / nom)
        if fich == "fst":
            for cle in CLES_FICHIERS_PARTAGES:
                valeur = _valeur_de(lignes, cle)
                if _sans_guillemets(valeur) != "unused":
                    remplacer_valeur(lignes, cle, f'"{rel}/{_sans_guillemets(valeur)}"')
                    journal["chemins_reecrits"].append(cle)
        for cle, val in modifs[fich].items():
            ancien = remplacer_valeur(lignes, cle, val)
            journal["modifications"].append({"fichier": nom, "cle": cle,
                                             "avant": _sans_guillemets(ancien), "apres": val})
        _ecrire_lignes(dossier / nom, lignes, fin)
        _controler_relecture(dossier / nom, modifs[fich])
    if modifs[TURBSIM]:
        res = generer_vent(dossier, modele, modifs[TURBSIM], executer=executer_turbsim)
        journal["turbsim"] = {"entree": res["entree"].relative_to(dossier).as_posix(),
                              "parametres": modifs[TURBSIM],
                              "bts": res["bts"].relative_to(dossier).as_posix() if res["bts"] else None}
    (dossier / "journal_cas.json").write_text(
        json.dumps(journal, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return dossier


def generer_serie(lct_csv, modele, sortie, executer_turbsim=True):
    """Un dossier par ligne de la LCT. Renvoie la liste des dossiers créés, dans l'ordre."""
    return [generer_cas(l, modele, sortie, executer_turbsim) for l in lire_lct(lct_csv)]
