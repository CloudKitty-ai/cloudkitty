# Tasks: Surface-Expansion Export

**Input**: Design documents from `/specs/035-surface-expansion/`
**Prerequisites**: plan.md, research.md (D1–D8), data-model.md, contracts/expansion-tool.md, quickstart.md
**Tests**: included — Article VI, the spec's acceptance scenarios, and the attestation are the feature; house style is tests-in-arc.

**Organization**: by user story. US1 = the mind crosses unchanged (P1),
US2 = deaf and mute (P1), US3 = first-class citizenship (P2).

**Test inputs**: the three committed pre-wall artifacts in `policies/` ARE
the real old-generation fixtures (read-only, `CARGO_MANIFEST_DIR`-anchored);
synthetic small old-generation artifacts are written directly via the
crate's own writers with old-pin headers where small shapes are needed.

## Phase 1: Setup

*(none — existing workspace; no new dependencies per plan)*

## Phase 2: Foundational (blocking prerequisites)

- [ ] T001 [P] Tooling-only raw-read entry for v2 artifacts in crates/cloudkitty-rl/src/policy.rs: parses format/structure of ANY generation, skips the schema-pin equality checks, loud name + doc stating it is for `ckpolicy-expand` only and the serving loader is untouched (research D2); unit test reads the committed `policies/e004-a1-s2.ckpolicy` (schema 3) successfully while `PolicyArtifact::load` still refuses it
- [ ] T002 [P] Tooling-only raw-read entry for v3 artifacts in crates/cloudkitty-rl/src/attn.rs, same doctrine; unit test reads the committed `policies/attn-a1-s1.ckpolicy` while the serving path still refuses it
- [ ] T003 [P] Module skeleton in crates/cloudkitty-rl/src/expand.rs (+ `pub mod expand` in lib.rs): `EXPANSION_TOOL_VERSION = 1`, `NEW_HEAD_FLOOR = -1.0e4_f32`, the attestation struct (source/target/output/tool/counts/verdict per contract §4), and the target-position-class accounting (MAPPED / INVARIANT-ZERO / INVARIANT-FLOOR must partition exactly — data-model)

## Phase 3: User Story 1 — a certified mind crosses the generation wall unchanged (P1) 🎯 MVP

**Goal**: both families expand deterministically into first-class schema-4
artifacts with a passing structural attestation.

**Independent test**: quickstart §2–4.

- [ ] T004 [US1] v2 MLP map in crates/cloudkitty-rl/src/expand.rs per data-model (obs columns: identity 0..164, legacy digest identity 164..196, new rows fresh, clock 196→224; W1 column permutation with new columns INVARIANT-ZERO; head rows 34..43 identity, 43..50 INVARIANT-FLOOR with weights 0 + bias −1.0e4; hidden identity); unit tests: bijection counts on a synthetic old-pin fixture, determinism (two runs → identical bytes), clock column verified moved not duplicated
- [ ] T005 [US1] v3 entity-attention map in crates/cloudkitty-rl/src/expand.rs porting the oracle recipe (type rows 0–5 + 6–13 identity, clock 14→21, new type rows 14–20 INVARIANT-ZERO, msg_head[..9] identity / [9..16] INVARIANT-FLOOR, all else identity), with the deafness parameter set verified against experiments/attn-oracle-2026-08-15/model_v4.py during implementation (plan D3 duty — record the verification in a code comment naming the file); unit tests as T004's
- [ ] T006 [US1] The bin crates/cloudkitty-rl/src/bin/ckpolicy-expand.rs: hand-parsed args `<source> <output>`, attestation report printed per contract §4, refusals per contract §2 (current-pin source, unknown version/ahead-of-surface, corrupted, attestation failure — nonzero exit naming path + reason), warn-not-fail on a nonconforming output name; integration tests for every refusal in crates/cloudkitty-rl/tests/expansion.rs
- [ ] T007 [US1] Round-trip tests in crates/cloudkitty-rl/tests/expansion.rs: expand ALL THREE committed artifacts into a temp dir; each attestation passes with counts partitioning exactly; each output loads through the UNTOUCHED serving loader at current expectations (FR-007/SC-001); repeat one expansion and assert identical sha (SC-002)

**Checkpoint**: quickstart §2–4 pass; US1 scenarios 1–3 green.

## Phase 4: User Story 2 — the expanded mind is deaf and mute in the new vocabulary (P1)

**Goal**: the invariants hold behaviorally, not just structurally.

**Independent test**: quickstart §5.

- [ ] T008 [US2] Deaf/mute behavioral tests in crates/cloudkitty-rl/tests/expansion.rs: (a) forward-level fuzz — expanded synthetic mind's message-head argmax is never a post-wall kind across seeded-varied observations (SimRng), and logits are bit-identical when new-kind digest features vary between zero and nonzero (deaf, SC-003 second clause); (b) world-level — two-kitty world with full vocabulary enabled, expanded mind seated as a behavior, neighbor's new-kind meow injected into world state, tick forward: zero post-wall-kind emissions from the expanded kitty and decisions unchanged vs the uninjected world
- [ ] T009 [US2] Attestation mutation tests in crates/cloudkitty-rl/tests/expansion.rs: a deliberately corrupted expansion (one new head bias set to 0.0; one new input parameter set nonzero; one source parameter dropped) each produce verdict FAIL naming the violated class — the attestation cannot be satisfied by accident (SC-004)

**Checkpoint**: US2 scenarios 1–2 green; the invariants are engine-proven.

## Phase 5: User Story 3 — first-class citizen of the artifact machinery (P2)

**Goal**: the paper trail is complete before any artifact lands.

**Independent test**: reading policies/README.md alone answers naming,
provenance, and retirement questions for an expanded artifact.

- [ ] T010 [US3] Amend policies/README.md Naming section: the `-o4` surface-token convention (consistent with name-identifies-a-run — the surface is the one distinguishing axis), the registry recipe provenance string format ("`<recipe>`, expanded from `<sha>` by ckpolicy-expand v1", contract §5), and one retirement line for the cutover: Superseded-by is ARTIFACT lineage, not seat inheritance (the exp-004 successor seats at Clementine; the lineage mind supersedes nothing)

**Checkpoint**: US3 scenario 1's registry mechanics are spec-034 machinery
already in force; scenario 2 executes at the seating PR per FR-011.

## Phase 6: Polish & cross-cutting

- [ ] T011 [P] CHANGELOG.md one-liner under `## Unreleased` (no markers — FR-012): the expansion tool, spec 035
- [ ] T012 Full validation: `cargo fmt --check`, `cargo clippy --workspace --all-targets -- -D warnings`, `cargo test --workspace` green with zero pre-existing assertions modified (SC-005); quickstart §2–3 eyes-on (expand attn-a1-s1, verify attestation + repeated-run sha); quickstart §6 — expand all three, record the three output sha256s in the completion report for the Experiments handoff

## Deviations

*(record at implement time if any)*

## Dependencies & execution order

- T001 ∥ T002 ∥ T003 (different files) block everything after
- T004 needs T001+T003; T005 needs T002+T003; T004 ∥ T005 (same file —
  sequential in practice, independent in content)
- T006 needs T004+T005; T007 needs T006; T008 needs T004 (v2 synthetic
  suffices) and T005 for any v3 leg; T009 needs T003+T006
- T010 independent of all code; T011 anytime; T012 last

**Parallel opportunities**: T001 ∥ T002 ∥ T003; T010 ∥ any code task;
T011 ∥ T012's prerequisites.

## Implementation strategy

MVP = Phases 2–3 (US1): the tool exists, expands both families, attests,
and outputs first-class artifacts. US2 makes the invariants behavioral
truth; US3 is one README amendment. Single-session scope; one PR; merge on
the owner's word. The three real expanded artifacts are generated at T012
and handed to Experiments — committed only at the seating PR (research D7).
