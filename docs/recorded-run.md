# Recorded GPU run and publication audit

The historical run record reports **1,453 completed jobs and zero failed jobs**. An independent read-only audit of its saved output artifacts corroborated completion. These are processing results, not an accuracy score.

## Historical result

`batch_summary.json` records:

| Field | Value |
| --- | ---: |
| Total jobs | 1,453 |
| Completed in that run | 1,453 |
| Already complete at run start | 0 |
| Failed in that run | 0 |

The matching log records a batch start at `2026-09-27T14:02:05` and completion at `2026-09-27T18:40:57`. These are local timestamps without an encoded UTC offset. They are retained as historical markers, not offered as a controlled speed benchmark.

| Final runtime category | Language | Mode | Jobs |
| --- | --- | --- | ---: |
| Authentic clips | English | Single file | 1,275 |
| Lesson Text recordings | English | Single file | 42 |
| Morning / Noon / Evening instruction | Persian | Single file | 126 |
| Cumulative reviews | Persian | Overlapping windows | 9 |
| Study guidance | Persian | Single file | 1 |
| **Total** | | | **1,453** |

An inventory discrepancy was resolved against final behavior: the manifest originally labels all 168 lesson voice files as Persian. The final runner ignores those classification fields and recomputes routing from paths, assigning the 42 Text recordings to English. Output metadata and runtime log agree with the corrected table.

## Configuration recovered from actual code

- Windows, whisper.cpp with Vulkan, `ggml-large-v3.bin`, device `0`, `-mc 64`.
- No VAD option and no initial prompt in the final runner.
- FFmpeg conversion to 16 kHz, mono, signed 16-bit PCM WAV.
- English for clip folders and voice stems containing the normalized Text marker; Persian for other lesson voice, review and help recordings. Classification normalizes Unicode with NFKC, removes format-control characters, and case-folds names.
- Up to three attempts per file, with reuse of saved JSON and review windows.
- Review windows of 60 seconds, advancing by 30 seconds until the final window reaches the recording's duration.
- Silence detection threshold `-35dB` and minimum silence `0.25` seconds; hybrid joining accepts a boundary error up to `1.6` seconds before choosing a fallback.

The final batch log identifies Vulkan device `0` but does not record its model name. An earlier `full_transcription.log` in the preserved GPU work explicitly identifies device `0` as **AMD Radeon RX 7800 XT**. Both the Vulkan executable and the large-v3 model were present at audit time. Presence is not a new hardware execution test.

### Review joining and timestamps

For each adjacent pair, the runner examines silences inside the overlap and proposes their midpoints as joins. It chooses left/right boundary segments according to their timestamp midpoints. Candidate error is the sum of distances from the left segment's end and right segment's start to the silence edges. Safe candidates favor longer silence, then smaller error, then proximity to the overlap center. If none qualify, it uses the minimum-error candidate; if none exist, it uses the overlap center.

Segments are retained in half-open midpoint intervals between the chosen joins. The process does not perform semantic deduplication or prove that every spoken word survives a join. Window-local millisecond offsets are converted to seconds, shifted by the window's start, and exported again as rounded millisecond offsets. Review rows retain `window_start`.

All nine saved review merge records were read. Together they contain **1,080 windows and 1,071 joins**: **1,039 `hybrid_safe`** and **32 `fallback_min_edge`**. No saved join in these records used the center fallback. Fallback joins are a reason to inspect boundary quality, not evidence of a failed processing job.

## Checks performed on 28 September 2026

The audit read the saved files; it did not rerun the completed corpus.

| Check | Observed result |
| --- | --- |
| Source media inventory | 178 M4A + 1,275 MP4 = 1,453 files |
| Lesson structure | 42 lesson directories; each has one PDF and four voice recordings |
| All PDFs in source tree | 51, including nine outside the lesson directories |
| Master-guide lesson table structure | 42 blocks, 12 target entries each, 504 entries total |
| Manifest source uniqueness | 1,453 distinct source paths |
| Output source uniqueness and coverage | 1,453 distinct sources, exactly matching the manifest |
| Source existence after correcting the historical root relocation | All 1,453 found |
| Completed job directories | 1,453 |
| `source.json` and `final.json` parsing | All 1,453 parsed successfully |
| Final metadata matching source metadata | Zero mismatches in source, kind, language or mode |
| Empty final transcription arrays | Zero |
| `final.txt` presence and JSON text consistency | All 1,453 present and matching, after line-ending normalization |
| Saved transcript segments examined structurally | 37,413 |
| Negative or reversed segment timestamps | Zero |
| Backward segment start times within a final transcript | Zero |

Representative raw/final schema checks covered each of the five routing categories. JSON final outputs contain source metadata, completion time and timestamped transcription rows; TXT contains the same row text. Reviews additionally contain their join metadata and window attribution. These checks do not certify that timestamps precisely align with audio, that neighboring segments never overlap, or that wording is correct.

The source directory moved after the run. Saved absolute paths still name the historical root. Verification applied the known root relocation in memory; it did not rewrite the originals. The original launcher therefore requires path configuration before it can run in the new location. The reusable project removes those embedded personal paths.

## Limits of this evidence

No word-error rate, human scoring exercise, pronunciation assessment or benchmark was produced by this audit. The guide itself reports transcription repetitions, hallucinations and truncated content. Successfully creating artifacts does not remove those problems.

The old runner's resume logic accepted JSON files based on existence and size alone. Its successful completed run is not proof of recovery from every interruption. The refactor's automated tests and any new smoke checks are reported separately from this historical evidence in the project validation documentation.

The [machine-readable evidence](../evidence/recorded-batch-summary.json) contains only sanitized aggregates and filenames. Private audio, transcript text, source paths and logs are deliberately omitted.
