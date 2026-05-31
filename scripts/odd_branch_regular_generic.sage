# Exact regular-generic check for the normalized odd branch.
#
# Run with:
#   HOME=/tmp SAGE_STARTUP_FILE=/tmp/empty.sage sage scripts/odd_branch_regular_generic.sage
#
# This script starts after the D0 = 0 denominator locus has been cleared.
# It solves the low-degree pair E6 = E7 = 0 for (A, P), substitutes into
# E11, E10, and the leading surface, then saturates by the live generic
# nonzero conditions:
#
#   D0 != 0, B != 0, v != 0, 2 P - B^2 != 0
#
# No u != 0 condition is imposed here.

from sage.all import PolynomialRing, QQ, sage_eval

import json
import os
import sys
import time
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
RESULT_JSON = ROOT / "results" / "odd_branch_regular_generic.json"
RESULT_MD = ROOT / "results" / "odd_branch_regular_generic.md"
MAX_BASIS_CHARS = 1400
RUN_SATURATION = os.environ.get("DIOPHANTINE_RUN_SATURATION") == "1"

sys.path.insert(0, str(ROOT / "scripts"))
import search_factor_pair_families as source


def sympy_to_sage_poly(expr, ring, locals_map):
    text = sp.sstr(sp.expand(expr)).replace("**", "^")
    return ring(sage_eval(text, locals=locals_map))


def truncate(text, limit=MAX_BASIS_CHARS):
    return text if len(text) <= limit else text[:limit] + " ... [truncated]"


def basis_profile(basis, limit=14):
    profile = []
    for g in basis[:limit]:
        profile.append(
            {
                "total_degree": int(g.total_degree()),
                "leading_monomial": str(g.lm()),
                "terms": int(len(g.monomials())),
            }
        )
    return profile


def write_artifacts(results):
    RESULT_JSON.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")

    lines = [
        "# Odd Branch Regular Generic Check",
        "",
        "Route: normalized odd branch after clearing the singular denominator locus `D0 = 0`.",
        "",
        "Live regular-branch exclusions tracked:",
        "",
        "- `D0 != 0`",
        "- `B != 0`",
        "- `v != 0`",
        "- `2 P - B^2 != 0`",
        "",
        "No `u != 0` condition is imposed.",
        "",
        "## Reduction",
        "",
        f"- solved equations: `{results.get('solved_equations')}`",
        f"- method: `{results.get('method')}`",
        f"- `A` denominator: `{results.get('A_denominator')}`",
        f"- `P` denominator: `{results.get('P_denominator')}`",
        f"- saturation product: `{results.get('saturation_product')}`",
        "",
        "Numerator profile after substituting `A(u,v,B)` and `P(u,v,B)`:",
        "",
    ]

    for item in results.get("numerators", []):
        lines.append(
            f"- `{item['name']}`: total degree `{item['total_degree']}`, "
            f"terms `{item['terms']}`, string length `{item['string_length']}`"
        )
    lines.extend(["", "## Result", ""])

    if results.get("error"):
        lines.extend(
            [
                f"- status: `error`",
                f"- error: `{results['error']}`",
                "",
                "Do not promote this branch until the exact run completes.",
                "",
            ]
        )
    else:
        lines.extend(
            [
                f"- seconds: `{results.get('seconds')}`",
                f"- Groebner basis length: `{results.get('basis_length')}`",
                f"- contains `1`: `{results.get('contains_one')}`",
                f"- dimension: `{results.get('dimension')}`",
                f"- degree / vector-space dimension: `{results.get('degree')}`",
                f"- rationally dead: `{results.get('rationally_dead')}`",
                f"- rational obstruction: `{results.get('rational_obstruction')}`",
                f"- lex profile: `{results.get('lex_profile')}`",
                f"- read: `{results.get('read')}`",
                "",
                "Basis profile:",
                "",
                "```text",
            ]
        )
        for item in results.get("basis_profile", []):
            lines.append(
                f"degree={item['total_degree']} terms={item['terms']} "
                f"leading={item['leading_monomial']}"
            )
        lines.extend(["```", "", "Basis head:", "", "```text"])
        lines.extend(results.get("basis_head", []))
        lines.extend(["```", ""])

        if results.get("rationally_dead"):
            lines.extend(
                [
                    "## Read",
                    "",
                    "The regular-generic odd branch is dead over `QQ` by the recorded exact obstruction.",
                    "",
                    "Together with the prior `D0 = 0` denominator-locus check, this closes the normalized odd branch under the recorded exclusions.",
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    "## Read",
                    "",
                    "The regular-generic check did not close in this run.",
                    "",
                    "Do not promote a generic-branch theorem from this artifact; inspect the remaining ideal profile and split the next exact subbranch.",
                    "",
                ]
            )

    RESULT_MD.write_text("\n".join(lines))


def main():
    started = time.time()
    results = {
        "generated_at_unix": float(started),
        "route": "normalized odd branch regular generic",
        "branch_conditions": ["D0 != 0", "B != 0", "v != 0", "2P - B^2 != 0"],
        "solved_equations": "E6 = E7 = 0 for (A, P)",
        "numerators": [],
    }

    try:
        A, B, P, u, v = sp.symbols("A B P u v")
        report = source.odd_branch_unit_normalization_reduction()
        E6 = sp.expand(sp.sympify(report["normalized_equations"]["E6"]))
        E7 = sp.expand(sp.sympify(report["normalized_equations"]["E7"]))
        E10 = sp.expand(sp.sympify(report["normalized_equations"]["E10"]))
        E11 = sp.expand(sp.sympify(report["normalized_equations"]["E11"]))
        leading = sp.expand(-A**3 + B**2 * P - P**2)

        print("solving E6/E7 for A,P", flush=True)
        solved = sp.solve([sp.Eq(E6, 0), sp.Eq(E7, 0)], [A, P], dict=True, simplify=False)
        if len(solved) != 1:
            raise RuntimeError(f"expected one (A,P) solution, got {len(solved)}")
        sol = solved[0]
        A_expr = sp.factor(sp.together(sol[A]))
        P_expr = sp.factor(sp.together(sol[P]))
        results["A_denominator"] = sp.sstr(sp.factor(sp.denom(A_expr)))
        results["P_denominator"] = sp.sstr(sp.factor(sp.denom(P_expr)))

        substituted = []
        for name, expr in [("E11", E11), ("E10", E10), ("LEADING", leading)]:
            num = sp.factor(sp.fraction(sp.together(expr.subs({A: sol[A], P: sol[P]})))[0])
            poly = sp.Poly(sp.expand(num), u, v, B, domain="QQ")
            substituted.append((name, num))
            results["numerators"].append(
                {
                    "name": name,
                    "total_degree": int(sp.total_degree(num)),
                    "degree_u": int(poly.degree(u)),
                    "degree_v": int(poly.degree(v)),
                    "degree_B": int(poly.degree(B)),
                    "terms": int(len(poly.terms())),
                    "string_length": int(len(sp.sstr(num))),
                }
            )

        D0 = -131769 * B + 53361 * u + 44649 * v + 7958
        H = sp.factor(sp.fraction(sp.together(2 * sol[P] - B**2))[0])
        results["saturation_product"] = "D0 * B * v * numerator(2P - B^2)"
        results["D0"] = sp.sstr(D0)
        results["root_swap_fixed_numerator_degree"] = int(sp.total_degree(H))

        print("building Sage ring for unsaturated core", flush=True)
        R = PolynomialRing(QQ, ("u", "v", "B"), order="degrevlex")
        su, sv, sB = R.gens()
        locals_map = {"u": su, "v": sv, "B": sB}
        polys = []
        for name, num in substituted:
            poly = sympy_to_sage_poly(num, R, locals_map)
            print(f"{name}: degree={poly.total_degree()} terms={len(poly.monomials())}", flush=True)
            polys.append(poly)
        D0_poly = sympy_to_sage_poly(D0, R, locals_map)
        H_poly = sympy_to_sage_poly(H, R, locals_map)
        saturation = D0_poly * sB * sv * H_poly

        print("running unsaturated Groebner basis", flush=True)
        ideal = R.ideal(polys)
        basis = ideal.groebner_basis()
        contains_one = any(g == R(1) for g in basis)

        dimension = None
        degree = None
        try:
            dimension = int(ideal.dimension())
        except Exception as exc:
            dimension = f"error: {exc}"
        if dimension == 0:
            try:
                degree = int(ideal.vector_space_dimension())
            except Exception as exc:
                degree = f"error: {exc}"

        rationally_dead = bool(contains_one)
        rational_obstruction = "ideal contains 1" if contains_one else None
        lex_profile = None
        method = "unsaturated_core"

        if not rationally_dead and dimension == 0:
            print("running lex rational-root obstruction", flush=True)
            lex_profile = []
            for variable_order in [("u", "v", "B"), ("u", "B", "v"), ("v", "B", "u")]:
                S = PolynomialRing(QQ, variable_order, order="lex")
                loc = {str(gen): gen for gen in S.gens()}
                lex_polys = [sympy_to_sage_poly(num, S, loc) for _name, num in substituted]
                lex_basis = S.ideal(lex_polys).groebner_basis()
                univariate = []
                for g in lex_basis:
                    variables = [str(var) for var in g.variables()]
                    if len(variables) == 1:
                        upoly = g.univariate_polynomial()
                        roots = [str(root) for root, _mult in upoly.roots(QQ)]
                        univariate.append(
                            {
                                "variable": variables[0],
                                "degree": int(upoly.degree()),
                                "factor_degrees": [int(factor.degree()) for factor, _exp in upoly.factor()],
                                "rational_roots": roots[:16],
                                "polynomial_head": truncate(str(g)),
                            }
                        )
                lex_profile.append(
                    {
                        "variable_order": variable_order,
                        "basis_length": int(len(lex_basis)),
                        "univariate": univariate[:6],
                    }
                )
                for item in univariate:
                    if item["degree"] > 0 and not item["rational_roots"]:
                        rationally_dead = True
                        rational_obstruction = (
                            f"zero-dimensional lex basis has a univariate degree-{item['degree']} "
                            f"polynomial in {item['variable']} with no rational roots"
                        )
                        break
                if rationally_dead:
                    break

        if not rationally_dead and RUN_SATURATION:
            print("running optional saturated Groebner basis", flush=True)
            S = PolynomialRing(QQ, ("u", "v", "B", "W"), order="degrevlex")
            tu, tv, tB, W = S.gens()
            loc = {"u": tu, "v": tv, "B": tB}
            sat_polys = [sympy_to_sage_poly(num, S, loc) for _name, num in substituted]
            sat_D0 = sympy_to_sage_poly(D0, S, loc)
            sat_H = sympy_to_sage_poly(H, S, loc)
            sat_product = sat_D0 * tB * tv * sat_H
            sat_ideal = S.ideal(sat_polys + [S(1) - W * sat_product])
            basis = sat_ideal.groebner_basis()
            contains_one = any(g == S(1) for g in basis)
            method = "saturated_core"
            rationally_dead = bool(contains_one)
            rational_obstruction = "saturated ideal contains 1" if contains_one else rational_obstruction
            try:
                dimension = int(sat_ideal.dimension())
            except Exception as exc:
                dimension = f"error: {exc}"
            degree = None
            if dimension == 0:
                try:
                    degree = int(sat_ideal.vector_space_dimension())
                except Exception as exc:
                    degree = f"error: {exc}"

        results.update(
            {
                "method": method,
                "seconds": float(round(time.time() - started, 3)),
                "basis_length": int(len(basis)),
                "contains_one": bool(contains_one),
                "dimension": dimension,
                "degree": degree,
                "rationally_dead": bool(rationally_dead),
                "rational_obstruction": rational_obstruction,
                "lex_profile": lex_profile,
                "basis_profile": basis_profile(basis),
                "basis_head": [truncate(str(g)) for g in basis[:8]],
                "read": (
                    "regular-generic branch has no rational point over QQ"
                    if rationally_dead
                    else "regular-generic branch remains open after this run"
                ),
            }
        )
    except Exception as exc:
        results["error"] = repr(exc)
        print(f"ERROR: {exc}", flush=True)
    finally:
        write_artifacts(results)
        print(f"wrote {RESULT_JSON}", flush=True)
        print(f"wrote {RESULT_MD}", flush=True)
        if results.get("error"):
            raise SystemExit(1)
        print(
            "contains_one=",
            results.get("contains_one"),
            "rationally_dead=",
            results.get("rationally_dead"),
            "basis_length=",
            results.get("basis_length"),
            "seconds=",
            results.get("seconds"),
            flush=True,
        )


main()
