<!-- destinations: github, word -->
# DMO-S9 — Fondations et structures
## Projet « DeepCwind » : de l'environnement du site au dommage de fatigue

**Ingénieur Génie Maritime — I5, parcours DMO — Semestre 9**
**Système étudié** : éolienne flottante NREL 5 MW sur la plateforme semi-submersible OC4-DeepCwind (profondeur 200 m, ancrage caténaire trois lignes), simulée avec OpenFAST v5.0.0.

---

### 1. Pourquoi ce projet

Une fondation ou un flotteur ne se dimensionne pas « au pire cas imaginé » : il se dimensionne sur une **liste de cas de charge** tirée des données du site, simulée, puis post-traitée en **extrême (ULS)** et en **fatigue (FLS)**. C'est le métier des bureaux d'études EMR. Vous allez parcourir cette chaîne complète, sur un système réel et documenté, avec les outils et les normes de la profession.

Vous ne deviendrez pas numériciens : vous deviendrez des ingénieurs capables de **commander, lire et critiquer** un calcul de charges. On vous demandera donc toujours trois choses : ce que la théorie prévoit, ce que vos chiffres montrent, et **ce que vos chiffres ne permettent pas de conclure**.

*Le tutoriel de la phase 0 transpose une progression inspirée d'un cours de Master Génie Maritime (2013) sur les outils de conception éolien pour les études d'avant-projet.*

### 2. Compétences visées

À la fin du projet, vous savez :

1. **Traduire un site en entrées de calcul** : vent (vitesse, turbulence, direction), mer (spectre, Hs, Tp, direction), courant, marée, seeds.
2. **Lire un scatter diagram et construire une Load Case Table (LCT)** : regrouper (binning), choisir une valeur représentative (lumping), affecter des occurrences, vérifier la représentativité.
3. **Choisir les Design Load Cases (DLC) pertinents** selon le composant (tour, flotteur, ancrage) et l'état limite (ULS / FLS).
4. **Mener une étude de sensibilité** sur un modèle couplé et en tirer des conclusions argumentées.
5. **Calculer un dommage de fatigue** : rainflow, courbe S-N (DNV-RP-C203), règle de Miner, DFF, **DEL** court et long terme — et en connaître les limites.
6. **Vérifier une section tubulaire** en ULS et en FLS, avec un **SCF**, selon les normes.

### 3. Organisation

**Trois groupes, un paramètre chacun.** Chaque groupe fait varier une famille de paramètres ; la synthèse finale est commune.

| Groupe | Famille étudiée | Questions de départ |
|---|---|---|
| **Bâbord** | **Vent** | Vitesse moyenne (classes de 4 à 24 m/s), intensité de turbulence, nombre de seeds. Quel effet sur le moment en pied de tour et sur la tension d'ancrage ? Combien de seeds faut-il ? |
| **Tribord** | **Mer et courant** | Hs, Tp, direction de houle, facteur de pic γ du JONSWAP, courant. Quelles cellules du scatter diagram font le dommage ? Que se passe-t-il près des périodes propres du flotteur ? |
| **Centre** | **Modélisation hydrodynamique et ancrage** | Théorie potentielle (base de données hydrodynamique WAMIT) vs Morison seul vs hybride ; ancrage dynamique (MoorDyn) vs quasi-statique (MAP++). Quand le choix du modèle change-t-il la conclusion ? |

Au sein de chaque groupe, vous travaillez en **binômes**. Chaque binôme est responsable d'une partie des cas du groupe.

**Points de calcul imposés** (les mêmes pour les trois groupes, pour que la synthèse soit possible) :

- **pied de tour** : moment de flexion `TwrBsMyt` (ElastoDyn) ;
- **chaumards** : tensions `FAIRTEN1` à `FAIRTEN3` (MoorDyn) ;
- **mouvements du flotteur** : `PtfmSurge`, `PtfmHeave`, `PtfmPitch`.

> **Limite à connaître dès maintenant** : dans le modèle de référence OpenFAST, le flotteur est **un seul corps rigide à 6 degrés de liberté**. HydroDyn calcule les efforts que la mer **applique** au flotteur (la part potentielle est ramenée en un point, la part Morison est répartie sur les membres), mais le calcul ne contient **aucun effort intérieur** : on n'obtient pas directement la contrainte dans une entretoise. C'est légitime pour les mouvements et l'ancrage (le flotteur est très raide devant la houle), pas pour la fatigue de ses assemblages. La structure du flotteur est donc traitée en phase 5 par des méthodes adaptées, et choisir le bon niveau de modèle fait partie du travail demandé.

### 3 bis. Comment aborder ce projet

**Ce que vous allez faire est un travail d'expert.** Il y a quelques années, ce parcours (du scatter diagram au dommage de fatigue sur une éolienne flottante) demandait plusieurs mois de stage en bureau d'études, encadré par des spécialistes. Vous allez le faire en 46 h, parce que les outils sont ouverts, que les modèles de référence existent et que les assistants d'IA accélèrent tout ce qui est mécanique. **Ce qui ne s'accélère pas, c'est le jugement** : savoir si un chiffre est plausible, si une hypothèse est acceptable, si une conclusion tient. C'est cela que le projet évalue.

**Chaque phase suit le même schéma** :

| Étape | Ce que vous faites |
|---|---|
| **Pourquoi** | Comprendre la question métier à laquelle la phase répond (quel ingénieur, quelle décision). |
| **À la main d'abord** | Un ordre de grandeur, un calcul simple, avant tout calcul numérique. Le numérique vient le confirmer ou le contredire. |
| **Simuler** | Lancer peu de cas, bien choisis, plutôt que beaucoup de cas mal compris. |
| **Confronter** | Théorie attendue → chiffres obtenus → **ce qu'ils ne permettent pas de conclure**. |
| **Point de contrôle** | Une vérification que vous faites vous-mêmes avant d'aller plus loin (tableau ci-dessous). |

**Points de contrôle** — ne passez pas à la suite sans eux :

| Phase | Point de contrôle | Piège classique |
|---|---|---|
| 0 | `openfast -v` = v5.0.0 ; moment en pied de tour de F01 ≈ poussée × (hauteur du moyeu − hauteur du pied de tour `TowerBsHt`), à ±20 % | Analyser le début de simulation, avant le régime établi |
| 1 | **LCT validée par l'enseignant avant tout lancement** ; somme des occurrences = 100 % | Oublier les états de mer peu probables mais proches des périodes propres |
| 2 | Équilibre et périodes de lâcher cohérents avec les valeurs publiées ; une seule famille de paramètres varie à la fois | Conclure sur une seule seed |
| 3 | DEL programmé = DEL de l'outil sur un signal test sinusoïdal (résultat connu à l'avance) | Mélanger étendue et amplitude ; oublier le DFF ; mauvaise courbe S-N (air / eau) |
| 4 | Tension maximale < charge de rupture avec le coefficient de sécurité retenu ; cas extrêmes conformes aux DLC choisis | Comparer des extrêmes issus de durées de simulation différentes |
| 5 | Domaine de validité de chaque formule (β, rapports d'épaisseur) vérifié avant usage | Appliquer un SCF hors de son domaine |

**Socle et approfondissement.** Chaque phase a un socle, exigé de tous, et des questions d'approfondissement (repérées ★ par l'enseignant au fil du projet). Mieux vaut un socle solide et bien argumenté qu'un approfondissement fragile.

**Outils d'IA : la règle du double contrôle.** Utilisez-les pour écrire un script, retrouver un paramètre dans un fichier OpenFAST, reformuler une norme. Mais tout résultat qu'ils produisent passe par deux contrôles : **un ordre de grandeur à la main** et **une source** (manuel OpenFAST, norme, document de référence). Un chiffre que vous ne savez pas recalculer ou justifier à l'oral n'a pas sa place dans un rendu.

**Le temps de calcul est une ressource d'ingénieur.** Une simulation de 600 s prend environ 25 min sur une machine de la salle, une simulation d'une heure plus de 2 h — ordre de grandeur pour un cas complet (flottant, houle, ancrage) ; les cas plus simples du tutoriel de prise en main sont nettement plus rapides (voir les temps mesurés dans `cas/README.md` et `seances/0b/README.md`). Une LCT mal construite coûte des heures de machine pour rien : c'est pour cela qu'elle est validée avant lancement.

**Fiches « minimum vital ».** Dix fiches de deux pages donnent le socle théorique nécessaire à chaque étape du projet (`fiches/` de ce dépôt). Six existent à ce jour (F1, F2, F3, F5, F9 et F10) ; les suivantes seront publiées au fil du projet.

| Fiche | Sujet | Utile pour |
|---|---|---|
| F1 — Aéro-régulation | TSR, zones de régulation, poussée du rotor | Phase 0a |
| [F2 — Houle linéaire](fiches/F2_Houle-lineaire.md) | Théorie d'Airy, spectre, Hs/Tp | Phase 0b, phase 1 |
| [F3 — Hydrostatique](fiches/F3_Hydrostatique.md) | Raideurs K33/K55, carène, GM | Phase 0b |
| F4 — Morison | Coefficients Cd/Ca, efforts répartis sur un membre | Phase 0b, phase 5 |
| [F5 — Hydrodynamique potentielle](fiches/F5_Hydrodynamique-potentielle.md) | Base de données WAMIT, radiation/diffraction | Phase 2 |
| F6 — Aérodynamique et amortissement négatif | Amortissement aéro d'un flotteur en tangage | Phase 2 |
| F7 — Caténaire statique | Équation de la chaîne, raideur de ligne | Phase 4 |
| F8 — Ancrage dynamique | MoorDyn vs quasi-statique, tension de chaumard `FAIRTEN` | Phase 4 |
| [F9 — Fatigue de structure](fiches/F9_Fatigue-de-structure.md) | Rainflow, courbe S-N, Miner, DEL, DFF, effet d'épaisseur | Phase 3, phase 4 (`FAIRTEN`) |
| [F10 — Structures tubulaires](fiches/F10_Structures-tubulaires.md) | Nœuds tubulaires, SCF, point chaud, domaine de validité | Phase 5 |

*Correspondance construite à partir du sujet de chaque fiche ; à confirmer phase par phase à mesure que les fiches F2-F10 sont rédigées et publiées.*

### 4. Déroulé et heures du référentiel

Les volumes suivent le référentiel DMO-S9 (cours 32 h, TD 26 h). Les dates sont au planning de la promotion.

| Phase | Contenu | Créneau du référentiel | Volume indicatif | Travail personnel estimé | Rendu |
|---|---|---|---|---|---|
| **0** | Tutoriel de prise en main : installation, éolienne fixe (monopieu) puis flottante (DeepCwind), vérifications à la main | Design of Offshore Structures (CM 3 h) + Analysis (TD 3 h) | 6 h — **0a lundi**, 0b séance suivante | — | R0 |
| **1** | Du site à la Load Case Table : scatter diagram, DLC, binning / lumping | Design of Offshore Structures (CM 3 h) | 3 h | — | R1 |
| **2** | Simulations de référence, lâchers, étude de sensibilité par groupe | Analysis (CM 4 h + TD 1 h) | 5 h | — | R2 |
| **3** | Fatigue : rainflow, S-N, Miner, DEL court et long terme | Analysis (CM 4 h + TD 4 h) | 8 h | **≈ 3 h** — la fin du premier passage de l'atelier tour (étape 0 : `SCF = 2` et le comparatif avec `SCF = 1`) se termine à la maison ; le début (prise en main, `SCF = 1`) se fait en séance | R3 |
| **4** | Extrêmes (ULS) et ancrage | Ancrage et accostage (CM 6 h + TD 6 h) | 12 h | — | R4 |
| **5** | Structures tubulaires : section de tour, effort dans une entretoise, SCF et domaine de validité | Ancrage et accostage (TD 8 h) | 8 h | **≈ 5 h** — fin du second passage de l'atelier (point 1, ≈ 3 h : sections FLS/ULS au-delà de celle traitée en séance) + boucle de dimensionnement (point 2, ≈ 2 h) à la maison ; le lancement du second passage sur vos propres données se fait en séance | R5 |
| **6** | Synthèse commune des trois groupes et soutenance | Ancrage et accostage (TD 4 h) | 4 h | — | Soutenance |
| | | | **46 h** | **≈ 8 h** | |

Le projet couvre l'essentiel de l'UE. Geotechnical Data (CM 4 h), la conférence acier et béton (8 h) et l'accostage sont **facultatifs cette année** et feront l'objet d'un cours séparé dans un second temps.

---

### 5. Le travail, phase par phase

Chaque séance et chaque phase a sa **consigne autonome**, au même format (objectif, avant de commencer, à faire étape par étape, post-traiter, ce qu'on rend, théorie à lire). L'`ENONCE.md` ne la reprend plus : il renvoie.

Le tableau du parcours (phases et séances, volumes, consignes, rendus) est dans le [`README.md`](README.md#le-parcours-phase-par-phase) : il n'est pas répété ici. Le guide du classeur de l'atelier (phases 3 et 5) est une ressource, présentée au README.

---

### 6. Évaluation

| Élément | Poids |
|---|---|
| R0 — Installation et prise en main | 5 % |
| R1 — Load Case Table et représentativité | 15 % |
| R2 — Simulations et sensibilité | 10 % |
| R3 — Fatigue et DEL | 20 % |
| R4 — Extrêmes et ancrage | 10 % |
| R5 — Structures tubulaires (tour, entretoise, SCF) | 10 % |
| Synthèse commune et soutenance | 10 % |
| **Attitude** (participation, tableau/oral, autonomie, rigueur, initiative — 4 niveaux) | **20 %** |

Critère transversal : toute conclusion non étayée par un chiffre, ou tout chiffre présenté sans ses limites, est pénalisé.

---

### 7. Lexique de la chaîne de charges

| Terme | Ce que c'est |
|---|---|
| **Load Case Table (LCT)** | Liste des simulations : chaque ligne fixe un vent (intensité, direction), un état de mer (spectre, Hs, Tp, direction), un courant (intensité, direction), une marée, une seed vent, une seed houle, et une occurrence. Si besoin : désalignement de nacelle, vague extrême (Hmax, Tmax), défaut. |
| **Scatter diagram** | Table d'occurrence conjointe des états de mer (Hs, Tp), souvent par direction. |
| **Binning / lumping** | Regrouper des événements voisins en classes / attribuer à chaque classe une valeur représentative (moyenne, maximum, ou proportionnelle au dommage). |
| **Seed** | Graine d'une réalisation aléatoire de vent turbulent ou de houle irrégulière. |
| **DLC** | Design Load Case : situation de conception (production, défaut, arrêt, parking…) associée à une condition de vent et de mer. |
| **NSS / SSS / ESS** | Normal / Severe / Extreme Sea State. |
| **ULS / FLS** | État limite ultime (extrêmes) / état limite de fatigue (cumul de dommage). |
| **Rainflow** | Comptage des cycles d'un signal (amplitude et moyenne de chaque cycle). |
| **Courbe S-N** | Nombre de cycles admissible N pour une étendue de contrainte S : log N = log ā − m·log S, en général bilinéaire. Dépend de la soudure, de la finition, du milieu et de l'épaisseur (DNV-RP-C203). |
| **Miner** | Dommage cumulé D = Σ nᵢ / Nᵢ. |
| **DFF** | Design Fatigue Factor : coefficient de sécurité sur la durée de vie. |
| **DEL court terme** | Sₑ = ( Σ nᵢ·Sᵢᵐ / nₑ )^(1/m), avec nₑ = fₑ·T. Exemple : fₑ = 1 Hz et T = 600 s donnent nₑ = 600 cycles. |
| **DEL long terme** | Sₑₜ = ( Σⱼ Oⱼ·Sₑ,ⱼᵐ )^(1/m), Oⱼ = part de la durée de vie représentée par la simulation j. |
| **Matrice de concomitance** | Combinaisons d'efforts simultanés utilisées pour la vérification ULS. |
| **SCF / point chaud** | Facteur de concentration de contrainte au point le plus sollicité d'un assemblage soudé. |

### 8. Règles du projet

- **Rendus** : dans le dossier `rendus/` de votre clone du dépôt (non suivi par git), au format indiqué pour chaque rendu, à la date du planning.
- **Normes** : les normes citées sont disponibles sur Vega. Citer la norme, l'édition et le paragraphe utilisés.
- **Outils d'IA** : autorisés comme assistants. Vous restez responsables de chaque chiffre et de chaque phrase rendus ; vous devez pouvoir refaire et expliquer tout calcul à l'oral.
- **Calcul** : les simulations longues se lancent hors séance (salle C09 ou machine personnelle). Le temps de calcul fait partie de la planification que l'on attend d'un ingénieur.
- **Ne pas conclure trop vite** : une tendance observée sur une seule seed ou un seul cas est une hypothèse, pas un résultat.
