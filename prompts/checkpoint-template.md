# Portable checkpoint

This is a blank template, not a learner record. Keep completed checkpoints private.
Save a copy at a pause, urgent summary, segment completion, or end-of-session
request. If E01 strict silence is selected, `Stop` produces no checkpoint response;
use `Urgent summary` before pausing or request the checkpoint after resuming.

Keep **current pending work** separate from **last accepted work**. A command may
change ACTIVE to PAUSED but cannot convert an unanswered exercise into completed
learning. Update an error observation without advancing the accepted checkpoint.

```text
PROGRESS_CHECKPOINT
Protocol: 504-words-voice-practice / 1
Checkpoint ID: [locally unique label or timestamp]
Supersedes: [previous checkpoint ID or none]
Material: [course/lesson identifier and version; no private file path needed]
Day / Lesson: [day] / [lesson]
Target count: [supplied lesson count; normally 12 in the source course]
Segment: [Morning | Noon | Evening | Text | Clips | Cumulative Review]
Segment status: [NOT_STARTED | ACTIVE | PAUSED | COMPLETE]
Scheduled scope: [target IDs and required micro-steps; explicit review scope]
Order: [target IDs in actual order; preserve any selected shuffle]
Current item: [position/count and stable target or story-chunk ID]
Current micro-step: [pronunciation | meaning | collocation | gloss | recall |
                     example | story | correction | retest]
Pending prompt: [exact short unanswered prompt]
Last confirmed: [target ID / step / accepted learner answer, or none]
Completed items/steps: [explicit IDs and steps, or reference to attached ledger]
Error queue: [ID / issue / correction or retest state; or none]
Weak items: [ID / issue / last review result; or none]
Skipped/deferred: [ID / explicit learner instruction / pending work; or none]
Morning: [status]
Noon: [status]
Evening: [status]
Text: [independent status and story chunk when relevant]
Other lessons: [per-lesson statuses, or attached ledger reference]
Cumulative review: [milestone / scheduled scope / status / last accepted item]
Optional rules KEEP: [IDs, or none]
Optional rules MODIFY: [ID = exact replacement behavior, or none]
Optional rules REMOVE: [IDs, or none]
Optional rules PENDING: [unselected E IDs and optional V IDs]
Core-aligned V rules: V02, V05, V07-V12, V20 (core behavior remains active)
Next action: [exact action on resume; no automatic next segment]
END_CHECKPOINT
```

For a longer course, attach a compact ledger with one row per lesson and one per
review milestone. A checkpoint for the current lesson must not imply that other
lessons are finished. Use `UNKNOWN` in descriptive fields when information is
unavailable; do not convert missing information into `NOT_STARTED` or `COMPLETE`.

Transfer procedure:

1. Copy the latest checkpoint and any ledger it references into a private file.
2. Start a new conversation with the quick-start prompt or full protocol.
3. Supply the checkpoint, selected rules, and the exact lesson material needed.
4. Ask **Where are we?** and compare the reported pending prompt with your copy.
5. Say **Continue** once the location is established. If records conflict, resolve
   the smallest ambiguity before advancing; the newer timestamp alone is not proof.
