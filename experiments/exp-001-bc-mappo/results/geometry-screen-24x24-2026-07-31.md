# Geometry screen: s6 on 24×24 — clean pass, effect grows (2026-07-31)

Exploratory screen per deviation 2026-07-31a (criteria fixed before the
run). Purpose: the owner is restoring the served world to its intended
24×24 in the post-#79 recert batch; screening s6 on the geometry alone,
on the *current* engine, retires the world-size variable from that
batch's bisection — if the recert ever surprises, only engine changes
remain as suspects. This is a screen, not a certification: §8's world
is 24×24 only when the owner lands it in `cloudkitty.toml`.

## Setup

`kitty-eval --artifact arm2.ckpolicy --config
configs/cloudkitty-24x24-screen.toml --seeds 1–10 --ticks 20000
--roster both` — certification shape. The variant config
(committed alongside this doc) differs from `cloudkitty.toml` in
exactly: width/height 32→24, Miso's soak seat reverted to
`needs_driven`, `[rl.policy.s6]` dropped. Engine unchanged (current
main). Element budget scales by rule (`floor(w·h/32)`: 32→18; per-tile
density preserved; kitty density ×1.78).

## Result: pass, on every count

- **Welfare bounds: PASS in all 20 runs** (10 seeds × both rosters).
- **Zero guardrail incidents anywhere**: max distress age 0, longest-low
  0, low-share 0.00% in every run; zero fallbacks.
- **The effect is larger than on 32×32**:

| roster | Δ (10 seeds) | 32×32 reference (same artifact) |
|---|---|---|
| AllSubject | **+0.0450** (range +0.0430…+0.0460, 10/10 positive) | +0.0418 |
| Mixed | **+0.0127** (10/10 positive) | +0.0110 |

- **Everyone is happier on the small world**: needs_driven baseline
  anchor ≈ 0.907 (vs 0.902 on 32×32); s6 AllSubject welfare ≈ 0.952
  (vs ≈ 0.944). Denser world → shorter travel, easier adjacency — the
  direction predicted before the run.

## Reading

24×24 sits inside the training family's geometry range (family-v1
spans 22–26 with two exact 24×24 members), while 32×32 was seen only
during the anneal phase — so this screen moved s6 *toward* its
training distribution, and the numbers agree. Geometry is retired as
a risk for the recert batch. No surprises are owed to world size; any
post-#79 regression points at the engine changes.

Evaluate-once note: this is s6's single pre-recert evaluation on this
geometry. The post-#79 recert (on the new engine, at 24×24 in
`cloudkitty.toml` proper) is a different measurement of a different
engine and does not re-run this one.

## Regeneration

```
A=experiments/exp-001-bc-mappo/artifacts/arm2-g0p998-s6
./target/release/kitty-eval --artifact $A/arm2.ckpolicy \
    --config experiments/exp-001-bc-mappo/configs/cloudkitty-24x24-screen.toml \
    --seeds 1,2,3,4,5,6,7,8,9,10 --ticks 20000 --roster both \
    --json $A/geometry-screen-24x24.json
```

Raw outputs: `artifacts/arm2-g0p998-s6/geometry-screen-24x24.{json,txt}`
(gitignored, machine-local). Artifact sha256 `8030b94d…` (unchanged).
