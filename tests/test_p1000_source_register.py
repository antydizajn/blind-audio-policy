import csv
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REGISTER = ROOT / "P1000_SOURCE_REGISTER_POST_UNBLINDING.csv"


class P1000SourceRegisterTests(unittest.TestCase):
    def test_register_has_exactly_one_complete_row_per_public_blind_id(self):
        with REGISTER.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 1000)
        self.assertEqual(set(rows[0]), {"blind_id", "artist", "track_title", "collection", "preview_url", "source_query"})
        blind_ids = [row["blind_id"] for row in rows]
        self.assertEqual(len(set(blind_ids)), 1000)
        self.assertTrue(all(row["artist"] and row["track_title"] and row["preview_url"] for row in rows))


if __name__ == "__main__":
    unittest.main()
