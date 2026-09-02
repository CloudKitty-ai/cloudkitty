# Feature Specification: No Stale Re-Proposal (don't re-propose an ended scene)

**Feature Branch**: `048-no-stale-reproposal`

**Created**: 2026-09-02

**Status**: Draft

**Input**: Owner request (relayed 2026-09-02, her words): "Can we bake the don't repropose ended play in there too?" — a cat should stop proposing the continuation of a scene whose partner or plaything is already gone, instead of burning a turn on a proposal the world will refuse.

## Problem

A cat committed to an ongoing scene keeps proposing "carry on" while the scene's counterpart — the critter it was batting at, the friend it was grooming — has already left the picture the cat decides against. The engine then ends the dead scene and refuses the stale proposal, and the cat stands idle for a turn. Each such turn also stamps a refusal record that is not a real refusal, inflating the partnered/element refusal-tax instrument the experiment thread reads (measured: roughly half of the raw tax in the current reference runs is this artifact).

Measured on the four Addendum 2 reference runs (20,000-tick windows, probe 2026-09-02):

- Critter play: 554–788 stale continuations per run; **none** were ever accepted (the world's critters move only after every cat has acted, so a critter gone at decision time is still gone at apply time). Pure waste.
- Grooming: 54–100 per run; ~10% were "rescued" (the friend became available again in the same turn). The fix forgoes these few rescues; the fresh decision may still choose to resume grooming.
- Kitty-kitty duets: **zero** — a duet ends for both partners at once, so a half-ended duet never survives to the next decision. (The remaining partnered refusal rows are same-tick races, out of scope — see Edge Cases.)
- Drinking: **zero** — water is permanent in every served world.

## Clarifications

### Session 2026-09-02

- Q: Should the rule cover every scene shape the engine's dead-scene rule covers, or only play scenes? (FR-003) → A: Full coverage — every shape (critter play, duet play, grooming, drinking); one shared definition with the engine's rule.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The critter got away; do something real (Priority: P1)

A cat is mid-play with a critter. The critter scurries off (or expires). On its next turn the cat can already see the critter is out of reach — it should make a fresh decision that turn (chase something else, pursue another need, play solo), not propose batting at the empty spot, get refused, and idle.

**Why this priority**: This is the owner's request verbatim ("don't repropose ended play") and the measured bulk of the artifact — 554–788 wasted turns and spurious refusal records per 20k-tick run, with a proven 0% chance the stale proposal ever succeeds.

**Independent Test**: Stage a cat mid-play with a critter, move the critter out of reach, advance one turn: the cat takes a real action that turn and no refusal record is stamped for it.

**Acceptance Scenarios**:

1. **Given** a cat mid-play with an adjacent critter, **When** the critter is no longer adjacent at the cat's next decision, **Then** the cat's decision that turn is a fresh choice (not the play continuation) and no refusal record is stamped for it.
2. **Given** a cat mid-play with a critter that expired, **When** the cat next decides, **Then** same as above.
3. **Given** a cat mid-play with a critter still adjacent, **When** the cat next decides, **Then** it continues the scene exactly as today.

---

### User Story 2 - The groomed friend walked away (Priority: P2)

A cat is grooming a friend. The friend walks off (or gets busy). On its next turn the cat should make a fresh decision, not re-propose grooming a friend who is gone.

**Why this priority**: Same failure shape, smaller volume (54–100 per run). Includes an accepted trade-off: in ~10% of these moments the friend would have become available again within the same turn and the old proposal would have been "rescued"; the fresh decision is free to choose grooming again, so at worst the scene restarts rather than resumes.

**Independent Test**: Stage a grooming pair, move the target friend away, advance one turn: the groomer takes a real action that turn.

**Acceptance Scenarios**:

1. **Given** a cat grooming a friend, **When** the friend is no longer available at the cat's next decision, **Then** the cat's decision that turn is a fresh choice.
2. **Given** a cat grooming a friend who is still present and available, **When** the cat next decides, **Then** it continues grooming exactly as today.

---

### User Story 3 - The refusal instrument reads true (Priority: P3)

The experiment thread reads the refusal record stream as a welfare/pricing instrument (the partnered-refusal tax). Stale-continuation rows are not refusals of a live proposal — after this change the stream no longer contains them, so the instrument reads what it claims to measure.

**Why this priority**: Rides along automatically once US1/US2 hold; it is why the experiment thread asked for the fix to land before their next measurement batch.

**Independent Test**: Reference run before/after: the stale critter-play refusal rows (554–788 per 20k-tick window) drop to zero; refusal rows from genuinely refused fresh proposals remain.

**Acceptance Scenarios**:

1. **Given** the reference world and seed, **When** the run is repeated on the fixed build, **Then** zero refusal records arise from dead-scene continuations.

---

### Edge Cases

- **Same-tick race (out of scope, documented)**: a duet partner that interrupts the duet in its own turn *after* this cat already decided produces one refused continuation this change cannot see — the cat decided against a world where the duet was still live. Measured 2,600–3,400 such rows per reference run; they are the two-phase turn structure's inherent cost, remain in the refusal stream, and are explicitly not this feature's target.
- **Counterpart gone AND the scene's driving need just emptied**: the cat already stops continuing when the need empties; whichever rule fires first, the outcome is a fresh decision. No ordering requirement.
- **Rescue forgone (grooming)**: a friend gone at decision time but back at apply time no longer resumes the old scene. Accepted; the fresh decision may start a new grooming scene with the same friend.
- **Counterpart entirely absent from the world** (not just out of reach): treated as gone, same as the engine's own scene-ending rule.
- **A scene inside its minimum duration**: the engine ends a dead-counterpart scene regardless of minimum ("minimum notwithstanding"), so the fresh decision is never overridden back into the dead scene.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A cat MUST NOT propose the continuation of an ongoing scene when the world it is deciding against already shows the scene's counterpart gone; it makes a fresh decision that turn instead.
- **FR-002**: "Counterpart gone" MUST mean exactly what the engine's own dead-scene ending rule means, and there MUST be one shared definition — the decision-side check and the engine's scene-ending check can never drift apart.
- **FR-003**: The rule covers every scene shape the engine's dead-scene ending rule covers (critter play, kitty-kitty play, grooming, drinking) — owner-ruled 2026-09-02 (Clarifications). Scene shapes the engine never ends for a vanished counterpart (sleeping, resting, solo scenes) are untouched.
- **FR-004**: A scene whose counterpart is present and live MUST continue exactly as today — this feature changes no decision where the counterpart survives.
- **FR-005**: The change applies to every cat personality that continues scenes (it is shared good sense, not a personality trait). It is not scoped to any one behavior.
- **FR-006**: There is no configuration knob: the fix is unconditional, and the default configuration's serialized form MUST NOT change.
- **FR-007**: Refusal records MUST no longer be stamped for dead-scene continuations (the proposal is never made); genuine refusals — including same-tick races — MUST keep being stamped exactly as today.
- **FR-008**: The recorded world evolution (golden pin) is expected to move; the new pin MUST be justified by this feature's changelog entry and marker.

### Key Entities

- **Ongoing scene**: a cat's committed activity with a counterpart in the world — playing with a critter, playing with a fellow kitty, grooming a friend, drinking.
- **Counterpart**: the thing the scene is with: the critter (must be within reach), the duet partner (must still be in the duet), the groomed friend (must be available), the water (must be within reach).
- **Continuation proposal**: the "carry on" action a committed cat proposes each turn until its scene's driving need is satisfied.
- **Refusal record**: the engine's stamp of a non-idle proposal that validated to nothing; consumed as a measurement stream by the experiment thread.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On the reference runs (same worlds, same seeds), stale critter-play continuation refusals drop from 554–788 per 20k-tick window to **zero**.
- **SC-002**: Every turn that previously idled on a dead-scene continuation now performs a real action the same turn.
- **SC-003**: No scene with a live counterpart ends or changes because of this feature (US1/US2 scenario 3 / 2 class of checks, plus the full existing suite).
- **SC-004**: The default configuration's serialized form is byte-identical before and after (defaults stamp unmoved).
- **SC-005**: Same-tick race refusals remain in the refusal stream (measured 2,600–3,400 per reference run) — the fix removes only what it claims to.

## Assumptions

- **Scope — full coverage (owner-ruled, no longer a default)**: every scene shape the engine's dead-scene rule covers (FR-003). Rationale on record: one shared definition is the simplest correct shape, drinking is unreachable in practice (water is permanent), and grooming has the same failure at smaller volume.
- The same-tick race class is structurally out of reach of any decision-time rule and is not attempted.
- The experiment thread re-baselines its refusal-tax readings on the fixed build (their Addendum 3 plan already sequences this fix before their batch).
- No compensating "wait for the counterpart to come back" behavior is added — the fresh decision simply runs the cat's normal decision process.
