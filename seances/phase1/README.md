<!-- destinations: github -->
# Phase 1 — Du site à la Load Case Table

Consigne autonome de la phase. Le cadre du projet (objectifs, évaluation, règles) est dans [`../../ENONCE.md`](../../ENONCE.md) ; [séance précédente](../0b/README.md) · [phase suivante](../phase2/README.md).

## 1. Objectif

Du site à la Load Case Table : scatter diagram, DLC, binning / lumping. Volume indicatif : 3 h. Rendu : **R1**.

Vous partez d'un site réel (la table des états de mer et de vent observés) et vous arrivez à **une liste de cas à simuler**, chacun avec
son occurrence : la LCT. Le travail d'ingénieur est dans les choix (quelles classes garder, quelle valeur représentative, quels DLC), et
dans ce que vous savez dire de ce que ces choix font perdre. **Point de contrôle** (ENONCE, §3 bis) : la LCT est **validée par
l'enseignant avant tout lancement**, et la **somme des occurrences = 100 %**.

## 2. Avant de commencer

Prérequis : l'environnement installé en [séance 0a](../0a/README.md) (`openfast -v` → `OpenFAST-v5.0.0`, contrôleur compilé),
et la séance [0b](../0b/README.md) (gabarit TurbSim à trous, lecture d'un cas).

**Données fournies** (dossier `data/metocean/` du dépôt) : un site réel au large de l'île de Barra (Écosse), à partir des conditions publiées
en accès ouvert par le projet européen FLOATECH (Papi et al., université de Florence, réanalyse ERA5, licence CC-BY 4.0) : distribution
conjointe vent / Hs / Tp / désalignement vent-houle (fichier lu par `s9gm.metocean`), et les états de mer normaux, sévères et extrêmes du site
(classeur `floatech_wob_metocean_ERA5.xlsx`, feuilles `NSS`, `SSS`, `ESS`, `DLC12`). **Ne reconstruisez pas la table** : elle n'est pas
régénérable ici.

**À consulter, non fournies** : pour le **courant** et les **niveaux d'eau**, consultez le livrable public D1.1 du projet LIFES50+
(« Oceanographic and meteorological conditions for the design », Iberdrola Ingeniería y Construcción, projet 640741, 03/10/2015, accessible par
CORDIS) : il n'est **pas redistribué** avec ce dépôt, **ses données ne sont pas fournies**, et aucune commande ci-dessous n'en dépend. Citer ces sources
dans vos rendus.

**Où vit ce que vous produisez** : sous `results/` et `rendus/` (ignorés par git) ; `cas/`, `modeles/` et `seances/` se lisent et se lancent sans être modifiés.

## 3. À faire, étape par étape

Les quatre points de l'ENONCE :

1. Lire le scatter diagram : quelles cellules sont les plus probables ? Lesquelles portent le plus d'énergie de houle ?
2. Choisir les DLC du projet et justifier par composant :
   - **FLS** : DLC 1.2 (production normale) ; discuter le DLC 7.2 (parking, faible amortissement aérodynamique) ;
   - **ULS** : DLC 6.1 (parking, vent extrême, ESS) et DLC 1.6 (production, SSS) ; justifier si le DLC 6.2 peut être écarté à ce stade.
3. **Construire la LCT de votre groupe** (10 à 15 cas maximum, 600 s simulées chacun) : binning, lumping, occurrence Oⱼ de chaque ligne. Le budget de calcul est une contrainte réelle : une simulation de 600 s prend environ 25 min sur une machine de la salle.
4. **Vérifier la représentativité** : comparer, paramètre par paramètre, les occurrences de votre LCT à celles du site. Dire où vous avez accepté d'être moins précis, et pourquoi c'est acceptable (loin des périodes propres ? faible occurrence ?).

**À la main d'abord.** Avant chaque étape de calcul, écrivez ce que vous attendez (forme du tableau, classe de vent la plus probable,
ordre des classes d'énergie) : le calcul vient le confirmer ou le contredire. Les commandes se lancent **depuis la racine du dépôt**,
environnement `s9gm-fowt` activé, dans une session Python ou un carnet, **dans l'ordre** : chaque étape réutilise les variables de la précédente.
Les valeurs entre `<…>` sont **vos choix** : la consigne ne les donne pas, vous les décidez et vous les justifiez dans votre rendu.

### Étape 1 — Charger les données FLOATECH

```python
from pathlib import Path
from s9gm import metocean

for dossier in ("results", "rendus"):               # dossiers de ce que vous produisez : ignorés par git, donc absents d'un clone neuf
    Path(dossier).mkdir(exist_ok=True)

t = metocean.lire()
print(t.P.shape, t.P.sum())                       # forme du tableau, somme des probabilités
print(t.meta["site"], "— vent à", t.meta["hauteur_vent_m"], "m")
for axe in metocean.AXES:                         # bornes des classes de chaque axe : début, première borne, fin
    print(axe, t.bords[axe][[0, 1, -1]])
```

**Vous devez voir** : une forme à quatre axes (vent, Hs, Tp, désalignement), une somme égale à 1, le nom du site et la hauteur de vent de la table.
`lire` **échoue** si la somme n'est pas 1 à `TOLERANCE_SOMME` près : un fichier abîmé n'est jamais renormalisé en silence.

| Symptôme | Cause | Geste |
|---|---|---|
| `ModuleNotFoundError: No module named 's9gm'` | Python lancé hors de la racine du dépôt | `cd` à la racine, ou `sys.path.insert(0, ".")` |
| `ValueError … Σ P = …` | `floatech_wob_pdf_array.bin` modifié ou tronqué | `git restore data/metocean/` ; ne modifiez jamais `data/` |
| `FileNotFoundError : results/…` (plus loin) | le dossier `results/` n'existe pas : git l'ignore, un clone neuf ne l'a pas | les deux premières lignes de l'étape 1 le créent ; relancez-les |

### Étape 2 — La distribution conjointe (point 1)

```python
import numpy as np
import matplotlib.pyplot as plt

for axe in metocean.AXES:
    print(metocean.marginales(t, axe).round(4).to_string())      # probabilité de chaque classe d'un axe, les trois autres sommés

PUH = t.P.sum(axis=(2, 3))                                       # probabilité jointe (vent, Hs)
energie = PUH * t.milieux("Hs")[None, :] ** 2                    # P · Hs² : proportionnelle à l'énergie de houle de la cellule
for nom, grille in (("les plus probables", PUH), ("les plus énergétiques", energie)):
    for k in np.argsort(grille.ravel())[::-1][:5]:
        i, j = divmod(int(k), grille.shape[1])
        print(nom, ": U =", t.milieux("U")[i], "m/s, Hs =", t.milieux("Hs")[j], "m")

fig, axes = plt.subplots(1, 4, figsize=(14, 3))
for ax, axe in zip(axes, metocean.AXES):
    m = metocean.marginales(t, axe)
    ax.bar(m.index, m.to_numpy(), width=0.8 * (m.index[1] - m.index[0]))
    ax.set_xlabel(axe)
fig.savefig("results/phase1_marginales.png", dpi=150)
```

**Vous devez voir** : quatre marginales dont chacune somme à 1 ; deux listes de cinq cellules (vent, Hs) ; un fichier `results/phase1_marginales.png`.
**Comparez les deux listes** : les cellules les plus probables sont-elles celles qui portent l'énergie de houle ? Qu'est-ce que cela change pour le choix des cas
(fiche F2, énergie de la houle linéaire) ? Une marginale ne suffit pas : le produit des marginales n'est pas le tableau (le vent fort s'accompagne de houle forte).

| Symptôme | Cause | Geste |
|---|---|---|
| `KeyError` sur un axe | nom d'axe inconnu | les axes sont `metocean.AXES` : `U`, `Hs`, `Tp`, `mis` |
| figure vide ou illisible | `width` de barre non adaptée à l'axe | adaptez la largeur à la largeur de classe de l'axe |

### Étape 3 — Choisir les classes (points 3 et 4)

```python
k = <votre k (diviseur de 18)>                  # fusion de k classes de vent consécutives (binning) ; k doit diviser 18
m = <votre exposant m>                          # exposant du lumping « dommage » (m = 1 redonne la moyenne)
seuil = <votre seuil de probabilité>            # on écarte les classes de vent moins probables que ce seuil

tb = metocean.binning(t, "U", k)
etats = metocean.lumper(tb, methode="<votre méthode de lumping>", axe_classes="U", m=m)
print(len(etats), "classes de vent représentées")
etats = etats[etats["P"] >= seuil].copy()
print("part du temps écartée :", 1.0 - etats["P"].sum())
etats["P"] = etats["P"] / etats["P"].sum()      # renormalisation EXPLICITE : à dire dans votre justification
etats = etats.reset_index(drop=True)
print(len(etats), "cas de fatigue")

rep = metocean.representativite(t, etats)
print(rep["energie"])
for axe in metocean.AXES:
    print(rep["marginales"][axe].round(4).to_string())
```

`lumper` donne **une valeur représentative de Hs par classe de vent** selon `methode` (`moyenne`, `maximum` ou `dommage`) ; `dommage` exige `m`.
**Vous devez voir** : le nombre de classes, la part du temps écartée par votre seuil, le nombre de cas retenus (**10 à 15**, ENONCE), l'énergie de houle du site et de votre
LCT avec l'écart relatif, puis, par paramètre, la marginale du site à côté de celle de votre LCT. **Un seuil écarte du temps** : `occurrences` refuse une somme
différente de 100 % ; c'est pourquoi la renormalisation est écrite, et à justifier (piège classique de l'ENONCE : oublier les états de mer peu probables mais proches
des périodes propres du flotteur). Dites où votre LCT est moins précise et pourquoi c'est acceptable (point 4).

| Symptôme | Cause | Geste |
|---|---|---|
| `ValueError : k = … ne divise pas le nombre de classes` | `k` n'est pas un diviseur de 18 | choisissez parmi 1, 2, 3, 6, 9, 18 |
| `ValueError : lumping « dommage » : exposant m > 0 obligatoire` | `m` absent ou nul | donnez `m` (même avec `moyenne`, il est ignoré) |
| plus de 15 cas, ou moins de 10 | seuil trop bas ou trop haut, `k` trop petit ou trop grand | ajustez `k` et le seuil, puis relancez l'étape ; écrivez ce que chaque choix coûte |
| écart d'énergie de houle important | règle de lumping qui déforme Hs | comparez `moyenne`, `dommage`, `maximum` : l'ordre attendu est dans le bloc Théorie de `lumper` |

### Étape 4 — La LCT : fatigue (DLC 1.2) et cas extrêmes (DLC 6.1 et 1.6) (points 2 et 3)

```python
import pandas as pd

Z_HUB = 90                                       # m : hauteur du moyeu (HubHt du gabarit TurbSim, RefHt de modeles/flottant)
LOI = dict(loi="<votre loi>", exposant=<votre exposant de vent>)   # ou dict(loi="logarithmique", z0=<votre z0>)
chemin_lct, chemin_etats = metocean.exporter_lct(
    etats, "results/lct_phase1.csv", "results/etats_phase1.csv",
    z_table=t.meta["hauteur_vent_m"], z_hub=Z_HUB, tmax=600,
    graine0=<votre graine>, iecturbc="<votre catégorie ou intensité>", **LOI)
print(pd.read_csv(chemin_etats)[["cas", "U_table", "U_hub", "Hs", "Tp", "mis", "O_h", "O_pct"]].round(3).to_string())

FLOATECH = "data/metocean/floatech_wob_metocean_ERA5.xlsx"
ess = pd.read_excel(FLOATECH, sheet_name="ESS", index_col=0)    # états de mer extrêmes : une ligne par période de retour
sss = pd.read_excel(FLOATECH, sheet_name="SSS", index_col=0)    # états de mer sévères : une ligne par classe de vent
print(ess.to_string())
r61 = ess.loc["<votre période de retour>"]                       # DLC 6.1 : la ligne de la feuille ESS que vous retenez
r16 = sss[sss["U100"].isin(<vos classes de vent>)]               # DLC 1.6 : les classes de vent que vous retenez
extremes = pd.concat([
    pd.DataFrame({"cas": ["X61"], "DLC": ["6.1"], "U_table": [r61["Uw"]], "Hs": [r61["Hs"]], "Tp": [r61["Tp mean"]]}),
    pd.DataFrame({"cas": [f"X16_{int(u)}" for u in r16["U100"]], "DLC": "1.6", "U_table": r16["U100"].to_numpy(),
                  "Hs": r16["Hs"].to_numpy(), "Tp": r16["Tp"].to_numpy()})], ignore_index=True)
extremes["U_hub"] = metocean.hauteur_vent(extremes["U_table"], t.meta["hauteur_vent_m"], Z_HUB, **LOI)
extremes.to_csv("results/extremes_phase1.csv", index=False)
print(extremes.round(3).to_string())

with pd.ExcelWriter("rendus/R1_LCT.xlsx") as xl:                  # le tableur du rendu R1
    pd.read_csv(chemin_etats).to_excel(xl, sheet_name="LCT fatigue", index=False)
    extremes.to_excel(xl, sheet_name="Extremes", index=False)
```

**Vous devez voir** : la LCT de fatigue (une ligne par cas : vent à la table et au moyeu, Hs, Tp, désalignement, occurrence en heures par an et en %), dont **la somme des
occurrences fait 100 %** ; les feuilles `ESS` et `SSS` ; la liste des lignes extrêmes avec leur vent au moyeu ; un classeur `rendus/R1_LCT.xlsx`. Le vent du tableau est à **100 m** et le
moyeu à **90 m** : la loi de conversion et son paramètre sont **un choix de modélisation à justifier** (`hauteur_vent` n'a aucune valeur par défaut).

**Les trous à justifier, dont la catégorie de turbulence.** `IECturbc` (catégorie IEC de turbulence, ou intensité en %) et la graine ne sont **pas imposés** : vous les choisissez et
vous les **justifiez**. Pour `IECturbc`, la justification porte sur **trois éléments** : l'**intensité de turbulence de référence** (Iref) que le projet OC3 a retenue pour les champs de vent de cette
machine (Jonkman et Musial 2010, NREL/TP-5000-48191, §2.4.1), la **classe de conception de la machine** (citez la source), et la **catégorie IEC** qui en découle dans la norme
IEC 61400-1 (édition 3). **Ce qui est noté, c'est la justification et la source citée (document, page), pas la lettre.**

**Les cas extrêmes sont des lignes de la LCT à valider, pas des cas lancés en phase 1.** Les feuilles `ESS` (une ligne par période de retour) et `SSS` (une ligne par classe de vent) donnent les états de
mer ; le choix de la **période de retour** pour le DLC 6.1, des **classes de vent** pour le DLC 1.6, et la justification du DLC 6.2 sont **les vôtres** (point 2). La feuille `ESS` ne précise pas la
hauteur de référence de `Uw` : citez la source (article FLOATECH) et justifiez. Le gabarit TurbSim est un vent de turbulence normale (`IEC_WindType = "NTM"`) : un vent extrême et un rotor à l'arrêt
(DLC 6.1) se modélisent en phase 4, pas ici.

| Symptôme | Cause | Geste |
|---|---|---|
| `ValueError : loi « puissance » : exposant obligatoire` | loi donnée sans paramètre | `exposant=` pour la loi puissance, `z0=` pour la logarithmique |
| `ValueError … Σ O_j … ≠ 100 %` | des classes ont été écartées sans renormaliser | revenez à l'étape 3 : la renormalisation y est explicite |
| `KeyError` sur le nom de la ligne de `ess` | ligne inexistante dans `ess` | `print(ess)` : les lignes se lisent dans l'index de la feuille |
| `ModuleNotFoundError: openpyxl` | environnement non activé | `micromamba activate s9gm-fowt` |
| `rendus/` introuvable | dossier absent de votre clone | `mkdir -p rendus` (dossier ignoré par git) |

### Étape 5 — Générer les cas avec le gabarit TurbSim à trous

```python
from s9gm import cas, lancer, lire

lct = pd.read_csv(chemin_lct)
et = pd.read_csv(chemin_etats)
lct["seastate.WaveMod"] = 2                       # houle irrégulière JONSWAP
lct["seastate.WaveHs"] = et["Hs"]
lct["seastate.WaveTp"] = et["Tp"]
lct.to_csv("results/lct_phase1_cas.csv", index=False)

GABARIT = "seances/0b/turbsim_gabarit.inp"
tous = cas.generer_serie("results/lct_phase1_cas.csv", "modeles/flottant", "results/phase1_tous",
                         executer_turbsim=False, turbsim_inp=GABARIT)
print(len(tous), "cas relus par s9gm.cas et fabriqués, sans TurbSim ni OpenFAST")
```

**Vous devez voir** : autant de dossiers que de lignes de la LCT, sous `results/phase1_tous/`, chacun avec son `main.fst`, son `SeaState.dat`, son `Wind/<cas>.inp`.
`cas` **refuse** un trou resté vide (`IECturbc`, `RandSeed1`) en nommant le champ ; le gabarit reste à sa place, vous ne le copiez pas. La houle est **irrégulière JONSWAP**
(graine de houle : celle du fichier `SeaState` du modèle ; la colonne `seastate.WaveSeed(1)` la change) ; une seule réalisation par état de mer ne dit rien de la variabilité entre réalisations.

**Limite du modèle : la direction de la houle reste 0°.** Le modèle flottant refuse une direction de houle non nulle (OpenFAST s'arrête à l'initialisation : les données WAMIT du
second ordre, `marin_semi.12d`, ne couvrent que le cap 0°). Le **désalignement vent-houle** (`mis`) reste dans le fichier d'états de votre LCT, mais **n'est pas simulé** : écrivez-le dans
votre rendu comme ce que la LCT ne permet pas de conclure. Que change ce désalignement sur la réponse, et comment le représenter un jour (par exemple en faisant tourner le vent) : **question de discussion** pour votre rendu, ce dépôt ne la tranche pas.

| Symptôme | Cause | Geste |
|---|---|---|
| `ValueError : colonne « … » : le préfixe doit être l'un de …` | colonne inconnue dans la table passée à `cas` | gardez dans cette table seulement `cas`, `fst.*`, `turbsim.*`, `seastate.*`, `inflow.*`, `elastodyn.*` (les occurrences restent dans le fichier d'états) |
| `ValueError` qui nomme `IECturbc` ou `RandSeed1` | trou du gabarit non rempli | la colonne `turbsim.IECturbc` / `turbsim.RandSeed1` de la LCT doit être remplie |
| `KeyError : clé « … » trouvée 0 fois` | faute de frappe dans une colonne | la clé fautive est nommée ; corrigez l'en-tête |
| OpenFAST s'arrête : « does not contain the range of wave directions » | colonne `seastate.WaveDir` non nulle | laissez la direction de houle à 0° (limite du modèle, ci-dessus) |

### Étape 6 — Essai technique de la chaîne : lancer le cas d'exemple `EX00` à 300 s, puis lire

**Votre LCT n'est pas lancée ici** : elle attend la validation de l'enseignant (point de contrôle, section 1). Cet essai vérifie seulement que la chaîne (TurbSim, OpenFAST, lecture)
tourne chez vous. Son cas, `EX00`, n'est pas un cas de votre LCT : vent turbulent à 7,5 m/s (celui de l'énoncé pour F03), mêmes Hs et Tp que le cas `D01` (`cas/lct_flottant.csv` : Hs 6 m, Tp 10 s), en houle irrégulière JONSWAP.
Seuls les deux trous du gabarit, `IECturbc` et la graine, reprennent **vos** choix (ceux de la première ligne de votre LCT) : le gabarit ne se lance pas sans.

```python
ex = pd.DataFrame([{"cas": "EX00", "fst.TMax": 300,                      # 300 s en séance
                    "turbsim.URef": 7.5,
                    "turbsim.IECturbc": lct["turbsim.IECturbc"].iloc[0], "turbsim.RandSeed1": lct["turbsim.RandSeed1"].iloc[0],
                    "seastate.WaveMod": 2, "seastate.WaveHs": 6, "seastate.WaveTp": 10}])
ex.to_csv("results/lct_phase1_exemple.csv", index=False)
dossiers = cas.generer_serie("results/lct_phase1_exemple.csv", "modeles/flottant", "results/phase1", turbsim_inp=GABARIT)
lancer.lancer_serie(dossiers, coeurs=1, journal="results/phase1_journal.csv")

df, unites = lire.lire("results/phase1/EX00/main.outb")
df.plot(x="Time", y="PtfmSurge"); plt.show()      # regardez la courbe AVANT de choisir le transitoire
print(lire.statistiques(df, ["TwrBsMyt", "PtfmSurge", "PtfmHeave", "PtfmPitch", "FAIRTEN1", "FAIRTEN2", "FAIRTEN3"],
                        t_transitoire=<votre valeur>))
```

**Vous devez voir** : `termine` dans le journal de `lancer`, un fichier `results/phase1/EX00/main.outb`, puis un tableau de statistiques (moyenne, écart-type, min, max)
pour les points de calcul imposés de l'ENONCE (pied de tour, chaumards, mouvements du flotteur). **Ce cas est un essai technique de la chaîne, pas un résultat de votre LCT** : aucun cas de votre LCT n'est lancé avant sa validation par l'enseignant. Écrivez `t_transitoire` **et sa raison** (voir [`../../s9gm/POST-TRAITER.md`](../../s9gm/POST-TRAITER.md)).
Le temps de calcul est mesuré dans la section « Temps mesurés » ci-dessous.

| Symptôme | Cause | Geste |
|---|---|---|
| `turbsim` introuvable | environnement non activé | `micromamba activate s9gm-fowt` |
| `echec` dans le journal de `lancer` | OpenFAST s'est arrêté | lisez la fin de `results/phase1/EX00/run.log` |
| `KeyError: 'turbsim.IECturbc'` | votre LCT n'a pas cette colonne (étape 4) | refaites l'export de l'étape 4 avec votre catégorie, ou ajoutez la colonne |
| `KeyError: 'FAIRTEN1'` | canal absent de la sortie | `print(list(df.columns))` |
| `lire.statistiques` refuse de tourner | `t_transitoire` absent | regardez la courbe, choisissez une valeur (0 seulement si vous l'assumez) |

**Temps mesurés** (rejeu des commandes dans un clone neuf, machine de développement du cours, seule sur la machine ; la salle sera plus lente) :

| Étape | Durée mesurée |
|---|---|
| 1 à 5 (lecture, classes, LCT, génération sans TurbSim de 13 cas) | moins d'une seconde au total |
| 6 : champ de vent TurbSim (un cas) | ≈ 107 s |
| 6 : OpenFAST, 300 s simulées (un cas flottant turbulent) | ≈ 363 s (rapport 0,83) |
| Étape 6 entière, rejeu | 471 s |

Pour la campagne : un cas de 600 s simulées prend environ 12 min de calcul sur cette machine (voir la phase 2), contre « environ 25 min » annoncé pour une machine de la salle (ENONCE, §3 bis).

## 4. Post-traiter

La démarche générale, du `.outb` aux statistiques, aux figures et au DEL, est dans [`../../s9gm/POST-TRAITER.md`](../../s9gm/POST-TRAITER.md). Cette phase ne produit pas de sortie OpenFAST à post-traiter : elle travaille sur la table conjointe du site, avec `s9gm/metocean.py`.

## 5. Ce qu'on rend

**Rendu R1** : la LCT (tableur), une page de justification, le tableau de représentativité.

## 6. Théorie à lire

F2 (Houle linéaire) : *fiche à venir (master)*.
