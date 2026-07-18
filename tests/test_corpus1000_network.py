import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from corpus1000_builder import fetch_with_retry


class Corpus1000NetworkTests(unittest.TestCase):
    def test_retries_transient_failure_then_returns_payload(self):
        attempts = []

        def operation():
            attempts.append(1)
            if len(attempts) < 3:
                raise TimeoutError("temporary")
            return ["ok"]

        result = fetch_with_retry(operation, attempts=3, sleep_fn=lambda _: None)
        self.assertEqual(result, ["ok"])
        self.assertEqual(len(attempts), 3)

    def test_returns_empty_after_exhausting_transient_failures(self):
        result = fetch_with_retry(lambda: (_ for _ in ()).throw(TimeoutError("temporary")), attempts=2, sleep_fn=lambda _: None)
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
