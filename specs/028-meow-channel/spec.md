# Feature Specification: The Meow Channel — exp-004 Schema Batch

**Feature Branch**: `028-meow-channel`

**Created**: 2026-08-08

**Status**: Draft

**Input**: The complete exp-004 spec-input package, `experiments/exp-004-design-inputs.md`
(final at PR #146, with review responses from PR #145 and settlements through PR #149).
Every design input is settled on the Experiments side; this spec is written end-to-end
from that package. This is the batch's **single generation wall**: every schema-level
change exp-004 needs lands here, together, as 026/027 were batched.

## Why (context for reviewers)

The meow channel is empirically dead: 0.2% of dataset v3, BC clone accuracy 0.0000,
policy meow rates 0.01–0.41 per 1k ticks across all nine exp-003 candidates. The
diagnosis (registered in the design inputs, owner-settled): a meow costs a whole turn,
the emitter cannot see its own signal, two of six needs have no word at all, and the
one reciprocal trade in the engine (grooming — Bath for the groomed, Cuddle for the
groomer) has no way to be advertised and has **never once occurred** in demonstrator
data (GroomKitty: 0 ticks in 800k). Interests are aligned (team welfare at p = 0), so
cheap talk is stable: the fix is to **zero the marginal cost and prevent spam
mechanically** — ride-along emission, grounded legality, cooldown in the mask — not
motivationally (no reward penalties; F-011).

The legible success criterion, quoted from the package: *if the rework works, cats
groom each other* — Bath and Cuddle both fall, and action classes 13–15 come alive.

**Owner-withdrawn / deliberately excluded** (recorded so nothing is "discovered"
later): the digest stays **anonymous** — no emitter identity, no addressee (spatial +
kind suffices at roster 4; identity invites partner-keying that heterogeneous rosters
would break). No per-meow reward penalty. No lower turn cost (superseded by
ride-along). No range/falloff on the broadcast.

## Clarifications

### Session 2026-08-08

- Q: After a cat emits any non-Silent message, what does the cooldown mask? → A:
  **Per cat per message kind** — emitting a kind cools only that kind for that cat;
  other kinds stay available (subject to their own grounding/gating/cooldowns).
- Q: What do the dedicated cosleep dials default to at ship? → A:
  **Behavior-preserving 15/15** (drip = mutual = today's effective rate); the
  pre-freeze pilot prices them by config rollout.
- Q: Scripted groom-responder gate default (band 15–20)? → A: **15** (Experiments
  concurring with Product, and firmly): the rare-class lesson is this experiment's
  founding trauma — restraint can be dialed up after collection, a silent
  demonstrator cannot be dialed into existence afterward; over-response is safe by
  construction (welfare-positive trade, responder rule sits inside the scripted
  decision ladder so urgent needs still win); and since the shipped default is what
  re-baseline `B` is measured under, 15 is decided once, now, and kept through
  freeze — any post-v4 tightening lands in the next generation's config, never
  between re-baseline and freeze. Correction for the record: the measured occupancy
  figures are needs_driven cuddle ≥ 20 = 12.1% and ≥ 25 = 5.1%; at 15 the in-gate
  share sits higher (roughly high teens by interpolation).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Announcing without giving up the turn (Priority: P1)

Every cat decision — scripted or learned — becomes a pair: an activity and a message.
A cat mid-walk to the water bowl can say "I want a bath!" without stopping. Watching
the world, the owner sees cats that talk *while* they act; nothing about what cats do
changes, only what they say alongside it.

**Why this priority**: This is the mechanism the whole rework rides on. Zero marginal
cost is what un-kills the channel; everything else (grounding, digest, demonstrators)
assumes it.

**Independent Test**: Run a seeded world with only this story implemented (structural
masks, no grounding): every decision carries a message slot, activities are identical
to a pre-change world up to the declared meow-turn→Idle translation (former meow
turns become Idle turns; exact equality beyond that is transitional — US4 shifts
distributions by design), determinism holds per seed, and a message can
be emitted on the same tick as any activity.

**Acceptance Scenarios**:

1. **Given** a cat walking toward water, **When** it emits `WantBath` on the same
   tick, **Then** its movement and activity resolve exactly as they would have with
   no message.
2. **Given** the same seed and config, **When** the world runs twice to tick N,
   **Then** both runs produce identical world states *including* every message
   emitted.
3. **Given** a learned policy, **When** its decision is sampled, **Then** exactly one
   random value is consumed for the whole (activity, message) decision — the decision
   count per tick is unchanged from today and independent of world contents.
4. **Given** dedicated meow-turn actions existed in the old activity menu, **When**
   the new menu is constructed, **Then** those rows are gone (menu 40 → 34) and the
   message channel is the only way to meow.

---

### User Story 2 - Honest announcements: grounded legality and courtesy for everyone (Priority: P2)

A cat can only say "I want X" while it genuinely wants X — the engine certifies every
announcement against the cat's real need at emission time. And no cat can chatter:
after speaking, a cat is quiet for a spell (the same spell its meow stays audible).
"Meow whenever it's legal" *is* the honest broadcast; spam is structurally impossible
rather than discouraged.

**Why this priority**: Grounding converts cheap talk into certified state — it's what
makes the channel trustworthy enough for responders (scripted and learned) to act on.

**Independent Test**: Property-test the message mask over randomized worlds: want-kind
legality tracks the grounding need against the dials with hysteresis; a cooldown
follows every emission; `Silent` is legal in every reachable state.

**Acceptance Scenarios**:

1. **Given** a cat with Bath need below the announce threshold, **When** its message
   mask is built, **Then** `WantBath` is masked; **When** the need crosses the
   threshold, **Then** `WantBath` becomes legal.
2. **Given** a cat whose need has crossed the threshold and is drifting down, **When**
   the need sits between (threshold − hysteresis) and threshold, **Then** the kind
   remains legal; only below (threshold − hysteresis) does it re-mask.
3. **Given** a cat that just emitted a non-Silent message of some kind, **When**
   masks are built for the following ticks, **Then** that kind is masked for the
   cooldown window while other kinds remain governed by their own grounding, gating,
   and cooldowns — repeating the *same* announcement within the window is
   structurally impossible.
4. **Given** any combination of grounding, gating, and cooldown masking, **Then**
   `Silent` is legal — a legal message action always exists (the message-head
   analogue of FR-018's never-all-zero guarantee).
5. **Given** `Purr`, **Then** it remains gated by `purr_earned` exactly as today.

---

### User Story 3 - A digest a listener can act on (Priority: P3)

A cat hearing meows perceives, per message kind: how fresh the freshest audible meow
is, where that emitter is, and how badly the emitter needs what it announced — and all
three facts describe the **same cat**. Today's digest can mix two emitters (presence
from one, direction to another); after this story a responder always has one coherent
target.

**Why this priority**: The digest is the listener's whole view of the channel; an
incoherent triple poisons the credit a responder can assign. Coherence + intensity
ride the same schema bump as the head, per the wall-economics constraint.

**Independent Test**: Construct a world with two same-kind emitters at different
recencies/positions; assert the digest's recency, direction, and intensity all
describe the single freshest audible emitter.

**Acceptance Scenarios**:

1. **Given** two cats both emitting `WantBath`, one fresher and one nearer, **When**
   a third cat's digest is built, **Then** recency, direction, and intensity all
   describe the fresher emitter (self excluded, as today).
2. **Given** a want-kind emission at need value V, **Then** the digest's intensity
   for that kind reads V/100 as stamped at emission (grounded — it cannot lie).
3. **Given** a `Purr` or `FollowMe` entry, **Then** its intensity reads a constant 0
   (no grounding value exists; a constant is honest).
4. **Given** the full observation, **Then** the digest occupies 8 kinds × 4 values
   (recency, direction ×2, intensity) = 32 values, and carries no emitter identity
   and no addressee.

---

### User Story 4 - Demonstrators that use the channel (Priority: P4)

Scripted cats show the behavior learning needs to imitate: a wet cat announces
`WantBath`; a cat whose cuddle need is real hears it, walks over, and grooms — paid in
the currency it wanted. A sleepy cat with real cuddle need naps *next to a friend*
instead of defaulting to a sunbeam. The reciprocal trade the engine has always
implemented finally happens on screen, and dataset v4 contains it **by construction**.

**Why this priority**: Without demonstrators the new channel is as dead as the old one
— BC has nothing to clone and PPO must discover coordination from scratch. This story
is what makes classes 13–15 nonzero.

**Independent Test**: Run scripted-only seeded worlds: GroomKitty occurs; groom
responses trigger only on audible meows (never on privileged need reads); announcing
cats continue their errands; cosleep share of sleep decisions rises above the 5.6%
baseline.

**Acceptance Scenarios**:

1. **Given** a scripted cat whose Bath (or Sleep) need crosses the announce
   threshold, **When** it next decides, **Then** it emits the matching want-kind
   alongside its chosen activity — the activity is what it would have chosen anyway.
2. **Given** a scripted cat with real cuddle need (at/above the responder gate) that
   hears `WantBath`, **When** it decides, **Then** it walks to the emitter and grooms
   — and its decision is a function only of information a policy could also observe
   (the digest), never a direct read of the other cat's needs (imitability
   principle).
3. **Given** a scripted cat choosing to sleep whose cuddle need is real, **When** a
   friend is reachable, **Then** it prefers sleeping adjacent to the friend over a
   sunbeam; the companion's behavior needs no change and is never conscripted.
4. **Given** dataset v4 collected from these demonstrators, **Then** GroomKitty
   classes 13–15 and the new message labels are nonzero, and the activity-label
   distribution conditioned on message ≠ Silent matches the unconditioned
   distribution to first order (announcing cats are mid-errand, not idle).

---

### User Story 5 - Companionship priced by presence, not drive-by (Priority: P5)

Today one tick of adjacency next to a sleeper pays a full cuddle rate — companionship
is economically instantaneous, so "staying" is never worth learning. After this story,
a passive companion earns a drip (flooring a real need takes sustained presence), and
the full rate is reserved for **mutual** engagement — both cats resting/sleeping
adjacent, each by its own choice. That coordination payoff is exactly what gives the
meow channel something to arrange.

**Why this priority**: Settled owner decision (B + C), but the channel functions
without it; it manufactures the *reason* to communicate rather than the means.

**Independent Test**: Simulate a sleeper with (a) a passive adjacent companion and
(b) a mutually-sleeping companion; assert the drip rate vs the full rate, dedicated
dials, and no change to grooming payment or rest-duet rates.

**Acceptance Scenarios**:

1. **Given** a sleeping cat with a named adjacent companion who is doing something
   else, **Then** cuddle credit flows at the cosleep drip rate — and stops the tick
   the companion departs (existing guarantee preserved).
2. **Given** both cats sleeping/resting adjacent, each by its own choice, **Then**
   cuddle credit flows at the full mutual rate to both.
3. **Given** the cosleep dials at their shipped defaults, **Then** the cuddle economy
   is numerically identical to today's (defaults are behavior-preserving; the
   pre-freeze dial-pricing pilot retunes by config rollout, never by generation
   wall).
4. **Given** any cosleep dial change, **Then** grooming payment and rest-duet rates
   are unaffected (the shared-dial coupling is severed; `cuddle_relief` no longer
   feeds three flows).

---

### User Story 6 - A migration that fails loudly and a world that survives it (Priority: P6)

The operator updating a config or resuming a world gets exactly what the generation
wall promises and nothing worse: a config still carrying retired keys refuses to load
with a clear error naming the key; a pre-batch world snapshot loads and runs — the
wall is policy-side only, and nobody needs to throw away the soak clock.

**Why this priority**: Operational safety net around everything above; cheap to build,
expensive to lack.

**Independent Test**: Load a config containing each retired key → clear refusal
naming it. Load a committed pre-batch snapshot fixture → world resumes and ticks.

**Acceptance Scenarios**:

1. **Given** a config carrying `courtesy_ticks`, `urgent_courtesy_ticks`, or
   `urgent_need_threshold`, **When** it is loaded, **Then** loading fails with an
   error naming the offending key (the intended migration signal).
2. **Given** a world snapshot serialized by the pre-batch engine, **When** the new
   engine loads it, **Then** the world resumes and runs (new message kinds extend the
   enum; old snapshots contain only old variants).
3. **Given** a pre-batch policy artifact, **When** the new engine loads it, **Then**
   it refuses loudly with a schema-generation error (the wall working as designed —
   see Rollout Notes for the deploy gate this implies).
4. **Given** an eval run, **Then** its report includes the distress-tick counter
   (per kitty × need: ticks at/above the distress threshold, plus episode count) —
   reported, never gated.

---

### Edge Cases

- **Everything masked but Silent**: all want-kinds below threshold, Purr unearned,
  cooldown active → the mask must still offer `Silent` (structural, not incidental).
- **Need oscillating at the threshold**: hysteresis must prevent mask flicker;
  legality changes only at threshold (rising) and threshold − hysteresis (falling).
- **Emission on the same tick legality is lost**: legality is evaluated at mask time
  against the start-of-tick snapshot (Article V); intensity is stamped from the same
  snapshot — mask and stamp must agree.
- **Two same-kind emitters, one nearer / one fresher**: the digest triple must
  describe one cat (the freshest), never a blend.
- **Cooldown vs audibility window**: both default to the same dial
  (`recent_window_ticks`); retuning it moves both together — a deliberate coupling,
  documented at the dial.
- **Multiple simultaneous `WantBath` emitters, one responder**: the responder keys on
  its digest (which names one emitter); no oscillation between targets mid-walk.
- **Responder's target becomes ineligible mid-approach** (need relieved, emitter
  moved): existing scripted retargeting/fallback rules apply; no new failure mode.
- **Mutual-tier boundary**: sleeper + companion who is *resting* adjacent counts as
  mutual; a companion mid-walk-through does not; the tier is evaluated per tick, and
  a departed partner stops granting (existing test-pinned guarantee).
- **Old snapshot carrying per-kind cooldown bookkeeping** from the retired courtesy
  system: must deserialize into the new engine without error (state shape is
  compatible; retired *semantics* lived in config, which is where the migration
  fires).
- **Purr's `announce_probability`**: untouched and must continue to work unchanged
  alongside the new head.

## Requirements *(mandatory)*

### Functional Requirements

**Channel structure**

- **FR-001**: Every kitty decision — scripted and learned alike — MUST be a pair
  (activity, message), where message is `Silent` or one of exactly **8 kinds**: the
  six currently-learned kinds plus `WantBath` and `WantSleep`. Emitting a message
  MUST NOT displace, delay, or alter the paired activity (zero marginal cost).
- **FR-002**: `WaitForMe` MUST remain engine-reserved: not selectable in the message
  head, absent from the digest, and expressible only through the existing yield rule.
- **FR-003**: The dedicated meow-turn actions MUST be removed from the activity menu
  (40 → 34 rows); the message channel becomes the only way to meow.
- **FR-004**: Determinism (Article V): the (activity, message) decision MUST consume
  exactly one random value per kitty per tick — both components derived by splitting
  that single value, never by a second draw — so decision count remains independent
  of world contents and the trajectory is reproducible per seed, messages included.

**Legality (the message mask)**

- **FR-005**: A want-kind MUST be legal only while its grounding need is at/above
  `announce_threshold`, with hysteresis: once legal, it remains legal until the need
  falls below `announce_threshold − announce_hysteresis`. Grounding is evaluated
  against the start-of-tick snapshot.
- **FR-006**: `Purr` MUST retain its `purr_earned` gate; `FollowMe` has no grounding
  predicate and is governed by cooldown only.
- **FR-007**: After a non-Silent emission of a given kind, that kind MUST be masked
  for that cat for `recent_window_ticks` ticks (a **per-cat, per-kind** cooldown —
  clarified 2026-08-08). A cat therefore holds at most one live digest entry *per
  kind*; same-kind repetition within the window is structurally impossible. This
  cooldown applies to every emitter — scripted and learned — replacing the
  scripted-only courtesy system.
- **FR-008**: `Silent` MUST never be masked: in every reachable state a legal message
  action exists (the message-head analogue of FR-018's never-all-zero guarantee),
  and this MUST be a structural guarantee with a property test, not an emergent one.

**The digest**

- **FR-009**: The meow digest MUST cover the 8 head kinds with **4 values per kind**
  (recency, relative position ×2, intensity) = 32 observation values, and all four
  values for a kind MUST describe the same emitter: the freshest audible emitter of
  that kind, own meows excluded (fixing the presence-vs-nearest incoherence).
- **FR-010**: Intensity MUST be the grounding need /100 stamped at emission for
  want-kinds, and a constant 0 for `Purr` and `FollowMe`.
- **FR-011**: The digest MUST remain anonymous: no emitter identity, no addressee
  (deliberate, reasoned exclusion — not to be "discovered" later).
- **FR-012**: The observation, action, and mask schemas and the artifact generation
  MUST bump exactly once for this whole batch; artifacts of the previous generation
  MUST refuse to load with a clear schema-generation error.

**Configuration**

- **FR-013**: The `[meow]` config section MUST land as exactly three keys:
  `recent_window_ticks` (default 10, doubling as the mask cooldown),
  `announce_threshold` (default 30), `announce_hysteresis` (default 5) — all
  simulation constants as dials per Article VI, so retuning is a config rollout,
  never a generation wall. `[purr] announce_probability` is untouched.
- **FR-014**: The courtesy trio (`courtesy_ticks`, `urgent_courtesy_ticks`,
  `urgent_need_threshold`) MUST be retired; strict loading MUST reject a config
  carrying any of them with an error naming the key (the intended migration).
- **FR-015**: Cosleep cuddle credit MUST move to **dedicated dials** decoupled from
  `cuddle_relief` (which continues to price the groomer's payment and rest duets
  only): a passive-companion drip rate and a full mutual-tier rate. Shipped defaults
  MUST be behavior-preserving (numerically equal to today's effective rates) so this
  batch alone does not move the cuddle economy; the pre-freeze dial-pricing pilot
  retunes by config rollout.
- **FR-016**: The mutual tier pays the full rate when both cats are sleeping/resting
  adjacent, each by its own choice; a companion doing anything else earns the drip.
  Non-conscription (spec 021 doctrine) is preserved: the companion is never bound,
  and credit stops the tick adjacency ends.

**Scripted demonstrators**

- **FR-017**: Scripted behaviors MUST be two-channel deciders returning (activity,
  message); announcing never displaces the activity. (If a scripted meow still spent
  the turn, dataset v4 would pair announcements with do-nothing activities and BC
  would learn Idle-when-announcing — the imitability principle inverted at the
  source.)
- **FR-018**: Scripted cats MUST announce want-kinds when grounded-legal ("meow
  whenever legal" is the honest broadcast), subject to the same mask as everyone.
- **FR-019**: A scripted responder whose own Cuddle need is at/above the real-cuddle
  gate (ONE config dial shared with FR-020, default 15 — chosen inside the analysis
  band 15–20, NOT 30) and who hears `WantBath` MUST walk to the emitter and groom. The response MUST key
  on the audible meow only — a function of information a policy could observe —
  never on a privileged read of another cat's needs (imitability principle).
- **FR-020**: The scripted napper MUST prefer sleeping adjacent to a reachable friend
  over a sunbeam when its own Cuddle need is real (the same shared dial as FR-019);
  the companion's behavior is unchanged.
- **FR-021**: The dataset collector's registered acceptance check: in dataset v4 the
  activity-label distribution conditioned on message ≠ Silent MUST match the
  unconditioned distribution to first order. The spec carries the check; Experiments
  runs it the day collection finishes.

**Compatibility, observability, interfaces**

- **FR-022**: Pre-batch world snapshots MUST load and run on the new engine — the
  wall is policy-side only. A committed pre-batch snapshot fixture MUST be resumed by
  an automated test (so nobody reaches for `--fresh` out of caution and throws away
  the soak clock).
- **FR-023**: A distress-tick counter MUST ride the eval reporting: per run × kitty ×
  need, ticks at/above the distress threshold plus distress-episode count —
  **reported, never gated** this generation. Its counting semantics MUST be identical
  to the registered census definition (the one that retro-reproduced exp-003's
  committed evals 810/810, `exp-003-water-schema/results/distress-census-2026-08-08.md`).
- **FR-024**: The seam's proposal/decision types MUST grow the message component and
  stay public (Experiments absorbs the recompiles of `bc-collect`/`twin-probe`/census
  tools); the exporter contract is that `label_msg` derives from the message channel.
- **FR-025**: `GET /config` MUST expose the new dials (additive change); the client
  receives the two new kinds in `recent_meows` and on kitty cards the tick they first
  fire.

### Key Entities

- **Message**: what a cat says on a tick — one of 8 kinds or Silent; carries emitter
  position and, for want-kinds, the grounded intensity stamped at emission.
- **Decision pair**: the unit of choice — (activity, message) — produced by every
  decider from one random draw.
- **Message mask**: per-cat, per-tick legality over Silent + 8 kinds, built from
  grounding (need vs dials, with hysteresis), `purr_earned`, and per-kind
  post-emission cooldowns; Silent always legal.
- **Meow digest**: the listener's view — per kind, a coherent
  (recency, direction, intensity) description of the freshest audible emitter;
  anonymous; 32 observation values.
- **Meow dials**: `recent_window_ticks`, `announce_threshold`,
  `announce_hysteresis` — the entire `[meow]` section.
- **Cosleep dials**: passive drip rate + mutual full rate, dedicated (decoupled from
  `cuddle_relief`).
- **Distress-tick counter**: per run × kitty × need, ticks-at/above-threshold and
  episode count, in eval reports.
- **World snapshot**: unchanged in shape for compatibility purposes; pre-batch
  snapshots remain loadable.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a scripted-only world at default dials, cats announce while acting:
  the activity distribution conditioned on message ≠ Silent matches the unconditioned
  distribution to first order, and every one of the six needs is announceable.
- **SC-002**: GroomKitty happens: scripted-only runs at default dials produce nonzero
  cat-to-cat grooming (against a measured baseline of 0 in 800k kitty-ticks), and
  dataset v4 contains nonzero GroomKitty classes 13–15 and new message labels **by
  construction** — checkable the day collection finishes.
- **SC-003**: Cosleep share of sleep decisions rises above the 5.6% v3 baseline in
  scripted-only runs (the routing change working), while the cuddle economy at
  shipped dial defaults stays numerically identical to today's.
- **SC-004**: Determinism holds: same seed + config → byte-identical world state at
  tick N, messages included; decision count per tick is unchanged from today.
- **SC-005**: No cat can spam a kind: a repeated same-kind announcement within the
  cooldown window is structurally impossible, so a cat holds at most one live digest
  entry per kind at any time.
- **SC-006**: The operator experience of the wall is exactly as promised: a
  pre-batch world snapshot resumes and runs; a config with any retired key refuses
  to load naming the key; a pre-batch policy artifact refuses to load with a
  schema-generation error.
- **SC-007**: The distress-tick counter's numbers on a replay of the registered
  census definition's fixtures agree exactly with the committed census record.
- **SC-008**: All constitutional gates stay green: Articles I–III property suites,
  never-all-zero (activity) and never-masked-Silent (message), fairness, and the
  release-honest defaults gate — updated to the new stamp by design, with changelog
  markers `[obs-schema]`, `[rng-sequence]`, `[stamp]`.

## Rollout Notes *(process requirements, owner-visible)*

- **The stamp legitimately moves.** New dials in, courtesy trio out —
  `engine_defaults_sha256` changes by design. Follow the release-honest gate process
  (record the new stamp; changelog markers `[obs-schema]`, `[rng-sequence]`,
  `[stamp]`; deliberately **no** `[world-fresh]`), not regression triage.
- **Single re-baseline after merge** (§4 ordering): scripted-behavior changes move
  `B` and every seeded trajectory; the exp-002 family byte-stability check will flag
  it — expected and fine. Re-baseline before the exp-004 prereg freeze, never freeze
  first.
- **Deploy gate — the live box cannot take this binary immediately**: both live
  policy seats run a previous-generation artifact, which the new engine refuses (the
  wall working as designed). Deploy only after the seats are re-parked to scripted
  (spec 026's parked-seats pattern) or a same-generation artifact certifies;
  otherwise `update.sh` boot-fails into rollback. Merging to main is fine; deploying
  is gated. **No `--fresh` needed** when deploy does happen — the world's history
  survives.
- **Client thread dependency (queued, not this spec's code)**: the client's
  kind→rendering map is the *only* home of meow strings post-#142 and needs
  `want_bath`/`want_sleep` entries before rollout, or live meows render as unknowns.
  `GET /config` growth is additive; client readers are tolerant.

## Assumptions

- **Shared dials across kinds**: one `announce_threshold`/`announce_hysteresis` pair
  governs all want-kinds (the `[meow]` section is exactly three keys by settled
  decision; per-kind thresholds are a future dial split if ever needed).
- ~~Cosleep dial defaults~~ **CLARIFIED 2026-08-08: behavior-preserving 15/15**
  (drip = mutual = today's effective rate) so the batch alone doesn't move the
  cuddle economy; the agreed pre-freeze pilot prices them
  (drip ∈ {1,2,3,5,15} × mutual {off,on}) by config rollout.
- ~~Responder gate default~~ **CLARIFIED 2026-08-08: 15** (see Clarifications —
  Experiments concurring with Product). The band's permissive end (in-gate share
  roughly high teens; the measured 12.1% attaches to threshold 20), maximizing
  demonstrator GroomKitty traffic for dataset v4. A dial; kept through freeze, with
  any tightening deferred to the next generation's config.
- ~~Cooldown scope~~ **CLARIFIED 2026-08-08: per cat per message kind** (see
  Clarifications). Consequence accepted: a cat with several real needs can hold one
  live digest entry per kind simultaneously; the occlusion fix rests on the digest
  coherence FR (one emitter per kind) plus same-kind cooldown, not on a global
  silence.
- **The FromConfig type-level refactor** (017 close-out: "at next harness touch") is
  in scope *if cheap* during planning, skipped if not — a flag, not a requirement.
- **Shaping (A1), γ pinning, and all prereg-registered values** are Experiments'
  side of the interface: config-only, no engine work in this batch.
- **Dataset v4 collection, BC v4, re-baseline runs** are Experiments' work on the
  new engine; this spec delivers the engine, seam, and registered acceptance checks
  they need.
