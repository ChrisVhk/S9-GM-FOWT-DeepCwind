# Atelier tour — tutoriel d'accompagnement

Ce tutoriel accompagne le **classeur de l'atelier**, distribué sur Vega. Ce n'est **pas un
second cours** : le support de l'atelier donne les étapes de calcul, pas la théorie qui les
justifie. C'est ce qui manque ici — question physique par question physique, pas colonne par
colonne.

## 0. Où ça se branche dans le projet

Cet atelier **répète en avance** ce que vous referez vous-même en [Phase 5](../../ENONCE.md),
niveau A (tour) :

> *« Tour (niveau A) : à partir des DEL long terme et des efforts extrêmes, vérifier une section
> en pied de tour en FLS (contrainte de flexion × SCF = 2 vs contrainte admissible en fatigue) et
> en ULS (Von Mises vs limite élastique). Ajuster l'épaisseur pour satisfaire les deux critères à
> masse minimale. »*

La seule différence : en Phase 5 vous partirez des sorties de **vos propres** simulations
OpenFAST (DEL et extrêmes du pied de tour, `TwrBsMyt`, `TwrBsFzt`...), pas d'un jeu de charges
déjà fourni. L'atelier sert donc de répétition générale de la méthode, sur un jeu de données prêt
à l'emploi, avant de la refaire sur vos propres résultats.

## 1. Tronc de cône creux et propriétés de section

### Bloc Théorie
**Question physique** : comment une tour tubulaire, de diamètre et d'épaisseur variables du pied
au sommet, se représente-t-elle dans un modèle de poutre comme celui d'ElastoDyn ?

**Modèle** : chaque tronçon de la tour est un tronc de cône creux (diamètre extérieur et
épaisseur interpolés linéairement entre le pied et le sommet). De sa géométrie on tire : la masse
linéique (colonne `TMassDen` d'ElastoDyn), l'aire de section et le moment quadratique `Iyy`
(raideur de flexion `TwFAStif`/`TwSSStif` = `E·Iyy`, identique dans les deux plans car la section
est circulaire). Domaine de validité : la poutre d'Euler-Bernoulli suppose que les sections planes
restent planes — valable tant que le rapport diamètre/épaisseur de la paroi reste assez petit pour
exclure un voilement local de la coque (hors du périmètre de cet atelier, voir §10).

**Ordre de grandeur attendu** : la masse linéique doit décroître du pied vers le sommet (le
diamètre et l'épaisseur diminuent tous les deux) ; l'inertie de flexion décroît plus vite encore,
car elle varie environ comme le cube du diamètre pour une coque mince.

**Ce que le modèle ne permet pas de conclure** : rien sur la répartition de contrainte **dans
l'épaisseur** de la paroi (flexion locale de la coque, ovalisation) — le modèle de poutre ne voit
que la section globale.

**Renvois** : colonnes `R`, `S`, `T` du classeur (masse linéique et raideurs ElastoDyn) ; voir
aussi `models/oc4_rtest/.../ElastoDyn_Tower.dat` pour la même table sur la tour de référence du
projet (§9a).

## 2. DEL court terme, DEL long terme

### Bloc Théorie
**Question physique** : comment résumer des heures de signal de moment fléchissant fluctuant
(un cas par classe de vent) en une poignée de chiffres utilisables pour un calcul de fatigue ?

**Modèle** : le comptage rainflow transforme un signal en cycles (étendue de contrainte, moyenne,
nombre d'occurrences). Le **DEL court terme** `Sₑ` est l'étendue de cycle constante qui
produirait, sur le même nombre total de cycles, le même dommage Miner que le spectre réel compté
— pour un exposant `m` de courbe S-N donné (la pondération en `étendue^m` vient directement de
Miner, pas d'un choix arbitraire). Le **DEL long terme** `Sₑₜ` combine les DEL court terme de
chaque classe de vent, pondérés par leur probabilité d'occurrence `Oⱼ` (loi de Weibull du site),
de la même façon : `Sₑₜ = (Σⱼ Oⱼ·Sₑ,ⱼᵐ)^(1/m)`.

**Ordre de grandeur attendu** : une moyenne d'ordre `m` est toujours comprise entre la moyenne
arithmétique pondérée des `Sₑ,ⱼ` et leur maximum — et d'autant plus proche de ce maximum que `m`
est grand. Le DEL long terme doit donc se situer dans cet intervalle, tiré vers les classes de
vent à la fois fréquentes et à fort DEL court terme (pas nécessairement les plus fréquentes tout
court : une classe de vent fort, rare, peut dominer si son DEL court terme est très supérieur aux
autres).

**Ce que le modèle ne permet pas de conclure** : le DEL ne dit rien sur l'ordre réel des cycles ni
sur d'éventuels effets de séquence (Miner suppose le dommage indépendant de l'ordre). Il ne dit
pas non plus si la distribution de vent utilisée est représentative d'une vie de 20-25 ans — voir
l'`ENONCE.md`, Phase 3, point 7 (confrontation à une référence de 50 ans).

**Renvois** : lexique de la chaîne de charges dans l'`ENONCE.md` (définitions DEL court/long
terme) ; onglet `Long term DEL` du classeur ; Phase 3 de l'`ENONCE.md` où vous programmerez ce
même calcul sur vos propres cas.

## 3. Courbe S-N, coude à 10⁷ cycles (milieu air), effet d'épaisseur

### Bloc Théorie
**Question physique** : à quelle étendue de contrainte une soudure tient-elle un nombre donné
de cycles, et pourquoi cette tenue dépend-elle de l'épaisseur de la pièce ?

**Modèle** : une courbe S-N (DNV-RP-C203) relie étendue de contrainte et nombre de cycles à
rupture par une loi en puissance, `N·Sᵐ = a`, sur une pente `m` donnée — avec un **coude** à 10⁷
cycles où la pente change (la fissuration change de régime), pour les courbes en milieu air (les
courbes en eau de mer avec protection cathodique ont un coude à un autre nombre de cycles — une
tour de DeepCwind est émergée, donc en air). Au-delà d'une épaisseur de référence (25 mm chez
DNV), un **effet d'épaisseur** réduit la contrainte admissible : une tôle plus épaisse a un
gradient de contrainte plus faible en surface et des défauts de fabrication statistiquement plus
pénalisants, d'où un facteur correctif `(t_réf/t)^k`.

**Ordre de grandeur attendu** : la contrainte admissible doit décroître quand l'épaisseur
augmente au-delà de l'épaisseur de référence, et rester constante en dessous (le facteur correctif
est plafonné à 1).

**Ce que le modèle ne permet pas de conclure** : la courbe S-N ne dit rien sur la soudure
**réellement réalisée** sur le chantier (géométrie du cordon, défauts) — c'est pour cela qu'on
choisit une classe de détail pessimiste par convention, pas en mesurant la soudure a posteriori.
Le classeur de l'atelier retient une valeur de l'exposant `k` à confronter à la valeur DNV : à vous
de la retrouver et de juger si l'écart compte, sans publier ici lequel des deux est utilisé.

**Renvois** : DNV-RP-C203 (édition en vigueur), tableau des courbes S-N et correction
d'épaisseur — citez l'édition exacte et le numéro de section dans votre rendu, ce tutoriel ne les
donne pas ; colonnes `W` (contrainte admissible) et onglet `SN-Curve DATABASE` du classeur.

## 4. Pourquoi une somme de DEL est une hypothèse

### Bloc Théorie
**Question physique** : le classeur combine un DEL de moment de flexion et un DEL d'effort axial
en les additionnant directement en contrainte — sous quelle condition cela a-t-il un sens ?

**Modèle** : sommer deux DEL (calculés séparément sur deux canaux différents, chacun son propre
comptage rainflow) revient à supposer que leurs cycles maximaux sont **concomitants** — c'est-à-
dire qu'ils surviennent en même temps, dans le même sens. Deux signaux réels sont rarement
exactement en phase : une somme de DEL est donc une **majoration**, pas un calcul exact du dommage
combiné (qui demanderait de construire la contrainte combinée `σ(t) = Fz(t)/A + M(t)·c/I`
directement, point par point, puis de faire un seul comptage rainflow sur ce signal combiné).

**Ordre de grandeur attendu** : l'écart entre la somme de DEL et un rainflow direct sur la
contrainte combinée croît avec le déphasage entre les deux signaux d'effort ; il est nul si les
deux signaux sont parfaitement corrélés (même origine physique — par exemple, la poussée moyenne
du rotor et le moment de flexion moyen qu'elle induit en pied de tour varient tous les deux avec
la même vitesse de vent, et sont donc fortement corrélés).

**Ce que le modèle ne permet pas de conclure** : cette hypothèse ne dit rien sur le signe de
l'erreur commise pour **votre** cas particulier — seulement qu'elle va dans le sens
conservateur en théorie, pas qu'elle l'est forcément en pratique si le comptage lui-même est
biaisé.

**Renvois** : `ENONCE.md`, Phase 3, point 6 (« Limites : [...] perte de concomitance ») — vous y
retrouverez cette même question sur vos propres canaux.

## 5. Von Mises dans un tube

### Bloc Théorie
**Question physique** : comment combiner contrainte axiale, flexion (deux plans), cisaillement et
torsion en un seul critère de dimensionnement ULS ?

**Modèle** : en un point de la paroi, on calcule la contrainte normale (axiale + flexion
résultante dans le plan le plus défavorable) et la contrainte de cisaillement (effort tranchant +
torsion), puis on les combine par le critère de Von Mises,
`σ_vM = √(σ² + 3τ²)`, comparé à la limite élastique du matériau. Pour un tube soumis à un moment
fléchissant **biaxial** (Mx, My), le point le plus sollicité n'est pas forcément aligné avec l'un
des deux axes : il faut balayer plusieurs angles autour de la circonférence pour trouver le
maximum (le classeur en teste plusieurs, pas un seul).

**Ordre de grandeur attendu** : pour une tour élancée en flexion dominante, la contrainte de
cisaillement reste très inférieure à la contrainte normale — le terme `3τ²` pèse peu devant `σ²`
dans la combinaison.

**Ce que le modèle ne permet pas de conclure** : Von Mises est un critère de **plasticité**,
pertinent pour un matériau ductile en charge statique extrême (ULS) — ce n'est pas un critère de
fatigue (voir §3-4, où c'est une comparaison à une courbe S-N qui gouverne, pas Von Mises).

**Renvois** : colonnes `Z` à `AV` du classeur (transport des efforts, combinaison Von Mises) ;
`ENONCE.md`, Phase 5, point 1 (vérification ULS en pied de tour).

## 6. Dimensionnement pleinement contraint — et pourquoi le Solveur n'est pas indispensable

### Bloc Théorie
**Question physique** : comment choisir l'épaisseur de chaque tronçon pour minimiser la masse
totale tout en respectant les deux critères (FLS et ULS) ?

**Modèle** : les propriétés de section d'un tronçon (aire, inertie) ne dépendent que de **sa
propre** épaisseur. Si, de plus, aucun effort transporté par la tour ne dépend lui-même de
l'épaisseur des tronçons (à vérifier : un effort axial qui inclurait le poids propre des tronçons
au-dessus romprait cette indépendance), minimiser la masse totale
sous contrainte « les deux critères ≤ 1 partout » revient à amener **chaque tronçon** à son
critère le plus contraignant égal à 1 (dimensionnement pleinement contraint, *fully stressed
design*). Comme les tronçons sont indépendants, il n'y a pas besoin d'une optimisation globale
(Solveur) : une recherche de racine **section par section** (valeur-cible, ou *Objectif à
atteindre* dans un tableur) suffit, et donne le même résultat.

**Ordre de grandeur attendu** : la méthode section-par-section et le Solveur doivent converger
vers la même épaisseur à chaque section, à la tolérance du solveur numérique près.

**Ce que le modèle ne permet pas de conclure** : cette indépendance section par section, si elle
est vérifiée, est une conséquence du modèle choisi (section circulaire simple, pas de raidisseur
ni de bride qui coupleraient des tronçons voisins) — elle ne se généralise pas à toute structure.
Elle ne dit non plus rien sur le couplage **dynamique** (la fréquence propre de la tour dépend,
elle, de la distribution d'épaisseur dans son ensemble, pas section par section).

**Renvois** : colonne `O` du classeur.

## 7. Une section faite entièrement à la main

Les valeurs ci-dessous sont **inventées pour cet exemple** — aucun rapport avec le classeur de
l'atelier. L'objectif est de vérifier que vous savez refaire la chaîne complète sans tableur.

Tronçon tubulaire : diamètre extérieur `D = 1,0 m`. On cherche l'épaisseur `t` qui vérifie le
critère FLS avec `SCF = 1,5` (délibérément différent du `SCF = 2` imposé par le projet en Phase 3
— pour qu'aucun chiffre de cet exemple ne puisse se confondre avec un chiffre du projet ou de
l'atelier), DEL long terme de flexion `My = 2000 kN·m`, DEL long terme axial `Fz = 100 kN`
(convention OpenFAST : `z` = axe de la tour, effort axial ; `x`/`y` = cisaillement), contrainte
admissible au coude à 10⁷ cycles `σ_coude = 100 MPa`, épaisseur de référence `t_réf = 25 mm`,
exposant d'épaisseur `k = 0,2`. On suppose ici que le DEL long terme a été construit pour ce même
nombre de cycles de référence `nₑ = 10⁷` (sinon il faudrait d'abord ramener l'un ou l'autre au
même `nₑ`, par `Sₑₜ(nₑ)` ∝ `nₑ^(−1/m)` — c'est aussi ce que fait le DFF, le facteur de sécurité en
fatigue imposé en Phase 3, que cet exemple ignore par simplicité).

Aire et inertie d'un tube creux : `P(t) = (π/4)·[D² − (D−2t)²]`, `Q(t) = (π/64)·[D⁴ − (D−2t)⁴]`.
Contrainte DEL : `σ = SCF·(My·(D/2)/Q + Fz/P)`. Contrainte admissible :
`σ_adm = σ_coude·min(1, (t_réf/t)^k)`. Le critère `X_FLS = σ/σ_adm = 1` se résout par balayage
(essayer quelques épaisseurs, encadrer, affiner) — **refaites ce calcul vous-même avant de
regarder les valeurs ci-dessous**, qui ne sont données que pour vous permettre de vous
autocorriger :

| t (mm) | σ (MPa) | σ_adm (MPa) | X_FLS |
|---|---|---|---|
| 20 | 205,3 | 100,0 | 2,05 |
| 40 | 109,0 | 91,0 | 1,20 |
| 52,5 | 86,2 | 86,2 | 1,00 |
| 60 | 77,2 | 83,9 | 0,92 |

→ épaisseur retenue en FLS : **t ≈ 52,5 mm** (racine de `X_FLS = 1`, à affiner par dichotomie
entre 40 et 60 mm si votre balayage initial est plus grossier).

Vérification ULS à cette épaisseur, avec des efforts extrêmes concomitants **également
inventés** — et volontairement choisis plus grands que les DEL ci-dessus, comme il se doit pour
des efforts extrêmes (`Fz = −800 kN` axial, `Mx = 1200 kN·m`, `My = 3000 kN·m`, `Mz = 300 kN·m` de
torsion, acier `Re = 355 MPa`) : la flexion résultante vaut `√(Mx²+My²)·(D/2)/Q ≈ 91,8 MPa` en
valeur absolue, de part et d'autre de l'axe neutre. **Le point le plus défavorable est celui où
flexion et effort axial sont de même signe** (ici, la face comprimée : `σ = σ_axial − |σ_flex| ≈
−5,1 − 91,8 ≈ −96,9 MPa`, pas la face tendue où les deux se retranchent) — pensez-y aussi au §5
quand vous balayez les angles. Torsion pour le cisaillement (`τ = Mz·(D/2)/(2Q) ≈ 4,3 MPa`), puis
Von Mises : vous devriez trouver `σ_vM ≈ 97 MPa`, soit un ratio ULS `X_ULS ≈ 0,27` — très inférieur
à 1. Un tronçon dimensionné pile à sa limite de fatigue peut donc rester très en-deçà de sa limite
ULS : c'est une conséquence de ce jeu de charges et de ce `Re`, pas une généralité absolue (voyez
à quel ordre de grandeur de `Re` ou d'efforts extrêmes l'ULS redeviendrait dimensionnant).

## 8. Encadré — sous Ubuntu

**Table de données / Opérations multiples (LibreOffice Calc)** : `Données → Opérations
multiples` permet de faire varier une cellule d'entrée (par exemple l'épaisseur d'un tronçon) et
de lire l'effet sur une cellule de résultat (le ratio FLS ou ULS), sans modifier la feuille — utile
pour tracer à la main l'allure de `X(t)` avant de chercher la racine.

**Solveur (LibreOffice Calc)** : `Outils → Solveur`, cellule cible = ratio FLS ou ULS, valeur
`1`, cellule variable = l'épaisseur. Le §6 ci-dessus explique pourquoi, dans ce classeur précis,
une recherche de racine section par section (`Outils → Valeur cible`) suffit et donne le même
résultat qu'un Solveur réglé sur toutes les épaisseurs à la fois.

**Point de vigilance** : ces deux manipulations n'ont **pas pu être vérifiées en exécution dans
l'environnement de rédaction de ce tutoriel** (LibreOffice en mode sans affichage y échoue sur
tout fichier, indépendamment de ce classeur — défaut d'environnement documenté en coulisses, pas
du classeur). Les noms de menu ci-dessus sont ceux de LibreOffice Calc 24.x ; si un menu a bougé
dans votre version, testez et signalez l'écart en séance.

## 9. Pont DeepCwind

Deux questions ouvertes, sans valeur de réponse publiée ici.

**(a) Comparer `R`, `S`, `T` du classeur à la tour du modèle de référence du projet.** La tour
`models/oc4_rtest/5MW_OC4Semi_WSt_WavesWN/NRELOffshrBsline5MW_OC4DeepCwindSemi_ElastoDyn_Tower.dat`
donne la même table (`HtFract`, `TMassDen`, `TwFAStif`, `TwSSStif`) pour la tour réelle du projet.
Avant de comparer les valeurs, vérifiez d'abord la **longueur** et la **base** de cette tour dans
`NRELOffshrBsline5MW_OC4DeepCwindSemi_ElastoDyn.dat` (`TowerHt`, `TowerBsHt`) — est-ce la même
convention de hauteur que celle utilisée par le classeur de l'atelier (`C3`, longueur totale) ? Si
non, qu'est-ce que ça change pour comparer les deux séries de valeurs terme à terme ?

**(b) Tester l'hypothèse « somme des DEL » (§4) avec les jauges de tour OpenFAST.** Le modèle de
référence du projet a **une seule jauge de tour configurée, à mi-hauteur** (`NTwGages = 1`,
`TwrGagNd = 10` sur 20 nœuds de tour — pas en pied de tour), et aucun canal `TwHt*` dans
l'`OutList` : la capacité existe (`TwHt<N>{TD,AL,ML}{x,y,z}t`, moment de flexion compris) mais
n'est pas exploitée. Ajoutez en pied de tour les canaux nécessaires (`TwrBsFzt` pour l'effort
axial, `TwrBsMyt` pour le moment, déjà prévus par défaut) sur un cas turbulent, relancez, et
comparez deux calculs de dommage sur ce même pied de tour : (1) somme des DEL calculés séparément
sur `TwrBsFzt` et `TwrBsMyt` ; (2) rainflow direct sur la contrainte combinée reconstruite
point par point, `σ(t) = TwrBsFzt(t)/A + TwrBsMyt(t)·(D/2)/I` — l'écart entre les deux mesure
concrètement ce que coûte l'hypothèse de concomitance du §4.

## 10. Ce que l'atelier ne vérifie pas

| Point non couvert | Où il revient dans le projet |
|---|---|
| Voilement local (flambement de coque mince) | Non traité par ce projet — hors périmètre des niveaux A à D de la Phase 5 |
| Résonance 1P/3P (fréquence rotor/pales vs fréquence propre de tour) | Non traité par ce projet — la Phase 0a introduit la fréquence 1P (`RotSpeed`), mais seulement pour la lire sur le moment en pied de **pale**, pas pour vérifier un écartement avec la fréquence propre de la tour |
| Inertie et mouvements du flotteur (couplage avec la tour) | Phase 2 (simulations de référence et sensibilité) |
| Brides boulonnées (concentration de contrainte à l'assemblage) | Non traité par ce projet — le niveau D de la Phase 5 porte sur un assemblage colonne-entretoise du flotteur, pas sur les brides de tour |

---

*Atelier distribué sur Vega (geste de l'enseignant). Les deux classeurs (à trous et corrigé) ne
sont pas dans ce dépôt.*
