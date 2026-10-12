<!-- destinations: github -->
# Modèle flottant — NREL 5 MW sur la plateforme OC4-DeepCwind

Ce dossier est le modèle partagé des cas flottants `D00` à `D05` (séance [0b](../../seances/0b/README.md)). Il est **dérivé du cas
r-test OpenFAST `5MW_OC4Semi_WSt_WavesWN`** (tag v5.0.0, Apache-2.0, voir [`../oc4_rtest/`](../oc4_rtest/) et
[`PROVENANCE.md`](../../PROVENANCE.md)), sans copier ses fichiers : `main.fst` pointe vers `../oc4_rtest/5MW_OC4Semi_WSt_WavesWN/`
pour l'aérodynamique (AeroDyn), le contrôle (ServoDyn et son contrôleur compilé), l'hydrodynamique (HydroDyn, avec les données
WAMIT de `../oc4_rtest/5MW_Baseline/HydroData/`), l'ancrage (MoorDyn) et l'état de mer (SeaState). Il ne contient que ce qui
diffère du r-test :

| Fichier | Différence avec le r-test | Pourquoi |
|---|---|---|
| `main.fst` | `TMax = 300 s` ; `BDBldFile(1-3) = "unused"` ; sorties au pas de 0,1 s en binaire compressé (`OutFileFmt = 2`), sans fichier `.sum` ; fichiers de module cités par chemin relatif vers `../oc4_rtest/` | durée des cas du tutoriel ; même format de sortie que le modèle fixe, lisible par `s9gm.lire` (le format binaire 4 du r-test ne l'est pas) |
| `config_elastodyn.dat` | rotor **à l'arrêt** (`RotSpeed = 0`), plateforme **sans déplacement initial** (`PtfmSurge = 0`, `PtfmPitch = 0`) ; chemins des fichiers de pale et de tour vers `../oc4_rtest/` ; sorties `RootMyb1`, `RootMxb1`, `YawBrFxn` ajoutées à la liste de sorties | départ au repos, comme `modeles/fixe/` : la comparaison fixe / flottant (séance 0b) part de la même condition ; le r-test démarre rotor lancé et plateforme décalée. Les trois sorties ajoutées sont celles du tableau fixe / flottant de la séance 0b, que `modeles/fixe/` donne aussi (`YawBrFxn` y a été ajoutée de la même façon) |
| `config_inflow.dat` | celui de `modeles/fixe/` (vent par défaut : rampe lue dans `Wind/ramp_wind.dat`, propre au cas) | `s9gm.cas` le modifie cas par cas |

Ce que le modèle **ne** change **pas** par rapport au r-test : géométrie de la plateforme, ancrage, contrôleur (celui du r-test,
`DISCON_OC3Hywind`, compilé par `bash scripts/build_discon.sh`), couplage serré des modules (`ModCoupling = 3`), pas de temps
(0,0125 s), profondeur (200 m), état de mer par défaut (bruit blanc : chaque cas D le remplace par une houle régulière ou JONSWAP,
voir les colonnes `seastate.*` de [`cas/lct_flottant.csv`](../../cas/lct_flottant.csv)).

Le flotteur est **un seul corps rigide à 6 degrés de liberté** dans ce modèle (limite rappelée dans l'[`ENONCE.md`](../../ENONCE.md),
section 3 bis) : aucun effort intérieur n'en est tiré.

**Règle de ce dépôt** : ce dossier est une référence suivie par git ; on le lit et on le lance, on ne le modifie pas.
