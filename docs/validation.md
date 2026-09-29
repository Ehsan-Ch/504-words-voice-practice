# Validation and limitations

Publication validation was performed on **28–29 September 2026**. Historical batch
evidence, automated engineering tests, real GPU checks and prompt review are
separate kinds of evidence; none supplies a transcription accuracy score.

## Historical evidence checked without rerunning the batch

- Parsed all 1,453 historical final JSON files and matched their TXT output and
  source metadata. No missing/empty transcripts or metadata mismatches were found.
- Inspected 37,413 segment records: no negative/reversed timestamps or backward
  segment starts were found. Timestamp structure does not prove alignment accuracy.
- Confirmed 42 lesson folders, four voice recordings per lesson, and the guide's
  42 blocks of 12 target entries. The guide's full PDF-content review was not repeated.
- Checked all nine review merge records: 1,080 windows and 1,071 joins, including
  32 fallback joins. See [recorded-run.md](recorded-run.md) for exact scope.
- Ran the **new package's read-only inventory** over the actual media tree. Its
  1,453 jobs and all five routing totals matched the historical runtime categories.

## Actual GPU smoke checks

The installed whisper.cpp binary, existing `ggml-large-v3.bin`, FFmpeg/FFprobe
9.0.1 and AMD Radeon RX 7800 XT were available. Two small private samples were
processed with the refactored package on Windows and Python 3.12. The native logs
explicitly reported **Vulkan0**, GPU device **0**, and the RX 7800 XT.

| Check | Actual result |
|---|---|
| English single-file path | One approximately 2-second clip with a Persian filename completed; one recognized segment |
| Persian review path | One 65-second extract completed using windows starting at 0 and 30 seconds; 17 final segments |
| Review seam | One `hybrid_safe` seam selected by actual FFmpeg silence detection |
| Exports | JSON, TXT, SRT and VTT present for both jobs |
| Resume | A second invocation through the Windows launcher reported 0 newly completed, 2 already complete, 0 failures; no new inference |
| Baseline | Device 0, `-mc 64`, 60/30 review windows, no VAD or initial prompt |

These samples came from the private source media and remain ignored local test
artifacts. Neither sample audio, its transcript nor native logs is published.
The **full completed transcription batch was not rerun**. These checks establish
that the local backend and both execution paths work; they do not measure
accuracy or establish compatibility with another GPU, driver, model or machine.
Physical power loss was not induced; interruption recovery is exercised with
controlled failures in the automated suite.

## Automated checks

The final local run on Windows / Python **3.12.9** discovered **41 tests**:
**40 passed, 1 skipped, 0 failures**. The skipped directory-symlink test requires
a Windows privilege unavailable in this environment. Installation, source/test
compilation, CLI help, the Windows launcher and the staged public-file/link
audit also passed. The initial sandbox attempt could not create disposable
Windows temporary test files; the completed run used approved execution outside
that sandbox. No course data was used by the suite.

The suite uses original short text fixtures and simulated native tool responses.
It covers classification, Unicode paths, review boundaries and seams, timestamp
conversion, export formats, retries, corrupt/stale caches, incomplete final
writes, interruption recovery, directory isolation and concurrent-writer locks.
No private course data, model, FFmpeg installation or GPU is required.

```text
python -m unittest discover -s tests -v
python -m compileall -q src tests
python -m voice_practice --help
python scripts/check_public_files.py
```

The GitHub Actions workflow runs these checks on Windows and Ubuntu with Python
3.11 and 3.12. Configured coverage is not a claim that every hosted job has passed;
the actual workflow result must be read from GitHub.

## Prompt review

Static review confirmed 16 C rules, 14 E options, 20 V entries and the nine
CORE-ALIGNED V labels. The quick-start copy block has 285 words. All authored
local links were checked. Public teaching files were compared with the private
stories for matching normalized 12-word passages; none was found. The master
guide and full canonical corpus are excluded.

The [20 acceptance scenarios](../examples/prompt-scenarios.md) and
[scripted demonstration](../examples/demo-session.md) are original specifications
and illustrations. **They were not run as live voice-chat experiments.** They
do not establish host reliability or learning effectiveness.

## Practical limits

- ASR can hallucinate, repeat, omit, or misrecognize words. Canonical material
  remains authoritative. No word-error rate, accuracy benchmark or learning
  outcome was measured.
- Silence-based joining is heuristic. Inspect fallback seams and uncertain
  regions against audio rather than trusting job-completion status.
- The package is a Windows/Vulkan workflow with portable GPU-free checks; other
  runtime platforms and hardware require their own inference validation.
- Dependency cache identity uses file metadata, while source content and output
  artifacts are hashed. Metadata-preserving tool/model replacement needs a new
  cache location. See [architecture](architecture.md).
- Native tools can hang on malformed inputs; Ctrl+C interrupts the run. There is
  no unattended process timeout or guarantee against every hardware failure.
- Chatbots can disregard instructions or lose context. The prompt does not
  implement speech I/O, reliable pronunciation scoring, scheduling, durable
  learner storage or automatic cross-chat memory. Transfer checkpoints manually.
- `504_batch_runner.zip` was not located in the searched locations; its
  extracted final runner, launcher and README were available and inspected.
