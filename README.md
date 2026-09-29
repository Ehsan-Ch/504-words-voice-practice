# 504 Words Voice Practice — A Chatbot Prompt Built from the Course’s Teaching Method

**Practise English conversation and vocabulary with a voice-enabled chatbot.**
Start with the [quick-start prompt](prompts/quick-start.md), or use the
[complete teaching protocol](prompts/teaching-protocol.md) for a portable,
explicitly checkpointed routine.

1. Paste the quick-start prompt into your chatbot, or attach the full protocol.
2. Supply your own canonical lesson material: target words, meanings, examples,
   collocations, and the story only if you want Text practice. Try the original
   [demonstration lesson](examples/demo-lesson.md) first.
3. Choose the lesson and say **“Start Morning.”** Use your chatbot's voice chat
   for the speaking practice. Noon, Evening, and Text are separate segments;
   Text starts only when you explicitly request it.
4. Say **“Where are we?”** or **“Urgent summary”** to get a checkpoint. Copy it
   into the next chat with the protocol, your material, and saved rule choices.

The prompt uses short questions and active recall. Progress advances only after
a clearly heard and accepted response. Silence or a disconnect never counts as
progress. Optional correction and retesting rules remain **PENDING SELECTION**
until you select them; the 16 **ACTIVE CORE** rules are always active.

This is a **chatbot prompt and supporting transcription tools**. It does not
provide a voice app, automatic cross-chat memory, a learning-record database,
or a chatbot API integration. No Python or GPU is needed to use the prompt.

## Why this project exists

The source course divides vocabulary practice into Morning, Noon, Evening, and
Text recordings, with cumulative reviews. This project turns that teaching
structure into an explicit conversational protocol. Transcription supported the
analysis of delivery and review patterns; canonical lesson material supplies
the spelling and content. Noisy automatic transcripts never override it.

The local historical run recorded **1,453 completed jobs and zero failures**:
1,275 English clips, 42 English Text recordings, 126 Persian lesson recordings,
nine Persian reviews, and one Persian guidance recording. These are processing
counts, **not accuracy scores or learning-outcome measurements**. The new
package was derived from the final working runner, with the same GPU baseline
and review joining policy. See the [recorded evidence](docs/recorded-run.md),
[source provenance](docs/provenance.md), and [validation report](docs/validation.md).

## Explore

| Start here | Purpose |
|---|---|
| [Quick-start prompt](prompts/quick-start.md) | Copy into a chatbot and begin |
| [Teaching protocol](prompts/teaching-protocol.md) | Core rules, optional choices, segment flow |
| [Checkpoint template](prompts/checkpoint-template.md) | Transfer exact progress between chats |
| [Teaching-method analysis](docs/teaching-method.md) | How the protocol was derived |
| [Setup and usage](docs/setup.md) | Optional Windows/GPU transcription workflow |
| [Architecture](docs/architecture.md) | Routing, windows, timestamps, safe resumption |
| [Troubleshooting](docs/troubleshooting.md) | Actionable recovery instructions |
| [Validation](docs/validation.md) | Actual checks and remaining limitations |
| [Attribution and rights](NOTICE.md) | What is included and what remains private |

## Optional: transcribe your own material

Requires Python 3.11+, FFmpeg/FFprobe, an existing whisper.cpp Vulkan build,
and a separately obtained `ggml-large-v3.bin` model. The established Windows
hardware was an AMD Radeon RX 7800 XT. Other GPUs require their own validation.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
Copy-Item config.example.toml config.toml
# Edit config.toml to point to your source, tools, model and private output.
.\scripts\voice-practice.bat inventory --config config.toml
.\scripts\voice-practice.bat doctor --config config.toml
.\scripts\voice-practice.bat dry-run --config config.toml --limit 1
.\scripts\voice-practice.bat run --config config.toml --limit 1
```

Only `run` starts transcription. Begin with a small sample; remove `--limit`
only when you deliberately want a full batch. The original completed batch is
not rerun by setup or tests. See [setup](docs/setup.md) before starting.

The package uses the Python standard library at runtime. Automated checks use
original fixtures and simulated external tools, so they need no GPU, model, or
private course data:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Code, prompts, documentation, and original examples are MIT licensed. Course
recordings, PDFs, full transcripts, stories, model weights, and personal
learning records are excluded. See [NOTICE.md](NOTICE.md).
