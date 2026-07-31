# Feature Specification: Deliberate Purring & the Quiet Motor

**Feature Branch**: `022-deliberate-purr`

**Created**: 2026-07-31

**Status**: Draft

**Input**: User description: "Purr semantics for the post-soak engine batch
(issues #79 + #82, owner-approved direction 2026-07-31): reinstate deliberate
purring as a turn-consuming choice that starts a *real* purr — menu row 38,
shape A, no codec bump, cooldown-free, earned-gated — while the spontaneous
purr motor keeps purring exactly as visibly but stops broadcasting (announce
probability knob, default silent; silent starts stop stamping the Purr message
cooldown). Coupled retune, owner-decided: duration draw 8–13, `cooldown_ticks`
retired for `cooldown_factor = 2.5`. Hard constraint: no new MessageKind, no
observation or action-codec schema change — shipped artifacts must keep
loading. Doctrine amendments this spec must own: spec 011's 'purring is never
an action' and the MVP-era 'Meow is always legal' mask rule."

> Numbering note: this spec is 022 because 021 was consumed by the withdrawn
> cuddle-relief spec (tag `parked/021-withdrawn`); the number is not reused so
> historical references (FINDINGS, docs/cuddle-relief-semantics.md) stay
> unambiguous.

## The world before and after

Today a kitty has two purr surfaces that collide. The engine's spontaneous
motor (spec 011) starts a rumble whenever a kitty is content and off cooldown,
announcing each start with a `Purr` meow and stamping the shared 15-tick Purr
message cooldown. Separately, action-menu row 38 (`Meow(Purr)`) lets a kitty
*say* purr — but the cat doesn't actually purr, and because the motor fires in
the same happy moments and stamps the same cooldown, two-thirds of deliberate
purr-meows are silently swallowed (34.3% audible, measured:
`experiments/exp-001-bc-mappo/results/s6-promotion-2026-07-30.md`). Meanwhile
motor announcements outnumber deliberate ones ~36:1 (≈4,900 vs ≈137 per 200k
ticks), so the Purr digest channel is a near-constant hum carrying information
(nearby happiness) that is already directly observable in kitty slots.

After this change the two surfaces have distinct, coherent meanings:

- **Choosing to purr works.** Row 38 becomes the deliberate purr: a
  turn-consuming action that starts a *real* purr phase — the same phenomenon
  as the motor's rumble, initiated by choice — and always announces.
- **The motor purrs as much as ever, silently.** Spontaneous purr starts
  announce only with a configured probability (default: never). The meadow
  stays exactly as cozy; the broadcast channel changes meaning from "someone
  nearby is happy" to "someone *chose to tell you* they're happy."
- **The rhythm is retuned.** Purr durations draw 8–13 ticks (consistent 6–10
  second episodes; no blips, no drones) and the motor's rest becomes a
  freshly drawn multiple of the finished purr (factor drawn uniformly from
  1.75–2.75 at each purr end), making a happy kitty's purr duty cycle a
  constant ≈30.8% — set by the mean draw, regardless of the duration
  bounds — while no two rests repeat mechanically. The motor is the ambient
  floor; anything above it is a cat choosing to purr.

Stated for the record (owner-endorsed, issue #82): information that was
ambient becomes something cats must choose to share — a deliberate shift in
the world's character.

## Clarifications

### Session 2026-07-31

- Q: When a pre-022 snapshot is restored mid-purr (no stored duration), what
  deterministic rule stamps the proportional cooldown at purr end? → A:
  Treat the unknown duration as the configured minimum (`min_ticks`).
- Q: SC-004's "converges" needed a testable bound — what tolerance and
  horizon? → A: Within ±2 percentage points of 1/(1+`cooldown_factor`) over
  a run of at least 20,000 ticks.
- Q: Widen the healthy-vs-regression gap while we're here? → A: Yes —
  `cooldown_factor` default retuned 2.5 → 2.25 (owner, this session;
  supersedes issue #82's tuning comment). Duty target becomes ≈30.8%, and
  the separation from the flat-cooldown regression (≈25.9%) grows from
  2.7pp to 4.8pp, giving the ±2pp band real headroom.
- Q: Make the rest less regular, so the rhythm feels organic — draw the
  factor per purr instead of fixing it? → A: Yes (owner): at each purr end
  the factor is drawn uniformly from `[cooldown_factor_min,
  cooldown_factor_max]`, defaults 1.75–2.75. Long-run occupancy depends
  only on the *mean* draw (ratio of expectations over many cycles), and the
  midpoint is 2.25 — so the ≈30.8% target and the ±2pp/20k band stand
  (noise grows ~0.1–0.2pp, ceiling skew ≈0.45pp; the flat-cooldown
  regression still fails by ~4.5pp). Midpoint sets the ambient floor,
  spread sets the irregularity; equal bounds recover a fixed factor.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A kitty that chooses to purr really purrs (Priority: P1)

A policy kitty (or any advisor) that spends its turn on the purr action gets a
working, audible purr: the cat starts rumbling for a normally-drawn duration,
the meadow hears exactly one purr announcement, and nothing silently swallows
it. The motivating cat is real: arm2-g0p998-s6 already spends 0.101% of its
decisions on deliberate purr-meows, semantically correctly (mean happiness
93.8 at purr ticks), and today loses 66% of them to cooldown self-collision.

**Why this priority**: This is the batch's reason to exist — an action a
shipped policy already tries to use, retroactively gaining the behavior it
reads as intending. It is also the RL-legibility fix: a swallowable action is
one whose outcome a policy cannot predict, so it would be learned as
unreliable and abandoned.

**Independent Test**: Drive a content kitty to propose the purr action;
observe a purr phase begin with a duration inside the configured bounds,
exactly one Purr announcement at its start, and the whole turn consumed.
Repeat under an active motor cooldown and observe the purr still starts.

**Acceptance Scenarios**:

1. **Given** a kitty that is earned (happiness above the purr threshold, or
   happiness that just rose) and not currently purring, **When** it takes the
   purr action, **Then** it spends its entire turn, a purr phase starts with a
   duration drawn from the configured bounds, and exactly one Purr
   announcement is recorded — audible, never swallowed.
2. **Given** the same kitty but with the motor's purr cooldown still active,
   **When** it takes the purr action, **Then** the purr starts anyway — choice
   beats reflex; the deliberate purr ignores the motor cooldown.
3. **Given** a kitty that is already purring (either origin), **When** it
   takes the purr action, **Then** the turn is consumed and nothing else
   happens: no state change, no second announcement, no duration draw — a
   silent no-op.
4. **Given** a kitty that is not earned, **When** an external advisor proposes
   the purr action, **Then** the proposal is illegal and resolves to the idle
   no-op (Article IV); a policy kitty never proposes it because its legal-
   action mask excludes the purr row while unearned.
5. **Given** any purr in the world, of either origin, **When** it is running,
   **Then** it certifies a happy cat: both origins are gated by the same
   earned rule.

---

### User Story 2 - The meadow stays cozy while the channel goes quiet (Priority: P2)

A viewer watching the meadow sees kitties purring exactly as often as before —
same starts, same durations, same rumble — but the purr *broadcast* channel
falls nearly silent: spontaneous purr starts no longer announce (by default),
so nearly every Purr message any kitty hears is one a cat chose to send.

**Why this priority**: This is what makes US1's channel worth using. The
digest-zeroing probe (`results/meow-listening-2026-07-31.md`, PR #81) showed
policies act on what they hear; a channel that is 97% reflex hum drowns the
3% of intentional signal. Silencing the motor also removes the cooldown
self-collision, which is what lifts deliberate audibility from 34% to 100%.

**Independent Test**: Run a healthy world under default configuration for many
ticks; count purr phases (unchanged cadence) and Purr announcements (none from
the motor). Set the announce probability to 1 and observe every motor start
announcing, exactly one announcement per purr.

**Acceptance Scenarios**:

1. **Given** the default configuration (announce probability 0), **When** a
   spontaneous purr starts, **Then** the kitty starts rumbling normally but no
   Purr announcement is recorded and the Purr message cooldown is **not**
   stamped.
2. **Given** an announce probability strictly between 0 and 1, **When**
   spontaneous purrs start, **Then** each start independently announces with
   that probability; announcing starts are recorded, silent starts are not.
3. **Given** any announce probability, **When** a spontaneous purr starts,
   **Then** exactly one announce decision is drawn from the seeded RNG —
   configuration can change the outcome, never the draw count.
4. **Given** a viewer-facing surface (API state, client), **When** the motor
   purrs silently, **Then** the kitty still reads as purring for the whole
   phase — the announcement changed, the phenomenon did not.
5. **Given** a deliberate purr start, **When** it announces (it always does),
   **Then** the announcement is a state announcement: recorded directly and
   never swallowed by any message cooldown. (Purr-start stamping is retired
   altogether by companion spec 023 — see FR-008.)

---

### User Story 3 - The purr rhythm reads as intentional texture (Priority: P3)

An owner tuning the world gets purr dials whose meanings are clean: the
duration draw (8–13 ticks) sets the *texture* of episodes, and the cooldown
factor draw (1.75–2.75 per purr end) sets the rhythm — its midpoint fixes
the happy-kitty duty cycle at a constant 1/(1+2.25) ≈ 30.8% independent of
every other dial, while its spread keeps the rests from ever turning
metronomic (cycle length 22–49 ticks). Every happy cat rumbles just under a
third of the time, no two of them in step. The retired flat `cooldown_ticks`
knob is rejected loudly, never silently ignored.

**Why this priority**: Owner-decided tuning that gives the ambient world a
guaranteed floor while making everything above the floor attributable to
choice. It depends on US2 (see coupling requirement FR-013) and is meaningless
without US1.

**Independent Test**: Over long runs on a healthy world, per-kitty purring
occupancy lands within 2 percentage points of ≈30.8% over ≥20,000 ticks
under multiple duration-draw and factor-bound configurations sharing the
2.25 midpoint; every drawn duration lies in 8–13; a config file naming
`cooldown_ticks` is rejected at load with an error naming the factor-bounds
pair.

**Acceptance Scenarios**:

1. **Given** a purr that just finished (either origin), **When** the motor
   cooldown is stamped, **Then** it equals the ceiling of that end's freshly
   drawn factor × that purr's actual duration — always within
   ⌈`cooldown_factor_min` × d⌉ and ⌈`cooldown_factor_max` × d⌉, and
   reproduced exactly by the same seed.
2. **Given** a healthy kitty that re-earns immediately, **When** many
   purr/rest cycles pass, **Then** its purring share lands within SC-004's
   band around 1/(1 + the mean of the factor bounds), regardless of the
   duration bounds and of the factor spread.
3. **Given** a config file that still sets `[purr] cooldown_ticks`, **When**
   the world loads it, **Then** loading fails with a clear error naming the
   retired knob and its replacement — never a silent ignore.
4. **Given** default configuration, **When** durations are drawn, **Then**
   every purr (either origin) lasts between 8 and 13 ticks inclusive.

---

### Edge Cases

- **Deliberate purr while already purring**: silent no-op — turn consumed, no
  draw, no announcement, no state change (US1 scenario 3). This also covers
  "double purr" attempts: there is no way to extend or stack a purr.
- **Deliberate purr by an unearned kitty**: excluded by the legal-action mask
  for policy kitties; an external advisor's proposal resolves to idle per
  Article IV. The mask can never become all-zero from this: the idle row is
  always legal, and this change only ever *removes* legality from one row.
- **Legacy `Action::Purr` wire proposals** (pre-011 vocabulary, distinct from
  the meow-purr row): unchanged — still refused by validation and resolved to
  idle. Reinstating that action is shape B, explicitly rejected (issue #79).
- **Save/restore mid-purr**: the proportional cooldown needs the finished
  purr's duration at end-time, so the purr phase's identity (enough to derive
  its duration) must survive a snapshot. A snapshot taken mid-purr and
  restored must stamp the same cooldown the uninterrupted run would have. Old
  snapshots (pre-022, no stored duration) restore under the fixed convention
  of FR-012: the purr is treated as having the configured minimum duration.
- **Cooldown arithmetic lands on a fraction**: a drawn factor × duration is
  almost never integral (e.g., 2.3 × 9 = 20.7); the tick value is the
  ceiling —
  deterministic, and rest is never shortened by rounding.
- **Degenerate or invalid factor bounds**: validation requires
  0 < `cooldown_factor_min` ≤ `cooldown_factor_max`; equal bounds are legal
  and recover a fixed factor. The pre-022 "0 = back-to-back rumbles"
  capability is deliberately retired: back-to-back purring remains
  expressible, but only as a choice — the deliberate purr ignores the
  cooldown entirely.
- **Two kitties purr the same tick**: independent, as today; draws follow the
  pinned order (FR-011).
- **Announce probability at the boundaries** (exactly 0 or 1): the announce
  decision is still drawn once per spontaneous start, so moving a world
  between silent and always-announce never changes the draw shape.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The purr entry of the action menu (the meow-purr row, index 38)
  MUST become the deliberate purr: a turn-consuming action that, when applied
  by an eligible kitty, starts a purr phase identical in kind to a spontaneous
  one — same duration bounds, same served purring state, same viewer
  appearance — plus exactly one start announcement.
- **FR-002**: The deliberate purr MUST always spend the kitty's entire turn,
  including the no-op cases. "Purr constantly" is never free: a kitty spamming
  the purr action forfeits everything else it could have done, and its
  audibility saturates a clamped digest input rather than compounding.
- **FR-003**: Eligibility MUST be the earned rule, verbatim and unchanged
  from the motor: happiness above the purr threshold, or happiness that just
  rose. The rule gates both origins so every purr in the world certifies a
  happy cat. (The broader earned-rule rethink flagged in
  `experiments/exp-002-design-inputs.md` §2 is deliberately out of scope: the
  owner's duty-cycle tuning relies on the instant re-earn the current rule
  provides — see Assumptions.)
- **FR-004**: For policy kitties the earned rule MUST be reflected in the
  legal-action mask for the purr row — a mask *semantics* change with no
  shape, width, or index change. For external advisors, an unearned purr
  proposal is illegal and MUST resolve to the idle no-op per Article IV.
- **FR-005**: The deliberate purr MUST ignore the motor's purr cooldown
  ("choice beats reflex"). Rationale is RL legibility, not realism: the
  cooldown is not observable, so an action it could swallow would have
  unpredictable outcomes and be learned as unreliable.
- **FR-006**: A deliberate purr taken while the kitty is already purring
  (either origin) MUST be a silent no-op: turn consumed, no state change, no
  announcement, no RNG draw.
- **FR-007**: Spontaneous purr starts MUST announce only per a configured
  announce probability (default 0 — silent). A silent start emits nothing.
  An announcing start (probability satisfied) announces exactly as today.
  The motor's start *cadence* — when purrs begin and how long they last — is
  unchanged by this requirement.
- **FR-008**: Purr-start announcements of either origin are state
  announcements, not proposals: when they fire, they MUST be recorded
  directly — never swallowed by any message cooldown. Deliberate purr starts
  always announce; their audibility is 100% by construction. Purr starts
  stamp **nothing**: companion spec 023 (issue #84, same engine batch)
  retires engine-enforced meow cooldowns, leaving the Purr message cooldown
  with no reader — the stamp is deleted rather than kept as inert plumbing,
  and because the two specs land in one batch, no released engine ever
  carries an intermediate stamp semantics.
- **FR-009**: The flat motor rest (`cooldown_ticks`) MUST be retired in favor
  of a proportional rule with a drawn factor: when a purr of either origin
  ends, a factor is drawn uniformly from
  [`cooldown_factor_min`, `cooldown_factor_max`] and the motor cooldown
  stamped equals ⌈factor × that purr's actual duration⌉. The factor is drawn
  at end-time and used immediately — it is never persisted. The deliberate
  purr's cooldown exemption (FR-005) is unaffected — the stamp binds only
  the motor.
- **FR-010**: The configuration surface MUST change as follows, every knob a
  named tunable with a documented default and its own validation row
  (Article VI):
  - `[purr] announce_probability` — new; probability in [0, 1]; default 0.
  - `[purr] cooldown_factor_min` / `cooldown_factor_max` — new pair
    (mirroring the duration-bounds pattern); 0 < min ≤ max; defaults
    1.75 / 2.75. The midpoint (2.25) sets the duty target — retuned from
    issue #82's fixed 2.5 at clarify, then widened to a per-purr draw, both
    owner decisions (see Clarifications). Equal values recover a fixed
    factor.
  - `[purr] min_ticks` / `max_ticks` — defaults change 6/15 → 8/13; existing
    bounds validation unchanged.
  - `[purr] cooldown_ticks` — retired. A configuration that names it MUST be
    rejected at load with an error naming the retired knob and its
    replacement, never silently ignored.
- **FR-011**: Determinism (Article V) MUST be preserved and its draw
  discipline pinned: the deliberate purr's duration draw happens at action
  application, in the tick's fair apply order; the motor's draws happen in
  the purr phase in stable kitty-id order as today; every spontaneous start
  draws its announce decision exactly once regardless of the probability
  value; every purr end draws its cooldown factor exactly once, in the purr
  phase's stable order, even when the factor bounds are equal; and every
  duration draw happens even when min equals max —
  configuration can change outcomes, never the count or order of draws.
  Same seed + config + ticks → same world, including purrs of both origins.
- **FR-012**: Save/restore MUST reproduce the purr exactly: the state a
  snapshot carries MUST suffice to stamp the same proportional cooldown the
  uninterrupted run would have stamped. A pre-022 snapshot restored mid-purr
  carries no duration; its purr MUST be treated as having the configured
  minimum duration (`min_ticks`) when the cooldown is stamped — a fixed
  convention (the true duration is unrecoverable), biased to the shortest
  lawful rest.
- **FR-013**: Coupling: the proportional cooldown and retuned draw (US3) MUST
  NOT take effect in any released engine without the silent-motor change
  (US2). At these numbers purr starts become materially more frequent (mean
  cycle ≈34.5 vs ≈40.5 ticks today); under the old broadcast rules that
  would mean *more* cooldown-stamping and worse deliberate audibility — the
  retune ships with, never before, mechanism 2.
  (Within this spec the constraint is structural: one change-set, one batch.)
- **FR-014**: Compatibility MUST be schema-invariant: no new message kind, no
  observation change (digest width unchanged), no action-menu growth,
  renumbering, or codec version bump, no mask width change. Every shipped
  policy artifact loads and runs unmodified. Row 38's identity is preserved,
  not repurposed: it remains the purr-meow — the same wire action a policy
  already emits — with its effect corrected to include the purr it always
  named. (This is issue #79's shape A; shape B — a new `Action::Purr` menu
  entry — is rejected as a codec bump orphaning every shipped artifact.)
- **FR-015**: Doctrine reconciliation MUST land in the same change
  (Article VI governance):
  - Spec 011's "purring is never an action" is amended: purring remains
    engine-owned background *state* — there is still no purr action verb —
    but a purr can now be *initiated* by choice through the meow-purr row.
  - The MVP-era "Meow: always legal; the cooldown decides whether it is
    audible" doctrine (spec 001 data model, carried into the spec 014 mask
    contract) is amended: the purr row is the one earned-gated meow row.
    For the six other meow rows the doctrine is simultaneously
    *strengthened* by companion spec 023 — legal in effect, not just in the
    mask: no cooldown ever decides audibility again.
  - Guarding tests that pin the old semantics (purr-proposal-refused,
    always-legal-meow mask assertions, one-meow-per-purr counting) are
    re-baselined deliberately in the same change — a semantics correction
    reconciled with its tests, never a silent weakening.

### Key Entities

- **Purr phase**: the engine-owned rumble a kitty is in — begun by the motor
  or by choice, indistinguishable once running; carries its end tick and
  (new) enough identity to derive its duration at end-time for the
  proportional cooldown.
- **Purr announcement**: the one-time start broadcast (`Purr` message kind,
  unchanged); after this change, deliberate starts always carry it,
  spontaneous starts carry it only per the announce probability.
- **Motor cooldown**: the rest the *motor* observes between rumbles — now a
  freshly drawn multiple of the finished purr's duration; never binding on a
  deliberate purr.
- **Purr message cooldown**: the shared per-kitty message-kind cooldown that
  swallowed two-thirds of deliberate purrs; after this batch it can swallow
  nothing and purr starts no longer stamp it — its retirement (and the fate
  of per-kind meow bookkeeping generally) is owned by companion spec 023.
- **The purr action** (menu row 38 / wire meow-purr): the deliberate purr —
  turn-consuming, earned-gated, motor-cooldown-exempt.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A deliberate purr taken by an eligible kitty is audible to the
  meadow 100% of the time (announcement recorded at purr start), against the
  measured 34.3% before the change.
- **SC-002**: Under default configuration, spontaneous purr starts produce
  zero broadcast announcements while the motor's start cadence is unchanged —
  in a healthy long run the Purr broadcast count drops by ≥97% (from ≈4,900
  per 200k ticks to only what kitties choose to send) with no reduction in
  time spent purring.
- **SC-003**: Every purr in the world, of either origin, occurs at a moment
  the earned rule holds — property-tested over randomized configs and
  behaviors; no purr ever certifies an unhappy cat.
- **SC-004**: A healthy kitty's long-run purring occupancy lies within 2
  percentage points of 1/(1 + the mean of the factor bounds) (≈30.8% at
  defaults) over a run of at least 20,000 ticks, independent of the
  duration bounds and of the factor spread; every purr duration lies within
  the configured 8–13 tick bounds. (Calibration: long-run occupancy is a
  ratio of expectations, so only the mean draw matters; ceiling rounding
  puts the true expectation ≈0.45pp under the ideal and draw noise adds
  ~0.1–0.2pp; the flat-cooldown regression sits ≈4.8pp under it — inside
  the band and outside it respectively, with margin.)
- **SC-005**: Every previously shipped policy artifact loads and runs against
  the new engine without modification, and the RL interface reports identical
  shapes: observation width, action-menu size, mask width, and message-kind
  count all unchanged.
- **SC-006**: Determinism holds with purrs of both origins in play: same seed
  + configuration + tick count → identical world state, across process
  restarts and through a mid-purr save/restore.
- **SC-007**: A configuration naming the retired flat-cooldown knob fails to
  load with an error that names the replacement; no world ever runs silently
  ignoring a tuning the owner wrote down.

## Assumptions

- **The earned rule stays verbatim.** `experiments/exp-002-design-inputs.md`
  §2 flags the rule itself as open for rethink, but the owner's decided
  tuning (issue #82's tuning comment, 2026-07-31) *depends* on the current
  rule: the constant duty cycle (≈30.8% at the adopted defaults) follows
  only because a happy cat re-earns essentially instantly under the `rose`
  clause. Changing the rule
  here would silently invalidate the decided numbers; any rethink is a
  future, separately-specified change.
- **Ceiling rounding for the proportional cooldown** is chosen as the fixed
  rule (deterministic; never shortens rest). The duty-cycle target is
  unaffected beyond a fraction of a tick per cycle.
- **The announce-probability default of 0** is the owner's candidate default
  (issue #82), adopted here. The client consequence — spontaneous purrs lose
  their in-meadow speech bubble, the only in-meadow purr visual — was checked
  and accepted at kickoff (2026-07-31): the quieter meadow is the intended
  semantic shift, and no client work rides this spec.
- **Certified numbers do not survive, and that is planned.** New draws and a
  changed cadence shift the master RNG stream, and audible-meow changes shift
  every listener's observations — no trajectory from the current engine
  survives for comparison. Verification is by this spec's unit and property
  tests plus the full post-batch recertification of all deployable artifacts;
  no byte-identical diff against the old engine is claimed. (Same doctrine as
  the spec 017/SC-004 amendments: deliberate re-baseline, stated in advance.)
- **Sequencing is owner-controlled and out of band**: this engine change
  merges only after the §9.1 deployment soak concludes on the current engine,
  lands in one batch with companion spec 023 (issue #84, meow-cooldown
  retirement — owner decision 2026-07-31), the 24×24 world restore, and the
  `policies/` artifact-home cutover, and precedes exp-002's prereg freeze so
  exp-002 trains and evaluates under one engine. The spec records the
  constraint; the calendar belongs to the owner.
- **Scope boundaries**: no client work; no new message kinds; no change to
  the six non-purr meow rows or their honest-urgency cooldowns; no change to
  the legacy `Action::Purr` wire variant (still refused); no change to the
  purr threshold default (70) or to `thresholds.purr` semantics.
