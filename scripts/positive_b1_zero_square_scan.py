#!/usr/bin/env python3
"""Scan the remaining positive-a4 b1=0 rational-square obstruction.

This is not a proof by itself. It is the exact bounded evidence lane for the
only branch left after the normalized odd branch closure.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parents[1]


def divisors_from_factorization(factors: dict[int, int]) -> list[int]:
    divisors = [1]
    for prime, exponent in factors.items():
        powers = [prime**k for k in range(exponent + 1)]
        divisors = [d * power for d in divisors for power in powers]
    return sorted(divisors)


def is_square(n: int) -> bool:
    if n < 0:
        return False
    root = math.isqrt(n)
    return root * root == n


def is_weighted_primitive(a4: int, b3: int, p6: int) -> bool:
    limit = int(round(abs(a4) ** 0.25)) + 3 if a4 else 3
    for t in range(2, max(limit, 3)):
        if a4 % (t**4) == 0 and b3 % (t**3) == 0 and p6 % (t**6) == 0:
            return False
    return True


def square_obstruction_hit(a4: int, b3: int, p6: int) -> dict[str, int | bool]:
    d_poly = 10177 * b3**4 - 6102 * b3**2 * p6 + 688905 * p6**2
    numerator = 2 * a4
    denominator = d_poly
    gcd = math.gcd(numerator, denominator)
    reduced_num = numerator // gcd
    reduced_den = denominator // gcd
    return {
        "d": d_poly,
        "gcd": gcd,
        "reduced_num": reduced_num,
        "reduced_den": reduced_den,
        "is_rational_square": is_square(reduced_num) and is_square(reduced_den),
    }


def scan_positive_a4(bound: int, sample_limit: int) -> dict[str, object]:
    started = time.time()
    representatives: list[dict[str, int]] = []
    hits: list[dict[str, object]] = []
    total_representatives = 0
    checked_sides = 0
    exceptional_hits = 0

    for a4 in range(1, bound + 1):
        divisors = divisors_from_factorization({p: 3 * e for p, e in sp.factorint(a4).items()})
        cube = a4**3
        for p6 in divisors:
            q6 = cube // p6
            if p6 > q6:
                continue
            b3_squared = p6 + q6
            b3 = math.isqrt(b3_squared)
            if b3 * b3 != b3_squared:
                continue
            if not is_weighted_primitive(a4, b3, p6):
                continue

            row = {"a4": a4, "b3": b3, "p6": p6, "q6": q6}
            total_representatives += 1
            if len(representatives) < sample_limit:
                representatives.append(row)

            for side_name, side_p6 in [("p6", p6), ("q6", q6)]:
                if side_name == "q6" and q6 == p6:
                    continue
                checked_sides += 1
                exceptional = 1809 * side_p6 - 239 * b3_squared
                if exceptional == 0:
                    exceptional_hits += 1
                obstruction = square_obstruction_hit(a4, b3, side_p6)
                if obstruction["is_rational_square"]:
                    hits.append(
                        {
                            **row,
                            "side": side_name,
                            "side_p6": side_p6,
                            "exceptional": exceptional,
                            "obstruction": obstruction,
                        }
                    )

    return {
        "bound": bound,
        "seconds": round(time.time() - started, 3),
        "positive_primitive_representatives": total_representatives,
        "sample_representatives": representatives,
        "checked_root_swap_sides": checked_sides,
        "exceptional_hits": exceptional_hits,
        "square_hit_count": len(hits),
        "square_hits": hits[:sample_limit],
    }


def write_outputs(result: dict[str, object]) -> None:
    bound = result["bound"]
    json_path = ROOT / "results" / f"positive_b1_zero_square_scan_bound{bound}.json"
    md_path = ROOT / "results" / f"positive_b1_zero_square_scan_bound{bound}.md"
    json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

    lines = [
        "# Positive a4 b1=0 Square Scan",
        "",
        f"Bound: `1 <= a4 <= {bound}`",
        "",
        "Method: enumerate factor pairs `p6*q6 = a4^3` with `p6 + q6 = b3^2`, then test the exact b1=0 obstruction on both root-swap sides.",
        "",
        f"- seconds: `{result['seconds']}`",
        f"- positive primitive representatives: `{result['positive_primitive_representatives']}`",
        f"- sampled representatives stored: `{len(result['sample_representatives'])}`",
        f"- checked root-swap sides: `{result['checked_root_swap_sides']}`",
        f"- exceptional-slice hits: `{result['exceptional_hits']}`",
        f"- rational-square hits: `{result['square_hit_count']}`",
        "",
        "## Read",
        "",
    ]
    if result["square_hit_count"] == 0:
        lines.append("No positive-a4 rational-square hit was found in this exact bounded scan.")
    else:
        lines.append("At least one positive-a4 rational-square hit was found. Inspect `square_hits` in the JSON artifact before making any theorem claim.")
    lines.append("")
    md_path.write_text("\n".join(lines))
    print(f"wrote {json_path}")
    print(f"wrote {md_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bound", type=int, default=20000)
    parser.add_argument("--sample-limit", type=int, default=40)
    args = parser.parse_args()
    write_outputs(scan_positive_a4(args.bound, args.sample_limit))


if __name__ == "__main__":
    main()
