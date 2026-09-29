"""Explicit batch execution, isolated work paths and validated resumption."""

from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
import shutil
import stat
import uuid

from .classify import Classification, classify
from .config import Config, MEDIA_EXTENSIONS
from .media import MediaTools
from .merge import choose_seam, merge_windows, review_starts
from .state import atomic_json, atomic_text, digest, exclusive_run, file_hash, metadata, valid_checkpoint, write_checkpoint
from .transcripts import parse_rows, plain_text, subtitles, transcription


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass(frozen=True)
class Job:
    source: Path
    relative: Path
    classification: Classification

    def output_dir(self, config: Config) -> Path:
        # Retain the extension as a directory component: lesson.wav != lesson.mp3.
        output = config.output_root / self.relative
        if not output.resolve().is_relative_to(config.output_root.resolve()):
            raise ValueError(f"Output path escapes output_root: {output}")
        return output


def inventory(config: Config, limit: int | None = None) -> list[Job]:
    config.validate()
    if limit is not None and (type(limit) is not int or limit <= 0):
        raise ValueError("limit must be a positive integer")
    root = config.input_root.resolve()
    if not root.is_dir():
        raise ValueError(f"Input directory does not exist: {root}")
    jobs = []
    def walk_error(error: OSError) -> None:
        raise error

    def is_link_or_junction(path: Path) -> bool:
        attributes = path.lstat()
        # Windows reparse points include junctions; this also works on 3.11,
        # before os.path.isjunction was added. Never descend linked trees.
        return stat.S_ISLNK(attributes.st_mode) or bool(
            getattr(attributes, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
        )

    for directory, directories, files in os.walk(root, followlinks=False, onerror=walk_error):
        # Avoid following symlinks/junctions into other course trees or outputs.
        directories[:] = sorted(name for name in directories if not is_link_or_junction(Path(directory) / name))
        for name in sorted(files):
            source = Path(directory) / name
            if source.suffix.lower() not in MEDIA_EXTENSIONS or is_link_or_junction(source):
                continue
            if not source.resolve().is_relative_to(root):
                raise ValueError(f"Source escapes input_root: {source}")
            relative = source.relative_to(root)
            jobs.append(Job(source, relative, classify(relative)))
    jobs.sort(key=lambda job: job.relative.as_posix())
    if not jobs:
        raise ValueError(f"No supported audio/video files found below {root}")
    return jobs[:limit] if limit else jobs


def inventory_report(jobs: list[Job], config: Config) -> dict:
    counts = Counter(f"{j.classification.kind}/{j.classification.language}/{j.classification.mode}" for j in jobs)
    return {"total": len(jobs), "classification": dict(sorted(counts.items())), "jobs": [
        {"source": str(job.source), "relative": job.relative.as_posix(), "output": str(job.output_dir(config)),
         **asdict(job.classification)} for job in jobs]}


def _executable_metadata(value: str | Path) -> dict:
    resolved = shutil.which(str(value))
    return metadata(Path(resolved)) if resolved else {"configured": str(value), "unresolved": True}


def dependency_identity(config: Config) -> dict:
    return {"model": metadata(config.model), "whisper": metadata(config.whisper),
            "ffmpeg": _executable_metadata(config.ffmpeg), "ffprobe": _executable_metadata(config.ffprobe)}


def job_identity(job: Job, config: Config) -> dict:
    return {"pipeline_version": 1, "source": {**metadata(job.source), "sha256": file_hash(job.source)},
            "relative": job.relative.as_posix(), "classification": asdict(job.classification),
            "settings": config.processing_settings(), "dependencies": dependency_identity(config)}


def _raw_rows(job: Job, config: Config, media: MediaTools, job_dir: Path, work: Path,
              fingerprint: str, name: str, start: float | None, duration: float | None,
              logger: logging.Logger):
    raw = job_dir / f"{name}.json"
    marker = job_dir / f".{name}.complete.json"
    stage_fingerprint = digest({"job": fingerprint, "stage": name, "start": start, "duration": duration})
    if not valid_checkpoint(marker, stage_fingerprint, [raw], raw):
        marker.unlink(missing_ok=True)
        pending = work / uuid.uuid4().hex
        pending.mkdir(parents=True)
        wav, prefix = pending / "input.wav", pending / "whisper"
        produced = pending / "whisper.json"
        try:
            logger.info("Converting and transcribing %s (%s, %s)", job.relative, job.classification.language, name)
            media.convert(job.source, wav, start=start, duration=duration)
            result = media.transcribe(wav, prefix, job.classification.language)
            if result.resolve() != produced.resolve():
                raise RuntimeError("Transcriber returned an unexpected output path")
            parse_rows(result)
            atomic_text(raw, result.read_text(encoding="utf-8-sig"))
            write_checkpoint(marker, stage_fingerprint, [raw])
        finally:
            # Only remove the two files created for this attempt; never recurse.
            wav.unlink(missing_ok=True)
            produced.unlink(missing_ok=True)
            try:
                pending.rmdir()
            except OSError:
                pass
    else:
        logger.info("Reusing validated window: %s / %s", job.relative, name)
    return parse_rows(raw, start=start or 0.0, window=start)


def process_job(job: Job, config: Config, media: MediaTools, logger: logging.Logger) -> str:
    identity = job_identity(job, config)
    fingerprint = digest(identity)
    job_dir = job.output_dir(config)
    job_dir.mkdir(parents=True, exist_ok=True)
    required = [job_dir / f"final.{format}" for format in config.output_formats] + [job_dir / "source.json"]
    if job.classification.mode == "windowed_review":
        required.append(job_dir / "merge_meta.json")
    marker = job_dir / ".complete.json"
    if valid_checkpoint(marker, fingerprint, required, job_dir / "final.json"):
        return "already_complete"
    marker.unlink(missing_ok=True)
    work = config.work_root / digest({"source": str(job.source.resolve()), "output": str(job_dir.resolve())})[:24]
    work.mkdir(parents=True, exist_ok=True)
    merge = None
    if job.classification.mode == "single":
        rows = _raw_rows(job, config, media, job_dir, work, fingerprint, "raw", None, None, logger)
    else:
        duration = media.duration(job.source)
        starts = review_starts(duration, config.window_seconds, config.step_seconds)
        windows = []
        for index, start in enumerate(starts):
            length = min(config.window_seconds, max(0.1, duration - start))
            windows.append(_raw_rows(job, config, media, job_dir, work, fingerprint,
                           f"window_{index:04d}_{round(start):06d}", start, length, logger))
        seams = []
        for index in range(len(windows) - 1):
            first = starts[index + 1]
            length = max(0.0, min(starts[index] + config.window_seconds, duration) - first)
            silences = media.silences(job.source, first, length) if length > 0 else []
            seams.append(choose_seam(windows[index], windows[index + 1], first, length, silences, config.max_edge_error))
        rows = merge_windows(windows, seams)
        merge = {"review_duration_seconds": duration, "window_seconds": config.window_seconds,
                 "step_seconds": config.step_seconds, "max_edge_error": config.max_edge_error, "seams": seams}
        atomic_json(job_dir / "merge_meta.json", merge)
    # Do not certify results if the source or dependency files changed mid-job.
    if job_identity(job, config) != identity:
        raise RuntimeError(f"Input, model or executable changed during processing: {job.source}. Retry after the files stop changing.")
    payload = {"source": str(job.source), **asdict(job.classification), "completed_at": now(),
               "transcription": transcription(rows)}
    if merge is not None:
        payload["merge"] = merge
    atomic_json(job_dir / "final.json", payload)
    atomic_text(job_dir / "final.txt", plain_text(rows))
    for format in config.output_formats:
        if format in {"srt", "vtt"}:
            atomic_text(job_dir / f"final.{format}", subtitles(rows, format))
    atomic_json(job_dir / "source.json", identity)
    parse_rows(job_dir / "final.json")
    # This is deliberately the final durable write for the job.
    write_checkpoint(marker, fingerprint, required)
    try:
        work.rmdir()
    except OSError:
        pass
    return "completed_this_run"


def _logger(output: Path) -> logging.Logger:
    logger = logging.getLogger(f"voice_practice.{uuid.uuid4().hex}")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    for handler in (logging.StreamHandler(), logging.FileHandler(output / "run.log", encoding="utf-8")):
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


def run_batch(config: Config, jobs: list[Job] | None = None, media: MediaTools | None = None) -> dict:
    """Run explicitly selected jobs. KeyboardInterrupt propagates after a summary."""
    config.validate()
    jobs = inventory(config) if jobs is None else jobs
    # Validate supplied Job objects too; public API calls must not bypass isolation.
    for job in jobs:
        if not job.source.resolve().is_relative_to(config.input_root.resolve()) or job.relative != job.source.relative_to(config.input_root):
            raise ValueError(f"Job is outside the configured input hierarchy: {job.source}")
        if job.classification != classify(job.relative):
            raise ValueError(f"Job classification does not match its course path: {job.source}")
    counts = {"total": len(jobs), "completed_this_run": 0, "already_complete": 0, "failed_this_run": 0,
              "interrupted": False, "started_at": now()}
    with exclusive_run(config.output_root), exclusive_run(config.work_root):
        logger = _logger(config.output_root)
        media = media or MediaTools(config, logger)
        try:
            for index, job in enumerate(jobs, 1):
                logger.info("[%s/%s] %s", index, len(jobs), job.relative)
                for attempt in range(1, config.max_attempts + 1):
                    try:
                        result = process_job(job, config, media, logger)
                        counts[result] += 1
                        logger.info("%s: %s", result, job.relative)
                        break
                    except Exception as exc:
                        logger.error("Attempt %s/%s: %s", attempt, config.max_attempts, exc)
                        with (config.output_root / "failures.jsonl").open("a", encoding="utf-8") as stream:
                            stream.write(json.dumps({"time": now(), "source": str(job.source), "attempt": attempt,
                                                     "exhausted": attempt == config.max_attempts, "error": str(exc)}, ensure_ascii=False) + "\n")
                        if attempt == config.max_attempts:
                            counts["failed_this_run"] += 1
                atomic_json(config.output_root / "summary.json", {**counts, "updated_at": now()})
        except KeyboardInterrupt:
            counts["interrupted"] = True
            logger.warning("Interrupted. Re-run the same command to resume validated checkpoints.")
            raise
        finally:
            atomic_json(config.output_root / "summary.json", {**counts, "updated_at": now()})
            for handler in list(logger.handlers):
                handler.close()
                logger.removeHandler(handler)
    return counts
