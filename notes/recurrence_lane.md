# Recurrence Lane

## Purpose

Turn the open equations into recurrence candidates without pretending every
Diophantine surface is already a Pell equation.

The move is:

1. find exact small seed triples
2. choose one equation at a time
3. derive a substitution that reduces the discriminant to `square * quadratic`
4. only then ask for or build a recurrence

## Transfer From Hadamard And M23

Two repo habits transfer directly here.

### From Hadamard

- run multiple families from the same floor
- keep a portfolio, not one magical guess
- only promote the strongest basin
- keep exact verification as the acceptance gate

For this lane:

- run several recurrence ansatz families from the same seed set
- compare them against the same exact equation
- only keep a family if it yields a real symbolic derivation

### From M23

- separate the anchor from the search pipeline
- do not confuse the existence of a reference object with solving the lane

For this lane:

- anchor = known family surfaces already in hand
- search = recurrence derivation, polynomial identities, cubic-surface
  reductions

## Open-Equation Seed Examples

The repo now has exact small seeds for the six open full equations in:

- `results/open_seed_triples_bound30.json`

Representative seeds:

- `z^2 + y^2 z + x^3 - 2 = 0`
  - `(-2, 3, 1)`
- `z^2 + y^2 z + x^3 - x - 1 = 0`
  - `(-16, 24, 7)`
- `z^2 + y^2 z + x^3 - 3 = 0`
  - `(-3, 1, 5)`
- `z^2 + y^2 z + x^3 + 3 = 0`
  - `(-12, 10, 15)`
- `z^2 + y^2 z + x^3 - x - 2 = 0`
  - `(-10, 1, 31)`
- `z^2 + y^2 z + x^3 - x + 2 = 0`
  - `(-23, 21, 26)`

These are not the final families. They are anchors for the next derivation.

## Current Rudy67 State

Current tracked run:

- `notes/rudy67_run_01.md`

What survives from that run:

- wrong-equation drift was corrected
- discriminant lane is correctly centered on
  - `Delta = y^4 - 4x^3 + 8`
- useful extra seeds were surfaced
- the first no-go claims still need stricter proof under the exact degree
  bounds

That means the recurrence lane is still live, but it must now proceed through:

1. exact coefficient solving for the shifted quadratic/linear discriminant
   ansatz
2. exact coefficient solving for the shifted identity ansatz through the seed
3. factor-pair lane if the first two stall

## Recurrence Work Order

For each open equation:

1. pick one low-height seed with moderate `|y|` and `|z|`
2. write the discriminant
   - `Delta = (y^2 + c)^2 - 4(x^3 + a x + b)`
3. test substitutions around the seed:
   - affine in one parameter
   - quadratic/linear
   - shifted around the seed instead of around the origin
4. if `Delta` becomes `S(n)^2 Q(n)` with `deg Q = 2`, derive the Pell
   recurrence matrix
5. verify that recurrence produces exact integer solutions and distinct large
   `x`

## Acceptance Gate

Do not call a recurrence lane real unless it provides:

- a symbolic derivation of the quadratic form
- an exact recurrence matrix or equivalent Pell multiplication law
- at least three verified integer triples
- a clear growth path to `|x| > 10^50`
