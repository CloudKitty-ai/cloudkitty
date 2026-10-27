# Implementation Plan: Needy Behaviour Preset

**Branch**: `product/067-needy-preset` | **Date**: 2026-10-26 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/067-needy-preset/spec.md` (clarified 2026-10-26: m configurable 1..N, servicing-only mask, two presets; the Professor's four changes folded; FR-016 need-count agnostic).

## Summary

Two builtin behaviour presets, `needy` and `needy_hold`, that decide as
the `teacher` preset except for a MASK: a deterministic per-seat
schedule of episodes (onset tick, m masked needs, release at level or at
the hold limit, rest gap) during which the seat neither services the
masked needs nor accepts offered relief for them. The schedule's state
lives on the kitty in the world (`Kitty.needy`, absent for every other
kitty, so snapshots and every surface stay byte-identical), is advanced
by the engine once per tick after needs rise, and draws from a private
domain-tagged sub-stream seeded from (world seed, kitty id) exactly as
specs 062 and 065 do — the master stream and other kitties' streams are
never touched. The mask is ENGINE LAW at the apply slot (a `needy
verdict` beside the consent gate: a proposal that would relieve a masked
need of the proposer or of its target resolves to Idle) and a partner
availability rule (a kitty masked on a duet's partner-relief need is not
an available partner), with the preset's own ladder reading a masked
view of its needs so it chooses sensibly instead of wasting turns. Two
new spec-066 hazard modes (`needy`, `needy_hold`; mode name = preset
name), a `teaches()` flag on the behaviour trait read by the corpus
collector, a `[needy]` config section (N-sized weight vector, levels,
floors keyed by need name), and the per-tick mask/ordinal/phase on the
kitty in the snapshot plus a binding accessor beside `recent_meows()`.

## Technical Context

**Language/Version**: Rust (workspace pin `rust-toolchain.toml`), PyO3 binding (`cloudkitty-py`, abi3-py39).
**Primary Dependencies**: `rand_chacha` (ChaCha8Rng, the sub-stream pattern of 062/065), `serde`, `toml`; no new dependency.
**Storage**: the world snapshot JSON (`Kitty.needy: Option<NeedyState>`, skip-if-none).
**Testing**: `cargo test --workspace`; rule 5 via `scripts/mutate.sh --expect`; `pytest` for the binding accessor.
**Target Platform**: server, lab (binding), CI.
**Project Type**: engine library + server + binding.
**Performance Goals**: one extra per-tick pass over needy seats only (zero when none); no extra allocation on the inert path.
**Constraints**: byte-inert without a needy seat (FR-002); Article IV (engine is the law — the verdict lives in the engine); Article V (deterministic; fixed phase order; sub-stream only); no observation-schema or wire change (FR-014); nothing hard-codes N (FR-016).
**Scale/Scope**: ~6 engine files (`behavior/needy.rs` new, `behavior/mod.rs`, `behavior/teacher.rs`, `kitty.rs`, `world.rs`, `action.rs`), config (`config/needy.rs` new, `mod.rs`, `validate.rs`, `welfare_hazard.rs`), binding (`cloudkitty-py/src/lib.rs` + a pytest), the collector (`experiments/tools/bc-collect`, Experiments' lane — cross-lane with consent or theirs), CHANGELOG; no config files change, no golden re-cuts.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Article I (kitties cannot suffer)**: PASS. The mask governs choices only; needs stay bounded; the distress threshold, the safeguard spawn (environment phase, unchanged) and the happiness floor apply to a needy kitty exactly as to any kitty (FR-013; doctrine rule 12). A scripted seat is welfare-exempt (practice 2026-09-26). Guards: never applied to a covered seat (builtin only); never teaches (FR-010/011).
- **Article II / III**: PASS. No population change; a needy kitty is still a roster member and partner for every unmasked need.
- **Article IV (engine is the law)**: PASS by design. The needy preset PROPOSES like any behaviour; the ENGINE enforces the mask at the apply slot (the needy verdict → Idle) and in partner availability, so a malformed or bypassing proposal cannot relieve a masked need. The builtin's own masked view is advice quality, not law.
- **Article V (deterministic, server-authoritative)**: PASS. The schedule draws from a ChaCha8 sub-stream seeded by (world seed, kitty id, domain tag), carried in the kitty's state; the master `World.rng` and every `DecisionRng` are untouched (FR-003, SC-002). The advance step sits at one fixed point in Phase 4.
- **Article VI (spec-first, test-guarded)**: PASS. Spec clarified before this plan; every FR maps to a guard in quickstart §7 / tasks.

Post-design re-check (after Phase 1): unchanged — no new violation; the `is_available_friend` rule is engine law (Article IV), the binding accessor is read-only (Article V's pure view).

## Project Structure

### Documentation (this feature)

```text
specs/067-needy-preset/
├── plan.md              # this file
├── research.md          # D1–D14, measured against the tree at c9d85721
├── data-model.md        # NeedyConfig, NeedyState, Episode, phases, registry rows
├── quickstart.md        # validation scenarios + the rule-5 ledger shape
├── contracts/
│   └── needy-law.md     # the one place the schedule, mask and verdict are pinned
└── tasks.md             # /speckit-tasks output
```

### Source Code (repository root)

```text
crates/cloudkitty-core/src/
├── behavior/
│   ├── needy.rs           # NEW: Needy { hold: bool } Behavior; masked view; NAME/HOLD_NAME; teaches() = false
│   ├── mod.rs             # register "needy"/"needy_hold"; Behavior::teaches() default true; registry.teaches(name)
│   └── teacher.rs         # decide_action made reachable by needy.rs (pub(crate) already); no behaviour change
├── config/
│   ├── needy.rs           # NEW: NeedyConfig (+ defaults), OnsetLevels, floors keyed by need; validation
│   ├── mod.rs             # Config.needy: Option<NeedyConfig> skip-if-none; validate position 22
│   ├── validate.rs        # validate_needy (FR-008 rules; N from NeedKind::ALL.len())
│   └── welfare_hazard.rs  # HazardMode::{Needy, NeedyHold}; ALL; name(); activation() = first seat by behavior name; ALL-exhaustive test (N4)
├── kitty.rs               # Kitty.needy: Option<NeedyState> (#[serde(default, skip_serializing_if)])
├── needy.rs               # NEW: NeedyState, Episode, Phase, schedule law (sub-stream, draws, advance), relief map
├── world.rs               # try_generate: init needy state for needy seats; Phase 4: advance_needy after advance_needs; needy_verdict after consent_verdict (both sites: served loop + apply_slot_verdict); available_friend_in: masked partner rule
└── action.rs              # partner_relief(action) -> Option<NeedKind> (ONE table, cross-checked against apply_activity_effects)

crates/cloudkitty-py/src/lib.rs      # ParallelEnv.needy() -> list of (kitty_id, [need names], ordinal, phase) beside recent_meows()
crates/cloudkitty-py/tests/test_parallel_env.py  # accessor: absent → [], present → agrees with the schedule
experiments/tools/bc-collect/src/main.rs   # skip + log seats with registry.teaches(name) == false (Experiments' lane: cross-lane with consent, else theirs)
CHANGELOG.md
```

**Structure Decision**: the schedule law gets its own engine module
(`core/src/needy.rs`) with a porting-grade contract, like `starts.rs`
(062) and `init_needs.rs` (065); the behaviour preset is a thin wrapper
in `behavior/needy.rs` that reuses `Teacher::GEN2`'s ladder. The mask's
enforcement is in `world.rs` beside the consent gate, the one place the
apply slot already judges proposals about a target.

## Complexity Tracking

None: no constitution gate needs a justification. One deliberate
redundancy is recorded in research D7 (the mask enforced in the engine
AND read by the preset's ladder): the engine half is the law, the
behaviour half is advice quality; a test pins that removing the
behaviour half changes no outcome's legality, only the proposer's wasted
turns.
