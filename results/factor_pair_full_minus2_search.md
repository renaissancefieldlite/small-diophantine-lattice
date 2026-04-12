# Factor-Pair Search: full_minus2

- Generated: `2026-04-12 11:21:10`
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

### branch_lead_2_3_1

- Result: `partial_reduction`

### shifted_quadratic_quadratic_quadratic

- Result: `no_hit_in_bounded_scan`
- Normalized bounded scan on `(a, b)` in `[-6,6] x [-10,10]` returned `0` hit(s).

## Next Action

Three seed-shifted factor-pair templates are now eliminated exactly. The live next rung is the odd branch of the reduced quartic/cubic/sextic core on (a2, b1, b2) for the leading point (a4, b3, p6) = (2, 3, 1), after the exact elimination of the b1 = 0 branch.
