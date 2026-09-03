# Feature Specification: Fog Gen 1 — the 3.0 observation wall

**Feature Branch**: `049-fog-gen1`

**Created**: 2026-09-02

**Status**: Draft

**Input**: Owner kickoff 2026-09-02 (Product session). The feature description is the step-3 in/out doc — the "Step 3" section of `experiments/fog-gen1-timeline-2026-08-26.md` at main `8423060`, every member owner-ruled and the doc closed COMPLETE 2026-09-02 — plus the "Meow law under fog — owner ruled 2026-09-02" package in the same doc's Step 4 section (main `027563d`) and its "Coverage pass 2026-09-02" follow-ups (main `26504ac`), both relayed by Experiments and verified against the doc. This spec opens on those lists and argues none of them; where a ruling left a sub-decision open, it is either taken here with its reason on record (Assumptions) or put to the owner (Clarifications). Nothing enters that did not appear in that doc first.

## Problem

CloudKitty's cats see the whole meadow. Every kitty and every element is in every observation, so the meow channel is welfare-redundant under global vision (F-026 — the measured baseline this generation exists to overturn), and nothing about the world creates a reason to *tell* anyone where the food is. Fog Gen 1 narrows what a cat can see to a disc around it, keeps hearing global, and gives each cat a crude one-slot-per-kind memory of where it last saw each element kind, so the welfare cap it measures is "fog" and not "fog plus amnesia".

The wall is also the one moment the observation schema moves cheaply, so the owner-ruled pre-fog bundle rides it: a fourth kitty row so friends have permanent by-id rows instead of contended nearest-three slots; the meow digest moves from one global "freshest emitter per kind" block onto the kitty rows as per-speaker (recency, rate) pairs, so repetition and *who* is insisting become fields a memoryless mind can read; a scene-age float and a neighbour-in-water bit widen the rows; and 3.0 config hygiene deletes every pre-3.0 compatibility shim, because the 3.0 cutover is `--fresh` and no old world or artifact crosses it.

Fog also makes the words load-bearing. Under global vision the want-words are redundant (the speaker's needs are already in its row); under fog a want is legal only when the speaker cannot see or remember relief, so the word carries what no row does. Every here-word carries an engine-stamped reply flag, so "I answered you" is a fact a listener can read, and the scripted seats answer audible wants (the corpus contributors' half); the persistent-heading exploration a blind scripted cat falls back to is the same package.

This is the schema-5 wall (the code's `OBSERVATION_SCHEMA_VERSION` is 4 today, spec 033; the roadmap's "schema-4 wall" phrase predates that bump). Existing policy artifacts refuse to load on the far side by design; the Gen 1 roster is trained on the far side.

## Clarifications

### Session 2026-09-02 — owner rulings

Two sub-decisions the step-3 doc did not settle and that change the feature's meaning, not its plumbing. Both are ruled; no markers remain.

- **Q1 — does hearing carry direction? → RULED 2026-09-02: A, yes; RE-RULED the same day (coverage pass, timeline @ 26504ac): the position is the speaker's position at its LAST AUDIBLE MEOW, not live.** Live dx/dy (A as first ruled) leaked a moving cat's position for the whole window. Every `Meow` record now carries an engine-stamped `pos`; a heard-but-unseen row reads dx/dy/distance to that stamped position, and the digest recency says how stale it is. Not a memory slot ("no cat memory in Gen 1" stands) — a reduction over the recent-meow buffer. Knowledge fields (needs, happiness, activity, partner flag, target bit, water bit, scene age) stay masked. Encoded in FR-012; the step-3 doc's literal "position masked" wording is superseded. Background, kept for the record: the step-3 doc lists an unseen-but-heard friend's *position* among the masked fields. The schema-4 digest a policy reads today carries the emitter's live dx/dy for every audible kind (docs/encodings.md, spec 033 FR-005), and the scripted groom response walks to the WantBath emitter it hears (spec 028 FR-019, "everything this rung reads, a policy could observe"). If the position is masked, a `here_food` call from a cat outside the disc says "someone, somewhere, is at food" — no direction to walk in — and the grounded-reference comparison Gen 1 is built to run (F-026's overturn condition) has no gradient from unseen speakers; the groom response also loses its imitable target. See FR-012.
- **Q2 — what does a scripted cat do when the thing it needs is neither visible nor remembered? → RULED 2026-09-02 (timeline @ 027563d, ruling 4): explore with a persistent heading**, one cat-state field, redraw only when the wall ahead is within the radius — NOT the existing memoryless `wander` (√t coverage, a long first-sight tail against a 0.4/tick need, so the safeguard would rescue most blind cats and the corpus would read "call, mill about, get rescued"; a held heading sweeps an 11-tile column per step at r = 5, first sight in ~10 ticks, tail bounded by one crossing). Encoded in FR-023. The same sitting ruled the meow-law package (want law, reply bit, scripted reply) — FR-036 to FR-046. Background: today `seek_element` idles when no element of the kind exists ("the safeguard will provide one by the next environment phase"). Under fog "none visible" no longer means "none exists", so idling would starve a hungry cat that cannot see a bowl — a welfare bug in the anchors the Gen 1 cap is benchmarked against. See FR-023.
  **Experiments' input on record (2026-09-02, relayed at the owner's request; input only — the owner's ruling above supersedes it where they differ, notably by taking the persistent heading now rather than as a shakeout escalation):** recommended **A** for the anchors in the cap run and in every corpus collection, **B** rejected, **C** at most a default-off knob and only if the step-5 prereg commits to the screen below. Reasons: (1) C would be the first in-tree `here_*` listener — the 043 arc landed with "gate zero in-tree = no here-listener" as a standing guard, so C needs an explicit owner lift of that guard, not a spec FR. (2) C contaminates the registered comparison: lineage clones BC on the scripted seats' action corpus, so scripted listeners would teach "hear `here_water` → walk to speaker" by construction and the generation's question (is grounded reference learned and *used* under fog) would measure the teacher's design, not the channel — F-026's failure class from the other side; under A the corpus carries the speaker's half only, which is what F-034 measured and what the step-5 here-bar is calibrated on. (3) The cap under A is the honest fog tax: blind search is what a memoryless fogged mind faces; the Article I safeguard still spawns chow beside a distressed cat, so A surfaces the fog cost as distress / safeguard-spawn rate rather than starvation, which is what the cap should contain; A fires only when the kind is neither visible nor remembered, so with refuted-on-sight memory it is mostly an early-life and post-refutation state. (4) "Nor remembered" must mean the same engine-side memory the policy observes, not a private scripted memory (already FR-021/FR-022). (5) Ship the existing seeded `wander`; if the step-5 shakeout shows an unacceptable safeguard-spawn rate under A, a persistent-heading wander (one state field) is the next lever — a measured escalation, not a design guess. (6) The prereg would rather have the cap measured under A as the fixed reference and the here-word question asked on the policy side (vocabulary on/off or ablated); C's one legitimate use is a secondary screen (scripted-listener welfare minus scripted-wanderer welfare = the ceiling on what listening is worth at the `announce_here` density), worth building only if the prereg commits to running it.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A cat sees only its surroundings, and remembers where things were (Priority: P1)

A policy cat (or a scripted cat — same fog for everyone) observes the kitties and elements inside a disc of radius r around it: an entity at offset (dx, dy) is visible exactly when dx² + dy² ≤ r² in integer arithmetic. Everything outside the disc is absent from its view. When a bowl it saw drifts out of view, the cat still knows where it last saw chow — one remembered tile per element kind, with how stale that memory is — and that memory is corrected the moment the cat can see the tile again (refuted on sight). Hearing is unchanged: every meow in the world is audible.

**Why this priority**: This is the generation. Without the disc there is no information gradient and nothing else in the bundle has a reason to exist; without the memory the cap measures amnesia.

**Independent Test**: Build random worlds, encode every kitty's observation at several radii, and check that the set of entities present in the view is exactly the Euclidean disc; run a kitty past a bowl and out of range and read its memory row (present, offset, staleness) tick by tick; remove the bowl while the cat is out of range and walk it back — the memory clears on the first tick the tile is in view.

**Acceptance Scenarios**:

1. **Given** a friend at offset (3, 4) and r = 5, **When** the observing cat's view is encoded, **Then** the friend's row is fully populated (9 + 16 = 25 ≤ 25 — on the disc's edge counts as seen).
2. **Given** a friend at offset (5, 1) and r = 5, **When** the view is encoded, **Then** the friend is not seen (26 > 25) although it is six Manhattan steps away, while a friend at (3, 4), seven steps away, is.
3. **Given** a cat that saw a chow bowl at tile T and has since walked out of range, **When** its view is encoded, **Then** the chow memory row reads present = 1, offset = T − own position, staleness = (ticks since last seen) / 40 clamped to 1.
4. **Given** that remembered bowl was eaten away while the cat was out of range, **When** tile T re-enters the cat's disc, **Then** the chow memory row is all zero on that tick.
5. **Given** two chow bowls visible at once, **When** the memory updates, **Then** the remembered one is the nearer (Manhattan; ties to the lower element id) — the slot-fill rule, not a new rule.
6. **Given** r large enough to cover the whole world, **When** the view is encoded, **Then** every entity is seen and every memory row mirrors a visible element — global vision is a radius setting, not a code path.
7. **Given** any radius, **When** a cat's own tile holds water, **Then** its own in-water bit is set — own-tile facts are never fogged.

---

### User Story 2 - Every friend has a permanent row, and fog masks fields, not friends (Priority: P1)

With a roster of five, each cat's view carries four kitty rows, one per friend, ordered by kitty id and never re-sorted. A friend inside the disc fills its row completely. A friend outside the disc who has spoken within the digest window keeps its message block live (and, pending Q1, its direction) while its knowledge fields read zero. A friend outside the disc who has been silent is an all-zero row. `PlayKitty(slot)` therefore names the same cat every tick.

**Why this priority**: The digest moves onto the rows (US3) only if rows are stable; under nearest-three fill a fourth cat speaking at the edge of vision would either be inaudible or displace a near friend on every call.

**Independent Test**: Encode observations for a five-cat world across a walk that moves friends in and out of the disc and has them call; assert each friend's row index never changes, and that the per-row mask state (seen / heard / silent) matches the entity's true state tick by tick.

**Acceptance Scenarios**:

1. **Given** friends with ids 2, 3, 4, 5 observed by id 1, **When** any observation is encoded, **Then** row k holds friend k + 1's fields — whatever their distances.
2. **Given** friend 4 walks out of the disc and back, **When** the view is encoded on each tick, **Then** its row index is unchanged and its `present` bit reads 1 exactly on the ticks it is inside the disc.
3. **Given** friend 3 is outside the disc and called `here_water` 12 ticks ago (window 30) from tile T, **When** the view is encoded, **Then** row 2's `here_water` recency reads 1 − 12/30 = 0.6, its dx/dy/distance point at T (where it was when it called, however far it has walked since), its knowledge fields read zero, and `present` reads 0.
4. **Given** friend 5 is outside the disc and has not called within the window, **When** the view is encoded, **Then** row 4 is all zero.
5. **Given** a lab roster of three, **When** the world starts with the served slot count (4), **Then** the surplus row is permanently vacant (all zero) and nothing else changes.
6. **Given** a roster of six with the served slot count, **When** the world starts, **Then** startup is refused with an error naming the slot count and the roster (a friend without a row cannot exist under permanent rows; the ruling re-raises the count explicitly at a roster change).

---

### User Story 3 - Repetition and insistence are fields (Priority: P1)

Each kitty row carries, per speakable kind, that friend's recency (how fresh its last call of that kind is) and rate (how many calls of that kind it made in the window, as a fraction of the most it could have made under the cooldown). The observer carries the same pair for its own calls. The global "freshest emitter per kind" digest is gone. Five `here_water` calls and one no longer produce the same observation; a second simultaneous speaker of a kind is no longer inaudible; a memoryless mind can tell "I already asked" from "I have not".

**Why this priority**: Owner-ruled bundle member; the fog era raises the digest's load three ways (global hearing, roster five, knowledge dropping from global to seen), and the minds are memoryless, so if repetition is not a field it does not exist.

**Independent Test**: Script two speakers calling the same kind at different cadences and read the (recency, rate) cells per speaker and per kind over the window; read the observer's own block after it speaks.

**Acceptance Scenarios**:

1. **Given** friend A called `want_play` at ticks t − 25, t − 15, t − 5 (cooldown 10, window 30), **When** the view is encoded at t, **Then** A's `want_play` cell reads recency 1 − 5/30, rate 3/3 = 1.0.
2. **Given** friend B called `want_play` once at t − 5, **When** the view is encoded at t, **Then** B's cell reads recency 1 − 5/30, rate 1/3 — distinguishable from A's.
3. **Given** the observer itself called `here_food` at t − 2, **When** its view is encoded, **Then** its own `here_food` cell (self block) reads recency 1 − 2/30, rate 1/3, and no other row reflects that call.
4. **Given** a call older than the window, **When** the view is encoded, **Then** it contributes to neither field.
5. **Given** a reserve kind (trill, ekekek) in a world where it is not armed, **When** any view is encoded, **Then** its cells are zero in every row — the kind layout is frozen at 15; only the digest's shape moved.
6. **Given** friend A's last `want_eat` was stamped at need 62, **When** the view is encoded inside the window, **Then** A's `want_eat` intensity cell reads 0.62 whether or not A is visible; outside the window it reads 0. Here-kinds and the free register carry no intensity cell.

---

### User Story 4 - Scene age and a wet neighbour are visible facts (Priority: P2)

A cat mid-scene knows how long its scene has run (elapsed / 24, clamped to 1; zero outside a scene). For every *seen* friend it reads the same float for the friend's scene, and a bit saying whether the friend is standing in water. Unseen friends carry neither (knowledge fields).

**Why this priority**: Owner-ruled bundle members; both widen the kitty row, and rows widen once. The water bit is priced at zero in Gen 1 (contagion shelved) and is expected to be ignored by the trained mind — that is on record as expected, not a defect.

**Independent Test**: Stage a duet and read both partners' own and mutual scene-age floats over 30 ticks; stand a visible friend in a pond and read the bit; move the friend out of the disc and read zero.

**Acceptance Scenarios**:

1. **Given** a cat 12 ticks into a scene, **When** its view is encoded, **Then** its own scene age reads 0.5; at 30 ticks it reads 1.0; the tick after the scene ends it reads 0.
2. **Given** a seen friend 6 ticks into its scene, **When** the view is encoded, **Then** that friend's row carries 0.25 in its scene-age field.
3. **Given** a seen friend standing on a water tile, **When** the view is encoded, **Then** its row's water bit reads 1; the same friend outside the disc reads 0 there whatever its tile.
4. **Given** any repricing of sleep or the durations table, **When** the view is encoded, **Then** the scene-age normaliser is still 24 — it is a frozen constant, never derived from config at observation time.

---

### User Story 5 - Scripted cats live under the same fog (Priority: P1)

The built-in behaviours (`needs_driven`, `playful`, and the clone-corpus seats with `announce_here` armed) decide from the same information a policy in the same seat would observe: visible cats and elements, their own memory, global hearing. A scripted cat cannot walk to a bowl it cannot see and has never seen; it picks playmates among the cats it can see; it answers a bath ask it can hear. The engine enforces this by construction — the decision context it hands a behaviour holds nothing outside the fog — so no behaviour can reach past the disc by accident.

**Why this priority**: Owner-ruled 2026-09-02. The Gen 1 welfare cap is benchmarked against the scripted anchors on the same fog config (difficulty cancels only if they share it), and the `announce_here = 1` corpus must come from speakers whose "here" means what the listener's does.

**Independent Test**: Run the served roster all-scripted at r = 5 and at a world-covering r; assert no decision ever references an entity outside the deciding cat's disc-plus-memory-plus-hearing set (an instrumented context that records every read); confirm the world-covering run reproduces today's decisions byte for byte.

**Acceptance Scenarios**:

1. **Given** a hungry `needs_driven` cat with a bowl outside its disc and no chow memory, **When** it decides, **Then** it takes one step along its exploration heading (FR-023), references no element it cannot see, and its `want_eat` rides along if legal (FR-036).
2. **Given** the same cat remembers a bowl at tile T, **When** it decides, **Then** it walks toward T as if T held the bowl; when T comes inside its disc and holds no bowl, the memory clears and the cat drops into exploration (FR-023) on the same ladder that tick.
2b. **Given** a `needs_driven` cat with real cuddle need and a friend outside its disc who meowed inside the window from tile U, **When** it decides, **Then** the friend at U is a legal target and the cat walks toward U; on arrival with the friend not visible, the target is dropped that tick.
2c. **Given** a `WantBath` caller outside the listener's disc, **When** the groom response fires, **Then** it walks toward the caller's last-meow position (spec 028 FR-019 survives same-fog).
3. **Given** a `playful` cat with a friend outside its disc and a critter inside it, **When** it picks a playmate, **Then** only the critter is a candidate.
4. **Given** a world-covering radius, **When** the served roster runs all-scripted for 20,000 ticks, **Then** every *action* matches the pre-fog engine's at the same seed and config (fog at infinite radius is the pre-fog world), and the message stream differs only where the want law (FR-036) silences a want that was legal under the old armed-only law.
6. **Given** a blind cat exploring east on a 20-wide world at r = 5 from x = 14, **When** it decides, **Then** it redraws (the wall ahead is within 5) among north and south only (east is wall-within-radius, west is the reverse), takes that step, and holds the new heading on the following ticks.
5. **Given** a partner in a duet, **When** either partner decides, **Then** the partner is visible (adjacent means inside every r ≥ 1) — no scene can be running with an unseen partner.

---

### User Story 6 - A 3.0 config is complete, and nothing pre-3.0 crosses the wall (Priority: P2)

Every configuration the 3.0 engine loads states every section explicitly; a missing section is a startup error naming it, exactly as an unknown key already is. The seven retired keys that 2.x parsed only to reject are no longer known at all. Saved worlds and policy artifacts from the 2.x line are refused (the cutover is `--fresh`). The frozen `evals/v1` exams are a 2.x record; Gen 1 certification reads `evals/v2`, the same six designs written as complete 3.0 configs.

**Why this priority**: Owner-ruled 2026-08-26 and itemised 2026-09-02. A config surface strict in both directions is the safety property wanted before a five-seat training round; the shims exist only to load worlds that will never load again.

**Independent Test**: Feed the loader a config missing each formerly-optional section in turn and assert the named rejection; run the two config sweeps and the nan table; boot the served binary against a schema-4 artifact and assert the pin rejection names the schema.

**Acceptance Scenarios**:

1. **Given** `cloudkitty.toml` without a `[water]` section, **When** the engine loads it, **Then** it refuses, naming `water`.
2. **Given** a config carrying `[meow] courtesy_ticks`, **When** it is loaded, **Then** it is refused as an unknown key (the migration note carries the seven maps; the engine carries nothing).
3. **Given** every config the tooling loads at this HEAD (served, training, cert, collect, lab families, `binding_continuity` fixtures), **When** the sweeps run, **Then** each parses complete or is listed in the exclusions file with the reason.
4. **Given** the `[elements.<kind>] max` key, **When** the config is loaded, **Then** it is accepted as before — kept by ruling, its comment corrected to say what it feeds (density ceiling and the critic's chow scale).
5. **Given** a schema-4 policy artifact, **When** the 3.0 server starts with it, **Then** startup fails naming the observation schema and the found-versus-expected versions, before any tick.

---

### User Story 7 - A want means "I can't see it"; a here can answer (Priority: P1)

A cat may speak a want-word only when the need is armed, it is the cat's top need, and the cat has no visible or remembered relief for it — so under fog a `want_eat` says "I am hungry and I do not know where food is", which no row carries. Every here-word the engine records carries a reply flag: set when a matching want from another cat was audible and the speaker could see the referent, clear for today's adjacency-law heres. A listener reads, per friend and per here-kind, whether that friend's latest here answered *its* want.

**Why this priority**: Owner-ruled 2026-09-02. The generation's registered question is whether grounded reference gets learned and used under fog; F-026 wrote the want-half off under global vision because the words were redundant, and the knowledge gate is what makes them informative again. Action and speech are independent channels (spec 028), so none of this costs a turn.

**Independent Test**: Stage a cat with a bowl inside its disc, then outside it with no memory, then remembered; read `want_eat` legality in each state. Stage speaker/listener pairs and read the reply stamp and the answers-me bit tick by tick.

**Acceptance Scenarios**:

1. **Given** a cat whose eat need is armed and its top need, with a bowl inside its disc, **When** legality is evaluated, **Then** `want_eat` is illegal (relief is visible).
2. **Given** the same cat with no chow visible or remembered, **When** legality is evaluated, **Then** `want_eat` is legal; once it remembers a bowl, illegal again.
3. **Given** a cat whose top need is sleep but whose eat need is also armed, **When** legality is evaluated, **Then** `want_eat` is illegal and `want_sleep` is legal (top need only; `NeedKind::ALL` order breaks exact ties).
4. **Given** friend B said `want_drink` at tick t and cat A can see a pond (not adjacent) at tick t + 1, **When** A says `here_water`, **Then** the word is legal (widened law) and stamped reply = 1; at tick t + 2 B's row for A carries answers-me = 1 for `here_water`.
5. **Given** cat A adjacent to a pond with no `want_drink` audible, **When** A says `here_water`, **Then** it is legal (adjacency law) and stamped reply = 0; no friend's answers-me bit is set.
6. **Given** a `want_drink` from B at tick t, **When** any cat evaluates at tick t, **Then** no here at tick t can be a reply (everyone decides against the start-of-tick snapshot); want → here → heard is three ticks at best.
7. **Given** a cat whose play need is top and armed with a critter visible (or remembered) but no available friend in view or heard at a known position, **When** legality is evaluated, **Then** `want_play` is illegal — a known critter is known play relief (owner ruled 2026-09-03).
8. **Given** the same cat with a friend outside its disc who meowed inside the window, **When** legality is evaluated, **Then** `want_play` is illegal — a friend heard at a known position is known relief (the broadcast position is the invitation).

---

### User Story 8 - Scripted seats answer the wants they hear (Priority: P2)

A scripted cat that hears a want it can answer — it can see the matching referent and its here-kind cooldown is clear — replies with the matching here-word, provided the caller's stamped urgency reaches the listener floor. It answers the most urgent caller; its own action is untouched; and when it has a want of its own that turn, the more urgent of the two speaks and the other waits at most one tick.

**Why this priority**: Owner-ruled 2026-09-02. The scripted seats are the corpus contributors; policies learn their own listening. The standing no-here-listener guard (043) is untouched: the trigger is *want*-listening (the groom-response precedent), and no scripted cat ever acts on a here.

**Independent Test**: Stage callers with different stamped intensities and a listener with the floor set; read the reply choice, the ladder resolution against its own want, and byte-identity of the launch state with the floor unset.

**Acceptance Scenarios**:

1. **Given** `reply_intensity_floor` unset, **When** the served roster runs, **Then** the message stream is byte-identical to the no-reply engine (launch state, the 043 pattern).
2. **Given** floor 0.30, friend B's `want_eat` stamped 0.45 audible, and a bowl visible to A (cooldown clear), **When** A decides, **Then** A's message is `here_food` and its action is whatever the ladder chose regardless.
3. **Given** two audible wants, B's `want_eat` at 0.45 and C's `want_drink` at 0.60, both answerable, **When** A decides, **Then** A answers C (`here_water`); equal intensities go to the fresher call, then the lower id.
4. **Given** an answerable want at 0.45 and A's own legal want with raw need 50, **When** A decides, **Then** A speaks its own want (50 > 45); at raw need 45 it replies (ties reply); the loser is delayed one tick at most.
5. **Given** an answerable want and A's yield rule firing, **When** A decides, **Then** `wait_for_me` wins (WaitForMe > {reply, own want} > ambient here > Silent).
6. **Given** an answerable `want_eat` but A's `here_food` cooldown not clear, **When** A decides, **Then** no reply is spoken that tick (cooldowns are never bypassed).
7. **Given** an audible `want_cuddle` or `want_bath`, **When** any scripted cat decides, **Then** no reply exists for it (no here-word pairs with cuddle or bath).
8. **Given** `announce_here` armed and a want audible on A's phase tick with the referent visible, **When** A's ambient here lands, **Then** it is stamped reply = 1 (stamp and trigger are separate; the step-5 ambient arm expects a small non-zero reply count for this reason).
9. **Given** a scripted caller that receives a reply, **When** it next decides, **Then** it does nothing with it — it keeps exploring; replies feed policies and instruments only.

---

### Edge Cases

- **Radius validation**: r ≥ 2 is required — adjacency must be visible (partner play is legal only at Manhattan ≤ 1 and the never-all-zero mask keys on it) and the spec-012 yield rule needs its Manhattan-2 friend visible, which any r ≥ 2 gives. r < 2 is rejected at load naming the key. A radius covering the whole world is legal and is the no-fog control.
- **On the disc's edge**: dx² + dy² = r² is seen. Integer arithmetic only; no float compare.
- **Own tile**: always seen (0 ≤ r²); the own-tile water bit, the sunbeam-occupied bit and the "take what is here" rung are unaffected by fog.
- **Memory of a kind never seen**: all zero. Memory of a kind seen this tick: the nearest visible element of the kind, staleness 0 — the memory row is "last known", which while seeing is "now".
- **Memory of a moved critter**: the remembered tile stays until the tile re-enters the disc (clears if empty of that kind) or another critter of the kind is seen (overwrites). No timeout at the default; the `memory_timeout_ticks` knob (0 = off) is the only expiry.
- **Water**: permanent in every served world; the water memory therefore never clears in practice, only overwrites with a nearer pond.
- **Same-tick order**: memory is part of the frozen start-of-tick snapshot every decision reads; the engine updates each cat's memory during the environment phase from the resolved world, after actions apply and before invariants assert, so the next tick's snapshot is complete. A cat's own move this tick is reflected in its dx/dy next tick, like every other position.
- **Heard row whose window expires**: the row becomes silent (all zero) on the first tick no call of any kind is inside the window.
- **Digest window vs cooldown**: the window must be a positive integer multiple of the per-kind cooldown so the rate's maximum is exact (3 at 30/10); any other pair is rejected at load naming both keys.
- **Lab rosters below five**: surplus rows are permanently vacant; the slot config is not changed per lab.
- **Rosters above the slot count + 1**: refused at startup (US2 scenario 6).
- **Target-priority displacement (R1)**: unreachable once every friend has a row; the code stays, inert, by ruling.
- **The critic's global state**: unfogged and unchanged (privileged, training-only view; `GLOBAL_STATE_SCHEMA_VERSION` stays 1). Decentralised execution is enforced by API shape as before.
- **Snapshot save/restore**: memory is kitty state and round-trips; the world API's kitty listing gains it additively (no existing field changes; the client reads nothing new in Gen 1).
- **"Stocked" is struck** (coverage pass): a bowl at zero servings expires in the same tick's environment phase, so no snapshot holds an empty bowl; chow memory is presence only, refuted when gone; remembered servings are OUT for Gen 1 (a fifth memory field is layout, Gen 2). Only emission-time enforcement (live elements mid-tick) can meet an empty bowl, and the existing adjacent-stocked rule already handles that.
- **Safeguard under fog**: stays existence-based (Article I: a resource must exist and be reachable; not "be visible"). No fog-aware rescue — finding is the cat's job, and a rescue would teach policies that starving makes food appear. A distress-only fog-aware form stays a possible later knob, not built here. Anchor distress at the pinned radius is a radius finding.
- **Radius-edge flicker on the want gate**: accepted, no hysteresis — a bowl flickering at the disc's edge toggles the gate only on its first sighting; after that the memory holds it and the 10-tick cooldown bounds emission.
- **Heard-friend arrival**: a scripted cat that reaches a heard-unseen friend's last-meow position and does not see the friend drops the target that tick (a fresh decision follows). A heard position is never walked to twice without a new meow — the position is the meow's, not the cat's.
- **Want law at a world-covering radius**: relief is always visible when it exists, so want-words go silent in a world that always has chow and water — the ruled consequence, not a defect (the word means "I cannot see it").
- **`want_drink` after first sight of water**: water is permanent and its memory never clears, so a cat that has ever seen a pond never says `want_drink` again. Ruled consequence.
- **Exploration RNG**: draws happen only on a redraw (initial heading, or wall-ahead-within-radius), never per step — state-dependent count, config-independent. At a world-covering radius with the served element minimums, exploration never triggers, so the action stream stays identical to the pre-fog engine (FR-024).
- **Exploration on a narrow world**: if no direction is both non-reverse and clear of the wall, any non-reverse direction; if none, the current heading. The initial draw (no heading yet) has no reverse to exclude.
- **Exploration step blocked**: the step along the heading uses the existing step rule (occupied-tile and water-avoiding sidestep); a sidestep moves the cat, not the heading.
- **Reply latency**: a same-tick reply is impossible (start-of-tick snapshot); the floor is one tick, and id order never matters.
- **Stale intensity in the ladder**: a stamped intensity can be up to a cooldown (10 ticks) old, which slightly favours the own want in close calls. Accepted on the record.
- **Spec 035 expansion tool**: no expansion map across this wall; the tool's source generation stays pinned where it is and it refuses schema-5 targets. Gen 1 minds train on the far side (lineage BC per the bootstrap doctrine).

## Requirements *(mandatory)*

### Functional Requirements

**Vision**

- **FR-001**: An entity (kitty or element) at integer offset (dx, dy) from a cat is *visible* to that cat exactly when dx² + dy² ≤ r², where r is the configured vision radius. The check is integer arithmetic. Visibility is the same rule for policies and scripted behaviours.
- **FR-002**: The vision radius is a configuration key in the core (world-law) configuration, `[vision] radius`, shipped with placeholder default 5; the observation layout MUST NOT depend on its value (radius-invariant layout). The step-5 prereg screens the value; this spec does not.
- **FR-003**: Hearing is global: every meow in the world is audible to every cat regardless of distance, as today.
- **FR-004**: Element slots (chow, water, sunbeam, critter) fill nearest-K over *visible* elements only, by the existing (Manhattan distance, id) rule. The observation's distance fields stay Manhattan (they mean travel).
- **FR-005**: A cat's own block is never fogged: own tile facts, own scene age, own message block, own memory.

**Memory**

- **FR-006**: Each cat carries engine-side memory of the last-seen tile per element kind — one slot per kind in `ElementType::ALL` order (water, chow, bug, greeble, sunbeam) — holding the tile and the tick it was last seen. Cats are never remembered (no cat memory in Gen 1).
- **FR-007**: Memory updates once per tick, per cat, per kind, from the resolved world (chow memory is presence only — an empty bowl never appears in a snapshot): if any element of the kind is visible, the slot becomes the nearest visible one (Manhattan, ties to the lower id) at this tick (most-recent-wins, sighting elsewhere overwrites); else if the remembered tile is inside the disc and holds no element of the kind, the slot clears (refuted on sight); else the slot is unchanged.
- **FR-008**: Memory has no expiry by default. A `[vision] memory_timeout_ticks` key exists (default 0 = never); a positive value clears a slot whose age exceeds it. Nothing else expires memory.
- **FR-009**: The self block carries, per kind, four floats: present (0/1), dx and dy of the remembered tile relative to the cat's *current* position (/width, /height), and staleness = (tick − last seen) / 40 clamped to 1. The normaliser 40 is a frozen constant (the served 20×20 world's width + height, the observation's own distance scale) — never derived from config at observation time (the scene-age rule).
- **FR-010**: Memory is part of the cat's saved state: it survives a snapshot save/restore, it is deterministic under Article V, and its exposure on the world API is additive only.

**Kitty rows**

- **FR-011**: `[rl.observation] kitty_slots` = roster − 1, pinned at 4 for Gen 1 (served default 4). Each friend owns one permanent row; rows are ordered by kitty id ascending and never re-sorted. Startup refuses a roster larger than kitty_slots + 1, naming both numbers. Smaller rosters leave surplus rows permanently vacant.
- **FR-012**: A row's contents depend on the friend's state for the observer this tick: **seen** (inside the disc) → every field; **heard** (outside the disc, at least one call of any kind inside the digest window) → the message block live, knowledge fields (needs, happiness, activity one-hot, partner flag, target bit, water bit, scene age) zero, `present` = 0, and the row's dx/dy/distance pointing at the friend's **position at its last audible meow** (owner ruled 2026-09-02, Q1 = A re-ruled stale-at-meow in the coverage pass: sound has direction, but the position it gives is where the call came from, not where the cat is now; the message block's recency says how old it is); **silent** (outside the disc, no call in the window) → all zero.
- **FR-013**: `present` means seen this tick. Audibility is evidenced by the message block itself.
- **FR-014**: Each row gains four things: neighbour-in-water bit (tile-derived, as the own-tile bit is), scene age (the friend's elapsed / 24 clamped, 0 outside a scene), the 36-float message block (FR-016: recency + rate for all 15 kinds, plus last stamped intensity for the six want-kinds), and four answers-me bits, one per here-kind in `HERE_KINDS` order: 1 if that friend's freshest here of the kind inside the digest window was emitted *after* the observer's own matching want inside the window (FR-041). The answers-me bits are part of the message block for masking purposes (live on heard rows).
- **FR-015**: The R1 target-priority displacement stays in the code, inert (owner ruling: keep, do not delete).

**Digest**

- **FR-016**: The global 15 × 4 digest is deleted. In its place every kitty row carries, per `HEAD_KINDS` kind in head order, two floats about that friend's own calls: recency = 1 − (age of its freshest call of that kind) / window, clamped 0–1; rate = (its calls of that kind inside the window) / (window / cooldown), clamped 0–1. A call is inside the window when its age is strictly less than the window. For the six want-kinds each kitty row additionally carries the friend's last stamped intensity (need/100 at emission) for its freshest call of that kind inside the window, 0 outside it — under fog an unseen caller's needs are masked, so intensity is the only urgency channel and the one the reply ladder reads (this overrides the ROADMAP's "intensity dropped" line, which argued position, not urgency). Here-kinds and the free register carry recency + rate only. The self block carries the 30 recency/rate floats for the observer's own calls and no intensity cells (its own needs are already in the self block).
- **FR-017**: The digest window is its own key, `[meow] digest_window_ticks`, served at 30. The per-kind emission cooldown keeps its key `[meow] recent_window_ticks`, served at 10, with its documentation rewritten (it is the cooldown; audibility is now the digest window). Load validation requires the window to be a positive integer multiple of the cooldown.
- **FR-018**: `HEAD_KINDS` stays frozen at 15 in its current order; the reserve kinds' cells are zero wherever they are unarmed; the message head, message codec, and the vocabulary flags are unchanged.

**Scene age and water bit**

- **FR-019**: The self block carries the observer's scene age: activity-clock elapsed / 24 clamped to 1, zero when no scene runs. H = 24 is a frozen literal, never derived from config at observation time.
- **FR-020**: Seen friends' rows carry the friend's scene age by the same formula and a water bit (1 if a water element occupies the friend's tile). Both are knowledge fields under FR-012. The water bit carries no price in Gen 1 (contagion charge 0; shelving stands).

**Same fog for everyone**

- **FR-021**: The decision context handed to any behaviour (built-in or external) exposes exactly the information set the policy observation is built from: the cat's own full state, visible cats and elements with their full state, heard-but-unseen cats per FR-012's resolution, every recent meow, and the cat's own memory. Nothing outside that set is reachable through the context — enforcement is structural, not per-call.
- **FR-022**: Built-in target picking runs over the FR-021 set. **Elements**: candidates are the visible elements ∪ the one remembered tile per kind; a remembered tile is walked to as if it were the element; when it comes inside the disc it is confirmed (the element is there) or refuted (memory cleared), and a refuted memory drops the cat into FR-023 exploration on the same ladder that tick. **Friends** (cuddle, play, the groom response): candidates are visible friends ∪ heard-unseen friends at their last-meow position; on arrival, visible → proceed, not visible → drop the target this tick. The "take what is here" rung, sunbeam-worth-walking, and the water-avoiding step rule run over the same set.
- **FR-023**: When a built-in cat needs an element kind that is neither visible nor remembered, it explores with a persistent heading (owner ruling 4, 2026-09-02). Each cat carries one saved state field, `explore_heading` (a direction or none). On an exploring turn: if there is no heading, or the wall ahead along the heading is within `radius` tiles (arithmetic on position, heading, world bounds and the knob — no vision query), the cat redraws once from its decision RNG, uniformly among directions that are neither the reverse of the current heading nor wall-within-radius; if that set is empty, among any non-reverse direction; if that is empty, it keeps the current heading. It then takes one step along the heading with the existing step rule. The heading persists across turns and is consulted only while exploring. Idling (today's no-element branch) and the memoryless `wander` are not used for this case.
- **FR-024**: At a world-covering radius, with `reply_intensity_floor` unset and `announce_here` = 0, the built-in behaviours' *actions* MUST be identical to the pre-fog engine's at the same seed and config (fog at infinite radius is the pre-fog world; the byte-identical bar is house practice for refactors, and this is the proof the visibility filter changes nothing but visibility). The message stream MAY differ only where FR-036 silences a want that the old armed-only law allowed; the proof run asserts that this is the only difference.

**Schema, width, pins**

- **FR-025**: `OBSERVATION_SCHEMA_VERSION` moves 4 → 5. Every schema-4 artifact is refused at load naming the observation schema and found-versus-expected versions, before any tick.
- **FR-026**: The observation width at the served slot configuration is **exactly 404 floats**: self 85 | kitty 4 × 62 | chow 2 × 5 | water 2 × 4 | sunbeam 2 × 6 | critter 4 × 10 | clock 1. Self 85 = 34 (schema 4) + 1 scene age + 30 own message block + 20 memory (no reply bits on the self row — owner ruled 2026-09-03: "I answered someone" is derivable from the cat's own message block plus the want and referent it can see, and no reward reads it). Kitty row 62 = 20 (schema 4) + 1 water bit + 1 scene age + 30 recency/rate + 6 want intensities + 4 answers-me bits. Width stays `observation_len(cfg)`, config-derived; 404 is what the served config works out to, and the schema pin test asserts it literally (the spec-033 pattern: derived in the engine, literal in the pin, so a drive-by move is loud).
- **FR-027**: The activity menu at the served config is 39 entries (34 + one kitty-verb group for the fourth row); the v3 forward's kitty-pointer logits are 20 and its logit budget 55 (39 + 16). `ACTION_SCHEMA_VERSION` (3) and `MASK_SCHEMA_VERSION` (3) do not move: menu and mask sizes are config-derived by design and the layout rules are unchanged (owner: codec, HTTP API and `HEAD_KINDS` layout are out of scope).
- **FR-028**: The v3 artifact format (spec 030) is unchanged; its token groups derive from the block widths, so the message-kind tokens disappear with the global digest and the kitty/self tokens widen. The critic's global state (v1) is unchanged and unfogged. `docs/encodings.md` is rewritten to the schema-5 layout with the schema-4 table moved to the historical section.

**3.0 config hygiene** (members and scope per the step-3 doc; this spec restates, it does not re-argue)

- **FR-029**: `[elements.<kind>] max` is KEPT; its doc comment is corrected to name what it feeds (the density ceiling in validation and the critic's chow-remaining scale), and the ROADMAP line that called it dead is corrected.
- **FR-030**: The whole-table section-absence defaults on the core config — the 13 top-level and the four nested (`happiness.weights`, `actions.durations`, `meow.vocabulary`, `water.contagion_membership`) — are deleted; a missing section is a load error naming it. `rl`, `plugins`, `watchdog` stay optional. Per-field defaults on inert launch dials stay (they are the stamp discipline, not shims). The new `[vision]` section and `[meow] digest_window_ticks` follow the same rule: present in every 3.0 config, no absence default.
- **FR-031**: The seven parse-then-reject retired-key fields and their rejectors and guard tests are deleted: `[purr] cooldown_ticks`; `[meow] cooldown_ticks`, `urgent_cooldown_ticks`, `courtesy_ticks`, `urgent_courtesy_ticks`, `urgent_need_threshold`; `[actions] cuddle_relief`. `deny_unknown_fields` keeps refusing the keys; the wall's migration note carries the seven maps. The spec-025 play-key wording on the live chain link stays.
- **FR-032**: `explore_heading` (FR-023) and the meow record's `reply` and `pos` (FR-040) ride the step-4 snapshot bump. The snapshot restore shims are deleted: the seven in `kitty.rs`, `Pursuit.improved_at`'s default, the pre-041 duet fixture and the two `snapshot_resume` tests already marked for the wall. A pre-3.0 save does not load.
- **FR-033**: `evals/v1` is listed in `config-sweep-exclusions.txt` as a frozen 2.x record; `evals/v2` is cut — the same six exam designs as complete 3.0 configs with new manifest hashes, the freeze guard and the "frozen exams are in the sweep" assertion retargeted, and `kitty-eval` reading v2. v1 results stay a 2.x record.
- **FR-034**: Every config actively loaded by HEAD tooling (the served config, `training.toml`, cert, collect, lab families, `binding_continuity` fixtures) migrates to complete 3.0 form in the same change (65 in-scope files lacked `[water]` and 8 lacked ten or more sections at the step-3 count); result-backing families go to the exclusions file with a reason. A migration note at the wall lists every removed key, every formerly-optional section, and the new keys (`[vision] radius`, `[vision] memory_timeout_ticks`, `[meow] digest_window_ticks`, `[behavior] reply_intensity_floor`).

**Records**

- **FR-035**: The changelog entry carries `[obs-schema]`, `[world-fresh]` and `[stamp]`; `[rng-sequence]` is claimed only if a seeded run at a world-covering radius fails FR-024 (it is not expected to). The Unreleased section is expanded before any 3.0 tag.

**Meow law under fog** (owner rulings 1–3, 2026-09-02, timeline @ 027563d; restated, not re-argued)

- **FR-036 (want law)**: A want-kind is legal for a cat iff (a) its grounding need is armed (the existing `announce_threshold` + `announce_hysteresis` knobs; no per-kind thresholds), (b) that need is the cat's top need (`NeedKind::ALL` order breaks exact ties — the existing highest-pressure rule), and (c) the cat has no known relief for it: `want_eat` — no chow visible or remembered; `want_drink` — no water visible or remembered; `want_cuddle`, `want_bath` — no available friend in view OR heard at a known position (coverage pass: the broadcast position is the invitation), where "available" is the engine's existing partner-availability predicate for that scene kind (one shared definition); `want_play` — the same friend clause AND no critter visible or remembered (owner ruled 2026-09-03: play is always satisfiable by the solo pounce, so the word means "nothing better than solo is known", and the `want_play ↔ here_critter` pair only makes sense if a critter the caller can see silences the call; bugs and greebles are memory kinds, refuted on sight); `want_sleep` — need-only-when-top, no knowledge gate (the spec's pick between the two ruled options: sleep has no referent, and the `want_sleep → here_sunbeam` reply pair presupposes the word is speakable). Cooldown and vocabulary gates are unchanged. There is ONE predicate, used by the mask and by the built-in announce rule alike.
- **FR-037 (here law widened)**: A here-kind is legal iff its cooldown is clear, its vocabulary flag is on, and EITHER its referent is adjacent (today's law, unchanged) OR a matching want from another cat is audible in the speaker's start-of-tick snapshot AND the referent is visible from the speaker. Pairs: `here_food ↔ want_eat`, `here_water ↔ want_drink`, `here_sunbeam ↔ want_sleep`, `here_critter ↔ want_play`. Cuddle and bath have no here-word.
- **FR-038 (`announce_threshold` is screened, not moved)**: the served value stays 30 in this change; the step-5 prereg screens {10, 15, 20, 30} on the scripted seats (hysteresis 5) and sets the listener floor in the same sitting. Nothing here pre-empts that.
- **FR-039 (no new vocabulary)**: `HEAD_KINDS`, the message head and codec, and the vocabulary flags are unchanged; the reply flag is a stamp on a recorded meow, never a word a policy chooses.
- **FR-040 (reply stamp)**: Every recorded meow carries a `reply` flag, engine-stamped at emission and never policy-chosen: for a here-kind, reply = 1 iff a matching want from another cat was audible in the speaker's start-of-tick snapshot AND the referent was visible from the speaker — adjacency sits inside visibility, so an adjacent here with a want audible is also a reply; reply = 0 otherwise, and for every non-here kind. The stamp is separate from any trigger: an ambient here landing while a want is audible is stamped 1 too. Every recorded meow also carries `pos`, the speaker's position at emission, engine-stamped. Both fields are additive on the meow event stream and `/world` (owner ruling iv); rendering a reply is a Client backlog item for after Gen 1, not this spec's.
- **FR-041 (answers-me observation)**: Per kitty row and per here-kind, the observer reads 1 iff that friend's freshest here of the kind inside the digest window was emitted after the observer's own matching want inside the window — observer-relative "answers me", derived at build time from the recent-meow buffer, no new engine state. A same-tick reply cannot exist (everyone decides against the start-of-tick snapshot); want → here → heard is three ticks at best.
- **FR-042 (scripted reply trigger)**: A built-in cat replies by *want*-listening (the groom-response precedent, spec 028 FR-019); the standing no-here-listener guard (043) is untouched — no built-in ever consumes a here-word. It replies with the paired here-kind iff a matching want from another cat is audible, the referent is visible from it, the here-kind's cooldown is clear, and the caller's stamped intensity (need/100 at emission) is ≥ `[behavior] reply_intensity_floor`. The reply is message-only: the replier's action is untouched.
- **FR-043 (listener floor knob)**: `[behavior] reply_intensity_floor` is optional; unset = replies off and the launch state byte-identical (the 043 pattern). Placeholder 0.30 for corpus-collection configs, documented as provisional: revisited when the speaker floor is set at step 5 (a 0.30 listener floor over a 15 speaker floor yields calls nobody scripted answers). The replier's own needs play no part in the floor.
- **FR-044 (which caller)**: With several answerable wants audible, the built-in answers the highest stamped intensity; ties to the fresher call, then the lower kitty id.
- **FR-045 (scripted ladder)**: WaitForMe > {reply, own want} > ambient here > Silent. The middle pair resolves by urgency: the own want speaks iff own raw need > caller intensity × 100 (raw need on both sides); ties reply. The loser is delayed one tick at most (per-kind cooldowns count from the last emission). Here-kind cooldowns are never bypassed for replies; a blind caller re-emits every cooldown anyway.
- **FR-046 (callers ignore replies)**: A built-in cat does nothing with a reply it receives — it keeps exploring (FR-023). Replies feed policies and instruments only.
- **FR-047 (safeguard unchanged)**: The Article I safeguard stays existence-based: it spawns when no reachable resource exists, never because none is visible. No fog-aware rescue is built (owner ruling i).

### Key Entities

- **Vision disc**: the set of tiles at integer offset (dx, dy) with dx² + dy² ≤ r² around a cat; 81 tiles at r = 5 (the Manhattan diamond would be 61, the Chebyshev square 121).
- **Element memory**: per cat, per element kind, the last-seen tile and tick; sight-only, most-recent-wins, refuted on sight, no expiry by default.
- **Kitty row**: one permanent observation row per friend, by id; carries seen-state fields, knowledge fields, and the friend's message block; masked by row state (seen / heard / silent).
- **Message block**: 15 kinds × (recency, rate) about one speaker's own calls inside the digest window, plus last stamped intensity for the six want-kinds on friend rows; one per kitty row and (recency/rate only) one for the observer.
- **Meow record**: kitty, kind, tick, intensity — now also `pos` (speaker position at emission) and `reply`; both engine-stamped, both additive on the API.
- **Digest window / cooldown**: window 30 ticks (audibility and the rate's denominator); cooldown 10 (the speech-economy law, F-034's density ladder rides on it); window = 3 × cooldown so the rate maximum is exact.
- **Scene age**: activity-clock elapsed / 24 clamped; H = 24 frozen.
- **Want law**: armed AND top need AND no known relief; the one predicate the mask and the built-in announce share.
- **Reply flag**: engine stamp on a recorded here-word — a matching want was audible and the referent visible from the speaker.
- **Answers-me bit**: observer-relative reading of a friend's here against the observer's own earlier want, per here-kind; friend rows only.
- **Exploration heading**: one saved direction per cat, redrawn only when the wall ahead is within the radius; the blind scripted cat's search.
- **Listener floor**: `reply_intensity_floor`, the caller intensity a built-in must hear before it answers; unset = off.
- **3.0 config**: complete in every section, unknown keys and missing sections both refused.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: At the served configuration the observation is exactly 404 floats, the menu 39, the kitty-pointer logits 20, the logit budget 55, the observation schema 5 — asserted literally by the schema pin test and derived everywhere else.
- **SC-002**: Over randomised worlds and radii (property test), the entities present in a cat's observation and reachable through its decision context are exactly those inside its Euclidean disc (plus heard rows and own memory per FR-012/FR-021): zero misses, zero leaks.
- **SC-003**: Memory properties hold under property test: a slot is only ever the nearest visible element of its kind at its last-seen tick; a remembered tile inside the disc that holds no element of the kind reads cleared on that tick; no slot clears otherwise at the default timeout; staleness is monotone between sightings.
- **SC-004**: The served roster all-scripted at a world-covering radius (reply floor unset, `announce_here` 0) reproduces the pre-fog engine's action stream byte for byte over 20,000 ticks at the same seed and config, and the only message-stream difference is wants silenced by FR-036.
- **SC-010**: Under property test, no want-word is ever legal while its relief is visible or remembered, or while it is not the top need; no here-word is ever legal without an adjacent referent or (audible matching want AND visible referent); every reply = 1 stamp has an audible matching want and a visible referent at emission; every heard-unseen row's position equals the friend's stamped position at its freshest audible meow; no reply is ever stamped on the tick of the want it answers.
- **SC-011**: With `reply_intensity_floor` unset, the served roster's action and message streams are byte-identical to the same engine with the reply path absent; with it set, every scripted reply satisfies FR-042/FR-044/FR-045 (property test over staged callers).
- **SC-012**: A blind exploring cat first sights a bowl within one world crossing (≤ 40 ticks at 20×20) in every seeded trial with at least one bowl present; its RNG draw count equals its redraw count (zero draws per non-redraw step).
- **SC-005**: The served roster all-scripted at r = 5 runs 20,000 ticks with zero constitutional invariant failures; its welfare readings (distress events, watchdog) are recorded for the step-5 prereg, not gated here — the welfare bands are step 5's.
- **SC-006**: Same seed + config + tick count → identical world state including every cat's memory, across a save/restore mid-run.
- **SC-007**: Every config in the two config sweeps and the nan table loads complete or is excluded with a reason; a config missing any non-optional section is refused naming it; each of the seven retired keys is refused as unknown.
- **SC-008**: A schema-4 policy artifact is refused at startup naming the observation schema; no tick runs.
- **SC-009**: `binding_continuity.py` passes against a new reference record built on a 3.0 config with an all-scripted seating (the cutover housekeeping the step-3 doc assigns to the wall PR; the tool proves binding-vs-engine determinism).

## Assumptions

- **Authority**: the step-3 section of `experiments/fog-gen1-timeline-2026-08-26.md` (main `8423060`) is the in/out list; this spec adds nothing to it. Sub-decisions taken here are listed below with reasons; each is semantics-tier (retrain, never a break) unless marked.
- **Knob placement**: `[vision]` is a core (world-law) section, not `[rl.observation]`, because the radius governs scripted behaviours too (same fog for everyone). `memory_timeout_ticks` lives beside it. Both are required sections/keys under FR-030 (no absence default).
- **Radius floor 2, not 1**: adjacency needs r ≥ 1; the spec-012 yield rule needs its Manhattan-2 friend visible (the ruling's own note), which r ≥ 2 guarantees. The placeholder 5 and any screened value clear it.
- **`want_sleep` = need-only-when-top**: the ruling offered that or "never speakable"; the reply pair `want_sleep → here_sunbeam` presupposes speakable, and sleep has no referent to gate on.
- **`want_play` gate includes critters** (owner ruled 2026-09-03 on the draft's flag): a visible or remembered critter is known play relief; the friend clause is the same as cuddle and bath.
- **No reply bits on the self row** (owner ruled 2026-09-03 on the draft's flag): the "4 here kinds × 5 rows" in the ruling text was a miscount of the self row; answers-me bits live on friend rows only.
- **Exploration heading persists** when not exploring (no clear rule) — a stale heading pointing at a wall simply triggers a redraw on the next exploring turn; fewer rules, same behaviour.
- **Placeholder radius 5**: the worked example throughout the timeline and ROADMAP (81 tiles); screened at the step-5 prereg, not here.
- **Staleness normaliser 40**: frozen literal = the served 20×20 world's width + height, the scale the observation already uses for distance; a memory older than a full traverse is fully stale for navigation. Semantics tier; the prereg may retune it as its own line.
- **Memory while seeing**: the slot mirrors the nearest visible element with staleness 0 rather than holding only the last *out-of-view* sighting — one rule ("last known") instead of two.
- **Memory update timing**: environment phase, after actions and before invariants, so decisions read a complete start-of-tick snapshot (Article V tick order unchanged).
- **Cooldown key keeps its name**: `recent_window_ticks` stays the cooldown key and `digest_window_ticks` is new, rather than renaming the cooldown — the retired `[meow] cooldown_ticks` name is being deleted in this same change and reviving it with a new meaning would defeat the migration note; F-034's density-ladder tooling references the existing key. A rename is a plan-time option if the sweep shows no Python reader.
- **Heard-row `present` = 0**: the presence bit keeps meaning "seen"; hearing shows in the message block. Under the Q1 re-ruling a heard row is (present 0, position = last-meow position, message live), distinguishable from a seen row and from silence.
- **No intensity on the self row**: the coverage pass sized intensity at 6 kinds × 4 rows; the observer's own urgency is its own needs, already in the self block.
- **Heard-unseen friend distance = Manhattan to the stamped position** (travel to where the call came from), the same meaning the field has for seen friends.
- **Roster > slots + 1 is a startup error**, not a silent truncation: the ruling's "roster − 1" wording exists so a roster change re-raises the count explicitly.
- **Scripted anchors use memory**: the same information set as a policy includes the memory; a remembered tile is a navigation target. Without it a scripted cat would be strictly less informed than the mind it benchmarks.
- **Critic stays global and unfogged**: centralised training, decentralised execution — the existing doctrine; the global-state schema does not move.
- **Expansion tool**: no map across this wall; Gen 1 minds train fresh on the far side (bootstrap doctrine: lineage BC from the post-cutover corpus).
- **Step-5 bars are Experiments'**: the here-conditioned acceptance bar becomes three (reply-here, ambient-here, want), and the collector trace reads `reply` and want intensity off the meow record — instrument work on fields this spec already provides; no engine change beyond FR-040.
- **Speaker-floor screen is step 5's**: `announce_threshold` ∈ {10, 15, 20, 30} on scripted seats, listener floor set in the same sitting, welfare non-inferiority + informativeness bar declared at prereg. The spec ships the served 30 and the optional listener knob, nothing more.
- **Out of scope by ruling**: codec / `ACTION_SCHEMA_VERSION` layout rules, the HTTP API contract, `HEAD_KINDS` layout, the estimator/JEPA head (not wall-gated), waterline contagion (shelved, charge 0), the Here*-teacher (OUT; corpus = `announce_here = 1` seats), any client rendering of fog. Cutover housekeeping (binding-continuity re-baseline, `groom_cuddle_relief` 2.0 → 0.5 with its pin) is the wall / step-7 PRs' by ruling and is cited (SC-009), not specified.
- **Sequencing**: this is step 4. The 3.0 cutover deploy is `update.sh --fresh` at step 7 after step 5's shakeout and step 6's lock; nothing here deploys.
