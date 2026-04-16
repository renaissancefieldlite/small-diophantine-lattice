#!/usr/bin/env python3
"""Local browser control panel for the background search."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import webbrowser
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.parse import parse_qs, urlparse
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
RESULTS_DIR = ROOT / "results" / "primitive_queue_sections"
LOGS_DIR = RESULTS_DIR / "logs"
SECTION_RUNNER = SCRIPTS_DIR / "run_primitive_queue_section.py"
AUTOPILOT_RUNNER = SCRIPTS_DIR / "run_backup_autopilot.py"
AUTOPILOT_STATUS_PATH = ROOT / "results" / "backup_autopilot_status.json"
AUTOPILOT_LOG_PATH = ROOT / "results" / "backup_autopilot.log"
FACTOR_PAIR_STATE_PATH = ROOT / "results" / "factor_pair_full_minus2_search.json"
PORTFOLIO_STATE_PATH = ROOT / "results" / "portfolio_full_minus2.json"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import search_factor_pair_families as factor_pair  # noqa: E402


JOBS: dict[str, dict[str, Any]] = {}
AUTOPILOT: dict[str, Any] | None = None

STAGE_ORDER = [
    ("shifted_linear_linear_linear", "Seed-Shifted Linear Family"),
    ("shifted_quadratic_linear_cubic", "Quadratic / Linear / Cubic Family"),
    ("shifted_even_quartic_cubic_sextic", "Even Quartic / Cubic / Sextic Family"),
    ("general_quartic_cubic_sextic_reduction", "General Reduced Core"),
    ("general_b1_zero_leading_surface_reduction", "Universal b1 = 0 Reduction"),
    ("weighted_scaling_reduction", "Scaling Reduction"),
    ("t_sign_symmetry_reduction", "t -> -t Symmetry Reduction"),
    ("root_swap_symmetry_reduction", "Root-Swap Reduction"),
    ("odd_branch_unit_normalization_reduction", "Odd-Branch Normalization"),
]


def sanitize_label(label: str) -> str:
    safe = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in label.strip())
    return safe.strip("_") or "section_run"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def read_tail(path: Path, line_count: int = 12) -> str:
    if not path.exists():
        return ""
    lines = path.read_text().splitlines()
    return "\n".join(lines[-line_count:])


def summary_files() -> list[Path]:
    if not RESULTS_DIR.exists():
        return []
    files = [path for path in RESULTS_DIR.glob("*.json") if path.is_file()]
    return sorted(files, key=lambda path: path.stat().st_mtime, reverse=True)


def processed_section_points() -> set[tuple[int, int, int]]:
    rows: set[tuple[int, int, int]] = set()
    if not RESULTS_DIR.exists():
        return rows
    for path in RESULTS_DIR.glob("*.jsonl"):
        for line in path.read_text().splitlines():
            if not line.strip():
                continue
            payload = json.loads(line)
            point = payload.get("leading_point")
            if point:
                rows.add(tuple(int(value) for value in point))
    return rows


def build_queue_status(section_count: int) -> dict[str, Any]:
    queue = factor_pair.primitive_leading_surface_representatives()
    known_dead = factor_pair.known_dead_leading_points() | processed_section_points()
    unresolved = [point for point in queue if point not in known_dead]

    sections = []
    for section_index in range(1, section_count + 1):
        rows = factor_pair.contiguous_section_rows(queue, section_index, section_count)
        unresolved_rows = [point for point in rows if point not in known_dead]
        sections.append(
            {
                "section_index": section_index,
                "section_count": section_count,
                "size": len(rows),
                "known_dead": len(rows) - len(unresolved_rows),
                "remaining": len(unresolved_rows),
                "next_unresolved": list(unresolved_rows[0]) if unresolved_rows else None,
            }
        )

    return {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "queue_size": len(queue),
        "known_dead_count": len(known_dead),
        "remaining_count": len(unresolved),
        "next_unresolved": list(unresolved[0]) if unresolved else None,
        "section_count": section_count,
        "sections": sections,
    }


def serialize_summary(path: Path) -> dict[str, Any]:
    payload = read_json(path)
    payload["_file_name"] = path.name
    payload["_modified_at"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(path.stat().st_mtime))
    return payload


def template_detail(row: dict[str, Any]) -> str:
    proof = row.get("proof_summary")
    if isinstance(proof, list) and proof:
        return proof[0]
    if isinstance(proof, str) and proof:
        return proof
    next_action = row.get("next_action")
    if isinstance(next_action, str) and next_action:
        return next_action
    return row.get("result", "recorded")


def build_live_state() -> dict[str, Any]:
    portfolio = read_json(PORTFOLIO_STATE_PATH) if PORTFOLIO_STATE_PATH.exists() else {}
    factor_state = read_json(FACTOR_PAIR_STATE_PATH) if FACTOR_PAIR_STATE_PATH.exists() else {}
    queue_state = build_queue_status(4)
    autopilot = serialize_autopilot()
    autopilot_state = autopilot.get("state") or {}

    templates = factor_state.get("templates", [])
    templates_by_slug = {row.get("slug"): row for row in templates if row.get("slug")}
    no_go_templates = [row for row in templates if row.get("result") == "no_go"]
    symbolic_templates = [row for row in templates if row.get("result") == "symbolic_reduction"]
    branch_kills = [row for row in no_go_templates if str(row.get("slug", "")).startswith("branch_lead_")]

    evolution = []
    for slug, title in STAGE_ORDER:
        row = templates_by_slug.get(slug)
        if not row:
            continue
        evolution.append(
            {
                "slug": slug,
                "title": title,
                "result": row.get("result", "recorded"),
                "detail": template_detail(row),
            }
        )

    directions: list[str] = []
    for text in [
        factor_state.get("next_action"),
        templates_by_slug.get("odd_branch_unit_normalization_reduction", {}).get("next_action"),
        templates_by_slug.get("general_b1_zero_leading_surface_reduction", {}).get("next_action"),
    ]:
        if isinstance(text, str) and text and text not in directions:
            directions.append(text)

    recent_outcomes: list[dict[str, Any]] = []
    seen_points: set[tuple[int, int, int]] = set()
    for row in autopilot_state.get("cycle_results", []):
        point = tuple(int(value) for value in row.get("leading_point", [])) if row.get("leading_point") else None
        if point and point not in seen_points:
            recent_outcomes.append(
                {
                    "generated_at": row.get("generated_at"),
                    "leading_point": list(point),
                    "result": row.get("result", "recorded"),
                    "summary": row.get("proof_summary", []),
                }
            )
            seen_points.add(point)

    for path in summary_files():
        payload = serialize_summary(path)
        for row in reversed(payload.get("recent_results", [])):
            point = tuple(int(value) for value in row.get("leading_point", [])) if row.get("leading_point") else None
            if not point or point in seen_points:
                continue
            recent_outcomes.append(
                {
                    "generated_at": row.get("generated_at") or payload.get("generated_at"),
                    "leading_point": list(point),
                    "result": row.get("result", "recorded"),
                    "summary": row.get("proof_summary", []),
                }
            )
            seen_points.add(point)
            if len(recent_outcomes) >= 8:
                break
        if len(recent_outcomes) >= 8:
            break

    current_stage = {
        "title": "Reduced-Core Odd Frontier",
        "summary": (
            "The live frontier is the asymmetric unit-normalized odd surface "
            "b1 = 1 with 2 P != B^2, while the b1 = 0 side still wants a global "
            "proof that the square obstruction never hits."
        ),
        "counts": {
            "template_no_go_count": len(no_go_templates),
            "symbolic_reduction_count": len(symbolic_templates),
            "exact_branch_kill_count": len(branch_kills) + queue_state["known_dead_count"],
        },
    }

    equation = factor_state.get("equation") or portfolio.get("equation") or {}
    seed = portfolio.get("seed") or portfolio.get("overview", {}).get("chosen_seed") or {}
    factor_formulation = factor_state.get("factor_pair_formulation", {})

    return {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "equation": {
            "slug": equation.get("slug") or portfolio.get("overview", {}).get("equation_slug"),
            "display": equation.get("equation"),
            "seed": [seed.get("x"), seed.get("y"), seed.get("z")],
            "factor_formulation": factor_formulation,
        },
        "frontier": {
            "autopilot_status": autopilot.get("status"),
            "remaining_count": queue_state["remaining_count"],
            "next_unresolved": queue_state["next_unresolved"],
            "cycle_index": autopilot_state.get("cycle_index"),
        },
        "current_stage": current_stage,
        "evolution": evolution,
        "directions": directions,
        "recent_outcomes": recent_outcomes,
    }


def poll_jobs() -> None:
    for job in JOBS.values():
        process: subprocess.Popen[str] = job["process"]
        job["returncode"] = process.poll()


def mark_autopilot_stopped_state() -> None:
    state = read_json(AUTOPILOT_STATUS_PATH) if AUTOPILOT_STATUS_PATH.exists() else {}
    state["generated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    state["status"] = "stopped"
    AUTOPILOT_STATUS_PATH.write_text(json.dumps(state, indent=2))


def poll_autopilot() -> None:
    global AUTOPILOT
    if AUTOPILOT is None:
        return
    AUTOPILOT["returncode"] = AUTOPILOT["process"].poll()
    if AUTOPILOT["returncode"] is not None:
        if AUTOPILOT.get("stop_requested"):
            AUTOPILOT["status"] = "stopped"
            mark_autopilot_stopped_state()
        else:
            AUTOPILOT["status"] = f"exited ({AUTOPILOT['returncode']})"


def serialize_job(job: dict[str, Any]) -> dict[str, Any]:
    return {
        "label": job["label"],
        "pid": job["process"].pid,
        "started_at": job["started_at"],
        "status": "running" if job["returncode"] is None else f"exited ({job['returncode']})",
        "section_index": job["section_index"],
        "section_count": job["section_count"],
        "limit": job["limit"],
        "log_path": str(job["log_path"]),
        "summary_path": str(job["summary_path"]),
        "log_tail": read_tail(job["log_path"]),
    }


def serialize_autopilot() -> dict[str, Any]:
    poll_autopilot()
    state = read_json(AUTOPILOT_STATUS_PATH) if AUTOPILOT_STATUS_PATH.exists() else None
    if AUTOPILOT is None and state and state.get("status") == "running":
        state["generated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        state["status"] = "stopped"
        AUTOPILOT_STATUS_PATH.write_text(json.dumps(state, indent=2))
    payload = {
        "status": "stopped",
        "pid": None,
        "started_at": None,
        "log_path": str(AUTOPILOT_LOG_PATH),
        "status_path": str(AUTOPILOT_STATUS_PATH),
        "log_tail": read_tail(AUTOPILOT_LOG_PATH),
        "state": read_json(AUTOPILOT_STATUS_PATH) if AUTOPILOT_STATUS_PATH.exists() else None,
    }
    if AUTOPILOT is None:
        return payload
    payload.update(
        {
            "status": AUTOPILOT.get("status", "running"),
            "pid": AUTOPILOT["process"].pid,
            "started_at": AUTOPILOT["started_at"],
            "log_tail": read_tail(AUTOPILOT_LOG_PATH),
            "state": read_json(AUTOPILOT_STATUS_PATH) if AUTOPILOT_STATUS_PATH.exists() else None,
        }
    )
    return payload


def control_server_is_healthy(host: str, port: int) -> bool:
    url = f"http://{host}:{port}/api/queue-status?section_count=4"
    try:
        with urlopen(url, timeout=0.75) as response:
            payload = json.loads(response.read().decode())
    except (URLError, TimeoutError, json.JSONDecodeError, OSError):
        return False
    return isinstance(payload, dict) and "queue_size" in payload and "sections" in payload


def next_usable_port(host: str, start_port: int, search_span: int = 24) -> tuple[int, bool]:
    for port in range(start_port, start_port + search_span):
        if control_server_is_healthy(host, port):
            return port, True
        try:
            probe = ThreadingHTTPServer((host, port), ControlHandler)
        except OSError as exc:
            if exc.errno == 48:
                continue
            raise
        probe.server_close()
        return port, False
    raise OSError(f"no usable port found in range {start_port}-{start_port + search_span - 1}")


def launch_section_job(payload: dict[str, Any]) -> dict[str, Any]:
    section_index = int(payload.get("section_index", 1))
    section_count = int(payload.get("section_count", 1))
    limit = int(payload.get("limit", 1))
    label = sanitize_label(payload.get("label") or f"section_{section_index}_of_{section_count}")
    reset_output = bool(payload.get("reset_output", False))
    include_known = bool(payload.get("include_known", False))
    a4_bound = int(payload.get("a4_bound", 1200))
    b3_bound = int(payload.get("b3_bound", 500))

    existing = JOBS.get(label)
    if existing and existing["returncode"] is None:
        raise ValueError(f"job '{label}' is already running")

    jsonl_path, summary_path = (
        RESULTS_DIR / f"{label}.jsonl",
        RESULTS_DIR / f"{label}.json",
    )
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOGS_DIR / f"{label}.log"

    cmd = [
        sys.executable,
        str(SECTION_RUNNER),
        "--section-index",
        str(section_index),
        "--section-count",
        str(section_count),
        "--limit",
        str(limit),
        "--label",
        label,
        "--a4-bound",
        str(a4_bound),
        "--b3-bound",
        str(b3_bound),
        "--emit-jsonl",
        str(jsonl_path),
        "--emit-summary",
        str(summary_path),
    ]
    if reset_output:
        cmd.append("--reset-output")
    if include_known:
        cmd.append("--include-known")

    log_handle = log_path.open("a")
    process = subprocess.Popen(
        cmd,
        cwd=str(ROOT),
        stdout=log_handle,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
    )
    log_handle.close()

    JOBS[label] = {
        "label": label,
        "process": process,
        "section_index": section_index,
        "section_count": section_count,
        "limit": limit,
        "log_path": log_path,
        "summary_path": summary_path,
        "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "returncode": None,
    }
    return serialize_job(JOBS[label])


def start_autopilot() -> dict[str, Any]:
    global AUTOPILOT
    poll_autopilot()
    if AUTOPILOT is not None and AUTOPILOT["returncode"] is None:
        raise ValueError("background search is already running")

    log_handle = AUTOPILOT_LOG_PATH.open("a")
    process = subprocess.Popen(
        [sys.executable, str(AUTOPILOT_RUNNER)],
        cwd=str(ROOT),
        stdout=log_handle,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
    )
    log_handle.close()
    AUTOPILOT = {
        "process": process,
        "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "returncode": None,
        "status": "running",
        "stop_requested": False,
    }
    return serialize_autopilot()


def stop_autopilot() -> dict[str, Any]:
    global AUTOPILOT
    poll_autopilot()
    if AUTOPILOT is None or AUTOPILOT["returncode"] is not None:
        return serialize_autopilot()
    AUTOPILOT["stop_requested"] = True
    AUTOPILOT["process"].terminate()
    try:
        AUTOPILOT["process"].wait(timeout=5)
    except subprocess.TimeoutExpired:
        AUTOPILOT["process"].kill()
        AUTOPILOT["process"].wait(timeout=5)
    AUTOPILOT["returncode"] = AUTOPILOT["process"].returncode
    AUTOPILOT["status"] = "stopped"
    mark_autopilot_stopped_state()
    return serialize_autopilot()


class ControlHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def send_json(self, payload: Any, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, indent=2).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self.send_response(HTTPStatus.FOUND)
            self.send_header("Location", "/dashboard/index.html")
            self.end_headers()
            return
        if parsed.path == "/api/queue-status":
            section_count = int(parse_qs(parsed.query).get("section_count", ["4"])[0])
            self.send_json(build_queue_status(section_count))
            return
        if parsed.path == "/api/jobs":
            poll_jobs()
            payload = {
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "jobs": [serialize_job(job) for job in JOBS.values()],
            }
            self.send_json(payload)
            return
        if parsed.path == "/api/section-summaries":
            payload = {
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "summaries": [serialize_summary(path) for path in summary_files()],
            }
            self.send_json(payload)
            return
        if parsed.path == "/api/autopilot-status":
            self.send_json(serialize_autopilot())
            return
        if parsed.path == "/api/live-state":
            self.send_json(build_live_state())
            return
        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", "0"))
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
            if parsed.path == "/api/run-section":
                job = launch_section_job(payload)
                self.send_json({"ok": True, "job": job}, status=HTTPStatus.CREATED)
                return
            if parsed.path == "/api/autopilot-start":
                autopilot = start_autopilot()
                self.send_json({"ok": True, "autopilot": autopilot}, status=HTTPStatus.CREATED)
                return
            if parsed.path == "/api/autopilot-stop":
                autopilot = stop_autopilot()
                self.send_json({"ok": True, "autopilot": autopilot}, status=HTTPStatus.OK)
                return
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        except Exception as exc:  # noqa: BLE001
            self.send_json({"ok": False, "error": str(exc)}, status=HTTPStatus.BAD_REQUEST)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8421)
    parser.add_argument("--open-browser", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    port, already_running = next_usable_port(args.host, args.port)
    url = f"http://{args.host}:{port}/dashboard/index.html"
    if already_running:
        print(f"Background search control already running at {url}")
        if args.open_browser:
            webbrowser.open(url)
        return 0

    if port != args.port:
        print(f"Port {args.port} is occupied by a different service. Using port {port} instead.")

    server = ThreadingHTTPServer((args.host, port), ControlHandler)

    print(f"Background search control running at {url}")
    if args.open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
