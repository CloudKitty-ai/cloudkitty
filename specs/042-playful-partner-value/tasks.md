# Tasks: Playful 2.0 — partner-value play selection

**Input**: Design documents from `specs/042-playful-partner-value/`

**Prerequisites**: plan.md, spec.md (3 clarify rulings), research.md
(D1–D9), data-model.md, contracts/behavior-dials.md, quickstart.md

**Tests**: INCLUDED — spec FR-011 mandates rule-5/6 discipline: every
new guard shown red first, the must-green pile sorted before running.

**Organization**: Execution order follows the plan's two-commit
contract — **US3 (config surface, commit 1) → US1 + US2 (behavior
rewiring, commit 2)**. Spec priority (P1 = the score) names where the
value lives; US3 is the pure prerequisite, exactly 041's pattern.
Unlike 041, there is NO intentionally-red intermediate state: every
commit is fully green, and the golden evolution digest (pin
`7b361b2a…`) is a **must-GREEN throughout — a red golden is a HALT**
(the inert-launch claim failed).

## Format: `[ID] [P?] [Story] Description`

All paths relative to the worktree root `~/ai/cloudkitty-playful/`.

---

## Phase 1: Setup

- [X] T001 Confirm worktree `~/ai/cloudkitty-playful` on branch `042-playful-partner-value` fast-forwarded to origin/main (plan merged @ b48c264); `git fetch && git status -sb`; `cargo test --workspace` green at base
- [X] T002 Record the baseline `engine_defaults_sha256` value (from a run of the suite.rs stamp tests or a one-off print) and confirm `golden_evolution_flag_absent_10k_ticks` green, into `specs/042-playful-partner-value/continuity-baseline.md` — BOTH must be unchanged at the end of the feature (contract §2, quickstart §Prerequisites)

---

## Phase 2: Foundational (rule-6 sort)

**⚠️ CRITICAL**: no story work until the list exists.

- [X] T003 Write the sorted test list to `specs/042-playful-partner-value/redden-list.md` from research D9: **must-green headline** = golden digest (pin 7b361b2a), full `selection.rs`/`playful.rs` batteries at defaults, `approach_etiquette.rs`, behavior_variation, both shipped-config sweeps, defaults-stamp tests, Article I–V property suites; **new red-first guards** = one per dial per D9's list. Name exact test fns; record the D9 coupling watch items (`solo_play_reach`/urgent interplay, `should_wait_for`, opportunism pass untouched)

**Checkpoint**: baselines banked, list written.

---

## Phase 3: User Story 3 — The dial surface launches inert and sweep-ready (Priority: P3, **commit 1**) 🎯 first landable increment

**Goal**: twelve dials at identity defaults, skip-serialized at
identity (stamp UNMOVED), validated, documented — pure addition,
everything green.

**Independent Test**: config validation guards + stamp compare vs
T002 + golden green; each dial loads alone in a scratch config.

- [X] T004 [US3] Red-first validation guards: extend the `[behavior]` nan/negativity test table in `crates/cloudkitty-core/src/config/mod.rs` tests with all 12 dials (`w_value`, `w_busy`, `w_serious`, `t_self`, `t_partner`, `critter_appeal` finite-only, and the six `comfort_weight.*`). Predicted red: compile error on missing fields, then poison-accepted before the validate.rs entries (rule 5 — predict each before running)
- [X] T005 [US3] Add the six score/gate fields to `BehaviorConfig` in `crates/cloudkitty-core/src/config/mod.rs` — f32, identity default 0.0 via serde default fns, each `skip_serializing_if` at identity (copy the `pounce` field's 039-D5 idiom + comment), doc comments naming spec 042 + the convention that pricing is the sweep's
- [X] T006 [US3] Add `ComfortWeights` struct (eat/drink/sleep/play/cuddle/bath f32, each default 1.0, `is_identity` helper) + `#[serde(default, skip_serializing_if = "ComfortWeights::is_identity")] comfort_weight` field on `BehaviorConfig`, same file
- [X] T007 [US3] Append the dial checks inside `validate_behavior` in `crates/cloudkitty-core/src/config/validate.rs` (spec-020 section order untouched): finite ≥ 0 for the three `w_*`, both `t_*`, and all six weights; finite-any-sign for `critter_appeal`; errors name `[behavior] <field>` / `[behavior.comfort_weight] <need>` — flips T004 green
- [X] T008 [P] [US3] Add the commented documentation block to `cloudkitty.toml` `[behavior]` section (the `[elements]` placement-dials pattern: dials listed with identity values, commented out, one-line meanings + "priced by the joint sweep") — NO live keys (contract §6)
- [X] T009 [US3] Verify: `cargo test --workspace` fully green; `engine_defaults_sha256` IDENTICAL to T002's baseline (contract §2 — if it moved, a skip-at-identity is missing: HALT and fix); golden digest green
- [X] T010 [US3] Commit 1: "spec 042 commit 1/2: the dial surface (identity defaults, stamp unmoved)" — message cites the stamp compare and the 12 red-first validation guards

**Checkpoint**: config surface live and provably inert; sweep configs could already set dials (they'd just feed nothing until commit 2).

---

## Phase 4: User Story 1 — Partner-value play selection (Priority: P1, **commit 2, part 1**)

**Goal**: the scored ranking replaces the distance pick — admission
(D2), eligibility filter (D3), score arithmetic + total order (D4),
busy-adjacent solo fallback (D5). Byte-identical at defaults.

**Independent Test**: research D9's per-dial guards on staged worlds;
the identity guard; golden stays green.

### Red-first guards (write ALL, run once, record each predicted red)

- [ ] T011 [US1] Write in `crates/cloudkitty-core/src/behavior/selection.rs` tests (using the existing `decision_context`/staging idioms): (a) **identity guard** — all-defaults pick equals today's on a staged mixed field with friends, critters, and a distance tie (green on arrival, pinned as the SC-001 unit witness); (b) **value ranking** — adjacent zero-play-need friend vs distant high-need friend at `w_value > 0` → distant wins (red: distance pick takes adjacent); (c) **`t_partner` eligibility** — zero-need adjacent friend below threshold → critter/solo, friend left in peace (red); (d) **`t_self`** — own play need below threshold → no friend bothered (red); (e) **eligibility-filter semantics, clarify ruling 1** — best-*scoring* friend fails `t_partner`, lower-scoring friend passes → the passing friend wins (red)
- [ ] T012 [US1] Write red-first: (f) **wait cost** — two equal-need friends, one mid-scene, at `w_busy > 0` the free one wins (red only once busy admission exists — predict accordingly); (g) **busy admission, D2** — at ALL-DEFAULT dials a busy adjacent friend is NOT picked and today's next choice is (green-on-arrival pin, the byte-identity witness for admission); at `w_value > 0` the busy friend may rank; (h) **seriousness excludes play, clarify ruling 2** — candidate with high EAT pressure penalized at `w_serious > 0`; equal candidate with high PLAY pressure NOT penalized (red); (i) **standalone appeal, clarify ruling 3** — raising `w_value` alone moves no critter's rank; raising `critter_appeal` alone moves only critters (red)
- [ ] T013 [US1] Write red-first: (j) **busy-adjacent fallback** — adjacent mid-scene best pick yields `play_solo`, never `Action::play_with`, never `Idle` (red: today's code path can't produce the scenario until admission exists — stage via direct `play_action_with` call with a busy target)
- [ ] T014 [US1] Write red-first: (k) **FR-010 re-selection** — stage a cat one step into a chase toward a distant high-value friend, collapse that friend's play need (or fill it) between ticks, assert the next decision tick's pick changes (redirect or critter/solo) — no target lock-in. Predicted red only if implementation ever caches the pick; on today's re-scan idiom this is a green-on-arrival pin: it exists so FR-010 is guarded, not vacuous (analysis C1)
- [ ] T015 [US1] Write red-first: (l) **FR-008 exclusion under score** — a chase-excluded friend with the highest value at `w_value > 0` is NOT ranked (the score must not resurrect written-off targets); same for a stalled-pursuit target (analysis C2; predicted red if admission skips the `is_viable` bookkeeping)

### Implementation

- [ ] T016 [US1] Rewrite the body of `nearest_viable_playmate` (`crates/cloudkitty-core/src/behavior/selection.rs:247`), keeping the `(ctx) -> Option<(TargetRef, Position)>` signature (D1): candidate admission per data-model §2 step 1 (free friends + critters always; mid-scene friends iff `w_value > 0`; chase-exclusion/stalled-pursuit via the existing `is_viable` bookkeeping — split its busy check out so exclusion/patience still apply to all candidates); eligibility filter (step 2); ranking by `score` via `f32::total_cmp` desc with ascending `(manhattan_distance, tag, id)` behind it (step 3)
- [ ] T017 [US1] Add the score helpers in the same file: `expected_wait` from the partner's `ActivityClock` + `Activity::bounds(&config.actions.durations).min`, clamped ≥ 0 (D4); `top_non_play_pressure` (max over eat/drink/sleep/cuddle/bath); friend `value`/`score` and critter `score = critter_appeal − distance` per data-model §1
- [ ] T018 [US1] Add the busy-adjacent solo fallback in `play_action_with` (`selection.rs:340`): adjacent kitty target mid-scene → `Action::play_solo()` for the tick (D5); the `Action::play_with` arm now fires only for free adjacent kitties and critters (FR-004 defense in depth)
- [ ] T019 [US1] Run the batteries: all T011–T015 guards green; must-green pile (full selection/playful/etiquette battery, `solo_play_reach`/urgent rule, `should_wait_for` etiquette) untouched-green; golden digest GREEN (HALT on red)

**Checkpoint**: the score is live and provably inert at defaults.

---

## Phase 5: User Story 2 — Weighted get-serious trigger (Priority: P2, **commit 2, part 2**)

**Goal**: per-need weighted pressures vs the comfort line,
trigger-only.

**Independent Test**: both-direction weight guards + the all-1.0
identity guard + the trigger-only guard.

- [ ] T020 [US2] Write red-first in `crates/cloudkitty-core/src/behavior/playful.rs` tests: (a) eat weight 1.5, eat pressure between comfort/1.5 and comfort → gets serious where unweighted stays playful (red); (b) bath weight 0.5, bath pressure between comfort and comfort/0.5 → stays playful where unweighted trips (red); (c) all-1.0 weights reproduce the unweighted decision across a staged pressure sweep (green-on-arrival identity pin); (d) trigger-only (US2/AC4) — when the weighted check trips, the serious action equals what `selection::choose` picks from unweighted needs (green-on-arrival pin)
- [ ] T021 [US2] Replace the check at `crates/cloudkitty-core/src/behavior/playful.rs:56-64`: `max over NeedKind::ALL of comfort_weight(kind) · pressure(kind) >= playful_comfort` (D6); update the comment block (the comfort line + weights story, spec 042)
- [ ] T022 [US2] Run: T020 guards green; full playful battery green; golden digest GREEN

**Checkpoint**: both levers live, everything green, still byte-identical at defaults.

---

## Phase 6: Polish & PR

- [ ] T023 Re-read `redden-list.md` against what actually ran: every red-first guard seen red for its predicted reason, every must-green green (running is not reading — rule 6); record the OBSERVED notes in the file
- [ ] T024 Final continuity: golden digest ×3 green; `engine_defaults_sha256` compare vs T002 — identical; `cargo test --workspace` + clippy + fmt clean
- [ ] T025 Smoke run (quickstart §End-to-end): scratch config in the scratchpad with `w_value = 1.0`, `t_partner = 20`, `comfort_weight.eat = 1.5` on a scripted world; watch a playful seat redirect toward a high-need friend and get serious on a food peak; record a line in redden-list.md OBSERVED
- [ ] T026 [P] Add the one-liner to `## Unreleased` in `CHANGELOG.md` (no compatibility markers apply: stamp unmoved, no schema, no world-fresh, no rng change — say so)
- [ ] T027 Commit 2: "spec 042 commit 2/2: partner-value selection + weighted trigger (byte-identical at defaults)"; open the implementation PR (2 commits, base main) — body = inert-launch evidence (golden ×3, stamp compare), per-dial red-first list, sequencing note for Experiments' sweep; wait on CI. **Merge is the owner's word**

---

## Dependencies & Execution Order

- **Phases strictly sequential**: 1 → 2 → 3 (commit 1) → 4 → 5 → 6
  (commit 2 + PR). US1 and US2 share commit 2 but are independently
  testable (different files, different guards).
- Within US3: T004 (red) before T005–T007 (green); T008 parallel;
  T009 before T010.
- Within US1: T011–T015 (guards, one file — write together, run once)
  before T016–T018; T019 last.
- Within US2: T020 before T021; T022 last.
- **Story independence caveat**: US1/US2 are testable independently
  but ship in one commit (plan §Commit sequence); US3 alone is the
  only separately-landable increment.

### Parallel Opportunities

Limited — selection.rs and config/mod.rs each serialize their own
tasks. Genuinely parallel: T008 (toml comments) beside T005–T007;
T026 (changelog) beside T023–T025.

---

## Implementation Strategy

1. Phases 1–3 → **commit 1 verified alone** (stamp identical, golden
   green): the config surface is a pure-addition no-op and the only
   independently-landable increment.
2. Phases 4–5 → commit 2, fully green (no intentionally-red
   intermediate state anywhere in this feature).
3. Phase 6 → continuity ×3 + smoke → PR.

HALT conditions: golden digest red at ANY point (the inert-launch
claim failed — find the leak, do not regenerate); stamp moved at T009
or T024 (a skip-at-identity is missing); any green-on-arrival
identity pin (T011a, T012g, T020c/d) failing (the defaults path
diverged from today).
