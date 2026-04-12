# Strategy

## Goal

Reduce the live frontier to a disciplined residue and attack that residue with
explicit direct-substitution searches before widening into heavier geometry.

Side note:

- the concept build for this lane came from a combination of nodes
- that is background context, not the main work product here
- the main work product is the exact derivation/search pipeline

## Current Split

### Node 1: Known-family verification

Keep the known family surfaces executable and checked:

- warm-up Tomita recurrence
- `-z + x^3 + 2` cube-forcing family
- `x + 1` quartic/cubic/sextic identity

Why:

- they prove the repo's verification path works
- they stop us from confusing `no current hit` with `bad code`
- they expose two genuinely different direct-substitution mechanisms

### Node 2: Pell-discriminant ansatz

For

`z^2 + (y^2 + c) z + x^3 + a x + b = 0`

we get

`Delta = (y^2 + c)^2 - 4(x^3 + a x + b)`.

The first search family is:

- `x = A n^2 + B n + C`
- `y = D n + E`

Search objective:

- `Delta` factors as `square * quadratic`
- the squarefree part has degree `2`
- the quadratic part is indefinite or otherwise Pell-usable

This is the warm-up pattern and may hit some of the remaining equations.

### Node 2A: Seed-to-recurrence derivation

Before asking for a recurrence, pin down a real seed and a real transformed
quadratic form.

Process:

- start from an exact seed triple for one open equation
- rewrite the discriminant around a substitution family
- force the squarefree part toward a degree-`2` indefinite form
- only then derive the recurrence matrix

This is where Rudy's Pell instinct belongs, but as a derived step rather than
as a generic first guess.

### Node 3: Polynomial-identity ansatz

The second search family is:

- `x = a t^4 + b t^2 + c`
- `y = p t^3 + q t`
- `z = r t^6 + s t^4 + u t^2 + v`

for equations with no linear `z` term.

Search objective:

- solve the coefficient identity
  - `z(t)^2 + y(t)^2 z(t) + x(t)^3 + alpha x(t) + beta = 0`
  identically in `t`

This is the shape that solves `x + 1`.

## Order Of Attack

1. verify all known family surfaces locally
2. run bounded Pell-discriminant scans on the six open equations
3. build seed sets and recurrence questions from exact small solutions
4. if the discriminant scan is sparse, add the polynomial-identity engine
5. if both direct-substitution families stall, shift to cubic-surface geometry:
   - rational point
   - tangent-secant
   - rational curves
   - elliptic or conic fibrations after substitution

## What Counts As Progress

- any exact polynomial identity for one open equation
- any Pell-style recurrence family for one open equation
- any clean reduction of an open equation to a genus-`0` or elliptic family
  with infinitely many integral points

## What Does Not Count

- rediscovering only the warm-up family and calling the residue solved
- producing giant numerical triples without a reproducible family
- mixing solved and open equations in one report without status labels
