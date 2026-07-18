import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from corpus1000_audio import build_curl_command, build_transcode_command, required_free_bytes


class Corpus1000AudioTests(unittest.TestCase):
    def test_transcode_command_strips_metadata_and_limits_duration(self):
        command = build_transcode_command("https://example.invalid/source", "/out/p0001.ogg", duration_seconds=12)
        self.assertIn("-map_metadata", command)
        self.assertIn("-1", command)
        self.assertIn("libopus", command)
        self.assertIn("-t", command)
        self.assertIn("12", command)
        self.assertIn("pipe:0", command)
        self.assertNotIn("https://example.invalid/source", command)

    def test_disk_requirement_reserves_headroom_for_resumable_download(self):
        self.assertGreater(required_free_bytes(track_count=1000, bytes_per_track=120_000), 500 * 1024 * 1024)

    def test_curl_command_retries_transient_transport_failures(self):
        command = build_curl_command("https://example.invalid/source")
        self.assertIn("--retry", command)
        self.assertIn("--retry-all-errors", command)
        self.assertIn("--max-time", command)


if __name__ == "__main__":
    unittest.main()
