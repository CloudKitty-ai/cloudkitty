# Act-head parameter ladder — results (read 2026-11-05 UTC, the evening of 2026-11-04 local; zero collection)

Declared 2026-11-04 at 1ae72312 on her word "Do it"; guards l1–l5 red
on record at 2c26664d; the six heads trained and all four reads ran on
that commit (no tracked file changed between the reds commit and this
write-up; `seconds` in the reads' JSON: accuracy 378, fit 334,
reliability 282; the curve read takes seconds). The new heads are
B5-s1..3 and B15-s1..3 in the act arc's heads store
(`minifriend-act-2026-11-03/results-raw/heads/`, sha256 of each
`head-best.pt` in its `done.json`), beside the act arc's B10 / B20 /
B30. Every arm figure is the seed mean ± SD over three heads. 0 covered
cat-ticks.

## Headline

The curve is concave and bends gradually; there is no knee. On the needy
tuning half's covered friends at y0, log-loss falls 1.149 → 1.090 →
1.066 → 1.055 → 1.042 across B5 / B10 / B15 / B20 / B30 (3,942 → 8,182
→ 12,438 → 16,792 → 24,822 trained parameters), so each step buys less
per parameter than the one before: 0.0140, 0.0055, 0.0025 and 0.0017 of
log-loss per 1,000 added parameters (P33 MET; the ratios of successive
gains are 2.6, 2.2 and 1.5). Of the total log-loss gain from B5 to B30
(0.107), B10 holds 0.55, B15 0.77 and B20 0.87. Top-1 runs 0.615 /
0.634 / 0.640 / 0.644 / 0.647 with the same shape (per 1,000 added
parameters: 0.0045, 0.0016, 0.0007, 0.0004). Every arm is honest at
T = 1 (the largest registered-cell ECE is B10 heard, 0.0149; no
registered cell is over her 0.05 trigger, so no temperature is fitted
for adoption or applied) and every arm's in-sight entropy ranks right
over wrong ticks with AUROC 0.856–0.860. B5 is the weak end on every
accuracy axis (heard top-1 0.496 against B10's 0.522; y10 0.395 against
0.410), with the widest top-1 seed spread on the ladder at y0 all (SD
0.005). The Phase 2 act
head is her pick after this curve (DECLARATION §6); nothing here
selects.

## What ran

| head | GRU width | trained params | best epoch (of run) | best validation loss | wall time |
|---|---|---|---|---|---|
| B5-s1 | 14 | 3,942 | 155 (165) | 2.8474 | 2,701 s |
| B5-s2 | 14 | 3,942 | 60 (70) | 2.8911 | 1,166 s |
| B5-s3 | 14 | 3,942 | 110 (120) | 2.8737 | 1,984 s |
| B15-s1 | 32 | 12,438 | 90 (100) | 2.7176 | 2,230 s |
| B15-s2 | 32 | 12,438 | 119 (129) | 2.7358 | 2,748 s |
| B15-s3 | 32 | 12,438 | 112 (122) | 2.7393 | 2,481 s |

Each head stopped on the plateau rule (no validation gain over 10
epochs; cap 200 not reached). The act arc's heads, for the same column:
B10 2.7623 / 2.7788 / 2.7631, B20 2.7302 / 2.6806 / 2.7010, B30 2.6871 /
2.6804 / 2.6545 (validation loss is CE(y0) + CE(y10 masked) on Phase
1e's validation split; the seed means fall with size at this layer too,
with two of the four neighbour pairs overlapping by seed: B15-s1 2.7176
is under B20-s1 2.7302 and B20-s2 2.6806 under B30-s1 2.6871).

| read | worlds | samples per head (y0) | seconds |
|---|---|---|---|
| accuracy (the act arc's `read_accuracy`, five B arms), needy tuning half + the lived LWG and P worlds, covered friends | 180 tuning + lived | 9,864,000 tuning (seen 5,153,794, heard 4,677,151, silent 33,055); lived LWG 2,800,000, P 4,000,000 | 378 |
| fit (the calibration arc's `read_fit`), Phase 1e validation split, every 10th tick — reported only, T = 1 ruled | 52 | 372,000 | 334 |
| reliability (`read_reliability`), needy tuning half, covered friends; the 0.05 trigger at T = 1 | 180 | 9,864,000 | 282 |
| curve (`read_curve`), from `reads/accuracy.json` | — | — | seconds |

## R-1 — the curve (`reads/curve.md`; tuning half, covered friends, y0, seed means)

| arm | width | params | share of trunk | top-1 | log-loss | macro recall | seen top-1 | heard top-1 | y10 top-1 |
|---|---|---|---|---|---|---|---|---|---|
| B5 | 14 | 3,942 | 0.0467 | 0.615 | 1.149 | 0.472 | 0.721 | 0.496 | 0.395 |
| B10 | 24 | 8,182 | 0.0969 | 0.634 | 1.090 | 0.494 | 0.734 | 0.522 | 0.410 |
| B15 | 32 | 12,438 | 0.1473 | 0.640 | 1.066 | 0.507 | 0.740 | 0.529 | 0.414 |
| B20 | 39 | 16,792 | 0.1988 | 0.644 | 1.055 | 0.510 | 0.742 | 0.534 | 0.418 |
| B30 | 50 | 24,822 | 0.2939 | 0.647 | 1.042 | 0.513 | 0.745 | 0.537 | 0.424 |

Marginal change per 1,000 added parameters at each step (the "bang for
the buck" axis, DECLARATION §5):

| step | Δ params | Δ log-loss | log-loss per 1,000 | Δ top-1 | top-1 per 1,000 |
|---|---|---|---|---|---|
| B5 → B10 | 4,240 | −0.0593 | −0.01399 | +0.0192 | +0.00453 |
| B10 → B15 | 4,256 | −0.0233 | −0.00547 | +0.0066 | +0.00155 |
| B15 → B20 | 4,354 | −0.0110 | −0.00253 | +0.0031 | +0.00071 |
| B20 → B30 | 8,030 | −0.0134 | −0.00167 | +0.0030 | +0.00037 |

Per seed (tuning, y0, all, top-1 / log-loss): B5 0.6202 / 1.1352,
0.6106 / 1.1599, 0.6132 / 1.1515; B10 0.6336 / 1.0905, 0.6336 / 1.0909,
0.6344 / 1.0873; B15 0.6410 / 1.0626, 0.6413 / 1.0655, 0.6393 / 1.0708;
B20 0.6395 / 1.0703, 0.6479 / 1.0408, 0.6434 / 1.0550; B30 0.6453 /
1.0460, 0.6448 / 1.0485, 0.6497 / 1.0312. The seed ranges of B15 (1.0626–1.0708) and B20
(1.0408–1.0703) overlap; B30's (1.0312–1.0485) does not overlap B15's; the B15 → B20 step (0.011) is inside B20's seed SD
(0.015). B5's top-1 seed SD (0.005) is the widest on the ladder and its
log-loss SD (0.013) second to B20's (0.015); B10's (0.0005, 0.002) are
the narrowest.

The same shape holds off the tuning half (unregistered, reported): on
the lived P worlds log-loss runs 1.142 / 1.077 / 1.056 / 1.044 / 1.031
(per 1,000: 0.0153, 0.0048, 0.0027, 0.0016) and on the lived LWG worlds
1.148 / 1.081 / 1.060 / 1.048 / 1.035 (0.0157, 0.0049, 0.0028, 0.0016);
within the tuning half, in sight 0.0115 / 0.0050 / 0.0021 / 0.0013 and
heard 0.0167 / 0.0061 / 0.0030 / 0.0021 — every step shrinks in every
cut, and the heard regime gains more per parameter than sight at every
step.

## R-2 — five-arm accuracy by regime (`reads/accuracy.md`; tuning half, covered friends)

| arm | y0 all top-1 | y0 all log-loss | seen top-1 | seen log-loss | heard top-1 | heard log-loss | silent top-1 | y10 all top-1 | y10 all log-loss |
|---|---|---|---|---|---|---|---|---|---|
| B5 | 0.615 ± 0.005 | 1.149 ± 0.013 | 0.721 ± 0.004 | 0.821 ± 0.012 | 0.496 ± 0.005 | 1.513 ± 0.012 | 0.832 ± 0.001 | 0.395 ± 0.002 | 1.760 ± 0.007 |
| B10 | 0.634 ± 0.001 | 1.090 ± 0.002 | 0.734 ± 0.001 | 0.772 ± 0.001 | 0.522 ± 0.001 | 1.443 ± 0.003 | 0.834 ± 0.002 | 0.410 ± 0.002 | 1.724 ± 0.005 |
| B15 | 0.640 ± 0.001 | 1.066 ± 0.004 | 0.740 ± 0.002 | 0.751 ± 0.005 | 0.529 ± 0.001 | 1.417 ± 0.004 | 0.835 ± 0.004 | 0.414 ± 0.002 | 1.707 ± 0.008 |
| B20 | 0.644 ± 0.004 | 1.055 ± 0.015 | 0.742 ± 0.005 | 0.742 ± 0.016 | 0.534 ± 0.004 | 1.404 ± 0.013 | 0.834 ± 0.001 | 0.418 ± 0.003 | 1.696 ± 0.008 |
| B30 | 0.647 ± 0.003 | 1.042 ± 0.009 | 0.745 ± 0.004 | 0.732 ± 0.010 | 0.537 ± 0.002 | 1.387 ± 0.009 | 0.837 ± 0.002 | 0.424 ± 0.003 | 1.678 ± 0.007 |
| F | 0.315 | 1.915 | 0.299 | 1.965 | 0.329 | 1.864 | 0.812 | 0.314 | 1.916 |
| V | 0.457 | — | 0.572 | — | 0.329 | — | 0.812 | 0.282 | — |
| R | 0.724 | — | 0.717 | — | 0.731 | — | 0.896 | 0.232 | — |

Counts: all 9,864,000, seen 5,153,794, heard 4,677,151, silent 33,055
(y10 all 9,842,400). The B10 / B20 / B30 rows equal F-074's (0.634 /
0.644 / 0.647; 1.090 / 1.055 / 1.042); the baselines F / V / R are
F-074's. Every arm keeps F-074's regime ordering: seen above heard
above y10, and every arm is above V in sight (B5 0.721 against 0.572)
and above F in every tuning cell; in the silent cell by only
0.020–0.024 from the unrounded means (F 0.812) and under R's 0.896 (the frequency prior feeds the policy
when silent, P25 as amended, so this cell is not consulted). The ladder's reach: B5 → B30 adds 0.024 of in-sight top-1
and 0.041 heard; the heard regime is where size pays most and where
every arm knows least.

## R-3 — reliability at T = 1 and the 0.05 trigger (`reads/reliability.md`; tuning half, y0)

| arm | regime | top-1 | mean top-prob | mean entropy | ECE T = 1 | AUROC 1 − entropy | AUROC top-prob |
|---|---|---|---|---|---|---|---|
| B5 | seen | 0.721 ± 0.004 | 0.720 ± 0.002 | 0.342 ± 0.003 | 0.0065 ± 0.0024 | 0.856 ± 0.001 | 0.861 ± 0.001 |
| B5 | heard | 0.496 ± 0.005 | 0.493 ± 0.009 | 0.631 ± 0.009 | 0.0096 ± 0.0020 | 0.642 ± 0.006 | 0.652 ± 0.005 |
| B10 | seen | 0.734 ± 0.001 | 0.737 ± 0.003 | 0.316 ± 0.004 | 0.0057 ± 0.0033 | 0.860 ± 0.001 | 0.864 ± 0.001 |
| B10 | heard | 0.522 ± 0.001 | 0.537 ± 0.009 | 0.584 ± 0.011 | 0.0149 ± 0.0079 | 0.657 ± 0.002 | 0.665 ± 0.002 |
| B15 | seen | 0.740 ± 0.002 | 0.741 ± 0.004 | 0.311 ± 0.004 | 0.0030 ± 0.0007 | 0.859 ± 0.001 | 0.863 ± 0.002 |
| B15 | heard | 0.529 ± 0.001 | 0.532 ± 0.012 | 0.588 ± 0.009 | 0.0100 ± 0.0070 | 0.658 ± 0.002 | 0.668 ± 0.002 |
| B20 | seen | 0.742 ± 0.005 | 0.746 ± 0.006 | 0.303 ± 0.008 | 0.0047 ± 0.0009 | 0.859 ± 0.002 | 0.863 ± 0.001 |
| B20 | heard | 0.534 ± 0.004 | 0.541 ± 0.010 | 0.574 ± 0.011 | 0.0091 ± 0.0043 | 0.662 ± 0.001 | 0.672 ± 0.002 |
| B30 | seen | 0.745 ± 0.004 | 0.747 ± 0.009 | 0.303 ± 0.009 | 0.0054 ± 0.0013 | 0.860 ± 0.001 | 0.864 ± 0.001 |
| B30 | heard | 0.537 ± 0.002 | 0.545 ± 0.003 | 0.569 ± 0.006 | 0.0082 ± 0.0021 | 0.665 ± 0.003 | 0.675 ± 0.002 |

The 0.05 trigger (her ruling, calib DECLARATION §9) at T = 1, seed
means: B5 0.0065 / 0.0096, B10 0.0057 / 0.0149, B15 0.0030 / 0.0100,
B20 0.0047 / 0.0091, B30 0.0054 / 0.0082 (seen / heard); none over, so
no temperature is fitted for adoption and every head stays at T = 1.
Mean top-prob sits within 0.015 of top-1 in every registered cell; the
heard gap (mean top-prob − top-1, from the unrounded values) runs
−0.003 (B5, slightly under-confident), +0.014 (B10), +0.003 (B15),
+0.008 (B20), +0.008 (B30), so B10's heard cell is the most
over-confident of the ten registered cells and B5 the only arm under in
either regime (seen −0.001, heard −0.003). In sight,
size barely moves the certainty ranking (AUROC of 1 − entropy 0.856 →
0.860 across the ladder, against +0.024 of top-1), which is F-075's
reading of B10 against B30 extended down to B5. Heard, size moves the
ranking more than F-075 saw between B10 and B30: 0.642 → 0.665 from B5
to B30 (+0.022 from the unrounded means, past the 0.02 bar F-075's P31
declared for B30 − B10 and applied here to the wider B5 → B30 span; the
excess 0.002 is inside B5's heard seed SD of 0.006), of which +0.014 is
the B5 → B10 step; the smallest head ranks its heard ticks worse than
the other four, which sit within 0.008 of each other (0.657–0.665). Unregistered: the silent
cell's ECE is 0.0617 ± 0.0618 for B5 (per seed 0.0115 / 0.1307 /
0.0429 — the small head's silent confidence varies by seed), 0.0240
for B10, 0.0378 for B15, 0.0207 for B20 and 0.0179 for B30, on 33,055
samples and not consulted by the policy; the y10 seen and heard cells sit
under 0.017 for every arm (B20 seen y10 0.0168 the largest). Fitted temperatures, reported only (`reads/temperature.md`,
validation split): every non-silent y0 fit across the fifteen heads
lies in 0.96–1.03 (B5 0.96–1.00, B15 0.97–1.00; B5's heard fits 0.96 /
0.97 / 0.99 all under 1, the under-confidence above seen on the
validation split too), y10 0.96–1.04.

## Predictions scored (DECLARATION §6)

- **P33 MET.** Log-loss gain per 1,000 added parameters, tuning half,
  covered friends, y0: |B5 → B10| 0.01399 > |B10 → B15| 0.00547 >
  |B15 → B20| 0.00253 > |B20 → B30| 0.00167. Top-1's gains shrink at
  every step too (0.00453 > 0.00155 > 0.00071 > 0.00037; reported, not
  registered).
- No registered cell is UNDECIDABLE (the smallest holds 4,677,151
  samples against the 10,000 floor of DECLARATION §4).

Unscored expectations, reported: B5's top-1 under 0.62 and log-loss
over 1.13 — as expected (0.615, 1.149); B15 within 0.004 top-1 and 0.015
log-loss of B20 — as expected (0.0031, 0.0110); every arm's ECE at T = 1
under 0.05 in both registered cells — as expected (largest 0.0149);
every arm ≥ V in sight — as expected (B5 0.721 against 0.572); seen /
heard / y10 ordering as in F-074 for every arm — as expected.

## Decision rules applied (DECLARATION §6)

- **The Phase 2 act head.** No selector; the curve is reported in full
  and the head is her pick, to be recorded verbatim in DECLARATION §8.
  Where the curve puts the sizes: B10 holds 0.55 of the B5 → B30
  log-loss gain at 0.097 of the trunk's parameters; B15 0.77 at 0.147;
  B20 0.87 at 0.199; B30 all of it at 0.294. Every arm is honest at
  T = 1 in its registered cells (largest ECE 0.0149) and none is over
  the trigger, so no arm needs a temperature before it can be picked.
- **Her conditional.** "We can extend to 20,30 if we see real welfare
  benefit" travels into the Phase 2 declaration as written: a larger
  head runs only if the chosen head's arm beats the trunk on welfare.
- **FINDINGS.** The declared test for an entry is a knee the record did
  not have. The curve has no knee — the gain per parameter shrinks by a
  factor of 1.5–2.6 at each step, and the record already placed the bend
  between 10 and 20 (DECLARATION §1 printed the two existing steps as
  0.0041 → 0.0016 per 1,000; at this read's precision 0.0040 → 0.0017)
  — so the ladder is a Phase 2
  input cited from this arc, no F-entry; F-074's line "By the declared
  rule the act predictor is B10" is annotated as the thread's rule
  superseded by her pick once she has
  made it (its own commit, with the confirming-half read of the chosen
  head).

## What stands alone

Nothing is minted. What the record gains: the act head's log-loss
against parameter count has a steep end below B10 (0.014 per 1,000
parameters from 3,942 to 8,182) and bends through B15 and B20 to 0.0017
per 1,000 at B30, concave at every step, with the same shape in sight,
heard and on the lived worlds; the five arms are all calibrated at T = 1
(registered-cell ECE ≤ 0.0149) and size barely moves the in-sight
certainty ranking (AUROC 0.856–0.860). Domain: Gen 2 rot2 behaviour on
the needy set's tuning half, read by the committed heads.

## Guards and reds

l1–l5 (DECLARATION §7) green at 1ae72312 and RED CONFIRMED at 2c26664d,
each at the predicted first assertion (reds log in the session
scratchpad, `ladder-reds.log`; the commit subject and DECLARATION §7
carry the record); l1–l4 re-run green by the session on this write-up's
tree (`4 passed`; l5 trains smoke heads and was not re-run; the smoke
dirs `B5-s1-smoke`, `B15-s1-smoke` are never read). No reader changed
after the reds commit.

## Limitations

1. The curve is five points with three seeds each. The B15 → B20 step
   (0.011 of log-loss) is inside B20's seed SD (0.015), and B15's and
   B20's seed ranges overlap; the ordering of the seed means is as
   printed, the concavity verdict rests on the means, and the shrinking
   is monotone in every cut reported (tuning all / seen / heard, lived P,
   lived LWG).
2. Widths are the largest under each nominal cap; the parameter counts
   are therefore not equally spaced (steps of 4,240 / 4,256 / 4,354 /
   8,030), which the per-1,000 column normalises.
3. Only the GRU width moves; the input (167 cells) and the two 11-way
   outputs are fixed, so the smallest arm still spends 168 × 14 = 2,352
   of its 3,942 parameters on the input layer (weights and bias). A different architecture at the
   same count is not on this ladder.
4. The tuning half is the only registered surface; the lived worlds and
   the regimes are reported for shape. The confirming half is untouched
   (one read of the chosen head after her pick).
5. These are read on rot2 behaviour; a policy that reacts to the head
   changes the acts it predicts (F-074's re-verify clause) and the F-074
   / F-075 drift monitors carry into Phase 2 for whichever head she
   picks.
6. The validation-loss column in "What ran" is the trainer's early-stop
   quantity (CE y0 + CE y10 masked, Phase 1e split); it is not the
   tuning-half log-loss and the two are not compared across layers.

## Regeneration (reads)

```
### Read (the gate runs these; fresh outputs to its scratchpad, never over reads/)
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $C/ladder_act.py accuracy    --out <scratch>/accuracy.json    --md --quiet   # about 6 min
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $C/ladder_act.py fit         --out <scratch>/temperature.json --md --quiet   # about 6 min; Phase 1e validation worlds
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $C/ladder_act.py reliability --out <scratch>/reliability.json --md --quiet   # about 5 min; reads $C/reads/temperature.json
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $C/ladder_act.py curve       --out <scratch>/curve.json       --md           # seconds; reads $C/reads/accuracy.json
```

(`A` = `experiments/needy-set-2026-10-28`, `C` =
`experiments/minifriend-act-ladder-2026-11-04`, absolute paths in use.
`reliability` reads the committed `reads/temperature.json` and `curve`
the committed `reads/accuracy.json` as inputs; fresh `fit` and
`accuracy` leaf-equal to those files verify the inputs. Heads: the
fifteen `<arm>-s<k>/head-best.pt` in the act arc's store, sha256 in each
`done.json`.)

**Accuracy gate: PASS 2026-11-05, round 5** (rounds 1–4 FAIL on wording
and companion copy only; every regenerated number equal in all five
rounds: the four reads' JSON leaf-equal to `reads/` but for `seconds`,
the md files byte-identical, every arm / seed / cell count equal, the
fifteen heads' sha256 equal to their done.json, the B10 / B20 / B30 and
baseline cells leaf-equal to the act arc's read). Round 5: about 400
reader-backed numbers (3 ROUNDING, each the reader's own printed digits
one unit from the unrounded mean: B15 top-1 0.640, B30 silent top-1
0.837, B30 seen top-prob AUROC 0.864), about 75 derived figures all
SUPPORTED, 5 thresholds all sourced, about 25 characterisations all
SUPPORTED (2 notes outside the fail zones, both reworded after the
pass: "two of the four neighbour pairs"; the UTC date in the title), 0
UNDECIDABLE, about 22 provenance checks all passed, companions PASS.
What rounds 1–4 caught, in order: "the weak end on every axis" when B5
has the lowest ECE (accuracy axis only); "widest seed SD" when B20's
log-loss SD is wider; "no cell over the trigger" unscoped over the
unregistered silent cells; F-075's size-versus-ranking reading extended
to five arms when the heard span crosses its 0.02 bar; a companion
dropping "registered-cell"; "no temperature is fitted" when fifteen
were fitted and reported ("for adoption"); "every arm is honest"
unscoped inside Decision rules; a companion dropping the metric name
from a gain series; both companions dropping "tuning half, covered
friends, y0". Raw-dir hash of the heads store after the six new heads
and the two smoke dirs landed: `v1:4135e34f68487201`
(`scripts/rawdir-hash.sh`; F-074 / F-075 stamped the store before them
as `v1:5b29e9a2736a84f7`).

## Addendum after the stamp — R-C, the confirming half, B15 once (2026-11-05; `reads/confirming.md`, covered friends)

Written after her pick (DECLARATION §8, RULED 2026-11-05: "Let's try
B15, and we can compare to B10 to see if the accuracy gain translates to
welfare"; "1) yes"). One read of B15's three heads on the needy
CONFIRMING half, the act arc's `read_confirming` with the arm passed in
(`ladder_act.py confirming`, guard l6 red on record before the read,
commit a6a8b859); that half's fifth touch, one arm, nothing selected on
it. Seed mean ± SD over the three heads; F / V / R the act arc's
baselines on the same samples.

| state | n (y0) | B15 y0 top-1 | B15 y0 log-loss | F | V | R | B15 y10 top-1 | F y10 |
|---|---|---|---|---|---|---|---|---|
| all | 9,864,000 | 0.640 ± 0.001 | 1.069 ± 0.004 | 0.316 | 0.458 | 0.725 | 0.415 ± 0.002 | 0.315 |
| seen | 5,125,876 | 0.742 ± 0.001 | 0.750 ± 0.005 | 0.300 | 0.572 | 0.717 | 0.415 ± 0.003 | 0.306 |
| heard | 4,705,307 | 0.528 ± 0.001 | 1.420 ± 0.004 | 0.330 | 0.330 | 0.732 | 0.412 ± 0.002 | 0.321 |
| silent | 32,817 | 0.824 ± 0.006 | 0.647 ± 0.005 | 0.793 | 0.793 | 0.901 | 0.795 ± 0.002 | 0.770 |

Macro recall, all states, y0: 0.506 ± 0.002. Per head (y0 all, top-1 /
log-loss): 0.6403 / 1.0649, 0.6406 / 1.0687, 0.6386 / 1.0736.

**Against the tuning half** (R-2, same arm; differences from the
unrounded means): in every cell but the silent ones, top-1 and macro
recall move by at most 0.0014 and log-loss by at most 0.0033 (y0 all:
top-1 0.6405 → 0.6399, log-loss 1.0663 → 1.0691); the silent cells move
more (y0 top-1 0.835 → 0.824, log-loss 0.618 → 0.647; y10 top-1 0.807 →
0.795), on 32,817 samples. The arm-N group moves against its own
tuning-half cells the same way: at most 0.0013 of top-1 in the non-silent
cells, the silent cells more (y0 all 0.639, log-loss 1.070). **Beside
B10's confirming read**
(act arc RESULTS R-C: 0.633 ± 0.000, log-loss 1.092 ± 0.002; seen 0.735,
heard 0.521, y10 0.410): B15 is +0.007 top-1 and −0.023 log-loss on the
confirming half, the same gap as on the tuning half (R-1: +0.0066,
−0.0233). The clean number the Phase 2 declaration cites for B15 is this
table; it changes nothing about the pick, which was hers before the read.

Provenance. Heads `B15-s1..3/head-best.pt` in the act arc's store,
sha256 in each `done.json`, unchanged since the stamp above. The store's
raw-dir hash is now `v1:4171820c2260bed7`: the act arc's own guard suite
(`test_act.py`, run green 2026-11-05 before the reader edit was
committed, 7 passed) retrains the smoke heads `A-s1-smoke` and
`B10-s1-smoke` each run, and those two directories' bytes moved; no read
touches a smoke head. Read wall 63 s.

### Read (the gate runs this; fresh output to its scratchpad, never over reads/)

```
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $C/ladder_act.py confirming --out <scratch>/confirming.json --md --quiet   # about 1 min; B15's three heads on the needy confirming half
```

(`A`, `C` as above. The tuning-half comparison cells come from the
committed `reads/accuracy.json`; B10's confirming cells from the act
arc's committed `reads/confirming.json`.)

**Accuracy gate (addendum): PASS 2026-11-05, round 1** (fresh read 63.6 s,
leaf-equal to `reads/confirming.json` but for `seconds`, md
byte-identical, all 192 n cells equal, heads exactly B15-s1..3 with
sha256 equal to their done.json; 52 reader-backed cells all match (0
ROUNDING), 21 derived figures SUPPORTED, 1 self-set descriptive bound
reported, 9 characterisations 8 SUPPORTED and 1 WEAK outside the fail
zones — the arm-N sentence named no comparator and no silent-cell scope;
reworded after the pass to the tuning-half comparison with the silent
cells excluded — 1 UNDECIDABLE (test_act "7 passed", not re-run because
it rewrites the smoke heads), 17 provenance checks passed, companions
PASS). Heads-store hash `v1:4171820c2260bed7`.
