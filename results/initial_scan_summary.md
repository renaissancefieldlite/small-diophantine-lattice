# Initial Scan Summary

Date: `2026-04-11`

## Verified benchmark families

File:

- `known_families_examples.json`

Verified locally:

- warm-up `z^2 + y^2 z + x^3 + 2 = 0`
- `z^2 + y^2 z - z + x^3 + 2 = 0`
- `z^2 + y^2 z + x^3 + x + 1 = 0`

Each of those benchmark lanes now has explicit examples with `|x| > 10^50`.

## Bounded Pell-discriminant scan

File:

- `initial_discriminant_scan_bound2.json`
- `initial_discriminant_scan_bound3.json`

Search:

- open equations only
- ansatz:
  - `x = A n^2 + B n + C`
  - `y = D n + E`
- coefficient box:
  - `A, B, C, D, E in [-2, 2]`
  - `A != 0`, `D != 0`
- hit condition:
  - discriminant squarefree part has degree `2`

Result:

- `0` hits for each of the six currently open full equations

Wider follow-up:

- `initial_discriminant_scan_bound3.json`
- same ansatz
- coefficient box:
  - `A, B, C, D, E in [-3, 3]`
- result:
  - again `0` hits for each of the six currently open full equations

Interpretation:

- the remaining residue does not immediately collapse to the same tiny
  Pell-discriminant family that solves the warm-up
- the next code rung should be a polynomial-identity search in the `x ~ t^4`,
  `y ~ t^3`, `z ~ t^6` style
