# Rick Small Diophantine Boot

## Purpose

This file is the baton-pass note for the small-Diophantine lane.

It exists so the next Rick does not flatten:

- the warm-up reference lane
- the full-problem equations already solved by direct substitution
- the still-open residue

into one vague story.

## Ground Truth

Start from this and do not drift:

1. The overall Epoch small-Diophantine problem is still unsolved.
2. As of `2026-04-11`, the latest Epoch page says:
   - public direct-substitution families exist for:
     - `z^2 + y^2 z - z + x^3 + 2 = 0`
     - `z^2 + y^2 z + x^3 + x + 1 = 0`
   - the problem authors subsequently solved
     - `z^2 + y^2 z + x^3 + x - 1 = 0`
3. That leaves exactly `6` open full equations.
4. The warm-up
   - `z^2 + y^2 z + x^3 + 2 = 0`
   is a reference lane, not one of the nine full equations.
5. The warm-up family is real and should be treated as a verified reference
   surface.
6. The direct-substitution lane is still alive because it solved multiple
   equations, but it is no longer enough to assume that every remaining
   equation falls to the same tiny ansatz.

## Current Repo Role

This repo currently does four things:

1. preserve the source-backed status of the problem
2. verify the known family surfaces already in hand
3. scan the residue for warm-up-style Pell-discriminant substitutions
4. hold the next attack plan for direct polynomial identities

Route-level continuity for the current factor-pair / reduced-core build is now
tracked in:

- `DIOPHANTINE_LOG.md`

## Current Search Split

### Lane A: Verified known-family surfaces

Keep these separate and checked:

- warm-up Tomita family
- `-z + x^3 + 2` direct-substitution family
- `x + 1` quartic/cubic/sextic identity family

### Lane B: Remaining open residue

Open full equations as of `2026-04-11`:

- `z^2 + y^2 z + x^3 - 2 = 0`
- `z^2 + y^2 z + x^3 - x - 1 = 0`
- `z^2 + y^2 z + x^3 - 3 = 0`
- `z^2 + y^2 z + x^3 + 3 = 0`
- `z^2 + y^2 z + x^3 - x - 2 = 0`
- `z^2 + y^2 z + x^3 - x + 2 = 0`

## First Commands

```bash
cd /Users/renaissancefieldlite1.0/Documents/Playground/small-diophantine-lattice
python3 scripts/verify_known_families.py --emit-json results/known_families_examples.json
python3 scripts/search_direct_families.py --status open --bound 3 --max-results 12 \
  --emit-json results/initial_discriminant_scan_bound3.json
```

## Do Not Do

- do not call the warm-up a full-problem solve
- do not say seven equations remain open; the current dated source says six
- do not claim the bounded discriminant scan solves the residue if it only
  rediscovers known families or returns no hits
- do not let direct-substitution hope outrun checked artifact state
