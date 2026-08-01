# Contract: Encodings — Observation v1, Action Menu v1, Mask v1, Global State v1

The single Rust implementation (FR-007), `cloudkitty-rl`. All four carry
schema versions; artifacts pin the versions they were trained against and
mismatches fail loudly at startup. A Python reimplementation of any of
these is forbidden.

## Observation v1

Layout and slot-fill rule as specified in
[data-model.md](../data-model.md#observationschema-v1). Normative points:

- Derived from the frozen start-of-tick snapshot alone; deterministic
  (same snapshot → identical vector, guarded by test).
- All values normalized to documented bounds; trait features are each
  kitty's configured need rate over `reference_need_rate`, clamped to
  **[0, 4]** (a schema-versioned bound, not a tunable). Slot counts and
  normalization constants live in config (`[rl.observation]`), defaults:
  3 kitty, 4 critter, 2 chow, 2 water, 2 sunbeam slots.
- **Slot fill (normative)**: nearest, distance-ordered, ties by id —
  **the ongoing activity's referenced entity always granted a slot in
  its table** (referenced kitty of a cuddle/co-sleep/groom/social play
  in a kitty slot; played-with critter in a critter slot; displacing the
  farthest otherwise-eligible; `is-activity-target` bit set on that
  slot). Chow/water/sunbeam slots — pure nearest-K, ties by id.

## Action menu v1 — normative index table (40 entries)

Targeted entries name observation slots, resolved through the
TargetTable. Direction order is the engine's: North, East, South, West.

| Index | Proposal |
|-------|----------|
| 0–3   | Move North / East / South / West |
| 4     | Rest (solo) |
| 5–7   | Rest with kitty slot 0 / 1 / 2 (cuddle) |
| 8     | Sleep (solo) |
| 9–11  | Sleep with kitty slot 0 / 1 / 2 |
| 12    | Groom (self) |
| 13–15 | Groom kitty slot 0 / 1 / 2 |
| 16    | Eat |
| 17    | Drink |
| 18–21 | Chase critter slot 0 / 1 / 2 / 3 |
| 22–24 | Chase kitty slot 0 / 1 / 2 |
| 25    | Play (solo pounce) |
| 26–29 | Play with critter slot 0 / 1 / 2 / 3 |
| 30–32 | Play with kitty slot 0 / 1 / 2 |
| 33–38 | Meow: want-eat / want-drink / follow-me / want-play / want-cuddle / purr |
| 39    | Idle |

- **Totality (guarded both directions)**: every index decodes to a
  proposal — a vacant or stale slot decodes to a proposal the engine
  lawfully resolves to idle, never a decode error; every proposable
  action encodes to an index. `Purr` (the action) is retired and absent;
  the wait-for-me meow is engine-reserved (spec 012) and absent.
- **Extensibility**: growth only by codec version bump; indices never
  repurposed; no reserved indices.
- **Purr-meow gate (amendment 2026-07-31, spec 022)**: index 38 is the
  deliberate purr — the one earned-gated meow row (the motor's rule:
  happiness above the purr threshold, or happiness that rose). The gate
  lives in engine validation; the mask derives it like every other verdict
  (no carve-outs) and never-all-zero is untouched (idle, index 39). Not a
  repurposing: the index keeps its wire form and identity — its effect
  gained the purr it always named.

## Legal-action mask v1 (versioned with the codec)

- One bit per menu entry: set iff the proposal, made as the world stood
  at the start of the tick, would be applied **as proposed** (passes
  validation; duration enforcement would not rewrite it). Inside an
  activity's minimum the mask reduces to that activity's continuations.
- **Never all-zero — structural** (amended FR-018): target-priority slot
  ordering keeps every activity's exact continuation expressible in the
  menu at any roster or population size — the referenced kitty or
  critter always holds a slot; untargeted continuations (eat, drink,
  solo rest/sleep/play, self-groom) are untargeted entries; outside
  activities the idle bit is genuinely legal.
- **Advisory**: legality speaks to the frozen snapshot; within-tick
  contention is resolved by the engine's fair order. Necessary, never
  sufficient.
- **Guarding test (no carve-outs)**: for every menu entry, mask verdict
  == the engine's validate-plus-enforcement verdict against a world in
  the snapshot's state — the engine's own judgment replayed, not an
  independent re-derivation, so the guard pins the mask's assembly to
  the one implementation of the law; plus a property test that the mask
  is never all-zero across randomized worlds, rosters, and activities.

## Global state v1 (FR-019)

Layout per [data-model.md](../data-model.md#globalstate-v1-versioned):
full roster without slot truncation, bounded configured element summary,
episode clock. Exposed through the Python surface's `state()`
(training/evaluation only); the deployed behavior API cannot receive it.
Versioned like the observation schema; covered by the same determinism
and reproducibility guards (SC-002 includes the global-state stream).
