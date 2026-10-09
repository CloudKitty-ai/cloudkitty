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

## 2026-09-27 · enrichment-decay stage A (Experiments) · PASS round 3 of 3

Gated: `experiments/enrichment-decay-sweep-2026-09-26/RESULTS.md`.
Numbers clean; failure modes: (1) an inverted ordering claim ("below
as often as above" where 14/16 pairings ran one way) — the write-up
resisted a result unflattering to its own prediction; (2) an
unreported WELFARE-EXPECTATION BREACH (4,108 > the prereg's ≤2,286
line) — the author again read markers, not rows, for welfare
accounting; (3) a phantom "seed-matched pairs" control (run indices
differ; no shared randomness exists); (4) a wrong PREREG hash copied
from the previous screen. Round 3's advisories (greedy-vs-training
divergence; the recommended corner nearest the over-tending bar)
went to STAGE-B-INPUTS rather than post-PASS edits.

## 2026-09-27 · free-register baseline (Experiments) · PASS round 10 of 10 · RETROACTIVE

First retroactive gate under the owner-approved five-file package.
Found and fixed real damage in a nine-day-old doc: three wrong
emission percentages carried forward as Gen 2 comparison numbers
(also frozen into PREREG amendment 2 — noted, not edited); a
double-rounded cell; and a control-mechanism story ("speaker silent
30+ ticks, stale row") REFUTED by measuring the control pool the
reader actually builds (99.5% other-word speakers, median 2 ticks) —
which re-opened F-048's row-vs-word attribution, retitled the
finding, and killed a planned instrument refinement that already
described the existing instrument. New failure modes for the
fixture: (a) DOUBLE-ROUNDING — deriving printed figures from
already-rounded reader outputs instead of raws (three instances);
(b) THE CORRECTOR NEEDS THE GATE TOO — the correction addendum
itself failed three rounds (wrong per-word claim, truncated quote
that failed to retire, count-slip after a list edit); (c)
F-INHERITANCE SURFACES — title, index row, and body paragraph of the
downstream finding each carried the refuted claim and each needed
its own retirement; a caveat below the fold does not retire a title.
Also this window (stage-B guard): SHARED-CONSTANT VACUITY — a
reference implementation importing the trainer's constants moves
with the mutation; independent literals only (one vacuous red caught
it live).

## 2026-09-28 · cross-platform determinism (Experiments) · PASS round 4 of 4

Gated: `experiments/cross-platform-determinism-2026-09-27/RESULTS.md`.
All numbers clean every round; all four rounds' failures were SCOPE
on the owner-ruling line (the evidence-archive consequence bullet):
r1 extended one checkpoint/world/greedy to "eval batteries"; r2
dropped all-seats + the zeroed observation clock; r3 dropped seeds ×
horizon. New failure class for the fixture: CONSEQUENCE-LINE SCOPE
EROSION — the bullet that applies a result to a ruling re-states the
scope from memory and loses a clause per hop; the fix is carrying
the full measured scope INTO the consequence sentence, plus naming
the extension ("an inference from the rate, not a measurement").
Also caught: a characterisation literally false against the code
("asserted before any comparison" when layer 1 prints first);
"single-threaded" contradicted by the raws' pre-set-call
torch_threads field (doc now cites the code); a modal overclaim
("would flip" where the drift stats support "could"). One real
cross-platform drift surfaced by the gate itself: 1 ulp in a
Python-side exp/log reduction — worth a doc bullet, invisible to
the headline claim.

## 2026-09-28 · seating analysis v1, gen1-A baseline (Experiments) · PASS round 2 of 2

Gated: `experiments/seating-analysis-2026-09-28/RESULTS.md` (first
run of the standing instrument). Round 1 found a REAL INSTRUMENT
DEFECT the write-up inherited: PRINTER-TIE NONDETERMINISM —
`max(set(xs), key=xs.count)` resolves ties by hash seed, and two
per-seed top-partner votes were genuine 2–2 ties, so the doc's
"verbatim" block failed to reproduce on one cell per run. Lesson: a
"verbatim" fence is a determinism claim about the PRINTER, not just
the reader; gate briefs should re-run printers under two or more
PYTHONHASHSEED values. Also round 1: two social-structure sentences
CONTRADICTED BY THE DOC'S OWN TABLE (a "mutual modal" claim over a
tie; a "top-two with every cat but X" claim where X's side also
ranked the cat top-two — the author narrated the matrix from
memory instead of re-reading it by row); an F-047 clause carrying
F-050's "removed" language (F-inheritance across sibling findings);
"statistically stationary" asserted off nine successive-window
values with an unmeasured causal attribution. Round 2 clean; one
WEAK ("closest spatial pair" where the distance column ties)
adopted as the verifier's exact wording. Guard side, same arc: the
worst-gate mutate red came back VACUOUS once — the test sampled
only the one cat whose fixture median is insensitive to the dropped
index (rig-encodes-a-belief, in a guard); reference all rows.

## 2026-09-28 · seating-analysis flags addendum (Experiments) · PASS scoped round 2

Gated: the flagged-values addendum appended to
`experiments/seating-analysis-2026-09-28/RESULTS.md` (owner's
representation rule: |x − group median| / sample σ, † 1–2σ, ‡ ≥2σ).
Design note that worked: the flags mode is OPT-IN (`--flags-only`)
so the already-gated fence stays byte-identical — verified by md5
against the r2 stamp; no re-gate of the main doc needed. Round-1
FAIL was pure CORRECTOR-NEEDS-THE-GATE: the reading paragraph
miscounted the ‡ rows in the block pasted two lines above it (said
7, block has 8; said five-of-seven Biscuit, is six-of-eight) and
cited "the doc's first bullet" for what is the second. Count claims
about a pasted block must be grepped from the block, not recalled.
Verifier extra: simulated the "third of cells pass 1σ by chance at
n=5" hedge (0.322 at 100k draws) — hedges are claims too and this
one held.

## 2026-09-28 · seating-analysis pair-structure addendum (Experiments) · PASS scoped round 2

Gated: the pair-structure addendum (owner's territory-map reading,
confirmed and recorded). Every pair/modal/JS number survived both
rounds; the two round-1 failures were both COMPRESSION ERRORS IN
THE SUMMARY SENTENCE: "south in ALL five seeds" silently switched
referent from south-of-Miso (true, 5/5) to south-of-midline (false
for three cat-seeds), and "attached through Clementine" dropped a
94%-as-large tie to Biscuit. Same lesson shape as the flags round:
the table is safe, the sentence ABOUT the table is where errors
live — a summary clause that names a set ("all five", "through X")
gets re-derived against the set, not remembered. Verifier practice
worth keeping: it graded "west of center" and "south" against the
SAME midline, catching the referent switch.

## 2026-09-29 · enrichment-decay stage B (Experiments) · PASS round 3 of 3

Gated: `enrichment-decay-sweep-2026-09-26/RESULTS-B.md` + F-056 +
the F-055 dated note. Regeneration clean every round; all failures
prose. New failure classes: (1) UNIT RELABELING ACROSS A QUOTE
BOUNDARY — "leg" meant a 30-seed battery leg in the prereg and in
the doc's own header, then silently shrank to one seed-episode in
the welfare accounting, minting a fake order-of-magnitude margin
(real: ~5×); (2) MEANING-INVERTING COPY DRIFT — "ran both variants
past the traction bar" (= cleared it, in F-055's own idiom) for
"both missed"; the F-entry paraphrased the RESULTS sentence and
flipped it; (3) CROSS-DOC NUMBER PAIRING — the Professor
percentiles quoted from memory paired p17 with the wrong β
(STAGE-B-INPUTS says under-p5 for 0.03). Also: the prereg's
decision bullet must be QUOTED AND ITS BINARY STATED (round 1
substituted a third reading for mechanism-vs-corner), and a
register cross-reference (F-055's Invalidated-by) is a claim needing
character-exact quoting plus an explicit consistency resolution —
here a dated note in F-055, with the interpretation stated openly
for the owner's strict-reading call.

## 2026-10-01 · stage-B seat-lift addendum (Experiments) · PASS scoped round 3

Gated: the per-seat play-lift addendum to
`enrichment-decay-sweep-2026-09-26/RESULTS-B.md`. All 40 arithmetic
claims clean in every round (verifier re-derived every lift cell
independently, grouping arms by name prefix, not the reader's
FAMILIES). Round-1 fail: QUOTATION MARKS AROUND A PARAPHRASE — the
memo's discriminator compressed to "if only Biscuit moved…" and
quoted, with "predicted" where the memo says "Discriminator, zero
training"; an out-of-repo memo is quotable only verbatim, and the
gate could read it (full path in the doc). Round-2 fail: THE
CORRECTION MINTED A NEW FALSE UNIVERSAL — "all four seats negative
on both seeds" for a 7-of-8 fact; precision-raising rewrites need
the same cell-level re-derivation as the original claim. Also
adopted: name the absent noise line instead of leaning on "line
noise"; "unpaid mechanism" → "accrual gate" (open-gate play IS
paid).

## 2026-10-01 · dead-or-held probe (Experiments) · PASS (RESULTS-C r2 + F-057 copy-check r2)

Gated: `enrichment-decay-sweep-2026-09-26/RESULTS-C.md` + F-057 +
the stamp. Regeneration byte-clean throughout (~100 arithmetic
checks matched every round). Round-1 fails: the "LEG" UNIT
MISLABEL'S THIRD APPEARANCE (an aborted seed's episode is not a
leg); an arc-scope claim ("the arc's worst") contradicted by stage
A's own table; a "whole program" first-ever claim contradicted by
a different arc's doc (cross-world's positive deltas — scope
superlatives need a sweep, not a memory); a WEAK inherited from
THE FROZEN PREREG ITSELF (PREREG-C paraphrased F-019's direction
backwards — recorded as an erratum note in the deviations file,
noted not edited, free-register precedent); and a decision-rule
branch applied without stating no branch condition was met as
written. F-entry copy-check then caught the SAME nearest-branch
qualifier dropped again in compression, numbers cited from the
VERIFIER'S OWN DERIVATIONS with no printed source (now printed in
RESULTS-C), a deviations count gone stale inside the package, and
a confound hedge dropped. New practice from the verifier: the
stamp's raw hash now states its recipe in one clause (no prior
stamp recorded one — relay to Harness, SKILL.md is theirs).

## 2026-10-03 — RESULTS-D (joint release arm) — FAIL r1, PASS r2

Gated: `enrichment-decay-sweep-2026-09-26/RESULTS-D.md` + F-058 +
the stamp. Regeneration byte-clean (verbatim block byte-identical,
fresh == recorded JSON on a full recursive compare, every trainer-
side number confirmed from the artifacts). Round-1 fails, all
prose: (1) MAGNITUDE-WORD SHORTHAND — "two orders inside the line"
for a 14.7× ratio; compute the ratio BEFORE choosing a magnitude
word, "roughly 15× and 900×" is both shorter and true. (2) A
UNIVERSAL MINTED IN COMPRESSION — "under every reference" on the
F-line, when both totals exceed l14-s1's 0.0722; the doc's own
sentence had it right ("within/below l14's totals") and the
F-entry compression upgraded it to a universal — the F-056-era
"corrections mint new false universals" class, now appearing at
first writing. (3) SEED-COMPRESSION DROPPING A TWIN — "s2 improves
all 30 pairs" when BOTH j14 seeds do; naming one seed implies the
other failed. (4) CITATION FROM MEMORY — F-058 cited "RESULTS-D
§Decision rules", a section that document does not have; cite
sections by LOOKING at the document's own headings, and name the
prereg when the rules live there. Also fixed from reported-only:
the "asymmetric stops never fired" wording (plateau is itself a
declared stop and is what fired — name WHICH stops never fired)
and a provenance line that over-claimed what VALIDATION.md records
about the first replay attempt. Verifier practice note: it
accepted the hash-recipe clause introduced at RESULTS-C without
reverse-engineering — the recipe line pays for itself.

## 2026-10-04 — RESULTS-D control-provenance addendum — PASS scoped r3

The OWNER caught what the gate structurally cannot: a LOAD-BEARING
OMISSION. RESULTS-D leaned on "the recorded l14 runs are the
control" without stating that the control's provenance check (the
bitwise replay of current code against the recorded runs) ran —
the chain lived only in PREREG-D §Control and VALIDATION.md. The
gate verifies claims that are PRESENT; it has no inventory of the
claims a conclusion NEEDS. Writer-side rule from this: when a
conclusion leans on a verification, the gated doc states in one
line that the verification ran and where its record lives — "the
control claim leans on it, so it needs one line in the results
either way" (her words). Addendum paragraph gated scoped r3, all
SUPPORTED; the verifier's one improvement (name the regeneration
path for non-archived evidence) taken.

## 2026-10-04 — RESULTS-L (E-visibility discriminators) — FAIL r1, PASS r2

Gated: `enrichment-decay-sweep-2026-09-26/RESULTS-L.md` (no
F-entry; the F-058 dated note follows separately). Round-1 fails:
(1) BORROWED COMPARATOR, SCOPE WIDENED — "arc maximum 0.0915"
lifted from RESULTS-C where it was the PROBE's maximum; the arc
maximum is b14-s2's 0.0955, sitting in RESULTS-C's own comparator
line one table up. A borrowed superlative inherits the scope of
the doc it came from until a sweep says otherwise. (2)
TRAINING-TRACE NUMBER WEARING AN EVAL LABEL — "E p50 at eval
~0.55–0.62" was lastq trace values; the real eval medians
(0.685/0.735, from the raws) were never printed anywhere, and the
fix had to derive them and name the derivation in Regeneration.
Side-label every stock/stat with its SIDE (train trace vs eval
battery) at first write. (3) "VERBATIM" ON A REFORMATTED BLOCK —
the doc's compact one-line-per-kind form is faithful in values
and key order but is not what the reader prints; label the
transformation. (4) READ FENCE NOT REPRODUCIBLE AS WRITTEN — the
summary globbed npz from the output path's parent, so the
verifier's scratch --out found nothing; a fence must be runnable
to a scratch path without touching recorded copies (--npz-dir
added; fence re-run byte-identical). Also surfaced: the frozen
prereg's "tick-exact" described a mean-happiness-at-4dp checksum
proxy — erratum note, prereg never edited; the same wording sits
in gated RESULTS-D's provenance paragraph and e_edges_replay's
docstring (same proxy there), flagged here rather than silently
rewritten post-gate.

## 2026-10-04 — F-058 dated note copy-check — FAIL r1, PASS r2

The note's numbers were all clean; the fails were framing. (1)
QUOTE WITH A SILENT CUT — the invalidation clause quoted without
an ellipsis for its dropped middle clause; RESULTS-L's own copy
kept the "…" and the note's didn't survive the re-type. (2) A
NOTE THAT PRE-DECIDED THE OWNER'S CALL — "a yes invalidates
nothing by itself" contradicted the clause's own "or" (the total
clearing 0.10 is sufficient as written) while ending "her
reading, not this note's". A note that frames an owner ruling
states each answer's consequence FROM THE TEXT and stops; it
never predicts or softens the outcome. (3) "gave back its gain"
compression (s2 kept ~10%) — print the endpoints and the
universal corrects itself.

## 2026-10-04 — RESULTS-L E-occupancy addendum — FAIL r1, PASS r2

Her free-read ask (sighted-vs-blind E occupancy) confirmed the
satiation story with non-overlapping means/p25 at matched play.
Round-1 fails: (1) THE ASK QUOTED TWO WAYS — the reader docstring
dropped her "before Gen 3" while the doc header kept it; when the
same owner words appear in two places, ONE is the copy of record
and the other is checked against it at write time. (2)
"rarely" FOR A 22–27% SHARE — an intensity word standing in for a
number the reader did not yet print; the fix added the low-edge
column so the comparison (22–27% vs 31–36%) regenerates instead
of living in prose. (3) "near full" WEAK — at-cap shares were no
higher than blind's; the supported claim was HIGHER, not near
full. Self-caught before the round: a two-cell table
transcription error (values from the neighboring row) — pasted
tables get re-diffed against the print, not retyped.

## 2026-10-04 — F-058 ruling edits + F-059 mint + doctrine 11/12 — FAIL r1, PASS r2

Copy-check of a ruling's execution (owner "A) confirmed" / "B) all
items confirmed"). Round-1 fails: (1) CELLS-VS-DIRECTION — "the
cells the test was not aimed at" when the signature sat in the
TESTED cells in the untested SIGN; name which axis the instrument
missed. (2) A MECHANISM MINTED IN A SUMMARY — "timing play against
decay" appears in no gated read; the gated claim was "holds the
stock higher". (3) DOMAIN LINE INCOHERENT WITH ITS OWN NEW RULE —
F-059 declared "trained arms at declared settings" while its first
trigger requires an eval-time ablation; rule 11's wider form
existed one file over. (4) A PEER'S FRAMING RELAYED INTO DOCTRINE
UNCHECKED — the Professor's "self-blind + loose leash = the
measured wide-tail recipe" is CONTRADICTED by the register (arc's
widest tail: stage A d100-1000-s2 at 4,108, blind at STANDARD
leash; an E-visible arm carried the abort): relayed authority gets
the same fact-check as my own prose before it lands in a doctrine
file. Post-round: the unsourced "project ≥3-seed bar" got a
checkable home (gen3-roadmap-inputs-2026-10-04.md) and rule 12's
normative stretch clause was cut on the verifier's caution.

## 2026-10-05 — roadmap-inputs-2026-10-05.md (RLHF=1.2 + self-other pilot) — FAIL r1, PASS r2

Copy-check of a confirmations record built from a peer relay (her
in-session word: "Confirmed"). Round-1 fails: (1) MODALITY DROPPED
— the source's "must be co-designed" became "is co-designed",
turning a banked requirement into settled design; a requirement
keeps its modal verb. (2) PROFESSOR'S REASONING UNLABELED — the
ladder/pump argument sat as plain content in a doc titled "owner
confirmations" when only the 1.2 slot is hers; in a confirmations
record, every sentence carries its author. Also took the "One
trap" note (the source leaves room for more traps). Quotes,
numbers, formulas clean both rounds.

## 2026-10-06 — roadmap-inputs-2026-10-06.md (nine-item walkthrough record) — FAIL r1, FAIL r2, PASS r3

Copy-check of the 1.3 + versioning confirmations walkthrough.
Round-1 fail: PUNCTUATION INSIDE A QUOTE — the framing line
carried my semicolon where the source (Professor's stage-b
review) has a full stop and capital; the verifier found the true
source file unprompted, and a quote is verbatim down to its
punctuation or it is a paraphrase without quote marks. Round-2
fail: ACCEPTANCE OVERREACH — "Experiments' reading, which she
accepted" when her "Yes" answered a proposal that itself left
that reading open; a yes to a proposal is not a yes to every
clause inside it, least of all one the proposal deferred.
Verifier-side lesson both rounds: the coordinator's KEY-LINES
source summary omitted relay lines ("agreed on all of these",
the transfer-story parenthetical), producing flags the full text
cleared — hand the verifier whole sources, or expect to adjudicate
its misses yourself and say so in the record.

## 2026-10-08 — partner-absent-split RESULTS.md (full gate, r1 FAIL → r2 PASS)

Full gate (Read fence re-run, three-way compare byte-identical) on
`experiments/partner-absent-split-2026-10-07/RESULTS.md`, with copy
checks on the refusal-baseline addendum, gen2-kickoff-rulings §3/§5,
and three GEN2-INPUTS insertions. First stamp under the rawdir-hash
v1 recipe (#443).

r1 FAIL, two classes, both wording while all 22 arithmetic claims
held:
- Owner-ruling overreach in prose: the decision feed wrote "the
  owner ruled" where the named record itself says announced-outcome
  with flag-if-otherwise. Same class as the 10-06 r2 acceptance
  overreach — the write-up firmed a scope the record kept soft.
- Cross-doc precision drop: the ruling record compressed "185 of
  189 at distance 2, 4 at distance 3" into "one tile short",
  contradicted for 4 rows. A summary line in a SECOND doc rounded
  away a tail the gated doc kept.
Also reported (non-failing, fixed anyway): an over-broad "no
learning, mask or price can touch these"; a "same day" date
ambiguity; an unsourced "welfare-null"; the <= 2-tick run-gap
reader constant now disclosed as not prereg'd.

r2 PASS on the five edits, full-set verdict PASS. Coordinator-side
lesson: derivative summaries of a gated doc (ruling records, shelf
lines) are where precision quietly drops — gate them as companions
every time, it is exactly where both failures lived.

## 2026-10-09 — gen2-sitting-rulings record (copy check, r1 FAIL → r2 FAIL → r3 PASS)

Ruling-record copy check, fresh verifier, her thirteen in-session
quotes handed over whole. r1: 3 FAILs — wrong line refs
(needs_driven 406–410 were comment lines; the decision reads live
at 398–400/423–430), empty-bowl misclassed as a teacher change
(BACKLOG bills a spec-006 amendment affecting every cat), and her
item-2 words stretched across riders and contrasts from different
turns; 9 labeling NOTEs, all taken. r2: 1 new FAIL — a rule-12
misquote the FIX introduced ("others hidden" for "others' states
hidden"); plus the verifier exposed a wrong fact the COORDINATOR
had supplied (claimed the latency bridge was in the banking prompt;
it was not — re-derived from the session and corrected to
instrument-detail-no-owner-word). r3: PASS, full set.

Two lessons. (1) Conversation facts the coordinator hands a
verifier are themselves a failure surface the verifier cannot
check — re-derive each one from the transcript before supplying
it, and correct on record when wrong. (2) The basis taxonomy that
survived review: direct word > acceptance of a presented package >
acknowledgement after a banks-on-your-word prompt > acquiescence
to an announced banking > instrument detail claiming no word —
rulings records should name which one each item rests on.
