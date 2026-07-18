from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any

import librosa
import numpy as np

from replication_1000 import build_repetition_schedule, summarize_repetitions


POSITIVE = ("T", "D", "C", "F", "N")
PENALTIES = ("Qclip", "Qsilence", "Qrepeat")


def declared_utility(component: dict[str, float]) -> float:
    return (
        0.25 * component["T"] + 0.20 * component["D"] + 0.20 * component["C"] + 0.20 * component["F"] + 0.15 * component["N"]
        - (0.07 * component["Qclip"] + 0.06 * component["Qsilence"] + 0.10 * component["Qrepeat"])
    )


def percentile_components(raw: dict[str, dict[str, float]]) -> dict[str, dict[str, float]]:
    if not raw:
        raise ValueError("raw components are required")
    result = {blind_id: dict(component) for blind_id, component in raw.items()}
    for key in POSITIVE:
        values = np.array([raw[blind_id][key] for blind_id in sorted(raw)], dtype=float)
        order = np.argsort(values, kind="stable")
        ranks = np.empty(len(values), dtype=float)
        ranks[order] = np.arange(1, len(values) + 1, dtype=float) / len(values)
        for blind_id, rank in zip(sorted(raw), ranks, strict=True):
            result[blind_id][key] = float(rank)
    for key in PENALTIES:
        values = np.array([raw[blind_id][key] for blind_id in sorted(raw)], dtype=float)
        maximum = float(values.max())
        for blind_id, value in zip(sorted(raw), values, strict=True):
            result[blind_id][key] = 0.0 if maximum == 0.0 else float(value / maximum)
    return result


def raw_audio_components(path: pathlib.Path) -> dict[str, float]:
    y, sample_rate = librosa.load(path, sr=22050, mono=True)
    if len(y) < sample_rate:
        raise ValueError("audio shorter than one second")
    onset = librosa.onset.onset_strength(y=y, sr=sample_rate)
    onset_autocorrelation = librosa.autocorrelate(onset)
    T = float(onset_autocorrelation[1:].max() / (onset_autocorrelation[0] + 1e-12)) if len(onset_autocorrelation) > 1 else 0.0
    rms = librosa.feature.rms(y=y)[0]
    sections = np.array_split(rms, 8)
    D = float(np.std([float(section.mean()) for section in sections if len(section)]))
    chroma = librosa.feature.chroma_cqt(y=y, sr=sample_rate)
    C = float(np.mean(np.max(chroma, axis=0)))
    F = float(np.mean(np.abs(np.diff(onset)))) if len(onset) > 1 else 0.0
    spectral = librosa.feature.spectral_centroid(y=y, sr=sample_rate)[0]
    spectral_sections = [float(section.mean()) for section in np.array_split(spectral, 8) if len(section)]
    N = float(np.mean(np.abs(np.diff(spectral_sections)))) if len(spectral_sections) > 1 else 0.0
    Qclip = float(np.mean(np.abs(y) >= 0.999))
    Qsilence = float(np.mean(rms <= 0.001))
    chroma_sections = [section.mean(axis=1) for section in np.array_split(chroma, 8, axis=1) if section.shape[1]]
    correlations = []
    for left, right in zip(chroma_sections, chroma_sections[1:], strict=False):
        denominator = float(np.linalg.norm(left) * np.linalg.norm(right))
        correlations.append(float(np.dot(left, right) / denominator) if denominator else 0.0)
    Qrepeat = float(np.mean(correlations)) if correlations else 0.0
    return {"T": T, "D": D, "C": C, "F": F, "N": N, "Qclip": Qclip, "Qsilence": Qsilence, "Qrepeat": Qrepeat}


def run_feature_repetitions(audio_dir: pathlib.Path, repetitions: int = 10, top_k: int = 10) -> dict[str, Any]:
    paths = {path.name: path for path in sorted(audio_dir.glob("p*.ogg"))}
    raw: dict[str, dict[str, float]] = {}
    failures: dict[str, str] = {}
    for blind_id, path in paths.items():
        try:
            raw[blind_id] = raw_audio_components(path)
        except Exception as exc:
            failures[blind_id] = f"{type(exc).__name__}:{exc}"
    normalized = percentile_components(raw) if raw else {}
    schedule = build_repetition_schedule(sorted(paths), repetitions=repetitions)
    results = []
    for trial in schedule:
        blind_id = trial["blind_id"]
        if blind_id in failures:
            results.append({**trial, "status": "failed", "utility": None, "components": {}, "reason": failures[blind_id]})
        else:
            component = normalized[blind_id]
            results.append({**trial, "status": "scored", "utility": declared_utility(component), "components": component, "reason": ""})
    report = summarize_repetitions(results, top_k=top_k)
    report["corpus_files_present"] = len(paths)
    report["feature_failures"] = failures
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run declared feature-based blind selections over local anonymous OGG files.")
    parser.add_argument("--audio-dir", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    parser.add_argument("--repetitions", type=int, default=10)
    parser.add_argument("--top-k", type=int, default=10)
    args = parser.parse_args()
    report = run_feature_repetitions(args.audio_dir, args.repetitions, args.top_k)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print(f"FEATURE_SELECTION_PASS files={report['corpus_files_present']} trials={report['scheduled_trials']} failures={report['failed_trials']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
