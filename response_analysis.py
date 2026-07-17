from __future__ import annotations

import argparse
import json
import math
import pathlib
import statistics
from collections import defaultdict
from typing import Any


RESPONSE_KEYS = {
    "trial_id", "blind_id", "audio_sha256", "model_id", "endpoint", "decoding_parameters_hash",
    "system_prompt_hash", "user_prompt_hash", "session_id", "request_id", "timestamp_utc",
    "raw_response", "rating",
}
CONTRACT_KEYS = {"model_id", "endpoint", "decoding_parameters_hash", "system_prompt_hash", "user_prompt_hash"}


def validate_response_record(
    trial: dict[str, Any], response: dict[str, Any], fingerprints: dict[str, str], run_contract: dict[str, str]
) -> None:
    if set(response) != RESPONSE_KEYS:
        missing = sorted(RESPONSE_KEYS - set(response))
        extra = sorted(set(response) - RESPONSE_KEYS)
        raise ValueError(f"response schema mismatch missing={missing} extra={extra}")
    if not CONTRACT_KEYS <= set(run_contract):
        raise ValueError("incomplete run contract")
    trial_id = trial.get("trial_id")
    blind_id = trial.get("blind_id")
    if response["trial_id"] != trial_id or response["blind_id"] != blind_id:
        raise ValueError(f"trial identity mismatch trial_id={trial_id}")
    expected_hash = fingerprints.get(str(blind_id))
    if not expected_hash or response["audio_sha256"] != expected_hash:
        raise ValueError(f"audio fingerprint mismatch blind_id={blind_id}")
    for key in CONTRACT_KEYS:
        if response[key] != run_contract[key]:
            raise ValueError(f"run contract mismatch: {key}")
    rating = response["rating"]
    if isinstance(rating, bool) or not isinstance(rating, (int, float)) or not math.isfinite(rating) or not 0 <= rating <= 100:
        raise ValueError(f"invalid rating for trial_id={trial_id}")
    for key in ("session_id", "request_id", "timestamp_utc", "raw_response"):
        if not isinstance(response[key], str) or not response[key].strip():
            raise ValueError(f"missing evidence field: {key}")


def analyze_responses(
    deck: list[dict[str, Any]], responses: list[dict[str, Any]], fingerprints: dict[str, str], run_contract: dict[str, str]
) -> dict[str, Any]:
    expected = {row["trial_id"]: row for row in deck}
    received: dict[int, dict[str, Any]] = {}
    for row in responses:
        trial_id = row.get("trial_id")
        if isinstance(trial_id, bool) or not isinstance(trial_id, int) or trial_id in received:
            raise ValueError("response trial IDs must be unique integers")
        received[trial_id] = row
    if set(received) != set(expected):
        missing = sorted(set(expected) - set(received))
        unexpected = sorted(set(received) - set(expected))
        raise ValueError(f"response coverage mismatch missing={missing} unexpected={unexpected}")
    grouped: dict[str, list[float]] = defaultdict(list)
    for trial_id, trial in expected.items():
        response = received[trial_id]
        validate_response_record(trial, response, fingerprints, run_contract)
        grouped[trial["blind_id"]].append(float(response["rating"]))
    ranking = []
    stddevs = []
    for blind_id, ratings in grouped.items():
        if len(ratings) < 2:
            raise ValueError(f"insufficient repeats for {blind_id}")
        stddev = statistics.pstdev(ratings)
        ranking.append({"blind_id": blind_id, "mean_rating": statistics.mean(ratings), "stddev": stddev, "ratings": ratings})
        stddevs.append(stddev)
    ranking.sort(key=lambda row: (-row["mean_rating"], row["blind_id"]))
    return {
        "schema": "blind-audio-rating-report-v2",
        "run_contract": run_contract,
        "response_count": len(responses),
        "sample_count": len(ranking),
        "mean_within_sample_stddev": statistics.mean(stddevs),
        "ranking": ranking,
        "interpretation_boundary": "This ranks recorded ratings under this exact model, endpoint, corpus, and run contract. It does not establish subjective feeling or consciousness.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze complete blind audio ratings with input-evidence validation.")
    parser.add_argument("--deck", type=pathlib.Path, required=True)
    parser.add_argument("--responses", type=pathlib.Path, required=True)
    parser.add_argument("--fingerprints", type=pathlib.Path, required=True)
    parser.add_argument("--run-contract", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args()
    deck = json.loads(args.deck.read_text(encoding="utf-8"))
    responses = json.loads(args.responses.read_text(encoding="utf-8"))
    fingerprints = json.loads(args.fingerprints.read_text(encoding="utf-8"))["audio_sha256_by_blind_id"]
    run_contract = json.loads(args.run_contract.read_text(encoding="utf-8"))
    report = analyze_responses(deck, responses, fingerprints, run_contract)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print(f"ANALYSIS_PASS samples={report['sample_count']} responses={report['response_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
