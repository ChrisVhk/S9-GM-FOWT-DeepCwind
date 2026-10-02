# Ce qui distingue OC5 d'OC4 (pour construire ce dossier plus tard)

Dossier vide : aucun modèle OC5 construit dans ce dépôt pour l'instant (travail enseignant à venir,
hors périmètre du projet étudiant actuel).
Source : `papers/02_Robertson_OC5-DeepCwind-Definition.md` (document de définition OC5, lu intégralement).

## Différences constatées, sourcées

1. **Turbine différente** (`papers/02_*.md`, p.5). La turbine testée en 2013 (OC5) reproduit la
   poussée/couple/puissance du NREL 5 MW à l'échelle 1/50 ; celle testée en 2011 (OC4, notre
   `models/oc4_rtest/`) n'était qu'une mise à l'échelle GÉOMÉTRIQUE du NREL 5 MW, sans reproduire son
   comportement aérodynamique. **Ce n'est donc pas la même turbine** — construire OC5 n'est pas un
   simple ajustement de la plateforme OC4 existante, il faut une nouvelle définition de rotor.
2. **Ancrage quasi identique, pas rigoureusement** (`papers/02_*.md`, Tableau 3-13). Longueur non
   tendue 835.5 m (OC5) vs 835.35 m (r-test/OC4) — écart de 0.15 m à vérifier s'il est significatif ou
   un simple arrondi de publication.
3. **Géométrie de plateforme** : les cotes de colonnes/pontons du document OC5 (Tableaux 3-10/3-11)
   n'ont pas été comparées chiffre à chiffre à celles du cas r-test dans cette passe — à faire avant de
   construire quoi que ce soit ici (comparaison directe, pas une supposition d'identité).
4. **Données hydro WAMIT** : `models/oc4_rtest/.../marin_semi.*` provient de r-test (tag v5.0.0) ; le
   document OC5 ne fournit pas ces fichiers lui-même (ils vivent dans des fichiers WAMIT séparés,
   référencés mais non inclus dans le PDF de définition). À vérifier si r-test's `marin_semi.*` est la
   version OC4 ou déjà la version OC5 (le nom de fichier est identique entre les deux cas dans le dépôt
   LHEEA) — **point à trancher avant de construire OC5**, pas supposé.

## Ce qu'il faudrait pour construire ce dossier
- Les fichiers WAMIT spécifiques OC5 (si différents de ceux déjà dans `models/oc4_rtest/`) — chercher
  sur le Wind Data Hub (`wdh.energy.gov/ds/oc5/oc5.phase2`), non récupérés dans cette passe.
- La définition de turbine OC5 (rotor mis à l'échelle en performance, pas en géométrie seule).
- Décision de l'enseignant : construire OC5 a-t-il un intérêt pédagogique suffisant vu l'écart avec
  l'OC4 déjà validé, ou le cours s'appuie-t-il sur OC4 en citant les résultats OC5 comme référence
  externe (cf `papers/SYNTHESE.md`, comparaisons 1 et 3) ? Question posée à l'enseignant dans le rapport.
