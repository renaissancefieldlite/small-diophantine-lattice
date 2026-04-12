# Small Diophantine Lattice

Dedicated repo for the Epoch FrontierMath small-Diophantine lane.

The goal here is not to mix the warm-up, already-solved direct-substitution
families, and still-open frontier residue into one blurred story. This repo
keeps those layers separate, verifies the known benchmark families, and builds
search code for the remaining open equations.

## Current State

As of `2026-04-11`, the latest Epoch page says:

- the overall problem is still unsolved
- `GPT-5.4 Pro` solved two of the nine full equations by direct substitution
- the problem authors then adapted one of those substitutions to solve a third
  full equation

That leaves `6` open full equations, plus the separate warm-up benchmark.

Benchmarks / solved direct-substitution surfaces:

- warm-up:
  - `z^2 + y^2 z + x^3 + 2 = 0`
  - solved via Tomita's MathOverflow family
- full equation solved by direct substitution:
  - `z^2 + y^2 z - z + x^3 + 2 = 0`
- full equation solved by direct substitution:
  - `z^2 + y^2 z + x^3 + x + 1 = 0`
- full equation now also marked solved on Epoch:
  - `z^2 + y^2 z + x^3 + x - 1 = 0`
  - public family not yet copied into this repo

Still-open full equations:

- `z^2 + y^2 z + x^3 - 2 = 0`
- `z^2 + y^2 z + x^3 - x - 1 = 0`
- `z^2 + y^2 z + x^3 - 3 = 0`
- `z^2 + y^2 z + x^3 + 3 = 0`
- `z^2 + y^2 z + x^3 - x - 2 = 0`
- `z^2 + y^2 z + x^3 - x + 2 = 0`

## Repo Layout

- `data/equations.json`
  - equation metadata and latest known status
- `notes/latest-source-state.md`
  - source-backed status note with dated references
- `notes/strategy.md`
  - current attack plan for the remaining residue
- `RICK_SMALL_DIOPHANTINE_BOOT.md`
  - continuity / baton-pass note for the next Rick
- `scripts/verify_known_families.py`
  - verifies benchmark families and emits explicit giant examples
- `scripts/search_direct_families.py`
  - bounded direct-substitution ansatz scanner
- `results/`
  - generated scan outputs and verified examples

## Search Surfaces

The current first-pass search is intentionally narrow and explicit.

### Surface 1: Pell-discriminant family search

For equations of the form

`z^2 + (y^2 + c) z + x^3 + a x + b = 0`

the quadratic formula in `z` gives discriminant

`Delta = (y^2 + c)^2 - 4(x^3 + a x + b)`.

The warm-up falls because, after a direct substitution

- `x = A n^2 + B n + C`
- `y = D n + E`

the discriminant factors as

`(quadratic)^2 * (quadratic)`,

and the squarefree quadratic can be solved by Pell-style recurrences.

`scripts/search_direct_families.py` searches for exactly that shape.

### Surface 2: Direct polynomial identity search

The solved `x + 1` equation shows a different pattern:

- `x(t)` quartic
- `y(t)` cubic
- `z(t)` sextic

with an identity holding for every integer `t`.

That second surface is described in `notes/strategy.md` and is the next code
addition after the first discriminant scan is stable.

## Quick Start

Verify the known benchmark families:

```bash
cd /Users/renaissancefieldlite1.0/Documents/Playground/small-diophantine-lattice
python3 scripts/verify_known_families.py --emit-json results/known_families_examples.json
```

Run the bounded discriminant scan on the open residue:

```bash
cd /Users/renaissancefieldlite1.0/Documents/Playground/small-diophantine-lattice
python3 scripts/search_direct_families.py --status open --bound 2 --max-results 12 \
  --emit-json results/initial_discriminant_scan_bound2.json
```

## Immediate Goal

The first milestone is not a full solve claim. It is a clean split:

- benchmark families verified
- latest source state preserved
- residue reduced to the actual open equations
- bounded ansatz scan running reproducibly in code

Once that is stable, the next rung is to add the direct polynomial-identity
engine for the `x + 1` style family and aim it at the remaining six equations.

## Current Artifact State

Generated locally in the first pass:

- `results/known_families_examples.json`
  - benchmark giant examples verified for
    - warm-up
    - `-z + x^3 + 2`
    - `x + 1`
- `results/initial_discriminant_scan_bound2.json`
  - zero Pell-discriminant hits in the `[-2, 2]` coefficient box for all six
    currently open full equations
- `results/initial_discriminant_scan_bound3.json`
  - zero Pell-discriminant hits in the `[-3, 3]` coefficient box for all six
    currently open full equations
