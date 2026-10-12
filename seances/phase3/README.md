<!-- destinations: github -->
# Phase 3 — Fatigue

Consigne autonome de la phase. Le cadre du projet (objectifs, évaluation, règles) est dans [`../../ENONCE.md`](../../ENONCE.md) ; [séance précédente](../phase2/README.md) · [phase suivante](../phase4/README.md).

## 1. Objectif

Fatigue : rainflow, S-N, Miner, DEL court et long terme. Volume indicatif : 8 h. Rendu : **R3**.

**Travail personnel estimé** : ≈ 3 h — la fin du premier passage de l'atelier tour (étape 0 : `SCF = 2` et le comparatif avec `SCF = 1`) se termine à la maison ; le début (prise en main, `SCF = 1`) se fait en séance.

## 2. Avant de commencer

Prérequis : l'environnement installé en [séance 0a](../0a/README.md) (`openfast -v` → `OpenFAST-v5.0.0`, contrôleur compilé).

**À lire avant la séance : F8 (Ancrage dynamique et fatigue)** — dès qu'elle est publiée.

**Où vit ce que vous produisez** : sous `results/` et `rendus/` (ignorés par git) ; `cas/`, `modeles/` et `seances/` se lisent et se lancent sans être modifiés.

## 3. À faire, étape par étape

0. **Atelier tour, premier passage** : prise en main de la chaîne DEL court terme → long terme →
   courbe S-N → épaisseur, sur le classeur de l'atelier tel quel (sa propre géométrie de tour et
   ses propres données d'entrée, pas celles du projet) — d'abord avec `SCF = 1`, puis `SCF = 2`, en
   comparant épaisseurs et masse. Voir [`seances/atelier_tour/`](../atelier_tour/README.md)
   pour la théorie derrière chaque étape. C'est la **méthode** (pas la géométrie ni les résultats)
   que vous reprendrez au point 2 ci-dessous, sur la tour du projet, puis en Phase 5 avec vos
   propres charges.
1. **Rainflow** sur `TwrBsMyt` et `FAIRTEN1-3`, pour chaque cas.
2. **Contrainte en pied de tour** : passer du moment à la contrainte de flexion, avec les
   caractéristiques de section de la tour de **référence** (aire, inertie) — pas une donnée
   fournie, à calculer vous-mêmes comme à l'étape 0, mais pour cette géométrie-ci : diamètre
   extérieur lu dans le fichier AeroDyn de la tour (`TwrDiam`/`TwrElev`), épaisseur à retrouver à
   partir de la masse linéique (`TMassDen` du fichier tour ElastoDyn) — **à condition de choisir
   une masse volumique**, et c'est un choix à justifier, pas une évidence : l'acier pur donne
   7850 kg/m³, mais une tour réelle inclut peinture, boulonnerie et soudures, souvent représentées
   par une masse volumique « effective » plus élevée dans ce genre de modèle. Dites laquelle vous
   retenez et pourquoi, et vérifiez la cohérence du résultat (diamètre/épaisseur réalistes pour une
   éolienne 5 MW). Appliquer un **SCF = 2** (hypothèse d'avant-projet).
3. **Courbe S-N** : choisir la courbe DNV-RP-C203 adaptée (type de soudure, milieu air ou eau, épaisseur) et justifier ce choix.
4. **Dommage** : Miner sur chaque cas, puis cumul pondéré par les occurrences Oⱼ ; durée de vie avec le DFF imposé.
5. **DEL** : programmer vous-mêmes le DEL court terme Sₑ et long terme Sₑₜ (formules au lexique), puis comparer avec l'outil d'`openfast_toolbox`. Un écart entre les deux doit être expliqué.
6. **Limites** : montrer sur un de vos cas pourquoi le DEL ne suffit pas pour conclure (perte de concomitance, hypothèse monopente, dépendance à la fréquence propre).
7. **Confrontation à une référence de 50 ans** : le projet FLOATECH a simulé la même éolienne OC4 sur le même site pendant 50 ans d'états de mer réels (environ 450 000 simulations d'une heure). Comparez le DEL long terme obtenu avec votre LCT de 10 à 15 cas au DEL de référence fourni. L'écart mesure la qualité de votre binning et de votre lumping : expliquez-le, et dites ce qu'il faudrait changer dans votre LCT pour le réduire.

> **À compléter** : les commandes exactes de cette phase ne sont pas encore écrites (outil : `s9gm/fatigue.py` (squelette : à compléter par vous)).

## 4. Post-traiter

La démarche générale, du `.outb` aux statistiques, aux figures et au DEL, est dans [`../../s9gm/POST-TRAITER.md`](../../s9gm/POST-TRAITER.md). Rainflow, contrainte, dommage de Miner, DEL court et long terme : voir les points 1 à 7 de la section 3, avec `s9gm/fatigue.py`.

## 5. Ce qu'on rend

**Rendu R3** : comparatif SCF = 1 / SCF = 2 de l'atelier tour (étape 0) ; note de calcul fatigue (hypothèses, courbe S-N retenue, dommages par cas, durée de vie), comparaison DEL maison vs outil.

## 6. Théorie à lire

F8 (Ancrage dynamique et fatigue) : *fiche à venir (master)*.

L'atelier tour donne la théorie derrière chaque étape de calcul : [`../atelier_tour/README.md`](../atelier_tour/README.md).
