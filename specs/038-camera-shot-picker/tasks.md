# Tasks: Camera shot picker

**Input**: Design documents from `/specs/038-camera-shot-picker/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md,
contracts/shot-grammar.md, quickstart.md

**Tests**: REQUIRED — Constitution Article VI and the shot-grammar contract
demand every rule land with a mutation-verified check in the existing
harness. House rules 5/6 apply to every task below: each new assertion is
introduced with its exact counter-bug, predicted red first, then green; the
sorted must-fail/must-pass piles from T002 govern the whole arc.

**Organization**: Nearly everything lives in two files (`client/anim.js`,
`client/test-motion.mjs`), so tasks are SEQUENTIAL unless marked [P]. Story
phases follow spec priority: US1 calm hold, US2 stage-always-kitties (both
P1), US3 finds-the-action, US4 following (both P2).

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

- [x] T001 Verify baseline: `node client/test-motion.mjs` and
      `node client/test-meadow.mjs` green on branch `038-camera-shot-picker`;
      record both check counts (the rule-6 must-pass pile baseline)
- [x] T002 Sort the changed behaviour's checks (house rule 6): inventory every
      camera assertion in `client/test-motion.mjs`, classify **must-go-red**
      (fit-everyone width, anchor hysteresis, continuous-ease expectations)
      vs **must-stay-green** (`limitsFor` bounds, camera-off identity,
      letterbox predicate, follow basics, FR-020 roster-drop); record the two
      lists in the T002 commit message — deletions/replacements happen in
      T021, not silently along the way

## Phase 2: Foundational (blocking all stories)

- [x] T003 Add the new dials to `VIEW.camera` in `client/anim.js` with
      documented defaults per research D13 (`linkTiles` 5, `nearDwellTicks`
      5, `farDwellTicks` 15, `safeZoneFrac` 0.80, `moveMs` 700, `panMs`
      1100, `fitMarginFrac` 0.195); removals wait for T021
- [x] T004 Implement grouping + fit in `client/anim.js`: connected
      components at `linkTiles` over drawn positions, and `widthNeeded =
      max(spanX, spanY/aspect) / (1 - 2·fitMarginFrac)`; checks in
      `client/test-motion.mjs` (component transitivity on crafted positions;
      desktop margin equivalence to the old `fitMarginTiles` within 0.1
      tile; mutations: break transitivity, drop the aspect division)
- [x] T005 Implement chain tracking + the evidence function in
      `client/anim.js` per research D5/D10: majority-overlap continuation,
      per-chain near/far consecutive-tick counters, thresholds compared only
      at the two decision sites; checks: contract §5 chain-churn fixture (a
      rival swapping one member mid-dwell keeps its counter; mutation:
      exact-set keying goes red)
- [x] T006 Replace camera-mode motion in `Camera.update` in `client/anim.js`
      with the episode engine (research D7): REST/EASING, latched goal,
      cubic ease-in-out over duration, EXACT snap on arrival, still-frame
      hold, reduced-motion instant arrival, camera-off arrive-cut preserved;
      checks: contract §5 snap-to-rest (N consecutive frames bit-identical
      `left/top/across`; mutation: keep exponential pursuit), still-frame
      no-progress, reduced-motion instant
- [x] T007 Split decide-on-ticks from move-on-frames in `client/anim.js`
      (research D2): `world.tick` edge detection in `update` — no previous
      tick COUNTS as an edge, so the very first update decides (SC-009) —
      decision steps run once per tick in contract §2 order, consuming the
      aspect/cssWidth of the frame they run in; check: dwell counters
      advance once per tick when the harness draws 8 frames per tick
      (mutation: decide per frame)
- [x] T008 Implement cold-start shot selection in `client/anim.js`: greedy
      maximal-count window of groups that fits, lowest-kitty-id tiebreak,
      incumbent-keeps-ties thereafter (research D6); first decided shot
      arrives unesased via the existing `across === 0` path (SC-009); checks:
      tie determinism under roster reorder (mutation: array-order tie)

**Checkpoint**: grammar skeleton decides and moves; stories build on it

## Phase 3: User Story 1 — A camera calm enough to leave open (P1) 🎯 MVP

**Goal**: literal stillness at rest; discrete eased corrections with a
visible reason; no easing tail.

**Independent Test**: synthetic drives in `client/test-motion.mjs`: a
milling-inside group leaves the camera bit-still indefinitely; a member
pressing the edge produces exactly one correction episode ending in rest.

- [x] T009 [US1] Hold + correction for fitting shots in `client/anim.js`:
      inner `safeZoneFrac` rect test on members' drawn positions; press →
      one `correction` episode latched to the re-centred bbox at current fit
      width (clamped); checks: milling fixture (bit-still), press fixture
      (exactly one episode; mutations: threshold sign flip, per-frame
      re-latch)
- [x] T010 [US1] Overflow centre-hold (FR-007a) in `client/anim.js`:
      overflow = unclamped `widthNeeded` > ceiling; trigger = bbox centre
      drift > `aimDeadzoneTiles`; member positions NEVER trigger in
      overflow; checks: contract §5 overflow fixture (members exit frame →
      still; centre drifts past deadzone → one correction; mutation: member
      trigger in overflow mode)
- [x] T011 [US1] Non-pan re-latch discipline in `client/anim.js` (research
      D9): a fresh trigger mid-episode re-latches the goal once (a counted
      event), never per frame; check: second press mid-correction moves the
      goal exactly once (mutation: continuous goal tracking)
- [x] T012 [US1] US1 acceptance sweep in `client/test-motion.mjs`: scripted
      drive (group walks a straight line across the map at cat speed)
      asserting rest on ≥60% of ticks — the harness PROXY for SC-001,
      whose authoritative measure is T025's live capture — and zero
      motion after each episode's arrival

**Checkpoint**: MVP — the calm hold is real and measured in the harness

## Phase 4: User Story 2 — The stage always has kitties on it (P1)

**Goal**: ≥2 framed whenever possible; breaks re-frame without a cut; empty
frames impossible outside a pan's middle.

**Independent Test**: scatter/dissolve fixtures — no state reachable where
the camera frames fewer than two while a pair could share the widest frame.

- [x] T013 [US2] Minimum-two + closest-pair fallback (FR-004) in
      `client/anim.js`: when no window of ≥2 fits, frame the closest pair at
      the ceiling and tolerate partial visibility; checks: all-scattered
      fixture (mutation: permit a singleton window), plus a 3-kitty
      roster variant where the biggest group is a pair — SC-010's
      tightest case in the harness
- [x] T014 [US2] Membership follow + shed (FR-008/FR-010) in
      `client/anim.js`: shot = union of chains holding shot members; when
      the union stops fitting, keep the maximal-count fitting subset
      (incumbency tiebreak) via one `shed` episode — this is also US3's
      tighten-after-dispersal; checks: drift-apart fixture (mutation: shed
      the larger half)
- [x] T015 [US2] Break rule (FR-011) in `client/anim.js`: group-mode shot
      <2 → re-pick via T008 selection through one eased `break` episode,
      never a cut; checks: contract §5 break fixture (continuity of
      `left/top/across` across the re-frame; mutation: teleport on break)

**Checkpoint**: both P1 stories complete and independently green

## Phase 5: User Story 3 — The camera finds the action (P2)

**Goal**: maximal-count interest; near rivals admitted by widening; far
rivals need strict superiority sustained 15 ticks and get one committed pan.

**Independent Test**: contract §5 near-widen / far-pan / mid-pan fixtures
fire on their exact ticks and profiles.

- [ ] T016 [US3] Admission (FR-009) in `client/anim.js`: disjoint chain
      admissible-near with `nearTicks ≥ nearDwellTicks` → one `widen`
      episode admitting it; checks: near-widen fixture fires on the 5th
      qualifying tick, not the 4th or 6th (mutations: off-by-one, `>` for
      `≥`)
- [ ] T017 [US3] Far pan (FR-012/FR-013) in `client/anim.js`: strictly
      bigger + not admissible + `farTicks ≥ farDwellTicks` → committed `pan`
      episode on the `panMs` profile; decision steps 2–6 suspended until
      arrival; equal counts never fire; checks: far-pan fixture (15th tick
      exact; equal-never with a same-size rival; mutation: `≥` on count),
      mid-pan commit fixture (destination dissolves; latched goal unchanged)
- [ ] T018 [US3] Recorded-sample parity in `client/test-motion.mjs`: embed a
      50-tick REAL excerpt of `client-measurements/camera-aim/sample.jsonl`
      (house rule 5: recorded payloads, not hand-written), drive the real
      `Camera` tick-by-tick, assert event counts within the reference
      model's bands (pan 0, widen ≤2 for the excerpt) and ≥2 framed on
      every tick

**Checkpoint**: full group-mode grammar live and measured

## Phase 6: User Story 4 — Following still works (P2)

**Goal**: 036 following intact; shot pinned to her group; solo follow frames
her alone; rivals never steal a follow.

**Independent Test**: existing 036 follow checks stay green; new fixtures
for pin, solo, and suppressed rivals pass.

- [ ] T019 [US4] Follow pin (FR-014, research D12) in `client/anim.js`:
      subject = followed kitty's chain (+ admissions per FR-008–FR-011);
      far-rival evidence not evaluated; solitary follow frames her alone at
      the floor (min-two exempt); checks: contract §5 solo-follow fixture,
      bigger-group-elsewhere fixture (mutation: evaluate far evidence while
      following)
- [ ] T020 [US4] Release re-entry + 036 regression in `client/anim.js` and
      `client/test-motion.mjs`: release → group grammar re-entered through
      one eased episode (no cut); re-run AND re-read the must-stay-green
      pile from T002 (follow click/release/persistence/FR-020) — reading is
      not running (house rule 6)

**Checkpoint**: all four stories complete

## Phase 7: Polish & Cross-Cutting

- [ ] T021 Delete the dead machinery from `client/anim.js`: `anchorFor`, the
      `hysteresis` dial, camera-mode `panRate`/`zoomRate` use,
      `fitMarginTiles`; resolve T002's must-go-red pile (each red check
      replaced by its 038 successor or deleted with a pointer to the
      successor in the diff); `grep` proves no surviving references
- [ ] T022 [P] Verify the zero-diff claim: `git diff main -- client/render.js`
      is empty; if the pan needed a render hint after all, flag it in the PR
      description as the plan's one permitted touch
- [ ] T023 Full-suite audit: both harnesses green; READ the final counts and
      compare against T001's baseline plus additions; confirm every contract
      §5 fixture has its recorded red (the mutation, the predicted failure,
      the observed failure) in its task's commit message
- [ ] T024 [P] Docs: one-liner under `## Unreleased` in `CHANGELOG.md`;
      update the camera-logic entry in `BACKLOG.md` (epsilon-snap item is
      subsumed by 038's episode engine); add a pointer to spec 038 in
      `client-measurements/camera-aim/README.md`
- [ ] T025 Acceptance measurement per quickstart §4: capture a local
      five-kitty session with `client-measurements/camera-aim/camera-sample.mjs`,
      replay through the harness event counters, and record rest %,
      events/min, pans/min, at-ceiling %, ≥2-framed %, median frame width
      (→ kitty-size ratio vs the pinned-wide camera, SC-004), mean framed
      and maximal-or-tied % (SC-005) against SC-001…SC-005 in
      `specs/038-camera-shot-picker/acceptance-2026-08-21.md`
- [ ] T026 Stand up the local five-kitty world (quickstart §3) for the
      owner's live judgement and the dial pass (SC-010; dials bake only on
      her paste, house method) — owner-gated, the arc's final gate

## Dependencies

```text
T001 → T002 → [T003 → T004 → T005 → T006 → T007 → T008]  (foundational, sequential)
Foundational → US1 (T009→T010→T011→T012)
US1 → US2 (T013→T014→T015)          # break rides selection + episodes
US2 → US3 (T016→T017→T018)          # admission/pan ride membership + evidence
US3 → US4 (T019→T020)               # follow pin suppresses the rival logic it needs built
US4 → Polish (T021→T023→T025→T026; T022, T024 parallel any time after T021)
```

Single-file reality: US2–US4 could interleave, but the order above keeps
every checkpoint independently green, which is worth more than parallelism
in one file.

## Parallel Example

```text
After T021: T022 (render.js verification) ∥ T024 (CHANGELOG/BACKLOG/README)
— different files, no shared state with T023's audit.
```

## Implementation Strategy

**MVP = Phases 1–3** (setup, foundation, US1): a camera that picks one shot
and holds it in literal stillness is already the complaint fixed — worth a
live look before the full grammar lands. Then US2 completes P1
(deliver both before any deploy); US3/US4 complete the grammar; polish
deletes the old model rather than leaving it dormant. Every checkpoint
leaves both harnesses green and the branch deployable `--client-only`.
