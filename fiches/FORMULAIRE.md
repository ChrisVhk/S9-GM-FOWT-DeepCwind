<!-- destinations: github, word -->
# Formulaire du projet DMO-S9 — une feuille recto-verso, par phase

Rappel de **relations**, pas de valeurs : aucune valeur de réponse aux questions de rendu. Chaque
formule a son unité, son domaine et son piège. Pour la démarche et les exemples, voir les fiches
(F1 pour la phase 0). Les fiches des phases suivantes s'ajouteront ; ce formulaire se complète sans
réécriture (sections par phase).

## RECTO

### Phase 0 — Aéro-régulation et vérifications à la main (fiche F1)

| Relation | Unités | Domaine / piège |
|---|---|---|
| `λ = Ω·R / V` | `Ω` rad/s, `R` m, `V` m/s | `RotSpeed` est en **tr/min** : `Ω[rad/s] = Ω[tr/min] × 2π/60` |
| `P = ½ ρ A V³ Cp(λ, β)`, `A = πR²` | W | `Cp ≤ 16/27` (Betz), jamais atteint |
| `T = ½ ρ A V² Ct(λ, β)` | N | `Ct` varie avec `λ` et le calage : à `Ct` constant seulement sous le régime nominal |
| `Ω_gén = N_boîte × Ω_rotor` | rad/s | les seuils du contrôleur sont **côté génératrice** : convertir avant de comparer |
| Loi de Region 2 : `Ω = λ*·V/R` | rad/s | **vérifier la région d'abord** : sous le seuil de Region 2, rampe de Region 1½ ; au-dessus du régime nominal, plafonnée |
| `TwrBsMyt ≈ T × (H_moyeu − TowerBsHt)` | N·m | moment au **pied de tour** : bras compté depuis `TowerBsHt` (lu dans ElastoDyn), pas depuis le niveau de la mer |
| `f₁ₚ = RotSpeed / 60`, `f₃ₚ = 3 f₁ₚ` | Hz | `RotSpeed` en tr/min ; la pale voit 1P, la tour 3P (3 pales identiques) |
| Statistiques d'un canal : `ȳ`, `σ = √(Σ(yᵢ−ȳ)²/N)`, min, max | unité du canal | **sur `t ≥ t₀`** : écarter le transitoire, `t₀` choisi sur la courbe, jamais 0 par défaut |

Constantes du modèle (lues dans `main.fst`) : `g = 9,80665 m/s²`, `ρ_air = 1,225 kg/m³`,
`ρ_eau = 1025 kg/m³`.

### Phase 1 — Du site à la Load Case Table

| Relation | Domaine / piège |
|---|---|
| Occurrences `O_j` des cases (classes de vent, Hs, Tp) | `Σ O_j = 100 %` — falsifie le binning |
| Énergie de houle par unité de surface `E = ρ g Hs² / 16` | proportionnelle à `Hs²` : comparer la LCT au site par l'énergie, pas par la moyenne de `Hs` |
| Intensité de turbulence `TI = σ_u / U_moy` | par classe de vent ; une seule *seed* ne donne pas la variabilité |
| Durée de référence d'un cas turbulent : 600 s (IEC 61400-1) | 300 s = durée réduite du tutoriel |

### Phase 2 — Hydrostatique, houle, flotteur

| Relation | Unités | Domaine / piège |
|---|---|---|
| Dispersion `ω² = g k tanh(k h)` | rad/s, 1/m, m | eau profonde : `ω² = g k`, `λ_houle = g T² / (2π)` |
| Raideur de heave `K₃₃ = ρ g A_wp` | N/m | `A_wp` : aire de flottaison |
| `GM = KB + BM − KG`, `BM = I_wp / ∇` | m | `K₅₅ ≈ ρ g ∇ GM` (sans ancrage) |
| Période propre `T_n = 2π √((M + A_ajoutée) / K)` | s | masse **ajoutée** comprise |
| Morison (cylindre fin) : `f = ρ C_m (πD²/4) u̇ + ½ ρ C_d D · abs(u) · u`, `C_m = 1 + C_a` | N/m | **valable si `D/λ_houle < 0,2`** ; forme du cylindre fixe — pour une structure mobile, vitesses relatives ; au-delà, théorie potentielle (WAMIT) |
| Keulegan–Carpenter `KC = u_max T / D` | – | choisit le régime inertie / traînée |

## VERSO

### Phase 3 — Fatigue

| Relation | Domaine / piège |
|---|---|
| Courbe S–N : `N = a · S⁻ᵐ` | `S` = **étendue** de contrainte, pas l'amplitude : `ΔS = 2 × amplitude` (piège de l'énoncé) |
| Miner : `D = Σ nᵢ / Nᵢ` | linéaire, sans effet de séquence ; `D < 1/DFF` |
| Court terme (DEL) : `S_e = (Σ nᵢ Sᵢᵐ / n_e)^(1/m)`, `n_e = f_e · T` | `m` de la courbe S–N ; `f_e` : fréquence équivalente choisie et annoncée |
| Long terme : `S_e,LT = (Σⱼ O_j · S_e,j^m)^(1/m)` | pondération par les occurrences de la LCT (`O_j` en fraction, `Σ O_j = 1` ; même `n_e` pour tous les cas) |
| Rainflow (ASTM E1049) | compte des cycles fermés ; résidu à traiter |

Test de bon sens : une sinusoïde d'étendue et de fréquence connues doit redonner le DEL calculé à la main.

### Phase 4 — Extrêmes et ancrage

| Relation | Domaine / piège |
|---|---|
| Ligne caténaire (partie suspendue) : tension en tête `T = H + w·h` | `H` : tension horizontale, `w` : poids linéique **immergé**, `h` : hauteur de la tête au-dessus du fond ; ligne partiellement posée au fond seulement |
| Extrême d'une grandeur : maximum sur **plusieurs réalisations** de vent | un maximum d'une seule réalisation n'est pas un extrême de dimensionnement |

### Phase 5 — Structures tubulaires (tour, flotteur)

| Relation | Unités | Domaine / piège |
|---|---|---|
| Tube mince : `A ≈ π D t`, `I ≈ π D³ t / 8`, `W = I/(D/2) = π D² t / 4` | m², m⁴, m³ | valable pour `t ≪ D` |
| Contrainte de flexion composée : `σ = N/A + M/W` | Pa | signe de `N` (compression négative) |
| Cisaillement maximal tube mince : `τ_max = 2V / A` | Pa | |
| Von Mises (σ axial + τ) : `σ_VM = √(σ² + 3 τ²)` | Pa | comparer à la limite élastique avec coefficient |
| Nœud tubulaire : `β = d / D` (d : diamètre de l'entretoise, D : du membre principal) | – | les formules paramétriques (Efthymiou) ont un **domaine de validité** ; hors domaine, refuser le calcul, ne pas extrapoler |

<!-- DTU : emplacement réservé, invisible des étudiants — relations supplémentaires d'aéro-régulation et de charges du cours construit
     avec le DTU. Crédit à inscrire quand la matière entrera : « Technical University of Denmark (DTU) — https://www.dtu.dk/english ».
     [DTU:BEGIN FORM-AERO] [DTU:END FORM-AERO] -->

## Sources

Relations usuelles de la mécanique, de l'hydrodynamique et de la résistance des matériaux ; constantes
`g`, `ρ_air`, `ρ_eau` : fichier `main.fst` du tutoriel. Jonkman et al. 2009 (NREL/TP-500-38060) pour la machine ;
fiche F1 pour la phase 0. Les relations de fatigue et de structure renvoient aux fiches de phase quand elles
seront publiées : en attendant, toute valeur numérique (courbe S–N, paramètres de nœud) se relit à la source
avant d'entrer dans un rendu.
