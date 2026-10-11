<!-- destinations: github -->
# Animer un calcul — `s9gm.visu.animer`

Une animation montre ce que la structure *fait* pendant un calcul, surtout ce qui bouge assez pour se voir : le
rotor qui tourne. Elle sert à repérer un mouvement incohérent avant de lire un canal. Ce n'est **pas**
une validation du modèle : c'est une cinématique calculée (voir le bloc Théorie de `s9gm/_rendu_vtk.py`, rubrique 4).

**Ce que l'exemple ci-dessous montre, et ce qu'il ne fait que contenir.** La vidéo **montre** le **rotor qui tourne**
(l'azimut de la pale 1, lu dans la série VTK, égale le canal `Azimuth`). Deux autres grandeurs sont **justes dans le
fichier VTK** (mesurées contre les canaux du même calcul par les tests `FA-3` et `FA-8b` de `s9gm/tests/`) mais ne sont
**pas lisibles à l'écran** : le calage des pales (égal à `BldPitch1`, il varie à peine pendant la fenêtre, et la pale à
pas nul de référence n'est pas dans la fenêtre) et le déplacement du sommet de tour (égal à celui des canaux, de
l'ordre de quelques pixels à l'échelle 1 : à lire sur les courbes, ou à exagérer avec `amplification`).

L'exemple est un cas à vent uniforme dans la région de fonctionnement où le régulateur limite la puissance
(Region 3, fiche F1), sur le `modele_fixe`. Il ne répond à aucune question notée et n'en donne aucune valeur.

**Prérequis** : `pvbatch` et `ffmpeg` installés — voir `INSTALLATION.md`, section 5. Sans eux, `animer`
s'arrête avec un message qui y renvoie. Environnement `s9gm-fowt` activé, contrôleur compilé
(`bash scripts/build_discon.sh`).

## 1. Un cas où le rotor tourne, avec sortie VTK

Le `modele_fixe` démarre rotor à l'arrêt : en 10 s il ne tournerait presque pas, et l'animation ne montrerait qu'une
mise en charge de la tour. On part donc du **régime nominal publié** (`ENONCE.md`, §4 : 12,1 tr/min), par une copie
d'ElastoDyn propre au cas — le fichier partagé du tutoriel n'est jamais modifié —, avec un vent de 15,4 m/s ; le pas
initial reste à 0 : c'est le régulateur qui trouve le sien.

Depuis la racine du dépôt :

```bash
mkdir -p results/animation
printf 'cas,fst.TMax,inflow.WindType,inflow.HWindSpeed,inflow.PLExp,elastodyn.RotSpeed\nREGIME3,31.2,1,15.4,0,12.1\n' \
  > results/animation/lct.csv
python - <<'PY'
from s9gm import cas, lancer, visu
d = cas.generer_serie("results/animation/lct.csv", "tutorials/prise_en_main/modele_fixe",
                      "results/animation", executer_turbsim=False)[0]
visu.preparer_animation(d, vtk_type=1, vtk_fps=5)   # WrVTK = 2, surfaces, 5 images par seconde
lancer.lancer_cas(d)
PY
```

`cas` écrit `RotSpeed` dans une copie `config_elastodyn.dat` du dossier du cas (colonne `elastodyn.RotSpeed`) et
relit le fichier produit. `preparer_animation` ne change que trois lignes du `main.fst` : `WrVTK`, `VTK_type`,
`VTK_fps`. `VTK_type = 1` dessine des surfaces ; `2` (lignes et points) est le repli si les surfaces échouent.

**Volume — à mesurer avant de lancer plus long.** OpenFAST écrit la série VTK **depuis t = 0** : on ne peut pas ne
l'écrire que sur la fenêtre. À 5 images par seconde, une dizaine de maillages et ≈ 1 Mo par fichier de pale, on
compte de l'ordre de 17 Mo par seconde simulée : choisissez un `TMax` juste suffisant (début de fenêtre + durée voulue).
Après le calcul : `du -sh results/animation/REGIME3/vtk`.

## 2. Choisir la fenêtre : après le transitoire

Au début du calcul, le régulateur amène la machine vers son régime : ce n'est pas la fenêtre à animer. Comme pour
`t_transitoire` dans `s9gm.lire.statistiques`, le début se choisit par un **critère écrit avant de regarder la
courbe** ; `lire.debut_regime` l'applique : vitesse à 2 % du nominal **et** calage stable à 0,5° près sur les
5 s suivantes. `animer` arrondit ce début à l'image VTK suivante. Rien n'est à lire ni à recopier : le début est
passé tel quel à `fenetre=`.

## 3. Images puis vidéo

```bash
python - <<'PY'
from s9gm import lire, visu
d = "results/animation/REGIME3"
df, _ = lire.lire(d + "/main.outb")
debut = lire.debut_regime(df, nominal=12.1, tol_rel=0.02, stab_pas=0.5, duree=5.0)
visu.animer(cas="REGIME3", modele="modele_fixe", etat="rejoué le JJ/MM", dossier_cas=d,
            sortie=d + ".mp4", fenetre=(debut, df["Time"].iloc[-1]))
PY
```

Le même appel existe en ligne de commande, avec l'option `--fenetre` suivie des deux instants si vous les connaissez déjà :
`python -m s9gm.visu animer DOSSIER_CAS SORTIE.mp4 --cas … --modele … --etat … --fenetre …`.

`cas`, `modele` et `etat` sont obligatoires : ils composent la ligne de provenance incrustée dans **chaque
image**. `fenetre` ne rend que les images de l'intervalle ; sans lui, toute la série. L'horloge `t = …` en haut à
gauche est le **temps du calcul**, jamais le temps depuis le début de la fenêtre. Les images sont dans
`results/animation/REGIME3_images/`, la vidéo (`H.264`, `yuv420p`, lisible par PowerPoint et VLC) dans
`results/animation/REGIME3.mp4`, et dure `images / VTK_fps` secondes : temps réel.

Chaque étape s'appelle aussi seule : `visu.preparer_animation`, `visu.rendre`, `visu.monter` ; en Python,
`visu.animer(..., fenetre=(t_debut, t_fin))`.

## 4. Légende des couleurs, et ce qu'il ne faut pas conclure

- **Couleurs** : pales TEAL (vert), moyeu MARINE (bleu foncé), **tour et nacelle PALE (gris-bleu très clair)
  bordées d'un contour MARINE** (en mode lignes, `VTK_type = 2` : MARINE, sans contour), sous-structure TEALD, surface libre LIGHT (bleu clair). Une pièce en **CORAIL**
  (orange) est un maillage que `s9gm` ne connaît pas (ligne d'ancrage, plateforme, autre) : il est dessiné tel que
  calculé, sans rien supposer de lui ; regardez-le avec prudence. Le gris est réservé à la ligne de provenance. Le
  contour est un artifice de rendu : il épaissit la tour et la nacelle de 30 % de leur rayon environ, il ne dit rien de
  la géométrie.
- **Avant** de regarder : de combien de degrés le rotor tourne-t-il entre deux images ? C'est `Ω / VTK_fps`
  (`Ω` en rad/s : `RotSpeed` du cas, en tr/min, × 2π/60 ; ou prévu par la fiche F1). Trois pales identiques redonnent la
  même image tous les 120° : au-delà de **60°** par image le rotor paraît déjà tourner à l'envers, et à
  120° il paraît immobile. C'est un repliement de l'échantillonnage (Shannon), pas un défaut du
  calcul. Augmentez `VTK_fps`, en gardant `1 / (VTK_fps·DT)` entier (OpenFAST arrondit à un multiple de `DT`).
- **Amplification** : `amplification=N` (`--amplification N` en ligne de commande) exagère les déplacements
  de la tour et de la sous-structure, **depuis l'image 0** (un décalage déjà présent à l'image 0 n'est pas
  amplifié). Elle n'est acceptée que si tous les maillages de la série sont ceux vérifiés sur
  `modele_fixe` (pales, moyeu, nacelle, tour, Morison, surface libre) : avec un maillage d'ancrage,
  de plateforme ou de lignes (`VTK_type = 2`), `animer` s'arrête avant tout rendu et nomme les
  maillages en cause ; `N = 1` reste toujours possible. Elle est écrite sur chaque image
  (« déplacements ×N ») : une animation amplifiée donne une idée fausse des proportions.
- Ni la vidéo ni les fichiers VTK ne sont versionnés : `results/` est ignoré par git. Ne les ajoutez pas.
