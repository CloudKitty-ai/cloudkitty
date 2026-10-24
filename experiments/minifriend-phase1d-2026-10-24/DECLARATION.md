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
