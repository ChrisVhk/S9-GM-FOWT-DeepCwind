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

| `config_aerodyn.dat` (cas 02 à 05) | `AFAeroMod=1` (modèle stationnaire actif) ; le bloc Beddoes-Leishman qui suit (`UAMod=3`) est présent dans le fichier mais inactif, puisqu'il n'est utilisé que si `AFAeroMod=2` | `AFAeroMod` remplacé par `UA_Mod`, qui pilote directement le modèle. Valeur migrée : `UA_Mod=3` (Beddoes-Leishman Minnema/Pierce, actif) | La valeur numérique du champ dormant (`3`) a été reprise lors de la migration ; l'aérodynamique de profil des 4 cas (02-05) est donc instationnaire, pas stationnaire comme dans le tutoriel d'origine — à mentionner si ce cas sert à introduire la notion de modèle quasi-stationnaire | `openfast main.fst` → `EXIT=0` sur les 4 cas ; comparaison documentée ici, pas encore rejouée avec `UA_Mod=0` |

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

## Non testé dans cette passe

Les notebooks `practicals/practical1.ipynb` et `practical2.ipynb` (Small Wind Research Turbine,
`SWRT`) n'ont pas été exécutés avec l'environnement Python actuel (`openfast_toolbox` v3.5.1) —
copiés tels quels, gabarits à trous (`[TO COMPLETE]`), aucune réponse numérique dedans (vérifié).
