# Tutoriel de prise en main — de l'éolienne fixe à l'éolienne flottante

Ce tutoriel transpose en OpenFAST v5.0.0 une progression inspirée d'un cours de Master Génie
Maritime (2013) sur les outils de conception éolien pour les études d'avant-projet. Il sert
d'ouverture au cours DMO-S9 (phase 0 de l'énoncé).

## Organisation

```
modele_fixe/      fichiers communs de l'éolienne fixe (monopieu OC3) -- ne pas lancer directement
F01/, F02/, ...    un dossier LÉGER par cas : main.fst (pointe vers modele_fixe/) + ce qui change
modele_flottant/   (à construire, séance 0b) fichiers communs de l'éolienne flottante DeepCwind
D00/, D01/, ...    (à construire, séance 0b) idem, pour le flottant
run_cas.sh         lance un cas (ou plusieurs, ou "all")
```

**Règle de résolution des chemins** : un chemin relatif écrit DANS un fichier secondaire
(ElastoDyn, AeroDyn, ServoDyn…) se résout par rapport au dossier DE CE FICHIER SECONDAIRE
lui-même, pas par rapport au dossier du `.fst` primaire. `main.fst` peut donc pointer vers
`../modele_fixe/config_aerodyn.dat`, et ce dernier garde ses propres références internes
(`Airfoils/DU21_A17.dat`) inchangées : elles visent toujours `modele_fixe/Airfoils/`, jamais le
dossier du cas qui l'appelle.

**Commande qui le démontre** : un `main.fst` contenant uniquement `config_inflow.dat` en local et
les 7 autres champs de fichiers réécrits en `"../modele_fixe/config_xxx.dat"`, exécuté par
`cd F01 && openfast main.fst`, charge correctement les `Airfoils/` de `modele_fixe/` (AeroDyn) et
le contrôleur compilé dans `models/oc4_rtest/5MW_Baseline/ServoData/` (ServoDyn) — chemin lui-même
écrit à l'intérieur de `modele_fixe/config_servodyn.dat`, à TROIS niveaux (`../../../models/...`,
relatif à `modele_fixe/`), jamais réécrit lors du partage. `OpenFAST terminated normally.` dans les
deux cas.

**Conséquence pour le dépôt** : `F01/` et `F02/` ne contiennent plus que `main.fst` et ce qui leur
est propre (`config_inflow.dat`, et `Wind/ramp_wind.dat` pour F02) — `Airfoils/`, `tower.dat`,
`blade_*.dat`, `SeaState.dat` et les `config_*.dat` partagés vivent une seule fois, dans
`modele_fixe/`.

**Pour créer un nouveau cas** : créez un dossier léger, copiez-y `main.fst` depuis un cas existant
(il pointe déjà vers `modele_fixe/`), et ne modifiez que ce qui doit changer (le plus souvent
`config_inflow.dat`, propre à chaque cas, et `TMax` dans `main.fst`).

## Avant de lancer un cas

Depuis la racine du dépôt (une seule fois après chaque `git clone`) :
```
micromamba activate s9gm-fowt
bash scripts/build_discon.sh
```

Puis, depuis ce dossier :
```
bash run_cas.sh F01
bash run_cas.sh F01 F02
bash run_cas.sh all
```

## Cas disponibles

| Cas | Vent | Houle | Ce qu'on regarde |
|---|---|---|---|
| F01 | constant 7,5 m/s | — (fixe) | régime établi : poussée, moment en pied de tour, RotSpeed |
| F02 | échelon 5 → 20 m/s à t = 100 s | — (fixe) | passage d'une zone de régulation à l'autre |
| F03-F05 | turbulent (TurbSim, à générer) 7,5 / 12 / 16 m/s | — (fixe) | *à construire, séance 0b* |
| D00-D05 | — / constant / échelon / turbulent (mêmes vents que F01-F05) | — / régulière / JONSWAP | *à construire, séance 0b* |

**Lecture d'un `.fst`** : ouvrez `F01/main.fst` dans un éditeur de texte. Les sections qui
changent d'un cas à l'autre dans ce tutoriel : `TMax` (durée), le nom du fichier `InflowFile`
(éventuellement son contenu), et plus tard (D00+) `CompHydro`/`SeaStFile`/`HydroFile`/
`MooringFile`. Tout le reste (degrés de liberté, pas de temps, modules actifs, sorties) reste
identique au modèle de base pour ce tutoriel — c'est volontaire : on apprend d'abord à changer une
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

*À compléter pour F03-F05 et D00-D05 (séance 0b) : si le temps de calcul dépasse ce que permettent
les 3 h de séance, réduire la durée simulée et le signaler ici.*

## Vérifications à la main (F01)

Avec R = 63 m, TSR optimal = 7,55, vent = 7,5 m/s : calculez la vitesse de rotation attendue
Ω = TSR·V/R (voir fiche F1) et comparez-la au `RotSpeed` observé en régime établi — doit être
cohérente avec la zone de régulation (en dessous du régime nominal 12,1 tr/min). Comparez aussi ce
calcul à la fréquence 1P visible sur `RootMyb1` (fréquence = RotSpeed / 60).

Pour le moment en pied de tour (`TwrBsMyt`) : estimez la poussée du rotor à partir de la théorie du
disque actuateur (voir fiche F1) et comparez `TwrBsMyt` ≈ poussée × (hauteur du moyeu − `TowerBsHt`), à ±20 %.
`TwrBsMyt` est le moment **au pied de la tour** : le bras de levier se compte depuis ce pied,
dont la hauteur `TowerBsHt` se lit dans `modele_fixe/config_elastodyn.dat`, et non depuis le
niveau de la mer ni depuis le sol (le
modèle complet inclut aussi le poids de la nacelle/tour en flexion, d'où l'écart toléré).
