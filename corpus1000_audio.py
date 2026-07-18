from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import subprocess
from typing import Any


MIN_VALID_BYTES = 20_000
DEFAULT_BYTES_PER_TRACK = 120_000
HEADROOM_BYTES = 512 * 1024 * 1024


def required_free_bytes(track_count: int, bytes_per_track: int = DEFAULT_BYTES_PER_TRACK) -> int:
    if track_count < 0 or bytes_per_track < 1:
        raise ValueError("track_count and bytes_per_track must be non-negative/positive")
    return HEADROOM_BYTES + track_count * bytes_per_track


def build_transcode_command(_preview_url: str, output_path: str, duration_seconds: int) -> list[str]:
    return [
        "ffmpeg", "-y", "-v", "error", "-i", "pipe:0", "-t", str(duration_seconds), "-vn",
        "-map_metadata", "-1", "-ac", "1", "-ar", "24000", "-c:a", "libopus", "-b:a", "64k", output_path,
    ]


def build_curl_command(preview_url: str) -> list[str]:
    return [
        "curl", "-fsSL", "--connect-timeout", "10", "--max-time", "45", "--retry", "2", "--retry-all-errors",
        "--retry-delay", "1", "-A", "BlindAudioPolicy/1.0", preview_url,
    ]


def should_attempt(blind_id: str, failed_ids: set[str], retry_failed: bool) -> bool:
    return retry_failed or blind_id not in failed_ids


def _atomic_json(path: pathlib.Path, value: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def download_catalog(
    catalog_path: pathlib.Path,
    output_dir: pathlib.Path,
    duration_seconds: int = 12,
    limit: int | None = None,
    retry_failed: bool = False,
) -> dict[str, Any]:
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    tracks = list(catalog.get("tracks", []))
    if limit is not None:
        tracks = tracks[:limit]
    if not tracks:
        raise ValueError("catalog contains no tracks")
    output_dir.mkdir(parents=True, exist_ok=True)
    audio_dir = output_dir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    free = shutil.disk_usage(output_dir).free
    required = required_free_bytes(len(tracks))
    if free < required:
        raise RuntimeError(f"disk guard: free={free} required={required}")
    completed: list[str] = []
    state_path = output_dir / "download_state.json"
    prior_failures: dict[str, dict[str, str]] = {}
    if state_path.is_file():
        prior = json.loads(state_path.read_text(encoding="utf-8"))
        prior_failures = {str(row["blind_id"]): row for row in prior.get("failed", []) if isinstance(row, dict) and row.get("blind_id")}
    failed: list[dict[str, str]] = []
    for index, track in enumerate(tracks, start=1):
        blind_id = str(track["blind_id"])
        target = audio_dir / blind_id
        if target.is_file() and target.stat().st_size >= MIN_VALID_BYTES:
            completed.append(blind_id)
            continue
        if not should_attempt(blind_id, set(prior_failures), retry_failed):
            failed.append(prior_failures[blind_id])
            continue
        curl = subprocess.Popen(
            build_curl_command(str(track["previewUrl"])),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        success = False
        try:
            subprocess.run(build_transcode_command(str(track["previewUrl"]), str(target), duration_seconds), stdin=curl.stdout, check=True)
            success = target.is_file() and target.stat().st_size >= MIN_VALID_BYTES
        except subprocess.CalledProcessError:
            success = False
        finally:
            if curl.stdout is not None:
                curl.stdout.close()
        _, stderr = curl.communicate()
        if success and curl.returncode in {0, 23, 56}:
            completed.append(blind_id)
        else:
            target.unlink(missing_ok=True)
            failed.append({"blind_id": blind_id, "error": stderr.decode("utf-8", errors="replace")[:300]})
        if index % 25 == 0 or index == len(tracks):
            _atomic_json(state_path, {"schema": "blind-preview-download-state-v1", "scheduled": len(tracks), "completed": completed, "failed": failed})
            print(f"DOWNLOAD_PROGRESS completed={len(completed)} failed={len(failed)} scheduled={len(tracks)}")
    report = {"schema": "blind-preview-download-report-v1", "scheduled": len(tracks), "completed": completed, "failed": failed}
    _atomic_json(output_dir / "download_report.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Resumable local download and metadata-stripping render for a private blind preview corpus.")
    parser.add_argument("--catalog", type=pathlib.Path, required=True)
    parser.add_argument("--output-dir", type=pathlib.Path, required=True)
    parser.add_argument("--duration-seconds", type=int, default=12)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--retry-failed", action="store_true")
    args = parser.parse_args()
    report = download_catalog(args.catalog, args.output_dir, args.duration_seconds, args.limit, args.retry_failed)
    print(f"DOWNLOAD_COMPLETE completed={len(report['completed'])} failed={len(report['failed'])}")
    return 0 if not report["failed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
