<!-- destinations: github, word -->
# Fiche F1 — Aérodynamique et régulation de l'éolienne

**À lire avant** : phase 0 (prise en main OpenFAST, cas F01-F02).

## Pourquoi

Les cas `F01`/`F02` du tutoriel `prise_en_main/` font tourner une éolienne à vitesse de vent
imposée et vous donnent en sortie `RotSpeed`, `GenPwr`, `TwrBsMyt`. Sans ces notions, ces
nombres sont des courbes sans signification : vous ne pouvez ni les prévoir avant de lancer le
calcul, ni juger s'ils sont physiquement plausibles une fois le calcul fini. C'est le contrôle le
plus simple et le plus rapide que vous ferez sur chaque cas de ce projet.

## Minimum vital

**Théorie du disque actuateur (Betz)** : un rotor extrait une puissance
`P = 1/2 · ρ · A · V³ · Cp(λ, β)`, où `A = πR²` est la surface balayée, `V` la vitesse du vent
non perturbé, `Cp` le coefficient de puissance (limite théorique de Betz : `Cp,max = 16/27 ≈
0,593`, jamais atteinte en pratique — pertes de bout de pale, trainée de profil). `Cp` dépend de
deux paramètres pilotés par la machine :
- **λ (TSR, tip-speed ratio)** = `Ω·R / V` (Ω en rad/s) — rapport entre la vitesse de bout de
  pale et la vitesse du vent ;
- **β** — l'angle de calage des pales (pitch).

La poussée axiale (ce qui charge la tour en flexion) suit la même logique :
`T = 1/2 · ρ · A · V² · Ct(λ, β)`, avec `Ct` du même ordre de grandeur que `Cp` (typiquement
`Ct ≈ 0,7-0,9` en-dessous du régime nominal).

**Les zones de régulation** d'une machine à vitesse variable, pitch variable (c'est le cas de la
NREL 5 MW de ce projet) ; Jonkman 2009 en distingue cinq (1, 1½, 2, 2½, 3), dont les deux
premières ne concernent que le tout petit vent (démarrage) et ne sont pas mobilisées dans ce
tutoriel. Les trois qui comptent ici :
- **Region 2** (entre cut-in et le vent nominal) : pitch fixe (souvent proche de 0°), le couple
  générateur est piloté pour maintenir `λ` à sa valeur optimale `λ*` (celle qui maximise `Cp`) —
  la vitesse de rotation suit donc le vent : `Ω(V) = λ*·V/R`.
- **Region 3** (au-dessus du vent nominal) : la puissance est plafonnée à la puissance nominale,
  `Ω` est maintenue constante (régime nominal), c'est le **pitch** qui augmente pour réduire `Cp`
  et évacuer l'excès de puissance.
- **Region 2½** (transition, zone étroite) : la loi de Region 2 ferait dépasser la vitesse de
  rotation nominale avant même d'atteindre le vent nominal ; cette région limite donc le couple
  pour plafonner `Ω` à sa valeur nominale un peu plus tôt — chez Jonkman, la raison d'être
  explicite est de limiter la vitesse de bout de pale (et le bruit associé), pas seulement le
  couple générateur.

## Ordre de grandeur sur la NREL 5 MW (DeepCwind et monopile OC3)

| Grandeur | Valeur | Source |
|---|---|---|
| Rayon rotor R | 63 m | Jonkman 2009, Tab. 1-1 (diamètre 126 m ; valeur précise 62,94 m précône inclus) |
| Puissance nominale | 5 MW | idem |
| Vitesse de rotation nominale | 12,1 tr/min (≈ 1,267 rad/s) | idem |
| Vitesse de vent nominale | 11,4 m/s | idem |
| Cut-in / cut-out | 3 m/s / 25 m/s | idem |
| λ* (TSR optimal, Region 2) | 7,55 | Jonkman 2009, §7.2 p.26 et Tab. 7-2 p.27 |
| Cp maximal (à λ*, pas à 0°) | 0,482 | idem |

**Méthode** : en Region 2, `Ω attendu = λ*·V/R` (rad/s), à convertir en tr/min (`× 60/(2π)`).
Cette loi ne s'applique que tant que `Ω` calculé reste en dessous du régime nominal — **à vous de
calculer à quelle vitesse de vent ce régime est atteint**, et de comparer ce résultat au vent
nominal (11,4 m/s) : si les deux diffèrent, c'est que la Region 2½ s'intercale entre les deux,
avant la Region 3.

## Confrontation OpenFAST

Pour le cas F01 du tutoriel (vent constant, Region 2) : calculez `Ω` attendu avec la méthode
ci-dessus, et comparez-le au `RotSpeed` observé en régime établi. Un écart tolérable est attendu
(la loi de couple réelle du contrôleur ne colle pas parfaitement à `λ*` à toutes les vitesses), et
il y a un régime transitoire au démarrage à écarter de la moyenne (cf `outils/lire_outb.py`,
option `t_min`). Si l'écart dépasse ~15-20 %, suspectez d'abord le transitoire inclus dans la
moyenne, pas une erreur de configuration.

Pour `TwrBsMyt` (moment fléchissant en pied de tour) : estimez la poussée
`T = 1/2 · ρ · A · V² · Ct` (air `ρ ≈ 1,225 kg/m³`, `Ct ≈ 0,8` en Region 2 à défaut de valeur
précise tirée du modèle) puis `TwrBsMyt ≈ T × (H_moyeu − TowerBsHt)` : `TwrBsMyt` est le moment **au pied de la tour**,
dont la hauteur `TowerBsHt` (à lire dans `config_elastodyn.dat`) est le point de référence du bras de
levier — pas le niveau de la mer. Comparez à ±20 % : le modèle complet
inclut en plus le poids propre de la nacelle/tour en flexion et la variation de `Ct` avec `λ`.

**Fréquence 1P** : une pale fait un tour en `1/f` ; la fréquence de rotation est
`f₁ₚ = RotSpeed / 60` (Hz, `RotSpeed` en tr/min). Chaque pale traverse à chaque tour le même
cisaillement de vent, le même sillage de tour et subit la même gravité : ses moments d'emplanture
(`RootMyb1`, hors plan ; `RootMxb1`, dans le plan, surtout par la gravité) oscillent à 1P. La tour, elle, ne voit que la somme des trois pales, déphasées de 120° :
les harmoniques qui ne sont pas multiples de 3 se compensent, il reste 3P (bloc Théorie du §6 de
`seances/0a/README.md`).

## Limites

- La théorie du disque actuateur est **1D et stationnaire** : elle ignore la rotation du
  sillage, les pertes de bout/pied de pale, les effets tridimensionnels le long de la pale. Le
  BEM (Blade Element Momentum), utilisé par AeroDyn, les ajoute mais reste lui-même une théorie
  d'ingénieur calée empiriquement (facteurs de correction de Prandtl, Glauert), pas une
  simulation CFD.
- Les cas `F01-F05` de ce tutoriel tournent en **BEMT quasi-stationnaire (`Wake_Mod=1`), pas en
  DBEMT (`Wake_Mod=2`)** — le modèle dynamique du sillage n'est pas actif. En vent turbulent ou
  en régime transitoire rapide (échelon de F02), la réponse aérodynamique instantanée peut
  différer d'un calcul DBEMT ou d'une mesure réelle (cf `tutorials/prise_en_main/README.md`).
- Les coefficients `Cp`/`Ct` utilisés ici sont des ordres de grandeur usuels pour ce type de
  machine, **pas des valeurs tirées d'une table `Cp(λ,β)` du modèle** — une vérification plus
  fine nécessiterait d'extraire cette table (sortie `RtAeroCp`/`RtAeroCt` d'AeroDyn).

## Pièges

- Confondre `Ω` en rad/s et en tr/min dans le calcul de `λ` (facteur `60/(2π) ≈ 9,55`).
- Appliquer la loi Region 2 (`Ω = λ*·V/R`) au-delà du vent où elle fait atteindre le régime
  nominal : `Ω` ne continue pas à croître avec `V` au-delà de ce point, elle est plafonnée dès la
  Region 2½ — qui commence **avant** le vent nominal (11,4 m/s, début de la Region 3), pas à
  partir de lui.
- Moyenner `RotSpeed`/`GenPwr` sur toute la durée simulée, transitoire de démarrage inclus — biais
  systématique signalé dans `outils/lire_outb.py` (argument `t_min`).
- Oublier que `Ct` n'est pas constant : il décroît avec `λ` au-delà de l'optimum — une estimation
  de poussée à `Ct = 0,8` devient fausse en Region 3 (le pitch réduit fortement `Ct`).

## Auto-test

1. Pour `V = 9 m/s`, avec `λ* = 7,55` et `R = 63 m`, quelle vitesse de rotation `Ω` (en tr/min)
   attendez-vous en Region 2 ?
2. L'éolienne tourne en Region 3 à puissance nominale 5 MW et vitesse nominale 12,1 tr/min. Quel
   couple générateur (en kN·m) cela représente-t-il ? (`P = T_gen · Ω`, `Ω` en rad/s)
3. Avec `ρ = 1,225 kg/m³`, `R = 63 m`, `Ct = 0,8`, estimez la poussée du rotor `T` (en kN) à
   `V = 10 m/s`, puis l'ordre de grandeur du moment `TwrBsMyt` attendu avec une hauteur de moyeu
   de 90 m et un pied de tour à `TowerBsHt` = 10 m au-dessus du niveau de la mer.

## Sources

- J. Jonkman, S. Butterfield, W. Musial, G. Scott, *Definition of a 5-MW Reference Wind Turbine
  for Offshore System Development*, NREL/TP-500-38060, 2009 — paramètres de la machine (R,
  puissance/vitesse nominales, cut-in/out, λ* et Cp max §7.2 et Tab. 7-2).
- M. O. L. Hansen, *Aerodynamics of Wind Turbines*, Routledge — théorie du disque actuateur et
  BEM (relation de référence, formule, pas de reproduction de texte).
- J. F. Manwell, J. G. McGowan, A. L. Rogers, *Wind Energy Explained*, Wiley — définitions
  TSR/Cp/Ct et zones de régulation (relation de référence).
- `models/oc4_rtest/5MW_Baseline/ServoData/DISCON/DISCON.F90` (`VS_Rgn2K`) — loi de couple de
  Region 2 effectivement utilisée dans ce dépôt ; `models/oc4_rtest/5MW_OC4Semi_WSt_WavesWN/
  NRELOffshrBsline5MW_OC4DeepCwindSemi_ServoDyn.dat` pour les paramètres ServoDyn du cas flottant
  de référence.
