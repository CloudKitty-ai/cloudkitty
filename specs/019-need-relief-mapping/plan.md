# Implementation Plan: Need→Relief Mapping — One Source of Truth for the Baseline Cat

**Branch**: `019-need-relief-mapping` | **Date**: 2026-07-26 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/019-need-relief-mapping/spec.md`

## Summary

The need→relief correspondence is encoded independently in three consumer
steps of the built-in behavior stack: `selection::distance_given` prices
each need's relief source, `needs_driven::pursue` walks to and uses it,
and `needs_driven::take_what_is_here` opportunistically grabs it when
adjacent. The plan centralizes the *pairing* — which relief shape and
which action belong to each need — as one `ReliefSource` definition per
`NeedKind` in a new `behavior/relief.rs`, and rewrites the three consumers
to match on relief *shapes* (element, sunbeam terrain, playmate, friend,
in-place) instead of needs. Adding a need that reuses an existing shape
then costs exactly one entry at one site, and the compiler forces the
definition (exhaustive over `NeedKind`) while the shape arms cover every
consumer. Behavior is preserved bit-identically: same predicates, same
evaluation order (the emergency ladder becomes an explicit ordered
constant), same tie-breaks, zero RNG changes — verified by the
determinism suite, welfare gates, unchanged tests, and byte-identical
certification + suite reruns against pre-refactor main.

## Technical Context

**Language/Version**: Rust (workspace toolchain, edition 2021)

**Primary Dependencies**: `cloudkitty-core` only (the behavior module refactors within itself); `cloudkitty-rl` used solely for verification reruns

**Storage**: N/A — no serialization, snapshot, or config surface touched

**Testing**: `cargo test --workspace` (determinism suite, long-run welfare gates, behavior property tests — all must pass with zero assertion changes); byte-identical `kitty-eval` reruns per quickstart

**Target Platform**: unchanged (developer machines + CI)

**Project Type**: internal engine-crate refactor, single module cluster

**Performance Goals**: unchanged — a shape-enum dispatch replaces direct match arms; no new allocation, no new iteration

**Constraints**: bit-identical decisions (FR-004): every predicate, threshold comparison, evaluation order, tie-break, and RNG draw shape must survive exactly; knowledge moves, logic does not

**Scale/Scope**: `behavior/needs_driven.rs` (~1,023 lines), `behavior/selection.rs` (~991), one new ~70-line `behavior/relief.rs`; no other files

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Article I–III (welfare, immortality, companionship)**: PASS — no
  mechanic changes; the long-run welfare gates re-verify Article I's
  guarantees over the refactored behavior (FR-005).
- **Article IV (engine is the law)**: PASS — the refactor stays inside
  the advisor (behavior) layer; validation and enforcement are untouched.
  Note: the engine's own action-validation rules independently encode
  what's *legal*, not what the cat *prefers* — this feature deliberately
  does not attempt to unify policy with law (out of scope by spec).
- **Article V (deterministic simulation)**: PASS and load-bearing —
  FR-004's bit-identical bar is Article V applied as the acceptance
  criterion; the plan preserves RNG draw count/order by construction
  (no draw sites are touched).
- **Article VI (spec-first, test-guarded)**: PASS — spec 019 ratified and
  clarified (no critical ambiguities, 2026-07-26); FR-005 forbids
  weakening tests; no config constants involved.

**Post-Phase-1 re-check**: PASS — the design adds one crate-internal
module and rewires three functions; no article implicated.

## Project Structure

### Documentation (this feature)

```text
specs/019-need-relief-mapping/
├── plan.md              # This file
├── research.md          # Phase 0: decisions D1–D5
├── data-model.md        # Phase 1: ReliefSource shapes + consumer mapping
├── quickstart.md        # Phase 1: bit/byte verification procedure + walkthrough
└── tasks.md             # Phase 2 (/speckit-tasks — not created here)
```

No `contracts/` directory: the feature's entire surface is crate-internal
(`pub(crate)` within `cloudkitty-core`'s behavior module); the external
contracts that matter — the CLI's outputs and the engine's serialized
forms — are explicitly unchanged and verified so by the quickstart.

### Source Code (repository root)

```text
crates/cloudkitty-core/src/behavior/
├── mod.rs               # + `mod relief;` (crate-internal)
├── relief.rs            # NEW — ReliefSource enum + impl NeedKind::relief()
│                        #   (inherent impl in the same crate as needs.rs;
│                        #    the one authoritative definition, FR-001)
├── selection.rs         # distance_given matches ReliefSource shapes
├── needs_driven.rs      # pursue + take_what_is_here match ReliefSource
│                        #   shapes; emergency-ladder order becomes an
│                        #   explicit ordered constant beside the ladder
└── playful.rs           # untouched (shares take_what_is_here by call)
```

**Structure Decision**: one new crate-internal module holding the
definition; the three consumers keep their files and their logic. The
`impl NeedKind` block lives in `relief.rs` (legal: same crate as the
enum's definition in `needs.rs`), which satisfies the spec's "the way the
kitty module centralizes Activity mappings" pattern while keeping the
behavior-policy knowledge in the behavior layer rather than the engine's
data layer.

## Complexity Tracking

No constitution violations; table intentionally empty.
