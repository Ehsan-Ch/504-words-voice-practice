"""External tools, with the validated Vulkan inference command unchanged."""

import math
import logging
import os
from pathlib import Path
import re
import shutil
import subprocess
from .config import Config


def run_command(command: list[str | Path], label: str) -> subprocess.CompletedProcess:
    try:
        result = subprocess.run([str(part) for part in command], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, encoding="utf-8", errors="replace", check=False)
    except OSError as exc:
        raise RuntimeError(f"Cannot start {label}: {exc}. Check the configured executable and PATH.") from exc
    if result.returncode:
        tail = (result.stderr or result.stdout)[-4000:]
        raise RuntimeError(f"{label} failed (exit {result.returncode}):\n{tail}")
    return result


def parse_silences(stderr: str, overlap_start: float, overlap_len: float) -> list[tuple[float, float]]:
    """Pair ordered silence events, including silence reaching the clip's end."""
    pending = None
    pairs = []
    for event, raw in re.findall(r"silence_(start|end):\s*(-?\d+(?:\.\d+)?(?:e[+-]?\d+)?)", stderr, flags=re.I):
        value = min(overlap_len, max(0.0, float(raw)))
        if event == "start":
            pending = value
        else:
            first = pending if pending is not None else 0.0
            if value >= first:
                pairs.append((overlap_start + first, overlap_start + value))
            pending = None
    if pending is not None and pending < overlap_len:
        pairs.append((overlap_start + pending, overlap_start + overlap_len))
    return pairs


class MediaTools:
    def __init__(self, config: Config, logger: logging.Logger | None = None):
        self.config = config
        self.logger = logger

    def duration(self, source: Path) -> float:
        result = run_command([self.config.ffprobe, "-v", "error", "-show_entries", "format=duration",
                              "-of", "default=nw=1:nk=1", source], "ffprobe")
        try:
            duration = float(result.stdout.strip())
        except ValueError as exc:
            raise RuntimeError(f"ffprobe returned an invalid duration for {source}: {result.stdout!r}") from exc
        if not math.isfinite(duration) or duration <= 0:
            raise RuntimeError(f"ffprobe returned a nonpositive/nonfinite duration for {source}: {duration}")
        return duration

    def convert(self, source: Path, wav: Path, start: float | None = None, duration: float | None = None) -> None:
        wav.parent.mkdir(parents=True, exist_ok=True)
        command = [self.config.ffmpeg, "-y", "-hide_banner", "-loglevel", "error"]
        if start is not None:
            command += ["-ss", f"{start:.3f}"]
        if duration is not None:
            command += ["-t", f"{duration:.3f}"]
        command += ["-i", source, "-vn", "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", wav]
        run_command(command, "ffmpeg audio conversion")

    def transcribe(self, wav: Path, prefix: Path, language: str) -> Path:
        prefix.parent.mkdir(parents=True, exist_ok=True)
        result = run_command([self.config.whisper, "-m", self.config.model, "-f", wav,
                              "-l", language, "-dev", str(self.config.device), "-mc", str(self.config.max_context),
                              "-oj", "-of", prefix], "whisper-cli")
        if self.logger is not None:
            # Includes backend/device messages needed to verify actual GPU use.
            # These machine-specific diagnostics stay in private output/run.log.
            self.logger.info("whisper-cli diagnostics:\n%s\n%s", result.stdout.rstrip(), result.stderr.rstrip())
        path = Path(str(prefix) + ".json")
        if not path.is_file():
            raise RuntimeError(f"Whisper finished without creating JSON: {path}")
        return path

    def silences(self, source: Path, start: float, duration: float) -> list[tuple[float, float]]:
        result = run_command([self.config.ffmpeg, "-hide_banner", "-ss", f"{start:.3f}", "-t", f"{duration:.3f}",
                              "-i", source, "-af", f"silencedetect=noise={self.config.silence_noise}:d={self.config.silence_min}",
                              "-f", "null", os.devnull], "ffmpeg silence detection")
        return parse_silences(result.stderr, start, duration)


def doctor(config: Config) -> list[dict]:
    """Read-only dependency checks; never starts transcription or loads the model."""
    checks = []
    for name, path in (("input_root", config.input_root), ("whisper", config.whisper), ("model", config.model)):
        ok = path.is_dir() if name == "input_root" else path.is_file() and path.stat().st_size > 0
        checks.append({"check": name, "ok": ok, "detail": str(path)})
    for name in ("ffmpeg", "ffprobe"):
        executable = getattr(config, name)
        found = shutil.which(executable)
        ok, detail = bool(found), found or f"Not found: {executable}"
        if found:
            try:
                result = run_command([found, "-version"], name)
                detail = (result.stdout or result.stderr).splitlines()[0]
            except (RuntimeError, IndexError) as exc:
                ok, detail = False, str(exc)
        checks.append({"check": name, "ok": ok, "detail": detail})
    # Presence of a binary does not establish Vulkan support or successful inference.
    checks.append({"check": "gpu_inference", "ok": None,
                   "detail": "Not tested by doctor. Use run --limit 1 and inspect the whisper/Vulkan diagnostics in output_root/run.log."})
    return checks
