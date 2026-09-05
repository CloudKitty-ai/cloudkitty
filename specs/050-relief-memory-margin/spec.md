# Feature Specification: Relief Memory Margin (the fog want law's memory reach)

**Feature Branch**: `050-relief-memory-margin`

**Created**: 2026-09-04

**Status**: Draft

**Input**: Owner ruling (2026-09-04, relayed from the Experiments session; the invocation of `/speckit-specify` here is her go): a fog want-law knob `[meow] relief_memory_margin`, so `want_drink` stops being structurally silent. Legality only, no observation-layout change. The numbers are FINDINGS F-040 (main @ 9e0ab5e).

## Problem

Under the fog want law (spec 049 FR-036) a want-word is legal only for the cat's top need with **no known relief**, and known relief for eat, drink and play reads "the element visible OR its tile remembered". Memory is one slot per element kind, refreshed on sight, refuted only on sight, and never expiring at the served `memory_timeout_ticks = 0`. Water pools are permanent: they never move, empty or despawn. So the first sight of any pool silences `want_drink` for the rest of the run — the cat "knows relief" that may be twenty tiles away behind the fog. Chow escapes the same fate only because an emptied bowl despawns and refutes the memory.

Measured on the Experiments anchor (F-040): 3,000 ticks at r = 5, zero `want_drink` calls, zero `here_water` replies, nineteen observation columns constant. The scripted teacher corpus carries no drink want, and the step-5 learners cannot learn a reply to a word that is never said.

The owner's rule: a remembered element counts as known relief only when its remembered tile lies **within `[vision] radius + margin` Manhattan tiles** of the cat. Visible relief counts as it does today. At margin 0, Manhattan ≤ r implies the tile is inside the Euclidean disc, so memory never silences a want and the law reads "visible relief only" — radius-invariant. A margin of 1 or 2 lets memory bite in the ring just outside the disc. Key absent keeps today's unbounded rule, so nothing moves until a config sets it.

## Clarifications

### Session 2026-09-05

- Q: Where do the staged tests place the "remembered at Manhattan r + 1" tile, given a diagonal tile at that Manhattan distance can sit inside the Euclidean disc? → A: Option A with B's check — axis-aligned at (x + r + 1, y) or (x, y + r + 1), and the test asserts the tile is outside the disc anyway (protects the fixture if it is later moved). The same fixture is the inclusive-bound case: not known at margin 0 (want legal), known at margin 1 (want silent); that pair is the red-first guard that the bound is inclusive and Manhattan.
- Q: Under which config is the SC-004 / US1 "here_water replies > 0" count taken, given the served toml leaves `reply_intensity_floor` unset? → A: Option A — the `want_drink` count runs on the served toml verbatim; the reply count sets a floor in the test only, any value > 0 (0.30 is provisional and not a contract of this spec); served stays unset.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A thirsty cat out of sight of water may ask (Priority: P1)

A cat whose top need is drink and who remembers a pool it cannot currently see says `want_drink` when that pool lies beyond its memory reach; a friend who can see water answers `here_water`.

**Why this priority**: the whole point — the drink channel of the meow law is dead on the served world, and the step-5 corpus is collected from these seats.

**Independent Test**: stage a thirsty cat (drink armed and top) with a water tile remembered at Manhattan `r + 1`, axis-aligned (`(x + r + 1, y)` or `(x, y + r + 1)`) so it lies outside the Euclidean disc, and no water in view; the test asserts the tile is outside the disc. At margin 0 the want is legal; at margin 1 it is silent; with the key absent it is silent. The margin-0 / margin-1 pair on this one fixture is the guard that the bound is inclusive and Manhattan.

**Acceptance Scenarios**:

1. **Given** margin 0, drink armed and top, no water in view, a pool remembered at Manhattan `r + 1`, **When** legality is read, **Then** `want_drink` is legal.
2. **Given** the same cat at margin 1, **When** legality is read, **Then** `want_drink` is silent (the remembered tile is within reach).
3. **Given** the same cat with the key absent, **When** legality is read, **Then** `want_drink` is silent (today's rule).
4. **Given** margin 0 and a pool IN VIEW, **When** legality is read, **Then** `want_drink` is silent at every margin (visible relief is unchanged).
5. **Given** margin 0 on the served roster, **When** 20,000 ticks (the house stream horizon) run all-scripted at r = 5 on the served config verbatim, **Then** `want_drink` is said more than zero times (the number is recorded, not gated). *Implement-time correction (2026-09-05, redden-list §U2)*: the draft said 1,000 ticks on F-040's anchor rate (~12 per 1,000), but the served config — floor unset, `announce_here` 0, the served seed — reads ~1.2 per 1,000 with its first call at tick 1,610, so 1,000 ticks read 0 and 5,000 read 3; the horizon is 20,000 so the guard measures the mechanism, not the seed.
6. **Given** the same run with a reply floor set in the test only (any value > 0; the served config keeps the floor unset and the number is not a contract of this spec), **When** 20,000 ticks run, **Then** `here_water` replies appear — the claim is "the reply path fires on a `want_drink`", not "at a particular floor".

---

### User Story 2 - Nothing moves until a config asks for it (Priority: P2)

A config without the key behaves exactly as today, so every existing want-law guard, golden and stream pin keeps its meaning, and the served config's change is one key.

**Why this priority**: the house discipline — a knob's absence must be the unchanged engine, and the served diff must be legible.

**Independent Test**: the existing want-law tests run with the key absent and are untouched; the served `cloudkitty.toml` diff against main is exactly `relief_memory_margin = 0` under `[meow]`.

**Acceptance Scenarios**:

1. **Given** the key absent, **When** the existing want-law, meow-law-fog and mask-oracle guards run, **Then** none is edited and all stay green.
2. **Given** the served `cloudkitty.toml`, **When** it is diffed against main, **Then** the only changes are the one key set to 0, its comment block, and the head-comment phrase.
3. **Given** the 2.x replay era (`LawEra::PreFog`), **When** the margin is set, **Then** nothing changes (the 2.x law has no relief clause).

---

### User Story 3 - One rule for every remembered relief (Priority: P3)

Eat (remembered chow), drink (remembered water) and play (remembered bug or greeble) read the same reach; cuddle, bath and sleep are untouched.

**Why this priority**: one rule, not per-kind — the owner's words; and eat is where the second-order effect lands (F-040: +10–13 eat calls per 1,000 ticks at margin 0).

**Independent Test**: the same staged distance test as US1 for a hungry cat with a bowl remembered at `r + 1` and a playful cat with a bug remembered at `r + 1`; a cuddly cat's legality does not read the margin at all.

**Acceptance Scenarios**:

1. **Given** margin 0 and a bowl remembered at `r + 1` (none in view), **When** legality is read, **Then** `want_eat` is legal; at margin 1 silent.
2. **Given** margin 0 and a bug remembered at `r + 1` (no critter and no idle friend in view), **When** legality is read, **Then** `want_play` is legal; at margin 1 silent.
3. **Given** any margin, **When** `want_cuddle` / `want_bath` / `want_sleep` legality is read, **Then** the margin plays no part.

---

### Edge Cases

- **Exactly at the bound**: a remembered tile at Manhattan `r + margin` counts as within reach (inclusive), one tile farther does not. The staged fixture is the axis-aligned tile at `r + 1`: outside the disc, not known at margin 0, known at margin 1.
- **Staging geometry**: a diagonal tile at Manhattan `r + 1` can lie inside the Euclidean disc (e.g. `(3, 3)` at r = 5) and so be in view; every "remembered, none in view" stage uses an axis-aligned tile and asserts it is outside the disc.
- **Standing on the remembered tile** (distance 0): within reach at every margin; but the tile is in view, so the visible clause decides — the memory clause is never the deciding arm inside the disc at margin ≥ 0.
- **Refuted memory**: a remembered tile that came into view empty is already cleared by the engine (spec 049 R3); no clause reads it.
- **Very large margin** (≥ width + height): equivalent to the key absent; not refused.
- **Negative margin**: refused at config validation (a non-negative integer).
- **Memory timeout set** (`memory_timeout_ticks > 0`): the two rules compose — a slot that expired is not relief; a live slot is relief iff within reach.
- **Navigation is not the law**: `priced_nearest_element` keeps reading the remembered tile as a walking target whatever the margin; a cat may walk to a pool it also asks about.
- **Mid-tick enforcement**: the margin is read off the cat's own position at enforcement (after its move this tick), the same seam as every other clause (spec 049 review 2 finding 3); a step that brings the remembered tile within reach silences the word that tick.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A new optional config key `[meow] relief_memory_margin`, a non-negative integer. Absent = today's unbounded memory rule. Validation refuses a negative value; there is no upper bound.
- **FR-002**: With the key set, a REMEMBERED element counts as known relief for a want-word iff the Manhattan distance from the cat's current position to the remembered tile is ≤ `[vision] radius + relief_memory_margin`.
- **FR-003**: Visible relief is unchanged: an element (stocked bowl, water, critter) inside the disc silences its want exactly as today, at every margin.
- **FR-004**: The rule applies to every want with a memory clause — eat (chow), drink (water), play (bug, greeble) — and to nothing else. Cuddle, bath and sleep read no memory and are untouched. One rule, not per kind.
- **FR-005**: Navigation and targeting are untouched: the built-in element scan (visible ∪ remembered) and the exploration ladder read memory as before.
- **FR-006**: The mask probe and the enforcement seam read ONE predicate, as today; the verdict stays recomputable from the observer's own knowledge (its position, its memory dx/dy, the radius and the margin) — the prereg's A14 property.
- **FR-007**: The served `cloudkitty.toml` sets `relief_memory_margin = 0` with a comment block (what it does, why 0, that key-absent is the old rule, and that the step-5 prereg screens 0 and 1). The served-config diff is exactly that one key, its comment block, and the one-phrase amendment to the `[meow]` head comment. The compiled default leaves the key absent.
- **FR-008**: The test-side `LawEra::PreFog` replay (spec 049 FR-024a) is unaffected: the 2.x law has no relief clause and reads no margin.
- **FR-009**: Records: the meow-law contract's known-relief table gains the reach; the config-3.0 migration note and the served comment block name the key; CHANGELOG Unreleased carries a one-liner; the defaults-stamp guard, goldens and stream pins that the served key moves are re-pinned once from one run with the justification in each file's doctrine comment; the served and compiled welfare readings are re-taken and recorded (readings, not gates — owner ruling 2026-09-04).

### Key Entities

- **Relief memory margin**: the integer reach beyond the vision radius within which a remembered tile still counts as known relief; absent = unbounded.
- **Remembered tile**: the per-kind memory slot (spec 049 FR-006): position and last-seen tick; refreshed on sight, refuted on sight, expiring only under a positive timeout.
- **Known relief**: the want law's clause 4 (spec 049 FR-036): what silences a want-word; visible relief ∨ (remembered relief within reach).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A thirsty cat with water remembered at an axis-aligned tile at Manhattan `r + 1` (asserted outside the disc) and none in view may say `want_drink` at margin 0, may not at margin 1, and may not with the key absent — asserted by a guard seen red on the unchanged engine at the margin-0 arm.
- **SC-002**: A cat with water in view may not say `want_drink` at any margin (0, 1, 8, absent).
- **SC-003**: With the key absent every existing want-law, meow-law-fog and mask-oracle guard is untouched and green.
- **SC-004**: On the served roster at r = 5, margin 0, all-scripted, 20,000 ticks: `want_drink` calls > 0 on the served config verbatim; `here_water` replies > 0 with a reply floor > 0 set in the test only (the served `reply_intensity_floor` stays unset; the floor's value is not encoded as a contract). Readings recorded beside the pin, not gated: served verbatim 23 drink calls per 20,000 (~1.2 per 1,000; 0 under the old rule at every horizon); F-040's ~12 per 1,000 is the ANCHOR config's rate (floor 0.30, `announce_here` 1), not the served one.
- **SC-005**: The served `cloudkitty.toml` diff against main is exactly the one key, its comment block, and the one-phrase amendment to the `[meow]` head comment ("nothing remembered within reach"); the defaults stamp is unmoved (the key is absent from the default serialization, asserted by the stamp guard).
- **SC-006**: The same reach test (same axis-aligned `r + 1` fixture, margin 0 legal / margin 1 silent) holds for eat (remembered chow) and play (remembered critter); cuddle/bath/sleep legality does not read the margin.
- **SC-007**: Served welfare readings at r = 5 and r = 64 re-taken after the served key lands; numbers recorded in the welfare gate's comment (0 / 0 today).

## Assumptions

- Manhattan distance, inclusive bound, matching the owner's words, F-040's read and the blind-price doctrine (spec 049 T090: Manhattan is the lower bound on the walk). Manhattan ≤ r implies inside the Euclidean disc, which is what makes margin 0 "visible relief only".
- The compiled `Config::default()` leaves the key absent, so the compiled-world goldens keyed on defaults do not move; the served toml sets 0, so the served-roster stream pins (SC-011's r = 5 streams, SC-004b's named-cause run) and the served welfare readings move and are re-pinned / re-read once.
- The Experiments `anchor.toml` is Experiments' file; they set `relief_memory_margin = 0` there and re-smoke (schema_check A1/A9, the relief sweep) after the merge; the want_drink group leaves their `declared_constant.json`; the PREREG config rule gains the key.
- The served `cloudkitty.toml` keeps `reply_intensity_floor` unset (its 0.30 is provisional, owner-pinned at declaration on the Experiments anchor). The SC-004 reply count therefore sets a floor in the test only, any value > 0, so the declaration-time pin never ripples into this spec's guards.
- F-041 (the strict answers-me bit hiding same-tick re-call replies) is a separate finding and out of scope here.
- No observation-layout change: schema 5 stays 408 floats; no wire, artifact or exam width moves.
