# Le terminal en une page

Vous n'avez pas besoin de savoir programmer en shell pour faire tourner les calculs : seulement savoir **où vous êtes** et **ce que vous lancez**. Les lignes qui commencent par `$` se tapent ; on ne tape pas le `$`.

## Où suis-je ? Que contient ce dossier ?
```bash
$ pwd
$ ls
```
`pwd` affiche le dossier courant, `ls` son contenu. Une erreur « fichier introuvable » vient presque toujours d'un chemin relatif lu depuis un autre dossier que celui qu'on croit.

## Se déplacer
```bash
$ cd ~/S9-GM-FOWT-DeepCwind
$ cd seances/0a
$ cd ..
$ cd ~
```
`~` est votre dossier personnel, `..` le dossier parent. Remplacez `~/S9-GM-FOWT-DeepCwind` par l'endroit où vous avez cloné le dépôt.

## Chemin absolu, chemin relatif
Un chemin **absolu** commence par `/` ou `~` et désigne le même fichier depuis n'importe où ; un chemin **relatif** se lit à partir du dossier courant.
```bash
$ ls ~/S9-GM-FOWT-DeepCwind/seances/0a
$ cd ~/S9-GM-FOWT-DeepCwind && ls seances/0a
```
Les deux lignes affichent la même chose. **Les fonctions de `s9gm` lisent un chemin relatif à partir de la racine du dépôt** (`results/...`, `data/...`) : vous pouvez les lancer depuis n'importe quel dossier.

## Activer l'environnement
À faire dans **chaque nouveau terminal** :
```bash
$ micromamba activate s9gm-fowt
$ python -c "import s9gm; print(s9gm.__file__)"
```
La seconde ligne affiche d'où vient `s9gm` : ce doit être le clone que vous utilisez. Pour une session Python interactive, tapez `python` (on en sort avec `exit()`), pour un carnet `jupyter notebook` : les deux se lancent depuis n'importe quel dossier.

## Quand ça coince
```bash
$ s9gm doctor
```
`s9gm doctor` vérifie votre poste point par point et écrit **la commande exacte** à taper pour chaque point à corriger. Si la commande `s9gm` est introuvable, l'environnement n'est pas activé (voir plus haut).

## Un message d'erreur
Copiez-le **en entier**, de la première à la dernière ligne, et lisez d'abord la **dernière** : c'est elle qui dit ce qui s'est passé (`FileNotFoundError`, `ModuleNotFoundError`, `KeyError`, …) ; les lignes au-dessus disent où. Notez la commande que vous aviez tapée et le résultat de `pwd`.
