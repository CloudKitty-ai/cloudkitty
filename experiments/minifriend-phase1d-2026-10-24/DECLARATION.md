# Mini-friend Phase 1d — two reads on the committed heads: the filter's spread and a grave probability from the frozen 1b states (declaration 2026-10-24; owner-requested)

Owner's words, 2026-10-24, after the Professor's review of Phase 1c
was carried to her (`~/ai/professor/notes/for-experiments-minifriend-
phase1c-sd-head-review-2026-10-24.md`, receipt 15ef6660): "Let's run
those in three in the order you listed". The three, in the order
listed to her: (1) the ten-minute filter-spread test, (2) the
25-parameter logistic grave read on the frozen 1b states, (3) the
Phase 2 head choice. This arc runs (1) and (2); (3) is hers with the
reads in hand. The Professor's review is advice; her word in this
session is the kickoff.

Prereg: Gen 2 FROZEN at 18f06f84, §8 items 3 and 4 as Phase 1c's
declaration states them. Nothing here trains a new belief head or
moves the cap (8,445): read (1) touches no weights; read (2) fits a
25-parameter logistic read on top of the FROZEN 1b GRU states, so
every MSE and bias cell of F-064, F-065 and F-066 is unchanged by
construction. Recorded as deviations entry 13 (an addition before the
Phase 2 winner is named; no prereg text moves). Phase 1, 1b and 1c's
verdicts, floors and findings stand.

Welfare-cost line: 0 new covered cat-ticks. Nothing rolls out; every
sample is a Phase 1 or 1b raw already on disk, every weight a
committed head's.

## Questions

1. **Does the SD filter smear?** The Professor's mechanism (review
   §1b): a fractional two-tap shift of fraction f adds variance
   f(1 − f) bins² per tick, so a sharp belief under pure drift widens
   as √n while the engine's need rises with no uncertainty at all. If
   true, one mechanism explains F-066's residual share (2.013), the
   filter alone losing to the marginal mean in common states (153.18
   against 75.10) and the learned rates sitting under the empirical
   step and falling with width. Read-only on 1c's `head-best.pt`.
2. **Did the histogram make the probability?** F-066's one clean
   asset is a grave probability near the diagonal above p = 0.7 with
   mean P(grave) 0.474 on grave samples in sight. Any GRU head can
   emit a grave probability through one sigmoid. Is a logistic read
   of "the true stratum is GRAVE" on the frozen NF-h24 (and DR-h24)
   states as well calibrated as SD at width 16? If it is, the
   histogram bought nothing a probability-reading consumer needs and
   the hybrid (a Phase 1 head plus one sigmoid) is the candidate
   shape; if SD is clearly better calibrated, the structure bought
   real belief quality.

## Read 1 — R1d, the filter's spread (`filter_spread.py`)

For each of 1c's nine runs (widths 8 / 16 / 32 × seeds 1–3; the
committed `head-best.pt`), and for the initial rate every run started
from (0.4 points per tick = 0.08 bins per tick):

- A delta belief at bin 2 (the sharp prior) is propagated n ∈ {1, 10,
  50, 100} ticks of pure drift with 1c's `shift_matrix` — no relief
  (p_rel = 0), no residual — and its standard deviation reported in
  bins and in need points; also at n = 500 with a flag when mass has
  reached the top bin (the clamp; the closed form does not apply
  there). Per run the learned rate of every (friend, need) cell is
  read (25 cells), and the table reports the median cell, the
  largest cell and the smallest cell, plus the initial rate.
- The closed form beside each unclamped cell: each tick is one
  Bernoulli step of an extra bin with probability f (the fractional
  part; the integer part is deterministic), so after n ticks the
  extra displacement is Binomial(n, f) and the sd is exactly
  √(n f (1 − f)) bins. The read reports the implementation against
  the arithmetic (max absolute difference) and the arithmetic against
  the Professor's figure (2.7 bins at the initial rate after 100
  ticks).
- One relief step: a delta at bin 12 under one down-shift by the
  learned relief size per need; its sd in bins.

No bar; a reading rule: **the mechanism stands** if the unclamped
sds match √(n f (1 − f)) within 1e-6 bins and the 100-tick sd at the
initial rate is within 0.1 bins of 2.7. Prediction registered here:
both hold (the shift is a binomial by construction; the arithmetic
is the Professor's), and at the learned width-16 rates the 100-tick
sd is below the initial-rate figure in proportion to √(f (1 − f)).

## Read 2 — R2d, a grave probability from the frozen 1b states (`grave_probe.py`)

**Base heads**: Phase 1b's width-24 runs NF-h24-s{1,2,3} and
DR-h24-s{1,2,3} (`head-best.pt`, 7,807 params each; symlinked under
this arc's `results-raw/heads/`). Loaded, set to evaluation mode,
never updated: the probe reads the GRU output z (T, 24) produced
exactly as `train_heads.predict_world` produces it (hidden state zero
at a world's start, carried across 500-tick chunks). **Guard of
construction** (t2, and asserted at run time on the first evaluation
world): the frozen head's own output layer applied to the z the
probe extracted reproduces 1b's committed `pred-<set>-<seed>.npz`
to 1e-4 on the /100 scale, so the state the probe reads is the one
every F-065 cell was read from.

**Probe**: `Linear(24 → 1)` + sigmoid, 25 parameters; the hybrid's
total is 7,832, under the cap. Target per sample: the true stratum is
GRAVE (`strata.stratum` on the friend's true state; GRAVE includes
the happiness-only edge, which the probe CAN carry because the state
feeds the happiness output — SD's need histograms could not; 1c
counted those samples against SD and this read counts them for both;
the mean p on happiness-only grave samples is reported separately).
Loss: BCE at natural frequency (no stratum weight — a reweighted BCE
is not a probability; doctrine rules 1–2, pricing nothing), on the
TRAINING worlds' samples (74 worlds × 20 pairs, every tick), Adam lr
1e-2, batches of 65,536 samples shuffled each epoch, probe seed = the
base run's seed. Early stop on the VALIDATION worlds' BCE with a
**relative** margin: a new best when val < best × (1 − 1e-3), patience
10, cap 200 epochs. The margin is relative on the Professor's point
(review §2c): Phase 1's absolute 1e-4 was a 2% bar on NF's loss and a
0.009% bar on SD's; this read's BCE sits between those scales and an
absolute margin would again be a different rule. Outputs per base run
under `results-raw/probe/<run>+p/`: `run-manifest.json`,
`metrics.jsonl`, `probe.pt`, `pgrave-<set>-<seed>.npz` (p (T, 5, 5)
[observer, friend], NaN on the diagonal) for every evaluation world,
`done.json`.

**Reads** (`read_phase1d.py`; group P = the P1..P5 evaluation worlds,
4,000,000 samples, as 1c's R4c; per probe run then mean ± SD over the
three seeds; 1c's R4c instrument, refactored so it takes a
probability directly — `calibration_p` — with 1c's own read
regenerating byte for byte):

- **R2d(a) Calibration** of NF-h24+p and DR-h24+p beside SD at width
  16 (1c's committed R4c cells, pinned: guard t4), in three versions:
  in sight (the mind-visible samples), under fog (the rest), all.
  Per version: Brier, mean p on GRAVE, on COMMON, on ADJACENT, on
  happiness-only GRAVE; reliability in ten equal-width bins (count
  per seed, seed-mean p, seed-mean realised grave fraction); the
  **above-0.7 gap** = the mean over the bins with lower edge ≥ 0.7 of
  |seed-mean p − seed-mean realised fraction| (bins empty in every
  seed skipped); AUROC of p against the grave label.
- **R2d(b) Runs**: params, epochs to the plateau, best validation
  BCE, the base run's sha256 (unchanged).

**Decision rule, declared now** (rule 11; domain: group P evaluation
worlds, in sight, every covered sample pooled, mean of seeds 1–3;
comparator SD width 16 from 1c's committed read; the base head is
NF-h24 — DR-h24+p is read beside it and enters no rule). Let m_SD and
m_NF be the seed-mean P(grave) on GRAVE samples with seed SDs s_SD
and s_NF, Δ = m_SD − m_NF, s = √(s_SD² + s_NF²); let g_SD and g_NF
be the above-0.7 gaps.

- **(A) within the spread**: |Δ| ≤ s → the histogram bought nothing
  the consumer needs; the hybrid (a Phase 1 head plus one sigmoid) is
  the candidate shape for a probability-reading Phase 2 consumer and
  the SD line closes.
- **(B) SD clearly better**: Δ > s AND g_SD < g_NF → the structure
  bought real belief quality; ONE loop-fixed, diffusion-fixed SD run
  at the cap would be justified — a new declaration on her word, with
  a relative stopping margin and a learning-rate schedule.
- **(C) otherwise** (Δ > s with g_SD ≥ g_NF, or Δ < −s): mixed or
  reversed, reported as such; the shape question is hers.

Brier and the fog version are reported beside the rule and enter it
only as the write-up's context. The Professor's registered
predictions are scored here beside the originals, never overwritten:
**P2** "the frozen-state logistic read on NF-h24 reaches mean
P(grave) on grave samples ≥ 0.40 (SD-w16: 0.474) and ≤ 0.002 on
common samples, in sight" — scored by R2d(a); **P1** (a longer-cap
SD re-run stays READ over 1 with the signature on ≥ 4 friends) is
not scorable here (no such run) and is carried forward. Prediction
registered by this arc: outcome (A), with m_NF between 0.35 and 0.60
— the state already carries what the mean reads, and a BCE-fitted
logistic is calibrated on its training distribution by construction.

Not read: any MSE or bias cell (unchanged by construction; F-064,
F-065, F-066 stand); welfare; group G; the Phase 2 consumer; any
Phase 2 head choice (hers).

## Doctrine check (CLAUDE.md rule 8)

- Rules 1 and 2 moved the probe's loss: natural-frequency BCE, because
  a stratum-weighted BCE prices the under-read into the probability
  and the probability must report, not price (the Professor's §1c
  caution on quantile reads applies to weights the same way).
- Rule 8 (scarcity of information): the probe sees the frozen state
  only; nothing of the friend's hidden state enters as input. The
  target is the same truth stream 1c's R4c scored against.
- Rule 10 moved the reads: descriptive, seeds pooled as mean ± SD,
  the comparator pinned to a committed read, the decision rule
  stated with its domain before any probe is fitted.
- Rule 12: no rollout, nothing to stop. Rules 3–7, 9: checked, moved
  nothing.
- FINDINGS read (rule 7): F-066 (the R4c cells this answers and the
  residual share R1d explains), F-065 (the base heads), F-064.

## Instrument and guards (each with a predicted red before trust)

`test_phase1d.py` (plain-assert runner; Phase 1 arc venv; this arc's
split and symlinked raws):

- t1 spread arithmetic: a delta at bin 2 under one half-bin up-shift
  has sd 0.5 bins; under four such ticks sd 1.0 = √(4 × 0.25); the
  implementation equals √(n f (1 − f)) on a hand grid of f and n
  while unclamped; a clamped case is flagged. Red: the sd taken
  about the start bin instead of the belief's mean.
- t2 frozen state: on a 600-tick slice of one evaluation world, the
  probe's extracted z passed through the base head's own output
  layer equals 1b's committed prediction file to 1e-4; the base
  head's parameters are byte-identical before and after a probe fit
  on a 2-chunk smoke. Red: the hidden state reset at every chunk.
- t3 reader arithmetic: `calibration_p` on a hand case (Brier, mean p
  by class, reliability counts summing to n, the above-0.7 gap); the
  decision rule returns A / B / C on three hand cases. Red: the
  rule's spread inequality flipped.
- t4 provenance: `split.json` equals Phase 1b's; the SD width-16
  cells this arc re-reads from 1c's belief files (Brier, mean p on
  GRAVE, in sight) equal `../minifriend-phase1c-2026-10-23/
  phase1c-read.json`; the base runs' `head-best.pt` sha256 equal
  their `done.json`. Red: the comparator pointed at width 8.

Each red by `scripts/mutate.sh --expect <test name>` on the committed
file; the result lines are recorded below before any read is cited.
RESULTS.md gated by `/accuracy-gate` before commit; Collect (none —
no rollout; the probe fits are the Read fence's inputs and are
re-runnable in minutes) and Read fences separate, runtime declared.

## Run order (each step its own commit before its data)

1. This declaration, `split.json`, the raw and run symlinks
   (untracked), deviations entry 13, the timeline entry.
2. `filter_spread.py`, `grave_probe.py`, the `calibration_p` refactor
   of 1c's reader (1c's read regenerated byte for byte), `test_phase1d.py`
   t1–t4, reds on record. Smoke of the probe (2 chunks per set) to the
   scratchpad only.
3. The six probe fits (`run_probe.sh`), then R1d and R2d in one Read
   fence; `phase1d-read.json` + `.md` committed.
4. RESULTS.md gated; F-entry; deviations 13 closed; timeline updated;
   report to the owner with the decision rule's outcome. The Phase 2
   head choice stays hers.

Reds on record 2026-10-24 (`scripts/mutate.sh --expect <test>` on the
committed file at 95cc5aec; each predicted first, each RED CONFIRMED,
1 passed after every restore; 4 passed on the restored suite): t1 —
`belief_sd` taking the sd about bin 2 instead of the belief's mean →
`AssertionError` at the 0.5-bin line of `test_t1_spread_arithmetic`;
t2 — the hidden state reset at every chunk in `states_world` (`h =
None` after each append) → `AssertionError: ('NF-h24-s1', 'P1',
1095452, 0.497…)` inside `check_reproduces` (the 1b prediction no
longer reproduced past tick 500); t3 — the spread inequality flipped
(`abs(delta) > s`) → the first hand case returns C, `AssertionError`
at the `== "A"` line of `test_t3_reader_arithmetic`; t4 — `SD_WIDTH`
pointed at 8 → the re-read comparator no longer matches 1c's width-16
cells, `AssertionError: ('visible', 'brier')`. Smoke (DR-h24-s2,
2 train / 1 val / 1 eval world, 2 chunks, 2 epochs, scratchpad only):
the base reproduces 1b's prediction to 2.4e-7; probe 25 params, hybrid
7,832; `pgrave-L-905001.npz` (20000, 5, 5), NaN on the diagonal.
Phase 1c's 8 guards pass after the `calibration_p` refactor and its
read regenerates byte for byte (JSON and markdown).

## Addendum 2026-10-24: which need, and how soon (owner, the same day)

Her words, after the report and a sanity-check exchange on whether the
minis give the main models what they need: "Agreed, let's proceed.
First the breakdown by need and latency read". Two further reads on
the outputs already on disk (0 new cat-ticks; no weight touched),
declared here before either is run. Group P, seeds 1–3, mean ± SD.

**R3d — which need.** Domain: grave samples whose grave status is
carried by a need (some hidden need ≥ 90; the happiness-only grave
samples are excluded, having no grave need to name), per version (in
sight / under fog / all). Per head, the named need = the argmax over
the five hidden needs of the head's per-need score; a sample is
CORRECT when the named need is one of the sample's grave needs (≥ 90;
usually one). Heads and their per-need score: SD-w16 grave mass
(`belief-*.npz`), SD-w16 mean, NF-h24 mean, DR-h24 mean (the hybrid
keeps its base head's five means, so NF-h24 mean and DR-h24 mean are
the hybrid's which-need read; the probe emits one number and names no
need). Reported: accuracy pooled and per true grave need; the 5 × 5
confusion (true grave need × named need) for NF-h24 mean in sight;
top-2 accuracy; the marginal baseline (always name the most frequent
grave need on the training worlds' truth streams); the count of
samples with two or more grave needs. Fail-closed at Phase 1's
MIN_N = 200 per cell.

**R4d — latency.** Episodes on the truth stream: for each evaluation
world and friend j, a maximal run of consecutive ticks in stratum
GRAVE; one episode per observer k ≠ j (each observer carries its own
belief). Per episode and head, the detection tick is the first tick
of the episode at which the head's signal crosses its threshold;
latency = detection tick − onset tick (0 = detected at onset); an
episode with no crossing is MISSED. Signals and thresholds: P(grave)
≥ 0.2 and ≥ 0.5 for SD-w16 (1 − ∏(1 − m)), NF-h24+p and DR-h24+p; and
the mean-reading consumer, max over needs of the head's mean ≥ 90, for
SD-w16, NF-h24 and DR-h24 (the ostrich in latency terms). Reported per
head × threshold: episodes, detected fraction, median and 90th
percentile latency among detected (ticks), the fraction detected
within 10 ticks of onset; split by whether the friend was in the
observer's sight at onset (onset in sight / onset under fog) and
pooled; episode length median and 90th percentile. False alarms: per
head × threshold, maximal runs of the signal above threshold that
contain no grave tick, as a count per 10,000 observer-ticks and their
median length. Episodes shorter than 1 tick do not exist; no minimum
length is imposed; the length distribution is printed so a reader can
condition on it.

**Reading rules (not gates; what "enough to hand the trunk" means for
this sanity check, stated before the read):** (i) which-need accuracy
for NF-h24 mean in sight, pooled, ≥ 0.80 with every per-need cell with
n ≥ 200 above 0.60; (ii) NF-h24+p at P(grave) ≥ 0.2 detects ≥ 0.90 of
episodes with onset in sight, median latency ≤ 10 ticks. Both hold →
"enough for detection and naming, on this evidence"; one → partial,
reported; neither → the belief is not ready to hand over as read, and
the gap named. Registered predictions: (i) holds (the five means are
read on the states that feed them; the grave need is usually the only
high one); (ii) holds at 0.2 and the mean-reading rule (≥ 90) detects
under half of the same episodes — the ostrich as a missed-detection
rate. No decision beyond the sanity check; the Phase 2 declaration is
hers.

**Doctrine (rule 8):** rule 10 moved the reads (descriptive, per need
before pooled, min-n fail-closed, both thresholds printed so no single
operating point is privileged); rule 1–2 unchanged (nothing is
priced); nothing else moved.

**Guards** (`test_phase1d.py`, each with a predicted red): t5
which-need on a hand case (argmax among five scores; a sample with two
grave needs correct for either; happiness-only excluded; a cell under
MIN_N fails closed to None). Red: argmin. t6 latency on a hand slice
(two episodes, one crossing three ticks after onset, one never
crossing; a false-alarm run between them; onset-in-sight classified
from the visibility at the onset tick). Red: latency measured from the
slice's first tick instead of the onset. Reds recorded below before
the read is cited. The regenerated `phase1d-read.json` must keep R1d,
R2d, the decision and P2 blocks identical to the committed read
(asserted by the reader against the committed file before writing).

**Run order:** (1) this addendum, deviations 13 reopened, the timeline
line; (2) reader + t5–t6, reds; (3) the read (one fence); (4) RESULTS
§Addendum gated; F-entry; deviations 13 closed again; report.

Reds on record 2026-10-24 for the addendum (`scripts/mutate.sh --expect
<test>` on `read_phase1d.py` at 887020e4; each predicted first, each
RED CONFIRMED, 1 passed after every restore; 6 passed on the restored
suite): t5 — `which_need` naming the argmin instead of the argmax →
`AssertionError` at the accuracy line of `test_t5_which_need`; t6 —
the crossing searched from the slice's first tick instead of the
onset (`above[:en]`) → latency 7 for the hand episode's 3,
`AssertionError` at the median-latency line of `test_t6_latency`.

Post-read addition 2026-10-24 (after gate round 1 on the addendum,
which found that 200 of the 288 episodes begin at the world's first
tick — group P's per-cat grave starts — so a crossing there is the
head's prior, not a detection): R4d gains a split by onset class,
RESET (onset at the slice's first tick) against mid-world in sight
and mid-world under fog, beside the declared splits; "anticipated" is
measured slice-relative (never across a slice boundary; a reset
episode cannot be anticipated); false-alarm runs are reported all and
excluding runs that start at the world's first tick. The declared
reading rules and predictions are scored as declared (every in-sight
onset, reset included); the mid-world-only numbers are DISCLOSED
beside them, not a rule. Guard t6 extended (a reset episode, a
cross-boundary signal, a reset-transient run); red: the reset flag
forced false.

Red on record 2026-10-24 for the extended t6 (`scripts/mutate.sh
--expect test_t6_latency` on `read_phase1d.py` at 36da006d; predicted
first, RED CONFIRMED, 1 passed after the restore; 6 passed): the reset
flag forced false (`reset = False`) → the reset episode of the hand
case counted as mid-world, `AssertionError` at the reset line of
`test_t6_latency`. The "anticipated" definition is stated in full
after gate round 2: over the threshold at onset AND at the tick
before it, within the observer slice (the code's condition from the
start; the earlier wording named only the tick before).

## Addendum 2 2026-10-24: the operating-point sweep (owner, the same day)

Her words, while talking through the Phase 2 decisions (decisions 1, 2
and 4 ruled as recommended: two-stage on the frozen Phase 1b head, NF,
per-need probabilities added), after asking whether any analysis had
been run around the 0.2 mark: "Let's run the read and see what we
find". One further read on the probe outputs already on disk (0 new
cat-ticks; no weight touched), declared here before it runs.

**R5d — the operating-point sweep.** R4d's latency instrument
(`latency`, unchanged: detection = the first tick at or over the
threshold; episodes classed reset / mid-world in sight / mid-world
under fog; anticipation slice-relative; false-alarm runs all and
excluding runs that start at the world's first tick) applied to
NF-h24+p and DR-h24+p at thresholds 0.05, 0.10, 0.15, 0.20, 0.25,
0.30, 0.40, 0.50 (0.20 and 0.50 are R4d's rows and must reproduce
them). Two evaluation sets, read separately: group P (P1–P5, the
addendum's set) and group LWG (the evaluation worlds of Phase 1's L, W
and G — held out from the probe's training as P's are, but with no
per-cat grave start, so grave episodes are expected rare there; the
episode counts are printed and the reader conditions on them, no
fail-closed floor on an episode cell). Reported per set × head ×
threshold, seeds 1–3, mean ± SD: the mid-world in-sight and mid-world
fog detected fraction, anticipated fraction, median and p90 latency;
the reset detected fraction and median latency; mid-world false-alarm
runs per 10,000 observer-ticks and their median length; all-run false
alarms; and one derived column, mid-world false-alarm runs per 100
detected mid-world episodes (a ratio of printed counts).

**No reading rule.** The sweep is descriptive: it draws the trade-off
a threshold moves along. The pick is hers, with a stated price (the
odds at which a flag is worth acting on), which this read does not
supply. Disclosed in advance: a threshold picked from group P and then
read on group P in Phase 2 is a re-read of the same 20 mid-world
in-sight episodes; group LWG is read so a pick can rest on worlds
Phase 2 will not score. Platt scaling is monotone and does not change
this curve, only the labels on its points. Expectation stated before
the read (not a prediction to score): mid-world detection and
mid-world false alarms both non-increasing in the threshold, and
between 0.15 and 0.30 the mid-world false-alarm rate moving by less
than the seed spread of the mid-world in-sight detected fraction
(R4d: 0.073 → 0.064 per 10,000 ticks between 0.2 and 0.5, against a
seed SD of 0.087 on that fraction).

**Guard** t7 (`test_phase1d.py`): the sweep on a hand slice — a signal
sitting exactly at the threshold counts as a crossing (at or over);
detected fraction and false-alarm runs non-increasing across the
ladder; and the sweep's 0.2 and 0.5 rows on group P equal the
committed R4d rows. Red: `>=` → `>` in the crossing test (the hand
signal sitting exactly at the threshold is then missed).

**Doctrine (rule 8):** rule 10 moved it (both sets printed, counts
printed, no single operating point privileged, no rule); nothing
priced; nothing else moved. Welfare cost: 0 covered cat-ticks.

**Run order:** (1) this addendum, deviations 13 reopened, the timeline
line; (2) `sweep_threshold.py` + t7, red; (3) the read (one fence);
(4) RESULTS §Addendum 2 gated; the curve to her; the pick hers.

Red on record 2026-10-24 for t7 (`scripts/mutate.sh --expect 'exactly
at the threshold counts'` on `read_phase1d.py` at 8990ccee; predicted
first — t7 red at the exactly-at-threshold line, t6 green since its
signals sit at 0.9 against 0.5 — RED CONFIRMED, 2 passed after the
restore; 7 passed on the restored suite): the crossing test changed
from at-or-over to strictly-over (`>= thresh` → `> thresh`) → the hand
signal sitting exactly on 0.2 at onset is missed, `AssertionError` at
the first detected-fraction line of `test_t7_sweep`.

Post-read addition 2026-10-24 (after the first run of the sweep, before
any write-up). Two things the declaration got wrong, stated here: (a)
the expectation that false-alarm RUNS are non-increasing in the
threshold did not hold — on L / W / G the mid-world run count rises
from 0.27 to 0.41 per 10,000 ticks between 0.05 and 0.50, and on group
P it is flat; the mechanism is run splitting (a higher threshold cuts
one run into several, and a sub-run of a run that contained a grave
tick becomes a run that contains none), so the sweep gains one
post-read column, non-grave ticks at or over the threshold per 10,000
observer-ticks, which is a tick count and monotone by construction
(it includes the ticks just before an onset and after an episode's
end, so it is not a false-alarm rate; the run columns stay the
false-alarm read); (b) grave is not rare on L / W / G: G is Phase 1's
grave-start group (all six needs started in 60–95), so the set carries
296 episodes of which 196 are reset, and L contributes none — the
sweep gains a per-set episode composition. Guard t7 extended for both
(the tick column on the hand slice, monotone; the composition). Red on
record 2026-10-24 (`scripts/mutate.sh --expect nongrave_above_per_10k`
on `sweep_threshold.py` at dd11ce6a; predicted first — the 0.10 cell
survives the mutation by coincidence, two grave ticks at or over 0.10
against two non-grave, and the 0.15 cell catches it — RED CONFIRMED, 1
passed after the restore): non-grave ticks counted as grave
(`!= GRAVE` → `== GRAVE`) → `AssertionError` at the tick-column line of
`test_t7_sweep`.

Second post-read addition 2026-10-24 (after accuracy-gate round 1 on
RESULTS §Addendum 2, before any number of it was cited). The round
measured, read-only on the saved outputs, that the runs R4d counts as
mid-world false alarms almost all start within a slice's first hundred
ticks, and that the L / W / G rate's rise with the threshold is
world-start runs whose first tick falls under the threshold (they then
start at offset 1 and escape R4d's first-tick exclusion) — not the run
splitting the first write-up named, and the non-grave ticks over the
threshold are not mostly anticipation. So the sweep gains the
run-start detail per row: the number of mid-world false-alarm runs
starting at offset 1, the fraction starting within the first 100 ticks
(offset ≤ 100, inclusive), and the runs starting after tick 100 per
10,000 observer-ticks. 100 is a reporting constant, chosen after the
distribution was seen; it is not a declared burn-in and no rule rests
on it. Guard t7 extended (a 300-tick hand slice with runs at offsets
1, exactly 100 and 200; the detail's run count asserted equal to
R4d's). Red on record 2026-10-24 (`scripts/mutate.sh --expect
frac_start_le_early` on `sweep_threshold.py` at 2d7bfbff; predicted
first — the offset-100 run reclassified as late, the fraction 1/3 for
2/3 — RED CONFIRMED, 1 passed after the restore; 7 passed on the
restored suite): the early/late boundary moved from "after 100" to "at
or after 100" (`st > EARLY` → `st >= EARLY`) → `AssertionError` at the
fraction line of `test_t7_sweep`.

## Addendum 3 2026-10-25: the burn-in (owner, after the sweep report)

Her words, on the sweep report (decision 3 of the Phase 2 talk-through,
the threshold): "Agreed, let's start with 0.10. Run the burn in". Two
things follow. (a) The threshold ruling: P(grave) ≥ 0.10 for the
evaluation's reading rule, "start with" recorded verbatim — the pick
is hers and stays hers to move. (b) One further read on the probe
outputs already on disk (0 new cat-ticks; no weight touched), declared
here before it runs.

**R6d — the burn-in.** The sweep (§Addendum 2) found that nine in ten
or more of the false-alarm runs R4d counts as mid-world start within a
slice's first 100 ticks, and reported 100 as a post-read constant
with no rule on it. This read makes the burn-in an instrument: the
alarm is forced off for the first B ticks of every observer slice (the
saved P(grave) replaced by a value under every threshold at offsets
0 … B − 1; nothing else changes), and R4d's `latency` instrument runs
unchanged on the masked signal. NF-h24+p only (decision 2 ruled NF),
seeds 1–3, mean ± SD, group P and the L / W / G evaluation worlds as in
§Addendum 2. The full grid is read — burn-in lengths 0, 25, 50, 100,
150, 200, 300 ticks × the sweep's eight thresholds — and two
cross-sections are printed per set: the burn-in ladder at her
threshold, 0.10, and the threshold ladder at a burn-in of 100.
Per cell: the fraction of observer-ticks the alarm is blind to (B over
the slice length, summed); the mid-world in-sight and fog detected
fractions and p90 latency as before; the number of mid-world episodes
whose onset falls inside the burn-in and, for those, the detected
fraction and median latency (an onset at offset k < B can be caught
no earlier than B − k); the reset detected fraction and median latency
(a reset episode is caught no earlier than B); all false-alarm runs
per 10,000 observer-ticks (under a burn-in there is no first-tick run
to exclude, so the all-runs column is the false-alarm read) and their
median length; the runs that begin exactly at offset B (the transient
still running when the burn-in ends); and false-alarm runs per 100
detected mid-world episodes. Three identities hold by construction
and the reader asserts them before writing: the B = 0 cells equal the
sweep's NF-h24+p cells at every threshold on both sets; mid-world
episodes whose onset is at or after B have the same per-episode
latency as at B = 0; and at B = 100 the false-alarm run count equals
the sweep's runs-starting-after-tick-100 count plus the runs beginning
exactly at offset 100.

**No reading rule.** Descriptive, as the sweep was: it prices a
burn-in length in blind ticks and in delayed episodes against the
false alarms it removes. The burn-in is a consumer rule for our
evaluation, of the same standing as the threshold: the policy gets the
probability. Expectations stated before the read (not predictions to
score): false-alarm runs per 10,000 non-increasing in B at a fixed
threshold on both sets (a run can only vanish or be truncated; a
truncated run that kept no grave tick becomes a false alarm, so this
can fail and the reader prints the count that would show it — the
runs beginning at offset B); at B = 100 and 0.10 the false-alarm rate
on group P within 0.05 per 10,000 of the sweep's late-runs column
(0.007); reset detection delayed to a median latency of B on every
cell with B > 0.

**Guard** t8 (`test_phase1d.py`): on the sweep's 300-tick hand slice
(runs at offsets 1, 100, 200, no grave tick) the run count under
burn-in 0 / 100 / 101 / 102 is 3 / 2 / 2 / 1 with the run beginning
at the boundary counted at 100 and 101, and the blind fraction is
B / 300; on the sweep's 20-tick slice an onset inside the burn-in is
missed when its only over-threshold tick is masked and caught at
latency B − k when a later tick is over; an onset at or after B keeps
its B = 0 latency; the reader's identities on group P at 0.10 and 0.20
with B = 0 and 100. Red: the mask's end moved one tick short
(`a + B` → `a + B − 1`; the tick at offset B − 1 escapes the burn-in) —
at B = 101 the run at offsets 100–101 is no longer truncated, so no run
begins at the boundary: `AssertionError` at the boundary line.

**Doctrine (rule 8):** rule 10 moved it (the full grid read, both
cross-sections and the counts printed, no burn-in privileged, no
rule); nothing priced; nothing else moved. Welfare cost: 0 covered
cat-ticks.

**Run order:** (1) this addendum, deviations 13 reopened, the timeline
line with her ruling; (2) `burnin_read.py` + t8, red; (3) the read
(one fence); (4) RESULTS §Addendum 3 gated; the price to her; the
burn-in length hers.

Red on record 2026-10-25 for t8 (`scripts/mutate.sh --expect
fa_runs_at_boundary` on `burnin_read.py` at ea60a35d; predicted first —
the B = 0 and B = 100 hand cases survive the mutation since the tick
that escapes carries no signal there, and the B = 101 case catches it
— RED CONFIRMED, 1 passed after the restore): the mask's end moved one
tick short (`< burnin` → `< burnin - 1`) → at B = 101 the run at
offsets 100–101 is no longer truncated and no run begins at the
boundary, `AssertionError: (101, 0)` at the boundary line of
`test_t8_burnin`.

Post-read addition 2026-10-25 (after the first run of the burn-in read,
before any write-up). The read's "mid-world onsets inside the burn-in"
column reached every mid-world episode by B = 100 on both sets (88 of
88 on group P, 100 of 100 on L / W / G): no grave episode in either
evaluation set begins after a slice's hundredth tick. That is a fact
about the sets the sweep's composition did not show (it counted onsets
as reset or not, never where the non-reset ones fall), and it changes
what a burn-in costs, so the reader gains two post-read blocks per set,
both measured before any sentence of the write-up was drafted: (a) the
mid-world onset offsets — count, min, median, max, the counts at or
under 25 / 50 / 100 ticks, how many share their slice with a reset
episode (the grave-start friend crossing back into grave), and per
slice whether a grave tick falls inside the first 100 ticks, after them,
and how many ticks; (b) the start-up split per threshold — among slices
with a grave tick inside the first 100 ticks and among slices with
none, the fraction whose alarm fires inside that window (the alarm's
discrimination during the transient, which is where every onset is).
100 is the declared burn-in cross-section, not a rule. Guard t8
extended (the 20-tick slice's offsets; three hand slices with a reset
plus a re-entry, grave only after the window, and no grave; the split
on a signal firing in two of the three). Red: the split's window test
widened to the whole slice (`grave[a:a + window]` → `grave[a:b]` in
`startup_split`) — the slice with grave only after the window is then
counted among the grave slices, `AssertionError` at the grave-slices
line.

Red on record 2026-10-25 for the extended t8 (`scripts/mutate.sh --expect
grave_slices` on `burnin_read.py` at b70449dc; predicted first — RED
CONFIRMED, 1 passed after the restore): the split's window test widened
to the whole slice → the hand slice with grave only after the window
joins the grave slices, `AssertionError` at the grave-slices line of
`test_t8_burnin`.

Second post-read addition 2026-10-25 (after accuracy-gate round 1 on
RESULTS §Addendum 3, before any number of it was cited). The round
measured, read-only on the saved outputs, that the false-alarm rate's
rise from B = 25 to B = 50 on group P is entirely the truncation case
this addendum named as possible — boundary runs that are the tail of
an unmasked run which began before the burn-in and held a grave tick,
a detection run cut by the mask into a false alarm — where the draft
had called it "one part … unmeasured"; and that the draft's
composition of the clean slices and L's dimensions were wrong. So the
reader gains, per cell, the boundary runs cut from a grave run (the
unmasked run containing offset B began before B and holds a grave
tick), and per set the slice composition (slices, observer-ticks,
slices with grave in the window, by evaluation set). Guard t8 extended
(a slice with grave at 0–2 and the signal over the threshold at 0–5:
at B = 4 the boundary run is a cut one, at B = 6 there is none; a run
beginning exactly at the boundary with no grave tick is not cut; the
per-set composition of the three hand slices). Red: the unmasked
signal replaced by the masked one in the cut test
(`boundary_runs(idx, above_m, above_0, …)` → `(idx, above_m, above_m,
…)`) — no unmasked run then begins before the boundary, so the cut
count is 0 where the hand case has 1, `AssertionError` at the cut line.

Red on record 2026-10-25 for the second extension of t8
(`scripts/mutate.sh --expect fa_runs_at_boundary_cut_from_grave_run` on
`burnin_read.py` at 49137bf9; predicted first — RED CONFIRMED, 1 passed
after the restore): the unmasked signal replaced by the masked one in
the cut test → the cut count 0 where the hand case has 1,
`AssertionError` at the cut line of `test_t8_burnin`.

## Addendum 4 2026-10-25: history and state — the zero-collection reads (owner, after the burn-in report and the Professor's note)

Her words. On the burn-in report and the Professor's note of the same
day (`~/ai/professor/notes/for-experiments-midworld-onset-instrument-
2026-10-25.md`, sha256 prefix 2139fc3a389fbec6 at receipt — the Professor appended a relay-status block to the note afterwards, so the file's hash has moved; §Q6 is quoted verbatim in RESULTS §Addendum 4): "Let's do another
threshold sweep rather than choosing an arbitrary value. Maybe
0.1,0.3.,0.5 to start so we can get a feel for the trade-off.
Zero-collection reads first. What other decisions do you need in order
to proceed?"; then "Yes on splice test. Yes on relay to product.
Confirm 3" (3 = the small burn-ins and the warm start below, in place
of ruling 100). Three things follow. (a) **Decision 3 is reopened**:
the "start with 0.10" of §Addendum 3 is withdrawn by her; every table
of this addendum reads the three-point ladder P(grave) ≥ 0.10 / 0.30 /
0.50 and the pick waits on these reads. No burn-in is ruled. (b) The
reads below run on arrays already on disk — the saved observation
streams of the evaluation worlds, the frozen NF-h24 heads, the three
probes, SD width 16's heads — 0 new cat-ticks, no weight touched. (c)
The scripted "needy" friend goes to Product as a relay on her word
(sent 2026-10-25, msg fe6e7d7c); its set, if built, gets its own
declaration and welfare line and waits for these reads.

What the burn-in established, and what nobody has asked. Every grave
onset in every evaluation set is a start-up onset or a re-entry within
72 ticks of one, read by a GRU state at most that old; the B = 0 false
alarms are first-tick runs (runs beginning at the slice's first tick:
800 / 242 / 800 of 830 / 271 / 828 at 0.10 on group P, per seed, from
the committed sweep file), the zero-state transient. Nothing on disk
has asked the probe to see grave arriving on a state that has tracked
a long clean history. That question splits in two, history and
signature, and the history half is answerable without a world.

**R7d — five reads, one reader (`history_read.py`), NF-h24+p seeds
1–3, mean ± SD; SD width 16 seeds 1–3 in read (b) only.** The frozen
head is re-run exactly as `grave_probe.states_world` runs it (hidden
state zero at the slice start, carried across 500-tick chunks; the
chunking changes nothing under no_grad) and the probe's logit z_t =
w·h_t + b and P(grave) = σ(z_t) are kept per tick. Guard of
construction: on the first evaluation world of group P the re-run
P(grave) equals the committed `pgrave-*.npz` to 1e-5 before anything
else runs.

(a) *State convergence on L* (the Professor's P3). Over L's 60
evaluation slices (all clean: no grave tick in 1,200,000
observer-ticks), per seed: the step d_t = ‖h_t − h_{t−1}‖₂ and the
drift D_t = ‖h_t − h_100‖₂, medians over slices and ticks within the
windows [1, 100), [100, 300), [300, 1,000), [1,000, 5,000),
[5,000, 20,000); the logit's per-slice least-squares slope over
t ≥ 300 (logits per 1,000 ticks), its mean and SD over slices, the
within-slice SD of z_t over t ≥ 300 (mean over slices), and the ratio
|mean slope × 19,700| / mean within-slice SD (the drift over the rest
of the slice in units of the scatter). Also kept: h̄ = the mean of
h_t over t ≥ 1,000 and all 60 slices (per seed), the warm-start state
of read (c), and σ(w·h̄ + b).
P3 scored as: (i) the median d_t in [300, 1,000) is within a factor
of 2 of the median in [1,000, 20,000) and both are under the median in
[1, 100); and (ii) the drift-to-scatter ratio is under 1. Both hold →
met.

(b) *The splice* (P4). Donors: the 200 reset episodes of group P's
evaluation slices (50 worlds × the four observers of the grave-start
seat): the friend's 58-cell row over ticks 0 … en − 1 of the episode,
and its in-sight bit at tick 0. Recipients: L's 60 evaluation slices,
donor i → slice i mod 60. For each history length H ∈ {100, 500,
2,000}: the input is the recipient pair's own 167-cell rows for ticks
0 … H − 1, then for ticks H … H + en − 1 the recipient observer's own
self block (109 cells, continuing as recorded) beside the donor
friend's row; the head runs from the zero state; the episode is
[H, H + en). Per H × threshold: detected fraction, median and p90
latency from the junction, within 10 ticks, split by the donor's
in-sight bit at onset; H = 0 is the donor episode in its own slice
(the committed P(grave); its reset rows must equal the sweep's at
0.10 / 0.50, asserted). *Junction control*: the same recipients and
history lengths with a donor segment of the same length from the
same P world and observer watching a default-start friend (the next
seat in roster order after the grave-start seat, skipping the
observer) — the fraction of junctions whose alarm fires inside the
segment, per threshold; a control that fires as often as the grave
donors would make the detection a junction artefact. *SD width 16*:
the same spliced inputs through the three SD-s heads (friend index =
the donor friend's seat throughout; state from the seat's prior at
tick 0), P(grave) = 1 − ∏(1 − grave mass) as R4c defines it, the same
columns; its H = 0 reset row at 0.50 must equal R4d's committed SD
row. Limitation declared: the donor's row at the junction is a
fresh-world row (scene age, spatial group, answers-me are the donor
observer's), so the junction is a jump into a covered friend's grave,
not a crossing; the read licenses "does the response to a covered
grave signature depend on how long the state watched the friend be
fine", nothing about a slow crossing.
P4 scored as: for NF-h24+p at 0.10, the range over H ∈ {100, 500,
2,000} of the seed-mean detected fraction is under the mean over H of
its seed SD, and the same for the median latency; both hold → met.
The SD rows are reported beside; the one condition the Professor
named (NF degrades with H and SD does not) is read off them, not
scored as a prediction.

(c) *Small burn-ins and the warm start* (P5). The §Addendum 3 grid at
B ∈ {0, 2, 5, 10} × the three thresholds on group P and on L / W / G
through `burnin_read.grid` unchanged (B = 0 pinned to the sweep as
before). Then the warm start: every evaluation slice of both sets
re-run from h_0 = h̄ (per seed, from read (a)) instead of zero, the
resulting P(grave) read through the same grid at B = 0: the start-up
split, the reset detected fraction and median latency, all-runs false
alarms per 10,000 and the runs beginning at the first tick, at the
three thresholds.
P5 scored as: at B = 5 and 0.10 on group P the all-runs false alarms
are ≤ 0.20 per 10,000 and the reset detected fraction ≥ 0.90 (seed
means); and the warm start at B = 0 has false alarms ≤ B = 5's and
reset detection ≥ B = 5's. All hold → met.

(d) *The self-block swap* (P8). On group P's 200 grave-start slices:
the input keeps the friend row of (observer k, grave-start seat j*)
and takes the 109-cell self block of observer k′ = the next seat in
roster order after k, skipping j* (k′ ≠ k). The head runs from zero;
R4d's `latency` runs on these 200 slices swapped and unswapped (the
unswapped signal recomputed from the committed P(grave) on the same
sub-index, so the two differ in the self block alone) at the three
thresholds: reset detected fraction and median latency, mid-world
in-sight and fog detected fractions (the re-entries), all-runs false
alarms per 10,000, the start-up split, and mean P(grave) on grave and
on common ticks.
P8 scored as: at 0.10 the mid-world in-sight and the mid-world fog
detected fractions move by less than the unswapped row's seed SD
(|Δ of seed means| < SD; where the unswapped SD is 0 the bar is a
move of 0). Both hold → met.

(e) Every table at 0.10 / 0.30 / 0.50; per seed and mean ± SD; no
threshold privileged.

**No reading rule.** Descriptive; the four scored bars are the
Professor's registered predictions with this thread's
operationalisations stated above, scored beside the originals and
sent to them. This thread's own expectations, not predictions to
score: the junction control fires in under 0.05 of junctions at 0.10
at every H (a higher rate is reported as a confound of (b)); the warm
start removes at least nine in ten of the first-tick runs at 0.10 on
group P; the swap moves the reset detected fraction at 0.10 by under
0.05.

**Guard** t9 (`test_phase1d.py`). Hand cases, no head: the
convergence windows and the slope on a synthetic state that decays
to a constant and a logit with a known linear trend (window medians,
slope recovered, ratio); the splice assembly on hand arrays (ticks
0 … H − 1 are the recipient's 167 cells; from H the first 109 cells
are the recipient's self rows H …, the last 58 the donor's rows
0 …; the episode is [H, H + en); a hand P(grave) crossing at H + 3
reads latency 3 and a crossing at H − 1 does not count); the swap
assembly (first 109 cells from k′, last 58 the (k, j*) row; k′ never
k or j*); the junction-control donor is the declared seat. Real pins:
the re-run head reproduces the committed P(grave) on the first P
evaluation world to 1e-5; H = 0's reset rows equal the sweep's at
0.10 / 0.50; the unswapped sub-index rows at 0.10 are consistent with
the sweep's reset rows (same episodes, same latencies). Red: the
donor rows shifted one tick late in the assembly (`donor[t]` →
`donor[t + 1]` at the junction) — the hand assembly's first donor row
no longer equals the donor's row 0, `AssertionError` at the junction
line.

**Doctrine (rule 8):** rule 10 moved it (every table on the full
three-point ladder, per seed, the bars declared and operationalised
before the read, the junction control beside the detection, no
threshold or burn-in privileged, no rule); rule 9 moved read (b)'s
design (no covered friend is forced grave: the covered grave rows come
from episodes already collected); nothing priced; nothing else moved.
Welfare cost: 0 covered cat-ticks.

**Run order:** (1) this addendum, deviations 13 reopened a fourth
time, the timeline line with her words; (2) `history_read.py` + t9,
red; (3) the read (one fence; the head re-run over every evaluation
slice three times — plain, warm, spliced — plus SD on the splices:
minutes, declared on the fence); (4) RESULTS §Addendum 4 gated; the
four scores to the Professor beside their originals; the threshold
and the burn-in to her with the ladder.

Red on record 2026-10-25 for t9 (`scripts/mutate.sh --expect "junction:
the donor's rows begin at H"` on `history_read.py` at 944211dd;
predicted first — RED CONFIRMED, 1 passed after the restore): the
donor rows shifted one tick late in the splice assembly
(`x[H:, SELF:] = donor_rows` → `x[H:-1, SELF:] = donor_rows[1:]`) →
the first spliced donor row keeps the recipient's friend row,
`AssertionError: junction: the donor's rows begin at H` in
`test_t9_history`.

Post-read addition 2026-10-25 (after the first run of the history read,
before any sentence of the write-up). Two results need a column each
before they can be written about. First, the splice: detection of the
covered grave rows is near-complete at H = 0 and falls to about a third
at H = 100, then stays flat to H = 2,000 (NF+p and SD alike), with the
junction control never firing; and the warm start cuts reset detection
on the real episodes to about six in ten. Between H = 0 and H = 100
two things change at once, the state's history and the self block
(the donor observer's at H = 0, the L recipient's at H ≥ 100), and
read (d) separates them only at the zero state. So the reader gains
the splice at **H = 0 with the recipient's self block** (the
recipient's self rows 0 … en − 1 beside the donor's rows, from the
zero state; the same columns; NF+p and SD; its control is the clean
rows from the zero state): if it detects as H = 0 does, the collapse
is the state's; if it collapses too, the self block or the world type
is in it. Second, the obvious question about the fitted worlds: the
reader gains, per role (train, val, eval) over every set, the grave
ticks by offset from the world start (count, max offset, counts at or
under 100 / 300 / 500 / 1,000) and the grave episode onsets (count,
max onset offset, onsets after tick 100), per world × friend — so any
sentence about what the head was shown is a measured one. Guard t9
extended (the H = 0 assembly and its reset episode; a hand set of code
columns with an onset exactly at tick 100, which is not "after" it).
Red: the after-window test made inclusive (`st > windows[0]` →
`st >= windows[0]`) — the onset at tick 100 is then counted after it,
`AssertionError` at the onsets-after line.

Red on record 2026-10-25 for the extended t9 (`scripts/mutate.sh
--expect onsets_after_100` on `history_read.py` at 3a41d7bc; predicted
first — RED CONFIRMED, 1 passed after the restore): the after-window
test made inclusive → the hand onset at tick 100 counted after it,
`AssertionError: onsets_after_100: an onset exactly at tick 100 is not
after it` in `test_t9_history`.

## Addendum 5 2026-10-26: the knee — where between 0 and 100 clean ticks the probe stops seeing a covered grave (owner, on the ladder walkthrough)

Her words. On the walkthrough of the three outstanding items after
§Addendum 4's report, item 1 ruled first ("We'll start with your
recommendation (10/2) , then after we get the mid-episode testing, we
can reevaluate and dial in on the optimal level." — P(grave) ≥ 0.10
with a 2-tick burn-in, provisional; deviations entry 13), then item 2:
"Run the knee read now". The read is the Professor's proposal in
their note's §Scoring (`~/ai/professor/notes/for-experiments-midworld-
onset-instrument-2026-10-25.md`, sha256 prefix 202cac6c4d7c7b30 as read
today), quoted verbatim: "The collapse is somewhere in H ∈ (0, 100).
Running the existing splice at H ∈ {1, 2, 5, 10, 20, 50} on the same
donors and recipients costs one fence and locates the knee. The stratum
boundaries in item 1 should be set from that knee, not from 100; and
the knee is the one number that tells her whether a 2-tick or 5-tick
burn-in sits before or after the head stops seeing grave on P's own
data. Threshold and burn-in remain hers on the ladder; this read only
prices the ladder."

**R8d — one read, one reader (`knee_read.py`), the §Addendum 4 splice
unchanged at six new history lengths.** `history_read.splice_rows_nf`
and `splice_rows_sd` run exactly as §Addendum 4 (b) declared them —
the same 200 covered reset-grave donors of group P, the same 60 clean L
recipients (donor i → slice i mod 60), the recipient's self block
continuing from the junction, the head from the zero state, the
junction control (a default-start friend's rows of the same length)
beside — at H ∈ {1, 2, 5, 10, 20, 50}, NF-h24+p seeds 1–3 and SD width
16 seeds 1–3, every table at 0.10 / 0.30 / 0.50, the same columns
(detected fraction, median and p90 latency from the junction, within
10, split by the donor's in-sight bit, false alarms inside the
history, the control's fired fraction). Guard of construction: the
reader also re-runs H = 100 and asserts, per seed and per threshold,
that its detected fraction and median latency equal the committed
`phase1d-history.json` rows exactly (the same function on the same
arrays), before any new H is read; the committed H = 0 / 0r / 500 /
2,000 rows are quoted beside the new ones, not re-run. The §Addendum 4
limitation stands: the junction is a jump into a covered friend's
grave, not a crossing.

**The knee, operationalised** (descriptive, declared before the read):
the smallest H in {1, 2, 5, 10, 20, 50, 100} at which the seed-mean
detected fraction at 0.10 is at or under the midpoint between the
committed H = 0 reset detection (0.995) and the committed plateau (the
mean of the H = 500 and H = 2,000 detected fractions, 0.2875), i.e.
≤ 0.641; reported for NF-h24+p and for SD width 16 with its own
committed endpoints. A control that fires at a small H says the
recipient's own start-up transient is in that row; the knee is read
with the control beside it, and the first H at which the control
fires in under 0.05 of junctions is reported as the end of the
recipient transient.

**Registered prediction, the Professor's P9, verbatim from the note's
§"Registered predictions, added 2026-10-26":** "On the splice at 0.10,
NF-h24+p, seed-mean detection at H = 10 is below 0.70, and detection at
H = 20 is within one seed SD of H = 100's 0.358." Scored as: (i) the
seed-mean detected fraction at H = 10 and 0.10 is < 0.70; (ii) |seed-
mean detected fraction at H = 20 − the committed H = 100 seed mean
(0.358)| ≤ the committed H = 100 seed SD (0.175). Both hold → met.

This thread's expectation, not a prediction: the junction control at
0.10 fires in under 0.05 of junctions at every H ≥ 5 (the first-tick
false-alarm runs have median length about 1 tick, and §Addendum 4's
burn-in grid shows the boundary runs gone by B = 5).

**No reading rule.** The knee prices the ladder and sets the needy
set's onset strata (Product's spec 067 makes the level boundaries
configurable with the Professor's example as the default; the set's
declaration sets them from this number); the threshold and burn-in
stay as ruled above.

Doctrine check (CLAUDE.md rule 8): no rule moves a choice; the read
is the declared §Addendum 4 instrument at new values of its one
parameter, on arrays already on disk.

Guard (rule 5, predicted red before trust): `test_phase1d.py`
`test_t10_knee` — `knee_read.knee_of` on a hand ladder (detected
0.90 / 0.80 / 0.64 / 0.30 at H 1 / 2 / 5 / 10, endpoints 1.00 and
0.28, midpoint 0.64) returns 5, the first H AT OR UNDER the midpoint;
`knee_read.score_p9` on hand rows (H = 10 at 0.65; H = 20 exactly one
SD from the reference) returns met. Predicted red: the knee's "at or
under" made strict (`<=` → `<`) → the hand ladder's knee moves from 5
to 10, `AssertionError: knee: the first H at or under the midpoint`.

Welfare cost: 0 new cat-ticks; reads on arrays already on disk; no
weight touched; nothing a covered mind experiences changes.

Run order: (1) this addendum committed; (2) `knee_read.py` + t10, run,
committed; (3) the red via `scripts/mutate.sh`, on record; (4) the
read (`phase1d-knee.json` / `.md`), committed; (5) RESULTS §Addendum 5
drafted, gated, stamped; a FINDINGS entry only if the knee is a
finding on its own; (6) the number to Product (spec 067's strata) and
the P9 score to the Professor, both on her standing word for this
read.
