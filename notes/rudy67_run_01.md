# Rudy67 Run 01

## Scope

Current target:

- `z^2 + y^2 z + x^3 - 2 = 0`

Primary seed:

- `(-2, 3, 1)`

## What Rudy67 First Did Wrong

The first drift was equation substitution:

- switched to the unrelated Pell equation `x^2 - 2 y^2 - 1 = 0`

That is not this FrontierMath lane.

The correct target remains:

- `z^2 + y^2 z + x^3 - 2 = 0`

## Corrected Run Summary

After correction, Rudy67 reported:

### Lane 1

- treated the equation as a quadratic in `z`
- wrote the discriminant
  - `Delta = y^4 - 4 x^3 + 8`
- tested a shifted ansatz around the seed:
  - `x = -2 + u(n)`
  - `y = 3 + v(n)`
  - with `u` quadratic and `v` linear
- reported that this ansatz did not produce a clean Pell-style factorization

### Lane 2

- produced additional exact small integer points, including:
  - `(-2, 3, 1)`
  - `(-7, 8, 5)`
  - `(8, 7, -15)`
  - `(20, 17, -31)`
  - `(26, 19, -58)`

### Lane 3

- tested a quartic/cubic/sextic identity family
- reported no solution under the unshifted degree bound

## Corrections To Preserve

Two exact corrections were necessary.

### Correction 1

“did not factor cleanly” is not a result.

For the discriminant lane, the requirement is:

- solve the coefficient system exactly
- or give a real impossibility proof under the stated degree bounds

### Correction 2

The first Lane 3 no-go does not count, because the polynomial ansatz was not
shifted through the seed.

The next identity search must satisfy:

- `x(0) = -2`
- `y(0) = 3`
- `z(0) = 1`

## Next Exact Prompt

Use the exact prompt preserved in:

- `notes/deepseek_question_pack.md`

Specifically:

- `Current Active Prompt`

## Decision Rule After The Next Run

- if the shifted discriminant lane succeeds:
  - build a recurrence verifier
- if the shifted identity lane succeeds:
  - build a symbolic family verifier
- if both fail but the factor-pair lane gives structure:
  - promote the factor-pair lane
- if all three fail under proof:
  - move the exact same packet to
    - `z^2 + y^2 z + x^3 - 3 = 0`
    - seed `(-3, 1, 5)`

## Why This Note Exists

This note keeps the current DeepSeek/Rudy67 run from collapsing into a thin
memory like:

- “it failed”
- “try Pell”
- “no recurrence yet”

The real state is sharper:

- wrong equation corrected
- useful seed points extracted
- first no-go claims require stricter proof
- next prompt is now exact and seed-shifted
