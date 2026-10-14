<!-- destinations: github -->
# Phase 6 — Synthèse commune et soutenance

Consigne autonome de la phase. Le cadre du projet (objectifs, évaluation, règles) est dans [`../../ENONCE.md`](../../ENONCE.md) ; [séance précédente](../phase5/README.md).

## 1. Objectif

Synthèse commune des trois groupes et soutenance. Volume indicatif : 4 h. Rendu : **Soutenance**.

## 2. Avant de commencer

**Premier geste, depuis n'importe quel dossier : `s9gm doctor`** (il vérifie votre poste et donne la commande exacte pour chaque point en défaut ; si `s9gm` est introuvable, activez l'environnement : `micromamba activate s9gm-fowt`). Un terminal ne vous est pas familier : [`annexes/TERMINAL.md`](../../annexes/TERMINAL.md), une page.

Prérequis : l'environnement installé en [séance 0a](../0a/README.md) (`openfast -v` → `OpenFAST-v5.0.0`, contrôleur compilé).

**Où vit ce que vous produisez** : sous `results/` et `rendus/` (ignorés par git) ; `cas/`, `modeles/` et `seances/` se lisent et se lancent sans être modifiés.

## 3. À faire, étape par étape

Les trois groupes mettent leurs résultats en commun dans **un seul tableau de sensibilité** : pour chaque famille de paramètres, l'effet sur le dommage en pied de tour, le dommage aux chaumards et les extrêmes. Question finale : **pour un projet réel sur ce site, quelles études de sensibilité demanderiez-vous au bureau d'études, et lesquelles jugeriez-vous inutiles ?**

**Le point commun est le cas `D01`** (cas de référence de la phase 2, `cas/D01`, le même pour les trois groupes) : il ne sert que de **contrôle de cohérence du modèle** (les trois groupes retrouvent les mêmes maximums sur `D01`) ; si les trois `D01` ne s'accordent pas, il y a un défaut de méthode à trouver **avant** toute comparaison de familles.
**Un effet se mesure contre la ligne de référence de sa famille** (`SREF`, phase 2, étape 3 : même vent, même graine, même houle, **un seul paramètre change**), et non contre `D01` : `D01` est en vent stationnaire et en houle régulière, les cas de sensibilité sont turbulents, et rapporter à `D01` mêlerait **deux causes** (le paramètre étudié et le passage du stationnaire au turbulent). **La sensibilité de chaque groupe part de la LCT du groupe** (phase 2, étape 3).
Les groupes échangent leurs fichiers par **dépôt sur Vega**, avec un **nom imposé par groupe** : `synthese_<groupe>.csv` (celui que l'étape 1 écrit dans `rendus/`). Chacun rapatrie les trois fichiers dans `rendus/groupes/` (dossier ignoré par git).
Les commandes se lancent **depuis n'importe quel dossier**, environnement `s9gm-fowt` activé. **Chaque bloc est autonome** et lit des fichiers écrits par les phases précédentes dans `results/` (`results/phase3_parametres.json`, `results/D01`, `results/phase2/S*`, `results/lct_sensibilite.csv`, `results/phase4_uls.csv`).
Les valeurs entre `<…>` sont **vos choix** : la consigne ne les donne pas.

### Étape 1 — La synthèse de votre groupe (un fichier, au format commun)

Pour `D01`, pour la **référence de votre famille** (`SREF`) et pour chaque cas de votre sensibilité (`results/phase2/S*`) : le dommage de fatigue en pied de tour **rapporté à une heure** (même courbe S-N, même section, même `SCF` que la phase 3), le DEL de la tour, le DEL de la ligne la plus chargée, le maximum du moment en pied de tour, de la tension de chaumard et des mouvements du flotteur (`PtfmSurge`, `PtfmHeave`, `PtfmPitch`). Pour chaque cas ULS (phase 4) : le maximum de la tension et du moment en pied. Le format est **le même pour les trois groupes** : c'est ce qui permet de les rassembler.

```python
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from s9gm import lire, structure
from s9gm.chemins import RENDUS, RESULTS

from s9gm import ma_copie
fatigue = ma_copie("fatigue")

P = json.loads((RESULTS / "phase3_parametres.json").read_text(encoding="utf-8"))
GROUPE, FAMILLE = "<votre groupe>", "<votre famille de paramètres>"
courbe = fatigue.CourbeSN(**P["sn"])
A, I, W = structure.section_tubulaire(P["D"], P["t_paroi"])
sens = pd.read_csv(RESULTS / "lct_sensibilite.csv").set_index("cas")
variables = [c for c in sens.columns if c != "cas" and sens[c].astype(str).nunique() > 1]         # ce qui varie dans votre sensibilité

lignes = []
for dossier in [RESULTS / "D01", *sorted((RESULTS / "phase2").glob("S*"))]:
    df, unites = lire.lire(dossier / "main.outb")
    u = df[df["Time"] >= P["T_TRANS"]]
    T = float(u["Time"].iloc[-1] - u["Time"].iloc[0])
    sigma = P["SCF"] * structure.contrainte_flexion(u["TwrBsMyt"].to_numpy() * 1e3, P["D"], I) / 1e6
    r = fatigue.rainflow(sigma)
    tensions = [c for c in ("FAIRTEN1", "FAIRTEN2", "FAIRTEN3") if c in u.columns] or ["T[1]", "T[2]", "T[3]"]     # MAP++ : T[i] ↔ FAIRTEN i (phase 4)
    del_lignes = []
    for tension in tensions:
        rl = fatigue.rainflow(u[tension].to_numpy())
        del_lignes.append(fatigue.del_court_terme(rl["etendue"], rl["compte"], P["M_LIGNE"], P["F_EQ"] * T))
    variation = "" if dossier.name in ("D01", "SREF") else "; ".join(f"{c} = {sens.loc[dossier.name, c]}" for c in variables)
    type_ = "point commun" if dossier.name == "D01" else ("référence de famille" if dossier.name == "SREF" else "sensibilité")
    lignes.append({"groupe": GROUPE, "famille": FAMILLE, "type": type_,
                   "cas": dossier.name, "variation": variation,
                   "dommage_tour_par_heure": fatigue.miner(r["etendue"], r["compte"], courbe, t=P["t_paroi"] * 1e3, t_ref=P["T_REF"]) * 3600 / T,
                   "DEL_tour_MPa": fatigue.del_court_terme(r["etendue"], r["compte"], P["M_TOUR"], P["F_EQ"] * T),
                   "DEL_ligne_max_N": max(del_lignes),
                   "max_TwrBsMyt_kNm": float(u["TwrBsMyt"].abs().max()), "max_tension_N": float(max(u[t].max() for t in tensions)),
                   **{f"max_{c}": float(u[c].abs().max()) for c in ("PtfmSurge", "PtfmHeave", "PtfmPitch")}})
uls = pd.read_csv(RESULTS / "phase4_uls.csv")
for _, x in uls.iterrows():
    lignes.append({"groupe": GROUPE, "famille": FAMILLE, "type": "extrême", "cas": x["cas"], "variation": "",
                   "max_TwrBsMyt_kNm": x["max_TwrBsMyt_kNm"], "max_tension_N": x["max_tension"],
                   **{c: x[c] for c in ("max_PtfmSurge", "max_PtfmHeave", "max_PtfmPitch")}})
pd.DataFrame(lignes).to_csv(RENDUS / f"synthese_{GROUPE}.csv", index=False)
print(pd.DataFrame(lignes).round(4).to_string(index=False))
```

**Vous devez voir** : une ligne pour `D01` (type `point commun`), une pour `SREF` (type `référence de famille`), une par cas de votre sensibilité, une par cas ULS, et le fichier `rendus/synthese_<groupe>.csv`. **Transmettez ce fichier** aux deux autres groupes : c'est lui qui est rassemblé à l'étape suivante.

| Symptôme | Cause | Geste |
|---|---|---|
| `FileNotFoundError … results/D01/main.outb` | le cas de référence n'a pas été lancé | `bash cas/run_cas.sh D01` (phase 2, étape 1) |
| aucune ligne `sensibilité` | pas de `results/phase2/S*` | phase 2, étape 3 |
| `FileNotFoundError … phase4_uls.csv` | la phase 4 n'est pas terminée | phase 4, étape 3 |
| `KeyError … phase3_parametres.json` | la phase 3 n'a pas été faite avec ces commandes | refaites la phase 3, étape 3 |

### Étape 2 — Rassembler les trois groupes, vérifier le point commun

Vous rassemblez les trois fichiers de synthèse. **Avant** de comparer les familles, **contrôlez le point commun** : les trois `D01` donnent des **maximums** de moment et de tension (`max_TwrBsMyt_kNm`, `max_tension_N`) qui ne dépendent que d'OpenFAST, pas de votre post-traitement. Ils doivent concorder ; **écrivez la tolérance** à laquelle vous les jugez identiques et **pourquoi** (même modèle, même version, même cas : ce qui reste est de l'arrondi).
Les dommages et les DEL, eux, dépendent de **vos choix** (section, courbe S-N) : ils **ne se comparent pas** d'un groupe à l'autre en valeur absolue, mais **rapportés à la référence de leur famille**.

```python
from pathlib import Path

import pandas as pd
from s9gm.chemins import RENDUS

fichiers = sorted((RENDUS / "groupes").glob("*.csv"))
print("fichiers rassemblés :", [f.name for f in fichiers])
tout = pd.concat([pd.read_csv(f) for f in fichiers], ignore_index=True)

commun = tout[tout["type"] == "point commun"].set_index("groupe")
TOLERANCE = <votre tolérance relative sur D01>
ecart = commun[["max_TwrBsMyt_kNm", "max_tension_N"]].apply(lambda c: (c - c.mean()).abs() / c.mean())
print("écart relatif des trois D01 à leur moyenne :")
print(ecart.round(6).to_string())
print("point commun cohérent à la tolérance retenue ?", bool((ecart <= TOLERANCE).all().all()))

# effet de chaque variation, rapporté à la ligne de référence de SA famille (même groupe, même famille : un seul paramètre change)
lignes = []
for (g, famille), bloc in tout.groupby(["groupe", "famille"]):
    refs = bloc[bloc["type"] == "référence de famille"]
    if refs.empty:
        raise ValueError(f"groupe {g}, famille {famille} : aucune ligne « référence de famille » (cas SREF de la phase 2, étape 3) ; "
                         "relancez l'étape 3 de la phase 2, puis l'étape 1 de cette phase")
    ref = refs.iloc[0]
    for _, x in bloc[bloc["type"] == "sensibilité"].iterrows():
        lignes.append({"groupe": g, "famille": x["famille"], "cas": x["cas"], "variation": x["variation"],
                       "dommage_tour_relatif": x["dommage_tour_par_heure"] / ref["dommage_tour_par_heure"],
                       "DEL_ligne_relatif": x["DEL_ligne_max_N"] / ref["DEL_ligne_max_N"],
                       "max_moment_relatif": x["max_TwrBsMyt_kNm"] / ref["max_TwrBsMyt_kNm"],
                       "max_tension_relatif": x["max_tension_N"] / ref["max_tension_N"],
                       "max_PtfmSurge_relatif": x["max_PtfmSurge"] / ref["max_PtfmSurge"],
                       "max_PtfmHeave_relatif": x["max_PtfmHeave"] / ref["max_PtfmHeave"],
                       "max_PtfmPitch_relatif": x["max_PtfmPitch"] / ref["max_PtfmPitch"]})
synthese = pd.DataFrame(lignes)
synthese.to_csv(RENDUS / "tableau_synthese.csv", index=False)
print(synthese.round(3).to_string(index=False))
```

**Vous devez voir** : la liste des fichiers rassemblés (trois), l'écart relatif des trois `D01` à leur moyenne et le verdict de cohérence à **votre** tolérance, puis le **tableau de synthèse** : une ligne par variation, avec ses sept effets **relatifs à la référence de sa famille** (1 = pas d'effet), écrit dans `rendus/tableau_synthese.csv`.
Si le verdict est `False`, **cherchez pourquoi avant de continuer** (version d'OpenFAST, modèle modifié par erreur, fenêtre différente) ; ne le contournez pas en élargissant la tolérance sans le dire.

| Symptôme | Cause | Geste |
|---|---|---|
| `ValueError: No objects to concatenate` | `rendus/groupes/` est vide | déposez-y les trois fichiers `synthese_<groupe>.csv` |
| `ValueError … aucune ligne « référence de famille »` | le fichier d'un groupe n'a pas de ligne `SREF` : la phase 2, étape 3, a été faite sans la référence, ou l'étape 1 n'a pas relu `results/phase2/SREF` | relancez l'étape 3 de la phase 2 (elle ajoute `SREF`), puis l'étape 1 ; le message nomme le groupe et la famille |
| un groupe n'a pas de ligne `point commun` | son fichier n'a pas été produit par l'étape 1 (`results/D01` absent) | `bash cas/run_cas.sh D01`, puis l'étape 1 |
| écarts relatifs de `D01` de plusieurs % | cas ou version différents d'un groupe à l'autre | comparez `main.fst` et `openfast -v` de chaque groupe |

### Étape 3 — Les figures de la synthèse

Une figure par effet, **une courbe par famille**, avec la ligne de provenance de `s9gm.visu` (cas, modèle, état). Une figure sans ordonnée lisible ne se discute pas : vérifiez les échelles avant de la mettre dans la soutenance.

```python
from pathlib import Path

import pandas as pd
from s9gm import visu
from s9gm.chemins import RENDUS

synthese = pd.read_csv(RENDUS / "tableau_synthese.csv")
EFFETS = [("dommage_tour_relatif", "dommage du pied de tour / référence"), ("DEL_ligne_relatif", "DEL de la ligne / référence"),
          ("max_moment_relatif", "moment max en pied / référence"), ("max_tension_relatif", "tension max / référence"),
           ("max_PtfmSurge_relatif", "cavalement max / référence"), ("max_PtfmPitch_relatif", "tangage max / référence")]
panneaux = []
for colonne, etiquette in EFFETS:
    courbes = []
    for famille, g in synthese.groupby("famille"):
        courbes.append({"label": famille, "x": list(range(1, len(g) + 1)), "y": g[colonne].to_numpy(), "style": "points"})
    panneaux.append({"ylabel": etiquette, "courbes": courbes})
fig = visu.tracer_courbes(panneaux, xlabel="variation (rang dans la sensibilité du groupe)", cas="références de famille et sensibilités de chaque groupe",
                          modele="flottant", etat="<votre date de rejeu>", titre="Effet de chaque famille de paramètres")
fig.savefig(RENDUS / "synthese_sensibilite.png", dpi=150, facecolor="white")
print("figure : rendus/synthese_sensibilite.png")
```

**Vous devez voir** : la figure `rendus/synthese_sensibilite.png`, six panneaux (un par effet), une couleur et une forme de point par famille, la ligne de provenance en pied. **Lisez-la** : quelle famille déplace le plus le dommage du pied de tour ? Celui des lignes ? Les extrêmes ? Y en a-t-il une dont l'effet est dans le bruit d'une seule réalisation (phase 2, étape 5) ?

| Symptôme | Cause | Geste |
|---|---|---|
| `ValueError` de `tracer_courbes` | plus de six panneaux, ou provenance manquante | six panneaux ici ; `cas`, `modele` et `etat` sont obligatoires |
| une seule famille tracée | les trois fichiers n'ont pas des `famille` distincts | vérifiez la colonne `famille` de chaque fichier de synthèse |

### Étape 4 — Rédiger la synthèse et préparer la soutenance

Rien à calculer de plus : le tableau (`rendus/tableau_synthese.csv`) et la figure disent ce que les trois groupes ont mesuré. Votre soutenance (voir « Ce qu'on rend ») répond à la **question finale** : pour un projet réel sur ce site, **quelles études de sensibilité demanderiez-vous au bureau d'études, et lesquelles jugeriez-vous inutiles ?**
Chaque réponse s'appuie sur une ligne du tableau (un effet chiffré, relatif à la référence de sa famille), dit **ce que cet effet ne permet pas de conclure** (une réalisation, un site, un modèle sans la souplesse du flotteur, une houle à 0°), et nomme ce qu'il faudrait faire de plus pour trancher.

**Temps mesurés** : les trois étapes de calcul (synthèse du groupe, rassemblement, figure) prennent moins de 1 s ; les simulations qu'elles lisent (`D01`, la sensibilité) sont celles des phases 2 à 4.

## 4. Post-traiter

La démarche générale, du `.outb` aux statistiques, aux figures et au DEL, est dans [`../../s9gm/POST-TRAITER.md`](../../s9gm/POST-TRAITER.md). Cette phase met en commun des résultats déjà post-traités : voir la section 3 (`rendus/tableau_synthese.csv`, `rendus/synthese_sensibilite.png`).

## 5. Ce qu'on rend

Soutenance par groupe : 15 min + 10 min de questions. Appuyez-la sur `rendus/tableau_synthese.csv` et sur la figure de la synthèse, avec le contrôle du point commun `D01`.

## 6. Théorie à lire

Aucune fiche n'est prévue pour cette phase (voir le tableau des fiches de l'`ENONCE.md`, section 3 bis).
