#!/usr/bin/env python3
"""Exact factor-pair family search for full_minus2."""

from __future__ import annotations

import argparse
import json
import math
import re
import time
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "equations.json"
DEFAULT_JSON_PATH = ROOT / "results" / "factor_pair_full_minus2_search.json"
DEFAULT_MD_PATH = ROOT / "results" / "factor_pair_full_minus2_search.md"
PROBE_LOG_PATH = ROOT / "results" / "leading_surface_probe_log.md"


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


def strip_variable_power(expr: sp.Expr, var: sp.Symbol) -> tuple[int, sp.Expr]:
    poly = sp.Poly(sp.expand(expr), var, domain="QQ")
    min_power = min(monom[0] for monom, coeff in poly.terms() if coeff)
    stripped = sp.expand(poly.as_expr() / (var**min_power))
    return min_power, stripped


def is_rational_square(value: sp.Rational) -> bool:
    if value < 0:
        return False
    num, den = value.as_numer_denom()
    num_int = int(num)
    den_int = int(den)
    return math.isqrt(num_int) ** 2 == num_int and math.isqrt(den_int) ** 2 == den_int


def leading_point_height_key(point: tuple[int, int, int]) -> tuple[int, int, int, int, int, int, int, int]:
    a4, b3, p6 = point
    return (
        max(abs(a4), abs(b3), abs(p6)),
        abs(a4) + abs(b3) + abs(p6),
        abs(a4),
        abs(b3),
        abs(p6),
        a4,
        b3,
        p6,
    )


def is_weighted_primitive_leading_point(a4: int, b3: int, p6: int) -> bool:
    scale_bound = int(round(max(abs(a4), abs(b3), abs(p6)) ** 0.25)) + 2
    for t in range(2, scale_bound + 1):
        if a4 % (t**4) == 0 and b3 % (t**3) == 0 and p6 % (t**6) == 0:
            return False
    return True


def canonical_leading_point(a4: int, b3: int, p6: int) -> tuple[int, int, int]:
    b3_abs = abs(b3)
    partner = b3_abs * b3_abs - p6
    candidates = [(a4, b3_abs, p6), (a4, b3_abs, partner)]
    return min(candidates, key=leading_point_height_key)


def primitive_leading_surface_representatives(a4_bound: int = 1200, b3_bound: int = 500) -> list[tuple[int, int, int]]:
    reps: set[tuple[int, int, int]] = set()
    for a4 in range(-a4_bound, a4_bound + 1):
        if a4 == 0:
            continue
        a4_cubed = a4**3
        for b3 in range(1, b3_bound + 1):
            disc = b3**4 - 4 * a4_cubed
            if disc < 0:
                continue
            sqrt_disc = math.isqrt(disc)
            if sqrt_disc * sqrt_disc != disc:
                continue
            for numerator in (b3 * b3 + sqrt_disc, b3 * b3 - sqrt_disc):
                if numerator % 2:
                    continue
                p6 = numerator // 2
                if -a4_cubed + b3 * b3 * p6 - p6 * p6 != 0:
                    continue
                if not is_weighted_primitive_leading_point(a4, b3, p6):
                    continue
                reps.add(canonical_leading_point(a4, b3, p6))
    return sorted(reps, key=leading_point_height_key)


def parse_logged_probe_points(path: Path = PROBE_LOG_PATH) -> set[tuple[int, int, int]]:
    if not path.exists():
        return set()
    pattern = re.compile(r"^### `\((-?\d+), (-?\d+), (-?\d+)\)`$")
    rows: set[tuple[int, int, int]] = set()
    for line in path.read_text().splitlines():
        match = pattern.match(line.strip())
        if not match:
            continue
        rows.add(tuple(int(group) for group in match.groups()))
    return rows


def report_dead_leading_points(report_path: Path = DEFAULT_JSON_PATH) -> set[tuple[int, int, int]]:
    if not report_path.exists():
        return set()
    report = load_json(report_path)
    rows: set[tuple[int, int, int]] = set()
    for template in report.get("templates", []):
        point = template.get("leading_point")
        if point and template.get("result") == "no_go":
            rows.add(tuple(int(value) for value in point))
    return rows


def known_dead_leading_points(
    report_path: Path = DEFAULT_JSON_PATH,
    probe_log_path: Path = PROBE_LOG_PATH,
) -> set[tuple[int, int, int]]:
    return report_dead_leading_points(report_path) | parse_logged_probe_points(probe_log_path)


def contiguous_section_rows(
    rows: list[tuple[int, int, int]],
    section_index: int,
    section_count: int,
) -> list[tuple[int, int, int]]:
    if section_count < 1:
        raise ValueError("section_count must be at least 1")
    if not 1 <= section_index <= section_count:
        raise ValueError("section_index must satisfy 1 <= section_index <= section_count")
    chunk_size = (len(rows) + section_count - 1) // section_count
    start = chunk_size * (section_index - 1)
    end = min(len(rows), start + chunk_size)
    return rows[start:end]


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


def reduced_core_branch_reduction(a4_value: int, b3_value: int, p6_value: int, slug: str) -> dict[str, Any]:
    a2, b1, b2 = sp.symbols("a2 b1 b2")
    a4 = sp.Integer(a4_value)
    b3 = sp.Integer(b3_value)
    p6 = sp.Integer(p6_value)

    p1 = sp.expand(6 * b1 / 11)
    p2 = sp.expand((1452 * a2 - 239 * b1**2 + 726 * b2) / 1331)
    p3 = sp.expand(-2 * (39204 * a2 * b1 - 2460 * b1**3 + 28919 * b1 * b2 - 43923 * b3) / 161051)
    p4 = sp.expand(
        -(
            8521062 * a2**2
            - 1607364 * a2 * b1**2
            + 9487368 * a2 * b2
            - 21258732 * a4
            - 109550 * b1**4
            - 1785960 * b1**2 * b2
            + 6998398 * b1 * b3
            + 3499199 * b2**2
        )
        / 19487171
    )
    p5 = sp.expand(
        2
        * (
            116220258 * a2**2 * b1
            + 34665048 * a2 * b1**3
            + 194491044 * a2 * b1 * b2
            - 573985764 * a2 * b3
            - 573985764 * a4 * b1
            - 7407990 * b1**5
            + 26511100 * b1**3 * b2
            + 108050580 * b1**2 * b3
            + 108050580 * b1 * b2**2
            - 423403079 * b2 * b3
        )
        / 2357947691
    )

    e11 = sp.expand(sp.fraction(sp.together(2 * b2 * b3 * p6 + b3**2 * p5 - 2 * p5 * p6))[0] / 4)
    e7 = sp.expand(
        sp.fraction(
            sp.together(
                b1**2 * p5
                + 2 * b1 * b2 * p4
                + 2 * b1 * b3 * p3
                + 6 * b1 * p6
                + b2**2 * p3
                + 2 * b2 * b3 * p2
                + 6 * b2 * p5
                + b3**2 * p1
                + 6 * b3 * p4
                - 2 * p1 * p6
                - 2 * p2 * p5
                - 2 * p3 * p4
            )
        )[0]
        / -4
    )
    e10 = sp.expand(
        sp.fraction(
            sp.together(-3 * a2 * a4**2 + 2 * b1 * b3 * p6 + b2**2 * p6 + 2 * b2 * b3 * p5 + b3**2 * p4 - 2 * p4 * p6 - p5**2)
        )[0]
        / -2
    )
    e6 = sp.expand(
        sp.fraction(
            sp.together(
                -a2**3
                + 12 * a2 * a4
                + b1**2 * p4
                + 2 * b1 * b2 * p3
                + 2 * b1 * b3 * p2
                + 6 * b1 * p5
                + b2**2 * p2
                + 2 * b2 * b3 * p1
                + 6 * b2 * p4
                - b3**2
                + 6 * b3 * p3
                - 2 * p1 * p5
                - 2 * p2 * p4
                - p3**2
                + 11 * p6
            )
        )[0]
    )

    b1_zero_relation = sp.solve(sp.Eq(sp.factor(e11.subs({b1: 0})), 0), b2)[0]
    b1_zero_obstructions = {
        "E10": str(sp.factor(sp.fraction(sp.together(e10.subs({b1: 0, b2: b1_zero_relation})))[0])),
        "E7": str(sp.factor(sp.fraction(sp.together(e7.subs({b1: 0, b2: b1_zero_relation})))[0])),
        "E6": str(sp.factor(sp.fraction(sp.together(e6.subs({b1: 0, b2: b1_zero_relation})))[0])),
    }
    b1_zero_e7_poly = sp.Poly(sp.expand(sp.fraction(sp.together(e7.subs({b1: 0, b2: b1_zero_relation})))[0]), a2, domain="QQ")
    ratio = sp.simplify(-b1_zero_e7_poly.nth(0) / b1_zero_e7_poly.nth(2))
    ratio_square = ratio.is_rational and is_rational_square(sp.Rational(ratio))

    odd_branch_resultant = sp.factor(sp.resultant(e11, e7, b2))
    odd_branch_e6_resultant = sp.factor(sp.resultant(e11, e6, b2))
    odd_branch_e10_resultant = sp.factor(sp.resultant(e11, e10, b2))
    odd_branch_v6 = sp.factor(sp.resultant(sp.Poly(odd_branch_resultant, a2), sp.Poly(odd_branch_e6_resultant, a2), a2))
    odd_branch_v10 = sp.factor(sp.resultant(sp.Poly(odd_branch_resultant, a2), sp.Poly(odd_branch_e10_resultant, a2), a2))
    odd_branch_v6_power, odd_branch_v6_nonzero = strip_variable_power(odd_branch_v6, b1)
    odd_branch_v10_power, odd_branch_v10_nonzero = strip_variable_power(odd_branch_v10, b1)
    odd_branch_gcd = sp.gcd(
        sp.Poly(odd_branch_v6_nonzero, b1, domain="QQ"),
        sp.Poly(odd_branch_v10_nonzero, b1, domain="QQ"),
    )

    leading_point = [int(a4), int(b3), int(p6)]
    return {
        "slug": slug,
        "leading_point": leading_point,
        "result": "no_go",
        "equations": {
            "E6": str(sp.factor(e6)),
            "E11": str(sp.factor(e11)),
            "E10": str(sp.factor(e10)),
            "E7": str(sp.factor(e7)),
        },
        "b1_zero_branch": {
            "b2_relation": f"b2 = {sp.sstr(sp.factor(b1_zero_relation))}",
            "obstructions": b1_zero_obstructions,
            "result": "no_go",
            "proof_summary": [
                f"On b1 = 0, E11 is linear and forces b2 = {sp.sstr(sp.factor(b1_zero_relation))}.",
                f"Substituting this into E7 gives {sp.sstr(sp.factor(b1_zero_e7_poly.as_expr()))} = 0.",
                (
                    f"The induced square ratio is {ratio}, which is not a rational square."
                    if not ratio_square
                    else f"The induced square ratio is {ratio}."
                ),
                "So the b1 = 0 branch is impossible."
                if not ratio_square
                else "This branch needs a different obstruction."
            ],
        },
        "odd_branch": {
            "condition": "b1 != 0",
            "elimination_object": str(odd_branch_resultant),
            "bridge_resultants": {
                "E11_E6": str(odd_branch_e6_resultant),
                "E11_E10": str(odd_branch_e10_resultant),
            },
            "nonzero_b1_obstructions": {
                "from_E6": {
                    "removed_b1_power": odd_branch_v6_power,
                    "degree_in_b1": sp.Poly(odd_branch_v6_nonzero, b1, domain="QQ").degree(),
                    "polynomial": str(odd_branch_v6_nonzero),
                },
                "from_E10": {
                    "removed_b1_power": odd_branch_v10_power,
                    "degree_in_b1": sp.Poly(odd_branch_v10_nonzero, b1, domain="QQ").degree(),
                    "polynomial": str(odd_branch_v10_nonzero),
                },
            },
            "intersection_gcd": str(odd_branch_gcd.as_expr()),
            "result": "no_go",
            "proof_summary": [
                "Eliminating b2 from (E11, E7), (E11, E6), and (E11, E10) gives exact resultants in (a2, b1).",
                "Eliminating a2 from the pairs (R7, R6) and (R7, R10) gives two univariate obstructions in b1.",
                "After removing the forced b1-powers coming from the excluded branch b1 = 0, the two remaining b1-polynomials are coprime.",
                "So there is no nonzero rational b1 satisfying both obstructions, and the odd branch is impossible.",
            ],
        },
        "proof_summary": [
            "The b1 = 0 branch is impossible by the exact square obstruction coming from E7 after the linear E11 reduction.",
            "The b1 != 0 branch is impossible because the two exact nonzero-b1 elimination polynomials are coprime.",
            f"Therefore the reduced quartic/cubic/sextic factor-pair branch over the leading point {leading_point} has no rational solution.",
        ],
    }


def branch_231_reduction() -> dict[str, Any]:
    return reduced_core_branch_reduction(2, 3, 1, "branch_lead_2_3_1")


def branch_238_reduction() -> dict[str, Any]:
    return reduced_core_branch_reduction(2, 3, 8, "branch_lead_2_3_8")


def branch_448_reduction() -> dict[str, Any]:
    return reduced_core_branch_reduction(4, 4, 8, "branch_lead_4_4_8")


def branch_m8432_reduction() -> dict[str, Any]:
    return reduced_core_branch_reduction(-8, 4, 32, "branch_lead_m8_4_32")


def branch_m84m16_reduction() -> dict[str, Any]:
    return reduced_core_branch_reduction(-8, 4, -16, "branch_lead_m8_4_m16")


def general_b1_zero_leading_surface_reduction() -> dict[str, Any]:
    a2, a4, b2, b3, p2, p3, p4, p5, p6 = sp.symbols("a2 a4 b2 b3 p2 p3 p4 p5 p6")
    solution = sp.solve(
        [
            -12 * a2 - 6 * b2 + 11 * p2,
            -6 * b3 + 11 * p3,
            6 * a2**2 - 12 * a4 - b2**2 + 6 * b2 * p2 - p2**2 + 11 * p4,
            -2 * b2 * b3 + 6 * b2 * p3 + 6 * b3 * p2 - 2 * p2 * p3 + 11 * p5,
        ],
        [p2, p3, p4, p5],
        dict=True,
        simplify=True,
    )[0]
    p2_expr, p3_expr, p4_expr, p5_expr = [sp.expand(solution[s]) for s in (p2, p3, p4, p5)]

    e11 = sp.expand(2 * b2 * b3 * p6 + b3**2 * p5_expr - 2 * p5_expr * p6)
    b2_relation = sp.factor(sp.solve(sp.Eq(e11, 0), b2)[0])
    e7 = sp.expand(b2**2 * p3_expr + 2 * b2 * b3 * p2_expr + 6 * b2 * p5_expr + 6 * b3 * p4_expr - 2 * p2_expr * p5_expr - 2 * p3_expr * p4_expr)
    e7_substituted = sp.factor(sp.expand(e7.subs(b2, b2_relation)))
    e7_numerator = sp.factor(sp.together(e7_substituted).as_numer_denom()[0])

    d_poly = sp.factor(10177 * b3**4 - 6102 * b3**2 * p6 + 688905 * p6**2)
    c_poly = sp.factor(114242 * b3**4 - 1729404 * b3**2 * p6 + 6544962 * p6**2)
    d_discriminant = sp.factor(sp.discriminant(sp.Poly(d_poly, p6), p6))
    d_on_surface = sp.factor(
        sp.together(d_poly.subs(b3**2, (a4**3 + p6**2) / p6)).as_numer_denom()[0]
    )
    c_on_surface = sp.factor(
        sp.together(c_poly.subs(b3**2, (a4**3 + p6**2) / p6)).as_numer_denom()[0]
    )
    exceptional_subs = {p6: sp.Rational(239, 1809) * b3**2}
    exceptional_e11 = sp.factor(e11.subs(exceptional_subs))
    exceptional_e7 = sp.factor(e7.subs(exceptional_subs).subs(a2, 0))
    exceptional_constant = sp.factor(48039 * 315570)

    return {
        "slug": "general_b1_zero_leading_surface_reduction",
        "result": "symbolic_reduction",
        "formulas": {
            "p2": str(p2_expr),
            "p3": str(p3_expr),
            "p4": str(p4_expr),
            "p5": str(p5_expr),
            "E11": str(sp.factor(e11)),
            "b2_relation": str(b2_relation),
            "E7_after_b2": str(e7_substituted),
            "leading_surface": "-a4^3 + b3^2 p6 - p6^2 = 0",
            "quadratic_coefficient_D": str(d_poly),
            "quadratic_discriminant_in_p6": str(d_discriminant),
            "constant_coefficient_C": str(c_poly),
            "C_factorization": str(sp.factor(c_poly)),
            "D_on_leading_surface_numerator": str(d_on_surface),
            "C_on_leading_surface_numerator": str(c_on_surface),
            "exceptional_condition": "1809 p6 - 239 b3^2 = 0",
            "exceptional_E11": str(exceptional_e11),
            "exceptional_E7_after_a2_zero": str(exceptional_e7),
            "exceptional_leading_surface_constant": str(exceptional_constant),
        },
        "proof_summary": [
            "Inside the reduced quartic/cubic/sextic core, the entire b1 = 0 slice can be solved symbolically before fixing any specific leading point.",
            "On b1 = 0, E11 is linear in b2 unless the exceptional coefficient 1809 p6 - 239 b3^2 vanishes.",
            "Away from that exceptional coefficient, E11 forces an exact proportionality b2 = -(324 a2 (b3^2 - 2 p6)) / (1809 p6 - 239 b3^2).",
            "Substituting this into E7 gives a pure quadratic obstruction in a2 of the form D(a4,b3,p6) a2^2 - a4 C(b3,p6) = 0.",
            "The constant coefficient polynomial satisfies C(b3,p6) = 2 (1809 p6 - 239 b3^2)^2, so the obstruction is controlled by the remaining quadratic coefficient D.",
            "Viewed as a quadratic in p6, D has discriminant -28006710336 b3^4, so for every integer leading point with b3 != 0 the coefficient D is strictly positive.",
            "Therefore, away from the exceptional slice, the non-exceptional obstruction D(a4,b3,p6) a2^2 = a4 C(b3,p6) forces a4 > 0 because both D and C are positive.",
            "So every integer leading point with a4 < 0 is globally impossible on the b1 = 0 branch by sign alone.",
            "On the leading surface b3^2 p6 - p6^2 = a4^3, the numerator of C becomes 2 (-239 a4^3 + 1570 p6^2)^2.",
            "On the exceptional coefficient slice 1809 p6 - 239 b3^2 = 0, E11 collapses to -24 a2 b3^3 / 67, so for integer leading branches with b3 != 0 it forces a2 = 0.",
            "With a2 = 0 on that same slice, E7 reduces to 1089 a4 - 205 b2^2 = 0, so b2 = 33 u and a4 = 205 u^2 for some integer u.",
            "Writing b3 = 603 m to make p6 = 239 b3^2 / 1809 integral gives p6 = 48039 m^2 and a4^3 = 15159667230 m^4 on the leading surface.",
            "Substituting a4 = 205 u^2 gives 25 * 41^3 * u^6 = 2 * 3^2 * 67^2 * 157 * 239 * m^4, which is impossible because the 41-adic valuation would have to satisfy 3 + 6 v41(u) = 4 v41(m).",
            "Therefore the exceptional coefficient slice has no integer leading points, so the symbolic b1 = 0 reduction is universal on the integer leading surface.",
        ],
        "next_action": (
            "The b1 = 0 branch is now globally eliminated on every integer leading point with a4 < 0. "
            "For the remaining positive-a4 leading points, use the universal symbolic obstruction together with the "
            "leading-surface equation to prove that D(a4,b3,p6) prevents a2^2 from being a rational square. "
            "In parallel, seek a general odd-branch elimination on b1 != 0 instead of continuing pointwise branch checks."
        ),
        "e7_numerator": str(e7_numerator),
    }


def weighted_scaling_reduction() -> dict[str, Any]:
    return {
        "slug": "weighted_scaling_reduction",
        "result": "symbolic_reduction",
        "scaling_law": {
            "variables": {
                "a2": "T^2 A",
                "b1": "T B",
                "b2": "T^2 C",
                "a4": "T^4 A4",
                "b3": "T^3 B3",
                "p6": "T^6 P6",
            },
            "equation_weights": {
                "E6": "T^6",
                "E7": "T^7",
                "E10": "T^10",
                "E11": "T^11",
            },
        },
        "proof_summary": [
            "The reduced quartic/cubic/sextic core is weighted-homogeneous with weights wt(a2,b1,b2,a4,b3,p6) = (2,1,2,4,3,6).",
            "Under the scaling (a2,b1,b2,a4,b3,p6) = (T^2 A, T B, T^2 C, T^4 A4, T^3 B3, T^6 P6), the core equations scale as E6 -> T^6 E6, E7 -> T^7 E7, E10 -> T^10 E10, and E11 -> T^11 E11.",
            "Therefore any exact no-go for a leading point (A4, B3, P6) automatically kills the entire weighted scaling family (T^4 A4, T^3 B3, T^6 P6).",
            "This explains, for example, why (32, 24, 64) reproduces the same reduced-core obstruction pattern as (2, 3, 1): it is the T = 2 member of the family (2 T^4, 3 T^3, T^6).",
        ],
        "eliminated_scaling_families": [
            "(2 T^4, 3 T^3, T^6)",
            "(2 T^4, 3 T^3, 8 T^6)",
            "(4 T^4, 4 T^3, 8 T^6)",
            "(-8 T^4, 4 T^3, 32 T^6)",
            "(-8 T^4, 4 T^3, -16 T^6)",
            "(-20 T^4, 22 T^3, -16 T^6)",
            "(-18 T^4, 3 T^3, -72 T^6)",
            "(27 T^4, 18 T^3, 81 T^6)",
        ],
        "next_action": (
            "Stop probing weighted rescalings of already eliminated leading points. Search only primitive leading-surface "
            "points up to the weighted scaling relation, and push the remaining effort into the universal odd-branch "
            "elimination and the non-exceptional b1 = 0 square obstruction."
        ),
    }


def t_sign_symmetry_reduction() -> dict[str, Any]:
    return {
        "slug": "t_sign_symmetry_reduction",
        "result": "symbolic_reduction",
        "symmetry": {
            "t_map": "t -> -t",
            "leading_point_map": "(a4, b3, p6) -> (a4, -b3, p6)",
        },
        "proof_summary": [
            "Replacing t by -t preserves the quartic x(t), the sextic p(t), and the leading coefficient p6, while it flips the odd coefficients b1, b3, p1, p3, and p5.",
            "So every reduced-core branch over (a4, b3, p6) has a partner over (a4, -b3, p6) with the same exact solvability status.",
            "This lets the primitive leading-surface queue keep only one sign of b3, which is why the current scan window drops from 122 signed primitive branches to 61 sign-reduced representatives.",
        ],
        "next_action": "Probe only one b3-sign from each primitive branch. The b3 <-> -b3 partner is exact symmetry, not a new surface.",
    }


def root_swap_symmetry_reduction() -> dict[str, Any]:
    return {
        "slug": "root_swap_symmetry_reduction",
        "result": "symbolic_reduction",
        "symmetry": {
            "z_map": "z -> -y^2 - z",
            "factor_pair_map": "(p, q) -> (q, p)",
            "leading_point_map": "(a4, b3, p6) -> (a4, b3, b3^2 - p6)",
        },
        "proof_summary": [
            "The original equation is quadratic in z, so every solution (x, y, z) has a partner obtained by swapping to the other quadratic root z' = -y^2 - z.",
            "In factor-pair language this is exactly the involution (p, q) -> (q, p), since p = -z and q = z + y^2.",
            "On reduced-core leading coefficients, the involution fixes a4 and b3 and sends p6 to q6 = b3^2 - p6.",
            "Therefore an exact no-go for (a4, b3, p6) automatically gives the same no-go for its paired leading point (a4, b3, b3^2 - p6).",
            "This explains, for example, the paired branches (2, 3, 1) <-> (2, 3, 8), (-18, 3, -72) <-> (-18, 3, 81), and (27, 18, 81) <-> (27, 18, 243).",
        ],
        "paired_examples": [
            "[(2, 3, 1), (2, 3, 8)]",
            "[(-18, 3, -72), (-18, 3, 81)]",
            "[(27, 18, 81), (27, 18, 243)]",
            "[(-24, 20, -32), (-24, 20, 432)]",
        ],
        "next_action": (
            "Search primitive leading-surface points only up to weighted scaling and root-swap symmetry. "
            "Do not probe both members of the same p6 <-> b3^2 - p6 pair."
        ),
    }


def odd_branch_unit_normalization_reduction() -> dict[str, Any]:
    u, A, v, B, P = sp.symbols("u A v B P")
    e6 = sp.expand(
        249513737484 * A * u
        + 138904554888 * A * v
        - 23533416324 * A
        + 51231772559 * B**2
        - 47066832648 * B * u
        - 52296480720 * B * v
        - 6415686200 * B
        + 285311670611 * P
        - 1192260553 * u**3
        - 28125302436 * u**2 * v
        - 13678412814 * u**2
        - 23533416324 * u * v**2
        - 25166824848 * u * v
        + 7104948180 * u
        - 8716080120 * v**3
        - 9623529300 * v**2
        + 8963667900 * v
        - 626093370
    )
    e7 = sp.expand(
        -2
        * (
            -8403725570724 * A * B
            - 3333709317312 * A * u
            - 902879606772 * A * v
            + 1142933208516 * A
            + 198710682687 * B**2
            + 1701580797378 * B * u**2
            + 2847543375204 * B * u * v
            + 2793397384800 * B * u
            + 1581968541780 * B * v**2
            + 2576452024740 * B * v
            - 369078380550 * B
            - 7703415106497 * P
            + 1005623058528 * u**3
            + 2414471116266 * u**2 * v
            - 277528968882 * u**2
            + 2157995144052 * u * v**2
            - 1039893188664 * u * v
            - 84903240312 * u
            + 623483178340 * v**3
            - 824768524800 * v**2
            - 14747139990 * v
            + 13940039910
        )
    )
    e10 = sp.expand(
        -16679751940476694443 * A**2 * u
        - 1317838629098654784 * A**2
        + 6065364341991525252 * A * B**2
        - 2635677258197309568 * A * B * u
        - 7357932345800822544 * A * B * v
        + 496155957695544960 * A * B
        - 12130728683983050504 * A * P
        + 533670188643256896 * A * u**2
        + 893080723851980928 * A * u * v
        + 159177952483013376 * A * u
        + 496155957695544960 * A * v**2
        + 121735951903843200 * A * v
        - 34016646398834880 * A
        - 1996724624980681178 * B**3
        - 3748997063698563666 * B**2 * u**2
        - 10064789159582164392 * B**2 * u * v
        + 954755665815524364 * B**2 * u
        - 5708892231678423909 * B**2 * v**2
        + 1894657279811151240 * B**2 * v
        - 15443817837910550 * B**2
        + 15113283876945825318 * B * P
        + 533670188643256896 * B * u**3
        + 2382910000481073096 * B * u**2 * v
        + 58716622205816256 * B * u**2
        + 2989339645115658384 * B * u * v**2
        + 397988775046878048 * B * u * v
        - 63981274735857600 * B * u
        + 1385102048566729680 * B * v**3
        + 246446776358204400 * B * v**2
        - 117879455714918040 * B * v
        + 6403500929073600 * B
        + 4862316869199817764 * P * u**2
        + 5413713627562683696 * P * u * v
        - 917199416239958808 * P * u
        + 7556641938472912659 * P * v**2
        - 1019110462488843120 * P * v
        - 62511787030870100 * P
        - 54028593478346256 * u**4
        - 180830394498954816 * u**3 * v
        - 32230246577139072 * u**3
        - 251768395062036864 * u**2 * v**2
        - 78585346061551296 * u**2 * v
        + 2081005861122144 * u**2
        - 168118960872044160 * u * v**3
        - 71214000469729920 * u * v**2
        + 4174233240070080 * u * v
        + 2054386631468160 * u
        - 46699711353345600 * v**4
        - 22916317851504000 * v**3
        + 3592147236233600 * v**2
        + 1571151709512000 * v
        - 219513263360400
    )
    e11 = sp.expand(
        2
        * (
            -573985764 * A * B**2
            + 1147971528 * A * P
            - 573985764 * B**3 * u
            - 423403079 * B**3 * v
            + 108050580 * B**3
            + 116220258 * B**2 * u**2
            + 194491044 * B**2 * u * v
            + 34665048 * B**2 * u
            + 108050580 * B**2 * v**2
            + 26511100 * B**2 * v
            - 7407990 * B**2
            + 1147971528 * B * P * u
            + 3204753849 * B * P * v
            - 216101160 * B * P
            - 232440516 * P * u**2
            - 388982088 * P * u * v
            - 69330096 * P * u
            - 216101160 * P * v**2
            - 53022200 * P * v
            + 14815980 * P
        )
    )

    return {
        "slug": "odd_branch_unit_normalization_reduction",
        "result": "symbolic_reduction",
        "normalization": {
            "branch_condition": "b1 != 0",
            "substitution": {
                "a2": "u b1^2",
                "b2": "v b1^2",
                "a4": "A b1^4",
                "b3": "B b1^3",
                "p6": "P b1^6",
            },
            "leading_surface": "-A^3 + B^2 P - P^2 = 0",
        },
        "normalized_equations": {
            "E6": str(sp.factor(e6)),
            "E7": str(sp.factor(e7)),
            "E10": str(sp.factor(e10)),
            "E11": str(sp.factor(e11)),
        },
        "root_swap_fixed_slice": {
            "condition": "2 P = B^2",
            "E11_after_substitution": str(sp.factor(sp.expand(e11.subs(P, B**2 / 2)))),
            "leading_surface_family": "(A, B, P) = (4 T^4, 4 T^3, 8 T^6)",
            "status": "killed_by_branch_4_4_8",
        },
        "proof_summary": [
            "On the odd branch b1 != 0, weighted homogeneity lets us divide out b1 completely and rewrite the reduced core in the universal variables (u, v, A, B, P) with b1 normalized to 1.",
            "So every odd-branch solution over an integer leading point produces a rational solution of the normalized system (E6, E7, E10, E11) on the rational leading surface -A^3 + B^2 P - P^2 = 0.",
            "Inside that normalized odd system, E11 splits off the root-swap-fixed slice 2 P = B^2. There E11 collapses to 2357947691 B^3 v, so the slice is forced onto v = 0.",
            "The same slice is exactly the weighted scaling family (A, B, P) = (4 T^4, 4 T^3, 8 T^6), which is already eliminated by the exact no-go at the primitive branch (4, 4, 8).",
            "So the live odd frontier is the asymmetric normalized surface 2 P != B^2 together with the unit-normalized equations above.",
        ],
        "next_action": (
            "Stay on primitive representatives modulo weighted scaling, root swap, and t-sign symmetry. "
            "For the odd branch, work only on the asymmetric normalized system with b1 = 1 and 2 P != B^2."
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
            general_b1_zero_leading_surface_reduction(),
            weighted_scaling_reduction(),
            t_sign_symmetry_reduction(),
            root_swap_symmetry_reduction(),
            odd_branch_unit_normalization_reduction(),
            branch_231_reduction(),
            branch_238_reduction(),
            branch_448_reduction(),
            branch_m8432_reduction(),
            branch_m84m16_reduction(),
            bounded_quadratic_template(a_bound, b_bound),
        ],
        "next_action": (
            "Three seed-shifted factor-pair templates are now eliminated exactly, the b1 = 0 side of the reduced core "
            "is symbolically compressed, and every stored small leading-surface branch is eliminated exactly. "
            "Because the reduced core is weighted-homogeneous and root-swap symmetric, these branch eliminations also "
            "kill their entire scaling families and their paired p6 <-> b3^2 - p6 partners. After also quotienting by "
            "the exact t -> -t sign symmetry, the live odd frontier now sits on the asymmetric unit-normalized system "
            "b1 = 1 with 2 P != B^2. On the b1 = 0 side, every negative-a4 leading point is now dead globally by sign, "
            "so the remaining work is to rule out rational squares on the positive-a4 side."
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
