# Factor-Pair Search: full_minus2

- Generated: `2026-04-16 00:50:29`
- Equation: `z^2 + y^2 z + x^3 - 2 = 0`

## Formulation

- `p = -z`
- `q = z + y^2`
- `p q = x^3 - 2`
- `p + q = y^2`

## Canonical Examples

- `x=-380`: `y=39`, `p=-6686`, `q=8207`, `y^2=1521`
- `x=-199`: `y=308`, `p=-83`, `q=94947`, `y^2=94864`
- `x=-94`: `y=221`, `p=-17`, `q=48858`, `y^2=48841`
- `x=-52`: `y=31`, `p=-129`, `q=1090`, `y^2=961`
- `x=-32`: `y=9`, `p=-145`, `q=226`, `y^2=81`
- `x=-7`: `y=8`, `p=-5`, `q=69`, `y^2=64`
- `x=-2`: `y=3`, `p=-1`, `q=10`, `y^2=9`
- `x=0`: `y=1`, `p=-1`, `q=2`, `y^2=1`
- `x=1`: `y=0`, `p=1`, `q=-1`, `y^2=0`
- `x=8`: `y=7`, `p=15`, `q=34`, `y^2=49`
- `x=20`: `y=17`, `p=31`, `q=258`, `y^2=289`
- `x=26`: `y=17`, `p=87`, `q=202`, `y^2=289`

## Repeated y-Shells

- `y=17` (`y^2=289`) occurs for `x=[20, 26]`

## Template Results

### shifted_linear_linear_linear

- Result: `no_go`
- The Groebner basis contains w^4, so every rational solution has w = 0.
- With w = 0, the quadratic form 12 v^2 + 12 v w + 97 w^2 reduces to 12 v^2, so v = 0.
- The linear basis relation 12 u + 6 v - 11 w = 0 then forces u = 0.

### shifted_quadratic_linear_cubic

- Result: `no_go`
- If u2 = 0, then the leading equation forces a3 = 0, and the remaining Groebner basis forces a2 = 0, which collapses to the already-eliminated linear template.
- If u2 != 0, write u2 = -m^2 and a3 = ± m^3. After the exact substitutions u1 = m U and v1 = m V, both sign cases reduce to Groebner basis 1 in U and V.
- So this shifted quadratic/linear/cubic factor-pair family has no rational nonconstant solution through the seed.

### shifted_even_quartic_cubic_sextic

- Result: `no_go`
- The odd-degree coefficients force b1 = 0 and b3 = 0, so the cubic y-profile collapses to y = 3 + b2 t^2.
- With b3 = 0, the leading equation becomes a4^3 = -p6^2, so write a4 = -m^2 and p6 = ± m^3.
- After the exact substitutions a2 = A m and b2 = B m, both sign cases reduce to Groebner basis 1 in A and B.
- So this even quartic/cubic/sextic factor-pair identity has no rational nonconstant solution through the seed.

### general_quartic_cubic_sextic_reduction

- Result: `reduced_core_system`

### general_b1_zero_leading_surface_reduction

- Result: `symbolic_reduction`
- Inside the reduced quartic/cubic/sextic core, the entire b1 = 0 slice can be solved symbolically before fixing any specific leading point.
- On b1 = 0, E11 is linear in b2 unless the exceptional coefficient 1809 p6 - 239 b3^2 vanishes.
- Away from that exceptional coefficient, E11 forces an exact proportionality b2 = -(324 a2 (b3^2 - 2 p6)) / (1809 p6 - 239 b3^2).
- Substituting this into E7 gives a pure quadratic obstruction in a2 of the form D(a4,b3,p6) a2^2 - a4 C(b3,p6) = 0.
- The constant coefficient polynomial satisfies C(b3,p6) = 2 (1809 p6 - 239 b3^2)^2, so the obstruction is controlled by the remaining quadratic coefficient D.
- Viewed as a quadratic in p6, D has discriminant -28006710336 b3^4, so for every integer leading point with b3 != 0 the coefficient D is strictly positive.
- Therefore, away from the exceptional slice, the non-exceptional obstruction D(a4,b3,p6) a2^2 = a4 C(b3,p6) forces a4 > 0 because both D and C are positive.
- So every integer leading point with a4 < 0 is globally impossible on the b1 = 0 branch by sign alone.
- On the leading surface b3^2 p6 - p6^2 = a4^3, the numerator of C becomes 2 (-239 a4^3 + 1570 p6^2)^2.
- On the exceptional coefficient slice 1809 p6 - 239 b3^2 = 0, E11 collapses to -24 a2 b3^3 / 67, so for integer leading branches with b3 != 0 it forces a2 = 0.
- With a2 = 0 on that same slice, E7 reduces to 1089 a4 - 205 b2^2 = 0, so b2 = 33 u and a4 = 205 u^2 for some integer u.
- Writing b3 = 603 m to make p6 = 239 b3^2 / 1809 integral gives p6 = 48039 m^2 and a4^3 = 15159667230 m^4 on the leading surface.
- Substituting a4 = 205 u^2 gives 25 * 41^3 * u^6 = 2 * 3^2 * 67^2 * 157 * 239 * m^4, which is impossible because the 41-adic valuation would have to satisfy 3 + 6 v41(u) = 4 v41(m).
- Therefore the exceptional coefficient slice has no integer leading points, so the symbolic b1 = 0 reduction is universal on the integer leading surface.

### weighted_scaling_reduction

- Result: `symbolic_reduction`
- The reduced quartic/cubic/sextic core is weighted-homogeneous with weights wt(a2,b1,b2,a4,b3,p6) = (2,1,2,4,3,6).
- Under the scaling (a2,b1,b2,a4,b3,p6) = (T^2 A, T B, T^2 C, T^4 A4, T^3 B3, T^6 P6), the core equations scale as E6 -> T^6 E6, E7 -> T^7 E7, E10 -> T^10 E10, and E11 -> T^11 E11.
- Therefore any exact no-go for a leading point (A4, B3, P6) automatically kills the entire weighted scaling family (T^4 A4, T^3 B3, T^6 P6).
- This explains, for example, why (32, 24, 64) reproduces the same reduced-core obstruction pattern as (2, 3, 1): it is the T = 2 member of the family (2 T^4, 3 T^3, T^6).

### t_sign_symmetry_reduction

- Result: `symbolic_reduction`
- Replacing t by -t preserves the quartic x(t), the sextic p(t), and the leading coefficient p6, while it flips the odd coefficients b1, b3, p1, p3, and p5.
- So every reduced-core branch over (a4, b3, p6) has a partner over (a4, -b3, p6) with the same exact solvability status.
- This lets the primitive leading-surface queue keep only one sign of b3, which is why the current scan window drops from 122 signed primitive branches to 61 sign-reduced representatives.

### root_swap_symmetry_reduction

- Result: `symbolic_reduction`
- The original equation is quadratic in z, so every solution (x, y, z) has a partner obtained by swapping to the other quadratic root z' = -y^2 - z.
- In factor-pair language this is exactly the involution (p, q) -> (q, p), since p = -z and q = z + y^2.
- On reduced-core leading coefficients, the involution fixes a4 and b3 and sends p6 to q6 = b3^2 - p6.
- Therefore an exact no-go for (a4, b3, p6) automatically gives the same no-go for its paired leading point (a4, b3, b3^2 - p6).
- This explains, for example, the paired branches (2, 3, 1) <-> (2, 3, 8), (-18, 3, -72) <-> (-18, 3, 81), and (27, 18, 81) <-> (27, 18, 243).

### odd_branch_unit_normalization_reduction

- Result: `symbolic_reduction`
- On the odd branch b1 != 0, weighted homogeneity lets us divide out b1 completely and rewrite the reduced core in the universal variables (u, v, A, B, P) with b1 normalized to 1.
- So every odd-branch solution over an integer leading point produces a rational solution of the normalized system (E6, E7, E10, E11) on the rational leading surface -A^3 + B^2 P - P^2 = 0.
- Inside that normalized odd system, E11 splits off the root-swap-fixed slice 2 P = B^2. There E11 collapses to 2357947691 B^3 v, so the slice is forced onto v = 0.
- The same slice is exactly the weighted scaling family (A, B, P) = (4 T^4, 4 T^3, 8 T^6), which is already eliminated by the exact no-go at the primitive branch (4, 4, 8).
- So the live odd frontier is the asymmetric normalized surface 2 P != B^2 together with the unit-normalized equations above.

### branch_lead_2_3_1

- Result: `no_go`
- The b1 = 0 branch is impossible by the exact square obstruction coming from E7 after the linear E11 reduction.
- The b1 != 0 branch is impossible because the two exact nonzero-b1 elimination polynomials are coprime.
- Therefore the reduced quartic/cubic/sextic factor-pair branch over the leading point [2, 3, 1] has no rational solution.

### branch_lead_2_3_8

- Result: `no_go`
- The b1 = 0 branch is impossible by the exact square obstruction coming from E7 after the linear E11 reduction.
- The b1 != 0 branch is impossible because the two exact nonzero-b1 elimination polynomials are coprime.
- Therefore the reduced quartic/cubic/sextic factor-pair branch over the leading point [2, 3, 8] has no rational solution.

### branch_lead_4_4_8

- Result: `no_go`
- The b1 = 0 branch is impossible by the exact square obstruction coming from E7 after the linear E11 reduction.
- The b1 != 0 branch is impossible because the two exact nonzero-b1 elimination polynomials are coprime.
- Therefore the reduced quartic/cubic/sextic factor-pair branch over the leading point [4, 4, 8] has no rational solution.

### branch_lead_m8_4_32

- Result: `no_go`
- The b1 = 0 branch is impossible by the exact square obstruction coming from E7 after the linear E11 reduction.
- The b1 != 0 branch is impossible because the two exact nonzero-b1 elimination polynomials are coprime.
- Therefore the reduced quartic/cubic/sextic factor-pair branch over the leading point [-8, 4, 32] has no rational solution.

### branch_lead_m8_4_m16

- Result: `no_go`
- The b1 = 0 branch is impossible by the exact square obstruction coming from E7 after the linear E11 reduction.
- The b1 != 0 branch is impossible because the two exact nonzero-b1 elimination polynomials are coprime.
- Therefore the reduced quartic/cubic/sextic factor-pair branch over the leading point [-8, 4, -16] has no rational solution.

### shifted_quadratic_quadratic_quadratic

- Result: `no_hit_in_bounded_scan`
- Normalized bounded scan on `(a, b)` in `[-6,6] x [-10,10]` returned `0` hit(s).

## Next Action

Three seed-shifted factor-pair templates are now eliminated exactly, the b1 = 0 side of the reduced core is symbolically compressed, and every stored small leading-surface branch is eliminated exactly. Because the reduced core is weighted-homogeneous and root-swap symmetric, these branch eliminations also kill their entire scaling families and their paired p6 <-> b3^2 - p6 partners. After also quotienting by the exact t -> -t sign symmetry, the live odd frontier now sits on the asymmetric unit-normalized system b1 = 1 with 2 P != B^2. On the b1 = 0 side, every negative-a4 leading point is now dead globally by sign, so the remaining work is to rule out rational squares on the positive-a4 side.
