<!-- destinations: github -->
# Phase 2 — Simulations de référence et sensibilité

Consigne autonome de la phase. Le cadre du projet (objectifs, évaluation, règles) est dans [`../../ENONCE.md`](../../ENONCE.md) ; [séance précédente](../phase1/README.md) · [phase suivante](../phase3/README.md).

## 1. Objectif

Simulations de référence, lâchers, étude de sensibilité par groupe. Volume indicatif : 5 h. Rendu : **R2**.

## 2. Avant de commencer

**Premier geste, depuis n'importe quel dossier : `s9gm doctor`** (il vérifie votre poste et donne la commande exacte pour chaque point en défaut ; si `s9gm` est introuvable, activez l'environnement : `micromamba activate s9gm-fowt`). Un terminal ne vous est pas familier : [`annexes/TERMINAL.md`](../../annexes/TERMINAL.md), une page.

Prérequis : l'environnement installé en [séance 0a](../0a/README.md) (`openfast -v` → `OpenFAST-v5.0.0`, contrôleur compilé).

**À lire avant la séance : F5 (Hydrodynamique potentielle), F6 (Aérodynamique et amortissement négatif)** — dès qu'elles sont publiées.

**Où vit ce que vous produisez** : sous `results/` et `rendus/` (ignorés par git) ; `cas/`, `modeles/` et `seances/` se lisent et se lancent sans être modifiés.

## 3. À faire, étape par étape

Les quatre points de l'ENONCE :

1. **Référence commune** (modèle flottant OC4 : [`modeles/flottant/`](../../modeles/flottant/README.md) ; cas de référence **`D01`**, le même pour les trois groupes : c'est le point commun que la synthèse de la phase 6 retrouvera chez chacun ; votre sensibilité, elle, part de la LCT de votre groupe) : lancer, vérifier l'équilibre (tension statique des lignes, position moyenne du flotteur).
2. **Lâchers (free decay)** en surge, heave, pitch : mesurer les périodes propres. Les comparer aux valeurs publiées ([`data/periodes_lacher_reference.md`](../../data/periodes_lacher_reference.md)) et **dire où se situent ces périodes par rapport aux périodes de houle de votre scatter diagram**.
3. **Sensibilité** : lancer la LCT de votre groupe en ne faisant varier **que** votre famille de paramètres, tout le reste fixé à la référence.
4. Pour chaque cas : statistiques (moyenne, écart-type, max, min) aux points imposés, et spectres de réponse.

Les points de calcul imposés (ENONCE, §3) : `TwrBsMyt` (pied de tour), `FAIRTEN1` à `FAIRTEN3` (chaumards), `PtfmSurge`, `PtfmHeave`, `PtfmPitch` (mouvements du flotteur).
Les commandes se lancent **depuis la racine du dépôt**, environnement `s9gm-fowt` activé. **Chaque bloc est autonome** (il importe ce dont il a besoin) et lit des fichiers
écrits par les blocs précédents, dans `results/`. Les valeurs entre `<…>` sont **vos choix** ou ceux de l'enseignant : la consigne ne les donne pas. **Une seule famille de paramètres
varie à la fois** (point de contrôle de l'ENONCE : conclure sur une seule seed est le piège de la phase).

### Étape 1 — Le cas de référence commun (point 1)

```python
import subprocess
from s9gm import lire
from s9gm.chemins import CAS, RESULTS

REF = "D01"                                                 # le cas de référence commun aux trois groupes
subprocess.run(["bash", CAS / "run_cas.sh", REF], check=True)  # copie le cas sous results/ et le lance (300 s simulées)

df, unites = lire.lire(RESULTS / REF / "main.outb")
df.plot(x="Time", y="PtfmSurge")                           # regardez la courbe AVANT de choisir le transitoire
print(df.loc[df["Time"] == 0, ["FAIRTEN1", "FAIRTEN2", "FAIRTEN3"]])    # tensions des lignes à t = 0 : flotteur non déplacé, lignes à l'équilibre statique
print(lire.statistiques(df, ["PtfmSurge", "PtfmHeave", "PtfmPitch", "FAIRTEN1", "FAIRTEN2", "FAIRTEN3"], t_transitoire=<votre valeur>))
```

**Vous devez voir** : `OK en NN s -> …/results/<cas>/main.outb`, les trois tensions de lignes à t = 0 (le flotteur n'a pas encore bougé : c'est la tension statique de chaque ligne),
puis, après transitoire, la position moyenne du flotteur (surge, heave, pitch) et les tensions moyennes. **Vérifier l'équilibre**, c'est dire si la position moyenne est stable (la courbe ne dérive plus) et
si les tensions statiques des trois lignes sont cohérentes entre elles et avec ce que le cas applique (vent, houle) ; le cas de référence ne se modifie pas (il est dans `cas/`).
Temps de calcul : voir « Temps mesurés ».

| Symptôme | Cause | Geste |
|---|---|---|
| `Cas inconnu : …` | `REF` ne désigne pas un cas de `cas/` | `ls cas/` ; le cas de référence commun est `D01` |
| `ERREUR : le controleur DISCON n'est pas compile` | étape 2 de `INSTALLATION.md` oubliée | `bash scripts/build_discon.sh` |
| `KeyError: 'FAIRTEN1'` | canal absent | `print(list(df.columns))` |

### Étape 2 — Lâchers : les périodes propres (point 2)

```python
import numpy as np
import pandas as pd
from scipy.signal import find_peaks
from s9gm import cas, lancer, lire
from s9gm.chemins import MODELES, RESULTS

DUREE = <votre durée de lâcher (s)>              # assez longue pour plusieurs périodes de chaque mode (le surge est le plus lent)
lach = pd.DataFrame({
    "cas": ["LAC_surge", "LAC_heave", "LAC_pitch"], "fst.TMax": DUREE,
    "fst.CompInflow": 0, "fst.CompAero": 0, "seastate.WaveMod": 0,                       # ni vent, ni aérodynamique, ni houle
    "elastodyn.PtfmSurge": [<votre déplacement de surge (m)>, 0, 0],
    "elastodyn.PtfmHeave": [0, <votre déplacement de heave (m)>, 0],
    "elastodyn.PtfmPitch": [0, 0, <votre rotation de pitch (°)>]})
lach.to_csv(RESULTS / "lct_lachers.csv", index=False)
dossiers = cas.generer_serie(RESULTS / "lct_lachers.csv", MODELES / "flottant", RESULTS / "phase2_lachers")
lancer.lancer_serie(dossiers, coeurs=3, journal=RESULTS / "phase2_lachers_journal.csv")

for nom, canal in (("surge", "PtfmSurge"), ("heave", "PtfmHeave"), ("pitch", "PtfmPitch")):
    df, _ = lire.lire(RESULTS / "phase2_lachers" / f"LAC_{nom}" / "main.outb")
    t, y = df["Time"].to_numpy(), df[canal].to_numpy()
    pics, _ = find_peaks(y)
    print(nom, ":", len(pics), "pics ;", "période moyenne entre pics (s) :", float(np.diff(t[pics]).mean()) if len(pics) > 1 else "pas assez de pics")

et = pd.read_csv(RESULTS / "etats_phase1.csv")      # les états de mer de votre LCT (phase 1)
print("périodes de pic Tp de votre LCT : de", et["Tp"].min(), "à", et["Tp"].max(), "s")
```

**Vous devez voir** : trois dossiers de lâcher, pour chacun le nombre de pics de la réponse et la période moyenne entre pics, puis l'étendue des `Tp` de votre scatter diagram. Pour chaque mode,
**dites si la période propre tombe dans cette étendue ou à côté, et ce que cela implique** (une période propre dans la gamme de la houle excite le flotteur ; la comparaison au scatter, pas
la valeur seule, est ce qui compte). **Comparez aux périodes propres publiées** (valeurs de référence données dans [`data/periodes_lacher_reference.md`](../../data/periodes_lacher_reference.md), valeurs mesurées de Coulling et al. 2013, source et page citées) ; vous pouvez aussi confronter à `s9gm.hydro` (séance 0b). Un écart se **chiffre et s'attribue**, il ne se constate pas.

| Symptôme | Cause | Geste |
|---|---|---|
| `pas assez de pics` | durée trop courte ou mode trop amorti pour un déplacement initial trop petit | allongez `DUREE`, ou augmentez le déplacement initial ; le surge demande le plus de temps |
| période incohérente d'un pic à l'autre | le premier pic est le déplacement initial, ou bruit | regardez la courbe ; gardez les pics de la décroissance libre |
| `KeyError : clé « … » trouvée 0 fois` | colonne `elastodyn.…` mal écrite | `elastodyn.PtfmSurge`, `.PtfmHeave`, `.PtfmPitch` |

### Étape 3 — Sensibilité : une famille de paramètres, tout le reste fixé (point 3)

L'ENONCE donne **une famille de paramètres par groupe**, pas un paramètre : le choix du paramètre **dans votre famille** est le vôtre, et la consigne n'en privilégie aucun. Chaque
paramètre se fait varier par **une colonne de la LCT** :

| Groupe | Famille (ENONCE) | Paramètre | Colonne de la LCT |
|---|---|---|---|
| **Bâbord** | Vent | vitesse moyenne (classes de 4 à 24 m/s) | `turbsim.URef` |
| | | intensité de turbulence | `turbsim.IECturbc` (le trou de la phase 1 : justification et source à refaire pour chaque valeur) |
| | | nombre de seeds | `turbsim.RandSeed1` : une ligne par graine |
| **Tribord** | Mer et courant | Hs ; Tp ; facteur de pic γ du JONSWAP | `seastate.WaveHs` ; `seastate.WaveTp` ; `seastate.WavePkShp` |
| | | direction de houle | `seastate.WaveDir` — **limite du modèle : 0° seulement** (voir la phase 1) ; ne la faites pas varier. Le désalignement vent-houle est une **question de discussion** pour votre rendu, pas une variation |
| | | courant | `seastate.CurrMod` (1 pour l'activer), `seastate.CurrDIV` et `seastate.CurrDIDir` (courant uniforme sur la profondeur : vitesse, direction), ou les colonnes `CurrSS…`, `CurrNS…` du fichier `SeaState` |
| **Centre** | Modélisation hydrodynamique et ancrage | ancrage dynamique (MoorDyn) vs quasi-statique (MAP++) | `fst.CompMooring` (3 : MoorDyn ; 1 : MAP++) **avec** `fst.MooringFile` (le fichier correspondant de `modeles/oc4_rtest/5MW_OC4Semi_WSt_WavesWN/`, chemin relatif au dossier du cas : `../../../modeles/…`) |
| | | théorie potentielle (WAMIT) vs Morison seul vs hybride | `fst.HydroFile` : un fichier HydroDyn **que vous copiez sous `results/`** et dont vous changez les options (voir ci-dessous) |

```python
import pandas as pd
from s9gm import cas, lancer
from s9gm.chemins import MODELES, RESULTS, SEANCES

GABARIT = SEANCES / "0b" / "turbsim_gabarit.inp"
lct = pd.read_csv(RESULTS / "lct_phase1_cas.csv")           # la LCT de votre groupe (phase 1)
base = lct.iloc[[<indice du cas de base>]]                 # le cas de base : tout le reste est fixé à la référence
variations = <vos variations>                              # {colonne de LCT : [valeurs]} : des listes de même longueur, au moins deux valeurs
n = len(next(iter(variations.values())))
sens = pd.concat([base.assign(cas=f"S{j:02d}") for j in range(n)], ignore_index=True)
for colonne, valeurs in variations.items():
    sens[colonne] = valeurs
sens["fst.TMax"] = <votre durée de simulation (s)>        # 300 s en séance, 600 s hors séance (étape 5)
sens.to_csv(RESULTS / "lct_sensibilite.csv", index=False)
dossiers = cas.generer_serie(RESULTS / "lct_sensibilite.csv", MODELES / "flottant", RESULTS / "phase2", turbsim_inp=GABARIT)
lancer.lancer_serie(dossiers, coeurs=<vos coeurs>, journal=RESULTS / "phase2_journal.csv")
```

**Vous devez voir** : autant de dossiers `results/phase2/S00`, `S01`, … que de valeurs, chacun avec son `main.outb`, `termine` dans le journal. **Seule la famille de votre groupe varie** : relisez
`results/lct_sensibilite.csv` : les colonnes que vous n'avez pas citées dans `variations` sont **identiques** d'une ligne à l'autre. Un seul cas par valeur ne dit rien de la variabilité entre
réalisations : pour toute autre famille que le nombre de graines, gardez la **même graine** d'une ligne à l'autre (ce qui est comparé, c'est l'effet du paramètre, pas du tirage).

**Famille Centre, théorie potentielle vs Morison.** Le fichier HydroDyn du modèle (`HydroFile` de `modeles/flottant/main.fst`) ne se modifie pas : **copiez-le sous `results/`** (`results/hydrodyn_perso.dat`),
**corrigez dans la copie les chemins relatifs** (`PotFile`, qui pointe vers les données WAMIT : il doit désormais viser `../modeles/oc4_rtest/5MW_Baseline/HydroData/marin_semi`), changez dans la copie les options que
votre groupe étudie (potentiel : `PotFile`, `PropPot` des membres ; Morison : `Cd` et `Ca` des membres), puis pointez la copie par la colonne `fst.HydroFile` (chemin relatif au dossier du cas : `../../hydrodyn_perso.dat`).
Le mécanisme (copie locale, chemins corrigés, colonne `fst.HydroFile`) est éprouvé ; **quelles options changer et quelles valeurs de coefficients prendre est la question de votre groupe**.

| Symptôme | Cause | Geste |
|---|---|---|
| OpenFAST : « The input file, … was not found » (HydroDyn ou ancrage) | chemin relatif de la colonne faux | un cas vit sous `results/phase2/<cas>` : la racine du dépôt est à `../../../`, `results/` à `../../` |
| `KeyError : clé « … » trouvée 0 fois` | colonne mal écrite, ou clé absente du fichier concerné | la clé fautive est nommée ; `seastate.…` pour `SeaState`, `fst.…` pour `main.fst` |
| `ValueError` sur les longueurs | listes de `variations` de longueurs différentes | une valeur par cas, pour chaque colonne |
| `ValueError … trou` (gabarit) | `IECturbc` ou `RandSeed1` vide dans la LCT de la phase 1 | refaites la phase 1, étape 4 |
| calcul beaucoup plus long | trop de cas en parallèle | `coeurs=` plus petit ; `lancer` saute les cas terminés |

### Étape 4 — Comparer : statistiques, figures, spectres (points 3 et 4)

```python
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch
from s9gm import lire, visu
from s9gm.chemins import RESULTS

CANAUX = ["TwrBsMyt", "FAIRTEN1", "FAIRTEN2", "FAIRTEN3", "PtfmSurge", "PtfmHeave", "PtfmPitch"]
stats, series = {}, {}
for d in [RESULTS / "D01", *sorted((RESULTS / "phase2").glob("S*"))]:      # D01 : le point commun aux trois groupes
    df, _ = lire.lire(d / "main.outb")
    series[d.name] = df
    presents = [c for c in CANAUX if c in df.columns]        # avec MAP++, les tensions s'appellent T[1], T[2], T[3] (voir ci-dessous)
    stats[d.name] = lire.statistiques(df, presents, t_transitoire=<votre valeur>)
    print(d.name); print(stats[d.name].round(3).to_string())

for canal in ("TwrBsMyt", "PtfmPitch"):
    fig = visu.tracer_statistiques(stats, canal, modele="flottant", etat="rejoué le JJ/MM", titre=f"{canal} : effet du paramètre")
    fig.savefig(RESULTS / f"phase2_{canal}.png", dpi=150, facecolor="white")

dernier = sorted(series)[-1]
fig = visu.tracer_series(series[dernier], ["TwrBsMyt", "PtfmPitch"], cas=dernier, modele="flottant",
                         etat="rejoué le JJ/MM", t_transitoire=<votre valeur>)
fig.savefig(RESULTS / "phase2_series.png", dpi=150, facecolor="white")

plt.figure()
for nom, df in series.items():
    y = df.loc[df["Time"] >= <votre valeur>, "PtfmPitch"].to_numpy(dtype=float)
    dt = float(np.median(np.diff(df["Time"])))
    f, P = welch(y - y.mean(), fs=1 / dt, nperseg=min(len(y), 512))
    plt.semilogy(f, P, label=nom)
plt.xlabel("f (Hz)"); plt.ylabel("densité spectrale"); plt.legend()
plt.savefig(RESULTS / "phase2_spectres.png", dpi=150)
```

**Vous devez voir** : un tableau de statistiques par cas (moyenne, écart-type, min, max), deux figures de comparaison (une barre par cas : moyenne, ± écart-type, min–max), une figure de séries temporelles avec le
transitoire teinté, un graphique de spectres de la réponse en tangage (un trait par cas). **Pour chaque tendance observée** (R2) : **théorie attendue → ce que montrent les chiffres → ce qu'ils ne
permettent pas de conclure** (une seule seed ? durée trop courte ? autre paramètre couplé ?). Un pic de spectre se compare aux périodes propres de l'étape 2 et aux `Tp` de votre LCT.
**MAP++** : les tensions de chaumard s'appellent `T[1]`, `T[2]`, `T[3]` (pas `FAIRTEN…`) ; **la correspondance de `T[2]` et `T[3]` avec les lignes 2 et 3 de MoorDyn est à établir** avant de comparer
(le fichier MAP ne décrit qu'une ligne, répétée à `repeat 240 120`).

| Symptôme | Cause | Geste |
|---|---|---|
| `lire.statistiques` refuse de tourner | `t_transitoire` absent | regardez la courbe, choisissez, écrivez la raison |
| `visu` : `ValueError : provenance incomplète` | `cas`, `modele` ou `etat` vide | les trois sont obligatoires |
| `KeyError` sur un canal dans `tracer_statistiques` | canal absent d'un des cas (MAP++ : pas de `FAIRTEN…`) | n'y comparez que les canaux présents partout |
| `results/phase2` vide | l'étape 3 n'a pas tourné | relancez l'étape 3 |

### Étape 5 — 300 s ou 600 s ? (la durée est un résultat)

```python
import numpy as np
import pandas as pd
from s9gm import cas, lancer, lire
from s9gm.chemins import MODELES, RESULTS, SEANCES

lct = pd.read_csv(RESULTS / "lct_phase1_cas.csv")
base = lct.iloc[[<indice du cas de base>]]
deux = pd.concat([base.assign(cas="T300"), base.assign(cas="T600")], ignore_index=True)
deux["fst.TMax"] = [300, 600]                                   # 300 s en séance ; 600 s pour la maison ou la salle C09
deux.to_csv(RESULTS / "lct_300_600.csv", index=False)
dossiers = cas.generer_serie(RESULTS / "lct_300_600.csv", MODELES / "flottant", RESULTS / "phase2_300_600",
                             turbsim_inp=SEANCES / "0b" / "turbsim_gabarit.inp")
lancer.lancer_serie(dossiers, coeurs=2, journal=RESULTS / "phase2_300_600_journal.csv")

a, _ = lire.lire(RESULTS / "phase2_300_600" / "T300" / "main.outb")
b, _ = lire.lire(RESULTS / "phase2_300_600" / "T600" / "main.outb")
canaux = ["TwrBsMyt", "FAIRTEN1", "PtfmSurge", "PtfmHeave", "PtfmPitch"]
n = len(a)
print("écart maximal sur les 300 premières secondes :", {c: float(np.abs(a[c].to_numpy() - b[c].to_numpy()[:n]).max()) for c in canaux})
s300 = lire.statistiques(a, canaux, t_transitoire=<votre valeur>)
s600 = lire.statistiques(b, canaux, t_transitoire=<votre valeur>)
print((s600 - s300)[["moyenne", "ecart_type", "max"]])          # ce que 300 s de plus changent
```

**Vous devez voir** : deux cas (même graine, même état de mer, même champ de vent) ; la première ligne imprimée montre que **les 300 premières secondes du calcul de 600 s sont les mêmes que le calcul de 300 s** (écart
maximal nul aux arrondis près) ; la seconde, ce que changent 300 s de plus sur la moyenne, l'écart-type et le maximum de chaque canal. **Question d'analyse** : ces écarts sont-ils **dans le bruit, ou significatifs** ?
Comparez-les à l'écart-type du canal, et à l'effet du paramètre de votre étape 3. **Qu'est-ce que cela vous dit sur la durée à retenir pour un rendu qui compte ?** (Le maximum d'un canal croît-il avec la durée ?
une seule graine suffit-elle ?) Il n'y a pas de valeur attendue : la réponse est la vôtre, avec ses chiffres et ses limites.

| Symptôme | Cause | Geste |
|---|---|---|
| `ValueError` : champ de vent trop court pour 600 s | gabarit TurbSim modifié (durée utile réduite) | ne modifiez pas le gabarit : sa durée utile est de 600 s |
| `TMax` de `SeaState` inférieur à 600 s | `seastate.WaveTMax` abaissé | laissez la valeur du modèle (600 s) |
| les deux cas ne démarrent pas ensemble | `coeurs=1` | `coeurs=2` pour les lancer en parallèle |

**Temps mesurés** (machine de développement du cours ; la salle sera plus lente) :

| Calcul | Durée mesurée |
|---|---|
| Étape 1 : cas de référence D01, 300 s simulées | ≈ 305 s (rejeu en clone neuf) |
| Étape 2 : trois lâchers de 60 s simulées, en parallèle | ≈ 95 s |
| Étape 5 : cas turbulent flottant, 300 s simulées (deux cas en parallèle) | 384 s |
| Étape 5 : le même cas, 600 s simulées (en parallèle du précédent) | 709 s (rapport 0,85) |
| Champ de vent TurbSim (deux champs identiques) | ≈ 140 s |
| Rejeu complet de la phase 2 (valeurs d'essai courtes pour les lâchers et la sensibilité) | 1553 s |

Les calculs à 300 s et à 600 s ont été mesurés ensemble : seul, un cas va un peu plus vite.

## 4. Post-traiter

La démarche générale, du `.outb` aux statistiques, aux figures et au DEL, est dans [`../../s9gm/POST-TRAITER.md`](../../s9gm/POST-TRAITER.md). Statistiques (moyenne, écart-type, max, min) aux points imposés et spectres de réponse pour chaque cas, périodes propres des lâchers : voir les points 2 et 4 de la section 3.

## 5. Ce qu'on rend

**Rendu R2** : tableau des résultats, figures commentées. Pour chaque tendance observée : *théorie attendue → ce que montrent les chiffres → ce qu'ils ne permettent pas de conclure* (une seule seed ? durée trop courte ? autre paramètre couplé ?).

## 6. Théorie à lire

F5 (Hydrodynamique potentielle), F6 (Aérodynamique et amortissement négatif) : *fiche à venir (master)*.
