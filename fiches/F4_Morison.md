<!-- destinations: github -->
<!-- master: Cours/OFFSHORE_Structures-Fondations/03_Morison-et-efforts-sur-elements-elances.md ; nature : fiche, sélection du master (sections 1 à 8 et 12) -->
# Fiche F4 — Morison

**À lire avant** : séance 0b (architecture du modèle de flotteur, étape 3.2 : lire les colonnes `Cd` et `Ca` d'un membre) ; phase 2 (famille Centre : potentiel contre Morison contre hybride) ; phase 5 (efforts d'inertie sur les colonnes) ; les fiches F2 (cinématique de la houle) et F5 (hydrodynamique potentielle).

## Pourquoi

La théorie potentielle (fiche F5) ne prévoit **aucune traînée** : l'eau y est parfaite et ne se décolle jamais du corps. Pour un tube mince,
c'est justement la séparation de l'écoulement qui compte. La formule de Morison est l'outil des **éléments élancés** : elle donne l'effort
par mètre de tube à partir de la vitesse et de l'accélération de l'eau, au prix de deux coefficients empiriques, `C_D` et `C_M`.
Cette fiche vous dit ce que contient chaque terme, de quoi dépendent les coefficients, **jusqu'où** la formule vaut, ce que l'on fait quand
le tube bouge, et pourquoi le choix « Morison ou potentiel » d'un élément est une question de taille devant la longueur d'onde.

## Minimum vital

### La formule

Pour un cylindre de diamètre `D`, de section `S = πD²/4`, dans une eau de vitesse `U` et d'accélération `\dot U` (perpendiculaires à l'axe), l'effort par unité de longueur est :

```math
F=\rho\,C_M\,S\,\dot U+\tfrac12\,\rho\,C_D\,D\,U\lvert U\rvert ,\qquad C_M=1+C_A .
```

- Le terme en `\dot U` est l'**inertie**. Le potentiel l'explique : la pression de l'écoulement non perturbé (Froude-Krylov) donne `ρ S \dot U`,
  la masse ajoutée du cercle donne autant (`C_A = 1`), d'où `C_M = 2` en fluide parfait.
- Le terme en `U\lvert U\rvert` est la **traînée**, ajout empirique : elle n'existe pas en fluide parfait.
- Les deux sont **en quadrature** pour une houle sinusoïdale : l'inertie est maximale quand la traînée est nulle, et inversement. La force totale n'atteint
  donc pas la somme des deux maxima.
- Le master dérive la formule d'un écoulement sinusoïdal en gardant les deux premiers termes d'une série de Fourier (en phase avec l'accélération, en phase avec la vitesse).

La DNV (RP-C205, OS-J101) l'écrit sous la même forme ; la J101 l'écrit par tranche `dz` avec la vitesse de **l'eau** notée `\dot x`
(et non celle de la structure : attention au symbole).

### Élément qui bouge : quatre formes d'emploi (RP-C205)

Avec `\dot X`, `\ddot X` la vitesse et l'accélération de l'élément et `U_r = U − \dot X` la vitesse relative :

```math
\text{fixe : } F=\rho(1+C_A)S\dot U+\tfrac12\rho C_D D\,U\lvert U\rvert ,\qquad
\text{relative : } F=-\rho C_A S\ddot X+\rho(1+C_A)S\dot U+\tfrac12\rho C_D D\,U_r\lvert U_r\rvert .
```

La forme relative s'écrit aussi `ρ S \dot U + ρ C_A S(\dot U − \ddot X)` : l'inertie ne voit que l'**accélération relative** pour sa part « masse ajoutée ».
Les deux autres formes (élément en eau calme ; « champs indépendants ») sont dans le master. Avec la vitesse relative, **un seul** coefficient de traînée suffit et la norme dit de ne pas ajouter d'amortissement hydrodynamique en plus.

### Pieu vertical en houle : inertie et traînée intégrées

Pour une houle d'Airy d'amplitude `A` en profondeur `h`, intégrées du fond au niveau de repos (`ω² = g k tanh kh`) :

```math
F_I=-\rho C_M\frac{\pi D^2}{4}\,A g\tanh kh\,\sin\omega t ,\qquad
F_D=\tfrac14\rho C_D D\,A^2 g\Big(1+\frac{2kh}{\sinh 2kh}\Big)\cos\omega t\lvert\cos\omega t\rvert .
```

En eau profonde, l'inertie s'applique à `1/k` sous la surface, la traînée à `1/(2k)` : l'inertie est appliquée **deux fois plus bas**, ce qui compte pour le moment à la base d'une colonne.
Intégrer jusqu'au niveau de repos néglige la crête : l'erreur est mineure quand l'inertie domine, importante quand la traînée domine.

### Qui domine ? Le nombre de Keulegan-Carpenter

`KC = v_m T / D` (vitesse orbitale maximale `v_m`, période `T`) compare le chemin de l'eau en une demi-houle au diamètre ; pour une houle de hauteur `H`, `KC = πH/D`.
Le rapport des maxima de traînée et d'inertie (RP-C205) vaut :

```math
\frac{f_{D,\max}}{f_{I,\max}}=\frac{C_D}{\pi^2(1+C_A)}\,KC .
```

`KC` petit : l'eau contourne le tube sans se décoller, l'inertie domine. `KC` grand : sillage, traînée. Trois sources donnent trois seuils d'égalité (de l'ordre de 20, 23 et 40 en `KC`, suivant la définition) : ce sont trois questions différentes, pas trois contradictions.

### Les coefficients `C_D` et `C_M`

Ils dépendent de `KC`, du nombre de Reynolds `Re` et de la **rugosité relative** `k/D` (hauteur d'aspérité sur diamètre) ; la forme de la section et l'orientation jouent aussi. Le paramètre visqueux est `β_S = Re/KC = D²/(νT)`.
Deux familles de sources :

- **Normative (RP-C205 et J101)** : mêmes formules, une seule voix (ajustement sur un document antérieur de l'API) ; l'accord de l'une avec l'autre ne dit rien de plus que « même ajustement ». Traînée stationnaire `C_DS(k/D)` : lisse `0,65`, rugueux `1,05`, interpolation logarithmique entre les deux ; facteur de sillage `ψ(KC)` donné pour `KC < 12` seulement (au-delà, une courbe sans formule) ; `C_M = 2` pour `KC < 3`, puis décroissance jusqu'à `1,6` (lisse) ou `1,2` (rugueux) aux grands `KC`. La J101 propose aussi des valeurs de projet pour la mer du Nord (fatigue, diamètres modestes), de source unique.
- **Physique (Molin)** : régimes de Reynolds (sous-critique, critique, sur-critique, trans-critique), chute de traînée au régime critique, rugosité qui l'avance et l'atténue, mesures en tube en U : `C_M` peut descendre sous 1 aux `β_S` faibles, `C_D` passe par un maximum vers `KC ≈ 10`. Ces essais sont à `β_S` bien plus petit que ceux de projet : on ne les transpose pas.

Pour juger un `C_D` qu'on vous rapporte, demandez la norme employée, le `KC`, la rugosité et l'épaisseur de croissance marine.

### Rugosité et croissance marine

La croissance marine épaissit le tube (`D = D_C + 2t`), le rend rugueux et l'alourdit. La RP-C205 la dit linéaire sur deux ans et fournit des épaisseurs de 30 à 100 mm selon la latitude et la profondeur ; Molin donne typiquement 50 à 100 mm, de masse volumique voisine de 1300 kg/m³ : les deux s'accordent.
Elle compte aussi pour les appendices (anodes). Le calcul qui suit est un **exemple fictif** du master : 100 mm sur un tube d'un mètre multiplient la traînée par 1,8 à 1,9 (diamètre ×1,2, coefficient ×1,5 à 1,6) : la rugosité compte plus que l'épaisseur pour les tubes de l'ordre du mètre (moitié-moitié vers 2 m).

### Jusqu'où la formule vaut : le rapport `D/λ`

La formule suppose que la houle n'est pas perturbée par le tube. Trois sources posent un seuil, le plus souvent présenté comme une indication. Les voici **côte à côte** ; la fiche n'en recommande aucun.

| Source | Énoncé | Nuance dans la source |
|---|---|---|
| RP-C205, p.78 | `D < λ/5` (`λ > 5D`) : Morison « normalement » applicable | *normalement* |
| RP-C205, p.96-97 | grand volume si `D > λ/6`, dit **équivalent** à `πD/λ > 0,5` | *habituellement* |
| OS-J101 | `D < 0,2 λ` ; au-delà, « typiquement », l'inertie se calcule par diffraction | net, puis *typiquement* |
| Molin | `D < λ/6`, soit `k a ≲ 0,5` (`a` rayon) : un critère de corps « petit » | *un critère* |

Lecture du master : ce ne sont que **deux valeurs numériques**, `D/λ = 1/5` (0,200) et `1/6` (0,167), plus la variante `πD/λ = 0,5` (soit 0,159). L'équivalence « `D > λ/6 ⇔ πD/λ > 0,5` » n'est juste qu'à 5 % près (4,7 %, car `π/6 = 0,524`). Entre 1/6 et 1/5, la RP-C205 dit deux choses : le recouvrement est interne à cette norme, et aucune des sources ne propose de règle de transition. Un exemple de Molin : un diamètre de 20 m impose, pour rester sous 1/6, une période d'au moins 9 s environ.
Le seuil ne dit rien de la valeur des coefficients : `KC`, `Re` et `k/D` comptent aussi (voir plus haut). Aux seuils, la houle qui déferle (`H/λ ≈ 0,14`) limite `KC` à 2 ou 3 environ : près de la frontière de diffraction, la traînée est faible et l'inertie domine.

### Au-delà du seuil : MacCamy-Fuchs

La diffraction d'une houle régulière par un cylindre vertical circulaire posé au fond a une **solution exacte** (Molin l'attribue à Havelock en profondeur infinie, étendue à la profondeur finie ; la J101 la nomme MacCamy-Fuchs et la tabule). Elle revient à corriger le **coefficient d'inertie** : l'amplitude de la charge divisée par `ρ π a² A g tanh kh` vaut 2 quand `ka → 0` (Morison avec `C_M = 2`), puis s'en écarte avec `ka = πD/λ`. Valeurs du master pour un cylindre isolé :

| `D/λ` | `C_M` effectif | écart à 2 |
|---|---|---|
| 0,05 | 2,04 | +1,8 % |
| 1/6 | 1,99 | −0,6 % |
| 1/5 | 1,89 | −5,7 % |
| 0,25 | 1,68 | −16 % |
| 0,50 | 0,79 | −60 % |

L'amplitude dépasse légèrement 2 sous 1/6 (maximum 2,065 vers `D/λ ≈ 0,10`), puis baisse vite au-delà de 1/5, et la charge se déphase (11° à 1/6, 14,5° à 1/5 pour la J101). **Ces valeurs valent pour un cylindre isolé, traversant la surface** : ni les groupes de cylindres, ni les corps immergés ne sont couverts. Que HydroDyn utilise cette solution n'est dans aucune source présente.

### Mouvement relatif et amortissement de traînée

La RP-C205 recommande la vitesse relative si l'amplitude du mouvement `X_m` dépasse un diamètre, ou si la vitesse réduite `V_R = v T_n / D` (période propre `T_n` de la structure) atteint 20 ; entre 10 et 20 le risque est de surestimer l'amortissement, sous 10 on peut négliger la vitesse de la structure. Pour la **dérive lente** d'un flotteur (colonnes en mouvement de grande période), Molin et la norme s'accordent sur la pratique : champs indépendants, une traînée pour l'écoulement lent et une pour l'écoulement rapide.
Aux échelles réelles, les grosses colonnes amortissent peu tant que `KC < 5` environ (mouvement inférieur à un diamètre), ce qui explique le faible amortissement des mouvements lents.
Ne confondez pas un coefficient **d'élément** (sans dimension, propre à une section, un `KC` et un `Re`) et un coefficient **global** quadratique (en N·s²/m², propre à un objet et à une calibration) : l'amortissement de Coulling est du second type, un coefficient par degré de liberté.

### Linéariser la traînée

Pour un calcul en fréquence, on remplace `U\lvert U\rvert` par un terme linéaire équivalent. Deux hypothèses, deux coefficients :

```math
\sin\omega t\,\lvert\sin\omega t\rvert\simeq\frac{8}{3\pi}\sin\omega t ,\qquad U\lvert U\rvert\simeq\sqrt{8/\pi}\;\sigma_U\,U\ \ (U\ \text{gaussien, moyenne nulle}).
```

Harmonique (signal sinusoïdal d'amplitude connue) et stochastique (écart-type `σ` de la vitesse relative) se résolvent par itération, car la réponse inconnue fixe le coefficient. Ils ne sont pas interchangeables : à écart-type égal, un sinusoïde donne `1,20 σ` contre `1,60 σ` pour un gaussien. Limites : la linéarisation convient à la **réponse** (la traînée dissipe l'énergie), pas aux **charges extrêmes** ; elle exige une moyenne nulle, et la forme linéarisée avec un courant moyen n'est donnée par aucune des sources.

## Ordres de grandeur, par la méthode

Les exemples sont **fictifs** et sortent du master ; refaites la démarche avec vos propres données.

- **Qui domine** : pour `H = 15 m` en eau profonde, un tube de `D = 1 m` a `KC = πH/D ≈ 47` (traînée) ; pour un diamètre de plusieurs mètres, `KC` tombe à quelques unités et l'inertie domine (exemple fictif, d'après le master). Calculez `KC` avant de choisir un modèle.
- **Bras de levier** : pour `T = 10 s`, `λ ≈ 156 m`, donc `1/k ≈ 25 m` et `1/(2k) ≈ 12 m` : l'inertie s'applique deux fois plus bas.
- **Seuil et période** : en eau profonde (`λ = 1,56 T²`), la période minimale pour que `D` reste sous `λ/5` ou `λ/6` se calcule en une ligne ; l'écart entre les deux seuils est d'une fraction de seconde pour `D = 20 m`.
- **Diffraction d'un cylindre isolé** : pour `D = 8 m`, `T = 8 s` et `A = 1,5 m` en 30 m d'eau, `D/λ ≈ 0,08`, et l'amplitude d'inertie exacte dépasse celle de Morison (`C_M = 2`) d'environ 3 %.
- **Croissance marine** : écrivez `D = D_C + 2t`, recalculez `k/D`, `C_DS` et la section ; le facteur sur la traînée vient du diamètre et du coefficient.

## Application à un flotteur à plusieurs colonnes : lecture qualitative

Dans un modèle de semi-submersible, le tutoriel du code suggère une lecture qualitative : les **grands diamètres** (colonnes et embases) relèvent du potentiel et de la diffraction, les **éléments minces** (pontons, entretoises) de Morison, et la frontière **dépend de la période**, puisque `λ` en dépend. Ce n'est qu'une lecture : le fichier d'entrée ne fait pas de partition (le potentiel y est appliqué à tous les éléments) et le master ne tranche pas. En regard, le calcul de `D/λ` du master (un calcul, **pas** un critère de HydroDyn) place les colonnes sous les seuils sauf pour les houles courtes, et les seules embases au-delà des seuils pour les houles les plus courtes. Une embase **immergée** ne traverse pas la surface : la solution de MacCamy-Fuchs ne s'y applique pas, et aucune source présente n'en traite la diffraction. La proximité des colonnes voisines n'est traitée par aucune source.
En phase 2, l'amortissement quadratique se calibre soit par **élément** (un `C_D` par membre), soit par un coefficient **global** par degré de liberté ; la linéarisation est le pont entre les deux, non un facteur de conversion.

## Ce que le modèle ne permet pas de conclure

- **Les coefficients `C_D` et `C_A` des éléments du DeepCwind ne sont pas sourcés ici** : la définition du système n'en contient aucun, l'article de Coulling donne des coefficients globaux, et le manuel de HydroDyn n'est pas fourni. Les valeurs de cette fiche sont celles d'un cylindre isolé de la norme : **ce ne sont pas des valeurs recommandées** pour un élément du projet. L'usage de MacCamy-Fuchs dans HydroDyn et le rôle du choix potentiel / Morison par élément y sont de même non sourcés.
- Les **seuils `D/λ`** sont des indications d'ordre de grandeur, non des bornes tranchées. Aucune source ne donne de règle de transition entre Morison et diffraction.
- **Plaque de pilonnement pleine** : sans modèle dans le master. **Vibrations induites par vortex (VIV)** : le master les renvoie à un traitement ailleurs ; la fiche ne les décrit pas.
- Les coefficients **de laboratoire** (tube en U, `β_S` faible) ne se transposent pas aux `β_S` de projet ; les valeurs de projet de la J101 valent pour la mer du Nord, des diamètres modestes et la fatigue.
- Le **courant** et la houle plongeante ou déferlante, le ringing : traités dans le master, non repris ici.
- Un coefficient global de Coulling ne se convertit pas en `C_D` d'élément ; ses limites sont les grandes amplitudes et les extrêmes.
- La **vitesse** à employer dans la linéarisation de la traînée de Morison (vitesse relative ou vitesse de structure) : la RP-C205 ne la précise pas.

## Pour aller plus loin

Le master du sous-module « Morison et efforts sur éléments élancés » (chemin en tête de cette fiche) donne les dérivations, les coefficients complets, la comparaison des sources, les tables de la J101 et les effets de proximité ou de géométrie.
Sources principales : DNV-RP-C205 (édition 2014) ; DNV-OS-J101 ; B. Molin, *Offshore Structure Hydrodynamics*, chapitre 4 ; J101 édition de mai 2014 pour sa section houle ; autres sources mobilisées par le master : Coulling et la définition OC5 pour le flotteur.
Fiches voisines : [F2](F2_Houle-lineaire.md) (cinématique), [F5](F5_Hydrodynamique-potentielle.md) (potentiel et diffraction), [F10](F10_Structures-tubulaires.md) (structures tubulaires). Le [Formulaire](FORMULAIRE.md) rassemble les relations de base.
Le module [`s9gm/hydro.py`](../s9gm/hydro.py) porte, dans ses blocs *Théorie*, les relations utilisées par le code.
