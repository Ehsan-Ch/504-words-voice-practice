"""Validate Whisper JSON and render portable transcript formats."""

from dataclasses import dataclass
import json
import math
from pathlib import Path


@dataclass(frozen=True)
class Row:
    start: float
    end: float
    text: str
    window_start: float | None = None

    @property
    def midpoint(self) -> float:
        return (self.start + self.end) / 2.0


def parse_payload(data: object, start: float = 0.0, window: float | None = None) -> list[Row]:
    if not isinstance(data, dict) or not isinstance(data.get("transcription"), list):
        raise ValueError("Whisper JSON requires a transcription array (an empty array is valid silence)")
    rows = []
    for index, segment in enumerate(data["transcription"]):
        if not isinstance(segment, dict) or not isinstance(segment.get("offsets"), dict):
            raise ValueError(f"Segment {index}: missing offsets")
        offsets = segment["offsets"]
        values = [offsets.get("from"), offsets.get("to")]
        if any(isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) for x in values):
            raise ValueError(f"Segment {index}: offsets must be finite numeric milliseconds")
        first, last = values
        if first < 0 or last < first:
            raise ValueError(f"Segment {index}: offsets are negative or reversed")
        text = segment.get("text")
        if not isinstance(text, str):
            raise ValueError(f"Segment {index}: text must be a string")
        text = text.strip()
        if text:
            rows.append(Row(start + first / 1000.0, start + last / 1000.0, text, window))
    return rows


def parse_rows(path: Path, start: float = 0.0, window: float | None = None) -> list[Row]:
    try:
        return parse_payload(json.loads(path.read_text(encoding="utf-8-sig")), start, window)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"Invalid transcript {path}: {exc}") from exc


def transcription(rows: list[Row]) -> list[dict]:
    return [
        {"offsets": {"from": round(row.start * 1000), "to": round(row.end * 1000)}, "text": row.text,
         **({"window_start": row.window_start} if row.window_start is not None else {})}
        for row in rows
    ]


def plain_text(rows: list[Row]) -> str:
    return "".join(row.text + "\n" for row in rows)


def _timestamp(seconds: float, separator: str) -> str:
    milliseconds = round(seconds * 1000)
    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    secs, milliseconds = divmod(milliseconds, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}{separator}{milliseconds:03d}"


def subtitles(rows: list[Row], format: str) -> str:
    if format not in {"srt", "vtt"}:
        raise ValueError("Subtitle format must be srt or vtt")
    separator = "," if format == "srt" else "."
    blocks = []
    for index, row in enumerate(rows, 1):
        # A blank line terminates a subtitle cue; keep each recognized phrase together.
        text = " ".join(row.text.splitlines())
        blocks.append(f"{index}\n{_timestamp(row.start, separator)} --> {_timestamp(row.end, separator)}\n{text}\n\n")
    return ("WEBVTT\n\n" if format == "vtt" else "") + "".join(blocks)
