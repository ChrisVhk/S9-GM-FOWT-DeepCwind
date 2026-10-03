<!-- destinations: github -->
# Séance 0a — lundi (3 h)

Déroulé pas à pas. L'énoncé complet est dans [`../../ENONCE.md`](../../ENONCE.md) (phase 0,
séance 0a) — ce document-ci en est la version « pas à pas » pour la séance.

**À lire avant la séance** : fiche F1 — Aéro-régulation ([`../../fiches/F1_Aero-regulation.md`](../../fiches/F1_Aero-regulation.md)).

## 1. Installation (environ 20 min)

Suivez [`../../INSTALLATION.md`](../../INSTALLATION.md), sections 1 et 2 :
- cloner le dépôt, lancer `bash env/install.sh` ;
- vérifier `openfast -v` → doit afficher `OpenFAST-v5.0.0` ;
- compiler le contrôleur : `bash scripts/build_discon.sh`.

**Si ça ne marche pas** : voir « En cas d'échec » dans `INSTALLATION.md`. Notez l'erreur exacte,
continuez avec un camarade en binôme pour la suite, et terminez l'installation après la séance
(avant la séance 0b, au plus tard en salle C09).

## 2. Anatomie d'un cas OpenFAST (environ 20 min, en binôme)

*D'après le tutoriel OpenFAST Quickstart du LHEEA (Apache-2.0), adapté — voir
[`../../tutorials/lheea/NOTICE`](../../tutorials/lheea/NOTICE).*

OpenFAST est un code « glue » : il couple des modules indépendants (ElastoDyn pour la structure,
AeroDyn pour l'aérodynamique, HydroDyn pour l'hydrodynamique, ServoDyn pour le contrôle, MoorDyn
pour l'ancrage…), chacun avec son propre fichier de configuration. Un seul fichier pilote tout :
`main.fst`.

Ouvrez `tutorials/lheea/01_TowerStructure/1_Configuration/main.fst` dans un éditeur de texte.
Trois sections à repérer :
- **SIMULATION CONTROL** : `TMax` (durée), `DT` (pas de temps), `InterpOrder`.
- **FEATURE SWITCHES AND FLAGS** : quels modules sont actifs (`CompElast`, `CompInflow`,
  `CompAero`, `CompHydro`, `CompServo`, `CompMooring`…). Pour ce premier cas, seul `CompElast=1`
  est actif — tout le reste est éteint.
- **INPUT FILES** : le fichier de configuration de chaque module actif, en chemin relatif.

Pour chaque section, notez ce que vous changeriez pour une nouvelle étude (`TMax`, le pas de
temps, les degrés de liberté actifs, les fichiers d'entrée, la liste de sorties `OutList`) et ce
qui reste identique d'un cas à l'autre dans ce tutoriel.

## 3. Cas LHEEA 01 — dynamique structurelle de la tour seule (environ 20 min)

*D'après le tutoriel OpenFAST Quickstart du LHEEA (Apache-2.0), §1, adapté — voir
[`../../tutorials/lheea/NOTICE`](../../tutorials/lheea/NOTICE).*

### Bloc Théorie

1. **Question physique** — Avant d'ajouter des charges complexes (vent, houle) à un modèle,
   comment vérifier que sa description mécanique seule (masse, raideur) est correcte ?
2. **Modèle** — la tour est lâchée depuis un déplacement initial (`TTDspFA`), sans aucune charge
   extérieure ni module aérodynamique actif (`CompAero=0`) : seule la raideur structurelle du
   système la rappelle vers l'équilibre. **Domaine de validité** — lisez `config_elastodyn.dat`
   avant de conclure, section DEGREES OF FREEDOM : les modes de flexion de pale (`FlapDOF1/2`,
   `EdgeDOF`) et de tour (`TwFADOF1/2`, `TwSSDOF1/2`) sont actifs, ainsi que la rotation libre du
   générateur (`GenDOF`) et le lacet (`YawDOF`) ; mais **la plateforme est totalement bloquée**
   (les 6 `Ptfm*DOF` à `False`) et le calage de pale est fixe (`PitchDOF=False`). Sans charge
   aérodynamique ni condition initiale sur les autres DOF, c'est le déplacement initial de la tour
   qui domine la réponse observée.
3. **Ordre de grandeur attendu** — la méthode : repérer la période d'oscillation sur la courbe du
   déplacement du sommet de tour, en déduire la fréquence propre ; la comparer à l'ordre de
   grandeur habituel pour une tour d'éolienne de cette taille (quelques dixièmes de Hz).
4. **Ce que le modèle ne permet pas de conclure** — une oscillation propre correcte ne valide que
   la raideur et la masse du système dans cette configuration précise, pas le couplage
   aéro-élastique réel (aucune charge aérodynamique ici) ni le comportement d'un flotteur (la
   plateforme est bloquée dans ce cas, pas libre comme au cas 05).
5. **Renvois** — tutoriel OpenFAST Quickstart du LHEEA §1 (voir NOTICE pour le détail des
   adaptations v3.2.1→v5.0.0, `ADAPTATION_LHEEA.md`).

```bash
cd tutorials/lheea/01_TowerStructure/1_Configuration
openfast main.fst
```

Doit se terminer par `OpenFAST terminated normally.`. C'est le cas le plus simple du dépôt — s'il
échoue, l'installation n'est pas correcte, reprenez l'étape 1.

## 4. Cas LHEEA 02 — éolienne libre en vent constant (environ 15 min)

*D'après le tutoriel OpenFAST Quickstart du LHEEA (Apache-2.0), §2, adapté — voir
[`../../tutorials/lheea/NOTICE`](../../tutorials/lheea/NOTICE).*

### Bloc Théorie

1. **Question physique** — Que se passe-t-il si un rotor tourne librement sous l'effet du vent,
   sans aucun frein ni contrôle de couple ?
2. **Modèle** — le rotor accélère jusqu'à ce que le couple aérodynamique s'annule (portance et
   traînée se compensent dans le plan de rotation) : un équilibre libre, pas une régulation.
   **Domaine de validité** : vent constant avec profil de cisaillement (loi de puissance) ; le
   sillage est traité en BEMT quasi-stationnaire (`Wake_Mod=1`), mais l'aérodynamique de profil,
   elle, est **instationnaire** (`UA_Mod=3`, modèle de décrochage dynamique de Beddoes-Leishman) —
   ne confondez pas les deux sous-modèles en répondant à une question sur ce cas. `UA_Mod=3` est la
   valeur du modèle de référence de ce projet (`models/oc4_rtest`), pas un choix propre à ce cas.
3. **Ordre de grandeur attendu** — la méthode : observer le plateau de `RotSpeed` en régime
   établi, et le comparer au régime nominal de la machine (fiche F1) pour juger si cette vitesse
   libre est réaliste ou extrême.
4. **Ce que le modèle ne permet pas de conclure** — ce régime libre n'est pas physiquement tenable
   pour une vraie éolienne (vitesse de bout de pale et nombre de Mach excessifs, signalé par le
   tutoriel LHEEA lui-même) : ce cas sert à introduire le *besoin* de régulation, pas à représenter
   un fonctionnement réel — c'est l'objet du bloc suivant.
5. **Renvois** — tutoriel OpenFAST Quickstart du LHEEA §2 ; fiche F1 (régulation, bloc suivant).

```bash
cd tutorials/lheea/02_FreeRotatingWT/1_Configuration
openfast main.fst
```

Doit se terminer par `OpenFAST terminated normally.`.

## 5. Régulation de la NREL 5 MW, à la main (environ 30 min)

### Bloc Théorie

1. **Question physique** — Pourquoi une éolienne ne tourne-t-elle pas à une vitesse de rotation
   fixe quel que soit le vent, et pourquoi faut-il la piloter (couple générateur, puis pitch)
   plutôt que la laisser suivre librement l'aérodynamique ?
2. **Modèle** — TSR `λ = Ω·R/V` ; coefficient de puissance `Cp(λ,β)`, maximal pour un `λ*`
   donné ; loi de Region 2 `Ω(V) = λ*·V/R` (couple piloté, pitch fixe) ; en Region 1½, `Ω` est solution de l'équilibre
   `Q_aéro(Ω) = N·Q_gen(NΩ)` (couple aérodynamique `½ρπR²V³·Cp(λ)/Ω` contre couple de la rampe du
   contrôleur, fiche F1). **Domaine de validité** :
   machine à vitesse variable et pitch variable (c'est le cas ici), et seulement entre le seuil de
   Region 2 et le régime nominal : en dessous, la rampe de couple de Region 1½ gouverne ; au-delà,
   Region 2½ puis 3. Repérez la région avant d'appliquer une loi.
3. **Ordre de grandeur attendu** — la méthode : pour chaque vitesse de vent du tableau, repérer la région
   (seuils de la fiche F1), puis calculer `Ω` par la loi `λ*·V/R` (Region 2) ou par l'équilibre des couples
   (Region 1½) ; repérer la vitesse de vent où `Ω` atteint le régime nominal donné par la fiche F1. Les valeurs numériques du cas particulier F01/F02 répondent à une question
   notée (Q0.1/Q0.2) : ne les cherchez pas dans ce dépôt, calculez-les.
4. **Ce que le modèle ne permet pas de conclure** — la loi `λ* = constante` est une
   approximation : la loi de couple réelle du contrôleur peut s'en écarter légèrement à certaines
   vitesses, et ce modèle stationnaire ne dit rien du régime transitoire ni du comportement en
   Region 2½/3. **Point de cours — Region 1½** : en Region 1½ le couple suit une rampe
   linéaire, non la parabole de Region 2. Cette rampe est *raide* (pente bien supérieure à celle de la
   parabole) : une petite variation de vitesse suffit à rééquilibrer le couple aérodynamique, donc `Ω`
   reste **confinée dans la bande entre les deux seuils**, quel que soit le vent de la région. Conséquence
   à savoir énoncer : la loi `λ*·V/R` ne vaut qu'**en haut de la bande**, près du seuil de Region 2 ; plus bas
   dans la région, `Ω` est tenue au-dessus de ce que donnerait la loi (la bande est un plancher), et le
   `λ` réel s'écarte de `λ*`. Le fait que `Cp(λ)` soit plat autour de son maximum explique seulement que
   la *puissance* perdue reste faible quand `λ` s'écarte un peu de `λ*`, pas que la loi donne `Ω`. À
   vérifier sur vos résultats (écart relatif de `RotSpeed` à `λ*·V/R`).
5. **Renvois** — fiche F1, section « Minimum vital » et « Ordre de grandeur » ; Jonkman 2009,
   §7.2 p.19 et Tab. 7-2 p.27 (paramètres numériques).

Avec la fiche F1 : R = 63 m, vitesse de bout de pale maximale 80 m/s, régime nominal 12,1 tr/min,
puissance nominale 5 MW, TSR optimal 7,55 (Jonkman 2009). Construisez le tableau vitesse de vent →
vitesse de rotation → puissance, et identifiez les zones de fonctionnement (Region 1½, 2, 2½, 3), **avec l'`Ω` attendu dans chaque région** :
loi `λ*·V/R` en Region 2, **équilibre des couples** en Region 1½ (la fiche F1 donne la loi de la rampe du
contrôleur, la courbe `Cp(λ)` du modèle à calage nul et la méthode). C'est la question Q0.1 du rendu R0.

## 6. Cas F01 et F02 — éolienne fixe (environ 45 min)

### Bloc Théorie

1. **Question physique** — Le calcul OpenFAST produit des courbes de sortie : comment savoir
   si elles sont physiquement plausibles avant de les utiliser dans un rendu, sans attendre qu'un
   enseignant les valide ?
2. **Modèle** — poussée du rotor par la théorie du disque actuateur,
   `T = 1/2 · ρ · A · V² · Ct`, puis `TwrBsMyt ≈ T × (H_moyeu − TowerBsHt)` — le moment est pris au
   pied de la tour, dont la hauteur `TowerBsHt` se lit dans `config_elastodyn.dat`. **Domaine de validité** :
   vent stationnaire pour F01 (le modèle stationnaire ne s'applique pas directement à l'échelon de
   F02), `Ct` supposé à peu près constant sous le régime nominal (voir la fiche F1, qui donne les
   seuils du contrôleur : à vous de repérer la région de F01), régime établi
   atteint (transitoire de démarrage écarté de la moyenne).
3. **Ordre de grandeur attendu** — la méthode : calculer `Ω` attendu (bloc précédent) et le
   comparer à `RotSpeed` observé (écart tolérable ~15-20 %, fiche F1) ; estimer `T` et
   `TwrBsMyt ≈ T × (H_moyeu − TowerBsHt)`, à comparer à `TwrBsMyt` observé (±20 %, énoncé §3 bis). Les
   valeurs numériques pour F01 répondent à Q0.2 : à calculer, pas à relever.
4. **Ce que le modèle ne permet pas de conclure** — un écart dans la tolérance ne prouve pas
   que la configuration est correcte (un transitoire mal filtré peut produire le même symptôme
   qu'une vraie erreur), et cette vérification stationnaire ne valide rien sur la dynamique de
   F02 (échelon), qui demande une lecture différente (temps de réaction du calage).
5. **Renvois** — fiche F1, section « Confrontation OpenFAST » ; `outils/lire_outb.py` (option
   `t_min`, pour écarter le transitoire).

### Bloc Théorie — fréquence 1P

1. **Question physique** — Q0.2 demande de repérer la fréquence de rotation 1P sur le moment
   d'emplanture d'une pale : pourquoi cette fréquence apparaît-elle, et pourquoi la tour ne
   « voit »-elle pas la même chose que la pale ?
2. **Modèle** — `f₁ₚ = RotSpeed / 60` (Hz, `RotSpeed` en tr/min). Dans le repère tournant, une
   pale rencontre à chaque tour les mêmes conditions non uniformes : cisaillement du vent (le haut
   du disque voit plus de vent que le bas), sillage de la tour (effets hors plan du rotor), poids propre de
   la pale (moment dans le plan, `RootMxb1`). Sa charge est donc périodique de période un tour :
   harmonique 1P, visible sur `RootMyb1` pour les deux premiers effets. Dans le repère fixe (tour), les trois pales identiques, déphasées de 120°, se
   somment : les harmoniques qui ne sont pas multiples du nombre de pales se compensent, il reste
   3P, 6P… **Domaine de validité** : rotor à trois pales identiques, vitesse de rotation quasi
   constante (régime établi de F01) ; un rotor déséquilibré ou un vent turbulent ajoute du 1P et
   des harmoniques sur la tour.
3. **Ordre de grandeur attendu** — la méthode : convertir le `RotSpeed` établi en Hz, puis
   chercher ce pic sur le spectre de `RootMyb1` (FFT, après avoir écarté le transitoire) ; le
   pic 3P de la tour se déduit en multipliant par trois. Les valeurs répondent à Q0.2 : à
   calculer, pas à relever ici.
4. **Ce que le modèle ne permet pas de conclure** — retrouver 1P sur `RootMyb1` ne dit pas
   laquelle des causes (cisaillement, tour, gravité) domine, ni ce que vaut l'amplitude ; et la
   position de 1P/3P ne dit rien d'une résonance tant qu'on ne la compare pas aux fréquences
   propres de la tour (phase 5).
5. **Renvois** — fiche F1 (ligne « Fréquence 1P ») ; Jonkman 2009, p.15 (fréquences propres de la
   tour placées entre 1P et 3P sur le diagramme de Campbell) ; `RootMyb1` : liste des sorties
   d'OpenFAST (`OutListParameters.xlsx`).

```bash
cd tutorials/prise_en_main
bash run_cas.sh F01
bash run_cas.sh F02
```

| Cas | Vent | Ce qu'on regarde |
|---|---|---|
| F01 | constant 7,5 m/s | régime établi, poussée, moment en pied de tour |
| F02 | échelon de 5 à 20 m/s | passage d'une zone de régulation à l'autre, temps de réaction du calage des pales |

Voir `tutorials/prise_en_main/README.md` pour la méthode de vérification à la main (fréquence 1P,
poussée, `TwrBsMyt`).

## 7. Rendu R0 (à finir hors séance si besoin)

Questions Q0.1 et Q0.2 de l'énoncé (section « Phase 0 », rendu R0) : tableau de régulation à la
main comparé à F02, et vérifications à la main de F01. Les questions Q0.3 à Q0.5 portent sur la
séance 0b, pas sur celle-ci.

## Séance suivante

[`seances/0b/`](../0b/README.md) : cas LHEEA pilotés, monopieu et flottant, puis construction de
vos propres cas (F03-F05, D00-D05).
