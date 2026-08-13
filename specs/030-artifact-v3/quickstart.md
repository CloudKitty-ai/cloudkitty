# Quickstart: Validating Policy Artifact v3

Runnable scenarios that prove the feature works end to end. Details live in
`contracts/policy-artifact-v3.md`, `contracts/forward-v3.md`, and `data-model.md`.

## Prerequisites

- The Rust workspace builds (`cargo build -p cloudkitty-rl`).
- A v3 fixture artifact and its parity file, produced either by the Rust test
  writer (`write_artifact` v3) or by the Experiments exporter from the step-2
  checkpoint. The parity file follows the format in `forward-v3.md`.
- The existing v2 fixture artifact (already in the `cloudkitty-rl` tests) for the
  no-regression check.

## Scenario 1 — Load and serve a v3 policy (US1, SC-001)

```
cargo test -p cloudkitty-rl artifact_v3_load
```

Expected: a valid v3 artifact loads; its SHA-256 and the three schema versions
are logged; the forward returns a `menu_len + message_head_len` vector; a decision
decodes to a legal proposal. A v2 fixture loaded in the same test still serves,
byte-identically (SC-004).

## Scenario 2 — Reject incompatible artifacts (US2, SC-003)

```
cargo test -p cloudkitty-rl artifact_v3_reject
```

Expected: one case per rejection class fails load, each naming
`[rl.policy.<name>].artifact` and the reason, with no tick run:

- a v3 artifact on a `{2}`-only build → rejected by version, listing the set;
- an unknown/misspelled header key → rejected naming the field;
- a wrong `observation_schema`/`action_schema`/`mask_schema` → schema mismatch;
- `architecture` other than `entity_attention` → rejected naming the field;
- `d_model % heads != 0` or a non-positive hyperparameter → rejected naming it;
- a blob length inconsistent with the hyperparameters → blob-size mismatch.

## Scenario 3 — Parity against the oracle (US3, SC-002)

```
cargo test -p cloudkitty-rl artifact_v3_parity
```

Expected: over the ≥100 fixture rows, the Rust forward's logits are within `1e-4`
max absolute error of the expected logits, and the greedy activity argmax matches
on every row. Running the forward twice on the same rows yields identical output
(same-binary reproducibility, FR-018).

## Scenario 4 — Boot the server with a v3 and a v2 seat (US1, SC-001)

Boot `cloudkitty-server` against a scripted test world with two policy seats —
one `artifact` pointing at the v3 fixture, one at the v2 fixture — and tick.

Expected: both policies load and log before the first tick; both produce lawful
decisions against the same masks; the world ticks without error. This is the
integration test in `cloudkitty-server/tests/`.

## Scenario 5 — Serving cost (SC-005)

The parity test times the forward over the fixture batch. Expected: per-row time
is microseconds — negligible against the 800 ms tick. (The reference numpy batch
of 4,096 rows runs in ~60 ms; the scalar Rust per-row cost is well under that.)

## Success signals

All five scenarios pass; the v2 path is unchanged; every rejection is a named
startup failure, never a tick-time error. At that point the format is ready for
the Experiments exporter to convert the trained checkpoint into a servable v3
artifact.
