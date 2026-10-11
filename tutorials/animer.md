<!-- destinations: github -->
# Animer un calcul — `s9gm.visu.animer`

Une animation montre ce que la structure *fait* pendant un calcul : le rotor tourne, la tour fléchit,
la surface libre passe. Elle sert à repérer un mouvement incohérent avant de lire un canal. Ce
n'est **pas** une validation du modèle : c'est une cinématique calculée (voir le bloc Théorie de
`s9gm/_rendu_vtk.py`, rubrique 4).

L'exemple ci-dessous est un cas à vent uniforme (`modele_fixe`, sans turbulence), sur 10 s, avec
un vent choisi pour l'exemple, qui n'est pas celui d'un cas du tutoriel : il ne montre que la mise en
route d'un calcul et ne répond à aucune question notée.

**Prérequis** : `pvbatch` et `ffmpeg` installés — voir `INSTALLATION.md`, section 5. Sans eux, `animer`
s'arrête avec un message qui y renvoie. Environnement `s9gm-fowt` activé, contrôleur compilé
(`bash scripts/build_discon.sh`).

## 1. Un cas court avec sortie VTK

Depuis la racine du dépôt :

```bash
mkdir -p results/animation
printf 'cas,fst.TMax,inflow.WindType,inflow.HWindSpeed,inflow.PLExp\nANIM,10,1,8.2,0.11\n' \
  > results/animation/lct.csv
python - <<'PY'
from s9gm import cas, lancer, visu
d = cas.generer_serie("results/animation/lct.csv", "tutorials/prise_en_main/modele_fixe",
                      "results/animation", executer_turbsim=False)[0]
visu.preparer_animation(d, vtk_type=1, vtk_fps=5)   # WrVTK = 2, surfaces, 5 images par seconde
lancer.lancer_cas(d)
PY
```

`preparer_animation` ne change que trois lignes du `main.fst` du cas : `WrVTK`, `VTK_type`, `VTK_fps`.
`VTK_type = 1` dessine des surfaces ; `2` (lignes et points, `Ln2Mesh`) est le repli si les surfaces échouent.

**Volume — à mesurer avant de lancer plus long.** Les fichiers VTK sont volumineux : une dizaine de
maillages, un fichier par maillage et par image. Après le calcul : `du -sh results/animation/ANIM/vtk`.
Sur ce cas (10 s, 5 images par seconde), on est de l'ordre de la centaine de Mo ; le volume est
proportionnel à la durée simulée et à `VTK_fps`.

## 2. Une commande : images puis vidéo

```bash
python -m s9gm.visu animer results/animation/ANIM results/animation/ANIM.mp4 \
  --cas ANIM --modele modele_fixe --etat "rejoué le JJ/MM"
```

`--cas`, `--modele` et `--etat` sont obligatoires : ils composent la ligne de provenance incrustée
dans **chaque image**. Les images sont dans `results/animation/ANIM_images/`, la vidéo
(`H.264`, `yuv420p`, lisible par PowerPoint et VLC) dans `results/animation/ANIM.mp4`. La vidéo dure
`images / VTK_fps` secondes : temps réel.

Chaque étape s'appelle aussi seule : `visu.preparer_animation`, `visu.rendre`, `visu.monter`.

## 3. Ce qu'il faut regarder, et ce qu'il ne faut pas conclure

- **Avant** de regarder : de combien de degrés le rotor tourne-t-il entre deux images ? C'est `Ω / VTK_fps`
  (`Ω` en rad/s, lu dans `RotSpeed` du cas, ou prévu par la fiche F1). Trois pales identiques redonnent la
  même image tous les 120° : au-delà de **60°** par image le rotor paraît déjà tourner à l'envers, et à
  120° il paraît immobile. C'est un repliement de l'échantillonnage (Shannon), pas un défaut du
  calcul. Augmentez `VTK_fps`, en gardant `1 / (VTK_fps·DT)` entier (OpenFAST arrondit à un multiple de `DT`).
- **Une pièce en CORAIL** (orange) est un maillage que `s9gm` ne connaît pas (ligne d'ancrage, plateforme,
  autre) : il est dessiné tel que calculé, sans rien supposer de lui ; regardez-le avec prudence. Le gris
  est réservé à la ligne de provenance.
- **Amplification** : `amplification=N` (`--amplification N` en ligne de commande) exagère les déplacements
  de la tour et de la sous-structure, **depuis l'image 0** (un décalage déjà présent à l'image 0 n'est pas
  amplifié). Elle n'est acceptée que si tous les maillages de la série sont ceux vérifiés sur
  `modele_fixe` (pales, moyeu, nacelle, tour, Morison, surface libre) : avec un maillage d'ancrage,
  de plateforme ou de lignes (`VTK_type = 2`), `animer` s'arrête avant tout rendu et nomme les
  maillages en cause ; `N = 1` reste toujours possible. Elle est écrite sur chaque image (« déplacements ×N ») : une
  animation amplifiée donne une idée fausse des proportions.
- Ni la vidéo ni les fichiers VTK ne sont versionnés : `results/` est ignoré par git. Ne les ajoutez pas.
