<!-- destinations: github -->
# Phase 2 — Simulations de référence et sensibilité

Consigne autonome de la phase. Le cadre du projet (objectifs, évaluation, règles) est dans [`../../ENONCE.md`](../../ENONCE.md) ; [séance précédente](../phase1/README.md) · [phase suivante](../phase3/README.md).

## 1. Objectif

Simulations de référence, lâchers, étude de sensibilité par groupe. Volume indicatif : 5 h. Rendu : **R2**.

## 2. Avant de commencer

Prérequis : l'environnement installé en [séance 0a](../0a/README.md) (`openfast -v` → `OpenFAST-v5.0.0`, contrôleur compilé).

**À lire avant la séance : F5 (Hydrodynamique potentielle), F6 (Aérodynamique et amortissement négatif)** — dès qu'elles sont publiées.

**Où vit ce que vous produisez** : sous `results/` et `rendus/` (ignorés par git) ; `cas/`, `modeles/` et `seances/` se lisent et se lancent sans être modifiés.

## 3. À faire, étape par étape

1. **Référence commune** (modèle flottant OC4 : [`modeles/flottant/`](../../modeles/flottant/README.md), cas de la séance [0b](../0b/README.md) — *à compléter : le cas désigné comme référence commune de la phase 2 reste à choisir*) : lancer, vérifier l'équilibre (tension statique des lignes, position moyenne du flotteur).
2. **Lâchers (free decay)** en surge, heave, pitch : mesurer les périodes propres. Les comparer aux valeurs publiées OC4/OC5 (référence fournie) et **dire où se situent ces périodes par rapport aux périodes de houle de votre scatter diagram**.
3. **Sensibilité** : lancer la LCT de votre groupe en ne faisant varier **que** votre famille de paramètres, tout le reste fixé à la référence.
4. Pour chaque cas : statistiques (moyenne, écart-type, max, min) aux points imposés, et spectres de réponse.

> **À compléter** : les commandes exactes de cette phase ne sont pas encore écrites (outil : `s9gm/cas.py`, `s9gm/lancer.py`, `s9gm/lire.py`, `s9gm/visu.py`).

## 4. Post-traiter

La démarche générale, du `.outb` aux statistiques, aux figures et au DEL, est dans [`../../s9gm/POST-TRAITER.md`](../../s9gm/POST-TRAITER.md). Statistiques (moyenne, écart-type, max, min) aux points imposés et spectres de réponse pour chaque cas, périodes propres des lâchers : voir les points 2 et 4 de la section 3.

## 5. Ce qu'on rend

**Rendu R2** : tableau des résultats, figures commentées. Pour chaque tendance observée : *théorie attendue → ce que montrent les chiffres → ce qu'ils ne permettent pas de conclure* (une seule seed ? durée trop courte ? autre paramètre couplé ?).

## 6. Théorie à lire

F5 (Hydrodynamique potentielle), F6 (Aérodynamique et amortissement négatif) : *fiche à venir (master)*.
