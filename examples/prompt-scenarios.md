# Prompt acceptance scenarios

These are manual behavioral acceptance specifications using the original demo.
They are **not recorded live voice-test results**. A written protocol check can
confirm rule coverage; it cannot prove that a particular chatbot handles live
audio, interruptions, or memory reliably. Record the chatbot/version, selected
rules, observed response, and result when running an actual session.

| # | Setup and event | Expected behavior | Rules |
|---|---|---|---|
| 1 | No material or checkpoint is supplied; learner asks to continue. | State that the exact source/position is unavailable; ask for the needed lesson/checkpoint. Do not claim a remembered item. | C10, C13, C16 |
| 2 | Active Noon, demo-a-2 collocation prompt; silence or disconnect. | Pending prompt and last accepted answer are unchanged. Do not accept, skip, or complete the item. | C11, C12 |
| 3 | Accepted demo-a-1 gloss; interrupted demo-a-2 answer; V04 kept. | Ask only for demo-a-2's current answer again. Do not restart Demo A. | C10–C12, V04 |
| 4 | Teacher prompt cut in half; V03 kept; learner says Continue. | Repeat the full current prompt before accepting a response. | C10–C12, V03 |
| 5 | Urgent summary during an unfinished Noon block. | Report item, micro-step, last accepted answer, error/weak items, each block status, and next action; mark PAUSED, not COMPLETE. | C03, C08–C09 |
| 6 | Finish all Morning tasks. | Announce Morning complete, summarize/checkpoint, and end. Noon, Evening, and Text stay unchanged. | C04–C07 |
| 7 | Learner says Where are we? after pasting the demo pause checkpoint in a new chat. | Report Noon PAUSED at refill collocation recall with kettle retest pending; credit the supplied checkpoint and do not advance. | C09–C13 |
| 8 | E05 and V16 kept; wrong source collocation. | Give correct form, require production, queue later uncued retest. Immediate imitation alone does not clear the retest. | E05, V16 |
| 9 | E05, E10, V16, V17 remain pending. | Do not silently impose corrected repetition, extra weak-item drills, a mandatory retest gate, or shuffled Evening order. Still record observed errors and apply core acceptance rules. | C08, C12, selection policy |
| 10 | Canonical demo says bookmark; noisy transcript says bookmarket. | Use bookmark and flag the conflict if relevant. Do not alter canonical targets. | C16 |
| 11 | Learner completes Noon, then asks for Text explicitly. | Start only Text. Text completion never implies Evening completion. | C06–C08 |
| 12 | E01 kept strictly; learner says Stop. | Pause silently without summary, acknowledgment, or new content. Resume only on Start/Continue. | C01, E01 |
| 13 | E01 kept strictly; learner says Urgent summary. | Provide the requested checkpoint, then pause. Do not confuse this with Stop alone. | C03, command distinction |
| 14 | V17 kept; Evening order is 3,1,2; interruption after item 3. | Resume the next pending step in saved order; do not reshuffle or infer item 1 was accepted. | C10–C12, V17 |
| 15 | Learner requests Skip this item. | Record skipped/pending status; never count it as mastered or silently claim full original-scope completion. | C08, completion gate |
| 16 | Calendar day changes with Noon paused. | Keep the same lesson, block, and pending micro-step. | C08, C10 |
| 17 | Learner requests a sample cumulative review of lessons 1–5. | Record sample scope separately; do not mark the full 1–5 milestone complete. | C08, C14 |
| 18 | V14 kept; ambiguous speech could be correct. | Ask one repeat/confirmation before diagnosing an error; do not accept an unclear response. | C12, V14 |
| 19 | Learner removes V02 or V15. | Explain if necessary that C11/C15 still apply; silence cannot advance and prompts remain short and single-purpose. | core precedence |
| 20 | Two supplied checkpoints disagree. | Identify the smallest conflict and resolve it using available accepted-response evidence or a focused question. Do not merge invented history. | C10, C13 |

Suggested result record, kept privately when it contains learner responses:

```text
Scenario: [number]
Host and model/version: [known value or unavailable]
Mode: [text simulation | live voice]
Selected optional rules: [IDs]
Observed response: [brief exact description]
Result: [PASS | FAIL | NOT RUN]
Evidence: [private session reference]
```
