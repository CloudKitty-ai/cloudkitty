# Implementation Plan: Per-Target Play Relief

**Branch**: `025-play-relief-split` | **Date**: 2026-08-02 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/025-play-relief-split/spec.md`

## Summary

One bounded dynamics change: split the uniform `play_relief` (20) by
play target. Two new serde-defaulted keys on `ActionEffects`
(`play_relief_bug = 25`, `play_relief_greeble = 35`); the
`Activity::Playing { Element }` effect arm (`action.rs:712-714`) gains
an effect-time element lookup that routes bug→bug, greeble→greeble,
and anything else — a despawned id or (defensively) a non-critter —
to `solo_play_relief`; and `validate_actions` (`validate.rs:542-562`)
grows from the single solo-vs-play guard into the strict four-value
chain plus the duet ceiling `greeble < 2 × play_relief`, both with
errors that teach the economics. The duet and solo arms are
byte-for-byte untouched. This is the generation's second and final
planned comparability break: `engine_defaults_sha256` moves by
construction (it hashes `Config::default()`'s canonical JSON —
`suite.rs:169-178`), `run-json.golden.json` regenerates once, and
`welfare_longrun` re-verifies (floors expected to gain margin).

## Technical Context

**Language/Version**: Rust (stable workspace toolchain), no new dependencies

**Primary Dependencies**: existing workspace crates only — `cloudkitty-core` (engine + config), `serde`/`toml` (config parsing)

**Storage**: none new — no world state added; snapshot format untouched (relief values are dynamics, not state)

**Testing**: `cargo test --workspace`, golden regeneration via `UPDATE_GOLDENS=1`, pytest surface unaffected (no schema change)

**Target Platform**: unchanged (server binary + headless test drivers)

**Project Type**: mini engine spec — one dynamics change in `cloudkitty-core`

**Performance Goals**: the effect-time lookup is one `world.element(id)` scan per Playing{Element} serviced tick — same cost class as the Eating arm's `adjacent_stocked_chow` lookup (`action.rs:681`); no measurable tick-time impact

**Constraints**: observation dim 182 / action codec 40 untouched (asserted by existing tests); RNG draw shape untouched (no randomness in the effect body); served `cloudkitty.toml` not edited; frozen exam configs stay byte-identical and valid (serde defaults, no `deny_unknown_fields`); hash pins untouched; `/config` payload changes additively only (two new keys)

**Scale/Scope**: 3 source files in core (`config/mod.rs`, `config/defaults.rs`, `config/validate.rs`) + the one match arm in `action.rs`; tests beside their subjects; goldens regenerated; ~small-hundreds of lines including tests

## Constitution Check

*GATE: evaluated against constitution v1.2.0 before Phase 0; re-checked after Phase 1.*

- **Article I (no suffering)**: PASS. Relief magnitudes only ever
  *lower* need pressure through the clamped `Need` type ("Article I
  holds no matter what magnitudes the config carries" —
  `action.rs:402-403`). Larger relief values cannot create distress;
  the relief guarantee is untouched (play's relief sources don't
  change shape, only per-tick magnitude).
- **Article II (no death)**: PASS — element expiry (the despawn edge)
  is already lawful for environment elements and this spec only reads
  it; nothing touches kitty existence.
- **Article III (never alone)**: PASS — untouched.
- **Article IV (engine is the law)**: PASS. Proposal validation is
  unchanged (`Action::Play` legality, `action.rs:382-392`, is not
  touched); only the effect magnitude of an already-legal activity
  routes differently. No advisor surface changes.
- **Article V (deterministic, fair)**: PASS. The effect body draws no
  randomness; the lookup reads world state already fixed by the tick's
  phases. Config values change outcomes, never draw shape (the
  fixed-shape rule is not implicated — no RNG involved at all).
- **Article VI (spec-first, config constants)**: PASS. Both new
  constants are config keys with documented defaults; both guards are
  executable validators with tests, not prose; the spec precedes the
  code; CI gates unchanged.

**Post-Phase-1 re-check**: PASS. Design added no projects, no
dependencies, no state, no schema. The one semantics addition beyond
the handoff (despawn fallback → solo) is pinned in the spec and
surfaced in the plan report, not hidden.

## Project Structure

### Documentation (this feature)

```text
specs/025-play-relief-split/
├── plan.md              # This file
├── research.md          # Phase 0 output — R1..R6 decisions
├── data-model.md        # Phase 1 output — config entity + routing table
├── quickstart.md        # Phase 1 output — validation guide
├── contracts/
│   └── play-relief-split.md  # config keys, routing semantics, guards
└── tasks.md             # Phase 2 output (/speckit-tasks — NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
crates/cloudkitty-core/src/
├── config/mod.rs        # ActionEffects: two new fields + Default + doc re-scope of play_relief
├── config/defaults.rs   # default_play_relief_bug (25), default_play_relief_greeble (35)
├── config/validate.rs   # validate_actions: strict chain + duet ceiling (supersedes :551)
└── action.rs            # Playing{Element} arm: effect-time type lookup + solo fallback

crates/cloudkitty-core/tests/
└── welfare_longrun.rs   # re-verify (tighten-only bounds; floors expected to gain margin)

crates/cloudkitty-rl/tests/goldens/
└── run-json.golden.json # regenerate once (UPDATE_GOLDENS=1) — the break's visible mark
```

**Structure Decision**: everything lands beside the code it changes, in
the files above — no new modules, no new test files except where a
routing test naturally extends the existing `action.rs` test module and
the existing config tests in `config/mod.rs`. The `engine_defaults_sha256`
stamp moves automatically (it hashes compiled defaults, `suite.rs:169`);
no pin file exists to edit, and `harness_policy.rs:406` only asserts the
key's presence.

## Complexity Tracking

No constitution violations; table not needed.
