# Données du projet

| Fichier | Contenu | Statut |
|---|---|---|
| `geometrie_deepcwind.md` | Dimensions, membres, masse/inerties, ancrage de la DeepCwind | Fait (sourcé) |
| `section_tour.md` | Section de tour en pied (D, t, I, module de flexion) | **Ouvert** — à compléter |
| `iea15_wisdem_performance.csv` | Courbes de fonctionnement idéalisées de l'IEA 15 MW (V, calage, P, Ω, T, Cp, Ct), feuille « Rotor Performance » du classeur du dépôt `IEA-15-240-RWT` ; sert de référence « publiée » au carnet 0b | Fait (sourcé, `PROVENANCE.md`) |
| `iea15_openfast_stationnaire.csv.gz` | Séries temporelles (600 s, pas de 0,1 s) des six cas IEA 15 MW à vent stationnaire, lues par `s9gm.lire` (`outils/exporter_iea15_stationnaire.py`) ; jeu livré du carnet 0b | Fait (produit par `cases/iea15_stationnaire/lct.csv`) |
| `metocean/` | Table conjointe vent (100 m) × Hs × Tp × désalignement du site West of Barra (réanalyse ERA5, 1979-2000), probabilités, avec ses métadonnées. **Source : Papi F., Perignon Y., Bianchini A., Zenodo [10.5281/zenodo.10102696](https://doi.org/10.5281/zenodo.10102696), v1.1.0, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) (projet FLOATECH, UE 101007142), fichiers renommés non modifiés.** Lue par `s9gm.metocean` | Fait (sourcé, `PROVENANCE.md`) |
| `periodes_lacher_reference.md` | Périodes propres publiées (OC4/OC5) pour comparaison aux lâchers | **Ouvert** — LOT E |

La table metocean de `data/metocean/` (FLOATECH, CC BY 4.0) est le jeu de travail du module `s9gm.metocean` ; ne la reconstruisez pas vous-mêmes.

Toute valeur sans source exacte (document, tableau, page) et marquée « hypothèse » doit être
vérifiée avant d'être utilisée dans un calcul qui compte pour un rendu.
