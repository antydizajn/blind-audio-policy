import pathlib
import sys
import tempfile
import unittest
import wave

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from corpus_builder import (
    build_pairwise_selection_deck,
    build_presentation_deck,
    build_render_plan,
    make_corpus_fingerprint,
    public_corpus_manifest,
    validate_corpus_fingerprint,
)


class CorpusBuilderTests(unittest.TestCase):
    def test_short_loop_is_rendered_by_looping_not_silent_padding(self):
        item = {"blind_id": "sample_07.wav", "source_type": "loop", "source_path": "/a/loop.ogg", "target_path": "/out/sample_07.wav"}
        plan = build_render_plan(item, duration_seconds=30)
        self.assertIn("-stream_loop", plan)
        self.assertIn("-1", plan)
        self.assertIn("30", plan)

    def test_full_track_is_rendered_as_bounded_excerpt(self):
        item = {"blind_id": "sample_01.wav", "source_type": "full_track", "source_path": "/a/track.mp3", "target_path": "/out/sample_01.wav"}
        plan = build_render_plan(item, duration_seconds=30)
        self.assertNotIn("-stream_loop", plan)
        self.assertIn("-ss", plan)
        self.assertIn("-t", plan)

    def test_public_manifest_contains_no_provenance_or_style(self):
        private = {"clips": [{"blind_id": "sample_01.wav", "style": "techno", "source_path": "/secret/a.mp3", "source_type": "loop"}]}
        public = public_corpus_manifest(private)
        self.assertEqual(public, {"schema": "blind-corpus-v2", "clips": [{"blind_id": "sample_01.wav"}]})

    def test_presentation_deck_covers_each_sample_once_per_pass(self):
        deck = build_presentation_deck(["sample_01.wav", "sample_02.wav", "sample_03.wav"], passes=3, seed=17)
        self.assertEqual(len(deck), 9)
        for pass_number in (1, 2, 3):
            ids = [row["blind_id"] for row in deck if row["pass"] == pass_number]
            self.assertEqual(set(ids), {"sample_01.wav", "sample_02.wav", "sample_03.wav"})

    def test_pairwise_selection_deck_counterbalances_every_pair(self):
        deck = build_pairwise_selection_deck(["sample_01.wav", "sample_02.wav", "sample_03.wav"], seed=17)
        self.assertEqual(len(deck), 6)
        pairs = {(row["left_id"], row["right_id"]) for row in deck}
        self.assertIn(("sample_01.wav", "sample_02.wav"), pairs)
        self.assertIn(("sample_02.wav", "sample_01.wav"), pairs)
        self.assertTrue(all(row["required_output"] == "chosen_id" for row in deck))

    def test_fingerprint_detects_audio_tampering(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = pathlib.Path(temp_dir)
            wav_path = root / "sample_01.wav"
            with wave.open(str(wav_path), "wb") as handle:
                handle.setnchannels(1)
                handle.setsampwidth(2)
                handle.setframerate(44100)
                handle.writeframes(b"\x00\x00" * 44100)
            public = {"schema": "blind-corpus-v2", "clips": [{"blind_id": "sample_01.wav"}]}
            deck = [{"trial_id": 1, "pass": 1, "blind_id": "sample_01.wav"}]
            fingerprint = make_corpus_fingerprint(root, public, deck, "renderer-v1")
            validate_corpus_fingerprint(root, public, deck, fingerprint)
            wav_path.write_bytes(wav_path.read_bytes() + b"tamper")
            with self.assertRaises(ValueError):
                validate_corpus_fingerprint(root, public, deck, fingerprint)


if __name__ == "__main__":
    unittest.main()
