# Here-word density screen — Half A results (2026-08-31)

Run as pre-registered (`../here-word-density-screen.md` + the FR-006
amendment; declaration + acceptance in `collection-2026-08-31.md`).
Engine main `2f5fb6c` (spec 043 merged); collection band
1,060,001–25 paired across arms; `train_clone6.py` verbatim defaults,
EntityPolicyV4 78,434 params; readouts `readout_screen.py` on the
held-out val seeds (r03/r13/r23, same three worlds in every arm),
predictions by the trainer's own masked-argmax definition. Raw:
`results-raw/readout.json`.

## The headline: the cliff is real and it sits HIGH

Opportunity-use (of val rows where kind K was legal and the source
spoke no want-word, the fraction the clone predicts K):

| arm | period | here% of corpus | food | water | critter | sunbeam | msg@1 on here-rows |
|---|---|---|---|---|---|---|---|
| A0 | off | 0.000 | .0000 | .0000 | .0000 | .0000 | — (0 rows) |
| A1 | 1 | 8.176 | **.5814** | **.7516** | **.8028** | **.6806** | **.8748** |
| A2 | 4 | 5.561 | .0027 | .0000 | .0000 | .0033 | .0039 |
| A3 | 16 | 2.363 | .0000 | .0005 | .0007 | .0014 | .0043 |

Predicted emission per 1k val rows vs the scripted source (the F-022
comparison shape):

| arm | source here/1k | clone here/1k |
|---|---|---|
| A1 | 82.4 (16.0/24.5/22.9/19.1) | 84.5 (15.4/25.7/24.1/19.3) — tracks per kind |
| A2 | 55.9 | 0.3 |
| A3 | 23.5 | 0.3 |

A1's clone speaks the register at source rate and in source
proportions. A2's and A3's clones are functionally mute in it — three
orders of magnitude under their sources — despite A2's corpus carrying
5.6% here-words, over a full percentage point of density for each of
the four kinds.

## Predictions scored (pre-registered §7)

1. **Gate zero — CONFIRMED** (in-tree test + corpus scale: actions
   byte-identical at all 25 paired seeds, every message diff
   Silent→Here\*, non-here cooldown columns clean).
2. **Monotone realized share — CONFIRMED** (8.18 / 5.56 / 2.36% at
   periods 1/4/16; ladder compressed by per-kind cooldowns, A1:A3 ≈
   3.5× not 16×).
3. **Threshold, not gradient — the SHAPE is confirmed, the LOCATION
   was wrong.** Learning is a cliff: near-total on one side (.58–.80
   use), near-zero on the other (≤.0033) with nothing in between. But
   the cliff sits **between 5.6% and 8.2% corpus share**, not near the
   hypothesized ~1%. The F-022 anchor points (0.2% → mute; purr-rich
   ≈10% → fluent) never bracketed the middle; this screen did, and the
   middle belongs to the mute side.
4. **act@1 unchanged — CONFIRMED**: .7986 / .7991 / .8010 / .8037
   (A0→A3). The vocabulary costs no action learning at any density.
5. **Welfare null — CONFIRMED, stronger than null**: `reward.npy`
   byte-identical across arms at all 25 seeds (gate zero makes the
   charge exactly zero; F-026 report-only satisfied).

## Reading

- **A workable density exists and it is period 1.** 8.2% corpus share
  teaches all four kinds with zero action-fidelity and zero welfare
  cost. The knob's aggressive end is the only end that works under
  this recipe.
- **The dial's middle is dead.** Period 4 supplies 5.6% and buys
  nothing. Combined with the cooldown-compressed ladder (the ceiling
  is only ~8%), the usable range of `announce_here` for corpus
  seeding is effectively binary: 1 or off.
- **The Here\*-teacher collapse (plan §8) is now supported**: the
  existing scripted behaviors with `announce_here = 1` produce a
  corpus a V4 clone learns the register from. The parked teacher item
  can likely be scoped away — pending the owner's read.
- **exp-003's failure was never near the boundary.** At 0.2% it sat
  40× under a cliff at ~6–8%, not 5× under one at 1%.

## Disclosed limits

- **Fixed training budget**: verbatim recipe = 20 epochs, patience 3.
  A2's val loss was still improving at epoch 19–20, so "mute at 5.6%"
  is a claim about this recipe's budget, not a learnability
  asymptote. An epoch-extension probe on A2 would separate
  optimization speed from asymptote — not run (would deviate from the
  registered recipe); flagged as the natural follow-up.
- **Offline operationalization**: emission = masked argmax on held-out
  states, not live rollouts. Live emission (the exp-004 104.66/1k was
  the same offline shape, but certification measured live) needs the
  lab binding — `binding_continuity.py` gate first.
- Opportunity counts differ across arms by construction (here-kind
  cooldowns shrink legality when the knob speaks often); the
  conditioning handles it, but the denominators are not comparable
  across arms.
- One collection deviation on record: drop rate 0.138% vs the v6
  anchor's ≈0.06% (chase-dominated; consistent with 042's partner
  pick; identical across arms so no contrast is touched).

## What this changes downstream

- Fog corpus collection parameter: `announce_here = 1` (not a swept
  dial).
- The fog prereg's vocabulary arms can assume a seedable register at
  period 1 and must not assume one at period ≥ 4.
- Half B (does density change USE) stays post-fog per F-026, unchanged.
