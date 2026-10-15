<!-- destinations: github -->
<!-- master: Cours/OFFSHORE_Structures-Fondations/01_Houle-et-hydrodynamique-des-flotteurs.md ; nature : fiche, sélection du master (section 4) -->
# Fiche F3 — Hydrostatique d'un flotteur

**À lire avant** : phase 0b, étape 3.3 (raideurs hydrostatiques à la main) ; utile en phase 2 (périodes propres).

## Pourquoi

Un flotteur reste droit et à son tirant d'eau parce que l'eau le rappelle : s'il s'enfonce ou s'incline, la poussée change
et le rappelle vers l'équilibre. Les **raideurs hydrostatiques** disent de combien. Sans elles, vous ne pouvez ni prévoir les
périodes propres de la phase 2, ni juger si le fichier de coefficients hydrostatiques du modèle est cohérent, ni expliquer
l'écart entre votre calcul à la main et celui de l'outil.

## Minimum vital

### Ce que l'hydrostatique linéarisée calcule

Seule la pression hydrostatique `p = p₀ − ρ g z` est prise en compte. On cherche la **variation de la poussée** (force et
moment) quand le corps se déplace un peu dans un ou plusieurs de ses six degrés de liberté, les moments étant pris au centre
de gravité `G`.

- Un corps **totalement immergé** subit la poussée d'Archimède `ρ g ∀`, appliquée au centre de carène `B`, fixe dans le repère
  du corps : si aucune charge extérieure n'agit, il ne reste droit que si `B` est au-dessus de `G`.
- Un corps **qui traverse la surface libre** se ferme par le plan de flottaison : ce qui change quand il bouge est le volume
  mouillé et la position de `B`. D'où des termes qui font intervenir l'**aire** et les **inerties de la flottaison**.

### Les raideurs

Notons `S_WP` l'aire de flottaison, `∀` le volume déplacé, `I_X`, `I_Y` ses moments du premier ordre et `I_XX`, `I_YY`, `I_XY` ses
moments du second ordre (`I_XY = −∬ X Y dS`). La raideur hydrostatique est notée `C_ij` dans ce projet (`K_ij` chez Molin).

```math
C_{33}=\rho g\,S_{WP},\qquad C_{44}=\rho g\big(\forall\,\overline{GB}+I_{YY}\big),\qquad C_{55}=\rho g\big(\forall\,\overline{GB}+I_{XX}\big),
```

```math
C_{34}=\rho g\,I_Y,\qquad C_{35}=-\rho g\,I_X,\qquad C_{45}=\rho g\,I_{XY}.
```

- `C₃₃` se lit comme un **poids par mètre d'enfoncement** : la force verticale qu'il faut pour enfoncer le flotteur d'un mètre.
- `C₄₄` (roulis) et `C₅₅` (tangage) sont d'autant plus faibles que les colonnes sont proches de l'axe et que `G` est haut.
- `G B̄` est une **distance algébrique** : si `G` est au-dessus de `B`, `G B̄` est négatif. Un flotteur peut rester stable avec
  `G` au-dessus de `B` si ses hauteurs métacentriques sont positives (`∀ G B̄ + I_YY = ∀ GM_α`).
- Avec la symétrie bâbord-tribord, `I_XY = 0` ; pour un flotteur symétrique, `C₃₄ = C₄₅ = 0`.
- La matrice complète `6 × 6` n'a de termes non nuls que sur les lignes et colonnes 3, 4 et 5.

### Deux écritures du même objet

Les outils et les normes écrivent le terme de poids à part. Avec `S₁`, `S₂` (moments du premier ordre), `S₁₁`, `S₂₂`, `S₁₂` (du second
ordre) de la flottaison, `V` le volume déplacé, `z_B` et `z_G` les cotes de `B` et de `G`, `M` la masse :

```math
C_{44}=\rho g\big(S_{22}+V z_B\big)-M g z_G,\qquad C_{55}=\rho g\big(S_{11}+V z_B\big)-M g z_G .
```

Pour un flotteur libre (poids égal à la poussée, `M = ρ V`), les deux écritures **coïncident** : `ρ g V (z_B − z_G) = ρ g ∀ G B̄`. La
seule différence est la **présentation du poids** : résumé dans `G B̄` d'un côté, écrit à part (`− M g z_G`) de l'autre. Pour un
flotteur libre, `C₄₄ = ρ g V GM_T` et `C₅₅ = ρ g V GM_L`, avec `GM = S/V + z_B − z_G` (`S₂₂` pour le roulis, `S₁₁` pour le tangage).

### L'ancrage, à part

L'ancrage ajoute **sa propre raideur** `K_A`, qui s'écrit à côté de `C` dans l'équation du mouvement : elle ne fait pas partie de
la matrice hydrostatique. Un code de diffraction-rayonnement peut la recevoir par une matrice extérieure ; pour une ligne donnée,
elle se calcule à part (le comportement des lignes d'ancrage relève d'un autre sous-module du master).

### Un moment extérieur, des réservoirs, de grandes inclinaisons

- **Assiette sous un moment pur** `C_y` (avec `C₃₄ = C₄₅ = 0`) : l'angle de tangage vaut `−C₃₃ C_y / (C₃₃ C₅₅ − C₃₅²)` (`C_y` : le moment extérieur ; à ne pas confondre avec une raideur). Le **centre de
  flottaison** (point de la flottaison qui ne bouge pas) est le centroïde de la flottaison.
- **Réservoirs à surface libre** : chacun **diminue** les raideurs de roulis et de tangage de `ρ_n g` fois l'inertie de sa surface
  libre interne ; cloisonner un réservoir améliore la stabilité.
- **Grandes inclinaisons** : la raideur linéarisée ne suffit plus ; on redétermine la flottaison à chaque angle et on trace la courbe du
  bras de rappel `GZ(α)`. La hauteur métacentrique est sa pente à l'origine.

## Ordres de grandeur, par la méthode

- **`C₃₃`** : additionnez les aires des seules colonnes qui traversent la flottaison, multipliez par `ρ g`. C'est le poids que
  porte l'eau par mètre d'enfoncement.
- **`C₅₅` et `C₄₄`** : calculez l'inertie de la flottaison (`I_XX` ou `I_YY`), puis le terme `∀ G B̄` (ou `V z_B − M z_G / ρ`). Si `G` est au-dessus
  de `B`, ce second terme est négatif alors que l'inertie est positive : écrivez les deux termes séparément avant de les ajouter.
- **Période propre** : `T = 2π √(inertie totale / raideur)` ; pour le pilonnement, `T₃ = 2π √((M + A₃₃) / C₃₃)` avec la masse ajoutée
  `A₃₃` à la fréquence de la période (voir la fiche F5).
- **Comparer à un fichier de coefficients** : relisez d'abord ce que le fichier contient (poussée seule ? poids compris ? unités ?
  adimensionnement ?) avant de conclure à un écart.

## Ce que le modèle ne permet pas de conclure

- **Petits déplacements seulement** : tout ce qui précède suppose des déplacements et des angles petits, autour d'axes fixes. Au-delà,
  il faut la courbe `GZ(α)`.
- **Piège de signe** : les deux documents de référence du flotteur du projet (la définition OC5 et le rapport VUB) donnent des
  raideurs de roulis et de tangage **négatives** ; OC5 précise qu'il s'agit des termes de **poussée seule, sans le poids** : il faut y
  ajouter le terme de poids pour obtenir la raideur de rappel totale. **Ne concluez pas à l'instabilité d'un flotteur sur ce seul signe.**
- **L'ancrage** : on ne peut pas déduire sa contribution à la raideur de pilonnement ou de roulis-tangage d'un cas à partir du seul rapport VUB
  (unités non écrites, définition de la ligne absente) ; la définition OC5, elle, donne la géométrie et les caractéristiques des lignes plutôt qu'une matrice.
- **Second ordre** : des termes quadratiques en les angles couplent pilonnement, roulis, tangage et lacet ; ils peuvent être à l'origine
  d'instabilités paramétriques. Ils ne sont pas traités ici.
- **Le poids** : la raideur de rappel dépend de la masse et de la position de `G` (terme `− M g z_G`). Pour la matrice de masse, une
  erreur de rayon de giration est la source d'erreur la plus courante des programmes (DNV).

## Pour aller plus loin

Le master du sous-module « houle et hydrodynamique des flotteurs » (chemin en tête de cette fiche, section 4) donne les démonstrations,
la comparaison des trois écritures (Molin, DNV, WAMIT), l'assiette sous moment, les carènes liquides et la stabilité aux grands angles.
Sources principales : B. Molin, *Offshore Structure Hydrodynamics*, annexe B ; DNV-RP-C205 (2014), § 7.2 ; manuel WAMIT, chapitre 4.
