# Tasks: Observation Schema 2 — In-Water Self-Signal and Raised Wet-Fur Pricing

**Input**: Design documents from `/specs/026-in-water-obs/`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/observation-v2.md, quickstart.md

**Tests**: requested (Article VI / house practice). Each story's tests
land with its edit — one coherent unit per task, no ceremony.

**Organization**: by user story, so each is independently verifiable.

## Phase 1: Setup

No setup tasks. The worktree, branch, and design artifacts exist; no
scaffolding, dependencies, or tooling changes are needed.

## Phase 2: Foundational

No foundational tasks. US1 carries the generation bump itself; every
other story is either independent of it (US2, US4) or tests against
whatever constants are compiled (US3).

## Phase 3: User Story 1 — A kitty can see that it is wet (P1) 🎯 MVP

**Goal**: the in-water flag exists in the self block; generation 2 is
real (schema 2, default length 183); layout otherwise unmoved.

**Independent Test**: `cargo test -p cloudkitty-rl` — layout asserts
183, flag reads 1.0 on a water tile / 0.0 elsewhere, adjacency does
not leak, determinism holds.

- [ ] T001 [US1] Add the in-water flag to the self block in
  `crates/cloudkitty-rl/src/observe.rs`: `SELF_BLOCK` 33→34 (:59),
  push the flag immediately after the in-sunbeam push (:199-202) —
  1.0 iff any water element's `pos` equals `me.pos` in the snapshot
  (tile-derived; independent of activity and of `[water]` dials, per
  research.md R1) — bump `OBSERVATION_SCHEMA_VERSION` 1→2 (:45), and
  update the module doc (:1-31), which is the normative layout doc,
  including the deliberate tile-vs-activity asymmetry with the
  neighboring in-sunbeam flag.
- [ ] T002 [US1] Update and extend the codec tests in
  `crates/cloudkitty-rl/src/observe.rs` (tests module, :467+):
  `the_default_layout_is_182_values` becomes the 183 assertion
  (rename to match); add flag tests — kitty on water tile → 1.0,
  on grass → 0.0, water on an *adjacent* tile → 0.0, water-related
  activity on a dry tile → 0.0; assert the flag's exact index (self
  block position) so a layout drift fails loudly; assert
  `observation_len` under a non-default slot config is exactly gen-1
  + 1 (spec US1 scenario 4).
- [ ] T003 [US1] Point the three test-helper headers at the compiled
  constant instead of a literal 1: `crates/cloudkitty-rl/src/policy.rs`
  (:290, :300) and `crates/cloudkitty-rl/src/test_support.rs` (:38)
  use `OBSERVATION_SCHEMA_VERSION` so synthetic artifacts always match
  the binary's generation (research.md R2).

**Checkpoint**: `cargo test -p cloudkitty-rl` green; no literal 182 or
`observation_schema: 1` remains outside deliberately-stale fixtures.

## Phase 4: User Story 2 — Lounging in water costs enough to learn from (P2)

**Goal**: defaults 3.5 / 60 flow from `defaults.rs` through validation,
`GET /config`, and the boot banner; semantics untouched.

**Independent Test**: `cargo test -p cloudkitty-core` green; quickstart
SC-004 shows `3.5 60.0` from a `[water]`-less config.

- [ ] T004 [P] [US2] Raise the dial defaults in
  `crates/cloudkitty-core/src/config/defaults.rs`:
  `default_water_bath_gain` 1.5→3.5 (:92-94),
  `default_water_bath_gain_ceiling` 50→60 (:96-98); update the
  `[water]` field docs in `crates/cloudkitty-core/src/config/mod.rs`
  (:96-110) — the "legible framing" comment still describes 1.5 and
  must describe 3.5 (≈17.5× the 0.2/tick ambient rise), plus the
  owner's rationale (accumulated-cost signal for learning,
  2026-08-05; ceiling re-set 65→60 same day — the frozen heterogeneity
  exam's 4× bath cat is the binding constraint) and the narrowed
  trait headroom (max bath ratio ≈4.28,
  was ≈16.7 — configs that validated at ceiling 50 can now fail, and
  that is the certification-hygiene guard working).
- [ ] T005 [US2] Prove the defaults land: grep
  `crates/cloudkitty-core` tests for assumptions pinning 1.5/50 (the
  `water_safeguard.rs` suite sets explicit values and should be
  untouched — verify, do not weaken); add/extend a test asserting
  `Config::default()` yields gain 3.5, ceiling 60, and that
  `validate_water` passes the shipped roster arithmetic (63.5 < 75)
  and the frozen-exam sweep (heterogeneity: 60 + 14 = 74 < 75);
  run `cargo test -p cloudkitty-core` and fix only what the default
  change legitimately moved.

**Checkpoint**: core suite green with untouched semantics tests.

## Phase 5: User Story 4 — Main stays runnable between break and rollout (P2)

**Goal**: a fresh clone boots the default world on the gen-2 binary;
provenance intact.

**Independent Test**: quickstart SC-003 — boot with the repo config,
four kitties served, no artifact opened.

- [ ] T006 [P] [US4] Park the two policy seats in `cloudkitty.toml`:
  kitty 1 Miso and kitty 4 Kittybear `behavior` → `"needs_driven"`,
  each with a comment naming the parked artifact
  (`policies/e001-a2-s6.ckpolicy` / `policies/e002-m0-g998-s1.ckpolicy`),
  why (generation-1 artifact; a generation-2 binary refuses it at
  boot, by design), and the re-seat condition (exp-003's certified
  schema-2 winner at the post-exp-003 rollout). Keep both
  `[rl.policy.*]` blocks and their provenance comments verbatim;
  update only the block comments' "deployed" phrasing if it now
  overclaims.
- [ ] T007 [US4] Record the generation gap in `policies/README.md`
  (both artifacts are observation-schema 1 / width 182; unseated on
  main since spec 026; still running on the served box's schema-1
  binary until the post-exp-003 rollout), and add a server test in
  `crates/cloudkitty-server/tests/policy_kitty.rs` asserting the
  shipped `cloudkitty.toml` registers cleanly with zero policy
  references — `register_policy_behaviors` returns Ok without
  touching any artifact file (the early-return path, lib.rs:49-51).

**Checkpoint**: fresh-clone boot works (quickstart SC-003).

## Phase 6: User Story 3 — The generation wall is legible (P3)

**Goal**: refusal messages answer the contract's four questions
(file, seat, disagreement, remedy) in both directions.

**Independent Test**: `cargo test -p cloudkitty-rl artifact` plus the
server context test; message text asserts, not just variants.

- [ ] T008 [US3] Enrich the refusal texts in
  `crates/cloudkitty-rl/src/policy.rs`: `SchemaMismatch` display
  (:44-49) gains generation language and the remedy ("artifact was
  trained for observation schema {found}; this binary speaks
  {expected}; an artifact re-trained for this generation is
  required"); the first-layer `Shape` arm (:164-169) states alongside
  the widths that a mismatch against the compiled observation size
  ordinarily means the artifact predates the binary's observation
  generation. No new variants, no signature changes (research.md R4).
- [ ] T009 [US3] Assert legibility in
  `crates/cloudkitty-rl/tests/artifact_validation.rs`: the
  schema-mismatch error text carries found+expected+remedy; add the
  symmetric case (schema-2 artifact under schema-1 expectations —
  build with an explicit stale header); assert the width-gate message
  carries both widths and the generation hint; and verify the server
  context layer still prefixes policy name + path
  (`crates/cloudkitty-server/tests/policy_kitty.rs` — extend the
  existing corrupt-artifact test's assertion if it doesn't already
  pin the `[rl.policy.<name>].artifact (<path>)` context line).

**Checkpoint**: contract C3's four questions all answered by asserted
text.

## Phase 7: Polish & Cross-Cutting

- [ ] T010 [P] Sweep living docs for the old generation's numbers:
  grep `docs/` and `README.md` for `182` and observation-schema-1
  claims; update living documents only (historical specs and
  experiment results stay as written); confirm
  `crates/cloudkitty-py/src/lib.rs` needs no edit (re-export, :774).
- [ ] T011 Full verification: `cargo fmt --check`, `cargo clippy`
  workspace-clean, `cargo test --workspace` (foreground, generous
  timeout), then quickstart SC-002 (refusal, via a config copy
  re-seating a policy), SC-003 (fresh boot), SC-004 (dials on
  `GET /config` + boot banner). Confirm the engine-defaults stamp
  moved and record the new value in the PR body for Experiments'
  re-baseline (handoff §4 step 2).

## Dependencies & Execution Order

- **US1 (T001→T003)** first — it defines the generation everything
  else compiles against. T002/T003 follow T001 (same files/crate).
- **US2 (T004→T005)** and **US4 (T006→T007)**: independent of US1 and
  of each other — T004 and T006 are [P] eligible.
- **US3 (T008→T009)** after US1 (its tests assert against the
  compiled generation pair).
- **Polish (T010 [P], T011)** last; T011 is the gate.

## Implementation Strategy

MVP is US1 alone (the generation exists and is test-proven). Then
US2 + US4 in either order or interleaved, US3, polish. Single
implementer, sequential commits per task or per story — each
checkpoint leaves the tree green, so review can bisect cleanly.
