# Phase 0 Research: Policy Artifact v3

All the forks this feature could have opened were resolved in the spec and the
clarify session, so no `NEEDS CLARIFICATION` markers reached Phase 0 and no
research agents were dispatched. This document records the consolidated
decisions and the two the clarify session deferred here.

## D1 — Forward: hand-rolled scalar `f32`, no crate dependency

**Decision**: Implement the attention forward in Rust as scalar `f32` loops with
a fixed reduction order, reusing a preallocated scratch buffer, matching the v2
MLP forward in `policy.rs`.

**Rationale**: The v2 forward is deliberately no-BLAS with fixed accumulation
order so reductions are reproducible. Article V's determinism and the parity
gate both depend on that. A BLAS-backed crate (`candle`, `ndarray` + a backend)
reorders sums and would defeat same-binary reproducibility, add a heavy
dependency, and buy nothing at 23 tokens / 77k params where a single row is
microseconds. The forward is larger than v2's (embeddings, N encoder layers,
pooling, four heads, pointer scatter) — roughly 150–250 lines — but every piece
is a scalar loop.

**Alternatives considered**: `candle` (heavy dep, non-deterministic reductions,
rejected); `ndarray` with a pure-Rust backend (still reorders, adds a dep for no
speed that matters, rejected); a `matrixmultiply`-style micro-BLAS (reduction
order not under our control, rejected).

## D2 — Header authority: the header owns the architecture

**Decision** (clarify 2026-08-13): The v3 header is the sole authority for the
transformer architecture. The loader accepts any `d_model`/`heads`/
`encoder_layers`/`ffn` that are positive and self-consistent (`d_model %
heads == 0`), derives every tensor shape from them, and asserts only the schema
boundaries (token widths sum to `observation_len`; output width `= menu_len +
message_head_len`) plus the exact blob length. The forward is generic over the
four hyperparameters.

**Rationale**: This mirrors the v2 loader, which reads layer shapes from the
header and asserts only the schema-derived edges. It makes a re-tuned model a
drop-in artifact swap with no rebuild, which is the reason the hyperparameters
live in the header at all.

**Alternatives considered**: Pin the hyperparameters against compiled constants
(rigid; every re-tune needs a release; rejected). Put the full per-tensor shape
list in the header (redundant with the derivation, invites drift from the
compiled schema, rejected — FR-003).

## D3 — Version gating: a supported set, not a bumped constant

**Decision**: Replace the v2 loader's single `ARTIFACT_VERSION` exact-match with
a supported-set dispatch. After the version field is read, the loader branches:
version 2 → the existing MLP header parse + validation + forward; version 3 →
the attention path; anything else → rejected by version, listing the supported
set. `PolicyArtifact` becomes a version-keyed enum whose `forward` dispatches.

**Rationale**: Bumping the constant to 3 would reject every v2 artifact,
breaking "v2 keeps loading" (FR-010). A supported set keeps both live in one
binary and guarantees a v3 artifact on a v2-only binary is rejected *by version*,
not by a downstream shape accident (FR-011).

**Alternatives considered**: Separate binaries per version (operationally worse,
rejected). A conversion shim from v2 to v3 (there is no equivalence between the
architectures, rejected — and the v2 loader already advertises "no conversion
mode").

## D4 — Determinism tier: same-binary reproducibility + oracle parity

**Decision**: The contract is (a) bit-identical decisions for a given artifact,
observation, and seed on the same binary and platform, and (b) ≤1e-4 max
absolute logit parity to the numpy oracle across platforms. Cross-platform
bit-exactness is not promised.

**Rationale**: The forward includes `exp` (softmax) and `sqrt` (LayerNorm),
whose results depend on the platform libm. Once transcendentals enter, cross-
platform bit-exactness is unreachable — this was always going to arrive with the
first non-linear served policy. The production world runs one binary on one
platform, so same-binary reproducibility is what its replay actually needs, and
Article V's determinism clause is scoped to built-in behaviors and the engine,
not to a policy advisor's internal math (Article IV).

**Alternatives considered**: Fixed-point or a bundled softmax/exp polynomial for
cross-platform bit-exactness (large complexity, parity oracle still needed,
rejected as out of proportion to the benefit).

## D5 — Type-embedding table: kept separate, not folded into biases (deferred here from clarify)

**Decision**: Carry the type-embedding table as its own parameter block in the
artifact; do not fold each row into the corresponding per-type linear's bias at
export.

**Rationale**: The type-embedding row is mathematically absorbable into each
type's linear bias (it is a constant added per token after the linear). Folding
would shave ~15×`d`×4 bytes and one add, but it would diverge the Rust module
inventory from the PyTorch reference's, so a per-token intermediate can no longer
be compared 1:1 when chasing a parity mismatch. At the ≤1e-4 gate, keeping the
module structure isomorphic to the oracle is worth more than the bytes. Revisit
only if artifact size ever matters, which at 77k params it does not.

**Alternatives considered**: Fold at export (smaller, simpler forward, but harder
parity debugging; rejected for the first cut).

## D6 — Weight-blob module order (deferred here from clarify)

**Decision**: Fix a single canonical module order for the blob, pinned in
`contracts/forward-v3.md`: the eight per-type embedding linears, the type-
embedding table, each encoder layer in index order (attention in-proj, attention
out-proj, the two pre-norm LayerNorms, the two feed-forward linears), the final
summary LayerNorm, then the four output heads (dense activity, message, kitty
pointer, critter pointer). Every tensor is row-major `[out][in]` for weights and
`[out]` for biases, `f32` little-endian, matching the v2 convention.

**Rationale**: The blob is opaque bytes; the exporter and the Rust reader must
agree on order and layout exactly or parity is impossible. Pinning it in the
contract makes the exporter (Experiments) and the reader (Product) two
implementations of one written spec.

**Alternatives considered**: A named-tensor manifest in the header (adds header
surface and parsing, redundant with a fixed order; rejected — the order is
static for a given architecture).

## D7 — Parity fixture format: Product-defined, dependency-free (deferred here)

**Decision**: The parity fixtures are a plain little-endian `f32` file the Rust
test reads without a numpy-format dependency: `[u32 n_rows][u32 obs_len][u32
logit_len]` then `n_rows × (obs_len + logit_len)` `f32` values (each row: the
observation followed by the expected logits). Experiments writes it from numpy
via `tobytes()`; Product reads it in the parity test.

**Rationale**: Rust reading `.npy`/`.npz` would add a dependency for a test
fixture. A trivially-specified raw format keeps the Rust side dep-free and gives
Experiments a one-line writer. This is the one new cross-thread interface, so it
is pinned in the contract.

**Alternatives considered**: `.npy` (adds a Rust dep, rejected); JSON (larger,
float round-trip risk against the 1e-4 gate, rejected).
