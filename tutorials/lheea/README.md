# Tutoriel OpenFAST Quickstart (LHEEA)

Ce dossier contient les fichiers de cas du tutoriel OpenFAST Quickstart du LHEEA (Nantes
Université — ORACLE), licence Apache 2.0 (voir `LICENSE` et `NOTICE`).

**Le récit pédagogique de ce tutoriel n'est pas ici, dans un document séparé** : il est intégré
directement dans le déroulé des séances du cours —
[`../../seances/0a/README.md`](../../seances/0a/README.md) (cas 01-02) et
[`../../seances/0b/README.md`](../../seances/0b/README.md) (cas 03-05). C'est là qu'il faut aller
pour comprendre ce que chaque cas enseigne, avec son bloc théorique et ses renvois.

Ce dossier-ci ne contient que les **fichiers de configuration** des cas (`01_TowerStructure/` à
`05_FOWT/`) et les pratiques complémentaires (`practicals/`, notebooks à trous). Pour le détail
des adaptations faites depuis la version d'origine (OpenFAST v3.2.1, Windows) vers la version de
ce dépôt (v5.0.0, Linux), voir [`ADAPTATION_LHEEA.md`](ADAPTATION_LHEEA.md).

Le document PDF original du tutoriel LHEEA (« Introduction to OpenFAST ») n'est **pas inclus dans
ce dépôt** (ce dépôt ne suit aucun PDF, voir `README.md` racine). Les renvois à ses sections (« §1 »
à « §5 », « §4.1 ») dans les séances et dans `ADAPTATION_LHEEA.md` servent de repère de traçabilité
pour la provenance de chaque contenu, pas de lien vers un document consultable ici.

**`practicals/practical2.ipynb`** : le cas `SWRT_022` qu'il utilise ne tourne pas encore (fichier
AeroDyn mal apparié, détail dans `ADAPTATION_LHEEA.md`) — la cellule qui lit `SWRT_022.out`
échouera. `practical1.ipynb` s'exécute intégralement.
