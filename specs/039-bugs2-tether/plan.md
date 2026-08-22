# Implementation Plan: Bugs 2.0 — the roam-cell tether

**Branch**: `039-bugs2-tether` | **Date**: 2026-08-21 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/039-bugs2-tether/spec.md`

## Summary

Confine each bug to the world-aligned cell it was born in (configurable
cell size, served world adopts 4×4), raise both critter lifetimes 300 →
600 in the served config, change nothing else. The mechanism is
stateless — a bug's cell is derived from its position by integer
division, so ragged edges, old saves, and determinism all come free.
The engine proves confinement and inertness; Experiments' pre-registered
chase-census grid proves the economics on this branch before merge
(FR-010 division of proof).

## Technical Context

**Language/Version**: Rust (workspace toolchain, as pinned by the repo)

**Primary Dependencies**: none new — `cloudkitty-core` only (element,
world, config); serde/toml already in tree

**Storage**: none — deliberately no new persisted state (FR-007); the
snapshot format is untouched

**Testing**: cargo test (workspace suite); seeded property runs for
confinement; a golden evolution digest for inertness; mutation passes
per CLAUDE.md rule 6

**Target Platform**: the served Linux box + dev machines, unchanged

**Project Type**: existing Rust workspace, engine crate only — no
client, server-API, or RL-crate changes

**Performance Goals**: no measurable tick-time movement; the added work
is four integer divisions per bug move attempt (3 bugs/world)

**Constraints**: byte-identical world evolution when the key is absent
(FR-009/SC-002); no RNG draw-count change (FR-003); fingerprint
unmoved (FR-007); `engine_defaults_sha256` unmoved (D5); scripted
behaviors and all cat decision rules byte-frozen (FR-008)

**Scale/Scope**: ~1 predicate + 1 config field + validation + served
toml values; the bulk of the arc is its test battery

## Constitution Check

*GATE: evaluated against constitution v1.2.0.*

- **Article I (no suffering)**: PASS — element movement only; needs,
  relief, and safeguard machinery untouched. Bugs remain a play
  resource; the safeguard's relief guarantee is unaffected (play is
  satisfiable by critters or friends; critter counts don't change).
- **Article II (kitties cannot die)**: PASS — expiration continues to
  apply to elements only; lifetime 600 is a value change inside the
  already-constitutional element-expiry mechanic.
- **Article III (never alone)**: PASS — no roster or kitty-count
  surface touched.
- **Article IV (engine is the law)**: PASS — no behavior/proposal
  surface touched; the tether binds the environment phase, not
  advisors.
- **Article V (deterministic, fair, fixed tick order)**: PASS with
  design attention — the tether lives inside environment resolution
  (tick phase 3), draws no extra RNG (the direction draw happens
  exactly as today; an outward draw is a lost step, never a redraw),
  and preserves seed-determinism. FR-009's golden test guards it.
- **Article VI (spec-first, test-guarded, no magic numbers)**: PASS —
  this plan follows the spec; the cell size is configuration with a
  documented default (absent = unbounded), never a code constant.

Post-design re-check: no violations introduced by Phase 1 artifacts.

## Project Structure

### Documentation (this feature)

```text
specs/039-bugs2-tether/
├── plan.md              # This file
├── research.md          # Phase 0: decisions D1–D7 with precedents
├── data-model.md        # Phase 1: roam cell, config field, validation
├── quickstart.md        # Phase 1: runnable validation scenarios
├── contracts/
│   └── roam-config.md   # Phase 1: config surface + partition semantics
└── tasks.md             # Phase 2 (/speckit-tasks — not created here)
```

### Source Code (repository root)

```text
crates/cloudkitty-core/src/
├── grid.rs              # + same_roam_cell(a, b, cell) pure predicate
├── world.rs             # move_critters: Bug arm gains the cell check
├── config/mod.rs        # ElementRule + roam_cell: Option<u32>
│                        #   (serde default + skip_serializing_if None)
└── config/validate.rs   # refuse roam_cell < 2; refuse on non-bug types

cloudkitty.toml          # [elements.bug] roam_cell = 4, ttl = 600;
                         # [elements.greeble] ttl = 600; comments
CHANGELOG.md             # Unreleased entry (markers: none claimed —
                         # neutrality proven, see research D7)

crates/cloudkitty-core/  # tests: partition properties, confinement
  (unit + integration     #   property run, golden inertness digest,
   tests in-crate)        #   cadence count, validation refusals,
                         #   old-save adoption
```

**Structure Decision**: single-crate change inside the existing
workspace; no new crates, files only where the feature's seams already
live (grid geometry in grid.rs, environment phase in world.rs, config
in config/).

## Phase 0: research.md

Seven decisions, each grounded in an in-repo precedent — see
[research.md](research.md). Headlines: D1 stateless partition by
integer division (ragged edges free); D2 the check rides the Bug arm
after the direction draw (draw counts preserved); D3 `roam_cell` on
`ElementRule` mirroring the `servings` "one type honors it" pattern
but with strict validation (newer house culture); D4 lifetimes change
in the served toml only, engine defaults untouched; D5 stamp
neutrality via `skip_serializing_if` (guarded by the existing stamp
test); D6 golden evolution digest generated on main for the inertness
proof; D7 CHANGELOG marker honesty (no markers, neutrality proven).

## Phase 1: data-model.md, contracts/, quickstart.md

- [data-model.md](data-model.md): the roam cell (derived, unpersisted),
  the config field with validation rules, and the explicit statement of
  what does NOT change (Element struct, snapshot schema, fingerprint,
  observation surface).
- [contracts/roam-config.md](contracts/roam-config.md): the
  configuration surface as an external interface — key name, type,
  legality, partition semantics including ragged edges and
  world-smaller-than-cell, absent-means-today, and the served package
  values.
- [quickstart.md](quickstart.md): runnable scenarios proving
  confinement, inertness, ragged-edge behavior, validation refusals,
  and old-save adoption — plus the handoff point where Experiments'
  branch-build census grid takes over (SC-004) and the re-baseline
  gate (SC-005).

## Sequencing rider (from the spec, binding on implementation)

Implementation may complete on this branch at any time, but the PR
does not open for merge until (a) the phase-1 `--fresh` has run on the
box and (b) Experiments' acceptance grid passes on a build of this
branch. The merge then carries the served-config package (clarified
2026-08-21). The deploy that makes the box serve it remains a separate
owner-gated act.
