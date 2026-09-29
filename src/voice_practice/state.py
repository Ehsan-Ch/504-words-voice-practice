"""Atomic, validated checkpoints. An output file alone is never completion."""

from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import tempfile
from .transcripts import parse_rows

STATE_VERSION = 1


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def digest(data: object) -> str:
    return hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def metadata(path: Path) -> dict:
    stat = path.stat()
    return {"path": str(path.resolve()), "size": stat.st_size, "mtime_ns": stat.st_mtime_ns}


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def atomic_json(path: Path, value: object) -> None:
    atomic_text(path, json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def valid_checkpoint(marker: Path, fingerprint: str, required: list[Path], transcript: Path) -> bool:
    try:
        value = json.loads(marker.read_text(encoding="utf-8"))
        if not isinstance(value, dict) or value.get("state_version") != STATE_VERSION or value.get("fingerprint") != fingerprint:
            return False
        expected = value.get("outputs")
        if not isinstance(expected, dict) or set(expected) != {path.name for path in required}:
            return False
        if any(not path.is_file() or file_hash(path) != expected[path.name] for path in required):
            return False
        parse_rows(transcript)
        return True
    except (OSError, ValueError, TypeError, UnicodeError):
        return False


def write_checkpoint(marker: Path, fingerprint: str, required: list[Path]) -> None:
    atomic_json(marker, {"state_version": STATE_VERSION, "fingerprint": fingerprint,
                         "outputs": {path.name: file_hash(path) for path in required}})


@contextmanager
def exclusive_run(output_root: Path):
    """OS-released lock prevents concurrent writers and survives abrupt exits.

    The small lock file can remain after exit; only the OS lock is authoritative.
    """
    output_root.mkdir(parents=True, exist_ok=True)
    path = output_root / ".run.lock"
    with path.open("a+b") as stream:
        stream.seek(0, os.SEEK_END)
        if stream.tell() == 0:
            stream.write(b"0")
            stream.flush()
        stream.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise RuntimeError(f"Another process is using output_root: {output_root}") from exc
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == "nt":
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
