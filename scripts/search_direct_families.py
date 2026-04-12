#!/usr/bin/env python3
"""Search bounded direct-substitution families for the small-Diophantine lane.

Current surface:
  x = A n^2 + B n + C
  y = D n + E

For z^2 + (y^2 + c) z + x^3 + a x + b = 0, the discriminant in z is

  Delta = (y^2 + c)^2 - 4 * (x^3 + a x + b).

The warm-up succeeds because Delta factors as (quadratic)^2 * (quadratic), so
the squarefree part has degree 2 and can be attacked by Pell-style recurrences.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "equations.json"


def load_equations() -> list[dict[str, Any]]:
    return json.loads(DATA_PATH.read_text())


def squarefree_part(poly: sp.Expr, n: sp.Symbol) -> tuple[sp.Expr, list[dict[str, Any]]]:
    coeff, factors = sp.factor_list(sp.expand(poly))
    odd_part = sp.Integer(1)
    factor_rows: list[dict[str, Any]] = []
    for factor, exp in factors:
        deg = int(sp.Poly(factor, n).degree())
        factor_rows.append(
            {
                "factor": str(sp.factor(factor)),
                "exp": int(exp),
                "degree": deg,
            }
        )
        if exp % 2 == 1:
            odd_part *= factor
    if coeff < 0:
        odd_part *= -1
    return sp.expand(odd_part), factor_rows


def candidate_row(
    equation: dict[str, Any],
    params: tuple[int, int, int, int, int],
    delta: sp.Expr,
    squarefree: sp.Expr,
    factor_rows: list[dict[str, Any]],
    n: sp.Symbol,
) -> dict[str, Any]:
    A, B, C, D, E = params
    delta_poly = sp.Poly(sp.expand(delta), n)
    sf_poly = sp.Poly(sp.expand(squarefree), n)
    return {
        "equation_slug": equation["slug"],
        "equation": equation["equation"],
        "status": equation["status"],
        "params": {"A": A, "B": B, "C": C, "D": D, "E": E},
        "delta": str(sp.factor(delta)),
        "delta_degree": int(delta_poly.degree()),
        "squarefree_part": str(sp.factor(squarefree)),
        "squarefree_degree": int(sf_poly.degree()),
        "factorization": factor_rows,
    }


def search_equation(
    equation: dict[str, Any],
    bound: int,
    max_results: int,
) -> list[dict[str, Any]]:
    n = sp.symbols("n")
    a = int(equation["a"])
    b = int(equation["b"])
    c = int(equation["c"])
    hits: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    for A in range(-bound, bound + 1):
        if A == 0:
            continue
        for B in range(-bound, bound + 1):
            for C in range(-bound, bound + 1):
                x = A * n**2 + B * n + C
                cubic = x**3 + a * x + b
                for D in range(-bound, bound + 1):
                    if D == 0:
                        continue
                    for E in range(-bound, bound + 1):
                        y = D * n + E
                        delta = sp.expand((y**2 + c) ** 2 - 4 * cubic)
                        if sp.Poly(delta, n).degree() != 6:
                            continue
                        squarefree, factor_rows = squarefree_part(delta, n)
                        squarefree_degree = int(sp.Poly(squarefree, n).degree())
                        if squarefree_degree != 2:
                            continue
                        key = (str(sp.factor(delta)), str(sp.factor(squarefree)))
                        if key in seen:
                            continue
                        seen.add(key)
                        hits.append(
                            candidate_row(
                                equation=equation,
                                params=(A, B, C, D, E),
                                delta=delta,
                                squarefree=squarefree,
                                factor_rows=factor_rows,
                                n=n,
                            )
                        )
                        if len(hits) >= max_results:
                            return hits
    return hits


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--status",
        default="open",
        choices=["all", "open", "benchmark", "solved"],
        help="Which equation subset to scan.",
    )
    parser.add_argument(
        "--bound",
        type=int,
        default=3,
        help="Coefficient search bound for A, B, C, D, E.",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=12,
        help="Maximum hits to keep per equation.",
    )
    parser.add_argument(
        "--emit-json",
        type=Path,
        default=None,
        help="Optional output path for the JSON result.",
    )
    return parser.parse_args()


def keep_equation(equation: dict[str, Any], mode: str) -> bool:
    status = equation["status"]
    if mode == "all":
        return True
    if mode == "open":
        return status == "open"
    if mode == "benchmark":
        return equation["group"] == "warmup" or status.startswith("solved")
    if mode == "solved":
        return status != "open"
    raise ValueError(f"unknown mode: {mode}")


def main() -> int:
    args = parse_args()
    equations = [eq for eq in load_equations() if keep_equation(eq, args.status)]
    payload: dict[str, Any] = {
        "status_filter": args.status,
        "bound": args.bound,
        "max_results_per_equation": args.max_results,
        "results": {},
    }

    for equation in equations:
        hits = search_equation(
            equation=equation,
            bound=args.bound,
            max_results=args.max_results,
        )
        payload["results"][equation["slug"]] = {
            "equation": equation["equation"],
            "status": equation["status"],
            "hit_count": len(hits),
            "hits": hits,
        }
        print(f"{equation['slug']}: {len(hits)} hits")
        for hit in hits[: min(3, len(hits))]:
            params = hit["params"]
            print(
                "  "
                f"A={params['A']} B={params['B']} C={params['C']} "
                f"D={params['D']} E={params['E']} "
                f"sf={hit['squarefree_part']}"
            )

    if args.emit_json is not None:
        args.emit_json.parent.mkdir(parents=True, exist_ok=True)
        args.emit_json.write_text(json.dumps(payload, indent=2))
        print(f"\nwrote {args.emit_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
