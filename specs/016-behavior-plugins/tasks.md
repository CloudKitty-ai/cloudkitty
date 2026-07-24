# Tasks: Proposal Boundary Hardening & External Behavior Plugins

**Input**: Design documents from `/specs/016-behavior-plugins/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md,
contracts/wire-protocol.md, quickstart.md

**Tests**: included — this feature's P1 deliverable *is* a test suite
(FR-005), and Article VI makes the suites the acceptance instrument
(SC-001–SC-007).

**Organization**: grouped by user story. US3 (remote HTTP transport) is
**deferred by clarification** — it has no tasks; everything built here must
stay transport-agnostic (FR-007 note).

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

**Purpose**: capture the pre-change baseline the success criteria compare
against.

- [X] T001 Capture green baseline on the unmodified tree: run `cargo fmt --all --check && cargo clippy --workspace --all-targets -- -D warnings && cargo test --workspace`, and save a short summary (suite counts, pass/fail) to specs/016-behavior-plugins/baseline.txt

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: the constitutional ground rule and the one dispatch seam every
story builds on.

**⚠️ CRITICAL**: no user story work can begin until this phase is complete.

- [X] T002 Amend Article IV to v1.2.0 in .specify/memory/constitution.md using the wording drafted in research.md R10 (two safe outcomes — needs-based fallback as the default resolution, idle no-op — never an error state, never a reshaped legal action); update the sync-impact comment block per the file's own conventions and bump the version/amended date (FR-017)
- [X] T003 Extend the `Behavior` trait in crates/cloudkitty-core/src/behavior/mod.rs with the provided method `try_decide(&self, ctx) -> Option<Action>` defaulting to `Some(self.decide(ctx).await)` (research.md R11); route `run_catching` (both served and budgetless dispatch) through `try_decide` so a `None` takes the existing crashed-advisor path (fallback from the dealt seed, `FallbackTaken` provenance); all existing behavior tests must pass unchanged

**Checkpoint**: foundation ready — US1 can start; US2 additionally consumes
US1's parser.

---

## Phase 3: User Story 1 — A malformed proposal is never mistaken for a legal one (Priority: P1) 🎯 MVP

**Goal**: the action wire becomes a documented, tested contract: strict
parsing per shape, malformed → fallback (default), well-formed-but-illegal →
idle, both observable.

**Independent Test**: `cargo test -p cloudkitty-core proposal` — round-trip +
rejection matrix green with no plugin code in existence (quickstart step 2);
`Unintelligible` dispatch test proves failed-proposal → fallback end to end.

### Implementation for User Story 1

- [X] T004 [US1] Add `ProposalError` to crates/cloudkitty-core/src/action.rs with the kinds from data-model.md (NotJson, NotAnObject, MissingKind, UnknownKind, InvalidFields wrapping the mirror's serde error — which itself names unknown fields — TooLarge) and a human-readable Display used by the rejection log event
- [X] T005 [US1] Implement `parse_proposal(&str) -> Result<Action, ProposalError>` in crates/cloudkitty-core/src/action.rs per research.md R1 (hybrid-mirror variant): parse to `serde_json::Value`, require an object, take the `action` tag, deserialize the remaining fields into a per-variant mirror struct with `#[serde(deny_unknown_fields)]`, convert to the `Action` variant (Play's conversion carries the strict-target logic); the mirrors' accepted sets are the per-shape table in data-model.md; export `PROPOSAL_WIRE_VERSION: u32 = 1`
- [X] T006 [P] [US1] Round-trip suite in crates/cloudkitty-core/src/action.rs tests (module name containing `proposal` so quickstart's `cargo test -p cloudkitty-core proposal` filter matches): for every constructible shape (move × 4 directions, rest/sleep with and without `with`, groom both forms, eat, drink, chase × element/kitty, play solo + both targets, purr, meow × all 7 kinds, idle), `parse_proposal(serde_json::to_string(a)) == a` (SC-002 half 1; FR-005)
- [X] T007 [P] [US1] Rejection suite in crates/cloudkitty-core/src/action.rs tests (same `proposal` module-name rule as T006): table-driven malformed matrix per shape — unknown kind, missing required field, wrong-typed field, unrecognized closed-set value, incomplete target (chase without id, partial play target), unknown extra field, non-object JSON, non-JSON bytes — asserting the expected `ProposalError` kind; include every `rejected` example from specs/016-behavior-plugins/contracts/wire-protocol.md verbatim; assert `purr` parses (validation-idle, not parse error); and pin duplicate-key semantics (`{"action":"move","direction":"north","direction":"south"}` parses as move south — last occurrence wins before strict checks) (SC-002 half 2)
- [X] T008 [US1] Add the `Unintelligible` hostile behavior (overrides `try_decide` → `None`) to crates/cloudkitty-core/src/behavior/test_behaviors.rs, plus dispatch tests in crates/cloudkitty-core/src/behavior/mod.rs: on both the served and budgetless paths a `None` proposal resolves to the fallback deciding from the dealt seed with `FallbackTaken` provenance, and the tick completes (spec US1 acceptance scenario 3; FR-003)
- [X] T009 [US1] Update the module docs to the amended Article IV: crates/cloudkitty-core/src/behavior/mod.rs ("anything illegal becomes an idle turn" → the two-outcome rule with fallback as default) and crates/cloudkitty-core/src/action.rs header (name `parse_proposal` as the mandatory entry for external bytes, derive reserved for trusted internal data — research.md R2)

**Checkpoint**: SC-002 fully demonstrable; the wire is a contract.

---

## Phase 4: User Story 2 — A local program drives a kitty (Priority: P2)

**Goal**: `ScriptBehavior` — a long-running external process attached by
config, speaking one NDJSON exchange per decision on the hardened wire, under
every existing Article IV protection.

**Independent Test**: quickstart steps 3–5 — hostile endurance, well-behaved
day, kill-mid-run — all via `cargo test -p cloudkitty-core --test plugin_e2e`.

### Implementation for User Story 2

- [X] T010 [P] [US2] Add `reply_max_bytes` (default 65536) and `relaunch_cooldown_ticks` (default 20) to `BehaviorConfig` in crates/cloudkitty-core/src/config.rs with doc comments stating the defaults (Article VI), serde defaults, and non-zero validation in `Config::validate()` alongside `budget_strikes`/`bench_ticks` (including config tests)
- [X] T011 [US2] Create crates/cloudkitty-core/src/behavior/script.rs with the `DecisionRequest` type per data-model.md (`v`, `tick`, `kitty_id`, `me`, `world`, `seed`, `config`; `seed` is one u64 drawn from `ctx.rng` — research.md R5) and its serialization test
- [X] T012 [US2] Implement `ScriptBehavior` in crates/cloudkitty-core/src/behavior/script.rs: `Mutex<ChildState>` (NotSpawned/Running/Dead per data-model.md), lazy spawn, one-line write + capped one-line read (`reply_max_bytes`), reply parsed as the strict correlated envelope (`tick`/`kitty_id` must echo the request; `proposal` via `parse_proposal`); unparseable reply → failed proposal only; oversized reply or correlation mismatch → failed proposal **and** child killed (stream resync); any failure → `try_decide` returns `None`; relaunch gated by `relaunch_cooldown_ticks` against `ctx.world.tick`; stderr passed through; `is_builtin()` false; structured tracing events (`proposal rejected` with `ProposalError` + truncated sample, `plugin exchange failed`, `plugin reply desynced`, `plugin relaunched` — research.md R3/R8); register the module in behavior/mod.rs
- [X] T013 [P] [US2] Add fixture plugins under crates/cloudkitty-core/tests/fixtures/: a well-behaved script echoing the request's `tick`/`kitty_id` in the envelope and proposing simple legal actions (portable `python3` or `/bin/sh`), a hostile script emitting malformed output every decision, an oversized-reply script, and a desyncing script that emits an extra reply line; executable, no external dependencies
- [X] T014 [US2] Parse `PluginsConfig` (`[plugins.<name>] command/args`) in crates/cloudkitty-server/src/main.rs `load_config` alongside `RlConfig` — same file, separate struct, never placed in the served `Config` (FR-014); startup validation: command exists and is a file, else a clear startup error (FR-011), with a unit test asserting a nonexistent command yields that error (analysis finding C2)
- [X] T015 [US2] Add `register_plugin_behaviors(&mut BehaviorRegistry, &PluginsConfig)` to crates/cloudkitty-server/src/lib.rs constructing a `ScriptBehavior` per entry, and wire it in main.rs immediately after `register_policy_behaviors` and before `config.validate_behavior_names()` (the spec-014 seam), with a startup log line naming registered plugins
- [X] T016 [US2] End-to-end tests in crates/cloudkitty-core/tests/plugin_e2e.rs driving headless worlds with `ScriptBehavior` + the fixtures: `well_behaved` (600 ticks — one full in-world day — proposals applied, `PolicyMade` provenance; SC-004), `hostile` (1,000+ ticks, every tick completes, constitution invariants hold, all affected decisions `FallbackTaken`; SC-003), `killed_mid_run` (kill the child mid-run: zero missed ticks, fallback from the first affected decision, relaunch only after `relaunch_cooldown_ticks`; SC-005), `oversized_reply` (failed proposal + child killed; FR-010), and `desynced_reply` (extra-line fixture: the stale line is never applied — correlation mismatch → fallback + child killed + relaunch; analysis finding I1)
- [X] T017 [P] [US2] Add a commented example `[plugins.<name>]` block to cloudkitty.toml documenting command/args and the two `[behavior]` knobs' defaults — commented out so the default world runs plugin-free (FR-012, SC-006)

**Checkpoint**: SC-003/SC-004/SC-005 demonstrable; a real kitty can be driven
by a real script (quickstart step 7, owner smoke test).

---

## Phase 5: User Story 3 — A remote service drives a kitty (Priority: P3 — DEFERRED)

**No tasks.** Deferred by clarification (2026-07-23) to a future sitting.
Guardrail on the phases above: the proposal wire (T005) and `DecisionRequest`
(T011) carry no local-process assumptions — the HTTP transport must be able
to reuse both verbatim (contracts/wire-protocol.md, Compatibility promises).

---

## Phase 6: User Story 4 — A plugin author succeeds from the docs alone (Priority: P4)

**Goal**: the contract, lifecycle, and livelock warning rendered for authors,
with every example verified by a test.

**Independent Test**: quickstart step 6 (`cargo test -p cloudkitty-core
docs_examples`) plus a completeness read against FR-015/FR-016.

### Implementation for User Story 4

- [ ] T018 [P] [US4] Write docs/plugins.md: the wire contract per shape with `json accepted` / `json rejected` fenced examples (annotated exactly so for extraction), the `DecisionRequest` context and the correlated reply envelope (why the echo protects authors from their own desyncs), lifecycle (long-running, relaunch cooldown), budget/bench and failure semantics (the resolution table from contracts/wire-protocol.md), a worked end-to-end example using the demo plugin, and — prominently — the multi-agent livelock warning with the symmetry-breaking advice from crates/cloudkitty-core/src/behavior/mod.rs (FR-015, FR-016)
- [ ] T019 [P] [US4] Ship the runnable demo plugin docs/examples/demo_plugin.py referenced by docs/plugins.md and quickstart step 7: reads request lines, replies with the correlated envelope, proposes simple sensible actions, breaks symmetry using the request `seed`, comments aimed at first-time authors
- [ ] T020 [US4] Add the docs-extraction test (`docs_examples`) in crates/cloudkitty-core/tests/docs_examples.rs: `include_str!` docs/plugins.md, extract fenced blocks annotated `json accepted`/`json rejected`, assert each parses/fails via `parse_proposal` accordingly; fail the test if zero blocks are found (research.md R9; SC-007)

**Checkpoint**: all in-scope stories complete.

---

## Phase 7: Polish & Cross-Cutting

- [ ] T021 [P] Retire the two shipped P2 entries in BACKLOG.md ("Harden the whole proposal boundary", "External behavior plugins") with a shipped-in-016 note recording that the HTTP transport remains open (deferred, spec'd in specs/016-behavior-plugins/)
- [ ] T022 Run the automated quickstart gates (steps 1–6 and 8 of specs/016-behavior-plugins/quickstart.md), including `cargo fmt --all` **before** the final check (the 015 CI lesson); fix any fallout; record results in specs/016-behavior-plugins/post-check.txt. Step 7 (manual viewer smoke) is the owner's.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)** → nothing; run first.
- **Foundational (Phase 2)**: T002 independent; T003 blocks T008, T012.
- **US1 (Phase 3)**: needs T003; T004 → T005 → {T006, T007 in parallel};
  T008 after T003 (parallel with T004–T007); T009 after T002.
- **US2 (Phase 4)**: needs US1's T005 (the parser) and T003; T010, T013, T017
  parallel anytime in-phase; T011 → T012 → T016; T014 → T015.
- **US3 (Phase 5)**: no tasks (deferred).
- **US4 (Phase 6)**: T018/T019 parallel after US1 (examples need
  `parse_proposal` semantics settled; the worked example needs US2's shape);
  T020 after T018.
- **Polish (Phase 7)**: after all in-scope stories; T021 parallel with T022.

### Parallel Opportunities

- T006 ∥ T007 (both test-only, distinct test modules)
- T008 ∥ T004–T007 (different files)
- T010 ∥ T011 ∥ T013 ∥ T017 at the start of US2
- T014–T015 (server crate) ∥ T016 (core e2e) once T012 lands
- T018 ∥ T019; T021 ∥ T022

## Implementation Strategy

**MVP = Phase 1 + 2 + 3 (US1)**: the hardened wire alone is shippable — it
turns the action wire into a tested contract with zero behavior change for
every existing world. **Incremental**: US2 lands the plugin door on top of
the contract; US4 documents it; polish retires the backlog debt. Stop and
validate at each checkpoint (the suites are the gates). Commits follow the
repo convention: branch `016-behavior-plugins`, logical-unit commits, CI
green before merge.
