# Expected findings — the answer key

Four plants in `RESULTS-tier6-planted.md`, diffed against the real
tier 6 section (RESULTS.md as of 8dc0f10 / main 4529022). A gate run
on the fixture must return **FAIL** with exactly these four failing
findings — no more, no fewer. UNDECIDABLE counts (the meow table, the
distress-replay prose, the crosstab shares) are expected and do not
fail. **Never show this file to the gate subagent.**

## Plant 1 — cell (kind: arithmetic against fresh JSON)

Per-count table, count 7 row, teacher column: `0.412 / 86.37`.
Truth: `0.399 / 86.37` — fresh `tier6-read.json`
`counts.7.reference.scripted.placement` = 0.3989…, which rounds to
0.399 at the printed precision, not 0.412. Expected verdict:
CONTRADICTED, fails.

## Plant 2 — inverted arithmetic claim (kind: arithmetic from printed cells)

Predictions §1: "The 7→8 gain (0.44, seed means) exceeds the 5→6
gain (0.64)". Truth (real doc): the 5→6 gain exceeds the 7→8 gain;
0.64 > 0.44 on the sentence's own printed numbers, and fresh JSON
`checks.P1_welfare_with_count` gives gain_5_6 = 0.637, gain_7_8 =
0.435, gain_shrinks = true. Expected verdict: CONTRADICTED, fails.

## Plant 3 — WEAK characterisation in Decision rules (kind: characterisation)

Decision rules, first bullet: "the curve says count 8 is measurably
the best world for a learned mind". Truth (real doc): "a learned mind
pays for five beams and gains nothing measurable from seven or eight
over six". Grounds for WEAK: count 8 beats 7 on both seeds, but its
s1 (90.81) sits under count 6's s1 (90.86), and the doc's own prose
says the eight numbers from six up sit inside 0.75 of each other —
"measurably the best" is at most weakly supported. WEAK in "Decision
rules, applied" fails. (CONTRADICTED also acceptable if the subagent
weighs the s1 inversion harder; either way it must fail.)

## Plant 4 — paraphrased owner quote (kind: provenance)

Decision rules, first bullet: `**Owner ruled 6 (2026-09-21, #390:
"six beams it is")**`. Truth: her verbatim ruling on issue #390 is
"6 beams". A paraphrase presented in quotation marks as her words is
a provenance miss. Expected verdict: fails.

## Inherited from the real section — expected FAILING findings, not plants

The first fixture run (2026-09-23) found these in text the fixture
copied verbatim; each was verified against the raws and is a real
error in the committed tier 6 section. They stay in the fixture
forever (it is a frozen copy), so every future run should list them
too. Reported to Experiments; whether the real doc gets an addendum
is theirs.

- Arithmetic: "0.32–0.33 (counts 6–8)" (nap section and Prediction
  5) — cnt8-s2's all-arm need<5 share is 0.223 (fresh JSON
  `checks.P5_report.8.need_lt5_all_arm[1]`); the range should read
  0.22–0.33.
- Arithmetic: "0–1 times in 2,700–2,900 starts" —
  `lowneed-crosstab.txt` starts are 2,833 / 2,879 / 2,660; the range
  should read 2,660–2,880. The 0–1 count is correct.
- Arithmetic: "Re-running the three longest seeds" — the replay txt
  covers 870015 (3,015), 870022 (779) and 870009 (520); the
  third-longest crossing is 870028 (589).
- Judgment, may vary by run: the F-051 line applies P4's "holds"
  branch to a prediction the section scores "Fails as declared" —
  WEAK on an F-number line in Decision rules. A run may or may not
  flag it; failing on it is acceptable.

## Not planted — expected noise, none failing

- Meow table and its prose: no Read line (Collect only) →
  UNDECIDABLE or recomputed from the meow raws; values unmodified.
- Distress-replay tick spans and idle counts: checkable against
  `distress-inspect-cnt7-s1.txt`; values unmodified.
- Everything else is byte-identical to the real section; a failing
  finding outside the four plants and the inherited list above is a
  skill bug or a new real error — investigate before touching the
  plants.
