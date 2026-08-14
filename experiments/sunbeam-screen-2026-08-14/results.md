# Spec-031 dial screen: {6, 7, 8} indistinguishable — pin the owner's 7

**2026-08-14.** The screen the design doc registered
(`../sunbeam-warmth-2026-08-13/design-input.md`): shared-warmth rule
live (PR #216), `sleep_relief_sunbeam` ∈ {6, 7, 8}, all four seats
forced scripted (`needs_driven` via control override — the served
seats hold frozen policies, which cannot respond to a dial), paired
seeds 1–10 × 20k ticks. Instrument `sunbeam_screen.py`; raw rows in
`results-raw/screen.json`.

## Result: the dial does not move scripted welfare

| dial | happiness | sleep share | naps (len) | sleep-on-beam | cosleep∣sleep | warmth conducted |
|---|---|---|---|---|---|---|
| 6 | 90.640 | 0.0855 | 13,674 (5.0) | 55.3% | 7.6% | 0.39% |
| 7 | 90.627 | 0.0853 | 13,654 (5.0) | 55.2% | 7.5% | 0.36% |
| 8 | 90.631 | 0.0853 | 13,654 (5.0) | 55.2% | 7.5% | 0.36% |

Happiness spans 0.013 across the three dials with inconsistent sign
(6 > 8 > 7); per-seed spread is ±0.1. At 10-seed power the dials are
welfare-indistinguishable. Mechanism: scripted cats nap short (5.0
ticks) and mostly solo — cosleep is only 7.5% of their sleep — so the
conduction rule fires on ~0.4% of sleep ticks, and the per-tick rate
difference washes out entirely.

Policy-world companion read (valence probe, same day): the attention
seeds cosleep 87% of their sleep but place piles on beams at ~chance
(cosleep-on-beam 0.9–1.7% of sleep vs beams ≈ 1% of tiles; conducted
0.2–0.6%). Nobody alive today seeks the bonus — as the design doc
predicted, the rule's payoff belongs to the next trained generation.

## Verdict

**Pin 7** — the owner's opening preference, now with a measured cost
of zero on the scripted side, the softer nap-shortening when the next
generation does learn beam-seeking, and a slightly longer beam nap
than today's 8 for whoever wanders on. The re-pin moves the config
stamp and rides the pre-freeze re-baseline per the design doc (no
live-world change now; Product owns the config edit when the
generation batch lands). F-016's caveat stands recorded: a scripted
floor is not a proxy for policy behavior on this dial in either
direction — the real test is the trained generation's census.
