# Environnement du cours

Voir le `README.md` à la racine du dépôt pour l'installation complète (sans droits
administrateur). En résumé :

```
bash env/install.sh
micromamba activate s9gm-fowt
bash scripts/build_discon.sh
openfast -v   # doit afficher OpenFAST-v5.0.0
```

## Pourquoi ces choix

- **`openfast=5.0.0=hd1f9c02_2`** : build conda-forge épinglé exactement (même build que celui
  validé et utilisé pour produire les résultats de référence de ce cours). Une version différente
  peut donner des résultats légèrement différents (précision numérique) — toujours vérifier
  `openfast -v`.
- **`fortran-compiler`** : fournit `gfortran` DANS l'environnement conda, pas besoin d'en installer
  un sur le système (impossible sans droits administrateur sur les machines de l'école).
- **`openfast_toolbox`** épinglé à un commit GitHub précis (pas sur PyPI sous ce nom) : pour que
  tout le monde utilise exactement le même code de lecture des fichiers `.outb`.
- **`turbsim`** : installé automatiquement avec le paquet `openfast` (même distribution
  conda-forge) — pas une dépendance séparée.
