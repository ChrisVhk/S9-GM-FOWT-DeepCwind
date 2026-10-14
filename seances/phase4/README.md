<!-- destinations: github -->
# Phase 4 — Extrêmes et ancrage

Consigne autonome de la phase. Le cadre du projet (objectifs, évaluation, règles) est dans [`../../ENONCE.md`](../../ENONCE.md) ; [séance précédente](../phase3/README.md) · [phase suivante](../phase5/README.md).

## 1. Objectif

Extrêmes (ULS) et ancrage. Volume indicatif : 12 h. Rendu : **R4**.

**Pourquoi** : une ligne d'ancrage se dimensionne sur son extrême ; le bureau d'études doit savoir quel cas la sollicite le plus et si une méthode quasi-statique, bien moins chère, suffit pour le dire.

**À la main d'abord** : avant de lancer les cas ULS, estimez avec votre `raideur_horizontale` (à la main sur un cas, ou après l'étape 1) le déport que produit la poussée du rotor et la tension de chaumard qui en résulte ; vous la confronterez à l'étape 3.

## 2. Avant de commencer

**Premier geste, depuis n'importe quel dossier : `s9gm doctor`** (il vérifie votre poste et donne la commande exacte pour chaque point à corriger ; si `s9gm` est introuvable, activez l'environnement : `micromamba activate s9gm-fowt`). Un terminal ne vous est pas familier : [`annexes/TERMINAL.md`](../../annexes/TERMINAL.md), une page.

Prérequis : l'environnement installé en [séance 0a](../0a/README.md) (`openfast -v` → `OpenFAST-v5.0.0`, contrôleur compilé).

**À lire avant la séance : F7 (Caténaire statique)** — dès qu'elle est publiée.

**Où vit ce que vous produisez** : sous `results/` et `rendus/` (ignorés par git) ; `cas/`, `modeles/` et `seances/` se lisent et se lancent sans être modifiés.

## 3. À faire, étape par étape

Les étapes de cette phase suivent ce que l'ENONCE exige (§3, §3 bis) ; la numérotation « point n » est celle de la consigne de la phase. Les commandes se lancent **depuis la racine du dépôt**, environnement `s9gm-fowt` activé. **Chaque bloc est autonome** (il importe ce dont il a besoin) et lit des fichiers écrits par les blocs précédents, dans `results/`.
Les valeurs entre `<…>` sont **vos choix** ou ceux de l'enseignant : la consigne ne les donne pas, et chacune se justifie dans votre rendu. Vous partez de **vos lignes extrêmes** de la phase 1 (`results/extremes_phase1.csv`, DLC 6.1 et 1.6) et de votre LCT (`results/lct_phase1_cas.csv`).

### Étape 1 — Votre copie du squelette `s9gm.ancrage`, et les tests qui doivent passer

`s9gm/ancrage.py` est un **squelette** : `poids_immerge`, `lire_moordyn`, `systeme_lignes` et `courbe_deport` sont écrits ; deux fonctions sont à programmer par vous : `catenaire_elastique` (effort au chaumard d'une caténaire élastique) et `raideur_horizontale`
(le bloc « Théorie » du module donne le modèle, le domaine de validité et ce qu'il ne permet pas de conclure). Le fichier du dépôt ne se modifie pas : vous travaillez sur **une copie sous `results/`**.

```bash
s9gm copie ancrage
```

`s9gm copie` crée `results/mon_s9gm/ancrage.py` dans votre clone — **sans jamais écraser** une copie existante —, affiche son chemin complet et le nombre de trous. Elle marche **depuis n'importe quel dossier**. Programmez les deux fonctions dans cette copie (éditeur de votre choix), puis lancez les tests du dépôt, d'abord sur le squelette du dépôt, ensuite sur **votre copie** :

```bash
s9gm tester ancrage --squelette
```

```bash
s9gm tester ancrage
```

**Vous devez voir** : avec `--squelette`, des tests `xfailed` (attendus en échec : `NotImplementedError`) et des `passed` (les parties déjà écrites) ; sans option, sur votre copie : **tant que vos fonctions ne sont pas programmées, des `failed` qui nomment la fonction à programmer** ; **une fois les deux programmées, `passed` pour tous les tests de `test_ancrage.py`, aucun `failed`, aucun `xfailed`**.

| Symptôme | Cause | Geste |
|---|---|---|
| `failed` encore présents dans « votre copie » | un trou reste, ou une fonction est fausse (le test nomme la grandeur) | `s9gm copie ancrage` affiche le nombre de trous restants ; `grep -n NotImplementedError results/mon_s9gm/ancrage.py` les liste |
| `s9gm : commande introuvable` | l'environnement n'est pas activé, ou le paquet n'est pas installé | `micromamba activate s9gm-fowt`, puis `s9gm doctor` (il donne la commande exacte) |
| j'ai corrigé ma fonction mais **rien ne change** | en Python, `ancrage = ma_copie("ancrage")` a été exécuté avant la correction : la variable garde l'ancienne version | relancez la ligne `ma_copie("ancrage")` : elle relit le fichier à chaque appel (inutile de redémarrer Python). `s9gm tester ancrage` relit toujours le fichier |
| `s9gm copie ancrage` dit que la copie existe déjà | normal : votre travail n'est jamais écrasé | pour repartir d'un squelette vierge, déplacez `results/mon_s9gm/ancrage.py` ailleurs (ne le supprimez pas), puis relancez `s9gm copie ancrage` |
| le test de fermeture échoue | branche posée / suspendue mal distinguée | relisez le bloc Théorie (deux branches) ; vérifiez `L_fond` |
| les deux raideurs ne concordent pas | pas de la différence finie trop grand ou jacobienne fausse | réduisez `pas` ; recalculez la jacobienne à la main sur un cas |

### Étape 2 — Écrire et lancer les cas ULS : DLC 6.1 et 1.6, référence et variante (point 1)

Pour **chaque ligne extrême** de votre phase 1, deux cas : la **référence** (modèle du dépôt tel quel) et la **variante la plus pénalisante de votre groupe** (celle que vos résultats de la phase 2 désignent : une colonne de votre famille de paramètres à une valeur que **vous** choisissez).
**Comparer des extrêmes issus de durées de simulation différentes est le piège du point de contrôle** : tous les cas de ce bloc ont la même durée, et vous écartez le même transitoire à l'étape 3.

Ce que l'outillage permet, et ce qu'il ne fait pas pour vous :
- **DLC 1.6** (état de mer sévère, rotor en fonctionnement) : comme en phase 3, avec le gabarit TurbSim (vent de turbulence normale, `NTM`) à la vitesse `U_hub` de la ligne, et son état de mer ;
- **DLC 6.1** (vent extrême, rotor à l'arrêt, état de mer extrême). **Le gabarit est un vent `NTM`** ; pour un vent extrême, la colonne `turbsim.IEC_WindType` prend `<x>EWM50` (ou `<x>EWM1`), où `x` est **la classe de la machine** (1, 2 ou 3 : votre choix, à justifier avec celui de la phase 1).
  Deux conséquences constatées en préparant cette consigne (à refaire : lisez le `.sum` produit et le message de TurbSim) : (i) **la colonne `turbsim.URef` n'a alors plus d'effet** : la vitesse moyenne vient de la classe `x` (lisez-la dans `results/phase4/<cas>/Wind/<cas>.sum`) ; (ii) **`IECturbc` doit être une lettre** (`A`, `B` ou `C`) : TurbSim refuse un pourcentage avec un vent extrême. Le rotor à l'arrêt se **modélise** ainsi : `elastodyn.GenDOF` à `False`,
  `elastodyn.RotSpeed` à 0, `elastodyn.BlPitch(1)`, `(2)`, `(3)` au calage de drapeau, et une **copie du fichier ServoDyn sous `results/`** où les trois `TPitManS` valent 0 (manœuvre de pas vers `BlPitchF` dès le début) ; la colonne `fst.ServoFile` pointe la copie. Ce n'est **ni un frein ni un arrêt d'urgence modélisés** : c'est une approximation à dire dans votre rendu.
  **L'azimut du rotor arrêté** (`elastodyn.Azimuth`) et le **désalignement** vent-houle sont des choix ; la houle reste à 0° (limite du modèle, phase 1).
- **Le choix de la période de retour** (DLC 6.1), des **classes de vent** (DLC 1.6), la **hauteur de référence de `Uw`** et la justification du DLC 6.2 sont **les vôtres** : ils sont déjà faits dans `results/extremes_phase1.csv`. Ce bloc ne les décide pas ; il les lit.

```python
import re
from pathlib import Path

import pandas as pd
from s9gm import cas, lancer
from s9gm.chemins import MODELES, RESULTS, SEANCES

# 1. copie locale du fichier ServoDyn : les trois manœuvres de pas démarrent à t = 0 ; chemins corrigés (le fichier vit désormais sous results/)
SRV = MODELES / "oc4_rtest" / "5MW_OC4Semi_WSt_WavesWN" / "NRELOffshrBsline5MW_OC4DeepCwindSemi_ServoDyn.dat"
txt = SRV.read_text(encoding="utf-8")
txt = re.sub(r"^(\s*)\S+(\s+TPitManS\(\d\))", r"\g<1>0\2", txt, flags=re.M)
txt = txt.replace('"../5MW_Baseline/', '"../modeles/oc4_rtest/5MW_Baseline/')
(RESULTS / "ServoDyn_arret.dat").write_text(txt, encoding="utf-8")

# 2. une ligne de LCT par cas ULS
ext = pd.read_csv(RESULTS / "extremes_phase1.csv")                     # vos lignes DLC 6.1 (cas X61) et DLC 1.6 (cas X16_…)
phase1 = pd.read_csv(RESULTS / "lct_phase1_cas.csv").iloc[0]
arret = (ext["DLC"].astype(str) == "6.1").to_list()                  # DLC 6.1 : vent extrême, rotor à l'arrêt
lct = pd.DataFrame({"cas": ext["cas"], "fst.TMax": <votre durée>, "turbsim.URef": ext["U_hub"].round(3),
                    "turbsim.RandSeed1": <votre graine>,
                    "seastate.WaveMod": 2, "seastate.WaveHs": ext["Hs"].round(3), "seastate.WaveTp": ext["Tp"].round(3)})
# colonnes de texte : une valeur pour les lignes 6.1, une cellule vide (= « ne rien changer ») pour les autres
lct["turbsim.IECturbc"] = ["<votre catégorie (lettre)>" if a else str(phase1["turbsim.IECturbc"]) for a in arret]
lct["turbsim.IEC_WindType"] = ["<votre classe de la machine>EWM50" if a else "" for a in arret]
for colonne, valeur in {"fst.ServoFile": "../../ServoDyn_arret.dat", "elastodyn.RotSpeed": "0", "elastodyn.GenDOF": "False",
                        "elastodyn.BlPitch(1)": "90", "elastodyn.BlPitch(2)": "90", "elastodyn.BlPitch(3)": "90"}.items():
    lct[colonne] = [valeur if a else "" for a in arret]
variante = lct.copy()
variante["cas"] = variante["cas"] + "_V"
variante["<votre colonne de variation>"] = "<votre valeur de variation>"        # la variante de votre groupe : une colonne de votre famille, une valeur
lct = pd.concat([lct, variante], ignore_index=True)
lct.to_csv(RESULTS / "lct_phase4.csv", index=False)

GABARIT = SEANCES / "0b" / "turbsim_gabarit.inp"
dossiers = cas.generer_serie(RESULTS / "lct_phase4.csv", MODELES / "flottant", RESULTS / "phase4", turbsim_inp=GABARIT)
lancer.lancer_serie(dossiers, coeurs=<votre nombre de coeurs>, journal=RESULTS / "phase4_journal.csv")
```

**Vous devez voir** : un dossier `results/phase4/<cas>` par cas (référence : `X61`, `X16_…` ; variante : mêmes noms suffixés `_V`), un `main.outb` dans chacun, `termine` dans le journal. Pour un cas DLC 6.1, ouvrez `Wind/<cas>.sum` : la vitesse moyenne y est celle de la classe, et dans la sortie le pas des pales (`BldPitch1`) est au calage de drapeau, `RotSpeed` proche de zéro.

| Symptôme | Cause | Geste |
|---|---|---|
| TurbSim : « the IEC wind type must be "NTM" » | `IECturbc` est un pourcentage avec un vent extrême | une lettre `A`, `B` ou `C` pour les lignes 6.1 |
| OpenFAST : « The input file … ServoDyn_arret.dat was not found » | chemin de `fst.ServoFile` faux | un cas vit sous `results/phase4/<cas>` : la copie est à `../../ServoDyn_arret.dat` |
| OpenFAST : « … DISCON … not found » | chemin de la bibliothèque non corrigé dans la copie | relisez la ligne `DLL_FileName` de la copie : `../modeles/oc4_rtest/5MW_Baseline/ServoData/…` |
| `KeyError : clé « BlPitch(1) » …` | colonne mal écrite | la clé s'écrit avec ses parenthèses : `elastodyn.BlPitch(1)` |
| la variante est identique à la référence | la colonne de variation n'existe pas dans les fichiers du modèle, ou vaut déjà sa valeur de référence | `print(lct.loc[:, lct.columns.str.contains("votre|seastate|turbsim|fst")])` |

### Étape 3 — Extrêmes et charge de rupture de la ligne (point 2)

Pour chaque cas : le maximum de chaque tension de chaumard, celui du moment en pied de tour, les mouvements maximaux du flotteur ; puis le rapport de la tension maximale à la **charge de rupture de la ligne** divisée par le **coefficient de sécurité que vous retenez**.
**La charge de rupture de la ligne n'est pas dans ce dépôt** : `data/geometrie_deepcwind.md` la déclare ouverte, et aucune source locale ne la donne. **Vous la justifiez avec la norme** : la charge de rupture (nature de la chaîne, diamètre, classe, formule ou tableau de la norme, avec son édition et sa page) **et** le coefficient de sécurité (norme d'ancrage, classe de conséquence), comme vous l'avez fait pour `IECturbc`. Une valeur sans source se marque « hypothèse ». Ce qui est noté est la justification et la source, pas le nombre.

```python
from pathlib import Path

import pandas as pd
from s9gm import lire
from s9gm.chemins import RESULTS

CHARGE_RUPTURE = <votre charge de rupture (N)>               # à documenter : valeur remise par l'enseignant, ou hypothèse marquée
COEF_SECURITE = <votre coefficient de sécurité>

lignes = []
for dossier in sorted((RESULTS / "phase4").glob("*")):
    df, unites = lire.lire(dossier / "main.outb")
    u = df[df["Time"] >= <votre valeur>]                     # le même transitoire écarté pour tous les cas
    ligne = {"cas": dossier.name, "duree_utile_s": float(u["Time"].iloc[-1] - u["Time"].iloc[0])}
    for k in (1, 2, 3):
        ligne[f"max_FAIRTEN{k}"] = float(u[f"FAIRTEN{k}"].max())
    ligne["max_tension"] = max(ligne[f"max_FAIRTEN{k}"] for k in (1, 2, 3))
    ligne["utilisation"] = ligne["max_tension"] * COEF_SECURITE / CHARGE_RUPTURE            # < 1 : la ligne tient avec ce coefficient
    ligne["max_TwrBsMyt_kNm"] = float(u["TwrBsMyt"].abs().max())
    for c in ("PtfmSurge", "PtfmHeave", "PtfmPitch"):
        ligne[f"max_{c}"] = float(u[c].abs().max())
    lignes.append(ligne)
uls = pd.DataFrame(lignes).set_index("cas")
uls.to_csv(RESULTS / "phase4_uls.csv")
print(uls.round(3).to_string())
```

**Vous devez voir** : un tableau avec une ligne par cas ; le rapport `utilisation` de chaque cas ; la durée utile **identique** d'un cas à l'autre. **Point de contrôle de l'ENONCE** : tension maximale **inférieure** à la charge de rupture avec le coefficient retenu ; si `utilisation ≥ 1`, dites quel cas et quelle variante. Un maximum est un maximum **de cette réalisation** :
une seule graine par cas ne donne pas un extrême de dimensionnement, dites ce que vous en concluez et ce que vous feriez de plus.

| Symptôme | Cause | Geste |
|---|---|---|
| `KeyError: 'FAIRTEN1'` | cas lancé avec MAP++ | les tensions s'appellent `T[1]`, `T[2]`, `T[3]` ; correspondance à l'étape 5 |
| durées utiles différentes | durées de simulation différentes entre cas | refaites l'étape 2 avec une seule durée |

### Étape 4 — Comparer la tension de chaumard de MoorDyn à l'approche quasi-statique (point 3, tous les groupes)

La tension quasi-statique est celle que donne la caténaire élastique de votre `ancrage.catenaire_elastique` à **chaque pas de temps**, pour la position du chaumard que donne le mouvement du flotteur : elle ne connaît ni l'inertie de la ligne, ni sa traînée, ni son amortissement. **Approximation à dire** : seules les **translations** du flotteur déplacent le chaumard
ici ; les rotations (tangage, roulis, lacet) sont négligées. Le calcul se fait pour la première ligne du fichier MoorDyn = `FAIRTEN1`, etc. (même ordre).

```python
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from openfast_toolbox.io import FASTInputFile
from s9gm import lire
from s9gm.chemins import MODELES, RESULTS

from s9gm import ma_copie
ancrage = ma_copie("ancrage")                                                # VOTRE copie (rechargée à chaque appel)

MOORDYN = MODELES / "oc4_rtest" / "5MW_OC4Semi_WSt_WavesWN" / "NRELOffshrBsline5MW_OC4DeepCwindSemi_MoorDyn.dat"
RHO = float(FASTInputFile(MODELES / "flottant" / "main.fst")["WtrDens"])           # masse volumique de l'eau (kg/m3) du modèle ; `SeaState.dat` dit « default » (voir le manuel de SeaState)
lignes_mooring = ancrage.lire_moordyn(MOORDYN, RHO)

resultat = []
for dossier in sorted((RESULTS / "phase4").glob("*")):
    df, _ = lire.lire(dossier / "main.outb")
    u = df[df["Time"] >= <votre valeur>]
    for i, li in enumerate(lignes_mooring, start=1):
        xf = li.chaumard[0] + u["PtfmSurge"].to_numpy()
        yf = li.chaumard[1] + u["PtfmSway"].to_numpy()
        zf = li.chaumard[2] + u["PtfmHeave"].to_numpy()
        d = np.hypot(li.ancre[0] - xf, li.ancre[1] - yf)       # distance horizontale chaumard - ancre
        qs = np.array([ancrage.catenaire_elastique(a, z - li.ancre[2], li.L, li.EA, li.w).tension for a, z in zip(d, zf)])
        of = u[f"FAIRTEN{i}"].to_numpy()
        resultat.append({"cas": dossier.name, "ligne": i, "moyenne_OpenFAST": of.mean(), "moyenne_quasi_statique": qs.mean(),
                         "max_OpenFAST": of.max(), "max_quasi_statique": qs.max(), "ecart_max_relatif": (qs.max() - of.max()) / of.max()})
comparaison = pd.DataFrame(resultat)
comparaison.to_csv(RESULTS / "phase4_quasi_statique.csv", index=False)
print(comparaison.round(3).to_string(index=False))
```

**Vous devez voir** : une ligne par cas et par ligne ; les **moyennes** des deux approches proches (la tension moyenne est une affaire de position moyenne), les **maximums** qui s'écartent d'autant plus que le cas est dynamique. **Dites quand l'approche quasi-statique sous-estime le maximum**
(signe de `ecart_max_relatif`), et ce que la dynamique de la ligne apporte que la caténaire n'a pas : c'est la question du groupe centre dans l'ENONCE ; **tous les groupes** la traitent ici (elle éclaire leur variante), et le **groupe centre** la prolonge à l'étape 5.

| Symptôme | Cause | Geste |
|---|---|---|
| `NotImplementedError` | un trou de votre copie n'est pas programmé | étape 1 |
| `ValueError … flotte` | masse volumique ou diamètre incohérents dans `poids_immerge` | `RHO` en kg/m³ |
| écart énorme dès la moyenne | ordre des lignes ou référentiel du chaumard | `chaumard` est relatif au centre de la plateforme au repos ; contrôlez le signe de chaque axe sur une ligne |

### Étape 5 — Groupe centre : MoorDyn contre MAP++ sur le même cas extrême (point 3)

Le groupe centre relance le **même cas extrême** avec l'ancrage quasi-statique (MAP++), toutes choses égales par ailleurs, et compare les tensions. **Correspondance des canaux, établie** : MAP++ nomme les trois tensions de chaumard `T[1]`, `T[2]`, `T[3]`, et `T[i]` correspond à `FAIRTEN` *i* de MoorDyn (`T[1]` ↔ `FAIRTEN1`, `T[2]` ↔ `FAIRTEN2`, `T[3]` ↔ `FAIRTEN3`).
La raison : le fichier MAP ne décrit qu'**une** ligne (celle du chaumard à 60°) et la répète par `repeat 240 120` ; MAP++ numérote la première répétition à +120° (cap 180°, ligne 2 de MoorDyn) et la seconde à +240° (cap 300°, ligne 3 de MoorDyn).
**Comment cela a été établi** (vous pouvez le refaire : le bloc ci-dessous le vérifie sur deux calculs de 5 s) : un flotteur décalé de 10 m en **cavalement** tend la ligne du cap 180° ; décalé de 10 m en **embardée**, il tend la ligne du cap 300° ; dans les deux calculs, la ligne la plus tendue est la même avec MAP++ et avec MoorDyn, et les tensions initiales concordent à moins d'un demi-pour-cent.

```python
import pandas as pd
from s9gm import cas, lancer, lire
from s9gm.chemins import MODELES, RESULTS

PREFIXE = "../../../modeles/oc4_rtest/5MW_OC4Semi_WSt_WavesWN/NRELOffshrBsline5MW_OC4DeepCwindSemi_"
ordre = {}
for axe, cle in (("cavalement", "elastodyn.PtfmSurge"), ("embardee", "elastodyn.PtfmSway")):
    lct = pd.DataFrame([
        {"cas": f"{axe}_MD", "fst.TMax": 5, "fst.CompInflow": 0, "fst.CompAero": 0, "seastate.WaveMod": 0, cle: 10,
         "fst.CompMooring": 3, "fst.MooringFile": PREFIXE + "MoorDyn.dat"},
        {"cas": f"{axe}_MAP", "fst.TMax": 5, "fst.CompInflow": 0, "fst.CompAero": 0, "seastate.WaveMod": 0, cle: 10,
         "fst.CompMooring": 1, "fst.MooringFile": PREFIXE + "MAP.dat"}])
    lct.to_csv(RESULTS / f"lct_phase4_{axe}.csv", index=False)
    dossiers = cas.generer_serie(RESULTS / f"lct_phase4_{axe}.csv", MODELES / "flottant", RESULTS / f"phase4_correspondance_{axe}", executer_turbsim=False)
    lancer.lancer_serie(dossiers, coeurs=2, journal=RESULTS / "phase4_correspondance_journal.csv")
    md, _ = lire.lire(RESULTS / f"phase4_correspondance_{axe}" / f"{axe}_MD" / "main.outb")
    mp, _ = lire.lire(RESULTS / f"phase4_correspondance_{axe}" / f"{axe}_MAP" / "main.outb")
    t_md = md.loc[0, ["FAIRTEN1", "FAIRTEN2", "FAIRTEN3"]].to_numpy(dtype=float)
    t_mp = mp.loc[0, ["T[1]", "T[2]", "T[3]"]].to_numpy(dtype=float)
    ordre[axe] = (int(t_md.argmax()), int(t_mp.argmax()))                  # la ligne la plus tendue (les deux autres sont symétriques : leur ordre ne discrimine pas)
    print(axe, "MoorDyn :", t_md.round(0), "MAP++ :", t_mp.round(0))
print("même ligne la plus tendue dans les deux calculs ?", {a: o[0] == o[1] for a, o in ordre.items()})
```

**Vous devez voir** : pour chaque axe, les trois tensions initiales de MoorDyn et de MAP++ (proches, à moins d'un demi-pour-cent), et `True` pour les deux axes (même ligne la plus tendue). Les cas sont sans vent ni houle : c'est une vérification d'indexation, pas un cas d'étude.

Puis, pour votre étude, **relancez votre cas extrême le plus pénalisant** avec MAP++ : dans `results/lct_phase4.csv`, recopiez la ligne du cas, nommez-la `<cas>_MAP`, et fixez `fst.CompMooring` à 1 et `fst.MooringFile` au fichier `…MAP.dat`
(chemin relatif au dossier du cas : `../../../modeles/oc4_rtest/5MW_OC4Semi_WSt_WavesWN/NRELOffshrBsline5MW_OC4DeepCwindSemi_MAP.dat`). Comparez ensuite `T[i]` à `FAIRTEN i` comme à l'étape 3 : **quand l'approche quasi-statique sous-estime-t-elle les tensions ?**

| Symptôme | Cause | Geste |
|---|---|---|
| `KeyError: 'T[1]'` | le cas n'a pas été lancé avec MAP++ | `fst.CompMooring` doit valoir 1 et le fichier être le `…MAP.dat` |
| OpenFAST : « … MAP.dat was not found » | chemin relatif au dossier du cas | un cas sous `results/<dossier>/<cas>` : `../../../modeles/…` |
| `False` à la vérification de la ligne la plus tendue | indexation différente de celle de cette consigne | ne comparez pas avant d'avoir trouvé pourquoi : ouvrez les deux fichiers de lignes |

### Étape 6 — Rainflow des tensions de chaumard

Le rainflow et le DEL des tensions `FAIRTEN1` à `FAIRTEN3` sont dans la [phase 3](../phase3/README.md) (étape 3, exposant `m` de la ligne, DEL long terme à l'étape 4) : **ils ne sont pas refaits ici**. Utilisez ce résultat pour dire si le cas extrême ou la fatigue dimensionne la ligne.

### Étape 7 — Groupes bâbord et tribord (point 4)

Pour votre famille de paramètres (vent ; mer et courant), écrivez ce qui, dans la variante de l'étape 2, **pilote l'extrême d'ancrage** : comparez, cas par cas, la tension maximale de la variante à celle de la référence (`results/phase4_uls.csv`), et rattachez l'écart à un mécanisme physique (effort de dérive moyen, mouvement lent, effort de rotor) que vous **appuyez sur une grandeur de vos sorties** (position moyenne du flotteur, spectre du cavalement, effort du rotor), pas sur une intuition.

**Temps mesurés** (rejeu des commandes dans un clone neuf, machine de développement du cours à 16 cœurs, cas de **300 s simulées** ; la salle sera plus lente, et un cas de 600 s dure environ le double) :

| Étape | Durée mesurée |
|---|---|
| Étape 2, 6 cas ULS (3 lignes extrêmes × référence et variante) : TurbSim à la suite, puis OpenFAST en parallèle | ≈ 1180 s (20 min) |
| Étape 3 (tableau ULS) | ≈ 1 s |
| Étape 4 (caténaire quasi-statique, 6 cas × 3 lignes) | ≈ 1 s |
| Étape 5, vérification MAP++ / MoorDyn (4 calculs de 5 s) | ≈ 44 s |

## 4. Post-traiter

La démarche générale, du `.outb` aux statistiques, aux figures et au DEL, est dans [`../../s9gm/POST-TRAITER.md`](../../s9gm/POST-TRAITER.md). Tensions maximales des lignes et mouvements maximaux du flotteur : étape 3 de la section 3 (`results/phase4_uls.csv`) ; comparaison à la caténaire : étape 4.

## 5. Ce qu'on rend

**Rendu R4** : tableau ULS (`results/phase4_uls.csv`) avec le choix des cas extrêmes justifié, vérification des lignes contre la charge de rupture et le coefficient de sécurité retenus, comparaison MoorDyn / caténaire quasi-statique (et MAP++ pour le groupe centre), conclusion argumentée ; votre caténaire complétée (`results/mon_s9gm/ancrage.py`) et le résultat de ses tests.

## 6. Théorie à lire

F7 (Caténaire statique), F8 (Ancrage dynamique et fatigue) : *fiche à venir (master)*.
