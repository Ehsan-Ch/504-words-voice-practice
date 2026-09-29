# Illustrative session: correction, interruption, and exact resume

This is a **scripted original example**, not a transcript of a real learner,
benchmark, or completed voice test. Use [demo-lesson.md](demo-lesson.md) as its
canonical material. The opening setup explicitly supplies its simulated state.

## Setup

**Learner:** Use Demo A, Day 1. This is a simulated Noon practice example. In this
example Morning is complete, Noon has not started, and Evening and Text have not
started. KEEP E05, E10, V03, V04, V14, V16, V17, V18. Other optional rules remain
at their initial status. Start Noon.

**Teacher:** Demo Day 1, Demo A — Noon, item 1 of 3. For “bookmark,” say the demo
collocation.

**Learner:** A paper bookmark.

**Teacher:** Correct. What is its Persian gloss?

**Learner:** نشانک کاغذی

**Teacher:** Correct. For “kettle,” say the demo collocation.

**Learner:** Fill a kettle up.

**Teacher:** That is understandable English. Our exact demo phrase is “fill the
kettle.” Say “fill the kettle.”

**Learner:** Fill the kettle.

**Teacher:** Corrected. What is its Persian gloss?

**Learner:** کتری را پر کردن

**Teacher:** Correct. For “refill,” say the demo collocation.

*The connection drops before a clear answer. No response is accepted and no
progress is inferred. The kettle phrase remains queued for a later uncued retest.*

**Learner:** Urgent summary.

**Teacher:** Demo Day 1, Demo A — Noon paused at item 3 of 3, refill, collocation
recall. Bookmark is complete. Kettle's correction and gloss were accepted; its
collocation still needs a retest. Last accepted: kettle's Persian gloss. Morning
is complete; Evening and Text have not started. Next: repeat the refill prompt.

```text
PROGRESS_CHECKPOINT
Protocol: 504-words-voice-practice / 1
Checkpoint ID: demo-noon-pause-1
Supersedes: none
Material: demo-reading-break-v1
Day / Lesson: Demo Day 1 / Demo A
Target count: 3
Segment: Noon
Segment status: PAUSED
Scheduled scope: demo-a-1, demo-a-2, demo-a-3 / collocation recall + gloss recall;
                 selected error retests
Order: demo-a-1, demo-a-2, demo-a-3; then queued retests
Current item: 3/3 / demo-a-3 / refill
Current micro-step: recall / collocation
Pending prompt: For "refill," say the demo collocation.
Last confirmed: demo-a-2 / gloss recall / کتری را پر کردن / accepted
Completed items/steps: demo-a-1 collocation + gloss;
                       demo-a-2 corrected collocation + gloss
Error queue: demo-a-2 / source phrase mismatch / uncued collocation retest pending
Weak items: demo-a-2 / source phrase recall
Skipped/deferred: none
Morning: COMPLETE (simulated setup)
Noon: PAUSED
Evening: NOT_STARTED
Text: NOT_STARTED
Other lessons: none in this demo
Cumulative review: none in this demo
Optional rules KEEP: E05, E10, V03, V04, V14, V16, V17, V18
Optional rules MODIFY: none
Optional rules REMOVE: none
Optional rules PENDING: E01-E04, E06-E09, E11-E14, V01, V06, V13, V15, V19
Core-aligned V rules: V02, V05, V07-V12, V20 (core behavior active)
Next action: on Continue, ask the pending refill collocation prompt
END_CHECKPOINT
```

## Resume in another conversation

*The learner manually pastes the protocol, demo lesson, and checkpoint above into
a new chat. The teacher does not recover it through repository-provided memory.*

**Learner:** Where are we?

**Teacher:** Your supplied checkpoint puts Demo Day 1, Demo A, at Noon paused,
item 3 of 3, refill collocation recall. Last accepted: kettle's gloss. Kettle needs
an uncued collocation retest. Morning is complete in this demo; Evening and Text
are not started. Next is the unanswered refill prompt.

**Learner:** Continue.

**Teacher:** For “refill,” say the demo collocation.

**Learner:** Refill a bottle.

**Teacher:** Correct. What is its Persian gloss?

**Learner:** دوباره پر کردن بطری

**Teacher:** Correct. Retest: for “kettle,” say the demo collocation.

**Learner:** Fill the kettle.

**Teacher:** Correct. For one short extra practice sentence, use “kettle.”

**Learner:** I fill the kettle before making tea.

**Teacher:** Correct. Noon complete for Demo Day 1, Demo A: all three targets
recalled; kettle corrected and retested. Error queue empty. Kettle remains a
weak item for a future review. Morning and Noon are complete; Evening and Text
are not started. Next pending core block: Evening, on your command.

```text
PROGRESS_CHECKPOINT
Protocol: 504-words-voice-practice / 1
Checkpoint ID: demo-noon-complete-2
Supersedes: demo-noon-pause-1
Material: demo-reading-break-v1
Day / Lesson: Demo Day 1 / Demo A
Target count: 3
Segment: Noon
Segment status: COMPLETE
Scheduled scope: demo-a-1, demo-a-2, demo-a-3 / collocation recall + gloss recall;
                 demo-a-2 correction, uncued retest, and extra sentence
Order: demo-a-1, demo-a-2, demo-a-3; demo-a-2 retest
Current item: none / scheduled Noon work complete
Current micro-step: none
Pending prompt: none
Last confirmed: demo-a-2 / example / I fill the kettle before making tea. / accepted
Completed items/steps: all three collocations + glosses; demo-a-2 correction,
                       uncued collocation retest, and extra sentence
Error queue: none
Weak items: demo-a-2 / source phrase recall; retest passed
Skipped/deferred: none
Morning: COMPLETE (simulated setup)
Noon: COMPLETE
Evening: NOT_STARTED
Text: NOT_STARTED
Other lessons: none in this demo
Cumulative review: none in this demo
Optional rules KEEP: E05, E10, V03, V04, V14, V16, V17, V18
Optional rules MODIFY: none
Optional rules REMOVE: none
Optional rules PENDING: E01-E04, E06-E09, E11-E14, V01, V06, V13, V15, V19
Core-aligned V rules: V02, V05, V07-V12, V20 (core behavior active)
Next action: wait for an explicit next-block instruction
END_CHECKPOINT
```

The teacher ends there. If the learner later says **Start Text for Demo Day 1**,
only Text begins; completing Text will not mark Evening complete.
