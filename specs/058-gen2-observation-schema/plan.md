# Implementation Plan: Gen 2 Observation Schema Bump

**Branch**: `product/schema-bump` | **Date**: 2026-10-09 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/058-gen2-observation-schema/spec.md`

## Summary

One schema wall carrying every ruled Gen 2 observation change:
Manhattan bearing + two-scale magnitude for all spatial features
(frozen literals 40/400), four wall-distance cells replacing
fractional position, hidden friend needs (five of six — bath stays)
and the happiness view-hole removed from the row layout, a 14-cell
self-only identity block extending the existing trait cells, the
clock dropped, waypoint bearing added, two inert dirt-reserve cells,
and a schema-version-keyed column map published through the binding.
Observation v5→6, global state v1→2, action/mask unchanged. Design
decisions in `research.md` (R1–R12); layout in
`contracts/observation-v6.md`.

## Technical Context

**Language/Version**: Rust (pinned by `rust-toolchain.toml`), PyO3
binding via maturin for the Python surface

**Primary Dependencies**: workspace crates only — `cloudkitty-core`
(config accessors, Lattice), `cloudkitty-rl` (observe, global_state,
schema_map new), `cloudkitty-py` (exports); no new external deps

**Storage**: N/A (schema constants in code; dials in toml config)

**Testing**: cargo test (workspace), proptest-style randomized encodes
where the suite already uses them, `scripts/mutate.sh --expect` for
every new assertion (rule 5), config sweeps for the new toml keys

**Target Platform**: server crates + Python binding, as today

**Project Type**: single Rust workspace, existing layout

**Performance Goals**: encoder stays a per-tick pure function; +~24
self cells and −5 per row are noise at current roster sizes — no
budget change

**Constraints**: determinism (Article V) — encoder remains a pure
function of (FogView, config); frozen literals 40/400 deliberately
NOT config (ruled, spec-049 pattern); served Gen 1 world byte-stable
on schema 5

**Scale/Scope**: ~6 source files in `cloudkitty-rl`/`-core`/`-py`,
1 new module (`schema_map`), 1 new pins test, config validator
additions; no serving/deploy changes

## Constitution Check

*GATE: evaluated pre-Phase 0; re-evaluated post-Phase 1 — PASS both.*

- **Art. I–III (suffering/death/alone)**: untouched — no needs,
  relief, spawn, or roster semantics change. The observation is a
  read-only projection.
- **Art. IV (engine is law)**: untouched — proposal validation, menu,
  and mask semantics unchanged (action/mask versions hold).
- **Art. V (deterministic, server-authoritative)**: preserved — the
  encoder stays a pure function of the frozen snapshot; the Lattice
  waypoint derivation is stateless from config (research R4); no new
  RNG.
- **Art. VI (spec-first, constants in config)**: this spec; one
  deliberate deviation logged in Complexity Tracking — the frozen
  normalizer literals.

## Project Structure

### Documentation (this feature)

```text
specs/058-gen2-observation-schema/
├── plan.md
├── research.md          # R1–R12 decisions
├── data-model.md        # blocks, widths, accessors, version pins
├── quickstart.md        # validation scenarios 1–10
├── contracts/
│   └── observation-v6.md
├── checklists/requirements.md
└── tasks.md             # /speckit-tasks output (not this command)
```

### Source Code (repository root)

```text
crates/cloudkitty-core/src/
├── config/mod.rs        # comfort_slack_for / consent_line_for /
│                        #   favourite_weight_for accessors (R5)
├── config/validate.rs   # range checks for the new dials
└── behavior/mod.rs      # served_clock removal (R9)

crates/cloudkitty-rl/src/
├── observe.rs           # v6 encoder: spatial groups, walls, identity,
│                        #   row removals, waypoint, reserve, no clock
├── global_state.rs      # v2: identity extension per kitty
├── schema_map.rs        # NEW: column_map(version), v5 literal table
└── config.rs            # ObservationConfig additions if any

crates/cloudkitty-rl/tests/
├── schema_five_pins.rs  # FROZEN v5 oracle (validates map's v5 table)
├── schema_six_pins.rs   # NEW: every v6 offset literal
└── (row visibility / size invariance / reserve / no-clock /
     overshoot tests per quickstart)

crates/cloudkitty-py/src/lib.rs  # COLUMN_MAPS + ACTION_MENU exports
```

**Structure Decision**: existing workspace layout; the only new file
homes are `schema_map.rs` and the new test files.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Art. VI "constants live in configuration": 40, 400, slack/40, consent/100 are frozen code literals | Ruled (owner 2026-09-25 "Approved"; spec-049 precedent for time normalizers): a config change must never move an observation's meaning — the constants ARE the schema | Config-sourced normalizers re-create the size/reprice entanglement this spec exists to remove |

## Phase 0 / Phase 1 outputs

- `research.md` — all unknowns resolved (R1 metric, R2 removal form,
  R3 strip list, R4 waypoint, R5 identity/accessors, R6 encoder-level
  hiding, R7 version set, R8 column map, R9 clock, R10 reserve,
  R11 vocab flags, R12 heard rows). No NEEDS CLARIFICATION remain.
- `data-model.md`, `contracts/observation-v6.md`, `quickstart.md` —
  generated.

## Cross-spec coordination (for /speckit-tasks)

- **Spec 059 (teacher rework)** consumes the identity-dial accessors
  (R5) and owns the rule-5 audit of teacher reads; 058 does NOT touch
  behavior-rule reads (R6). The consent_line extension's call-site
  flips are 059's.
- **Experiments lane**: flipping `experiments/` readers onto
  `COLUMN_MAPS` is theirs, after this merges (relay thread,
  2026-10-09).
- **Reported, not fixed**: the plugin advisor wire serializes visible
  friends' full state (research R6) — surfaced to the owner; out of
  scope here.
