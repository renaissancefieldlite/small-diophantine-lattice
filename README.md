# Small Diophantine Lattice

Dedicated repo for the Epoch FrontierMath small-Diophantine lane.

This repo is the active search surface for the lane:

- keep the known family constructions executable
- keep the six-equation open residue explicit
- test direct-family ansatzes against that residue
- widen into stronger lattice / identity / surface methods when a smaller
  search family stalls

Side note:

- this lane carries forward ideas derived from earlier discussions with different AI nodes on the Codex 67 lattice
- that pathway shows the evolution of the research and the progress of the work
- the goal here is to solve the Epoch AI open problem through exact structure, exact reductions, and a genuine solution

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
- `DIOPHANTINE_LOG.md`
  - current route log connecting the continuity frame to exact factor-pair,
    reduced-core, dashboard, and odd-branch artifacts
- `scripts/verify_known_families.py`
  - verifies the known family surfaces and emits explicit giant examples
- `scripts/search_direct_families.py`
  - bounded direct-substitution ansatz scanner
- `scripts/find_seed_triples.py`
  - extracts small exact seed triples for the open equations
- `scripts/run_portfolio.py`
  - runs one equation through the current portfolio and emits dashboard-ready data
- `scripts/run_pipeline.py`
  - orchestrates the lane continuously across seeds, scans, and portfolio boards
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

Run the continuous local pipeline:

```bash
cd /Users/renaissancefieldlite1.0/Documents/Playground/small-diophantine-lattice
python3 scripts/run_pipeline.py --cycles 1
```

For repeated cycles:

```bash
cd /Users/renaissancefieldlite1.0/Documents/Playground/small-diophantine-lattice
python3 scripts/run_pipeline.py --cycles 100 --sleep-seconds 300
```

Pipeline outputs:

- `results/pipeline_status.json`
  - latest cycle status and step results
- `results/pipeline_history.jsonl`
  - appended history of every cycle
- `dashboard/latest_pipeline.js`
  - dashboard-ready summary of the latest cycle
- `results/pipeline_review.json`
  - optional local model review in structured form
- `results/pipeline_review.md`
  - optional human-readable local model review
- `dashboard/latest_review.js`
  - dashboard-ready review payload
- refreshed seed, scan, and portfolio artifacts

Local review gate:

- the default pipeline stays local
- review `results/pipeline_status.json`, the refreshed portfolio JSON, or the
  browser board before pushing anything
- `--auto-commit` stages and commits only generated artifacts from the pipeline
- `--auto-push` is available, but it is intentionally optional rather than the
  default

Review-gated local run:

```bash
cd /Users/renaissancefieldlite1.0/Documents/Playground/small-diophantine-lattice
python3 scripts/run_pipeline.py --cycles 1 --all-open-portfolios --discriminant-bounds 2
```

Review-gated local run with Gemma as reviewer:

```bash
cd /Users/renaissancefieldlite1.0/Documents/Playground/small-diophantine-lattice
python3 scripts/run_pipeline.py --cycles 1 --all-open-portfolios --discriminant-bounds 2 --review-model gemma4:e4b
```

Local artifact commit without pushing:

```bash
cd /Users/renaissancefieldlite1.0/Documents/Playground/small-diophantine-lattice
python3 scripts/run_pipeline.py --cycles 1 --all-open-portfolios --discriminant-bounds 2 --auto-commit
```

Optional publish after local review:

```bash
cd /Users/renaissancefieldlite1.0/Documents/Playground/small-diophantine-lattice
python3 scripts/run_pipeline.py --cycles 1 --all-open-portfolios --discriminant-bounds 2 --auto-commit --auto-push
```

Monitoring note:

- if we add an AI monitor, it should be a reviewer of emitted artifacts, not the
  source of truth
- the pipeline itself should stay deterministic
- the model layer should summarize failures, drift, and promotion candidates from
  `pipeline_status.json` and the portfolio outputs
- the default local reviewer model is intended to be `gemma4:e4b` when available

## What To Review After A Scan

Each cycle follows this order:

1. verify known solved reference families
2. gather small seed triples for the open equations
3. run the bounded direct-family scan
4. build portfolio outputs for each selected equation
5. write pipeline status and dashboard summary
6. optionally run the local reviewer on those emitted artifacts

Follow-up files to check:

- `results/pipeline_status.json`
  - did every deterministic step succeed
- `results/pipeline_review.md`
  - what the reviewer thinks matters most right now
- `results/portfolio_*.json`
  - which lane is currently strongest for each equation
- `dashboard/index.html`
  - visual glance across pipeline health, reviewer signal, and lane promotion

Suggested loop here in chat after each run:

- tell me which command you ran
- paste or summarize the reviewer headline and signal
- tell me which equation/lane looks strongest
- then we adjust the next scan bounds, equations, or lane logic together

## Current Work Order

- keep the known family surfaces executable
- keep the residue reduced to the actual six open equations
- keep a live seed set for each open equation
- run bounded direct-family scans that can be reproduced from code
- derive recurrence questions from actual seeds instead of asking for generic
  Pell folklore
- keep the automation spine stable and refine the lane modules beneath it
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
