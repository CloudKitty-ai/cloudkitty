# BC dataset v1 + Arm 0 plumbing (2026-07-28)

**Tools**: `family-gen --family` (sampled variants), `bc-collect`, `zero-artifact`.

## Arm 0 / deploy-chain plumbing

- The zero artifact (182→256→256→40, all zeros) loads, seats, and runs
  through `kitty-eval --artifact` on both roster modes: bounds fire
  correctly on the degenerate greedy policy (first-legal-action bot pins
  its own kitty at mean 8.6; Nash collapses to 0.007 all-subject / ~0.3
  Mixed — the fairness objective behaving exactly as designed), zero
  fallbacks, paired baseline reported. **Deploy chain verified end-to-end.**
- True uniform-under-mask Arm 0 needs sampling selection; `kitty-eval`
  currently seats artifacts greedy-only ([rl.policy] has `sample` but the
  CLI doesn't expose it) → **product handback: a `--sample` flag**.
  Meanwhile the statistical floor via the Python surface: uniform masked-
  random team reward ≈ **0.53–0.54** (training world) / **0.57** (default),
  3 seeds × 2000 ticks, vs `needs_driven` ≈ 0.88–0.90.

## Family v1

8 variants from `family-gen --family 8 --family-seed 20260728 --base
training.toml` (regenerable; manifest with base sha256 alongside): size
{22,24,26}², water/chow ±1 (floor 2), sunbeams {2,3}, global rate ×
{0.9,1.0,1.1}, trait overrides ±0.1. Roster fixed at 5 (v1 scope,
documented in the tool).

## Dataset v1 (`raw/bc-v1/`, gitignored, regenerable)

`bc-collect --config training.toml --family-dir raw/family-v1 --rollouts 5
--ticks 8000 --seed-base 5000`: 45 rollouts × 8,000 ticks →
**1,776,076 decisions** (prereg band 1–2M), 1.3 GB npy shards
(obs 182 f32 / mask 40 u8 / applied-action label / kitty / tick / per-tick
team reward for critic MC targets).

Validation: **0 labels illegal under their own mask** (checked across all
shards); 29/40 menu actions appear (missing: far-slot targeted variants
the expert never takes); reward traces at the known baseline (~0.88).
Label = **applied** action (mask-consistent by construction). Drop rate
**1.12%**, entirely the engine-reserved WaitForMe meow (excluded from the
menu by spec-014 design — the prereg's "<1%" expectation was a slight
underestimate with a now-identified benign cause). Mask-mismatch rate
0.21% (joint-resolution edge cases, excluded from the dataset).

Episode clock cycles (tick mod 2000)/2000 across the 8k rollouts — input
range covered while the clock-blind expert teaches clock-invariance.

## Next

BC clone (framework choice + trainer skeleton) → critic pretrain on MC
targets (states with ≥1,500 ticks realized future only, deviation 27c).
