# Exact denominator-locus check for the normalized odd branch.
#
# Run with:
#   HOME=/tmp SAGE_STARTUP_FILE=/tmp/empty.sage sage scripts/odd_branch_denominator_locus.sage
#
# This script works on the D0 = 0 singular locus from DIOPHANTINE_LOG.md.
# It intentionally writes a small result artifact so later Rick threads do not
# have to reconstruct the collapsed Sage run from chat.

import json
import os
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT_JSON = ROOT / "results" / "odd_branch_denominator_locus.json"
RESULT_MD = ROOT / "results" / "odd_branch_denominator_locus.md"
MAX_BASIS_CHARS = 1200
CHECK_QQ_VARIETY = os.environ.get("DIOPHANTINE_CHECK_QQ_VARIETY") == "1"
CHECK_LEX = os.environ.get("DIOPHANTINE_CHECK_LEX", "1") == "1"

R = PolynomialRing(QQ, ("A", "P", "u", "v"), order="degrevlex")
A, P, u, v = R.gens()

B = QQ(53361) / QQ(131769) * u + QQ(44649) / QQ(131769) * v + QQ(7958) / QQ(131769)

E6 = (
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

E7 = -2 * (
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

E11 = 2 * (
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

LEADING = -A**3 + B**2 * P - P**2

L1 = 11737 * u + 6534 * v - 1107
C3 = (
    14962517399511 * u**3
    + 30463146452772 * u**2 * v
    + 2987415641628 * u**2
    + 28152853752672 * u * v**2
    - 1132236728172 * u * v
    + 509898643254 * u
    + 8317691482320 * v**3
    - 3715788290940 * v**2
    + 1607295770520 * v
    - 269513845340
)


def run_branch(name, generators):
    started = time.time()
    ideal = R.ideal([R(g) for g in generators])
    basis = ideal.groebner_basis()
    basis_strings = [str(g) for g in basis[:8]]
    basis_head = [
        text if len(text) <= MAX_BASIS_CHARS else text[:MAX_BASIS_CHARS] + " ... [truncated]"
        for text in basis_strings
    ]
    basis_profile = []
    for g in basis[:12]:
        basis_profile.append(
            {
                "total_degree": int(g.total_degree()),
                "leading_monomial": str(g.lm()),
            }
        )
    contains_one = any(g == R(1) for g in basis)
    rationally_dead = bool(contains_one)
    rational_obstruction = "ideal contains 1" if contains_one else None
    dimension = None
    degree = None
    rational_points = None
    rational_point_error = None
    lex_profile = None
    lex_error = None
    try:
        dimension = int(ideal.dimension())
    except Exception as exc:
        dimension = f"error: {exc}"
    if dimension == 0:
        try:
            degree = int(ideal.vector_space_dimension())
        except Exception as exc:
            degree = f"error: {exc}"
        if CHECK_QQ_VARIETY:
            try:
                rational_points_raw = ideal.variety(QQ)
                rational_points = [
                    {str(key): str(value) for key, value in point.items()}
                    for point in rational_points_raw[:8]
                ]
            except Exception as exc:
                rational_point_error = str(exc)
        else:
            rational_point_error = "skipped; set DIOPHANTINE_CHECK_QQ_VARIETY=1 to run this slower check"
        if CHECK_LEX:
            try:
                S = PolynomialRing(QQ, ("A", "P", "u", "v"), order="lex")
                S_polys = [S(g) for g in generators]
                lex_basis = S.ideal(S_polys).groebner_basis()
                univariate = []
                for g in lex_basis:
                    variables = [str(var) for var in g.variables()]
                    if variables == ["v"]:
                        upoly = g.univariate_polynomial()
                        factor_degrees = [int(factor.degree()) for factor, _exp in upoly.factor()]
                        rational_roots = [str(root) for root, _mult in upoly.roots(QQ)]
                        text = str(g)
                        univariate.append(
                            {
                                "degree": int(upoly.degree()),
                                "factor_degrees": factor_degrees,
                                "rational_roots": rational_roots[:12],
                                "polynomial_head": text if len(text) <= MAX_BASIS_CHARS else text[:MAX_BASIS_CHARS] + " ... [truncated]",
                            }
                        )
                lex_profile = {
                    "basis_length": int(len(lex_basis)),
                    "univariate_in_v": univariate[:4],
                }
                if univariate and all(not item["rational_roots"] for item in univariate):
                    rationally_dead = True
                    rational_obstruction = (
                        "zero-dimensional lex basis contains a univariate polynomial in v with no rational roots"
                    )
            except Exception as exc:
                lex_error = str(exc)
    return {
        "name": name,
        "seconds": float(round(time.time() - started, 3)),
        "basis_length": int(len(basis)),
        "contains_one": bool(contains_one),
        "dimension": dimension,
        "degree": degree,
        "rationally_dead": bool(rationally_dead),
        "rational_obstruction": rational_obstruction,
        "rational_points": rational_points,
        "rational_point_error": rational_point_error,
        "lex_profile": lex_profile,
        "lex_error": lex_error,
        "basis_profile": basis_profile,
        "basis_head": basis_head,
    }


results = {
    "generated_at_unix": float(time.time()),
    "route": "normalized odd branch denominator locus D0 = 0",
    "D0": "-131769*B + 53361*u + 44649*v + 7958",
    "B_substitution": "B = (53361*u + 44649*v + 7958) / 131769",
    "branches": [],
}

results["branches"].append(
    run_branch("linear_compatibility_branch", [L1, E6, E7, E11, LEADING])
)
results["branches"].append(
    run_branch("cubic_compatibility_branch", [C3, E6, E7, E11, LEADING])
)

RESULT_JSON.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")

lines = [
    "# Odd Branch Denominator Locus",
    "",
    "Route: normalized odd branch, singular denominator locus `D0 = 0`.",
    "",
    "`D0 = -131769 B + 53361 u + 44649 v + 7958`",
    "",
    "After substituting `B = (53361 u + 44649 v + 7958) / 131769`, the compatibility split is checked on:",
    "",
    "- linear branch: `11737 u + 6534 v - 1107 = 0`",
    "- cubic branch: the `C3(u,v) = 0` compatibility factor recorded in `scripts/odd_branch_denominator_locus.sage`",
    "",
    "## Results",
    "",
]
for branch in results["branches"]:
    lines.extend(
        [
            f"### {branch['name']}",
            "",
            f"- seconds: `{branch['seconds']}`",
            f"- Groebner basis length: `{branch['basis_length']}`",
            f"- contains `1`: `{branch['contains_one']}`",
            f"- dimension: `{branch['dimension']}`",
            f"- degree / vector-space dimension: `{branch['degree']}`",
            f"- rationally dead: `{branch['rationally_dead']}`",
            f"- rational obstruction: `{branch['rational_obstruction']}`",
            f"- rational points over `QQ` (first 8): `{branch['rational_points']}`",
            f"- rational point error: `{branch['rational_point_error']}`",
            f"- lex profile: `{branch['lex_profile']}`",
            f"- lex error: `{branch['lex_error']}`",
            "",
            "Basis profile:",
            "",
            "```text",
            *[
                f"degree={item['total_degree']} leading={item['leading_monomial']}"
                for item in branch["basis_profile"]
            ],
            "```",
            "",
            "Basis head:",
            "",
            "```text",
            *branch["basis_head"],
            "```",
            "",
        ]
    )

if all(branch["rationally_dead"] for branch in results["branches"]):
    lines.extend(
        [
            "## Read",
            "",
            "Both compatibility branches on `D0 = 0` are dead over `QQ`.",
            "",
            "The linear branch contains `1`. The cubic branch is zero-dimensional of degree `45`; its lex basis contains a univariate degree-45 polynomial in `v` with no rational roots, so it has no rational point.",
            "",
            "This clears the denominator-locus branch. The next gate is the regular generic odd branch `D0 != 0`, `B != 0`, `v != 0`, `2P != B^2`.",
            "",
        ]
    )
else:
    open_branches = ", ".join(branch["name"] for branch in results["branches"] if not branch["contains_one"])
    lines.extend(
        [
            "## Read",
            "",
            f"The denominator-locus check is not fully closed. Open branch(es): `{open_branches}`.",
            "",
            "Do not promote a denominator-locus theorem until every branch contains `1` or has a separate exact obstruction.",
            "",
        ]
    )

RESULT_MD.write_text("\n".join(lines))
print(f"wrote {RESULT_JSON}")
print(f"wrote {RESULT_MD}")
for branch in results["branches"]:
    print(branch["name"], "contains_one=", branch["contains_one"], "basis_length=", branch["basis_length"], "seconds=", branch["seconds"])
