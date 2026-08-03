# Research: Per-Target Play Relief

No NEEDS CLARIFICATION markers remained after the spec (the handoff
fixed the values and the evidence; the spec pinned the two open
semantics). This file records the decisions and the code walk that
grounds them — every line-number claim below was read, not recalled,
on `8bed190` (branch base).

## R1 — Key naming: keep `play_relief`, add two keys

- **Decision**: `play_relief` keeps its name and becomes formally the
  kitty/duet value; add `play_relief_bug` and `play_relief_greeble`,
  each `#[serde(default = ...)]`. No aliases, no renames.
- **Rationale**: The handoff's constraint is that existing configs
  carrying `play_relief` keep parsing with today's meaning. Renaming
  to `play_relief_kitty` with a serde *alias* would satisfy parsing
  but change the **serialized** key in the `/config` payload — a
  wire-level change the handoff rules out ("Client: no work — no
  visible or wire-level change"). Keeping the name satisfies both
  constraints with zero machinery.
- **Alternatives considered**: (a) rename + alias — rejected, wire
  change + Serialize/Deserialize asymmetry to maintain; (b) a nested
  `[actions.play]` table — rejected, restructures a section for no
  behavioral gain and touches the 020 config-restructure surface.

## R2 — Despawn/absent-id fallback: solo value

- **Decision**: the `Playing { Element }` effect arm looks the element
  up each serviced tick; on a miss (expired id) or a non-critter kind
  (unreachable via validation, `action.rs:385-388`), the tick pays
  `solo_play_relief`.
- **Rationale** *(corrected during implementation — the original
  reading here and in the handoff was wrong about the tail)*: elements
  expire mid-scene (`world.rs:807`, `Element::is_expired`), and the
  effect arm indeed never looks the element up — but the slot
  pipeline's `prune_dead_activity` (`world.rs:421-456`) ends a
  vanished-target scene at the kitty's next slot, before any further
  effect lands (guarded by
  `world::tests::a_vanished_critter_ends_play_where_it_stands`). There
  was never a 20/tick tail in the canonical loop, and there is no
  35/tick grind vector to close. The fallback earns its place as
  defense-in-depth instead: `apply` is public and total, and the arm
  must never pay a critter's price for an id it cannot resolve. "The
  critter is gone, the kitty is pouncing at nothing" is the honest
  price for that path.
- **Alternatives considered**: (a) keep paying the kitty value
  (today's accidental behavior) — rejected, preserves the exploit
  tail and gives a vanished greeble the duet price; (b) end the
  activity on despawn — rejected, a scene-lifecycle change the
  handoff didn't ask for and a bigger behavioral delta than the
  fallback (out of the mini-spec's footprint).

## R3 — Guard strictness: strict `<` everywhere

- **Decision**: `solo < play_relief < bug < greeble`, strict; ceiling
  `greeble < 2 × play_relief`, strict.
- **Rationale**: the handoff writes the chain with `<`. Equality
  anywhere in the chain makes two play forms indistinguishable —
  exactly the team-neutrality the split exists to remove. At the
  ceiling boundary (`greeble == 2×kitty`) a myopic defection is
  exactly team-neutral, so the dilemma's edge goes flat; strict keeps
  the margin real. Tighten-only is house doctrine (spec 017), and no
  shipped or frozen config sits on a boundary (checked: eval configs
  carry no play keys; served config is 10/20). One in-repo **test
  fixture** does collide: the old-shape-parses test
  (`config/mod.rs:1440-1481`) carries `play_relief = 25.0` and calls
  `validate()` — with `play_relief_bug` defaulting to 25 the chain
  rejects `25 < 25`. The fixture's value is arbitrary to its intent
  (old-shape TOML parses; omitted keys default in); it is reconciled
  to `20.0` in the same change. Not a weakened test — a fixture kept
  lawful under the new contract, recorded here so the diff is
  expected.
- **Alternatives considered**: non-strict `<=` at the solo boundary to
  preserve today's acceptance of `solo == play_relief` — rejected;
  nothing depends on it and it contradicts the gradient's purpose.

## R4 — Where the routing lives: effect body only

- **Decision**: the only code change outside config is the
  `Activity::Playing { Element }` arm of `apply_activity_effects`
  (`action.rs:712-714`). Proposal validation, `begin_activity`, the
  duet arm, the solo arm, and scene ending rules are untouched.
- **Rationale**: `apply_activity_effects` is "the *only* effect body:
  the starting tick and every continuation both land here"
  (`action.rs:661-664`) — one arm covers tick 1 and ticks 2..n by
  construction. The lookup mirrors the Eating arm's existing pattern
  of consulting the world at effect time (`action.rs:681`).
- **Alternatives considered**: resolving the element type once at
  `begin_activity` and storing it in the activity — rejected, adds
  world-state shape (snapshot surface) and *freezes* the type across
  the scene, which reintroduces the despawn exploit R2 closes.

## R5 — Behavior layer: no re-rank, verified

- **Decision**: no behavior-layer change.
- **Rationale**: needs_driven selects relief by shape
  (`relief.rs` ReliefSource), never magnitude. The one
  `actions.solo_play_relief` read in `behavior/selection.rs` (line
  585) is inside `#[cfg(test)]` (verified by reading the enclosing
  module), and solo's value does not change. The census confirms solo
  play never starts in scripted worlds (0 in 400k world-ticks).
- **Alternatives considered**: none needed.

## R6 — Re-baseline inventory: what moves and what must not

- **Decision**: regenerate `run-json.golden.json` once
  (`UPDATE_GOLDENS=1`); let `engine_defaults_sha256` move (automatic —
  it hashes `Config::default()`'s canonical JSON, `suite.rs:169-178`;
  `harness_policy.rs:406` asserts only the key's presence, no pinned
  value exists in-repo); re-run `welfare_longrun` and expect floors to
  hold with more margin (verify, never loosen). Must NOT move: obs dim
  182, codec 40, snapshot format (no state change), frozen exam
  configs (no `deny_unknown_fields` on `Config` — verified during 024),
  hash pins, served `cloudkitty.toml`.
- **Rationale**: same one-break discipline as 024; the stamp move is
  the break's visible mark and Experiments re-runs its measurement
  stack keyed on it (registered prediction: play/chase probe class
  rises off its 0.1× floor).
- **Alternatives considered**: none — the inventory is the handoff's,
  confirmed against the code.
