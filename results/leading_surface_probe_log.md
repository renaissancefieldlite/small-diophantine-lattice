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

## Current Read

The stored reduced-core branches are all dead, and the first four additional
integer leading-surface probes outside the original small list are also dead.
The live solver task is now to understand the leading-surface equation itself,
not to revisit the already eliminated finite branch set.
