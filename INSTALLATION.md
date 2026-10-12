# Installation et premiers calculs

Ce document est écrit pour quelqu'un qui n'a **jamais vu OpenFAST**. Suivez-le dans l'ordre.

## 1. Installer l'environnement (sans droits administrateur)

Les machines de l'école n'ont pas de droits administrateur — tout s'installe dans votre dossier
personnel, rien ne touche au système.

```bash
git clone <adresse du dépôt donnée en séance>
cd S9-GM-FOWT-DeepCwind
bash env/install.sh
```

Ce script installe `micromamba` (un gestionnaire d'environnements, comme `conda` mais plus léger)
dans `~/.local`, puis crée un environnement `s9gm-fowt` contenant OpenFAST, le compilateur Fortran
et les outils Python nécessaires. **Comptez 5 à 15 minutes** selon votre connexion (téléchargement
d'environ 300-400 Mo).

À chaque nouvelle session de terminal, avant de travailler :
```bash
micromamba activate s9gm-fowt
```

### Vérification obligatoire

```bash
openfast -v
```

Doit afficher une ligne contenant **`OpenFAST-v5.0.0`**. Si ce n'est pas le cas (autre version,
ou commande introuvable), **ne continuez pas** : reprenez l'installation, ou voir
« En cas d'échec » plus bas.

## 2. Compiler le contrôleur (une fois par clone)

Le contrôleur de l'éolienne (qui pilote le calage des pales et le couple du générateur) est un
petit programme Fortran. Pour des raisons de licence et de reproductibilité, **aucun binaire
compilé n'est suivi dans ce dépôt** — vous le compilez vous-même, en quelques secondes :

```bash
bash scripts/build_discon.sh
```

À refaire après chaque nouveau `git clone` (mais pas à chaque session : le fichier compilé reste
sur votre disque tant que vous ne supprimez pas le dépôt).

## 3. Premier calcul : les cas d'échauffement E01 et E02

Depuis la racine du dépôt, environnement activé :

```bash
bash cas/run_cas.sh E01
bash cas/run_cas.sh E02
```

Si tout va bien, chaque calcul se termine par `OK en NN s` et produit un fichier `main.outb` (les résultats, au format
binaire OpenFAST) dans `results/E01/` et `results/E02/` (copies des cas de référence, que le lanceur crée) ; `results/E01/run.log` se termine par `OpenFAST terminated normally.`. Ces deux cas sont
rapides (quelques secondes à quelques dizaines de secondes). Les cas suivants (F01 et suivants) utilisent le contrôleur
compilé à l'étape 2.

## 4. La suite

Pour la séance 0a, suivez [`seances/0a/README.md`](seances/0a/README.md) : c'est une consigne autonome, de l'installation
jusqu'aux cas F01 et F02. Le [`README.md`](README.md) de la racine donne la carte du dépôt et le parcours séance par séance.

## 5. Animation (facultatif) : ParaView et ffmpeg

Seule fonction de ce dépôt qui sorte de l'environnement `s9gm-fowt` : l'animation d'un calcul
(`s9gm.visu.animer`, voir `s9gm/ANIMER.md`) appelle deux programmes **du système**, `pvbatch`
(ParaView) et `ffmpeg`. Rien n'est à installer dans l'environnement Python. Ces deux paquets
s'installent avec `apt`, donc **avec les droits administrateur** : sur votre machine personnelle,
ou en demandant à l'administrateur de la salle. Sans eux, tout le reste du dépôt fonctionne.

Ubuntu 24.04 et 26.04 (mêmes commandes ; 24.04 livre ParaView 5.11, 26.04 livre ParaView 6.0) :

```bash
sudo apt update
sudo apt install paraview ffmpeg
```

Vérification (les trois commandes doivent répondre, sans message d'erreur) :

```bash
pvbatch --version && ffmpeg -version | head -1 && ffprobe -version | head -1
```

Doit afficher une ligne `paraview version 5.11…` ou `6.0…`, puis deux lignes `ffmpeg version …` et
`ffprobe version …`. Si l'une manque, `s9gm.visu.animer` s'arrête avec un message qui renvoie ici.

## En cas d'échec

- **`openfast: command not found`** après `micromamba activate s9gm-fowt` : l'environnement n'a
  pas été créé correctement. Relancez `bash env/install.sh`. Si l'erreur persiste, notez le
  message d'erreur exact (copier-coller) pour la séance.
- **`openfast -v` affiche une version différente** : vous avez peut-être un autre OpenFAST déjà
  installé sur le système, qui passe avant celui de l'environnement. Vérifiez avec
  `which openfast` : le chemin doit contenir `micromamba/envs/s9gm-fowt`.
- **Le contrôleur ne charge pas** (« could not be loaded ») : avez-vous bien lancé
  `bash scripts/build_discon.sh` depuis la racine du dépôt, avec l'environnement activé ?
- **Toute demande de mot de passe / `sudo`** : c'est anormal pour les sections 1 à 4 — arrêtez-vous et
  signalez-le, rien ici ne doit nécessiter les droits administrateur. Seule exception : la
  section 5 (animation, facultative), qui installe deux paquets du système.
- Si rien ne fonctionne avant la séance 0b : terminez l'installation en salle C09, et notez
  l'erreur exacte dans votre rendu R0 (point de contrôle de la phase 0).

## Licences et attributions

Voir `PROVENANCE.md`. En résumé : modèle de référence et contrôleur sous licence Apache 2.0
(projet [OpenFAST](https://github.com/OpenFAST/openfast)) ; tutoriel LHEEA sous licence Apache 2.0
([openfast_quickstart](https://gitlab.in2p3.fr/lheea/oracle/tutorials/openfast_quickstart)), avec
attribution dans `annexes/lheea/NOTICE`.
