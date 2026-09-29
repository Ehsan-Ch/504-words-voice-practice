# Source provenance and engineering lineage

This project refactors the author's completed GPU transcription work and publishes a reusable teaching prompt derived from the course's teaching method. It is not a publication of the underlying course. The source audio, PDFs, full transcripts, stories, model weights, machine logs, and personal progress remain private.

## Sources inspected

The publication audit on 28 September 2026 read these existing local artifacts before choosing the implementation baseline:

| Artifact | Role in the project |
| --- | --- |
| `run_all_504.py` in the extracted `504_batch_runner` directory | Final batch runner; the engineering baseline |
| `START_504_BATCH.bat` and `README_504_BATCH.txt` | Actual Windows launch instructions and original input/output contract |
| `processing_manifest.jsonl` | Source inventory; its language labels are superseded by final runtime classification |
| `batch_summary.json` and `batch_run.log` | Historical completion records |
| All 1,453 output directories and their `source.json`, `final.json`, and `final.txt` | Independent structural verification of completed artifacts |
| Raw JSON examples and all nine review merge records | Output schema, language routing, timestamp and review-joining evidence |
| Earlier `transcribe_all_504_gpu.py` and `transcribe_lesson1_gpu.py` | Experimental history; not the final baseline |
| `504_Words_Voice_Teaching_System_Portable_Master_Guide.md` | Teaching protocol, explicit rule-selection status, source priorities, and private canonical course reference |

The extracted batch directory contains the runner, launcher and README. A separate `504_batch_runner.zip` was not found in the searched Downloads and GPU work locations. Recovering the archive was unnecessary because its runnable contents were available. Configuration was embedded in the final Python runner; no separate final configuration file was found there.

The original work was read without modification. The excluded CPU work was not used. No complete transcription batch was rerun for this audit.

The earlier conversations named `504` and `504_2` were accessible and their
recent relevant messages were consulted. They provided historical context for
the review-window experiments and the master guide. Actual final code and
recorded output take precedence over conversational claims.

## Why this baseline

The final runner and its matching completion log select `ggml-large-v3.bin`, Vulkan device `0`, and `-mc 64`. Its command has neither VAD nor an initial prompt. Earlier files in the GPU work directory contain VAD and prompt experiments and, in some cases, omit clips. Their filenames alone do not identify the successful final pipeline.

The final runner supplies JSON output from whisper.cpp, converts inputs to 16 kHz mono signed 16-bit PCM, routes English clips and Text recordings separately from Persian instruction, and applies overlapping review windows. This behavior is the source of the reusable implementation. Portability and reliable interruption recovery are engineering improvements, not claims about features the old runner already guaranteed.

### Output hierarchy and formats

The earlier `transcribe_all_504_gpu.py` mirrored source-relative folders and wrote TXT. The final batch instead used a 16-character identifier derived from the case-folded absolute source path. Each job's `source.json` retained the full source path and therefore the original hierarchy as metadata. Its public-facing final artifacts were `final.json` and `final.txt`; reviews also retained window JSON and `merge_meta.json`.

Thus, “preserved hierarchy” in the historical handoff should not be interpreted as a claim that the final output directories mirrored the course tree. The final batch retained the mapping. See the reusable tool's usage documentation for its current layout options. SRT and VTT, where offered by the refactor, are new exports from the preserved millisecond timestamps; they are not claimed as historical batch outputs.

### Resumption and retries

The old runner retried each job up to three times, reused completed review windows, caught interruptions, and updated a summary. Its cache acceptance rule was only “file exists and is larger than 20 bytes.” It did not prove that a cached JSON was complete, matched the current source/configuration, or had a matching TXT. The refactor strengthens these checks. Historical success does not establish that interruption recovery was safe for every possible failure.

## Teaching-method lineage

The master guide separates **ACTIVE CORE** from inherited and proposed rules marked **PENDING SELECTION**. The public prompts preserve this distinction. The guide supplies independent Morning, Noon, Evening and explicitly requested Text segments, short answerable turns, active recall, explicit acceptance before progress, weak-item review, and portable checkpoints.

Canonical lesson material controls target spelling and story content. Transcripts help explain delivery rhythm and review order; noisy speech recognition cannot replace canonical material. The guide embeds the full course and personal context, so it is intentionally not included in this repository. Public prompts require learners to supply material they are entitled to use.

The audit counted 42 canonical lesson blocks and 12 target rows in every block of the guide, for 504 target entries. It also found 42 lesson directories with one lesson PDF and four voice recordings each. This checks structure, not every definition, pronunciation or story against the PDFs. The guide describes a prior three-pass content review; this publication audit does not claim to have repeated that full content review.

## Fingerprints

SHA-256 values identify the private originals used for this work. They are identifiers, not downloadable source content or independent proof of transcription accuracy.

| Original artifact | SHA-256 |
| --- | --- |
| `run_all_504.py` | `050543a76106ac632317ce5f991573766c03fb1ce9abb06ada2a6eb9b62092ce` |
| `START_504_BATCH.bat` | `461493cb41846b685da6dba4d9689a381e58c737031f49a080a5a56cdd599dbc` |
| `README_504_BATCH.txt` | `96e0be4b6cc818f3fbf49f254ea2b70828c460be5b1ea1c97e88e70c734196f4` |
| `batch_summary.json` | `5030105fb71de19612596bcb7943909c46d42e7919b8956987e06097e064e990` |
| `batch_run.log` | `a493e7ded21d5c00ac1199f9f8c6f6643bf1be45525bdc87324bf907793e2199` |
| `processing_manifest.jsonl` | `c1243ff20adcf641fad79e5249f072868c6d9b75683d535d5c749ab9e95186c3` |
| `504_Words_Voice_Teaching_System_Portable_Master_Guide.md` | `d187656168d250c5a7b2afcd93012824502ec2ce6cf4b3a5136e1445a93e1423` |

The [recorded-run report](recorded-run.md) and [sanitized evidence](../evidence/recorded-batch-summary.json) provide the checked aggregates. The repository does not include machine-specific logs or private source manifests.
