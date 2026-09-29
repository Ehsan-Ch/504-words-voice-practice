from dataclasses import replace
import json
import logging
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from voice_practice.config import Config
from voice_practice.pipeline import inventory, run_batch
from voice_practice.state import atomic_json, exclusive_run, write_checkpoint


class FakeMedia:
    """Original deterministic utterances; no real media/model/GPU is used."""
    def __init__(self, duration=65, failures=0, malformed=0, interrupt_call=None):
        self.seconds = duration
        self.failures = failures
        self.malformed = malformed
        self.interrupt_call = interrupt_call
        self.calls = 0
        self.conversions = []
        self.requests = {}

    def duration(self, source):
        return self.seconds

    def convert(self, source, wav, start=None, duration=None):
        self.conversions.append((start, duration))
        self.requests[wav] = (start, duration)
        self.assert_ascii(wav)
        wav.write_bytes(b"synthetic audio placeholder; never decoded")

    @staticmethod
    def assert_ascii(path):
        if not str(path).isascii():
            raise AssertionError("Whisper work path is not ASCII")

    def transcribe(self, wav, prefix, language):
        self.assert_ascii(prefix)
        self.calls += 1
        if self.calls == self.interrupt_call:
            raise KeyboardInterrupt()
        if self.calls <= self.failures:
            raise RuntimeError("Synthetic backend failure")
        path = Path(str(prefix) + ".json")
        if self.calls <= self.malformed:
            path.write_text('{"transcription":', encoding="utf-8")
        else:
            atomic_json(path, {"transcription": [
                {"offsets": {"from": 0, "to": 10000}, "text": "I opened my notebook."},
                {"offsets": {"from": 20000, "to": 30000}, "text": "Please describe the room."},
            ]})
        return path

    def silences(self, source, start, duration):
        return []


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="voice_pipeline_")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name).resolve()
        self.config = Config(self.root / "درس", self.root / "نتیجه", self.root / "work",
                             self.root / "whisper", self.root / "model")
        self.config.whisper.write_bytes(b"original placeholder executable")
        self.config.model.write_bytes(b"original placeholder model")
        source_dir = self.config.input_root / "lesson 1" / "voice"
        source_dir.mkdir(parents=True)
        self.source = source_dir / "متن.mp3"
        self.source.write_bytes(b"original source placeholder")
        self.logger = logging.getLogger("voice_practice_tests")
        self.logger.handlers = [logging.NullHandler()]
        self.logger.propagate = False
        logger_patch = patch("voice_practice.pipeline._logger", return_value=self.logger)
        logger_patch.start()
        self.addCleanup(logger_patch.stop)

    def output(self, source=None):
        return self.config.output_root / (source or self.source).relative_to(self.config.input_root)

    def run_fake(self, media=None, config=None):
        return run_batch(config or self.config, media=media or FakeMedia())

    def test_success_and_resume_requires_no_second_inference(self):
        media = FakeMedia()
        result = self.run_fake(media)
        self.assertEqual(result["completed_this_run"], 1)
        self.assertEqual(result["failed_this_run"], 0)
        self.assertTrue((self.output() / ".complete.json").is_file())
        final = json.loads((self.output() / "final.json").read_text(encoding="utf-8"))
        self.assertEqual(final["language"], "en")
        self.assertEqual(final["transcription"][0]["text"], "I opened my notebook.")
        result = self.run_fake(media)
        self.assertEqual(result["already_complete"], 1)
        self.assertEqual(media.calls, 1)

    def test_json_without_marker_is_not_completion(self):
        self.output().mkdir(parents=True)
        atomic_json(self.output() / "final.json", {"transcription": []})
        media = FakeMedia()
        result = self.run_fake(media)
        self.assertEqual(result["completed_this_run"], 1)
        self.assertEqual(media.calls, 1)
        self.assertTrue((self.output() / "final.txt").is_file())

    def test_missing_or_corrupted_final_repairs_from_valid_raw(self):
        media = FakeMedia()
        self.run_fake(media)
        (self.output() / "final.txt").unlink()
        self.assertEqual(self.run_fake(media)["completed_this_run"], 1)
        self.assertEqual(media.calls, 1)
        (self.output() / "final.json").write_text("broken json", encoding="utf-8")
        self.assertEqual(self.run_fake(media)["completed_this_run"], 1)
        self.assertEqual(media.calls, 1)

    def test_corrupted_raw_cache_cannot_be_reused(self):
        media = FakeMedia()
        self.run_fake(media)
        (self.output() / "final.txt").unlink()
        (self.output() / "raw.json").write_text('{"transcription": [', encoding="utf-8")
        self.assertEqual(self.run_fake(media)["completed_this_run"], 1)
        self.assertEqual(media.calls, 2)

    def test_raw_json_without_cache_marker_is_not_trusted(self):
        self.output().mkdir(parents=True)
        atomic_json(self.output() / "raw.json", {"transcription": []})
        media = FakeMedia()
        self.run_fake(media)
        self.assertEqual(media.calls, 1)

    def test_same_size_same_mtime_source_change_is_detected_by_hash(self):
        media = FakeMedia()
        self.run_fake(media)
        source_stat = self.source.stat()
        data = self.source.read_bytes()
        self.source.write_bytes(b"X" + data[1:])
        os.utime(self.source, ns=(source_stat.st_atime_ns, source_stat.st_mtime_ns))
        self.assertEqual(self.run_fake(media)["completed_this_run"], 1)
        self.assertEqual(media.calls, 2)

    def test_model_metadata_and_processing_config_invalidate_results(self):
        media = FakeMedia()
        self.run_fake(media)
        self.config.model.write_bytes(b"changed model metadata and size")
        self.assertEqual(self.run_fake(media)["completed_this_run"], 1)
        self.assertEqual(media.calls, 2)
        self.assertEqual(self.run_fake(media, replace(self.config, max_context=32))["completed_this_run"], 1)
        self.assertEqual(media.calls, 3)

    def test_failure_retries_then_completes_and_records_attempt(self):
        media = FakeMedia(failures=1)
        result = self.run_fake(media)
        self.assertEqual(result["completed_this_run"], 1)
        self.assertEqual(result["failed_this_run"], 0)
        self.assertEqual(media.calls, 2)
        failures = [json.loads(line) for line in (self.config.output_root / "failures.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(failures), 1)
        self.assertFalse(failures[0]["exhausted"])

    def test_exhausted_failure_never_marks_complete(self):
        media = FakeMedia(failures=99)
        result = self.run_fake(media)
        self.assertEqual(result["failed_this_run"], 1)
        self.assertEqual(result["completed_this_run"], 0)
        self.assertEqual(media.calls, 3)
        self.assertFalse((self.output() / ".complete.json").exists())

    def test_malformed_whisper_json_is_retried(self):
        media = FakeMedia(malformed=1)
        result = self.run_fake(media)
        self.assertEqual(result["completed_this_run"], 1)
        self.assertEqual(media.calls, 2)
        self.assertTrue((self.output() / ".complete.json").exists())

    def test_review_offsets_partial_tail_and_valid_window_resume(self):
        self.source.unlink()
        review_dir = self.config.input_root / "0 review after lesson6@kharpackbot"
        review_dir.mkdir()
        self.source = review_dir / "مرور.mp3"
        self.source.write_bytes(b"original review placeholder")
        media = FakeMedia(duration=65, interrupt_call=2)
        with self.assertRaises(KeyboardInterrupt):
            self.run_fake(media)
        summary = json.loads((self.config.output_root / "summary.json").read_text(encoding="utf-8"))
        self.assertTrue(summary["interrupted"])
        self.assertEqual(summary["completed_this_run"], 0)
        self.assertFalse((self.output() / ".complete.json").exists())
        media.interrupt_call = None
        result = self.run_fake(media)
        self.assertEqual(result["completed_this_run"], 1)
        # First window survived the interrupted second inference.
        self.assertEqual(media.calls, 3)
        self.assertEqual(media.conversions, [(0.0, 60.0), (30.0, 35.0), (30.0, 35.0)])
        final = json.loads((self.output() / "final.json").read_text(encoding="utf-8"))
        self.assertEqual(final["merge"]["seams"][0]["seam"], 45)
        self.assertEqual(final["transcription"][-1]["offsets"], {"from": 50000, "to": 60000})
        self.assertEqual(final["transcription"][-1]["window_start"], 30)

    def test_interrupt_after_output_before_completion_marker_recovers(self):
        media = FakeMedia()
        def interrupt_final(marker, fingerprint, required):
            if marker.name == ".complete.json":
                raise KeyboardInterrupt()
            return write_checkpoint(marker, fingerprint, required)
        with patch("voice_practice.pipeline.write_checkpoint", side_effect=interrupt_final):
            with self.assertRaises(KeyboardInterrupt):
                self.run_fake(media)
        self.assertFalse((self.output() / ".complete.json").exists())
        self.assertEqual(self.run_fake(media)["completed_this_run"], 1)
        self.assertEqual(media.calls, 1)

    def test_optional_exporters_are_part_of_completion(self):
        config = replace(self.config, formats=("json", "txt", "srt", "vtt"))
        media = FakeMedia()
        self.run_fake(media, config)
        self.assertTrue((self.output() / "final.vtt").read_text(encoding="utf-8").startswith("WEBVTT"))
        (self.output() / "final.srt").unlink()
        self.assertEqual(self.run_fake(media, config)["completed_this_run"], 1)
        self.assertEqual(media.calls, 1)

    def test_changed_source_mid_job_is_not_certified(self):
        media = FakeMedia()
        real_transcribe = media.transcribe
        def change_source(*args):
            result = real_transcribe(*args)
            self.source.write_bytes(b"changed while whisper was running")
            return result
        media.transcribe = change_source
        result = self.run_fake(media, replace(self.config, max_attempts=1))
        self.assertEqual(result["failed_this_run"], 1)
        self.assertFalse((self.output() / ".complete.json").exists())

    def test_os_lock_excludes_concurrent_writer_and_releases(self):
        with exclusive_run(self.config.output_root):
            with self.assertRaisesRegex(RuntimeError, "Another process"):
                with exclusive_run(self.config.output_root):
                    self.fail("Second writer acquired the lock")
        with exclusive_run(self.config.output_root):
            pass


if __name__ == "__main__":
    unittest.main()
