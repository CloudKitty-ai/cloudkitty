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

## First real use — Experiments thread, Fable, 2026-09-24

Gated `experiments/fog-deafening-2026-09-23/RESULTS.md` plus the
same-commit F-052 entry and the edited F-026 line. Fresh read
byte-identical to the recorded JSON; 30/30 seeds asserted; ~58
arithmetic claims all matched, zero ROUNDING flags.

**Run 1: FAIL, four items, all real.** (1) "the same deafening
measured −0.011" — F-026 had no all-kinds arm; −0.011 was purr-deaf
alone, both-deaf measured +0.013 (the prereg inherited the
mis-citation; fixed by deviations appendix 1c457ab). (2) "the F-026
signature exactly" for here-deaf — contradicted by the doc's own
table (−0.455 is a real mean cost; the whisper was flat-welfare
purr-deafening). (3) "its redundancy claim is a global-vision
property" — attribution-shaped wording in Decision rules on an
F-number line, barred by F-026's own SC-005. (4) instrument SHA: the
collecting harness copy was afc43ae's, not 207f8c9's (caught from
tool_sha256 in the battery headers). Advisories also fixed:
family-arm additivity wording, mid-collection HEAD move disclosed,
reader's one-sided P2 check disclosed.

**Runs 2–3: re-verified the fixes; PASS.** Run 2 caught one more
provenance overpromise in the fix itself ("predictions and outcomes
named in prereg §Instrument" — the prereg names the mutations only).

**Verdict on the gate**: it caught source mis-citations and
SHA-provenance errors a numeric diff cannot see, on a doc whose
numbers were 100% clean. The claim-kind rubric (kinds 3 and 5) did
the work. Standing gap it named: mutate.sh keeps no log, so rule-5
reds are permanently UNDECIDABLE to the gate — a mutate.sh log file
would close it (Harness's call).

## Second collection addendum — Experiments thread, Fable, 2026-09-24

Gated the residual-split addendum (free and rows arms, prereg-2.md)
plus F-052's updated attribution. Fresh six-arm read byte-identical
to the recorded deafen-read-2.json; 43 arithmetic claims all matched.

**Run 1: FAIL.** (1) WEAK-on-F-line: "the position of unseen cats
carries the load" — the rows arm erases position AND unseen-cat words
together; reworded to "what a cat hears about unseen cats". (2) The
F-052 headline gained a clause against prereg-2's own "headline does
not change" rule — reverted. (3) prereg-2's quoting rule was broken:
the replaced attribution bound was overwritten unquoted — the
addendum now quotes it verbatim. It also caught a wrong hash claim in
frozen prereg-2 text (tool hash differs between collections by
construction) — deviations appendix 8390b28.

**Run 2: PASS**, quotes verified verbatim against f4d66d7.

**Verdict on the gate**: second write-up in a row where every number
was clean and the fails were attribution wording and the write-up's
own declared rules — the gate is functioning as a discipline on
claims, not just a diff. The declaration itself is now twice a
source of gate-caught errors (mis-citation, hash wording): worth a
line in the skill someday — the gate reads the prereg as ground
truth, and preregs carry prose too.

## Third collection addendum (R sweep) — Experiments thread, Fable, 2026-09-24

Gated the direction-sweep addendum plus F-052's appended sentences.
Fresh twelve-arm read byte-identical to the recorded
deafen-read-3.json; 60 arithmetic claims matched, P7-P9 all held.

**Run 1: FAIL, three WEAK on F-052 lines.** (1) The 0.97 recovery
credited to "bearing" where the dir arms also keep unseen-cat words
(the same over-attribution the second addendum's first run caught —
twice now, same author, same shape: crediting the named manipulation
and forgetting what rides along). (2)+(3) "sounding too near is mild"
claimed on welfare where the asymmetry lives in the distress tail;
at matched offsets welfare is level (dir28 − dir5 = −0.037). The
gate computed the matched-offset comparison itself.

**Run 2: PASS** after rewording; the gate re-derived the new per-seed
counts (dir16's 53 ticks from 2 seeds; intact's 4 nonzero seeds).

**Verdict on the gate**: third write-up, still zero number errors
reaching main and every fail a claim-scope error. The repeat pattern
(over-crediting the named variable) is now a known author failure
mode the gate reliably catches; worth a fixture plant someday.
