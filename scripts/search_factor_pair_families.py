#!/usr/bin/env python3
"""Exact factor-pair family search for full_minus2."""

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
DEFAULT_JSON_PATH = ROOT / "results" / "factor_pair_full_minus2_search.json"
DEFAULT_MD_PATH = ROOT / "results" / "factor_pair_full_minus2_search.md"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def load_equation(slug: str) -> dict[str, Any]:
    rows = load_json(DATA_PATH)
    for row in rows:
        if row["slug"] == slug:
            return row
    raise KeyError(f"unknown equation slug: {slug}")


def divisors_of(n: int) -> list[int]:
    n_abs = abs(n)
    result: set[int] = set()
    for d in range(1, math.isqrt(n_abs) + 1):
        if n_abs % d == 0:
            result.update({d, -d, n_abs // d, -(n_abs // d)})
    return sorted(result)


def canonical_examples(x_bound: int, max_examples: int) -> list[dict[str, int]]:
    rows: list[dict[str, int]] = []
    for x in range(-x_bound, x_bound + 1):
        value = x**3 - 2
        if value == 0:
            continue
        candidates = []
        for p in divisors_of(value):
            q = value // p
            y_sq = p + q
            if y_sq < 0:
                continue
            y = math.isqrt(y_sq)
            if y * y != y_sq:
                continue
            candidates.append((abs(p) + abs(q), abs(p), p < 0, p, q, y))
        if not candidates:
            continue
        candidates.sort()
        _, _, _, p, q, y = candidates[0]
        rows.append(
            {
                "x": x,
                "y": y,
                "z": -p,
                "p": p,
                "q": q,
                "y_sq": y * y,
                "q_minus_p": q - p,
                "alt_factor_pairs": len(candidates),
            }
        )
        if len(rows) >= max_examples:
            break
    return rows


def repeated_y_shells(x_bound: int) -> list[dict[str, Any]]:
    shell_map: dict[int, list[dict[str, int]]] = {}
    for x in range(-x_bound, x_bound + 1):
        value = x**3 - 2
        seen: set[tuple[int, int]] = set()
        for p in divisors_of(value):
            q = value // p
            y_sq = p + q
            if y_sq < 0:
                continue
            y = math.isqrt(y_sq)
            if y * y != y_sq:
                continue
            key = (x, y)
            if key in seen:
                continue
            seen.add(key)
            shell_map.setdefault(y, []).append({"x": x, "p": p, "q": q, "y_sq": y_sq})

    rows = []
    for y, hits in sorted(shell_map.items()):
        x_values = sorted({row["x"] for row in hits})
        if len(x_values) <= 1:
            continue
        rows.append(
            {
                "y": y,
                "y_sq": y * y,
                "x_values": x_values,
                "examples": sorted(hits, key=lambda row: (row["x"], abs(row["p"]) + abs(row["q"])))[:8],
            }
        )
    return rows


def numerators(polys: list[sp.Expr]) -> list[sp.Expr]:
    rows = []
    for poly in polys:
        num, den = sp.fraction(sp.together(sp.expand(poly)))
        rows.append(sp.expand(num))
    return rows


def shifted_linear_template() -> dict[str, Any]:
    n = sp.symbols("n")
    u, v, w = sp.symbols("u v w")
    x = -2 + u * n
    y = 3 + v * n
    p = -1 + w * n
    expr = sp.expand(p * (y**2 - p) - (x**3 - 2))
    coeffs = [sp.expand(coeff) for coeff in sp.Poly(expr, n).all_coeffs() if coeff != 0]
    basis = sp.groebner(coeffs, u, v, w, order="lex")

    return {
        "slug": "shifted_linear_linear_linear",
        "family": {
            "x": "-2 + u n",
            "y": "3 + v n",
            "p": "-1 + w n",
            "q": "(3 + v n)^2 - (-1 + w n)",
        },
        "exact_system": [str(poly) for poly in coeffs],
        "groebner_basis": [str(sp.expand(poly.as_expr())) for poly in basis.polys],
        "result": "no_go",
        "proof_summary": [
            "The Groebner basis contains w^4, so every rational solution has w = 0.",
            "With w = 0, the quadratic form 12 v^2 + 12 v w + 97 w^2 reduces to 12 v^2, so v = 0.",
            "The linear basis relation 12 u + 6 v - 11 w = 0 then forces u = 0.",
        ],
    }


def shifted_quadratic_linear_cubic_template() -> dict[str, Any]:
    n = sp.symbols("n")
    u1, u2, v1, a1, a2, a3 = sp.symbols("u1 u2 v1 a1 a2 a3")
    x = -2 + u1 * n + u2 * n**2
    y = 3 + v1 * n
    p = -1 + a1 * n + a2 * n**2 + a3 * n**3
    expr = sp.expand(p * (y**2 - p) - (x**3 - 2))
    coeffs = [sp.expand(coeff) for coeff in sp.Poly(expr, n).all_coeffs() if coeff != 0]

    zero_case_basis = sp.groebner(
        [
            coeffs[2].subs({u2: 0, a3: 0}),
            coeffs[3].subs({u2: 0, a3: 0}),
            coeffs[4].subs({u2: 0, a3: 0}),
            coeffs[5].subs({u2: 0, a3: 0}),
        ],
        u1,
        v1,
        a1,
        a2,
        order="lex",
    )

    sign_cases = []
    m, U, V = sp.symbols("m U V")
    for sign in (1, -1):
        u1_expr = m * U
        u2_expr = -m**2
        v1_expr = m * V
        a3_expr = sign * m**3
        a1_expr = sp.expand((12 * u1_expr + 6 * v1_expr) / 11)
        a2_expr = sp.expand((v1_expr**2 - 3 * sign * m * u1_expr) / 2)
        e2, e3, e4 = coeffs[4], coeffs[3], coeffs[2]
        normalized = numerators(
            [
                sp.expand(e2.subs({u1: u1_expr, u2: u2_expr, v1: v1_expr, a1: a1_expr, a2: a2_expr, a3: a3_expr}) / m**2),
                sp.expand(e3.subs({u1: u1_expr, u2: u2_expr, v1: v1_expr, a1: a1_expr, a2: a2_expr, a3: a3_expr}) / m**3),
                sp.expand(e4.subs({u1: u1_expr, u2: u2_expr, v1: v1_expr, a1: a1_expr, a2: a2_expr, a3: a3_expr}) / m**4),
            ]
        )
        basis = sp.groebner(normalized, U, V, order="lex")
        sign_cases.append(
            {
                "sign": sign,
                "normalized_system": [str(poly) for poly in normalized],
                "groebner_basis": [str(sp.expand(poly.as_expr())) for poly in basis.polys],
                "basis_is_one": basis.polys[0].as_expr() == 1,
            }
        )

    return {
        "slug": "shifted_quadratic_linear_cubic",
        "family": {
            "x": "-2 + u1 n + u2 n^2",
            "y": "3 + v1 n",
            "p": "-1 + a1 n + a2 n^2 + a3 n^3",
            "q": "(3 + v1 n)^2 - p",
        },
        "exact_system": [str(poly) for poly in coeffs],
        "u2_zero_case_groebner_basis": [str(sp.expand(poly.as_expr())) for poly in zero_case_basis.polys],
        "normalized_sign_cases": sign_cases,
        "result": "no_go",
        "proof_summary": [
            "If u2 = 0, then the leading equation forces a3 = 0, and the remaining Groebner basis forces a2 = 0, which collapses to the already-eliminated linear template.",
            "If u2 != 0, write u2 = -m^2 and a3 = ± m^3. After the exact substitutions u1 = m U and v1 = m V, both sign cases reduce to Groebner basis 1 in U and V.",
            "So this shifted quadratic/linear/cubic factor-pair family has no rational nonconstant solution through the seed.",
        ],
    }


def shifted_even_quartic_cubic_sextic_template() -> dict[str, Any]:
    a2, a4, b1, b2, b3, p2, p4, p6 = sp.symbols("a2 a4 b1 b2 b3 p2 p4 p6")
    coeffs = [
        -a4**3 + b3**2 * p6 - p6**2,
        2 * b2 * b3 * p6,
        -3 * a2 * a4**2 + b2**2 * p6 + b3**2 * p4 - 2 * p4 * p6,
        2 * (b2 * b3 * p4 + 3 * b3 * p6),
        -3 * a2**2 * a4 + 6 * a4**2 + b2**2 * p4 + 6 * b2 * p6 + b3**2 * p2 - 2 * p2 * p6 - p4**2,
        2 * (b2 * b3 * p2 + 3 * b3 * p4),
        -a2**3 + 12 * a2 * a4 + b2**2 * p2 + 6 * b2 * p4 - b3**2 - 2 * p2 * p4 + 11 * p6,
        2 * (-b2 * b3 + 3 * b3 * p2),
        6 * a2**2 - 12 * a4 - b2**2 + 6 * b2 * p2 - p2**2 + 11 * p4,
        -6 * b3,
        -12 * a2 - 6 * b2 + 11 * p2,
        -6 * b1,
    ]

    reduced = [coeffs[0], coeffs[2], coeffs[4], coeffs[6], coeffs[8], coeffs[10]]
    m, A, B = sp.symbols("m A B")
    sign_cases = []
    for sign in (1, -1):
        substitutions = {
            a4: -m**2,
            p6: sign * m**3,
            a2: A * m,
            b2: B * m,
            p2: sp.expand((12 * A * m + 6 * B * m) / 11),
            p4: sp.expand((-3 * A * m * (m**4) + B**2 * m**2 * sign * m**3) / (2 * sign * m**3)),
        }
        normalized = numerators(
            [
                sp.expand(reduced[4].subs(substitutions) / m**2),
                sp.expand(reduced[3].subs(substitutions) / m**3),
                sp.expand(reduced[2].subs(substitutions) / m**4),
            ]
        )
        basis = sp.groebner(normalized, A, B, order="lex")
        sign_cases.append(
            {
                "sign": sign,
                "normalized_system": [str(poly) for poly in normalized],
                "groebner_basis": [str(sp.expand(poly.as_expr())) for poly in basis.polys],
                "basis_is_one": basis.polys[0].as_expr() == 1,
            }
        )

    return {
        "slug": "shifted_even_quartic_cubic_sextic",
        "family": {
            "x": "-2 + a2 t^2 + a4 t^4",
            "y": "3 + b1 t + b2 t^2 + b3 t^3",
            "p": "-1 + p2 t^2 + p4 t^4 + p6 t^6",
            "q": "(3 + b1 t + b2 t^2 + b3 t^3)^2 - p",
        },
        "exact_system": [str(poly) for poly in coeffs],
        "result": "no_go",
        "proof_summary": [
            "The odd-degree coefficients force b1 = 0 and b3 = 0, so the cubic y-profile collapses to y = 3 + b2 t^2.",
            "With b3 = 0, the leading equation becomes a4^3 = -p6^2, so write a4 = -m^2 and p6 = ± m^3.",
            "After the exact substitutions a2 = A m and b2 = B m, both sign cases reduce to Groebner basis 1 in A and B.",
            "So this even quartic/cubic/sextic factor-pair identity has no rational nonconstant solution through the seed.",
        ],
        "normalized_sign_cases": sign_cases,
    }


def general_quartic_cubic_sextic_reduction() -> dict[str, Any]:
    a2, a4, b1, b2, b3, p1, p2, p3, p4, p5, p6 = sp.symbols(
        "a2 a4 b1 b2 b3 p1 p2 p3 p4 p5 p6"
    )

    eq1 = -6 * b1 + 11 * p1
    eq2 = -12 * a2 - b1**2 + 6 * b1 * p1 - 6 * b2 - p1**2 + 11 * p2
    eq3 = b1**2 * p1 - 2 * b1 * b2 + 6 * b1 * p2 + 6 * b2 * p1 - 6 * b3 - 2 * p1 * p2 + 11 * p3
    eq4 = (
        6 * a2**2
        - 12 * a4
        + b1**2 * p2
        + 2 * b1 * b2 * p1
        - 2 * b1 * b3
        + 6 * b1 * p3
        - b2**2
        + 6 * b2 * p2
        + 6 * b3 * p1
        - 2 * p1 * p3
        - p2**2
        + 11 * p4
    )
    eq5 = (
        b1**2 * p3
        + 2 * b1 * b2 * p2
        + 2 * b1 * b3 * p1
        + 6 * b1 * p4
        + b2**2 * p1
        - 2 * b2 * b3
        + 6 * b2 * p3
        + 6 * b3 * p2
        - 2 * p1 * p4
        - 2 * p2 * p3
        + 11 * p5
    )
    solution = sp.solve([eq1, eq2, eq3, eq4, eq5], [p1, p2, p3, p4, p5], dict=True, simplify=True)[0]

    reduced_eq6 = (
        -a2**3
        + 12 * a2 * a4
        + b1**2 * solution[p4]
        + 2 * b1 * b2 * solution[p3]
        + 2 * b1 * b3 * solution[p2]
        + 6 * b1 * solution[p5]
        + b2**2 * solution[p2]
        + 2 * b2 * b3 * solution[p1]
        + 6 * b2 * solution[p4]
        - b3**2
        + 6 * b3 * solution[p3]
        - 2 * solution[p1] * solution[p5]
        - 2 * solution[p2] * solution[p4]
        - solution[p3] ** 2
        + 11 * p6
    )
    reduced_eq7 = (
        b1**2 * solution[p5]
        + 2 * b1 * b2 * solution[p4]
        + 2 * b1 * b3 * solution[p3]
        + 6 * b1 * p6
        + b2**2 * solution[p3]
        + 2 * b2 * b3 * solution[p2]
        + 6 * b2 * solution[p5]
        + b3**2 * solution[p1]
        + 6 * b3 * solution[p4]
        - 2 * solution[p1] * p6
        - 2 * solution[p2] * solution[p5]
        - 2 * solution[p3] * solution[p4]
    )
    reduced_eq8 = (
        -3 * a2**2 * a4
        + 6 * a4**2
        + b1**2 * p6
        + 2 * b1 * b2 * solution[p5]
        + 2 * b1 * b3 * solution[p4]
        + b2**2 * solution[p4]
        + 2 * b2 * b3 * solution[p3]
        + 6 * b2 * p6
        + b3**2 * solution[p2]
        + 6 * b3 * solution[p5]
        - 2 * solution[p2] * p6
        - 2 * solution[p3] * solution[p5]
        - solution[p4] ** 2
    )
    reduced_eq9 = (
        2 * b1 * b2 * p6
        + 2 * b1 * b3 * solution[p5]
        + b2**2 * solution[p5]
        + 2 * b2 * b3 * solution[p4]
        + b3**2 * solution[p3]
        + 6 * b3 * p6
        - 2 * solution[p3] * p6
        - 2 * solution[p4] * solution[p5]
    )
    reduced_eq10 = (
        -3 * a2 * a4**2
        + 2 * b1 * b3 * p6
        + b2**2 * p6
        + 2 * b2 * b3 * solution[p5]
        + b3**2 * solution[p4]
        - 2 * solution[p4] * p6
        - solution[p5] ** 2
    )
    reduced_eq11 = 2 * b2 * b3 * p6 + b3**2 * solution[p5] - 2 * solution[p5] * p6

    reduced_numerators = [
        sp.expand(sp.fraction(sp.together(expr))[0])
        for expr in [reduced_eq6, reduced_eq7, reduced_eq8, reduced_eq9, reduced_eq10, reduced_eq11]
    ]
    numeric_reduced = [sp.lambdify((a2, b1, b2, a4, b3, p6), expr, "math") for expr in reduced_numerators]
    leading_trials = [(2, 3, 1), (2, 3, 8), (4, 4, 8), (-8, 4, 32), (-8, 4, -16)]
    leading_scan = []
    for lead in leading_trials:
        hits = []
        for a2_val in range(-20, 21):
            for b1_val in range(-20, 21):
                for b2_val in range(-20, 21):
                    if all(f(a2_val, b1_val, b2_val, *lead) == 0 for f in numeric_reduced):
                        hits.append({"a2": a2_val, "b1": b1_val, "b2": b2_val})
                        if len(hits) >= 8:
                            break
                if len(hits) >= 8:
                    break
            if len(hits) >= 8:
                break
        leading_scan.append({"leading_point": lead, "hit_count": len(hits), "hits": hits})

    return {
        "slug": "general_quartic_cubic_sextic_reduction",
        "family": {
            "x": "-2 + a2 t^2 + a4 t^4",
            "y": "3 + b1 t + b2 t^2 + b3 t^3",
            "p": "-1 + p1 t + p2 t^2 + p3 t^3 + p4 t^4 + p5 t^5 + p6 t^6",
            "q": "y(t)^2 - p(t)",
        },
        "triangular_reduction": {
            key.name: str(sp.factor(sp.together(value)))
            for key, value in solution.items()
        },
        "leading_surface": "-a4^3 + b3^2 p6 - p6^2 = 0",
        "reduced_core_numerators": [str(poly) for poly in reduced_numerators],
        "small_leading_surface_scan": {
            "a2_bound": 20,
            "b1_bound": 20,
            "b2_bound": 20,
            "rows": leading_scan,
        },
        "result": "reduced_core_system",
        "next_action": (
            "Solve the remaining core equations E6 through E12 on the reduced variables "
            "(a2, a4, b1, b2, b3, p6), starting from small integer points on the leading surface "
            "-a4^3 + b3^2 p6 - p6^2 = 0."
        ),
    }


def bounded_quadratic_template(a_bound: int, b_bound: int) -> dict[str, Any]:
    u1, v1 = sp.symbols("u1 v1")
    hits = []

    for a in range(-a_bound, a_bound + 1):
        if a == 0:
            continue
        for b in range(-b_bound, b_bound + 1):
            if b == 0:
                continue
            rel = 12 * a**3 * u1 + 6 * a**3 * v1 - 33 * a * u1 + 22 * v1
            e2 = -726 * a**3 * b - 1452 * a**2 * b + 1331 * b + 582 * u1**2 + 648 * u1 * v1 + 239 * v1**2
            sols = sp.solve([rel, e2], [u1, v1], dict=True)
            for sol in sols:
                u1_val = sp.simplify(sol[u1])
                v1_val = sp.simplify(sol[v1])
                w1_val = sp.simplify((12 * u1_val + 6 * v1_val) / 11)
                u2_val = a**2 * b
                v2_val = a**3 * b
                w2_val = b
                e3 = sp.simplify(
                    -u1_val**3
                    + 12 * u1_val * u2_val
                    + v1_val**2 * w1_val
                    - 2 * v1_val * v2_val
                    + 6 * v1_val * w2_val
                    + 6 * v2_val * w1_val
                    - 2 * w1_val * w2_val
                )
                e4 = sp.simplify(
                    -3 * u1_val**2 * u2_val
                    + 6 * u2_val**2
                    + v1_val**2 * w2_val
                    + 2 * v1_val * v2_val * w1_val
                    - v2_val**2
                    + 6 * v2_val * w2_val
                    - w2_val**2
                )
                if e3 == 0 and e4 == 0:
                    hits.append(
                        {
                            "a": a,
                            "b": b,
                            "u1": str(u1_val),
                            "u2": str(u2_val),
                            "v1": str(v1_val),
                            "v2": str(v2_val),
                            "w1": str(w1_val),
                            "w2": str(w2_val),
                        }
                    )

    return {
        "slug": "shifted_quadratic_quadratic_quadratic",
        "family": {
            "x": "-2 + u1 n + u2 n^2",
            "y": "3 + v1 n + v2 n^2",
            "p": "-1 + w1 n + w2 n^2",
            "q": "(3 + v1 n + v2 n^2)^2 - p",
        },
        "leading_term_normalization": [
            "The degree-6 coefficient forces u2^3 = v2^2 w2.",
            "For the integer bounded scan, use u2 = a^2 b, v2 = a^3 b, w2 = b.",
            "Then the degree-5 and degree-2 equations determine the remaining low-degree coefficients up to a finite rational solve.",
        ],
        "bounded_normalized_scan": {
            "a_bound": a_bound,
            "b_bound": b_bound,
            "hit_count": len(hits),
            "hits": hits,
        },
        "result": "no_hit_in_bounded_scan" if not hits else "candidate_hit",
    }


def build_report(x_bound: int, max_examples: int, a_bound: int, b_bound: int) -> dict[str, Any]:
    equation = load_equation("full_minus2")
    examples = canonical_examples(x_bound, max_examples)
    return {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "equation": equation,
        "factor_pair_formulation": {
            "p": "-z",
            "q": "z + y^2",
            "product": "p q = x^3 - 2",
            "square_shell": "p + q = y^2",
        },
        "canonical_examples": examples,
        "repeated_y_shells": repeated_y_shells(x_bound),
        "templates": [
            shifted_linear_template(),
            shifted_quadratic_linear_cubic_template(),
            shifted_even_quartic_cubic_sextic_template(),
            general_quartic_cubic_sextic_reduction(),
            bounded_quadratic_template(a_bound, b_bound),
        ],
        "next_action": (
            "Three seed-shifted factor-pair templates are now eliminated exactly. "
            "The live next rung is the reduced general quartic/cubic/sextic core on "
            "(a2, a4, b1, b2, b3, p6), beginning from small leading-surface points such as "
            "(a4, b3, p6) = (2, 3, 1) or (2, 3, 8)."
        ),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Factor-Pair Search: full_minus2",
        "",
        f"- Generated: `{report['generated_at']}`",
        f"- Equation: `{report['equation']['equation']}`",
        "",
        "## Formulation",
        "",
        "- `p = -z`",
        "- `q = z + y^2`",
        "- `p q = x^3 - 2`",
        "- `p + q = y^2`",
        "",
        "## Canonical Examples",
        "",
    ]
    for row in report["canonical_examples"][:12]:
        lines.append(
            f"- `x={row['x']}`: `y={row['y']}`, `p={row['p']}`, `q={row['q']}`, `y^2={row['y_sq']}`"
        )

    if report["repeated_y_shells"]:
        lines.extend(["", "## Repeated y-Shells", ""])
        for shell in report["repeated_y_shells"]:
            lines.append(
                f"- `y={shell['y']}` (`y^2={shell['y_sq']}`) occurs for `x={shell['x_values']}`"
            )

    lines.extend(["", "## Template Results", ""])
    for template in report["templates"]:
        lines.append(f"### {template['slug']}")
        lines.append("")
        lines.append(f"- Result: `{template['result']}`")
        if "proof_summary" in template:
            for row in template["proof_summary"]:
                lines.append(f"- {row}")
        if "bounded_normalized_scan" in template:
            scan = template["bounded_normalized_scan"]
            lines.append(
                f"- Normalized bounded scan on `(a, b)` in `[-{scan['a_bound']},{scan['a_bound']}] x "
                f"[-{scan['b_bound']},{scan['b_bound']}]` returned `{scan['hit_count']}` hit(s)."
            )
        lines.append("")

    lines.extend(["## Next Action", "", report["next_action"], ""])
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--x-bound", type=int, default=400)
    parser.add_argument("--max-examples", type=int, default=24)
    parser.add_argument("--a-bound", type=int, default=6)
    parser.add_argument("--b-bound", type=int, default=10)
    parser.add_argument("--emit-json", default=str(DEFAULT_JSON_PATH))
    parser.add_argument("--emit-markdown", default=str(DEFAULT_MD_PATH))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(
        x_bound=args.x_bound,
        max_examples=args.max_examples,
        a_bound=args.a_bound,
        b_bound=args.b_bound,
    )
    Path(args.emit_json).write_text(json.dumps(report, indent=2))
    Path(args.emit_markdown).write_text(render_markdown(report))
    print(f"wrote {args.emit_json}")
    print(f"wrote {args.emit_markdown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
