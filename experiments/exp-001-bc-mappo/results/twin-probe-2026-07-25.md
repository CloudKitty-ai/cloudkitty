# Twin-probe result: the credit horizon of the training world

**Date**: 2026-07-25 · **Prereg**: [§6 of prereg.md](../prereg.md) · **Status**: measurement complete, γ decision informed

> **Scope notice (2026-07-27)**: these numbers were measured *before* the
> baseline retune (PR #60, cf82007 — happiness weights and social relief
> rates changed, reaching `training.toml` via the compiled defaults). They
> stand as the historical record of the pre-retune world; the prereg's
> Deviations appendix records the consequence — the probe re-runs on the
> retuned baseline before the γ sweep, and F-001 gets a confirm-or-supersede
> verdict from that run. The regeneration commands below reproduce *this*
> dataset only at cf82007's parent or earlier.

## Headline

CloudKitty's credit structure splits into two channels with very different
speeds. An action's effect on the **actor's own happiness** is fast and
front-loaded: ~60% of the significant signal mass lands within 18 ticks
(direct relief). Its effect on **teammates** — the cooperative channel — is
slow and delayed: essentially zero mass within 18 ticks (0.3%), a
significant band from ~50–200 ticks peaking at k≈106. The **team reward**
inherits the teammate channel's shape: 90% of significant mass within 200
ticks, peak at k≈108, last significant tick 380.

Interpretation: self-service credit is directly observable in near-term
reward, but *cooperation credit* — who yielded the bowl, who left the
sunbeam, whether a duet stayed available — takes ~100 ticks to propagate
into other kitties' welfare. The credit horizon that matters for the
cooperative hypothesis is the 50–200-tick teammate band.

## Decisions (per prereg §6 rules)

- **γ**: the tail (contiguous significance to ~130, band again at ~190,
  sporadic to 380) sits between the prereg's two thresholds → the
  pre-registered sweep {0.99, 0.995} proceeds, now with a registered
  prediction: **0.995 wins**. Quantified: discounting the significant
  team-reward signal mass, γ = 0.995 preserves **0.59** of it vs **0.38**
  at γ = 0.99 — the 0.99 horizon (~100 ticks) cuts through the middle of
  the cooperative band.
- **λ**: stays 0.95. The γλ ≈ 18-tick direct GAE window covers the self
  channel (59.5%) but none of the spillover (0.3%); no reachable λ bridges
  a 100-tick gap. Consequence worth registering: **cooperative credit is
  carried almost entirely by the critic** — critic explained-variance is
  the make-or-break diagnostic, and the privileged global state
  (MAPPO-over-IPPO) is empirically motivated, not just conventional.

## Numbers

Run: 1,000 valid samples (1,159 attempts, 159 degenerate → decision-point
density 0.86), 600-tick traces, 20 world seeds (101–120), substitution
ticks uniform in [100, 1100), probe seed 42, config `training.toml`.
Substituted actions: move 704, chase 76, drink 40, sleep 39, play 36,
groom 34, eat 30, meow 24, rest 17. 15% of samples fully healed (zero
reward divergence over the last 100 ticks) — most substitutions matter,
some genuinely don't.

Per-tick significance = |across-sample mean of signed diff| > 2·SE
(~30/600 false positives expected by chance):

| Channel | Significant ticks | Band | Peak | Mass ≤18 | ≤100 | ≤200 |
|---|---|---|---|---|---|---|
| Team reward (dr) | 110 | 0–7, 54–126, 187–198 | 3.4e-3 at k=108 | 3.6% | 51.5% | 90.1% |
| Self happiness | 32 (≈chance beyond band) | 0–17 | 0.548 at k=0 | 59.5% | 62.2% | 73.3% |
| Teammates (spillover) | 122 | 52–76, 78–128, 183–195 | 0.382 at k=106 | 0.3% | 44.1% | 85.1% |

Methodology cautions honored: signed means only (chaotic diffusion is
sign-symmetric and averages out — single-trace |Δ| overstates persistence);
no decay fitting below the noise floor (an earlier exploratory exponential
fit that ignored this produced a nonsense τ≈4,900 and is superseded by the
significance-band analysis); isolated late significant blips are consistent
with the multiple-testing base rate.

## Reproduce

```
cargo build --release --manifest-path experiments/tools/twin-probe/Cargo.toml
./experiments/tools/twin-probe/target/release/twin-probe \
  --config training.toml --samples 1000 --trace-len 600 \
  --seeds 101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120 \
  --probe-seed 42 --out experiments/exp-001-bc-mappo/raw/twin-probe-training-1k.jsonl
python3 experiments/tools/twin-probe/analyze.py \
  experiments/exp-001-bc-mappo/raw/twin-probe-training-1k.jsonl 0.99 0.995
```

Raw JSONL is gitignored (`raw/`); the run above regenerates it
bit-identically (probe sampling and every world are seeded). Wall-clock:
~35 s. Manifest: config = `training.toml` at this commit; probe and
analysis code in `experiments/tools/twin-probe/` at this commit.

## Follow-ups

- Figures (per prereg §10.2): divergence envelope + per-channel mean-signed
  traces with significance shading — pending the visualization pass.
- Condition the analysis by substituted-action class (move-dominated mix;
  eat/drink substitutions likely carry the fast channel).
- Repeat on the default world and the scale exam config to see how the
  teammate band shifts with geometry (transfer question).
