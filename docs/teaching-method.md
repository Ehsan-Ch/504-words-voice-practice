# From a spoken course to a reusable practice protocol

The main output of this project is a prompt that guides vocabulary practice in
an existing chatbot voice conversation. The transcription tools support the
analysis of teaching materials; they are not required to use the prompt and do
not implement an interactive voice tutor.

Start with [the quick-start prompt](../prompts/quick-start.md), attach a lesson you
are permitted to use, and name the block you want. The [full protocol](../prompts/teaching-protocol.md)
preserves explicit rule choices. The public [demo lesson](../examples/demo-lesson.md)
shows the method without distributing the private course corpus.

## Evidence and the boundary of this analysis

The source work included a private Portable Master Guide containing teaching
rules, source precedence, lesson structure, checkpoint examples, and the full
42-lesson course appendix. This public adaptation retains the operating method
and replaces the embedded course with user-supplied material. It contains no
personal learning checkpoint or course story copied from that appendix.

The guide reports three historical reviews: structural completeness; canonical
PDF/content review; and cross-source/voice-suitability review. These are historical
claims recorded in that guide, not three new audits performed during this public
project preparation. Likewise, successful transcription jobs are evidence of a
finished processing run, not a word-accuracy score, teaching benchmark, or proof
that a learner mastered the vocabulary. Current engineering validation and its
scope are documented separately in the project documentation.

## What the teaching structure contributes

| Observed structure in the guide | Public prompt behavior | Practical purpose |
|---|---|---|
| Morning teaching, later Noon and Evening recall | Independent introduction and retrieval blocks | Practice can revisit the same material without a long explanation each time. |
| Target → collocation → Persian gloss | Retrieve the phrase and its meaning in separate short turns | A word is practiced in a usable phrase while voice requests remain answerable. |
| Story/Text handled separately | Text starts only by explicit command and has its own status | Learners can schedule story work independently without losing vocabulary progress. |
| Weak/error items recorded | Keep an item-specific queue; apply the learner's chosen correction/retest policy | The next practice action follows observed difficulty rather than guessed mastery. |
| Repeated and cumulative recall | Review agreed earlier scope at recorded milestones | Earlier material can be revisited without contaminating current-lesson completion. |
| Interrupted conversations | Save accepted work and pending work separately | A dropped connection does not silently become an answer. |
| PDF/transcript disagreements | Canonical material determines content; transcripts inform delivery | ASR errors cannot redefine a lesson target or story. |

These are design rationales derived from the supplied method, not measured
learning-effectiveness claims. The project makes no promise of proficiency gains,
automatic pronunciation scoring, or clinical-quality speech assessment.

## Preserve choices instead of inflating the rule set

The guide distinguishes **16 ACTIVE CORE rules (C01–C16)** from **14 inherited E
options** and **20 proposed V rules**. Nine V entries are labeled CORE-ALIGNED:
V02, V05, V07, V08, V09, V10, V11, V12, and V20. The other eleven V entries are
pending, as are all fourteen E entries.

There are additional behavioral overlaps: V15's one-question rule overlaps C15;
E03 overlaps exact resume; E09 overlaps short voice prompts; E12 overlaps basic
progress tracking. An optional identifier can remain pending while its shared
core behavior is active. Removing an optional identifier does not switch off a
core requirement. Selecting it can add detail beyond the shared minimum.

Some flow sections in the guide use unconditional wording for retesting or mixed
Evening order despite the earlier pending labels. The public adaptation resolves
that tension explicitly: the selection status controls extra obligations. E05
enables required corrected production, V16 enables a later retest gate, E10
enables extra weak-item repetitions, and V17 enables shuffled Evening recall.
No one is silently enrolled in all of them.

In the core-only version, the teacher still gives source-grounded feedback,
tracks observed difficulty, refuses to accept unclear or wrong answers as
successful responses, and records incomplete work honestly. Optional rules
specify additional practice steps rather than granting permission for basic
truthfulness or progress tracking.

## A response, a correction, and a retest are different events

The checkpoint identifies the last learner action that was both clearly heard
and accepted. Saying a new prompt is not progress. An ASR fragment is not a
reliable answer. Recording an error updates the observation record without
advancing the accepted learning step.

When E05 is selected, the learner produces the corrected form. When V16 is also
selected, the teacher returns later for an uncued retest. Those are separate
steps: repeating a just-heard phrase does not establish independent recall.
Weak-item tracking can continue after a successful retest without claiming the
item is permanently mastered. Explicit skips stay pending and any reduced scope
is labeled accurately.

The [scripted demo](../examples/demo-session.md) illustrates this with newly
written phrases. It is an explanatory artifact, not a recorded test or personal
history. The [acceptance scenarios](../examples/prompt-scenarios.md) define expected
behavior for interruptions, source conflicts, optional selections, and completion.
Actual voice-host performance requires testing in that host; static rule coverage
alone does not verify it.

## Portability is an explicit handoff

The state hierarchy is:

```text
Course → Day/Lesson → Segment → Item → Micro-step → Accepted response
```

A portable checkpoint records that hierarchy, the pending prompt, selected rules,
error/weak-item queues, independent block statuses, and review scope. The learner
saves it privately and provides it to the next conversation along with the
needed lesson. The [checkpoint template](../prompts/checkpoint-template.md) gives
a reusable format and transfer instructions.

This is manual transfer. The repository does not persist a learner database,
authenticate to a chatbot, listen to the microphone, reconnect voice sessions,
or recover chats it cannot access. A model may lose context or fail to follow a
prompt, and host behavior varies. The protocol makes the expected behavior
inspectable; it does not turn those expectations into application guarantees.

## Bring your own material

Supply a lesson identifier and target table with spelling, pronunciation guidance
when available, part of speech, meanings, collocations, and support-language
glosses. Add the story only if you want Text practice. Preserve the original
source privately so discrepancies can be checked. Do not treat automatically
generated transcripts as authoritative without checking them against that source.

Persian gloss support reflects the supplied course method. Other support languages
can be used by an explicit learner adaptation while keeping the same acceptance,
source, and checkpoint principles. Do not fabricate translations and label them
as source material. The public three-item demo provides a fully usable example
without implying that it is part of the 42-lesson course.

The course's full audio, video, PDFs, collocations, and stories remain with their
respective rights holders and are not granted rights by this project's code
license. Use your own or appropriately authorized learning materials. Public
examples should be original or separately licensed, and actual learner records
should remain private.
