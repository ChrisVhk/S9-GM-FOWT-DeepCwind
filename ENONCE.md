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

**Le temps de calcul est une ressource d'ingénieur.** Une simulation de 600 s prend environ 25 min sur une machine de la salle, une simulation d'une heure plus de 2 h — ordre de grandeur pour un cas complet (flottant, houle, ancrage) ; les cas plus simples du tutoriel de prise en main sont nettement plus rapides (voir les temps mesurés dans `tutorials/prise_en_main/README.md` et `seances/0b/README.md`). Une LCT mal construite coûte des heures de machine pour rien : c'est pour cela qu'elle est validée avant lancement.

**Fiches « minimum vital ».** Huit fiches de deux pages donnent le socle théorique nécessaire à chaque étape du projet (`fiches/` de ce dépôt). Une seule existe à ce jour (F1) ; les suivantes seront publiées au fil du projet, pas toutes avant lundi.

| Fiche | Sujet | Utile pour |
|---|---|---|
| F1 — Aéro-régulation | TSR, zones de régulation, poussée du rotor | Phase 0a |
| F2 — Houle linéaire | Théorie d'Airy, spectre, Hs/Tp | Phase 0b, phase 1 |
| F3 — Hydrostatique | Raideurs K33/K55, carène, GM | Phase 0b |
| F4 — Morison | Coefficients Cd/Ca, efforts répartis sur un membre | Phase 0b, phase 5 |
| F5 — Hydrodynamique potentielle | Base de données WAMIT, radiation/diffraction | Phase 2 |
| F6 — Aérodynamique et amortissement négatif | Amortissement aéro d'un flotteur en tangage | Phase 2 |
| F7 — Caténaire statique | Équation de la chaîne, raideur de ligne | Phase 4 |
| F8 — Ancrage dynamique et fatigue | MoorDyn vs quasi-statique, FAIRTEN et rainflow | Phase 3, phase 4 |

*Correspondance construite à partir du sujet de chaque fiche ; à confirmer phase par phase à mesure que les fiches F2-F8 sont rédigées et publiées.*

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

#### Phase 0 — Tutoriel de prise en main : de l'éolienne fixe à l'éolienne flottante (6 h)

**À lire avant la séance : F1 (Aéro-régulation).**

**Objectif** : savoir organiser, lancer, lire et **vérifier à la main** une simulation OpenFAST, puis voir ce que change le passage du fixe au flottant. Le tutoriel se trouve dans `tutorials/prise_en_main/` du dépôt du cours.

##### Séance 0a — lundi (3 h)

1. **Installer l'environnement** (sans droits administrateur) en suivant `INSTALLATION.md` du dépôt :
   - cloner le dépôt du cours (adresse donnée en séance) ;
   - créer l'environnement à partir du fichier `environment.yml` fourni ;
   - vérifier : `openfast -v` doit afficher **`OpenFAST-v5.0.0`**. Une autre version = installation à reprendre.
2. **Organisation d'un calcul** : fichiers de base du modèle / un dossier par cas de charge / un script de lancement. Lancer les cas LHEEA 01 (tour seule) et 02 (rotor libre) pour vérifier que tout fonctionne.
3. **Lire un `.fst`** : pour chaque section, dire ce qu'on modifie pour débuter (durée, pas de temps, modules actifs, degrés de liberté, sorties) et ce qu'on laisse tel quel.
4. **Régulation de l'éolienne NREL 5 MW, à la main** (fiche F1) : avec R = 63 m, vitesse en bout de pale maximale 80 m/s, régime nominal 12,1 tr/min, puissance nominale 5 MW et un TSR optimal de 7,55 (Jonkman 2009), construire le tableau vitesse de vent → vitesse de rotation → puissance, et identifier les zones de fonctionnement (Region 2, 2½, 3).
5. **Éolienne fixe (monopieu OC3), cas à vent constant et à échelon** :

| Cas | Vent | Ce qu'on regarde |
|---|---|---|
| F01 | constant 7,5 m/s | régime établi, poussée, moment en pied de tour |
| F02 | échelon de 5 à 20 m/s | passage d'une zone de régulation à l'autre, temps de réaction du calage des pales |

**Vérifications à la main** (à confronter aux sorties) : fréquence de rotation 1P à partir de `RotSpeed` et sa trace sur le moment en pied de pale ; poussée du rotor (ordre de grandeur) ; moment en pied de tour ≈ poussée × (hauteur du moyeu − hauteur du pied de tour `TowerBsHt`) — `TowerBsHt` se lit dans `config_elastodyn.dat` : le moment est pris au pied de la tour, pas au niveau de la mer.

##### Séance 0b — séance suivante (3 h)

**À lire avant la séance : F2 (Houle linéaire), F3 (Hydrostatique), F4 (Morison)** — dès qu'elles sont publiées.

6. **Éolienne fixe, vent turbulent** : générer les champs de vent avec **TurbSim** (vous choisissez et justifiez l'intensité de turbulence), puis lancer :

| Cas | Vent | Zone de régulation |
|---|---|---|
| F03 | turbulent 7,5 m/s | zone 1 |
| F04 | turbulent 12 m/s | zone intermédiaire |
| F05 | turbulent 16 m/s | zone 3 |

7. **Architecture du modèle de flotteur, au tableur** : à partir de la géométrie de la DeepCwind (dimensions fournies), compléter le classeur `DeepCwind_ARCHITECTURE.xlsx` du tutoriel : **nœuds** (coordonnées dans le repère inertiel), **membres** (nœud 1 → nœud 2, jeu de propriétés, discrétisation), **jeux de propriétés** (diamètre, épaisseur) et **coefficients hydrodynamiques** (Cd, Ca) par groupe — colonne centrale, colonnes déportées, bases, pontoons, entretoises. Retrouver ensuite chaque colonne du tableau dans le fichier HydroDyn du modèle. C'est la façon la plus directe de comprendre comment OpenFAST « voit » une structure tubulaire, et ce tableau resservira en phase 5 (entretoises, β = d/D).
8. **Éolienne flottante (DeepCwind)** — d'abord **à la main** : raideur hydrostatique en pilonnement K33 = ρ·g·Awl et en tangage K55 = Δ·g·GM, à partir des dimensions fournies ; comparer aux valeurs utilisées par HydroDyn, puis aux périodes propres.

| Cas | Vent | Houle |
|---|---|---|
| D00 | aucun | régulière (Airy), H = 6 m, T = 10 s |
| D01 | constant 7,5 m/s | régulière, H = 6 m, T = 10 s |
| D02 | échelon de 5 à 20 m/s | régulière, H = 6 m, T = 10 s |
| D03 à D05 | turbulent 7,5 / 12 / 16 m/s (mêmes champs que F03-F05) | irrégulière JONSWAP, Hs = 6 m, Tp = 10 s |

9. **Comparer fixe et flottant** sur un même tableau : pour `RootMyb1`, `YawBrFxn`, `TwrBsFxt`, `TwrBsMyt` et `RotSpeed`, relever **maximum et écart-type** des cas 03 à 05. Le DEL de ce tableau sera complété en phase 3, quand vous l'aurez programmé.
10. **Le vent apparent** : sur D01, estimer l'amplitude de la variation de vent vue par le rotor du fait des mouvements du flotteur.

**Rendu R0** :
- Q0.1 — Tableau de régulation à la main et comparaison avec le cas F02.
- Q0.2 — Vérifications à la main de F01 (1P, poussée, moment en pied de tour) : écarts et explication.
- Q0.3 — Classeur d'architecture complété, et correspondance avec le fichier HydroDyn ; K33 et K55 à la main contre HydroDyn ; périodes propres qui en découlent.
- Q0.4 — Tableau fixe / flottant (max, écart-type) et trois constats argumentés : ce qui change, pourquoi, et ce que ce tableau ne permet pas encore de conclure sur la fatigue.
- Q0.5 — Citez les paramètres qui définissent une ligne de Load Case Table (au moins huit) et dites lesquels vous avez déjà fait varier dans ce tutoriel.
- Q0.6 (si vous avez relancé un cas turbulent à 600 s en plus des 300 s de la séance) — Comparez les statistiques d'un même canal entre les deux durées : l'écart est-il dans le bruit, ou significatif ? Qu'est-ce que cela vous dit sur la durée à retenir pour un rendu qui compte ?

**Si l'installation échoue en séance** : elle doit être terminée **avant la séance 0b**, à la maison ou en salle C09. Noter l'erreur exacte dans R0. Les cas turbulents prennent du temps de calcul : lancez-les dès la fin de la séance 0b si vous n'avez pas fini.

#### Phase 1 — Du site à la Load Case Table

**Données fournies** (dossier `data/metocean/` du dépôt, publié par l'enseignant avant cette phase — absent du dépôt à son ouverture) : un site réel au large de l'île de Barra (Écosse), à partir des conditions publiées en accès ouvert par le projet européen FLOATECH (Papi et al., université de Florence, réanalyse ERA5, licence CC-BY 4.0) : distribution conjointe vent / Hs / Tp / désalignement vent-houle, extrêmes ; courant et niveaux d'eau d'après le projet européen LIFES50+. Citer ces sources dans vos rendus.

1. Lire le scatter diagram : quelles cellules sont les plus probables ? Lesquelles portent le plus d'énergie de houle ?
2. Choisir les DLC du projet et justifier par composant :
   - **FLS** : DLC 1.2 (production normale) ; discuter le DLC 7.2 (parking, faible amortissement aérodynamique) ;
   - **ULS** : DLC 6.1 (parking, vent extrême, ESS) et DLC 1.6 (production, SSS) ; justifier si le DLC 6.2 peut être écarté à ce stade.
3. **Construire la LCT de votre groupe** (10 à 15 cas maximum, 600 s simulées chacun) : binning, lumping, occurrence Oⱼ de chaque ligne. Le budget de calcul est une contrainte réelle : une simulation de 600 s prend environ 25 min sur une machine de la salle.
4. **Vérifier la représentativité** : comparer, paramètre par paramètre, les occurrences de votre LCT à celles du site. Dire où vous avez accepté d'être moins précis, et pourquoi c'est acceptable (loin des périodes propres ? faible occurrence ?).

**Rendu R1** : la LCT (tableur), une page de justification, le tableau de représentativité.

#### Phase 2 — Simulations de référence et sensibilité

**À lire avant la séance : F5 (Hydrodynamique potentielle), F6 (Aérodynamique et amortissement négatif)** — dès qu'elles sont publiées.

1. **Référence commune** (cas LHEEA 05 / modèle OC4) : lancer, vérifier l'équilibre (tension statique des lignes, position moyenne du flotteur).
2. **Lâchers (free decay)** en surge, heave, pitch : mesurer les périodes propres. Les comparer aux valeurs publiées OC4/OC5 (référence fournie) et **dire où se situent ces périodes par rapport aux périodes de houle de votre scatter diagram**.
3. **Sensibilité** : lancer la LCT de votre groupe en ne faisant varier **que** votre famille de paramètres, tout le reste fixé à la référence.
4. Pour chaque cas : statistiques (moyenne, écart-type, max, min) aux points imposés, et spectres de réponse.

**Rendu R2** : tableau des résultats, figures commentées. Pour chaque tendance observée : *théorie attendue → ce que montrent les chiffres → ce qu'ils ne permettent pas de conclure* (une seule seed ? durée trop courte ? autre paramètre couplé ?).

#### Phase 3 — Fatigue

**À lire avant la séance : F8 (Ancrage dynamique et fatigue)** — dès qu'elle est publiée.

0. **Atelier tour, premier passage** : prise en main de la chaîne DEL court terme → long terme →
   courbe S-N → épaisseur, sur le classeur de l'atelier tel quel (sa propre géométrie de tour et
   ses propres données d'entrée, pas celles du projet) — d'abord avec `SCF = 1`, puis `SCF = 2`, en
   comparant épaisseurs et masse. Voir [`seances/atelier_tour/`](seances/atelier_tour/README.md)
   pour la théorie derrière chaque étape. C'est la **méthode** (pas la géométrie ni les résultats)
   que vous reprendrez au point 2 ci-dessous, sur la tour du projet, puis en Phase 5 avec vos
   propres charges.
1. **Rainflow** sur `TwrBsMyt` et `FAIRTEN1-3`, pour chaque cas.
2. **Contrainte en pied de tour** : passer du moment à la contrainte de flexion, avec les
   caractéristiques de section de la tour de **référence** (aire, inertie) — pas une donnée
   fournie, à calculer vous-mêmes comme à l'étape 0, mais pour cette géométrie-ci : diamètre
   extérieur lu dans le fichier AeroDyn de la tour (`TwrDiam`/`TwrElev`), épaisseur à retrouver à
   partir de la masse linéique (`TMassDen` du fichier tour ElastoDyn) — **à condition de choisir
   une masse volumique**, et c'est un choix à justifier, pas une évidence : l'acier pur donne
   7850 kg/m³, mais une tour réelle inclut peinture, boulonnerie et soudures, souvent représentées
   par une masse volumique « effective » plus élevée dans ce genre de modèle. Dites laquelle vous
   retenez et pourquoi, et vérifiez la cohérence du résultat (diamètre/épaisseur réalistes pour une
   éolienne 5 MW). Appliquer un **SCF = 2** (hypothèse d'avant-projet).
3. **Courbe S-N** : choisir la courbe DNV-RP-C203 adaptée (type de soudure, milieu air ou eau, épaisseur) et justifier ce choix.
4. **Dommage** : Miner sur chaque cas, puis cumul pondéré par les occurrences Oⱼ ; durée de vie avec le DFF imposé.
5. **DEL** : programmer vous-mêmes le DEL court terme Sₑ et long terme Sₑₜ (formules au lexique), puis comparer avec l'outil d'`openfast_toolbox`. Un écart entre les deux doit être expliqué.
6. **Limites** : montrer sur un de vos cas pourquoi le DEL ne suffit pas pour conclure (perte de concomitance, hypothèse monopente, dépendance à la fréquence propre).
7. **Confrontation à une référence de 50 ans** : le projet FLOATECH a simulé la même éolienne OC4 sur le même site pendant 50 ans d'états de mer réels (environ 450 000 simulations d'une heure). Comparez le DEL long terme obtenu avec votre LCT de 10 à 15 cas au DEL de référence fourni. L'écart mesure la qualité de votre binning et de votre lumping : expliquez-le, et dites ce qu'il faudrait changer dans votre LCT pour le réduire.

**Rendu R3** : comparatif SCF = 1 / SCF = 2 de l'atelier tour (étape 0) ; note de calcul fatigue (hypothèses, courbe S-N retenue, dommages par cas, durée de vie), comparaison DEL maison vs outil.

#### Phase 4 — Extrêmes et ancrage

**À lire avant la séance : F7 (Caténaire statique)** — dès qu'elle est publiée.

1. Lancer les cas ULS retenus en phase 1 (DLC 6.1 et 1.6) pour la référence et pour la variante la plus pénalisante de votre groupe.
2. Comparer tensions maximales et capacité de la ligne (fournie) ; mouvements maximaux du flotteur.
3. **Groupe centre** : comparer MoorDyn et MAP++ sur le même cas extrême — quand l'approche quasi-statique sous-estime-t-elle les tensions ?
4. **Groupes bâbord et tribord** : ce qui, dans votre famille de paramètres, pilote l'extrême d'ancrage.

**Rendu R4** : tableau ULS, vérification des lignes, conclusion argumentée.

#### Phase 5 — Structures tubulaires : tour et flotteur

Quatre niveaux de modèle existent pour la structure d'un flotteur. Le projet en mobilise trois.

| Niveau | Méthode | Ce qu'il donne | Qui |
|---|---|---|---|
| **A** | Modèle rigide (référence) | Fatigue et extrêmes du pied de tour et des chaumards | Tous |
| **B** | Effort de section estimé à la main : force d'écartement / de pincement des colonnes (*split / squeeze*) en houle de travers | Effort nominal dans une entretoise, puis contrainte nominale × SCF | Tous |
| **C** | Flotteur flexible modélisé en poutres (SubDyn couplé au flotteur) | Séries temporelles d'efforts intérieurs par membre, donc rainflow sur une entretoise | Groupe centre |
| **D** | Éléments finis locaux de l'assemblage | Contrainte au point chaud, SCF « vrai » | Lecture d'une étude publiée |

1. **Tour (niveau A), atelier tour second passage, avec vos données.** Même méthode qu'à la Phase
   3 (étape 0), mais toutes les entrées sont désormais les vôtres, pour **chaque groupe** :
   - **géométrie de départ** = tour OC4 du modèle de référence — longueur et base lues dans le
     fichier ElastoDyn principal (`TowerHt`, `TowerBsHt`), diamètres extérieurs lus dans le fichier
     AeroDyn de la tour (`TwrDiam`/`TwrElev`), épaisseurs retrouvées comme au point 2 de la Phase 3
     (à partir de `TMassDen` et d'une masse volumique justifiée) — rien n'est présumé ;
   - **DEL court terme** par cas de votre LCT (sur les canaux de pied ou de tête de tour que vous
     aurez identifiés au §4/§9b du tutoriel atelier tour, exposant `m = 4` pour la branche
     principale et `m = 3`/`5` pour la sensibilité) — un outil dédié sera annoncé en séance, sinon
     reprenez le programme du point 5 de la Phase 3 ;
   - **occurrences `Oⱼ`** = celles de **votre** LCT de la Phase 1 (table conjointe vent × houle ×
     courant), pas la loi de Weibull propre au classeur de l'atelier (voir
     [`seances/atelier_tour/`](seances/atelier_tour/README.md), §2) ;
   - **efforts extrêmes** = vos cas DLC 1.6 et 6.1 de la Phase 4 (ceci complète l'ULS du niveau A,
     qui restait partiel avec les seules données de l'atelier) ;
   - **test de l'hypothèse « somme des DEL »** (théorie au §4, exercice concret au §9b de
     `seances/atelier_tour/`) avec les jauges de tour OpenFAST, à **trois hauteurs** (pied, milieu,
     sommet) : à chacune, trois DEL à comparer deux à deux, pas directement entre les extrêmes —
     la méthode de l'atelier (deux DEL combinés après coup) contre le calcul exact du même modèle
     de transport (un seul rainflow sur le signal combiné point par point) isole le coût de
     l'hypothèse de concomitance ; ce calcul exact contre le DEL mesuré directement à la jauge
     isole ce que le modèle de transport statique ne capture pas (poids propre et inertie de la
     tour, mouvements du flotteur en tangage, absents du classeur de l'atelier qui suppose une
     tour sur base fixe). Commentez les deux écarts et leur sens, et s'ils sont les mêmes aux trois
     hauteurs.

   Vérifier la section résultante en FLS (contrainte de flexion × SCF = 2 vs contrainte admissible
   en fatigue) et en ULS (Von Mises vs limite élastique). Ajuster l'épaisseur pour satisfaire les
   deux critères à masse minimale.
2. **Boucle de dimensionnement, une itération.** Réinjectez les `R`, `S`, `T` (masse linéique,
   raideurs) de la tour dimensionnée au point 1 dans le fichier tour d'ElastoDyn, et relancez
   **un** nouveau calcul OpenFAST : un cas de fatigue représentatif (celui qui dimensionnait au
   point 1) et le cas ULS dimensionnant. Commentez la variation des efforts obtenus par rapport au
   premier passage.
   > **Point dur, à régler avant de lancer ce calcul** : ElastoDyn ne demande pas seulement `R`,
   > `S`, `T` par station, mais aussi les **formes modales** de la tour (coefficients polynomiaux
   > `TwFAM1Sh(2-5)` etc., qui décrivent la déformée assumée du premier mode). Aucun outil de
   > calcul de ces coefficients à partir d'une nouvelle distribution de masse/raideur n'est
   > disponible dans l'environnement du cours (ni BModes, ni d'équivalent dans `openfast_toolbox` —
   > son module `linearization` analyse un modèle déjà construit, via la linéarisation d'OpenFAST
   > lui-même, mais ne calcule pas de nouveaux coefficients d'entrée). **Approximation retenue** :
   > conservez les
   > coefficients polynomiaux d'origine tels quels, et dites-le explicitement comme une
   > approximation.
   >
   > Pour en estimer l'ordre de grandeur sur la fréquence propre (sans attendre un résultat
   > garanti), un quotient de Rayleigh, en réutilisant la **même** déformée assumée `φ(x)` (celle
   > des coefficients d'origine) mais évaluée avec la **nouvelle** distribution de raideur `EI(x)`
   > et de masse linéique `m(x)` :
   > `f² ∝ [∫EI(x)·φ''(x)²dx] / [∫m(x)·φ(x)²dx + M_tête·φ(L)²]`
   > — le terme `M_tête·φ(L)²` (masse du rotor + moyeu + nacelle en tête, très supérieure à la
   > masse de la tour elle-même : à relever dans le fichier ElastoDyn principal, `NacMass`,
   > `HubMass`, et la masse des pales) **ne doit pas être oublié**, il domine le dénominateur pour
   > une éolienne. Attention à l'interprétation : le principe de Rayleigh garantit qu'une déformée
   > assumée différente de la vraie déformée propre **d'une même structure** surestime sa fréquence
   > — il ne garantit **pas** que la fréquence obtenue ainsi pour la tour redimensionnée encadre sa
   > vraie nouvelle fréquence (ce sont deux structures différentes). Ce calcul donne donc un ordre
   > de grandeur de l'effet de l'approximation, pas une borne garantie. Si l'écart avec la fréquence
   > d'origine est significatif, dites-le et discutez-en — ce point ne demande pas de corriger
   > l'approximation, seulement d'en estimer l'effet.

   Comparez les fréquences propres de la tour (avant/après l'itération) aux fréquences 1P et 3P du
   rotor (voir `seances/atelier_tour/`, §10, point non couvert par l'atelier — à faire ici).
3. **Entretoise (niveau B)** : estimer l'effort d'écartement des colonnes pour la houle la plus pénalisante (longueur d'onde de l'ordre de deux fois l'entraxe des colonnes), en déduire l'effort axial et la contrainte nominale dans l'entretoise. Comparer à une contrainte admissible.
4. **Domaine de validité du SCF** : relever dans le document de définition OC4 les diamètres des entretoises, des colonnes déportées et de la colonne centrale ; calculer β = d/D pour chaque jonction ; dire si les formules paramétriques d'Efthymiou (établies pour les jackets) s'appliquent. Conclure sur ce qu'il faut faire quand elles ne s'appliquent pas.
5. **Groupe centre (niveau C)** : comparer, sur un même état de mer, l'effort dans une entretoise obtenu au niveau B et la série temporelle du modèle flexible. Expliquer pourquoi la répartition des efforts hydrodynamiques (potentiels ramenés en un point / Morison répartis) conditionne la validité du résultat.
6. **Assemblage (niveau D)** : à partir de l'étude publiée fournie (assemblage colonne-entretoise d'une semi-submersible), expliquer la chaîne *efforts globaux → modèle local éléments finis → SCF au point chaud → S-N → durée de vie*, et discuter les ordres de grandeur obtenus.

Rappel : aux niveaux A, B et C on obtient une contrainte **nominale**. Le SCF reste indispensable, et il faut savoir justifier d'où il vient.

**Rendu R5** : note de vérification de la tour (premier passage et itération), calcul d'entretoise (niveau B), tableau β et conclusion sur le SCF ; groupe centre : comparaison B / C.

#### Phase 6 — Synthèse commune et soutenance

Les trois groupes mettent leurs résultats en commun dans **un seul tableau de sensibilité** : pour chaque famille de paramètres, l'effet sur le dommage en pied de tour, le dommage aux chaumards et les extrêmes. Question finale : **pour un projet réel sur ce site, quelles études de sensibilité demanderiez-vous au bureau d'études, et lesquelles jugeriez-vous inutiles ?**

Soutenance par groupe : 15 min + 10 min de questions.

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
