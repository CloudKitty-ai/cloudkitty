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
