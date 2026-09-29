import json
from pathlib import Path
import unittest

from voice_practice.media import parse_silences
from voice_practice.merge import choose_seam, merge_windows, review_starts
from voice_practice.transcripts import Row, parse_payload, parse_rows, subtitles, transcription


class WindowAndMergeTests(unittest.TestCase):
    def test_exact_boundaries_and_partial_tail(self):
        for duration, expected in [(0.1, [0]), (60, [0]), (60.01, [0, 30]), (90, [0, 30]),
                                   (90.01, [0, 30, 60]), (120, [0, 30, 60])]:
            with self.subTest(duration=duration):
                self.assertEqual(review_starts(duration), expected)

    def test_invalid_window_specs(self):
        for args in [(0,), (-1,), (float("nan"),), (10, 5, 6), (10, 0, 1)]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                review_starts(*args)

    def test_safe_seam_prefers_longest_silence(self):
        left = [Row(30, 41, "left")]
        right = [Row(45, 55, "right")]
        seam = choose_seam(left, right, 30, 30, [(41, 45), (41.5, 44.5)])
        self.assertEqual(seam["method"], "hybrid_safe")
        self.assertEqual(seam["seam"], 43)
        self.assertEqual(seam["silence_duration"], 4)
        self.assertEqual(seam["edge_error"], 0)

    def test_safe_threshold_is_inclusive(self):
        seam = choose_seam([Row(0, 1.6, "left")], [Row(5, 10, "right")], 0, 10, [(0, 5)])
        self.assertEqual(seam["method"], "hybrid_safe")
        self.assertAlmostEqual(seam["edge_error"], 1.6)

    def test_fallback_prefers_minimum_edge_error(self):
        seam = choose_seam([Row(0, 36, "left")], [Row(50, 60, "right")], 30, 30,
                           [(37, 40), (40, 48)], max_edge_error=1.6)
        self.assertEqual(seam["method"], "fallback_min_edge")
        self.assertEqual(seam["seam"], 44)
        self.assertEqual(seam["edge_error"], 6)

    def test_no_usable_candidate_falls_back_to_center(self):
        for silences in ([], [(90, 92)], [(40, 44)]):
            with self.subTest(silences=silences):
                seam = choose_seam([], [Row(40, 50, "right")], 30, 30, silences)
                self.assertEqual(seam["method"], "fallback_center_no_silence")
                self.assertEqual(seam["seam"], 45)

    def test_no_overlap(self):
        seam = choose_seam([], [], 60, 0, [])
        self.assertEqual(seam["method"], "no_overlap")
        self.assertEqual(seam["seam"], 60)

    def test_midpoint_boundary_owned_by_right_window_once(self):
        windows = [[Row(0, 10, "early", 0), Row(40, 50, "left duplicate", 0)],
                   [Row(40, 50, "right accepted", 30), Row(60, 70, "late", 30)]]
        merged = merge_windows(windows, [{"seam": 45}])
        self.assertEqual([row.text for row in merged], ["early", "right accepted", "late"])

    def test_three_window_partition(self):
        windows = [[Row(10, 20, "one", 0), Row(45, 55, "discard", 0)],
                   [Row(40, 50, "two", 30), Row(75, 85, "discard", 30)],
                   [Row(70, 80, "three", 60), Row(90, 100, "four", 60)]]
        self.assertEqual([x.text for x in merge_windows(windows, [{"seam": 45}, {"seam": 75}])],
                         ["one", "two", "three", "four"])
        with self.assertRaisesRegex(ValueError, "exactly one"):
            merge_windows(windows, [])
        with self.assertRaisesRegex(ValueError, "ordered"):
            merge_windows(windows, [{"seam": 80}, {"seam": 40}])

    def test_silence_events_offset_and_trailing_silence(self):
        stderr = "silence_start: 2.5\nsilence_end: 4\nsilence_start: 28\n"
        self.assertEqual(parse_silences(stderr, 30, 30), [(32.5, 34), (58, 60)])
        self.assertEqual(parse_silences("silence_end: 1.5", 30, 30), [(30, 31.5)])


class TranscriptTests(unittest.TestCase):
    def test_original_fixture_offsets_and_window_metadata(self):
        path = Path(__file__).parent / "fixtures" / "original_whisper.json"
        rows = parse_rows(path, start=30, window=30)
        self.assertEqual(rows[0], Row(30.25, 31.75, "I packed a small notebook.", 30))
        final = transcription(rows)
        self.assertEqual(final[0]["offsets"], {"from": 30250, "to": 31750})
        self.assertEqual(final[0]["window_start"], 30)

    def test_malformed_payloads_are_not_accepted_as_empty_success(self):
        invalid = [{}, [], {"transcription": None}, {"transcription": [{}]},
                   {"transcription": [{"offsets": {"from": 0, "to": 1}, "text": None}]},
                   {"transcription": [{"offsets": {"from": 2, "to": 1}, "text": "x"}]},
                   {"transcription": [{"offsets": {"from": -1, "to": 1}, "text": "x"}]},
                   {"transcription": [{"offsets": {"from": True, "to": 1}, "text": "x"}]},
                   {"transcription": [{"offsets": {"from": 0, "to": float("nan")}, "text": "x"}]}]
        for payload in invalid:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                parse_payload(payload)
        self.assertEqual(parse_payload({"transcription": []}), [])

    def test_optional_subtitle_rendering_handles_hour_rollover(self):
        rows = [Row(3599.9996, 3601.5, "An original sentence.")]
        self.assertIn("01:00:00,000 --> 01:00:01,500", subtitles(rows, "srt"))
        self.assertTrue(subtitles(rows, "vtt").startswith("WEBVTT\n\n"))
        self.assertIn("01:00:00.000 --> 01:00:01.500", subtitles(rows, "vtt"))
        self.assertNotIn("window_start", transcription(rows)[0])


if __name__ == "__main__":
    unittest.main()
