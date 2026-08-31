# Research: Waterline Contagion (spec 044)

No NEEDS CLARIFICATION markers remained after `/speckit-clarify` (one
question, owner-ruled Option A: own-activity scene membership). The
decisions below resolve every implementation choice against the codebase
as of origin/main a2e93f8.

## D1 — Knob home and name: `[water] contagion_factor`

- **Decision**: `pub contagion_factor: f32` on `WaterConfig`
  (`config/mod.rs:122`), `#[serde(default, skip_serializing_if =
  "f32_is_zero")]`, reusing the existing `f32_is_zero` helper
  (`config/mod.rs:1022`). Default 0.0 = feature off.
- **Rationale**: Contagion is a *price on the bath need sourced from
  water* — it belongs beside `bath_gain` and `bath_gain_ceiling`, whose
  semantics it reuses. Identity-skip keeps the default config stamp
  byte-identical (FR-002), the 042/043 discipline; `f32_is_zero` is
  already the house pattern for six comfort-weight fields.
- **Alternatives considered**: `[behavior]` (rejected: 043's knob shapes
  *decisions*; this shapes *needs*); an `Option<f32>` (rejected: 0.0 is
  a perfectly good identity, no tri-state needed).

## D2 — Charge site and the borrow problem

- **Decision**: charge in `World::advance_needs` (`world.rs:870-916`),
  the same phase as occupancy. Before the kitty loop (which holds
  `&mut self.kitties`), pre-collect two things when
  `contagion_factor > 0 && bath_gain > 0`:
  1. `wet_ids: BTreeSet<KittyId>` — kitties standing on a water
     position (reusing the already-collected `water: Vec<Position>`);
  2. `contagious: BTreeSet<KittyId>` — ids of kitties **not** in
     `wet_ids` whose `activity.partner()` (`kitty.rs:106`) is in
     `wet_ids`.
  Inside the loop, a kitty in `contagious` (and below the ceiling)
  takes `contagion_factor * bath_gain * bath_ratio(self)`.
- **Rationale**: mirrors how occupancy already solves the same borrow
  (water positions snapshotted pre-loop). Reading partner state from a
  pre-loop snapshot also makes the charge order-independent: every
  cat's wetness is evaluated at the same instant, so tick order cannot
  leak into who pays (Article V fairness). `Activity::partner()` is
  exactly the four-paired-kinds selector the spec names, and returns
  `None` for critter play (spec edge case) — no new classifier needed.
- **Alternatives considered**: charging at activity-apply time
  (`apply_activity_effects`) — rejected: wetness is positional
  per-tick state, and split charging would double-touch the ceiling
  gate; a `Vec<bool>` indexed by roster order — rejected: `BTreeSet`
  on ids is deterministic and roster-order-proof.

## D3 — Gate shape and mutual exclusivity

- **Decision**: extend the existing occupancy `if` into an
  `if occupancy { … } else if contagious { … }` chain sharing the
  ceiling gate on the pre-charge value. Contagion arm:
  `contagion_factor > 0.0 && bath_gain > 0.0 && bath < ceiling &&
  !on_water && contagious.contains(id)`.
- **Rationale**: `else if` makes FR-005 (never both charges) structural
  rather than tested-only; the shared pre-charge ceiling read keeps
  FR-004's overshoot bound identical to occupancy's.

## D4 — Validation: bounds first, budget widened

- **Decision**: in `validate_water` (`config/validate.rs:569`):
  1. **before** the existing `gain == 0.0` early return: reject a
     non-finite or negative `contagion_factor` (FR-010) — a nonsense
     factor must fail even in a water-disabled config;
  2. widen the budget: `ceiling + max(1.0, factor) * gain * max_ratio
     < safeguard` (FR-009). At factor ≤ 1.0 this is bit-for-bit the
     old check, so the served config and both sweeps
     (`tests/shipped_configs.rs`, `cloudkitty-rl/tests/
     shipped_configs_rl.rs`) pass unchanged (FR-011).
- **Rationale**: the dry-member-only rule caps any single tick at one
  charge, and Option A caps sources at one partner, so
  `max(1, factor)` is the exact worst case — not an approximation.
- **Alternatives considered**: capping factor at 1.0 (rejected: the
  owner may sweep above 1.0 later; the budget handles it honestly);
  a separate `validate_contagion` (rejected: one water budget, one
  validator — splitting hides the coupling the re-statement exists to
  state).

## D5 — Inertness proof (SC-001)

- **Decision**: three existing instruments, no new golden:
  1. the stamp guard — extend the
     `roam_cell_stays_out_of_the_default_serialization` pattern
     (`config/mod.rs:2494`) with the contagion factor (a sibling
     assertion in the same test or adjacent);
  2. `tests/evolution_golden.rs` — unregenerated golden proves the
     default-config serialized stream is byte-identical;
  3. `tests/determinism.rs` — unchanged, knob-off replay.
  Code shape completes the argument: with factor 0.0 the contagion
  arm is unreachable and no pre-loop collection runs.
- **Rationale**: this is exactly how 042/043 proved their inert
  launches; a cross-build byte-diff can't live in-tree.

## D6 — Armed test surface (SC-002/003/005)

- **Decision**: new integration file
  `crates/cloudkitty-core/tests/waterline_contagion.rs` (sibling of
  `water_safeguard.rs`, reusing its pinned-world helpers' style):
  - one test per paired kind: dry member accrues exactly
    `ambient + factor × gain × ratio` (hand-computed, to tolerance);
  - wet-member exemption: the swimmer's rise is exactly occupancy;
  - ceiling gate: at/above ceiling, no contagion;
  - nothing-cases: both-dry, both-wet, critter play, asymmetric
    reference (idle groomee of a wet groomer pays nothing — the
    clarified Option A rule, pinned in-tree);
  - armed determinism: two same-seed factor-1.0 runs, identical
    streams.
  Plus validator unit tests beside `validate_water`'s existing ones:
  boundary accept/reject at factor 0.0 / 1.0 / >1.0, negative,
  non-finite (SC-004).
- **Rationale**: activity states can be constructed directly on a
  generated world (the `water_safeguard.rs` and `action.rs` test
  idiom), so each scenario is a few ticks, not a soak.

## D7 — What this spec does NOT touch

- No RL surface: `legal_action_mask`, the refusal seam, KITTY_SLOT —
  all untouched (FR-007; the observation float is wall-gated).
- No `[kitty]` per-cat override for the factor: one world dial, like
  `bath_gain` itself. Per-cat texture already arrives via
  `bath_ratio`.
- No wet timer, no new persisted world state: `contagious` is derived
  per tick and dropped (FR-006).
- CHANGELOG: one line under `## Unreleased` rides the PR (house
  changelog practice); no docs page exists for `[water]` beyond the
  config doc-comments, which D1 updates in place.
