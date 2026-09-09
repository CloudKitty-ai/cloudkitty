# Quickstart: validating Key Settings (spec 052)

Run from the worktree root (`~/ai/cloudkitty-settings`, branch `052-key-settings`). Commit before any mutate-then-revert cycle; write predictions before each red into `redden-list.md`; every red goes through `scripts/mutate.sh --expect`.

## 0. Baseline (cycle 0, before any change)

```bash
cargo test --workspace --no-fail-fast 2>&1 | tail -30     # record pass / fail / ignored
cargo fmt --all -- --check && cargo clippy --workspace --all-targets -- -D warnings
```

Also record `/config` on the served toml for SC-003 (a fresh world on an ephemeral port; kill it after):

```bash
cargo run -p cloudkitty-server -- --config cloudkitty.toml --snapshot /tmp/ck052.json --fresh --no-backup &
sleep 3; curl -s http://127.0.0.1:8090/config > /tmp/config-before.json; kill %1
```

(`[world] bind` in the served toml is the box's; override to `127.0.0.1:0`-style by a scratch copy of the toml if the port is busy — the diff is against the same copy both times.)

## 1. Unit guards (`crates/cloudkitty-server/src/settings.rs`)

```bash
cargo test -p cloudkitty-server settings::
```

| guard | FR | red (mutate.sh --expect) | prediction |
|---|---|---|---|
| key-name golden | FR-011 | drop `water.contagion_membership` from the list | exactly the golden test fails, naming the missing entry |
| minimal toml + one optional key → source | FR-011a / FR-003a | source decided by `value == default` instead of presence | the minimal-toml test fails: the fixture writes `[actions] groom_cuddle_relief = 15.0` (the default, on purpose) and expects `toml`; the mutant reads `default` |
| no file → all default | FR-011a | `raw.is_none()` branch returns `Toml` | exactly the no-file test fails |
| Option sentinels | FR-003 | render `None` as `null` | the sentinel test fails on `meow.relief_memory_margin` |
| render_text grammar | contract §2 | omit the `(default: …)` parenthesis for keys that have one | the grammar test fails on the first defaulted line |
| announce (log capture) | FR-012 / SC-004 | log the JSON instead of `render_text()` | exactly the announce test fails |

## 2. Integration guards (`crates/cloudkitty-server/tests/server_integration.rs`)

```bash
cargo test -p cloudkitty-server --test server_integration settings
```

| guard | FR / SC | red | prediction |
|---|---|---|---|
| wire carries the built value: JSON == `to_value(&block)`, text == `render_text()` | FR-012 / SC-004 | serve a clone with one entry's `source` flipped | exactly the JSON half fails; then flip the text branch to serve JSON, the text half fails |
| `Accept: text/plain` negotiation | contract §2 | ignore the header | the text half fails (JSON came back) |
| every entry present on a minimal config | FR-004 / SC-002 | skip entries whose `source` is `default` | the count assertion fails |
| `/config` unchanged | FR-005 / SC-003 | (no code red — see §4) | — |

## 3. The script's tail (`docs/deploy/test-update-tail.sh`)

```bash
bash docs/deploy/test-update-tail.sh
```

Four cases: 200 + body → section printed, exit 0; 404 → message 1, exit 1; 200 empty → message 2, exit 1; closed port → message 3, exit 1.

| red | prediction |
|---|---|
| treat 404 as success | the 404 case fails (exit 0, no message) |
| drop the empty-body check | the empty case fails |
| swallow curl's exit status | the closed-port case fails (it reports "unusable" instead of "stopped answering") |

### 3a. The CI step (FR-015 / SC-007)

After T022, the branch's CI run shows a `Shell tests` step running all four scripts. Its red is a pushed commit with `exit 1` appended to `scripts/test-mutate.sh` (predict: that step fails, the Rust steps stay green), reverted in the next commit; both run URLs go into `redden-list.md`. Locally:

```bash
bash docs/deploy/test-update-tail.sh && bash .claude/hooks/test-revert-guard.sh \
  && bash .claude/hooks/test-checkout-guard.sh && bash scripts/test-mutate.sh
```

## 4. SC-003: `/config` byte-identical, stamp unmoved

After the change, repeat the §0 capture into `/tmp/config-after.json`:

```bash
cmp /tmp/config-before.json /tmp/config-after.json && echo "config byte-identical"
cargo test -p cloudkitty-rl the_engine_defaults_stamp_is_stable_and_well_formed
```

Record the stamp value before and after in `redden-list.md`; they must match.

## 5. End to end, by hand

```bash
cargo run -p cloudkitty-server -- --config cloudkitty.toml --snapshot /tmp/ck052.json --fresh --no-backup
# in another shell:
curl -s http://127.0.0.1:8090/settings | jq .
curl -s -H 'Accept: text/plain' http://127.0.0.1:8090/settings
```

Expected: the boot log shows one `key settings` block; the text fetch is byte-identical to it; the JSON has every entry from `data-model.md`'s table; on the served toml every listed key reads `[toml]` except those the toml leaves absent (read the toml, do not assume).

## 6. Full suite + CI-exact lint before the PR

```bash
cargo test --workspace --no-fail-fast 2>&1 | tail -30
cargo fmt --all -- --check && cargo clippy --workspace --all-targets -- -D warnings
bash docs/deploy/test-update-tail.sh
```

Compare against the cycle-0 counts: the only movement is the new tests. Then the four shell tests in one line (§3a) — the same four CI runs.

## Not run in this arc

Nothing deploys. The box's first print of the section happens at its next deploy; that deploy is the live proof of US1 and is reported then, not here.
