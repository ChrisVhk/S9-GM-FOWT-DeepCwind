<!-- destinations: github -->
# Séance 0b — éolienne pilotée, monopieu, flottant (3 h)

Déroulé pas à pas. L'énoncé complet est dans [`../../ENONCE.md`](../../ENONCE.md) (phase 0,
séance 0b).

**À lire avant la séance** : fiches F2 (Houle linéaire), F3 (Hydrostatique), F4 (Morison) — à
publier avant la séance ; en leur absence, les renvois de cette page pointent vers le tutoriel
LHEEA et la fiche F1 déjà disponibles.

Cette séance poursuit la progression du tutoriel OpenFAST Quickstart du LHEEA (cas 03 à 05),
commencée en séance 0a (cas 01-02) : du contrôle réaliste d'une éolienne jusqu'au flotteur ancré.
Elle prépare la construction de vos propres cas (F03-F05, D00-D05) du tutoriel `prise_en_main/`.

## 1. Cas LHEEA 03 — éolienne pilotée en vent variable (environ 30 min)

*D'après le tutoriel OpenFAST Quickstart du LHEEA (Apache-2.0), §3, adapté — voir
[`../../tutorials/lheea/NOTICE`](../../tutorials/lheea/NOTICE).*

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

```bash
cd tutorials/lheea/03_ControlledWT/1_Configuration
openfast main.fst
```

## 2. Cas LHEEA 04 — éolienne sur monopieu (environ 30 min)

*D'après le tutoriel OpenFAST Quickstart du LHEEA (Apache-2.0), §4, adapté — voir
[`../../tutorials/lheea/NOTICE`](../../tutorials/lheea/NOTICE).*

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

```bash
cd tutorials/lheea/04_MonopileWT/1_Configuration
openfast main.fst
```

## 3. Cas LHEEA 05 — éolienne flottante (environ 30 min)

*D'après le tutoriel OpenFAST Quickstart du LHEEA (Apache-2.0), §5, adapté — voir
[`../../tutorials/lheea/NOTICE`](../../tutorials/lheea/NOTICE).*

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

Le cas 05 nécessite un fichier de vent turbulent supplémentaire (~70 Mo, non suivi par git) :
générez-le d'abord avec `bash scripts/generer_vent_turbulent_05.sh` (voir `README.md` racine).

```bash
cd tutorials/lheea/05_FOWT/1_Configuration
openfast main.fst
```

## Carnet — « la théorie par les chiffres » (IEA 15 MW, environ 30 min, à faire quand vous voulez)

[`theorie_par_les_chiffres.ipynb`](theorie_par_les_chiffres.ipynb) reprend les formules de la fiche F1
(coefficient de puissance, régions du contrôleur, puissance, poussée, calage, fréquences 1P et 3P) et les calcule
**à la main sur une autre machine que celle de votre rendu** (l'IEA 15 MW sur monopieu), puis les confronte à un
calcul OpenFAST lu par `s9gm.lire` et aux valeurs publiées (Gaertner et al. 2020). Il vous demande de modifier un
paramètre et de voir l'effet, et de **justifier chaque écart** plutôt que de le constater. Il ne répond à aucune
question de votre rendu R0. Les six calculs OpenFAST sont livrés (`data/`) ; pour les relancer vous-même :
`bash scripts/installer_rosco.sh` puis `LANCER = True` dans le carnet (environ un quart d'heure, 6 cœurs).

```bash
micromamba activate s9gm-fowt
jupyter notebook seances/0b/theorie_par_les_chiffres.ipynb
```

## 4. Vos propres cas — F03-F05 et D00-D05 (à construire)

Les cas 01-05 du tutoriel LHEEA (ci-dessus et séance 0a) montrent la progression complète fixe →
flottant sur des exemples déjà construits. Il vous reste à construire les vôtres, dans
`tutorials/prise_en_main/` (voir son `README.md` pour l'organisation modèle partagé + dossier
léger par cas) :

| Cas | Vent | Houle |
|---|---|---|
| F03 à F05 | turbulent 7,5 / 12 / 16 m/s (générés par vous, TurbSim) | — (fixe) |
| D00 | aucun | régulière (Airy), H = 6 m, T = 10 s |
| D01 | constant 7,5 m/s | régulière, H = 6 m, T = 10 s |
| D02 | échelon de 5 à 20 m/s | régulière, H = 6 m, T = 10 s |
| D03 à D05 | turbulent (mêmes champs que F03-F05) | irrégulière JONSWAP, Hs = 6 m, Tp = 10 s |

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

### Fabriquer, lancer, lire : le paquet `s9gm`

Pour six cas, éditer des fichiers à la main est possible ; pour soixante (phase 2), c'est une
source d'erreurs. Le paquet `s9gm` (dossier `s9gm/`, trois modules courts à lire — chacun
commence par son bloc Théorie) automatise exactement ce que vous venez de faire :

1. **`cas`** — une Load Case Table (CSV : une ligne par cas, une colonne `fichier.Clé` par
   paramètre) → un dossier léger par cas à côté de `modele_fixe/`, plus un `journal_cas.json` des
   valeurs avant/après. Une clé inconnue est une erreur, jamais un cas silencieusement inchangé.
2. **`lancer`** — exécute les cas, plusieurs à la fois (`coeurs=`), saute ceux qui sont déjà
   terminés et relance ceux qui ont été interrompus ou ont échoué ; note temps réel et temps simulé de chaque cas.
3. **`lire`** — lit un `.outb`, calcule moyenne, écart-type, min, max d'un canal. Vous *devez*
   donner `t_transitoire` : il n'y a pas de valeur par défaut, parce que le bon choix se lit sur la
   courbe.

Exemple pour F03-F05 (le champ de vent `.bts` est celui que vous avez généré avec TurbSim, à
placer dans le sous-dossier `Wind/` du dossier du cas, après l'étape `cas` qui le crée ; `WindType = 3` désigne un champ TurbSim) — fichier `lct_0b.csv` :

```
cas,fst.TMax,inflow.WindType,inflow.FileName_BTS
F03,300,3,"Wind/F03.bts"
F04,300,3,"Wind/F04.bts"
F05,300,3,"Wind/F05.bts"
```

À lancer depuis la racine du dépôt, environnement `s9gm-fowt` activé (c'est lui qui met
`openfast` dans le PATH) :

```python
from s9gm import cas, lancer, lire

dossiers = cas.generer_serie("lct_0b.csv", "tutorials/prise_en_main/modele_fixe",
                             "tutorials/prise_en_main")
# ... ici : déposer chaque Wind/F0x.bts dans le dossier du cas, puis :
lancer.lancer_serie(dossiers, coeurs=2, journal="journal_lancer.csv")
df, unites = lire.lire("tutorials/prise_en_main/F03/main.outb")
print(lire.statistiques(df, ["RotSpeed", "TwrBsMyt"], t_transitoire=<durée à écarter, en s>))
# à vous de la choisir en regardant la courbe : sans elle, lire refuse de calculer
```

À retenir : le modèle partagé a pour vent par défaut une rampe lue dans `Wind/ramp_wind.dat`, chemin
relatif au dossier du cas (que `cas` ne copie pas) ; un cas qui ne précise pas `inflow.WindType`
cherchera ce fichier et s'arrêtera. Pour les cas flottants (D00-D05),
même démarche avec votre `modele_flottant/` ; en revanche `cas` ne sait éditer que `main.fst` et
`config_inflow.dat` : la houle (`SeaState.dat`) est un fichier de plus à ajouter à `FICHIERS` dans
`s9gm/cas.py` — c'est un exercice de lecture du code, avec ses tests dans `s9gm/tests/`.

**TurbSim depuis la LCT (option).** Si le modèle contient un `turbsim.inp`, des colonnes `turbsim.Clé` (`turbsim.RandSeed1`,
`turbsim.URef`, `turbsim.IECturbc`…) éditent une copie de ce fichier dans `Wind/<cas>.inp` et `cas` lance TurbSim :
`Wind/<cas>.bts` est produit, et `inflow.WindType` / `inflow.FileName_BTS` y sont pointés (sauf si votre LCT les
fixe). Fixez `turbsim.RandSeed1` : même graine, même champ — c'est ce qui rend un cas reproductible. À vous de
choisir (et de justifier) l'intensité de turbulence.

**En séance : `TMax = 300 s`** pour les cas turbulents (F03-F05, D03-D05) — tient dans les 3 h.
**En option, à la maison : `TMax = 600 s`**, à relancer et comparer au cas de 300 s (Q0.6, si
vous le faites).

Temps de calcul mesuré pour un cas turbulent fixe de ce type (génération TurbSim + simulation
OpenFAST, machine de développement du cours) :

| Durée simulée | Génération TurbSim | Simulation OpenFAST | Total |
|---|---|---|---|
| 300 s | 1 min 07 s | 2 min 01 s | ≈ 3 min 10 s |

*À compléter pour 600 s et pour les cas flottants (D0x) une fois construits.*

Classeur d'architecture du flotteur (`DeepCwind_ARCHITECTURE.xlsx`) et raideurs hydrostatiques
K33/K55 à la main : voir `ENONCE.md`, phase 0, séance 0b, points 7-8.

## Rendu R0 (suite)

Questions Q0.3 à Q0.5 de l'énoncé (section « Phase 0 », rendu R0) : classeur d'architecture,
tableau fixe/flottant, paramètres d'une Load Case Table. Q0.6, optionnelle : comparaison 300 s /
600 s si vous avez relancé un cas aux deux durées.
