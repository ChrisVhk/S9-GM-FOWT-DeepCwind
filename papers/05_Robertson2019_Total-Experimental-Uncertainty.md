# Robertson, Bachynski, Gueydon, Wendt, Schünemann (2019) — Total Experimental Uncertainty in Hydrodynamic Testing of a Semisubmersible Wind Turbine, Considering Numerical Propagation of Systematic Uncertainty

**Référence complète** : *Ocean Engineering*, publié en ligne le 13 décembre 2019. OSTI ID 1580490.
Auteurs : Amy Robertson (NREL), Erin E. Bachynski (NTNU), Sebastien Gueydon (MARIN), Fabian Wendt
(NREL), Paul Schünemann (Universität Rostock).

**Accès** : **texte intégral lu** (pages 1-3 et 24-31 sur 35, via PDF récupéré sur `osti.gov` —
accessible sans détour par `nrel.gov`). Toutes les valeurs ci-dessous portent leur ligne/figure source.

## Question posée
Quantifier l'incertitude expérimentale TOTALE (systématique + aléatoire) des essais hydrodynamiques sur
l'OC5-DeepCwind, pour déterminer si la sous-estimation basse fréquence observée en OC5 (Robertson et
al. 2017, fiche 03) est réelle ou se situe dans la marge d'incertitude de mesure (l.14-26).

## Système modélisé
Version simplifiée de l'OC5-DeepCwind (même flotteur, tour rigide, masse représentant le rotor-nacelle,
ancrage ressort simplifié représentant la raideur linéaire de la caténaire d'origine) — essais MaRINET2
au bassin MARIN, échelle 1/50e (l.44-51).

## Outil et version
Trois outils de simulation (FAST, SMA/aNySIM, aNySIM_PQ — variantes PQ et Morison), appliqués par 4
utilisateurs différents (l.75-76).

## Réglages hydro comparés
Approche potentiel-flow (PQ) vs Morison, sources d'incertitude systématique injectées : centre de
masse (CMx/CMz), raideur d'ancrage, tirant d'eau, diamètre de colonne, élévation de houle, inerties,
masse/flottabilité (Figure 10, l.516 — liste complète des 8 sources + aléatoire).

## Modèle d'ancrage
Ressort souple linéarisé (pas caténaire dynamique dans cette campagne simplifiée) — limite explicite
de représentativité pour la raideur basse fréquence réelle (l.48-51).

## Cas de charge
Houle régulière (2 cas), houle irrégulière, houle « bruit blanc » (l. Figure 7 légende).

## Résultats chiffrés clés
- **Incertitude PSD basse fréquence (Figure 9, l.490-496)** : amplitude totale ~30-50 % en surge, ~40 %
  en tangage (cas houle bruit blanc) ; incertitude en fréquence de houle < 20 %.
- **Sources dominantes (Figure 10, l.498-508)** : raideur/prétension d'ancrage pour le surge basse
  fréquence ; décalage du centre de masse pour le tangage. Contribution de l'incertitude ALÉATOIRE
  négligeable devant l'incertitude SYSTÉMATIQUE (l.507-508).
- **Application aux résultats OC5 (§6.4, l.541-554, Figures 13-14)** : sur les 21 résultats numériques
  de participants OC5 (Robertson et al. 2017), **UN SEUL** tombe dans l'intervalle d'incertitude
  expérimentale totale pour la métrique PSD basse fréquence en surge ; **AUCUN** ne tombe dans
  l'intervalle pour la métrique PSD basse fréquence en tangage (l.547-550). Conclusion explicite :
  « the underprediction... is larger than the experimental uncertainty » (résumé, l.25-26).

## Ce que l'article dit explicitement ne pas expliquer
l.533-534 : impossible de déterminer si l'usage de modèles d'ingénierie (vs outils haute-fidélité) donne
une estimation conservative ou non-conservative de l'incertitude totale. l.465-467 : l'incertitude du
surge moyen en houle régulière cas 1 est probablement surestimée (effet statique non isolé par un seul
outil) — réserve explicite sur la fiabilité de CE chiffre particulier.

## Reproductible avec nos moyens ?
**Oui, partiellement, et c'est notre comparaison n°2 retenue.** Nous n'avons pas la campagne d'essai
MaRINET2 simplifiée, mais nous POUVONS reproduire le calcul PSD basse fréquence sur notre propre cas
houle (irrégulière ou bruit blanc, déjà dans `models/oc4_rtest/`) et le confronter QUALITATIVEMENT à
l'ordre de grandeur publié (30-50 % / 40 %) — sans prétendre reproduire l'intervalle MARIN exact
(système différent, cf réserve fiche 02 sur OC4≠OC5).
