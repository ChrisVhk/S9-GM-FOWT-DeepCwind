# Wang, Robertson, Jonkman et al. — OC6 Phase Ib: Validation of the CFD Predictions of Difference-Frequency Wave Excitation on a FOWT Semisubmersible

**Référence complète** : *Ocean Engineering* (ScienceDirect, sciencedirect.com/science/article/abs/pii/
S0029801821013603). Preprint accepté sur OSTI (ID correspondant au fichier `1881411`), auteurs : Lu
Wang, Amy Robertson, Jason Jonkman (NREL), Yi-Hsiang Yu (NREL), Arjen Koop (MARIN), Adrià Borràs Nadal
(IFPEN), Haoran Li, Erin Bachynski-Polić (NTNU), Romain Pinguet (Principe Power / Aix-Marseille),
Wei Shi, Xinmeng Zeng, Yang Zhou (Dalian Univ.), Qing Xiao, Rupesh Kumar (Univ. Strathclyde), Hamid
Sarlak (DTU), Edward Ransley, Scott Brown, Martyn Hann (Univ. Plymouth), Stefan Netzband, Malwin
Wermbter (TUHH), Beatriz Méndez López (CENER). Également référencé : WDH `oc6/oc6.phase1b`.

**Accès** : **texte intégral partiellement lu** (pages 1-2 : résumé, affiliations, introduction).

## Question posée
Valider par CFD (en complément du génie-outil d'ingénierie) les prédictions d'excitation de houle au
second ordre en fréquence-différence sur l'OC5-DeepCwind, et confronter ces prédictions CFD aux mesures
d'un essai bassin dédié — le tout sur une géométrie SIMPLIFIÉE permettant d'isoler l'effet de chaque
colonne.

## Système modélisé
OC5-DeepCwind simplifié : colonne centrale et croisillons RETIRÉS, seules les trois colonnes latérales
conservées (confirmé par la recherche externe, cf résumé WebSearch) — plateforme fixe, houle bichromatique.

## Outil et version
Simulations CFD (plusieurs codes, contributeurs multiples — liste p.1) + essais bassin MARIN, avec
analyse d'incertitude pour les deux volets (expérimental ET CFD) (résumé, p.1).

## Réglages hydro
Excitation de houle au second ordre, fréquence-différence en particulier (titre + résumé) ; mesure de
l'excitation sur CHAQUE colonne séparément (résumé, p.1) — permet une validation par colonne, pas
seulement globale.

## Résultats chiffrés clés
**p.1 (résumé)** : accord global entre prédictions CFD et mesures expérimentales pour l'excitation en
fréquence-différence (« the CFD predictions of the difference-frequency excitations agree with the
experimental measurements ») — pas de chiffre d'écart % donné dans les pages lues ; conclusion
qualitative : les solutions CFD peuvent servir de référence pour caler/améliorer les outils d'ingénierie.
**p.2** : rappel du contexte — sous-estimation OC5 de **10 à 20 %** des charges ultimes et de fatigue.

## Ce que l'article dit explicitement ne pas expliquer
Pages de résultats détaillés et de discussion non lues dans cette passe (hors budget de cette session) —
à compléter. Le résumé ne tranche pas si l'accord CFD/essai suffit à expliquer la totalité de la
sous-estimation observée en OC5 Phase II, seulement que l'excitation de fréquence-différence est
correctement capturée par la CFD.

## Reproductible avec nos moyens ?
**Non.** Nécessite une géométrie simplifiée dédiée (3 colonnes seules) et un code CFD, hors périmètre de
ce dépôt (OpenFAST/outils d'ingénierie uniquement). Utile comme RÉFÉRENCE qualitative : si notre propre
modèle potentiel-flow (WAMIT, QTF) de l'ancrage/plateforme s'écarte significativement, cet article
indique que l'excitation second-ordre elle-même n'est probablement pas la cause dominante (déjà
validée par CFD), ce qui oriente l'attribution d'un écart (cf INV-25) vers d'autres sources (ancrage,
amortissement visqueux, couplage aérodynamique).
