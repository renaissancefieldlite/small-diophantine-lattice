# Exact D0-saturation check for the regular normalized odd branch.
#
# Run with:
#   HOME=/tmp SAGE_STARTUP_FILE=/tmp/empty.sage sage scripts/odd_branch_regular_d0_saturation.sage
#
# This follows the regular-generic reduction after solving E6 = E7 = 0 for
# (A, P). The unsaturated three-equation core is one-dimensional. Saturating by
# the solved-system denominator D0 is the next exact gate, because the singular
# D0 = 0 locus has already been cleared separately.

from sage.all import PolynomialRing, QQ, sage_eval

import json
import os
import sys
import time
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
RESULT_JSON = ROOT / "results" / "odd_branch_regular_d0_saturation.json"
RESULT_MD = ROOT / "results" / "odd_branch_regular_d0_saturation.md"
MAX_CHARS = 1400
RUN_LEX = os.environ.get("DIOPHANTINE_RUN_LEX") == "1"

sys.path.insert(0, str(ROOT / "scripts"))
import search_factor_pair_families as source


def trunc(text, limit=MAX_CHARS):
    return text if len(text) <= limit else text[:limit] + " ... [truncated]"


def sympy_to_sage_poly(expr, ring, locals_map):
    text = sp.sstr(sp.expand(expr)).replace("**", "^")
    return ring(sage_eval(text, locals=locals_map))


def sage_to_sage_poly(poly, ring, locals_map):
    return ring(sage_eval(str(poly), locals=locals_map))


def profile_basis(basis, limit=12):
    return [
        {
            "total_degree": int(g.total_degree()),
            "terms": int(len(g.monomials())),
            "leading_monomial": str(g.lm()),
        }
        for g in basis[:limit]
    ]


def lex_rational_obstruction(sat_basis):
    runs = []
    for variable_order in [("u", "v", "B"), ("u", "B", "v"), ("v", "B", "u")]:
        print(f"lex order {variable_order}", flush=True)
        S = PolynomialRing(QQ, variable_order, order="lex")
        loc = {str(gen): gen for gen in S.gens()}
        lex_generators = [sage_to_sage_poly(g, S, loc) for g in sat_basis]
        lex_basis = S.ideal(lex_generators).groebner_basis()
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
                        "polynomial_head": trunc(str(g)),
                    }
                )
        run = {
            "variable_order": variable_order,
            "basis_length": int(len(lex_basis)),
            "univariate": univariate[:8],
        }
        runs.append(run)
        for item in univariate:
            if item["degree"] > 0 and not item["rational_roots"]:
                return {
                    "rationally_dead": True,
                    "rational_obstruction": (
                        f"zero-dimensional D0-saturated lex basis has a "
                        f"univariate degree-{item['degree']} polynomial in "
                        f"{item['variable']} with no rational roots"
                    ),
                    "lex_profile": runs,
                }
    return {
        "rationally_dead": False,
        "rational_obstruction": None,
        "lex_profile": runs,
    }


def write_artifacts(results):
    RESULT_JSON.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")

    lines = [
        "# Odd Branch Regular D0 Saturation",
        "",
        "Route: normalized odd branch, regular core after solving `E6 = E7 = 0` for `(A, P)`.",
        "",
        "This run saturates by:",
        "",
        "`D0 = -131769 B + 53361 u + 44649 v + 7958`",
        "",
        "The `D0 = 0` singular locus is checked separately in `results/odd_branch_denominator_locus.md`.",
        "",
        "## Core",
        "",
        f"- base dimension: `{results.get('base_dimension')}`",
        f"- base Groebner basis length: `{results.get('base_basis_length')}`",
        f"- D0 saturation exponent: `{results.get('d0_saturation_exponent')}`",
        f"- saturated dimension: `{results.get('saturated_dimension')}`",
        f"- saturated degree / vector-space dimension: `{results.get('saturated_degree')}`",
        f"- saturated Groebner basis length: `{results.get('saturated_basis_length')}`",
        f"- contains `1`: `{results.get('contains_one')}`",
        f"- rationally dead: `{results.get('rationally_dead')}`",
        f"- rational obstruction: `{results.get('rational_obstruction')}`",
        f"- seconds: `{results.get('seconds')}`",
        "",
        "## Lex Profile",
        "",
        "```text",
        trunc(str(results.get("lex_profile"))),
        "```",
        "",
        "## Saturated Basis Profile",
        "",
        "```text",
    ]
    for item in results.get("saturated_basis_profile", []):
        lines.append(
            f"degree={item['total_degree']} terms={item['terms']} "
            f"leading={item['leading_monomial']}"
        )
    lines.extend(["```", "", "## Read", ""])
    if results.get("rationally_dead"):
        lines.extend(
            [
                "The D0-saturated regular core has no rational point over `QQ`.",
                "",
                "Because this check does not impose `B != 0`, `v != 0`, or `2P != B^2`, it is stronger than the remaining regular-generic exclusions.",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "The D0-saturated regular core did not close over `QQ` in this run.",
                "",
                "The next exact split is to inspect the zero-dimensional saturated ideal for rational candidates and then apply the remaining exclusions `B`, `v`, and `2P - B^2`.",
                "",
            ]
        )
    RESULT_MD.write_text("\n".join(lines))


def main():
    started = time.time()
    results = {
        "generated_at_unix": float(started),
        "route": "normalized odd branch regular D0 saturation",
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
        sol = sp.solve([sp.Eq(E6, 0), sp.Eq(E7, 0)], [A, P], dict=True, simplify=False)[0]
        substituted = []
        for name, expr in [("E11", E11), ("E10", E10), ("LEADING", leading)]:
            num = sp.factor(sp.fraction(sp.together(expr.subs({A: sol[A], P: sol[P]})))[0])
            substituted.append((name, num))

        D0 = -131769 * B + 53361 * u + 44649 * v + 7958
        R = PolynomialRing(QQ, ("u", "v", "B"), order="degrevlex")
        su, sv, sB = R.gens()
        loc = {"u": su, "v": sv, "B": sB}
        polys = [sympy_to_sage_poly(num, R, loc) for _name, num in substituted]
        D0_poly = sympy_to_sage_poly(D0, R, loc)

        print("base Groebner", flush=True)
        base = R.ideal(polys)
        base_basis = base.groebner_basis()
        results["base_dimension"] = int(base.dimension())
        results["base_basis_length"] = int(len(base_basis))

        print("saturating by D0", flush=True)
        saturated, exponent = base.saturation(D0_poly)
        sat_basis = saturated.groebner_basis()
        contains_one = any(g == R(1) for g in sat_basis)
        results["d0_saturation_exponent"] = int(exponent)
        results["saturated_dimension"] = int(saturated.dimension())
        results["saturated_basis_length"] = int(len(sat_basis))
        results["contains_one"] = bool(contains_one)
        results["saturated_basis_profile"] = profile_basis(sat_basis)
        try:
            results["saturated_degree"] = int(saturated.vector_space_dimension())
        except Exception as exc:
            results["saturated_degree"] = f"error: {exc}"

        results["rationally_dead"] = bool(contains_one)
        results["rational_obstruction"] = "D0-saturated ideal contains 1" if contains_one else None
        results["lex_profile"] = None
        if not contains_one and results["saturated_dimension"] == 0 and RUN_LEX:
            lex_result = lex_rational_obstruction(sat_basis)
            results.update(lex_result)

        results["seconds"] = float(round(time.time() - started, 3))
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
            "rationally_dead=",
            results.get("rationally_dead"),
            "obstruction=",
            results.get("rational_obstruction"),
            "seconds=",
            results.get("seconds"),
            flush=True,
        )


main()
