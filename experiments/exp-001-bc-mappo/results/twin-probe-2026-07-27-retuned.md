# Twin-probe result: the retuned baseline's credit horizon (supersedes F-001's numbers)

**Date**: 2026-07-27 · **Prereg**: [§6 of prereg.md](../prereg.md) (+ Deviations 2026-07-25, 2026-07-27) · **Baseline**: post-retune main (758ec28; retune = PR #60, cf82007) · **Status**: measurement complete — F-001 superseded by F-003

## Headline

The companionship retune (happiness weights eat/drink→0.20, cuddle/bath→0.15;
groom/play relief→20, cuddle relief→15) **roughly tripled the environment's
credit horizon**. The two-channel structure survives — fast self, slow
teammate — but every band moved out:

| Quantity | Pre-retune (F-001) | Post-retune (this run) |
|---|---|---|
| Teammate (spillover) band | ~50–200, peak k≈106 | ~230–430 contiguous, peak k≈406; diffuse real tail past 1000 |
| Team-reward peak | k≈108 | k≈230 |
| Team-reward mass ≤200 ticks | 90% | 16% |
| Team-reward mass ≤400 ticks | ~100% | 36% |
| Self mass ≤18 ticks | 59.5% | 25% |
| Decision-point density | 0.86 | 0.72 |
| γ=0.99 team-signal retention | 0.38 | **0.10** |
| γ=0.995 team-signal retention | 0.59 | **0.20** |
| γ=0.998 team-signal retention | — | **0.45** |

Mechanism, as predicted qualitatively in the prereg's 2026-07-27 deviation
(direction right, magnitude underestimated): slower social relief makes
scenes longer — a cuddle pile or grooming pair occupies its participants
2–3× as many ticks — so contention and coordination consequences propagate
through the roster later and over a wider window. Longer scenes also mean
more mid-scene ticks where an idle substitution is rewritten back by
duration enforcement, which is the drop in decision-point density.

## Consequences for exp-001 (decision inputs, not yet decisions)

- **The pre-registered γ sweep {0.99, 0.995} no longer brackets the
  environment.** γ=0.99's ~100-tick horizon now ends before the cooperative
  band *begins*; it retains 0.10 of the team signal and can no longer test
  the cooperative hypothesis. Even γ=0.995 (200-tick horizon) bisects the
  band's onset. γ=0.998 (500-tick horizon) covers the contiguous band and
  retains 0.45. **Recommendation for the owner** (the sweep set is a prereg
  amendment, owner's call, doc still unfrozen): sweep **{0.995, 0.998}**,
  dropping 0.99 as empirically dead rather than sweeping it to prove it.
- **λ=0.95 still fine**: the direct GAE window (~18–19 ticks at either γ)
  covers the self channel's front-loaded quarter and was never going to
  reach a 230-tick band. The F-001 implication that **cooperative credit is
  critic-carried** is *strengthened* — even more of the team signal now
  lives beyond any reachable GAE window; critic explained-variance remains
  the watch-first diagnostic, and the episode horizon (2,000) still gives
  ≥3× the significant band, so truncation bias stays modest.
- **Rollout fragment 256 is unchanged** (≫ direct window; GAE bootstraps at
  the edge either way).

## Numbers (1,200-tick traces, primary run)

Run: 1,000 valid samples (1,396 attempts, 396 degenerate → decision-point
density 0.72), 20 world seeds (101–120), substitution ticks uniform in
[100, 1100), probe seed 42, config `training.toml` on post-retune compiled
defaults. Substituted actions: move 717, chase 93, sleep 36, drink 32,
groom 29, eat 28, play 26, meow 21, rest 18. 13% healed by trace end.

Per-tick significance = |across-sample mean of signed diff| > 2·SE
(~60/1,200 false positives expected by chance):

| Channel | Significant ticks | Contiguous bands (first 10) | Peak | Mass ≤18 | ≤200 | ≤400 | γ=0.995 | γ=0.998 |
|---|---|---|---|---|---|---|---|---|
| Team reward (dr) | 201 | 0–12, 44–50, 60, 106–112, 123–134, 220–222, 226–251, 254–257, 395–425, 429 | 2.6e-3 at k=230 | 3.2% | 15.6% | 36.3% | 0.20 | 0.45 |
| Self happiness | 89 | 0–18, 21–22, then sporadic | 0.481 at k=3 | 24.8% | 38.9% | 52.6% | 0.37 | 0.55 |
| Teammates (spillover) | 161 | 1–2, 46–47, 59–60, 103, 106–110, 124–135, 142, 227–252, 254–258, 368 | 0.246 at k=406 | 0.1% | 13.2% | 38.7% | 0.18 | 0.45 |

**Trace-length note**: the first pass used the shipped 600-tick traces and
was **truncated** — significance was still present at k=597. Doubling to
1,200 ticks (identical sampling: same probe seed, same 1,396 attempts, and
the shared prefix's bands match exactly) resolved it. Future runs on this
baseline should use `--trace-len 1200`.

**Late-tail caution**: beyond the last big contiguous band (~430), the
significant ticks (≈96 in 430–1,200, vs ≈38 expected by chance) are real in
aggregate but diffuse, and the mass metric weights them by diffusion-scale
amplitudes — read the ≤k mass fractions as the robust quantities and the
raw "last significant k" (1,068) as an overstatement of usable signal, per
the same noise-floor discipline as the 2026-07-25 run.

## Reproduce

```
cargo build --release --manifest-path experiments/tools/twin-probe/Cargo.toml
./experiments/tools/twin-probe/target/release/twin-probe \
  --config training.toml --samples 1000 --trace-len 1200 \
  --seeds 101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120 \
  --probe-seed 42 --quiet \
  --out experiments/exp-001-bc-mappo/raw/twin-probe-training-1k-retuned-t1200.jsonl
python3 experiments/tools/twin-probe/analyze.py \
  experiments/exp-001-bc-mappo/raw/twin-probe-training-1k-retuned-t1200.jsonl 0.99 0.995 0.998
```

Raw JSONL is gitignored (`raw/`); the run regenerates bit-identically.
Wall-clock: ~80 s. Manifest: `training.toml` + compiled defaults at
758ec28 (post-retune, pre-v2.5-tag); probe and analysis code at this
commit (probe flags added in PR #62 — `--quiet` used here does not affect
sampling).

## Follow-ups

- Owner decision: amend the prereg γ sweep to {0.995, 0.998} (recommended
  above) or keep {0.99, 0.995} as registered.
- Figures (prereg §10.2), now on this dataset.
- By-action-class conditioning via `--only-action` (mix is 72% move).
- Default-world repeat (F-003 carries the scope gap forward).
- `training.toml` calibration sanity: 20k `needs_driven` rollout under the
  retuned defaults — confirm the training world still sits in the useful
  band (welfare-passing, not saturated).
