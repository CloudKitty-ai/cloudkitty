# Contract: The Joint-Action Seam (FR-001..004, FR-017)

The engine-side surface `cloudkitty-rl` and every external driver build on.
Rust API, `cloudkitty-core`. No RL vocabulary crosses this boundary.

## `World::tick_with_proposals`

```text
tick_with_proposals(&mut self, proposals: &JointProposal) -> TickReport
```

- Advances the world **exactly one tick** in constitutional order: fair
  turn order draw → validation → duration enforcement → apply → activity
  ends → environment phase → needs → distress → purr → invariants.
  Behavior dispatch is the only step bypassed (FR-001).
- **Shared implementation**: the behavior-driven tick and this seam call
  one pipeline for all applied phases — the seam is a different *source*
  of proposals, never a different law (FR-002).
- **RNG discipline**: consumes the master RNG with the identical draw
  shape as a behavior-driven tick, including the per-kitty decision-seed
  draws in stable id order — same seed, same futures (FR-002). The drawn
  decision seeds are carried in the TickReport.
- **Absent / malformed / unknown entries**: a kitty with no proposal (or
  an unparseable one, when proposals arrive over a wire) idles; entries
  for unknown ids are reported unconsumed; the tick never fails, blocks,
  or skips another kitty (Article IV).

## TickReport

Per kitty: `proposed`, `validated`, `applied` (the triple that makes
validation rejections and duration rewrites visible), provenance mark,
and drawn decision seed. Tick-level: distress events, activity endings
(FR-003).

## Headless behavior-driven driver

```text
drive_tick(&mut world, &behaviors) -> TickReport   // budgetless
```

- Resolves every behavior against the frozen snapshot **without the
  wall-clock budget** (FR-017): panic isolation and default-behavior
  fallback remain; every decision is marked `policy-made` /
  `fallback-taken`. The served world keeps today's timeout wrapper —
  untouched (research.md R5).
- The report includes the **dispatched proposals**, which is the parity
  capture mechanism (research.md R4).

## Guarding tests (CI, Article VI)

1. **Golden parity (SC-001)**: behavior-driven run (proposals collected)
   vs joint-action run fed those proposals, same seed, default world,
   ≥ 5,000 ticks → byte-identical serialization including RNG state.
2. **Degradation**: joint proposals with one absent and one malformed
   entry → those kitties idle, all others act, invariants hold.
3. **Draw-shape**: RNG state after a joint-action tick equals RNG state
   after the equivalent behavior-driven tick.
