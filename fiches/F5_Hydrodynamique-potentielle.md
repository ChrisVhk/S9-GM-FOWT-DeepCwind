<!-- destinations: github -->
<!-- master: Cours/OFFSHORE_Structures-Fondations/01_Houle-et-hydrodynamique-des-flotteurs.md ; nature : fiche, sélection du master (sections 4 à 8) -->
# Fiche F5 — Hydrodynamique potentielle d'un flotteur

**À lire avant** : phase 2 (lâchers libres, périodes propres, sensibilités) ; utile dès que vous lisez un fichier de coefficients hydrodynamiques (`.1`, `.3`, `.hst`).

## Pourquoi

Le modèle de flotteur d'OpenFAST ne calcule pas lui-même la façon dont l'eau pousse sur la coque : il lit des
**coefficients** produits par un code de diffraction-rayonnement (WAMIT, ou son équivalent libre NEMOH). Sans cette fiche,
ces fichiers sont des colonnes de nombres. Avec elle, vous savez ce que chaque colonne représente, ce qu'une période
propre mesurée dans un lâcher doit à ces coefficients, et ce que la théorie potentielle ne sait pas faire.

## Minimum vital

### Trois problèmes, un seul fluide

Le fluide est parfait et irrotationnel, la houle est faible : le potentiel de vitesses se décompose en trois parties,
que l'on résout séparément pour une pulsation `ω` donnée :

```math
\varphi=\varphi_I+\varphi_D+\varphi_R .
```

- `φ_I` : la **houle incidente**, celle de la fiche F2, comme si le corps n'était pas là ;
- `φ_D` : le potentiel **diffracté**, le corps étant tenu **fixe** : la coque perturbe la houle ;
- `φ_R` : le potentiel **rayonné**, le corps oscillant dans une eau sans houle, un degré de liberté à la fois.

### Ce que donne chaque problème

| Problème | Ce qu'il fournit | Forme |
|---|---|---|
| Incidente + diffraction | l'**excitation** `f_j(ω, β)` : l'effort de houle sur le corps fixe, par degré de liberté `j` et par cap `β` | complexe : module et phase |
| Rayonnement | la **masse ajoutée** `A_{jk}(ω)` et l'**amortissement de rayonnement** `B_{jk}(ω)` | réels, matrices `6 × 6` |

L'excitation contient deux parts : l'effort **de Froude-Krylov** (la pression de la houle non perturbée, intégrée sur la coque)
et l'effort **de diffraction** (la correction due à la présence du corps). Si le corps est petit devant la
longueur d'onde, la diffraction est négligeable et Froude-Krylov suffit ; sinon la diffraction compte. Le critère usuel
est un diamètre supérieur à environ `L/6`.

Propriétés à retenir sur `A` et `B` : les deux matrices sont **symétriques** ; les termes diagonaux de `B` sont positifs
(les ondes rayonnées emportent de l'énergie) ; les termes diagonaux de `A` peuvent, dans certains cas (près de la
surface, ou près d'une résonance de bassin entre deux coques), devenir **négatifs**. Par symétrie bâbord-tribord,
cavalement, pilonnement et tangage n'excitent ni embardée, ni roulis, ni lacet.

### L'équation du mouvement en fréquence

Pour une houle régulière de pulsation `ω`, avec `M` la matrice de masse du corps, `C` la raideur hydrostatique et `K_A`
celle de l'ancrage, le mouvement complexe `x` vérifie :

```math
\Big[-\omega^2\big(\mathbf M+\mathbf A(\omega)\big)-i\,\omega\,\mathbf B(\omega)+\mathbf C+\mathbf K_A\Big]\,\vec x=\vec f(\omega,\beta).
```

C'est un oscillateur à six degrés de liberté couplés dont la masse et l'amortissement dépendent de la fréquence.
**Le signe devant `iωB` dépend de la convention de temps** : `−` avec une dépendance en `e^{−iωt}`, `+` avec `e^{+iωt}`.
Les fichiers de WAMIT sont en `e^{+iωt}` (le chapitre ne l'écrit pas : on le déduit du signe de leur terme d'amortissement) ; avant de combiner des
coefficients et des phases d'origines différentes, vérifiez la convention de chacun.

### La RAO

La **RAO** (*Response Amplitude Operator*) est la réponse complexe d'un degré de liberté par mètre d'amplitude de
houle : `x_j = A · RAO_j(ω, β)`. Son module est la réponse par mètre d'amplitude, sa phase est relative à
l'élévation de la houle incidente **à l'origine du repère**. En mer irrégulière, pour une houle d'une seule direction :

```math
S_{X_j}(\omega)=S(\omega)\,\big|\mathrm{RAO}_j(\omega,\beta)\big|^2,\qquad \sigma_{X_j}=\sqrt{m_{j0}},
```

où `m_{j0}` est l'aire du spectre de réponse. Les maxima d'une réponse de bande étroite suivent Rayleigh, comme les
vagues (fiche F2) : le maximum sur une durée donnée s'exprime en quelques `σ`.

### Périodes propres

La pulsation propre d'un degré de liberté `j` annule le déterminant de l'équation précédente, au premier ordre `ω_j = √(raideur / inertie totale)`, c'est-à-dire :

```math
T_j = 2\pi\sqrt{\frac{M_{jj}+A_{jj}(\omega_j)}{C_{jj}+K_{jj}}} .
```

La masse ajoutée dépend de `ω` : **la période propre doit être cherchée à la fréquence à laquelle on a pris `A`**
(itération, ou intersection de deux courbes). Pour le pilonnement, `C₃₃ = ρ g S_f` (aire de flottaison `S_f`) ; pour le
tangage, `C₅₅ = ρ g V · GM_L`. L'ancrage ajoute sa raideur `K_{jj}` : très faible en cavalement (les périodes propres
horizontales sont très au-dessus de la bande de houle).

### Lire une RAO comme un oscillateur

Pour un seul degré de liberté, `M ẍ + B ẋ + K x = F`, avec `ω₀ = √(K/M)` et le taux d'amortissement `ζ = B/(2√(KM))` :

```math
x=\frac{F_0}{K}\,\frac{1}{1-\omega^2/\omega_0^2-2i\zeta\,\omega/\omega_0}.
```

Trois régimes : **raide** (`ω ≪ ω₀`) : `x ≃ F₀/K`, le flotteur suit l'effort ; **mou** (`ω ≫ ω₀`) : `|x| ≃ F₀/(Mω²)`, le
flotteur ne bouge plus ; **résonance** : amplification `1/(2ζ)`. À amortissement faible, la résonance est étroite, et c'est
l'amortissement qui borne le mouvement. Un lâcher libre donne la période propre amortie (`ω₀√(1−ζ²)`) et, par la
décroissance par cycle `e^{−2πζ}`, l'amortissement : c'est ce que fait la phase 2.

### Du fréquentiel au temporel

OpenFAST intègre en temps. Pour cela, l'effort de rayonnement s'écrit avec une **mémoire** (l'eau garde trace du
mouvement passé) :

```math
\sum_j\Big\{\big[M_{ij}+A_{ij}(\infty)\big]\ddot X_j+\int_{-\infty}^{t}\dot X_j(\tau)\,R_{ij}(t-\tau)\,d\tau+C_{ij}X_j\Big\}=F_i(t),
```

avec `A(∞)` la masse ajoutée à fréquence infinie et `R` la **fonction de retard**, reliée à `B(ω)` par
`R_{ij}(t) = (2/π) ∫₀^∞ B_{ij}(ω) cos ωt dω`. Deux conséquences : `B(ω)` de 0 à l'infini détermine `R`, donc `A(ω) − A(∞)` ;
et la qualité d'un calcul temporel dépend de la plage de fréquences fournie dans les fichiers.

### Les fichiers de WAMIT

| Fichier | Contenu |
|---|---|
| `.1` | période, `i`, `j`, masse ajoutée et amortissement adimensionnés |
| `.2` / `.3` | période, cap, `i`, module, phase, parties réelle et imaginaire de l'excitation (deux méthodes de calcul, qui se contrôlent l'une l'autre) |
| `.4` | idem pour les mouvements (RAO) |
| `.hst` | matrice de raideur hydrostatique |

Les grandeurs y sont **adimensionnées** (par `ρ`, `g`, une longueur de référence) : relire la définition avant de comparer à
un résultat en unités physiques. Les périodes y sont repérées par `2π/ω` ; une période nulle désigne `ω = ∞`, une
période négative `ω = 0`.

## Ordres de grandeur, par la méthode

- **Période propre d'un degré de liberté** : calculez `C_{jj}` (hydrostatique ou ancrage), estimez `M_{jj}` et la masse
  ajoutée (lue dans le fichier `.1` à la bonne fréquence), puis `T = 2π√(inertie/raideur)`.
  Le résultat fixe où chercher la résonance dans le signal d'un lâcher.
- **Facteur d'amplification à la résonance** : `1/(2ζ)` ; avec un amortissement de quelques pour cent, l'amplification est
  de l'ordre de la dizaine.
- **Pic de la RAO de pilonnement** : à la période propre, avec une hauteur de l'ordre de `1/(2ζ)` si l'excitation y est du même
  ordre qu'ailleurs ; aux houles très longues, la RAO tend vers 1 (le flotteur suit la surface).
- **Où est la houle** : comparez la période propre à la bande de périodes de la houle courante (fiche F2). Un mouvement propre
  éloigné de cette bande est peu excité ; un mouvement propre dans la bande se lit sur la RAO.

## Ce que le modèle ne permet pas de conclure

- **Tout est linéaire** : excitation et réponse proportionnelles à l'amplitude de houle, amortissement indépendant de l'amplitude. La
  théorie potentielle n'inclut **ni la viscosité** (tourbillons autour des colonnes et entretoises, traînée) **ni les
  efforts du second ordre** (dérive moyenne, dérive lente, QTF). Pour les éléments élancés, on utilise un modèle de Morison ; des modèles dits « duals »
  combinent diffraction-rayonnement et éléments de Morison.
- Les **périodes propres horizontales** d'un flotteur amarré sont très longues : un lâcher court ne les mesure pas.
- Un coefficient lu dans un fichier est celui **de la maille et de la plage de fréquences** du calcul d'origine. Un fichier
  de coefficients ne dit pas comment il a été calculé (maillage, profondeur, cap).
- **Conventions** : convention de temps, signe de la phase, cap de la houle (0° ou 180°), sens des axes, unités des
  fichiers adimensionnés. Une RAO ou une phase mal interprétée est l'erreur la plus fréquente.
- Les fichiers WAMIT sont lus par HydroDyn d'OpenFAST ; **la façon dont HydroDyn les traite** (interpolation en fréquence, extrapolation
  de `A(∞)`, calcul de la fonction de retard) n'est pas décrite dans le master ni dans cette fiche : voir la
  documentation de l'outil.
- Les relations de Kramers-Kronig, qui lient `A(ω)` et `B(ω)`, ne sont pas développées ici.

## Pour aller plus loin

Le master du sous-module « houle et hydrodynamique des flotteurs » (chemin en tête de cette fiche) donne les définitions
détaillées, la comparaison des conventions entre sources, les relations de Haskind, les limites du potentiel et l'écart entre
modèles. Sources principales : B. Molin, *Offshore Structure Hydrodynamics* ; manuel WAMIT, chapitre 4 ; DNV-RP-C205
(2014) ; rapport du projet BEL-Float (VUB, 2025) pour l'usage de NEMOH et de WAMIT par OpenFAST.
