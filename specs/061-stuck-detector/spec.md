# Feature Specification: Stuck Detector at Decoding

**Feature Branch**: `product/stuck-detector`

**Created**: 2026-10-13

**Status**: Planned (clarify complete 2026-10-14; cross-artifact analysis remediated 2026-10-15)

**Input**: The owner's kickoff in the Product session, 2026-10-13
("061 stuck detector") — the last of the Gen 2 build-phase Product
specs (prereg skeleton §10.1), after the schema wall (058, merged),
the teacher rework (059, #447), and the empty-bowl early end (060,
#448). Corpus collection waits on this landing.

**Ruling sources** (records beat this spec on any discrepancy):
`experiments/fog-gen1-shakeout/GEN2-INPUTS.md` §"Same mind in several
seats: the twin fragility" (**RULED by the owner 2026-09-16, "options
3+4 for gen 2"** — option 3 is this detector: "Fires on an exact
observation-and-action repetition (or net-zero displacement with an
armed need) over a short window and perturbs: a random legal move, or
the scripted brain for one tick. Inert on healthy behavior; fires on
the symptom whatever the cause; the same trigger the deferred distress
intervention needs. Served-side, so it guards a mind regardless of
what it was trained with"); §"The clock input" (**RULED 2026-10-07,
"2) drop"** — the clock cell is gone at the Gen 2 schema bump, landed
in 058; this detector is the served-side net that replaces the
accidental de-synchronizer); the corpus recipe item 4 (a stuck read as
an INVESTIGATE row: net-zero displacement over N ticks with an armed
need, per seat); `experiments/FINDINGS.md` F-043 (the stuck detector
is the intended fix for the pacing shape; re-verify at each Gen 2
battery) and F-044 (the pinned-clock probe series: nine watchdog
crossings in 618 world-probes with one mind in every seat, the worst a
perfect MoveW/MoveE 174/174 two-tile limit cycle with the bowl in
view); prereg skeleton §10.1 (lands before corpus collection).

## Why now

Every twin failure on record is one mechanism: a greedy deterministic
policy in a state the world keeps returning it to makes the same
choice forever, and nothing breaks the loop. The drifting clock input
was breaking it by accident; Gen 2 drops the clock (058) and removes
the mirror-symmetry cause with the identity block (058, option 4).
This spec is option 3, the safety net: a serving-side guard that fires
on the symptom whatever the cause, so a seated mind — Gen 1, Gen 2, or
the future LLM seat — cannot sit in a loop while a need climbs. It is
not a reprice (GEN2-INPUTS "What it is not"): the Nash team reward
already values the starving cat, and doctrine rule 9 says a frozen
model cannot answer a price change anyway. The guard lives where the
mind's action is decoded into a proposal, which is also why it must
land before corpus collection: the same trigger is the corpus
INVESTIGATE row and the hook the deferred distress intervention
(BACKLOG; the LLM → local → scripted fallback chain) will key on.

## Clarifications

### Session 2026-10-13

- Q: Which perturbation form does a fire substitute — a random legal
  move, the scripted brain for one tick, or an escalation between
  them? → A: **B** (scripted brain for one tick), her words: "B (if we
  run into scenarios where that still loops, we'll look to fix it for
  the scripted agent)". The mirror-twin residual is accepted: if the
  scripted substitute itself loops, the fix lands in the scripted
  agent, not in added randomness.
- Q: Armed by default on the served, certified Gen 1 roster, or
  configuration-armed and dark until the Gen 2 seating? → A: **A**
  (ships dark; arms at the Gen 2 seating). Certified Gen 1 behavior
  and the live refusal/welfare baselines stay untouched until then.
- Q: Does "no net movement" mean strictly stationary, or never
  escaping a small neighborhood of where the window started? → A:
  **B** (confined: never leaves Manhattan radius 1 of the
  window-anchor tile), her words: "B, first verify if there would
  have been any false positives under this rule". Verified 2026-10-13
  by replaying the rule over recorded behavior
  (`verification-2026-10-13.md` in this directory): on the certified
  policy roster (125,000 cat-ticks, lab replay under the trained
  clock) **zero false positives** — every fire belongs to one real
  135-tick corner-starvation episode (Biscuit at the (18–19, 0)
  corner, eat 69 → 100, the GEN2-INPUTS corner signature verbatim);
  on the scripted anchor traces (300,000 cat-ticks) zero fires at
  window ≥ 30 or armed line 90, and two borderline fires at the
  loosest sweep point (window 20, armed 75): a cat pacing beside a
  cuddle partner who arrived four ticks later — and scripted seats
  are exempt regardless (FR-003). The replay also forced one
  refinement, folded into FR-001/FR-002: a strict
  no-scene-in-the-window gate misses the real episode at window ≥ 30
  (the loop contains one-to-two-tick play flickers), so scene ticks
  pause the armed streak rather than reset it, and only a scene
  relieving the tracked need clears it; with that gate the real
  episode fires at every window length swept and the healthy arms
  stay clean.
- Q: Should the detector's enablement be a simple on/off switch, or
  three-state — off, observe-only (fires recorded, nothing
  substituted), and enforce? → A: **B** (three-state: off /
  observe-only / enforce). Observe-only tracks the signature and
  writes the full fire record but substitutes nothing, so the live
  Gen 1 fire rate can be read without touching certified behavior.
  The served Gen 1 default remains off (dark, per the arming answer
  above); any move to observe-only before the Gen 2 seating is the
  owner's call.

### Session 2026-10-15

- Q: Does the substitute stay the needs-driven scripted brain at the
  Gen 2 seating (not the Gen 2 corpus demonstrator)? → A: her words:
  "Yes, substitute brain should be scripted (needs driven) until
  LLMs/two-tier fallback exists" — pinned in FR-004; the two-tier
  (LLM → local → scripted) chain is the deferred distress
  intervention's (BACKLOG), and revisiting the substitute belongs to
  that future spec.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A trapped mind gets freed (Priority: P1)

A watcher sees a cat pace the same two tiles, hungry, with the bowl in
plain view — the F-044 limit cycle. With the detector in place the
loop ends within a short, declared window: one of the cat's proposals
is replaced, the repeating state is broken, and the cat's own policy
resumes from the new state. The watcher sees a cat that hesitated and
recovered, not one that starved in place.

**Why this priority**: This is the ruled purpose. The pinned-clock
re-run raised the catastrophe tail from 0 to 3 runs in 120 on exactly
this shape; the detector is the standing answer once the clock crutch
is gone.

**Independent Test**: Seat a mind (or a doctored advisor) that
reproduces an exact movement loop with an armed need; run past the
window; assert the loop breaks and the detector fired exactly where
the signature held.

**Acceptance Scenarios**:

1. **Given** a mind-class seat confined within the configured radius
   of its window anchor with a need accumulating armed scene-free
   ticks, **When**
   the stuck window completes, **Then** the detector substitutes that
   seat's next proposal, records the fire, and the engine applies or
   refuses the substitute under its ordinary rules.
2. **Given** the same loop shape on a seat whose needs are all below
   the armed line (contented idling in a static view), **When** any
   number of ticks pass, **Then** the detector never fires.
3. **Given** a kitty holding still inside a need-relieving scene (a
   long sleep at the bed), **When** the window elapses, **Then** the
   detector never fires — relief in progress is not stuck.

---

### User Story 2 - Every intervention is on the record (Priority: P2)

The operator and the Experiments thread can read every fire: which
seat, which tick, what signature held (window, displacement, the armed
need and its level), what the mind proposed, and what was substituted.
The corpus-collection instrument reads stuck events per seat off these
rows (the INVESTIGATE-row consumer), and each Gen 2 battery re-reads
the fire rate (F-043's re-verify clause).

**Why this priority**: An unobserved intervention would silently edit
the behavior record that certification and the corpus read. The
detector exists to be read as much as to act.

**Independent Test**: Force a fire; assert the record carries full
attribution and is queryable alongside the serving logs the welfare
watchdog already writes.

**Acceptance Scenarios**:

1. **Given** any fire, **When** it is recorded, **Then** the record
   names the seat, tick, window length, anchor tile and confinement
   span, the armed need and its value, the proposal replaced, and the
   substitute proposed — nothing anonymous.
2. **Given** a served world with the detector in observe or enforce,
   **When** the operator queries serving status, **Then** per-seat
   fire counts are visible without reading raw logs.

---

### User Story 3 - The baseline stays trustworthy (Priority: P3)

A researcher comparing runs can trust that the detector changed
nothing it did not announce: scripted seats never pass through it,
healthy minds never trigger it, and a replay of the same world under
the same configuration reproduces the same fires and the same
substitutions.

**Why this priority**: The served Gen 1 roster is certified and the
refusal/welfare baselines are live. A guard that perturbed
unreproducibly, or brushed scripted seats, would cost more in
invalidated reads than it buys in safety.

**Independent Test**: Run the healthy reference roster with the
detector on and off; assert zero behavioral divergence outside fires,
and bitwise-identical fire sequences across replays of the same seed
and configuration (deterministic seats).

**Acceptance Scenarios**:

1. **Given** a scripted-class seat, **When** the world runs any length,
   **Then** the detector never observes, fires on, or substitutes for
   that seat.
2. **Given** two replays of the same seed, configuration, and
   deterministic mind, **When** both complete, **Then** their fire
   records are identical, substitutions included.

---

### Edge Cases

- A fire's substitute proposal is itself illegal or refused at apply
  time: the engine resolves it exactly as any refused proposal
  (Article IV — safe outcome, refusal row); the detector does not
  retry within the tick.
- The seat is still stuck after a fire (the loop's period exceeds the
  window, or the perturbation fed back into it): the detector re-arms
  and may fire again only after a fresh full window — never on
  consecutive ticks.
- Two mirrored seats are stuck in the same twin loop: each fires
  independently on its own window and each gets the scripted brain's
  decision for its own kitty. Mirror-symmetric scripted substitutes
  re-entering the loop is an accepted residual (owner, 2026-10-13):
  "if we run into scenarios where that still loops, we'll look to fix
  it for the scripted agent" — the fix, if ever needed, lands in the
  scripted agent, not in added randomness here.
- A boxed-in seat with no legal move available: the substitution
  resolves to a safe no-op through the ordinary proposal path; the
  fire is still recorded.
- Stepping outside the radius mid-window: the window resets with a
  new anchor; confinement never accumulates across escapes.
- A scene opens mid-window: the tracked need's streak pauses for the
  scene's ticks and resumes after — unless the scene relieves that
  need, which clears the streak (FR-002). A cat spending the whole
  window inside relieving scenes therefore never fires.
- An armed need crossing the line mid-window: that need's streak
  starts at the crossing, not retroactively.

## Requirements *(mandatory)*

### Functional Requirements

**Trigger (the stuck signature)**

- **FR-001**: The system MUST track, per mind-class seat, a stuck
  signature defined as (clarified 2026-10-13, option B, replay-
  verified): over a configurable window of consecutive ticks the
  kitty never leaves the configurable confinement radius (Manhattan;
  default 1, the replay-verified value) of the window-anchor tile
  (the tile where the window opened), while some one need
  accumulates a window-length count of armed scene-free ticks —
  ticks at or above the armed line with no activity scene in
  progress.
- **FR-002**: Window bookkeeping: stepping outside the radius resets
  the anchor to the current tile and the window with it. A scene
  tick PAUSES a need's armed streak (neither advances nor clears
  it) — unless the seat's own scene relieves that need, which clears
  the streak: the scene's governing need is that need, counting only
  the seat's own relief (grooming another relieves the friend's
  bath, not the groomer's; solo rest governs nothing). A scene-free
  tick below the armed line clears the streak too; a below-line
  value during a non-relieving scene only pauses. Both the pause
  gate and this relief rule are replay-verified
  (`verification-2026-10-13.md`, including the 2026-10-15 re-run
  under the governing-need rule). Strict no-scene-in-the-window
  semantics are WRONG by measurement: the one real episode on record
  carries one-to-two-tick play flickers that would mask it at
  window ≥ 30.
- **FR-003**: Scripted-class seats MUST be entirely outside the
  detector: never observed, never fired on, never perturbed. The
  seat-class declaration the server already carries is the boundary.

**Perturbation (the fire)**

- **FR-004**: On a completed signature the detector MUST replace that
  seat's next decoded proposal with the scripted brain's decision for
  that kitty for that one tick (clarified 2026-10-13, option B): the
  substitute is whatever the default built-in needs-based behavior —
  Article IV's own named fallback — would propose from the same
  start-of-tick snapshot. That brain stays the substitute at the
  Gen 2 seating too (it is the constitutional fallback, not the Gen 2
  corpus demonstrator) — RULED by the owner 2026-10-15: "substitute
  brain should be scripted (needs driven) until LLMs/two-tier
  fallback exists" (the deferred distress intervention's
  LLM → local → scripted chain, BACKLOG). One tick only; the mind
  resumes on the next.
- **FR-005**: A perturbed action MUST never carry a free-register
  emission — the sound-named kinds (mew, chirp, trill, ekekek) whose
  meaning only the cats author (doctrine rule 6: the free register is
  never scripted, and a guard's substitute is scripted output).
  Law-named words (Want*/Here*/WaitForMe, Purr) mean what their
  legality rule enforces and MAY appear in a substitute.
- **FR-006**: The perturbation MUST act only on the proposal side.
  The engine validates the substitute exactly as it validates any
  proposal (Article IV); no engine rule, tick-order step, or scene
  rule changes under this spec.
- **FR-007**: After a fire the detector MUST stand down for that seat
  until a fresh full window completes (no consecutive-tick firing).

**Determinism and reproducibility**

- **FR-008**: The perturbation introduces no new randomness: the
  scripted substitute is a function of the same start-of-tick snapshot
  the seats decide against and of the seat's dealt per-tick decision
  stream (which the mind's own decision may have advanced), and any
  randomness it draws flows through the one seeded RNG as always
  (Article V). A replay of the same seed,
  configuration, and deterministic seat MUST reproduce the identical
  fire sequence and identical substitutes. On ticks where no
  substitution occurs — no fire, or a fire under observe-only —
  detector bookkeeping MUST leave the engine's RNG sequence
  untouched.

**Scope of deployment**

- **FR-009**: The detector MUST apply to every mind-class seat
  regardless of what the mind was trained with (Gen 1, Gen 2, future
  LLM seats) — it is the served-side net, not a Gen 2 training
  feature. It SHIPS configuration-armed but dark (clarified
  2026-10-13, option A): the served default is off, with enforce
  armed at the Gen 2 seating; observe-only (FR-010) is available
  earlier on the owner's word. The certified Gen 1 roster's live
  behavior and the standing refusal/welfare baselines are untouched
  by this spec's deploy.

**Configuration**

- **FR-010**: Window length, armed line, confinement radius, and the
  detector's enablement MUST be configuration with documented
  defaults, living with the serving layer's own settings (the welfare
  watchdog's pattern), never magic numbers (Article VI). Enablement
  is three-state (clarified 2026-10-13, option B), the configuration
  literals `"off"` / `"observe"` / `"enforce"`: off; observe
  (observe-only — the signature is tracked and every completed fire
  recorded with full FR-011 attribution, but no proposal is
  substituted; on a budgetless run the world is tick-for-tick
  identical to off, and on the served path the only difference is
  the time spent computing the record inside the seat's decision
  budget); and enforce. The served Gen 1 default is off (FR-009).
  Window, armed-line, and radius defaults are set at plan time from
  the measured cycle data (the F-044 limit cycle and the healthy-soak
  stillness distribution), not guessed.

**Observability**

- **FR-011**: Every fire MUST be recorded with full attribution: seat
  and kitty, tick, window length, the window-anchor tile and the
  confinement span (ticks confined), the armed need and its value,
  the proposal replaced, and the substitute. The records MUST be
  readable by the corpus instrumentation (the INVESTIGATE-row
  consumer) and alongside the serving logs.
- **FR-012**: Per-seat fire counts MUST be visible in the serving
  status surface without log archaeology, and the trigger condition
  MUST be exposed in a form the deferred distress intervention can
  later key on without re-deriving it (BACKLOG; forward hook only —
  the intervention itself is out of scope).

### Key Entities

- **Stuck signature**: the per-seat window state — anchor tile,
  confined-tick count, per-need armed scene-free streaks. Exists only
  for mind-class seats; bookkeeping per FR-002.
- **Fire record**: one perturbation event with the FR-011 attribution.
  The unit the corpus INVESTIGATE row, the Gen 2 battery re-read, and
  the deferred intervention all consume.
- **Seat class**: the existing scripted/mind declaration; the
  detector's hard boundary (FR-003).
- **Detector configuration**: window length, armed line, confinement
  radius, enablement (three-state per FR-010: `"off"` / `"observe"` /
  `"enforce"`), and the status ring capacity; the perturbation form is
  fixed (the scripted brain, clarified 2026-10-13);
  serving-layer-owned (FR-010).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On the F-044 reproduction (one mind in every seat,
  pinned-clock conditions, the two-tile limit cycle), every stuck
  episode ends within one detector window plus one tick of the
  signature completing, and the catastrophe shape (distress age ≥ 150
  on the pacing signature) is absent from the re-run arm.
- **SC-002**: On the healthy reference roster (the five-network,
  30 × 20k soak shape), the fire rate is measured and declared, both
  arms on record — a declared number read from a paired observe-mode /
  off comparison, never an assumed zero and never a pass bar
  (doctrine rule 10); the paired off and observe arms show zero
  behavioral divergence (an enforce arm diverges from its first
  substitution onward, by design).
- **SC-003**: 100% of fires in any run carry the full FR-011
  attribution; zero anonymous or partial records.
- **SC-004**: Two replays of the same seed, configuration, and
  deterministic seats produce identical fire records end to end.
- **SC-005**: Scripted-class seats show zero detector observations and
  zero fires across the whole test battery, by construction and by
  test.

## Design-doctrine check (CLAUDE.md rule 8)

This spec observes and scripts behavior, so each doctrine rule was
checked; the ones that moved a choice:

- **Rule 9 (frozen models cannot answer a reprice)** moved the whole
  shape: the pacing/limit-cycle defect is answered by a served-side
  guard, not a price or reward change — GEN2-INPUTS records "not a
  reprice" as part of the ruling.
- **Rule 6 (the free register is never scripted)** moved FR-005: a
  substitute action is never a free-register emission.
- **Rule 10 (a noise reading is never a pass bar)** moved SC-002's
  form: the healthy-roster fire rate is declared from a paired read,
  not gated on an assumed zero.
- **Rule 12 (relief is always available)** moved the posture: the
  detector guards access to relief (a stuck cat is a cat its own
  policy has cut off from a visible resource) and hides nothing.

Checked and moved nothing: rule 1 (no reward term enters or changes),
rule 2 (no state of the world is priced), rule 3 (no side relief — the
detector relieves nothing itself), rule 4 (no new behavior is built),
rule 5 (no teacher acts here), rule 7 (no behavior-world pairing
question), rule 8 (no scarcity or incentive design), rule 11 (the
invalidation domain belongs to the Gen 2 prereg, which already names
the detector).

## Assumptions

- **Trigger form**: the ruled text offers "an exact
  observation-and-action repetition (or net-zero displacement with an
  armed need)". This spec pins the displacement-with-armed-need form
  (FR-001): it is the form two of the three ruling records use (the
  clock ruling and the corpus recipe item), and the exact-repetition
  form false-positives on healthy stillness — a contented cat idling
  in a static view repeats its observation and action exactly without
  being stuck. The known F-044 cycles (MoveW/MoveE dithers) stay
  confined to radius 1, so nothing on record escapes the pinned form.
  Confirmed at clarify (option B, 2026-10-13) and replay-verified.
- **Armed line default**: the safeguard threshold's neighborhood
  (Article I places guaranteed relief at 75); the exact default is a
  plan-time choice from data, per FR-010.
- **Window default**: set at plan time from the F-044 cycle lengths
  and the healthy-soak stillness distribution, long enough that the
  measured ~0.4%-of-ticks single-idle refusal races (the
  partner-absent split) sit nowhere near it.
- **Seat classes exist**: the server already carries a
  scripted-or-mind declaration per seat (the refusal-stamp work);
  FR-003 leans on it rather than inventing a parallel notion.
- **Engine untouched**: the whole feature lives with the serving
  layer; the engine's rules, tick constitution, and
  `engine_defaults_sha256` are unchanged (the welfare watchdog set
  the pattern).
- **Not in scope**: the distress intervention itself (deferred,
  BACKLOG — this spec only exposes its trigger); the identity input
  (landed in 058); the corpus coverage instrument and the INVESTIGATE
  reads themselves (Experiments-lane consumers of FR-011's records);
  any training-time use.
