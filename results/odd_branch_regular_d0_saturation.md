# Odd Branch Regular D0 Saturation

Route: normalized odd branch, regular core after solving `E6 = E7 = 0` for `(A, P)`.

This run saturates by:

`D0 = -131769 B + 53361 u + 44649 v + 7958`

The `D0 = 0` singular locus is checked separately in `results/odd_branch_denominator_locus.md`.

## Core

- base dimension: `1`
- base Groebner basis length: `39`
- D0 saturation exponent: `3`
- saturated dimension: `0`
- saturated degree / vector-space dimension: `176`
- saturated Groebner basis length: `43`
- contains `1`: `False`
- rationally dead: `False`
- rational obstruction: `None`
- seconds: `323.713`

## Lex Profile

```text
None
```

## Saturated Basis Profile

```text
degree=11 terms=177 leading=v*B^10
degree=11 terms=177 leading=B^11
degree=10 terms=174 leading=v^6*B^4
degree=10 terms=174 leading=u^5*B^5
degree=10 terms=174 leading=u^4*v*B^5
degree=10 terms=174 leading=u^3*v^2*B^5
degree=10 terms=174 leading=u^2*v^3*B^5
degree=10 terms=174 leading=u*v^4*B^5
degree=10 terms=174 leading=v^5*B^5
degree=10 terms=174 leading=u^4*B^6
degree=10 terms=174 leading=u^3*v*B^6
degree=10 terms=174 leading=u^2*v^2*B^6
```

## Read

The D0-saturated regular core did not close over `QQ` in this run.

The next exact split is to inspect the zero-dimensional saturated ideal for rational candidates and then apply the remaining exclusions `B`, `v`, and `2P - B^2`.
