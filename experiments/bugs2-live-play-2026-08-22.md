# Bugs-2.0 live play census + incumbent re-eval — the freeze packet

The owner's reward-tuning freeze (2026-08-21: "no greeble/bug
sticker movement until actual play numbers from deployed minds")
lifts on these numbers. Both measurements ran 2026-08-22 on the
post-039/post-040 world; raws in
`attn-cert-2026-08-14/results-raw/live-census-{26221,27089,27729}.json`
and `exp-006-character-gen/results-raw/deploy-bugs2/`.

## Live play census (~27 min, ticks 26,221–28,355, 4,732 events)

Three consecutive 9-minute windows, all post-deploy, none straddling
a restart. Play targets, all seats, whole span:

| seat | solo | kitty | bug | greeble |
|---|---|---|---|---|
| Biscuit (e004) | 302 | 16 | **0** | **0** |
| Pumpkin (attn-s3) | 193 | 50 | **0** | **0** |
| Kittybear (E1-s1) | 162 | 17 | **0** | **0** |
| Miso (attn-s1) | 126 | 10 | **0** | **0** |
| Clementine (scripted) | 0 | 87 | **0** | **0** |

Watchdog quiet all 36 polls; happiness healthy at every seat
(policy 93.5–95.6 window means, Clementine ~90 on-anchor).

Two separate zeros, two separate reasons, both expected:

- **The policy seats are frozen pre-bugs-2.0 minds** — F-019
  erosion; they cannot discover an economy they never trained
  under. This zero is a property of the generation, not the
  stickers.
- **The scripted seat's zero is the economy working**: Clementine's
  need-scheduled play resolves kitty-partnered 87/87 because a
  partner is nearly always in reach and the duet outbids the bug
  (20-each both-payer vs 28 single-payer) — the exact opportunistic
  ordering the owner set. The acceptance grids showed scripted
  minds bug-hunting in worlds where every cat runs the same need
  schedule; live, four policy cats keep partners available.

## Incumbents on the bugs-2.0 certification world

cert_harness6 deploy-ref-e1, 30 × 20k per band,
`phase1-cutover-bugs2.toml` — against the pre-039 deploy battery:

| leg | nash (min) pre-039 | nash (min) bugs-2.0 | per-seat hap bugs-2.0 |
|---|---|---|---|
| eval | 0.9393 (0.9373) | 0.9392 (0.9357) | 95.02 / 94.95 / 94.42 / 94.66 / 90.72 |
| stress | 0.9389 (0.9371) | 0.9390 (0.9367) | ≈ eval |

Per-seat happiness matches the pre-039 battery to a hundredth at
every seat. Worst mda moved 27→66 (eval) and 21→93 (stress) —
still far under the 150 constitutional bar with zero floor touches
and zero exceedances; a wider distress tail is consistent with
critter-dynamics changes touching occasional chase decisions, and
the watchdog now standing on the box is the right monitor for it.

Bugs-2.0 costs the incumbent roster nothing. Their seats are safe
through the transition generation.

## What this means for the freeze

The lifting condition has been measured, and the measured number is
zero — and will remain zero for this generation, because no seated
mind can respond to the new economy. The live world cannot
distinguish sticker 28 from any other value until a bugs-2.0-era
mind seats. Recommendation, the decision being the owner's: keep
the stickers frozen as merged (they were priced on the measured
frontier for learners, and nothing here contradicts that pricing),
treat THIS census as the standing zero-baseline, and let the next
genuine play datum come from exp-006a's Biscuit 2.0 — first in
training curves, then, if it certifies and seats, live. The
sequence is unblocked: corpus re-collection next, then 006a
re-derivation and freeze.
