<!-- destinations: github -->
# Phase 5 — Structures tubulaires : tour et flotteur

Consigne autonome de la phase. Le cadre du projet (objectifs, évaluation, règles) est dans [`../../ENONCE.md`](../../ENONCE.md) ; [séance précédente](../phase4/README.md) · [phase suivante](../phase6/README.md).

## 1. Objectif

Structures tubulaires : section de tour, effort dans une entretoise, SCF et domaine de validité. Volume indicatif : 8 h. Rendu : **R5**.

**Travail personnel estimé** : ≈ 5 h — fin du second passage de l'atelier (point 1, ≈ 3 h : sections FLS/ULS au-delà de celle traitée en séance) + boucle de dimensionnement (point 2, ≈ 2 h) à la maison ; le lancement du second passage sur vos propres données se fait en séance.

Quatre niveaux de modèle existent pour la structure d'un flotteur. Le projet en mobilise trois.

| Niveau | Méthode | Ce qu'il donne | Qui |
|---|---|---|---|
| **A** | Modèle rigide (référence) | Fatigue et extrêmes du pied de tour et des chaumards | Tous |
| **B** | Effort de section estimé à la main : force d'écartement / de pincement des colonnes (*split / squeeze*) en houle de travers | Effort nominal dans une entretoise, puis contrainte nominale × SCF | Tous |
| **C** | Flotteur flexible modélisé en poutres (SubDyn couplé au flotteur) | Séries temporelles d'efforts intérieurs par membre, donc rainflow sur une entretoise | Groupe centre |
| **D** | Éléments finis locaux de l'assemblage | Contrainte au point chaud, SCF « vrai » | Lecture d'une étude publiée |

## 2. Avant de commencer

Prérequis : l'environnement installé en [séance 0a](../0a/README.md) (`openfast -v` → `OpenFAST-v5.0.0`, contrôleur compilé).

**Où vit ce que vous produisez** : sous `results/` et `rendus/` (ignorés par git) ; `cas/`, `modeles/` et `seances/` se lisent et se lancent sans être modifiés.

## 3. À faire, étape par étape

*Les renvois « §n » à l'atelier tour (§2, §4, §9b, §10) suivent la correspondance donnée au début de sa [consigne](../atelier_tour/README.md).*

1. **Tour (niveau A), atelier tour second passage, avec vos données.** Même méthode qu'à la Phase
   3 (étape 0), mais toutes les entrées sont désormais les vôtres, pour **chaque groupe** :
   - **géométrie de départ** = tour OC4 du modèle de référence — longueur et base lues dans le
     fichier ElastoDyn principal (`TowerHt`, `TowerBsHt`), diamètres extérieurs lus dans le fichier
     AeroDyn de la tour (`TwrDiam`/`TwrElev`), épaisseurs retrouvées comme au point 2 de la Phase 3
     (à partir de `TMassDen` et d'une masse volumique justifiée) — rien n'est présumé ;
   - **DEL court terme** par cas de votre LCT (sur les canaux de pied ou de tête de tour que vous
     aurez identifiés au §4/§9b du tutoriel atelier tour, exposant `m = 4` pour la branche
     principale et `m = 3`/`5` pour la sensibilité) — un outil dédié sera annoncé en séance, sinon
     reprenez le programme du point 5 de la Phase 3 ;
   - **occurrences `Oⱼ`** = celles de **votre** LCT de la Phase 1 (table conjointe vent × houle ×
     courant), pas la loi de Weibull propre au classeur de l'atelier (voir
     [`seances/atelier_tour/`](../atelier_tour/README.md), §2) ;
   - **efforts extrêmes** = vos cas DLC 1.6 et 6.1 de la Phase 4 (ceci complète l'ULS du niveau A,
     qui restait partiel avec les seules données de l'atelier) ;
   - **test de l'hypothèse « somme des DEL »** (théorie au §4, exercice concret au §9b de
     `seances/atelier_tour/`) avec les jauges de tour OpenFAST, à **trois hauteurs** (pied, milieu,
     sommet) : à chacune, trois DEL à comparer deux à deux, pas directement entre les extrêmes —
     la méthode de l'atelier (deux DEL combinés après coup) contre le calcul exact du même modèle
     de transport (un seul rainflow sur le signal combiné point par point) isole le coût de
     l'hypothèse de concomitance ; ce calcul exact contre le DEL mesuré directement à la jauge
     isole ce que le modèle de transport statique ne capture pas (poids propre et inertie de la
     tour, mouvements du flotteur en tangage, absents du classeur de l'atelier qui suppose une
     tour sur base fixe). Commentez les deux écarts et leur sens, et s'ils sont les mêmes aux trois
     hauteurs.

   Vérifier la section résultante en FLS (contrainte de flexion × SCF = 2 vs contrainte admissible
   en fatigue) et en ULS (Von Mises vs limite élastique). Ajuster l'épaisseur pour satisfaire les
   deux critères à masse minimale.
2. **Boucle de dimensionnement, une itération.** Réinjectez les `R`, `S`, `T` (masse linéique,
   raideurs) de la tour dimensionnée au point 1 dans le fichier tour d'ElastoDyn, et relancez
   **un** nouveau calcul OpenFAST : un cas de fatigue représentatif (celui qui dimensionnait au
   point 1) et le cas ULS dimensionnant. Commentez la variation des efforts obtenus par rapport au
   premier passage.
   > **Point dur, à régler avant de lancer ce calcul** : ElastoDyn ne demande pas seulement `R`,
   > `S`, `T` par station, mais aussi les **formes modales** de la tour (coefficients polynomiaux
   > `TwFAM1Sh(2-5)` etc., qui décrivent la déformée assumée du premier mode). Aucun outil de
   > calcul de ces coefficients à partir d'une nouvelle distribution de masse/raideur n'est
   > disponible dans l'environnement du cours (ni BModes, ni d'équivalent dans `openfast_toolbox` —
   > son module `linearization` analyse un modèle déjà construit, via la linéarisation d'OpenFAST
   > lui-même, mais ne calcule pas de nouveaux coefficients d'entrée). **Approximation retenue** :
   > conservez les
   > coefficients polynomiaux d'origine tels quels, et dites-le explicitement comme une
   > approximation.
   >
   > Pour en estimer l'ordre de grandeur sur la fréquence propre (sans attendre un résultat
   > garanti), un quotient de Rayleigh, en réutilisant la **même** déformée assumée `φ(x)` (celle
   > des coefficients d'origine) mais évaluée avec la **nouvelle** distribution de raideur `EI(x)`
   > et de masse linéique `m(x)` :
   > `f² ∝ [∫EI(x)·φ''(x)²dx] / [∫m(x)·φ(x)²dx + M_tête·φ(L)²]`
   > — le terme `M_tête·φ(L)²` (masse du rotor + moyeu + nacelle en tête, très supérieure à la
   > masse de la tour elle-même : à relever dans le fichier ElastoDyn principal, `NacMass`,
   > `HubMass`, et la masse des pales) **ne doit pas être oublié**, il domine le dénominateur pour
   > une éolienne. Attention à l'interprétation : le principe de Rayleigh garantit qu'une déformée
   > assumée différente de la vraie déformée propre **d'une même structure** surestime sa fréquence
   > — il ne garantit **pas** que la fréquence obtenue ainsi pour la tour redimensionnée encadre sa
   > vraie nouvelle fréquence (ce sont deux structures différentes). Ce calcul donne donc un ordre
   > de grandeur de l'effet de l'approximation, pas une borne garantie. Si l'écart avec la fréquence
   > d'origine est significatif, dites-le et discutez-en — ce point ne demande pas de corriger
   > l'approximation, seulement d'en estimer l'effet.

   Comparez les fréquences propres de la tour (avant/après l'itération) aux fréquences 1P et 3P du
   rotor (voir `seances/atelier_tour/`, §10, point non couvert par l'atelier — à faire ici).
3. **Entretoise (niveau B)** : estimer l'effort d'écartement des colonnes pour la houle la plus pénalisante (longueur d'onde de l'ordre de deux fois l'entraxe des colonnes), en déduire l'effort axial et la contrainte nominale dans l'entretoise. Comparer à une contrainte admissible.
4. **Domaine de validité du SCF** : relever dans le document de définition OC4 les diamètres des entretoises, des colonnes déportées et de la colonne centrale ; calculer β = d/D pour chaque jonction ; dire si les formules paramétriques d'Efthymiou (établies pour les jackets) s'appliquent. Conclure sur ce qu'il faut faire quand elles ne s'appliquent pas.
5. **Groupe centre (niveau C)** : comparer, sur un même état de mer, l'effort dans une entretoise obtenu au niveau B et la série temporelle du modèle flexible. Expliquer pourquoi la répartition des efforts hydrodynamiques (potentiels ramenés en un point / Morison répartis) conditionne la validité du résultat.
6. **Assemblage (niveau D)** : à partir de l'étude publiée fournie (assemblage colonne-entretoise d'une semi-submersible), expliquer la chaîne *efforts globaux → modèle local éléments finis → SCF au point chaud → S-N → durée de vie*, et discuter les ordres de grandeur obtenus.

Rappel : aux niveaux A, B et C on obtient une contrainte **nominale**. Le SCF reste indispensable, et il faut savoir justifier d'où il vient.

> **À compléter** : les commandes exactes de cette phase ne sont pas encore écrites (outil : `s9gm/structure.py` (squelette : à compléter par vous)).

## 4. Post-traiter

La démarche générale, du `.outb` aux statistiques, aux figures et au DEL, est dans [`../../s9gm/POST-TRAITER.md`](../../s9gm/POST-TRAITER.md). Contraintes de section, effort dans l'entretoise, DEL de tour : voir la section 3, avec `s9gm/structure.py` et `s9gm/fatigue.py`.

## 5. Ce qu'on rend

**Rendu R5** : note de vérification de la tour (premier passage et itération), calcul d'entretoise (niveau B), tableau β et conclusion sur le SCF ; groupe centre : comparaison B / C.

## 6. Théorie à lire

F4 (Morison) : *fiche à venir (master)*.

L'atelier tour donne la théorie derrière chaque étape de calcul : [`../atelier_tour/README.md`](../atelier_tour/README.md).
