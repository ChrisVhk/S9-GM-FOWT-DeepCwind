# Séance 0a — lundi (3 h)

Déroulé pas à pas. L'énoncé complet est dans [`../../ENONCE.md`](../../ENONCE.md) (phase 0,
séance 0a) — ce document-ci en est la version « pas à pas » pour la séance.

**À lire avant la séance** : fiche F1 — Aéro-régulation ([`../../fiches/F1_Aero-regulation.md`](../../fiches/F1_Aero-regulation.md)).

## 1. Installation (environ 20 min)

Suivez [`../../INSTALLATION.md`](../../INSTALLATION.md), sections 1 et 2 :
- cloner le dépôt, lancer `bash env/install.sh` ;
- vérifier `openfast -v` → doit afficher `OpenFAST-v5.0.0` ;
- compiler le contrôleur : `bash scripts/build_discon.sh`.

**Si ça ne marche pas** : voir « En cas d'échec » dans `INSTALLATION.md`. Notez l'erreur exacte,
continuez avec un camarade en binôme pour la suite, et terminez l'installation après la séance
(avant la séance 0b, au plus tard en salle C09).

## 2. Premiers calculs — cas LHEEA 01 et 02 (environ 15 min)

```bash
cd tutorials/lheea/01_TowerStructure/1_Configuration
openfast main.fst
cd ../../02_FreeRotatingWT/1_Configuration
openfast main.fst
```

Les deux doivent se terminer par `OpenFAST terminated normally.`. Ce sont les cas les plus
simples du dépôt — s'ils échouent, l'installation n'est pas correcte, reprenez l'étape 1.

## 3. Lire un `.fst` (environ 20 min, en binôme)

Ouvrez `tutorials/lheea/01_TowerStructure/1_Configuration/main.fst` dans un éditeur de texte.
Pour chaque section, notez ce que vous changeriez pour une nouvelle étude (`TMax`, le pas de
temps, les degrés de liberté actifs, les fichiers d'entrée, la liste de sorties `OutList`) et ce
qui reste identique d'un cas à l'autre dans ce tutoriel.

## 4. Régulation de la NREL 5 MW, à la main (environ 30 min)

### Bloc Théorie

1. **Question physique** — Pourquoi une éolienne ne tourne-t-elle pas à une vitesse de rotation
   fixe quel que soit le vent, et pourquoi faut-il la piloter (couple générateur, puis pitch)
   plutôt que la laisser suivre librement l'aérodynamique ?
2. **Modèle** — TSR `λ = Ω·R/V` ; coefficient de puissance `Cp(λ,β)`, maximal pour un `λ*`
   donné ; loi de Region 2 `Ω(V) = λ*·V/R` (couple piloté, pitch fixe). **Domaine de validité** :
   machine à vitesse variable et pitch variable (c'est le cas ici), et seulement tant que `Ω`
   calculé reste en dessous du régime nominal — au-delà, ce n'est plus cette loi qui gouverne
   (Region 2½ puis 3).
3. **Ordre de grandeur attendu** — la méthode : calculer `Ω` pour chaque vitesse de vent du
   tableau demandé via `λ*·V/R`, repérer la vitesse de vent où `Ω` atteint le régime nominal donné
   par la fiche F1. Les valeurs numériques du cas particulier F01/F02 répondent à une question
   notée (Q0.1/Q0.2) : ne les cherchez pas dans ce dépôt, calculez-les.
4. **Ce que le modèle ne permet pas de conclure** — la loi `λ* = constante` est une
   approximation : la loi de couple réelle du contrôleur peut s'en écarter légèrement à certaines
   vitesses, et ce modèle stationnaire ne dit rien du régime transitoire ni du comportement en
   Region 2½/3.
5. **Renvois** — fiche F1, section « Minimum vital » et « Ordre de grandeur » ; Jonkman 2009,
   §7.2 p.26 et Tab. 7-2 p.27 (paramètres numériques).

Avec la fiche F1 : R = 63 m, vitesse de bout de pale maximale 80 m/s, régime nominal 12,1 tr/min,
puissance nominale 5 MW, TSR optimal 7,55 (Jonkman 2009). Construisez le tableau vitesse de vent →
vitesse de rotation → puissance, et identifiez les zones de fonctionnement (Region 2, 2½, 3).
C'est la question Q0.1 du rendu R0.

## 5. Cas F01 et F02 — éolienne fixe (environ 45 min)

### Bloc Théorie

1. **Question physique** — Le calcul OpenFAST produit des courbes de sortie : comment savoir
   si elles sont physiquement plausibles avant de les utiliser dans un rendu, sans attendre qu'un
   enseignant les valide ?
2. **Modèle** — poussée du rotor par la théorie du disque actuateur,
   `T = 1/2 · ρ · A · V² · Ct`, puis `TwrBsMyt ≈ T × hauteur_moyeu`. **Domaine de validité** :
   Region 2 (loin du régime nominal, `Ct` à peu près constant), vent stationnaire pour F01 (le
   modèle stationnaire ne s'applique pas directement à l'échelon de F02), régime établi atteint
   (transitoire de démarrage écarté de la moyenne).
3. **Ordre de grandeur attendu** — la méthode : calculer `Ω` attendu (bloc précédent) et une
   estimation de `T`/`TwrBsMyt`, puis les comparer à `RotSpeed`/`TwrBsMyt` observés, à ±15-20 %.
   Les valeurs numériques pour F01 répondent à Q0.2 : à calculer, pas à relever.
4. **Ce que le modèle ne permet pas de conclure** — un écart dans la tolérance ne prouve pas
   que la configuration est correcte (un transitoire mal filtré peut produire le même symptôme
   qu'une vraie erreur), et cette vérification stationnaire ne valide rien sur la dynamique de
   F02 (échelon), qui demande une lecture différente (temps de réaction du calage).
5. **Renvois** — fiche F1, section « Confrontation OpenFAST » ; `outils/lire_outb.py` (option
   `t_min`, pour écarter le transitoire).

```bash
cd tutorials/prise_en_main
bash run_cas.sh F01
bash run_cas.sh F02
```

| Cas | Vent | Ce qu'on regarde |
|---|---|---|
| F01 | constant 7,5 m/s | régime établi, poussée, moment en pied de tour |
| F02 | échelon de 5 à 20 m/s | passage d'une zone de régulation à l'autre, temps de réaction du calage des pales |

Voir `tutorials/prise_en_main/README.md` pour la méthode de vérification à la main (fréquence 1P,
poussée, `TwrBsMyt`).

## 6. Rendu R0 (à finir hors séance si besoin)

Questions Q0.1 et Q0.2 de l'énoncé (section « Phase 0 », rendu R0) : tableau de régulation à la
main comparé à F02, et vérifications à la main de F01. Les questions Q0.3 à Q0.5 portent sur la
séance 0b, pas sur celle-ci.

## Séance suivante

`seances/0b/` : éolienne fixe en vent turbulent, classeur d'architecture du flotteur, premiers
cas flottants (D0x). Squelette en place, contenu détaillé à publier avant la séance.
