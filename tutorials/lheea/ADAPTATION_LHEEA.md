<!-- destinations: github, word -->
# Adaptations apportées au tutoriel OpenFAST Quickstart (LHEEA)

Document préparé pour être transmis au LHEEA (Nantes Université — ORACLE), dont ce tutoriel est
issu (dépôt `openfast_quickstart`, commit `6040b6430bba78d3906877f2ea4d3effe3a4eb5e`, licence
Apache-2.0). Il recense, cas par cas, chaque modification apportée pour faire tourner le tutoriel
sous **OpenFAST v5.0.0** (version d'origine : v3.2.1) sur **Linux** (version d'origine : Windows,
exécutable `.exe`).

Conformément à la licence Apache-2.0 (§4b), chaque modification est signalée ici ; voir aussi
[`NOTICE`](NOTICE) pour le résumé synthétique côté attribution.

## Cas 01 — Tour seule (`01_TowerStructure/`)

| Champ / fichier | Avant (v3.2.1) | Après (v5.0.0) | Raison | Test qui le valide |
|---|---|---|---|---|
| `config_elastodyn.dat` | ~25 champs absents (`PitchDOF`, `PtfmRefxt/yt`, `PBrIner/BlPIner` ×3, `HubIner_Teeter`, `PtfmXYIner/YZIner/XZIner`, section YAW-FRICTION complète, bloc de sortie par station de pale) | Champs ajoutés à leurs valeurs par défaut documentées | Format d'entrée ElastoDyn v5.0.0 : lecture positionnelle Fortran, un champ manquant décale la lecture de tous les suivants | `openfast main.fst` → `EXIT=0`, 10 s simulées |
| `main.fst` | Sans `ModCoupling`, `RhoInf`/`ConvTol`/`MaxConvIter`, `NRotors`, `CompSeaSt`, `CompSoil`, `MirrorRotor`, `SeaStFile` | Champs ajoutés | Format `.fst` v5.0.0 (module SeaState introduit, support multi-rotor) | idem |

## Cas 02 — Rotor libre (`02_FreeRotatingWT/`)

| Champ / fichier | Avant (v3.2.1) | Après (v5.0.0) | Raison | Test qui le valide |
|---|---|---|---|---|
| `config_aerodyn.dat` | `WakeMod`, `SkewMod`, `AFAeroMod` unique | Renommés `Wake_Mod`, `Skew_Mod` ; `AFAeroMod` scindé en `UA_Mod` + `IntegrationMethod` | Renommage/refonte de champs AeroDyn v5.0.0 | `openfast main.fst` → `EXIT=0`, 200 s simulées |
| `config_inflow.dat` | Sans `VelInterpCubic`, sans section LIDAR | `VelInterpCubic` ajouté en tête ; section LIDAR complète ajoutée (12 champs, à leurs valeurs par défaut — non utilisée avec `WindType=1/2/3`, mais doit être présente) | Lecture positionnelle Fortran : absence de la section cause un décalage de lecture, pas une erreur explicite | Erreur initiale détectée (décalage), corrigée ; `EXIT=0` après correction |

| `config_aerodyn.dat` (cas 02 à 05) | `AFAeroMod=1` (modèle stationnaire actif) ; le bloc Beddoes-Leishman qui suit (`UAMod=3`) est présent dans le fichier mais inactif, puisqu'il n'est utilisé que si `AFAeroMod=2` | `AFAeroMod` remplacé par `UA_Mod`, qui pilote directement le modèle. Valeur retenue : `UA_Mod=3` (Beddoes-Leishman Minnema/Pierce, actif) | **Alignement sur le modèle de référence du projet** : `models/oc4_rtest/5MW_OC4Semi_WSt_WavesWN/NRELOffshrBsline5MW_OC3Hywind_AeroDyn.dat` porte la même valeur (`UA_Mod=3`), vérifiée avant de trancher. L'aérodynamique de profil des 4 cas (02-05) est donc instationnaire, pas stationnaire comme dans le tutoriel d'origine — à mentionner si ce cas sert à introduire la notion de modèle quasi-stationnaire | `openfast main.fst` → `EXIT=0` sur les 4 cas (inchangé, aucun fichier modifié) ; même valeur confirmée dans `tutorials/prise_en_main/modele_fixe/` |

## Cas 03 — Éolienne contrôlée (`03_ControlledWT/`)

| Champ / fichier | Avant (v3.2.1) | Après (v5.0.0) | Raison | Test qui le valide |
|---|---|---|---|---|
| `config_servodyn.dat` | Sans `PitNeut`/`PitSpr`/`PitDamp` ×3 | Ajoutés après `TPCOn`, avant `TPitManS` | Format ServoDyn v5.0.0 (ressort/amortisseur de pas passif) | `EXIT=0`, 600 s simulées |
| Contrôleur (`DLL_FileName`) | `DISCON.dll` (binaire Windows tiers, version/provenance non tracée) | `DISCON.so`, compilé par chaque étudiant (`scripts/build_discon.sh`) depuis `DISCON.F90`, source du tag OpenFAST v5.0.0 (Apache-2.0) | `.dll` inutilisable sous Linux ; traçabilité de la source (le binaire d'origine n'était pas accompagné de son code source identifié) | `nm -D DISCON.so \| grep " T DISCON$"` (symbole exporté) et log d'exécution `Running ServoDyn Interface for Bladed Controllers (using GNU Fortran for Linux)` |

## Cas 04 — Monopieu (`04_MonopileWT/`)

| Champ / fichier | Avant (v3.2.1) | Après (v5.0.0) | Raison | Test qui le valide |
|---|---|---|---|---|
| Hydrodynamique | Fichier HydroDyn v2.03 unique (environnement + houle + courant + membres Morison) | Scindé en `SeaState.dat` (environnement/houle/courant) + `HydroDyn.dat` (membres Morison), repris du cas r-test `5MW_OC3Mnpl_DLL_WTurb_WavesIrr` | Refonte du format HydroDyn en v5.0.0 (module SeaState introduit) ; conversion champ-à-champ manuelle jugée trop risquée | Comparaison géométrique ligne à ligne (joints, sections, coefficients hydrodynamiques) entre le fichier LHEEA d'origine et le fichier r-test repris : identiques (même système OC3-Monopile standard) |
| `Wake_Mod` | `2` (DBEMT, choix d'origine) | `1` (BEMT) | OpenFAST v5.0.0 refuse `Wake_Mod=2` pour cette combinaison de projection (« Wake_Mod must be 0, 1, or 3 ») — **changement d'API découvert à l'exécution, pas anticipé par diff de champs**. **Conséquence pédagogique** : la dynamique d'écoulement enseignée n'est plus la même (BEMT quasi-stationnaire, pas DBEMT dynamique) | Message d'erreur explicite à l'exécution avant correction ; `EXIT=0` après |
| Vent | `WindType=3` (TurbSim), fichier `.bts` absent de la distribution amont (exclu par le dépôt LHEEA lui-même) | `WindType=2`, fichier `Wind/ramp_wind.dat` déjà fourni par le tutoriel | Le `.bts` n'a jamais été distribué avec le dépôt amont | `EXIT=0`, 600 s simulées |

## Cas 05 — Éolienne flottante (`05_FOWT/`)

| Champ / fichier | Avant (v3.2.1) | Après (v5.0.0) | Raison | Test qui le valide |
|---|---|---|---|---|
| Hydrodynamique / ancrage | Fichier HydroDyn v2.03 + MoorDyn d'origine | `SeaState.dat` + `HydroDyn.dat` + `MoorDyn.dat` repris du cas r-test `5MW_OC4Semi_WSt_WavesWN` (même plateforme OC4-DeepCwind, même ancrage) ; réglages de houle du tutoriel réappliqués (`WaveMod=2` JONSWAP, `WaveHs=5`, `WaveTp=10`, au lieu du bruit blanc `WaveMod=3` du r-test) | Même raison que le cas 04 | Même méthode de comparaison géométrique que le cas 04 |
| `Wake_Mod` / contrôleur | Idem cas 04 | `Wake_Mod=1` ; `DISCON_OC3Hywind.F90` (cohérent avec le contrôleur du cas r-test équivalent) | Idem cas 04 | Idem cas 04 |
| Vent | `.bts` absent de la distribution amont | **Régénéré** avec TurbSim (`scripts/generer_vent_turbulent_05.sh`) à partir du fichier `.inp` d'origine LHEEA, conservé intact | Fichier jamais distribué par l'amont, et trop volumineux (~70 Mo) pour être suivi dans ce dépôt non plus | `EXIT=0`, 600 s simulées, vent TurbSim + houle JONSWAP + ancrage MoorDyn + contrôleur actifs simultanément |

## Point non lié à la migration v3.2.1→v5.0.0, mais à Linux

Le tutoriel original signale déjà lui-même (texte du PDF, §4.1, note de bas de page) que les
utilisateurs Linux doivent utiliser un fichier `.so` plutôt qu'un `.dll` pour le contrôleur — ce
n'est donc pas une adaptation liée à la version d'OpenFAST, mais à l'OS. L'écart réel introduit
ici est **la provenance du `.so`** : compilé depuis la source Apache-2.0 d'OpenFAST, pas un binaire
tiers.

## Practicals SWRT (`practicals/`) — exécutés et migrés

Les notebooks `practical1.ipynb` et `practical2.ipynb` (Small Wind Research Turbine, `SWRT`) ont
été exécutés avec l'environnement actuel (`openfast_toolbox` v3.5.1 + `jupyter nbconvert
--execute`). Les cas `.fst`/ElastoDyn qu'ils utilisent dataient d'une version antérieure à
v3.2.1 et n'avaient jamais été migrés.

| Fichier | Avant | Après | Raison | Test qui le valide |
|---|---|---|---|---|
| `SWRT_01/SWRT_01.fst`, `SWRT_02/SWRT_02{1,2,3}.fst` | Section SIMULATION CONTROL sans `ModCoupling`/`RhoInf`/`ConvTol`/`MaxConvIter` ; FEATURE SWITCHES sans `NRotors`/`CompSeaSt`/`CompSoil`/`MirrorRotor` ; INPUT FILES sans `SeaStFile`/`SoilFile` | Champs ajoutés (mêmes valeurs par défaut que les cas 01-05) | Même refonte de format `.fst` v5.0.0 que les cas principaux (lecture positionnelle Fortran) | `openfast <cas>.fst` → `EXIT=0` pour `SWRT_01` et `SWRT_021` |
| `SWRT_01/Elastodyn/SWRT_ED.dat`, `SWRT_02/Elastodyn/SWRT_ED{,_rigid}.dat` | Sans `PitchDOF`, `PtfmRefxt/yt`, `PBrIner`×3, `BlPIner`×3, `HubIner_Teeter`, `PtfmXYIner/YZIner/XZIner`, section YAW-FRICTION, bloc de sortie par station de pale | Champs/section ajoutés | Même refonte ElastoDyn v5.0.0 que les cas principaux | idem |
| `SWRT_021.fst`, champ `InflowFile` | `"unused"` alors que `CompInflow=1` | `"InflowWind/SWRT_IW.dat"` (cohérent avec `SWRT_022`/`SWRT_023`, qui référencent déjà ce fichier) | **Défaut préexistant du fichier d'origine, indépendant de la migration v5.0.0** — `SWRT_021` ne pouvait pas fonctionner même sous v3.5.2 avec ce réglage | `openfast SWRT_021.fst` → `EXIT=0` après correction |
| `SWRT_022.fst`, `SWRT_023.fst`, chemins `AeroDyn/...` | `"AeroDyn/SWRT_AD(15).dat"` | `"Aerodyn/SWRT_AD(15).dat"` | **Sensibilité à la casse Windows→Linux** : le dossier réel s'appelle `Aerodyn` (minuscule), le chemin écrit dans le `.fst` utilisait `AeroDyn` — invisible sous Windows (NTFS insensible à la casse), bloquant sous Linux (ext4 sensible à la casse) | Le fichier est trouvé (l'erreur suivante change de nature, voir ci-dessous) |

### Non résolu dans cette passe — `SWRT_022.fst`, mésappariement AeroDyn v14/v15

`SWRT_022.fst` déclare `CompAero=2` (AeroDyn, sens v5.0.0 générique) mais son `AeroFile` pointe
vers `Aerodyn/SWRT_AD.dat`, dont l'en-tête dit explicitement **« AeroDyn v14.04.* INPUT FILE »**
— un format de fichier complètement différent (pas de champ `Echo` en tête, schéma différent),
que le parseur v5.0.0 ne sait pas lire (`ParseLoVar: The variable "Echo" was not found on line
#4`). `SWRT_023.fst`, lui, pointe correctement vers `Aerodyn/SWRT_AD15.dat` (format v15) et n'a
pas cette incohérence.

**Ce n'est pas un défaut de migration** : même sous OpenFAST v3.5.2 (version d'origine de ces
fichiers), le module « AeroDyn v14 » est un driver distinct de l'« AeroDyn v15 » utilisé partout
ailleurs dans ce dépôt — réparer `SWRT_022` demanderait soit de reconstruire un fichier AeroDyn
v15 complet pour cette turbine (portage de la géométrie de pale), soit de clarifier l'intention
pédagogique originale (le fichier v14 était peut-être volontaire, avec un `CompAero` mal réglé).
**Hors budget de cette passe** — engagement ouvert (voir `ENGAGEMENTS.md`).

Conséquence pour les notebooks : `practical1.ipynb` s'exécute intégralement sans erreur
(`jupyter nbconvert --execute`, 0 erreur). `practical2.ipynb` s'exécute jusqu'à la cellule qui lit
`SWRT_022.out` (le calcul ne produit pas ce fichier, `SWRT_022.fst` ne tourne pas) — aucune
cellule réponse n'a été ajoutée ou modifiée pour contourner ce point.

`SWRT_023.fst` a reçu les mêmes corrections `.fst`/ElastoDyn mais n'a pas été testé plus loin : il
n'est référencé par aucune cellule de code des deux notebooks.

**Nouvelle dépendance** : `notebook` et `ipykernel` ajoutés à `env/environment.yml` — sans eux,
rien dans l'environnement pinné ne permettait d'ouvrir ou d'exécuter ces notebooks.
