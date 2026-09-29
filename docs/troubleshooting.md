# Troubleshooting

| Symptom | Next action |
|---|---|
| `voice_practice` cannot be imported | Install with the same Python interpreter used to run it. The Windows launcher prefers `.venv`. |
| Config or executable missing | Check `config.toml` paths; run `doctor`. Preserve the native executable's companion DLLs. |
| FFmpeg/FFprobe not found | Install both or configure their executable paths. Start a new terminal if PATH changed. |
| Unicode/native file error | Use an ASCII scratch directory and supported tool/model paths. Do not rename original media merely to work around Whisper. |
| Input classified incorrectly | Inspect its full relative path and `inventory`; Text routing recognizes `متن` in a `voice` filename. Unknown layouts need an explicit classifier change. |
| Model load or GPU allocation fails | Verify the actual model file, free GPU memory, device selection, Vulkan build and driver. Do not silently change the established baseline. |
| Native process fails repeatedly | Read the job's error and native stderr tail. Fix the tool/input problem, then rerun; three retries cannot fix a missing dependency. |
| Interrupted or partial JSON | Resume with the same configuration. Completion requires validated outputs and the completion marker; file size alone is insufficient. |
| Completed job runs again | Source, settings or dependency identity changed, a marker is absent, or an output is damaged. This is deliberate cache invalidation. |
| Review words repeat or disappear | Inspect raw adjacent windows and seam metadata against audio. Joining is heuristic; fallback seams deserve special attention. |
| Empty or implausible transcript | Check language, audio, timestamps and original sound. A successful process return is not a quality guarantee. |
| Chatbot jumps ahead after silence | Say “Where are we?”, supply the last accepted checkpoint, and explicitly restore it. |
| Chatbot invents cross-chat memory | Paste the actual checkpoint, rule choices and canonical lesson material into the new chat. |
| Chatbot applies all optional rules | Restore the PENDING/KEEP/MODIFY/REMOVE selections. Core-aligned rows do not activate other optional policies. |

The public tests simulate tool behavior. Passing them cannot establish Vulkan
compatibility, ASR accuracy, voice-chat reliability or learning effectiveness on
your own system. See [validation](validation.md) for the checks actually run.
