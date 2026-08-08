# Needs data for the meow announce threshold — the grounding decision

**2026-08-08.** Dataset v3's 1.9M scripted kitty-tick rows (obs[0:6] =
needs, 60 rollouts, v4 family), split by expert behavior: 1.49M
needs_driven rows, 0.41M playful. Scripts here (`needs_analysis.py`
occupancy + dynamics + raw decision-conditioning; `needs_analysis2.py`
initiation-conditioned decisions — relief actions span ticks, so raw
decision rows conflate initiation with continuation; run-start
filtering is the honest version). Data lives in the gitignored
`exp-003-water-schema/raw/bc-v3/`; the numbers below are the record.

## The headline

**`urgent_need_threshold = 75` is above the lived range of every
scripted cat** — occupancy at 75 is ≤ 0.02% for both behaviors, all six
needs. Grounding inherited from it = a channel that is never legal.
The decision space is the 20–60 band.

## Occupancy (share of kitty-ticks with need ≥ T, %)

| need | nd@30 | nd@40 | nd@50 | nd@60 | pf@30 | pf@40 | pf@50 | pf@60 |
|---|---|---|---|---|---|---|---|---|
| eat | 3.46 | 0.59 | 0.13 | 0.03 | 46.4 | 28.2 | 12.6 | 1.20 |
| drink | 1.79 | 0.28 | 0.06 | 0.01 | 41.4 | 25.3 | 11.5 | 1.26 |
| sleep | 0.70 | 0.18 | 0.04 | 0.00 | 44.2 | 26.5 | 10.3 | 0.28 |
| play | 0.31 | 0.01 | 0.00 | 0.00 | 0.03 | 0.00 | 0.00 | 0.00 |
| cuddle | 2.54 | 0.50 | 0.09 | 0.01 | 21.5 | 12.4 | 5.84 | 1.43 |
| bath | 0.41 | 0.14 | 0.06 | 0.01 | 43.3 | 25.1 | 8.11 | 0.17 |

## Where cats initiate self-relief (need value at action start, ×100)

| action | needs_driven med / p90 | playful med / p90 |
|---|---|---|
| Eat | 23.0 / 33.0 | 56.8 / 61.6 |
| Drink | 21.2 / 29.0 | 56.8 / 62.4 |
| SleepSolo | 17.0 / 23.7 | 56.2 / 59.1 |
| GroomSelf (bath) | 13.5 / 22.3 | **55.3 / 60.4** |
| RestWith (cuddle) | 15.2 / 27.7 | 11.4 / 51.4 |

`needs_driven` self-serves everything by ~25. `playful` defers
everything (except play) to **~55** — its neglect zone is where an
announcement is informative: real need, unattended, help has time to
matter.

## Dynamics at candidate thresholds (episodes/1k ticks, mean dwell, emits/1k under cooldown 10)

needs_driven totals across all kinds: **T30 ≈ 13.4 emits/1k, T40 ≈
2.6, T50 ≈ 0.7** — near-silent at 40, firing only when genuinely
stuck. playful: **T30 ≈ 212/1k (always-on), T40 ≈ 130/1k (~28–31 per
kind = one per ~33 ticks), T50 ≈ 59/1k**. The one flappy signal: bath
under the wet-fur charge — needs_driven dwells above 40 are **2–3
ticks** (F-016's spike); everything playful dwells 40–70 ticks.

## Recommendation (PROPOSED 2026-08-08 — owner confirmation pending)

- **Announce threshold 40, global**: above needs_driven's entire
  self-serve band (p90 ≤ 33), below playful's ~55 ceiling. The
  40→55 window ≈ 15 need-points ≈ **37 ticks** at 0.4/tick — longer
  than a cross-board walk (~10–20 ticks), so a responder can arrive
  before self-relief. At 50 the window (~12 ticks) drops below walk
  time; at 30 the playful signal is always-on and needs_driven noise
  rises 5×.
- **Hysteresis 5** (legal ≥ 40, stays legal until < 35): sized by the
  2–3-tick wet-fur bath spikes; nothing else flaps.
- **Cooldown = `recent_window_ticks` (10), no new dial**: dwells at 40
  span multiple cooldown periods, so a persisting need re-announces as
  its digest entry fades — the honest persistent signal.
- **Responder gate (spec consequence)**: the demonstrated chain is
  playful-announces → needs_driven-responds (needs_driven bath emits at
  40 ≈ 0.4/1k). The responder's "cuddle is real" condition must sit at
  ~15–20 (their natural cuddle-initiation region, 12% occupancy at 20);
  at 30 (2.5% occupancy) the answered-chain rate collapses.
- **WantSleep behaves identically** (playful 29 emits/1k at 40;
  needs_driven 0.2) — in the batch per the owner's call, demonstrated
  by the same structure.
