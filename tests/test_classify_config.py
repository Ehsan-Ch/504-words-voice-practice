from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest

from voice_practice.classify import Classification, classify, normalize
from voice_practice.config import Config, load_config
from voice_practice.pipeline import inventory, inventory_report


class ClassificationTests(unittest.TestCase):
    def test_all_established_routes(self):
        cases = {
            "lesson 1/clip/word.mp4": ("clip", "en", "single"),
            "lesson 1/voice/متن 1.mp3": ("voice", "en", "single"),
            "lesson 1/voice/صبح.mp3": ("voice", "fa", "single"),
            "0 review after lesson6@kharpackbot/review.mp3": ("review", "fa", "windowed_review"),
            "0 help@kharpackbot/help.mp3": ("help", "fa", "single"),
        }
        for path, expected in cases.items():
            with self.subTest(path=path):
                self.assertEqual(classify(path), Classification(*expected))

    def test_unicode_formatting_compatibility_and_case(self):
        self.assertEqual(normalize("\u200f ＶＯＩＣＥ \u200c"), "voice")
        self.assertEqual(classify("درس/\u200fＶＯＩＣＥ/م\u200cتن.mp3").language, "en")
        self.assertEqual(classify(r"lesson\CLIP\Test.MP4").language, "en")
        self.assertEqual(classify("0 REVIEW AFTER LESSON6@KHARPACKBOT/clip/sample.mp3").kind, "review")

    def test_unknown_layout_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unclassified"):
            classify("lesson 1/voice-notes/sample.mp3")


class ConfigAndInventoryTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="voice_config_")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name).resolve()
        self.config = Config(self.root / "course", self.root / "results", self.root / "work",
                             self.root / "whisper", self.root / "model")
        self.config.input_root.mkdir()

    def test_relative_paths_and_defaults(self):
        path = self.root / "config.toml"
        path.write_text('[paths]\ninput_root="course"\noutput_root="results"\nwork_root="work"\nwhisper="whisper"\nmodel="model"\n', encoding="utf-8")
        config = load_config(path)
        self.assertEqual(config.input_root, self.config.input_root)
        self.assertEqual(config.max_context, 64)
        self.assertEqual(config.output_formats, ("json", "txt"))
        self.assertEqual(config.step_seconds, 30.0)

    def test_unknown_setting_is_not_silently_ignored(self):
        path = self.root / "bad.toml"
        path.write_text('[paths]\ninput_root="course"\noutput_root="results"\nwork_root="work"\nwhisper="whisper"\nmodel="model"\n[transcription]\nmax_atempts=2\n', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "max_atempts"):
            load_config(path)

    def test_overlapping_paths_rejected_in_both_directions(self):
        changes = [
            {"output_root": self.config.input_root / "out"},
            {"work_root": self.config.input_root},
            {"output_root": self.root},
            {"work_root": self.config.output_root / "work"},
        ]
        for change in changes:
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, "non-overlapping"):
                replace(self.config, **change).validate()

    def test_invalid_processing_settings_rejected(self):
        cases = [{"window_seconds": 0}, {"step_seconds": 61}, {"silence_min": float("nan")},
                 {"max_edge_error": float("inf")}, {"max_attempts": 0}, {"device": True},
                 {"max_context": 1.5}, {"formats": ("docx",)}, {"silence_noise": "-35dB;command"},
                 {"formats": ("json", "json")}, {"work_root": self.root / "کار"}]
        for change in cases:
            with self.subTest(change=change), self.assertRaises(ValueError):
                replace(self.config, **change).validate()

    def test_unicode_hierarchy_and_same_stem_extensions_stay_distinct(self):
        directory = self.config.input_root / "درس ۱" / "voice"
        directory.mkdir(parents=True)
        for name in ("متن.mp3", "متن.wav"):
            (directory / name).write_bytes(b"original test fixture")
        jobs = inventory(self.config)
        self.assertEqual(len(jobs), 2)
        self.assertEqual(len({job.output_dir(self.config) for job in jobs}), 2)
        self.assertTrue(all(job.classification.language == "en" for job in jobs))
        self.assertEqual(jobs[0].output_dir(self.config), self.config.output_root / "درس ۱" / "voice" / "متن.mp3")
        self.assertEqual(inventory_report(jobs, self.config)["classification"], {"voice/en/single": 2})
        self.assertFalse(self.config.output_root.exists())
        self.assertFalse(self.config.work_root.exists())

    def test_inventory_is_sorted_limited_and_ignores_other_files(self):
        directory = self.config.input_root / "clip"
        directory.mkdir()
        for name in ("b.mp4", "a.mp4", "notes.txt"):
            (directory / name).write_text("fixture", encoding="utf-8")
        self.assertEqual([job.relative.as_posix() for job in inventory(self.config, 1)], ["clip/a.mp4"])
        with self.assertRaises(ValueError):
            inventory(self.config, 0)

    def test_symlinked_directory_is_not_ingested(self):
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "private.mp3").write_bytes(b"private")
        (self.config.input_root / "clip").mkdir()
        (self.config.input_root / "clip" / "original.mp3").write_bytes(b"original")
        try:
            (self.config.input_root / "clip" / "link").symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("Directory symlinks unavailable without platform privileges")
        self.assertEqual(len(inventory(self.config)), 1)


if __name__ == "__main__":
    unittest.main()
