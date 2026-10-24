# Mini-friend Phase 1c — the structured discrete belief head (declaration 2026-10-23; owner-requested)

Owner's words, 2026-10-23, after the F-065 report and a design
exchange (a structured-dynamics belief with a discrete likelihood as
the remedy for the ostrich read): "Let's try it. Currently our accuracy
is low enough that we can reevaluate model size limit if needed. Let's
test this approach first though". This arc tests the approach UNDER
the §8 item 4 cap; the cap is not moved here (a wider head stays a
further deviations entry on her word, per entry 11).

Prereg: Gen 2 FROZEN at 18f06f84, §8 item 3 (Phase 1: one 2 × 2 of
loss weighting × stratum, offline heads on frozen trunk rollouts) and
item 4 (Phase 2 takes the winner; amendment A4's working direction: a
recurrent per-friend belief state, updated from the friend's visible
row, held under fog on learned drift rates, read by the estimate head
and the act predictor). This arc adds a THIRD offline candidate beside
NF and DR on the same rollouts, before the winner is named — recorded
as deviations entry 12 (an addition; no prereg text moves). Phase 1's
and 1b's verdicts, floors, F-064 and F-065 stand.

Welfare-cost line: 0 new covered cat-ticks. Nothing rolls out; every
sample is a Phase 1 or 1b raw already on disk.

## Question

F-065 left the Phase 2 head choice between a natural-frequency head
that under-reads a grave friend in sight by about ten need points and a
distress-reweighted head that halves neither the bias nor the loss gap.
Both are one regression on squared error: under ambiguity about a
hidden need their estimate is the conditional mean, which sits where
the prior sits. Does a head that (a) carries the engine's need law as
structure — monotone rise at a learned per-friend rate, fall on
relief — and (b) reports a histogram instead of a point, trained by
cross-entropy, read grave states better than NF and DR at the same
capacity, and does it remove the ostrich signature? Secondary: is its
grave probability calibrated, does its structure carry the fit, and
does it recover the friends' rise rates from observation alone?

## Head

`sd_head.py` — the SD head, 6,679 parameters (cap 8,445; `check_cap`
enforced, no probe flag). Inputs, samples, split, chunking (500 ticks,
state carried and detached), optimiser (Adam 1e-3), batch (128
sequences), early stopping (validation loss, patience 10, margin 1e-4,
cap 200 epochs) and seeds (1, 2, 3) are Phase 1's, imported from
`train_heads.py`; the per-sample weight is 1 (natural frequency).

- **Belief**: per hidden need, a histogram over K = 20 bins of 5 need
  points. Grave mass = bins 18–19 (≥ 90, `strata.NEED_DISTRESS`).
- **Drift**: each tick the histogram shifts UP by a learned rate per
  (friend, need), in bins per tick (fractional two-tap shift; the top
  bin accumulates, as the engine clamps at 100). Initialised at 0.4
  points per tick for every cell; never read from the served config.
- **Relief**: with probability p_rel (per need, per tick) the histogram
  shifts DOWN by a learned relief size per need (bins per relieving
  tick; the floor accumulates). p_rel = sigmoid of a linear read of a
  width-16 GRU over the observer's 167 input cells — the act predictor
  in embryo: in sight the friend's activity is in the row, under fog it
  is inferred.
- **Residual**: the GRU state adds a logit correction to the histogram,
  renormalised by softmax. At prediction time the residual can be
  zeroed (`nores/`), which is the R6c read.
- **Prior**: a learned histogram per (friend, need) at t = 0.
- **Aux outputs**: happiness and bath by a linear read of the GRU state
  and the five belief means (Phase 1's loss terms, kept so the reader's
  columns exist; reference only).
- **Loss** per sample: CE of the five histograms against two-hot targets
  (the true value's mass split between its two nearest bin centres, so
  the target's mean is the true value), mean over needs; plus 0.5 × BCE
  of p_rel against the true relief indicator (the need fell since the
  previous tick — a transform of the same ground-truth target stream,
  §6 pre-commitment (1); 0 at t = 0); plus mse_hap + 0.1 × mse_bath.
- **Point estimate** for every Phase 1 read: the histogram mean. The
  prediction file is Phase 1's (`pred-<set>-<seed>.npz`), so Phase 1's
  reader reads SD unchanged; `belief-<set>-<seed>.npz` carries the
  grave mass and p_rel.

Two comparability caveats, declared: SD sees an auxiliary target (the
relief indicator) NF and DR did not, and emits a distribution they did
not. Both are the approach; the comparison is approach against
approach at equal capacity, not likelihood against likelihood.

## Data

`split.json` is Phase 1b's byte for byte (seed 20261023; L / W / G from
Phase 1's split, P1..P5 10 / 10). Raws are symlinks: L, W, G to Phase
1's, P1..P5 to Phase 1b's. Roles under the Phase 1 carve: 74 training
worlds, 17 validation, 69 evaluation (L 3, W 8, G 8, P 50). Comparators
are Phase 1b's six width-24 runs (NF-h24-s1..3, DR-h24-s1..3),
symlinked under this arc's `results-raw/heads/` and RE-READ through
this arc's reader; the re-read must equal the gated 1b cells (guard
t6). Evaluation groups as 1b: **P** = the P1..P5 eval worlds, **G** =
Phase 1's G eval worlds.

## Reads, declared now (all descriptive; rule 10)

`read_phase1c.py`, on group P unless stated; pooled = sample-weighted
over covered friends, mean of three seeds, SD between seeds; ratios
with the first-order SD and 1b's READ rule (|r − 1| > SD).

- **R1c. Accuracy.** SD's Phase 1 cells (mse5, bias per stratum class ×
  version, per friend then pooled) beside NF-h24 and DR-h24 on P and G;
  the marginal and persistence baselines beside.
- **R2c. Contrast.** r = SD loss over NF-h24 loss, and over DR-h24 loss,
  per class × version, with the READ rule. The headline is the
  mind-visible GRAVE cell on P.
- **R3c. Ostrich.** Phase 1's R4 (grave bias, common bias, gap, the
  1.5× signature) for SD, per friend and pooled, both versions.
- **R4c. Calibration of the grave probability.** Per sample, P(grave by
  need) = 1 − ∏(1 − grave mass_i) over the five needs (independence
  across needs assumed; declared). Against the true stratum (GRAVE
  includes the happiness-only edge, which the need histograms cannot
  carry — the count of happiness-only grave samples is reported and
  those samples count against the head): reliability in ten
  probability bins, Brier score, mean predicted probability on GRAVE
  against COMMON samples; per version. No bar.
- **R5c. Rate recovery.** The learned rise rates (points per tick, per
  friend × need) beside the empirical median positive one-tick change
  of the same need on the TRAINING worlds' truth streams (the
  descriptor; never the served config). No bar.
- **R6c. Residual share and the act embryo.** (a) SD's cells with the
  residual zeroed (`nores/`) over the full head's, per class × version:
  the structure carries the fit if the no-residual grave loss is within
  2× the full head's (a reading rule, not a bar). (b) p_rel's AUROC
  against the true relief indicator, in sight and under fog separately,
  pooled over friends.
- **R7c. Against the floors (informational).** Phase 1's dissolution
  procedure with SD as the candidate: SD against DR-h24's pooled
  mind-visible GRAVE floor and the per-friend clause (1.10, the
  between-seed SD), and the same against NF-h24. Scope as Phase 1: this
  licenses head choice only.
- **R8c. Runs.** Params against 8,445; epochs to the plateau; learned
  relief sizes per need.

**What would count as the approach helping** (rule 11; domain: group P
eval worlds, mind-visible, pooled over covered friends, mean of seeds
1–3, comparators 1b's width-24 runs re-read here):
(i) R2c GRAVE: SD over NF-h24 READ under 1; (ii) R3c pooled GRAVE bias
within ±5.0 need points (1b at width 24: NF −10.10, DR −7.57) with no
pooled signature. Both hold → the approach helps on both counts; one →
partial, reported as such; neither → the approach does not help at this
capacity, and the cap question is hers with that read in hand.
Nothing here is a welfare claim.

Not read: anything Phase 1 and 1b did not read; welfare; any
comparison pooling P with G; the Phase 2 consumer reads.

## Doctrine check (CLAUDE.md rule 8)

- Rule 8 (scarcity of information) moved the input: SD sees exactly the
  167 cells NF and DR saw, nothing of the friend's hidden state; the
  structure is a prior over how a hidden quantity moves, not a leak.
  The rise rates are learned from observation and only COMPARED to the
  truth streams afterwards (R5c), never initialised from the config.
- Rules 1 and 2 moved the likelihood choice: an asymmetric (pessimistic)
  loss was considered and NOT taken, because it prices under-reading
  into the estimator; cross-entropy against the true histogram prices
  nothing.
- Rule 10 moved the reads: descriptive, per friend before pooled, SDs
  over three seeds, min-n fail-closed (Phase 1's 200), ratios with a
  READ rule; the two "helping" criteria are stated with their domain
  (rule 11) and license head choice only.
- Rule 5 (a teacher acts on what the student sees): no teacher here;
  the relief indicator is a training target, consumed offline.
- Rule 12: no rollout, so nothing to stop; unchanged.
- Rules 3, 4, 6, 7, 9: checked, moved nothing.
- FINDINGS read (rule 7): F-065 (the comparators and the ostrich depth
  this answers), F-064 (Phase 1's floor and clause), F-060 (the roster),
  F-063 (Kittybear's seat supplies many lived grave ticks).

## Welfare (practice, owner 2026-09-26)

No new rollout: 0 covered cat-ticks; the heads train on raws already
collected under Phase 1's and 1b's declarations and stops. Engine and
venv: Phase 1's arc venv (`../minifriend-phase1-2026-10-22/.venv`,
engine a2e8d044), untouched. Compute: three seeds in parallel, three
torch threads each, about 90 s per epoch; expected one to three hours.

## Instrument and guards (each with a predicted red before trust)

`test_phase1c.py` (plain-assert runner; Phase 1 arc venv):

- t1 shift operators: an up-shift of half a bin moves a delta at bin 3
  to 0.5 / 0.5 over bins 3 / 4; a down-shift of 2.0 bins moves a delta
  at bin 1 wholly to bin 0; an up-shift of a delta at the top bin stays
  there; every result sums to 1. Red: drop the boundary clamp.
- t2 two-hot targets: sum to 1; mean equals the value inside the centre
  range; the top value puts every unit in bin 19. Red: drop the
  half-bin offset.
- t3 the residual switch: with `residual=False` the belief is a
  distribution at every tick and does not depend on the correction
  weights; with it on, it does. Red: ignore the flag.
- t4 prediction consistency: on a 600-tick slice of one world, the
  prediction file's five need columns equal the histogram means and
  the grave mass equals the belief's mass over bins 18–19. Red: write
  the histogram mode.
- t5 reader arithmetic: the grave-probability combination on a hand
  case (1 − ∏(1 − m)); reliability-bin counts sum to n; AUROC 1.0 /
  0.0 / 0.5 on hand rankings. Red: combine by max.
- t6 provenance: `split.json` equals Phase 1b's; the comparator cells
  re-read here (NF-h24, DR-h24, group P, pooled mind-visible GRAVE
  mse5 and bias) equal `../minifriend-phase1b-2026-10-23/
  phase1b-read.json` at width 24. Red: point the comparators at width
  12.

Each red by `scripts/mutate.sh --expect <test name>` on the committed
file; the result lines are recorded below before any head is read.

Reds on record 2026-10-23 (`scripts/mutate.sh --expect <test>` on
`sd_head.py` at 2f4fc242's successor commit; each predicted first,
each RED CONFIRMED, 4 passed after every restore): t1 — the boundary
clamp dropped from `shift_matrix` → `test_t1_shift_operators` red; t2 —
the half-bin offset dropped from `two_hot` → `test_t2_two_hot_targets`
red; t3 — the `residual` flag ignored (`if True:`) →
`test_t3_residual_switch` red; t4 — `predict_world` writing the
histogram mode (`CENTRES[argmax]`) instead of the mean →
`test_t4_prediction_consistency` red. Reader reds the same day on
`read_phase1c.py` (6 passed after every restore): t5 — the grave
probability combined by max instead of 1 − ∏(1 − m) →
`test_t5_reader_arithmetic` red; t6 — the provenance pin pointed at
1b's width-12 read instead of 24 → the re-read comparators no longer
match, `AssertionError: ('NF', 'mse5', …)` inside `test_t6_provenance`.
RESULTS.md gated by `/accuracy-gate` before commit; Collect (none —
no rollout) and Read fences separate, runtime declared.

## Run order (each step its own commit before its data)

1. This declaration, `split.json`, the raw and comparator symlinks
   (untracked), deviations entry 12, the timeline entry.
2. `sd_head.py` + `test_phase1c.py` t1–t4, reds on record. Smoke
   (2 epochs, 2 chunks, one world) to the scratchpad only.
3. Seeds 1, 2, 3 in parallel (`run_sd.sh`). No read until all three
   have `done.json`.
4. `read_phase1c.py` + t5–t6, reds on record; the read;
   `phase1c-read.json` + `.md` committed.
5. RESULTS.md gated; F-entry; deviations 12 closed; timeline updated;
   report to the owner. Phase 2 head choice stays hers.

## Addendum 2026-10-23: three widths (owner, the same day)

Her words, after the launch report: "Let's try 3 model sizes this time
as well so we can get an idea of what more/less parameters buy".

The width r of the recurrent part (the input projection, the GRU, the
p_rel read, the residual correction, the aux read) is the size knob;
the filter's own parameters (rates 25, relief sizes 5, priors 500) are
530 at every width:

| width r | params | vs cap 8,445 | vs trunk 84,450 | role |
|---|---|---|---|---|
| 8 | 3,279 | under | 3.9% | the small candidate |
| 16 | 6,679 | under | 7.9% | the declared head (§Head); its three runs were training when this addendum was written and keep their launch name `SD-s<seed>` |
| 32 | 15,783 | OVER (1.9×) | 18.7% | probe only: `--over-cap` must be passed; the manifest marks it; never a Phase 2 candidate |

Chosen before any width-8 or width-32 run as the halving and doubling
of the declared width (×2.0 and ×2.4 in params), one head on each side
of the cap, as 1b's 12 / 24 / 48 were. **The cap is not moved.** Run
names `SD-h<r>-s<seed>`; seeds 1, 2, 3; everything else §Head verbatim
(`sd_head.py --hidden <r> [--over-cap]`). The width-16 runs were
launched from `sd_head.py` at 5fed6daa; the flags added for this
addendum default to that behaviour (guard t7 below).

Read added — **R9c. Size effect.** 1b's R2b rule on SD: r(h) = SD
pooled loss at width h over the loss at width 16, per class × version,
groups P and G, first-order SD, READ when |r − 1| > SD. The cap-binds
question is r(32) on mind-visible GRAVE, group P: a READ ratio under 1
says capacity above the budget buys grave accuracy for this head too;
a tie says it does not. R1c–R8c run at every width (calibration, rate
recovery, residual share, p_rel AUROC and the floors per width). The
"approach helps" criteria stay as declared, at width 16 against the
width-24 comparators; nothing at width 8 or 32 enters them. The
width-32 read is an input to her cap question ("we can reevaluate
model size limit if needed"), never a Phase 2 candidate under the
standing cap.

Welfare: 0 new cat-ticks (the same raws). Compute: six more runs at
two torch threads each beside the three running; per-epoch time is
set by the per-tick filter loop and is near width-independent (165 s
at width 16 on three threads), so the six should finish within the
day.

Guard t7 (`test_phase1c.py`): `configure` at width 8 builds 3,279
params named `SD-h8-s1`; at 16, 6,679 named `SD-s1`; at 32 without
`--over-cap`, `check_cap` refuses (SystemExit); with it, 15,783 marked
over_cap. Red: `configure` ignores the width and builds the default
head. The red is recorded below before any width-8 or width-32 run is
read.

Run order step 3b: `run_sd.sh` with widths 8 and 32 (skip-if-done,
skip-if-running); no read of any width until all nine runs have
`done.json`. Steps 4–5 then read all three widths.

Red on record 2026-10-23 (`scripts/mutate.sh --expect
test_t7_widths_and_cap` on `sd_head.py` at ffcdbfa0; predicted first,
RED CONFIRMED, 1 passed after the restore): t7 — `configure` building
`SDHead()` at the default width instead of `SDHead(r=a.hidden)` →
`AssertionError: {'params': 6679, 'param_cap': 8445, 'over_cap': False,
'hidden': 8}` at the width-8 line of `test_t7_widths_and_cap`. Guards
t1–t6 unchanged, 7 passed at ffcdbfa0. Width-32 smoke (2 epochs, one
world, `--over-cap`, scratchpad only): manifest `params 15783,
over_cap true, hidden 32`; the same invocation without `--over-cap`
refused by `check_cap`.

Read-time guard added 2026-10-24: the first Read fence wrote the JSON
and then died printing the markdown (the width loop's variable `h` was
rebound by the per-head loops to "SD" / "NF" / "DR"; `KeyError: 'DR'`
at the second width's header). t8 `test_t8_md_every_width`: the
markdown built from the committed `phase1c-read.json` prints every
width × group block, every R2c table, R9c and R5c per width. Red
(`scripts/mutate.sh --expect test_t8_md_every_width` on
`read_phase1c.py` at 3ffd3e20; predicted first, RED CONFIRMED, 1
passed after the restore): the loop variable renamed back to `h` →
`KeyError: 'DR'`. 8 guards.

Gate round 1 (2026-10-24) found the R4c reliability table printing
seed 1's bin count beside a seed-mean fraction. `calibration_block`
now carries the count PER SEED (a list) and the markdown says so; t8
exercises it on a hand case (two seeds, one empty bin). Red
(`scripts/mutate.sh --expect test_t8_md_every_width` on
`read_phase1c.py` at d9365927; predicted first, RED CONFIRMED, 1
passed after the restore): the count written from seed 1 only
(`"n": r0["n"]`) → `AssertionError` on the hand case's `[7, 10]`.
