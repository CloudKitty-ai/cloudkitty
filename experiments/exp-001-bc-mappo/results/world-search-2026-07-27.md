# World-search result: probe-guided training-world selection (and a statistics lesson)

**Date**: 2026-07-27 · **Baseline**: post-retune main (F-003 world) ·
**Tools**: `experiments/tools/family-gen`, `experiments/tools/world-search`,
twin-probe · **Status**: winner frozen into `training.toml`

## Question

Which feasible training-world configuration maximizes the *detectable*
discounted cooperative team-reward signal

S(γ) = Σ over significant-band ticks k of |mean dr_k| · γ^k

subject to `needs_driven` staying welfare-passing with margin (team welfare
≥ 0.78, all bounds)? Candidates: element scarcity (2 levels), need-rate
tempo (×1.5, ×1.75 of engine defaults; base is ×1.25), grid 20×20, and
combinations — 10 worlds, each measured by a 1,000-sample twin probe
(1,200-tick traces) plus a 3-seed × 20k-tick `needs_driven` welfare run.

## The methodological finding first (it changes every number below)

The first pass (20 world seeds per run, per-sample significance testing)
produced a phantom: `rates150` appeared to **triple** the credit signal
(S(.995) = 0.188 vs base 0.060). A replication on 20 *disjoint* world
seeds collapsed it to 0.037. Samples that share a world share long-lived
state, so for slow common-mode signal the effective N is the number of
**worlds**, not the number of samples — per-sample SEs overstate
confidence exactly where the cooperative band lives.

**Fix, applied everywhere below**: 100+ worlds per run (~10 samples each)
and cluster-robust statistics — per-tick mean and SE computed over
per-world mean traces. This is now the house rule for every probe
analysis; the F-001/F-003 datasets (20 worlds) share the weakness, which
F-004 records in their margin of error.

## Results (cluster-robust; S = discounted band mass of dr)

| Candidate | Batch A (worlds 1001–1100) S(.995) / S(.998) | Batch B (2001–2100) | welfare_min |
|---|---|---|---|
| base (`training.toml` pre-freeze) | 0.018 / 0.028 | 0.021 / 0.026 | 0.901 |
| scarcity1 | 0.018 / 0.032 | — | 0.897 |
| scarcity2 | 0.012 / 0.036 | — | 0.890 |
| rates150 | 0.024 / 0.061 | 0.011 / 0.021 | 0.889 |
| rates175 | 0.012 / 0.022 | — | 0.875 |
| grid20 | 0.011 / 0.013 | — | 0.903 |
| **scarcity1-rates150** | **0.030 / 0.041** | **0.010 / 0.041** | **0.881** |
| scarcity1-grid20 | 0.005 / 0.009 | — | 0.900 |
| rates150-grid20 | 0.022 / 0.040 | — | 0.892 |
| scarcity1-rates150-grid20 | 0.014 / 0.034 | — | 0.887 |

Decisive third batch (300 worlds, 3,000 samples, seeds 3001–3300):

| | significant ticks (chance ~60) | S(.995) / S(.998) | late bands |
|---|---|---|---|
| base | **40** — at the false-positive floor beyond k≈14 | 0.011 / 0.014 | none coherent |
| scarcity1-rates150 | 68 | 0.013 / **0.026** | 733–754, 860–876, 925–937 — **same bands in the spillover channel** |

Readings:

- **Most knobs do nothing or hurt.** Grid shrinking hurts everywhere
  (more collisions → faster chaotic mixing → higher variance). ×1.75
  tempo is worse than ×1.5 (trajectory noise outruns signal — tempo has
  a sweet spot). Scarcity alone is a wash.
- **Base's cooperative dr signal is at the detection floor.** At
  300-world rigor, the current world's team-reward significance beyond
  the early self-mediated band (k ≤ 14) is statistically indistinguishable
  from the 5% false-positive rate. The F-003 horizon numbers stand as
  measured, but their amplitudes are at the edge of what 3,000 samples
  resolve.
- **`scarcity1-rates150` is the one replicated improver**: S(.998)
  advantage over base in all three disjoint batches (0.041 vs 0.028,
  0.041 vs 0.026, 0.026 vs 0.014; ×1.5–1.8), with dr and spillover
  bands co-occurring at the same ticks in the decisive batch — two
  channels agreeing is corroboration no single channel provides. Its
  signal is *late* (k ≈ 730–940), consistent with scarcity adding
  queueing/turn-taking dynamics whose consequences take longest to
  propagate — the cooperative content we want the policy to learn.

## Decision

**Frozen**: `training.toml` becomes `scarcity1-rates150` — need rates
×1.5 of engine defaults (eat/drink/play/cuddle 0.6, sleep 0.42, bath 0.3),
water/chow 3–4, sunbeams exactly 2. Verified on the frozen file itself
(clean constants, not the generator's float-dust `0.6000000000000001`):
the decisive-batch probe reproduces **identically** (same 68 significant
ticks, same bands, same S), and welfare confirms at 0.881–0.883 with all
bounds passing — margin of 0.10 over the 0.78 feasibility floor, and
lower than base's 0.901, which is itself useful: more headroom for a
policy to demonstrate improvement over `needs_driven`.

Consequences carried into the prereg (Deviations 2026-07-27b):

- γ sweep **{0.995, 0.998}** (F-003's recommendation, unchanged by the
  search: the winner's measured band is late, favoring 0.998; 0.995
  covers state-mediated credit arriving earlier than probe-visible
  reward effects).
- The searched-and-rejected worlds are the recorded H0a contingency:
  if Arm 2 ≈ Arm 1, the next hardening step is chosen from this table's
  Pareto set with fresh measurement, not invented.

## Reproduce

```
cargo build --release --manifest-path experiments/tools/family-gen/Cargo.toml
cargo build --release --manifest-path experiments/tools/twin-probe/Cargo.toml
cargo build --release -p cloudkitty-rl --bin kitty-eval
python3 experiments/tools/world-search/search.py                    # batch A
python3 experiments/tools/world-search/search.py --seed-start 2001 \
    --candidates base,rates150,scarcity1-rates150                   # batch B
# decisive batch: twin-probe --samples 3000 --seeds 3001..3300 on
# training.toml (frozen) — exact command in this doc's git history and
# search.py's constants.
```

Raw JSONL/eval outputs are gitignored under
`exp-001-bc-mappo/raw/world-search/` (bit-reproducible; the first-pass
20-world rows are archived in `results-20worlds-SUPERSEDED.jsonl` as the
record of the phantom). ~35 min wall-clock all-in.

## Follow-ups

- Figures: S-vs-welfare Pareto scatter + the winner's band traces
  (visualization pass, dataviz skill first).
- The probe's `--only-action` conditioning on the frozen world (mix still
  ~72% move).
- F-001/F-003-style default-world repeat on the frozen world's numbers
  is NOT needed (the gym is not the bar), but the eval-side F-003
  default-world repeat remains open.
