# Research: Key Settings (spec 052)

All facts below were read off the tree at a757595 or the box on 2026-09-08. No `NEEDS CLARIFICATION` remained after the spec's clarification pass; these are the design decisions the plan rests on.

## R1 — Where the list lives

**Decision**: a new module `crates/cloudkitty-server/src/settings.rs`.

**Rationale**: the block needs three inputs only the server holds together: the validated `cloudkitty_core::Config`, the server-owned `WatchdogConfig` (spec 040: a foreign table to the engine, never serialized by it), and the loaded config file's text (for presence). `main.rs` already has all three in `load_config`. Putting the list in the engine would force the engine to know about `[watchdog]`, or split the list in two — which is the drift FR-001 forbids.

**Alternatives**: engine-side list (rejected: watchdog is not the engine's, and any engine change risks the stamp); script-side list (rejected in the spec: the script cannot see defaults or presence).

## R2 — The shape

**Decision**: `KeySettings { engine_defaults_sha256: String, entries: Vec<Entry> }`, `Entry { group: &'static str, key: String, value: serde_json::Value, default: Option<serde_json::Value>, source: Source }`, `Source::{Toml, Default}` serialising as `"toml"` / `"default"`. JSON is the serde form of the struct; entries are an **ordered list**, not a map, so the wire order is the display order.

**Rationale**: the stamp is a computed identity, not a dial with a source, so it is the block's header rather than an entry (the spec's table lists it under group `engine` with no default; FR-011's golden still names it). `serde_json::Value` lets one entry type carry numbers, booleans, strings, and the seat objects without a type per key.

## R3 — Deciding the source

**Decision**: `load_config` additionally returns `Option<toml::Value>`: `Some(text.parse()?)` when a file was loaded, `None` on the built-in-defaults path. An entry's source is `Toml` iff its path resolves in that value: tables by name (`vision` → `radius`), seats by array index (`kitty[i]` → `behavior`). Never by comparing value to default (FR-003a).

**Rationale**: the file is already read as a string; a second parse into the generic tree is one line and cannot disagree with the typed parse (same text, same parser). The typed parse cannot answer presence: serde has already filled the defaults by the time we see the struct.

**Alternatives**: `Option<T>` fields everywhere in `Config` (rejected: engine change, stamp moves, `/config` changes); a serde `deserialize_with` presence hook (rejected: engine change for a server concern).

## R4 — Defaults and sentinels

**Decision**: engine defaults from `Config::default()` per key; watchdog defaults from `WatchdogConfig::default()`; no default for `world.*`, the seats, or the stamp. Option keys render a sentinel string in **both** value and default: `[meow] relief_memory_margin` `None` → `"unbounded"`; `[behavior] reply_intensity_floor` `None` → `"none"`. `contagion_membership` renders its serde name (`option_a` / `bidirectional`).

**Engine defaults as of a757595** (for the data model; the block reads them live, these are not pinned): vision radius 5, memory_timeout_ticks 0, groom_cuddle_relief 15.0, bath_gain 3.5, bath_gain_ceiling 60.0, contagion_factor 0.0, contagion_membership option_a, announce_here 0, contagion_aware_ladder false, reply_intensity_floor none, relief_memory_margin unbounded, watchdog threshold 150, remind_every 150.

## R5 — One text renderer

**Decision**: `KeySettings::render_text() -> String`, lines of the form `group.key = value (default: d) [source]`; the parenthesis omitted where `default` is `None`; header line `engine_defaults_sha256 = <hex>`; seats as `kitty.<id> = <name> <behavior> [toml]`. Scalars print bare (no JSON quotes on strings). The boot log is one event, `tracing::info!("key settings\n{}", self.render_text())`, emitted by `KeySettings::announce(&self)` — kept in `settings.rs` rather than `main.rs` so a unit test can install a capturing `tracing` subscriber (`tracing::subscriber::with_default` with a `Vec<u8>` writer) and assert the event's message carries `render_text()` verbatim (analysis finding C1: by-construction agreement is not a guard). `main.rs` calls it after the existing watchdog "standing by" line and **before** `sim_task::spawn` (FR-006: before the first tick). The existing wet-fur / contagion / vision / ladder lines are not touched (FR-007).

**Rationale**: one renderer means the journal, the terminal and the `text/plain` wire are the same bytes by construction; FR-012's "agree on every key" then has nothing to disagree about, and the integration test only has to show the wire carries the built value unchanged.

## R6 — The endpoint

**Decision**: `GET /settings`. Default response `application/json` (R2's shape). If the request's `Accept` header contains `text/plain`, respond `text/plain; charset=utf-8` with `render_text()`. `AppState` gains `settings: Arc<KeySettings>`, built in `main.rs` before `build_router` and therefore before `TcpListener::bind` (FR-006a). Three test-side `AppState` constructions in `tests/server_integration.rs` (lines 149, 322, 926 at a757595) gain the field.

**Rationale**: the script then needs only `curl -H 'Accept: text/plain'` — no `jq`, no python — and the section it prints is the boot block verbatim. (The box does have `jq` and `python3` today, checked 2026-09-08; the decision does not depend on it.)

**Alternatives**: JSON only + `jq` in the script (rejected: a box dependency and a second renderer); a separate `/settings.txt` route (rejected: two routes for one resource); a `rendered` field inside the JSON (rejected: ugly, and still a second reader).

## R7 — How the script tells the three failures apart

**Decision** (verified on the box 2026-09-08): an unknown route on the live server falls through to the static-file fallback and answers **404** (`curl -w %{http_code}` on `/settings` and on `/nope` both read 404 today). So:

| outcome | signal | message |
|---|---|---|
| binary predates the endpoint | HTTP 404 | `this binary does not serve /settings (predates spec 052?)` |
| unusable | HTTP 200 with empty body, or any other status | `/settings answered <code> with an unusable body` |
| server gone | curl exit ≠ 0 (connect failed / timeout) | `the server stopped answering after the health check` |

Each exits the script with status 1, after the `deployed` line and the backup prune (FR-009). No rollback branch is entered.

## R8 — Where the function lives and how it is tested

**Decision**: `print_key_settings()` is defined in `update.sh` beside `wait_healthy()` and called at the end of the healthy branch: `if print_key_settings; then exit 0; else exit 1; fi` replaces the bare `exit 0`. `update.sh` stays one file (the provisioning script installs it by path).

**Testing**: `update.sh` takes a lock (`/run/cloudkitty-deploy.lock`) and runs top-level statements before its functions are defined, so it cannot be sourced on a laptop. `docs/deploy/test-update-tail.sh` extracts the function text with `sed -n '/^print_key_settings()/,/^}/p'`, `eval`s it with `log()` and `UPSTREAM` stubbed, and drives it against a python3 `http.server` handler in four modes: 200 with a body (prints the section, exit 0), 404 (message 1, exit 1), 200 empty (message 2, exit 1), and a closed port (message 3, exit 1). Reds: flip each branch and predict exactly which case fails.

**Alternatives**: restructure `update.sh` into a sourceable library (rejected: moves the lock and the trap for a test's convenience; touch only what you must); no test for the script (rejected: FR-008/009 are behavior, rule 5 applies).

## R9 — Proving `/config` did not move

**Decision**: nothing in `cloudkitty-core` changes, `AppState.config` is the same `Arc<Config>`, and `get_config` is untouched. Guards: the existing `the_foreign_tables_never_serialize` and the stamp's own stability test in `cloudkitty-rl` stay green; a new integration test fetches `/config` and asserts its key set is the one the spec-039 contract lists is **not** added (it would be a new golden for an old contract) — instead `quickstart.md` records a byte diff of `/config` on the served toml, before and after, as SC-003's evidence.

## R10 — The key-name golden

**Decision**: a unit test in `settings.rs` asserts the exact ordered list of `group.key` names (plus the header) against a literal array — an in-code golden. Adding a key is a two-line diff (the list and the array) in one file.

**FR-011a**: a second unit test builds the block from a minimal raw tree: `Config::default()` serialized to TOML (every section present — under the 3.0 rule every section is required, verified at implement time: no `#[serde(default)]` on any `Config` section field) with the nine optional listed keys removed (`meow.relief_memory_margin`, `actions.groom_cuddle_relief`, `behavior.announce_here`, `behavior.contagion_aware_ladder`, `behavior.reply_intensity_floor`, `water.bath_gain`, `water.bath_gain_ceiling`, `water.contagion_factor`, `water.contagion_membership`; `[watchdog]` absent), re-parsed as `Config` to prove it is still a valid file, plus exactly one optional listed key written **at its default** (`[actions] groom_cuddle_relief = 15.0`) so that a value-comparison mutant is caught — and asserts that key and the required keys (`world.*`, `kitty.*`, `vision.*`) read `toml` and every other optional listed key reads `default`; a third builds with `None` presence and asserts every source is `default`.

## R12 — Shell tests in CI (owner ruling 2026-09-08, analysis C2)

**Decision**: one new step in `.github/workflows/ci.yml`, after `cargo test`, running the four shell tests in sequence: `bash docs/deploy/test-update-tail.sh`, `bash .claude/hooks/test-revert-guard.sh`, `bash .claude/hooks/test-checkout-guard.sh`, `bash scripts/test-mutate.sh`. All four build their fixtures in `mktemp -d` with `git init` and need only bash, git, curl and python3 — all on `ubuntu-latest`. The step is part of the required check.

**Rationale**: the deploy-tail test guards the feature's own failure semantics, which is where its value lives; a by-hand guard runs only when remembered. The owner extended the ruling to the hook self-tests and the mutation-runner test so "run in CI" holds for every guard in the tree.

**Guard against a vacuous pass**: `test-update-tail.sh` extracts `print_key_settings` from `update.sh` by text boundaries; it asserts `declare -F print_key_settings` succeeds after the `eval`, so a reformat that moves the closing brace fails loudly instead of extracting nothing.

**Alternatives**: by-hand only (rejected by the owner); `continue-on-error` (rejected: a green that means nothing).

## R11 — Docs and changelog

**Decision**: README endpoint table gains one row in the table's own register; `docs/deployment.md` gains one paragraph under "Updating" (the script ends with the section; what a non-zero exit after `deployed` means) and one bullet under "What is public, on purpose" (`/settings` is public like `/config`, lists no paths or bind address); `CHANGELOG.md` `## Unreleased` gains one line with **no** compatibility marker (no obs-schema, no world-fresh, no rng-sequence, no stamp).
