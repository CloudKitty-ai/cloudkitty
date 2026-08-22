# SC-005 re-baseline: the bugs-2.0 world's fresh numbers

Definition of done from bugs2-spec-input-2026-08-21.md, run against
main @ 6dd5666 (PR #282). Certification config for the new world:
`exp-006-character-gen/configs/phase1-cutover-bugs2.toml` (sha
`952224aa…`) — phase1-cutover.toml (D-003 lineage) plus exactly the
merged package: bug ttl 600 + roam_cell 4, greeble ttl 600 + dart,
play_relief_bug 28, pounce. Semantic diff verified against the
served cloudkitty.toml.

## Instrument continuity first (F-028 discipline)

Before any new number, the old ones were reproduced on the merged
binary — all three instrument paths check out byte-exact:

- kitty-eval scripted anchor on the pre-039 config: byte-identical
  to `results-raw/d003/anchor.txt` (30 seeds, every line).
- cert_harness6 policy path: family-11-r5 candidate/stress seed
  880001 reproduces its banked row to full float precision.
- playful anchor: the body-price correction's engine-native cell was
  a scratchpad one-off; it is now a committed instrument
  (`exp-006-character-gen/playful_anchor.py`, provenance-stamped per
  F-028) and reproduces the banked 79.72 exactly on the pre-039
  config.

The merged engine is behavior-preserving on pre-039 configs at
census scale — the flag-off inertness claim, confirmed on a third
and fourth instrument.

## Anchors, old world → bugs-2.0 world

| anchor | pre-039 | bugs-2.0 | Δ |
|---|---|---|---|
| scripted team welfare (30 seeds, eval band) | 0.9072 (min 0.9058) | 0.9077 (min 0.9063) | +0.0005 |
| thermostat parity (needs_driven at Biscuit) | 90.64 | 90.71 | +0.07 |
| playful anchor (THE CHARACTER at Biscuit, 5 seeds) | 79.72 | **79.31** | **−0.41** |

Worst mda 0, floors 0, welfare bounds 30/30 PASS on the new config.
Raw: `exp-006-character-gen/results-raw/anchor-bugs2.txt`,
`results-raw/playful-anchor-phase1-cutover{,-bugs2}.json`.

Readings: the world's welfare arithmetic is unchanged for
needs-driven minds — the package is economy, not difficulty. The
playful character reads 0.41 lower (spread ±0.35, 5 seeds): small,
direction consistent with shorter tethered chases changing the
play-scene texture the character lives in. It is an anchor, not a
gate; exp-006a's bar re-derivation starts from 79.31, and the
thermostat cap from 90.71, per the owner's scope ruling. Character
price on this world: 90.71 − 79.31 = **11.40** (was 10.92) — the
~11-point lifestyle price carries, slightly widened.

## Purrsonality zero-play baseline (re-banked)

Live census of the deployed phase-1 roster, deliberately taken
BEFORE the bugs-2.0 deploy so the before/after brackets only the
mechanics change: ticks 20,676–21,301, five seats, 1,593 events —
solo 266 · kitty 44 · **bug 0 · greeble 0**. The F-019 erosion
signature carries into the new generation. Register entry updated
(`policies/purrsonality.md`); raw:
`attn-cert-2026-08-14/results-raw/live-census-20676.json`. The
"after" is the post-deploy live census — the owner's reward-tuning
freeze lifts on those numbers.

## Tail benchmark and F-026

- family-11-r5: divergence note added to
  `tail-benchmarks/README.md` — the pinned world carries no 039
  keys, runs flag-off, and reproduces byte-equal; the benchmark
  detects what it always detected, but an r5 reading is no longer
  evidence about critter behavior on the served world.
- F-026: confound note added in FINDINGS.md — fog-era channel
  comparisons now span two world changes; the deafening ablation
  re-runs on the post-039/pre-fog world before any fog attribution.

## What this unblocks

Incumbent re-evaluation on `phase1-cutover-bugs2.toml`, then corpus
re-collection (two-cat far-spawn isolation families included), then
exp-006a numbers re-derivation and freeze. The deploy itself remains
owner-gated with Product; the live play census follows it.
