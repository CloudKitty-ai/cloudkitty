# Feature Specification: Waterline Contagion (price, not law)

**Feature Branch**: `044-waterline-contagion`

**Created**: 2026-08-31

**Status**: Draft

**Input**: User description: "Waterline contagion (owner-ruled 2026-08-30, factor 1.0 for Gen 1; engine half only). A dry cat in a partnered scene (any of the four paired activity kinds) with an in-water partner receives the wet-fur charge as if in water, behind one new config factor inert at 0.0. No wet timer; dry member only; prices not prohibitions. The water-headroom validation budget must be re-stated with contagion in it. Acceptance per `experiments/waterline-contagion-handoff-2026-08-30.md`."

## Clarifications

### Session 2026-08-31

- Q: When only one side of a paired scene names the partner in its own activity — a groomer grooming an idle cat — should the referenced cat (the idle groomee) also pay the contagion charge when its groomer is standing in water? → A: No — own-activity only (Option A). A cat pays only when *its own* activity names an in-water partner; a merely-referenced cat pays nothing. Social play is reciprocal by construction, so both members pay there either way; rest, co-sleep, and groom charge the naming side only. This also makes stacking impossible (one partner per activity → at most one contagion charge per cat per tick), keeping the per-tick worst case and the validation budget exactly as FR-009 states them.
- Q (post-implementation review amendment, owner-ruled 2026-08-31): a cat's activity can name a partner one tick stale — a free rest companion or groomee who moves onto water after the namer's slot, before the namer's next prune. Does the stale naming still charge? → A: No — the charge additionally requires the named partner to be **currently adjacent** at needs time (the engine's one shared adjacency predicate). A scene the tick has already dissolved never draws a trailing charge. This only narrows exposure, so the FR-009 budget and per-tick worst case are untouched.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Inert launch (Priority: P1)

The operator merges and deploys this change with the contagion factor unset (or explicitly 0.0). Every world — served, lab, replayed — behaves exactly as it did before the merge: same decisions, same needs, same persisted artifacts, byte for byte. The flip to a nonzero factor is a deliberate, separate config change at its own later deploy.

**Why this priority**: The house launch pattern. The merge must be safe alongside anything (the 041 soak, the here-word density screen's collection) precisely because it changes nothing until the factor is flipped. If inertness fails, nothing else about the feature may ship.

**Independent Test**: Run a fixed-seed world for N ticks on the pre-merge build and the post-merge build with the factor unset; compare the full serialized world stream byte for byte.

**Acceptance Scenarios**:

1. **Given** a config that never mentions the contagion factor, **When** a world runs any number of ticks, **Then** its serialized state stream is byte-identical to the same seed and tick count on the pre-merge engine.
2. **Given** a config that sets the factor explicitly to 0.0, **When** the same world runs, **Then** the stream is byte-identical to the factor-unset run.
3. **Given** a default config written back to disk, **When** the factor holds its inert value, **Then** the factor does not appear in the serialized output (identity values stay out of the default serialization, per the standing stamp guard).

---

### User Story 2 - The dry partner pays the wet-fur price (Priority: P2)

With the factor set above zero, a dry cat sharing a partnered scene with a partner who is standing in water accrues the wet-fur charge as if it were in the water itself: the charge scales by the configured factor, the world's wet-fur gain, and the cat's own trait-scaled bath sensitivity. The cat already in the water keeps paying exactly the occupancy charge it always paid — never contagion on top.

**Why this priority**: This is the mechanism the owner ruled IN for Gen 1. It prices closeness to a wet friend without prohibiting anything: no activity becomes illegal, no refusal is added, the social fabric is untouched — the bath need simply rises, and grooming absorbs the charge (priced welfare-benign up to factor 1.0).

**Independent Test**: Construct scenes of each of the four paired activity kinds with one member on a water tile and one on land, tick once, and read both members' bath need against hand-computed expectations.

**Acceptance Scenarios**:

1. **Given** a dry cat resting with a friend who is on a water tile, **When** a tick elapses, **Then** the dry cat's bath need rises by the ambient rate plus factor × wet-fur gain × its own bath ratio.
2. **Given** the same arrangement in each of the other three paired kinds (co-sleeping, social play with a kitty, grooming a kitty), **When** a tick elapses, **Then** the dry member accrues the same contagion charge.
3. **Given** the wet member of any such scene, **When** the tick elapses, **Then** it pays exactly the occupancy charge (its own ratio-scaled wet-fur gain) and no contagion — no cat ever pays both charges in one tick.
4. **Given** a dry cat whose bath need already sits at or above the wet-fur ceiling, **When** its partner is in water, **Then** no contagion charge lands (the same pre-charge ceiling gate as occupancy).
5. **Given** a partnered scene with both members on land, or both members in water, **When** a tick elapses, **Then** no contagion charge lands on either member.
6. **Given** a cat playing with a critter (not a kitty) while a nearby unrelated cat swims, **When** a tick elapses, **Then** no contagion lands — only a partnered scene with an in-water *partner* prices.

---

### User Story 3 - The headroom budget still cannot be broken (Priority: P3)

The configuration validator's water-headroom rule — the guarantee that no amount of voluntary swimming can ever cause a safeguard or distress event, enforced by rejecting any config whose ceiling plus worst single charge reaches the safeguard threshold — is re-stated to include contagion in the budget. A config that could produce a contagion charge breaking that guarantee is unrepresentable, not merely untested.

**Why this priority**: Certification hygiene. The dry-member-only rule keeps the per-tick worst case unchanged at factor ≤ 1.0, so the served config and both config sweeps are expected to pass unchanged — but the budget's statement must now cover the new charge, and a factor above 1.0 must widen the budget accordingly.

**Independent Test**: Feed the validator configs at the budget boundary with the factor at 0.0, 1.0, and above 1.0; confirm acceptance and rejection flip exactly where the widened budget says they must.

**Acceptance Scenarios**:

1. **Given** a config whose ceiling plus the largest single wet-fur charge (occupancy or contagion, whichever is larger) stays strictly below the safeguard threshold, **When** it is validated, **Then** it passes.
2. **Given** a config where a factor above 1.0 pushes the largest contagion charge to or past that boundary, **When** it is validated, **Then** it is rejected with an error naming the offending keys and the remedy.
3. **Given** the served world config and both config sweep suites, **When** validation runs with the re-stated budget, **Then** all pass unchanged.
4. **Given** a config with a nonsensical factor (negative, non-finite), **When** it is validated, **Then** it is rejected.

---

### Edge Cases

- A partnered scene is read from a cat's **own current activity**: the dry cat pays only when its own activity names an in-water partner **who is currently adjacent** (amended by owner ruling 2026-08-31, see Clarifications). A cat merely referenced by someone else's activity (e.g. the recipient of grooming who is itself idle) is not in a scene of its own and pays nothing, and a named partner who has already wandered out of adjacency draws no trailing charge. (See Assumptions.)
- A cat's activity names at most one partner, so at most one contagion charge can land per cat per tick; there is no stacking from multiple wet neighbours.
- The ceiling gates on the **pre-charge** value, so a cat just under the ceiling can overshoot by at most one scaled charge — identical to the occupancy behavior the headroom budget already covers.
- Contagion draws no randomness and fires in the same need-advance phase as occupancy: enabling it must not perturb any random stream, and disabling it must restore byte-identical behavior.
- Leaving the water ends wetness instantly (no wet timer, owner-ruled): a partner who steps off the water tile stops transmitting contagion on the very next tick.
- Water tiles may expire mid-scene; contagion follows the partner's actual standing-on-water state each tick, not any remembered state.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose one new numeric contagion factor in the water configuration section, defaulting to 0.0, with 0.0 (or absence) producing behavior and persisted artifacts byte-identical to the pre-feature engine.
- **FR-002**: The inert default MUST stay out of the default serialization (identity-skip), preserving the standing config-stamp guarantee.
- **FR-003**: When the factor is above 0.0, a cat whose current activity is one of the four paired kinds (resting with a friend, co-sleeping with a friend, social play with a kitty, grooming a kitty) and whose named partner currently stands on a water tile **and is currently adjacent to the cat** (owner ruling 2026-08-31, see Clarifications), and who is not itself on a water tile, MUST accrue a bath charge of factor × wet-fur gain × its own trait-scaled bath ratio that tick.
- **FR-004**: The contagion charge MUST gate on the same wet-fur ceiling as the occupancy charge, evaluated on the pre-charge value.
- **FR-005**: A cat standing on a water tile MUST pay only the occupancy charge — never the contagion charge in the same tick — so the per-tick worst case for any cat at factor ≤ 1.0 is unchanged.
- **FR-006**: The feature MUST NOT introduce any persistent wetness state: whether a partner is "wet" is exactly whether it stands on a water tile this tick.
- **FR-007**: The feature MUST NOT change action legality, the legal-action mask, or the refusal seam in any way; it prices needs only.
- **FR-008**: The contagion path MUST draw no randomness, keeping worlds deterministic and replayable with the factor at any value.
- **FR-009**: The water-headroom validation MUST re-state its budget to cover contagion: the ceiling plus the largest single charge any rostered cat can receive — occupancy or contagion, whichever is larger (i.e. scaled by max(1, factor)) — must stay strictly below the safeguard threshold, with violations rejected at validation time.
- **FR-010**: The validator MUST reject non-finite or negative factor values with an actionable error.
- **FR-011**: The served world config and both existing config sweep suites MUST pass the re-stated validation without modification.

### Key Entities

- **Contagion factor**: one dial in the water configuration; 0.0 = feature off (launch state), 1.0 = the Gen 1 ruling; scales the contagion charge only, never occupancy.
- **Partnered scene**: the state of a cat whose own current activity names a kitty partner — one of four kinds: resting with a friend, co-sleeping with a friend, social play with a kitty partner, grooming a kitty.
- **Wet-fur charge**: the existing per-tick bath price of water; occupancy (standing on water) and contagion (partnered with a cat standing on water) are its two sources, mutually exclusive per cat per tick.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: With the factor unset or 0.0, a fixed-seed world's serialized stream over at least 1,000 ticks is byte-identical to the pre-merge engine's, and the default-config stamp is unchanged.
- **SC-002**: With the factor above 0.0, a dry cat in each of the four paired kinds with an in-water partner accrues exactly the expected charge (verified to numeric tolerance against the hand-computed value), and accrues nothing when the gate or exemptions apply.
- **SC-003**: In every armed scenario, no cat's single-tick bath rise ever exceeds the occupancy worst case while the factor is at most 1.0.
- **SC-004**: A config whose widened budget (ceiling + max(1, factor) × largest ratio-scaled gain) reaches the safeguard threshold is rejected by validation — the broken guarantee is unrepresentable.
- **SC-005**: The full existing test suite passes with zero modified assertions, and armed runs replay deterministically (two same-seed runs produce identical streams).
- **SC-006**: The served config and both config sweeps validate green with no config edits.

## Assumptions

- **Scene membership is read from a cat's own activity** — owner-confirmed 2026-08-31 (see Clarifications). Asymmetric references (a groomed cat that is itself idle) do not create a scene for the referenced cat; the charge always follows the paying cat's own choice of scene.
- The KITTY_SLOT neighbour-in-water observation float is **out of scope** — it stays gated on the fog schema wall. This feature is the engine half only; learnability arrives with the wall.
- The flip to factor 1.0 is **not** part of this delivery: it is a config-only change at its own deploy with its own soak, after the 041 deploy + soak completes and the here-word density screen finishes collection. This spec ships the mechanism inert.
- Pricing evidence is taken as given from the needflow work (welfare-benign at every factor up to 1.0; grooming absorbs the charge); no new pricing study rides this spec.
- The existing per-cat bath-ratio scaling and ceiling semantics are reused exactly as the occupancy charge defines them; this spec introduces no new scaling concepts.
