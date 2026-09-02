# Tasks: Partner Consent Line for Playful Targeting

**Input**: Design documents from `/specs/047-consent-line/`

**Prerequisites**: plan.md, spec.md (FRs + Clarifications 2026-09-01), research.md (D1–D5), data-model.md, contracts/consent-gate.md

**Tests**: REQUIRED — FR-008 mandates red-first guards; every cycle (prediction → observed red → revert → green) is recorded in `specs/047-consent-line/redden-list.md`. READ THE COUNT after every suite run.

**Organization**: US1 = the gate (P1, MVP), US2 = identity at default (P2), US3 = validation (P3).

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

- [X] T001 Create `specs/047-consent-line/redden-list.md` with the cycle-log table (cycle #, guard, injected bug, predicted red, observed red, reverted-green) and a baseline section
- [X] T002 Baseline run: `cargo test --workspace` on the untouched branch; record the passing count and confirm the evolution-golden and defaults-stamp tests are green pre-change (baseline row in redden-list.md)

---

## Phase 2: Foundational

**Purpose**: the dial and the predicate every story consumes.

**⚠️ CRITICAL**: complete before any user story.

- [X] T003 Factor `top_non_play(k)` out of `partner_value` in `crates/cloudkitty-core/src/behavior/selection.rs` (pure refactor — same fold, one home; FR-009's single definition); suite count unchanged vs T002
- [X] T004 Add `consent_line: f32` to `BehaviorConfig` in `crates/cloudkitty-core/src/config/mod.rs` — placed in the spec-042 dial block, `#[serde(default, skip_serializing_if = "f32_is_zero")]`, `Default` 0.0, doc comment naming spec 047 and the three gated sites (research D1)
- [X] T005 Add `consent_blocks(ctx, k)` in `crates/cloudkitty-core/src/behavior/selection.rs`: `line <= 0.0` short-circuit FIRST, then `top_non_play(k) > line && top_non_play(k) > k.play` (strict both, research D4); unit tests pin the tie edges (top non-play == line → not blocked; top non-play == play → not blocked); rule-5 red by mutating `>` to `>=` (predict: only the tie pins red), revert, record

**Checkpoint**: dial exists (inert), predicate proven, ties pinned.

---

## Phase 3: User Story 1 — A burdened friend is left in peace (P1) 🎯 MVP

**Goal**: the owner's rule live on ALL THREE playful friend-play paths (FR-002, Clarifications 2026-09-01).

**Independent Test**: quickstart.md §2 — staged scenes per path; blocked friend never proposed to, critters/elements/solo untouched.

**⚠️ Test-first**: each site's guard is written BEFORE its site is wired — the pre-implementation red IS the site-removal proof Experiments asked for.

- [X] T006 [US1] Guard (site 1, ranking): eligibility-trio test against `scored_playmate` in `crates/cloudkitty-core/src/behavior/selection.rs` tests — line 30, adjacent friend at (play 10, eat 40) never selected; (play 10, eat 25) selected; (play 45, eat 40) selected. PLUS one score-ON sub-case (analysis C2, FR-005): with `w_value`/`w_serious` live, the blocked friend stays dropped and the under-line friend stays ranked — the gate must not live inside the score term. Predict red on the blocked cases (site unwired); observe, record
- [X] T007 [US1] Wire site 1: `.filter(|k| !consent_blocks(ctx, k))` on the `friends` iterator at candidate construction in `scored_playmate` (`crates/cloudkitty-core/src/behavior/selection.rs` ~:437); T006 green
- [X] T008 [US1] Guard: critter adjacent to a blocked friend is still chosen by `scored_playmate` (`crates/cloudkitty-core/src/behavior/selection.rs` tests); rule-5 red by temporarily applying the gate to the critter arm (predict: this guard alone reds), revert, record
- [X] T009 [US1] Guard (site 2, get-serious): playful above `playful_comfort` with play the winning need and a blocked friend nearest — `decide_action` returns a PLAY action that is not `play_with(friend)` (assert the positive: solo or element play, analysis C1 / Article III degradation), test in `crates/cloudkitty-core/src/behavior/playful.rs`. Predict red (site unwired); observe, record
- [X] T010 [US1] Wire site 2: consent-aware variant of `choose`/`nearest_viable_playmate` (parameterized internals, classic pub signatures byte-untouched, research D3) in `crates/cloudkitty-core/src/behavior/selection.rs`; switch `playful.rs:73` to it; T009 green, T006/T008 still green
- [X] T011 [US1] Guard (site 3, opportunism): blocked idle friend ADJACENT, no critter in reach, play need ≥ `worth_a_detour` — playful's opportunism rung yields no `play_with(friend)` AND the decision still lands on a lawful action with solo play reachable downstream (assert what the cat does, not only what it avoids — analysis C1), test in `crates/cloudkitty-core/src/behavior/playful.rs`. Predict red (site unwired); observe, record
- [X] T012 [US1] Wire site 3: parameterize `take_what_is_here` internals in `crates/cloudkitty-core/src/behavior/needs_driven.rs` + a consent-aware `adjacent_playmate` arm in `selection.rs`; playful's call (`playful.rs:52`) passes consent, needs_driven's entry point unchanged; T011 green
- [X] T013 [US1] Removal-red audit (FR-008 exactness): re-remove each site's check one at a time; confirm ONLY that site's guard goes red each time (three cycles), restore, full suite green with count recorded

**Checkpoint**: the gate is complete and each site independently proven.

---

## Phase 4: User Story 2 — Nothing changes until the dial is turned (P2)

**Goal**: byte identity at default; the 042 doctrine holds (FR-001, FR-005).

**Independent Test**: quickstart.md §1 — golden + stamp unmoved on the finished branch.

- [X] T014 [US2] Identity red cycle: temporarily set `Default` to 30.0 (predict: evolution golden AND defaults stamp both red — the dial serializes once non-zero); observe both, revert to 0.0, both green UNMOVED (research D5: a moved pin on the real branch is a bug, never a regen); record
- [X] T015 [US2] Guard (doctrine): with `consent_line` 30 set, a needs_driven kitty still conscripts a burdened adjacent friend (test in `crates/cloudkitty-core/src/behavior/needs_driven.rs`); rule-5 red by temporarily passing consent from needs_driven's `take_what_is_here` entry point (predict: only this guard reds), revert, record

**Checkpoint**: identity structural, needs_driven pinned untouched.

---

## Phase 5: User Story 3 — A bad dial value is refused loudly (P3)

**Goal**: negative/non-finite rejected at load naming the dial (FR-006).

**Independent Test**: quickstart.md §3.

- [X] T016 [US3] Add the `consent_line` row to the poison-table test `the_playful2_dials_reject_negative_and_non_finite_values` in `crates/cloudkitty-core/src/config/mod.rs` FIRST (predict red: nothing rejects yet); then add `("[behavior] consent_line", b.consent_line)` to the finite-and-non-negative loop in `crates/cloudkitty-core/src/config/validate.rs`; green; record

---

## Phase 6: Polish & Cross-Cutting

- [X] T017 [P] Add the commented `consent_line` row to `cloudkitty.toml`'s `[behavior]` section beside the 042 dials (wording from contracts/consent-gate.md)
- [X] T018 [P] Mirror spec 042's dial-documentation locations for `consent_line` (grep where `t_partner`/`w_value` are documented outside the source — README dial table if one exists; FR-007) and re-read `contracts/consent-gate.md` against the implementation, amending the contract if any name drifted
- [X] T019 [P] Add the one-line `## Unreleased` entry to `CHANGELOG.md` (changelog practice: marker + one-liner as the arc merges)
- [X] T020 Full gate: `cargo fmt --all --check`, CI-exact `cargo clippy --workspace --all-targets -- -D warnings`, `cargo test --workspace`; READ THE COUNT, record the suite trajectory (T002 baseline → final) in redden-list.md
- [X] T021 Walk quickstart.md §§1–4 top to bottom as written; fix any drift between the guide and reality

---

## Dependencies & Execution Order

- **Phase 1 → 2 → 3 → 4 → 5 → 6** is the natural order; Phase 2 blocks all stories.
- Within US1 the order is fixed by test-first pairs: T006→T007, T009→T010, T011→T012; T008 after T007; T013 last.
- US2 and US3 are independent of each other; both need Phase 2 (US2's T014 also wants US1 wired to be meaningful on the real branch — run it after Phase 3).
- Polish tasks T017–T019 are [P] (different files); T020–T021 last.

## Parallel Opportunities

Small single-crate feature — parallelism is limited by design (most tasks touch `selection.rs`/`playful.rs`). Genuinely parallel: T017/T018/T019.

## Implementation Strategy

MVP = Phases 1–3 (the gate, all sites proven). US2 (identity) and US3 (validation) are cheap and land in the same PR — this ships as one small PR like 043/046, with `redden-list.md` as the review's proof ledger.
