from __future__ import annotations

import argparse
import json
import pathlib
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from typing import Any


SEEDS = [
    "baroque classical", "romantic symphony", "opera aria", "chamber music", "jazz quartet", "bebop jazz", "blues guitar", "soul music", "funk music", "disco music",
    "rock music", "hard rock", "punk rock", "post punk", "grunge", "alternative rock", "progressive rock", "heavy metal", "thrash metal", "death metal",
    "black metal", "doom metal", "industrial metal", "gothic metal", "house music", "deep house", "progressive house", "techno music", "minimal techno", "trance music",
    "psytrance", "hardstyle", "drum and bass", "jungle music", "dubstep", "breakbeat", "ambient music", "downtempo electronic", "synthwave", "new wave",
    "hip hop", "rap music", "trap music", "rnb music", "reggaeton", "salsa music", "afrobeat", "latin pop", "folk music", "country music",
    "bluegrass", "indie pop", "dream pop", "kpop", "jpop", "flamenco", "world music", "experimental music", "noise music", "post rock",
]
FORBIDDEN_PUBLIC = {"trackName", "artistName", "collectionName", "previewUrl", "primaryGenreName", "seed"}


def _norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def select_distinct_catalog(candidates: list[dict[str, Any]], required_count: int, max_per_artist: int = 1) -> list[dict[str, Any]]:
    if required_count < 1 or max_per_artist < 1:
        raise ValueError("required_count and max_per_artist must be positive")
    selected: list[dict[str, Any]] = []
    artist_counts: dict[str, int] = {}
    seen_pairs: set[tuple[str, str]] = set()
    seen_urls: set[str] = set()
    for item in candidates:
        artist = str(item.get("artistName", "")).strip()
        title = str(item.get("trackName", "")).strip()
        url = str(item.get("previewUrl", "")).strip()
        artist_key, title_key = _norm(artist), _norm(title)
        if not artist_key or not title_key or not url:
            continue
        pair = (artist_key, title_key)
        if pair in seen_pairs or url in seen_urls or artist_counts.get(artist_key, 0) >= max_per_artist:
            continue
        selected.append(item)
        seen_pairs.add(pair)
        seen_urls.add(url)
        artist_counts[artist_key] = artist_counts.get(artist_key, 0) + 1
        if len(selected) == required_count:
            return selected
    raise ValueError(f"insufficient distinct candidates: {len(selected)}<{required_count}")


def public_manifest(private: dict[str, Any]) -> dict[str, Any]:
    tracks = private.get("tracks")
    if not isinstance(tracks, list) or not tracks:
        raise ValueError("private catalog requires tracks")
    result = {"schema": "blind-preview-corpus-v3", "tracks": [{"blind_id": item["blind_id"]} for item in tracks]}
    encoded = json.dumps(result, sort_keys=True)
    if any(key in encoded for key in FORBIDDEN_PUBLIC):
        raise ValueError("public metadata leak")
    return result


def fetch_with_retry(operation: Callable[[], list[dict[str, Any]]], attempts: int = 3, sleep_fn: Callable[[float], None] = time.sleep) -> list[dict[str, Any]]:
    if attempts < 1:
        raise ValueError("attempts must be positive")
    for attempt in range(attempts):
        try:
            return operation()
        except (TimeoutError, urllib.error.URLError, urllib.error.HTTPError):
            if attempt == attempts - 1:
                return []
            sleep_fn(float(1 + attempt))
    return []


def fetch_search(term: str, limit: int = 200) -> list[dict[str, Any]]:
    query = urllib.parse.urlencode({"country": "PL", "entity": "song", "limit": min(limit, 200), "term": term})
    request = urllib.request.Request("https://itunes.apple.com/search?" + query, headers={"User-Agent": "BlindAudioPolicy/1.0"})

    def operation() -> list[dict[str, Any]]:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return [
            {
                "trackName": row["trackName"],
                "artistName": row["artistName"],
                "collectionName": row.get("collectionName", ""),
                "primaryGenreName": row.get("primaryGenreName", ""),
                "previewUrl": row["previewUrl"],
                "seed": term,
            }
            for row in payload.get("results", [])
            if row.get("trackName") and row.get("artistName") and row.get("previewUrl")
        ]

    return fetch_with_retry(operation)


def build_catalog(output_dir: pathlib.Path, count: int, max_per_artist: int, pause_seconds: float) -> None:
    candidates: list[dict[str, Any]] = []
    for term in SEEDS:
        candidates.extend(fetch_search(term))
        time.sleep(pause_seconds)
    selected = select_distinct_catalog(candidates, count, max_per_artist)
    tracks = [{"blind_id": f"p{index:04d}.ogg", **item} for index, item in enumerate(selected, start=1)]
    private = {"schema": "private-preview-catalog-v3", "tracks": tracks}
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "catalog_private.json").write_text(json.dumps(private, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
    (output_dir / "manifest_public.json").write_text(json.dumps(public_manifest(private), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"CATALOG_PASS count={len(tracks)} max_per_artist={max_per_artist}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a private 1,000-track metadata catalog for a blind local audio corpus.")
    parser.add_argument("--output-dir", type=pathlib.Path, required=True)
    parser.add_argument("--count", type=int, default=1000)
    parser.add_argument("--max-per-artist", type=int, default=1)
    parser.add_argument("--pause-seconds", type=float, default=0.2)
    args = parser.parse_args()
    build_catalog(args.output_dir, args.count, args.max_per_artist, args.pause_seconds)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
