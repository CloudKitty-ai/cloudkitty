# Implementation Plan: The `announce_here` Knob

**Branch**: `043-announce-here` | **Date**: 2026-08-30 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/043-announce-here/spec.md`; Experiments handoff `experiments/here-word-screen-handoff-2026-08-30.md`; screen design `experiments/here-word-density-screen.md`.

## Summary

Give the shared scripted announce rule (`behavior/mod.rs::announce`) a second, lower-precedence register: when no want-word claims the message slot, a cat may speak one of the four Here\* kinds — gated by a new `[behavior] announce_here` period knob (0/absent = off, the default), the cat's deterministic speaking phase, and the existing grounded legality funnel. Zero randomness anywhere in the path; knob-off is byte-identical (stamp and golden both unmoved); gate zero (actions identical off vs on) ships as an in-tree paired test so the property is CI-guarded forever, not observed once.

## Technical Context

**Language/Version**: Rust (workspace toolchain pinned by `rust-toolchain.toml`, spec #305)

**Primary Dependencies**: `cloudkitty-core` only — `serde` (config field), `sha2` (test-side digests, already a dev-dependency of the golden). No new crates.

**Storage**: N/A — FR-009: no new persistent state; the speaking phase derives from `(tick, kitty_id)`, so snapshots and resume are untouched.

**Testing**: `cargo test` (unit guards in `behavior/mod.rs` + `config/mod.rs`; one new integration test `tests/announce_here_gate_zero.rs`). House rules 5/6: every new guard shown red first for its predicted reason; redden list sorted before running.

**Target Platform**: The engine crate; no server, client, schema, or wire changes.

**Project Type**: Library (engine core).

**Performance Goals**: Announce runs per scripted kitty per tick; the here path adds at most one modulo check on non-phase ticks and four legality checks on phase ticks. No measurable budget concern.

**Constraints**: (1) Knob-off byte-identity: `engine_defaults_sha256` unmoved, golden evolution pin `7b361b2a…` stays green, full suite green unmodified. (2) Knob-on action-identity: gate zero. (3) No master-RNG draw in the decision path (Article V determinism is stronger than that — but the specific hazard is stream divergence via `gen_bool`). (4) Outside 041/042 surfaces and the fog wall.

**Scale/Scope**: One config field, one function extended, one new integration test, unit guards. Single PR, two commits (see Structure Decision).

## Constitution Check

*GATE: evaluated pre-Phase-0 and re-checked post-Phase-1 — PASS both times.*

- **Article I (no suffering)**: Messages carry no need effects; `emit_message` only stamps a cooldown and pushes to `recent_meows`. No welfare surface. PASS.
- **Article II (no death)**: Untouched. PASS.
- **Article III (never alone)**: Untouched. PASS.
- **Article IV (engine is the law)**: The knob governs scripted *proposal* only; the engine's message-legality enforcement at `world.rs:346` (illegal → Silent) rules every emission exactly as before. The knob adds candidates, never bypasses the funnel — FR-007 restates Article IV's shape. PASS.
- **Article V (deterministic, single seeded RNG)**: The here path draws nothing from the RNG; both derivations are pure functions of `(tick, kitty_id, legal set)`. Determinism is *strengthened* in the sense that the paired gate-zero test adds a standing action-projection witness. PASS.
- **Article VI (spec-first, config constants)**: The period lives in `[behavior]` with a documented default (0 = off); no magic numbers. Spec precedes code; FR-006 amended at plan time for the aliasing finding (research D3) before any implementation. PASS.

## Project Structure

### Documentation (this feature)

```text
specs/043-announce-here/
├── spec.md              # /speckit-specify output (FR-006 amended per research D3)
├── plan.md              # This file
├── research.md          # Phase 0: decisions D1–D8
├── data-model.md        # Phase 1: knob + HERE_KINDS + (no) state
├── quickstart.md        # Phase 1: validation guide
├── contracts/
│   └── announce-here-knob.md   # Config + message-channel + gate-zero contracts
└── tasks.md             # /speckit-tasks output (not created here)
```

### Source Code (repository root)

```text
crates/cloudkitty-core/src/
├── config/mod.rs        # BehaviorConfig.announce_here: u64 (serde default +
│                        #   skip_serializing_if = u64_is_zero, new helper);
│                        #   stamp-guard test gains the "announce_here" key
├── meow.rs              # MessageKind::HERE_KINDS: [MessageKind; 4] (stable order)
├── behavior/mod.rs      # announce(): want loop unchanged; here path appended
│                        #   (phase gate → legality filter → indexed pick);
│                        #   unit guards in the existing tests module
└── (unchanged)          # behavior/needs_driven.rs, behavior/playful.rs — their
                         #   decide() already calls the shared announce();
                         #   world.rs enforcement seam; action.rs emit_message

crates/cloudkitty-core/tests/
└── announce_here_gate_zero.rs   # NEW: paired off/on lockstep run — action
                                 #   projection digests equal, message streams
                                 #   differ with Here* present, want/WaitForMe
                                 #   streams identical (SC-002/SC-006)

cloudkitty.toml          # Commented documentation block for the knob (042 pattern;
                         #   value NOT set — served world launches knob-off)
CHANGELOG.md             # ## Unreleased entry (no [stamp] marker — stamp unmoved)
```

**Structure Decision**: Single PR on `043-announce-here`, two commits, both independently green:

1. **Config surface (inert)** — `announce_here` field + `u64_is_zero` helper + stamp-guard key + `HERE_KINDS` const + config unit guards. Stamp and golden provably unmoved (the field never serializes at 0 and nothing reads it yet).
2. **The here path + instruments** — `announce()` extension, behavior unit guards, the gate-zero integration test, `cloudkitty.toml` doc block, CHANGELOG. Golden stays green (knob-off default); the paired test is the knob-on witness.

## Complexity Tracking

No constitution violations; table not needed.
