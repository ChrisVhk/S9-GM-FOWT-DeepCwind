<!-- destinations: github -->
# Séance 0b — éolienne pilotée, monopieu, flottant (3 h)

Consigne autonome de la séance. Le cadre du projet (objectifs, évaluation, règles) est dans
[`../../ENONCE.md`](../../ENONCE.md) ; la séance précédente est la [0a](../0a/README.md), la phase suivante la
[phase 1](../phase1/README.md).

## 1. Objectif

Savoir **organiser, lancer, lire et vérifier à la main** une simulation OpenFAST, puis **voir ce que change le
passage du fixe au flottant** (phase 0 du projet, seconde moitié). Cette séance vous fait : générer des champs de
vent turbulents (TurbSim) et lancer l'éolienne fixe dans trois zones de régulation (F03 à F05) ; comprendre comment
OpenFAST « voit » une structure tubulaire (architecture du flotteur, au tableur) ; calculer à la main les raideurs
hydrostatiques du flotteur ; lancer l'éolienne flottante (D00 à D05) ; comparer fixe et flottant sur un même tableau.

## 2. Avant de commencer

**Premier geste, depuis n'importe quel dossier : `s9gm doctor`** (il vérifie votre poste et donne la commande exacte pour chaque point en défaut ; si `s9gm` est introuvable, activez l'environnement : `micromamba activate s9gm-fowt`). Un terminal ne vous est pas familier : [`annexes/TERMINAL.md`](../../annexes/TERMINAL.md), une page.

**À lire avant la séance** : fiche F2 (Houle linéaire), fiche F3 (Hydrostatique), fiche F4 (Morison) — *fiches à venir
(master)*. En leur absence, les renvois de cette page pointent vers le tutoriel LHEEA et la fiche F1 déjà disponibles
([`../../fiches/F1_Aero-regulation.md`](../../fiches/F1_Aero-regulation.md)).

**Ce qui doit déjà marcher** (séance [0a](../0a/README.md)) : `openfast -v` affiche `OpenFAST-v5.0.0` ; le contrôleur
est compilé (`bash scripts/build_discon.sh`) ; vous avez lancé F01 et F02 ; `turbsim` est dans le PATH
(`which turbsim`, environnement `s9gm-fowt` activé).

**Où vit ce que vous produisez.** `cas/`, `modeles/` et `seances/` sont des références suivies par git : vous les
**lisez et les lancez, sans les modifier**. Vos tables de cas, vos copies, vos sorties et vos figures vivent sous
`results/` (ou `rendus/` pour ce que vous rendez), que git ignore : un `git pull` ne vous les prendra jamais. Pour
travailler sur un fichier de référence (le carnet, le gabarit TurbSim), **copiez-le d'abord sous `results/`**.

**Si l'installation a échoué en 0a** : elle doit être terminée **avant cette séance**, à la maison ou en salle C09. Les
cas turbulents prennent du temps de calcul : lancez-les dès la fin de la séance si vous n'avez pas fini.

## 3. À faire, étape par étape

### 3.1 Éolienne fixe, vent turbulent : F03 à F05 (environ 45 min, calculs compris)

*Théorie : sections 6.1 et 6.2 (vent turbulent et gabarit TurbSim) ; 6.3 (contrôleur complet), 6.4 (monopieu).*

Générer les champs de vent avec **TurbSim** (vous choisissez la **catégorie de turbulence IEC** et la justifiez par le
projet OC3 (Jonkman et Musial, NREL/TP-5000-48191, §2.4.1) et par la correspondance des catégories de la norme
IEC 61400-1 ; vous fixez aussi la graine), puis lancer :

| Cas | Vent | Houle |
|---|---|---|
| F03 à F05 | turbulent 7,5 / 12 / 16 m/s (générés par vous, TurbSim) | — (fixe) |

| Cas | Vent | Zone de régulation |
|---|---|---|
| F03 | turbulent 7,5 m/s | à identifier (même vent moyen que F01) |
| F04 | turbulent 12 m/s | zone intermédiaire |
| F05 | turbulent 16 m/s | zone 3 |

**Fabriquer, lancer, lire : le paquet `s9gm`.** Pour six cas, éditer des fichiers à la main est possible ; pour
soixante (phase 2), c'est une source d'erreurs. Le paquet `s9gm` (dossier `s9gm/`, trois modules courts à lire —
chacun commence par son bloc Théorie) automatise exactement ce que vous avez fait en 0a :

1. **`cas`** — une Load Case Table (CSV : une ligne par cas, une colonne `fichier.Clé` par paramètre) → un dossier
   léger par cas, dans le dossier de sortie que vous indiquez (sous `results/`), à côté duquel `modeles/fixe/` reste
   inchangé, plus un `journal_cas.json` des valeurs avant/après. Une clé inconnue est une erreur, jamais un cas
   silencieusement inchangé.
2. **`lancer`** — exécute les cas, plusieurs à la fois (`coeurs=`), saute ceux qui sont déjà terminés et relance ceux
   qui ont été interrompus ou ont échoué ; note temps réel et temps simulé de chaque cas.
3. **`lire`** — lit un `.outb`, calcule moyenne, écart-type, min, max d'un canal. Vous *devez* donner
   `t_transitoire` : il n'y a pas de valeur par défaut, parce que le bon choix se lit sur la courbe.

**Le champ de vent : gabarit TurbSim.** [`turbsim_gabarit.inp`](turbsim_gabarit.inp) est un fichier d'entrée TurbSim
**complet, sauf deux champs** marqués `A_COMPLETER`, que **vous choisissez et justifiez** : `IECturbc` (la catégorie de
turbulence IEC) et `RandSeed1` (la graine). **Justification attendue de `IECturbc`** : citez la valeur de référence
d'intensité de turbulence que le projet OC3 a retenue pour les champs de vent de cette machine (Jonkman et Musial 2010,
NREL/TP-5000-48191, §2.4.1), et la catégorie IEC qui lui correspond dans la norme IEC 61400-1 (édition 3) ; la source
et la page comptent plus que la lettre choisie. Le vent moyen vient de l'énoncé (7,5 m/s dans le gabarit, pour F03 ;
pour F04 et F05 vous le changez dans votre LCT par `turbsim.URef`). Le gabarit **reste à sa place** : vous ne le
copiez pas dans `modeles/` ; vous le passez à `cas` par `turbsim_inp=` et vous remplissez les deux trous par des
colonnes `turbsim.Clé` de votre LCT (ou, si vous préférez un fichier, vous le copiez sous `results/` et vous éditez la
copie).

**Étape 1 — la table de cas.** Créez `results/lct_0b.csv` :

```
cas,fst.TMax,turbsim.URef,turbsim.IECturbc,turbsim.RandSeed1
F03,300,7.5,<votre catégorie>,<votre graine>
F04,300,12,<votre catégorie>,<votre graine>
F05,300,16,<votre catégorie>,<votre graine>
```

`cas` écrit alors `Wind/<cas>.inp`, lance TurbSim, produit `Wind/<cas>.bts` et pointe `inflow.WindType` /
`inflow.FileName_BTS` dessus (sauf si votre LCT les fixe). Un trou laissé vide est **refusé**, avec le nom du champ.
Fixer la graine rend le cas reproductible ; la changer donne une autre réalisation.

**Étape 2 — générer et lancer.** À lancer depuis la racine du dépôt, environnement `s9gm-fowt` activé (c'est lui qui
met `openfast` dans le PATH) :

```python
from s9gm import cas, lancer, lire
from s9gm.chemins import MODELES, RESULTS, SEANCES

dossiers = cas.generer_serie(RESULTS / "lct_0b.csv", MODELES / "fixe", RESULTS / "cas_0b",
                             turbsim_inp=SEANCES / "0b" / "turbsim_gabarit.inp")
lancer.lancer_serie(dossiers, coeurs=2, journal=RESULTS / "journal_lancer.csv")
```

**Vous devez voir** : un dossier `results/cas_0b/F03/`, `F04/`, `F05/` avec chacun un `Wind/Fxx.bts` (le champ de
vent) et un `main.outb`. Durée attendue : environ **3 min par cas** pour 300 s simulées (voir le tableau plus bas) ; la
génération du vent se fait avant le lancement du calcul.

**Avant de lire les résultats**, comme pour F01 : écrivez le vent moyen et l'intensité de turbulence attendus au
moyeu, puis relisez-les sur le champ produit (moyenne et écart-type de `Wind1VelX`). Si votre estimation et le champ
diffèrent, c'est l'estimation ou le fichier d'entrée qui est faux.

**Variante — vous avez déjà un champ `.bts`** (généré à part avec TurbSim, à placer dans le sous-dossier `Wind/` du
dossier du cas, après l'étape `cas` qui le crée ; `WindType = 3` désigne un champ TurbSim). Fichier `results/lct_0b.csv` :

```
cas,fst.TMax,inflow.WindType,inflow.FileName_BTS
F03,300,3,"Wind/F03.bts"
F04,300,3,"Wind/F04.bts"
F05,300,3,"Wind/F05.bts"
```

**À retenir** : le modèle partagé a pour vent par défaut une rampe lue dans `Wind/ramp_wind.dat`, chemin relatif au
dossier du cas (que `cas` ne copie pas) ; un cas qui ne précise pas `inflow.WindType` cherchera ce fichier et
s'arrêtera. Pour les cas flottants (D00-D05), même démarche avec `modeles/flottant/` ; `cas` édite `main.fst`,
`config_inflow.dat`, l'état de mer (`seastate.Clé`, copie locale de `SeaState.dat`) et l'entrée TurbSim
(`turbsim.Clé`) ; ses tests (`s9gm/tests/test_cas_flottant.py`) comparent chaque fichier généré à un fichier fait à la
main.

**Étape 3 — lire.** Pour chaque cas, **choisissez `t_transitoire` en regardant la courbe**, puis comparez F03, F04, F05 :

```python
from s9gm.chemins import RESULTS
df, unites = lire.lire(RESULTS / "cas_0b" / "F03" / "main.outb")
print(lire.statistiques(df, ["RotSpeed", "TwrBsMyt"], t_transitoire=<durée à écarter, en s>))
# à vous de la choisir en regardant la courbe : sans elle, lire refuse de calculer
```

Moyenne, écart-type, max de `RotSpeed`, `BldPitch1`, `TwrBsMyt`. Repérez la **région de régulation** de chacun avec les
seuils de la fiche F1 avant de commenter.

**En séance : `TMax = 300 s`** pour les cas turbulents (F03-F05, D03-D05) — tient dans les 3 h. **En option, à la
maison : `TMax = 600 s`**, à relancer et comparer au cas de 300 s (Q0.6, si vous le faites).

Temps de calcul mesuré pour un cas turbulent fixe de ce type (génération TurbSim + simulation OpenFAST, machine de
développement du cours) :

| Durée simulée | Génération TurbSim | Simulation OpenFAST | Total |
|---|---|---|---|
| 300 s | 1 min 07 s | 2 min 01 s | ≈ 3 min 10 s |

Cas flottants (OpenFAST seul, 300 s simulées, trois cas en parallèle, machine de développement du cours) :

| Cas | Simulation OpenFAST |
|---|---|
| D00, D01, D02 | 408 s, 439 s, 437 s (≈ 7 min) |
| D03, D04, D05 (champ de vent déjà généré) | ≈ 7 min 20 s chacun |

*À compléter pour 600 s.*

| Symptôme | Cause | Geste |
|---|---|---|
| `clé « … » trouvée 0 fois` | faute de frappe dans une colonne de la table | la clé fautive est nommée dans le message ; corrigez l'en-tête de votre LCT |
| erreur sur un champ vide | `IECturbc` ou `RandSeed1` non rempli | le champ est nommé ; le remplir (et le justifier) |
| le cas cherche `ramp_wind.dat` et s'arrête | `inflow.WindType` non fixé et pas de TurbSim | utiliser les colonnes `turbsim.*` ci-dessus |
| cas sauté (`termine`) | `lancer` saute un cas dont `run.log` et `main.outb` existent déjà | normal ; pour le refaire, supprimez le `main.outb` de ce cas |
| `turbsim` introuvable | environnement non activé | `micromamba activate s9gm-fowt` |

**Ce que ces cas ne permettent pas de conclure** : une seule graine ne dit rien de la variabilité entre graines, et un
maximum est un maximum *de cette réalisation*, pas un extrême de dimensionnement. 300 s est une durée réduite ; la
référence IEC est 600 s.

### 3.2 Architecture du modèle de flotteur, au tableur (environ 30 min)

*Théorie : section 6.5 (flotteur) ; fiche F4 (à venir (master)).*

À partir de la géométrie de la DeepCwind (dimensions fournies), compléter votre copie (sous `results/`) du classeur `DeepCwind_ARCHITECTURE.xlsx` : **nœuds**
(coordonnées dans le repère inertiel), **membres** (nœud 1 → nœud 2, jeu de propriétés, discrétisation), **jeux de propriétés**
(diamètre, épaisseur) et **coefficients hydrodynamiques** (Cd, Ca) par groupe — colonne centrale, colonnes déportées, bases,
pontons, entretoises. Retrouver ensuite chaque colonne du tableau dans le fichier HydroDyn du modèle. C'est la façon la plus
directe de comprendre comment OpenFAST « voit » une structure tubulaire, et ce tableau resservira en phase 5 (entretoises,
β = d/D).

Le classeur est [`DeepCwind_ARCHITECTURE.xlsx`](DeepCwind_ARCHITECTURE.xlsx) : un fichier suivi par git, que vous **copiez d'abord
sous `results/`** et dont vous remplissez la copie (LibreOffice Calc ou Excel ; enregistrez au format `.xlsx`).

```bash
cp seances/0b/DeepCwind_ARCHITECTURE.xlsx results/
```

**Ce que contient le classeur.**
- `Donnees` : les dimensions du document de définition OC5 (Tables 3-10 et 3-11, avec leur page), et la liste de ce que ce
  document **ne donne pas** (épaisseurs de paroi, Cd, Ca, discrétisation) : cela se lit dans le fichier HydroDyn du modèle
  flottant, [`modeles/oc4_rtest/…/NRELOffshrBsline5MW_OC4DeepCwindSemi_HydroDyn.dat`](../../modeles/flottant/README.md) (le
  `HydroFile` de `modeles/flottant/main.fst`).
- `Noeuds`, `Membres`, `Proprietes`, `Coefficients` : à remplir. Les cellules « à remplir » sont en jaune. **La colonne centrale
  (membre `M1`) est résolue en exemple**, en vert : regardez comment elle relie les quatre feuilles.
- Étiquettes : un nœud s'appelle `N…`, un jeu de propriétés `P…`, un membre `M…` (numéro du membre dans HydroDyn). Vous numérotez
  vos nœuds et vos jeux comme vous voulez (choisissez des étiquettes libres) ; vous les citez dans `Membres`.

**Contrôle.** Le script compare votre classeur, membre par membre, au fichier HydroDyn de `modeles/flottant` :

```bash
python scripts/verifier_architecture.py results/DeepCwind_ARCHITECTURE.xlsx
```

**Vous devez voir** : une ligne par membre du fichier HydroDyn, `juste`, `écart (…)` ou `manquant (…)`, puis un décompte. Sur le
classeur tel que livré : seule la colonne centrale est `juste`, les autres membres sont `manquant` (cellules encore « à remplir »).
À mesure que vous remplissez, les `manquant` deviennent `juste` ou `écart` ; un `écart` nomme le champ fautif et votre valeur, jamais
celle du fichier (à vous de la relire). **Un écart n'est pas forcément votre erreur** : le document de définition arrondit ses coordonnées (le script
tolère 7 cm), et le fichier HydroDyn peut contenir des joints et des membres que le tableau du document ne contient pas
(ceux-là n'ont pas de nom dans votre classeur : `sans nom`). Votre
travail est de **retrouver chaque colonne dans le fichier, puis d'attribuer chaque écart restant** (quel membre, quelle
différence entre le document et le fichier) : c'est l'objet de Q0.3.

| Symptôme | Cause | Geste |
|---|---|---|
| `Classeur illisible : …` | fichier non `.xlsx`, ouvert ailleurs, ou feuille renommée | enregistrez la copie en `.xlsx`, sans renommer les feuilles ni les colonnes |
| `manquant (nœud 1, …)` sur un membre que vous avez rempli | l'étiquette citée n'existe pas dans `Noeuds`, ou une faute de frappe (`n3`, `N 3`) | citez exactement l'étiquette de la feuille `Noeuds` |
| `manquant (coordonnées de N7 (nœud 1))` | le nœud est cité mais ses coordonnées sont encore « à remplir » | remplissez la ligne `N7` de `Noeuds` |
| `manquant (Cd du groupe …)` | la ligne du groupe est encore « à remplir » | remplissez `Coefficients` |
| `écart (nœud 2 N… : z = … ne correspond pas au fichier)` | coordonnée différente de celle du fichier au-delà de 7 cm | relisez la section « MEMBER JOINTS » ; est-ce votre erreur, ou une différence entre document et fichier ? |
| `écart (nœud 1 …)` et `écart (nœud 2 …)` inversés | sens du membre inversé | nœud 1 → nœud 2 dans le sens du fichier |

### 3.3 Raideurs hydrostatiques, à la main (environ 30 min)

*Théorie : fiche F3 (à venir (master)).*

Éolienne flottante (DeepCwind) — d'abord **à la main** : raideur hydrostatique en pilonnement K33 = ρ·g·Awl et en
tangage K55 = Δ·g·GM, à partir des dimensions fournies — **raideur totale = part de poussée + part de poids** : le
fichier `.hst` ne contient que la part de poussée, séparez-la de la part de poids pour comparer ; **conventions du
calcul « colonnes seules »** : l'aire et l'inertie de flottaison sont celles des colonnes seules, mais le volume de
carène V et le centre de carène z_B portent sur **l'ensemble des membres immergés**, d'après
[`../../data/geometrie_deepcwind.md`](../../data/geometrie_deepcwind.md) ; comparer aux valeurs utilisées par HydroDyn,
puis aux périodes propres. **Calculez d'abord sur les colonnes seules, à la main, sans rien ouvrir d'autre ;
confrontez ensuite le résultat à `s9gm.hydro` et au fichier `.hst` du modèle, puis attribuez l'écart** (quel membre,
quelle hypothèse, quel terme négligé l'explique).

**Pourquoi calculer à la main, puis confronter à `s9gm.hydro` (la théorie par les chiffres).** Le module `s9gm.hydro`
sait calculer ces raideurs depuis la géométrie : l'outil ne remplace pas votre calcul, il le **met à l'épreuve**. Un
calcul à la main sur les colonnes seules donne une première réponse ; la confrontation au module et au fichier `.hst` du
modèle vous montre un écart. Cet écart n'est ni une faute ni un bruit : c'est de l'information, à attribuer à ce que
vous avez laissé de côté (un membre, une hypothèse, un terme). Même démarche pour les périodes propres, où ce qui est
négligé pèse davantage : à vous de le chiffrer, terme par terme, avant de l'invoquer. Le module n'est utile que si vous
savez prédire ce qu'il va dire.

### 3.4 Éolienne flottante : D00 à D05 (environ 45 min, calculs compris)

*Théorie : sections 6.5 (flotteur) et 6.2 (vent turbulent).*

| Cas | Vent | Houle |
|---|---|---|
| D00 | aucun | régulière (Airy), H = 6 m, T = 10 s |
| D01 | constant 7,5 m/s | régulière, H = 6 m, T = 10 s |
| D02 | échelon de 5 à 20 m/s | régulière, H = 6 m, T = 10 s |
| D03 à D05 | turbulent 7,5 / 12 / 16 m/s (mêmes champs que F03-F05) | irrégulière JONSWAP, Hs = 6 m, Tp = 10 s |

Même principe qu'en 0a : **on change le moins de choses possible d'un cas à l'autre** — de D00 à D01, le vent s'ajoute ; de D01
à D02, le vent devient un échelon ; de D02 à D03, le vent devient turbulent (et la houle irrégulière).

Le modèle partagé est [`modeles/flottant/`](../../modeles/flottant/README.md) : la NREL 5 MW sur la plateforme OC4-DeepCwind, dérivée
du cas r-test OpenFAST, partant **au repos** comme le modèle fixe (rotor à l'arrêt, plateforme sans déplacement initial). Le
flotteur y est un seul corps rigide à 6 degrés de liberté.

**D00, D01, D02 sont des cas de référence** (`cas/`) : vous les lancez, sans les modifier.

```bash
for c in D00 D01 D02; do bash cas/run_cas.sh $c & done; wait     # les trois ensemble (un seul `run_cas.sh D00 D01 D02` les enchaînerait)
```

**Vous devez voir** : `OK en NN s -> .../results/D0x/main.outb` pour chacun environ **7 minutes par cas** pour 300 s simulées (mesuré avec les trois lancés ensemble, comme ci-dessus ; enchaînés, comptez la
somme) ; lancez-les dans un second terminal, pendant que vous travaillez sur autre chose. Lisez ensuite `results/D0x/main.outb` comme
au 3.1 : `lire.lire`, choix de `t_transitoire` en regardant la courbe, `lire.statistiques`. D00 n'a **aucun vent** (air au repos, sans
aérodynamique : `CompInflow = 0`, `CompAero = 0`) : le flotteur ne répond qu'à la houle.

**D03, D04, D05 sont à générer par vous**, avec les **mêmes champs de vent que F03, F04, F05** : ils n'existent que dans vos
dossiers de sortie, puisque la catégorie de turbulence et la graine sont vos choix. Une seconde table de cas, **dans le même
dossier de sortie que F03-F05**, dit à chaque cas D de relire le champ de son cas F :

```
cas,fst.TMax,inflow.WindType,inflow.FileName_BTS,seastate.WaveMod,seastate.WaveHs,seastate.WaveTp
D03,300,3,../F03/Wind/F03.bts,2,6,10
D04,300,3,../F04/Wind/F04.bts,2,6,10
D05,300,3,../F05/Wind/F05.bts,2,6,10
```

(`seastate.WaveMod = 2` : houle irrégulière JONSWAP ; `WaveHs`, `WaveTp` : Hs et Tp.) Enregistrez-la sous `results/lct_0b_flottant.csv`
puis, **une fois F03 à F05 générés** (3.1) :

```python
from s9gm.chemins import MODELES, RESULTS
dossiers = cas.generer_serie(RESULTS / "lct_0b_flottant.csv", MODELES / "flottant", RESULTS / "cas_0b")
lancer.lancer_serie(dossiers, coeurs=2, journal=RESULTS / "journal_lancer_D.csv")
```

**Vous devez voir** : `results/cas_0b/D03/`, `D04/`, `D05/`, chacun avec son `main.outb`, environ **7 à 8 minutes par cas** pour 300 s
simulées (mesuré sur la machine de développement du cours, trois cas en parallèle ; prévoyez le même ordre de grandeur en salle). Si un cas D ne trouve pas son
champ de vent (`FileName_BTS`), vérifiez que `results/cas_0b/F03/Wind/F03.bts` existe : le chemin est relatif au dossier du cas D.

| Symptôme | Cause | Geste |
|---|---|---|
| `D03` s'arrête à l'initialisation (fichier de vent introuvable) | F03 pas encore généré, ou autre dossier de sortie | générez F03-F05 d'abord, dans le même dossier de sortie que D03-D05 |
| `main.outb` absent après un cas D | `run.log` du cas se termine par une erreur | lisez la fin de `run.log` du cas |
| calcul beaucoup plus long que prévu | machine chargée, trop de cas en parallèle | `coeurs=` plus petit ; relancez `lancer` (il saute les cas terminés) |

### 3.5 Comparer fixe et flottant ; le vent apparent (environ 30 min)

*Théorie : sections 6.4 et 6.5.*

**Comparer fixe et flottant** sur un même tableau : pour `RootMyb1`, `YawBrFxn`, `TwrBsFxt`, `TwrBsMyt` et `RotSpeed`,
relever **maximum et écart-type** des cas 03 à 05. Le DEL de ce tableau sera complété en phase 3, quand vous l'aurez
programmé.

**Le vent apparent** : sur D01, estimer l'amplitude de la variation de vent vue par le rotor du fait des mouvements du
flotteur.

### 3.6 Carnet — « la théorie par les chiffres » (IEA 15 MW, environ 30 min, à faire quand vous voulez)

[`theorie_par_les_chiffres.ipynb`](theorie_par_les_chiffres.ipynb) reprend les formules de la fiche F1
(coefficient de puissance, régions du contrôleur, puissance, poussée, calage, fréquences 1P et 3P) et les calcule
**à la main sur une autre machine que celle de votre rendu** (l'IEA 15 MW sur monopieu), puis les confronte à un
calcul OpenFAST lu par `s9gm.lire` et aux valeurs publiées (Gaertner et al. 2020). Il vous demande de modifier un
paramètre et de voir l'effet, et de **justifier chaque écart** plutôt que de le constater. Il ne répond à aucune
question de votre rendu R0. Les six calculs OpenFAST sont livrés (`data/`) ; pour les relancer vous-même :
`bash scripts/installer_rosco.sh` puis `LANCER = True` dans le carnet (environ un quart d'heure, 6 cœurs).

Le carnet est un fichier suivi par git : **travaillez sur une copie** sous `results/` (vos modifications et ses
figures n'y toucheront pas la référence), puis ouvrez la copie :

```bash
micromamba activate s9gm-fowt
cp seances/0b/theorie_par_les_chiffres.ipynb results/
jupyter notebook results/theorie_par_les_chiffres.ipynb
```

## 4. Post-traiter

La démarche complète, du `.outb` aux statistiques, aux figures et au DEL, est dans
[`../../s9gm/POST-TRAITER.md`](../../s9gm/POST-TRAITER.md). Ce qui est propre à cette séance :

- pour chaque cas turbulent, choisir et justifier `t_transitoire` en regardant la courbe, puis comparer les
  statistiques d'un même canal aux deux durées (300 s et, si vous l'avez fait, 600 s) ;
- tableau fixe / flottant : maximum et écart-type des cinq canaux imposés (étape 3.5) ;
- raideurs hydrostatiques : confrontation de votre calcul à `s9gm.hydro` et au fichier `.hst` (étape 3.3).

## 5. Ce qu'on rend

**Rendu R0 — seconde partie**, dans `rendus/` (les questions Q0.1 et Q0.2 sont celles de la [séance 0a](../0a/README.md)) :

- Q0.3 — Classeur d'architecture complété (votre copie remplie, dans `rendus/`), et correspondance avec le fichier HydroDyn ; K33 et K55 **à la main**
  (colonnes seules), puis **confrontés à `s9gm.hydro` et au fichier `.hst` du modèle, avec attribution de l'écart** ;
  périodes propres qui en découlent, et ce qui les écarte des valeurs publiées. L'attribution compte plus que le chiffre.
- Q0.4 — Tableau fixe / flottant (max, écart-type) et trois constats argumentés : ce qui change, pourquoi, et ce que ce
  tableau ne permet pas encore de conclure sur la fatigue.
- Q0.5 — Citez les paramètres qui définissent une ligne de Load Case Table (au moins huit) et dites lesquels vous avez
  déjà fait varier dans ce tutoriel.
- Q0.6 (si vous avez relancé un cas turbulent à 600 s en plus des 300 s de la séance) — Comparez les statistiques d'un
  même canal entre les deux durées : l'écart est-il dans le bruit, ou significatif ? Qu'est-ce que cela vous dit sur la
  durée à retenir pour un rendu qui compte ?

Pour chaque cas lancé (F03 à F05, D00 à D05), joignez : le `t_transitoire` choisi avec sa raison, les statistiques retenues, la
région de régulation, et une phrase sur ce que le cas ne permet pas de conclure.

Le carnet de la section 3.6 ne répond à aucune question de ce rendu.

## 6. Théorie à lire

Index de la théorie : [`fiches/README.md`](../../fiches/README.md).

Fiche F2 : [`../../fiches/F2_Houle-lineaire.md`](../../fiches/F2_Houle-lineaire.md). Fiches F3, F4 : *fiche à venir (master)*. Fiche F1 : [`../../fiches/F1_Aero-regulation.md`](../../fiches/F1_Aero-regulation.md).
Les blocs ci-dessous reprennent, pour les trois premiers, ceux des cas 03 à 05 du tutoriel LHEEA, que ce parcours ne
lance plus (ils restent consultables dans [`../../annexes/lheea/`](../../annexes/lheea/README.md)).

### 6.1 Vent turbulent et durée de simulation

### Bloc Théorie
1. **Question physique** — Un dommage de fatigue ou une statistique de charge calculés sur un
   vent turbulent dépendent-ils de la durée simulée, et si oui comment ?
2. **Modèle** — un champ de vent turbulent est une réalisation aléatoire (une « seed ») ; ses
   statistiques (moyenne, écart-type, valeurs extrêmes) ne convergent vers celles du processus
   qu'avec la durée. **Domaine de validité** : la norme IEC 61400-1 recommande 10 minutes (600 s)
   comme durée de référence pour les statistiques de charge — 300 s est une durée réduite, acceptée
   ici pour tenir dans la séance, pas la durée de référence professionnelle.
3. **Ordre de grandeur attendu** — la méthode : comparer, sur un même cas relancé à 300 s puis à
   600 s (en option, à la maison), les statistiques d'un canal (moyenne, écart-type, max) — pas
   leur valeur elle-même, l'écart entre les deux durées.
4. **Ce que le modèle ne permet pas de conclure** — une seule seed, quelle que soit sa durée, ne
   dit rien de la variabilité entre seeds (point revu en phase 1-2, Load Case Table).
5. **Renvois** — IEC 61400-1 (durée de référence) ; phase 1 de l'énoncé (occurrences, Load Case
   Table).

### 6.2 Le champ de vent : gabarit TurbSim

### Bloc Théorie
1. **Question physique** — Un vent turbulent est une réalisation aléatoire : quelles grandeurs décident de ce
   que vous simulez, et lesquelles sont des choix (catégorie de turbulence, graine) à justifier plutôt que des données ?
2. **Modèle** — TurbSim synthétise un champ de vitesse 3D à partir d'un spectre (modèle de Kaimal selon IEC),
   d'une cohérence spatiale, d'un profil moyen en loi de puissance, et d'une graine : mêmes entrées, mêmes
   graines, **même champ**, octet pour octet. Le vent moyen fixe le point de fonctionnement ; la classe de
   turbulence fixe l'écart-type ; la graine fixe *quelle* réalisation. **Domaine de validité** : turbulence
   atmosphérique neutre type IEC, au-dessus d'une surface rugueuse ; pas de rafale extrême, pas de jet de
   basse couche.
3. **Ordre de grandeur attendu** — la méthode : avant de lancer, écrire le vent moyen et l'intensité de
   turbulence que vous attendez à la hauteur du moyeu (la catégorie IEC que vous avez justifiée la fixe), puis les relire sur le champ produit (moyenne et
   écart-type de la composante longitudinale au moyeu). Si votre estimation et le champ diffèrent, c'est
   l'estimation ou le fichier d'entrée qui est faux.
4. **Ce que le modèle ne permet pas de conclure** — qu'une seule graine représente la variabilité du site :
   deux graines donnent deux champs différents, et leurs charges diffèrent ; une graine ne dit rien de
   l'extrême de dimensionnement.
5. **Renvois** — fiche F1 (vent moyen et régions de régulation) ; IEC 61400-1 (modèle de turbulence normale) ;
   `s9gm/cas.py` (génération du champ depuis la LCT), `s9gm/tests/test_cas.py` (mêmes entrées, même champ).

### 6.3 Contrôleur complet en vent variable (cas LHEEA 03)

*D'après le tutoriel OpenFAST Quickstart du LHEEA (Apache-2.0), §3, adapté — voir
[`../../annexes/lheea/NOTICE`](../../annexes/lheea/NOTICE). Ce bloc décrit le cas 03 du tutoriel, que ce parcours ne
lance plus ; le contrôleur est le même que celui de F02 et de F03 à F05.*

### Bloc Théorie
1. **Question physique** — Comment un contrôleur complet (couple ET pitch) répond-il quand le
   vent passe du régime normal au régime nominal ?
2. **Modèle** — contrôleur Bladed-DLL complet (`DISCON.so`, compilé depuis `DISCON.F90` —
   `scripts/build_discon.sh`) : couple piloté (rampe de Region 1½, puis loi de Region 2) en dessous du régime nominal,
   pitch actif au-delà pour plafonner la puissance. **Domaine de validité** : la rampe de vent de
   ce cas est lente (600 s) — elle teste la réponse en quasi-statique, pas la réactivité face à une
   rafale rapide ou à un vent turbulent.
3. **Ordre de grandeur attendu** — la méthode : repérer sur le résultat l'instant où le calage
   des pales (`BldPitch1`) commence à s'écarter de zéro, et vérifier que la puissance se stabilise
   près de sa valeur nominale au-delà plutôt que de continuer à croître avec le vent.
4. **Ce que le modèle ne permet pas de conclure** — une rampe lente ne teste pas la réactivité du
   contrôleur face à une rafale rapide, et ce cas isolé ne dit rien de la variabilité d'un vent réel
   (turbulence, vue au cas 05).
5. **Renvois** — tutoriel OpenFAST Quickstart du LHEEA §3 — **attention** : le texte du tutoriel y
   décrit un contrôleur élémentaire sans pitch, mais le fichier de ce dépôt utilise déjà le
   contrôleur complet (voir `ADAPTATION_LHEEA.md`) ; fiche F1 (régulation).

### 6.4 Éolienne sur monopieu (cas LHEEA 04)

*D'après le tutoriel OpenFAST Quickstart du LHEEA (Apache-2.0), §4, adapté — voir
[`../../annexes/lheea/NOTICE`](../../annexes/lheea/NOTICE). Ce bloc décrit le cas 04 du tutoriel, que ce parcours ne
lance plus ; le modèle `modeles/fixe/` des cas F01 à F05 est lui aussi un monopieu représenté par SubDyn.*

### Bloc Théorie
1. **Question physique** — Comment modélise-t-on une fondation flexible (pas un simple
   encastrement rigide ponctuel) pour une structure offshore ?
2. **Modèle** — SubDyn représente le monopieu par des membres-poutres cylindriques droits reliés
   à des nœuds (pas articulés, liaisons rigides entre membres) ; un seul nœud, au fond marin, est
   un véritable encastrement (les 6 DDL y sont bloqués) — le nœud du haut est l'interface avec la
   partie ElastoDyn (transition piece), où la plateforme reste libre dans ses 6 DDL. **Domaine de
   validité** : SubDyn représente une structure comme un assemblage de poutres élancées droites —
   c'est le même principe qui sera utilisé en phase 5 (niveau C) pour le flotteur, pas une méthode
   différente ; ce qui change d'un cas à l'autre, c'est la géométrie assemblée, pas la méthode.
3. **Ordre de grandeur attendu** — la méthode : sur la rampe de vent fournie par ce cas
   (déterministe, pas de turbulence ici), comparer le moment en pied de structure en début et fin
   de rampe, et le relier à la variation de poussée du rotor avec le vent. La flexibilité du
   monopieu se traduit par une petite rotation de la plateforme (`PtfmPitch`) — pas nulle, mais
   faible comparée à ce que vous observerez au cas flottant (05).
4. **Ce que le modèle ne permet pas de conclure** — une rampe déterministe ne représente pas la
   variabilité d'un vent réel : c'est le cas suivant (05) qui introduit un vent turbulent, généré
   par TurbSim. Par ailleurs, ce cas (comme le 05) tourne en BEMT quasi-stationnaire
   (`Wake_Mod=1`), pas en DBEMT dynamique — la dynamique du sillage observée n'est donc pas
   exactement celle d'un calcul DBEMT, à garder en tête si vous comparez à une documentation qui le
   suppose.
5. **Renvois** — tutoriel OpenFAST Quickstart du LHEEA §4 — **attention** : le texte du tutoriel y
   décrit un vent turbulent (TurbSim), mais ce dépôt utilise une rampe déterministe à la place, le
   fichier `.bts` d'origine n'ayant jamais été distribué par l'amont (voir `ADAPTATION_LHEEA.md`).

### 6.5 Éolienne flottante (cas LHEEA 05)

*D'après le tutoriel OpenFAST Quickstart du LHEEA (Apache-2.0), §5, adapté — voir
[`../../annexes/lheea/NOTICE`](../../annexes/lheea/NOTICE). Ce bloc décrit le cas 05 du tutoriel, que ce parcours ne
lance plus ; les cas D00 à D05 reposent sur la même plateforme OC4-DeepCwind.*

### Bloc Théorie
1. **Question physique** — Qu'est-ce qui change structurellement dans le modèle quand la
   fondation n'est plus ancrée au sol (monopieu encastré) mais libre de bouger (flotteur ancré par
   des lignes caténaires) ?
2. **Modèle** — HydroDyn combine théorie potentielle (grands éléments, coefficients WAMIT
   précalculés, fichier `marin_semi.*`) et théorie de Morison (éléments fins, entretoises) ;
   MoorDyn calcule l'ancrage caténaire dynamique. **Domaine de validité** : les coefficients WAMIT
   sont précalculés pour CETTE géométrie précise (DeepCwind) — ne se transposent pas tels quels à
   un autre flotteur.
3. **Ordre de grandeur attendu** — la méthode : comparer les mouvements de plateforme
   (`PtfmPitch`, faible au cas 04 — flexibilité du monopieu seule — attendu bien plus grand ici,
   réponse du flotteur à la houle et au vent) et la puissance produite entre le cas fixe sur
   monopieu (04, vent en rampe) et ce cas flottant (05, vent turbulent) — **sans oublier que les deux
   cas ne partagent pas le même vent** : une partie de la différence observée vient de là, pas
   seulement de la fondation.
4. **Ce que le modèle ne permet pas de conclure** — rappel de l'énoncé (§3) : le flotteur est un
   seul corps rigide dans ce modèle — aucun effort intérieur (contrainte dans une entretoise) n'en
   est directement tiré ; ce point est traité en phase 5 par d'autres méthodes.
5. **Renvois** — tutoriel OpenFAST Quickstart du LHEEA §5 ; `ENONCE.md` §3 (limite du corps
   rigide) ; fiche F5 (hydrodynamique potentielle, à publier).
