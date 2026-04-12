# Latest Source State

Date checked: `2026-04-11`

## Epoch page

Source:

- <https://epoch.ai/frontiermath/open-problems/small-diophantine>

Latest source-backed status on that page:

- the overall problem is still unsolved
- on `2026-03-05`, `GPT-5.4 Pro` solved two of the nine full equations by
  direct substitution
- the page now also says the problem authors adapted one of those substitutions
  to solve a third equation:
  - `z^2 + y^2 z + x^3 + x - 1 = 0`

Therefore the currently open full residue is:

- `z^2 + y^2 z + x^3 - 2 = 0`
- `z^2 + y^2 z + x^3 - x - 1 = 0`
- `z^2 + y^2 z + x^3 - 3 = 0`
- `z^2 + y^2 z + x^3 + 3 = 0`
- `z^2 + y^2 z + x^3 - x - 2 = 0`
- `z^2 + y^2 z + x^3 - x + 2 = 0`

## Official direct-substitution note

Source:

- <https://epoch.ai/files/open-problems/small-diophantine-two-families.pdf>

This PDF gives explicit infinite families for:

- `z^2 + y^2 z - z + x^3 + 2 = 0`
- `z^2 + y^2 z + x^3 + x + 1 = 0`

The first family is built by forcing the right-hand side to become an obvious
cube after:

- `y = s + 2`
- `z = -31 s^2 + 4 s - 1`
- `x = u s`
- `u^3 + 930 s = 368`

The second family is a polynomial identity:

- `x(t) = -108 t^4 - 24 t^2 - 2`
- `y(t) = 36 t^3 + 2 t`
- `z(t) = 648 t^6 + 288 t^4 + 50 t^2 + 3`

## Warm-up source

Source:

- <https://mathoverflow.net/a/412128>

Tomita's construction solves:

- `Y(Z^2 - Y) = X^3 + 2`

Under:

- `X = x`
- `Y = -z`
- `Z = y`

this is exactly the warm-up:

- `z^2 + y^2 z + x^3 + 2 = 0`

The warm-up is therefore a verified benchmark lane, but it is not one of the
nine full equations.
