import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from feature_selection import declared_utility, percentile_components


class FeatureSelectionTests(unittest.TestCase):
    def test_percentile_components_are_bounded_and_ranked_per_corpus(self):
        raw = {
            "p0001.ogg": {"T": 1.0, "D": 2.0, "C": 3.0, "F": 4.0, "N": 5.0, "Qclip": 0.0, "Qsilence": 0.0, "Qrepeat": 0.0},
            "p0002.ogg": {"T": 2.0, "D": 1.0, "C": 2.0, "F": 3.0, "N": 4.0, "Qclip": 0.0, "Qsilence": 0.0, "Qrepeat": 0.0},
        }
        normalized = percentile_components(raw)
        self.assertEqual(normalized["p0002.ogg"]["T"], 1.0)
        self.assertEqual(normalized["p0001.ogg"]["T"], 0.5)
        self.assertTrue(all(0.0 <= value <= 1.0 for component in normalized.values() for value in component.values()))

    def test_declared_utility_rewards_structure_and_penalizes_repetition(self):
        rich = {"T": 1.0, "D": 1.0, "C": 1.0, "F": 1.0, "N": 1.0, "Qclip": 0.0, "Qsilence": 0.0, "Qrepeat": 0.0}
        repetitive = {"T": 1.0, "D": 1.0, "C": 1.0, "F": 1.0, "N": 1.0, "Qclip": 0.0, "Qsilence": 0.0, "Qrepeat": 1.0}
        self.assertGreater(declared_utility(rich), declared_utility(repetitive))


if __name__ == "__main__":
    unittest.main()
