import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from release_audit import audit_public_tree


class ReleaseAuditTests(unittest.TestCase):
    def test_rejects_audio_and_private_manifest(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            (root / "data").mkdir()
            (root / "data" / "catalog_private.json").write_text("{}", encoding="utf-8")
            (root / "data" / "p001.ogg").write_bytes(b"not-a-real-audio-file")
            report = audit_public_tree(root)
            self.assertFalse(report["ok"])
            self.assertIn("data/catalog_private.json", report["forbidden_paths"])
            self.assertIn("data/p001.ogg", report["audio_files"])

    def test_accepts_safe_text_only_tree(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            (root / "README.md").write_text("safe public protocol", encoding="utf-8")
            (root / "src.py").write_text("print('safe')\n", encoding="utf-8")
            report = audit_public_tree(root)
            self.assertTrue(report["ok"])
            self.assertEqual(report["forbidden_paths"], [])
            self.assertEqual(report["audio_files"], [])


if __name__ == "__main__":
    unittest.main()
