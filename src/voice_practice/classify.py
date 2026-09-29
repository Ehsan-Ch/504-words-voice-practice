"""Course-specific routing recovered from the completed batch runner."""

from dataclasses import dataclass
from pathlib import Path
import unicodedata


@dataclass(frozen=True)
class Classification:
    kind: str
    language: str
    mode: str


def normalize(text: str) -> str:
    """Ignore compatibility, case and invisible formatting differences."""
    text = unicodedata.normalize("NFKC", text)
    return "".join(c for c in text if unicodedata.category(c) != "Cf").strip().casefold()


def classify(source: Path | str) -> Classification:
    """Route a course-relative path; unknown structures fail explicitly.

    Both slash styles are accepted so Windows paths can be tested on Linux.
    Routing precedence is identical to the final working runner.
    """
    parts = [normalize(p) for p in str(source).replace("\\", "/").split("/")]
    stem = normalize(Path(str(source).replace("\\", "/")).stem)
    if normalize("0 review after lesson6@kharpackbot") in parts:
        return Classification("review", "fa", "windowed_review")
    if "clip" in parts:
        return Classification("clip", "en", "single")
    if "voice" in parts:
        return Classification("voice", "en" if normalize("متن") in stem else "fa", "single")
    if normalize("0 help@kharpackbot") in parts:
        return Classification("help", "fa", "single")
    raise ValueError(f"Unclassified course path: {source}. Use the documented course folder layout.")
