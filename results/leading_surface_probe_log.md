# Leading Surface Probe Log

- Generated: `2026-04-12`
- Equation lane: `z^2 + y^2 z + x^3 - 2 = 0`
- Reduced-core leading surface: `-a4^3 + b3^2 p6 - p6^2 = 0`

## Extended Exact Probes

These probes were checked with the exact reduced-core branch eliminator
`reduced_core_branch_reduction(a4, b3, p6, slug)`.

### `(-20, 22, -16)`

- Result: `no_go`
- `b1 = 0`: `E11` forces `b2 = -41796*a2/36155`
- `E7` then gives `32595461*a2^2 + 10457472200 = 0`
- `b1 != 0`: odd-branch intersection gcd is `1`

### `(-18, 3, -72)`

- Result: `no_go`
- `b1 = 0`: `E11` forces `b2 = -5508*a2/14711`
- `E7` then gives `44148913*a2^2 + 7790886756 = 0`
- `b1 != 0`: odd-branch intersection gcd is `1`

### `(27, 18, 81)`

- Result: `no_go`
- `b1 = 0`: `E11` forces `b2 = 648*a2/853`
- `E7` then gives `827329*a2^2 - 39290886 = 0`
- `b1 != 0`: odd-branch intersection gcd is `1`

### `(32, 24, 64)`

- Result: `no_go`
- `b1 = 0`: `E11` forces `b2 = -126*a2/19`
- `E7` then gives `4501*a2^2 - 23104 = 0`
- `b1 != 0`: odd-branch intersection gcd is `1`

### `(-24, 20, -32)`

- Result: `no_go`
- `b1 = 0`: `E11` forces the exact linear branch relation, and `E7` then gives
  `9421345*a2^2 + 4417231152 = 0`
- `b1 != 0`: odd-branch intersection gcd is `1`

### `(72, 102, 36)`

- Result: `no_go`
- `b1 = 0`: `E11` forces the exact linear branch relation, and `E7` then gives
  `212229661*a2^2 - 162870359184 = 0`
- `b1 != 0`: odd-branch intersection gcd is `1`

### `(54, 45, 81)`

- Result: `no_go`
- `b1 = 0`: `E11` forces `b2 = -3726*a2/2083`, and `E7` then gives
  `1724245*a2^2 - 468600012 = 0`
- `b1 != 0`: odd-branch intersection gcd is `1`

### `(27, 18, 243)`

- Result: `no_go`
- `b1 = 0`: `E11` forces `b2 = -648*a2/4471`, and `E7` then gives
  `6289753*a2^2 - 1079451414 = 0`
- `b1 != 0`: odd-branch intersection gcd is `1`

### `(-36, 24, -72)`

- Result: `no_go`
- `b1 = 0`: `E11` forces `b2 = -3240*a2/3721`, and `E7` then gives
  `1389049*a2^2 + 996900552 = 0`
- `b1 != 0`: odd-branch intersection gcd is `1`

### `(-36, 18, -108)`

- Result: `no_go`
- `b1 = 0`: `E11` forces `b2 = -270*a2/421`, and `E7` then gives
  `37816765068258*(22189*a2^2 + 12761352) = 0`
- `b1 != 0`: odd-branch intersection gcd is `1`

### `(75, 130, 25)`

- Result: `no_go`
- `b1 = 0`: `E11` forces `b2 = -218376*a2/159755`, and `E7` then gives
  `54624216209706*(929441741*a2^2 - 765649800750) = 0`
- `b1 != 0`: odd-branch intersection gcd is `1`

### `(-108, 132, -72)`

- Result: `no_go`
- `b1 = 0`: `E11` forces `b2 = -79056*a2/59647`, and `E7` then gives
  `277322943833892*(598171417*a2^2 + 768477155544) = 0`
- `b1 != 0`: odd-branch intersection gcd is `1`

### `(-60, 28, -216)`

- Result: `no_go`
- `b1 = 0`: `E11` forces `b2 = -49248*a2/72265`, and `E7` then gives
  `58826078995068*(123219509*a2^2 + 125333525400) = 0`
- `b1 != 0`: odd-branch intersection gcd is `1`

### `(-198, 189, -216)`

- Result: `no_go`
- `b1 = 0`: `E11` forces `b2 = -16068*a2/12247`, and `E7` then gives
  `3573684298950381*(2731561*a2^2 + 6599516396) = 0`
- `b1 != 0`: odd-branch intersection gcd is `1`

### `(92, 312, 8)`

- Result: `no_go`
- `b1 = 0`: `E11` forces `b2 = -39816*a2/29357`, and `E7` then gives
  `655490594516472*(153732817*a2^2 - 158577354616) = 0`
- `b1 != 0`: odd-branch intersection gcd is `1`

### `(-56, 13, -343)`

- Result: `no_go`
- `b1 = 0`: `E11` forces `b2 = -138510*a2/330439`, and `E7` then gives
  `27312108104853*(20423341069*a2^2 + 12229272464752) = 0`
- `b1 != 0`: odd-branch intersection gcd is `1`

## Primitive `b1 = 0` Scan

A direct scan of primitive leading-surface points up to
`|a4| <= 1200`, `|b3| <= 500` found:

- `242` primitive leading-surface points up to weighted scaling
- `0` hits where the non-exceptional symbolic obstruction made `a2^2` a rational square
- `0` hits on the exceptional slice `1809 p6 - 239 b3^2 = 0`

So the symbolic `b1 = 0` obstruction is not just branchwise plausible. It is
holding cleanly on a much larger primitive sample.

## Primitive Representative Queue

After quotienting primitive leading-surface points by:

- weighted scaling
- root swap `p6 <-> b3^2 - p6`
- the exact sign symmetry `t -> -t`, which identifies `b3` with `-b3`

the search space in the same scan window drops to `61` primitive
representatives.

The first sign-reduced representatives by small height are:

1. `(2, 3, 1)`
2. `(4, 4, 8)`
3. `(-8, 4, -16)`
4. `(-20, 22, -16)`
5. `(-24, 20, -32)`
6. `(-18, 3, -72)`
7. `(27, 18, 81)`
8. `(-36, 24, -72)`
9. `(-36, 18, -108)`
10. `(54, 45, 81)`
11. `(72, 102, 36)`
12. `(75, 130, 25)`

Several of the earliest entries in this reduced queue are already exact `no_go`.
Entries 9 and 12 are now exact `no_go` as well, so the practical frontier is
shrinking toward a much smaller primitive branch set than the raw
leading-surface point cloud suggests. In the current sign-reduced height
ordering, the next unresolved representative after these stored deaths is
`(-98, 49, -343)`.

## Current Read

The stored reduced-core branches are all dead, and the next five primitive
representatives `(-36, 18, -108)`, `(75, 130, 25)`, `(-108, 132, -72)`,
`(-60, 28, -216)`, `(-198, 189, -216)`, `(92, 312, 8)`, and `(-56, 13, -343)`
are also dead. The live solver task is no longer branchwise queue maintenance
alone. The odd branch is best viewed through the unit normalization `b1 = 1`,
with the root-swap-fixed slice `2 p6 = b3^2` already collapsed to the
eliminated scaling family through `(4, 4, 8)`. So the real frontier is the
asymmetric normalized odd surface `2 P != B^2` together with a global proof
that the non-exceptional `b1 = 0` square obstruction never hits.
