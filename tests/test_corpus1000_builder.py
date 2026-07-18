import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from corpus1000_builder import public_manifest, select_distinct_catalog


class Corpus1000BuilderTests(unittest.TestCase):
    def test_selects_only_unique_artist_track_pairs_and_respects_artist_cap(self):
        candidates = [
            {"trackName": "Alpha", "artistName": "Artist A", "previewUrl": "https://x/a1", "primaryGenreName": "Rock"},
            {"trackName": "Alpha", "artistName": "Artist A", "previewUrl": "https://x/a2", "primaryGenreName": "Rock"},
            {"trackName": "Beta", "artistName": "Artist A", "previewUrl": "https://x/a3", "primaryGenreName": "Rock"},
            {"trackName": "Gamma", "artistName": "Artist B", "previewUrl": "https://x/b1", "primaryGenreName": "Jazz"},
            {"trackName": "Delta", "artistName": "Artist C", "previewUrl": "https://x/c1", "primaryGenreName": "Classical"},
        ]
        selected = select_distinct_catalog(candidates, required_count=3, max_per_artist=1)
        self.assertEqual([(x["artistName"], x["trackName"]) for x in selected], [
            ("Artist A", "Alpha"), ("Artist B", "Gamma"), ("Artist C", "Delta"),
        ])

    def test_rejects_insufficient_distinct_candidates(self):
        candidates = [{"trackName": "Alpha", "artistName": "Artist A", "previewUrl": "https://x/a1"}]
        with self.assertRaises(ValueError):
            select_distinct_catalog(candidates, required_count=2, max_per_artist=1)

    def test_public_manifest_exposes_only_blind_id_and_sha_placeholder(self):
        private = {"tracks": [{"blind_id": "p0001.ogg", "artistName": "Artist A", "trackName": "Alpha", "previewUrl": "https://x/a1"}]}
        public = public_manifest(private)
        self.assertEqual(public, {"schema": "blind-preview-corpus-v3", "tracks": [{"blind_id": "p0001.ogg"}]})


if __name__ == "__main__":
    unittest.main()
