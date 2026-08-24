# E1 per-pair calibration curves — the pre-fog baseline (2026-08-23)

The prereg's E1 arm registered "per-pair calibration error logged **and
BANKED** (the care-coupling program's pre-fog baseline, design-inputs
§4c)". The logging shipped with the arm; this is the bank, owed since the
exp-006 closeout and report-only (G5).

**Instrument**: `calib_curves.py`, reducing `artifacts/ppo-E1-s{1,2}/
metrics.jsonl` — 6,510 logged updates per seed, 3,072 to 19,998,720 ticks,
each carrying a 5×5 MAE matrix and its 5×5 sample counts from
`train_ppo6.calibration`. Curves and both windows banked at
`results-raw/e1-calib-curves.json` with an F-028 header.

**Units**: needs are the global-state block's first six features,
normalised /100, so **0.010 MAE = one need point** on the 0–100 scale.

```
cd experiments/exp-006-character-gen && .venv/bin/python calib_curves.py
```

## Per-pair, late training (final third, count-weighted)

**ppo-E1-s1**

| observer \ target | Miso | Biscuit | Pumpkin | Kittybear | Clementine |
|---|---|---|---|---|---|
| Miso | 0.0364 | 0.0422 | 0.0422 | 0.0410 | 0.0442 |
| Biscuit | 0.0410 | 0.0376 | 0.0421 | 0.0410 | 0.0443 |
| Pumpkin | 0.0409 | 0.0422 | 0.0375 | 0.0410 | 0.0443 |
| Kittybear | 0.0412 | 0.0427 | 0.0422 | 0.0369 | 0.0443 |
| Clementine | 0.0409 | 0.0460 | 0.0424 | 0.0427 | 0.0397 |

**ppo-E1-s2**

| observer \ target | Miso | Biscuit | Pumpkin | Kittybear | Clementine |
|---|---|---|---|---|---|
| Miso | 0.0377 | 0.0433 | 0.0432 | 0.0423 | 0.0457 |
| Biscuit | 0.0430 | 0.0378 | 0.0433 | 0.0424 | 0.0459 |
| Pumpkin | 0.0429 | 0.0433 | 0.0378 | 0.0424 | 0.0459 |
| Kittybear | 0.0431 | 0.0436 | 0.0430 | 0.0376 | 0.0459 |
| Clementine | 0.0431 | 0.0472 | 0.0428 | 0.0445 | 0.0410 |

The two seeds agree pair-for-pair within 0.002, which is the first thing
worth knowing about a baseline that has to survive two generations.

## Three readings

**1. Coverage is complete — no ignored cat.** All 25 pairs carry
supervision in the final third of both runs. §4c's warning was that *a
wireheader can stay calibrated on cats it ignores*; the coverage screen it
implies passes, and the off-diagonal spread is 0.005 (s1) and 0.005 (s2),
so no pair is being quietly abandoned. Clementine is the hardest target for
every observer in both seeds (its column, 0.044–0.047) and the weakest
self-predictor (0.0397 / 0.0410) — a real per-seat asymmetry, small.

**2. Every observer reads itself better than it reads others**, by
0.0048 (s1) and 0.0055 (s2) on average — and per observer the gap is
0.0032–0.0063, positive in all ten observer-runs. Since this compares
predictions made on the *same fragments*, it is the strongest claim here:
the head uses observer-specific information rather than emitting one
roster-wide guess.

**3. The absolute level sits at constant-predictor scale, and the
early→late drop is confounded.** The curve falls 0.154 (0.5M ticks) →
0.060 (3.5M) → ~0.044 (6.5M) and then flattens, ending near 0.040. A
constant-predictor baseline on a played world — `c006a-L04s3`, 4,000
ticks, mean need 0.0587 — sits at MAD **0.0390** for "predict each seat's
own mean need" and **0.0425** for "predict the global per-need mean".
Late E1 is 0.037 on the diagonal and 0.042–0.044 off it. So most of the
training-long improvement plausibly tracks the *need distribution
collapsing* as the policy learns to satisfy needs (an idle, starved world
gives MAD 0.075, right where the early MAE sits), not the estimator
sharpening.

That third reading is a caveat about the measurement, not a verdict on the
arm. The baseline is a **proxy**: it is computed on the certification world
under the seated composition, while training ran on the family worlds under
a mixed-population draw whose need distribution moved as the policy
improved. Absolute comparisons across that gap are weak. The internal
comparisons — pair against pair, observer against itself, seed against seed
— are not, and they are what a pre-fog baseline is for.

## The exact fix, registered

Log a **constant-predictor MAE beside `calib_mae` on the same fragment**:
the mean absolute deviation of the fragment's own needs from their
per-(seat, need) mean. One line in `train_ppo6.calibration`, no new
machinery, and it makes every future estimator run interpret itself — the
skill measure becomes `calib_mae / baseline_mae` rather than a raw MAE
whose scale drifts with how well the policy is doing at its actual job.

Not done here: this bank reduces runs that are already complete, and
changing the trainer now would not retrofit them. It belongs to whichever
arm next carries an estimator head — which is the care-coupling program's
first training run, where the C-grounded/C-free comparison needs it.

## What this is for

The eventual C-grounded vs C-free comparison asks whether a mind that
predicts others' interiors cares differently. That comparison reads
per-pair calibration, never the average, and it needs a pre-fog number to
compare against. This is that number: **all 25 pairs supervised, self
0.037–0.038, others 0.042–0.044, seeds agreeing within 0.002, measured
under global vision on a 20×20 world where every need is observable.**

Whatever fog does to it, the comparison starts here.
