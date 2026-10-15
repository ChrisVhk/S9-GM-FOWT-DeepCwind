<!-- destinations: github -->
# Phase 3 — Fatigue

Consigne autonome de la phase. Le cadre du projet (objectifs, évaluation, règles) est dans [`../../ENONCE.md`](../../ENONCE.md) ; [séance précédente](../phase2/README.md) · [phase suivante](../phase4/README.md).

## 1. Objectif

Fatigue : rainflow, S-N, Miner, DEL court et long terme. Volume indicatif : 8 h. Rendu : **R3**.

**Pourquoi** : un bureau d'études doit dire si la tour et les lignes d'ancrage tiennent leur durée de service, et quel état de mer les use le plus ; le DEL permet de comparer des cas sans refaire tout le calcul de dommage, au prix d'hypothèses qu'il faut savoir dire.

**À la main d'abord** : avant tout rainflow, écrivez l'ordre de grandeur que vous attendez pour le DEL du moment en pied de tour de votre cas le plus chargé (à partir de l'écart-type de votre signal et de `m`) ; vous le confronterez au calcul de l'étape 3.

**Travail personnel estimé** : ≈ 3 h — la fin du premier passage de l'atelier tour (étape 0 : `SCF = 2` et le comparatif avec `SCF = 1`) se termine à la maison ; le début (prise en main, `SCF = 1`) se fait en séance.

## 2. Avant de commencer

**Premier geste, depuis n'importe quel dossier : `s9gm doctor`** (il vérifie votre poste et donne la commande exacte pour chaque point en défaut ; si `s9gm` est introuvable, activez l'environnement : `micromamba activate s9gm-fowt`). Un terminal ne vous est pas familier : [`annexes/TERMINAL.md`](../../annexes/TERMINAL.md), une page.

Prérequis : l'environnement installé en [séance 0a](../0a/README.md) (`openfast -v` → `OpenFAST-v5.0.0`, contrôleur compilé).

**Ressource :** le [guide du classeur de l'atelier](../../annexes/atelier_tour/README.md#a-theorie) (théorie derrière chaque étape du classeur ; le classeur lui-même est distribué sur Vega) ; on l'ouvre à l'étape 0 de cette phase.

**À lire avant la séance : F8 (Ancrage dynamique et fatigue)** — dès qu'elle est publiée.

**Où vit ce que vous produisez** : sous `results/` et `rendus/` (ignorés par git) ; `cas/`, `modeles/` et `seances/` se lisent et se lancent sans être modifiés.

## 3. À faire, étape par étape

Les étapes de cette phase suivent ce que l'ENONCE exige (§3 bis, §4, §5) ; la numérotation « point n » est celle de la consigne de la phase, dont l'ENONCE renvoie ici. Les commandes se lancent **depuis n'importe quel dossier**, environnement `s9gm-fowt` activé. **Chaque bloc est autonome** (il importe ce dont il a besoin) et lit des fichiers écrits
par les blocs précédents, dans `results/`. Les valeurs entre `<…>` sont **vos choix** ou ceux de l'enseignant : la consigne ne les donne pas, et chacune se **justifie** dans votre note de calcul.
Les états de mer, leurs occurrences et la durée de simulation viennent de **votre LCT validée** (phase 1) : `results/lct_phase1_cas.csv` et `results/etats_phase1.csv`.

0. **Atelier tour, premier passage** : prise en main de la chaîne DEL court terme → long terme →
   courbe S-N → épaisseur, sur le classeur de l'atelier tel quel (sa propre géométrie de tour et
   ses propres données d'entrée, pas celles du projet) — d'abord avec `SCF = 1`, puis `SCF = 2`, en
   comparant épaisseurs et masse. Voir le [guide du classeur de l'atelier](../../annexes/atelier_tour/README.md#a-theorie)
   pour la théorie derrière chaque étape. C'est la **méthode** (pas la géométrie ni les résultats)
   que vous reprendrez ci-dessous, sur la tour du projet, puis en Phase 5 avec vos propres charges.
   Cette phase ne modifie rien de l'atelier : elle y renvoie.

### Étape 1 — Votre copie du squelette `s9gm.fatigue`, et les tests qui doivent passer (points 1 et 5)

`s9gm/fatigue.py` est un **squelette** : `inversions`, `CourbeSN`, `nombre_cycles`, `dff_verif` et `lire_serie` sont écrits ; quatre fonctions sont à programmer par vous : `rainflow`, `miner`, `del_court_terme`, `del_long_terme`
(l'énoncé de chacune, ses hypothèses et les renvois à la norme sont dans le bloc « Théorie » en tête du module). Le fichier du dépôt ne se modifie pas : vous travaillez sur **une copie sous `results/`**.

```bash
s9gm copie fatigue
```

`s9gm copie` crée `results/mon_s9gm/fatigue.py` dans votre clone — **sans jamais écraser** une copie existante —, affiche son chemin complet et le nombre de trous. Elle marche **depuis n'importe quel dossier**. Programmez les quatre fonctions dans cette copie (éditeur de votre choix), puis lancez les tests du dépôt, d'abord sur le squelette du dépôt, ensuite sur **votre copie** :

```bash
s9gm tester fatigue --squelette
```

```bash
s9gm tester fatigue
```

**Vous devez voir** : avec `--squelette`, des tests `xfailed` (attendus en échec : `NotImplementedError`) et des `passed` (les parties déjà écrites) ; sans option, sur votre copie : **tant que vos fonctions ne sont pas programmées, des `failed` qui nomment la fonction à programmer** ; **une fois les quatre programmées, `passed` pour tous les tests de `test_fatigue.py`, aucun `failed`, aucun `xfailed`**.

Point de contrôle de l'ENONCE : **votre DEL programmé = le DEL de l'outil** d'`openfast_toolbox` sur une sinusoïde dont le résultat est connu à l'avance (60 cycles d'étendue 100). Rechargez votre copie (`ma_copie` relit le fichier à chaque appel) :

```python
import numpy as np
from openfast_toolbox.tools.fatigue import equivalent_load
from s9gm import ma_copie

fatigue = ma_copie("fatigue")                      # votre copie, rechargée depuis le fichier
t = np.linspace(0, 600, 24001)
x = 50 * np.cos(2 * np.pi * t / 10)
try:
    r = fatigue.rainflow(x)
    print("DEL de votre copie :", fatigue.del_court_terme(r["etendue"], r["compte"], 3, 600.0), "; DEL de l'outil :", equivalent_load(t, x, m=3, Teq=1.0))
except NotImplementedError:
    print("DEL de votre copie : pas encore programmé")
```

| Symptôme | Cause | Geste |
|---|---|---|
| `failed` encore présents dans « votre copie » | un trou est resté, ou une fonction renvoie une valeur fausse (le test nomme la grandeur) | `s9gm copie fatigue` affiche le nombre de trous restants ; `grep -n NotImplementedError results/mon_s9gm/fatigue.py` les liste |
| `s9gm : commande introuvable` | l'environnement n'est pas activé, ou le paquet n'est pas installé | `micromamba activate s9gm-fowt`, puis `s9gm doctor` (il donne la commande exacte) |
| j'ai corrigé ma fonction mais **rien ne change** | en Python, `fatigue = ma_copie("fatigue")` a été exécuté avant la correction : la variable garde l'ancienne version | relancez la ligne `ma_copie("fatigue")` : elle relit le fichier à chaque appel (inutile de redémarrer Python). `s9gm tester fatigue` relit toujours le fichier |
| `s9gm copie fatigue` dit que la copie existe déjà | normal : votre travail n'est jamais écrasé | pour repartir d'un squelette vierge, déplacez `results/mon_s9gm/fatigue.py` ailleurs (ne le supprimez pas), puis relancez `s9gm copie fatigue` |
| un test `amplitude_a_la_place_de_l_etendue` échoue | vous avez passé des amplitudes | les arguments sont des **étendues** `Δσ = σmax − σmin` |
| `rainflow` : somme des comptes fausse | demi-cycles du résidu mal comptés | relisez le bloc « Théorie » : un cycle compte 1, un demi-cycle 0,5 |

### Étape 2 — Lancer les cas de votre LCT (point 1)

Votre LCT est validée : on lance maintenant ses cas. Un cas de 600 s prend environ 12 min de calcul sur la machine de développement quand il tourne presque seul (mesure de la phase 2) ; `coeurs` cas tournent en parallèle, plus lentement chacun (voir « Temps mesurés » en fin de section). **La durée** est un choix du projet (600 s par cas : phase 1, point 3) : la même pour tous les cas.

```python
import pandas as pd
from s9gm import cas, lancer
from s9gm.chemins import MODELES, RESULTS, SEANCES

lct = pd.read_csv(RESULTS / "lct_phase1_cas.csv")             # votre LCT : une ligne par état de mer et de vent
lct["fst.TMax"] = <votre durée>                            # secondes simulées, la même pour tous les cas
lct.to_csv(RESULTS / "lct_phase3.csv", index=False)

GABARIT = SEANCES / "0b" / "turbsim_gabarit.inp"
dossiers = cas.generer_serie(RESULTS / "lct_phase3.csv", MODELES / "flottant", RESULTS / "phase3", turbsim_inp=GABARIT)
lancer.lancer_serie(dossiers, coeurs=<votre nombre de coeurs>, journal=RESULTS / "phase3_journal.csv")
```

**Vous devez voir** : une ligne `termine` par cas dans le journal de `lancer`, et un fichier `results/phase3/<cas>/main.outb` par cas. Un cas déjà terminé est sauté si vous relancez le bloc.

| Symptôme | Cause | Geste |
|---|---|---|
| `ValueError` qui nomme `IECturbc` ou `RandSeed1` | colonnes absentes de votre fichier de LCT | refaites l'export de la phase 1 (étape 4) |
| `echec` dans le journal | OpenFAST s'est arrêté | lisez la fin de `results/phase3/<cas>/run.log` |
| la machine sature | trop de cas en parallèle | diminuez `coeurs` |

### Étape 3 — Du moment à la contrainte, rainflow, DEL court terme et dommage de chaque cas (points 1 à 5)

Ce bloc enchaîne, pour **chaque cas** : la lecture de `TwrBsMyt` après le transitoire ; la contrainte nominale de flexion en pied de tour, multipliée par `SCF = 2` (hypothèse d'avant-projet du projet, déjà posée à l'étape 0 de l'atelier ; à justifier comme telle) ; le rainflow ; le DEL court terme ;
le même DEL par l'outil d'`openfast_toolbox` ; le dommage de Miner ; puis le DEL court terme des tensions `FAIRTEN1` à `FAIRTEN3`. Il prépare aussi le tableau de la suite.

**Ce que vous devez avoir décidé avant de lancer** (chaque valeur est à justifier dans votre note, avec sa source) :
- **la section de la tour au pied** : le diamètre extérieur est **lu** par le bloc dans le fichier AeroDyn de la tour (`TwrDiam`, première ligne de `TowProp`, la base à `TwrElev = TowerBsHt`). **L'épaisseur est à retrouver par vous**, à partir de la masse linéique `TMassDen` du fichier tour ElastoDyn
  (`NRELOffshrBsline5MW_OC4DeepCwindSemi_ElastoDyn_Tower.dat`, première ligne) : `TMassDen = ρ·A`, avec `A` l'aire de l'anneau (`D`, `t`). **Le résultat dépend d'une masse volumique, et c'est un choix à justifier** : l'acier pur donne 7850 kg/m³, mais une tour réelle inclut peinture,
  boulonnerie et soudures, souvent représentées par une masse volumique « effective » plus élevée. Dites laquelle vous retenez et pourquoi, et vérifiez la cohérence du résultat (diamètre et épaisseur réalistes pour une éolienne 5 MW) ;
- **la courbe S-N** (point 3) : classe de détail, milieu (air ou eau de mer, avec ou sans protection cathodique), épaisseur de référence et exposant d'épaisseur, **lus dans DNV-RP-C203** (tableau et page à citer, édition à nommer). `fatigue.CourbeSN` ne connaît aucune courbe : les paramètres sont les vôtres. Une courbe à une pente se décrit en laissant `log_a2`, `m2` et `n_coude` à `None` ;
- **les exposants** `m` du DEL : celui de la tour (courbe S-N de la soudure) et celui des lignes (courbe tension-cycles), qui ne sont pas les mêmes ; **la fréquence équivalente** `f_eq`, avec laquelle le DEL se donne (`n_eq = f_eq·T`) ;
- **`t_transitoire`** et sa raison (voir [`../../s9gm/POST-TRAITER.md`](../../s9gm/POST-TRAITER.md)) : la même fenêtre pour tous les cas.

```python
import json
import sys
from pathlib import Path

import pandas as pd
from openfast_toolbox.io import FASTInputFile
from openfast_toolbox.tools.fatigue import equivalent_load
from s9gm import lire, structure
from s9gm.chemins import MODELES, RESULTS

from s9gm import ma_copie
fatigue = ma_copie("fatigue")                                           # VOTRE copie (rechargée à chaque appel)

etats = pd.read_csv(RESULTS / "etats_phase1.csv").set_index("cas")
AERO = MODELES / "oc4_rtest" / "5MW_OC4Semi_WSt_WavesWN" / "NRELOffshrBsline5MW_OC3Hywind_AeroDyn.dat"
D = float(FASTInputFile(AERO)["TowProp"][0][1])         # diamètre extérieur au pied (m), lu dans le fichier AeroDyn
t_paroi = <votre épaisseur de paroi (m)>                 # à retrouver à partir de TMassDen et de votre masse volumique
A, I, W = structure.section_tubulaire(D, t_paroi)
SCF = 2                                                  # hypothèse d'avant-projet (étape 0 de l'atelier tour)
M_TOUR, M_LIGNE, F_EQ = <votre exposant m>, <votre exposant m de la ligne>, <votre f_eq (Hz)>
T_TRANS, T_REF = <votre valeur>, <votre épaisseur de référence (mm)>
DFF, SERVICE = <votre DFF>, <votre durée de service (ans)>           # imposés en séance (voir l'étape 4)
SN = dict(log_a1=<votre log ā1>, m1=<votre pente m1>, log_a2=<votre log ā2>, m2=<votre pente m2>,
          n_coude=<votre nombre de cycles au coude>, k=<votre exposant d'épaisseur k>,
          source="<votre source S-N (norme, tableau, page)>")
courbe = fatigue.CourbeSN(**SN)
# vos choix, écrits une fois : les phases 5 et 6 les relisent au lieu de vous les faire retaper
(RESULTS / "phase3_parametres.json").write_text(json.dumps(
    {"D": D, "t_paroi": t_paroi, "SCF": SCF, "M_TOUR": M_TOUR, "M_LIGNE": M_LIGNE, "F_EQ": F_EQ,
     "T_TRANS": T_TRANS, "T_REF": T_REF, "DFF": DFF, "SERVICE": SERVICE, "sn": SN}, indent=2), encoding="utf-8")

lignes = []
for dossier in sorted((RESULTS / "phase3").glob("*")):
    df, unites = lire.lire(dossier / "main.outb")
    assert unites["TwrBsMyt"] == "kN-m", unites["TwrBsMyt"]    # le moment est en kN·m : la conversion est écrite ci-dessous
    u = df[df["Time"] >= T_TRANS]                              # transitoire écarté
    T = float(u["Time"].iloc[-1] - u["Time"].iloc[0])
    sigma = SCF * structure.contrainte_flexion(u["TwrBsMyt"].to_numpy() * 1e3, D, I) / 1e6      # MPa : ÉTENDUES de contrainte au rainflow
    r = fatigue.rainflow(sigma)
    ligne = {"cas": dossier.name, "T": T}
    ligne["DEL_tour"] = fatigue.del_court_terme(r["etendue"], r["compte"], M_TOUR, F_EQ * T)
    ligne["DEL_tour_outil"] = equivalent_load(u["Time"], sigma, m=M_TOUR, Teq=1 / F_EQ)       # l'outil d'openfast_toolbox, mêmes entrées
    ligne["D_cas"] = fatigue.miner(r["etendue"], r["compte"], courbe, t=t_paroi * 1e3, t_ref=T_REF)
    ligne["D_an"] = ligne["D_cas"] * etats.loc[dossier.name, "O_h"] * 3600 / T                # dommage annuel de ce cas : O_h heures par an
    for k in (1, 2, 3):
        f = u[f"FAIRTEN{k}"].to_numpy()                                                        # tension de chaumard (N)
        rl = fatigue.rainflow(f)
        ligne[f"DEL_FAIRTEN{k}"] = fatigue.del_court_terme(rl["etendue"], rl["compte"], M_LIGNE, F_EQ * T)
    lignes.append(ligne)

tab = pd.DataFrame(lignes).set_index("cas")
tab.to_csv(RESULTS / "phase3_del_par_cas.csv")
print(tab.round(4).to_string())
```

**Vous devez voir** : un tableau avec une ligne par cas (durée utile `T`, DEL court terme de la tour, DEL de l'outil, dommage du cas, dommage annuel, DEL des trois lignes), écrit dans `results/phase3_del_par_cas.csv`. Le DEL de l'outil est **proche** du vôtre, **pas identique** :
l'outil regroupe les étendues en classes (`bins`, 100 par défaut) et son rainflow traite le résidu autrement. **Un écart entre les deux doit être expliqué** : chiffrez-le (relatif), dites ce que vous avez fait varier pour vérifier votre explication (le nombre de classes, par exemple), et ce que vous n'avez pas pu isoler.

| Symptôme | Cause | Geste |
|---|---|---|
| `NotImplementedError` | un trou de votre copie n'est pas programmé | étape 1 |
| `AssertionError` sur l'unité | l'unité de `TwrBsMyt` n'est pas `kN-m` | `print(unites)` ; adaptez la conversion et dites-le |
| `KeyError: 'FAIRTEN1'` | canal absent de la sortie | `print(list(df.columns))` ; avec MAP++ les tensions s'appellent `T[1]`, `T[2]`, `T[3]` (voir la phase 4) |
| `ValueError : section invalide` | `t_paroi` incompatible avec `D` (unités) | `D` est en m, `t_paroi` aussi |
| DEL de l'outil très différent du vôtre (plusieurs %) | amplitudes au lieu d'étendues, ou `Teq` mal posé | `Teq = 1 / f_eq` ; vos étendues et celles de l'outil sont des étendues |
| dommage très grand ou nul | unité de l'épaisseur ou paramètres de la courbe | `t` et `t_ref` du `miner` sont en **mm** ; relisez le tableau de la norme |

### Étape 4 — DEL long terme, dommage cumulé et durée de vie (points 4 et 5)

Le DEL long terme pondère les DEL court terme par les occurrences `Oⱼ` **de votre LCT** (somme égale à un, point de contrôle de la phase 1) ; le dommage annuel cumulé somme les dommages annuels de chaque cas.

```python
import json
import sys
from pathlib import Path

import pandas as pd
from s9gm.chemins import RESULTS

from s9gm import ma_copie
fatigue = ma_copie("fatigue")

tab = pd.read_csv(RESULTS / "phase3_del_par_cas.csv").set_index("cas")
etats = pd.read_csv(RESULTS / "etats_phase1.csv").set_index("cas")
O = (etats.loc[tab.index, "O_pct"] / 100.0).to_numpy()           # occurrences Oⱼ de votre LCT, somme = 1

P = json.loads((RESULTS / "phase3_parametres.json").read_text(encoding="utf-8"))          # vos choix de l'étape 3
del_tour_lt = fatigue.del_long_terme(tab["DEL_tour"].to_numpy(), O, P["M_TOUR"])
del_lignes_lt = [fatigue.del_long_terme(tab[f"DEL_FAIRTEN{k}"].to_numpy(), O, P["M_LIGNE"]) for k in (1, 2, 3)]
print("DEL long terme, tour (MPa) :", del_tour_lt)
print("DEL long terme, lignes 1 à 3 (N) :", del_lignes_lt)

D_an = float(tab["D_an"].sum())                                  # dommage cumulé par an, tous les cas
print("dommage annuel :", D_an, "; durée de vie estimée sans DFF (ans) :", 1.0 / D_an)
verdict = fatigue.dff_verif(D_an * P["SERVICE"], P["DFF"])
print(verdict)
pd.DataFrame({"grandeur": ["DEL_long_terme_tour", "dommage_annuel", "dommage_x_DFF", "marge", "ok"],
              "valeur": [del_tour_lt, D_an, verdict["dommage_x_dff"], verdict["marge"], verdict["ok"]]}).to_csv(RESULTS / "phase3_bilan.csv", index=False)
```

**Vous devez voir** : le DEL long terme de la tour et des trois lignes, le dommage annuel, la durée de vie estimée **sans** coefficient de sécurité, puis le verdict `D · DFF ≤ 1` sur votre durée de service. **Le DFF et la durée de service sont des paramètres que vous justifiez avec la norme** (DNV-RP-C203 renvoie à la norme de structure pour le DFF : citez l'édition, le tableau et la page, et dites quelles conséquences d'une rupture et quelle inspectabilité vous avez retenues) ; l'ENONCE ne les fixe pas, et la consigne n'en donne aucun. Comme pour `IECturbc`, ce qui est noté est la justification et la source, pas le nombre. Un verdict `ok = True` ne dit pas que la tour tient en fatigue : relisez
« ce que le modèle ne permet pas de conclure » dans le bloc Théorie de `miner`.

| Symptôme | Cause | Geste |
|---|---|---|
| `ValueError` sur la somme des occurrences | des cas manquent dans `results/phase3/` ou dans `etats_phase1.csv` | `print(len(tab), len(etats))` ; relancez l'étape 2 pour les cas manquants |
| durée de vie très grande ou très courte | dommage annuel : `O_h` ou `T` mal posés | `O_h` est en heures par an, `T` en secondes : le facteur est `O_h·3600/T` |
| `KeyError` sur un cas | un cas de `results/phase3/` n'est pas dans `etats_phase1.csv` | `ls results/phase3` contre `etats.index` |

### Étape 5 — Vérification à la main de la chaîne, au format du classeur de l'atelier (point 5)

Le classeur de l'atelier (onglet `Long term DEL`) calcule le DEL long terme `(Σⱼ Oⱼ·DELⱼ^m)^(1/m)` : **mêmes entrées, mêmes résultats** que votre chaîne Python, à une tolérance que vous nommez. Ce bloc écrit les entrées au format de l'onglet ; **vous les collez à la main** dans votre copie du classeur
(`Oⱼ` à la place de la colonne « Occurrence », le DEL de la tour dans la colonne du moment `My`, les lignes inutilisées à zéro, l'exposant du classeur égal à celui de votre chaîne) et vous comparez la cellule du DEL long terme au résultat de l'étape 4.

```python
import pandas as pd
from s9gm.chemins import RESULTS

tab = pd.read_csv(RESULTS / "phase3_del_par_cas.csv").set_index("cas")
etats = pd.read_csv(RESULTS / "etats_phase1.csv").set_index("cas")
export = pd.DataFrame({"milieu_de_classe_U": etats.loc[tab.index, "U_table"].to_numpy(),
                       "Oj": (etats.loc[tab.index, "O_pct"] / 100.0).to_numpy(),
                       "My": tab["DEL_tour"].to_numpy()}, index=tab.index)
export.to_csv(RESULTS / "phase3_export_long_terme.csv")
print(export.round(4).to_string())
```

**Vous devez voir** : un tableau `milieu_de_classe_U`, `Oj`, `My`, une ligne par cas, écrit dans `results/phase3_export_long_terme.csv`. Après collage, la cellule du DEL long terme du classeur **concorde** avec le vôtre ; **écrivez l'écart relatif et la tolérance que vous jugez acceptable (et pourquoi)** : les deux calculs partent des mêmes nombres, ce qui reste est de l'arrondi et du format.
Si l'écart dépasse votre tolérance, la cause est dans la mise en correspondance (exposant, occurrences non normalisées, unité), pas dans la physique : cherchez-la avant de conclure. *Cette vérification se fait dans le tableur ; elle n'est pas rejouée par un test du dépôt.*

### Étape 6 — Limites du DEL, sur un de vos cas (point 6)

Choisissez **un** de vos cas (celui que vous jugez le plus parlant) et montrez trois limites. Ce bloc calcule les trois comparaisons ; **leur interprétation est votre travail**.

```python
import json
import sys
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfiltfilt
from s9gm import lire, structure
from s9gm.chemins import RESULTS

from s9gm import ma_copie
fatigue = ma_copie("fatigue")

P = json.loads((RESULTS / "phase3_parametres.json").read_text(encoding="utf-8"))      # vos choix de l'étape 3
CAS = "<votre cas>"                                          # un nom de dossier de results/phase3
df, unites = lire.lire(RESULTS / "phase3" / CAS / "main.outb")
u = df[df["Time"] >= P["T_TRANS"]]
T = float(u["Time"].iloc[-1] - u["Time"].iloc[0])
dt = float(np.median(np.diff(u["Time"])))

def del_de(x):
    r = fatigue.rainflow(x)
    return fatigue.del_court_terme(r["etendue"], r["compte"], P["M_TOUR"], P["F_EQ"] * T)

# (a) concomitance : le DEL du moment résultant n'est pas la combinaison des DEL de ses composantes
mx, my = u["TwrBsMxt"].to_numpy(), u["TwrBsMyt"].to_numpy()
print("DEL(Mx), DEL(My), DEL(résultante) :", del_de(mx), del_de(my), del_de(np.hypot(mx, my)))
print("somme DEL(Mx)+DEL(My), racine de la somme des carrés :", del_de(mx) + del_de(my), np.hypot(del_de(mx), del_de(my)))

# (b) monopente : le DEL redonne le dommage d'une courbe à UNE pente ; la courbe réelle en a deux
A, I, W = structure.section_tubulaire(P["D"], P["t_paroi"])
sigma = P["SCF"] * structure.contrainte_flexion(my * 1e3, P["D"], I) / 1e6
r = fatigue.rainflow(sigma)
deux_pentes = fatigue.CourbeSN(**P["sn"])
une_pente = fatigue.CourbeSN(log_a1=P["sn"]["log_a1"], m1=P["sn"]["m1"], k=P["sn"]["k"], source="première branche seule")
for nom, c in (("deux pentes", deux_pentes), ("première branche prolongée", une_pente)):
    print("dommage,", nom, ":", fatigue.miner(r["etendue"], r["compte"], c, t=P["t_paroi"] * 1e3, t_ref=P["T_REF"]))

# (c) dépendance à la fréquence : le DEL de deux bandes de fréquence du même signal
fc = <votre fréquence de coupure (Hz)>                        # entre le contenu de houle et la fréquence propre de la tour (voir votre spectre, phase 2)
bas = sosfiltfilt(butter(4, fc, btype="low", fs=1 / dt, output="sos"), my)
haut = sosfiltfilt(butter(4, fc, btype="high", fs=1 / dt, output="sos"), my)
print("DEL du signal, basses fréquences, hautes fréquences :", del_de(my), del_de(bas), del_de(haut))
```

**Vous devez voir** : (a) le DEL de la résultante **différent** de la somme et de la racine de la somme des carrés des DEL de ses composantes : dites ce que cela dit de l'hypothèse « somme des DEL » (guide de l'atelier : [étape 3.4](../../annexes/atelier_tour/README.md#a-etape-3-4) et [étape 3.8, point (b)](../../annexes/atelier_tour/README.md#a-etape-3-8)) ;
(b) deux dommages **différents** : dites dans quel cas l'écart serait nul et ce que la deuxième pente change aux faibles étendues ; (c) trois DEL : dites quelle bande domine le dommage, et ce que cela implique si la fréquence propre de la tour change (phase 5). Aucune des trois comparaisons ne conclut seule : chacune est **une** réalisation de **un** cas.

| Symptôme | Cause | Geste |
|---|---|---|
| `KeyError: 'TwrBsMxt'` | canal absent | `print(list(df.columns))` |
| `ValueError` du filtre (`Wn`) | `fc` hors de `]0 ; f_Nyquist[` avec `f_Nyquist = 1/(2·dt)` | choisissez `fc` dans ce domaine |

### Point 7 — Confrontation à un DEL de référence

Le DEL long terme de votre LCT de 10 à 15 cas (étape 4) est confronté à un **DEL de référence**, **calculé par l'enseignant sur les classes de la feuille `DLC12`** du classeur FLOATECH (`data/metocean/`, Papi, Perignon et Bianchini, *J. Phys. Conf. Ser.* 2385 (2022) 012117, § 2.3.2), avec le même modèle, les mêmes canaux et les mêmes `m` et `N_ref` que votre chaîne. **Ce DEL est communiqué en séance** : elle n'est pas dans ce dépôt, et ce dépôt n'en donne aucune commande.
L'écart mesure ce que vos choix de **binning** et de **lumping** (phase 1) font perdre : expliquez-le (classes écartées, valeur représentative de chaque classe, état de mer qui domine le dommage), et dites ce qu'il faudrait changer dans votre LCT pour le réduire.
Ce que vous pouvez préparer avant la séance : votre DEL long terme, la liste de vos choix de binning et de lumping, et ce que vous attendez de l'écart (signe, ordre de grandeur).

## 4. Post-traiter

La démarche générale, du `.outb` aux statistiques, aux figures et au DEL, est dans [`../../s9gm/POST-TRAITER.md`](../../s9gm/POST-TRAITER.md). Rainflow, contrainte, dommage de Miner, DEL court et long terme : étapes 3 à 6 de la section 3, avec votre copie de `fatigue` sous `results/mon_s9gm/` (le squelette de `s9gm/fatigue.py` reste intact).

## 5. Ce qu'on rend

**Rendu R3** : comparatif SCF = 1 / SCF = 2 de l'atelier tour (étape 0) ; note de calcul fatigue (hypothèses et leurs sources : masse volumique, épaisseur, courbe S-N avec tableau et page, exposants, `f_eq`, DFF ; dommages par cas, dommage annuel, durée de vie) ; comparaison DEL maison / outil avec l'écart expliqué ; vérification dans le classeur de l'atelier avec la tolérance nommée ; les trois limites du DEL sur un cas ; votre copie de `fatigue` complétée (`results/mon_s9gm/fatigue.py`) et le résultat de ses tests.

## 6. Théorie à lire

Index de la théorie : [`fiches/README.md`](../../fiches/README.md).

F8 (Ancrage dynamique et fatigue) : *fiche à venir (master)*.

Le guide du classeur de l'atelier donne la théorie derrière chaque étape de calcul : [`annexes/atelier_tour/README.md`](../../annexes/atelier_tour/README.md).
