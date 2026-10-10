# Feature Specification: Empty-Bowl Early End (spec-006 amendment)

**Feature Branch**: `product/empty-bowl`

**Created**: 2026-10-10

**Status**: Draft

**Input**: The owner's kickoff in the Product session, 2026-10-10
("060 empty-bowl") — the third of the four Gen 2 build-phase specs
(prereg skeleton §10), after the schema wall (058) and the teacher
rework (059, merged #447).

**Ruling sources** (records beat this spec on any discrepancy):
`experiments/gen2-sitting-rulings-2026-10-08.md` S§6 ("Empty bowl end
early in" — classed as a spec-006 amendment, an engine scene rule
affecting EVERY cat, policy seats included, riding the generation
boundary); the BACKLOG shelf entry (owner ruling 2026-09-10 on
Experiments' read; tabled at the 048 merge, owner 2026-09-02: "scene
minimums exist to prevent frantic alternation, and locking a cat at an
EMPTY bowl serves neither"); spec 006 (the deliberate meal-end rule
this amends); prereg skeleton §10 (lands BEFORE corpus collection).

## Why now

Spec 006's meal-end rule ends an eating scene when its minimum is met
AND the bowl is empty or the belly full. The minimum exists to prevent
frantic alternation — a purpose only relief-in-progress can serve. A
cat held at a bowl with nothing left in it is spending welfare ticks
on neither relief nor steadiness, and in the Gen 2 corpus those held
ticks would be DEMONSTRATIONS: the teacher shown persisting at an
empty bowl, labeled as if that were the lesson. The window is small
(at most the eat minimum, ~2 ticks on the served config) but it rides
every meal that drains a bowl. It waited for Gen 2 deliberately
(doctrine rule 9: a scripted stream deciding differently in the same
state orphans the Gen 1 corpus and its declared rates; the Gen 1
policies were frozen against today's eating dynamics) — the mandatory
Gen 2 re-record absorbs the whole change in the one `[rng-sequence]`
boundary, alongside spec 059's.

## Clarifications

### Session 2026-10-10

- Q: An eating scene doesn't record which bowl it eats from — when a
  cat sits adjacent to TWO bowls and one empties, does the meal
  continue off the other stocked bowl, or end because "its" bowl
  emptied? (FR-001/FR-004) → A: The scene ends when NO adjacent
  stocked bowl remains — the meal's feeding condition (an adjacent
  stocked bowl exists, the engine's own meal predicate) fails; a
  second stocked bowl within reach keeps the meal alive. A meal has
  never been bound to a single bowl, and no bowl-identity state is
  introduced.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The bowl ends the meal when it empties (Priority: P1)

An eating scene left with no adjacent stocked bowl ends at that tick's
scene resolution — minimum met or not. The minimum-duration hold
remains for every scene still delivering relief (the spec-006 purpose,
untouched): need-at-zero before the minimum still "licks the bowl"
harmlessly to the minimum. The rule is the ENGINE's, at the scene-end
resolution where spec 006's ends already live — it binds every seat
(scripted, policy, plugin, future LLM) identically, and no advisor can
propose its way around or into it.

**Why this priority**: the whole amendment; everything else is
accounting.

**Independent Test**: in a deterministic run, no eating scene survives
a tick whose resolution finds no stocked bowl adjacent to the eater;
every other scene-end behavior is byte-identical to spec 006's.

**Acceptance Scenarios**:

1. **Given** a kitty mid-meal below the eat minimum, **When** the meal
   consumes the bowl's last serving, **Then** the scene ends at that
   tick's resolution and the kitty decides freely next tick — it is
   not held to the minimum.
2. **Given** a kitty mid-meal below the minimum at a bowl that still
   has servings, **When** its eat need reaches 0, **Then** the scene
   continues harmlessly to the minimum and ends there (spec 006
   scenario 2, unchanged — the steadiness purpose stands).
3. **Given** a kitty mid-meal past the minimum, **When** the bowl
   empties or the belly fills, **Then** the scene ends exactly as
   spec 006 already rules (unchanged behavior, kept green).
4. **Given** two kitties eating at the same bowl when it empties and
   neither has another stocked bowl within reach, **When** the tick
   resolves, **Then** BOTH scenes end — the rule reads the world, not
   the eater.
5. **Given** a kitty eating with TWO stocked bowls adjacent, **When**
   one of them empties, **Then** the scene continues — the feeding
   condition still holds (clarified 2026-10-10).

---

### User Story 2 - The change rides the generation boundary (Priority: P2)

The early end is a food-scene reprice and a scripted-stream change:
every deterministic stream pin that eats from a bowl moves. All of it
lands inside the one mandatory Gen 2 re-record, declared and counted —
never silently.

**Why this priority**: the accounting is what made the shelf ruling
safe; skipping it would be the frozen-models trap the shelf names.

**Independent Test**: the continuity fixtures and any stream pin that
diverges do so with the divergence declared, first-divergence ticks
recorded, and the CHANGELOG carrying `[rng-sequence]`; the Gen 1
served world (0.3.0 box) is untouched.

**Acceptance Scenarios**:

1. **Given** the re-based reference streams, **When** the early end
   lands, **Then** each re-record names this spec as its reason with
   the first divergence tick, in the same artifact style as 059's.
2. **Given** the shelved BACKLOG entry, **When** this spec merges,
   **Then** the entry comes out of BACKLOG.md at the merge (the
   branch-sweep hygiene rule).

---

### Edge Cases

- A bowl emptied by ANOTHER eater mid-tick: turn order decides who
  got the last serving; every eater left without an adjacent stocked
  bowl at resolution ends (scenario 4). No cat is charged a
  "refusal" — a scene end is not a refusal and touches no refusal
  machinery.
- The bowl ELEMENT disappearing entirely (despawn/expiry) is already
  spec-048's counterpart-gone pruning; this rule covers the bowl that
  still stands but holds nothing.
- Need reaching 0 AND bowl emptying on the same tick: one end, same
  tick, indistinguishable outcome — no double accounting.
- A one-tick meal (last serving consumed on the scene's first tick):
  the scene ends having delivered exactly that serving's relief; the
  minimum never engages.
- Solo rest/sleep/groom and partnered scenes: OUT — no other activity
  reads a consumable; their minimums are untouched.
- The window being ≤ the eat minimum (~2 ticks served) bounds the
  behavioral delta per meal; the shelf analysis (rows `absorbed=true`,
  never in R8's refusal tax) is re-confirmed at implementation.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: An eating scene MUST end at the scene-end resolution of
  any tick at which its feeding condition fails: no stocked bowl
  remains adjacent to the eater (clarified 2026-10-10 — a meal is not
  bound to one bowl; another stocked bowl within reach keeps it
  alive), regardless of the scene's minimum duration. One home: the
  same engine resolution step where spec 006's ends live — never a
  behavior-layer rule, so it binds every seat identically (S§6: an
  engine scene rule affecting every cat).
- **FR-002**: Every OTHER spec-006 end rule is unchanged and kept
  green: need-0-before-minimum continues to the minimum; minimum-met
  ends on need 0 or bowl empty exactly as today. The amendment
  removes one precondition from one clause; it adds no new end.
- **FR-003**: The early end is a scene END, not a refusal: no
  refusal-log row, no reason stamp, `last_action`/census semantics of
  scene ends unchanged. The freed kitty decides freely on the next
  tick through the normal machinery.
- **FR-004**: The rule reads WORLD state only at resolution — bowl
  servings and positions, never the eater's hidden state. It is
  evaluated per seat position (which bowls are within reach), so all
  eaters left without an adjacent stocked bowl end together; an eater
  that still has a second stocked bowl within reach continues.
- **FR-005**: The change rides the Gen 2 boundary: `[rng-sequence]`
  in CHANGELOG; every moved stream pin re-recorded with this spec
  named and first-divergence ticks captured (the 059 artifact
  pattern); the deployed 0.3.0 Gen 1 world untouched (cloudkitty.toml
  is the NEXT deploy; seats stay parked).
- **FR-006**: OUT of this spec: drinking (water has no servings; its
  end rules are untouched), counterpart-gone pruning (spec 048 owns
  the vanished bowl), any reward, observation, or teacher-ladder
  change (the 058 wall and the 059 teacher stand as merged), and any
  duration-config change ([actions.durations] values are untouched).
- **FR-007**: The shelved BACKLOG entry ("Spec-006 empty-bowl early
  end — SHELVED UNTIL GEN 2") comes out of BACKLOG.md at this spec's
  merge.

### Key Entities

- **The eating scene**: spec 006's minimum-held activity; gains one
  early end keyed to its consumable.
- **The bowl (chow element)**: the consumable whose emptiness now
  ends scenes it can no longer feed — unless another stocked bowl
  within the eater's reach still can.
- **The re-record artifact**: divergence declaration in the 059
  style — reasons named, first-divergence ticks on file.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a deterministic run across randomized worlds, ZERO
  eating-scene ticks occur with no stocked bowl adjacent to the
  eater: every such scene ends at the first resolution that finds
  the feeding condition failed.
- **SC-002**: Every non-bowl-empty scene-end behavior is
  byte-identical to the pre-amendment engine on the same seeds: a
  stream recorded with bowls that never empty mid-scene below the
  minimum shows zero divergence.
- **SC-003**: Welfare direction: on the reference config, ticks spent
  in zero-relief eating scenes drop to zero while total eat relief
  delivered is unchanged (the meals deliver the same servings, just
  without the empty tail).
- **SC-004**: The moved stream pins are re-recorded with the
  divergence declared (spec named, first-divergence tick), and the
  config sweeps stay green with zero config edits.

## Doctrine check (CLAUDE.md rule 8)

Checked against `experiments/DESIGN-DOCTRINE.md`, 2026-10-10:

- **Rule 2 (prices are physics)** moved FR-001/FR-003's placement:
  the early end is a world scene rule at the engine's resolution —
  pricing every seat identically, never an advisor preference and
  never a punishment surface (no refusal row).
- **Rule 9 (frozen models cannot answer a reprice)** moved the
  TIMING (the shelf's own ruling): the change waited for the
  generation boundary; it lands before collection, inside the
  mandatory re-record, with the Gen 1 seats parked.
- **Rule 5 (imitability)** was checked and moved nothing: the rule
  reads the bowl, which the observation's chow rows already show;
  no hidden state enters any decision, and the teacher is untouched.
- **Rules 1, 3, 4, 6, 7, 8, 10, 11, 12** were checked and moved
  nothing: no reward term, no observation change, no vocabulary,
  no gate semantics, no new tunables.

## Assumptions

- "Bowl" means the chow element's servings count — the only
  consumable a scene holds a cat at. Temporary water expires whole
  (element gone = spec 048's pruning), so drinking has no analogous
  state and stays out (FR-006).
- The end lands in the same resolution step as spec 006's existing
  ends (one home), so ordering questions (who ate the last serving)
  are settled by the existing turn order — no new ordering rule.
- The window analysis on the shelf (≤ eat minimum, ~2 ticks served;
  affected rows `absorbed=true`, outside R8's refusal tax) is
  re-verified at implementation, not re-derived here.
- Spec 061 (stuck detector) follows separately; both land before
  Experiments' corpus collection (skeleton §10).
