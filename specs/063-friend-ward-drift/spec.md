# Feature Specification: Friend-Ward Drift (bounded-detour social bias)

**Feature Branch**: `product/friend-ward-drift`

**Created**: 2026-10-17

**Status**: Draft

**Input**: Owner kickoff 2026-10-17 (her words, via the dispersion
requirements note and its relay: "Let's build it and see what happiness
delta it produces on 100x100"). Candidate 3 of the teacher
dispersion-coping package, requirements note
`experiments/gen2-teacher-dispersion-2026-10-15/REQUIREMENTS.md`.
Her ruled shape, verbatim: "if nearest friend > 10 manhattan distance,
prefer motion towards nearest friend (beyond just idle, if selecting
between two water sources, for example, choose the one closer to the
nearest friend)" and "I definitely don't want it to have an outsized
influence on clustering, so let's make it a toggleable flag and we can
compare long-term behavior with and without it. We can tweak the
distances (both friend distance and detour distance) if we need to to
get the desired initial convergence without impacting steady state
behavior." Candidates 1 and 2 of the package stay banked; they are not
this spec's.

## Why now

On 100×100 worlds with dispersed spawns, the roster's opening act is
costly: corners-vs-central bench (requirements note §Measured grounds)
shows early-window happiness 81.0–81.7 vs 84.3–85.4 and distress share
11–13% of kitty-ticks vs ~0%. The answer side of the meow law cannot
span a big map (feasibility hard-filter ≈ 28 tiles), so convergence
rides on the wanter side — where this candidate acts. The owner wants
the mechanism landed so Experiments can screen its happiness delta on
100×100, flag on vs off, seed-paired on the g2cmp comparator worlds;
tuning of both distances is expected to follow the screen, so both are
dials. The one F-053 abort world (size100 seed 905029) converged
without this mechanism — its value is the opening act and a gentle
steady-state nudge, which makes inert-when-off and
no-outsized-clustering the load-bearing requirements, not the drift
itself.

## Clarifications

### Session 2026-10-17

- Q: Should the friend-ward drift also steer the idle potter step, or
  only the choice among relief options? → A: Include the potter (owner:
  "A") — when the flag is on and the nearest known friend is beyond the
  gate, the potter step heads toward that friend, cadence unchanged; no
  separate sub-flag.
- Q: When a friend is known only by sound, may the drift use a stamp of
  any meow kind, or only want/here-word stamps? → A: Want + here words
  only for this feature (owner: "B") — the drift's own friend knowledge
  pre-applies the fence; existing heard-unseen consumers stay unchanged
  until Candidate 2 is kicked off.
- Q (review 1 HIGH-1, relayed to Experiments on her word, their take
  concurring): the cat-anchored relief gate livelocks at the boundary
  (probe-confirmed ping-pong beside a sleeping friend) — how is the
  relief gate measured? → A: "Ruled as recommended" (2026-10-17):
  CANDIDATE-anchored for relief choice — the drift fires on the
  cheapest candidate's friend distance, not the cat's, which removed
  the single-friend oscillation (review 2 then found and closed the
  multi-friend remainder; see its Q/A below and Edge Cases for the
  declared knowledge-flip residual). The potter keeps the cat-anchored
  gate (its boundary dither is harmless idle motion).
- Q (review 2 finding 1, relayed to Experiments on her word, their take
  concurring): the candidate-anchored gate still livelocked with TWO
  known friends — the key read distance to THE cat's-nearest friend,
  whose identity flips as the cat walks — how is the band keyed? → A:
  "As recommended" (2026-10-17): PER-CANDIDATE — each relief option is
  keyed by min over ALL known friends of the distance to that option,
  and the gate reads the cheapest option's key. Every ranking input is
  then fixed per candidate under fixed knowledge (the cheapest is
  absorbing; a fired target only ever switches to a strictly better
  key). The knowledge-flip residual (a friend crossing the vision-disc
  edge, a stamp expiring) is DECLARED, not fixed — see Edge Cases.
- Q (review 1 HIGH-2, same relay): the drift's detour cost flows into
  the need scores, so a near-tie need can flip — which law stands? →
  A: "Ruled as recommended" (2026-10-17): honest pricing kept — the
  score charges the drift winner's real cost, and FR-009 is amended to
  admit need-level reordering bounded by tile_cost × detour (4.0 at
  defaults), named so Experiments' screen prices it. Drift-blind
  scores were rejected: they would underprice walks the teacher
  actually takes and break the 004/019 score/walk invariants.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A toggleable flag that is inert when off (Priority: P1)

An operator runs today's world with the new engine. With the flag
absent (or off) in the config, every world — collection, training,
served — behaves byte-for-byte as it does today. With the flag on, the
same config is otherwise unchanged, so the long-term with/without
comparison the owner asked for is a pure config A/B.

**Why this priority**: Her word makes this the gate on everything else
("let's make it a toggleable flag and we can compare long-term behavior
with and without it"). An off-flag that leaks behavior poisons both
arms of every comparison downstream, and the flag ships off everywhere.

**Independent Test**: Build the engine with the feature, run any
existing config (flag absent) at a fixed seed, and compare every
readable output surface against the pre-feature engine at the same
seed: byte-identical. Flip the flag on in a copy of the config: the run
is accepted by validation and the engine runs to completion.

**Acceptance Scenarios**:

1. **Given** a config with no friend-ward keys, **When** a full run
   executes on the new engine, **Then** collection arrays, trace lines,
   and final world state are byte-identical to the pre-feature engine
   at the same seed.
2. **Given** a config with the flag explicitly off, **When** the same
   run executes, **Then** outputs are byte-identical to the flag-absent
   run.
3. **Given** a config with the flag on and dials at defaults, **When**
   validation runs, **Then** it passes; **Given** a nonsensical dial
   (gate 0, negative detour), **Then** validation rejects it by name.

---

### User Story 2 - Friend-ward choice among near-equal relief options (Priority: P2)

A teacher cat on a big map needs water. Two sources are known; their
walk costs differ by less than the detour bound. Its nearest known
friend is far away (beyond the friend-distance gate). With the flag on,
the cat picks the source closer to that friend — converging while
still relieving its need — instead of the marginally cheaper one.

**Why this priority**: This is her ruled example ("if selecting between
two water sources … choose the one closer to the nearest friend") and
the mechanism that lets dispersed cats drift together through their
ordinary errands.

**Independent Test**: Stage a world: one cat, its nearest known friend
beyond the gate, two relief sources of the same kind whose priced costs
differ by less than the detour bound, the friend-ward one costlier.
Flag on: the cat walks to the friend-ward source. Flag off: the cat
walks to the cheaper source. Options costlier than the band are never
chosen in either case.

**Acceptance Scenarios**:

1. **Given** flag on, nearest known friend beyond the gate, and two
   same-kind relief options within the detour band of each other,
   **When** the cat seeks that relief, **Then** it pursues the option
   closest to that friend, and the scored (decision) side and the walk
   side agree on the same option.
2. **Given** the same world with the friend within the gate of the
   cheapest option (the relief gate's anchor, ruled 2026-10-17),
   **When** the cat seeks relief, **Then** its choice is identical to
   flag-off.
3. **Given** a friend-ward option whose priced cost exceeds the
   cheapest by more than the detour bound, **When** the cat seeks
   relief, **Then** the cheapest option wins exactly as today — the
   drift is a bounded detour, never an open preference.
4. **Given** no known friend (none visible, none heard within the
   digest window), **When** the cat seeks relief, **Then** its choice
   is identical to flag-off.
5. **Given** relief of a kind with exactly one known option, **When**
   the cat seeks it, **Then** behavior is identical to flag-off — the
   drift reorders choices, it never changes whether relief is pursued.

---

### User Story 3 - Friend-ward potter when nothing presses (Priority: P3)

A teacher cat with no pressing need potters about. Its nearest known
friend is beyond the gate. With the flag on, the potter step prefers
the direction that closes distance to that friend, at the potter's
existing cadence — so dispersed cats drift together during exactly the
idle ticks that dominate the opening act after spawn (needs start low).

**Why this priority**: Her words put it in scope ("prefer motion
towards nearest friend (beyond just idle, …)" — idle motion is the base
case her generalization extends). It is P3 because the relief-choice
story carries her explicit example and the potter bias is severable: US1
+ US2 alone are a shippable, screenable mechanism.

**Independent Test**: Stage a cat with all needs below the potter
threshold and a known friend beyond the gate. Flag on: over repeated
potter steps, motion closes Manhattan distance to the friend. Flag
off, same seed: the potter is today's uniform random step,
byte-identical to the pre-feature engine.

**Acceptance Scenarios**:

1. **Given** flag on, nothing pressing, and the nearest known friend
   beyond the gate, **When** the potter fires, **Then** the step moves
   toward that friend (through the existing step rule, sidesteps
   included) rather than a uniform random direction.
2. **Given** flag on and the nearest known friend within the gate (or
   no known friend), **When** the potter fires, **Then** the step is
   today's uniform random step.
3. **Given** flag on, **When** potter opportunities occur, **Then**
   the potter's rate (how often a potter step happens at all) is
   unchanged from today — the drift turns its direction, never its
   cadence.

---

### Edge Cases

- No known friend at all (alone in the fog, nothing audible): every
  drift site is inert; behavior equals flag-off.
- Two known friends at equal Manhattan distance: the nearest-known-
  friend pick is deterministic (distance, then the lower id), matching
  the house tiebreak everywhere else.
- Two in-band relief options equidistant from the friend: deterministic
  fallback to today's ordering (priced cost, then the lower id).
- The remembered (memory) relief candidate participates in the band
  like any other option, measured from its remembered position; the
  existing rule that a real sighting beats a memory on ties is
  preserved.
- A relief kind with an acceptance bound (the sunbeam walk is accepted
  only within reach): the drift must never promote an option that
  fails the bound — it changes WHICH acceptable option wins, never
  WHETHER relief/walking happens. A friend-ward beam beyond reach loses
  to an in-reach beam even inside the band.
- The friend is known only as an audible stamp: the gate and the
  friend-ward distance are measured to the stamp's position; only
  want/here-word stamps qualify (FR-005), and a qualifying stamp
  contributes position and freshness only.
- A friend's freshest audible meow is a free-register word while an
  older want/here stamp of the same friend is still within the digest
  window: the drift uses the freshest QUALIFYING stamp — the
  free-register word neither places the friend nor hides the older
  lawful stamp.
- Flag on alters the engine's RNG consumption relative to flag off
  (the potter's direction draw): accepted and declared — the flag-on
  arm is its own stream; flag-off must consume draws exactly as today.
- Mid-walk stability (restated after review 2): under FIXED knowledge
  (the known-friend set and candidate set unchanged), every ranking
  input is fixed per candidate, the cheapest-wins state is absorbing,
  and a fired target can only switch to a strictly better key — so
  walking alone can never oscillate the choice. Two multi-tick
  regressions pin it (the review-1 single-friend probe and the
  review-2 two-friend probe). DECLARED RESIDUAL, not fixed: knowledge
  itself can change as the cat walks — a friend crossing the
  vision-disc edge, a stamp expiring — and can in principle ping-pong
  the choice (~1 per 100–200k random stages; transient in the live
  engine, where sleeps end, stamps expire and needs cross thresholds).
  At served vision radius 4 the relief gate cannot fire from visible
  knowledge alone; the displaced 100×100 legs run radius 5/6, so the
  screened flag-on arm IS exposed — Experiments' screen prices it, and
  F-053 stays the asymmetric backstop.
- Friend adjacent to the cat but far from the cheapest option: the
  relief gate FIRES (it measures from the candidate), and the drift
  prefers relief near the pod rather than walking away from an
  adjacent friend.
- Gate dial set below any realistic map distance or detour bound set
  to zero: both are lawful (zero detour = drift only among exact-cost
  ties; a huge gate = drift never fires). Gate zero is rejected:
  "further than zero away" would fire on adjacent friends and
  contradict the rule's intent.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The feature MUST be controlled by a single on/off flag in
  the world config's behavior section, default off, with "absent" and
  "off" indistinguishable in every observable way. No served or
  committed experiment config carries the flag on in this feature's
  PRs.
- **FR-002**: With the flag off, the engine MUST be behaviorally
  byte-identical to the pre-feature engine: same decisions, same RNG
  consumption, same outputs on every readable surface (collection
  arrays, traces, world state) for any config and seed. No existing
  golden, pin, or fixture is re-cut by this feature.
- **FR-003**: The friend-distance gate and the detour bound MUST both
  be config dials with defaults (gate: 10, Manhattan, her rule; detour
  bound: 4 priced-cost tiles, Experiments' pencil), validated with
  named errors (gate must be positive; detour bound must be
  non-negative).
- **FR-004**: Friend knowledge MUST be computed from the cat's fogged
  view only: the KNOWN-FRIEND SET is the visible roster members plus
  unseen roster members at their freshest audible want- or here-word
  stamp within the digest window. Relief choice (Site 1) ranks against
  the whole set (ruled 2026-10-17, review 2); the potter (Site 2)
  walks toward the single nearest known friend, picked by Manhattan
  distance with the lower id breaking ties. No read of unobservable
  state (true positions, needs, private counters) may enter either
  computation.
- **FR-005**: The drift's stamp set is law-named want and here words
  only (her ruling, Clarifications): a stamp of any other kind — the
  free register, purr, WaitForMe — MUST NOT enter the drift's friend
  knowledge. Within the admitted set, a stamp contributes position and
  freshness only. The existing heard-unseen consumers (cuddle walk,
  play scan) keep their current kind-agnostic set untouched — their
  narrowing is banked Candidate 2's, not this spec's.
- **FR-006**: The drift MUST fire only when the flag is on AND the
  known-friend set is non-empty AND the site's gate reading exceeds
  the gate — for relief choice, the CHEAPEST CANDIDATE's friend key
  (its distance to its own nearest known friend; ruled 2026-10-17);
  for the potter, the cat's distance to its nearest known friend. In
  every other case each drift site MUST decide exactly as flag-off.
- **FR-007** (relief choice): When the drift fires at the shared
  priced-element selection, the choice MUST be: among candidates whose
  priced travel cost is within the detour bound of the cheapest
  candidate — restricted to candidates satisfying any acceptance bound
  the calling context applies — the one with the smallest friend key
  (min over all known friends of the Manhattan distance to that
  candidate; ruled 2026-10-17), with ties falling back to today's
  ordering (priced cost, then id). The scored side and the walk side
  MUST keep choosing through the same shared rule, so they always
  agree on the same option.
- **FR-008** (potter): When the drift fires at the idle potter, the
  potter step MUST move toward the nearest known friend through the
  existing step rule instead of a uniform random direction. The
  potter's firing rate MUST be unchanged.
- **FR-009**: The drift MUST never change whether relief is taken once
  a need is pursued, nor any rung of the decision ladder above the
  scored selection (scene continuation, opportunism, groom response,
  cue answers, the luxury line). Within the scored selection, honest
  pricing is kept (ruled 2026-10-17): the score charges the drift
  winner's real walk cost, so a need's score may drop by at most
  tile_cost × detour relative to flag-off, and a near-tie need
  ordering may flip within that bound — a real, demonstrable
  trade-off, priced for Experiments' screen. Beyond that bound the
  drift changes nothing above target selection.
- **FR-010**: With the flag on, decisions MUST remain deterministic
  for a given context: identical contexts choose identically.
- **FR-011**: The full existing test and config surface MUST pass
  unchanged (shipped-config sweep green), and the documented behavior
  of this spec MUST be covered by tests that fail if the flag leaks
  into flag-off behavior.

### Key Entities

- **Friend-ward drift flag + dials**: three behavior-section config
  values — the flag (off by default), the friend-distance gate
  (Manhattan tiles), the detour bound (priced-cost tiles). Dials exist
  because her ruling names them as the tuning levers for "initial
  convergence without impacting steady state".
- **Nearest known friend**: a derived, observation-only quantity —
  (position, id) of the closest roster member the cat can currently
  see or has heard via a want/here-word stamp within the digest
  window (FR-005's fence).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A full run at a fixed seed on any pre-feature config,
  flag absent, is byte-identical on every readable output surface to
  the pre-feature engine; likewise flag explicitly off. Zero existing
  tests, goldens, or pins change in this feature's PRs.
- **SC-002**: In a staged two-option scenario (friend beyond gate,
  costs within the band), the flag-on engine picks the friend-ward
  option and the flag-off engine picks the cheaper one; with the cost
  gap beyond the band, both pick the cheaper one. Score side and walk
  side agree in all cases.
- **SC-003**: In staged gate scenarios (friend within gate; no known
  friend), flag-on decisions equal flag-off decisions exactly.
- **SC-004**: In a staged potter scenario (nothing pressing, friend
  beyond gate), flag-on potter steps close Manhattan distance to the
  friend; the potter's firing rate over a fixed window matches
  flag-off within binomial tolerance.
- **SC-005**: Dial validation rejects gate 0 and negative detour with
  errors naming the section and key; defaults load when the keys are
  absent but the flag is on.
- **SC-006**: The mechanism supports Experiments' screen as a pure
  config A/B: the same binary, the same config apart from the flag,
  runs both arms of the 100×100 seed-paired comparison (the happiness,
  clustering, and dispersion reads are Experiments' lane and are not
  re-specified here).

## Design-doctrine check (CLAUDE.md rule 8)

This spec scripts teacher behavior, so each doctrine rule was checked
before planning:

- **Rule 5 (a teacher may only act on what the student can see) —
  moved choices.** FR-004 exists because of it: "nearest friend" was
  amended to nearest KNOWN friend (visible or freshest audible stamp)
  precisely so the drift never navigates toward state the student's
  observation masks. The knowledge base is the same fogged view and
  heard-unseen digest the observation already carries; no new
  observation cell, so no schema boundary.
- **Rule 6 (the free register is never scripted) — moved a choice.**
  FR-005 exists because of it: the drift's friend knowledge admits
  law-named want/here stamps only (her ruling, Clarifications), so no
  scripted decision ever keys on a free-register word — harmony with
  059 FR-012's "mute and deaf" rather than the apparent tension
  Experiments' rule-3 report flags on the existing kind-agnostic
  consumers. Keying on law-named kinds is established practice (the
  groom response keys on WantBath). Within the admitted set a stamp
  contributes position and freshness only. The existing consumers'
  narrowing stays banked Candidate 2's; this spec touches none of
  them.
- **Rule 9 (frozen models / pins) — moved choices.** FR-001/FR-002:
  the flag ships off everywhere, flag-off is byte-identical, so no
  pin or golden re-cuts and no deploy question arises. Turning the
  flag on in collection or a served world is a freeze-sitting /
  deploy ruling, not this spec's. Flag-on RNG divergence is declared
  (edge case list) and attributed to the flag by construction.
- **Rule 7 (build when the world values it) — checked, consciously
  sequenced.** Whether the world values friend-ward drift is exactly
  what Experiments' 100×100 screen measures (SC-006) before any
  decision to collect a corpus with the flag on. This spec lands the
  mechanism; it does not seed the behavior into training.
- **Rule 8 (scarcity, not incentives) — checked, moved nothing.** No
  observation or scarcity change; the drift is teacher coping under
  the existing fog, on the wanter side where the requirements note
  shows convergence must ride.
- **Rule 12 (relief always available) — moved a choice.** FR-009 and
  the acceptance-bound edge case: the drift never changes whether
  relief is pursued or taken, only which near-equal option wins —
  relief availability is untouched by construction.
- **Rule 2 (prices are physics) — checked, moved nothing.** No price,
  reward, or payout moves; the drift is a scripted-choice rule, and
  the detour band is bounded by the existing priced-travel physics
  rather than introducing a new pay.
- **Rules 1, 3, 4, 10, 11 — checked, moved nothing.** No reward term,
  no rider or specialist change, no edge or charm pay, no gate or bar
  moves, no invalidation clause drafted here (Experiments' screen
  declares its own reads in their lane).

## Assumptions

- The blind lattice-tour search (explore) is explicitly out of scope —
  that surface belongs to candidate 1 (waypoint start-index), which
  stays banked. (The idle potter's inclusion is ruled, not assumed:
  see Clarifications.)
- **Friend knowledge is the drift's own, fenced to want+here stamps**
  (ruled, see Clarifications); the shared heard-unseen helper's
  existing consumers are untouched. If banked Candidate 2 later lands
  the same fence on those consumers, the two meet with no change to
  this feature.
- **"Friend" means any other roster member**, as everywhere else in
  the teacher (no friendship graph exists); busy/idle state does not
  gate the drift (knowledge of a friend's position is enough to drift
  toward it — drifting is not conscription).
- The detour bound is denominated in priced-cost tiles (the same
  units as the existing priced travel), so a wet detour is dearer
  than a dry one — consistent with the walk physics the band sits on.
- Dial names, exact config types, and the validation wording are
  plan-level choices; the gate default 10 and detour default 4 are
  the pencils from her rule and Experiments' amendment, expected to
  move after the screen ("we can tweak the distances … if we need
  to").
- Experiments' screening protocol (corners bench, 20×20 guard, watch
  channels, density-pin re-runs) lives in their requirements note and
  is not duplicated here; this spec's deliverable is the mechanism
  and its config surface.
