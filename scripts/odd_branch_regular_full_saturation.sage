# Staged full-exclusion saturation for the regular normalized odd branch.
#
# Run with:
#   HOME=/tmp SAGE_STARTUP_FILE=/tmp/empty.sage sage scripts/odd_branch_regular_full_saturation.sage
#
# This is staged on purpose. It writes after every saturation step so a heavy
# later exclusion does not erase the exact earlier rung.

from sage.all import PolynomialRing, QQ, sage_eval

import json
import sys
import time
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
RESULT_JSON = ROOT / "results" / "odd_branch_regular_full_saturation.json"
RESULT_MD = ROOT / "results" / "odd_branch_regular_full_saturation.md"

sys.path.insert(0, str(ROOT / "scripts"))
import search_factor_pair_families as source


def sympy_to_sage_poly(expr, ring, locals_map):
    text = sp.sstr(sp.expand(expr)).replace("**", "^")
    return ring(sage_eval(text, locals=locals_map))


def summarize_ideal(name, ideal, basis=None, exponent=None, seconds=None):
    if basis is None:
        basis = ideal.groebner_basis()
    contains_one = any(g == ideal.ring()(1) for g in basis)
    try:
        dimension = int(ideal.dimension())
    except Exception as exc:
        dimension = f"error: {exc}"
    degree = None
    if dimension == 0:
        try:
            degree = int(ideal.vector_space_dimension())
        except Exception as exc:
            degree = f"error: {exc}"
    return {
        "name": name,
        "exponent": None if exponent is None else int(exponent),
        "seconds": None if seconds is None else float(round(seconds, 3)),
        "basis_length": int(len(basis)),
        "contains_one": bool(contains_one),
        "dimension": dimension,
        "degree": degree,
        "basis_profile": [
            {
                "total_degree": int(g.total_degree()),
                "terms": int(len(g.monomials())),
                "leading_monomial": str(g.lm()),
            }
            for g in basis[:10]
        ],
    }


def write_artifacts(results):
    RESULT_JSON.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")

    lines = [
        "# Odd Branch Regular Full Saturation",
        "",
        "Route: regular normalized odd branch after solving `E6 = E7 = 0` for `(A, P)`.",
        "",
        "Saturation order:",
        "",
        "1. `D0`",
        "2. `B`",
        "3. `v`",
        "4. `H = numerator(2P - B^2)`",
        "",
        "`D0 = -131769 B + 53361 u + 44649 v + 7958`",
        "",
        "## Steps",
        "",
    ]
    for step in results.get("steps", []):
        lines.extend(
            [
                f"### {step['name']}",
                "",
                f"- exponent: `{step['exponent']}`",
                f"- seconds: `{step['seconds']}`",
                f"- basis length: `{step['basis_length']}`",
                f"- contains `1`: `{step['contains_one']}`",
                f"- dimension: `{step['dimension']}`",
                f"- degree / vector-space dimension: `{step['degree']}`",
                "",
                "Basis profile:",
                "",
                "```text",
            ]
        )
        for item in step["basis_profile"]:
            lines.append(
                f"degree={item['total_degree']} terms={item['terms']} "
                f"leading={item['leading_monomial']}"
            )
        lines.extend(["```", ""])
    lines.extend(
        [
            "## Read",
            "",
            results.get("read", "Run still in progress or no final read recorded."),
            "",
        ]
    )
    RESULT_MD.write_text("\n".join(lines))


def main():
    started = time.time()
    results = {
        "generated_at_unix": float(started),
        "route": "normalized odd branch regular full saturation",
        "steps": [],
        "read": "Run started.",
    }
    write_artifacts(results)

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
        substituted.append((name, sp.factor(sp.fraction(sp.together(expr.subs({A: sol[A], P: sol[P]})))[0])))

    D0 = -131769 * B + 53361 * u + 44649 * v + 7958
    H = sp.factor(sp.fraction(sp.together(2 * sol[P] - B**2))[0])

    R = PolynomialRing(QQ, ("u", "v", "B"), order="degrevlex")
    su, sv, sB = R.gens()
    loc = {"u": su, "v": sv, "B": sB}
    polys = [sympy_to_sage_poly(num, R, loc) for _name, num in substituted]
    factors = [
        ("D0", sympy_to_sage_poly(D0, R, loc)),
        ("B", sB),
        ("v", sv),
        ("H", sympy_to_sage_poly(H, R, loc)),
    ]

    ideal = R.ideal(polys)
    base_basis = ideal.groebner_basis()
    results["steps"].append(summarize_ideal("base", ideal, base_basis, seconds=time.time() - started))
    results["read"] = "Base core recorded."
    write_artifacts(results)
    print("base recorded", flush=True)

    for name, factor in factors:
        step_started = time.time()
        print(f"saturating by {name}", flush=True)
        ideal, exponent = ideal.saturation(factor)
        basis = ideal.groebner_basis()
        step = summarize_ideal(name, ideal, basis, exponent, time.time() - step_started)
        results["steps"].append(step)
        if step["contains_one"]:
            results["read"] = f"After saturating by {name}, the regular branch ideal contains 1."
            write_artifacts(results)
            print(results["read"], flush=True)
            return
        results["read"] = f"Completed saturation by {name}; branch not closed yet."
        write_artifacts(results)
        print(
            f"after {name}: exponent={step['exponent']} dim={step['dimension']} "
            f"degree={step['degree']} basis={step['basis_length']}",
            flush=True,
        )

    results["read"] = (
        "All regular exclusions were saturated without producing 1. "
        "The next gate is rational-candidate inspection of the final zero-dimensional ideal."
    )
    write_artifacts(results)


main()
