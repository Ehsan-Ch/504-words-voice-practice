import json
import logging
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from voice_practice.config import Config
from voice_practice.media import MediaTools, run_command


class NativeContractTests(unittest.TestCase):
    def test_validated_inference_flags_and_diagnostics_are_preserved(self):
        with tempfile.TemporaryDirectory(prefix="voice_native_") as directory:
            root = Path(directory)
            config = Config(root / "input", root / "output", root / "work",
                            root / "whisper", root / "large-v3.bin")
            prefix = root / "result"
            prefix.with_suffix(".json").write_text('{"transcription": []}', encoding="utf-8")
            result = subprocess.CompletedProcess([], 0, "", "using Vulkan0 backend")
            logger = logging.getLogger("native_contract_test")
            with patch("voice_practice.media.run_command", return_value=result) as command:
                with self.assertLogs(logger, level="INFO") as captured:
                    MediaTools(config, logger).transcribe(root / "input.wav", prefix, "fa")
            args = [str(part) for part in command.call_args.args[0]]
            self.assertEqual(args[1:], ["-m", str(config.model), "-f", str(root / "input.wav"),
                                      "-l", "fa", "-dev", "0", "-mc", "64", "-oj", "-of", str(prefix)])
            self.assertIn("using Vulkan0 backend", "\n".join(captured.output))

    def test_native_failure_retains_reason_and_executable_advice(self):
        with patch("voice_practice.media.subprocess.run", side_effect=FileNotFoundError("missing")):
            with self.assertRaisesRegex(RuntimeError, "Cannot start.*configured executable"):
                run_command(["absent-tool"], "whisper-cli")
        failure = subprocess.CompletedProcess([], 17, "", "model could not be loaded")
        with patch("voice_practice.media.subprocess.run", return_value=failure):
            with self.assertRaisesRegex(RuntimeError, r"exit 17.*\nmodel could not be loaded"):
                run_command(["fake-tool"], "whisper-cli")

    def test_cli_dry_run_needs_no_model_and_creates_no_outputs(self):
        with tempfile.TemporaryDirectory(prefix="voice_cli_") as directory:
            root = Path(directory)
            source = root / "input" / "clip"
            source.mkdir(parents=True)
            (source / "original.wav").write_bytes(b"original placeholder, never decoded")
            config = root / "config.toml"
            config.write_text('[paths]\ninput_root="input"\noutput_root="output"\n'
                              'work_root="work"\nwhisper="missing-whisper"\nmodel="missing-model"\n',
                              encoding="utf-8")
            result = subprocess.run([sys.executable, "-m", "voice_practice", "dry-run",
                                     "--config", str(config), "--limit", "1"],
                                    capture_output=True, text=True, encoding="utf-8", check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["classification"], {"clip/en/single": 1})
            self.assertFalse((root / "output").exists())
            self.assertFalse((root / "work").exists())


if __name__ == "__main__":
    unittest.main()
