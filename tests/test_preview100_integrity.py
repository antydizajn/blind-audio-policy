import hashlib
import json
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from preview100_integrity import verify_preview100


class Preview100IntegrityTests(unittest.TestCase):
    def test_accepts_exact_anonymous_corpus(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            audio = root / "audio"
            audio.mkdir()
            payload = b"local-audio-bytes"
            (audio / "p001.ogg").write_bytes(payload)
            manifest = {
                "schema": "blind-preview-corpus-v2",
                "tracks": [{"blind_id": "p001.ogg", "sha256": hashlib.sha256(payload).hexdigest()}],
            }
            manifest_path = root / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            report = verify_preview100(audio, manifest_path)
            self.assertTrue(report["ok"])
            self.assertEqual(report["verified_count"], 1)

    def test_rejects_changed_or_extra_audio(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            audio = root / "audio"
            audio.mkdir()
            (audio / "p001.ogg").write_bytes(b"changed")
            (audio / "unexpected.ogg").write_bytes(b"extra")
            manifest = {
                "schema": "blind-preview-corpus-v2",
                "tracks": [{"blind_id": "p001.ogg", "sha256": hashlib.sha256(b"expected").hexdigest()}],
            }
            manifest_path = root / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            report = verify_preview100(audio, manifest_path)
            self.assertFalse(report["ok"])
            self.assertIn("p001.ogg", report["hash_mismatches"])
            self.assertIn("unexpected.ogg", report["unexpected_files"])


if __name__ == "__main__":
    unittest.main()
