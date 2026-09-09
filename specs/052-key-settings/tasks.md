# Tasks: Key Settings (spec 052)

**Input**: Design documents from `/specs/052-key-settings/` — plan.md, spec.md (§Clarifications 2026-09-08), research.md (R1–R11), data-model.md, contracts/key-settings.md, quickstart.md.

**Tests**: REQUIRED — FR-011, FR-011a and FR-012 are tests by name, and every guard is seen red first (CLAUDE.md rules 5/6) via `scripts/mutate.sh --expect <prediction>`, the prediction written into `redden-list.md` BEFORE the run and the count re-read after. Commit before every mutate cycle (the hook refuses a dirty file anyway).

**Organization**: by user story. US1 (P1) is the deploy tail: the script's function and its stub-driven test, which need no server. US2 (P2) is the endpoint and the block's content guards. US3 (P3) is the boot log. Phase 2 builds the block itself, which all three read.

**House rules in force**: worktree `~/ai/cloudkitty-settings`, branch `052-key-settings`; `cloudkitty-core` is not touched; the served `cloudkitty.toml`, README prose and `docs/deployment.md` prose are the owner's (add beside, edit nothing); nothing deploys, no tag; the client-only path of `update.sh` is not touched.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependency on an incomplete task)
- **[Story]**: US1 / US2 / US3

---

## Phase 1: Setup

- [X] T001 Create `specs/052-key-settings/redden-list.md` in the 050 format: standard paragraph, then cycle 0 = `cargo test --workspace --no-fail-fast` on the untouched branch (record pass / fail / ignored, re-read from the output), `cargo fmt --all -- --check` and `cargo clippy --workspace --all-targets -- -D warnings` clean, the `engine_defaults_sha256` value from `cargo test -p cloudkitty-rl the_engine_defaults_stamp_is_stable_and_well_formed -- --nocapture` (or a one-line `cargo run` print), and the `/config` capture of quickstart §0 saved to the session scratchpad as `config-before.json`. Commit the spec artefacts (`specs/052-key-settings/*`) with the redden list.

---

## Phase 2: Foundational — the block exists

- [X] T002 Create `crates/cloudkitty-server/src/settings.rs` per research R2/R4/R5 and data-model.md: `pub struct KeySettings { engine_defaults_sha256: String, entries: Vec<Entry> }`, `pub struct Entry { group: &'static str, key: String, value: serde_json::Value, #[serde(skip_serializing_if = "Option::is_none")] default: Option<serde_json::Value>, source: Source }`, `#[serde(rename_all = "lowercase")] pub enum Source { Toml, Default }` (all `Serialize`, `Debug`, `Clone`, `PartialEq`); `pub fn build(config: &cloudkitty_core::Config, watchdog: &crate::watchdog::WatchdogConfig, raw: Option<&toml::Value>) -> KeySettings` producing the entries in data-model.md's order (stamp via `cloudkitty_rl::suite::engine_defaults_sha256()`, defaults via `Config::default()` / `WatchdogConfig::default()`, sentinels `"unbounded"` / `"none"`, `contagion_membership` via its serde name, seats as `{ "name", "behavior" }` keyed by id); a private `fn present(raw: Option<&toml::Value>, path: &[PathSeg]) -> Source` walking tables by name and `kitty` by index; `pub fn render_text(&self) -> String` per contracts §2 (header line, `group.key = value (default: d) [source]`, parenthesis omitted when `default` is `None`, strings bare, seats `kitty.<id> = <name> <behavior> [source]`, trailing newline); `pub fn announce(&self)` emitting the one boot event `tracing::info!("key settings\n{}", self.render_text())` (research R5: kept here so a test can capture it). Module doc comment names spec 052 and FR-001 (one list, three readers).
- [X] T003 Register the module in `crates/cloudkitty-server/src/lib.rs` (`pub mod settings;`) and add `pub settings: Arc<crate::settings::KeySettings>` to `AppState` in `crates/cloudkitty-server/src/api.rs` with a doc comment (spec 052: built at boot, before bind — FR-006a).
- [X] T004 In `crates/cloudkitty-server/src/main.rs`: `load_config` returns a fifth value `Option<toml::Value>` (`None` on the no-file path; `Some(text.parse::<toml::Value>()?)` with the same `could not load` context otherwise, research R3); after `config.validate_behavior_names(...)` and the `Arc::new(config)`, build `let settings = Arc::new(cloudkitty_server::settings::build(&config, &watchdog_config, raw.as_ref()))`; pass `settings: settings.clone()` into `AppState`. (The boot log line is US3's task; do not add it here.)
- [X] T005 Update the three `AppState { … }` constructions in `crates/cloudkitty-server/tests/server_integration.rs` (at a757595: lines ~149, ~322, ~926) to carry `settings: Arc::new(cloudkitty_server::settings::build(&config, &Default::default(), None))`; add a `settings(config: &Config) -> Arc<KeySettings>` helper beside `test_config()` so the three sites share one line.
- [X] T006 `cargo build -p cloudkitty-server --all-targets` and `cargo test -p cloudkitty-server` green; fmt + clippy clean; predict: count = cycle 0 (no new tests yet); record as cycle F0 in `redden-list.md`; commit.

**Checkpoint**: the block is built at boot and held in state; nothing reads it yet.

---

## Phase 3: User Story 1 — A deploy ends by stating what is on (P1) 🎯 MVP

**Goal**: `update.sh` prints the `key settings` section last on the server-restart path, and exits 1 with one of three named messages when it cannot (FR-008, FR-009, FR-010).

**Independent test**: `docs/deploy/test-update-tail.sh` drives the function against a python3 stub in four modes with no CloudKitty server involved.

- [X] T007 [US1] Add `print_key_settings()` to `docs/deploy/update.sh` directly after `wait_healthy()`, per contracts §4 and research R7: `curl -sS --max-time 5 -H 'Accept: text/plain' -o "$body" -w '%{http_code}' "http://${UPSTREAM}/settings"`; curl exit ≠ 0 → `echo "!! the server stopped answering after the health check" >&2; return 1`; code 404 → `echo "!! this binary does not serve /settings (predates spec 052?)" >&2; return 1`; code ≠ 200 or empty body → `echo "!! /settings answered ${code} with an unusable body" >&2; return 1`; else `log "key settings"` then `cat "$body"`; the temp file under `mktemp` and removed on every path. Comment block above it: spec 052, why after the prune, why no rollback.
- [X] T008 [US1] In the healthy branch of `docs/deploy/update.sh` (the `if wait_healthy; then … exit 0; fi` block after `systemctl start`), replace the closing `exit 0` with `if print_key_settings; then exit 0; else exit 1; fi` so the section is the last output and its failure is the exit code, after the `deployed` line and the backup prune (FR-009). Leave the `--client-only` block (lines ~160–175) and the rollback branch untouched (FR-010).
- [X] T009 [US1] Create `docs/deploy/test-update-tail.sh` (executable, `set -euo pipefail`, runnable from the repo root on a laptop): `eval "$(sed -n '/^print_key_settings()/,/^}/p' docs/deploy/update.sh)"` with `log()` stubbed to `printf '==> %s\n'`, then `declare -F print_key_settings >/dev/null || { echo 'extraction found no function' >&2; exit 1; }` so a reformat of update.sh cannot make the test pass on nothing (research R12); a python3 inline `http.server` handler parameterised by mode (`ok` → 200 + `engine_defaults_sha256 = deadbeef\nvision.radius = 5 (default: 5) [toml]\n`; `notfound` → 404; `empty` → 200 with an empty body) bound to an ephemeral port on 127.0.0.1, plus a `closed` case that points `UPSTREAM` at a port nothing listens on; four cases asserting exit status AND the exact message (or, for `ok`, that stdout contains `==> key settings` followed by the body); prints `N passed` and exits non-zero on any failure, in the style of `.claude/hooks/test-revert-guard.sh`.
- [X] T010 [US1] Reds for the tail via `scripts/mutate.sh --expect` on `docs/deploy/update.sh` with `bash docs/deploy/test-update-tail.sh` as the test command: (a) treat 404 as success → predict exactly the `notfound` case fails; (b) drop the empty-body check → exactly the `empty` case fails; (c) swallow curl's exit status (`|| true`) → exactly the `closed` case fails, reporting "unusable" instead of "stopped answering". Record all three in `redden-list.md`; commit.

**Checkpoint**: the script's tail is proven in all four outcomes without a server. (Its live proof is the box's next deploy, outside this arc.)

---

## Phase 4: User Story 2 — Anyone can ask the running server (P2)

**Goal**: `GET /settings` serves the block as JSON, and as the text block under `Accept: text/plain`; every listed key is present on every config with value, default and source; `/config` is untouched (FR-003, FR-003a, FR-004, FR-005, FR-011, FR-011a, FR-012).

**Independent test**: unit tests on `settings::build` for content, integration tests that the wire carries the built value unchanged, the `/config` byte diff.

- [X] T011 [P] [US2] Unit tests in `crates/cloudkitty-server/src/settings.rs` (`#[cfg(test)] mod tests`), each with a doc line naming its FR: **golden** — build from a two-seat fixture toml (not the served `cloudkitty.toml`, whose roster count would make the golden move with every reseat) and assert the exact ordered `Vec<String>` of `group.key` names against a literal array (FR-011; seats appear as `kitty.1`, `kitty.2`); **minimal + one optional key** — fixture = `Config::default()` serialized to TOML and re-parsed as `toml::Value`, the nine optional listed keys removed (research R10 names them; `[watchdog]` absent), the text re-parsed as `Config` to prove validity, then `[actions] groom_cuddle_relief = 15.0` inserted (the default, on purpose); assert `world.*`, `kitty.*`, `vision.*`, `actions.groom_cuddle_relief` read `Toml` and every other entry reads `Default` (FR-011a, FR-003a); **no file** — `build(&config, &wd, None)` → every source `Default` (FR-011a); **sentinels** — margin absent → value and default both `"unbounded"`, floor absent → `"none"`, margin `= 0` → value `0`, default `"unbounded"` (FR-003); **grammar** — `render_text()` on the minimal fixture: first line `engine_defaults_sha256 = <64 hex>`, a defaulted line matches `^[a-z_]+\.[a-z_]+ = .+ \(default: .+\) \[(toml|default)\]$`, a `world.*` line has no parenthesis, trailing newline (contracts §2); **announce** — install a `tracing_subscriber::fmt` subscriber writing to a shared `Vec<u8>` (a `MakeWriter` over `Arc<Mutex<Vec<u8>>>`) via `tracing::subscriber::with_default`, call `announce()`, assert the captured bytes contain `render_text()` verbatim (FR-012).
- [X] T012 [P] [US2] Add `get_settings` to `crates/cloudkitty-server/src/api.rs`: `pub async fn get_settings(State(state): State<AppState>, headers: HeaderMap) -> Response`; if the `Accept` header's value contains `text/plain`, respond `200` with `Content-Type: text/plain; charset=utf-8` and `state.settings.render_text()`; otherwise `Json(state.settings.clone())` (research R6). Doc comment: spec 052 contracts §1/§2, read-only, FR-005 (touches nothing `/config` serializes).
- [X] T013 [US2] Add `.route("/settings", get(api::get_settings))` after the `/config` route in `crates/cloudkitty-server/src/lib.rs`.
- [X] T014 [US2] Integration tests in `crates/cloudkitty-server/tests/server_integration.rs`: **wire == built** — boot via `start_server`, build the expected block with the same helper, assert `reqwest::get(url("/settings")).json::<Value>()` equals `serde_json::to_value(&expected)` and that a request with `Accept: text/plain` returns `Content-Type` starting `text/plain` and a body equal to `expected.render_text()` (FR-012, SC-004); **complete on a minimal config** — the `test_config()` roster sets no optional keys, so assert every `group.key` in the golden list is present in the JSON `entries`, every entry has a `source`, and no `value` is `null` (FR-004, SC-002); one more line: `reqwest::Client::new().post(url("/settings")).send()` answers 405 (US2 scenario 6, inherited from the `get()` route).
- [X] T015 [US2] Reds via `scripts/mutate.sh --expect`: (a) in `settings.rs` drop `water.contagion_membership` from the list → exactly the golden test fails naming it; (b) decide `Source` by `value == default` → exactly the minimal-fixture test fails on `actions.groom_cuddle_relief`; (c) `None` presence returns `Toml` → exactly the no-file test fails; (d) render `None` as `null` → exactly the sentinel test fails; (e) in `api.rs` ignore the `Accept` header → exactly the text half of wire-==-built fails; (f) serve a clone with one entry's `source` flipped → exactly the JSON half fails; (g) in `announce()` log a different string (the JSON) → exactly the announce test fails. Record each in `redden-list.md`; commit.
- [X] T016 [US2] SC-003: repeat quickstart §0's `/config` capture as `config-after.json` and `cmp` against `config-before.json` (byte-identical); re-run the stamp test and compare the value to cycle 0's; record both in `redden-list.md`.

**Checkpoint**: `curl /settings` and `curl -H 'Accept: text/plain' /settings` on a local server match data-model.md; `/config` unchanged.

---

## Phase 5: User Story 3 — The journal says the same thing (P3)

**Goal**: one `key settings` block logged at info level after validation and before the first tick, the same text the endpoint serves; the existing per-spec lines untouched (FR-006, FR-006a, FR-007).

**Independent test**: boot a local server and compare the journal block to the text fetch by eye (quickstart §5); the equality is by construction (one renderer), pinned by T014.

- [X] T017 [US3] In `crates/cloudkitty-server/src/main.rs`, after the watchdog "standing by" `tracing::info!` and BEFORE `sim_task::spawn(...)`, add `settings.announce();` with a comment: spec 052 FR-006 (before the first tick), FR-006a (the block is the same `Arc` the endpoint serves), FR-007 (the wet-fur / contagion / vision / ladder lines above stay as their specs' evidence). Do not edit those lines.
- [X] T018 [US3] Run quickstart §5 by hand on `cloudkitty.toml` (a scratch copy with `[world] bind = "127.0.0.1:0"`-style port if 8090 is busy): confirm one block in the boot log, `curl -H 'Accept: text/plain'` byte-identical to it, the JSON carrying every entry; paste the block into `redden-list.md` as the arc's served-toml reading (which keys read `[toml]` vs `[default]` — read, do not assume). Commit.

**Checkpoint**: journal, endpoint and (via T010's stub) the script tail all speak the same block.

---

## Phase 6: Polish & cross-cutting

- [X] T019 [P] Add one row to the endpoint table in `README.md` after the `GET /config` row: `| \`GET /settings\` | The key settings — every dial anyone has needed to verify after a deploy, each as effective value, engine default and source (\`toml\` / \`default\`); \`Accept: text/plain\` returns the boot-log block verbatim |` (in the table's register; no other README edit).
- [X] T020 [P] In `docs/deployment.md`: under "Updating", one paragraph after the `update.sh` paragraph saying the script now ends with a `key settings` section read from the running server, and that a non-zero exit AFTER the `deployed` line means the world is serving but the section could not be produced (older binary, unusable answer, or the server stopped answering) — no rollback happened; under "What is public, on purpose", one bullet: `GET /settings` is public like `/config`, lists dials only (no paths, no bind address). Owner's existing prose untouched.
- [X] T021 [P] Add one line to `## Unreleased` in `CHANGELOG.md` (no compatibility marker): the key settings block — boot log, `GET /settings` (JSON, or the text block under `Accept: text/plain`), and `update.sh`'s closing section with a non-zero exit when it cannot be produced (spec 052).
- [ ] T022 Add one step to `.github/workflows/ci.yml` after `Tests (includes the Articles I-III invariant suite)`: `- name: Shell tests (deploy tail, hook self-tests, mutate runner)` with `run: |` and the four lines `bash docs/deploy/test-update-tail.sh`, `bash .claude/hooks/test-revert-guard.sh`, `bash .claude/hooks/test-checkout-guard.sh`, `bash scripts/test-mutate.sh` (research R12; FR-015). Comment above the step: spec 052 — every guard in the tree runs here; the four build their fixtures under `mktemp -d`. Run all four locally first; after the push, confirm the step appears in the branch's CI run and passes (SC-007), and record the run URL in `redden-list.md`. Red for the step itself: push one commit with a deliberate `exit 1` appended to `scripts/test-mutate.sh`, see the run fail on that step, revert — recorded as the CI red in `redden-list.md`.
- [X] T023 Final cycle: `cargo test --workspace --no-fail-fast`, fmt + clippy CI-exact, `bash docs/deploy/test-update-tail.sh`; predict count = cycle 0 + the new tests (T011: 6, T014: 2); record as the final cycle in `redden-list.md`; commit.
- [ ] T024 Open the PR from `052-key-settings` against `main` with the house body (what / why / behavior table from contracts §4 / verification table from `redden-list.md` with predicted vs observed / not covered: the live deploy print is the box's next deploy); wait for CI treating "no checks reported" as pending; report to the owner. Merge only on the owner's word.

---

## Dependencies

- Phase 2 (T002–T006) blocks US2 and US3. US1 (T007–T010) depends on nothing in the crate — it can run before or in parallel with Phase 2.
- Within US2: T011 and T012 are parallel; T013 after T012; T014 after T013; T015 after T011 + T014; T016 after T013.
- US3 (T017) after Phase 2; T018 after T013 + T017.
- Phase 6: T019–T021 parallel, any time after Phase 2; T022 after T009 (its test must exist) and before T024's CI wait; T023 after everything; T024 last.

## Parallel example

```text
Session A: T007 → T008 → T009 → T010     (script + stub test; no crate dependency)
Session B: T002 → T003 → T004 → T005 → T006 → T011 ∥ T012 → T013 → T014 → T015 → T016 → T017 → T018
Then:      T019 ∥ T020 ∥ T021 ∥ T022 → T023 → T024
```

## Implementation strategy

MVP = Phase 2 + US1 + the endpoint half of US2 (T012–T014): at that point a deploy prints the section. The content guards (T011, T015), the boot log (US3) and the docs complete the spec; none of them changes the wire. Nothing deploys from this arc; the first live print is the box's next deploy and is reported then.
