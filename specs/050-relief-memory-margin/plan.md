# Implementation Plan: Relief Memory Margin (the fog want law's memory reach)

**Branch**: `050-relief-memory-margin` | **Date**: 2026-09-05 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/050-relief-memory-margin/spec.md` (3 user stories, 9 FRs, 7 SCs; owner ruled 2026-09-04; two clarifications 2026-09-05, no markers).

## Summary

One optional config key, `[meow] relief_memory_margin` (non-negative integer, absent = today's law), and one predicate change: a REMEMBERED element counts as known relief for a want-word only when its remembered tile lies within `[vision] radius + margin` Manhattan tiles of the cat's current position. Visible relief is unchanged; navigation is unchanged; the layout is unchanged (schema 5 stays 408 floats). The served `cloudkitty.toml` sets the key to 0, which makes the served want law "visible relief only" and revives `want_drink` (F-040: 0 → ~12 calls per 1,000 ticks). The compiled default leaves the key absent, so every default-keyed golden stays put and the defaults stamp does not move; the served r = 5 stream pins move once and are re-recorded from one run.

Technical approach: `known_relief` (meow.rs) gains the reach in its `remembered` closure, reading the margin passed in from `message_legal` (which already holds `config`) and the radius the `FogView` already carries — so the mask probe, the built-in announce ladder and the enforcement seam keep calling ONE predicate (FR-006) with no new plumbing. The key rides the 039-D5 skip-serialize discipline like `reply_intensity_floor`. Guards: the axis-aligned `r + 1` fixture in `meow.rs` unit tests (SC-001/002/006, the inclusive-Manhattan red-first pair the owner asked for), a new random-world property in `meow_law_fog.rs` that derives the verdict independently from position, memory tile, radius and margin (A14), and a new served-roster integration test counting `want_drink` calls and `here_water` replies over 1,000 ticks (SC-004).

## Technical Context

**Language/Version**: Rust, toolchain pinned by `rust-toolchain.toml` (no change). No Python change (the binding re-exports no config key; `observation_len` is untouched).

**Primary Dependencies**: `cloudkitty-core` only (config, meow law, one integration test, one stream re-pin). `cloudkitty-rl` is touched for a comment (welfare reading numbers) and nothing else; `cloudkitty-server`, `cloudkitty-py`: no change.

**Storage**: none. No snapshot, wire, artifact or exam width moves.

**Testing**: `cargo test --workspace --no-fail-fast` via `scratchpad/cycle.sh LABEL` (baseline at merge of 049: 884 / 0 / 6 ignored; re-read at cycle 0), fmt + clippy CI-exact, red-first per CLAUDE.md rule 5 recorded in `redden-list.md`; the ignored served welfare readings and the ignored preladder r = 5 recorder run once each.

**Target Platform**: unchanged. Nothing deploys in this arc; the served key lands on main and reaches the box at the step-7 cutover.

**Project Type**: Rust workspace, engine crate change.

**Performance Goals**: one Manhattan distance per remembered slot per want-legality probe (≤ 6 kinds × 5 slots per cat per tick across mask, announce and enforcement) — noise against the fog view build.

**Constraints**: determinism preserved (pure function of kitty position, memory, radius, margin; no RNG); Article V tick order unchanged; mask-oracle doctrine kept (mask and engine read the same predicate); one-serialization posture (the key is skip-serialized when absent, stamp unmoved); `LawEra::PreFog` reads no margin (FR-008); the frozen `evals/v2` files are NOT touched (spec 017 FR-012; the 049 s1 lesson).

**Scale/Scope**: 2 source files (`config/mod.rs`, `meow.rs`), 1 new integration test, 1 property test added to an existing file, 1 stream re-pin (2 fixture files), 1 comment update, the served TOML, 2 contracts, `docs/meows.md`, CHANGELOG, the redden list.

## Constitution Check

*GATE: evaluated pre-Phase-0 and re-checked post-design — PASS, no violations.*

- **Article I (Kitties Cannot Suffer)**: the change is speech legality only; what the world provides (safeguard, spawns, reachability) is untouched, and navigation still walks to the remembered pool (FR-005). A cat that may now *ask* for water is no worse off than one that could not. PASS.
- **Article II / III**: no population or roster mechanic touched. PASS.
- **Article IV (Engine Is the Law)**: the reach lives in `known_relief`, the engine's predicate; behaviours still only propose, and an illegal want downgrades to Silent at the seam exactly as today. PASS.
- **Article V (Deterministic)**: the predicate is pure; no draw; tick order unchanged. Same seed + config → same streams (the re-pinned r = 5 fixtures are that guarantee at the served key). PASS.
- **Article VI (Spec-First, Test-Guarded)**: the constant is configuration with a documented absence default; guarded by unit, property and served-roster tests, and the stream pin. PASS.

**Complexity Tracking**: no violations to justify.

## Project Structure

### Documentation (this feature)

```text
specs/050-relief-memory-margin/
├── spec.md              # 3 US / 9 FRs / 7 SCs; §Clarifications 2026-09-05
├── plan.md              # This file
├── research.md          # Phase 0: R1–R8 design decisions
├── data-model.md        # Phase 1: the key, the predicate, what moves
├── quickstart.md        # Phase 1: validation guide (guards, pins, readings, diff)
├── contracts/
│   └── relief-memory-margin.md   # the key, the reach rule, callers, records
├── checklists/requirements.md
├── redden-list.md       # implementation-time red-first record (house standard)
└── tasks.md             # Phase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
crates/cloudkitty-core/src/
├── config/mod.rs        # MeowConfig += relief_memory_margin: Option<u32>
│                        #   (serde default, skip_serializing_if none); doc comment;
│                        #   stamp test gains one `!json.contains(...)` line
└── meow.rs              # known_relief(want, kitty, view, margin): the `remembered`
                         #   closure reads Manhattan(kitty.pos, slot.pos) <= view.radius
                         #   .saturating_add(margin) when Some; message_legal passes
                         #   config.meow.relief_memory_margin; unit tests: the axis-aligned
                         #   r+1 fixture (SC-001/002/006), the bound, standing-on-tile
crates/cloudkitty-core/tests/
├── meow_law_fog.rs      # NEW property: the reach rule over random worlds and margins
│                        #   (independent oracle from pos/memory/radius/margin — A14);
│                        #   the existing property stays untouched (SC-003)
├── relief_memory_margin.rs   # NEW: served roster, r = 5, 1,000 ticks all-scripted:
│                        #   want_drink > 0 on the served toml verbatim; here_water
│                        #   replies > 0 with a test-only floor (0.01); eat/drink counts
│                        #   printed as readings (F-040 ~12)
├── fog_continuity.rs    # doc comment on reply_floor_unset_is_byte_identical: re-pinned
│                        #   for 050 (why + first divergence tick); no code change
└── fixtures/preladder-r5-20k.{actions,messages}.digest   # re-recorded ONCE
crates/cloudkitty-rl/tests/welfare_longrun.rs   # comment: served readings re-taken
cloudkitty.toml          # [meow] relief_memory_margin = 0 + comment block (FR-007);
                         #   the [meow] head comment's "visible or remembered" amended
specs/049-fog-gen1/contracts/meow-law-v5.md         # known-relief table: the reach
specs/049-fog-gen1/contracts/config-3.0-migration.md # new-keys row
docs/meows.md            # the law paragraph: "remembered within reach"
CHANGELOG.md             # Unreleased one-liner
```

**Structure Decision**: engine change confined to `cloudkitty-core`; the key is read at exactly one site (`message_legal` → `known_relief`), matching the spec's ONE-predicate requirement, and every downstream consumer (mask, announce ladder, enforcement) inherits it without edits.

## Complexity Tracking

No constitution violations; nothing to justify.
