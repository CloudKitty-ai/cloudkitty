# Implementation Plan: Parameterized Teacher Rework

**Branch**: `product/teacher-rework` | **Date**: 2026-10-10 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/059-teacher-rework/spec.md`
(post-clarify, three sessions logged), the 2026-10-10 consent re-key
ruling (eb9e860b, merged into this branch at 0c8bc6e2), and the code
survey recorded in research.md (all file:line anchors verified in this
worktree).

## Summary

Replace the `playful` and `needs_driven` brains with ONE `Teacher`
behavior whose decisions read the per-kitty identity dials through the
same config accessors the observation encoder uses. The old names
survive as preset registrations of the same Teacher. Consent moves out
of the proposer entirely: a target-side, engine-validated gate at the
apply slot (ruling eb9e860b), deliberately invisible to the RL legal
mask. Cue-answer response terms (`cuddle_response`, `play_response`)
join the teacher's ladder, keyed to digest-visible want-calls with the
FR-016 contention rule. Every hidden-state read a teacher decision
makes today is removed or re-keyed to digest/visible signals, with a
per-site audit record and a fire counter over the reference replay.

## Technical Context

**Language/Version**: Rust (workspace toolchain pinned by
`rust-toolchain.toml`; any new root toml reddens two config sweeps)

**Primary Dependencies**: `cloudkitty-core` (behavior, config, world),
`cloudkitty-rl` (mask, observe — read-only contract here: the 058 wall
stands, no observation change), `cloudkitty-py` bindings (pytest suite
is part of the local merge gate), `experiments/tools/bc-collect`
(reads behavior names; corpus labeling caveat recorded in research R9)

**Storage**: N/A (no serialization change: the slack gate reuses
`Kitty::last_relief_tick`, already serialized)

**Testing**: `cargo test` per crate + workspace; `scripts/mutate.sh
--expect` for every new/changed guard (rule 5); binding pytest via a
fresh `maturin develop` (the scratchpad ckpy venv is stale);
deterministic reference recorder (fog_continuity `record_streams`
pattern) for SC-001

**Target Platform**: server binary + python binding, as today

**Project Type**: single Rust workspace, engine-internal feature

**Performance Goals**: no regression on the tick loop; the consent
check is O(1) per partnered proposal; contention scoring is O(callers)
per decide

**Constraints**: determinism (Article V — no new RNG stream; the
needs_driven wander draw preserved exactly, including its
short-circuit order); byte-equality on the reference suite outside
consent sites (SC-001); no observation/schema change (058 wall);
constants derived from existing config or added as documented config
keys (Article VI)

**Scale/Scope**: ~6 source files in cloudkitty-core, 1 constant
relocation touching cloudkitty-rl, 1 new config key, no toml edits to
the 244 tracked configs (SC-006)

## Constitution Check

*GATE: evaluated pre-Phase-0 and re-evaluated post-design — PASS both.*

- **Article I (no suffering)**: no need semantics change. The consent
  refusal is a blocked proposal, not a punishment; distress machinery
  untouched. PASS.
- **Article II (no death)**: untouched. PASS.
- **Article III (never alone)**: untouched. PASS.
- **Article IV (engine is the law)**: strengthened — this is the
  article the consent re-key lives in. The target-side gate is engine
  validation at the apply slot; a refused proposal resolves to the
  existing safe outcomes (idle, or the ongoing scene when absorbed —
  `world.rs:352-376`), never an error state. The teacher remains an
  untrusted advisor; `NeedsDriven`-equivalent fallback totality is
  preserved by registering the needs_driven preset as the fallback
  instance (research R1). PASS.
- **Article V (deterministic, fair)**: no new RNG; the one existing
  behavior RNG draw (wander) keeps its exact draw order per preset
  (research R2). The consent gate reads the live mid-tick world
  exactly as `action::validate` does today — same authority, same
  slot. Response terms and contention scoring are pure functions of
  the snapshot. PASS.
- **Article VI (spec-first, config constants)**: k, D_w, I_min are
  derived relations from existing config
  (`announce_threshold`, `digest_window_ticks`, 1 tile/tick); the one
  genuinely new constant (`response_commitment_ticks`, the FR-016
  margin h in ticks) becomes a documented `[behavior]` config key
  with default 3 rather than a magic number. PASS.

## Project Structure

### Documentation (this feature)

```text
specs/059-teacher-rework/
├── plan.md              # This file
├── research.md          # Phase 0: survey findings + 14 decisions
├── data-model.md        # Phase 1: entities, config keys, state
├── quickstart.md        # Phase 1: validation guide (SC-001..006)
├── contracts/
│   ├── presets-and-dials.md   # FR-002's citable preset→dial table
│   ├── consent-gate.md        # target-side gate contract (eb9e860b)
│   ├── cue-answer.md          # FR-010/011/016 formulas + derivations
│   └── audit-record.md        # FR-007 per-site resolutions + FR-015 fire counter
└── tasks.md             # Phase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
crates/cloudkitty-core/src/
├── behavior/
│   ├── mod.rs           # registry: presets + "teacher" entry; fallback
│   ├── teacher.rs       # NEW: the one parameterized teacher (ladder)
│   ├── needs_driven.rs  # shrinks: logic moves to teacher.rs; groom_response + finish_what_you_started move with it
│   ├── playful.rs       # shrinks: logic moves to teacher.rs (luxury rung)
│   └── selection.rs     # consent filters removed; partner_value re-keyed; response-term valuation
├── config/
│   ├── mod.rs           # slack_cell_for; response_commitment_ticks; COMFORT_SLACK_NORMALISER moves here
│   └── validate.rs      # new key validation joins the shared loop
├── action.rs            # (unchanged validate; refusal_reason gains consent arm)
├── events.rs            # RefusalReason::ConsentDeclined (wire enum — tools note)
└── world.rs             # consent step in run_applied_phases_from_decisions + apply_slot_verdict

crates/cloudkitty-rl/src/
├── observe.rs           # slack cell reads core's slack_cell_for (value unchanged; pins stay green)
└── mask.rs              # UNCHANGED by design — consent-blind, documented

crates/cloudkitty-core/tests/   # preset byte-equality recorder, consent gate guards,
                                # response-term guards, evolution_golden (must stay green)
crates/cloudkitty-rl/tests/     # schema pins stay green; mask consent-blindness guard
```

**Structure Decision**: engine-internal rework inside the existing
workspace; one new source file (`behavior/teacher.rs`), no new crates,
no client/experiments-lane files (bc-collect finding is relayed, not
fixed — rule 3).

## Complexity Tracking

No constitution violations to justify. One deliberate complexity:
preset rung TOGGLES alongside the four dial groups (research R1) —
forced by FR-002's byte-equality against two structurally different
ladders; rejected alternative (dials-only) cannot reproduce
needs_driven's RNG-drawing wander rung or playful's missing
groom-response without one preset losing byte-equality.
