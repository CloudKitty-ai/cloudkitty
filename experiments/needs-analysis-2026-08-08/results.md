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

## The policy-side counterpart (added 2026-08-08, owner's question)

The scripted analysis missed the constituency that matters most: the
live world's future is agent cats, and the current generation keeps
needs in a **far more compressed band**. Instrument:
`experiments/tools/needs-census/` (replay via `run_one_with`, deployed
artifact `e003-m0-g998-s3`, current served 20×20, seeds 820001–820030
× 20k, both compositions; raw histograms in `needs-allpolicy.json` /
`needs-deployed.json`).

**All-policy (4 agent cats)** — per-need quantiles p50 / p90 / p99:
eat 7/17/29, drink 4/11/17, sleep 2/7/13, play 4/10/15, cuddle
2/7/16, bath 4/10/22. Initiation medians 1–13. Occupancy at 40 is
0.003–0.16% per need. **Expected traffic at threshold 40: ~0.6
meows/1k ticks per cat ≈ one meow per cat per ~23 live minutes** — a
channel that exists but is never seen. At 30: ~2.9/1k ≈ one per ~5.7
min per cat (one somewhere in the world every ~90 s). At 25: ~6.4/1k.

**Deployed 2+2**: policy cats similar (slightly lower); scripted
neighbors in policy company match the dataset-v3 picture (playful
ceiling ~55–56, needs_driven initiation 12–23).

## Recommendation (REVISED 2026-08-08 after the policy-side data)

- **Announce threshold 30, global** — the value that serves both
  populations: *above* needs_driven's initiation medians (13–23) and
  eat median (23), so a scripted meow at 30 still means "past my usual
  acting point"; *above the policy cats' p99* for five of six needs
  (13–29), so an agent meow at 30 is a top-1% state — highly
  informative; *below* playful's ~55 ceiling with a 30→55 window ≈
  **62 ticks**, double the walk time; and it keeps the 4-agent live
  world audibly alive (~3 meows/1k per cat) where 40 mutes it. The
  original 40 was correct for scripted distributions alone; the
  compressed policy band moves the sweet spot down.
- **Hysteresis 5** (legal ≥ 30, stays legal until < 25) — still sized
  by the wet-fur bath spikes.
- **Cooldown = `recent_window_ticks` (10), no new dial** — unchanged.
- **The threshold must be a config dial, not a constant** (spec
  requirement): grounded legality reads need-vs-dial at mask time, so
  retuning it later is a config rollout, **not a generation wall**.
  Register 30 for exp-004; the product can move it with evidence.
- **Responder gate**: unchanged, ~15–20 (needs_driven cuddle-initiation
  region; 12% occupancy at 20 vs 2.5% at 30).
- **WantSleep**: same structure both compositions (playful 46 emits/1k
  at 30; policy 0.02) — in the batch per the owner's call.
- Known cost of 30 vs 40: needs_driven eat-meows at ~9/1k (initiation
  p90 is 34, so a third of their normal top-band overlaps) and playful
  legal ~44% of ticks on four needs — chattier demonstrations, more
  channel rows in dataset v4, which is also the point.
