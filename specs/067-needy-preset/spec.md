# Feature Specification: Needy Behaviour Preset (Mid-World Need Onsets on a Scripted Seat)

**Feature Branch**: `product/067-needy-preset`

**Created**: 2026-10-26

**Status**: Draft

**Input**: Owner kickoff 2026-10-26, her words in this session: "Let's
knock out the last spec for the mid episode welfare testing before we
jump on the next round of engine work." Her framing, relayed by
Experiments 2026-10-25 (relay fe6e7d7c, on her word "Yes on relay to
product"; a relay, never a kickoff): "I'm thinking maybe a new scripted
model that demonstrates various states mid-episode?" and, verbatim: "So
essentially we want a 'needy' preset that will drive needs up. I'm not
sure the best way to do this and maintain determinism, but what I'm
thinking is: periodically choose a random need to run up. Have need
selection and periodicity be random enough that occasionally there is
overlap between high need (so it's not always just a single need, which
is not realistic in our world), or even have it deliberately run up all
but one need occasionally. Essentially we want it to focus on single
need, but also demonstrate multi-need and all-but-one-need patterns that
are likely to occur in the real world." Design context: the Professor's
note `~/ai/professor/notes/for-experiments-midworld-onset-instrument-2026-10-25.md`
§Q2 (advisory; this spec is Product's), Experiments' Phase 1d
declaration §Addendum 4, findings F-068 and F-069, and the design notes
worked out 2026-10-25 that she called "All reasonable" (recorded under
Assumptions, not redone here). Depends on spec 066 (landed, PR #469 →
3ba039c4), which supplies the hazard registry, the acknowledgement table
and the server switch this preset plugs into.

## Why now

The mini-friend probe reads a friend's hidden grave need, and the
evidence says it does so only as a property of a young world (F-069):
every grave onset in every training and evaluation set is a start-up
onset (spec 065's distressed start) or a re-entry within 72 ticks of
one; no world holds a grave onset after offset 322. The same grave rows
the probe detects 0.995 of the time at a world's first tick it detects
0.358 of the time when spliced after 100 clean ticks of lived history.
Nothing on disk has asked the probe to see grave ARRIVE mid-world on a
state that has tracked a long clean history, because no mechanism can
make it arrive. Forcing a covered (learning) friend grave is ruled out:
a covered mind is shaped by what it lives through, and relief is always
available by constitution. A scripted seat is welfare-exempt (welfare
practice 2026-09-26: covered = shaped by experience, scripted exempt),
so the instrument is a scripted preset that, on a declared schedule,
stops servicing chosen needs so they climb mid-world — single-need,
multi-need and all-but-one patterns — while every relief in the world
stays exactly as available as today. The Gen 3 and 1.0 roadmap waits on
this read; the owner's kickoff names it the last spec before the next
round of engine work.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A scripted seat drives needs up mid-world on a declared schedule (Priority: P1)

An experimenter seats one kitty on a needy preset (`needy`, which
releases each episode at the declared level, or `needy_hold`, which holds
it to the declared limit). From the world's
first tick that kitty behaves like today's scripted teacher. At a
declared onset tick its schedule opens an episode: a drawn set of one or
more needs is MASKED, and from then on the kitty stops servicing those
needs itself and refuses relief for them offered by friends, while it
keeps servicing every other need, keeps calling for what it wants, and
the world keeps offering relief exactly as before. The masked needs
climb. Under `needy` the episode releases when they reach the declared
release level (or the hold limit passes first); under `needy_hold` it
releases only when the hold limit passes, so the needs sit grave for a
sustained stretch. Either way the mask lifts, the kitty services them
again, and after a declared rest the next episode opens with a fresh
draw. Over a long world the kitty demonstrates single-need, multi-need
and many-need patterns, up to every need at once, each with a known
onset tick.

**Why this priority**: this is the instrument itself. Without it the
probe's mid-world question cannot be asked.

**Independent Test**: a scratch world with one needy seat at a fixed
seed, run for the schedule's first several episodes; the masked needs
rise from onset to release, the unmasked needs stay serviced, each
onset and release tick equals the schedule's declared tick, and the same
seed reproduces the identical schedule and identical world.

**Acceptance Scenarios**:

1. **Given** one needy seat and the default parameters, **When** the
   world runs through its first episode, **Then** between the declared
   onset tick and the release the masked needs rise monotonically apart
   from the engine's own floors and the kitty takes no action that
   relieves a masked need, while its unmasked needs are serviced as a
   teacher-preset kitty's would be.
2. **Given** a masked cuddle or bath need and a friend adjacent who
   proposes co-sleep, cuddle or grooming toward the needy kitty,
   **When** the friend's offer is resolved, **Then** the needy kitty
   refuses it for the masked need (the pattern does not collapse because
   a friend is nearby) and accepts it again once the episode releases.
3. **Given** the declared mix weights over the number of masked needs
   m (one weight per m from 1 to 6), **When** a long world runs,
   **Then** every m with a non-zero weight occurs, no m with a zero
   weight occurs, and the proportions match the weights within the
   run's sampling noise.
4. **Given** the `needy` preset, a release level L and a hold limit T,
   **When** an episode's masked needs all reach L before T ticks,
   **Then** the episode releases at that tick; **When** they do not,
   **Then** it releases at onset + T. **Given** the `needy_hold` preset,
   **When** the masked needs reach L, **Then** nothing releases; the
   episode releases at onset + T.
5. **Given** the same seed and config, **When** the world is generated
   twice, **Then** every onset tick, need set and release is identical;
   **Given** a different world seed or a different kitty id, **Then**
   the schedule differs.
6. **Given** two needy seats in one roster (either preset each),
   **When** the world runs, **Then** each has its own schedule and
   neither's draws move the other's.
7. **Given** the default first-onset levels, **When** many worlds are
   generated at different seeds, **Then** first onsets fall in every
   level with non-zero weight, in proportion to the weights, and no
   onset tick repeats across worlds more often than chance allows (the
   schedule carries no clock).

---

### User Story 2 - A world without a needy seat is byte-identical to today (Priority: P1)

An operator runs any existing config on the new engine. No kitty is
seated on either needy preset, so nothing changes: the three existing presets decide
exactly as before, every seeded draw lands where it did, the served
config surface, the defaults stamp and the world fingerprint are
unmoved.

**Why this priority**: inert-when-absent is the standing gate on every
world knob (specs 062–066); a leaking default poisons every golden and
every frozen pin, and the three presets are the Gen 2 corpus
demonstrators (doctrine rule 9).

**Independent Test**: the full suite green with zero golden, pin or
fixture re-cuts; a full run at a fixed seed with no needy seat
byte-identical to the pre-feature engine on every readable surface.

**Acceptance Scenarios**:

1. **Given** any config with no needy seat and no needy parameter
   section, **When** a full run executes, **Then** every readable output
   (serialized config, defaults stamp, world snapshot stream, decision
   log, boot log) is byte-identical to the pre-feature engine at the
   same seed.
2. **Given** the `needs_driven`, `playful` and `teacher` presets,
   **When** they decide, **Then** their decisions are byte-equal to the
   pre-feature engine's on every seeded world.
3. **Given** a config that writes the needy parameter section but seats
   no kitty on a needy preset, **When** it loads, **Then** it validates, the
   parameters are inert, and the generated world is identical to the
   same config without the section.

---

### User Story 3 - A needy seat is a welfare-hazardous mode and is treated as one (Priority: P2)

Spec 066 made every welfare-hazardous mode something that must be
acknowledged by name to load, kept out of every served and shipped
config, and served only on stated intent. Seating a kitty on `needy` is
the second such mode and on `needy_hold` the third (its own mode: a
sustained-grave world is a stronger statement than a crossing world, and
the acknowledgement is exact). A config with a needy seat loads only if
it acknowledges the matching mode name; the shipped-config sweeps refuse
such a config anywhere outside `experiments/`; the server serves it only
with `--allow-welfare-hazard` and then says so.

**Why this priority**: this is why spec 066 exists: a research-only
behaviour that manufactures hardship must never be seated by accident,
and a world that carries it must be visibly hazardous from tick 0.

**Independent Test**: spec 066's seven failure shapes run against a
needy-seat config with each mode name (`needy`, `needy_hold`); the sweeps' self-
tests run with a needy-seat file; the server hand check runs with a
needy-seat config.

**Acceptance Scenarios**:

1. **Given** a config seating one kitty on `needy` with no
   `[welfare_hazard]` table, **When** it loads, **Then** loading fails
   naming `needy`, the seat (which kitty, by name and id) that
   activates it, and the line to add; the same for `needy_hold`.
2. **Given** the same config acknowledging `["needy"]`, **When** it
   loads, **Then** it validates; **Given** it also carries a raised
   distressed start or a `needy_hold` seat, **Then** it must acknowledge
   every active mode, in registry order (`initial_needs`, `needy`,
   `needy_hold`), or fail naming the missing one.
3. **Given** an acknowledged needy-seat config outside `experiments/`,
   **When** either shipped-config sweep runs, **Then** it fails naming
   the file and the mode.
4. **Given** an acknowledged needy-seat config, **When** the server
   starts without the switch, **Then** it refuses before any world
   exists; **When** it starts with the switch, **Then** the boot line,
   `GET /config` and the key-settings row name the mode.

---

### User Story 4 - The pattern is observable and the world's welfare law is untouched (Priority: P2)

A lab reader studying the probe needs two things from a needy world:
the ground truth of what the needy kitty was doing, tick by tick, and
confidence that nothing else in the world changed. Each tick the
recorder sees, for every needy seat, which needs are masked, which
episode this is (its ordinal) and its phase. The needy kitty still calls
for what it wants with law-named words only. Every other kitty, every
relief source and every welfare safeguard behaves exactly as today.

**Why this priority**: an onset the reader cannot anchor to a tick is
not an instrument, and a reader cannot attribute a probe miss to the
signature unless the rest of the world is held fixed.

**Independent Test**: the lab recorder's per-kitty record for a needy
seat carries the mask, the ordinal and the phase each tick, and they
agree with the schedule; a non-needy seat's record is unchanged; the
needy kitty emits only law-named words; the engine's safeguard relief
and distress records fire for the needy kitty's climbing needs exactly
as for any kitty's.

**Acceptance Scenarios**:

1. **Given** a needy seat in a lab world, **When** the recorder reads a
   tick, **Then** that kitty's record names the masked need set, the
   episode ordinal and the phase (resting, held, releasing), and these
   match the schedule's declared values for that tick.
2. **Given** a non-needy seat in the same world, **When** the recorder
   reads a tick, **Then** its record is byte-identical to the pre-
   feature record (no new field, no changed value).
3. **Given** a needy kitty with a masked need above its want line,
   **When** it decides, **Then** it may call the matching law-named
   want (as any teacher-preset kitty would) and never a sound-named
   word.
4. **Given** a masked need crossing the engine's safeguard threshold,
   **When** the environment phase runs, **Then** the safeguard relief,
   the distress record and the Article I bounds apply to the needy
   kitty exactly as they do to any kitty — the mask governs only what
   the kitty CHOOSES, never what the world DOES.

---

### User Story 5 - A needy seat can never teach (Priority: P2)

A corpus collector drives a roster that includes a needy seat (the
scouts' census worlds will). The collector refuses to record the needy
seat's turns as teacher demonstrations: the seat is marked ineligible to
teach by the engine itself, and the refusal is by construction, not by
an experimenter remembering to exclude it.

**Why this priority**: doctrine rule 5 — a teacher may act only on what
the student can see. The needy schedule is the kitty's private state,
invisible to any student; that is lawful ONLY because this preset never
teaches. Spec 066 deferred the teacher-eligibility flag to this spec as
its first reader.

**Independent Test**: the engine exposes an eligibility answer per
seated behaviour; the three existing presets answer eligible, `needy`
answers ineligible; the collector's refusal is exercised against a
needy-seat roster.

**Acceptance Scenarios**:

1. **Given** the behaviour registry, **When** eligibility is read for
   `needs_driven`, `playful` and `teacher`, **Then** each is eligible;
   **When** read for `needy` or `needy_hold`, **Then** it is ineligible.
2. **Given** a corpus collection over a roster with one needy seat,
   **When** the collector runs, **Then** it records no demonstration row
   for that seat, says so once in its output, and records every other
   seat as today.

---

### Edge Cases

- **A masked need already at or above the release level at onset**
  (`needy`): the episode still opens; it holds until every masked need
  is at or above the release level (so a need that is already there
  waits for the others) or until the hold limit, whichever comes first.
  Under `needy_hold` the level plays no part.
- **Release level at or below an engine floor**: plain-tile sleep never
  drops below the engine's off-beam sleep floor, so a sleep release
  level at or below that floor is reached the moment sleep is masked:
  the episode would release at once and the stratum would be
  degenerate. Validation refuses a release level at or below any
  engine floor (today the one floor is the off-beam sleep floor).
- **The hold limit expires with no need at the release level**
  (`needy`): the episode releases anyway; the recorder's phase says so,
  so a reader can separate level-released from time-released episodes.
  Every `needy_hold` release is time-released by construction.
- **Two needy seats**: each derives its own schedule from (world seed,
  its kitty id); neither consumes the other's draws or the world's
  master stream.
- **A needy seat plus a distressed start (spec 065) in one config**,
  or both needy presets seated: every active mode must be acknowledged,
  in registry order (`initial_needs`, `needy`, `needy_hold`).
- **The needy parameter section written, no needy seat**: inert and
  valid (User Story 2, scenario 3); the section is not a hazard, the
  seat is.
- **A needy kitty asked to help a friend** (groom response, co-sleep
  proposal from another cat): unmasked needs do not change how it
  answers; the mask only stops it from accepting relief FOR a masked
  need and from seeking one.
- **A friend keeps proposing to a needy kitty every tick**: refusals
  are recorded as refusals are today, no new record type; the refusal
  record's reason names the mask (a new reason value, `needy_masked`,
  beside the consent reason — never the consent reason, which would
  mislabel it), and the same reason stamps the needy kitty's own
  refused proposal for a masked need. The friend's legal mask and
  every other kitty's refusal reasons are exactly today's: the mask is
  hidden state of the needy kitty, read by the engine at the apply slot
  only (the consent gate's precedent), never by validation.
- **A policy or plugin seat**: cannot carry a needy preset, by
  construction: a kitty carries needy state exactly when its configured
  behaviour is a needy preset name, the engine checks that pairing as
  an invariant every tick, a control override (the binding's per-kitty
  control map) that would seat a needy kitty on anything else or seat
  anything else on a needy config seat is refused before the world
  exists, and a resume that adds or removes a needy seat relative to
  the saved world is refused. So a covered mind can never be masked
  (doctrine rule 12, second guard).
- **Every need masked (m = N, six today)**: reachable when the set
  gives m = N a weight. The kitty services nothing and only calls; the world's relief
  and safeguards still act on it (FR-013). Her ruling: the cap is the
  set's, from 1 to all needs.
- **Save and resume**: every DRAW of the schedule is a pure function of
  (world seed, kitty id, parameters, draw order), but the episode's
  STATE is not: a level release depends on the path the masked needs
  took, so the state (phase, ordinal, mask, the private stream's
  position) is saved with the world and a resumed world continues from
  it; nothing is re-derived. A resume whose config seats a needy preset
  where the saved world carries no needy state, or the reverse, is
  refused (the policy-seat Edge Case above).
- **A first onset drawn beyond the world's length** (a late history
  level in a short world): the seat never opens an episode in that
  world; the recorder shows ordinal 0 throughout, and the set's
  declaration counts it as a world with no onset, not as a missed one.
- **An onset tick of 0**: "tick" throughout means the tick a snapshot
  carries, and the first snapshot after generation carries tick 1 (the
  generated world is tick 0, before any decision). An episode opens on
  the first published tick whose number is AT OR PAST its onset, so an
  onset of 0 opens on tick 1 and no onset is ever skipped; a rest gap
  of 1 opens the next episode on the tick after the release.
- **Switching off servicing mid-scene**: at onset, the needy kitty's
  own activity ends if it would relieve a masked need, and a friend's
  in-progress co-sleep or rest WITH the needy kitty drops to solo
  posture and a friend's groom OF the needy kitty ends, the same tick,
  so no relief for a masked need lands after the onset tick. Nothing
  else about the friend's scene changes.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST register two further builtin behaviour
  presets, `needy` (each episode releases at the declared level, or at
  the hold limit if the level is not reached first) and `needy_hold`
  (each episode releases only at the hold limit), seatable like
  `needs_driven`, `playful` and `teacher` through a kitty's `behavior`
  setting, and nowhere else. "A needy seat" below means either.
- **FR-002**: With no needy seat, the engine MUST be
  byte-identical to the pre-feature engine on every readable surface:
  the three existing presets' decisions, every seeded draw, the
  serialized config, the defaults stamp, the world fingerprint, the
  snapshot stream and the boot log. Zero golden, pin or fixture
  re-cuts.
- **FR-003**: Every DRAW of a needy seat's SCHEDULE — each episode's
  onset tick, masked need set and rest gap — MUST come from a private
  stream that is a deterministic function of the world seed, the
  kitty's id and the declared parameters, consuming neither the world's
  master stream nor any other kitty's private stream, so the same seed
  and config reproduce the identical schedule and no other kitty's
  draws move. The schedule's STATE (which episode, its phase, its mask,
  the stream's position) is world state: it is saved and resumed with
  the world (Edge Cases, save and resume), because a level release
  depends on the path the needs took.
- **FR-004**: Each episode MUST have: an onset tick (the previous
  release plus a rest gap drawn from a declared range; the FIRST onset
  of each needy seat drawn per world from declared history-length
  levels — at least five, spanning the world's length, e.g. 0–2 /
  2–10 / 10–50 / 50–200 / 200–20,000 ticks (A2: edges straddling the
  F-070 knee) — each level with a
  declared weight and the tick drawn flat or log-uniform within the
  level, so the schedule carries no clock: no onset tick is fixed
  across worlds and a head trained on the set cannot learn one (the
  Professor's change 1; the probe's grave read is a function of state
  age, F-069)); a masked need set of m distinct needs,
  m drawn by a declared weight vector with one weight per m from 1 to
  the engine's need count, N (six today; a zero weight excludes that
  count; the default mix is a coverage design, not a model of the
  world — owner ruling 2026-10-26, "C", configurable from one need to
  all needs); and the preset's release
  rule: `needy` releases when every masked need is at or above the
  declared release level, or when the declared hold limit has passed
  since onset, whichever is first; `needy_hold` releases when the hold
  limit has passed and never before (owner ruling, "B").
- **FR-005**: While a need is masked, no action of the needy kitty's
  own MAY relieve it: an action is judged by the full set of the
  ACTOR's needs it relieves (eat → eat; drink → drink; solo sleep →
  sleep; co-sleep → sleep AND cuddle; rest with a friend → cuddle;
  self-groom → bath; grooming a friend → the groomer's own cuddle;
  play, solo or social → play), and one that touches a masked need
  resolves to nothing at the engine's apply slot, however it was
  proposed. Relief OFFERED by another kitty for a masked need MUST be
  refused at the same slot, target-side (a friend's co-sleep or rest
  with the needy kitty → its cuddle; a friend's groom of it → its bath;
  a friend's social play with it → its play): the friend's proposal
  resolves to nothing and is recorded as a refusal. Needs not masked
  are serviced exactly as the base preset services them, and the
  preset's own choice avoids proposing what the slot would refuse, so a
  needy kitty masked only on cuddle still sleeps, alone. The mask
  suppresses SERVICING ONLY: the kitty's calling (the law-named want
  for a masked need, and every other word rule) is unchanged from the
  base preset (owner ruling 2026-10-26, "A"; the Professor's line (b):
  a cat that wants, calls and refuses relief is the realistic
  signature, and the message block is in the probe's input).
- **FR-006**: Outside the mask, both needy presets MUST decide exactly
  as the `teacher` preset (every rung on): the only difference between
  a needy kitty and a teacher-preset kitty is the mask, and the only
  difference between the two needy presets is the release rule. (Assumption A3;
  the base preset is a design default, not a ruling.)
- **FR-007**: The needy kitty MUST speak law-named words only (want,
  here, purr, wait-for-me), never a sound-named word, and its calling
  MUST follow the same rules as the base preset's.
- **FR-008**: The presets' parameters MUST be one shared configuration
  section: the mix weights (one per m from 1 to N, validated to exactly
  N entries with the error naming N), the release level
  (`needy` only; `needy_hold` ignores it), the hold limit, the rest-gap
  range and the first-onset history levels (boundaries and one weight
  each, at least five levels), each with a declared default, validated
  at load (every weight vector finite, non-negative and not all zero;
  release level in the need range and strictly above every engine
  floor, today the off-beam sleep floor; hold limit and gaps positive;
  level boundaries strictly increasing with at least five levels), and
  inspectable on the served config surface like any other section.
  Writing the section with no needy seat is valid and inert. (The
  design notes' per-need floor table is not a parameter: the engine's
  floors are already its own config, and the release rule reads them
  there.)
- **FR-009**: Seating any kitty on `needy` MUST register as the
  welfare-hazardous mode `needy`, and on `needy_hold` as the mode
  `needy_hold`, in spec 066's registry (mode name = preset name, one
  home): the activating site names the first such kitty (name and id);
  an unacknowledged needy seat fails to load with spec 066's
  missing-acknowledgement text; the exactness, sweep and server-switch
  rules of spec 066 apply unchanged; the registry order is
  `initial_needs`, `needy`, `needy_hold`.
- **FR-010**: The engine MUST answer, for every seated behaviour,
  whether it is eligible to teach: the three existing presets and
  every non-builtin seat answer eligible; `needy` and `needy_hold`
  answer ineligible.
  This is the teacher-eligibility flag spec 066 deferred, landing with
  its first reader.
- **FR-011**: The corpus collector MUST refuse to record a needy seat's
  turns as teacher demonstrations, by reading FR-010's answer, and MUST
  say once per run which seats it refused. (The collector is in
  Experiments' lane; this spec requires the behaviour and the plan
  settles whether the change crosses lanes or is theirs.)
- **FR-012**: For every needy seat, the lab recorder's per-kitty record
  MUST carry, each tick, the masked need set, the episode ordinal
  (counting from 1 at the first onset; 0 before it) and the episode
  phase (resting, held, or released on the release tick, with
  time-released distinguished from level-released). The record is the
  kitty's own entry in the world snapshot plus a binding accessor;
  records of non-needy seats MUST be unchanged. A needy kitty's state
  is its OWN: it appears in no other kitty's view of the world (the fog
  view blanks it on every kitty but the observer), so it never reaches
  a policy observation, a plugin decision request or a corpus row. The
  ground-truth surfaces — the saved world, the server's kitty and world
  endpoints and the corpus collector's `--trace` snapshot — carry it as
  they carry every kitty field (memory included); the served viewer
  shows nothing new.
- **FR-013**: The mask MUST govern only the needy kitty's own choices.
  No world law changes: relief sources, the safeguard relief, distress
  records, Article I bounds, the here-word and consent law for every
  other kitty, and the needy kitty's own needs physics are untouched.
- **FR-014**: No behaviour-API, observation-schema or plugin-wire
  change: the preset is an engine builtin, the decision request to
  external advisors is unchanged, and no new read enters any decision
  except the needy preset's own read of its schedule.
- **FR-015**: The spec MUST name the doubled role of any world set
  built with this preset: an INSTRUMENT for reading the probe (its
  purpose here) versus a TRAINING SOURCE (not licensed by this spec;
  the needy seat teaches nothing by FR-010/FR-011, and any other use of
  such a set as training data takes its own declaration). (The
  Professor's later change (c); binding text pending, see Assumptions.)

- **FR-016**: Nothing in the preset, its parameters, its validation,
  its recorder fields or its tests MAY hard-code the number of needs or
  the list of need names: every per-need value is keyed by need name
  and every per-count value is sized by the engine's single need list,
  so adding a seventh need to the engine extends the preset with no
  change to this feature beyond a default weight for m = 7 and a floor
  entry (owner, 2026-10-26: a seventh need is planned). The validation
  message for a wrong-length mix vector MUST name the current count.

### Key Entities

- **Needy presets**: two builtin behaviours, `needy` (level-released)
  and `needy_hold` (held to the limit); a teacher-preset ladder plus a
  schedule and a mask.
- **Schedule**: the ordered episodes a needy seat runs; every draw a
  pure function of (world seed, kitty id, parameters, draw order), the
  state saved with the world.
- **Episode**: onset tick, masked need set (m needs), release rule
  (level or hold limit), the rest gap that follows; its ordinal.
- **Mask**: the set of needs a needy kitty is currently refusing to
  service or accept relief for; empty while resting.
- **Needy parameters**: the shared config section — N mix weights (one
  per possible count), release level, hold limit, rest-gap range, the
  first-onset levels and their weights, the within-level draw shape.
- **Hazard modes `needy` and `needy_hold`**: spec 066's second and
  third registry entries; each active iff any seat carries that preset.
- **Teacher eligibility**: the per-behaviour answer the collector
  reads; false only for the two needy presets.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: With no needy seat, a full run at a fixed seed is
  byte-identical to the pre-feature engine on every readable surface,
  the full suite is green with zero golden, pin or fixture re-cuts, and
  the defaults stamp is unchanged.
- **SC-002**: Across any two generations of a world at the same seed
  and config, every needy seat's onset ticks, need sets and releases
  are identical. Changing one seat from `teacher` to a needy preset
  (the roster otherwise equal) leaves the generated world identical
  except that kitty's behaviour string and needy state, and until that
  kitty's first onset the two worlds tick identically on every surface
  except those two fields — the schedule's draws reach nothing shared.
  (The master stream deals one seed per kitty per tick and the turn
  order draws scale with the roster, so a roster of a different SIZE is
  a different world; the comparison holds the roster fixed.)
- **SC-003**: In a scratch world with one needy seat at the default
  parameters, run for its first ten episodes: every masked need rises
  monotonically (apart from engine floors) from onset to release; the
  kitty takes zero actions that relieve a masked need; every offered
  relief for a masked need is refused; every onset and release tick
  equals the schedule's declared tick.
- **SC-004**: Under the default parameters every stratum of the
  coverage design is REACHABLE and drawn in proportion to its weight:
  over 10,000 schedule draws, every history level with non-zero weight
  receives first onsets and no zero-weight level does, every m with
  non-zero weight occurs and no zero-weight m does, each of the N needs
  appears in drawn sets, and the observed proportions over levels and
  over m match the weights within two percentage points. The MINIMUM
  episode count per stratum, the number of worlds that buys it and the
  separate first-episode and later-episode reads (the ordinal is a
  covariate, never pooled) are the consumer's: Experiments' declaration
  of the set states them (doctrine rule 10).
- **SC-005**: The lab recorder's record for a needy seat agrees with
  the schedule on every tick of SC-003's run (mask, ordinal, phase);
  the record for every non-needy seat is byte-identical to the
  pre-feature record.
- **SC-006**: Spec 066's seven validation shapes, both sweeps and the
  server hand check all pass with each of `needy` and `needy_hold` as
  the mode, and with both seated at once: an unacknowledged needy seat
  fails to load naming the kitty; an acknowledged one loads; the
  sweeps refuse it outside `experiments/`; the server refuses without
  the switch and serves with it, naming the modes on all three
  surfaces.
- **SC-007**: A corpus collection over a roster with one needy seat
  records zero demonstration rows for that seat and the same rows as
  today for every other seat.

## Design-doctrine check (CLAUDE.md rule 8)

This spec scripts behaviour (a scripted seat that withholds its own
servicing) and touches welfare-visible state, so each doctrine rule was
checked before planning:

- **Rule 12 (relief is always available; kitties cannot suffer) —
  moved choices.** FR-005/FR-013: the preset masks a scripted seat's
  SERVICING, never the world's SUPPLY of relief: food, water, beams,
  partners and the Article I safeguard are untouched. A scripted rule
  refusing relief is not a mind suffering (scripted = exempt, welfare
  practice 2026-09-26). Two guards by construction: the preset can
  never teach (FR-010/FR-011) and can never be applied to a covered
  seat (Edge Cases; it is an engine builtin only). The welfare-cost
  line for any set built with it lives in Experiments' declaration of
  that set; this spec points at it and supplies the mechanism that
  keeps the register honest (FR-012, FR-013).
- **Rule 5 (a teacher may only act on what the student can see) —
  moved a choice.** The schedule is the needy kitty's private state,
  invisible to any student — unlawful for a teacher. It is lawful ONLY
  because this preset never teaches, so FR-010/FR-011 make
  ineligibility a construction, not a convention (the Professor's line
  (a)). No other scripted rule gains a read.
- **Rule 6 (the free register is never scripted) — checked, moved a
  choice.** FR-007: law-named words only; calling stays on (owner,
  "A"), because a cat that wants, calls and refuses relief is the
  realistic signature and is legal to script (the Professor's line
  (b)).
- **Rule 9 (frozen models / pins) — checked, moved nothing.** FR-002:
  the three presets are byte-equal, no observation schema change, no
  reprice, no artifact orphaned; a needy seat exists only in research
  configs under spec 066's rules. FR-003's stream isolation exists so
  any divergence a needy seat causes is attributable to the seat alone.
- **Rule 10 (two-layer gates) — checked, moved nothing.** Gates live
  with the consumer's declaration (Experiments' set); this mechanism
  carries none.
- **Rule 8 (scarcity, not incentives) — moved a choice.** The default
  parameters are declared a COVERAGE design (every stratum reaches a
  minimum count), not a sample of the world; readers read per stratum,
  never pooled (SC-004, Assumptions).
- **Rules 1, 2 (reward, prices) — checked, moved nothing.** No reward
  term, no price: a scripted refusal is neither.
- **Rules 3, 4, 7, 11 — checked, moved nothing.** No rider, edge,
  behaviour built for a world that does not value it (the preset is an
  instrument, not a seat for the served world), or invalidation clause.

## Clarifications

### Session 2026-10-26

- Q: "All but one" — what is the largest masked set, m up to 5 of the six
  needs (her words literally), m up to 4 (the Professor's coverage cap),
  or configurable? → A: Configurable from 1 to all six needs; the mix
  weights cover every m from 1 to 6 and a set's declaration picks which
  strata are reachable. Her words: "C ('all but one' was brainstorming
  and I'm not sure what I was thinking, it should be configurable from
  1-all needs)".
- Q: Does the mask suppress servicing only (the kitty still calls the
  matching law-named want) or servicing and calling? → A: Servicing
  only; calling stays on. Her choice, "A".
- Q: Is the release rule one preset with both parameters as config, two
  presets (release at level; hold to the limit), or release at level
  only? → A: Two presets, one per rule, each its own hazard mode. Her
  choice, "B".
- Q (process): may Experiments forward the Professor's four later design
  changes? → A: "Forward: yes" — Assumption A2 holds the text, received
  the same day.
- Owner note (2026-10-26) on the masked-count range: "Re: the 1-6
  needs, we're planning on adding a 7th need later. We don't need to
  implement now, but ensuring we can add additional needs with minimal
  issue would be nice." → Folded as FR-016: the spec never hard-codes
  six; every per-need or per-count parameter is sized by the engine's
  need count, and a new need joins the preset by joining the engine's
  need list.

## Assumptions

- **A1 — The design notes of 2026-10-25 stand** (she said "All
  reasonable"; recorded, not redone), with the per-need hold table
  corrected against the engine's effects at plan time: eat, drink and
  sleep are relieved only by the actor's own action, so the actor-side
  mask suffices for them; play is relieved by the actor's own play AND
  by a friend's social play with it; cuddle is lowered on both cats by
  a partner's co-sleep or rest and on the groomer by grooming a friend;
  bath is lowered by self-groom and by a friend's groom. So the
  target-side refusal is load-bearing for cuddle, bath and play, and
  the actor-side judgement reads the whole relief set of an action (a
  co-sleep relieves sleep and cuddle; grooming a friend relieves the
  groomer's cuddle). Plain-tile sleep never drops below the off-beam
  sleep floor, so a release level at or below it is degenerate and
  refused. "Grave" is the probe's lab band, not an engine term; any set
  imports its threshold from the probe's declaration.
- **A2 — The Professor's four later design changes, received 2026-10-26
  (forwarded by Experiments on her word "Forward: yes"; verbatim text
  from the note's §Scoring, "Does this change the Q2 schedule design?
  Yes, in four places"), bind as follows.** (1) History length at onset
  is the PRIMARY stratum and the schedule carries no clock: FR-004's
  first-onset levels (at least five, flat or log-uniform within a
  level, weights declared) and SC-004's per-level read. The level
  boundaries are parameters (FR-008). Experiments' knee read has run
  (F-070, main a203e63c, her word "Run the knee read now"): the frozen
  head's grave read falls gradually with the clean history before the
  grave rows, 0.995 at a world's start, 0.978 / 0.970 / 0.852 / 0.658 /
  0.537 / 0.362 after 1 / 2 / 5 / 10 / 20 / 50 clean ticks, 0.358 at
  100, most of the fall over by 20 ticks. The default level edges
  straddle that knee (0–2 / 2–10 / 10–50 / 50–200 / 200 to the end of
  a 20,000-tick world) so no default level pools 0.98 with 0.66; the
  set's declaration owns the edges and may move them — no mechanism
  here depends on the number. (2) The episode ordinal is
  a logged covariate: FR-012; first-episode and later-episode reads
  are never pooled (SC-004). (3) The set's role has doubled, and this
  spec names which role it builds for: an INSTRUMENT for reading the
  frozen head (FR-015). Use of a needy set as TRAINING DATA for a
  Phase 2 head is NOT licensed here and takes its own declaration with
  training-scale counts and a split by world seed. One doctrine
  question the Professor leaves to her and Product, OPEN at this
  write: whether an OBSERVER's observation stream in which a
  scripted-needy friend appears may enter a friend-state head's
  training set. The rule-5 bar was written for the needy cat's own
  turns as teacher rows (its schedule is private state no student can
  see); the head is not a policy and does not act, and rule 6 is
  untouched while the needy cat speaks law-named words only. This spec
  takes no position: FR-010/FR-011 bar the needy seat's TURNS from any
  corpus by construction, and leave observer streams to her ruling in
  the set's declaration. (4) The tie-back gains a second half (the same
  scripted friend going grave after a long clean history, on continuous
  natural rows with no junction, read against the splice's 0.29–0.36;
  then the anticipation read of the descent): a consumer-side read in
  Experiments' declaration; this spec's FR-012 phase and ordinal fields
  and FR-004's clock-free onsets are what make it readable. Unchanged
  per the Professor: schedule over a coin; coverage design read per
  stratum; calling on, servicing suppressed only; the rule-12 line; a
  covered friend forced grave still not recommended.
- **A3 — Base preset**: outside the mask the needy kitty decides as the
  `teacher` preset (every rung on), the Gen 2 corpus demonstrator, so
  the only behavioural difference between a needy world and a teacher
  world is the mask. The alternative (`needs_driven` as base) would
  confound the read with the compat presets' silence.
- **A4 — Default parameters are a coverage design**: N weights over
  m (six today) such as (0.5, 0.2, 0.15, 0.15, 0, 0) with the higher
  counts opened by a set's declaration, a release level such as 90 for
  `needy` (crossings) with `needy_hold` as the sustained-grave variant,
  a hold limit and rest gap long enough for several episodes per
  20,000-tick world, first-onset levels straddling the F-070 knee (A2);
  exact numbers are the plan's, read per stratum (play gets its own
  cell: the weakest named need in F-068 at 0.783). The spec declares
  the shape; no default is a model of the world.
- **A5 — Spec 066 is the only hazard machinery**: no new switch, table
  or sweep rule; the second and third registry entries plug into what
  landed in PR #469, and the registry list is tied to the enum at this touch
  (the N4 note from #469's review).
- **A6 — Scope boundaries**: observation emission for builtin seats
  (so a scripted seat could be recorded through the observation path)
  is separable and NOT asked (the rl episode's recorder path); the
  served viewer shows nothing new; `docs/deploy/` is untouched.
- **A7 — Downstream**: Experiments' needy world set, its declaration
  and welfare-cost line wait for her word after this spec lands; its
  reads (per stratum, the anticipation read, the tie-back) are theirs.
