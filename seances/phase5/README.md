<!-- destinations: github -->
# Phase 5 — Structures tubulaires : tour et flotteur

Consigne autonome de la phase. Le cadre du projet (objectifs, évaluation, règles) est dans [`../../ENONCE.md`](../../ENONCE.md) ; [séance précédente](../phase4/README.md) · [phase suivante](../phase6/README.md).

## 1. Objectif

Structures tubulaires : section de tour, effort dans une entretoise, SCF et domaine de validité. Volume indicatif : 8 h. Rendu : **R5**.

**Travail personnel estimé** : ≈ 5 h — fin du second passage de l'atelier (point 1, ≈ 3 h : sections FLS/ULS au-delà de celle traitée en séance) + boucle de dimensionnement (point 2, ≈ 2 h) à la maison ; le lancement du second passage sur vos propres données se fait en séance.

Quatre niveaux de modèle existent pour la structure d'un flotteur. Le projet en mobilise trois.

| Niveau | Méthode | Ce qu'il donne | Qui |
|---|---|---|---|
| **A** | Modèle rigide (référence) | Fatigue et extrêmes du pied de tour et des chaumards | Tous |
| **B** | Effort de section estimé à la main : force d'écartement / de pincement des colonnes (*split / squeeze*) en houle de travers | Effort nominal dans une entretoise, puis contrainte nominale × SCF | Tous |
| **C** | Flotteur flexible modélisé en poutres (SubDyn couplé au flotteur) | Séries temporelles d'efforts intérieurs par membre, donc rainflow sur une entretoise | Groupe centre |
| **D** | Éléments finis locaux de l'assemblage | Contrainte au point chaud, SCF « vrai » | Lecture d'une étude publiée |

## 2. Avant de commencer

**Premier geste, depuis n'importe quel dossier : `s9gm doctor`** (il vérifie votre poste et donne la commande exacte pour chaque point en défaut ; si `s9gm` est introuvable, activez l'environnement : `micromamba activate s9gm-fowt`). Un terminal ne vous est pas familier : [`annexes/TERMINAL.md`](../../annexes/TERMINAL.md), une page.

Prérequis : l'environnement installé en [séance 0a](../0a/README.md) (`openfast -v` → `OpenFAST-v5.0.0`, contrôleur compilé).

**Ressource :** le [guide du classeur de l'atelier](../../annexes/atelier_tour/README.md#a-etape-3-8) (théorie derrière chaque étape du classeur ; le classeur lui-même est distribué sur Vega) ; on l'ouvre au point 1 de cette phase (second passage).

**Où vit ce que vous produisez** : sous `results/` et `rendus/` (ignorés par git) ; `cas/`, `modeles/` et `seances/` se lisent et se lancent sans être modifiés.

## 3. À faire, étape par étape


Les étapes ci-dessous suivent ce que l'ENONCE exige (§3, §3 bis, §4) ; la numérotation « point n » est celle de la consigne de la phase. Les commandes se lancent **depuis n'importe quel dossier**, environnement `s9gm-fowt` activé. **Chaque bloc est autonome** et lit des fichiers écrits par les blocs précédents ou par les phases 3 et 4, dans `results/` :
`results/phase3_parametres.json` (vos choix de la phase 3 : diamètre et épaisseur au pied, `SCF`, exposants, courbe S-N, DFF), `results/phase3/` et `results/phase4/` (vos sorties), `results/etats_phase1.csv` (vos occurrences). Les valeurs entre `<…>` sont **vos choix** ou ceux de l'enseignant : la consigne ne les donne pas, chacune se justifie dans votre rendu.
**Partage séance / maison.** En séance : l'étape 1 et le lancement du second passage de l'atelier sur vos propres données (étapes 2 et 3). À la maison : la fin de ce second passage (sections FLS/ULS au-delà de la première jauge, étape 2 ; ≈ 3 h) et la boucle de dimensionnement (étapes 4 et 5 ; ≈ 2 h).
**Ce qui est proposé aux trois groupes : les niveaux A et B et le domaine de validité des SCF. Le niveau C (groupe centre) est « sous réserve de faisabilité » et n'a pas de commande ici.**

### Étape 1 — Votre copie du squelette `s9gm.structure`, et les tests qui doivent passer

`s9gm/structure.py` est un **squelette** : `section_tubulaire`, `contrainte_flexion` et `effort_axial_entretoise` sont écrits ; cinq fonctions sont à programmer par vous : `von_mises`, `verifier_domaine_efthymiou` (qui lève `HorsDomaineError`), et les trois SCF d'Efthymiou, `scf_ty_axial_encastre`, `scf_ty_flexion_plan`, `scf_ty_flexion_hors_plan`.
Le bloc « Théorie » du module donne le modèle et ses renvois ; **les bornes et les équations se lisent dans DNV-RP-C203, annexe B** (tableau B-1 : édition et page à citer) : le module n'en contient aucune valeur. Vous travaillez sur **une copie sous `results/`**.

```bash
s9gm copie structure
```

`s9gm copie` crée `results/mon_s9gm/structure.py` dans votre clone — **sans jamais écraser** une copie existante —, affiche son chemin complet et le nombre de trous. Elle marche **depuis n'importe quel dossier**. Programmez les cinq fonctions dans cette copie (éditeur de votre choix), puis lancez les tests du dépôt, d'abord sur le squelette du dépôt, ensuite sur **votre copie** :

```bash
s9gm tester structure --squelette
```

```bash
s9gm tester structure
```

**Vous devez voir** : avec `--squelette`, des tests `xfailed` (attendus en échec : `NotImplementedError`) et des `passed` (les parties déjà écrites) ; sans option, sur votre copie : **tant que vos fonctions ne sont pas programmées, des `failed` qui nomment la fonction à programmer** ; **une fois les cinq programmées, `passed` pour tous les tests de `test_structure.py`, aucun `failed`, aucun `xfailed`**.

| Symptôme | Cause | Geste |
|---|---|---|
| `failed` dans « votre copie » sur un test de domaine | `HorsDomaineError` ne nomme pas le paramètre, sa valeur et la borne | le message doit contenir les trois |
| `failed` sur un SCF « supérieur à un » | une équation mal recopiée | relisez le tableau B-1, avec l'édition que vous citez |
| `s9gm : commande introuvable` | l'environnement n'est pas activé, ou le paquet n'est pas installé | `micromamba activate s9gm-fowt`, puis `s9gm doctor` (il donne la commande exacte) |
| j'ai corrigé ma fonction mais **rien ne change** | en Python, `structure = ma_copie("structure")` a été exécuté avant la correction : la variable garde l'ancienne version | relancez la ligne `ma_copie("structure")` : elle relit le fichier à chaque appel (inutile de redémarrer Python). `s9gm tester structure` relit toujours le fichier |
| `s9gm copie structure` dit que la copie existe déjà | normal : votre travail n'est jamais écrasé | pour repartir d'un squelette vierge, déplacez `results/mon_s9gm/structure.py` ailleurs (ne le supprimez pas), puis relancez `s9gm copie structure` |

### Étape 2 — Tour, niveau A : section, FLS, ULS, épaisseur minimale (point 1)

Ce que vous avez déjà fait en phase 3, avec **le même modèle de section** (mêmes `D`, mêmes `SCF`, même courbe S-N, mêmes `DFF` et durée de service : lus dans `results/phase3_parametres.json`), mais sur **trois hauteurs de la tour** et avec un **critère d'extrême** en plus. Le bloc :
1. déduit la masse volumique effective **de votre épaisseur de la phase 3** (`TMassDen` du pied divisée par l'aire de votre section) et en tire l'épaisseur à chaque station du fichier tour, à `D` lu dans le fichier AeroDyn de la tour ;
2. calcule le **dommage annuel de fatigue** (rainflow du moment résultant à chaque jauge, `SCF`, courbe S-N, occurrences de votre LCT) pour une **grille d'épaisseurs** ;
3. calcule la **contrainte de Von Mises maximale en extrême** (cas DLC 6.1 et 1.6 de la phase 4) pour la même grille : flexion seule aux jauges ; au **pied**, flexion, effort normal, cisaillement et torsion à partir des canaux de pied ;
4. retient, à chaque hauteur, **la plus petite épaisseur qui satisfait les deux critères** (masse minimale à diamètre imposé).

Vos choix : la **limite d'élasticité** et le **coefficient partiel** (norme citée), la grille d'épaisseurs. Les trois jauges (`TwHt1`, `TwHt5`, `TwHt9`) sont à 11,94 m, 50,74 m et 85,66 m au-dessus du niveau de la mer ([guide de l'atelier, étape 3.8](../../annexes/atelier_tour/README.md#a-etape-3-8)) : la 9 est un nœud de calcul, pas le sommet de la tour.

```python
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from openfast_toolbox.io import FASTInputFile
from s9gm import lire
from s9gm.chemins import MODELES, RESULTS

from s9gm import ma_copie
fatigue = ma_copie("fatigue")
structure = ma_copie("structure")                                                  # VOS copies complétées (phase 3, étape 1 ; étape 1 ci-dessus)

P = json.loads((RESULTS / "phase3_parametres.json").read_text(encoding="utf-8"))
MODELE = MODELES / "oc4_rtest" / "5MW_OC4Semi_WSt_WavesWN"
ed = FASTInputFile(MODELE / "NRELOffshrBsline5MW_OC4DeepCwindSemi_ElastoDyn.dat")
HT_TOUR, BASE = float(ed["TowerHt"]), float(ed["TowerBsHt"])
stations = FASTInputFile(MODELE / "NRELOffshrBsline5MW_OC4DeepCwindSemi_ElastoDyn_Tower.dat")["TowProp"]     # HtFract, TMassDen, TwFAStif, TwSSStif
aero = FASTInputFile(MODELE / "NRELOffshrBsline5MW_OC3Hywind_AeroDyn.dat")["TowProp"]                          # TwrElev, TwrDiam, …

# 1. section à chaque station : masse volumique effective déduite de VOTRE épaisseur au pied (phase 3)
z_st = BASE + stations[:, 0] * (HT_TOUR - BASE)
D_st = np.interp(z_st, aero[:, 0], aero[:, 1])
A0 = structure.section_tubulaire(P["D"], P["t_paroi"])[0]
RHO = stations[0, 1] / A0
t_st = (D_st - np.sqrt(D_st ** 2 - 4 * stations[:, 1] / (np.pi * RHO))) / 2          # A = π t (D − t)  =>  t en fonction de D et de la masse linéique
print("masse volumique effective (kg/m3) :", round(RHO, 1), "; épaisseur au pied et au sommet (m) :", t_st[0].round(4), t_st[-1].round(4))

JAUGES = {1: 11.94, 5: 50.74, 9: 85.66}                              # numéro de jauge -> hauteur au-dessus du niveau de la mer (m)
GRILLE = np.arange(<votre épaisseur minimale (m)>, <votre épaisseur maximale (m)>, <votre pas d'épaisseur (m)>)
LIMITE, GAMMA = <votre limite d'élasticité (MPa)>, <votre coefficient partiel>
courbe = fatigue.CourbeSN(**P["sn"])
etats = pd.read_csv(RESULTS / "etats_phase1.csv").set_index("cas")

# 2. fatigue : le rainflow du moment ne dépend pas de l'épaisseur ; seule l'échelle des contraintes en dépend
cycles = {}                                                          # (cas, jauge) -> (étendues de moment en N·m, comptes, durée utile)
for dossier in sorted((RESULTS / "phase3").glob("*")):
    df, unites = lire.lire(dossier / "main.outb")
    assert unites["TwHt1MLxt"] == "kN-m", unites["TwHt1MLxt"]
    u = df[df["Time"] >= P["T_TRANS"]]
    T = float(u["Time"].iloc[-1] - u["Time"].iloc[0])
    for j in JAUGES:
        m_res = np.hypot(u[f"TwHt{j}MLxt"].to_numpy(), u[f"TwHt{j}MLyt"].to_numpy()) * 1e3
        r = fatigue.rainflow(m_res)
        cycles[(dossier.name, j)] = (r["etendue"].to_numpy(), r["compte"].to_numpy(), T)

# 3. extrême : Von Mises maximal, par cas ULS
extremes = {}
for dossier in sorted((RESULTS / "phase4").glob("*")):
    df, _ = lire.lire(dossier / "main.outb")
    u = df[df["Time"] >= P["T_TRANS"]]
    extremes[dossier.name] = u

lignes = []
for j, z in JAUGES.items():
    D = float(np.interp(z, z_st, D_st))
    for t in GRILLE:
        A, I, W = structure.section_tubulaire(D, t)
        d_an = 0.0
        for (cas, jj), (ranges, comptes, T) in cycles.items():
            if jj != j:
                continue
            sigma = P["SCF"] * structure.contrainte_flexion(ranges, D, I) / 1e6              # MPa : étendues de contrainte
            d_an += fatigue.miner(sigma, comptes, courbe, t=t * 1e3, t_ref=P["T_REF"]) * etats.loc[cas, "O_h"] * 3600 / T
        verdict_fls = fatigue.dff_verif(d_an * P["SERVICE"], P["DFF"])
        vm_max = 0.0
        for cas, u in extremes.items():
            m_res = np.hypot(u[f"TwHt{j}MLxt"].to_numpy(), u[f"TwHt{j}MLyt"].to_numpy()) * 1e3
            sx = structure.contrainte_flexion(m_res, D, I) / 1e6
            tau = 0.0
            if j == 1:                                                                         # au pied : effort normal, cisaillement et torsion
                sx = sx - u["TwrBsFzt"].to_numpy() * 1e3 / A / 1e6
                v = np.hypot(u["TwrBsFxt"].to_numpy(), u["TwrBsFyt"].to_numpy()) * 1e3
                tau = 2 * v / A / 1e6 + np.abs(u["TwrBsMzt"].to_numpy()) * 1e3 * (D / 2) / (2 * I) / 1e6      # tube mince : τ max = 2V/A ; torsion : T·(D/2)/J, J = 2I
            vm_max = max(vm_max, float(np.max([structure.von_mises(a, 0.0, 0.0, b) for a, b in zip(sx, np.broadcast_to(tau, sx.shape))])))
        lignes.append({"jauge": j, "z_m": z, "D_m": round(D, 4), "t_m": round(float(t), 4), "dommage_annuel": d_an, "fls_ok": verdict_fls["ok"],
                       "vm_max_MPa": vm_max, "uls_ok": vm_max <= LIMITE / GAMMA})
res = pd.DataFrame(lignes)
res.to_csv(RESULTS / "phase5_tour_epaisseurs.csv", index=False)
ok = res[res["fls_ok"] & res["uls_ok"]].groupby("jauge")["t_m"].min()
print("épaisseur minimale qui satisfait FLS et ULS, par jauge (m) :")
print(ok.to_string() if len(ok) else "aucune épaisseur de la grille ne convient : élargissez la grille")
```

**Vous devez voir** : la masse volumique effective et les épaisseurs aux deux extrémités ; puis, par jauge, **la plus petite épaisseur de votre grille qui satisfait le critère de fatigue (`D·DFF ≤ 1`) et le critère d'extrême (Von Mises ≤ limite / coefficient partiel)**, ou le message qu'aucune ne convient.
Le tableau complet (`results/phase5_tour_epaisseurs.csv`) dit **quel critère dimensionne** à chaque hauteur : dites-le, et dites ce que l'**atelier tour** vous avait montré sur le poids de `SCF = 1` contre `SCF = 2` sur ce choix. **Point de contrôle de l'ENONCE** : le domaine de validité de chaque formule est vérifié avant usage (flexion de poutre mince : `D/t` ; `SCF` de la tour : détail soudé de la courbe S-N, pas Efthymiou).

| Symptôme | Cause | Geste |
|---|---|---|
| `KeyError: 'TwHt1MLxt'` | canal de jauge absent de la sortie | `print(list(df.columns))` ; les jauges sont dans l'`OutList` d'ElastoDyn de `modeles/flottant` |
| `AssertionError` sur l'unité | `TwHt…` n'est pas en `kN-m` | adaptez la conversion et dites-le |
| `ValueError : section invalide` | une épaisseur de la grille ≥ `D/2` | resserrez la grille |
| `NotImplementedError` | un trou n'est pas programmé | étape 1 ; phase 3, étape 1 |
| la grille n'a aucune épaisseur valable | grille trop étroite, ou critère trop sévère | élargissez ; si rien ne convient, dites pourquoi |

### Étape 3 — Tour, niveau A : test de l'hypothèse « somme des DEL » à trois hauteurs (point 1)

À chaque jauge (pied, milieu, sommet), **trois DEL, à comparer deux à deux** (guide de l'atelier, [étape 3.8, point (b)](../../annexes/atelier_tour/README.md#a-etape-3-8)) : (1) **la méthode de l'atelier** : `DEL(effort tranchant) × bras de levier + DEL(moment)`, deux DEL combinés après coup ; (2) **le calcul exact du même modèle de transport** : le signal combiné point par point, `effort tranchant(t) × bras + moment(t)`, puis **un seul** rainflow ;
(3) **le DEL du moment mesuré à la jauge** (`TwHt<N>MLyt`). L'effort tranchant et le moment sont ceux du **palier d'orientation** en tête de tour (`YawBrFxp`, `YawBrMyp`), le bras de levier est la différence entre la hauteur de la tour et celle de la jauge. **1 contre 2** isole le coût de l'hypothèse de concomitance ; **2 contre 3** isole ce que le transport statique ne capture pas (poids propre, inertie, mouvements du flotteur).
**Ne comparez pas 1 et 3 directement.** Les exposants sont ceux de **cette consigne** (reprise de la consigne d'origine de la phase) : `m = 4` pour la branche principale, `m = 3` et `m = 5` pour la sensibilité ; si l'exposant de votre courbe S-N de la phase 3 diffère, dites pourquoi vous gardez ceux-ci.

```python
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from openfast_toolbox.io import FASTInputFile
from s9gm import lire
from s9gm.chemins import MODELES, RESULTS

from s9gm import ma_copie
fatigue = ma_copie("fatigue")

P = json.loads((RESULTS / "phase3_parametres.json").read_text(encoding="utf-8"))
HT_TOUR = float(FASTInputFile(MODELES / "oc4_rtest" / "5MW_OC4Semi_WSt_WavesWN" / "NRELOffshrBsline5MW_OC4DeepCwindSemi_ElastoDyn.dat")["TowerHt"])
JAUGES = {1: 11.94, 5: 50.74, 9: 85.66}                              # numéro de jauge -> hauteur (m), guide de l'atelier, étape 3.8 (b)
etats = pd.read_csv(RESULTS / "etats_phase1.csv").set_index("cas")

lignes = []
for dossier in sorted((RESULTS / "phase3").glob("*")):
    df, unites = lire.lire(dossier / "main.outb")
    assert unites["YawBrFxp"] == "kN" and unites["YawBrMyp"] == "kN-m"
    u = df[df["Time"] >= P["T_TRANS"]]
    T = float(u["Time"].iloc[-1] - u["Time"].iloc[0])
    fx, myb = u["YawBrFxp"].to_numpy(), u["YawBrMyp"].to_numpy()

    def del_de(x, m):
        r = fatigue.rainflow(x)
        return fatigue.del_court_terme(r["etendue"], r["compte"], m, P["F_EQ"] * T)

    for j, z in JAUGES.items():
        bras = HT_TOUR - z
        mesure = u[f"TwHt{j}MLyt"].to_numpy()
        for m in (4, 3, 5):                                            # 4 : branche principale ; 3 et 5 : sensibilité
            lignes.append({"cas": dossier.name, "jauge": j, "m": m,
                           "DEL_atelier": bras * del_de(fx, m) + del_de(myb, m),            # (1) deux DEL combinés après coup
                           "DEL_exact": del_de(myb + fx * bras, m),                           # (2) un seul rainflow sur le signal combiné
                           "DEL_jauge": del_de(mesure, m)})                                   # (3) le moment mesuré à la jauge
res = pd.DataFrame(lignes)
cas = sorted(res["cas"].unique())
O = (etats.loc[cas, "O_pct"] / 100.0).to_numpy()                      # occurrences de votre LCT, somme = 1
long_terme = []
for (j, m), g in res.groupby(["jauge", "m"]):
    g = g.set_index("cas").loc[cas]
    ligne = {"jauge": j, "m": m}
    for col in ("DEL_atelier", "DEL_exact", "DEL_jauge"):
        ligne[col] = fatigue.del_long_terme(g[col].to_numpy(), O, m)
    ligne["1_contre_2"] = ligne["DEL_atelier"] / ligne["DEL_exact"] - 1          # coût de l'hypothèse de concomitance
    ligne["2_contre_3"] = ligne["DEL_exact"] / ligne["DEL_jauge"] - 1            # ce que le transport statique ne capture pas
    long_terme.append(ligne)
tab = pd.DataFrame(long_terme)
tab.to_csv(RESULTS / "phase5_somme_des_DEL.csv", index=False)
print(tab.round(3).to_string(index=False))
```

**Vous devez voir** : un tableau long terme par jauge et par exposant `m`, avec les trois DEL et les deux écarts relatifs. Commentez **le signe de chaque écart** et **comment il varie avec la hauteur** : l'hypothèse de concomitance coûte-t-elle la même chose partout ? La part « transport incomplet » est-elle plus grande en pied ou en tête ?
Le DEL du moment est exprimé en **kN·m** (pas en contrainte) : les rapports ne dépendent pas de l'épaisseur.

| Symptôme | Cause | Geste |
|---|---|---|
| `AssertionError` sur les unités | `YawBrFxp` ou `YawBrMyp` n'est pas en `kN` / `kN-m` | `print(unites)` ; adaptez le bras et dites-le |
| `1_contre_2` et `2_contre_3` énormes | signe du bras ou repère | vérifiez que le signal combiné suit la jauge (corrélation proche de 1 au sommet) avant de lire le DEL |

### Étape 4 — Boucle de dimensionnement : une itération (point 2)

Vous réinjectez dans le fichier tour d'ElastoDyn les `R`, `S`, `T` (masse linéique et raideurs de flexion, avant-arrière puis latérale) **de la tour dimensionnée**, et vous relancez **deux** cas : un cas de fatigue représentatif (celui qui dimensionnait à l'étape 2) et le cas ULS dimensionnant.
**Simplifications à dire** : (i) la tour dimensionnée est la tour d'origine dont **tout le profil d'épaisseur est multiplié par le rapport** entre l'épaisseur retenue au pied et celle de la phase 3 (vous pouvez raffiner : un profil par tronçon) ; (ii) le module d'Young effectif est celui que donne la raideur du pied d'origine pour sa section ;
(iii) **les coefficients de la déformée assumée (`TwFAM1Sh`, …) restent ceux d'origine** : **aucun outil de calcul de ces coefficients** (ni BModes, ni équivalent dans `openfast_toolbox`, dont le module `linearization` analyse un modèle déjà construit) n'est disponible dans l'environnement du cours. **Approximation à écrire explicitement**, et à estimer à l'étape suivante.

```python
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from openfast_toolbox.io import FASTInputFile
from s9gm import cas, lancer
from s9gm.chemins import MODELES, RESULTS, SEANCES

from s9gm import ma_copie
structure = ma_copie("structure")

P = json.loads((RESULTS / "phase3_parametres.json").read_text(encoding="utf-8"))
MODELE = MODELES / "oc4_rtest" / "5MW_OC4Semi_WSt_WavesWN"
TOUR = MODELE / "NRELOffshrBsline5MW_OC4DeepCwindSemi_ElastoDyn_Tower.dat"
ed = FASTInputFile(MODELE / "NRELOffshrBsline5MW_OC4DeepCwindSemi_ElastoDyn.dat")
HT_TOUR, BASE = float(ed["TowerHt"]), float(ed["TowerBsHt"])
stations = FASTInputFile(TOUR)["TowProp"]
aero = FASTInputFile(MODELE / "NRELOffshrBsline5MW_OC3Hywind_AeroDyn.dat")["TowProp"]
D_st = np.interp(BASE + stations[:, 0] * (HT_TOUR - BASE), aero[:, 0], aero[:, 1])

A0, I0, _ = structure.section_tubulaire(P["D"], P["t_paroi"])
RHO = stations[0, 1] / A0                                          # masse volumique effective (étape 2)
E_EFF = stations[0, 2] / I0                                        # module d'Young effectif : raideur du pied / inertie de votre section
t_st = (D_st - np.sqrt(D_st ** 2 - 4 * stations[:, 1] / (np.pi * RHO))) / 2
facteur = <votre épaisseur retenue au pied (m)> / P["t_paroi"]
t_new = t_st * facteur
A_new = np.array([structure.section_tubulaire(d, t)[0] for d, t in zip(D_st, t_new)])
I_new = np.array([structure.section_tubulaire(d, t)[1] for d, t in zip(D_st, t_new)])

# fichier tour dimensionné : on remplace seulement les lignes du tableau (HtFract, TMassDen, TwFAStif, TwSSStif)
lignes = Path(TOUR).read_text(encoding="utf-8").split("\n")
i0 = next(i for i, l in enumerate(lignes) if "HtFract" in l) + 2
for k in range(len(stations)):
    lignes[i0 + k] = f"{stations[k, 0]:.7E}  {RHO * A_new[k]:.7E}  {E_EFF * I_new[k]:.7E}  {E_EFF * I_new[k]:.7E}"
(RESULTS / "tour_dimensionnee.dat").write_text("\n".join(lignes), encoding="utf-8")
print("masse linéique au pied, avant / après (kg/m) :", stations[0, 1].round(1), (RHO * A_new[0]).round(1))

# deux cas : fatigue représentatif (étape 2) et ULS dimensionnant ; mêmes lignes de LCT qu'aux phases 3 et 4, tour remplacée
l3 = pd.read_csv(RESULTS / "lct_phase3.csv")
l4 = pd.read_csv(RESULTS / "lct_phase4.csv")
lct = pd.concat([l3[l3["cas"] == "<votre cas de fatigue>"], l4[l4["cas"] == "<votre cas ULS>"]], ignore_index=True)
lct["elastodyn.TwrFile"] = "../../tour_dimensionnee.dat"          # un cas vit sous results/phase5/<cas>
lct.to_csv(RESULTS / "lct_phase5.csv", index=False)
dossiers = cas.generer_serie(RESULTS / "lct_phase5.csv", MODELES / "flottant", RESULTS / "phase5", turbsim_inp=SEANCES / "0b" / "turbsim_gabarit.inp")
lancer.lancer_serie(dossiers, coeurs=2, journal=RESULTS / "phase5_journal.csv")
```

Puis la comparaison, avant / après, **sur la même fenêtre** :

```python
import json
import sys
from pathlib import Path

import pandas as pd
from s9gm import lire
from s9gm.chemins import RESULTS

from s9gm import ma_copie
fatigue = ma_copie("fatigue")

P = json.loads((RESULTS / "phase3_parametres.json").read_text(encoding="utf-8"))
lignes = []
for dossier in sorted((RESULTS / "phase5").glob("*")):
    for etat, chemin in (("avant", RESULTS / "phase3" / dossier.name), ("avant", RESULTS / "phase4" / dossier.name), ("après", dossier)):
        if not (chemin / "main.outb").is_file():
            continue
        df, _ = lire.lire(chemin / "main.outb")
        u = df[df["Time"] >= P["T_TRANS"]]
        T = float(u["Time"].iloc[-1] - u["Time"].iloc[0])
        r = fatigue.rainflow(u["TwrBsMyt"].to_numpy())
        lignes.append({"cas": dossier.name, "etat": etat, "max_TwrBsMyt": float(u["TwrBsMyt"].abs().max()),
                       "DEL_TwrBsMyt": fatigue.del_court_terme(r["etendue"], r["compte"], P["M_TOUR"], P["F_EQ"] * T),
                       "max_TTDspFA": float(u["TTDspFA"].abs().max())})
comparaison = pd.DataFrame(lignes)
comparaison.to_csv(RESULTS / "phase5_boucle.csv", index=False)
print(comparaison.round(3).to_string(index=False))
```

**Vous devez voir** : le fichier `results/tour_dimensionnee.dat`, deux cas lancés dans `results/phase5/`, et un tableau avant / après du maximum et du DEL du moment en pied de tour, et du déplacement de tête. **Commentez la variation des efforts obtenue par rapport au premier passage** (une tour plus mince est plus souple : que deviennent le moment, le déplacement, la fréquence propre ?), et dites si l'**approximation (iii)** peut l'expliquer.

| Symptôme | Cause | Geste |
|---|---|---|
| OpenFAST : « … tour_dimensionnee.dat was not found » | chemin de `elastodyn.TwrFile` faux | un cas vit sous `results/phase5/<cas>` : `../../tour_dimensionnee.dat` |
| ElastoDyn : erreur de lecture du tableau | le tableau a été mal réécrit | comparez `results/tour_dimensionnee.dat` au fichier d'origine : seules les trois dernières colonnes et la masse changent |
| `IndexError` sur `lct[...]` / lignes vides | le nom du cas ne figure pas dans `lct_phase3.csv` ou `lct_phase4.csv` | `print(l3["cas"].tolist(), l4["cas"].tolist())` |
| résultats « avant » absents | cas d'origine absent de `results/phase3` ou `results/phase4` | seul le cas lancé dans `results/phase5` a un « avant » correspondant |

### Étape 5 — Fréquence propre de la tour : effet de l'approximation, et lecture du diagramme 1P / 3P (point 2)

Pour estimer l'effet de l'approximation (iii) **sans attendre un résultat garanti**, un **quotient de Rayleigh**, en réutilisant la **même** déformée assumée `φ(x)` (celle des coefficients d'origine `TwFAM1Sh(2…6)`) mais évaluée avec la **nouvelle** distribution de raideur `EI(x)` et de masse linéique `m(x)` :
`f² ∝ [∫EI(x)·φ''(x)²dx] / [∫m(x)·φ(x)²dx + M_tête·φ(L)²]`. Le terme `M_tête·φ(L)²` (masse du rotor, du moyeu et de la nacelle en tête : `NacMass`, `HubMass` et la masse des pales, à relever ou intégrer dans les fichiers du modèle) **ne doit pas être oublié** : il domine le dénominateur pour une éolienne.
**Interprétation** : le principe de Rayleigh garantit qu'une déformée assumée différente de la vraie déformée propre **d'une même structure** surestime sa fréquence ; il **ne garantit pas** que la fréquence obtenue pour la tour redimensionnée encadre sa vraie nouvelle fréquence (deux structures différentes). C'est un **ordre de grandeur** de l'effet de l'approximation, pas une borne.

```python
import json
from pathlib import Path

import numpy as np
from openfast_toolbox.io import FASTInputFile
from s9gm.chemins import MODELES, RESULTS

P = json.loads((RESULTS / "phase3_parametres.json").read_text(encoding="utf-8"))
MODELE = MODELES / "oc4_rtest" / "5MW_OC4Semi_WSt_WavesWN"
ed = FASTInputFile(MODELE / "NRELOffshrBsline5MW_OC4DeepCwindSemi_ElastoDyn.dat")
L = float(ed["TowerHt"]) - float(ed["TowerBsHt"])
origine = FASTInputFile(MODELE / "NRELOffshrBsline5MW_OC4DeepCwindSemi_ElastoDyn_Tower.dat")
nouvelle = FASTInputFile(RESULTS / "tour_dimensionnee.dat")
c = np.array([origine[f"TwFAM1Sh({i})"] for i in range(2, 7)], dtype=float)         # déformée assumée du 1er mode avant-arrière : Σ cᵢ (x/L)^i

def rayleigh(tour, masse_tete):
    x = tour["TowProp"][:, 0]                                                       # HtFract = x/L
    m, ei = tour["TowProp"][:, 1], tour["TowProp"][:, 2]
    phi = sum(ci * x ** i for ci, i in zip(c, range(2, 7)))
    phi2 = sum(ci * i * (i - 1) * x ** (i - 2) for ci, i in zip(c, range(2, 7))) / L ** 2
    num = np.trapezoid(ei * phi2 ** 2, x * L)
    den = np.trapezoid(m * phi ** 2, x * L) + masse_tete * phi[-1] ** 2
    return float(np.sqrt(num / den) / (2 * np.pi))

M_TETE = <votre masse en tête (kg)>                                                 # nacelle + moyeu + pales, à relever dans les fichiers du modèle
f0, f1 = rayleigh(origine, M_TETE), rayleigh(nouvelle, M_TETE)
print("fréquence du 1er mode avant-arrière, tour d'origine et dimensionnée (Hz) :", round(f0, 4), round(f1, 4))
print("1P (Hz), de la vitesse minimale à la vitesse nominale :", <votre vitesse minimale (rpm)> / 60, <votre vitesse nominale (rpm)> / 60)
print("3P (Hz), de la vitesse minimale à la vitesse nominale :", 3 * <votre vitesse minimale (rpm)> / 60, 3 * <votre vitesse nominale (rpm)> / 60)
```

**Vous devez voir** : les fréquences de la tour avant et après l'itération, et les bandes `1P` et `3P` du rotor. **Placez la fréquence de la tour par rapport à ces bandes** (voir le [guide de l'atelier, section 6.7](../../annexes/atelier_tour/README.md#a-theorie-6-7), point non couvert par l'atelier : à faire ici) : tombe-t-elle dans une bande, entre deux, au-dessus ? Que change l'itération ?
Si l'écart avec la fréquence d'origine est significatif, **dites-le et discutez-en** : ce point ne demande pas de corriger l'approximation, seulement d'en estimer l'effet. *Le résultat est un ordre de grandeur sur la tour seule (sans la souplesse du flotteur), pas la fréquence du système couplé.*

| Symptôme | Cause | Geste |
|---|---|---|
| `AttributeError: … trapezoid` | version de NumPy plus ancienne | remplacez par `np.trapz` |
| fréquence très éloignée d'une valeur plausible pour la tour | masse en tête oubliée ou unités | `M_TETE` en kg ; `EI` en N·m² ; `x · L` en mètres |

### Étape 6 — Entretoise, niveau B : effort d'écartement, effort axial, contrainte nominale (point 3)

Estimez **à la main** l'**effort d'écartement** (*split / squeeze*) des colonnes pour la houle la plus pénalisante : **longueur d'onde de l'ordre de deux fois l'entraxe** des colonnes déportées (50 m, `data/geometrie_deepcwind.md`). Le bloc vous aide à **choisir l'état de mer** (celui de votre LCT ou de vos extrêmes dont la longueur d'onde approche `2 × entraxe`) ; **l'estimation de l'effort d'écartement `ΔF` est la vôtre**
(efforts d'inertie de Morison sur les colonnes, F4 ; votre classeur d'architecture de la [séance 0b](../0b/README.md) vous donne les diamètres et les coefficients). Le bloc en déduit l'**effort axial** de l'entretoise (`structure.effort_axial_entretoise`, écrit : **le partage de l'effort entre entretoises est un choix à justifier**) et la **contrainte nominale**.

```python
import sys

import numpy as np
import pandas as pd
from s9gm import hydro
from s9gm.chemins import RESULTS

from s9gm import ma_copie
structure = ma_copie("structure")

PROFONDEUR, ENTRAXE = 200.0, 50.0                                     # m : `WtrDpth` du modèle ; entraxe des colonnes déportées (data/geometrie_deepcwind.md)
etats = pd.read_csv(RESULTS / "etats_phase1.csv")
ext = pd.read_csv(RESULTS / "extremes_phase1.csv")
tous = pd.concat([etats[["cas", "Hs", "Tp"]], ext[["cas", "Hs", "Tp"]]], ignore_index=True)
tous["longueur_d_onde_m"] = [hydro.longueur_onde(tp, PROFONDEUR) for tp in tous["Tp"]]
tous["ecart_a_2_entraxes"] = (tous["longueur_d_onde_m"] - 2 * ENTRAXE).abs()
print(tous.sort_values("ecart_a_2_entraxes").head(5).round(2).to_string(index=False))

DELTA_F = <votre effort d'écartement ΔF (N)>                          # votre estimation à la main, pour la houle que vous avez retenue
PHI, PARTAGE = <votre angle φ (°)>, <votre partage>                   # angle de l'entretoise avec la direction de l'effort ; part de l'effort reprise par l'entretoise
N = structure.effort_axial_entretoise(DELTA_F, PHI, partage=PARTAGE)
A, I, W = structure.section_tubulaire(<votre diamètre d'entretoise (m)>, <votre épaisseur d'entretoise (m)>)
sigma = N / A / 1e6                                                   # contrainte nominale axiale (MPa)
print("effort axial (N) :", N, "; contrainte nominale (MPa) :", sigma, "; rapport à l'admissible :", sigma / <votre contrainte admissible (MPa)>)
```

**Vous devez voir** : les cinq états de mer dont la longueur d'onde est la plus proche de `2 × entraxe`, puis l'effort axial, la contrainte nominale et son rapport à la contrainte admissible. **Comparez à une contrainte admissible** que vous **justifiez** (norme citée), et dites ce que **vous n'avez pas pris en compte** (flexion de l'entretoise, effort de la houle sur l'entretoise elle-même, SCF : étape suivante).

| Symptôme | Cause | Geste |
|---|---|---|
| `ValueError : partage = … : doit être entre 0 et 1` | `partage` hors de [0 ; 1] | un partage entre 0 et 1, justifié |
| `ValueError : section invalide` | diamètre ou épaisseur d'entretoise (unités) | mètres tous les deux ; relisez votre classeur 0b |
| longueurs d'onde toutes très loin de `2 × entraxe` | période pic de vos états hors de la gamme | dites-le : votre LCT ne contient pas l'état résonant, et ce que cela change |

### Étape 7 — Domaine de validité du SCF : β, τ, γ, α, θ de chaque jonction (point 4)

Relevez dans le **document de définition OC4** (voir [`annexes/papers/`](../../annexes/papers/REFERENCES.md) et votre classeur d'architecture de la [séance 0b](../0b/README.md)) les **diamètres** des entretoises, des colonnes déportées et de la colonne centrale ; calculez **β = d/D** pour chaque jonction, et les autres paramètres que demande le domaine de validité
(τ, γ, α, θ : leurs définitions sont dans DNV-RP-C203, annexe B). Le bloc contrôle le domaine **avant** d'appliquer les formules, et **dit quel paramètre sort de quelle borne**.

```python
import sys
from s9gm.chemins import RESULTS

from s9gm import ma_copie
structure = ma_copie("structure")

JONCTIONS = {
    "entretoise / colonne déportée": dict(d=<votre d (m)>, D=<votre D (m)>, tau=<votre τ>, gamma=<votre γ>, alpha=<votre α>, theta_deg=<votre θ (°)>),
    "entretoise / colonne centrale": dict(d=<votre d (m)>, D=<votre D (m)>, tau=<votre τ>, gamma=<votre γ>, alpha=<votre α>, theta_deg=<votre θ (°)>),
    "entretoise / colonne de base": dict(d=<votre d (m)>, D=<votre D (m)>, tau=<votre τ>, gamma=<votre γ>, alpha=<votre α>, theta_deg=<votre θ (°)>),
}
for nom, j in JONCTIONS.items():
    beta = j["d"] / j["D"]
    try:
        structure.verifier_domaine_efthymiou(beta, j["tau"], j["gamma"], j["alpha"], j["theta_deg"])
    except structure.HorsDomaineError as e:
        print(f"{nom} : β = {beta:.3f} — HORS DOMAINE : {e}")
        continue
    scf = structure.scf_ty_axial_encastre(beta, j["tau"], j["gamma"], j["alpha"], j["theta_deg"])
    print(f"{nom} : β = {beta:.3f} — dans le domaine ; SCF axial : {scf}")
```

**Vous devez voir** : une ligne par jonction avec son `β` et soit un **message d'hors-domaine qui nomme le paramètre, sa valeur et la borne violée**, soit les SCF calculés. **Point de contrôle de l'ENONCE** : le domaine est vérifié **avant** tout usage ; piège : appliquer un SCF hors de son domaine. Les formules paramétriques d'Efthymiou sont établies pour des jonctions de jackets (**sans** colonne de grand diamètre ni entretoise élancée) :
**dites si elles s'appliquent à ces jonctions**, et, quand elles ne s'appliquent pas, **ce qu'il faut faire** (un modèle local en éléments finis, niveau D ; un SCF publié pour la géométrie réelle ; une marge) — sans rendre un SCF hors domaine.

| Symptôme | Cause | Geste |
|---|---|---|
| `NotImplementedError` | un trou n'est pas programmé | étape 1 |
| tous les SCF sont « dans le domaine » | bornes mal lues ou paramètres mal calculés | relisez la définition de chaque paramètre (annexe B) et recalculez à la main une jonction |
| un SCF inférieur à 1 | équation recopiée à l'envers | un SCF de jonction soudée est supérieur à 1 : relisez l'équation |

### Étape 8 — Niveau C (groupe centre) : flotteur flexible en poutres — **sous réserve de faisabilité**

Comparer, sur un même état de mer, l'effort dans une entretoise obtenu au niveau B et la série temporelle du modèle flexible (SubDyn couplé au flotteur), et expliquer pourquoi la répartition des efforts hydrodynamiques (potentiels ramenés en un point / Morison répartis) conditionne la validité du résultat.
**Ce niveau est sous réserve de faisabilité** : le flotteur flexible n'est pas dans le modèle du dépôt, et sa faisabilité n'est pas établie. **Aucune commande n'est donnée** ; elle sera écrite si la faisabilité est établie. Ce que vous pouvez préparer d'ici là : votre estimation de niveau B (étape 6) et la liste de ce qu'un modèle flexible en changerait.

### Étape 9 — Niveau D : assemblage, éléments finis locaux (lecture d'une étude publiée)

À partir de l'**étude publiée** sur l'assemblage colonne-entretoise d'une semi-submersible, expliquer la chaîne *efforts globaux → modèle local éléments finis → SCF au point chaud → S-N → durée de vie*, et discuter les ordres de grandeur obtenus.
L'étude est : Ø. Fredheim, *Fatigue Analysis of Column-Brace Connection in a Semi-submersible Wind Turbine*, mémoire de master, NTNU, 2012, lien permanent <https://hdl.handle.net/11250/238200>. **Elle n'est pas redistribuée dans ce dépôt** (sa licence n'est pas confirmée) : vous la lisez à son adresse. Aucune commande : c'est un travail de lecture et de discussion.

Rappel : aux niveaux A, B et C on obtient une contrainte **nominale**. Le SCF reste indispensable, et il faut savoir justifier d'où il vient.

**Temps mesurés** (rejeu des commandes dans un clone neuf, machine de développement du cours à 16 cœurs, cas de **300 s simulées** ; la salle sera plus lente, et un cas de 600 s dure environ le double) :

| Étape | Durée mesurée |
|---|---|
| Étapes 2 et 3 (section, fatigue et extrême à trois hauteurs, somme des DEL) | moins de 2 s |
| Étape 4, boucle de dimensionnement : 2 calculs OpenFAST en parallèle | ≈ 580 s (10 min) |
| Étapes 5 à 7 (Rayleigh, entretoise, domaine des SCF) | moins de 1 s |

## 4. Post-traiter

La démarche générale, du `.outb` aux statistiques, aux figures et au DEL, est dans [`../../s9gm/POST-TRAITER.md`](../../s9gm/POST-TRAITER.md). Contraintes de section, effort dans l'entretoise, DEL de tour : voir la section 3 (étapes 2 à 7), avec votre copie de `structure` et de `fatigue` sous `results/mon_s9gm/`.

## 5. Ce qu'on rend

**Rendu R5** : note de vérification de la tour (premier passage et itération, avec l'approximation de la déformée dite et son effet estimé), test de l'hypothèse « somme des DEL » à trois hauteurs, calcul d'entretoise (niveau B), tableau β et conclusion sur le SCF ; groupe centre : la comparaison B / C n'est due **que si** sa faisabilité est établie (sous réserve) ; votre copie de `structure` complétée et le résultat de ses tests.

## 6. Théorie à lire

Index de la théorie : [`fiches/README.md`](../../fiches/README.md).

[F10 — Structures tubulaires](../../fiches/F10_Structures-tubulaires.md) ; [F4 — Morison](../../fiches/F4_Morison.md).

Le guide du classeur de l'atelier donne la théorie derrière chaque étape de calcul : [`annexes/atelier_tour/README.md`](../../annexes/atelier_tour/README.md).
