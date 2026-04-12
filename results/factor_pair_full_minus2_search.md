# Factor-Pair Search: full_minus2

- Generated: `2026-04-12 14:50:00`
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
- On the leading surface b3^2 p6 - p6^2 = a4^3, the numerator of C becomes 2 (-239 a4^3 + 1570 p6^2)^2.
- On the exceptional coefficient slice 1809 p6 - 239 b3^2 = 0, E11 collapses to -24 a2 b3^3 / 67, so for integer leading branches with b3 != 0 it forces a2 = 0.
- With a2 = 0 on that same slice, E7 reduces to 1089 a4 - 205 b2^2 = 0, so b2 = 33 u and a4 = 205 u^2 for some integer u.
- Writing b3 = 603 m to make p6 = 239 b3^2 / 1809 integral gives p6 = 48039 m^2 and a4^3 = 15159667230 m^4 on the leading surface.
- Substituting a4 = 205 u^2 gives 25 * 41^3 * u^6 = 2 * 3^2 * 67^2 * 157 * 239 * m^4, which is impossible because the 41-adic valuation would have to satisfy 3 + 6 v41(u) = 4 v41(m).
- Therefore the exceptional coefficient slice has no integer leading points, so the symbolic b1 = 0 reduction is universal on the integer leading surface.

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

Three seed-shifted factor-pair templates are now eliminated exactly, and every small integer leading-surface branch currently listed in the reduced core scan ((2, 3, 1), (2, 3, 8), (4, 4, 8), (-8, 4, 32), (-8, 4, -16)) is also eliminated exactly. The live next rung is no longer a stored branch point. It is the leading-surface equation -a4^3 + b3^2 p6 - p6^2 = 0 itself: generate new integer points or parametric families on that surface and feed them into the same exact reduced-core elimination.
