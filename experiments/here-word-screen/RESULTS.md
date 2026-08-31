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
| A1b | 2 | 7.607 | .3453 | .5343 | .5600 | .4755 | .6906 |
| A2 | 4 | 5.561 | .0027 | .0000 | .0000 | .0033 | .0039 |
| A3 | 16 | 2.363 | .0000 | .0005 | .0007 | .0014 | .0043 |

(A1b is the owner-routed 2026-08-31 addendum — declared before
collection, same paired seeds, same recipe; see the declaration's
addendum section.)

Predicted emission per 1k val rows vs the scripted source (the F-022
comparison shape):

| arm | source here/1k | clone here/1k |
|---|---|---|
| A1 | 82.4 (16.0/24.5/22.9/19.1) | 84.5 (15.4/25.7/24.1/19.3) — tracks per kind |
| A1b | 76.9 | 73.6 — RATE tracks, placement degraded (use ~.5) |
| A2 | 55.9 | 0.3 |
| A3 | 23.5 | 0.3 |

A1's clone speaks the register at source rate and in source
proportions. A1b's speaks at rate but only half in place. A2's and
A3's clones are functionally mute — three orders of magnitude under
their sources — despite A2's corpus carrying 5.6% here-words, over a
full percentage point of density for each of the four kinds.

## Predictions scored (pre-registered §7)

1. **Gate zero — CONFIRMED** (in-tree test + corpus scale: actions
   byte-identical at all 25 paired seeds, every message diff
   Silent→Here\*, non-here cooldown columns clean).
2. **Monotone realized share — CONFIRMED** (8.18 / 5.56 / 2.36% at
   periods 1/4/16; ladder compressed by per-kind cooldowns, A1:A3 ≈
   3.5× not 16×).
3. **Threshold, not gradient — half confirmed, twice revised.** The
   LOCATION was wrong: mute persists up to 5.6% corpus share, not
   ~1%. And with A1b the SHAPE resolves finer: not a pure step but a
   steep transition — mute at ≤ 5.6%, half-fluent at 7.6% (use ~.5),
   fluent at 8.2% — the entire rise packed into ~2.6 points of
   share. The F-022 anchors (0.2% → mute; purr-rich ≈10% → fluent)
   never bracketed the middle; this screen did.
4. **act@1 unchanged — CONFIRMED**: .7986–.8037 across all five arms
   (A1b .8009). The vocabulary costs no action learning at any
   density.
5. **Welfare null — CONFIRMED, stronger than null**: `reward.npy`
   byte-identical across arms at all 25 seeds (gate zero makes the
   charge exactly zero; F-026 report-only satisfied).

## Reading (revised with A1b, 2026-08-31)

- **A workable density exists and it is period 1.** 8.2% corpus share
  teaches all four kinds with zero action-fidelity and zero welfare
  cost.
- **The transition is steep, not a step** (A1b's revision of the
  first write-up's "binary dial"): period 2's 7.61% yields PARTIAL
  competence — emission rate fluent (73.6/1k vs source 76.9), but
  placement roughly half-right (use ~.5, msg@1|here .69). Mute below
  ~6%, half-fluent at 7.6%, fluent at 8.2%: the whole transition
  fits inside ~2.6 points of corpus share. Striking within it: a
  0.57-point share difference (A1b→A1) buys +.14–.24 of use — which
  hints the driver may not be raw share alone (period 1's every-
  legal-tick regularity is also the most predictable context), one
  clone per arm, so read the shape, not the decimals.
- **Period 4 and below buy nothing.** Combined with the
  cooldown-compressed ladder (ceiling ~8%), the usable settings are
  period 1 (fluent) and period 2 (degraded, no compensating benefit
  — the corpus is barely smaller). Period 1 dominates.
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

## Addendum 2 — the training-budget extension (2026-08-31)

Owner-routed, declared with a decision rule before running: fresh
60-epoch / patience-10 runs on A1, A1b, A2 (same corpora, same
trainer seed; patience loosened so a plateau-then-late-transition
could not be censored). No run early-stopped; every clone took all
60 epochs.

| arm | use @20ep | use @60ep | msg@1\|here @20ep | @60ep | act@1 @20ep | @60ep |
|---|---|---|---|---|---|---|
| A1 | .58–.80 | .60–.81 | .875 | .886 | .7991 | .8188 |
| A1b | .35–.56 | .39–.54 | .691 | .705 | .8009 | .8159 |
| A2 | ≤ .0033 | .000–.027 | .0039 | .0271 | .8010 | .8172 |

**Per the pre-declared rule: the recipe stands.** Tripling the
budget moved the vocabulary numbers by noise-level amounts — A1
+~.01, A1b mixed ±.04, A2 creeping from mute to still-mute (its
best kind reaches .027; here_critter stays exactly 0). The
transition's location is **density-shaped, not budget-shaped**:
20 epochs was never what kept A2 mute, and no plateau-then-jump
appeared anywhere in 60 epochs of history.

**What the budget DOES buy is action fidelity**: act@1 rose
~+1.6–2.0 points on every arm (.799–.801 → .816–.819) and val loss
was still improving at 60 in A1's case. So the fog Gen 1 BC
question splits cleanly: the vocabulary needs period-1 density and
is indifferent to budget; action quality benefits from a longer
cycle at ~3× cost (~40–120 s/epoch on a 1M-row corpus here; the
3.9M-row anchor scales ×4). Whether +2 act@1 is worth 3× training
time on five seats is an owner call at the fog prereg, not a screen
matter.
