#!/usr/bin/env python3
"""Run a non-overlapping section of the primitive leading-surface queue."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

import search_factor_pair_families as factor_pair


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "results" / "primitive_queue_sections"


def load_jsonl_points(path: Path) -> set[tuple[int, int, int]]:
    if not path.exists():
        return set()
    rows: set[tuple[int, int, int]] = set()
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        point = payload.get("leading_point")
        if point:
            rows.add(tuple(int(value) for value in point))
    return rows


def load_all_section_points(output_dir: Path = DEFAULT_OUTPUT_DIR) -> set[tuple[int, int, int]]:
    rows: set[tuple[int, int, int]] = set()
    if not output_dir.exists():
        return rows
    for path in output_dir.glob("*.jsonl"):
        rows |= load_jsonl_points(path)
    return rows


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    with path.open("a") as handle:
        handle.write(json.dumps(row))
        handle.write("\n")


def default_output_paths(section_index: int, section_count: int, label: str | None) -> tuple[Path, Path]:
    stem = label or f"full_minus2_section_{section_index}_of_{section_count}"
    return (
        DEFAULT_OUTPUT_DIR / f"{stem}.jsonl",
        DEFAULT_OUTPUT_DIR / f"{stem}.json",
    )


def build_record(
    point: tuple[int, int, int],
    row: dict[str, Any],
    section_index: int,
    section_count: int,
    ordinal_in_section: int,
) -> dict[str, Any]:
    return {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "section_index": section_index,
        "section_count": section_count,
        "ordinal_in_section": ordinal_in_section,
        "leading_point": list(point),
        "result": row["result"],
        "b1_zero_relation": row["b1_zero_branch"]["b2_relation"],
        "b1_zero_summary": row["b1_zero_branch"]["proof_summary"],
        "odd_branch_gcd": row["odd_branch"]["intersection_gcd"],
        "proof_summary": row["proof_summary"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--a4-bound", type=int, default=1200)
    parser.add_argument("--b3-bound", type=int, default=500)
    parser.add_argument("--section-index", type=int, default=1)
    parser.add_argument("--section-count", type=int, default=1)
    parser.add_argument("--limit", type=int, default=1)
    parser.add_argument("--include-known", action="store_true")
    parser.add_argument("--label")
    parser.add_argument("--emit-jsonl")
    parser.add_argument("--emit-summary")
    parser.add_argument("--reset-output", action="store_true")
    return parser.parse_args()


def run_section(
    *,
    a4_bound: int,
    b3_bound: int,
    section_index: int,
    section_count: int,
    limit: int,
    include_known: bool,
    label: str | None,
    emit_jsonl: Path | None,
    emit_summary: Path | None,
    reset_output: bool,
) -> dict[str, Any]:
    jsonl_path, summary_path = default_output_paths(section_index, section_count, label)
    if emit_jsonl is not None:
        jsonl_path = emit_jsonl
    if emit_summary is not None:
        summary_path = emit_summary

    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.parent.mkdir(parents=True, exist_ok=True)

    if reset_output:
        jsonl_path.unlink(missing_ok=True)
        summary_path.unlink(missing_ok=True)

    queue = factor_pair.primitive_leading_surface_representatives(a4_bound, b3_bound)
    full_section = factor_pair.contiguous_section_rows(queue, section_index, section_count)
    known_dead = set() if include_known else factor_pair.known_dead_leading_points()
    globally_processed = load_all_section_points()
    already_processed = load_jsonl_points(jsonl_path)
    all_known = known_dead | globally_processed

    todo = [point for point in full_section if point not in all_known and point not in already_processed]
    processed_now: list[dict[str, Any]] = []
    limit_value = len(todo) if limit <= 0 else min(limit, len(todo))

    for point in todo[:limit_value]:
        ordinal = full_section.index(point) + 1
        row = factor_pair.reduced_core_branch_reduction(*point, slug=f"section_{section_index}_{point[0]}_{point[1]}_{point[2]}")
        record = build_record(point, row, section_index, section_count, ordinal)
        append_jsonl(jsonl_path, record)
        processed_now.append(record)

    remaining = [point for point in todo if tuple(point) not in {tuple(row["leading_point"]) for row in processed_now}]
    summary = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "section_index": section_index,
        "section_count": section_count,
        "a4_bound": a4_bound,
        "b3_bound": b3_bound,
        "queue_size": len(queue),
        "section_size": len(full_section),
        "known_dead_in_section": sum(1 for point in full_section if point in all_known),
        "already_processed_in_section": sum(1 for point in full_section if point in already_processed),
        "processed_this_run": len(processed_now),
        "remaining_unprocessed_in_section": len(remaining),
        "next_unprocessed": list(remaining[0]) if remaining else None,
        "jsonl_path": str(jsonl_path),
        "recent_results": processed_now,
    }
    summary_path.write_text(json.dumps(summary, indent=2))
    return {
        "jsonl_path": jsonl_path,
        "summary_path": summary_path,
        "summary": summary,
    }


def main() -> int:
    args = parse_args()
    result = run_section(
        a4_bound=args.a4_bound,
        b3_bound=args.b3_bound,
        section_index=args.section_index,
        section_count=args.section_count,
        limit=args.limit,
        include_known=args.include_known,
        label=args.label,
        emit_jsonl=Path(args.emit_jsonl) if args.emit_jsonl else None,
        emit_summary=Path(args.emit_summary) if args.emit_summary else None,
        reset_output=args.reset_output,
    )
    summary = result["summary"]
    jsonl_path = result["jsonl_path"]
    summary_path = result["summary_path"]

    print(f"wrote {jsonl_path}")
    print(f"wrote {summary_path}")
    if summary["next_unprocessed"]:
        print(f"next_unprocessed={tuple(summary['next_unprocessed'])}")
    else:
        print("next_unprocessed=None")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
