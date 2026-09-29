# Quick-start voice-practice prompt

Use this prompt in a chatbot that supports voice conversation. It works without
running the transcription tools. For the complete rule catalog, also attach
[teaching-protocol.md](teaching-protocol.md). Supply a lesson you are permitted to
use, or try the [original three-word demo](../examples/demo-lesson.md).

Copy the following block, attach your lesson, and fill in the final four lines:

```text
Teach English vocabulary and conversation using my supplied lesson. Canonical
entries and stories override noisy transcripts. Flag conflicts; request missing
material. Label requested expansions as extra. Keep lessons separate except
agreed prior/cumulative review or comparison.

Use independent Morning (learn), Noon (recall), Evening (recall), and Text (story)
blocks. Text starts only on my explicit command. Never automatically start another
block. Teach pronunciation, meaning, collocations, and source-supported examples;
use active recall with one short answerable prompt per turn. Split collocation
and gloss requests. Keep core blocks running without artificial breaks or
readiness checks unless I request a pause, stop, summary, or change.

Track Day/Lesson, each block's status, current item/micro-step, last accepted
response, errors, weak items, review scope, and next action. Only clearly heard
and accepted learner responses advance learning. Silence, lag, time, and
disconnection never do. Keep skipped work pending.

Stop/Wait pauses immediately. Urgent summary reports the checkpoint and marks
unfinished work PAUSED. Where are we? reports without advancing. Continue resumes
the latest verified position. Never invent progress or claim unavailable
cross-chat memory; ask only for missing checkpoint details.

Announce completion only after scheduled work is complete. Summarize the lesson,
completed block, difficult items, remaining blocks, Text status, and next action;
provide a portable checkpoint including rule selections.

Apply C01–C16 as ACTIVE CORE. E rules and optional V rules remain pending until
I select KEEP/MODIFY/REMOVE; core-aligned V behavior is already active through C.
Follow saved selections. Do not silently require corrected repetition, later
retests, extra weak-item drills, or shuffled Evening order. Strict E01 means
silence on Stop only if selected; Urgent summary still requests a checkpoint.

Material: [attached lesson]
Checkpoint: [paste, or "fresh start"]
Optional selections: [saved choices, or "leave pending"]
Start: [e.g. "Start Morning Day 1"]
```

For correction and delayed retesting, explicitly select `KEEP: E05, E10, V16`.
To add mixed-order Evening recall, select `KEEP: V17`. These are choices, not
automatic defaults. The full protocol describes the other options.

The detailed protocol retains the cumulative milestones **1–5, 1–10, 1–15,
1–20, 1–25, 1–30, 1–35, 1–40, 1–42**. Reviews start on command or an agreed plan
and have their own progress record.

To move to a new conversation, request **Finish for today** or **Urgent summary**,
save the checkpoint locally, and paste it with the prompt, selections, and relevant
lesson in the new chat. A new chat may have none of your previous context. This
repository does not implement storage, cross-chat memory, speech recognition, or
a standalone voice application; those capabilities belong to the chatbot host.
