from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import pathlib
import random
import subprocess
import wave
from typing import Any


FORBIDDEN_PUBLIC_KEYS = {"style", "source_path", "source_type", "label_evidence", "artist", "title", "genre"}
RESPONSE_KEYS_FOR_TEMPLATE = {
    "trial_id", "blind_id", "audio_sha256", "model_id", "endpoint", "decoding_parameters_hash",
    "system_prompt_hash", "user_prompt_hash", "session_id", "request_id", "timestamp_utc",
    "raw_response", "rating",
}


def build_render_plan(item: dict[str, Any], duration_seconds: int) -> list[str]:
    source = str(item["source_path"])
    target = str(item["target_path"])
    common = [
        "ffmpeg", "-y", "-v", "error", "-i", source, "-map_metadata", "-1", "-map", "0:a:0",
        "-ac", "1", "-ar", "44100", "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-c:a", "pcm_s16le",
    ]
    if item["source_type"] == "loop":
        return [
            "ffmpeg", "-y", "-v", "error", "-stream_loop", "-1", "-i", source, "-t", str(duration_seconds),
            "-map_metadata", "-1", "-map", "0:a:0", "-ac", "1", "-ar", "44100",
            "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-c:a", "pcm_s16le", target,
        ]
    return [
        "ffmpeg", "-y", "-v", "error", "-ss", "30", "-t", str(duration_seconds), "-i", source,
        "-map_metadata", "-1", "-map", "0:a:0", "-ac", "1", "-ar", "44100",
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-c:a", "pcm_s16le", target,
    ]


def public_corpus_manifest(private: dict[str, Any]) -> dict[str, Any]:
    clips = private.get("clips")
    if not isinstance(clips, list) or not clips:
        raise ValueError("private corpus requires clips")
    result = {"schema": "blind-corpus-v2", "clips": [{"blind_id": item["blind_id"]} for item in clips]}
    validate_public_corpus_manifest(result)
    return result


def validate_public_corpus_manifest(manifest: dict[str, Any]) -> None:
    if manifest.get("schema") != "blind-corpus-v2":
        raise ValueError("wrong public corpus schema")
    clips = manifest.get("clips")
    if not isinstance(clips, list) or not clips:
        raise ValueError("public corpus requires clips")
    ids = []
    for item in clips:
        if set(item) != {"blind_id"}:
            raise ValueError("public manifest contains non-blind fields")
        clip_id = item["blind_id"]
        if not isinstance(clip_id, str) or not clip_id.endswith(".wav"):
            raise ValueError("invalid blind ID")
        ids.append(clip_id)
    if len(ids) != len(set(ids)):
        raise ValueError("blind IDs must be unique")
    encoded = json.dumps(manifest, sort_keys=True).lower()
    if any(f'"{key}"' in encoded for key in FORBIDDEN_PUBLIC_KEYS):
        raise ValueError("public manifest leakage")


def build_presentation_deck(blind_ids: list[str], passes: int, seed: int) -> list[dict[str, Any]]:
    if passes < 2:
        raise ValueError("at least two passes are required for stability")
    rng = random.Random(seed)
    rows: list[dict[str, Any]] = []
    trial_id = 1
    for pass_number in range(1, passes + 1):
        ordered = sorted(blind_ids)
        rng.shuffle(ordered)
        for blind_id in ordered:
            rows.append({"trial_id": trial_id, "pass": pass_number, "blind_id": blind_id, "condition": "B0"})
            trial_id += 1
    return rows


def build_pairwise_selection_deck(blind_ids: list[str], seed: int) -> list[dict[str, Any]]:
    if len(set(blind_ids)) != len(blind_ids) or len(blind_ids) < 2:
        raise ValueError("selection deck requires at least two unique blind IDs")
    rows: list[dict[str, Any]] = []
    trial_id = 1
    for first, second in itertools.combinations(sorted(blind_ids), 2):
        for left, right in ((first, second), (second, first)):
            rows.append({
                "trial_id": trial_id,
                "pair_key": f"{first}|{second}",
                "left_id": left,
                "right_id": right,
                "condition": "S0",
                "required_output": "chosen_id",
            })
            trial_id += 1
    random.Random(seed).shuffle(rows)
    for trial_id, row in enumerate(rows, start=1):
        row["trial_id"] = trial_id
    return rows


def make_corpus_fingerprint(
    output_dir: pathlib.Path, public_manifest: dict[str, Any], rating_deck: list[dict[str, Any]], renderer_version: str
) -> dict[str, Any]:
    validate_public_corpus_manifest(public_manifest)
    audio_sha256_by_blind_id: dict[str, str] = {}
    audio_properties: dict[str, dict[str, Any]] = {}
    for item in public_manifest["clips"]:
        blind_id = item["blind_id"]
        path = output_dir / blind_id
        if not path.is_file():
            raise ValueError(f"missing blind audio: {blind_id}")
        with wave.open(str(path), "rb") as handle:
            frames = handle.getnframes()
            sample_rate = handle.getframerate()
            channels = handle.getnchannels()
            sample_width = handle.getsampwidth()
        audio_sha256_by_blind_id[blind_id] = hashlib.sha256(path.read_bytes()).hexdigest()
        audio_properties[blind_id] = {
            "frames": frames,
            "sample_rate": sample_rate,
            "channels": channels,
            "sample_width_bytes": sample_width,
            "duration_seconds": frames / sample_rate,
        }
    canonical = lambda value: json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return {
        "schema": "blind-corpus-fingerprint-v1",
        "renderer_version": renderer_version,
        "public_manifest_sha256": hashlib.sha256(canonical(public_manifest)).hexdigest(),
        "rating_deck_sha256": hashlib.sha256(canonical(rating_deck)).hexdigest(),
        "audio_sha256_by_blind_id": audio_sha256_by_blind_id,
        "audio_properties": audio_properties,
    }


def validate_corpus_fingerprint(
    output_dir: pathlib.Path, public_manifest: dict[str, Any], rating_deck: list[dict[str, Any]], fingerprint: dict[str, Any]
) -> None:
    if fingerprint.get("schema") != "blind-corpus-fingerprint-v1":
        raise ValueError("wrong corpus fingerprint schema")
    actual = make_corpus_fingerprint(output_dir, public_manifest, rating_deck, str(fingerprint.get("renderer_version", "")))
    for key in ("public_manifest_sha256", "rating_deck_sha256", "audio_sha256_by_blind_id", "audio_properties"):
        if actual[key] != fingerprint.get(key):
            raise ValueError(f"corpus fingerprint mismatch: {key}")


def _write_json(path: pathlib.Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def build_corpus(private_manifest_path: pathlib.Path, output_dir: pathlib.Path, seed: int, duration_seconds: int) -> None:
    private = json.loads(private_manifest_path.read_text(encoding="utf-8"))
    if len(private.get("clips", [])) < 15:
        raise ValueError("build requires at least 15 source clips")
    public = public_corpus_manifest(private)
    output_dir.mkdir(parents=True, exist_ok=True)
    for source_item in private["clips"]:
        source = pathlib.Path(source_item["source_path"])
        target = output_dir / source_item["blind_id"]
        if not source.is_file():
            raise FileNotFoundError(source)
        item = dict(source_item)
        item["target_path"] = str(target)
        subprocess.run(build_render_plan(item, duration_seconds), check=True)
    blind_ids = [item["blind_id"] for item in public["clips"]]
    deck = build_presentation_deck(blind_ids, passes=3, seed=seed)
    selection_deck = build_pairwise_selection_deck(blind_ids, seed=seed)
    _write_json(output_dir / "manifest_public.json", public)
    _write_json(output_dir / "presentation_deck_b0.json", deck)
    _write_json(output_dir / "selection_deck_s0.json", selection_deck)
    fingerprint = make_corpus_fingerprint(output_dir, public, deck, "corpus-builder-v2")
    _write_json(output_dir / "corpus_fingerprint.json", fingerprint)
    _write_json(output_dir / "response_template.json", {
        "instruction": "For each blind audio file, return one complete record using the frozen corpus fingerprint and a preregistered run contract. Do not infer artist, genre, or source identity.",
        "required_record_keys": sorted(RESPONSE_KEYS_FOR_TEMPLATE),
    })
    verify_corpus(output_dir)


def verify_corpus(output_dir: pathlib.Path) -> None:
    manifest_path = output_dir / "manifest_public.json"
    deck_path = output_dir / "presentation_deck_b0.json"
    selection_path = output_dir / "selection_deck_s0.json"
    fingerprint_path = output_dir / "corpus_fingerprint.json"
    if not all(path.is_file() for path in (manifest_path, deck_path, selection_path, fingerprint_path)):
        raise ValueError("missing public artifacts")
    public = json.loads(manifest_path.read_text(encoding="utf-8"))
    validate_public_corpus_manifest(public)
    blind_ids = {item["blind_id"] for item in public["clips"]}
    if len(blind_ids) < 15:
        raise ValueError("corpus must contain at least 15 blind clips")
    deck = json.loads(deck_path.read_text(encoding="utf-8"))
    if len(deck) != len(blind_ids) * 3:
        raise ValueError("wrong rating deck size")
    for pass_number in (1, 2, 3):
        if {row["blind_id"] for row in deck if row["pass"] == pass_number} != blind_ids:
            raise ValueError("rating deck pass does not cover each blind clip exactly once")
    selection_deck = json.loads(selection_path.read_text(encoding="utf-8"))
    expected_selection_count = len(blind_ids) * (len(blind_ids) - 1)
    if len(selection_deck) != expected_selection_count:
        raise ValueError("wrong selection deck size")
    if any(row.get("left_id") not in blind_ids or row.get("right_id") not in blind_ids or row.get("left_id") == row.get("right_id") or row.get("required_output") != "chosen_id" for row in selection_deck):
        raise ValueError("invalid selection deck")
    fingerprint = json.loads(fingerprint_path.read_text(encoding="utf-8"))
    validate_corpus_fingerprint(output_dir, public, deck, fingerprint)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build or verify the 15-style blind audio corpus.")
    parser.add_argument("--private-manifest", type=pathlib.Path)
    parser.add_argument("--output-dir", type=pathlib.Path, required=True)
    parser.add_argument("--seed", type=int, default=20260717)
    parser.add_argument("--duration-seconds", type=int, default=20)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    if args.verify_only:
        verify_corpus(args.output_dir)
        print("VERIFY_PASS")
    else:
        if args.private_manifest is None:
            parser.error("--private-manifest is required unless --verify-only")
        build_corpus(args.private_manifest, args.output_dir, args.seed, args.duration_seconds)
        print("BUILD_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
