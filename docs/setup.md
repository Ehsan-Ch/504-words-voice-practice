# Setup and usage

## Prompt-only use

The [quick-start](../prompts/quick-start.md) and [full protocol](../prompts/teaching-protocol.md)
work as text instructions for a voice-enabled chatbot. Choose a service you
already use, supply material you are entitled to share with it, and start voice
chat. The repository does not require or collect API keys. Host features,
session limits, speech recognition, and instruction following vary.

Keep checkpoints outside Git. At the end of a session copy the exact checkpoint
and rule selections. In a new chat supply those, the same protocol, and the
needed canonical lesson material. Ask the chatbot to confirm the last accepted
step before continuing. Do not assume it can access previous chats or files.

## Transcription dependencies

- Python **3.11 or later** (the local validation environment uses 3.12).
- `ffmpeg` and `ffprobe`, both from a trusted [FFmpeg distribution](https://ffmpeg.org/download.html).
- A Windows `whisper-cli.exe` built with Vulkan and its companion DLLs.
- A Vulkan-capable driver and GPU; the recorded setup used **AMD Radeon RX 7800 XT**.
- The multilingual **`ggml-large-v3.bin`** model, obtained separately.

Reuse a known working build when available. The project does not rebuild,
upgrade, download, or copy your existing tools/model automatically. The local
whisper.cpp checkout inspected for provenance was commit
`d09f61a708f3487afa956ff578e60eae5e7a233c`; this identifies the checkout, not
an independently reproducible binary build. Upstream instructions describe
[Vulkan builds](https://github.com/ggml-org/whisper.cpp#vulkan-support) and
[model acquisition](https://github.com/ggml-org/whisper.cpp/tree/master/models).
Building typically needs CMake, a C++ toolchain and the Vulkan SDK; follow the
instructions for your selected whisper.cpp revision. Keep the tested binary,
driver, and model versions together when comparing runs.

## Install

From the repository root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
Copy-Item config.example.toml config.toml
```

No environment activation is necessary. The `.bat` launcher uses this local
environment if present, otherwise `python` on PATH. With an installed package,
`voice-practice` or `python -m voice_practice` exposes the same commands.

## Configuration

Edit `config.toml`, which is ignored by Git. Use forward slashes in quoted
Windows paths, or TOML literal strings for backslashes. Relative paths resolve
from the configuration file. Keep the input, output, and temporary work roots
separate, with no output/work directory inside the input tree. Use an **ASCII
work path** for native Whisper scratch files; input and final output paths may
contain Persian or other Unicode characters. Keep the native executable and
model in paths supported by your whisper.cpp build.

The example lists every supported setting. The baseline is:

| Setting | Value / purpose |
|---|---|
| Model | Multilingual `ggml-large-v3.bin` |
| Device | Vulkan device `0`; validate the device reported by the native log |
| Context | `-mc 64` |
| VAD / initial prompt | Neither is passed |
| Input WAV | 16 kHz, mono, signed 16-bit PCM |
| Review window / step | 60 seconds / 30 seconds (30-second overlap) |
| Silence threshold / duration | `-35dB` / 0.25 seconds |
| Join edge error bound | 1.6 seconds |
| Attempts | Up to 3 per job |
| Output | JSON and TXT required; SRT/VTT optional new exporters |

Do not substitute the older PDF-prompt or VAD experiment configuration when
trying to reproduce this baseline.

## Inspect, sample, run, resume

```powershell
.\scripts\voice-practice.bat inventory --config config.toml
.\scripts\voice-practice.bat doctor --config config.toml
.\scripts\voice-practice.bat dry-run --config config.toml --limit 1
.\scripts\voice-practice.bat run --config config.toml --limit 1
```

Inventory classifies course paths before execution. Doctor checks dependencies;
it does not prove that inference will run on the GPU. Dry-run previews the
selected jobs without transcribing. `--limit` bounds the sorted job selection.
To process all selected source files, deliberately omit `--limit` from `run`.

Press Ctrl+C to interrupt. Run the same command again to resume. Valid completed
outputs are skipped, while incomplete work is recovered or regenerated. Never
run two processes against the same output/work roots. Changing inputs,
configuration or tool/model identity can invalidate cached work.

Legacy hashed `batch_output` folders remain untouched. They are evidence of the
historical run, not automatically imported as verified completion markers for
the new package. A dry-run is appropriate for inventory verification; a full
rerun is not required to use the teaching prompt.

## Course layout

Routing follows the final runner's actual path rules. `clip` files are English;
`voice` files whose stem contains `متن` are English Text; other `voice` files are
Persian. The original review and help folder names identify Persian review and
guidance recordings. Unknown layouts fail with an actionable classification
error; organize your own small input fixture accordingly or adapt classification
with tests. No language is inferred from an untrusted old manifest label.

Final output mirrors the source-relative media path, including its extension,
for example `output/lesson-demo/voice/متن.m4a/final.json`. Scratch names are
hashed ASCII paths. The file extension in the directory prevents a video and
audio file with the same stem from colliding.
