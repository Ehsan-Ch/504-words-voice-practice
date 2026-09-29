"""Portable TOML configuration and source/output isolation checks."""

from dataclasses import dataclass, fields
import math
from pathlib import Path
import re
import tomllib

MEDIA_EXTENSIONS = frozenset({".mp3", ".mp4", ".m4a", ".wav", ".ogg", ".opus", ".flac", ".aac", ".wma", ".mkv", ".webm", ".mov", ".avi"})


def overlaps(a: Path, b: Path) -> bool:
    a, b = a.resolve(), b.resolve()
    return a == b or a in b.parents or b in a.parents


@dataclass(frozen=True)
class Config:
    input_root: Path
    output_root: Path
    work_root: Path
    whisper: Path
    model: Path
    ffmpeg: str = "ffmpeg"
    ffprobe: str = "ffprobe"
    device: int = 0
    max_context: int = 64
    window_seconds: float = 60.0
    step_seconds: float = 30.0
    max_edge_error: float = 1.6
    silence_noise: str = "-35dB"
    silence_min: float = 0.25
    max_attempts: int = 3
    formats: tuple[str, ...] = ("json", "txt")

    def validate(self) -> None:
        for name in ("window_seconds", "step_seconds", "silence_min"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be a positive finite number")
        if self.step_seconds > self.window_seconds:
            raise ValueError("step_seconds cannot exceed window_seconds (would omit audio)")
        if not isinstance(self.max_edge_error, (int, float)) or isinstance(self.max_edge_error, bool) or not math.isfinite(self.max_edge_error) or self.max_edge_error < 0:
            raise ValueError("max_edge_error must be finite and nonnegative")
        for name, minimum in (("max_attempts", 1), ("device", 0), ("max_context", 0)):
            value = getattr(self, name)
            if type(value) is not int or value < minimum:
                raise ValueError(f"{name} must be an integer >= {minimum}")
        if not isinstance(self.silence_noise, str) or not re.fullmatch(r"-?\d+(?:\.\d+)?dB", self.silence_noise):
            raise ValueError("silence_noise must be a decibel value such as '-35dB'")
        if not self.formats or any(x not in {"json", "txt", "srt", "vtt"} for x in self.formats):
            raise ValueError("formats supports json, txt, srt and vtt")
        if len(set(self.formats)) != len(self.formats):
            raise ValueError("formats must not contain duplicates")
        for a, b in ((self.input_root, self.output_root), (self.input_root, self.work_root), (self.output_root, self.work_root)):
            if overlaps(a, b):
                raise ValueError(f"Input, output and work directories must be separate, non-overlapping trees: {a} / {b}")
        if not str(self.work_root.resolve()).isascii():
            raise ValueError("work_root must resolve to an ASCII-only path for whisper.cpp; course and output paths may contain Unicode")

    @property
    def output_formats(self) -> tuple[str, ...]:
        """The established JSON/TXT deliverables are always produced."""
        return tuple(dict.fromkeys(("json", "txt", *self.formats)))

    def processing_settings(self) -> dict:
        return {f.name: getattr(self, f.name) for f in fields(self) if f.name not in {"input_root", "output_root", "work_root", "whisper", "model", "ffmpeg", "ffprobe", "max_attempts"}}


def load_config(path: Path | str) -> Config:
    path = Path(path).resolve()
    with path.open("rb") as stream:
        data = tomllib.load(stream)
    if set(data) - {"paths", "transcription"}:
        raise ValueError(f"Unknown config sections: {sorted(set(data) - {'paths', 'transcription'})}")
    paths = data.get("paths", {})
    trans = data.get("transcription", {})
    if not isinstance(paths, dict) or not isinstance(trans, dict):
        raise ValueError("[paths] and [transcription] must be TOML tables")
    path_keys = {"input_root", "output_root", "work_root", "whisper", "model", "ffmpeg", "ffprobe"}
    trans_keys = {f.name for f in fields(Config)} - path_keys
    unknown = (set(paths) - path_keys) | (set(trans) - trans_keys)
    if unknown:
        raise ValueError(f"Unknown configuration keys: {sorted(unknown)}")
    values = dict(trans)
    for key in ("input_root", "output_root", "work_root", "whisper", "model"):
        if not isinstance(paths.get(key), str) or not paths[key].strip():
            raise ValueError(f"Missing or invalid [paths].{key}")
        value = Path(paths[key]).expanduser()
        values[key] = (value if value.is_absolute() else path.parent / value).resolve()
    for key in ("ffmpeg", "ffprobe"):
        value = paths.get(key, key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"[paths].{key} must be an executable name or path")
        if "/" in value or "\\" in value:
            executable = Path(value).expanduser()
            value = str((executable if executable.is_absolute() else path.parent / executable).resolve())
        values[key] = value
    if "formats" in values:
        if not isinstance(values["formats"], list) or not all(isinstance(x, str) for x in values["formats"]):
            raise ValueError("formats must be an array of strings")
        values["formats"] = tuple(values["formats"])
    config = Config(**values)
    config.validate()
    return config
