# Quickstart: validating spec 035 end-to-end

From the repo root. Contract: [expansion-tool.md](contracts/expansion-tool.md).

## 1. The suite

```sh
cargo test --workspace
```

Green includes: the new `expansion` tests (maps, bijection, refusals,
determinism, fixture round-trip through the SERVING loader) and the
SC-003 engine-level deaf/mute integration test.

## 2. Expand a real artifact (eyes-on)

```sh
cargo run -p cloudkitty-rl --bin ckpolicy-expand -- \
  policies/attn-a1-s1.ckpolicy /tmp/attn-a1-s1-o4.ckpolicy
```

Expect: a passing attestation report (counts partition exactly; verdict
pass), and a printed sha256.

## 3. Determinism (SC-002)

Run step 2 twice into different paths; `shasum -a 256` both outputs —
identical. Same on CI hardware.

## 4. First-class load (FR-007 / SC-001)

Covered in the suite: a fixture expanded artifact seats through the
ordinary path in a booted test world. To eyeball with the real artifact,
point a scratch config's seat at the step-2 output (with a registry.toml
beside it carrying its new sha — FR-007 meets spec 034's gate) and boot.

## 5. Deaf and mute (SC-003)

Covered in the suite (`server_integration.rs`): expanded fixture mind +
full vocabulary + a new-kind-speaking neighbor → zero new-kind emissions;
decisions identical with new-kind observation inputs present vs zeroed.

## 6. All three candidates (SC-001, handoff)

Run step 2 for `attn-a1-s1`, `attn-a1-s3`, `e004-a1-s2`; record the three
output shas for Experiments' battery. Nothing is committed to `policies/`
until the seating PR (research D7).
