<!-- destinations: github -->
# Transition — vous aviez déjà cloné le dépôt avant le 12/10/2026

Le dépôt a été réorganisé : une consigne autonome par séance, un seul dossier de modèles, un seul outil de
post-traitement. **Si vous venez de cloner le dépôt, ignorez cette page** : tout est déjà à sa place.

Si vous aviez cloné avant, quatre gestes, dans cet ordre. Vos dossiers `results/` et `rendus/` **ne bougent pas** : git
ne les suit pas, `git pull` ne les touche pas.

## 1. Regarder l'état de votre dossier

```bash
git status
```

- **Rien sous « Changes not staged for commit »** (seulement des fichiers « Untracked », ou rien) : passez au geste 2.
- **Des fichiers « modified »** (par exemple `tutorials/prise_en_main/F01/main.fst`, que vous avez édité) : un `git pull`
  simple sera **refusé** (« Your local changes … would be overwritten »). Faites alors la recette ci-dessous **à la place**
  du `git pull` du geste 2, puis lisez le geste 4.

```bash
git stash          # met vos modifications de côté
git pull
git stash pop      # les remet, à l'emplacement des fichiers déplacés
```

Si `git stash pop` annonce un conflit, **ne forcez rien** : notez le message et demandez de l'aide en séance.

## 2. Récupérer le nouvel état

```bash
git pull
```

## 3. Recompiler le contrôleur

Git ne déplace pas les fichiers qu'il ignore : votre contrôleur compilé est resté dans l'ancien dossier `models/`. Dans le
nouvel état, le contrôleur est cherché dans `modeles/` : recompilez-le (quelques secondes), environnement activé.

```bash
micromamba activate s9gm-fowt
bash scripts/build_discon.sh
```

Si vous aviez installé le contrôleur de l'IEA 15 MW (carnet de la séance 0b) : `bash scripts/installer_rosco.sh`.

## 4. Ranger vos fichiers

Règle du nouveau parcours : **tout ce que vous créez ou modifiez vit sous `results/` ou `rendus/`** ; `cas/`, `modeles/`
et `seances/` se lisent et se lancent sans être modifiés.

- **Un fichier suivi que vous aviez modifié** (geste 1, recette `git stash`) se retrouve maintenant dans `cas/` ou
  `modeles/`. Copiez-le sous `results/` et restaurez l'original :

  ```bash
  cp -r cas/F01 results/F01_perso      # le cas que vous aviez modifié, à la même profondeur : ses chemins restent valables
  git restore cas/F01
  ```

- **Un cas que vous aviez créé** sous `tutorials/prise_en_main/` (par exemple `F03`) : déplacez-le sous `results/` et corrigez
  son chemin vers le modèle.

  ```bash
  mv tutorials/prise_en_main/F03 results/F03_perso
  sed -i 's#\.\./modele_fixe/#../../modeles/fixe/#g' results/F03_perso/main.fst
  ```

- **Votre table de cas** (par exemple `lct_0b.csv` à la racine) : `mv lct_0b.csv results/`.

Quand tout est rangé, `git status` ne doit plus montrer de fichier modifié.

## Où est passé quoi

| Avant | Maintenant |
|---|---|
| `tutorials/lheea/` | `annexes/lheea/` (référence à lire : plus aucune séance ne le lance) |
| `tutorials/prise_en_main/modele_fixe/` | `modeles/fixe/` |
| `tutorials/prise_en_main/F01`, `F02`, `run_cas.sh`, `README.md` | `cas/F01`, `cas/F02`, `cas/run_cas.sh`, `cas/README.md` |
| `tutorials/prise_en_main/PAS_A_PAS.md` | intégré aux consignes des séances [0a](seances/0a/README.md) et [0b](seances/0b/README.md) |
| `tutorials/animer.md` | `s9gm/ANIMER.md` |
| `models/` | `modeles/` |
| `cases/iea15_stationnaire/` | `cas/iea15_stationnaire/` |
| `outils/` | `annexes/outils/` (historique : le post-traitement est maintenant [`s9gm/POST-TRAITER.md`](s9gm/POST-TRAITER.md)) |
| `papers/` | `annexes/papers/` |

Les anciens dossiers `tutorials/`, `models/`, `cases/`, `outils/` et `papers/` peuvent subsister chez vous, vides de
fichiers suivis : ils ne contiennent plus que vos propres sorties ignorées par git. Vous pouvez les déplacer sous
`results/`, puis supprimer les dossiers vides.

## Mise à jour du 14/10/2026 : lancer le code depuis n'importe quel dossier

Cinq lignes, une fois par clone :
1. `git pull` (voir plus haut si git le refuse).
2. `micromamba activate s9gm-fowt`, puis, **depuis la racine de votre clone**, `pip install -e .` : le paquet `s9gm` s'installe dans l'environnement et s'importe depuis n'importe quel dossier.
3. `s9gm doctor` : il vérifie votre poste (et détecte un second clone) et donne la commande exacte pour chaque point à corriger.
4. **Vos copies `results/mon_s9gm/*.py` ne sont pas touchées** : continuez à les programmer. Les lignes `sys.path.insert(…)` des consignes disparaissent : `fatigue = ma_copie("fatigue")` charge votre fichier, **rechargé à chaque appel** (corrigez, relancez la ligne, sans redémarrer Python) ; les tests se lancent par `s9gm tester fatigue` (ou `ancrage`, `structure`).
5. `results/` et `rendus/` se créent seuls : plus de `mkdir` en tête de la phase 1. Les chemins `results/…` donnés à `s9gm` se lisent depuis la racine du dépôt, pas depuis le dossier courant.

## Mise à jour du 15/10/2026 : clarté du dépôt

| Avant | Maintenant |
|---|---|
| `seances/atelier_tour/` | `annexes/atelier_tour/` : le guide du classeur de l'atelier est une **ressource** des phases 3 et 5, plus une séance ; les renvois « §n » sont remplacés par des liens vers ses étapes |
| `annexes/historique/PAS_A_PAS_2026-10-12.md` | retiré du dépôt public : ses étapes sont dans les consignes des séances [0a](seances/0a/README.md) et [0b](seances/0b/README.md) depuis le 12/10 |
| le tableau du parcours répété dans `ENONCE.md` | un seul tableau, dans le [`README.md`](README.md#le-parcours-phase-par-phase) |
| `annexes/outils/lire_outb.py` et `annexes/outils/exemple_chaine.py` | retirés du dépôt public : `s9gm.lire` et les consignes des phases les remplacent ; `annexes/outils/` ne garde que deux scripts de provenance des données |
| `s9gm/POST-TRAITER.md` § 6 (dossier `results/fatigue_maison/`, `sys.path.insert`) | aligné sur la phase 3 : `s9gm copie fatigue`, copie sous `results/mon_s9gm/` |
| (nouveau) | [`fiches/README.md`](fiches/README.md) : l'index de la théorie, par phase |

Aucun contenu de consigne, de calcul ou de barème ne change. Si vous aviez ouvert l'ancien emplacement de l'atelier ou le pas-à-pas, `git pull` suffit : ils ne contenaient aucun fichier à vous.

