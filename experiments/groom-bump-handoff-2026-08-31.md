# Handoff: serving-world groom_cuddle_relief bump (TEMPORARY)
## (2026-08-31, Experiments → Product, owner-directed)

The owner directed this after the post-041 investigation
(`041-cuddle-investigation-2026-08-31.md`): Clementine's frozen e004
policy answers high cuddle with her trained groom-for-cuddle habit
(56% of high-cuddle ticks), but 041 repriced the groomer's relief to
0.5/tick — below her 0.7 rise — so the habit is a futile loop that
starves her other needs and trips the spec-040 watchdog
intermittently. The G6 soak cannot pass as gated while it runs.

## The change

`groom_cuddle_relief` on the SERVING config: **0.5 → 2.0**
(needflow-priced lean; 1.5 is the conservative alternative —
pricing table in `cuddle-economy-model/RESULTS.md` §serving bump:
welfare-benign at both, 95.36 → 95.83 modeled). Config-only, its
own small deploy, owner's restart.

## ⚠ TEMPORARY — reverted at the next training round

The canonical 041 value (0.5, the specialist split) remains the
design truth: specs, lab worlds, step-2 validation bands, and every
collection config keep 0.5. The bump is a serving-world
accommodation for FROZEN incumbents whose habits predate 041 —
**it is reverted when the Gen 1 retrain seats minds trained under
the canonical economy** (fog timeline step 7 seating). Please mark
the config comment accordingly (e.g. "temporary pre-Gen-1
accommodation, revert at reseating — see
groom-bump-handoff-2026-08-31.md") so the revert cannot be missed.

## Sequencing

1. Goes out as its own config deploy on the owner's word — after
   which the 041 soak clock RESTARTS on the remediated config (the
   alarms it fixes would otherwise fail the soak).
2. The post-041 census then reads 041+bump against the pre-041
   baseline — note that in the census record; the attribution is
   acceptable (the bump is config-only and priced).
3. No interaction with the contagion work: merge-inert anytime
   stands; the flip still waits for the (restarted) soak to pass.

## Acceptance

- Watchdog quiet over a G6-style soak window (no cuddle alarms;
  entries list empty or transient).
- Clementine's cuddle off the saturation cycle (spot checks: level
  not pinned ≥90; the "wanting cuddle for a while" caption not
  sustained).
- No new excursions elsewhere (the pricing predicts mild
  improvements across needs).

Experiments will re-run the census instruments post-deploy and bank
deltas vs `pre041-census-2026-08-28.md`.
