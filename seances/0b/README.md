# Séance 0b — éolienne pilotée, monopieu, flottant (3 h)

Déroulé pas à pas. L'énoncé complet est dans [`../../ENONCE.md`](../../ENONCE.md) (phase 0,
séance 0b).

**À lire avant la séance** : fiches F2 (Houle linéaire), F3 (Hydrostatique), F4 (Morison) — à
publier au fil de la rédaction du master DMO-S9 ; en leur absence, les renvois de cette page
pointent vers le tutoriel LHEEA et la fiche F1 déjà disponibles.

Cette séance poursuit la progression du tutoriel OpenFAST Quickstart du LHEEA (cas 03 à 05),
commencée en séance 0a (cas 01-02) : du contrôle réaliste d'une éolienne jusqu'au flotteur ancré.
Elle prépare la construction de vos propres cas (F03-F05, D00-D05) du tutoriel `prise_en_main/`.

## 1. Cas LHEEA 03 — éolienne pilotée en vent variable (environ 30 min)

*D'après le tutoriel OpenFAST Quickstart du LHEEA (Apache-2.0), §3, adapté — voir
[`../../tutorials/lheea/NOTICE`](../../tutorials/lheea/NOTICE).*

### Bloc Théorie

1. **Question physique** — Pourquoi un contrôle par couple seul ne suffit-il pas dès que le vent
   dépasse le régime nominal ?
2. **Modèle** — contrôleur ServoDyn élémentaire : couple nul en Region 1, proportionnel à `Ω²` en
   Region 2 (pitch fixe à 0°), constant en Region 3. **Domaine de validité** : cette forme ne pilote
   PAS le pitch — elle ne peut donc pas limiter la puissance une fois le régime nominal dépassé,
   ce que ce cas illustre directement (voir aussi la fiche F1, « Pièges »).
3. **Ordre de grandeur attendu** — la méthode : lire la rampe de vent fournie dans
   `tutorials/lheea/03_ControlledWT/1_Configuration/ramp_wind.dat`, repérer sur le résultat
   l'instant où la puissance dépasse sa valeur nominale, et le comparer, via la fiche F1, à la
   vitesse de vent théorique de transition Region 2/3.
4. **Ce que le modèle ne permet pas de conclure** — ce contrôleur élémentaire n'est pas réaliste :
   il sert à motiver le besoin du contrôleur complet (pitch + couple), utilisé dans les cas
   suivants (compilé depuis `DISCON.F90`, voir `scripts/build_discon.sh`).
5. **Renvois** — tutoriel OpenFAST Quickstart du LHEEA §3 ; fiche F1 (régulation).

```bash
cd tutorials/lheea/03_ControlledWT/1_Configuration
openfast main.fst
```

## 2. Cas LHEEA 04 — éolienne sur monopieu, vent turbulent (environ 30 min)

*D'après le tutoriel OpenFAST Quickstart du LHEEA (Apache-2.0), §4, adapté — voir
[`../../tutorials/lheea/NOTICE`](../../tutorials/lheea/NOTICE).*

### Bloc Théorie

1. **Question physique** — Comment un vent turbulent (plutôt que stationnaire) change-t-il la
   charge sur une structure offshore, et comment modélise-t-on une fondation flexible plutôt qu'un
   encastrement rigide ?
2. **Modèle** — SubDyn représente le monopieu par des membres-poutres cylindriques articulés à
   des nœuds ; le vent turbulent est un champ 3D discrétisé dans le temps et l'espace, généré par
   TurbSim. **Domaine de validité** : SubDyn suppose des membres élancés et droits — pas adapté à
   une géométrie complexe comme le flotteur DeepCwind (voir phase 5 du projet, autre méthode).
3. **Ordre de grandeur attendu** — la méthode : comparer les statistiques (moyenne, écart-type)
   du moment en pied de structure entre un vent stationnaire (cas 02, séance 0a) et ce vent
   turbulent, à vitesse moyenne comparable.
4. **Ce que le modèle ne permet pas de conclure** — une seule réalisation de vent turbulent (une
   seule « seed ») ne donne pas une statistique représentative : il en faudrait plusieurs pour
   conclure sur un écart-type fiable — point repris en phase 1 (Load Case Table) et phase 2.
5. **Renvois** — tutoriel OpenFAST Quickstart du LHEEA §4 ; `scripts/generer_vent_turbulent_05.sh`
   (méthode de génération TurbSim transposable à un autre cas).

```bash
cd tutorials/lheea/04_MonopileWT/1_Configuration
openfast main.fst
```

## 3. Cas LHEEA 05 — éolienne flottante (environ 30 min)

*D'après le tutoriel OpenFAST Quickstart du LHEEA (Apache-2.0), §5, adapté — voir
[`../../tutorials/lheea/NOTICE`](../../tutorials/lheea/NOTICE).*

### Bloc Théorie

1. **Question physique** — Qu'est-ce qui change structurellement dans le modèle quand la
   fondation n'est plus rigide (monopieu) mais flottante et ancrée ?
2. **Modèle** — HydroDyn combine théorie potentielle (grands éléments, coefficients WAMIT
   précalculés, fichier `marin_semi.*`) et théorie de Morison (éléments fins, entretoises) ;
   MoorDyn calcule l'ancrage caténaire dynamique. **Domaine de validité** : les coefficients WAMIT
   sont précalculés pour CETTE géométrie précise (DeepCwind) — ne se transposent pas tels quels à
   un autre flotteur.
3. **Ordre de grandeur attendu** — la méthode : comparer les mouvements de plateforme
   (`PtfmPitch`) et la puissance produite entre le cas fixe sur monopieu (04) et ce cas flottant, à
   conditions de vent comparables.
4. **Ce que le modèle ne permet pas de conclure** — rappel de l'énoncé (§3) : le flotteur est un
   seul corps rigide dans ce modèle — aucun effort intérieur (contrainte dans une entretoise) n'en
   est directement tiré ; ce point est traité en phase 5 par d'autres méthodes.
5. **Renvois** — tutoriel OpenFAST Quickstart du LHEEA §5 ; `ENONCE.md` §3 (limite du corps
   rigide) ; fiche F5 (hydrodynamique potentielle, à publier).

Le cas 05 nécessite un fichier de vent turbulent supplémentaire (~70 Mo, non suivi par git) :
générez-le d'abord avec `bash scripts/generer_vent_turbulent_05.sh` (voir `README.md` racine).

```bash
cd tutorials/lheea/05_FOWT/1_Configuration
openfast main.fst
```

## 4. Vos propres cas — F03-F05 et D00-D05 (à construire)

Les cas 01-05 du tutoriel LHEEA (ci-dessus et séance 0a) montrent la progression complète fixe →
flottant sur des exemples déjà construits. Il vous reste à construire les vôtres, dans
`tutorials/prise_en_main/` (voir son `README.md` pour l'organisation modèle partagé + dossier
léger par cas) :

| Cas | Vent | Houle |
|---|---|---|
| F03 à F05 | turbulent 7,5 / 12 / 16 m/s (générés par vous, TurbSim) | — (fixe) |
| D00 | aucun | régulière (Airy), H = 6 m, T = 10 s |
| D01 | constant 7,5 m/s | régulière, H = 6 m, T = 10 s |
| D02 | échelon de 5 à 20 m/s | régulière, H = 6 m, T = 10 s |
| D03 à D05 | turbulent (mêmes champs que F03-F05) | irrégulière JONSWAP, Hs = 6 m, Tp = 10 s |

**Point en attente de l'enseignant** : la durée simulée des cas turbulents (F03-F05, D03-D05) —
300 s en séance avec 600 s en option, 600 s systématiques analysés en phase 1, ou un seul cas
turbulent par binôme — n'est pas encore arbitrée.

Classeur d'architecture du flotteur (`DeepCwind_ARCHITECTURE.xlsx`) et raideurs hydrostatiques
K33/K55 à la main : voir `ENONCE.md`, phase 0, séance 0b, points 7-8.

## Rendu R0 (suite)

Questions Q0.3 à Q0.5 de l'énoncé (section « Phase 0 », rendu R0) : classeur d'architecture,
tableau fixe/flottant, paramètres d'une Load Case Table.
