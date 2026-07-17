from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
from typing import Any


AUDIO_SUFFIX = ".ogg"
SCHEMA = "blind-preview-corpus-v2"


def _sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_preview100(audio_dir: pathlib.Path, manifest_path: pathlib.Path) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != SCHEMA:
        raise ValueError("wrong preview100 manifest schema")
    tracks = manifest.get("tracks")
    if not isinstance(tracks, list) or not tracks:
        raise ValueError("manifest requires non-empty tracks")
    expected: dict[str, str] = {}
    for record in tracks:
        if set(record) != {"blind_id", "sha256"}:
            raise ValueError("manifest records must contain only blind_id and sha256")
        blind_id, expected_hash = record["blind_id"], record["sha256"]
        if not isinstance(blind_id, str) or not blind_id.startswith("p") or not blind_id.endswith(AUDIO_SUFFIX):
            raise ValueError("invalid blind ID")
        if not isinstance(expected_hash, str) or len(expected_hash) != 64:
            raise ValueError("invalid SHA-256")
        if blind_id in expected:
            raise ValueError("duplicate blind ID")
        expected[blind_id] = expected_hash
    actual_files = {path.name: path for path in audio_dir.glob(f"*{AUDIO_SUFFIX}") if path.is_file()}
    missing = sorted(set(expected) - set(actual_files))
    unexpected = sorted(set(actual_files) - set(expected))
    mismatches = sorted(name for name in set(expected) & set(actual_files) if _sha256(actual_files[name]) != expected[name])
    return {
        "schema": "preview100-integrity-report-v1",
        "expected_count": len(expected),
        "verified_count": len(expected) - len(missing) - len(mismatches),
        "missing_files": missing,
        "unexpected_files": unexpected,
        "hash_mismatches": mismatches,
        "ok": not missing and not unexpected and not mismatches,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify an anonymous local P100 corpus against public blind IDs and SHA-256 hashes.")
    parser.add_argument("--audio-dir", type=pathlib.Path, required=True)
    parser.add_argument("--manifest", type=pathlib.Path, required=True)
    args = parser.parse_args()
    report = verify_preview100(args.audio_dir, args.manifest)
    print(json.dumps(report, sort_keys=True, allow_nan=False))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
