<!-- destinations: github -->
# Phase 4 — Extrêmes et ancrage

Consigne autonome de la phase. Le cadre du projet (objectifs, évaluation, règles) est dans [`../../ENONCE.md`](../../ENONCE.md) ; [séance précédente](../phase3/README.md) · [phase suivante](../phase5/README.md).

## 1. Objectif

Extrêmes (ULS) et ancrage. Volume indicatif : 12 h. Rendu : **R4**.

## 2. Avant de commencer

Prérequis : l'environnement installé en [séance 0a](../0a/README.md) (`openfast -v` → `OpenFAST-v5.0.0`, contrôleur compilé).

**À lire avant la séance : F7 (Caténaire statique)** — dès qu'elle est publiée.

**Où vit ce que vous produisez** : sous `results/` et `rendus/` (ignorés par git) ; `cas/`, `modeles/` et `seances/` se lisent et se lancent sans être modifiés.

## 3. À faire, étape par étape

1. Lancer les cas ULS retenus en phase 1 (DLC 6.1 et 1.6) pour la référence et pour la variante la plus pénalisante de votre groupe.
2. Comparer tensions maximales et capacité de la ligne (fournie) ; mouvements maximaux du flotteur.
3. **Groupe centre** : comparer MoorDyn et MAP++ sur le même cas extrême — quand l'approche quasi-statique sous-estime-t-elle les tensions ?
4. **Groupes bâbord et tribord** : ce qui, dans votre famille de paramètres, pilote l'extrême d'ancrage.

> **À compléter** : les commandes exactes de cette phase ne sont pas encore écrites (outil : `s9gm/ancrage.py` (squelette : à compléter par vous)).

## 4. Post-traiter

La démarche générale, du `.outb` aux statistiques, aux figures et au DEL, est dans [`../../s9gm/POST-TRAITER.md`](../../s9gm/POST-TRAITER.md). Tensions maximales des lignes et mouvements maximaux du flotteur : voir le point 2 de la section 3.

## 5. Ce qu'on rend

**Rendu R4** : tableau ULS, vérification des lignes, conclusion argumentée.

## 6. Théorie à lire

F7 (Caténaire statique), F8 (Ancrage dynamique et fatigue) : *fiche à venir (master)*.
