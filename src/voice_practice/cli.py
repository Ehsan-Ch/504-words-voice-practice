"""A read-first CLI: transcription requires the explicit `run` command."""

import argparse
import json
from pathlib import Path
import sys
import tomllib

from . import __version__
from .config import load_config
from .media import doctor
from .pipeline import inventory, inventory_report, run_batch


def positive_integer(value: str) -> int:
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a positive integer") from exc
    if number <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Supporting transcription pipeline for 504 Words Voice Practice. No command runs automatically.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)
    descriptions = {
        "inventory": "List supported media, language routing and output paths; read-only.",
        "dry-run": "Preview the planned jobs and established inference settings; read-only.",
        "doctor": "Check paths and FFmpeg tools without loading the model or starting inference.",
        "run": "Explicitly transcribe the selected jobs, resuming only validated checkpoints.",
    }
    for name, description in descriptions.items():
        command = commands.add_parser(name, help=description, description=description)
        command.add_argument("--config", type=Path, required=True, help="TOML file; relative paths resolve beside this file")
        if name != "doctor":
            command.add_argument("--limit", type=positive_integer, help="Use the first N jobs in sorted relative-path order (recommended for an initial smoke test)")
    return parser


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    args = build_parser().parse_args(argv)
    try:
        config = load_config(args.config)
        if args.command == "doctor":
            checks = doctor(config)
            print(json.dumps({"checks": checks}, ensure_ascii=False, indent=2))
            return int(any(item["ok"] is False for item in checks))
        jobs = inventory(config, args.limit)
        if args.command in {"inventory", "dry-run"}:
            report = inventory_report(jobs, config)
            if args.command == "dry-run":
                report["settings"] = config.processing_settings()
                report["inference"] = "whisper-cli -m MODEL -f ASCII_WORK_WAV -l ROUTED_LANGUAGE -dev DEVICE -mc MAX_CONTEXT -oj -of ASCII_WORK_PREFIX"
                report["note"] = "Read-only preview. No model loading, conversion or transcription was performed."
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 0
        checks = doctor(config)
        errors = [f"{item['check']}: {item['detail']}" for item in checks if item["ok"] is False]
        if errors:
            raise ValueError("Preflight failed:\n" + "\n".join(errors))
        counts = run_batch(config, jobs)
        print(json.dumps(counts, ensure_ascii=False, indent=2))
        return int(counts["failed_this_run"] > 0)
    except KeyboardInterrupt:
        print("Interrupted. Re-run the same command to resume validated checkpoints.", file=sys.stderr)
        return 130
    except (OSError, ValueError, RuntimeError, tomllib.TOMLDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
