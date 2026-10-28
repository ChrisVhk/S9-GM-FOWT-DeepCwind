<!-- destinations: github -->
<!-- master: Cours/OFFSHORE_Structures-Fondations/02_Fatigue-et-structures-tubulaires.md ; nature : fiche, sélection du master (sections 1 à 6) -->
# Fiche F9 — Fatigue de structure

**À lire avant** : phase 3 (rainflow, Miner, DEL court et long terme, courbe S-N) ; la phase 3 de S9 est à lire pour ses étapes, cette fiche en donne la théorie minimale.

## Pourquoi

Une structure soudée ne casse pas seulement sous la plus grosse vague : elle s'use par la répétition de cycles de contrainte
bien plus petits. Pour dire si la tour et les lignes tiennent leur durée de service, et quel état de mer les use le plus, il faut
enchaîner quatre gestes : **compter** les cycles d'un signal, lire la **résistance** d'un détail sur une courbe S-N, **cumuler** le
dommage, puis le **comparer** à un critère de sécurité. Le DEL (charge équivalente en dommage) est un raccourci de cette chaîne ;
il sert à comparer des cas, au prix d'hypothèses qu'il faut savoir dire. Cette fiche donne le vocabulaire, les formules et leurs limites ;
elle ne choisit aucune valeur à votre place.

## Minimum vital

### Cycles de contrainte

Pour un cycle, l'**étendue** est `Δσ = σ_max − σ_min`, l'**amplitude** `σ_a = Δσ/2` et la **moyenne** `σ_m = (σ_max + σ_min)/2`.
Une courbe S-N prend en entrée l'étendue ; la moyenne est négligée pour un assemblage soudé. Ici, tout est écrit en **étendue**.
Confondre étendue et amplitude change le dommage d'un facteur `2^m` (8 pour `m = 3`), pas la contrainte.

### Comptage rainflow : le principe

Un historique irrégulier se décompose en cycles. Le rainflow repose sur la réponse contrainte-déformation du matériau : lorsque le parcours
referme une **boucle d'hystérésis** à l'intérieur d'un plus grand cycle, cette boucle est un petit cycle à part entière, **retirée** du grand
cycle, qui se poursuit comme s'il n'avait pas été interrompu. Le comptage produit une liste d'étendues (avec leurs moyennes si on les garde).
Ce que le comptage doit produire est donc clair ; la règle d'extraction, le traitement des cycles non fermés en fin d'historique
(résidu, demi-cycles) et le seuil des petites plages relèvent de l'algorithme détaillé : norme de référence, non fournie ici.
On regroupe souvent le résultat par classes d'étendue (spectre), ou en matrice moyenne × étendue.

### Courbe S-N de dimensionnement

Une courbe S-N relie l'étendue `Δσ` au nombre de cycles `N` jusqu'à ruine (traversée de l'épaisseur par la fissure). En log-log, c'est une droite :

```math
\log N=\log\bar a-m\log\Delta\sigma ,\qquad \log\bar a=\log a-2\,s_{\log N} .
```

`log ā` est l'intersection avec l'axe `log N`, `m` l'opposé inverse de la pente, `s_{log N}` l'écart-type de `log N` : la courbe de dimensionnement est la courbe moyenne
moins deux écarts-types (probabilité de survie de 97,7 %). Cette fiche s'appuie sur la **RP-C203 de DNV, édition 2010** ; une autre édition donne d'autres paramètres
pour certaines classes : **nommez l'édition**, et lisez les valeurs dans la norme (tableau et page à citer).

- **Famille de courbes** : les détails soudés sont rangés en classes (14 classes, B1 à W3), selon la géométrie, la direction de la contrainte par rapport au cordon, la qualité de fabrication et de contrôle ; tous les nœuds tubulaires relèvent de la classe T. Il y a une courbe par classe et par milieu.
- **Pentes et coude** : deux branches, `m₁` jusqu'au coude, `m₂ = 5` au-delà ; le coude est à `10⁷` cycles dans l'air, à `10⁶` cycles en eau de mer avec protection cathodique.
- **Limite de fatigue** : sous l'étendue `S_c` du coude (`N_c` = nombre de cycles du coude : `10⁷` dans l'air, `10⁶` en eau de mer protégée), la branche à pente `m₂` s'applique ; `S_c = 10^{(log ā₂ − log N_c)/m₂}`.
- **Milieu** : trois tables de la norme, **air**, **eau de mer avec protection cathodique**, **corrosion libre**. En corrosion libre, il n'y a **plus de coude** : une seule pente `m = 3`.
- **Contrainte moyenne** : négligée pour les soudures ; une réduction existe pour le métal de base non soudé.
- **Contrainte nominale ou de point chaud** : la contrainte appliquée à la courbe doit être de même nature que celle des essais qui l'ont fournie. Entrer une contrainte de point chaud dans une courbe nominale (ou l'inverse) est une erreur de méthode.

### Effet d'épaisseur

La résistance baisse quand l'épaisseur `t` traversée par la fissure augmente. La norme modifie la contrainte :

```math
\log N=\log\bar a-m\log\!\Big(\Delta\sigma\,\big(\tfrac{t}{t_{ref}}\big)^{k}\Big),\qquad t\ge t_{ref}.
```

À `N` donné, l'étendue admissible vaut `Δσ_adm(t) = Δσ_adm(t_ref)·(t_ref/t)^k` ; la durée de vie est multipliée par `(t_ref/t)^{km}`. Pour `t < t_ref`, on pose `t = t_ref` : aucun bénéfice des faibles épaisseurs.
L'**épaisseur de référence** `t_ref` et l'**exposant** `k` se lisent dans la norme : `t_ref` vaut 32 mm pour les nœuds tubulaires (classe T) et 25 mm pour les autres soudures, et `k` dépend de la classe. Ils ne se prennent
pas d'une autre norme (les `t_ref` diffèrent).

### Cumul de dommage : Palmgren-Miner

Chaque cycle d'étendue `Δσ_i` consomme la fraction `1/N_i` de la vie. Pour `k` blocs d'étendue constante comptant `n_i` cycles :

```math
D=\sum_{i=1}^{k}\frac{n_i}{N_i}=\frac{1}{\bar a}\sum_{i=1}^{k}n_i\,(\Delta\sigma_i)^{m}\le\eta .
```

La seconde égalité suppose **une seule pente**. Avec deux branches, chaque bloc se somme sur sa branche : `D = (1/ā₁) Σ_{Δσ_i ≥ S_c} n_i Δσ_i^{m₁} + (1/ā₂) Σ_{Δσ_i < S_c} n_i Δσ_i^{m₂}`.
La règle est linéaire : l'ordre des blocs n'intervient pas. La norme demande au moins 20 blocs d'étendue pour l'acier.

### DFF : le facteur de sécurité en fatigue

Le **DFF** est un facteur de sécurité sur la vie en fatigue, lié à la durée de service, à l'accessibilité du détail et à la conséquence d'une rupture. Il s'écrit de deux façons équivalentes :
`D ≤ η` avec `η = 1/DFF` (RP-C203), ou `D_d = DFF·D_c ≤ 1` (ST-0126). Le facteur est porté par le seuil, par le dommage ou par la vie, sans que la physique change :
un DFF `x` sur un service de `L` ans exige une vie caractéristique calculée de `x·L` ans au moins. Choisir un DFF, c'est choisir un programme d'inspection.
**La fiche n'en recommande aucun** : la valeur et la durée de service sont des paramètres que vous justifiez avec la norme (édition, tableau, page, conséquences d'une rupture retenues, inspectabilité).
La ST-0126 vise les éoliennes fixes : pour la tour d'un flotteur, on ne l'emploie que **par analogie**.

### DEL : charge équivalente en dommage

Le DEL est une charge constante qui produirait, sur la même durée, le même dommage que la charge variable. **Court terme** : on remplace le résultat du comptage par un cycle unique répété à une fréquence de référence `f_e`, avec une courbe de pente `m` unique et la règle de Miner :

```math
n_e\,S_e^{\,m}=\sum_i n_i\,S_i^{\,m},\qquad S_e=\Big(\frac{\sum_i n_i\,S_i^{\,m}}{n_e}\Big)^{1/m},\qquad n_e=f_e\,T_{sim}.
```

`S_i` est une classe d'étendue, `n_i` le nombre de cycles de la classe, `T_{sim}` la durée de simulation. Le DEL dépend du couple `(f_e, m)` : deux DEL ne se comparent que si ces deux choix sont les mêmes.
**Long terme** : pour des simulations `j`, chacune représentant la part `O_j` du temps de la vie,

```math
S_{et}=\Big(\sum_j O_j\,S_{e,j}^{\,m}\Big)^{1/m},
```

tous les `S_{e,j}` étant calculés à la même `f_e`. Il n'est pas imposé que `Σ_j O_j = 1` ; le temps non représenté reçoit un dommage nul. Pour contrôler, on compare la contrainte
produite par le DEL à l'étendue admissible lue sur la courbe S-N au nombre de cycles du DEL.

## Ordres de grandeur, par la méthode

Exemples **fictifs** (calculs du master, classe D en air, `log ā₁ = 12,164`, `m₁ = 3`, `log ā₂ = 15,606`, `m₂ = 5`).

- **Pente et dommage** : si la contrainte double, le dommage par cycle est multiplié par `2^m` (8 pour `m = 3`). À 100 MPa d'étendue, `N = 10^{12,164 − 3 log 100} ≃ 1,5·10⁶` cycles ;
  la même étendue répétée un an à 3,2·10⁶ cycles épuiserait la courbe en environ cinq mois et demi.
- **Milieu** : en eau de mer protégée, la même étendue donne `N ≃ 5,8·10⁵` cycles : un facteur 2,5 de moins qu'en air.
- **Épaisseur** : à `m = 3`, un nœud de 50 mm, de `t_ref = 32` mm et `k = 0,25`, perd `1 − 0,894³ ≃ 28 %` de durée de vie par rapport à 32 mm.
- **Coude** : pour `6,3·10⁸` cycles (vingt ans à 1 Hz), la courbe à deux pentes donne environ 23,0 MPa ; une droite de pente 4 forcée par le point `(10⁷ ; 52,6)` donne 18,7 MPa. Le choix de courbe pèse, il faut le dire.
- **DEL** : 60 cycles d'étendue 100 MPa en `T_sim = 600` s, `f_e = 1` Hz (`n_e = 600`) donnent `S_e = 100·(60/600)^{1/m} = 46,4 ; 56,2 ; 63,1` MPa pour `m = 3 ; 4 ; 5`.
- **Contrôle du nombre de cycles** : une houle de période 10 s impose environ `3,2·10⁶` cycles par an, `6,3·10⁷` en vingt ans.
- **Histogramme fictif de cinq blocs** (illustration des écarts, non une méthode) : courbe à deux pentes `D ≃ 0,90` ; pente unique prolongée `D ≃ 2,96` ; cycles sous la limite négligés `D ≃ 0,13`.

## Ce que le modèle ne permet pas de conclure

- **Miner** : règle linéaire, sans mémoire de l'ordre, fondée sur des essais à amplitude constante. Elle vise la fatigue à grand nombre de cycles et des contraintes élastiques ;
  prolonger la courbe vers moins de cycles n'est pas forcément du côté de la sécurité. La somme n'ajoute aucune marge : elles viennent de `ā`, du DFF et du choix prudent de l'histogramme.
  Un dommage `D ≤ η` ne dit pas que la structure tient : il se lit avec sa courbe, son DFF et la durée cumulée.
- **Remplacer des durées de simulation par la vie** suppose un processus stationnaire et ergodique ; la sensibilité à la forme de la distribution des étendues est forte.
- **Courbe à deux pentes et limite de fatigue** : ignorer les cycles sous la limite, ou prolonger la première pente, change fortement le dommage (dans l'exemple fictif ci-dessus : pente prolongée, 3,3 fois plus ; cycles négligés, environ 7 fois moins).
- **DEL** : il ne dit rien du dommage final de la section ; il suppose une courbe à **une** pente (la courbe réelle en a deux) ; il perd la **concomitance** des charges ; il dépend de la première **fréquence propre** de la fondation
  et de `(f_e, m)` ; en prédimensionnement, il n'est acceptable que si une composante de charge domine.
- **Somme de DEL de deux composantes** : l'additionner suppose que les deux composantes agissent en phase, hypothèse que la chaîne du DEL n'écrit pas ; aucune source du master ne tranche entre somme des DEL et DEL de la combinaison. La vérifier fait partie du travail du projet (phases 3 et 5).
- **Extrapolation** : un DEL, un dommage ou une durée de vie ne valent que pour les états de mer simulés, leur durée, la courbe, l'édition et l'épaisseur de référence choisis. Le temps hors plage simulée n'est pas compté.
- **Comptage** : le principe est donné ci-dessus ; son algorithme complet n'est pas dans cette fiche.

## Pour aller plus loin

- Le master du sous-module « fatigue et structures tubulaires » (chemin en tête) : sections 1 (cycles, comptage), 2 (courbes S-N, tables 2-1, 2-2 et 2-3 de l'édition 2010 : **tableau et page à citer**), 3 (effet d'épaisseur), 4 (Miner), 5 (DFF, ST-0126, table 4-20), 6 (DEL court et long terme).
- **DNV-RP-C203, édition 2010** : courbes S-N par classe de détail, milieu, effet d'épaisseur, formes de Weibull. **DNVGL-ST-0126** (supports d'éoliennes **fixes**, utilisée par analogie pour un flotteur) : critère `DFF·D_c ≤ 1` et table des DFF selon la zone et l'accessibilité.
- Fiche [F10](F10_Structures-tubulaires.md) : d'où vient la contrainte de point chaud (nœuds tubulaires, concentration de contrainte).
- Guide du classeur distribué en séance : [`../annexes/atelier_tour/README.md`](../annexes/atelier_tour/README.md).
- Formulaire : [`FORMULAIRE.md`](FORMULAIRE.md).
