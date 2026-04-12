# DeepSeek Question Pack

Use these as exact derivation prompts, not as open-ended brainstorming.

## Rule

Ask one equation at a time.
Pass in:

- the exact equation
- one or two exact seed triples
- the discriminant formula
- the explicit task

Do not ask for "ideas." Ask for a derivation or a no-go result for a specific
ansatz.

## Current Active Prompt

Use this exact prompt for the current `x^3 - 2` run. It incorporates the
seed-shift correction and the requirement that no-go claims must be proved under
the stated degree bounds.

```text
Good correction. Two exact fixes before the next rung:

1. “did not factor cleanly” is not sufficient. For Lane 1 you must either solve
   the coefficient equations exactly or prove impossibility under the ansatz.

2. Your Lane 3 no-go does not count yet, because you did not shift the
   polynomial ansatz through the seed (−2,3,1). The next identity search must
   satisfy x(0) = −2, y(0) = 3, z(0) = 1.

Work only on

  z^2 + y^2 z + x^3 - 2 = 0

with seed

  (x, y, z) = (-2, 3, 1).

Use these three exact formulations:

A. Discriminant formulation
Treat the equation as a quadratic in z:
  Delta(x,y) = y^4 - 4x^3 + 8.

Now impose the shifted ansatz
  x(n) = -2 + A n^2 + B n
  y(n) = 3 + C n

and determine whether there exist rational coefficients A,B,C and polynomials
  S(n) = s2 n^2 + s1 n + s0
  Q(n) = q2 n^2 + q1 n + q0,  q2 != 0
such that
  Delta(n) = S(n)^2 Q(n)
identically.

Do not summarize. Solve the coefficient system exactly or prove there is no
solution under this degree bound.

B. Shifted polynomial-identity formulation
Search for an identity through the seed of the form
  x(t) = -2 + a2 t^2 + a4 t^4
  y(t) =  3 + b1 t + b2 t^2 + b3 t^3
  z(t) =  1 + c2 t^2 + c4 t^4 + c6 t^6
satisfying
  z(t)^2 + y(t)^2 z(t) + x(t)^3 - 2 = 0
identically in t.

Again, solve the coefficient equations exactly or prove impossibility under
this shifted degree bound.

C. Factor-pair formulation
Set
  a = -z
  b = -(z + y^2).

Then derive exactly that
  ab = x^3 - 2
  a + b = y^2.

Use this reformulation to search for a family of factor pairs whose sum is a
square and whose product is x^3 - 2. If this route is more tractable than A or
B, say so and proceed.

Rules:
- do not switch to a different equation
- do not use phrases like “obvious”, “no obvious recurrence”, or “non-trivial”
- do not infer a recurrence from numerical pattern alone
- only derive a recurrence after an exact symbolic reduction produces it

Return:
- the exact algebra
- a no-go proof if an ansatz fails
- or an explicit recurrence / parametrization if one exists
```

## Question 1: Derive a Pell reduction from a seed

```text
Work on the integer surface

  z^2 + y^2 z + x^3 - 2 = 0.

One exact seed is (x, y, z) = (-2, 3, 1).

The quadratic discriminant in z is

  Delta = y^4 - 4 x^3 + 8.

Find an explicit substitution

  x = f(n), y = g(n)

with f quadratic and g linear or affine in n, such that

  Delta = S(n)^2 Q(n)

where Q(n) is a quadratic polynomial. If possible, derive the induced Pell-type
recurrence that generates infinitely many integer solutions. If this ansatz
cannot work, prove why it fails.
```

Use `Current Active Prompt` first for this equation. This older question is the
lighter version.

## Question 2: Shifted-seed discriminant search

```text
For the equation

  z^2 + y^2 z + x^3 - x - 2 = 0

start from the exact seed (x, y, z) = (-10, 1, 31).

Do not search around the origin. Search around the seed by setting

  x = x0 + u(n), y = y0 + v(n)

with u quadratic and v linear or affine. Determine whether the discriminant can
be reduced to square times an indefinite quadratic, and derive the resulting
Pell form if it exists.
```

## Question 3: Quartic/cubic/sextic identity search

```text
For the equation

  z^2 + y^2 z + x^3 + 3 = 0

search for an identity of the form

  x(t) = a t^4 + b t^2 + c
  y(t) = p t^3 + q t
  z(t) = r t^6 + s t^4 + u t^2 + v

that satisfies the equation identically in t.

Solve the coefficient equations exactly. If no such identity exists under this
shape, show the obstruction explicitly.
```

## Question 4: Cubic-surface reduction

```text
For the equation

  z^2 + y^2 z + x^3 - x - 1 = 0

and seed (x, y, z) = (-16, 24, 7),

determine whether the surface admits a rational curve or elliptic/conic
fibration passing through this seed. Give an explicit birational reduction if
possible, and explain how integer points would be recovered from that reduction.
```

## Question 5: Recurrence verification

```text
Suppose a candidate recurrence is proposed in matrix form

  [u_{n+1}]   [A B] [u_n]
  [v_{n+1}] = [C D] [v_n]

for a Pell-type reduction of one of the small-Diophantine equations.

Given the explicit map from (u_n, v_n) to (x_n, y_n, z_n), prove whether the
recurrence preserves integrality and the target equation exactly. Then derive
the asymptotic growth of x_n and determine the first n for which |x_n| > 10^50.
```
