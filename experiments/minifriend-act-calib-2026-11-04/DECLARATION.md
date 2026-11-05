# Act-head calibration — a zero-collection reliability read on B10 and B30 before Phase 2 declares (declaration 2026-11-04; on her word "Sounds good, let's get started")

Owner's words, 2026-11-04. Her question that opened this: "is there a
measure of predictive certainty we can use when feeding this information
into the main cat model, so allow it to decide based both on the
prediction and on how strong that prediction is?" The answer given: feed
the act head's full distribution plus top probability and entropy; the
needs head gets ticks-since-seen as its uncertainty proxy; and "an
act-head calibration read before the Phase 2 declaration freezes". She
had the findings and that exercise relayed to the Professor ("relay our
findings and this probability exercise to Professor for review and
feedback"); their note (sha256 938134f9…, confirmed by her) asked for the
read to be binned by regime AND to carry the within-regime axis
(accuracy binned by entropy inside the in-sight cell), to run on B10 and
B30 both, and to fit any temperature per regime on the validation split
and freeze it. To the order "reliability read → Phase 2 declaration →
recipe sharpenings" her word was "Sounds good, let's get started". The
act arc's §13 records the same day's rulings (P25's consequence amended
to sight and heard; arm C skipped; B20 only as a registered Phase 2
prediction).

**Status: DECLARED 2026-11-04 (2d111f51); guards c1–c7 RED CONFIRMED
(§7, this commit); nothing collects (0 covered cat-ticks); no weight
moves; nothing acts. No number from this arc exists at this write. The
reads start on this commit.**

Welfare-cost line. Covered minds: none exposed. Every read walks raws
already on disk (the needy set's tuning half, Phase 1e's 52 validation
worlds) with the committed act heads B10-s1..3 and B30-s1..3. Exposure
0. What it buys: whether the act head's confidence means what the policy
will be shown (a stated 0.8 is right 0.8 of the time, by regime), whether
its entropy separates right ticks from wrong ones inside a regime (the
question "how strong is this prediction" actually asks), whether the
wider head's log-loss gain is knowledge or calibration (the one argument
for B20 that could survive registration), and a frozen temperature for
Phase 2's certainty cells, so they mean the same thing after a retrain.

## 1. What is being asked

1. **Reliability by regime (C1).** On the tuning half's covered friends,
   bin each tick by the head's top probability and compare the bin's
   mean confidence with its accuracy; ECE on the top label per regime
   (seen / heard / silent, and all). The needs head's D5 showed regime
   dependence (over-confident about 2× on covered friends, under 1.4× on
   the scripted); the same shape is expected here.
2. **Certainty against correctness within a regime (C2).** Inside each
   regime, accuracy binned by the normalised entropy of the predicted
   distribution, and the AUROC of (1 − entropy) as a predictor of
   top-1 correctness (ties half). The same for top probability. A
   certainty cell the policy can use is one that moves with correctness
   inside the regime the row already tells it.
3. **Temperature (C3).** One scalar temperature per (head, horizon,
   regime), and a global one, fitted on Phase 1e's VALIDATION worlds
   (never the tuning half, never training) by grid search on the summed
   NLL; then the tuning-half ECE at T = 1, at the global T and at the
   regime T. A per-regime temperature is adopted for Phase 2's certainty
   cells only if regimes differ (P32).
4. **B30 against B10 (the Professor's point).** Top-1 is bounded by
   intrinsic unpredictability (the privileged previous act reads 0.724),
   so the log-loss gain at width (1.090 → 1.042) may be sharper
   calibration rather than more knowledge. If B30's entropy tracks
   correctness no better than B10's, the width buys what a temperature
   buys for free.

## 2. Instrument

`calib_act.py` (this arc), importing the act arc's `data_act`,
`train_act` (loader and forward) and `read_act` (worlds, row states,
tuning-half refusal). Heads: `minifriend-act-2026-11-03/results-raw/heads/{B10,B30}-s{1,2,3}/head-best.pt`
as committed (sha256 in each `done.json`). Horizons y0 and y10 as
defined there. The state is carried across CHUNK = 500 ticks from zero
at the world's start, as in every act read; no burn-in.

Definitions.

- **Regime** = the friend row's state at the tick (`data_act.row_state`):
  seen (present), heard (not present, any message / want / answers-me
  cell live), silent (58 zeros). "all" pools them.
- **Top probability** = max of the 11-way softmax. Bins
  [0, .2), [.2, .3), …, [.8, .9), [.9, 1] (the floor is 1/11).
- **Normalised entropy** = −Σ p log p / log 11; 0 for a one-hot, 1 for
  the uniform. Bins of width 0.1; the AUROC's histogram has 400 bins.
- **ECE** = Σ_bins (n_b / N) · |mean confidence_b − accuracy_b| on the
  top label. Reported at the three temperings; temperature leaves the
  argmax, hence top-1, unchanged.
- **AUROC** of a score for correctness = P(score of a correct tick >
  score of an incorrect tick) + ½ P(tie), from the 400-bin histograms.
  Scores: 1 − entropy, and top probability. Both at T = 1 only.
- **Temperature fit**: T on the grid 0.50 … 3.00 step 0.01 minimising
  Σ NLL of y under softmax(log p / T) over the validation worlds'
  covered-friend pairs, every 10th tick after the forward (`FIT_STRIDE
  10`; the GRU runs every tick, the fit thins the outputs). A regime
  under the floor (§3) takes the global T.

## 3. Data, cells and floors

- **Reliability and AUROC: the needy TUNING half, covered friends**, as
  in the act arc's R-A (180 worlds; 9,864,000 y0 samples per head, of
  which seen 5,153,794, heard 4,677,151, silent 33,055; shares 0.5225 /
  0.4742 / 0.0034). Every world passes `needy_read.refuse_unless` for
  the tuning half. The confirming half is not touched.
- **Temperature fit: Phase 1e's VALIDATION split**, 52 worlds (L / W /
  G / P1–P5 / TN1–5 / TE1–5), covered-friend pairs only (a TN / TE
  world's scripted seat is dropped as a friend), disjoint from training
  and from the lived evaluation worlds (guard c7). About 2M thinned
  samples per head and horizon.
- **Registered cells**: B10 and B30 × y0 × {seen, heard}. Floor:
  10,000 samples (a count, not a share; Professor's sharpening 3) — a
  registered cell under it is UNDECIDABLE, reported, not scored. Both
  are 460× over it on the record (guard c5 prints the shares before any
  read).
- **Reported cells** (no prediction rests on them): silent, all, every
  y10 cell, and the per-head bins. A bin under 1,000 samples is printed
  thin.
- **Memoryless baseline over the full row** (Professor's sharpening 2):
  not in this read — it is a trained head (the row-only act head), and
  her ruling places it as a Phase 2 side read. Stated here so its
  absence is a claim.

## 4. What this arc does not do

No collection; no training; no change to any head; no read of the
confirming half; no touch of the needs head NF1e-h24+p (its grave
channel's calibration is F-073's D5: ECE 0.0018 on covered friends). It
does not choose the act head (B10 is chosen, F-074) and cannot reopen
the budget (closed by P27); it can only register or not register the
B20 question in Phase 2 (§6). It sets no bar for the policy: calibration
is for legibility, threshold consumers and portability across a retrain,
not a gate for RL (the Professor's words, agreed).

## 5. Reads

- **C3a** `calib_act.py fit --out reads/temperature.json --md` — the
  validation fit: T per (head, horizon, regime) and global; NLL at T = 1
  and at the fit; counts. Runs first. About 5 minutes.
- **C1 / C2 / C3b** `calib_act.py reliability --out reads/reliability.json --md`
  — the tuning half: per head, horizon and regime, n, top-1, log-loss,
  mean top-prob, mean entropy, ECE at the three temperings, both
  AUROCs, the reliability bins and the entropy bins; seed mean ± SD in
  `summary`. Reads `reads/temperature.json`. About 10 minutes.
- **Score** `calib_act.py score --out reads/score.json --md` — P29–P32,
  the UNDECIDABLE list, the tempering rule's outcome per head, the B20
  consequence.

Cross-checks the reader carries: each cell's top-1 and log-loss at T = 1
must equal the act arc's `reads/accuracy.json` for the same (head,
horizon, regime) cell (the gate compares); the regimes' counts sum to
all.

## 6. Registered predictions (this thread's; declared before any number) and decision rules

- **P29 (confidence tracks regime).** B10's mean top probability on y0
  is at least 0.10 higher in sight than heard (seed means). Source of
  the bar: this thread's; the two regimes' top-1 differ by 0.21 and
  their log-loss by 0.67, so a head whose confidence did not follow by
  a tenth would be reporting confidence it does not have.
- **P30 (certainty tracks correctness within a regime).** B10's AUROC
  of (1 − entropy) for y0 correctness in sight is at least 0.70. Source:
  this thread's; 0.5 is no information, 0.70 is the point at which a
  consumer that trusted only the most certain half would be right
  materially more often than one that did not look.
- **P31 (the width gain is calibration, not discrimination).** On y0,
  in sight AND heard, B30's AUROC of (1 − entropy) exceeds B10's by less
  than 0.02 (seed means). Source: this thread's, the Professor's
  hypothesis made scorable; 0.02 is the seed-spread scale of these
  AUROCs expected at these counts.
- **P32 (miscalibration is regime-dependent).** B10's fitted y0
  temperatures differ between seen and heard by at least 0.10 (mean of
  the per-seed |T_seen − T_heard|). Source: this thread's; D5's regime
  dependence in the needs head was a factor of 2 against 1.4, and 0.10
  on a temperature is the smallest difference a policy input would
  notice.

Unscored expectations, reported: ECE at T = 1 under 0.05 in sight and
larger heard; the heard temperature above 1 (over-confident out of
sight); y10 flatter than y0 in every regime with the lower AUROC; the
silent cell's bins mostly thin; top-prob's AUROC within 0.02 of
entropy's (they are nearly the same scalar on an 11-way softmax).

**Decision rules.**

- **Tempering for Phase 2's certainty cells.** P32 met: the per-regime
  temperatures as fitted (per head and seed, `fits` in
  `reads/temperature.json`) are frozen here and Phase 2 applies them
  before computing top-prob and entropy. P32 not met: the global
  temperature is frozen instead. Either way, a head whose adopted
  tempering RAISES the tuning-half ECE in a registered cell over T = 1
  gets T = 1 (the fit did not transfer; reported). Phase 2 declares the
  outcome verbatim and never refits.
- **The B20 question.** P31 met: B20 is not registered in Phase 2 (its
  log-loss gain is what a temperature supplies for free; B10 as
  declared). P31 not met: the B20 welfare prediction (policy welfare
  with B20 inputs exceeds B10's by a declared margin) is registered in
  the Phase 2 declaration if the block can afford the ablation, her
  call. No reading of this arc changes the chosen head.
- **The certainty cells.** P30 met: entropy and top probability are
  Phase 2's two certainty scalars and the declaration may call them so.
  P30 not met: both are still fed (the policy decides what they are
  worth), but the Phase 2 declaration does not call either a certainty
  measure; it declares the row's regime state as the only certainty
  the policy is known to have, and reports the AUROCs.
- **P29 not met**: the regime discount cannot come from the head's
  confidence; the Phase 2 declaration says so and relies on the row's
  seen / heard / silent cells for it. Reported either way.
- A FINDINGS entry if a result stands alone (P31's answer would — it is
  the one question about width the record cannot otherwise settle);
  otherwise the read is a Phase 2 input, cited from this arc.

## 7. Instrument and guards (`test_calib.py`; each red via `scripts/mutate.sh --expect` on the committed files before any read; reds recorded here in the next commit)

- **c1** — entropy_norm: one-hot 0, uniform 1; bin_index lands the
  declared edges, the last bin closed.
- **c2** — temper: T = 1 identity, T = 2 flattens every row, T = 0.5
  sharpens, a per-row T applies per row; ece_from_bins equals a
  two-bin hand sum; an empty cell has no ECE.
- **c3** — auroc_from_hist: perfect separation 1, reversed 0, identical
  0.5, a hand case with ties, no positives → None.
- **c4** — fit_temperature recovers a known sharpening (labels drawn
  from q, p = temper(q, 0.5) fits T = 2.00 ± 0.06; p = q fits
  1.00 ± 0.06); nll_grid at T = 1 equals the hand NLL.
- **c5** — the cell-share guard (sharpening 4): prints every registered
  cell's count and share from the act arc's `reads/accuracy.json`
  before any read and fails if one is under the floor; the registered
  set is exactly B10 / B30 × seen / heard at y0.
- **c6** — reader smoke on one tuning world with B10-s1: regimes
  partition all; all = ticks × covered pairs; the cell's log-loss and
  top-1 equal `read_act.metrics_hand` on the same arrays (to 1e-6,
  float32 against float64 sums); at T = 1 the three temperings agree;
  the bins hold every tick.
- **c7** — the temperature fit's worlds are exactly Phase 1e's
  validation split (52), disjoint from training and from the lived
  evaluation worlds; covered_pairs drops the scripted friend (a TN
  world gives 4 × 3 = 12 pairs).

Predicted reds (the FIRST assertion each mutant reaches), cycles in the
next commit:

| guard | mutation | predicted first failure |
|---|---|---|
| c1 | `np.log(D.N_ACTS)` → `np.log(D.N_ACTS + 1)` in entropy_norm | "uniform entropy … expected 1" |
| c2 | `/ T` → `* T` in temper (the T = 1 identity short-circuits, so the first assertion the mutant reaches is the flattening one) | "T = 2 must raise every row's entropy" |
| c3 | `0.5 * neg` → `1.0 * neg` in auroc_from_hist | "identical … expected 0.5" |
| c4 | `np.argmin` → `np.argmax` in fit_temperature | "sharpened by 0.5, fitted T 3.0, expected 2.00 ± 0.06" |
| c5 | `FLOOR_CELL = 10_000` → `10_000_000` | "registered cell B10/y0/seen holds 5,153,794 samples, under the floor 10,000,000" |
| c6 | `ok` → `1.0 - ok` in the top-1 count (`self.correct += int(ok.sum())` → `int((1 - ok).sum())`) | "top-1 … vs metrics_hand …" |
| c7 | `D.role_lists()[1]` → `D.role_lists()[0]` in fit_worlds | "fit_worlds is not the validation split (194 worlds against 52)" |

**Reds on record 2026-11-04** (`scripts/mutate.sh --expect`, sequential,
baseline == restored, 7 passed each): seven of seven RED CONFIRMED, each
at the predicted first assertion, with one prediction corrected before
its confirming cycle. **c4**: predicted "fitted T 3.0" for argmin →
argmax; the mutant reached the predicted assertion but with T 0.5 — the
validation NLL of a sharpened distribution is largest at the sharp end
of the grid, not the flat end; mutate.sh exited 7 (wrong reason) on the
first cycle, the prediction was corrected to "fitted T 0.5, expected
2.00" and the cycle re-run RED CONFIRMED. Process note: the first cycles
of c2 / c3 / c4 / c7 exited 5 (no-op) because the replacement strings
carried regex escapes the plain-string helper does not read; re-run with
plain strings, no file changed. Logs in the session scratchpad
(`calib-reds*.log`).

## 8. Regeneration

```
### Read (the gate runs these; fresh outputs to its scratchpad, never over reads/)
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $C/calib_act.py fit         --out <scratch>/temperature.json --md --quiet   # about 5 min; Phase 1e validation worlds
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $C/calib_act.py reliability --out <scratch>/reliability.json --md --quiet   # about 10 min; reads reads/temperature.json
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $C/calib_act.py score       --out <scratch>/score.json       --md           # seconds; reads reads/{temperature,reliability}.json
```

`A` = `experiments/needy-set-2026-10-28`, `C` =
`experiments/minifriend-act-calib-2026-11-04`, absolute paths in use.
`run_calib.sh` runs the three in order into `reads/`.
