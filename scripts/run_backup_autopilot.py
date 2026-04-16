#!/usr/bin/env python3
"""Continuous backup autopilot for the primitive leading-surface queue."""

from __future__ import annotations

import json
import signal
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
RESULTS_DIR = ROOT / "results"
STATUS_PATH = RESULTS_DIR / "backup_autopilot_status.json"
LOG_PATH = RESULTS_DIR / "backup_autopilot_history.jsonl"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import search_factor_pair_families as factor_pair  # noqa: E402
import run_primitive_queue_section as section_runner  # noqa: E402


LANE_COUNT = 4
POINTS_PER_LANE_PER_CYCLE = 1
SLEEP_SECONDS = 8
RUNNING = True


def write_status(payload: dict) -> None:
    STATUS_PATH.write_text(json.dumps(payload, indent=2))


def append_history(payload: dict) -> None:
    with LOG_PATH.open("a") as handle:
        handle.write(json.dumps(payload))
        handle.write("\n")


def lane_label(index: int) -> str:
    return chr(64 + index)


def handle_stop(signum, frame) -> None:  # noqa: ANN001, ARG001
    global RUNNING
    RUNNING = False


def main() -> int:
    signal.signal(signal.SIGTERM, handle_stop)
    signal.signal(signal.SIGINT, handle_stop)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    cycle_index = 0

    while RUNNING:
        cycle_index += 1
        cycle_started = time.strftime("%Y-%m-%d %H:%M:%S")
        queue = factor_pair.primitive_leading_surface_representatives()
        known_dead = factor_pair.known_dead_leading_points() | section_runner.load_all_section_points()
        unresolved = [point for point in queue if point not in known_dead]
        cycle_results = []

        if not unresolved:
            payload = {
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "complete",
                "cycle_index": cycle_index,
                "lane_count": LANE_COUNT,
                "points_per_lane_per_cycle": POINTS_PER_LANE_PER_CYCLE,
                "remaining_count": 0,
                "next_unresolved": None,
                "cycle_results": [],
            }
            write_status(payload)
            append_history(payload)
            return 0

        for section_index in range(1, LANE_COUNT + 1):
            result = section_runner.run_section(
                a4_bound=1200,
                b3_bound=500,
                section_index=section_index,
                section_count=LANE_COUNT,
                limit=POINTS_PER_LANE_PER_CYCLE,
                include_known=False,
                label=f"backup_lane_{lane_label(section_index).lower()}",
                emit_jsonl=None,
                emit_summary=None,
                reset_output=False,
            )
            summary = result["summary"]
            if summary["recent_results"]:
                cycle_results.extend(summary["recent_results"])

        queue = factor_pair.primitive_leading_surface_representatives()
        known_dead = factor_pair.known_dead_leading_points() | section_runner.load_all_section_points()
        unresolved = [point for point in queue if point not in known_dead]
        payload = {
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "running",
            "cycle_index": cycle_index,
            "cycle_started": cycle_started,
            "lane_count": LANE_COUNT,
            "points_per_lane_per_cycle": POINTS_PER_LANE_PER_CYCLE,
            "sleep_seconds": SLEEP_SECONDS,
            "remaining_count": len(unresolved),
            "next_unresolved": list(unresolved[0]) if unresolved else None,
            "cycle_results": cycle_results,
        }
        write_status(payload)
        append_history(payload)

        if not RUNNING:
            break
        time.sleep(SLEEP_SECONDS)

    payload = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "stopped",
        "cycle_index": cycle_index,
        "lane_count": LANE_COUNT,
        "points_per_lane_per_cycle": POINTS_PER_LANE_PER_CYCLE,
        "remaining_count": len(
            [point for point in factor_pair.primitive_leading_surface_representatives() if point not in (factor_pair.known_dead_leading_points() | section_runner.load_all_section_points())]
        ),
        "next_unresolved": None,
        "cycle_results": [],
    }
    write_status(payload)
    append_history(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
