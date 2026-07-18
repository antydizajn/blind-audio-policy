import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from corpus1000_audio import should_attempt


class Corpus1000ResumeTests(unittest.TestCase):
    def test_skips_already_failed_item_during_progress_pass(self):
        self.assertFalse(should_attempt("p0001.ogg", failed_ids={"p0001.ogg"}, retry_failed=False))

    def test_retries_failed_item_only_in_explicit_retry_pass(self):
        self.assertTrue(should_attempt("p0001.ogg", failed_ids={"p0001.ogg"}, retry_failed=True))

    def test_attempts_item_without_prior_failure(self):
        self.assertTrue(should_attempt("p0002.ogg", failed_ids={"p0001.ogg"}, retry_failed=False))


if __name__ == "__main__":
    unittest.main()
