# Trial record

Every run of /accuracy-gate lands a section here: fixture reds,
real-write-up gates, pass or fail. Edits to SKILL.md check themselves
against this file — the skill is shaped by what actually failed, not
what plausibly could.

This file is append-shared (THREADS.md §1): the thread that runs the
gate appends its own section and never touches another thread's.
Harness appends through a worktree and a PR; the owning experiment
thread appends beside its write-up commit.

Lifetime: shakeout evidence, then frozen (owner ruled 2026-09-25;
the close-out procedure is in the condense skill's SKILL.md
§TRIALS lifetime). Shakeout closes on the owner's word, backstop
2026-10-15.

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

## World-size screen — Experiments thread, Fable, 2026-09-25

Gated world-size-screen-2026-09-24/RESULTS.md + F-053 + the GEN2
shelf pointer. Fresh read byte-identical; ~183 numbers all matched;
P1/P2 correctly scored as failing as declared.

**Run 1: FAIL, and the catch mattered more than usual.** The
harm-rule cell list — the passage that BLOCKS follow-up runs — was
under-inclusive: size28/rows (streak 9,278), size40/dir (2,293) and
size40-d2 (1,796) all had worse tails than named cells. A judgment
list under-protects; the fix was a declared threshold (every cell
over a 1,000-tick streak), which the gate then verified captures
exactly 13 cells with no unnamed crossing. Advisories fixed: P4
rescored "mixed as declared" (the dir cells fail the tail
prediction — a finding), a mislabeled saturation range, an
overclaimed "worst streaks" list (twice — the gate ordered all 13
streaks itself and pre-approved the final wording).

**Verdict on the gate**: fourth gated write-up; the recurring author
failure mode is now precise — lists framed as complete that were
assembled by eye. Threshold-defined lists are the fix the gate keeps
converging on.

## Reward-shape screen — Experiments thread, Fable, 2026-09-26

Gated reward-shape-screen-2026-09-24/RESULTS.md + F-054. Fresh read
byte-identical each round; the reader was extended mid-gate (trace
finals, sleep shares) at the gate's own suggestion so P3/P4 claims
became recoverable, and the additions changed no prior value.

**Run 1: FAIL.** An 8x headline figure that was really the ratio to
the null; a last-quarter label on final-update values; a doubled wall
time; and the substantive catch — "pressure doses behavior" was
backwards (the prereg magnitude-matched hard and cvx; the gate
computed realized per-tick terms, which order the OTHER way) — plus
the sleep-share gap: the prereg's named harmful dodge was unread, and
reading it revealed the arms buy placement partly by sleeping less.
**Run 2: FAIL.** Caught that my F-054 edit had silently no-opd (a
str.replace mismatch under different line wrapping, with a success
print that lied) — the register still said "dose"; also a
distress-tick claim that hid hard-s1's 4,737 behind hard-s2's 187.
**Run 3: PASS.**

**Verdict on the gate**: two new author failure shapes on record —
(1) unasserted text replacement (fix: every scripted edit asserts its
match; adopted), (2) citing the flattering member of a pair (the
187). And one instrument lesson: the gate's "make the reader emit
what the prose claims" suggestion is the recoverability rule working
in reverse — the write-up wanted numbers the reader did not print,
and the fix was the reader, not the prose.

## 2026-09-26 · enrichment-bonus screen (Experiments) · PASS round 7 of 7

Gated: `experiments/enrichment-bonus-screen-2026-09-26/RESULTS.md` +
F-055 copy + gen3 inputs §Screen verdict copy. Every number clean
from round 1 (fresh read byte-identical to recorded all seven
rounds); all six failures were prose. Author failure modes, for the
fixture:

1. **Rewrote the frozen decision branches into the recommendation**
   (round 1): merged P1-fail and a not-fired P2 branch, dropped "the
   fork is the owner's", presented the session's redesign as a fired
   branch. Same shape as the reward-shape screen's dose framing:
   the write-up wants the story it already believes.
2. **Paraphrase in quote marks** (rounds 1, 2): the owner's proposal
   and a shelf bullet both got quotation marks around words they
   never said. Quote marks now mean verbatim-or-nothing.
3. **A statistical claim with no test behind it** (round 1):
   "statistically indistinguishable" — a paired test actually
   separates the arms; the honest statement was a range overlap.
4. **The prereg's own definition contradicted a convenient claim**
   (round 3): "not the F-054 dodge" while bonus-s1 broke the ±0.015
   band P4 itself labels "the F-054 dodge, watched", plus a
   non-discriminating discriminator (low-need fall — F-054 moved the
   same way). The gate caught it by reading PREREG, not the numbers.
5. **NEW CLASS — hedges and labels do not survive copying** (rounds
   4, 5, 6): RESULTS said "consistent with / plausibly / this
   session's recommendation / if she takes the branch"; the F-entry
   and shelf copies dropped them and stated cause, attribution, and
   precedence as fact. Three consecutive rounds each caught another
   stripped qualifier. The copy check must compare HEDGES at the
   same fidelity as numbers — added to the round-6/7 subagent brief
   as "hedges and labels must survive the copy"; recommend the
   fixture grow a stripped-hedge plant.
6. **Unscoped generalisation from two points** (round 5): "β was not
   the binding constraint" from two β values × two seeds; scoped to
   the tested 0.015–0.03.

Also of note: round 7's watch items (title cost attribution rides
the dose gradient; "not an incentive" is diagnosis under a blanket
label) were judged SUPPORTED but are the same genus as item 5 —
titles compress, and compression strips hedges.

## 2026-09-26 · cross-world cost reads (Experiments) · PASS round 4 of 4

Gated: `experiments/cross-world-cost-reads-2026-09-26/RESULTS.md`.
Numbers clean every round; the four-round arc was all synthesis.
New failure modes for the fixture:

1. **An abort the author missed** (round 1): the welfare stop fired
   (lam-s1 seed 870015, 1,000-tick streak) and the write-up said "no
   leg aborted" — the author read the driver log's markers, not the
   rows. The gate's seed/abort audit caught it. Lesson mechanised in
   the brief: list every aborted_streak row and every short row.
2. **Synthesis outran the design** (rounds 1, 3): "no measured gap",
   "one fact, two views", "costs every mind" — each a narrative the
   comparison could not support (confounded with training world;
   same-mind pairing showed the world cost is mind-dependent). The
   fix each time was letting the sharper decomposition replace the
   story.
3. **A comparator that predates its field** (round 3): citing 0
   distress ticks from a cell with no dist_ticks field; the honest
   number came from the fresh same-config leg (360).
4. **Universals over eight legs** ("across the board", "generally")
   falsified by one leg (hard-s2 at 347). Check every leg before
   writing a quantifier.
