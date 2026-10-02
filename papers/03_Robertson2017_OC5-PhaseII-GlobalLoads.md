# Robertson et al. (2017) — OC5 Project Phase II: Validation of Global Loads of the DeepCwind Floating Semisubmersible Wind Turbine

**Référence complète** : Robertson, A.N.; Wendt, F.; Jonkman, J.M.; Popko, W.; Dagher, H.; Gueydon, S.;
Qvist, J.; Vittori, F.; Azcona, J.; Uzunoglu, E.; Guedes Soares, C. et al. *Energy Procedia*, vol. 137,
30 septembre 2017, p. [1-9 env.]. DOI: 10.1016/j.egypro.2017.10.333. OSTI ID 1416253.

**Accès** : **métadonnées et résumé seulement**. Le PDF (hébergé sur `docs.nrel.gov`) est inaccessible
(DNS, cf fiche 01) ; la redirection OSTI pour cet ID pointe vers un domaine `nlr.gov` anormal, non
suivi. Mendeley/Semantic Scholar/ResearchGate référencés mais non interrogés (hors périmètre d'accès
pour cette session). **Texte intégral non lu.**

## Question posée
Valider les modèles numériques du système flottant semi-submersible DeepCwind par comparaison aux
données de la campagne d'essai 1/50e menée au bassin MARIN (2013), dans le cadre d'IEA Wind Task 30.

## Système modélisé
OC5-DeepCwind semi-submersible (cf fiche 02), 21 jeux de résultats de participants (confirmé
indirectement par la fiche 05, qui republie les Figures 13/14 de cet article).

## Résultats chiffrés clés (connus indirectement, via la fiche 05 qui les cite et les republie)
- Sous-estimation systématique des charges ultimes et de fatigue par les outils numériques, dominée
  par la sous-estimation des charges aux fréquences propres de pilonnement/tangage et de la tour
  (cité par Robertson et al. 2019 — fiche 05 de ce dossier).
- Figure 13/14 de cet article (republiées dans la fiche 05, Figures 13-14, p.555-559 du PDF source) :
  sur 21 résultats de participants pour la métrique PSD basse fréquence en surge, un seul tombe dans
  l'intervalle d'incertitude expérimentale totale (établi a posteriori par Robertson et al. 2019) ;
  aucun résultat ne tombe dans cet intervalle pour la métrique PSD basse fréquence en tangage.
- OC6 Phase I (fiche 06) cite un ordre de grandeur de ~20 % de sous-estimation des charges globales.

## Ce que l'article dit explicitement ne pas expliquer
D'après la citation dans Robertson et al. (2019, fiche 05, lignes 35-36 du PDF) : « there were
persistent differences between the simulated results and measurements, the reasons for which could
not be ascertained » — c'est explicitement la question ouverte qui motive OC6.

## Reproductible avec nos moyens ?
**Partiel, et c'est la comparaison prioritaire du dépôt.** Nous ne pourrons pas rejouer les 21
participants, mais nous pouvons : (a) faire tourner NOTRE cas r-test (même système OC4, pas OC5 à
l'identique — cf réserve fiche 02) sur les mêmes conditions de houle que LC3.3 (citée par la fiche 05)
et comparer notre PSD basse fréquence à l'intervalle d'incertitude publié ; (b) documenter l'écart
système OC4≠OC5 comme limite de la comparaison. Retenue dans `papers/SYNTHESE.md` comme comparaison n°1.
