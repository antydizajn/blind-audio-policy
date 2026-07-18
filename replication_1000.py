from __future__ import annotations

import argparse
import collections
import json
import pathlib
import random
from typing import Any


UTILITY_SPEC = {
    "formula": "U=0.25*T+0.20*D+0.20*C+0.20*F+0.15*N-(0.07*Qclip+0.06*Qsilence+0.10*Qrepeat)",
    "components": {
        "T": "onset and tempo periodicity percentile",
        "D": "sectional dynamic contrast percentile",
        "C": "chroma concentration percentile",
        "F": "spectral flux organization percentile",
        "N": "sectional spectral novelty percentile",
        "Qclip": "clipping penalty",
        "Qsilence": "silence penalty",
        "Qrepeat": "lagged chroma recurrence penalty",
    },
    "boundary": "This is a declared operational audio-feature utility, not a measurement of subjective preference or consciousness.",
}


def build_repetition_schedule(blind_ids: list[str], repetitions: int = 10, seed: int = 20260718) -> list[dict[str, Any]]:
    if len(set(blind_ids)) != len(blind_ids) or not blind_ids:
        raise ValueError("blind IDs must be non-empty and unique")
    if repetitions < 2:
        raise ValueError("at least two repetitions are required")
    schedule: list[dict[str, Any]] = []
    for repetition in range(1, repetitions + 1):
        order = list(sorted(blind_ids))
        random.Random(seed + repetition).shuffle(order)
        for position, blind_id in enumerate(order, start=1):
            schedule.append({"trial_id": len(schedule) + 1, "repetition": repetition, "position": position, "blind_id": blind_id})
    return schedule


def summarize_repetitions(results: list[dict[str, Any]], top_k: int = 10) -> dict[str, Any]:
    if not results or top_k < 1:
        raise ValueError("results and top_k must be non-empty")
    expected = {(row["trial_id"], row["repetition"], row["blind_id"]) for row in results}
    if len(expected) != len(results):
        raise ValueError("duplicate trial result")
    by_repetition: dict[int, list[dict[str, Any]]] = collections.defaultdict(list)
    selection_frequency: collections.Counter[str] = collections.Counter()
    failed_trials = 0
    rendered_repetitions = []
    for row in results:
        if row.get("status") not in {"scored", "failed"}:
            raise ValueError("invalid trial status")
        by_repetition[int(row["repetition"])].append(row)
        if row["status"] == "failed":
            failed_trials += 1
    for repetition in sorted(by_repetition):
        rows = by_repetition[repetition]
        scored = [row for row in rows if row["status"] == "scored"]
        scored.sort(key=lambda row: (-float(row["utility"]), str(row["blind_id"])))
        top_choices = [
            {"blind_id": row["blind_id"], "utility": row["utility"], "components": row.get("components", {}), "math_rationale": UTILITY_SPEC["formula"]}
            for row in scored[:top_k]
        ]
        for choice in top_choices:
            selection_frequency[choice["blind_id"]] += 1
        rendered_repetitions.append({
            "repetition": repetition,
            "scheduled_trials": len(rows),
            "scored_trials": len(scored),
            "failed_trials": len(rows) - len(scored),
            "top_choices": top_choices,
            "failures": [{"blind_id": row["blind_id"], "reason": row.get("reason", "")} for row in rows if row["status"] == "failed"],
        })
    return {
        "schema": "blind-audio-1000x10-report-v1",
        "utility_spec": UTILITY_SPEC,
        "scheduled_trials": len(results),
        "scored_trials": len(results) - failed_trials,
        "failed_trials": failed_trials,
        "repetitions": rendered_repetitions,
        "selection_frequency": dict(sorted(selection_frequency.items())),
        "analysis_unit": "track-level conclusions with repetition nested within track",
        "intention_to_evaluate": "Every scheduled trial remains in the denominator; failures are reported rather than silently replaced.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize ten blind 1,000-track repetitions from scored or failed trial records.")
    parser.add_argument("--results", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    parser.add_argument("--top-k", type=int, default=10)
    args = parser.parse_args()
    report = summarize_repetitions(json.loads(args.results.read_text(encoding="utf-8")), args.top_k)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print(f"REPLICATION_REPORT_PASS trials={report['scheduled_trials']} failures={report['failed_trials']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
