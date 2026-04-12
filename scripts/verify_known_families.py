#!/usr/bin/env python3
"""Verify benchmark small-Diophantine families and emit giant examples."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def eval_equation(x: int, y: int, z: int, a: int, b: int, c: int) -> int:
    return z * z + y * y * z + c * z + x * x * x + a * x + b


def warmup_tomita_example(k: int) -> dict[str, int]:
    v, n = 5, 0
    for _ in range(k):
        v, n = 7 * v + 24 * n + 8, 2 * v + 7 * n + 2
    a_term = 3 * n * n + 2 * n + 1
    y = 3 * n + 1
    x = -3 * n * n - 2 * n - 2
    z = -((y * y) + v * a_term) // 2
    return {"x": x, "y": y, "z": z, "n": n, "v": v}


def minus_z_plus_2_example(k: int, residue: int) -> dict[str, int]:
    u = 930 * 10**11 + residue + 930 * k
    s = (368 - u**3) // 930
    x = u * s
    y = s + 2
    z = -31 * s * s + 4 * s - 1
    return {"x": x, "y": y, "z": z, "u": u, "s": s}


def plus_x_plus_1_example(t: int) -> dict[str, int]:
    x = -108 * t**4 - 24 * t**2 - 2
    y = 36 * t**3 + 2 * t
    z = 648 * t**6 + 288 * t**4 + 50 * t**2 + 3
    return {"x": x, "y": y, "z": z, "t": t}


def build_payload() -> dict[str, Any]:
    payload: dict[str, Any] = {"families": []}

    warmup_examples = [warmup_tomita_example(k) for k in (22, 23, 24)]
    payload["families"].append(
        {
            "slug": "warmup_plus2",
            "equation": "z^2 + y^2 z + x^3 + 2 = 0",
            "params": {"a": 0, "b": 2, "c": 0},
            "examples": warmup_examples,
            "source": "https://mathoverflow.net/a/412128",
        }
    )

    minus_z_examples = [
        minus_z_plus_2_example(k=offset, residue=residue)
        for offset, residue in enumerate((542, 602, 902))
    ]
    payload["families"].append(
        {
            "slug": "full_minus_z_plus_2",
            "equation": "z^2 + y^2 z - z + x^3 + 2 = 0",
            "params": {"a": 0, "b": 2, "c": -1},
            "examples": minus_z_examples,
            "source": "https://epoch.ai/files/open-problems/small-diophantine-two-families.pdf",
        }
    )

    plus_x_examples = [plus_x_plus_1_example(t) for t in (10**13, 10**13 + 1, 10**13 + 2)]
    payload["families"].append(
        {
            "slug": "full_plus_x_plus_1",
            "equation": "z^2 + y^2 z + x^3 + x + 1 = 0",
            "params": {"a": 1, "b": 1, "c": 0},
            "examples": plus_x_examples,
            "source": "https://epoch.ai/files/open-problems/small-diophantine-two-families.pdf",
        }
    )

    for family in payload["families"]:
        params = family["params"]
        verified_examples = []
        for example in family["examples"]:
            value = eval_equation(
                x=example["x"],
                y=example["y"],
                z=example["z"],
                a=params["a"],
                b=params["b"],
                c=params["c"],
            )
            verified_examples.append(
                {
                    **example,
                    "verified": value == 0,
                    "equation_value": value,
                    "abs_x_digits": len(str(abs(example["x"]))),
                }
            )
        family["examples"] = verified_examples
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--emit-json",
        type=Path,
        default=None,
        help="Optional path to write the verified examples as JSON.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload()
    for family in payload["families"]:
        print(f"{family['slug']}:")
        for example in family["examples"]:
            print(
                "  "
                f"x_digits={example['abs_x_digits']} "
                f"verified={example['verified']} "
                f"x={example['x']}"
            )
    if args.emit_json is not None:
        args.emit_json.parent.mkdir(parents=True, exist_ok=True)
        args.emit_json.write_text(json.dumps(payload, indent=2))
        print(f"\nwrote {args.emit_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
