# Research: Initial-Needs Distribution at World Creation

No NEEDS CLARIFICATION markers remained after /speckit-clarify (two
owner rulings recorded in spec.md §Clarifications). The decisions
below resolve the plan-level unknowns the spec deliberately left open.

## D1. Config shape: top-level table + per-kitty field

- **Decision**: `[initial_needs]` is an `InitialNeedsSpec` — six
  optional per-need entries, each a `NeedInit` (fixed value or
  `{ min, max }` range). The per-kitty override is
  `KittyConfig.initial_needs: Option<InitialNeedsSpec>` — the SAME
  type — with need-by-need precedence over the top-level table.
  Feature "active" = top-level table present OR any kitty carries the
  field.
- **Rationale**: `KittyConfig` already carries exactly this idiom for
  need RISE rates (`needs: Option<NeedRateOverrides>`) and for
  explicit x/y under `[starts]`; reusing it makes "override names a
  kitty not in the roster" impossible by construction (the spec's
  validation clause is satisfied vacuously — recorded here, noted in
  the contract). One shared type keeps precedence trivially
  need-by-need.
- **Alternatives considered**: an `overrides` array inside
  `[initial_needs]` keyed by kitty id — rejected: needs an
  id-exists-in-roster validation the field form gets for free, and
  diverges from the house per-kitty idiom.

## D2. NeedInit: untagged value-or-range

- **Decision**: `NeedInit` deserializes untagged: a bare number
  (`cuddle = 80.0`) is a fixed value; a table
  (`cuddle = { min = 60.0, max = 95.0 }`) is an inclusive range, its
  struct `deny_unknown_fields`. Validation: every number finite and in
  [0, 100]; `min <= max`; errors name the need and the kitty where
  applicable.
- **Rationale**: matches the KittyConfig x/y precedent of "the simple
  spelling round-trips byte-identically"; TOML-natural for the
  consumer (Experiments derive configs text-wise).
- **Alternatives**: always-range with min==max for fixed — rejected:
  noisier configs, and the fixed form should consume zero draws (D4).

## D3. Sub-stream: `ck-initnd-v1`, the 062 seed recipe

- **Decision**: a new ChaCha8 sub-stream seeded exactly as starts.rs
  does — world seed little-endian in bytes 0..8, the 12-byte domain
  tag `ck-initnd-v1` in bytes 8..20, zeros elsewhere. Law version
  `INIT_NEEDS_LAW_VERSION: u32 = 1`, bumped with the tag together on
  any law change.
- **Rationale**: FR-005 names the 062 law; a distinct tag
  domain-separates it from `ck-starts-v1`, so both knobs on changes
  neither draw (SC-003's composition clause).
- **Alternatives**: drawing from the master stream — forbidden by
  FR-005 (would move every existing golden under section-on and break
  attribution).

## D4. Draw law: order, consumption, mapping

- **Decision**: iterate kitties in id-ascending order, needs in
  `NeedKind::ALL` order. For each (kitty, need): resolve the governing
  setting (kitty-level if set, else top-level, else none). A RANGE
  consumes exactly one u64 draw — even when min == max (the
  fixed-shape rule: draw count depends only on config shape, the purr
  precedent at world.rs `min == max` comment). A FIXED value and an
  ungoverned need consume zero draws (the starts precedent: explicit
  kitties draw nothing). Mapping: `u = (draw >> 11) as f64 * 2^-53`
  (uniform in [0,1)), `value = min + u * (max - min)` as f32 — min and
  max both reachable only at min == max for max; inclusive-of-min,
  and max attained in the degenerate case; documented as "inclusive
  range [min, max], upper end approached" in the contract with the
  exact mapping pinned.
- **Rationale**: deterministic, porting-grade, shape-stable; per-kitty
  × per-need independence is the Q2 ruling.
- **Alternatives**: `rng.gen_range` — rejected: its rejection
  sampling can consume a variable number of draws; the law pins one
  draw per ranged need.

## D5. Application site and the tick-0 state family

- **Decision**: in `World::try_generate`, immediately after the kitty
  creation loop + id sort (before explore seeding — needs are
  position-independent, but one fixed site): apply resolved initial
  needs via `Needs::add`-equivalent direct sets (values are already
  validated in-bounds; `Need::new` clamps as belt-and-braces). The
  existing end-of-generate happiness recompute (world.rs ~178) then
  derives tick-0 happiness — FR-004 for free. After it, gated on the
  feature being active: `self.update_announce_arming(config)` then
  `self.record_distress(config)` — the exact Phase-4 order — so
  arming, `in_distress`, `distress_since` (anchored at tick 0), and
  `DistressLog` events all come from the engine's one definition
  (FR-006). `purr_phase` is NOT run: generation has never purred, and
  purring is relief-side, not distress-side.
- **Rationale**: `record_distress` is state-based (`value >=
  threshold`, edge via `in_distress.insert`), so calling it at
  generation IS the mid-run semantics at tick 0 — the spec's "no
  parallel path" assumption verified. Gating keeps the inert-absent
  proof trivial (064 pattern); with the feature inactive the calls
  would be provable no-ops, but not-running beats proving.
- **Alternatives**: seeding distress fields by hand at apply time —
  rejected: a second definition of "entering distress" (the spec
  assumption forbids it); running record_distress unconditionally —
  rejected: widens the byte-inertness argument for zero gain.

## D6. Serialization discipline

- **Decision**: `Config.initial_needs: Option<InitialNeedsSpec>` with
  `#[serde(default, skip_serializing_if = "Option::is_none")]` — the
  starts field's exact attrs and comment pattern;
  `KittyConfig.initial_needs` likewise. Inner per-need options
  skip-if-none. `deny_unknown_fields` on `InitialNeedsSpec` and the
  range struct.
- **Rationale**: FR-001/FR-002 — absence is the off state;
  `engine_defaults_sha256` and `GET /config` unmoved; the stamp test
  extends with the new key exactly as 063/064 did.

## D7. Safeguard interaction needs no code

- **Decision**: nothing to build for FR-007 — the environment phase's
  safeguard check already reads current needs each tick; an
  initialized need ≥ safeguard is indistinguishable from a risen one
  at the first environment phase. Covered by a test, not a mechanism.
- **Rationale**: constitution wording ("spawn one on the next
  environment phase") is satisfied by the existing machinery; adding
  a generation-time spawn would be new law the spec forbids ("no new
  rule, no exemption").
