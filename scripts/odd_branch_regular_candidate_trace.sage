# Rational-candidate trace test for the D0- and B-saturated regular odd core.
#
# Run with:
#   HOME=/tmp SAGE_STARTUP_FILE=/tmp/empty.sage sage scripts/odd_branch_regular_candidate_trace.sage
#
# After D0 saturation the regular core is zero-dimensional of degree 176.
# Rather than converting directly to a large lex basis, this script computes
# characteristic polynomials for multiplication by rational coordinate functions
# on the finite quotient. If any such characteristic polynomial has no rational
# roots, the finite core has no rational point over QQ.

from sage.all import Matrix, PolynomialRing, QQ, sage_eval

import json
import sys
import time
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
RESULT_JSON = ROOT / "results" / "odd_branch_regular_candidate_trace.json"
RESULT_MD = ROOT / "results" / "odd_branch_regular_candidate_trace.md"
MAX_CHARS = 1600

sys.path.insert(0, str(ROOT / "scripts"))
import search_factor_pair_families as source


def trunc(text, limit=MAX_CHARS):
    return text if len(text) <= limit else text[:limit] + " ... [truncated]"


def sympy_to_sage_poly(expr, ring, locals_map):
    text = sp.sstr(sp.expand(expr)).replace("**", "^")
    return ring(sage_eval(text, locals=locals_map))


def monomial_exp(poly):
    items = list(poly.dict().items())
    if len(items) != 1:
        raise ValueError(f"expected monomial, got {poly}")
    exp, coeff = items[0]
    if coeff != 1:
        raise ValueError(f"expected monic monomial, got {poly}")
    return exp


def write_artifacts(results):
    RESULT_JSON.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")

    lines = [
        "# Odd Branch Regular Candidate Trace",
        "",
        "Route: rational-candidate inspection for the `D0`- and `B`-saturated regular odd core.",
        "",
        "Method: compute multiplication characteristic polynomials on the finite quotient.",
        "",
        "If a rational point exists, every rational coordinate function has a rational value at that point, hence a rational root in its multiplication characteristic polynomial. A characteristic polynomial with no rational roots is therefore an exact rational obstruction.",
        "",
        "## Core",
        "",
        f"- dimension: `{results.get('dimension')}`",
        f"- vector-space dimension: `{results.get('vector_space_dimension')}`",
        f"- basis length: `{results.get('basis_length')}`",
        f"- D0 saturation exponent: `{results.get('d0_saturation_exponent')}`",
        f"- B saturation exponent: `{results.get('b_saturation_exponent')}`",
        f"- seconds before traces: `{results.get('setup_seconds')}`",
        "",
        "## Trace Tests",
        "",
    ]
    for test in results.get("tests", []):
        lines.extend(
            [
                f"### `{test['name']}`",
                "",
                f"- seconds: `{test.get('seconds')}`",
                f"- degree: `{test.get('degree')}`",
                f"- rational roots: `{test.get('rational_roots')}`",
                f"- rationally dead: `{test.get('rationally_dead')}`",
                f"- polynomial head: `{test.get('polynomial_head')}`",
                "",
            ]
        )
    lines.extend(["## Read", "", results.get("read", "Run did not finish."), ""])
    RESULT_MD.write_text("\n".join(lines))


def build_saturated_core():
    A, B, P, u, v = sp.symbols("A B P u v")
    report = source.odd_branch_unit_normalization_reduction()
    E6 = sp.expand(sp.sympify(report["normalized_equations"]["E6"]))
    E7 = sp.expand(sp.sympify(report["normalized_equations"]["E7"]))
    E10 = sp.expand(sp.sympify(report["normalized_equations"]["E10"]))
    E11 = sp.expand(sp.sympify(report["normalized_equations"]["E11"]))
    leading = sp.expand(-A**3 + B**2 * P - P**2)

    sol = sp.solve([sp.Eq(E6, 0), sp.Eq(E7, 0)], [A, P], dict=True, simplify=False)[0]
    substituted = []
    for _name, expr in [("E11", E11), ("E10", E10), ("LEADING", leading)]:
        substituted.append(sp.factor(sp.fraction(sp.together(expr.subs({A: sol[A], P: sol[P]})))[0]))

    D0 = -131769 * B + 53361 * u + 44649 * v + 7958

    R = PolynomialRing(QQ, ("u", "v", "B"), order="degrevlex")
    su, sv, sB = R.gens()
    loc = {"u": su, "v": sv, "B": sB}
    polys = [sympy_to_sage_poly(num, R, loc) for num in substituted]
    D0_poly = sympy_to_sage_poly(D0, R, loc)

    ideal = R.ideal(polys)
    ideal, d0_exp = ideal.saturation(D0_poly)
    ideal, b_exp = ideal.saturation(sB)
    basis = ideal.groebner_basis()
    return R, ideal, basis, int(d0_exp), int(b_exp)


def multiplication_trace_test(name, linear_form, ideal, normal_basis, exp_to_index):
    started = time.time()
    R = ideal.ring()
    n = len(normal_basis)
    matrix = Matrix(QQ, n, n)
    for col, monomial in enumerate(normal_basis):
        reduced = ideal.reduce(linear_form * monomial)
        for exp, coeff in reduced.dict().items():
            row = exp_to_index.get(exp)
            if row is None:
                raise RuntimeError(f"reduced monomial {exp} not in normal basis")
            matrix[row, col] = coeff
    charpoly = matrix.charpoly("T")
    roots = [str(root) for root, _mult in charpoly.roots(QQ)]
    return {
        "name": name,
        "seconds": float(round(time.time() - started, 3)),
        "degree": int(charpoly.degree()),
        "rational_roots": roots[:32],
        "rationally_dead": not roots,
        "polynomial_head": trunc(str(charpoly)),
    }


def main():
    started = time.time()
    results = {
        "generated_at_unix": float(started),
        "route": "normalized odd branch regular D0/B saturated rational-candidate trace",
        "tests": [],
        "read": "Run started.",
    }
    write_artifacts(results)

    print("building D0/B-saturated finite core", flush=True)
    R, ideal, basis, d0_exp, b_exp = build_saturated_core()
    su, sv, sB = R.gens()
    normal_basis = ideal.normal_basis()
    exp_to_index = {monomial_exp(mon): idx for idx, mon in enumerate(normal_basis)}

    results.update(
        {
            "dimension": int(ideal.dimension()),
            "vector_space_dimension": int(ideal.vector_space_dimension()),
            "basis_length": int(len(basis)),
            "d0_saturation_exponent": d0_exp,
            "b_saturation_exponent": b_exp,
            "setup_seconds": float(round(time.time() - started, 3)),
        }
    )
    results["read"] = "Finite core built; trace tests pending."
    write_artifacts(results)
    print("finite core degree", results["vector_space_dimension"], flush=True)

    tests = [
        ("B", sB),
        ("v", sv),
        ("u", su),
        ("u + 2v + 3B", su + 2 * sv + 3 * sB),
    ]
    for name, linear_form in tests:
        print(f"trace test {name}", flush=True)
        test = multiplication_trace_test(name, linear_form, ideal, normal_basis, exp_to_index)
        results["tests"].append(test)
        if test["rationally_dead"]:
            results["read"] = (
                f"The D0- and B-saturated finite core has no rational point over QQ: "
                f"multiplication by {name} has a degree-{test['degree']} characteristic "
                "polynomial with no rational roots."
            )
            write_artifacts(results)
            print(results["read"], flush=True)
            return
        results["read"] = f"Trace test {name} left rational roots; continuing."
        write_artifacts(results)

    results["read"] = (
        "Trace tests did not close the finite core. Use the recorded rational roots "
        "to split candidate fibers and then apply v != 0 and 2P != B^2."
    )
    write_artifacts(results)


main()
