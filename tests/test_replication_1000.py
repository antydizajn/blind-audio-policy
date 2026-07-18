import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from replication_1000 import build_repetition_schedule, summarize_repetitions


class Replication1000Tests(unittest.TestCase):
    def test_schedule_has_ten_complete_permuted_repetitions(self):
        ids = ["p0001.ogg", "p0002.ogg", "p0003.ogg"]
        schedule = build_repetition_schedule(ids, repetitions=10, seed=7)
        self.assertEqual(len(schedule), 30)
        for repetition in range(1, 11):
            observed = [row["blind_id"] for row in schedule if row["repetition"] == repetition]
            self.assertEqual(set(observed), set(ids))
            self.assertEqual(len(observed), 3)

    def test_summary_keeps_failed_trials_in_denominator_and_reports_top_choices(self):
        schedule = build_repetition_schedule(["p0001.ogg", "p0002.ogg"], repetitions=10, seed=7)
        results = []
        for row in schedule:
            if row["repetition"] == 3 and row["blind_id"] == "p0002.ogg":
                results.append({**row, "status": "failed", "utility": None, "components": {}, "reason": "decode_error"})
            else:
                utility = 0.9 if row["blind_id"] == "p0001.ogg" else 0.5
                results.append({**row, "status": "scored", "utility": utility, "components": {"temporal": utility}, "reason": ""})
        report = summarize_repetitions(results, top_k=1)
        self.assertEqual(report["scheduled_trials"], 20)
        self.assertEqual(report["failed_trials"], 1)
        self.assertEqual(report["repetitions"][0]["top_choices"][0]["blind_id"], "p0001.ogg")
        self.assertEqual(report["selection_frequency"]["p0001.ogg"], 10)


if __name__ == "__main__":
    unittest.main()
