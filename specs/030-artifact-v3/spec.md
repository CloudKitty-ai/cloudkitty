# Feature Specification: Policy Artifact v3 — Entity-Attention Format

**Feature Branch**: `030-artifact-v3`

**Created**: 2026-08-13

**Status**: Draft

**Input**: Serve entity-attention policies on observation schema 3. A new
policy-artifact version (v3) whose forward pass is a transformer encoder over
per-entity tokens with pointer action heads, replacing the v2 slot-structured
MLP. Article VI contract, 014-lineage. No engine, world, config, or
policy-behavior semantic change; schema 4 / variable rosters are out of scope.

## Context

Slot-structured MLP encodings extrapolate undefined on slot patterns outside
their training support (finding F-010): an empty kitty slot can collapse a
policy that never saw that vacancy pattern. The v3 encoding replaces
slot-position dependence with content-based entity tokens and padding masks,
so a vacant slot is a masked-out token rather than a novel input region.

Two committed experiments motivate the format. An entity-attention critic on
identical v4 targets reached validation EV 0.555 against the MLP's 0.53 with
36% fewer parameters (`experiments/attn-critic-2026-08-12/`). The v4 behavior
clone with only the trunk swapped reached activity top-1 79.9% against 72.7%
(`experiments/attn-clone-2026-08-12/`), with the largest gains on the
entity-targeted action classes. Both used the same registered recipe, so the
columns compare one to one.

This spec defines only the on-disk format, its load-time validation, and the
serving forward pass. Mask semantics, `ActionCodec`/`MessageCodec`, the
behavior seam, legality, and the certification harness are unchanged. The
artifact remains "weights plus header"; only the architecture inside the
forward differs from v2's Linear-ReLU stack.

## Clarifications

### Session 2026-08-13

- Q: Is the v3 header the sole authority for the transformer architecture, or
  must the loader pin the hyperparameters against compiled constants? → A:
  Header-authoritative. The loader accepts any self-consistent
  `d_model`/`heads`/`encoder_layers`/`ffn` and derives every tensor shape from
  them; the forward is generic over the four hyperparameters, so a re-tuned
  model is an artifact swap with no rebuild.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Serve a v3 policy alongside v2 (Priority: P1)

An operator points a `[rl.policy.<name>]` config block at a v3 artifact file
and starts the server. The binary recognizes the v3 version, validates the
header and weight blob against its compiled schema, logs the artifact hash and
schema versions, and serves decisions from the attention forward. A different
kitty in the same world may be driven by a v2 artifact at the same time.

**Why this priority**: This is the feature. Without it there is no v3 serving,
and it is the smallest slice that delivers value — one v3 policy running in a
real world, decisions flowing through the unchanged behavior seam.

**Independent Test**: Boot the server with one v3 and one v2 policy seat
against a scripted world; confirm both load, both log their hash and versions
before the first tick, and both produce lawful decisions.

**Acceptance Scenarios**:

1. **Given** a valid v3 artifact whose schema pins match the binary, **When**
   the server starts, **Then** it loads the artifact, logs its SHA-256 and the
   observation/action/mask schema versions, and serves without error.
2. **Given** a world seat on v3 and another on v2, **When** the world ticks,
   **Then** each seat decides through its own forward and both decisions are
   legal against the same mask.
3. **Given** a v3 artifact, **When** its forward runs on an observation with a
   vacant kitty slot, **Then** the vacant token is masked out and the decision
   does not depend on that slot's position.

---

### User Story 2 - Reject an incompatible artifact at startup (Priority: P1)

An operator supplies an artifact the binary cannot serve — a version the build
does not support, a schema pin that predates the binary's encoders, a
misspelled header key, or a weight blob whose length does not match the
declared architecture. The server refuses to start and names the offending
config field and reason. No tick runs first.

**Why this priority**: A policy that loads wrong and serves anyway is worse
than one that refuses to load. Fail-loud-at-startup is the safety contract the
v2 loader already holds, and v3 must not weaken it.

**Independent Test**: For each rejection class, hand the loader a crafted bad
artifact and assert startup fails with a message naming
`[rl.policy.<name>].artifact` and the specific reason, before any tick.

**Acceptance Scenarios**:

1. **Given** a v3 artifact on a binary whose supported set is `{2}`, **When**
   the server starts, **Then** it is rejected by version with a message listing
   the supported versions, not by a shape accident.
2. **Given** a v3 header with an unknown or misspelled key, **When** it is
   parsed, **Then** loading refuses and names the offending field.
3. **Given** a v3 header whose hyperparameters imply a weight blob length
   different from the file's, **When** it is validated, **Then** loading fails
   naming the expected and found blob sizes.
4. **Given** a v3 artifact whose observation schema pin does not match the
   compiled encoder, **When** it is validated, **Then** loading fails naming
   the schema and the found-versus-expected versions.

---

### User Story 3 - Certify a v3 forward against the reference oracle (Priority: P2)

A maintainer exporting a trained attention policy checks the Rust forward
against the Python reference on a fixed set of observation rows. The two agree
within tolerance, so the exported artifact is certified to serve the same
decisions the training checkpoint would.

**Why this priority**: The format is worthless if the served forward disagrees
with the trained model. Parity is what lets an experiment's checkpoint become a
served artifact. It is P2 only because it gates export, not the loader itself.

**Independent Test**: Run the Rust forward and the numpy reference on the same
~100 fixed rows and assert max absolute logit error stays within tolerance.

**Acceptance Scenarios**:

1. **Given** the step-2 checkpoint exported to a v3 artifact, **When** the Rust
   forward and the numpy reference run on the parity rows, **Then** the maximum
   absolute logit difference is within 1e-4.
2. **Given** the same artifact and the same seed, **When** the forward runs
   twice on the same binary and platform, **Then** the decisions are identical.
3. **Given** the parity rows, **When** greedy decoding runs, **Then** the Rust
   forward's activity argmax matches the reference on every row.

---

### Edge Cases

- A vacant kitty or critter slot (first feature at or below zero) is a
  masked-out token; the summary pool divides by the count of present tokens,
  never by zero (self and clock are always present).
- An observation with every entity slot vacant still has self and clock tokens,
  so the encoder input is never empty.
- A v2 artifact on a v3-capable binary loads and serves through the v2 MLP path
  with byte-identical output to today.
- A header that parses but declares an unrecognized `architecture` string is
  rejected by name, not silently treated as attention.
- Transcendental functions (`exp`, `sqrt`) make the forward reproducible for a
  given binary and platform but not bit-identical across platforms; the
  certification contract is same-binary reproducibility plus oracle parity.

## Requirements *(mandatory)*

### Functional Requirements

**Format and header**

- **FR-001**: A v3 artifact MUST use the existing container — magic `CKPOLICY`,
  a `u32` little-endian header length, a UTF-8 JSON header, then an `f32`
  little-endian weight blob.
- **FR-002**: The v3 header MUST declare `artifact_version` (3), the three
  schema pins (`observation_schema`, `action_schema`, `mask_schema`), an
  `architecture` string (`entity_attention`), and the four transformer
  hyperparameters `d_model`, `heads`, `encoder_layers`, `ffn`.
- **FR-003**: The v3 header MUST NOT restate any dimension derivable from the
  compiled slot config or the schema-3 block widths — token widths,
  type-embedding row count, and per-tensor shapes are derived at load, not read
  from the header.
- **FR-004**: The v3 header MUST be parsed with unknown fields rejected
  (`deny_unknown_fields`): an unknown or misspelled key fails loading and names
  the field. (This extends the PR #114 strict-loading posture from the TOML
  config structs to the artifact JSON header. The v2 header is unchanged.)
- **FR-005**: The weight blob MUST follow a single fixed module order defined in
  this spec's record-format contract: the per-type embedding linears, the
  type-embedding table, each encoder layer's parameters, the final summary
  LayerNorm, and the four output heads, each tensor row-major.

**Loading and validation**

- **FR-006**: Loading MUST validate in a fixed order and fail at the first
  problem, naming the config field `[rl.policy.<name>].artifact` and the
  reason, before any tick: magic → header length → strict JSON parse → version
  in the supported set → schema pins match the compiled encoders → architecture
  recognized → hyperparameters positive and mutually consistent → derived token
  widths sum to the compiled `observation_len` → output width equals
  `menu_len + message_head_len` → weight blob length exact.
- **FR-007**: Every tensor shape MUST be derived from the header hyperparameters
  plus the compiled slot config and asserted; the total blob byte length MUST
  equal the sum of the derived tensor sizes exactly, or loading fails naming
  expected and found sizes. The header is the sole authority for the transformer
  architecture: the loader MUST accept any hyperparameters that are positive and
  self-consistent (`d_model` divisible by `heads`) and MUST NOT pin them against
  compiled constants, so a re-tuned model loads without a rebuild. The forward
  MUST be generic over `d_model`, `heads`, `encoder_layers`, and `ffn`.
- **FR-008**: The loader MUST compute and log the SHA-256 of the whole artifact
  file and the three schema versions at load, as v2 does.

**Version dispatch**

- **FR-009**: The binary MUST support a set of artifact versions, not a single
  version. A v2 artifact loads through the existing MLP forward; a v3 artifact
  loads through the attention forward; any other version is rejected by version
  with a message listing the supported set.
- **FR-010**: v2 artifacts MUST continue to load and serve with output
  identical to today — no regression in the v2 path.
- **FR-011**: A v3 artifact on a binary that does not support v3 MUST be
  rejected by version, not by a downstream shape mismatch.

**Serving forward**

- **FR-012**: The v3 forward MUST be hand-rolled scalar `f32` with no linear-
  algebra or BLAS crate dependency, a fixed reduction order, and no per-decision
  heap allocation beyond reused scratch buffers — matching the v2 forward's
  determinism doctrine.
- **FR-013**: The forward MUST tokenize a schema-3 observation into the entity
  tokens (self, kitty×K, chow, water, sunbeam, critter×J, message-kind×8,
  clock), embed each by a per-type linear plus a type-embedding row (all kitty
  tokens share one row, all critter tokens share one, each message kind its
  own), and key-padding-mask any slot whose first feature is at or below zero.
- **FR-014**: The forward MUST run `encoder_layers` pre-norm transformer encoder
  layers (masked multi-head attention plus feed-forward) and form the summary as
  the self-token output concatenated with the masked mean pool over present
  tokens, followed by a LayerNorm.
- **FR-015**: The forward MUST emit a logit vector of width
  `menu_len + message_head_len` in the exact `ActionCodec::v2` and
  `MessageCodec` order: a dense head fills the non-entity menu indices, the
  message head fills the message slots, and verb-specific pointer heads read
  each kitty and critter token's output embedding and scatter into the menu
  (kitty slot k → 5+k, 9+k, 13+k, 22+k, 30+k; critter slot j → 18+j, 26+j).
- **FR-016**: The behavior seam MUST be unchanged: `decide_sync` splits the
  logit vector at `menu_len` into the activity and message heads exactly as it
  does for v2, and applies the same masks and sampling.

**Certification and export**

- **FR-017**: The v3 forward MUST reproduce the reference oracle within a
  maximum absolute logit error of 1e-4 over a fixed parity row set of at least
  100 observations.
- **FR-018**: Serving MUST be reproducible for a given binary and platform: the
  same artifact, observation, and seed yield the same decision across runs.
  Cross-platform bit-exactness is explicitly NOT promised.
- **FR-019**: A reference writer MUST be able to emit v3 artifacts (the analog
  of the v2 `write_artifact`) for fixtures and parity, serializing the header
  and the module-ordered weight blob.

**Scope boundary**

- **FR-020**: This feature MUST NOT change the engine, world, config schema, or
  any policy-behavior semantics. It MUST reuse the existing mask, `ActionCodec`,
  `MessageCodec`, legality, and certification harness unchanged.
- **FR-021**: This feature is scoped to observation schema 3 with the served
  slot config. Schema 4 and variable rosters are out of scope and get their own
  spec.

### Key Entities

- **v3 Artifact Header**: The JSON header declaring version, schema pins,
  architecture, and the four transformer hyperparameters. Strict-parsed.
- **Weight Blob**: The `f32` little-endian payload, laid out in the fixed module
  order the record-format contract defines.
- **Entity Token and Padding Mask**: One token per world entity slot plus self
  and clock; a mask marks vacant slots so attention and pooling skip them.
- **Type-Embedding Table**: One row per token type, with all kitty tokens
  sharing a row and all critter tokens sharing a row — the content-identity that
  carries the F-010 thesis.
- **Pointer Head**: A verb-specific linear read of an entity token's output
  embedding, scattered into the menu — the slot-order-free piece that will
  extend to variable rosters unchanged in a later spec.
- **Version Support Set**: The set of artifact versions a binary can serve;
  dispatch keys the forward on it and rejects the rest by version.
- **Parity Oracle Row Set**: The fixed observations and expected logits the Rust
  forward is certified against.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A v3 artifact and a v2 artifact both load and serve lawful
  decisions in the same running world.
- **SC-002**: The Rust v3 forward matches the reference oracle within 1e-4 max
  absolute logit error over at least 100 fixed rows, and its greedy activity
  argmax matches the reference on every row.
- **SC-003**: Each rejection class — unsupported version, schema mismatch,
  unknown header key, wrong blob length, unrecognized architecture — fails at
  startup naming the field and reason, before any tick runs.
- **SC-004**: The v2 serving path is byte-for-byte unchanged: existing v2
  artifacts produce identical decisions before and after this feature.
- **SC-005**: Per-kitty per-tick serving cost is negligible against the 800 ms
  tick — the reference forward runs a 4,096-row batch in about 60 ms, so a
  single row is microseconds.

## Assumptions

- The reference numpy forward and the fixed parity rows are supplied by the
  Experiments thread (parity_v4 pattern, ~1e-4 tolerance). The format, loader,
  and Rust forward can be specified and built before the oracle lands; only the
  parity gate depends on it.
- The step-2 run fixes the initial hyperparameters: `d_model` 64, 4 heads, 2
  encoder layers, FFN 128, ReLU in the feed-forward, 23 tokens at the served
  slot config. These are the values the first exported artifact carries, not
  compiled constants — per FR-007 the header is authoritative, so a re-tuned
  model is a header change rather than a code change.
- The feed-forward activation is pinned to ReLU by this contract rather than
  declared per-artifact, matching the v2 loader's fixed-activation check.
- The determinism contract is same-binary, same-platform reproducibility plus
  oracle parity. Cross-platform bit-exactness was never achievable once the
  forward includes transcendentals, and is not promised.
- Obs schema 3, action schema 2, and mask schema 2 are the current compiled
  pins; v3 bumps only `artifact_version`, leaving the three schema numbers and
  their independent validation untouched.
