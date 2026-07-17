from __future__ import annotations

import argparse
import pathlib
from typing import Any


AUDIO_SUFFIXES = {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".aac", ".opus"}
FORBIDDEN_FILENAMES = {
    "catalog_private.json",
    "manifest_private.json",
    "manifest_private_15.json",
    "run_contract.json",
    "omniroute_models_probe.json",
}
FORBIDDEN_TEXT_MARKERS = {
    "palantir foundry",
    "integrate.api.nvidia.com",
    "ri.language-model-service",
    "api_key",
    "authorization: bearer",
    "gho_",
    "ghp_",
}
TEXT_SUFFIXES = {".md", ".py", ".json", ".toml", ".txt", ".yml", ".yaml"}


def audit_public_tree(root: pathlib.Path) -> dict[str, Any]:
    forbidden_paths: list[str] = []
    audio_files: list[str] = []
    forbidden_markers: dict[str, list[str]] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or ".git" in path.parts:
            continue
        relative = path.relative_to(root).as_posix()
        # The auditor contains literal signatures it detects; scanning itself is a false positive.
        if relative == "release_audit.py":
            continue
        if path.name in FORBIDDEN_FILENAMES or "private" in path.name.lower():
            forbidden_paths.append(relative)
        if path.suffix.lower() in AUDIO_SUFFIXES:
            audio_files.append(relative)
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace").lower()
        except OSError:
            forbidden_markers.setdefault(relative, []).append("unreadable-text-file")
            continue
        hits = sorted(marker for marker in FORBIDDEN_TEXT_MARKERS if marker in text)
        if hits:
            forbidden_markers[relative] = hits
    return {
        "root": str(root),
        "forbidden_paths": forbidden_paths,
        "audio_files": audio_files,
        "forbidden_markers": forbidden_markers,
        "ok": not forbidden_paths and not audio_files and not forbidden_markers,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Fail closed if a public blind-audio repository contains non-public assets or secrets.")
    parser.add_argument("--root", type=pathlib.Path, required=True)
    args = parser.parse_args()
    report = audit_public_tree(args.root)
    if report["ok"]:
        print("PUBLIC_RELEASE_AUDIT_PASS")
        return 0
    print("PUBLIC_RELEASE_AUDIT_FAIL")
    for key in ("forbidden_paths", "audio_files", "forbidden_markers"):
        if report[key]:
            print(f"{key}={report[key]}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
