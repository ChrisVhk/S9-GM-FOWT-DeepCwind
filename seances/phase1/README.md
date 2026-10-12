<!-- destinations: github -->
# Phase 1 — Du site à la Load Case Table

Consigne autonome de la phase. Le cadre du projet (objectifs, évaluation, règles) est dans [`../../ENONCE.md`](../../ENONCE.md) ; [séance précédente](../0b/README.md) · [phase suivante](../phase2/README.md).

## 1. Objectif

Du site à la Load Case Table : scatter diagram, DLC, binning / lumping. Volume indicatif : 3 h. Rendu : **R1**.

## 2. Avant de commencer

Prérequis : l'environnement installé en [séance 0a](../0a/README.md) (`openfast -v` → `OpenFAST-v5.0.0`, contrôleur compilé).

**Données fournies** (dossier `data/metocean/` du dépôt, publié par l'enseignant avant cette phase — absent du dépôt à son ouverture) : un site réel au large de l'île de Barra (Écosse), à partir des conditions publiées en accès ouvert par le projet européen FLOATECH (Papi et al., université de Florence, réanalyse ERA5, licence CC-BY 4.0) : distribution conjointe vent / Hs / Tp / désalignement vent-houle, extrêmes ; pour le courant et les niveaux d'eau, **consultez** le livrable public D1.1 du projet LIFES50+ (« Oceanographic and meteorological conditions for the design », Iberdrola Ingeniería y Construcción, projet 640741, 03/10/2015, accessible par CORDIS) : il n'est pas redistribué avec ce dépôt, ses données ne sont pas fournies. Citer ces sources dans vos rendus.

**Où vit ce que vous produisez** : sous `results/` et `rendus/` (ignorés par git) ; `cas/`, `modeles/` et `seances/` se lisent et se lancent sans être modifiés.

## 3. À faire, étape par étape

1. Lire le scatter diagram : quelles cellules sont les plus probables ? Lesquelles portent le plus d'énergie de houle ?
2. Choisir les DLC du projet et justifier par composant :
   - **FLS** : DLC 1.2 (production normale) ; discuter le DLC 7.2 (parking, faible amortissement aérodynamique) ;
   - **ULS** : DLC 6.1 (parking, vent extrême, ESS) et DLC 1.6 (production, SSS) ; justifier si le DLC 6.2 peut être écarté à ce stade.
3. **Construire la LCT de votre groupe** (10 à 15 cas maximum, 600 s simulées chacun) : binning, lumping, occurrence Oⱼ de chaque ligne. Le budget de calcul est une contrainte réelle : une simulation de 600 s prend environ 25 min sur une machine de la salle.
4. **Vérifier la représentativité** : comparer, paramètre par paramètre, les occurrences de votre LCT à celles du site. Dire où vous avez accepté d'être moins précis, et pourquoi c'est acceptable (loin des périodes propres ? faible occurrence ?).

> **À compléter** : les commandes exactes de cette phase ne sont pas encore écrites (outil : `s9gm/metocean.py`).

## 4. Post-traiter

La démarche générale, du `.outb` aux statistiques, aux figures et au DEL, est dans [`../../s9gm/POST-TRAITER.md`](../../s9gm/POST-TRAITER.md). Cette phase ne produit pas de sortie OpenFAST à post-traiter : elle travaille sur la table conjointe du site, avec `s9gm/metocean.py`.

## 5. Ce qu'on rend

**Rendu R1** : la LCT (tableur), une page de justification, le tableau de représentativité.

## 6. Théorie à lire

F2 (Houle linéaire) : *fiche à venir (master)*.
