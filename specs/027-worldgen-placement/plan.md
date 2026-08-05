# Implementation Plan: Worldgen Placement — Guaranteed Lake and Edge-Avoiding Spawns

**Branch**: `027-worldgen-placement` (stacked on `026-in-water-obs`) | **Date**: 2026-08-05 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/027-worldgen-placement/spec.md`

## Summary

One file carries the mechanics: `spawn.rs` gains a lake obligation
(ensure a 2×2 all-water square whenever water's minimum ≥ 4, reusing
surviving tiles when re-forming) and an interior preference (a
configurable perimeter penalty inside the existing best-of-N score),
and loses its last two magic numbers (`SPREAD_CANDIDATES`,
`TTL_JITTER`) to `[elements]` config keys. Behavior at a zero penalty
and default dials is draw-for-draw identical to today. The
engine-defaults stamp moves again — the batch's single re-baseline
follows both merges.

## Technical Context

**Language/Version**: Rust workspace (CI-pinned toolchain; fmt + clippy + test gates)

**Primary Dependencies**: `cloudkitty-core` only (spawn.rs, world.rs call sites, config). No other crate changes; no new dependencies.

**Storage**: TOML config (three new `[elements]` keys); snapshots unaffected — `Config::fingerprint` (size, seed, roster ids) does not include the new keys, so existing worlds resume.

**Testing**: `cargo test` workspace; new property-style seeded-sample tests for the lake guarantee and the perimeter-share reduction; existing spread/safeguard/TTL tests must pass unmodified (they assert semantics the spec preserves).

**Target Platform**: server binary; no client or python surface involvement (worldgen is server-side; the viewer just draws what is served — the 008 pond renderer already merges adjacent water).

**Project Type**: simulation engine internals.

**Performance Goals**: generation-time lake search is a one-shot scan (anchors = O(area)); per-restock it short-circuits on "a lake exists", cheap against tiny water counts. No hot-path cost in the default world: permanent water means the standing lake satisfies the exists-check every environment phase.

**Constraints**: Article V RNG discipline — every draw through the master RNG, and the *number* of draws in `pick_spread_tile` stays independent of world contents (the existing unconditional-draw comment at :117-118 is load-bearing); preference-never-constraint for every placement rule; frozen exams (`scarcity.toml` water min 1) must validate unchanged; element budgets untouched (handoff §3d).

**Scale/Scope**: ~1 source file + config trio (mod.rs/defaults.rs/validate.rs) + `cloudkitty.toml` comments + tests. Smaller diff than 026 despite the bigger behavioral change.

## Constitution Check

*GATE: evaluated against Constitution v1.2.0 before Phase 0; re-checked after Phase 1 — PASS both times.*

- **Article I (no suffering)** — PASS with care taken. The safeguard
  path (`spawn.rs:35`) is untouched: lake and edge logic live in the
  ordinary placement flow, and both are preferences that always yield
  a tile when one exists. The lake never evicts, stacks, or blocks; an
  unmet lake carries over exactly like an unmet minimum (the existing
  break semantics at `spawn.rs:20-23`). Water stays passable; relief
  reachability is unchanged.
- **Article II (no death)** — untouched.
- **Article III (never alone)** — untouched.
- **Article IV (engine is law)** — untouched; no behavior/advisor
  surface changes.
- **Article V (deterministic, fair)** — PASS by design. All new draws
  (lake anchor sampling) flow through the master RNG; `pick_spread_tile`
  keeps its unconditional draw count (the penalty is applied in
  *scoring*, drawing nothing); same seed + config → same world, lake
  included. The seeded-world *break* relative to pre-027 is the
  documented, expected consequence of new draws in the sequence — not
  a determinism violation.
- **Article VI (config, not code)** — PASS and *improved*: this spec
  closes the known gap (two simulation constants in code) that made
  the config header's "every number" claim false. The new keys carry
  documented defaults and validated bounds.

No violations; Complexity Tracking not needed.

## Project Structure

### Documentation (this feature)

```text
specs/027-worldgen-placement/
├── spec.md
├── plan.md              # this file
├── research.md          # Phase 0: mechanism decisions, verified anchors
├── data-model.md        # Phase 1: config keys, lake invariant, scoring
├── quickstart.md        # Phase 1: runnable checks per SC
├── contracts/
│   └── worldgen-guarantees.md   # the lake guarantee + preference contract
└── tasks.md             # Phase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
crates/cloudkitty-core/src/
├── spawn.rs             # the whole mechanical change:
│                        #  - ensure_minimums (:16) gains the lake
│                        #    obligation ahead of the water top-up
│                        #  - pick_spread_tile (:114) + best_spread (:143)
│                        #    learn the edge penalty (scoring only; draw
│                        #    count untouched per the :117 comment)
│                        #  - SPREAD_CANDIDATES (:104) and TTL_JITTER (:93)
│                        #    become config reads; jittered_ttl (:98)
│                        #    parameterized
│                        #  - tests: lake guarantee (seeded sample),
│                        #    re-formation, carry-over, edge-share,
│                        #    penalty-0 identity
├── world.rs             # no logic change: generate (:117) and
│                        # environment_phase (:734) already route through
│                        # ensure_minimums — one home serves both
└── config/
    ├── mod.rs           # ElementsConfig gains spread_candidates,
    │                    # ttl_jitter, edge_penalty (+ docs incl. the
    │                    # rule.max-is-validation-only note, FR-007)
    ├── defaults.rs      # default_spread_candidates()=8,
    │                    # default_ttl_jitter()=100,
    │                    # default_edge_penalty()=2.0
    └── validate.rs      # spread_candidates >= 1; edge_penalty finite,
                         # >= 0; lake feasibility (width/height >= 2 when
                         # active — explicit even though world-size floors
                         # already imply it)

cloudkitty.toml          # stale "32 for this world" cap comment -> real
                         # arithmetic (18 at 24x24); rule.max note; new
                         # keys documented at their defaults (comments
                         # only — values come from engine defaults)
```

**Structure Decision**: everything lands in `cloudkitty-core`; the new
keys live on `ElementsConfig` (table-level `[elements]` scalars beside
the per-type sub-tables) because all three govern element placement
and expiry — the same section an operator already reads for those
concerns.

## Complexity Tracking

No constitution violations to justify.
