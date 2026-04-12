#!/usr/bin/env python3
"""Extract exact small seed triples for the open small-Diophantine equations."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "equations.json"


def load_equations() -> list[dict[str, Any]]:
    return json.loads(DATA_PATH.read_text())


def solve_z_values(x: int, y: int, a: int, b: int, c: int) -> list[int]:
    quad_b = y * y + c
    quad_c = x * x * x + a * x + b
    disc = quad_b * quad_b - 4 * quad_c
    if disc < 0:
        return []
    root = math.isqrt(disc)
    if root * root != disc:
        return []
    values: list[int] = []
    for numer in (-quad_b + root, -quad_b - root):
        if numer % 2 == 0:
            z = numer // 2
            if z * z + y * y * z + c * z + x * x * x + a * x + b == 0:
                values.append(z)
    return sorted(set(values))


def collect_seeds(equation: dict[str, Any], bound: int, max_per_equation: int) -> list[dict[str, int]]:
    a = int(equation["a"])
    b = int(equation["b"])
    c = int(equation["c"])
    seeds: list[dict[str, int]] = []
    seen: set[tuple[int, int, int]] = set()
    for x in range(-bound, bound + 1):
        for y in range(-bound, bound + 1):
            for z in solve_z_values(x, y, a, b, c):
                key = (x, y, z)
                if key in seen:
                    continue
                seen.add(key)
                seeds.append({"x": x, "y": y, "z": z})
                if len(seeds) >= max_per_equation:
                    return seeds
    return seeds


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--status", default="open", choices=["all", "open", "known", "solved"])
    parser.add_argument("--bound", type=int, default=30)
    parser.add_argument("--max-per-equation", type=int, default=8)
    parser.add_argument("--emit-json", type=Path, default=None)
    return parser.parse_args()


def keep_equation(equation: dict[str, Any], mode: str) -> bool:
    status = equation["status"]
    if mode == "all":
        return True
    if mode == "open":
        return status == "open"
    if mode == "known":
        return equation["group"] == "warmup" or status.startswith("solved") or status == "known_family"
    if mode == "solved":
        return status != "open"
    raise ValueError(f"unknown mode: {mode}")


def main() -> int:
    args = parse_args()
    equations = [eq for eq in load_equations() if keep_equation(eq, args.status)]
    payload: dict[str, Any] = {
        "status_filter": args.status,
        "bound": args.bound,
        "max_per_equation": args.max_per_equation,
        "results": {},
    }
    for equation in equations:
        seeds = collect_seeds(
            equation=equation,
            bound=args.bound,
            max_per_equation=args.max_per_equation,
        )
        payload["results"][equation["slug"]] = {
            "equation": equation["equation"],
            "status": equation["status"],
            "seed_count": len(seeds),
            "seeds": seeds,
        }
        print(f"{equation['slug']}: {len(seeds)} seed(s)")
        for seed in seeds[: min(4, len(seeds))]:
            print(f"  ({seed['x']}, {seed['y']}, {seed['z']})")

    if args.emit_json is not None:
        args.emit_json.parent.mkdir(parents=True, exist_ok=True)
        args.emit_json.write_text(json.dumps(payload, indent=2))
        print(f"\nwrote {args.emit_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
