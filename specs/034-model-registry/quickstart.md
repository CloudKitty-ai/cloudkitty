# Quickstart: validating spec 034 end-to-end

Prerequisites: this worktree, stable Rust toolchain. All commands from the
repo root. Contracts referenced: [registry-and-serving.md](contracts/registry-and-serving.md).

## 1. The suite (covers FR-004..011 mechanically)

```sh
cargo test --workspace
```

Expect green, including the new `registry_integrity` test (FR-008) and the
new `server_integration` assertions (Scripted default, display-line serving,
plugin absence, startup refusal).

## 2. Wall-window boot: everything "Scripted" (US1 scenario 2)

```sh
cargo run --bin cloudkitty-server -- --config cloudkitty.toml &
curl -s localhost:8420/kitties | jq '.[].behavior_description'
```

Expected: `"Scripted"` five times (all seats parked `needs_driven` in the
wall window). Kill the server after.

## 3. Policy seat serves the display line (US1 scenario 1)

Run the integration test that boots an ephemeral server with a fixture
artifact + fixture registry and asserts the kitty carries the row's
`display` — no manual steps; it is part of step 1. To eyeball it instead,
point a scratch config's seat at any `.ckpolicy` fixture with a
`registry.toml` beside it and repeat step 2's curl.

## 4. Refusal on a missing row (US3 scenario 1, FR-007)

Covered by the integration test that boots against a fixture artifact whose
registry lacks its sha: startup fails, error names `[rl.policy.<name>]`, the
artifact path, and the sha256.

## 5. Registry integrity gate (US3 scenario 2, FR-008)

```sh
cargo test -p cloudkitty-server --test registry_integrity
```

Then, to see it bite: temporarily blank a row in `policies/registry.toml`,
rerun, and watch it fail naming `e004-a1-s2.ckpolicy` and its sha. Restore
before committing.

## 6. Nothing else moved (SC-003, FR-009/011)

Step 1 passing without any modified assertion about existing fields is the
proof: `behavior` serves verbatim, no schema pin test changed, no fingerprint
test changed.
