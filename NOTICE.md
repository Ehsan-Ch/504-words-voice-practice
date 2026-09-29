# Attribution and content boundaries

Project author: **Ehsan Cheraghi**. This repository packages his local 504 Words
transcription work and the portable teaching guide developed through iterative
chatbot-assisted analysis. Code and public prompts were refactored and reviewed
with AI assistance; the recorded transcription run predates this refactor.

The MIT license covers the original code, public protocol, documentation, and
new demonstration fixtures in this repository. It does not license the underlying
commercial course, book, recordings, PDFs, video clips, stories, or third-party
software. This is an independent learning project; no course publisher,
instructor, OpenAI, or whisper.cpp endorsement is claimed. The available local
materials do not establish a redistribution license or a verified instructor
identity, so neither is invented here.

The course's structure and practice method informed the protocol. Its full
content is deliberately absent. Supply material you are entitled to use privately
and check the terms of your chosen chatbot before uploading it. Do not commit
personal checkpoints or learning records.

External components are installed separately:

- [whisper.cpp](https://github.com/ggml-org/whisper.cpp) by its contributors
  implements Whisper inference; see its MIT license.
- [OpenAI Whisper](https://github.com/openai/whisper) supplies the model family;
  weights are not distributed here. Check the license at the source of the model.
- [FFmpeg](https://ffmpeg.org/) supplies media conversion and silence detection;
  licensing depends on the particular build and enabled components.
- Your voice-enabled chatbot supplies speech input/output and conversation
  hosting. This project does not bundle a chatbot, an API service, or voice UI.
