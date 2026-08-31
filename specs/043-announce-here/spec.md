# Feature Specification: The `announce_here` Knob

**Feature Branch**: `043-announce-here`

**Created**: 2026-08-30

**Status**: Draft

**Input**: Experiments → Product handoff `experiments/here-word-screen-handoff-2026-08-30.md` (owner ruled 2026-08-30: the here-word density screen's Half A runs now). Full screen design, arms, and pre-registered predictions: `experiments/here-word-density-screen.md`. The screen's gate zero is this change's acceptance test.

## Context

Scripted cats are structurally mute in the Here\* register. The shared scripted announce rule considers only the want-family words (say the highest-pressure need whose want-kind is legal), so even though the grounded legality predicates for the four Here\* words already exist and all four kinds are enabled on the served world, no scripted cat ever speaks one. The here-word density screen needs a scripted corpus that carries Here\* words at a controllable density; this feature is the screen's one hard engine dependency.

The change: allow the scripted announce rule's candidate set to include the four Here\* words — HereFood, HereWater, HereCritter, HereSunbeam — behind a new scripted-behavior configuration knob, off by default, with the strict property that turning the knob on changes only what cats **say**, never what they **do**.

## Clarifications

### Session 2026-08-30 (plan-phase reconciliation, Article VI)

- Q: The handoff pins selection as `(tick + cat identity) % n_legal` — but on a speaking tick `(tick + cat identity)` is by definition a multiple of the period, so the index only reaches multiples of gcd(period, n_legal); at period 4 with 2 or 4 legal words it is always 0 and only the first legal kind ever speaks, skewing the corpus's kind mix as a function of the density dial. → A: FR-006 amended to index by the speaking-tick counter — `((tick + cat identity) / period) % n_legal` — which cycles all candidates at every period, preserves statelessness/no-RNG/determinism, and reduces exactly to the handoff's formula at period 1. Deviation flagged to Experiments in the PR body and `research.md` D3.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Arm the knob, collect a here-word corpus (Priority: P1)

An experimenter sets the new density knob in a world configuration and runs scripted compositions. Cats now speak grounded here-words when the moment is lawful: the referent is adjacent, the word's cooldown has lapsed, the word is enabled in the vocabulary, no want-word claims the turn, and the cat's density phase says this is a speaking tick. The resulting corpus carries Here\* emissions at a share that moves with the knob's value.

**Why this priority**: This is the feature — the density screen cannot run until scripted cats can speak Here\* words at a dialable density.

**Independent Test**: Configure the knob at a small period on a world with adjacent referents, run the scripted simulation, and observe Here\* messages in the event stream; raise the period and observe the emission share fall.

**Acceptance Scenarios**:

1. **Given** the knob is set to period 1 and a scripted cat stands adjacent to food with no want-word armed and no here-word cooldown active, **When** the cat's turn resolves, **Then** the cat emits HereFood alongside its normal action.
2. **Given** the knob is set to period 1 but the cat's highest-pressure need makes a want-word legal this tick, **When** the cat's turn resolves, **Then** the want-word is spoken and no here-word is (existing speech wins — owner precedence rule, 2026-08-23).
3. **Given** the knob is set to period 1 but this tick is not the cat's speaking phase for that period, **When** the cat's turn resolves, **Then** no here-word is spoken.
4. **Given** the knob is set to period 1 and more than one here-word is legal on the same tick, **When** the cat speaks, **Then** exactly one here-word is chosen by the fixed deterministic rule, and re-running the same world with the same seed reproduces the identical choice.
5. **Given** a here-word kind is disabled in the world's vocabulary table, **When** the knob is armed, **Then** that kind is never spoken (the knob adds candidates; it never bypasses legality).

---

### User Story 2 - Byte-identical launch with the knob off (Priority: P1)

An operator upgrades the engine without touching any configuration. Every existing world loads and runs exactly as before: same actions, same messages, same serialized defaults.

**Why this priority**: The house launch pattern — an absent/zero knob must be provably inert so the merge carries zero re-baselining debt (scripted anchor, thermostat parity, character price, eval-suite baseline all stand).

**Independent Test**: Load existing configurations against the new build; verify the engine defaults stamp and the golden evolution pin are unmoved and the full existing suite stays green.

**Acceptance Scenarios**:

1. **Given** a configuration that does not mention the new knob, **When** the world runs on the new build, **Then** behavior is byte-identical to the pre-change build (actions and messages both).
2. **Given** the knob set explicitly to 0, **When** the world runs, **Then** behavior is identical to the knob being absent.
3. **Given** the new build's default configuration serialization, **When** its digest is computed, **Then** it equals the pre-change digest (the knob is absent at its default).

---

### User Story 3 - Gate zero: speech never moves action (Priority: P1)

An experimenter runs the same all-scripted world twice — knob off and knob on — and compares the two runs: the action streams are byte-identical; only the message streams differ.

**Why this priority**: This is the screen's gate zero and this change's acceptance test. If arming the knob moves actions, every action-anchored baseline re-bases and the screen is not worth it. The property must be enforced in-tree, not just observed once: no scripted decision rung listens for Here\* words today, but nothing currently prevents a future one — the paired check makes that regression loud.

**Independent Test**: A paired in-tree test runs a deterministic scripted world with the knob off and on, asserts the action streams' digests are equal, and asserts the on-run's message stream contains at least one Here\* emission (so the equality is never vacuous).

**Acceptance Scenarios**:

1. **Given** a deterministic all-scripted world, **When** it is run knob-off and knob-on from the same seed, **Then** the two action streams are byte-identical.
2. **Given** the same paired run, **When** the message streams are compared, **Then** they differ and the on-run contains Here\* emissions.
3. **Given** the same paired run, **When** want-word and WaitForMe emissions are compared, **Then** they are identical in both runs (here-speech never displaces or delays existing speech, and per-kind cooldowns keep it from shifting other words' legality).

---

### Edge Cases

- Multiple here-words legal on one speaking tick → exactly one is spoken, chosen by the fixed deterministic derivation over the legal set in a stable order; no randomness.
- A want-word and a here-word both legal → the want-word wins, and the here-word is not "queued" — it simply isn't spoken this tick.
- The cat's speaking phase lands on a tick where no here-word is legal → silent in the Here\* register; nothing carries over.
- A here-word's own cooldown is active → that word drops out of the legal set like any other cooldown; if that empties the set, the cat is silent in the register.
- Period 1 → every tick is a speaking phase for every cat; density is then bounded only by legality.
- A very large period → here-words become correspondingly rare; no special-casing, the same rule.
- Policy-driven (non-scripted) seats → entirely unaffected; the knob governs scripted announcing only. Policy legality for Here\* words is already true and unchanged.
- Saving and resuming a world mid-run → no new persistent state exists; the speaking phase derives from tick and cat identity, so a resumed run speaks exactly as the unbroken run would.
- Unknown or misspelled field name in the configuration → rejected at load, per the existing strict-field policy.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The scripted-behavior configuration MUST gain one new field: a here-word announce period. Absent or 0 means off. Off is the default.
- **FR-002**: With the knob off, the system MUST behave byte-identically to the pre-change build: identical action streams, identical message streams, identical default-configuration digest (the field is omitted from serialized defaults at its default value, per the house stamp discipline).
- **FR-003**: With the knob on (period ≥ 1), the shared scripted announce rule MUST be able to select among the four Here\* kinds — HereFood, HereWater, HereCritter, HereSunbeam — in addition to its existing want-family candidates.
- **FR-004**: Precedence MUST be: existing speech wins. A here-word is considered only when the announce rule would otherwise say nothing (no want-word is legal-and-selected this tick). Here-speech never displaces, delays, or reorders any existing emission.
- **FR-005**: A cat MUST consider here-speech only on its speaking-phase ticks: the tick count plus the cat's identity, taken modulo the period, equals zero. This staggers cats' phases and makes the period the density dial.
- **FR-006**: When more than one here-word is legal on a speaking tick, the choice MUST be the stateless deterministic derivation — the cat's speaking-tick counter (tick count plus cat identity, divided by the period), modulo the number of legal candidates, indexing a stable ordering of those candidates. The decision path MUST draw nothing from the world's random stream. *(Amended at plan time — see Clarifications: the handoff's literal formula aliases against the speaking-phase gate and would pin the choice to the first legal candidate whenever the candidate count divides the period.)*
- **FR-007**: The knob MUST add candidates only, never legality: every here-word spoken must pass the existing grounded legality check (referent adjacency, vocabulary enablement, per-kind cooldown) exactly as a policy-spoken here-word would. The knob MUST NOT touch the vocabulary table's semantics.
- **FR-008**: Both scripted behaviors MUST honor the one knob through the shared announce rule; no per-behavior variant.
- **FR-009**: Emitting a here-word MUST follow the existing emission path (cooldown stamped arithmetically, no randomness), and MUST introduce no new persistent state: a resumed run speaks identically to an unbroken one.
- **FR-010**: The gate-zero property MUST be enforced by an in-tree paired test: one deterministic all-scripted world run knob-off and knob-on, asserting (a) action streams byte-identical, (b) message streams differ with at least one Here\* emission in the on-run. This test is the standing guard against any future scripted rung listening for Here\* words.
- **FR-011**: The new field MUST participate in configuration validation consistent with its neighbors (strict unknown-field rejection already applies; the period is a non-negative whole number by type, so no additional range rule is required).

### Key Entities

- **Here-word announce period (the knob)**: one whole-number field on the scripted-behavior configuration. 0/absent = off (default); N ≥ 1 = each cat considers here-speech every Nth tick on its own phase. It is a density dial for the scripted corpus, not a legality switch.
- **Here\* words**: the four grounded reference kinds (HereFood, HereWater, HereCritter, HereSunbeam), already defined with adjacency-grounded legality and per-kind cooldowns; this feature changes who can originate them (scripted cats), nothing about what they mean.

### Out of Scope

- The density screen itself (arms, corpus collection, clone training, read-outs) — Experiments' lane, from the merge.
- Any listener: no scripted behavior may begin acting on heard Here\* words (FR-010's guard makes a future attempt loud).
- Changes to the vocabulary legality table, the message codec, word set, or observation schema.
- The free-register words (Chirp, Trill, Ekekek) and reserve kinds — untouched.
- Anything inside specs 041/042's surfaces or the fog wall.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: With the knob absent, the default-configuration digest is unchanged from the pre-change build and the entire existing test suite passes unmodified.
- **SC-002**: The paired gate-zero run yields byte-identical action streams and differing message streams, with Here\* emissions present in the on-run — verified by an in-tree test that fails if either half breaks.
- **SC-003**: On a world with adjacent referents, arming the knob at period 1 produces Here\* emissions in the event stream, and raising the period strictly lowers the realized here-word share across the screen's pre-registered ladder (1 → 4 → 16), measured over the same seed and duration.
- **SC-004**: Two runs of the same armed world from the same seed produce identical message streams (bitwise), demonstrating the no-randomness rule.
- **SC-005**: Every here-word in an armed run satisfies its grounding at emission time (referent adjacent) and respects its cooldown — no emission the legality check would refuse.
- **SC-006**: Want-word and WaitForMe emission streams are identical between the paired off/on runs (here-speech is purely additive to the message channel).

## Assumptions

- The owner's precedence rule (2026-08-23, "existing speech wins") is settled and not revisited here.
- The knob arms both scripted behaviors at once through the shared announce rule; per-behavior periods are not needed for the screen and are not provided.
- The speaking-phase derivation staggers by cat identity (matching the existing critter-movement idiom), so at a given period different cats speak on different ticks; the screen measures realized share rather than assuming a formula.
- The four Here\* kinds are already enabled in the served world's vocabulary; worlds that disable a kind simply never hear it from scripted cats either.
- Sequencing per the handoff: this merges before the waterline-contagion enablement and before the fog spec window; the screen runs wholly on this side of both.
- No deploy is required for the screen: Experiments runs it on lab worlds from the merged tree.
