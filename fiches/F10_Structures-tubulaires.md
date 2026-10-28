<!-- destinations: github -->
<!-- master: Cours/OFFSHORE_Structures-Fondations/02_Fatigue-et-structures-tubulaires.md ; nature : fiche, sélection du master (sections 7 à 12) -->
# Fiche F10 — Structures tubulaires

**À lire avant** : phase 5 (tour, entretoise, domaine de validité du SCF) ; la fiche F9 (fatigue de structure) pour la courbe S-N et la règle de Miner, que cette fiche utilise sans les redémontrer.

## Pourquoi

Une entretoise, une colonne, une tour sont des tubes soudés. La fissure de fatigue n'y naît pas au milieu du tube mais au **pied d'un cordon**, là où la géométrie concentre la contrainte. Cette fiche donne les mots (corde, bretelle, selle, couronne), la façon de passer de la contrainte nominale à la contrainte de point chaud par un **facteur de concentration de contrainte** (SCF), et surtout la discipline qui accompagne toute formule de SCF : vérifier qu'on est dans son **domaine de validité** avant de s'en servir. Elle dit aussi ce qu'une tour tubulaire demande en plus : compacité, boulons de bride, soudures.

## Minimum vital

### Vocabulaire et typologie des nœuds

Un nœud relie un tube principal, la **corde** (diamètre `D`, épaisseur `T`), à une **bretelle** (`d`, `t`) inclinée de l'angle `θ`. Le long de l'intersection, la **couronne** est dans le plan de la bretelle, la **selle** hors de ce plan. La bretelle est sollicitée par un effort axial `N`, un moment dans le plan `M_IP`, un moment hors plan `M_OP`.

La classe d'un nœud (T/Y, X, K, KT) se décide **par le trajet de l'effort de chaque bretelle**, pas par la forme : T/Y si l'effort est repris en cisaillement de poutre dans la corde, X s'il traverse la corde, K s'il est équilibré par d'autres bretelles du même côté (à 10 % près, bretelles coplanaires à 15° près). La classe peut changer avec le cas de charge et peut être un mélange. Seuls les nœuds **simples** ont des formules paramétriques ; un nœud complexe ou multiplanaire (cas d'une entretoise de semi-submersible) se traite par éléments finis.

### Paramètres adimensionnels

Les SCF de la RP-C203 (annexe B) dépendent de cinq rapports et d'un angle :

```math
\beta=\frac dD,\qquad \alpha=\frac{2L}{D},\qquad \gamma=\frac{D}{2T},\qquad \tau=\frac tT,\qquad \zeta=\frac gD,\qquad \theta
```

avec `L` la longueur de corde et `g` l'entre-fer ; `ζ` peut être négatif (le master lit les bornes négatives comme un recouvrement). Attention, `α`, `β`, `τ` portent d'autres sens dans d'autres passages de la norme (cône, cisaillement) : on écrit toujours les six valeurs numériques du nœud avant de choisir une formule.

### Contrainte nominale, contrainte de point chaud

```math
\sigma_{hs}=\mathrm{SCF}\;\sigma_{nom}
```

`σ_nom` est la contrainte nominale de la **bretelle** (effort sur section, par la résistance des matériaux de poutre). Le SCF contient tous les effets de géométrie et de chargement, sauf l'entaille microscopique du cordon, qui est **dans la courbe S-N**. Il dépend du mode de chargement (axial, flexion dans le plan, flexion hors plan), varie le long de l'intersection, et se donne côté corde et côté bretelle : les deux côtés se traitent séparément. Pour combiner les modes, la RP-C203 évalue la contrainte en **huit points** autour de l'intersection (axial interpolé linéairement entre couronne et selle, flexion en sinus) ; le maximum peut tomber entre selle et couronne.

### SCF paramétriques d'Efthymiou (RP-C203, annexe B)

Le jeu de formules d'Efthymiou est donné par les tables B-1 à B-5 de la RP-C203 (32 équations, T/Y, X, K, KT). Exemple, nœud T/Y, effort axial, extrémités de corde encastrées, **selle de corde** :

```math
\gamma\,\tau^{1{,}1}\Big(1{,}11-3(\beta-0{,}52)^2\Big)(\sin\theta)^{1{,}6}
```

Pour une corde courte (`α < 12`), un facteur correctif réduit le SCF des selles ; pour les couronnes, la norme recommande en général des variantes qui n'exigent pas de paramètre de fixité, les formules de base ne valant que pour une action unique dans la bretelle. Le choix des équations suit le type de nœud et la charge.

### Domaine de validité

Les formules ne valent que dans ce **domaine de validité** (même bornes dans la RP-C203 et dans le manuel d'El-Reedy) :

| Paramètre | Borne |
|---|---|
| `β` | de 0,2 à 1,0 |
| `τ` | de 0,2 à 1,0 |
| `γ` | de 8 à 32 |
| `α` | de 4 à 40 (borne haute supprimée pour deux variantes de couronne) ; corrections de corde courte si `α < 12` |
| `θ` | de 20° à 90° |
| `ζ` | de `−0,6 β / sin θ` à 1,0 |

**Hors domaine**, la norme renvoie aux **éléments finis** : pas d'extrapolation de la formule. Un autre ouvrage propose de calculer le SCF aux valeurs réelles, aux valeurs limites, puis de prendre le maximum ; ce n'est pas dans la RP-C203.

### Autres singularités soudées d'un tube

La RP-C203 donne aussi des SCF pour : le désalignement et le changement d'épaisseur d'une soudure bout à bout de tubes (placer toute transition d'épaisseur à l'**extérieur**, en pente 1:4 ; l'ovalisation est en général la plus forte contribution), un anneau raidisseur, une transition conique, un tube long en traction, un gousset, un nœud injecté de coulis. Un nœud raidi par anneaux : les formules ne sont pas dans ce cours. Pour la ST-0126 (supports fixes ; emploi **par analogie** pour un flotteur) : distance minimale entre deux soudures circonférentielles, tolérances serrées, meulage du pied de cordon qui apporte un facteur **3,5 sur la durée de vie** si ses conditions sont remplies, sans bénéfice en corrosion libre.

### La tour tubulaire

La tour est un tube conique de grand diamètre et faible épaisseur, soudé par viroles et assemblé par brides boulonnées. La ST-0126 ne donne pas de formule de résistance de section : elle renvoie à des normes dont le domaine est limité en `D/t` (EN 1993-1-1 et 1-6 pour `D/t < 250` ; ISO 19902 ou NORSOK N-004 pour `D/t < 120`). Les relations de résistance de section d'un tube (contrainte équivalente de Von Mises, flexion, cisaillement d'un tube mince) relèvent d'un cours de résistance des matériaux ; cette fiche ne les développe pas.

- **Compacité** : un tube est compact si `D/t ≤ 50 ε²`, avec `ε = √(235/f_y)` (`f_y` en MPa) ; limites de 50, 70 et 90 `ε²` pour les types I, II, III. Au-delà, vérification de **voilement local de coque** : voir la norme (DNV-RP-C202 ou EN 1993-1-6).
- **Facteur partiel de matériau** `γ_M` : 1,10 pour les éléments tubulaires de base ; avec DNV-RP-C202 ou NORSOK N-004, il augmente avec l'élancement relatif de voilement (jusqu'à 1,40) ; avec l'EN 1993-1-6, 1,10.
- **Boulons de bride** : seuls les boulons précontraints sont admis ; précharge au plus `0,7 f_ub A_s` ; résistance de calcul en traction `F_t,Rd = 0,9 f_ub A_s / γ_M2` avec `γ_M2 = 1,25`.
- **Soudures** : pleine pénétration pour les assemblages dynamiques importants et pour les nœuds tubulaires ; `γ_Mw = 1,25` à l'état limite ultime.

## Ordres de grandeur, par la méthode

- **Vérifier un nœud** : relevez `D, T, d, t, g, θ, L` ; calculez `β, γ, τ, α, ζ` ; comparez chacun à la table du domaine ; notez si `α < 12`. Un seul paramètre dehors suffit à renvoyer aux éléments finis.
- **Effet d'un SCF sur le dommage** : la contrainte de calcul est multipliée par le SCF ; avec une courbe S-N de pente `m` (fiche F9), le nombre de cycles varie en `Δσ^{-m}`, donc, sur une branche de pente `m`, le dommage en `SCF^{m}`. Une référence bibliographique citée par le master dit que sous-estimer un SCF de 18 % peut doubler la vie prédite : `0,82^{-m}` vaut 1,81 pour `m = 3` et 2,00 pour `m = 3,5` (calcul du master).
- **Sensibilité** (exemple fictif) : pour la selle de corde du nœud T/Y ci-dessus, autour de `γ = 15`, `τ = 0,5`, `β = 0,5`, `θ = 90°`, l'équation donne 7,76 ; doubler `γ` double le résultat ; doubler `τ` le multiplie par `2^{1,1}`. Une paroi de corde mince et une bretelle épaisse sont les plus défavorables.
- **Un SCF reste supérieur à 1** (exemple fictif) : à `γ = 8`, `τ = 0,2`, `β = 0,5`, `θ = 90°`, une couronne de corde d'un nœud X donne 0,54, inférieur à 1 : sans plancher, une valeur de table pourrait entrer dans le dommage sous la contrainte nominale. La ST-0126 et El-Reedy donnent un plancher de 1,5 sur le SCF d'un nœud tubulaire ; le master n'en a pas retrouvé dans la RP-C203.
- **Gain du meulage** : un facteur 3,5 sur la vie équivaut à multiplier l'étendue admissible par `3,5^{1/m}` : 1,52 pour `m = 3`, 1,28 pour `m = 5`.
- **Compacité** (exemple fictif) : pour `f_y = 355` MPa, `ε² = 0,662` et les limites de `D/t` sont 33,1 ; 46,3 ; 59,6. Un tube de tour de grand `D/t` (plus de 200) n'est pas compact : il se vérifie au voilement.
- **Boulon** (exemple fictif) : avec `γ_M2 = 1,25`, la résistance de calcul vaut 1,03 fois la précharge maximale : la marge est de 3 % de la précharge.

Le choix du SCF de calcul du projet appartient à l'enseignant ; cette fiche n'en fixe aucun.

## Ce que le modèle ne permet pas de conclure

- **Un SCF paramétrique n'a de sens que dans son domaine** de validité, et seulement pour un nœud simple. Hors domaine, aucune extrapolation n'est justifiée ; un nœud avec raidisseurs, cloisons, plusieurs plans de bretelles relève des éléments finis.
- Les deux sources qui donnent le domaine sont deux transcriptions du même jeu de formules : leur accord confirme la lecture des bornes, non une validation physique indépendante.
- **Un SCF issu d'un modèle éléments finis** est une valeur de **ce modèle** : il dépend du maillage, de la procédure de lecture et d'extrapolation (par exemple lecture à `0,5 t` et `1,5 t` de la ligne d'intersection, sans cordon modélisé), des conditions d'appui, de la convention de côté (bretelle ou corde). Il ne se lit pas comme un abaque et ne se transpose pas à un autre joint.
- Le SCF ne contient pas l'entaille du cordon (elle est dans la courbe S-N) ; le choix de la courbe et de l'épaisseur de référence reste à faire (fiche F9).
- **Résistance statique d'un nœud** : la RP-C203 ne traite que la fatigue. La voie API (manuel d'El-Reedy) donne des capacités de bretelle par des facteurs `Q_u` et `Q_f`, dans un domaine différent de celui du SCF (`γ` de 10 à 50, `θ` de 30° à 90°). Le cours n'établit pas laquelle des deux voies, API ou DNV, est la plus prudente, et il ne faut pas panacher équations, courbe S-N et coefficients de sécurité de deux familles.
- La ST-0126 vise les éoliennes fixes : pour la tour d'un flotteur, elle s'emploie **par analogie**.
- Le voilement local de coque et la résistance de section d'un tube ne sont pas traités ici : se reporter à la norme et à un cours de résistance des matériaux.

## Pour aller plus loin

Le master du sous-module « fatigue et structures tubulaires » (chemin en tête de cette fiche) détaille, aux sections 7 à 12 : la typologie des nœuds (§ 7), le point chaud et la méthode des facteurs d'influence par éléments finis (§ 8), le domaine et les tables B-1 à B-5 (§ 9), la voie API comparée à la voie DNV (§ 10), les singularités soudées (§ 11), la tour, les brides et les soudures (§ 12). Sources : DNV-RP-C203, édition 2010 (annexe B, tables B-1 à B-5) ; DNVGL-ST-0126 ; le manuel d'El-Reedy (§ 3.7) ; la fiche F9 ; le [guide du classeur](../annexes/atelier_tour/README.md) ; le Formulaire ([`FORMULAIRE.md`](FORMULAIRE.md)).
