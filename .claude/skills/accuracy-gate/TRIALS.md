# Trial record

Every run of /accuracy-gate lands a section here: fixture reds,
real-write-up gates, pass or fail. Edits to SKILL.md check themselves
against this file — the skill is shaped by what actually failed, not
what plausibly could.

This file is append-shared (THREADS.md §1): the thread that runs the
gate appends its own section and never touches another thread's.
Harness appends through a worktree and a PR; the owning experiment
thread appends beside its write-up commit.

## Fixture red — Harness thread, Fable, 2026-09-23

The rule-5 red for the skill's first commit. mutate.sh does not fit
(the assertion under test is a subagent procedure, not a test
command; the mutation is the fixture's four plants, not an edit to a
clean file) — hand-rolled with the prediction written in the session
before the run, per the design the owner ruled 2026-09-22.

**Predicted**: FAIL with exactly four failing findings — the count-7
teacher placement cell (0.412 vs fresh 0.399); Prediction 1's
inverted gain comparison; "count 8 is measurably the best world"
WEAK-or-CONTRADICTED in Decision rules; the paraphrased #390 quote
("six beams it is" vs verbatim "6 beams"). Seed-count assertion
passes; fresh JSON identical to recorded.

**Got**: FAIL. All four plants caught, each at the predicted kind
and location; seed counts asserted (62 legs × 30 seeds); fresh JSON
identical to recorded; meow table recomputed from raws (48/48
match). The subagent also failed four findings the prediction did
not name: the need<5 range (cnt8-s2 = 0.223 outside "0.32–0.33"),
the crosstab starts range (2,660 outside "2,700–2,900"), "the three
longest seeds" (replay took 870009/520, not 870028/589), and a WEAK
call on the F-051 decision line. Harness verified the three
mechanical ones against the raws: all real, all inherited verbatim
from the committed tier 6 section — first-run true positives, not
gate bugs. They are now listed in `fixture/expected-findings.md` as
expected inherited findings, and the future-run bar is: the four
plants plus the inherited list, nothing else.

**Verdict on the gate**: red confirmed; no false positive
attributable to the skill. The prediction's "exactly four" was wrong
only because the fixture's source document carried real errors — a
fact about the doc, not the gate, and itself evidence the gate earns
its keep. The real-doc findings go to Experiments (their file) on
the owner's word.
