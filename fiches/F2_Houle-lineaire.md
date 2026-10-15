<!-- destinations: github -->
<!-- master: Cours/OFFSHORE_Structures-Fondations/01_Houle-et-hydrodynamique-des-flotteurs.md ; nature : fiche, sélection du master (sections 0.4, 1, 2, 3 et 6.7) -->
# Fiche F2 — Houle linéaire, spectre et états de mer

**À lire avant** : phase 0b (classeur de prise en main) et phase 1 (de la table des états de mer à la liste de cas).

## Pourquoi

Un flotteur est chargé par la houle, et la phase 1 vous demande de la décrire par
un petit nombre de nombres : une hauteur significative `Hs`, une période de pic `Tp`. Sans cette fiche,
ces deux nombres sont des étiquettes de colonnes. Avec elle, vous savez ce qu'ils résument, ce qu'ils
laissent de côté, et pourquoi un spectre représente un état de mer sans décrire une réalisation en particulier.

## Minimum vital

### La houle régulière (Airy)

Une houle plane, d'amplitude `A` et de pulsation `ω = 2π/T`, dans un fluide parfait, irrotationnel, de
faible cambrure, sur un fond plat à la profondeur `h` (axe `z` vers le haut, `z = 0` à la surface au repos) :

```math
\eta=A\cos(kx-\omega t),\qquad \omega^2=g\,k\tanh kh .
```

La seconde relation est la **relation de dispersion** : la longueur d'onde `L = 2π/k` dépend de la
période et de la profondeur, pas de l'amplitude. Deux limites à connaître :

- **eau profonde** (`kh > π`, soit `h > L/2`) : `tanh kh ≃ 1`, donc `L = gT²/2π ≃ 1,56 T²` (`T` en s, `L` en m) ;
- **eau peu profonde** (`kh ≪ 1`) : la célérité tend vers `√(gh)` et la houle n'est plus dispersive.

La crête avance à la **vitesse de phase** `C_P = ω/k`. L'énergie, elle, avance à la **vitesse de groupe**
`C_G = ∂ω/∂k`, avec `C_G / C_P = 1/2 + kh / sinh 2kh` : la moitié de `C_P` en eau profonde, `C_P` en eau peu profonde.

### Ce que fait la houle sous la surface

Les vitesses de l'eau sont, en eau profonde, `u = Aω e^{kz} cos(kx − ωt)` et `w = Aω e^{kz} sin(kx − ωt)` ;
la **pression dynamique** a pour amplitude `ρ g A e^{kz}` : tout décroît comme `e^{kz}` avec la profondeur (`z < 0`).
Les trajectoires des particules sont des cercles en eau profonde, des ellipses aplaties ailleurs. Conséquence
pour un flotteur : une houle longue se ressent plus profond qu'une houle courte, et un volume immergé profondément
est peu excité au premier ordre.

### Énergie

Par unité de surface, l'énergie totale d'une houle régulière vaut `½ ρ g A²` ; elle se propage à la vitesse
`C_G`. La répartition en fréquence de cette énergie est ce que décrit le spectre.

### Une mer irrégulière : la somme de houles d'Airy

Au premier ordre, une mer est la somme d'un grand nombre de houles d'Airy de phases aléatoires :

```math
\eta(t)=\sum_i A_i\cos(\omega_i t+\theta_i),\qquad A_i^2=2\,S(\omega_i)\,\Delta\omega_i ,
```

avec `S(ω)` le **spectre de variance, simple face**, et les phases `θ_i` tirées uniformément sur `[0, 2π]`.
Les **moments** `m_n = ∫₀^∞ ωⁿ S(ω) dω` donnent les grandeurs du tableau ci-dessous, sauf `T_P`, qui vient de la pulsation du pic :

| Grandeur | Définition | Remarque |
|---|---|---|
| Variance de l'élévation | `m₀` | l'écart-type est `√m₀` |
| Hauteur significative | `Hs = 4√m₀` (par définition) | environ égale à la moyenne du tiers supérieur des vagues |
| Période de passage par zéro | `T_Z = 2π √(m₀/m₂)` | intervalle moyen entre deux passages montants par zéro |
| Période moyenne | `T₁ = 2π m₀/m₁` | différente de `T_Z` |
| Période de pic | `T_P = 2π/ω_P` | `ω_P` : pulsation du maximum de `S` |

**`T_Z`, `T₁` et `T_P` sont trois nombres différents** : la période d'un état de mer ne se donne pas sans dire laquelle.

Deux formes de spectre de mer servent partout :

- **Pierson-Moskowitz** : mer pleinement développée (fetch infini) ; `T_P ≈ 1,4 T_Z`.
- **JONSWAP** : même base, avec un **facteur de pic** `γ` : `γ = 1` redonne Pierson-Moskowitz ; plus `γ` est grand, plus
  le pic est haut et étroit. La valeur moyenne mesurée lors de la campagne qui lui a donné son nom est `γ = 3,3`.
  La norme DNV-RP-C205 propose une valeur par défaut qui dépend de `Tp/√Hs`.

### Les vagues d'une mer : Rayleigh

Si la mer est gaussienne et de bande étroite, la hauteur d'une vague suit la loi de Rayleigh :
`P(H) = 1 − exp(−H²/8m₀)`. On en tire les deux résultats à retenir :

- la plus grande vague d'un état de mer de quelques heures vaut **environ deux fois `Hs`** (le master donne l'espérance
  asymptotique du maximum) ;
- le maximum d'une **réponse linéaire** se calcule de la même façon, à partir du spectre de la réponse
  (`S_X = S·|RAO|²`, voir la fiche F5), et vaut quelques écarts-types : il ne faut pas confondre amplitude et hauteur
  crête-creux (un facteur 2).

### Les états de mer d'un site

Un site se décrit par un **diagramme de dispersion** : un tableau à deux entrées (`Hs`, `Tp`), où chaque case dit
combien d'états de mer de 3 h on y observe. Par convention, un état de mer est supposé stationnaire pendant 3 h, soit
2 920 états par an. Les valeurs de projet (centennale, par exemple) s'obtiennent en ajustant une loi de queue
et en extrapolant ; une période de retour de 100 ans est la valeur dépassée en moyenne une fois par siècle, ce qui ne
garantit pas de la rencontrer au cours d'un siècle.

## Ordres de grandeur, par la méthode

- **Longueur d'onde en eau profonde** : `L ≈ 1,56 T²`. Donnez-vous une période, calculez `L`, puis comparez à la
  profondeur : `kh > π` ? Si oui, l'eau est profonde pour cette houle.
- **Profondeur d'influence** : à la profondeur `|z| = L/2`, la cinématique est multipliée par `e^{−π} ≈ 0,04` :
  au-delà d'une demi-longueur d'onde, la houle n'agite presque plus l'eau au premier ordre (au second ordre, certains termes décroissent beaucoup plus lentement).
- **Énergie** : elle est proportionnelle à `A²`, donc à `Hs²`. Comparer deux états de mer par leur énergie
  (rapport des `Hs²`), pas par leur `Hs`.
- **Hauteur de la plus grande vague** : `≈ 2 Hs` sur un état de 3 h ; **amplitude de réponse maximale** : quelques `σ`
  de la réponse (le facteur dépend du nombre de cycles).

## Ce que le modèle ne permet pas de conclure

- La théorie d'Airy est **linéaire** : elle suppose une cambrure faible. Pour une mer très cambrée, en eau peu
  profonde ou au-dessus du niveau moyen, d'autres théories sont nécessaires : Stokes d'ordre supérieur quand le nombre d'Ursell `U_R` (qui combine la cambrure et la profondeur relative) est modéré, fonction de
  courant près de la cambrure limite ou vers `U_R ≈ 30`, théories d'eau peu profonde (Korteweg-de Vries, Boussinesq, ondes cnoïdales)
  quand `U_R` est grand, modèles d'étirement de la cinématique (Wheeler, *delta-stretching*) au-dessus du niveau moyen. Cette fiche ne les développe pas.
- Un spectre résume **un état de mer**, pas une réalisation : deux réalisations du même `(Hs, Tp, γ)` ont des extrêmes
  différents (l'écart-type du maximum vaut une fraction de `Hs`). Les phases `θ_i` sont tirées au hasard : une **graine** fixe la réalisation.
- `Hs` et `Tp` ne disent rien de la **direction** ni de l'étalement directionnel.
- Un diagramme de dispersion est une statistique d'états de 3 h. Le regroupement de ses cases en un petit nombre de
  cas représentatifs relève de la méthode de l'ingénieur ; aucune source de cette fiche ne le décrit.
- **Piège de vocabulaire** : `Hs` est défini de deux façons selon les ouvrages (tiers supérieur, ou `4√m₀`). Les deux
  coïncident pour une mer de bande étroite ; ne les mélangez pas dans un même calcul sans le dire.
- **Piège de spectre** : un spectre se donne en `ω` ou en `f`, en simple ou double face. Un spectre en `f` se
  convertit par `S_f(f) = 2π S(2πf)`.

## Pour aller plus loin

Le master du sous-module « houle et hydrodynamique des flotteurs » (chemin en tête de cette fiche) donne la
dérivation, la comparaison des deux routes (analytique et normative), les domaines de validité des théories de
houle, le spectre directionnel et les statistiques de long terme. Sources principales : B. Molin, *Offshore Structure
Hydrodynamics* ; DNV-RP-C205 (2014), *Environmental conditions and environmental loads*.
