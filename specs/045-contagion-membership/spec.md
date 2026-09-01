# Feature Specification: Contagion Membership Dial + Charge-Aware Ladder

**Feature Branch**: `045-contagion-membership`

**Created**: 2026-08-31

**Status**: Draft

**Input**: User description: "Two lab-facing engine dials for the step-2
water's-edge avoidance smoke (design: `experiments/edge-avoidance-smoke-design-2026-08-31.md`
@ 9d258b6, owner-approved; Experiments handoff 2026-08-31; follow-up to
spec 044, not a rider). (1) A `contagion_membership` setting — `option_a`
(default, the shipped rule) or `bidirectional` — branching only which dry
cats the spec-044 contagion charge admits: under bidirectional a dry
member of a cross-waterline scene pays from either role (naming the wet
partner OR being named by it), referenced cats included; the adjacency
gate, formula, ceiling gate, and wet-member exemption are unchanged.
Lab-use only: the served config never sets it before the owner's
membership ruling; bidirectional is pre-priced welfare-benign at both
economies (`cuddle-economy-model/RESULTS.md` §Bidirectional). (2) A
charge-aware option for the scripted chooser's ladder, config-gated and
default OFF: when on, a candidate scene's value weighs the expected
contagion exposure (charge × expected scene duration) against the
payer's bath, reusing the needflow value shape as the reference. Neither
dial changes served behavior at defaults — byte-identical launch."

## Clarifications

### Session 2026-08-31

- Q: When the charge-aware ladder prices a candidate scene, does it
  weigh only the charge the choosing cat itself would pay, or the
  scene's total contagion cost no matter which member pays it? → A:
  Scene-total — the chooser weighs every contagion charge the candidate
  scene would generate under the active membership rule, whichever
  member pays. (Egocentric pricing would make the smoke's bidirectional
  arm choose identically to the Option A arm by construction, voiding
  the D-vs-C contrast the membership ruling depends on.)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Bidirectional membership for the lab arms (Priority: P1)

Experiments runs the water's-edge avoidance smoke with five arms. Arms D
and E need a world where the contagion charge admits a dry cat from
either role in a cross-waterline scene — the cat whose activity names a
wet partner AND a dry cat merely referenced by a wet partner's activity.
Today only the naming side can pay (Option A, owner-ruled at 044
clarify). A config setting flips the membership rule for a lab world
without touching anything else about the charge.

**Why this priority**: This is the smaller dial and the one the smoke's
candidate rule (arm D) and positive control (arm E) both require; without
it the owner's pre-fog bidirectional call has no data.

**Independent Test**: A lab config with the setting at `bidirectional`
and factor > 0 charges a dry, currently-adjacent cat that a wet groomer's
activity references — a cat that pays nothing under `option_a` in the
same scene. Deliverable on its own even if the ladder option never ships.

**Acceptance Scenarios**:

1. **Given** a wet cat grooming a dry adjacent friend whose own activity
   does not name the groomer, **When** the membership setting is
   `bidirectional` with factor 1.0, **Then** the dry friend accrues the
   contagion charge that tick; under `option_a` in the identical scene it
   accrues ambient only.
2. **Given** the same scene, **When** the referenced dry cat is no longer
   adjacent to the wet groomer, **Then** it accrues ambient only under
   both settings (the adjacency gate is membership-independent).
3. **Given** a dry cat naming a wet adjacent partner, **When** the
   setting is `bidirectional`, **Then** its charge is identical to the
   `option_a` charge (the naming side's price does not move).
4. **Given** a wet cat in any scene, **When** the setting is
   `bidirectional`, **Then** it pays occupancy only, never contagion (the
   wet-member exemption is membership-independent).

---

### User Story 2 - A ladder that can feel the charge (Priority: P2)

Gen 1 clones imitate the scripted teacher. A charge-blind ladder never
avoids the water's edge, so no clone can learn avoidance under either
membership rule — the smoke's arms C, D, and E need a scripted chooser
whose scene valuation weighs what the contagion charge will cost the
payer over the scene's expected duration. A config option turns this
weighting on for lab worlds; off (the default), the chooser is exactly
today's.

**Why this priority**: The larger of the two dials and required for
three of five arms — but the membership dial is independently
deliverable and the ladder's value shape gets an Experiments review at
plan time, so it lands second.

**Independent Test**: With the option on and a cranked factor, a
scripted cat facing two otherwise-equivalent candidate scenes — one
incurring contagion exposure, one not — ranks the unexposed scene
higher; with the option off, the two rank as they do today.

**Acceptance Scenarios**:

1. **Given** the option off (or absent), **When** a scripted world runs,
   **Then** every choice is byte-identical to the current engine at the
   same seed.
2. **Given** the option on with factor 0.0, **Then** choices are
   byte-identical to the option being off (zero charge weighs zero).
3. **Given** the option on with a large factor, **When** a candidate
   scene would generate a contagion charge for any member under the
   active membership rule, **Then** that scene's value is reduced by the
   scene-total expected exposure and an otherwise-equal unexposed scene
   wins.
4. **Given** the option on with membership `bidirectional`, **When** a
   wet cat weighs grooming a dry adjacent friend, **Then** the friend's
   charge counts against the scene's value even though the chooser pays
   nothing itself (scene-total pricing; the ladder always prices the
   rule that is live).

---

### User Story 3 - The served world never notices (Priority: P1)

The operator deploys engines carrying these dials long before any ruling
uses them. With both dials at their defaults — membership absent
(`option_a`), ladder option absent (off) — the served world's behavior,
config fingerprint, and stamp are byte-identical to the pre-045 engine.

**Why this priority**: Same bar every recent arc has cleared; a moved
stamp or golden invalidates live baselines mid-soak.

**Independent Test**: Default-config stamp unchanged; the 10k-tick
evolution golden passes unregenerated; explicit-default configs parse
equal to absent.

**Acceptance Scenarios**:

1. **Given** the current default config, **When** the 045 engine
   serializes it, **Then** neither new key appears and the stamp hash is
   unchanged.
2. **Given** a config writing both defaults explicitly, **When** parsed,
   **Then** it equals the absent-key config and a seeded run is
   byte-identical.
3. **Given** the served TOML as deployed today, **When** validated by
   the 045 engine, **Then** it is accepted with no warnings.

---

### Edge Cases

- A dry cat referenced by TWO wet cats' activities under `bidirectional`
  (e.g. two wet groomers naming the same dry friend): it pays at most
  one contagion charge per tick — membership is a set, not a sum.
- `bidirectional` set while factor is 0.0: inert — membership selects
  payers for a charge that is zero.
- Both scene members dry, or both wet: no contagion under either setting
  (unchanged 044 law; wet pays occupancy only).
- The ladder option on in a config whose world has no water: values
  identical to off (no exposure exists to price).
- Ladder on for a scene whose expected duration is one tick (critter-play
  style early ends are priced via measured expectation, not the
  activity's max): exposure weight uses the expected duration, so short
  scenes are cheap, not free.
- Invalid membership value in TOML (anything but the two names): config
  rejected at load with a message naming the two legal values.
- The membership dial does not create scenes, end scenes, or alter
  legality/masks/refusal — a cat that would not pair still does not
  pair; only who pays an existing price changes.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST expose a water contagion membership
  setting with exactly two values — `option_a` and `bidirectional` —
  defaulting to `option_a` when absent, and the absent default MUST be
  behaviorally and byte-identical to the shipped 044 engine.
- **FR-002**: Under `bidirectional`, a dry cat MUST accrue the contagion
  charge when it is a member of a partnered scene with a wet, currently
  adjacent scene-mate in either role: its own activity names the wet
  cat, or the wet cat's activity names it. Referenced-only cats are
  included; all other 044 law (charge formula, pre-charge ceiling gate,
  wet-member exemption, current-adjacency requirement, the four paired
  kinds) applies unchanged.
- **FR-003**: A cat MUST accrue at most one contagion charge per tick
  regardless of how many wet scene-mates admit it to membership.
- **FR-004**: Under `option_a`, charge behavior MUST be identical to the
  shipped 044 engine (the setting's default is a rename of the status
  quo, not a reimplementation).
- **FR-005**: The engine MUST expose a scripted-chooser option, default
  off, that when on weighs a candidate scene's expected contagion
  exposure — the per-tick charge times the scene's expected duration —
  in the scene's value, using the needflow value shape as the reference
  model. When off or absent, scripted choice MUST be byte-identical to
  the current engine.
- **FR-006**: The priced exposure is scene-total under the active
  membership setting: the chooser weighs every contagion charge the
  candidate scene would generate — whichever member pays it — as
  determined by the same configuration that decides who pays at
  need-accrual time (clarified 2026-08-31).
- **FR-007**: Neither dial may alter action legality, masks, refusal
  behavior, scene formation or termination, RNG draw order at defaults,
  or any need dynamics other than who the existing contagion charge
  admits (membership) and how scripted candidates are valued when the
  ladder option is on.
- **FR-008**: Config validation MUST reject an unrecognized membership
  value with a message naming both legal values, and MUST apply the
  existing contagion budget law unchanged (bidirectional does not raise
  the per-cat per-tick maximum, so the 044 headroom budget stands).
- **FR-009**: When contagion is armed at boot, the engine's boot log
  MUST state the active membership rule alongside the existing
  contagion line, so the on-box evidence at any future flip names both
  dials.
- **FR-010**: The served deployment config MUST NOT set either dial as
  part of this feature; both are lab-use until the owner's membership
  ruling. Nothing in this feature commits the served anchors to a
  charge-aware ladder.

### Key Entities

- **Membership setting**: which dry scene-members the contagion charge
  admits — the naming side only (`option_a`, default) or either side
  (`bidirectional`). Selects payers; never sizes the charge.
- **Expected contagion exposure**: the scene-total of per-tick
  contagion charge × expected scene duration, summed over every member
  who would pay under the active membership rule; the quantity the
  charge-aware ladder weighs against a candidate scene's value.
- **Charge-aware ladder option**: the on/off gate for exposure pricing
  in the scripted chooser; off is the served and default state.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Default-config stamp (`engine_defaults_sha256`) is
  unchanged and the 10k-tick evolution golden passes unregenerated;
  explicit-default configs parse equal to absent and run byte-identical
  at the same seed.
- **SC-002**: In each of the four paired kinds, a differential test
  shows the referenced dry adjacent cat charged under `bidirectional`
  and uncharged under `option_a`, while the naming side's charge is
  equal under both settings.
- **SC-003**: A multi-payer scene (two wet cats referencing one dry cat)
  moves the dry cat's bath by exactly ambient + one charge per tick.
- **SC-004**: With the ladder option on and an otherwise-equal pair of
  candidate scenes, the exposed scene ranks strictly lower at a cranked
  factor and ranks equal at factor 0.0; with the option off, a seeded
  scripted run is byte-identical to the pre-045 engine.
- **SC-005**: Both config sweeps pass with zero edits to existing
  configs, and the served TOML validates unchanged.
- **SC-006**: Two same-seed runs with any combination of the new dials
  produce identical worlds (no new nondeterminism).

## Assumptions

- The smoke design doc (`experiments/edge-avoidance-smoke-design-2026-08-31.md`
  @ 9d258b6) and the Experiments handoff define scope: engine dials
  only. The smoke itself (arms, collection, bars) is Experiments' lane;
  the instrument `--base` flag is Experiments' trivial tweak; neither is
  in this spec.
- "Either role" under bidirectional reads both cats' own activities —
  the same `Activity`-naming source 044 uses — with the 044
  current-adjacency requirement applied to the wet/dry pair being
  priced. No new state, timer, or RNG.
- Expected scene duration for the ladder follows the house practice of
  measured expectation (the critter-play `mlen` precedent), with the
  exact shape settled at plan time under Experiments' review of the
  needflow-derived value model (`cuddle-economy-model/RESULTS.md`).
- The ladder prices only candidates who are wet at decision time; it
  neither charges for nor discounts mid-scene waterline crossings (a
  dry partner stepping in, a wet partner stepping out). Consequence for
  the smoke, per Experiments' review 2026-08-31: the lab arms can
  express avoidance of wet partners, not anticipatory avoidance of
  water's-edge loiterers — the water-adjacent-share readout is expected
  to move less than cross-waterline adjacency, and a flat
  water-adjacent share is not evidence the charge produces no edge
  behavior. (Experiments mirrors this in the smoke design doc.)
- Bidirectional is pre-priced welfare-benign at both live economies
  (canonical 0.5 and serving 2.0 groom relief) — the budget law needs
  restating in docs only if the plan finds the per-tick maximum moved,
  which FR-008 asserts it does not.
- The 044 precedent governs delivery discipline: red-first evidence for
  every new assertion, stamp/golden proof, both sweeps, no auto-merge,
  CI watched explicitly.
- The boxed-cat jump-over backlog (94e5c97) is unrelated and stays out.
