# Implementation Plan: Policy Artifact v3 — Entity-Attention Format

**Branch**: `030-artifact-v3` | **Date**: 2026-08-13 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/030-artifact-v3/spec.md`

## Summary

Add a third policy-artifact version whose forward is a transformer encoder over
per-entity tokens with pointer action heads, serving on observation schema 3.
The container, behavior seam, codecs, masks, legality, and certification harness
are unchanged; only the version dispatch and the forward differ. The v2
Linear-ReLU path keeps serving byte-identically. The header carries the four
transformer hyperparameters and is authoritative, so a re-tuned model is an
artifact swap, not a rebuild. The Rust forward is hand-rolled scalar `f32`
matching the v2 no-BLAS determinism doctrine, certified against an
Experiments-supplied numpy oracle at ≤1e-4 max absolute logit error.

## Technical Context

**Language/Version**: Rust (workspace, existing toolchain). Python 3 for the
reference oracle, supplied by Experiments — not built here.

**Primary Dependencies**: None new. `serde`/`serde_json`, `sha2`, and `libc`
are already in `cloudkitty-rl`. No `ndarray`/`candle`/BLAS — the forward is
hand-rolled (FR-012).

**Storage**: Single artifact file in the existing `CKPOLICY` container (magic +
`u32` header length + JSON header + `f32` little-endian weight blob). A parity
fixture file accompanies it (raw-`f32` format defined in `contracts/forward-v3.md`).

**Testing**: `cargo test` in `cloudkitty-rl` — fixture-based load-and-serve,
one test per rejection class, and a parity harness reading the oracle rows. The
`cloudkitty-server` boot path is exercised by an integration test seating a v3
and a v2 policy together.

**Target Platform**: Linux server (production); macOS for development. Same-
binary reproducibility is the determinism contract; cross-platform bit-exactness
is not held (transcendentals).

**Project Type**: Library within the Rust workspace (`cloudkitty-rl`) plus
server wiring (`cloudkitty-server`). Single project.

**Performance Goals**: Per-kitty per-tick forward in microseconds against the
800 ms tick; the 4,096-row reference batch runs in ~60 ms, so a single row is
negligible.

**Constraints**: No per-decision heap allocation beyond reused scratch buffers.
Fixed reduction order. `≤1e-4` max absolute logit parity to the oracle over
≥100 fixed rows.

**Scale/Scope**: Initial artifact is 23 tokens, `d_model` 64, 4 heads, 2
encoder layers, FFN 128, ~77k parameters. The loader and forward are generic
over all four hyperparameters.

## Constitution Check

*GATE: passed before Phase 0; re-checked after Phase 1.*

- **Article I–III (kitties cannot suffer / die / be alone)**: No world, needs,
  resource, or kitty-count code is touched. Not applicable; no gate impact.
- **Article IV (engine is law; behaviors are untrusted advisors)**: A v3 policy
  is a `PolicyBehavior` — it only proposes; the engine validates against the
  same masks and legality. The behavior seam is unchanged (FR-016). An unloadable
  artifact fails at startup, never at tick time, so a bad policy degrades nothing.
  **PASS.**
- **Article V (deterministic simulation)**: The determinism guarantee is scoped
  to built-in behaviors and the engine core. Policy advisors sit under Article IV,
  not Article V, so a policy's internal float math is not bound by the seed-replay
  guarantee. The engine, the RNG sequence, and tick order are untouched, and the
  served forward is reproducible on a given binary and platform — which is what
  the single production box needs. Cross-platform bit-exactness is explicitly not
  promised (spec FR-018). **PASS**, with the determinism tier documented in
  `research.md`.
- **Article VI (spec-first, test-guarded, no magic numbers)**: Spec precedes
  code; the load, reject, and parity behaviors are CI-gated tests. The menu
  scatter map and dense-head ordering derive from `ActionCodec::v2`, the token
  widths from `observe.rs`, and the architecture from the artifact header — no
  magic numbers in the forward. **PASS.**

No violations. Complexity Tracking is empty.

## Project Structure

### Documentation (this feature)

```text
specs/030-artifact-v3/
├── plan.md              # This file
├── research.md          # Phase 0: consolidated decisions
├── data-model.md        # Phase 1: header + blob + runtime structs
├── quickstart.md        # Phase 1: validation scenarios
├── contracts/
│   ├── policy-artifact-v3.md   # container, header, validation, version dispatch
│   └── forward-v3.md           # forward architecture, module order, parity oracle
└── tasks.md             # Phase 2 (/speckit-tasks — not created here)
```

### Source Code (repository root)

```text
crates/cloudkitty-rl/
├── src/
│   ├── policy.rs        # CHANGED: container read + version dispatch; PolicyArtifact
│   │                    #   becomes a version-keyed enum {V2(Mlp), V3(Attn)};
│   │                    #   v2 header/forward unchanged and moved behind the enum
│   ├── attn.rs          # NEW: V3 header parse, shape derivation/validation,
│   │                    #   hand-rolled attention forward, scratch, v3 writer
│   ├── behavior.rs      # UNCHANGED seam: decide_sync calls artifact.forward()
│   │                    #   and splits at menu_len exactly as today
│   ├── codec.rs         # UNCHANGED: ActionCodec::v2 / MessageCodec are the source
│   │                    #   of the menu order the v3 scatter map derives from
│   └── observe.rs       # UNCHANGED: schema-3 block widths + observation_len
├── tests/
│   ├── artifact_v3_load.rs      # NEW: load + serve a v3 fixture; v2 still loads
│   ├── artifact_v3_reject.rs    # NEW: one case per rejection class
│   └── artifact_v3_parity.rs    # NEW: Rust forward vs oracle rows, ≤1e-4
└── Cargo.toml           # UNCHANGED (no new deps)

crates/cloudkitty-server/
├── src/lib.rs           # register_policy_behaviors: dispatch is inside load;
│                        #   wiring change limited to supported-set log/error text
└── tests/               # integration: boot with a v3 + a v2 seat
```

**Structure Decision**: Single project. The v3 forward lands in a new
`crates/cloudkitty-rl/src/attn.rs` so `policy.rs` stays a readable container +
dispatch layer, mirroring how the v2 forward is a self-contained unit today. No
new crate, no new dependency.

## Complexity Tracking

No constitution violations to justify.
