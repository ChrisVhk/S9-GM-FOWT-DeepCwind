<!-- destinations: github, word -->
# Corrigé des exercices gradués de la fiche F1 (IEA 15 MW)

Exercices non notés de [`F1_Aero-regulation.md`](F1_Aero-regulation.md). Données : Gaertner et al.
2020, NREL/TP-5000-75698 (Tab. ES-1 p.iv ; Tab. ES-2 p.vi ; §3.1 p.17 ; §3.2 p.18 ; §4 p.21).
Hypothèses : `ρ = 1,225 kg/m³` (non lue dans le rapport), pied de tour au sommet de la pièce de
transition (15 m), `R = 120 m`, `A = πR² ≈ 45 239 m²`, `λ* = 9,0`, `Cp = 0,489`, `Ct = 0,799`.
Ces exercices ne portent pas sur la NREL 5 MW du rendu R0.

1. **`V = 9 m/s`.** `Ω = 9 × 9/120 = 0,675 rad/s ≈ 6,45 rpm`. Au-dessus du minimum de 5 rpm et sous le
   régime nominal (7,55 rpm) : région de suivi du `λ` optimal (le vent est entre 6,98 et 10,59 m/s).
2. **`V = 6 m/s`.** `λ*·V/R = 9 × 6/120 = 0,45 rad/s ≈ 4,30 rpm`, sous le minimum de 5 rpm : région de vitesse
   minimale (« Region 1.5 »). La machine tient 5 rpm ; `λ` réel `= 5 × (2π/60) × 120/6 ≈ 10,5`, au-dessus de
   `λ* = 9,0`. (6 m/s est sous le seuil de 6,98 m/s : cohérent.)
3. **`V = 10 m/s`.** `Ω = 9 × 10/120 = 0,75 rad/s ≈ 7,16 rpm` (sous 7,55 rpm : encore dans la région du `λ`
   optimal). `T = ½ × 1,225 × 45 239 × 10² × 0,799 ≈ 2 214 kN`. Moment : `2 214 × (150 − 15) ≈ 2,99·10⁵ kN·m
   ≈ 299 MN·m`. `P_aéro = ½ × 1,225 × 45 239 × 10³ × 0,489 ≈ 13,5 MW`, inférieure à 15 MW : cohérent avec un vent
   (10 m/s) sous le vent nominal (10,59 m/s).
4. **1P et 3P.** À 5 rpm : `f₁ₚ = 5/60 ≈ 0,083 Hz`, `f₃ₚ ≈ 0,25 Hz`. À 7,55 rpm : `f₁ₚ ≈ 0,126 Hz`,
   `f₃ₚ ≈ 0,378 Hz`. Dans les deux cas `0,17 Hz` est entre 1P et 3P (le rapport l'affirme pour tous les
   vents, §4 p.21) : vérifié aux deux bornes, donc entre les deux.
5. **`M ≈ T × 150`.** L'erreur est de compter le bras depuis le niveau de la mer au lieu du pied de tour :
   `150/135 − 1 ≈ +11 %` sur le moment (`2 214 × 150 ≈ 332 MN·m` au lieu de `299 MN·m`). Cet écart est
   **sous** la tolérance de ±20 % : elle l'aurait laissé passer. C'est exactement pourquoi une tolérance
   large ne valide pas une formule — on vérifie d'abord le bras de levier, pas seulement l'écart final.
