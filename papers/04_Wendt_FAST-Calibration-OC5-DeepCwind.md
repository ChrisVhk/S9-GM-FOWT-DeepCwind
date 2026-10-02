# Wendt, Robertson, Jonkman — FAST Model Calibration and Validation of the OC5-DeepCwind Floating Offshore Wind System Against Wave Tank Test Data

**Référence complète** : Wendt, F.F.; Robertson, A.N.; Jonkman, J.M. *International Journal of Offshore
and Polar Engineering*, vol. 29, n°1, mars 2019, p. 1-9. DOI: 10.17736/ijope.2019.jc729.
OSTI ID 1524317 (preprint accepté, affilié NREL/CP-5000-68080 au sens de la consigne).

**Accès** : **texte intégral partiellement lu** (pages 1-2 : résumé, introduction, description du
modèle et de la calibration). Pages de résultats chiffrés non lues par manque de temps dans cette passe
— à compléter (chemin : fichier PDF conservé localement lors du fetch, relisible).

## Question posée
Identifier quels paramètres de modèle (hydrodynamique, aérodynamique, structure) permettent de réduire
l'écart calcul/essai observé en OC5 Phase II, par une série d'études de calibration qualitatives — sans
prétendre à une identification exhaustive de paramètres (p.1, résumé : « does not claim to be an
exhaustive parameter identification study »).

## Système modélisé
OC5-DeepCwind (cf fiche 02), modèle FAST v8 à pleine échelle (mise à l'échelle des essais bassin 1/50e).

## Outil et version
FAST v8 (NREL, 2015) — **antérieur à OpenFAST** ; à mettre en regard avec notre version épinglée
v5.0.0 pour toute transposition de paramètres de calibration (p.1).

## Réglages hydro
Modèle hybride : potentiel de diffraction/radiation (WAMIT) + traînée visqueuse de Morison ajoutée sur
tous les éléments submergés via HydroDyn (p.2). QTF somme/différence du second ordre calculées par
WAMIT, mais **intégrale de surface libre en champ lointain non évaluée** — le terme de fréquence-somme
n'est donc qu'approché (p.2, « sum-frequency potential term is only approximated here »). Coefficients
de traînée (transverses et axiaux) calés sur essais de lâcher libre ; amortissement linéaire additionnel
introduit pour caler les petites oscillations de lâcher (p.2, citant Wendt et al. 2016).

## Modèle d'ancrage
MoorDyn (dynamique), coefficients de traînée visqueux des éléments de ligne calés sur l'amplitude des
efforts au point fixe mesurés en houle régulière (p.2, citant Wendt et al. 2016 pour le détail).

## Cas de charge
Cas de calibration simples (houle seule / vent seul), puis validation sur cas combinés vent+houle plus
complexes (résumé, p.1).

## Résultats chiffrés clés
**Non lus dans cette passe** (pages suivantes non extraites). Ouvert pour complément.

## Ce que l'article dit explicitement ne pas expliquer
p.1 (résumé) : l'étude ne revendique pas une identification exhaustive des paramètres, et vise la
description de l'impact QUALITATIF des différents paramètres plutôt qu'une quantification complète.

## Reproductible avec nos moyens ?
**Partiel.** Les choix de calibration (amortissement additionnel, coefficients de traînée Morison,
traitement MoorDyn) sont directement transposables à notre modèle v5.0.0/SeaState+HydroDyn, mais nous
n'avons pas (faute d'accès à `/mnt/e`) les données d'essai brutes de calage. Reproductible comme
MÉTHODE (quelle calibration appliquer), pas comme comparaison chiffrée directe sans les données MARIN.
