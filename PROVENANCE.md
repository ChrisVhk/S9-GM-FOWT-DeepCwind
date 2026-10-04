# Provenance et licences

Ce dépôt assemble du code et des données de plusieurs origines. Voici, pour chaque dossier, d'où
il vient et sous quelle licence.

## `models/oc4_rtest/`
Origine : [OpenFAST/r-test](https://github.com/OpenFAST/r-test), tag `v5.0.0`
(SHA `dd5feaaaa500ba7283140107806300d551cff0a7`), cas `5MW_OC4Semi_WSt_WavesWN` et fichiers partagés
de `5MW_Baseline/`. **Licence Apache 2.0** (comme le dépôt [OpenFAST/openfast](
https://github.com/OpenFAST/openfast) dont il dépend). Repris tel quel, seuls les fichiers
effectivement lus par le cas de référence sont inclus (pas de BeamDyn, pas de champ de vent
turbulent pour ce cas précis).

## `tutorials/lheea/`
Origine : [openfast_quickstart](https://gitlab.in2p3.fr/lheea/oracle/tutorials/openfast_quickstart)
(LHEEA, Nantes Université — ORACLE), commit `6040b6430bba78d3906877f2ea4d3effe3a4eb5e`.
**Licence Apache 2.0** — voir `tutorials/lheea/LICENSE` et `tutorials/lheea/NOTICE` pour le résumé
des modifications, et `tutorials/lheea/ADAPTATION_LHEEA.md` pour le détail cas par cas (migration
v3.2.1→v5.0.0, Windows→Linux), prêt à être transmis au LHEEA. Reprise faite avec l'accord de
l'enseignant du cours, membre du LHEEA (cluster Cargo, ED SPIN/ENSTA Bretagne), qui proposera
ensuite cette adaptation au laboratoire. Le récit pédagogique des 5 cas est intégré directement
dans `seances/0a/` et `seances/0b/` du cours (pas un document séparé) ; chaque section reprise y
porte son attribution et un renvoi vers `tutorials/lheea/NOTICE`.

## `tutorials/prise_en_main/`
Construit pour ce cours, à partir des modèles ci-dessus (licence Apache 2.0 des sources) et d'une
progression inspirée d'un cours de Master Génie Maritime (2013) sur les outils de conception
éolien — adaptée ici en OpenFAST v5.0.0, pas une reproduction du document source.

## `models/oc5/`
Dossier vide + `NOTE.md`, écrit pour ce dépôt à partir du document public de définition OC5 (voir
`papers/02_*.md`) — pas de fichier de modèle OC5 construit à ce jour.

## `papers/`
Fiches de lecture écrites pour ce dépôt, sourcées sur des publications publiques (OC4/OC5/OC6,
références DOI/OSTI/HAL dans chaque fiche) — aucun PDF source inclus, aucune reproduction de texte
au-delà des relations/valeurs chiffrées citées avec leur page.

## `env/`, `scripts/`, `outils/`, `ENONCE.md`, `seances/`, `README.md`, `INSTALLATION.md`, `data/`
Écrits pour ce dépôt.

## `fiches/`
Source de vérité : `Cours/DMO-S9_Fondations-Structures/Fiches/` du dépôt de cours (privé). Copiées
ici telles quelles pour que les étudiants y accèdent sans avoir accès à ce dépôt privé.

## DISCON (contrôleur)
Les fichiers `DISCON.F90` / `DISCON_OC3Hywind.F90` (sources du contrôleur) proviennent du dépôt
OpenFAST (tag v5.0.0, licence Apache 2.0). **Aucun binaire compilé (`.so`) n'est suivi dans ce
dépôt** : chacun compile le sien avec `scripts/build_discon.sh` (voir le README).

## `models/iea15_monopile/`
Origine : [IEAWindTask37/IEA-15-240-RWT](https://github.com/IEAWindTask37/IEA-15-240-RWT), commit
`e4993d63de10f165389534461dd544006750fe60` (ReleaseNotes v1.1.6), dossiers `OpenFAST/IEA-15-240-RWT/`
(éléments communs) et `OpenFAST/IEA-15-240-RWT-Monopile/` (variante monopieu, contrôleur ROSCO). Modèle de
référence décrit dans Gaertner et al. 2020, NREL/TP-5000-75698. **Licence Apache 2.0** (`LICENSE` copié dans
le dossier). Variante monopieu retenue (pas le flotteur) : modèle de **la machine seule**, sans houle ni
hydrodynamique dans les cas de la séance 0b : le monopieu, lui, reste élastique (SubDyn actif, `CompSub = 1`) mais sans masse ajoutée ni charge hydrodynamique.

Vérifié le 05/10 (INV-18), pas présumé :
- **Compatibilité OpenFAST v5.0.0 — NON : les fichiers amont ne se lisent pas tels quels.** Ils suivent
  l'ancien format d'entrée ; OpenFAST v5.0.0 s'arrête sur chacun des cinq fichiers suivants. Dérivation,
  champs **ajoutés** (valeur neutre ; repérés par `[s9gm: …]` dans ElastoDyn, AeroDyn, SubDyn et ServoDyn, mais pas dans `main.fst`) ou **retirés** :
  `main.fst` (reconstruit sur la trame v5 : `ModCoupling`, `RhoInf`, `ConvTol`, `MaxConvIter`, `NRotors`,
  `CompSoil`, `MirrorRotor`, `SoilFile` ; valeurs amont conservées ; renommé en `main.fst`, `InflowFile`
  pointe vers `config_inflow.dat` copie de `IEA-15-240-RWT_InflowFile.dat`, `BDBldFile` = `"unused"`) ;
  `ElastoDyn` (+ `PitchDOF`, `PtfmRefxt/yt`, `PBrIner(1-3)`, `BlPIner(1-3)`, `BldFile1-3` → `BldFile(1-3)`) ;
  `AeroDyn15` (− `Buoyancy`, + colonnes `TwrCp`, `TwrCa` du tableau de tour, `BldNd_BladesOut` = 0 pour
  alléger les sorties) ; `SubDyn` (+ bloc `INITIAL RIGID-BODY POSITION`, + colonne `TPID` des joints
  d'interface) ; `ServoDyn` (+ `PitNeut`, `PitSpr`, `PitDamp` ×3, `DLL_FileName` → `../ServoData/libdiscon.so`).
  **Diff contre l'amont** (commit `e4993d6`, `diff -w`, fait le 05/10 ; sont **identiques** à l'amont (`diff`) : `ElastoDyn_tower`, `HydroDyn`, `SeaState`, `ROSCO.yaml`, `config_inflow.dat` (= `IEA-15-240-RWT_InflowFile.dat`), `IEA-15-240-RWT_ElastoDyn_blade.dat`, `IEA-15-240-RWT_AeroDyn15_blade.dat`, `Cp_Ct_Cq.IEA15MW.txt` et tout `Airfoils/`. La sortie des `diff` n'est pas versionnée : la preuve se rejoue contre le commit amont). Chaque ligne modifiée est classée *format* (clé renommée, ligne ou colonne ajoutée avec une valeur neutre, chemin, option de sortie) ou *physique* (valeur d'un paramètre de la machine changée) :

| Fichier | Lignes modifiées | Classe |
|---|---|---|
| `main.fst` (comparaison clé par clé) | `BDBldFile(1-3)` → `"unused"` (BeamDyn non utilisé, `CompElast = 1`) ; `InflowFile` → `config_inflow.dat` ; ajoutés : `ModCoupling = 1` (couplage lâche), `RhoInf`, `ConvTol`, `MaxConvIter`, `NRotors = 1`, `CompSoil = 0`, `MirrorRotor = F`, `SoilFile` | format |
| ElastoDyn | `BldFile1-3` → `BldFile(1-3)` ; ajoutés `PitchDOF = False`, `PtfmRefxt/yt = 0`, `PBrIner(1-3) = 0`, `BlPIner(1-3) = 0` | format (valeurs neutres) |
| AeroDyn15 | `Buoyancy = False` retiré ; colonnes `TwrCp`, `TwrCa` = 0 ajoutées au tableau de tour (20 lignes) ; `BldNd_BladesOut` 1 → 0 | format ; la dernière est une option de **sortie** |
| SubDyn | bloc `INITIAL RIGID-BODY POSITION` (zéros) ; colonne `TPID = 1` à la ligne d'interface | format |
| ServoDyn | `PitNeut`, `PitSpr`, `PitDamp` (×3, = 0) ajoutés ; `DLL_FileName` → `../ServoData/libdiscon.so` | format ; chemin |
| `DISCON.IN` | `LoggingLevel` 1 → 0 | option de **sortie** |

**Bilan : aucune ligne *physique*** (masses, raideurs, profils, polaires, gains, consignes inchangés). Réserves honnêtes : (1) le diff prouve ce qui a été écrit, pas que OpenFAST v5.0.0 *interprète* chaque valeur neutre ajoutée comme l'ancien comportement (valeurs 0 / `False` alignées sur le tutoriel LHEEA migré et sur la logique « terme absent », sans lecture de la documentation v5 ligne à ligne) ; (2) `TwrCp`, `TwrCa`, `PitNeut/Spr/Damp` : usage dans cette configuration non vérifié. Rien de cela n'explique par ailleurs l'écart de Cp du notebook, qui n'est pas attribué.
  `ROSCO` : `LoggingLevel` 1 → 0 (pas de fichier `.dbg`) . Fichiers non repris : BeamDyn (`CompElast = 1`),
  `HydroDyn`/`SeaState`/`SubDyn` conservés mais désactivés dans les cas (`CompSeaSt = CompHydro = 0`).
- **ROSCO** : `DISCON.IN` écrit par l'amont avec ROSCO 2.10.1 ; bibliothèque `libdiscon.so` fournie par le
  paquet **conda-forge `rosco` 2.10.6** (Apache-2.0), installé par `scripts/installer_rosco.sh` dans un
  environnement séparé (`s9gm-rosco`, `--no-deps`) puis copié dans `models/iea15_monopile/ServoData/`
  (jamais suivi : `*.so`). Écart 2.10.1 → 2.10.6 **non élucidé** : rien ne prouve qu'il soit sans effet sur Ω(V)
  au pour-cent ; la comparaison à Gaertner 2020 du carnet 0b en est le seul garde-fou.
- **`data/iea15_wisdem_performance.csv`** : tableau « Rotor Performance » du classeur
  `Documentation/IEA-15-240-RWT_tabular.xlsx` du même dépôt (50 lignes ; données idéalisées de WISDEM,
  état stationnaire — pas la même source que les courbes OpenFAST + ROSCO de la Fig. 3-1 du rapport).
