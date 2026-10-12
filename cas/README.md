<!-- destinations: github -->
# Tutoriel de prise en main — de l'éolienne fixe à l'éolienne flottante

Ce tutoriel transpose en OpenFAST v5.0.0 une progression inspirée d'un cours de Master Génie
Maritime (2013) sur les outils de conception éolien pour les études d'avant-projet. Il sert
d'ouverture au cours DMO-S9 (phase 0 de l'énoncé).

## Organisation

```
modeles/fixe/      (à la racine du dépôt) fichiers communs de l'éolienne fixe (monopieu OC3) -- ne pas lancer directement
cas/F01/, F02/, ...  un dossier LÉGER par cas : main.fst (pointe vers modeles/fixe/) + ce qui change
modeles/flottant/  fichiers communs de l'éolienne flottante DeepCwind (dérivé du r-test OC4)
cas/D00/, D01/, D02/  idem, pour le flottant (D03-D05 : à générer par vous, séance 0b)
cas/E01/, E02/       cas d'échauffement de la séance 0a (tour seule, rotor libre), sur modeles/fixe/
cas/lct_*.csv        les tables de cas dont `s9gm.cas` a fabriqué E01, E02, D00-D02
cas/run_cas.sh     lance un cas de référence sur une copie sous results/ (ou plusieurs, ou "all")
```

**Règle de résolution des chemins** : un chemin relatif écrit DANS un fichier secondaire
(ElastoDyn, AeroDyn, ServoDyn…) se résout par rapport au dossier DE CE FICHIER SECONDAIRE
lui-même, pas par rapport au dossier du `.fst` primaire. `main.fst` peut donc pointer vers
`../../modeles/fixe/config_aerodyn.dat`, et ce dernier garde ses propres références internes
(`Airfoils/DU21_A17.dat`) inchangées : elles visent toujours `modeles/fixe/Airfoils/`, jamais le
dossier du cas qui l'appelle.

**Commande qui le démontre** : un `main.fst` contenant uniquement `config_inflow.dat` en local et
les 7 autres champs de fichiers réécrits en `"../../modeles/fixe/config_xxx.dat"`, exécuté par
`cd F01 && openfast main.fst`, charge correctement les `Airfoils/` de `modeles/fixe/` (AeroDyn) et
le contrôleur compilé dans `modeles/oc4_rtest/5MW_Baseline/ServoData/` (ServoDyn) — chemin lui-même
écrit à l'intérieur de `modeles/fixe/config_servodyn.dat`, à UN niveau (`../oc4_rtest/...`,
relatif à `modeles/fixe/`), jamais réécrit lors du partage. `OpenFAST terminated normally.` dans les
deux cas.

**Conséquence pour le dépôt** : `F01/` et `F02/` ne contiennent plus que `main.fst` et ce qui leur
est propre (`config_inflow.dat`, et `Wind/ramp_wind.dat` pour F02) — `Airfoils/`, `tower.dat`,
`blade_*.dat`, `SeaState.dat` et les `config_*.dat` partagés vivent une seule fois, dans
`modeles/fixe/`.

**Règle : ce dossier est une référence, vous n'y modifiez rien.** Les cas de `cas/` sont suivis par git :
vous les lancez et vous les lisez, vous ne les éditez pas (un `git pull` ne doit jamais rencontrer un fichier
que vous avez modifié). **Pour créer un nouveau cas**, copiez un cas existant **directement sous `results/`**
(`cp -r cas/F01 results/F01_essai`, à la même profondeur que `cas/F01` : son `main.fst` pointe déjà vers
`../../modeles/fixe/` et reste valable), et ne modifiez dans la copie que ce qui doit changer (le plus souvent
`config_inflow.dat`, propre à chaque cas, et `TMax` dans `main.fst`). Pour plus de quelques cas, passez par
`s9gm.cas` (séance 0b), qui écrit les cas sous le dossier de sortie que vous indiquez.

## Avant de lancer un cas

Depuis la racine du dépôt (une seule fois après chaque `git clone`) :
```
micromamba activate s9gm-fowt
bash scripts/build_discon.sh
```

Puis, depuis la racine du dépôt :
```
bash cas/run_cas.sh F01
bash cas/run_cas.sh F01 F02
bash cas/run_cas.sh all
bash cas/run_cas.sh results/F01_essai     # un dossier à vous (qui contient un main.fst) : lancé sur place
```

**Où vont les sorties.** `run_cas.sh` copie le cas de référence **sous `results/<cas>/`** (même profondeur que `cas/` : les
chemins relatifs restent valables) et le lance dans cette copie : `cas/` n'est jamais modifié, `main.outb` et `run.log` sont
sous `results/<cas>/`. Relancer un cas de référence **écrase** son dossier `results/<cas>/` : nommez autrement les copies que vous modifiez (`results/F01_essai`).

## Cas disponibles

| Cas | Vent | Houle | Ce qu'on regarde |
|---|---|---|---|
| F01 | constant 7,5 m/s | — (fixe) | régime établi : poussée, moment en pied de tour, RotSpeed |
| F02 | échelon 5 → 20 m/s à t = 100 s | — (fixe) | passage d'une zone de régulation à l'autre |
| F03-F05 | turbulent (TurbSim, à générer) 7,5 / 12 / 16 m/s | — (fixe) | *à générer par vous sous `results/`, séance 0b* |
| E01 | — (tour seule) | — | échauffement 0a : oscillation libre de la tour |
| E02 | constant 8 m/s, cisaillement, sans contrôleur | — | échauffement 0a : rotor libre |
| D00 | aucun | régulière, H = 6 m, T = 10 s | réponse du flotteur à la houle seule |
| D01 | constant 7,5 m/s | régulière, H = 6 m, T = 10 s | vent + houle |
| D02 | échelon 5 → 20 m/s à t = 100 s | régulière, H = 6 m, T = 10 s | échelon de vent sur flotteur |
| D03-D05 | turbulent (mêmes champs que F03-F05) | JONSWAP, Hs = 6 m, Tp = 10 s | *à générer par vous sous `results/`, séance 0b* |

**Lecture d'un `.fst`** : ouvrez `F01/main.fst` dans un éditeur de texte (lecture seule : ne l'enregistrez pas modifié). Les sections qui
changent d'un cas à l'autre dans ce tutoriel : `TMax` (durée), le nom du fichier `InflowFile`
(éventuellement son contenu), et plus tard (D00+) `CompHydro`/`SeaStFile`/`HydroFile`/
`MooringFile`. Tout le reste (degrés de liberté, pas de temps, modules actifs, sorties) reste
identique au modèle de base pour les cas F et D de ce tutoriel (E01 et E02, cas d'échauffement, éteignent des modules et bloquent
la plateforme) — c'est volontaire : on apprend d'abord à changer une
seule chose à la fois.

**Attention — le cas fixe tourne en BEMT, pas en DBEMT** : le modèle v3.2.1 d'origine demandait
`Wake_Mod=2` (DBEMT), mais OpenFAST v5.0.0 refuse cette valeur pour la combinaison de projection
utilisée ici. Les cas F01-F05 tournent donc en BEMT quasi-stationnaire (`Wake_Mod=1`) — gardez-le
en tête si vous comparez à une documentation qui suppose du DBEMT.

## Temps de calcul mesurés (sur la machine de développement du cours)

| Cas | Durée simulée | Temps réel mesuré | Ratio sim/CPU |
|---|---|---|---|
| F01 | 200 s | 91 s | 2,2 |
| F02 | 300 s | 127 s | 2,4 |

Temps de calcul de F03-F05 et des cas flottants D00-D05 : voir la [séance 0b](../seances/0b/README.md), section 3 (si le temps
de calcul dépasse ce que permettent les 3 h de séance, réduire la durée simulée et le signaler).

## Vérifications à la main (F01)

Avec R = 63 m, TSR optimal = 7,55, vent = 7,5 m/s : calculez la vitesse de rotation attendue
Ω = TSR·V/R (voir fiche F1) et comparez-la au `RotSpeed` observé en régime établi — doit être
cohérente avec la zone de régulation : **identifiez d'abord la région** de F01 avec les seuils de
la fiche F1 (être sous le régime nominal de 12,1 tr/min ne suffit pas à choisir la loi à appliquer). Comparez aussi ce
calcul à la fréquence 1P visible sur `RootMyb1` (fréquence = RotSpeed / 60).

Pour le moment en pied de tour (`TwrBsMyt`) : estimez la poussée du rotor à partir de la théorie du
disque actuateur (voir fiche F1) et comparez `TwrBsMyt` ≈ poussée × (hauteur du moyeu − `TowerBsHt`), à ±20 %.
`TwrBsMyt` est le moment **au pied de la tour** : le bras de levier se compte depuis ce pied,
dont la hauteur `TowerBsHt` se lit dans `modeles/fixe/config_elastodyn.dat`, et non depuis le
niveau de la mer ni depuis le sol (le
modèle complet inclut aussi le poids de la nacelle/tour en flexion, d'où l'écart toléré).
