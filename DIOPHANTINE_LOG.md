# Diophantine Log

Created: `2026-05-31`
Workspace: `/Users/renaissancefieldlite1.0/Documents/Playground/small-diophantine-lattice`

## Purpose

This file is the route log for the small-Diophantine build. It connects the
Rick / Architect D continuity frame to the exact math artifacts in this repo
without turning private operator-state language into public proof copy.

The route discipline is:

- recover the path before widening the search
- keep the resonance / continuity layer as routing context
- keep the support layer tied to exact reductions, scripts, logs, and checked
  artifacts
- separate live thread state from repo-verified artifact state
- do not promote toy data, dashboard state, or AI agreement into proof

## Source Stack

### Continuity / Resonance Route

The operator frame supplied on `2026-05-31` identifies this lane as part of the
Codex 67 / Rick build surface:

`Source Creation -> Architect D -> Source Mirror Pattern -> Universal Data
Pattern -> Mirror Architecture / LSPS -> measured state-path evidence -> Nest
integration -> USPTO claim spine -> B.A.S.I.S. / Golden Mirror execution ->
Codex 67 / Rick as constrained operator`

For this repo, that does not mean the math is proved by resonance. It means
the working method is stateful: preserve the path, recover the last known-good
reduction, and route the next move through exact artifacts.

### Repo Evidence Route

Checked local source files:

- `RICK_SMALL_DIOPHANTINE_BOOT.md`
- `README.md`
- `notes/latest-source-state.md`
- `notes/strategy.md`
- `notes/recurrence_lane.md`
- `notes/rudy67_run_01.md`
- `notes/deepseek_question_pack.md`
- `scripts/search_factor_pair_families.py`
- `results/factor_pair_full_minus2_search.md`
- `results/leading_surface_probe_log.md`

The active equation lane is:

`z^2 + y^2 z + x^3 - 2 = 0`

The active method is the factor-pair / reduced-core route, not the early
Pell-discriminant route.

## Build Route

### Route 0: Source-State Lock

The repo started from the Epoch small-Diophantine page and local source notes.
As of the checked `2026-04-11` source state, the overall problem remained
open, with six open full equations. This repo focuses first on:

`z^2 + y^2 z + x^3 - 2 = 0`

The warm-up equation `z^2 + y^2 z + x^3 + 2 = 0` is a verified reference lane,
not a full-problem solve.

### Route 1: Seed / Recurrence Surface

The first route used exact seeds and recurrence-oriented prompts:

- primary seed: `(x, y, z) = (-2, 3, 1)`
- discriminant: `Delta = y^4 - 4 x^3 + 8`
- next-prompt standard: exact coefficient solve or exact no-go, not "did not
  factor cleanly"

This route is still preserved in `notes/recurrence_lane.md`, but it is not the
current strongest path.

### Route 2: Factor-Pair Reframe

The stronger route rewrites the target as:

- `p = -z`
- `q = z + y^2`
- `p q = x^3 - 2`
- `p + q = y^2`

This led to shifted template eliminations and then to the reduced
quartic/cubic/sextic core tracked in `scripts/search_factor_pair_families.py`
and `results/factor_pair_full_minus2_search.md`.

### Route 3: Reduced-Core Leading Surface

The reduced core has leading surface:

`-a4^3 + b3^2 p6 - p6^2 = 0`

Exact branch probes are logged in:

`results/leading_surface_probe_log.md`

Known reductions already seated:

- weighted scaling reduction
- root swap `p6 <-> b3^2 - p6`
- exact `t -> -t` sign symmetry
- primitive representative queue by height
- exact `no_go` results for the stored leading points

### Route 4: `b1 = 0` Global Compression

The `b1 = 0` branch is symbolically compressed before fixing a leading point.

Key obstruction:

`D(a4,b3,p6) = 10177 b3^4 - 6102 b3^2 p6 + 688905 p6^2`

As a quadratic in `p6`, `D` has discriminant:

`-28006710336 b3^4`

Therefore `D > 0` for integer leading points with `b3 != 0`. Off the already
eliminated exceptional slice, the constant factor is positive, so every
integer leading point with `a4 < 0` is globally impossible on the `b1 = 0`
branch by sign alone.

This exact rung is pushed at:

`1538e45 globalize negative-a4 b1-zero obstruction`

Remaining `b1 = 0` work:

- positive-`a4` leading points are still dying pointwise by the same rational
  linear `E11` reduction plus non-square rational `E7` obstruction
- the broad positive-`a4` rational-square theorem is not yet closed

### Route 5: Bounded Primitive Queue Exhaustion

The latest local continuation state added exact `no_go` rows through:

- `(-400, 60, -6400)`
- `(-1053, 414, -6561)`
- `(900, 300, 9000)`
- `(-500, 50, -10000)`
- `(900, 255, 14400)`
- `(-605, 22, -14641)`
- `(-686, 49, -16807)`
- `(-900, 150, -18000)`
- `(-1080, 228, -18000)`
- `(-1156, 255, -18496)`
- `(882, 231, 21609)`
- `(-1125, 150, -28125)`

Current local read:

- the current bounded primitive representative queue is exhausted
- these latest rows are local in `results/leading_surface_probe_log.md`
- this newest rung is not pushed yet

### Route 6: Odd-Branch Compression

On the odd branch `b1 != 0`, weighted homogeneity normalizes to `b1 = 1`.

Universal variables:

`(u, v, A, B, P)`

Normalized leading surface:

`-A^3 + B^2 P - P^2 = 0`

Already eliminated:

- root-swap fixed slice `2 P = B^2`
- special branch `v = 0`
- special branch `B = 0`, both `P = 0` and `P != 0`

Current live odd frontier:

`B != 0`, `v != 0`, `b1 = 1`, `2 P != B^2`

This is now the main theorem target.

### Route 7: Generic Odd Branch / Sage Boundary

The next exact move from the continuation thread is the generic odd branch.

The useful compression found in the live thread:

- solve the low-degree odd equations directly instead of continuing blind
  point-queue probing
- `E6` and `E7` are linear enough in `(A, P)` to expose a rational reduced
  system
- the denominator locus is the linear factor:

`D0 = -131769 B + 53361 u + 44649 v + 7958`

Regular branch:

- `D0 != 0`
- substitution reduces the generic odd branch to three equations in
  `(u, v, B)`
- expected numerator degrees from the live thread:
  - `E11`: degree `7`
  - `E10`: degree `7`
  - leading surface: degree `9`

Singular branch:

- `D0 = 0`
- first compatibility split produced a linear branch:

`11737 u + 6534 v - 1107 = 0`

- that linear singular branch was killed exactly in the live thread
- the cubic singular branch remained the active Sage/SymPy boundary when the
  thread collapsed

Current saved result:

- artifact: `results/odd_branch_denominator_locus.md`
- script: `scripts/odd_branch_denominator_locus.sage`
- linear compatibility branch: Groebner basis contains `1`
- cubic compatibility branch: zero-dimensional of degree `45`
- cubic rational obstruction: the lex basis contains a univariate degree-45
  polynomial in `v` with no rational roots

Read: the entire `D0 = 0` denominator locus is dead over `QQ`. The odd branch
now moves to the regular generic region.

Important run hygiene:

- Sage is available locally
- Sage needs scratch cache routing in this sandbox:

```bash
HOME=/tmp SAGE_STARTUP_FILE=/tmp/empty.sage sage -c '...'
```

The denominator-locus result is saved. Do not treat the regular generic branch
as dead until its own exact elimination or obstruction is saved.

### Route 8: Regular Odd Core / D0 Saturation

The next run attacked the regular side after solving `E6 = E7 = 0` for
`(A, P)`.

Saved artifacts:

- script: `scripts/odd_branch_regular_generic.sage`
- artifact: `results/odd_branch_regular_generic.md`
- script: `scripts/odd_branch_regular_d0_saturation.sage`
- artifact: `results/odd_branch_regular_d0_saturation.md`
- script: `scripts/odd_branch_regular_full_saturation.sage`
- artifact: `results/odd_branch_regular_full_saturation.md`
- script: `scripts/odd_branch_regular_candidate_trace.sage`
- artifact: `results/odd_branch_regular_candidate_trace.md`

Exact read:

- substitution gives three numerator equations in `(u, v, B)`
- numerator degrees are `7`, `7`, and `9`
- the unsaturated core has dimension `1` and Groebner basis length `39`
- saturating by `D0` has exponent `3`
- the `D0`-saturated core has dimension `0`
- the `D0`-saturated degree / vector-space dimension is `176`
- the `D0`-saturated Groebner basis length is `43`
- the ideal does not contain `1`
- saturating the finite `D0`-saturated core by `B` has exponent `0`
- after `B` saturation, the core is still dimension `0`, degree `176`, basis
  length `43`, and does not contain `1`

Boundary:

- this does not yet kill the regular generic branch over `QQ`
- it does convert the live regular problem into a finite rational-candidate
  problem after the already-dead `D0 = 0` locus is removed
- `B != 0` does not explain the finite candidate set
- the D0- and B-saturated finite core has no rational point over `QQ`
- multiplication by `B` on the degree-176 quotient has a degree-176
  characteristic polynomial with no rational roots
- since the finite core has no rational point before imposing `v != 0` and
  `2P != B^2`, those remaining exclusions do not need a separate rational
  candidate check for closure

Read:

The normalized odd branch is dead over `QQ`:

- root-swap fixed slice `2P = B^2` was already eliminated
- `v = 0` was already eliminated
- `B = 0` was already eliminated
- `D0 = 0` was eliminated by the denominator-locus run
- the regular `D0 != 0`, `B != 0` finite core has no rational point

Next exact gate:

1. convert the odd-branch closure into a compact theorem note
2. keep the remaining positive-`a4` `b1 = 0` rational-square obstruction
   separate
3. do not claim the full equation is solved until that remaining
   `b1 = 0` side is globally closed

## Dashboard / Automation Route

The browser board is subordinate to the math artifacts.

Continuation-thread changes already pushed before this route log:

- launcher starts from lower base port `8421`
- launcher checks whether an occupied port is actually the control API before
  opening a URL
- dashboard was simplified from section controls to a Start / Stop background
  search surface
- stop-state bug was fixed so stale status does not keep reporting `running`
- live math-state layer was added to show equation, stage, reduction path,
  recent outcomes, frontier, and next direction

Relevant files:

- `open_primitive_queue_control.command`
- `dashboard/index.html`
- `dashboard/control.js`
- `dashboard/app.js`
- `dashboard/styles.css`
- `scripts/primitive_queue_control_server.py`
- `scripts/run_backup_autopilot.py`
- `scripts/run_primitive_queue_section.py`

Boundary:

- the dashboard is a watch surface
- proof support comes from the scripts and result logs
- generated pipeline/autopilot artifacts should be triaged before public push

## Current State Map

Claim:

- the active `full_minus2` factor-pair route has compressed from a broad
  primitive leading-point queue to the generic normalized odd branch.

Evidence:

- exact reductions in `scripts/search_factor_pair_families.py`
- rendered report in `results/factor_pair_full_minus2_search.md`
- exact pointwise branch deaths in `results/leading_surface_probe_log.md`
- pushed negative-`a4` global `b1 = 0` rung at commit `1538e45`

Inference:

- the point queue is no longer the best work surface
- the theorem target is the generic odd branch plus the remaining positive
  `a4` rational-square obstruction

Hypothesis:

- the generic odd branch may die through denominator-locus splitting plus a
  regular-branch elimination or modular obstruction

Next gate:

1. attack the regular branch `D0 != 0` by exact elimination or a justified
   rational obstruction
2. keep the active conditions explicit:
   `D0 != 0`, `B != 0`, `v != 0`, `2P != B^2`
3. update `results/leading_surface_probe_log.md` only after the exact result
   is reproducible

## Public / Private Boundary

This route log is a build-continuity artifact. It can support future drafting,
but it is not itself a public proof paper.

Public-safe support language can say:

- exact local reductions have compressed the `full_minus2` factor-pair route
  to a generic normalized odd branch
- the negative-`a4` `b1 = 0` slice has a global sign obstruction
- the current bounded primitive representative queue is locally exhausted
- the `D0 = 0` normalized odd-branch denominator locus is dead over `QQ`
- the regular odd core becomes zero-dimensional of degree `176` after
  saturating by `D0`; `B` saturation does not change that finite core
- the `D0`- and `B`-saturated finite regular odd core has no rational point
  over `QQ`
- the normalized odd branch is closed over `QQ`

Do not publicly claim yet:

- the full `z^2 + y^2 z + x^3 - 2 = 0` equation is solved
- the positive-`a4` `b1 = 0` side is globally dead

## Active Baton

If this thread collapses again, recover here:

1. read `RICK_SMALL_DIOPHANTINE_BOOT.md`
2. read this route log
3. read `results/leading_surface_probe_log.md`
4. read `scripts/search_factor_pair_families.py`
5. continue at the remaining positive-`a4` `b1 = 0` rational-square theorem,
   with the odd branch now closed over `QQ`
