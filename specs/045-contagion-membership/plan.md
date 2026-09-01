# Implementation Plan: Contagion Membership Dial + Charge-Aware Ladder

**Branch**: `045-contagion-membership` | **Date**: 2026-08-31 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/045-contagion-membership/spec.md`

## Summary

Two lab-facing dials for the water's-edge avoidance smoke, both inert at
defaults. (1) `[water] contagion_membership` — a two-variant enum
branching only the `contagious`-set construction in `advance_needs`:
`option_a` (default, the shipped 044 rule — the dry namer pays) or
`bidirectional` (any dry member of a wet/dry adjacent pair pays, either
role, one charge per tick via the existing BTreeSet). (2) `[behavior]
contagion_aware_ladder` — a bool gating scene-total expected-exposure
pricing (charge × duration-bounds-MINIMUM (amended per Experiments review — see research D5), engine-faithful ceiling step, per the
clarified scene-total ruling) at the scripted chooser's three seams:
the selection score, the playmate ranking, and groom initiation.
Byte-identical launch proven the 044 way (stamp, golden,
explicit≡absent, seeded-run equality).

## Technical Context

**Language/Version**: Rust (workspace-pinned via `rust-toolchain.toml`)

**Primary Dependencies**: serde/toml (config), existing engine internals — no new crates

**Storage**: TOML config only; no runtime state, no persistence changes

**Testing**: cargo test — unit (config, validate, behavior), integration (`tests/waterline_contagion.rs` extension, behavior seeded-run equality), golden (`evolution_golden`), both config sweeps

**Target Platform**: engine crate (`cloudkitty-core`) + one boot-log line (`cloudkitty-server`); client untouched

**Project Type**: library/server workspace (existing)

**Performance Goals**: no regression — membership adds one pre-collected BTreeMap per tick only when factor > 0; ladder arithmetic only when its gate is on (lab worlds)

**Constraints**: byte-identical at defaults (stamp `6c73f894…` unmoved, golden unregenerated, explicit-default ≡ absent); no legality/mask/refusal change; no new RNG; served TOML untouched

**Scale/Scope**: ~6 files (config/mod.rs, validate.rs, world.rs, behavior/selection.rs, behavior/needs_driven.rs, server main.rs) + tests + docs

## Constitution Check

*GATE: evaluated pre-Phase-0 and re-checked post-design — **PASS** both times.*

- **Article I (no suffering)**: membership never raises the per-cat
  per-tick charge maximum (one charge, same magnitude, same ceiling
  gate — FR-003/FR-008), so the 044 headroom law keeping the safeguard
  unreachable by water stands verbatim; asserted by a
  membership-invariance test arm on `validate_water`.
- **Article II/III (no death, never alone)**: untouched.
- **Article IV (engine is law, behaviors advise)**: the membership dial
  is engine law (need accrual); the ladder changes only what the
  built-in advisor PROPOSES — legality, masks, refusal, and fallback
  resolution untouched. Declining a groom is a different proposal, not
  a new refusal class.
- **Article V (deterministic, server-authoritative)**: no new RNG; BTree
  ordering; same-seed determinism asserted per dial combination; all
  logic server-side.
- **Article VI (spec-first, config-not-magic)**: this plan; both dials
  are config with documented defaults; duration expectation reuses the
  existing `[durations]` config rather than baking measured constants
  into code.

## Project Structure

### Documentation (this feature)

```text
specs/045-contagion-membership/
├── spec.md
├── plan.md              # this file
├── research.md          # D1–D9
├── data-model.md
├── quickstart.md
├── contracts/
│   └── config-surface.md
├── checklists/requirements.md
├── redden-list.md       # created at implementation (044 discipline)
└── tasks.md             # /speckit-tasks output
```

### Source Code (repository root)

```text
crates/cloudkitty-core/src/
├── config/mod.rs        # ContagionMembership enum + WaterConfig field;
│                        #   BehaviorConfig.contagion_aware_ladder + bool_is_false;
│                        #   stamp/parse-equality/serde-error tests
├── config/validate.rs   # membership-invariance assertion on the budget (test-side; no new arithmetic)
├── world.rs             # advance_needs: bidirectional arm of the contagious-set
│                        #   filter (wet_namers BTreeMap); unit differential test
└── behavior/
    ├── selection.rs     # expected_scene_exposure helper; scored() + play_score() seams
    └── needs_driven.rs  # groom_response seam (decline when exposure > groomee bath pressure)

crates/cloudkitty-core/tests/
├── waterline_contagion.rs  # bidirectional differential arms per paired kind;
│                           #   multi-payer single-charge; determinism combos
└── (behavior seeded-run equality lives with the behavior unit tests)

crates/cloudkitty-server/src/main.rs  # boot log: membership named on the armed line;
                                      #   ladder line only when gated on

docs/wet-fur-pricing.md  # membership + ladder paragraphs; budget-invariance note
```

**Structure Decision**: existing workspace layout; no new files outside
tests — both dials extend the modules that own their seams (044
precedent: config surface in `config/mod.rs` with tests in-module per
repo idiom, charge law in `world.rs`, chooser pricing in
`behavior/selection.rs` which already owns every pricing site).

## Phase 0 → research.md

All unknowns resolved (D1–D9): dial homes and serde shapes, the
engine-branch construction, the exposure formula (scene-total,
engine-faithful ceiling step), duration source (bounds MINIMUM per research D5, zero new dials),
the three ladder seams, boot log, validation/budget invariance,
delivery discipline. The exposure value model (D4–D6) is flagged for
Experiments' review per the handoff — sent at plan time; the cap and
duration source are the expected adjustment points.

## Phase 1 → data-model.md, contracts/, quickstart.md

Generated. Key design commitments:

- No new runtime state; membership set rebuilt per tick, exposure
  computed per decision.
- FR-003's one-charge cap is structural (BTreeSet), not logic.
- Ladder off = short-circuit BEFORE arithmetic (structural
  byte-identity), mirroring the 043 gate-equality proof.
- Two commits planned (044 shape): (1) config surface inert + stamp
  proofs; (2) engine branch + ladder + tests + docs. Redden-list
  maintained throughout.

## Complexity Tracking

No constitution violations; table not needed.
