# Small Diophantine Lattice

Dedicated repo for the Epoch FrontierMath small-Diophantine lane.

This repo is the active search surface for the lane:

- keep the known family constructions executable
- keep the six-equation open residue explicit
- test direct-family ansatzes against that residue
- widen into stronger lattice / identity / surface methods when a smaller
  search family stalls

Side note:

- the concept stack behind this lane came from a combination of nodes
- that origin trail is not the priority here
- the priority here is the exact mathematical search surface itself

## Current State

As of `2026-04-11`, the latest Epoch page says:

- the overall problem is still unsolved
- two full equations have public direct-substitution families on the Epoch
  note
- the problem authors then adapted one of those substitutions to solve a third
  full equation

That leaves `6` open full equations, plus the separate warm-up reference lane.

Known family / solved reference surfaces:

- warm-up reference lane:
  - `z^2 + y^2 z + x^3 + 2 = 0`
  - solved via Tomita's MathOverflow family
- full equation with public direct-substitution family:
  - `z^2 + y^2 z - z + x^3 + 2 = 0`
- full equation with public direct-substitution family:
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
- `notes/recurrence_lane.md`
  - seed-to-recurrence plan built from the open equations
- `notes/deepseek_question_pack.md`
  - exact external-model questions for derivation work
- `RICK_SMALL_DIOPHANTINE_BOOT.md`
  - continuity / baton-pass note for the next Rick
- `scripts/verify_known_families.py`
  - verifies the known family surfaces and emits explicit giant examples
- `scripts/search_direct_families.py`
  - bounded direct-substitution ansatz scanner
- `scripts/find_seed_triples.py`
  - extracts small exact seed triples for the open equations
- `scripts/run_portfolio.py`
  - runs one equation through the current portfolio and emits dashboard-ready data
- `dashboard/`
  - optional static visual board for the current portfolio state
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

### Surface 3: Seed-to-recurrence lane

Each open equation already has small exact seed triples. The next recurrence
surface is:

- extract clean seed triples
- derive the discriminant form around those seeds
- search for substitutions that turn the discriminant into an indefinite
  quadratic
- only then build a Pell-style matrix recurrence

That lane now lives in:

- `scripts/find_seed_triples.py`
- `results/open_seed_triples_bound30.json`
- `notes/recurrence_lane.md`
- `notes/deepseek_question_pack.md`

## Quick Start

Verify the known family surfaces:

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

Generate the current one-equation portfolio board:

```bash
cd /Users/renaissancefieldlite1.0/Documents/Playground/small-diophantine-lattice
python3 scripts/run_portfolio.py --equation full_minus2
```

Optional visual component:

- open `dashboard/index.html` directly in a browser
- the board reads `dashboard/latest_portfolio.js`
- this is a thin tracking layer only; the repo and result artifacts remain the
  source of truth

## Current Work Order

- keep the known family surfaces executable
- keep the residue reduced to the actual six open equations
- keep a live seed set for each open equation
- run bounded direct-family scans that can be reproduced from code
- derive recurrence questions from actual seeds instead of asking for generic
  Pell folklore
- add the quartic/cubic/sextic polynomial-identity engine next
- widen into stronger lattice and cubic-surface methods if the smaller ansatzes
  keep returning zero-hit boxes

## Current Artifact State

Generated locally in the first pass:

- `results/known_families_examples.json`
  - giant examples verified for
    - warm-up
    - `-z + x^3 + 2`
    - `x + 1`
- `results/initial_discriminant_scan_bound2.json`
  - zero Pell-discriminant hits in the `[-2, 2]` coefficient box for all six
    currently open full equations
- `results/initial_discriminant_scan_bound3.json`
  - zero Pell-discriminant hits in the `[-3, 3]` coefficient box for all six
    currently open full equations
- `results/open_seed_triples_bound30.json`
  - exact seed triples for each of the six open equations, extracted in a small
    search box and ready for recurrence / surface reduction work
