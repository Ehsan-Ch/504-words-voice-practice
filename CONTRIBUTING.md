# Contributing

Keep the prompt the main entry point. Preserve the distinction between ACTIVE
CORE and unselected optional rules. Explain changes to rule-selection behavior
and checkpoint semantics with a short original example.

For code changes, install the package in a virtual environment and run:

```text
python -m unittest discover -s tests -v
python -m compileall -q src tests
python -m voice_practice --help
python scripts/check_public_files.py
```

Run the public-file check after staging any new files. Use original text fixtures
and simulated tool responses for tests; do not upload course data, real learner
records, native logs or model weights. A GPU run is optional and must be described
accurately: name the actual sample scope and backend, and keep private artifacts
out of Git. Do not silently change the proven transcription defaults.

Useful regression tests exercise interrupted writes, invalid cache reuse,
ambiguous review boundaries, Unicode routing and actionable failures. A passing
synthetic test is not an ASR accuracy result. Describe remaining uncertainty in
the pull request.
