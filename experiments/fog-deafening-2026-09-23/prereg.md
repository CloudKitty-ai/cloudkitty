# Fog-era deafening ablation — declaration

Declared 2026-09-23, before collection. Owner's word, Experiments
session, 2026-09-23: "Run the fog-era deafening ablation."

**Question** (registered by F-026, "Re-verify when: the fog generation
(the entire point)"): under fog, does hearing pay welfare? F-026
measured the pre-fog null: under global vision, hearer-side deafening
moved team happiness by at most 0.015 against a ±0.15 parity band, and
its implication bars "communication sustains welfare" from client-facing
copy until a fog-era ablation says otherwise. This read is that
ablation.

## Instrument (F-009 dimensions)

- **Composition**: `gen1-A`, the served five-network roster, on
  `experiments/fog-gen1-cert/anchor-b3.toml` — the deployment
  composition (F-012) on the served world. Served clock (the clock
  input pinned to 0, the engine's deploy seam), greedy on both heads.
- **Horizon**: 20,000 ticks per seed. **Seeds**: 30, band
  900101–900130 (claimed in `SEED-BANDS.md`, this commit). The same 30
  seeds run in every arm by design: the primary quantity is the paired
  per-seed delta (the here-word screen's precedent, band 1060001+).
- **Harness**: `experiments/fog-gen1-cert/cert_harness_fog.py` `--deaf`
  at 207f8c9. Hearer-side only; emission stays legal, so the deafened
  world settles into its own equilibrium (F-026's design). Per kitty
  row the mask zeroes the deafened kinds' (recency, rate) pairs, their
  want intensities, and the here-derived answers-me bits, then erases
  whole heard-only rows with no surviving message float — a deaf hearer
  would have had a Silent row, and a heard row's position is itself the
  call's information. Not masked: the self message block (self-speech,
  not hearing) and the element memory (sight-only,
  `world.rs::refresh_memories`). The mask is guarded by
  `test_deafen_mask.py` against an independent reference; three mutate
  reds at 207f8c9 (message-offset shift, dropped heard-row erasure,
  wrong here-kind set), each red for the predicted reason.
- **Arms**: `intact`; `want`-deaf (the six want kinds); `here`-deaf
  (the four Here kinds plus all answers-me bits); `all`-deaf (all 15
  head kinds, every heard row erased).

## Measures

Per seed per arm: team happiness (mean of per-seat means), nash_state,
low_share, floor_touches, dist_ticks (any-flag distress ticks per seat,
added at 207f8c9 for F-026's registered whisper), max_distress_age,
message-head counts. Primary: the paired per-seed team-happiness delta
(arm − intact), mean over the 30 disjoint worlds (per-world means,
F-004).

## Predictions

1. **All-deaf costs happiness.** Paired mean team-happiness delta
   < −0.15 — F-026's parity band reused as the line. Under global
   vision the same deafening measured −0.011; the fog thesis says the
   channel is now load-bearing (F-048: want words move listeners;
   F-049: asks draw here-word answers).
2. **The family arms sit between.** Neither want-deaf nor here-deaf
   lands below all-deaf on the paired mean, and neither lands above
   intact by more than the parity band.
3. **The whisper** (F-026, registered, not a claim): distress ticks
   rise under all-deaf. A ratio ≥ 2 over intact reproduces the pre-fog
   doubling at 6× the tick volume; the ratio is reported whatever it
   is.

## Decision rules

- P1 holds → the client-copy claim "communication sustains welfare" is
  claimable for the fog generation, and the result enters FINDINGS as a
  new entry (F-026 stays active; its scope is global vision).
- The all-deaf delta lands inside ±0.15 → the claim stays barred:
  F-026's implication extends to the fog generation, and the copy keeps
  the behavioral phrasing (F-048/F-049).
- Anything one-sided or ambiguous (a family arm outside the bracket, a
  distress move without a happiness move) → reported with options and a
  recommendation; the fork is the owner's.

## Bounds

Frozen minds: this measures hearing's value to cats that grew up
hearing, F-026's scope note carried over. One composition, one world,
one band; the claim inherits those bounds (F-009). Confound on record
(F-026 SC-005): the bugs-2.0 economy and the fog world both changed
since the pre-fog baseline, so this read attributes nothing to fog
alone — it answers channel-fitness of the served generation on the
served world, which is what the copy claim needs.

## Regeneration

### Collect

Runtime: about 30–60 minutes per arm on 6 workers (recorded in
`results-raw/stage.log`); never run by the accuracy gate.

```
cd /Users/elizabethkelly/ai/cloudkitty
caffeinate -s nohup bash experiments/fog-deafening-2026-09-23/deafen_stage.sh > experiments/fog-deafening-2026-09-23/results-raw/stage.log 2>&1 &
# deafen_stage.sh runs, sequentially, with the lab venv (experiments/exp-006-character-gen/.venv/bin/python):
#   cert_harness_fog.py gen1-A deaf --seeds 30 --ticks 20000 --workers 6 --out-dir experiments/fog-deafening-2026-09-23/results-raw/battery
#   ... --deaf want   ... --deaf here   ... --deaf all   (same band, same out-dir)
```

### Read

Runtime: under 5 seconds.

```
cd /Users/elizabethkelly/ai/cloudkitty
experiments/exp-006-character-gen/.venv/bin/python experiments/fog-deafening-2026-09-23/deafen_read.py \
  experiments/fog-deafening-2026-09-23/results-raw/battery/gen1-A-c0-deaf-30x20000.jsonl \
  experiments/fog-deafening-2026-09-23/results-raw/battery/gen1-A-deaf-want-c0-deaf-30x20000.jsonl \
  experiments/fog-deafening-2026-09-23/results-raw/battery/gen1-A-deaf-here-c0-deaf-30x20000.jsonl \
  experiments/fog-deafening-2026-09-23/results-raw/battery/gen1-A-deaf-all-c0-deaf-30x20000.jsonl \
  --out experiments/fog-deafening-2026-09-23/results-raw/deafen-read.json \
  --md experiments/fog-deafening-2026-09-23/results-raw/deafen-read.md
```

## Deviations (2026-09-24, post-collection; the declared lines and rules are unchanged)

- Prediction 1's motivating citation read "the same deafening measured
  −0.011". F-026 had no arm that silenced everything: purr-deaf
  measured −0.011, follow-me-deaf −0.014, both-deaf +0.013, and no
  pre-fog arm touched the want words. The declared −0.15 line does not
  depend on the citation. Caught by the accuracy gate's first pass.
- "Instrument at 207f8c9": the mask and its reds are 207f8c9's; the
  copy that collected is afc43ae's, whose only change is the `deaf`
  band entry (`tool_sha256` 3be2a687… in every battery header).
- Collect runtime was about 2.7 minutes per arm against the declared
  30–60; the read command and its outputs are as declared.
