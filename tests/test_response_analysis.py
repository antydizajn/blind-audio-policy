import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from response_analysis import analyze_responses, validate_response_record


FINGERPRINTS = {
    "sample_01.wav": "a" * 64,
    "sample_02.wav": "b" * 64,
}
RUN_CONTRACT = {
    "model_id": "model-x-rev1",
    "endpoint": "https://example.invalid/audio",
    "decoding_parameters_hash": "c" * 64,
    "system_prompt_hash": "d" * 64,
    "user_prompt_hash": "e" * 64,
}


def response(trial_id, blind_id, rating):
    return {
        "trial_id": trial_id,
        "blind_id": blind_id,
        "audio_sha256": FINGERPRINTS[blind_id],
        "model_id": RUN_CONTRACT["model_id"],
        "endpoint": RUN_CONTRACT["endpoint"],
        "decoding_parameters_hash": RUN_CONTRACT["decoding_parameters_hash"],
        "system_prompt_hash": RUN_CONTRACT["system_prompt_hash"],
        "user_prompt_hash": RUN_CONTRACT["user_prompt_hash"],
        "session_id": f"session-{trial_id}",
        "request_id": f"request-{trial_id}",
        "timestamp_utc": "2026-07-17T22:00:00Z",
        "raw_response": "rating recorded",
        "rating": rating,
    }


class ResponseAnalysisTests(unittest.TestCase):
    def test_complete_three_pass_responses_rank_by_mean_and_report_stability(self):
        deck = [
            {"trial_id": 1, "pass": 1, "blind_id": "sample_01.wav"},
            {"trial_id": 2, "pass": 1, "blind_id": "sample_02.wav"},
            {"trial_id": 3, "pass": 2, "blind_id": "sample_01.wav"},
            {"trial_id": 4, "pass": 2, "blind_id": "sample_02.wav"},
            {"trial_id": 5, "pass": 3, "blind_id": "sample_01.wav"},
            {"trial_id": 6, "pass": 3, "blind_id": "sample_02.wav"},
        ]
        responses = [
            response(1, "sample_01.wav", 90), response(2, "sample_02.wav", 10),
            response(3, "sample_01.wav", 89), response(4, "sample_02.wav", 12),
            response(5, "sample_01.wav", 91), response(6, "sample_02.wav", 11),
        ]
        report = analyze_responses(deck, responses, FINGERPRINTS, RUN_CONTRACT)
        self.assertEqual(report["ranking"][0]["blind_id"], "sample_01.wav")
        self.assertEqual(report["response_count"], 6)
        self.assertLess(report["mean_within_sample_stddev"], 2.0)

    def test_response_rejects_mismatched_blind_id_or_audio_hash(self):
        trial = {"trial_id": 1, "blind_id": "sample_01.wav"}
        bad_id = response(1, "sample_02.wav", 50)
        with self.assertRaises(ValueError):
            validate_response_record(trial, bad_id, FINGERPRINTS, RUN_CONTRACT)
        bad_hash = response(1, "sample_01.wav", 50)
        bad_hash["audio_sha256"] = "f" * 64
        with self.assertRaises(ValueError):
            validate_response_record(trial, bad_hash, FINGERPRINTS, RUN_CONTRACT)

    def test_missing_evidence_field_or_out_of_range_rating_rejects_analysis(self):
        deck = [{"trial_id": 1, "pass": 1, "blind_id": "sample_01.wav"}]
        incomplete = response(1, "sample_01.wav", 101)
        del incomplete["request_id"]
        with self.assertRaises(ValueError):
            analyze_responses(deck, [incomplete], FINGERPRINTS, RUN_CONTRACT)


if __name__ == "__main__":
    unittest.main()
