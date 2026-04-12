#!/usr/bin/env python3
"""Run a one-equation portfolio and emit dashboard-ready data."""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "equations.json"
SEED_PATH = ROOT / "results" / "open_seed_triples_bound30.json"
DASHBOARD_JS_PATH = ROOT / "dashboard" / "latest_portfolio.js"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def load_equation_map() -> dict[str, dict[str, Any]]:
    return {row["slug"]: row for row in load_json(DATA_PATH)}


def load_seed_map() -> dict[str, dict[str, Any]]:
    return load_json(SEED_PATH)["results"]


def choose_seed(seed_rows: list[dict[str, int]], seed_index: int | None) -> tuple[dict[str, int], int]:
    ranked = sorted(
        enumerate(seed_rows),
        key=lambda item: (
            abs(item[1]["x"]) + abs(item[1]["y"]) + abs(item[1]["z"]),
            item[1]["z"] < 0,
            item[1]["y"] < 0,
            abs(item[1]["z"]),
            abs(item[1]["y"]),
            abs(item[1]["x"]),
        ),
    )
    if seed_index is None:
        chosen_rank = ranked[0]
    else:
        chosen_rank = ranked[seed_index]
    return chosen_rank[1], chosen_rank[0]


def squarefree_part(poly: sp.Expr, n: sp.Symbol) -> tuple[sp.Expr, list[dict[str, Any]]]:
    coeff, factors = sp.factor_list(sp.expand(poly))
    odd_part = sp.Integer(1)
    factor_rows: list[dict[str, Any]] = []
    for factor, exp in factors:
        factor_rows.append(
            {
                "factor": str(sp.factor(factor)),
                "exp": int(exp),
                "degree": int(sp.Poly(factor, n).degree()),
            }
        )
        if exp % 2 == 1:
            odd_part *= factor
    if coeff < 0:
        odd_part *= -1
    return sp.expand(odd_part), factor_rows


def run_shifted_discriminant_lane(
    equation: dict[str, Any],
    seed: dict[str, int],
    bound: int,
    max_hits: int,
) -> dict[str, Any]:
    n = sp.symbols("n")
    A, B, C = sp.symbols("A B C")
    s2, s1, s0, q2, q1, q0 = sp.symbols("s2 s1 s0 q2 q1 q0")
    x = seed["x"] + A * n**2 + B * n
    y = seed["y"] + C * n
    a = int(equation["a"])
    b = int(equation["b"])
    c = int(equation["c"])
    delta = sp.expand((y**2 + c) ** 2 - 4 * (x**3 + a * x + b))
    identity = sp.expand(delta - (s2 * n**2 + s1 * n + s0) ** 2 * (q2 * n**2 + q1 * n + q0))
    system = [str(sp.expand(coeff)) for coeff in sp.Poly(identity, n).all_coeffs()]

    hits: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for Aval in range(-bound, bound + 1):
        if Aval == 0:
            continue
        for Bval in range(-bound, bound + 1):
            for Cval in range(-bound, bound + 1):
                if Cval == 0:
                    continue
                x_trial = seed["x"] + Aval * n**2 + Bval * n
                y_trial = seed["y"] + Cval * n
                delta_trial = sp.expand((y_trial**2 + c) ** 2 - 4 * (x_trial**3 + a * x_trial + b))
                if sp.Poly(delta_trial, n).degree() != 6:
                    continue
                squarefree, factor_rows = squarefree_part(delta_trial, n)
                if int(sp.Poly(squarefree, n).degree()) != 2:
                    continue
                key = (str(sp.factor(delta_trial)), str(sp.factor(squarefree)))
                if key in seen:
                    continue
                seen.add(key)
                hits.append(
                    {
                        "params": {"A": Aval, "B": Bval, "C": Cval},
                        "delta": str(sp.factor(delta_trial)),
                        "squarefree_part": str(sp.factor(squarefree)),
                        "factorization": factor_rows,
                    }
                )
                if len(hits) >= max_hits:
                    break
            if len(hits) >= max_hits:
                break
        if len(hits) >= max_hits:
            break

    return {
        "slug": "shifted_discriminant",
        "title": "Shifted Discriminant",
        "status": "candidate_hit" if hits else "no_hit_in_bounded_scan",
        "seed_formula": {
            "x": f"{seed['x']} + A n^2 + B n",
            "y": f"{seed['y']} + C n",
        },
        "summary": (
            f"Generated the exact degree-{sp.Poly(delta, n).degree()} discriminant system and "
            f"scanned A,B,C in [-{bound},{bound}] with A != 0 and C != 0."
        ),
        "unknown_count": 9,
        "equation_count": len(system),
        "bounded_scan": {"bound": bound, "hit_count": len(hits), "hits": hits},
        "exact_system": system,
        "next_action": (
            "Promote any bounded hit into an exact coefficient solve."
            if hits
            else "Keep the exact system, but do not claim a no-go beyond the bounded scan."
        ),
    }


def run_shifted_identity_lane(
    equation: dict[str, Any],
    seed: dict[str, int],
) -> dict[str, Any]:
    t = sp.symbols("t")
    a2, a4, b1, b2, b3, c2, c4, c6 = sp.symbols("a2 a4 b1 b2 b3 c2 c4 c6")
    x = seed["x"] + a2 * t**2 + a4 * t**4
    y = seed["y"] + b1 * t + b2 * t**2 + b3 * t**3
    z = seed["z"] + c2 * t**2 + c4 * t**4 + c6 * t**6
    expr = sp.expand(z**2 + y**2 * z + int(equation["c"]) * z + x**3 + int(equation["a"]) * x + int(equation["b"]))
    coeffs = sp.Poly(expr, t).all_coeffs()
    equations = [str(sp.expand(coeff)) for coeff in coeffs if coeff != 0]
    low_degree = []
    degree = sp.Poly(expr, t).degree()
    for idx, coeff in enumerate(coeffs):
        power = degree - idx
        if coeff != 0 and power <= 6:
            low_degree.append({"power": power, "equation": str(sp.expand(coeff))})

    return {
        "slug": "shifted_identity",
        "title": "Shifted Identity",
        "status": "system_generated",
        "seed_formula": {
            "x": f"{seed['x']} + a2 t^2 + a4 t^4",
            "y": f"{seed['y']} + b1 t + b2 t^2 + b3 t^3",
            "z": f"{seed['z']} + c2 t^2 + c4 t^4 + c6 t^6",
        },
        "summary": (
            "Built the exact shifted quartic/cubic/sextic identity system through the chosen seed."
        ),
        "unknown_count": 8,
        "equation_count": len(equations),
        "low_degree_equations": low_degree,
        "next_action": "Run an exact Groebner-basis or elimination solve on this shifted system.",
    }


def divisors_of(n: int) -> set[int]:
    n_abs = abs(n)
    result: set[int] = set()
    for d in range(1, math.isqrt(n_abs) + 1):
        if n_abs % d == 0:
            result.add(d)
            result.add(-d)
            result.add(n_abs // d)
            result.add(-(n_abs // d))
    return result


def run_factor_pair_lane(
    equation: dict[str, Any],
    x_bound: int,
    max_examples: int,
) -> dict[str, Any]:
    a = int(equation["a"])
    b = int(equation["b"])
    c = int(equation["c"])
    examples: list[dict[str, int]] = []
    seen: set[tuple[int, int, int]] = set()

    for x in range(-x_bound, x_bound + 1):
        value = x**3 + a * x + b
        if value == 0:
            continue
        for p in sorted(divisors_of(value)):
            if value % p != 0:
                continue
            q = value // p
            y_sq = p + q - c
            if y_sq < 0:
                continue
            y_root = math.isqrt(y_sq)
            if y_root * y_root != y_sq:
                continue
            z = -p
            for y in {y_root, -y_root}:
                key = (x, y, z)
                if key in seen:
                    continue
                if z * z + y * y * z + c * z + x * x * x + a * x + b != 0:
                    continue
                seen.add(key)
                examples.append({"x": x, "y": y, "z": z, "p": p, "q": q})
                if len(examples) >= max_examples:
                    break
            if len(examples) >= max_examples:
                break
        if len(examples) >= max_examples:
            break

    return {
        "slug": "factor_pair",
        "title": "Factor-Pair",
        "status": "exact_examples_found" if examples else "no_examples_in_bounded_x_scan",
        "summary": (
            f"Searched x in [-{x_bound},{x_bound}] using p=-z, q=z+y^2+{c}, so pq=x^3+{a}x+{b} and p+q=y^2+{c}."
        ),
        "bounded_x_scan": {"bound": x_bound, "example_count": len(examples), "examples": examples},
        "next_action": (
            "Promote the factor-pair reformulation into a family search around the strongest examples."
            if examples
            else "Widen the x-scan or combine this lane with seed-guided factor constraints."
        ),
    }


def build_overview(portfolio: dict[str, Any]) -> dict[str, Any]:
    lanes = portfolio["lanes"]
    lane_map = {lane["slug"]: lane for lane in lanes}
    if lane_map["shifted_discriminant"]["bounded_scan"]["hit_count"] > 0:
        recommended = {
            "lane": "shifted_discriminant",
            "action": "Take the bounded discriminant hit and promote it into an exact coefficient solve.",
        }
    elif lane_map["factor_pair"]["bounded_x_scan"]["example_count"] > 0:
        recommended = {
            "lane": "factor_pair",
            "action": "Promote the factor-pair lane as the strongest live surface while the identity system waits for exact elimination.",
        }
    else:
        recommended = {
            "lane": "shifted_identity",
            "action": "Move into an exact elimination pass on the shifted identity system.",
        }
    return {
        "generated_at": portfolio["generated_at"],
        "equation_slug": portfolio["equation"]["slug"],
        "chosen_seed": portfolio["seed"],
        "recommended_next_step": recommended,
        "workflow": [
            "Gather seeds",
            "Run shifted discriminant lane",
            "Build shifted identity system",
            "Run factor-pair lane",
            "Promote strongest exact surface",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--equation", default="full_minus2", help="Equation slug to run.")
    parser.add_argument("--seed-index", type=int, default=None, help="Optional ranked seed index.")
    parser.add_argument("--discriminant-bound", type=int, default=3)
    parser.add_argument("--factor-x-bound", type=int, default=60)
    parser.add_argument("--max-hits", type=int, default=8)
    parser.add_argument("--emit-json", type=Path, default=None)
    parser.add_argument("--emit-dashboard-js", type=Path, default=DASHBOARD_JS_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    equations = load_equation_map()
    seeds = load_seed_map()
    equation = equations[args.equation]
    seed_rows = seeds[args.equation]["seeds"]
    seed, chosen_seed_index = choose_seed(seed_rows, args.seed_index)

    portfolio = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "equation": equation,
        "seed": {
            **seed,
            "ranked_seed_index": chosen_seed_index,
            "seed_source": str(SEED_PATH.relative_to(ROOT)),
        },
        "lanes": [
            run_shifted_discriminant_lane(equation, seed, args.discriminant_bound, args.max_hits),
            run_shifted_identity_lane(equation, seed),
            run_factor_pair_lane(equation, args.factor_x_bound, args.max_hits),
        ],
    }
    portfolio["overview"] = build_overview(portfolio)

    output_json = args.emit_json or ROOT / "results" / f"portfolio_{args.equation}.json"
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(portfolio, indent=2))
    print(f"wrote {output_json}")

    args.emit_dashboard_js.parent.mkdir(parents=True, exist_ok=True)
    args.emit_dashboard_js.write_text(
        "window.PORTFOLIO_DATA = " + json.dumps(portfolio, indent=2) + ";\n"
    )
    print(f"wrote {args.emit_dashboard_js}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
