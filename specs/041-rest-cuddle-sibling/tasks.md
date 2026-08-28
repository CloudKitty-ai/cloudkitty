# Tasks: Rest becomes co-sleep's sibling

**Input**: Design documents from `specs/041-rest-cuddle-sibling/`

**Prerequisites**: plan.md, spec.md, research.md (D1–D9), data-model.md,
contracts/relief-dials.md, contracts/activity-event-tier.md, quickstart.md

**Tests**: INCLUDED — the spec mandates rule-5/6 discipline: every new
guard shown red first, the redden list sorted before running (D9).

**Organization**: Execution order follows the one-PR, three-commit
contract, so the story phases run **US3 → US1 → US2** (split →
engine sibling → reprice). Spec priority (P1 sibling) names where the
value and the risk live, not the build order: US3 is a pure
prerequisite, US2 is a config diff on top of both.

**Verification points** (owner-ratified): commit 1 verifies alone
(byte-identity); commits 2+3 verify together as one step. The
riders-partial arithmetic guards (T028) are *written* in commit 2,
shown red against the un-repriced toml, and turned green by commit 3's
config diff — that intermediate red is the rule-5 demonstration, and
commit 3 stays code-free.

## Format: `[ID] [P?] [Story] Description`

All paths relative to the worktree root `~/ai/cloudkitty-cuddle/`.

---

## Phase 1: Setup

- [X] T001 Confirm worktree `~/ai/cloudkitty-cuddle` is on branch `041-rest-cuddle-sibling` fast-forwarded to origin/main (plan merged @ 2555205); `git fetch && git status -sb`
- [X] T002 Baseline: `cargo test --workspace` green at the base commit before any edit (quickstart §Prerequisites)

---

## Phase 2: Foundational (rule-6 sort + continuity baseline)

**Purpose**: The sorted redden list and the pre-split digest are
prerequisites for every commit's verification.

**⚠️ CRITICAL**: No story work until both exist.

- [X] T003 Record the pre-split golden evolution digest ×3 (same seed + `cloudkitty.toml` + tick count, house practice) and save the digest values to `specs/041-rest-cuddle-sibling/continuity-baseline.md` for SC-001 comparison
- [X] T004 Sort the D9 redden list into named piles in `specs/041-rest-cuddle-sibling/redden-list.md`: **must-red** = rest conscription-legality behavior (`crates/cloudkitty-core/src/action.rs:375-378`), partner-binding/stamp assertions (~`action.rs:2245`, `:2613-2673`, ~`:1380-1400` classic-value-by-name), `crates/cloudkitty-rl/src/suite.rs:1512` dial sweep, nan-validation table (`crates/cloudkitty-core/src/config/mod.rs:~1829`), the two root-toml config sweeps; **must-green** = co-sleep pricing + warmth conduction, grooming, play, durations, golden digest, Article I–V property suites. List the exact test fn names, not just line ranges

**Checkpoint**: baseline digest banked, redden list written — commit work can begin.

---

## Phase 3: User Story 3 — The dial split, behavior-preserving (Priority: P3, **commit 1**) 🎯 first landable increment

**Goal**: `cuddle_relief` split into `rest_mutual_relief` +
`groom_cuddle_relief` at the classic value, `rest_drip_relief` added
at 0.0, old key accepted-but-inert — provably a no-op (SC-001/SC-002).

**Independent Test**: golden digest ×3 byte-identical vs T003; a
historical config carrying `cuddle_relief` loads and the key is inert.

### Red-first guards for US3

- [X] T005 [US3] Write deprecated-key guards in `crates/cloudkitty-core/src/config/mod.rs` tests, each shown red before its implementation exists: (a) config carrying `cuddle_relief` loads and the key feeds nothing, (b) a genuinely unknown key is still rejected, (c) `cuddle_relief = nan` is still a config error (inert key keeps its nan-table entry). Predict each failure before running (rule 5)
- [X] T006 [US3] Write the dial-independence guard in `crates/cloudkitty-core/src/action.rs` tests (red first): moving `rest_mutual_relief` alone changes only the rest-duet payment (`action.rs:797-798` site); moving `groom_cuddle_relief` alone changes only the groomer's warmth (`action.rs:762` site) — US3 acceptance scenario 3

### Implementation for US3

- [X] T007 [US3] Add `rest_mutual_relief` (default 15.0), `groom_cuddle_relief` (default 15.0), `rest_drip_relief` (default 0.0) to `crates/cloudkitty-core/src/config/mod.rs` (~:544-590); mark `cuddle_relief` deprecated/inert in its doc comment; add all three new keys to the nan-validation table (~:1829) keeping `cuddle_relief`'s entry
- [X] T008 [P] [US3] Add the split-at-classic comment to `crates/cloudkitty-core/src/config/defaults.rs` following the spec-028 pattern at :42-43
- [X] T009 [US3] Swap the two call sites in `crates/cloudkitty-core/src/action.rs`: groom rider `:762` → `groom_cuddle_relief`; rest duet `:797-798` → `rest_mutual_relief`. No other behavior change
- [X] T010 [US3] Update `cloudkitty.toml` (:225-267): add `rest_mutual_relief = 8.0`, `groom_cuddle_relief = 8.0`, `rest_drip_relief = 0.0` with provenance comments; keep `cuddle_relief = 8.0` in place marked deprecated/inert with a `3.0 config-hygiene: delete` marker (D8 handoff)
- [X] T011 [US3] Migrate the must-red pile from T004: run the suite, confirm each listed test went red **for the predicted reason** (rule 6 — a must-fail that stays green is vacuous; report pre-existing vacuity, don't fix silently), then repoint the classic-value-by-name assertions (~`action.rs:1380-1400`, `:2245`, `:2613-2673`) and the `suite.rs:1512` sweep at the new dial names
- [X] T012 [US3] Verify the must-green pile from T004 stayed green; `cargo test --workspace` fully green
- [X] T013 [US3] Run the golden evolution digest ×3 against T003's baseline — byte-identical required (SC-001). On any mismatch: HALT, this commit is not a no-op
- [X] T014 [US3] Spot-check SC-002 mechanics: load 2–3 of the 181 committed historical tomls (e.g. `phase1-cutover-bugs2.toml`) with the HEAD build; accepted + inert
- [X] T015 [US3] Commit 1: "spec 041: split cuddle_relief at the classic value (byte-identical)" — message cites SC-001 ×3 digest match and the migrated test list

**Checkpoint**: a provable no-op is on the branch; every price site now has its own dial.

---

## Phase 4: User Story 1 — Rest runs like co-sleep (Priority: P1, **commit 2**)

**Goal**: rest validates on availability, binds nobody, resolves
mutual/drip per serviced tick via one shared predicate, pays both
parties, carries tier counters onto `ActivityEnd` — with
`rest_drip_relief = 0.0` so this commit changes legality/binding/events
only.

**Independent Test**: quickstart §Commit 2 — `cargo test -p
cloudkitty-core action events` with every new guard shown red first.

### Shared predicate (behavior-preserving prerequisite)

- [X] T016 [US1] Extract the mutual predicate from `apply_sleep_relief`'s inline check (`crates/cloudkitty-core/src/action.rs:834-841`, evaluated once above both uses) into a named function (partner's activity matches `Sleeping | Resting`); swap co-sleep pricing and spec-031 warmth conduction to call it. Must-green: all co-sleep/warmth tests unchanged (D2 — this is a pure extraction)

### Red-first guards, batch A (legality + binding)

- [X] T017 [US1] Write red-first in `crates/cloudkitty-core/src/action.rs` tests: rest-with proposal toward a **busy** adjacent friend validates legal; toward a non-adjacent kitty resolves safely to idle (FR-001, US1 scenario 1). Predict the exact failure (today the busy-partner case is illegal via `is_conscriptable_friend`)
- [X] T018 [US1] Write red-first: partner is never bound (keeps own activity + clock untouched) and never stamped — the old conscription arm's mirrored-`Resting` write and `stamp_serviced(friend)` are the bugs these guards catch (US1 scenario 1)

### Implementation A

- [X] T019 [US1] Rewrite the Rest validate arm (`action.rs:375-378`): `is_conscriptable_friend` → `is_available_friend` (`crates/cloudkitty-core/src/world.rs:1155-1175`), matching the Sleep arm at `:379-382`. Single funnel, no parallel rule (FR-003)
- [X] T020 [US1] Rewrite the Rest apply arm (`action.rs:458-479`): no partner binding, no mirrored activity, no partner clock write — mirror the sleep apply shape
- [X] T021 [US1] Rewrite the Resting effects arm (`action.rs:797-799` + surrounding): per-tick partner re-filter by availability (mirror the Sleeping re-filter at `:808`), tier via the T016 predicate, pay **both** parties the resolved tier (`rest_mutual_relief` / `rest_drip_relief`), wandered partner → solo tick (posture only, no relief, duration clock not reset); drop `stamp_serviced(friend)`

### Red-first guards, batch B (tiers, counters, events, snapshots)

- [X] T022 [US1] Write red-first: tier resolves per serviced tick — a mid-scene partner settle flips drip → mutual on that tick, a wake flips back (no hysteresis, US1 scenario 2 + edge case); a rester beside a **sleeping** friend that never named it collects mutual from its own slot (US1 scenario 3)
- [X] T023 [US1] Write red-first: with `rest_drip_relief = 0.0` a busy-partner scene exists but pays nothing to either party (D5); with a nonzero test-config drip both parties are paid the drip rate
- [X] T024 [P] [US1] Add per-scene tier counters beside the activity clock in `crates/cloudkitty-core/src/kitty.rs`: two `u32`, `#[serde(default)]`, reset at scene start (data-model §3)
- [X] T025 [P] [US1] Add `mutual_ticks` / `drip_ticks` to `ActivityEnd` in `crates/cloudkitty-core/src/events.rs` (:30-46): `#[serde(default)]` on read, skip-serialized when zero; copied from the per-scene counters at scene end (contract activity-event-tier.md)
- [X] T026 [US1] Wire counter increments into the tiered effects arms (rest via T021, co-sleep via `apply_sleep_relief`): exactly one counter per serviced tick, mutual xor drip by the shared predicate; solo ticks increment neither. Guards red-first: sum-≤-span invariant driven red via a wandered-partner shortfall; a nonzero counter on any non-tiered activity is a bug; a zero-counter `ActivityEnd` serializes byte-identical to today's JSON (record a real payload, not a hand-written fixture — rule 5)
- [X] T027 [US1] Snapshot-resume guard red-first, then verify: a pre-change snapshot carrying a bound rest duet (both naming each other, live clocks) loads and resumes as two synchronized resters paying mutual — no error, no reshaping (FR-009, US1 scenario 5). Use a snapshot recorded from the pre-change build, not a hand-built one

### Verification for US1

- [X] T028 [US1] Write the riders-partial arithmetic guards (toml-driven, reading `cloudkitty.toml`): each rider's `rate × min_ticks` from a single slot < 5.1 measured mean need; drip < mutual within each activity. **Predicted RED here** against the un-repriced toml — record the red; commit 3's config diff is what turns them green (see Verification points note above)
- [X] T029 [US1] Full sweep: old-conscription guards all red and repointed at the new behavior (rule 6); must-green pile re-read then re-run — co-sleep, grooming, play, durations, Article I–V property suites, determinism; `cargo test -p cloudkitty-core action events` then `cargo test --workspace` green **except** the T028 pile (documented)
- [X] T030 [US1] Commit 2: "spec 041: rest becomes co-sleep's sibling (drip 0.0 — legality/binding/events only)" — message lists the red-first evidence and names the intentionally-red T028 guards

**Checkpoint**: the sibling shape is complete and price-inert; every guard has been seen red.

---

## Phase 5: User Story 2 — Riders go partial (Priority: P2, **commit 3**)

**Goal**: the reprice as one pure config diff; standing cuddle demand
makes rest worth choosing.

**Independent Test**: quickstart §Commit 3 — `git diff HEAD~1` touches
only `cloudkitty.toml`; the T028 guards flip green.

- [X] T031 [US2] Reprice `cloudkitty.toml` (D6): `cosleep_drip_relief` 3.0 → 0.25, `cosleep_mutual_relief` 8.0 → 0.6, `groom_cuddle_relief` 8.0 → 0.5, `rest_drip_relief` 0.0 → 0.25; `rest_mutual_relief` stays 8.0. No play dial moves
- [X] T032 [US2] Fix the stale comments in the same diff (FR-008): the "mean cuddle need of 11.6" claim → measured 5.1 mean / 2.8 median; both cosleep tier comments rewritten from saturating-delivery to riders-partial; add the per-scene-not-per-pair note; carry the drip < mutual convention in the dial comments; leave the play ladder comment untouched
- [X] T033 [US2] Verify commit purity + the predicted flip: `git diff HEAD~1` shows only `cloudkitty.toml`; T028 guards now green (red → green across exactly this diff = their rule-5 cycle complete); `cargo test --workspace` fully green
- [X] T034 [US2] Commit 3: "spec 041: reprice — riders partial, rest stays the specialist (config only)"

**Checkpoint**: all three stories on the branch; suite fully green for the first time since T028 — by design.

---

## Phase 6: Polish & PR

- [X] T035 Re-read `redden-list.md` against the three commit messages: confirm every must-red entry actually went red in its commit, for the predicted reason (running is not reading — rule 6)
- [X] T036 End-to-end: boot a local server on a scripted-seat world; confirm the first rest scenes appear and `/events/activity` rows carry the counters per contracts/activity-event-tier.md §Shape (F-029 emit-proof in miniature: see a nonzero drip and a nonzero mutual)
- [X] T037 [P] Add the one-liner to `## Unreleased` in the changelog (house practice; no tag)
- [X] T038 [P] Confirm the 3.0-wall markers are in place: the `cuddle_relief` deletion marker (T010) and a bound-duet-tolerance deletion marker beside the FR-009 resume path in `action.rs` (D8 handoff to the config-hygiene sweep)
- [X] T039 Open the PR (base main, one PR, three commits): body = commit contract, SC-001 digest evidence, the T028 red→green note for reviewers, constitution gates; wait on CI green. **Merge is the owner's word**

---

## Dependencies & Execution Order

- **Phase 1 → 2 → 3 → 4 → 5 → 6 strictly sequential** — the commit
  contract is a dependency chain, not a priority order: US3 (split)
  blocks US1 (sibling), which blocks US2 (reprice).
- Within US3: T005/T006 (guards) before T007–T010 (implementation);
  T011–T014 verification before T015 commit.
- Within US1: T016 (predicate extraction) first and alone —
  behavior-preserving; guards (T017/T018, T022/T023) written red
  before their implementation tasks (T019–T021, T024–T026); T027–T029
  before T030 commit.
- Within US2: T031/T032 are one diff; T033 before T034.
- **Story independence caveat** (deviation from template): US1 and US2
  are *testable* independently (unit battery vs config arithmetic) but
  not *landable* independently — the owner ruled one PR, and P1
  without P2 delivers zero visible scenes (spec: "they ship together;
  P1 carries the engine risk").

### Parallel Opportunities

Limited — `action.rs` serializes most of the work. Genuinely parallel:

- T008 (defaults.rs comment) beside T007 (config/mod.rs)
- T024 (kitty.rs) beside T025 (events.rs)
- T037 beside T038 in polish

---

## Implementation Strategy

Single-lane, commit-by-commit; each checkpoint is a review point:

1. Phases 1–3 → **commit 1 verified alone** (byte-identity ×3). This
   is the only independently-landable increment; if anything halts the
   arc here, the split still stands as a pure win.
2. Phase 4 → commit 2 (verified with commit 3 as one step; T028
   documented red in between).
3. Phase 5 → commit 3 → full-green suite → Phase 6 → PR.

HALT conditions: T013 digest mismatch (commit 1 is not a no-op); any
must-red staying green vacuously (report per rule 3 if pre-existing);
T028 failing to flip on the config diff alone (the arithmetic guard is
reading the wrong end).
