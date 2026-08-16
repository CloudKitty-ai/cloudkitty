# Tasks: Model Registry & Served Behavior Descriptions

**Input**: Design documents from `/specs/034-model-registry/`
**Prerequisites**: plan.md, research.md (D1–D8), data-model.md, contracts/registry-and-serving.md, quickstart.md
**Tests**: included — the constitution (Article VI) and the spec's acceptance scenarios require them; house style is tests-in-arc.

**Organization**: grouped by user story. US1 = serving (P1), US2 = registry as
source of truth (P2), US3 = enforcement (P2).

## Phase 1: Setup

- [ ] T001 Create `policies/registry.toml` with the three ship rows exactly per contracts/registry-and-serving.md §1–2 (sha-keyed tables, header comment block stating the born-in-the-artifact-PR / never-changes rules, plus the FR-002 anticipated forward values as comments — `"Scripted"` is fixed in code, `"Transformer · BC+PPO+leash"` expected for phase-1 lineage seats if the leash doctrine lands — documentation, not rows)

## Phase 2: Foundational (blocking prerequisites)

- [ ] T002 [P] Add `behavior_description: Option<String>` to `Kitty` in crates/cloudkitty-core/src/kitty.rs with `#[serde(default, skip_serializing_if = "Option::is_none")]` and a doc comment mirroring `behavior`'s: server-stamped presentation, registry/config authoritative on resume, never read by the engine (research D3)
- [ ] T003 [P] Registry loader in crates/cloudkitty-server/src/lib.rs: strict-parse structs for the file shape (deny_unknown_fields; required non-empty `architecture`/`recipe`/`display`), `fn load_registry_beside(artifact: &Path)` resolving `registry.toml` in the artifact's parent dir (research D2), typed errors distinguishing missing-file / parse / missing-row / empty-field; unit tests in-file for each error and the happy path

## Phase 3: User Story 1 — a viewer learns what kind of mind drives each cat (P1) 🎯 MVP

**Goal**: kitty objects on every serving surface carry `behavior_description`
per the contract table (§3): registry display for policy seats, "Scripted"
for builtins, absent for plugins.

**Independent test**: quickstart §2–3 — boot the shipped config and see
`"Scripted"` ×5; boot a fixture-seated config and see the row's display line.

- [ ] T004 [US1] Failing-first integration tests in crates/cloudkitty-server/tests/server_integration.rs: (a) shipped wall-window config serves `behavior_description == "Scripted"` for all kitties on `GET /kitties`; (b) a fixture temp-dir artifact + beside-it registry.toml seated on one kitty serves that row's `display` verbatim on `/kitties`, `/kitties/:id`, and `/world`; (c) a plugin-driven kitty's JSON has no `behavior_description` key; (d) `behavior` string unchanged in all cases (FR-009); (e) one WS message read asserting the field arrives identically over the socket (direct check on the payload-identical doctrine)
- [ ] T005 [US1] Extend `register_policy_behaviors` in crates/cloudkitty-server/src/lib.rs to resolve each seated artifact's sha256 against `load_registry_beside`, returning a `BTreeMap<String, String>` of `policy:<name>` → display; add `display = %…` to the existing `policy artifact validated` log line (research D4). Refusal wording is finalized in T009's contract — here just bail with context naming `[rl.policy.<name>]`, the artifact path, and the sha
- [ ] T006 [US1] Stamp function in crates/cloudkitty-server/src/lib.rs (`policy:*` → map lookup; `Behavior::is_builtin` → `"Scripted"`; plugin → `None`) and call it on the freshly generated world in crates/cloudkitty-server/src/main.rs before the sim task starts
- [ ] T007 [US1] Resume re-stamp in crates/cloudkitty-server/src/persist.rs, in the same loop that re-stamps `behavior` (registry authoritative over snapshot, research D3) — this threads the name→display map into the persist load path (signature change to the loader), and the re-stamp OVERWRITES unconditionally, including to `None` for plugin seats (a stale frozen description must not survive); extend the existing resume test module: a snapshot with a stale/absent description resumes with the freshly stamped value, a plugin-seated kitty's stale description clears to `None`, and a pre-034 snapshot (field missing entirely) loads then stamps

**Checkpoint**: quickstart §2–3 pass; US1 acceptance scenarios 1–3 green.

## Phase 4: User Story 2 — the registry is the auditable, atomic source of truth (P2)

**Goal**: the process rules live where artifact rules live.

**Independent test**: reading policies/README.md alone states the same-PR row
rule and points the "show brain" naming note at the registry.

- [ ] T008 [US2] Amend policies/README.md: add the same-PR registry-row rule to the Rules section (FR-003: a PR landing a top-level `.ckpolicy` adds its row; retirement keeps the row; Experiments authors rows at certification time), and rewrite the Naming-section pointer ("the human-readable description belongs … in a served field on `[rl.policy.*]`") to name `registry.toml` + spec 034, keeping the `description =`/deny_unknown_fields warning with its citation updated (FR-010)

**Checkpoint**: US2 scenario 1 is T001; scenarios 2–3 (rename/retire row
permanence) are properties of the sha-keyed design asserted by T010's test
comments — no further code.

## Phase 5: User Story 3 — a seating cannot silently skip the registry (P2)

**Goal**: both enforcement layers live and bite (FR-007 refuse + FR-008 repo
gate).

**Independent test**: quickstart §4–5.

- [ ] T009 [US3] Refusal integration tests in crates/cloudkitty-server/tests/server_integration.rs: startup against a fixture artifact whose beside-it registry lacks its sha fails with an error naming `[rl.policy.<name>]`, the artifact path, and the sha256; a fixture dir with no registry.toml at all fails the same way naming the looked-for path (contract §4). Tighten lib.rs error text if the assertions demand it
- [ ] T010 [P] [US3] Repo integrity test in crates/cloudkitty-server/tests/registry_integrity.rs (new): anchored via `CARGO_MANIFEST_DIR` to the repo's policies/, walk top-level `*.ckpolicy`, sha256 each (reuse `sha2`), strict-parse registry.toml, assert every file's sha has a row with non-empty fields — failure message names file + sha (FR-008, research D5); comment documents the deliberately unchecked row→file direction (rows outlive artifacts)

**Checkpoint**: US3 scenarios 1–2 green; deleting a row locally makes both
layers fail loudly (quickstart §5).

## Phase 6: Polish & cross-cutting

- [ ] T011 [P] CHANGELOG.md one-liner under `## Unreleased` (no `[stamp]`/`[obs-schema]` markers — research D7): registry + served behavior descriptions, spec 034
- [ ] T012 Full validation: `cargo fmt --check`, `cargo clippy --workspace --all-targets -- -D warnings`, `cargo test --workspace` green with zero pre-existing assertions modified (SC-003) — confirm during the run that no golden/exact-shape fixture pins kitty JSON (analysis A1 found none in the Rust suites; verify the claim holds once the field serializes); then quickstart §2 eyes-on boot (all "Scripted", `behavior` untouched)

## Dependencies & execution order

- T001 (registry file) blocks T010 and the shipped-config leg of T004; T002+T003 (parallel) block T005–T007
- US1 chain: T004 → T005 → T006 → T007 (T004 written first, failing)
- T008 (docs) is independent of all code — any time after T001
- T009 depends on T005; T010 depends only on T001
- T011 anytime; T012 last

**Parallel opportunities**: T002 ∥ T003 (different crates); T008 ∥ any code
task; T010 ∥ T009 (different files); T011 ∥ T012's prerequisites.

## Implementation strategy

MVP = Phases 1–3 (US1): the field serves correctly with the registry in
place. US3 (enforcement) and US2 (docs) complete the durability story and
are small. Single-session scope; one PR at the end (house practice: merge
only on the owner's word).
