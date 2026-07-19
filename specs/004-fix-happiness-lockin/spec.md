# Feature Specification: Fix Low-Happiness Lock-In

**Feature Branch**: `004-fix-happiness-lockin`

**Created**: 2026-07-18

**Status**: Draft

**Input**: User description: "Fix low-happiness lock-in in kitty decision-making. Root-cause analysis (2026-07-18, against a live state file plus a 6,000-tick reproduction) found kitties stuck in low-happiness episodes of 200–500 ticks, all three cats touching the happiness floor of 5. The causal chain: (1) play relief throughput is too low for an isolated cat; (2) the hard safeguard lock starves all other needs, including bath and sleep which are satisfiable at zero distance; (3) at the 100-clamp, the fixed tie-break order becomes a starvation queue. Scope: proportional urgency instead of the hard lock; higher play throughput (opportunistic play, distance-based target choice across critters and friends, abandoning futile chases); solo play backstop; tie-break by longest-since-relief; per-kitty time-in-distress observability. All magnitudes configurable per Article VI. Engine tick order, determinism (Article V), and the safeguard spawner untouched."

## The Problem *(context)*

Watchers have seen kitties stuck looking miserable for minutes at a time. The
root-cause analysis (2026-07-18, from the live state file at tick 1465 plus a
6,000-tick reproduction) established the mechanism:

1. **Trigger — play relief is too hard to earn.** A kitty pursuing play always
   chases the nearest critter. Because critters always exist (config minimums),
   the play-with-a-friend fallback effectively never runs. Greebles outrun
   kitties and are uncatchable; bugs wander randomly and often expire
   mid-chase. An isolated kitty can go hundreds of ticks without one successful
   play (observed: 216 ticks), while the play need only rises.
2. **Amplifier — the hard safeguard lock.** Once any need passes the safeguard
   threshold, the kitty pursues *only* the single most-pressing need. When that
   need is play and play is unattainable, the kitty ignores relief it could
   take on the spot — grooming and napping cost zero travel — and every other
   need climbs too.
3. **Floor-pin — tie-break starvation.** Needs cap at 100. Ties at the cap are
   broken in a fixed order, so relief serializes into a queue: the last need in
   the order (bath) can never win a tie and pins at exactly 100. With three or
   four needs pinned, happiness falls to the floor.

Observed impact with default configuration: low-happiness episodes of 200–500
ticks (4–7 real minutes), every kitty touching the happiness floor of 5 within
a 6,000-tick window, and 14–22% of time spent below happiness 45.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A kitty tends its needs in proportion, never fixating (Priority: P1)

As a watcher, when a kitty has several urgent needs at once, I see it take the
relief that is actually within reach — grooming where it stands, napping where
it stands — rather than ignoring everything while it treks after one
unattainable goal. Urgent needs still matter more: a genuinely hungry kitty
still heads for chow rather than grooming endlessly.

**Why this priority**: This is the amplifier that turns a play drought into
system-wide misery. Removing the hard lock keeps happiness in a healthy band
even when one need is temporarily unattainable — it is the single change with
the largest welfare effect.

**Independent Test**: Place a kitty with two needs at maximum pressure — one
satisfiable at zero distance (bath), one whose nearest relief is far away
(play) — and observe that the zero-distance need receives relief within a few
ticks, while a need with nearby relief still wins when its pressure is
markedly higher.

**Acceptance Scenarios**:

1. **Given** a kitty with bath at 100 and play at 100 whose nearest play
   partner is many tiles away, **When** the kitty decides, **Then** it grooms
   itself within a small bounded number of ticks instead of chasing
   indefinitely.
2. **Given** a kitty with eat past the safeguard threshold and chow a few
   tiles away, **When** it also has moderate needs satisfiable at zero
   distance, **Then** it still goes to eat — urgency continues to dominate at
   comparable distances.
3. **Given** the previous stuck state file (tick 1465), **When** the world
   resumes under the new selection rules, **Then** the stuck kitty's sleep and
   bath needs fall from their pinned values without waiting for a successful
   play.

---

### User Story 2 - Play is actually attainable (Priority: P2)

As a watcher, I see kitties succeed at playing: they bat at a bug they happen
to pass, they choose the nearest fun — whether that is a critter or a friend —
and they give up on a chase that clearly is not working instead of pursuing a
greeble forever.

**Why this priority**: Play is the need that triggers lock-in because its
relief almost never lands for an isolated kitty. Making play attainable
removes the trigger; even with the P1 fix in place, unattainable play would
still drag happiness down by its weight share.

**Independent Test**: Run a long simulation and measure play-success
throughput per kitty; verify a kitty adjacent to a critter plays with it even
while pursuing another need, and that a chase which fails to close distance is
abandoned within the configured number of ticks.

**Acceptance Scenarios**:

1. **Given** a kitty walking toward water with play need above the
   opportunism threshold, **When** its path brings it adjacent to a bug,
   **Then** it plays with the bug before resuming its errand.
2. **Given** a kitty whose nearest critter is farther away than its nearest
   fellow kitty, **When** it pursues play, **Then** it heads for the closer
   target — the friend.
3. **Given** a kitty chasing a greeble that stays out of reach, **When** the
   chase has not closed distance within the configured give-up window,
   **Then** the kitty abandons that chase and does something else worthwhile.

---

### User Story 3 - Solo play backstop (Priority: P3)

As a watcher, a kitty with nobody to play with entertains itself — pouncing at
nothing, as cats do — earning a smaller amount of play relief, so that play
(like bath, sleep and cuddle) is always satisfiable in the limit.

**Why this priority**: This is the structural guarantee behind Article I's
design assumption that play never requires a scarce resource. P1 and P2 make
lock-in rare; this makes it impossible, because no need can then be
indefinitely unattainable.

**Independent Test**: Isolate a kitty far from all critters and other kitties
with play at maximum; verify it performs solo play and its play need falls,
at a slower rate than social play would provide.

**Acceptance Scenarios**:

1. **Given** a kitty with play past the safeguard threshold and no play
   partner within its configured reach, **When** it decides, **Then** it plays
   by itself and receives the configured solo relief.
2. **Given** a kitty with a playmate adjacent, **When** it pursues play,
   **Then** it prefers the social option — solo play happens only when
   company is out of reach.

---

### User Story 4 - Fair tie-breaking at the cap (Priority: P4)

As a watcher, when several needs are equally desperate, the kitty rotates its
attention by whichever has waited longest for relief, so no need is
permanently shadowed just because of where it sits in an internal ordering.

**Why this priority**: With P1–P3 in place, exact ties at the cap become rare;
this is insurance that the pathological starvation queue can never re-form.

**Independent Test**: Construct a state with two needs at identical maximum
pressure and equal travel cost; verify the one longer without relief is
chosen, and that repeated ties alternate rather than always picking the same
need.

**Acceptance Scenarios**:

1. **Given** bath and play both at 100 with equal travel cost, **When** bath
   has gone longer without relief, **Then** bath is chosen.
2. **Given** identical repeated tie situations across a run, **When** the same
   seed and configuration are used, **Then** the choices are identical run to
   run (determinism preserved).

---

### User Story 5 - Trouble is visible while it is happening (Priority: P5)

As a watcher, I can see when a kitty has been distressed about the same need
for a long time — through the API and as a gentle cue in the kitty's panel —
instead of discovering it later by scrolling the distress log.

**Why this priority**: The stuck state sat in plain sight for 216 ticks with
the data already recorded but not surfaced. Observability does not improve
welfare by itself, but it turns any future regression from "noticed by eye,
eventually" into "visible immediately."

**Independent Test**: Drive one need into sustained distress and verify the
API reports how long it has been unresolved, and the panel shows its
indicator once the configured patience threshold passes — without alarming
language or imagery (distress is a signal for watchers, never a punishment).

**Acceptance Scenarios**:

1. **Given** a kitty whose play need crossed the distress threshold 50 ticks
   ago and has not recovered, **When** a watcher queries the API, **Then**
   the kitty's data includes the need and its unresolved duration in ticks.
2. **Given** a distress older than the configured indicator threshold,
   **When** the panel renders, **Then** a gentle indicator appears on that
   kitty's card, and disappears once the need recovers.

---

### Edge Cases

- All six needs at 100 simultaneously (the observed full-collapse state): the
  selection rule must still relieve zero-distance needs promptly and recover
  the kitty rather than serializing relief through a fixed queue.
- A kitty boxed into a corner with every play target unreachable for a long
  time: solo play keeps play bounded; no infinite chase results.
- The chase target expires or is consumed mid-chase: the kitty re-targets or
  abandons cleanly; the give-up window must not carry over stale state to an
  unrelated new chase.
- Give-up memory and the world's determinism: any per-kitty pursuit memory
  must survive save/resume so a restarted world continues the same future.
- Opportunistic play must not preempt the emergency ladder: a kitty starving
  beside its chow eats first; batting at a passing bug yields to
  higher-urgency zero-distance relief.
- Solo play while a partner sleeps adjacent: the sleeping partner counts as
  reachable company (social play is still the preferred, higher-relief path).
- Multiple needs distressed at once: the panel indicator reflects the
  longest-running distress rather than stacking alarm on alarm.
- Pre-existing saved worlds (including the stuck state file) must load and
  benefit from the new rules without migration.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Built-in need selection MUST always weigh pressure against
  travel distance for every candidate need — the exclusive "pursue only the
  most pressing need" rule above the safeguard threshold is removed.
- **FR-002**: Pressure above the safeguard threshold MUST carry configurable
  extra weight (an urgency emphasis) so that urgent needs dominate needs of
  similar convenience, while zero-travel relief for a pinned need still
  outranks pursuit of a distant or unreachable one.
- **FR-003**: All constants used by need selection — including the
  convenience travel cost and the opportunism ("worth a detour") threshold
  currently hard-coded in the behaviors — MUST become configuration values
  validated at startup (Article VI).
- **FR-004**: A kitty adjacent to a critter or fellow kitty, with play need at
  or above the configurable opportunism threshold, MUST be able to play
  opportunistically regardless of which need it is otherwise pursuing, at the
  same priority as the existing opportunistic eat/drink/sunbeam-nap rules and
  ordered below them.
- **FR-005**: Play pursuit MUST select its target by travel distance across
  both critters and fellow kitties, rather than always preferring critters.
- **FR-006**: A kitty MUST abandon a chase that has not reduced its distance
  to the target within a configurable number of ticks, and MUST NOT
  immediately re-select the abandoned target while the configured exclusion
  applies. Any per-kitty pursuit memory this requires MUST persist across
  save/resume and MUST NOT break resumption of older saved worlds.
- **FR-007**: A kitty whose play need is at or above the safeguard threshold
  with no play partner (critter or kitty) within a configurable reach MUST be
  able to play by itself for a configurable relief amount smaller than social
  play relief, so social play remains preferred whenever available.
- **FR-008**: When candidate needs tie on selection score, the tie MUST be
  broken in favor of the need that has gone longest without relief, with a
  stable deterministic ordering beneath that; the fixed enum-order tie-break
  is removed.
- **FR-009**: The per-kitty API payload MUST report, for each need currently
  in distress, how many ticks that distress has gone unresolved.
- **FR-010**: The viewer panel MUST show a gentle, non-alarming indicator on
  a kitty's card when any distress has been unresolved longer than a
  configurable threshold, and remove it when the need recovers. The viewer
  remains a pure view (Article V): it renders served data and adds no
  simulation logic.
- **FR-011**: Every new tunable introduced by this feature (urgency emphasis,
  travel cost, opportunism threshold, chase give-up window and exclusion,
  solo-play reach and relief, indicator patience) MUST be configurable with
  startup validation errors that name the field, value and allowed range
  (no magic numbers, Article VI).
- **FR-012**: The changes MUST be confined to built-in behavior decision
  logic, need bookkeeping, API payload additions, and viewer rendering. The
  engine tick order, the safeguard spawner, and Article V determinism
  guarantees (same seed and configuration produce identical runs) MUST be
  unchanged, and the property-test suite MUST continue to pass.
- **FR-013**: Saved worlds from the current release MUST resume cleanly under
  the new release; new per-kitty fields MUST default sensibly when absent
  from older snapshots.
- **FR-014**: The playful behavior profile MUST adopt the same anti-lock-in
  selection when it "gets serious" about needs, while keeping its
  play-forward personality; both built-in profiles must be immune to the
  lock-in mechanism.

### Key Entities

- **Need-selection score**: The value a built-in behavior assigns each
  candidate need per tick — combining pressure, urgency emphasis above the
  safeguard threshold, and travel distance — replacing the two-mode
  (locked/convenient) selection.
- **Pursuit memory**: Small per-kitty record of the current chase target, its
  starting distance, ticks elapsed, and any exclusion after giving up; part
  of the kitty's persisted state.
- **Relief recency**: Per-kitty, per-need record of when relief last landed;
  input to tie-breaking.
- **Distress age**: For each need in distress, the number of ticks since it
  crossed the distress threshold without recovering; derived from existing
  distress bookkeeping and exposed per kitty via the API.

## Success Criteria *(mandatory)*

### Measurable Outcomes

Baseline (measured 2026-07-18, default configuration, ~6,000-tick run):
happiness episodes below 45 lasting 200–500 ticks; every kitty touching the
floor of 5; 14–22% of time below happiness 45; one need pinned at exactly 100
for 90+ ticks while zero-distance relief existed.

- **SC-001**: In a 20,000-tick run with default configuration, no kitty
  spends more than 100 consecutive ticks below happiness 45.
- **SC-002**: In the same run, no kitty touches the happiness floor, and each
  kitty's time below happiness 45 is at most 5% (baseline: 14–22%).
- **SC-003**: In the same run, no need remains within one point of its cap
  for more than 25 consecutive ticks while relief for it is available at zero
  travel distance. Zero-distance relief means: bath and sleep — always; play
  — always once solo play exists; cuddle — a fellow kitty is adjacent; eat or
  drink — a satisfying resource is adjacent.
- **SC-004**: In the same run, no distress goes unresolved longer than 150
  ticks (baseline: 216+), and mean happiness per kitty is at least 65.
- **SC-005**: Resuming the archived stuck state file (tick 1465) under the
  new rules, the affected kitty's happiness recovers above 60 within 300
  ticks without relying on a lucky nearby critter spawn.
- **SC-006**: Two runs from the same seed and configuration remain
  tick-for-tick identical over 5,000 ticks (determinism preserved).
- **SC-007**: A watcher can tell from a kitty's card that it has been
  struggling within one glance once the configured patience threshold
  passes — no log reading required.

## Assumptions

- Default values for the new tunables are proposed at planning time and
  validated by observation, following the established practice of tuning
  world generosity empirically; the specific defaults are not fixed by this
  spec, only their existence, configurability and validation.
- "Travel distance" continues to mean the world's existing adjacency
  distance measure (the one already used for movement and adjacency); this
  feature introduces no new geometry.
- Solo play is expressed through the existing play action vocabulary (a play
  action without a partner target) rather than a new action concept, keeping
  external-behavior compatibility; the exact wire representation is a
  planning decision.
- Distress age is derived from the existing edge-triggered distress
  bookkeeping (crossing and re-arm events already recorded); no new event
  stream is required.
- The safeguard spawner's guarantees (chow and water always spawn for needs
  past the safeguard threshold) are unchanged and remain the world's side of
  Article I; this feature fixes the kitty's side — actually taking the
  relief the world provides.
- Per-kitty need-rate overrides (e.g. a snacky kitty) interact with the new
  selection only through pressure values; no per-kitty selection overrides
  are in scope.
