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

An experimenter seats one kitty on the `needy` preset. From the world's
first tick that kitty behaves like today's scripted teacher. At a
declared onset tick its schedule opens an episode: a drawn set of one or
more needs is MASKED, and from then on the kitty stops servicing those
needs itself and refuses relief for them offered by friends, while it
keeps servicing every other need, keeps calling for what it wants, and
the world keeps offering relief exactly as before. The masked needs
climb. When they reach the declared release level, or the declared hold
time passes, the episode releases: the mask lifts, the kitty services
them again, and after a declared rest the next episode opens with a
fresh draw. Over a long world the kitty demonstrates single-need,
multi-need and all-but-one patterns, each with a known onset tick.

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
   m, **When** a long world runs, **Then** episodes with m = 1, m = 2,
   m = 3 and the all-but-one count all occur, in proportions that match
   the weights within the run's sampling noise.
4. **Given** a release level L and a hold limit T, **When** an episode's
   masked needs all reach L before T ticks, **Then** the episode
   releases at that tick; **When** they do not, **Then** it releases at
   onset + T.
5. **Given** the same seed and config, **When** the world is generated
   twice, **Then** every onset tick, need set and release is identical;
   **Given** a different world seed or a different kitty id, **Then**
   the schedule differs.
6. **Given** two needy seats in one roster, **When** the world runs,
   **Then** each has its own schedule and neither's draws move the
   other's.

---

### User Story 2 - A world without a needy seat is byte-identical to today (Priority: P1)

An operator runs any existing config on the new engine. No kitty is
seated on `needy`, so nothing changes: the three existing presets decide
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

1. **Given** any config with no `needy` seat and no needy parameter
   section, **When** a full run executes, **Then** every readable output
   (serialized config, defaults stamp, world snapshot stream, decision
   log, boot log) is byte-identical to the pre-feature engine at the
   same seed.
2. **Given** the `needs_driven`, `playful` and `teacher` presets,
   **When** they decide, **Then** their decisions are byte-equal to the
   pre-feature engine's on every seeded world.
3. **Given** a config that writes the needy parameter section but seats
   no kitty on `needy`, **When** it loads, **Then** it validates, the
   parameters are inert, and the generated world is identical to the
   same config without the section.

---

### User Story 3 - A needy seat is a welfare-hazardous mode and is treated as one (Priority: P2)

Spec 066 made every welfare-hazardous mode something that must be
acknowledged by name to load, kept out of every served and shipped
config, and served only on stated intent. Seating a kitty on `needy` is
the second such mode. A config with a needy seat loads only if it
acknowledges `needy_preset`; the shipped-config sweeps refuse such a
config anywhere outside `experiments/`; the server serves it only with
`--allow-welfare-hazard` and then says so.

**Why this priority**: this is why spec 066 exists: a research-only
behaviour that manufactures hardship must never be seated by accident,
and a world that carries it must be visibly hazardous from tick 0.

**Independent Test**: spec 066's seven failure shapes run against a
needy-seat config with the mode name `needy_preset`; the sweeps' self-
tests run with a needy-seat file; the server hand check runs with a
needy-seat config.

**Acceptance Scenarios**:

1. **Given** a config seating one kitty on `needy` with no
   `[welfare_hazard]` table, **When** it loads, **Then** loading fails
   naming `needy_preset`, the seat (which kitty, by name and id) that
   activates it, and the line to add.
2. **Given** the same config acknowledging `["needy_preset"]`, **When**
   it loads, **Then** it validates; **Given** it also carries a raised
   distressed start, **Then** it must acknowledge both modes, in
   registry order, or fail naming the missing one.
3. **Given** an acknowledged needy-seat config outside `experiments/`,
   **When** either shipped-config sweep runs, **Then** it fails naming
   the file and `needy_preset`.
4. **Given** an acknowledged needy-seat config, **When** the server
   starts without the switch, **Then** it refuses before any world
   exists; **When** it starts with the switch, **Then** the boot line,
   `GET /config` and the key-settings row name `needy_preset`.

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
   **When** read for `needy`, **Then** it is ineligible.
2. **Given** a corpus collection over a roster with one needy seat,
   **When** the collector runs, **Then** it records no demonstration row
   for that seat, says so once in its output, and records every other
   seat as today.

---

### Edge Cases

- **A masked need already at or above the release level at onset**:
  the episode still opens; it holds until every masked need is at or
  above the release level (so a need that is already there waits for
  the others) or until the hold limit, whichever comes first.
- **Release level below an engine floor**: plain-tile sleep stops at
  the engine's off-beam sleep floor, so a sleep release level at or
  below that floor could never be reached in a cold world; validation
  refuses it. More generally a need the engine cannot hold at the
  release level is not a stratum, and the per-need floors are declared
  in the parameter section (Assumptions).
- **The hold limit expires with no need at the release level**: the
  episode releases anyway; the recorder's phase says so, so a reader
  can separate level-released from time-released episodes.
- **Two needy seats**: each derives its own schedule from (world seed,
  its kitty id); neither consumes the other's draws or the world's
  master stream.
- **A needy seat plus a distressed start (spec 065) in one config**:
  both modes are active; the acknowledgement must name both, in
  registry order (`initial_needs`, `needy_preset`).
- **The needy parameter section written, no needy seat**: inert and
  valid (User Story 2, scenario 3); the section is not a hazard, the
  seat is.
- **A needy kitty asked to help a friend** (groom response, co-sleep
  proposal from another cat): unmasked needs do not change how it
  answers; the mask only stops it from accepting relief FOR a masked
  need and from seeking one.
- **A friend keeps proposing to a needy kitty every tick**: refusals go
  through the engine's existing target-side gate and are recorded as
  refusals are today; no new record type.
- **A policy or plugin seat**: cannot carry the preset. `needy` is an
  engine builtin; the mask exists nowhere else, so a covered mind can
  never be masked (doctrine rule 12, second guard).
- **The all-but-one pattern on a six-need cat**: her words say "all but
  one"; the Professor's coverage design caps the drawn count at four.
  Which count the top stratum means is the first clarification below.
- **Save and resume**: a needy kitty's schedule is a pure function of
  (world seed, kitty id, parameters), so a resumed world continues the
  same schedule without storing it; the episode phase at the resume
  tick is re-derived, not stored.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST register a fourth builtin behaviour
  preset named `needy`, seatable like `needs_driven`, `playful` and
  `teacher` through a kitty's `behavior` setting, and nowhere else.
- **FR-002**: With no kitty seated on `needy`, the engine MUST be
  byte-identical to the pre-feature engine on every readable surface:
  the three existing presets' decisions, every seeded draw, the
  serialized config, the defaults stamp, the world fingerprint, the
  snapshot stream and the boot log. Zero golden, pin or fixture
  re-cuts.
- **FR-003**: A needy seat's SCHEDULE — the sequence of episodes, each
  with an onset tick, a masked need set and a release rule — MUST be a
  deterministic function of the world seed, the kitty's id and the
  declared parameters, derived without consuming the world's master
  stream or any other kitty's private stream, so the same seed
  reproduces the identical schedule and no other kitty's draws move.
- **FR-004**: Each episode MUST have: an onset tick (the previous
  release plus a rest gap drawn from a declared range; the first onset
  drawn from a declared, deliberately wide range so onsets span short
  and long histories — see Clarifications and Assumptions on the
  Professor's later change (a)); a masked need set of m distinct needs,
  m drawn by declared weights (the default mix is a coverage design,
  not a model of the world); and a release rule: release when every
  masked need is at or above the declared release level, or when the
  declared hold limit has passed since onset, whichever is first.
  [NEEDS CLARIFICATION: Q1 — does the top stratum "all but one" mean
  m = 5 of the six needs (her words) or m = 4, the Professor's cap?
  Options under Clarifications.]
- **FR-005**: While a need is masked, the needy kitty MUST NOT choose
  any action whose purpose is to relieve that need (the serious ladder,
  the take-what-is-here rung and the groom-response rung all skip it),
  and MUST refuse relief for that need offered by another kitty through
  the engine's existing target-side consent gate (co-sleep and cuddle
  lower cuddle on both cats; a friend's groom lowers the target's bath;
  for these the target-side refusal is load-bearing). Needs not masked
  are serviced exactly as the base preset services them.
  [NEEDS CLARIFICATION: Q2 — does the mask suppress servicing only,
  with the kitty still calling the matching law-named want (the
  Professor's recommendation: a cat that wants, calls and refuses
  relief is the realistic signature), or servicing and calling?]
- **FR-006**: Outside the mask, the needy preset MUST decide exactly as
  the `teacher` preset (every rung on): the only difference between a
  needy kitty and a teacher-preset kitty is the mask. (Assumption A3;
  the base preset is a design default, not a ruling.)
- **FR-007**: The needy kitty MUST speak law-named words only (want,
  here, purr, wait-for-me), never a sound-named word, and its calling
  MUST follow the same rules as the base preset's.
- **FR-008**: The preset's parameters MUST be configuration: the mix
  weights over m, the release level, the hold limit, the rest-gap
  range, the first-onset range and the per-need release floors, each
  with a declared default, validated at load (weights non-negative and
  not all zero; release level in the need range and above every
  declared floor; hold limit and gaps positive; the sleep release level
  above the engine's off-beam sleep floor), and inspectable on the
  served config surface like any other section. Writing the section
  with no needy seat is valid and inert.
- **FR-009**: Seating any kitty on `needy` MUST register as the
  welfare-hazardous mode `needy_preset` in spec 066's registry: the
  activating site names the kitty (name and id); an unacknowledged
  needy seat fails to load with spec 066's missing-acknowledgement
  text; the exactness, sweep and server-switch rules of spec 066 apply
  unchanged; the registry order is `initial_needs`, `needy_preset`.
- **FR-010**: The engine MUST answer, for every seated behaviour,
  whether it is eligible to teach: the three existing presets and
  every non-builtin seat answer eligible; `needy` answers ineligible.
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
  phase (resting, held, releasing, with time-released distinguished
  from level-released). Records of non-needy seats MUST be unchanged.
  The served viewer and the plugin wire are out of scope.
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

### Key Entities

- **Needy preset**: the fourth builtin behaviour; a teacher-preset
  ladder plus a schedule and a mask.
- **Schedule**: the ordered episodes a needy seat will run, a pure
  function of (world seed, kitty id, parameters).
- **Episode**: onset tick, masked need set (m needs), release rule
  (level or hold limit), the rest gap that follows; its ordinal.
- **Mask**: the set of needs a needy kitty is currently refusing to
  service or accept relief for; empty while resting.
- **Needy parameters**: the config section — mix weights, release
  level, hold limit, rest-gap range, first-onset range, per-need
  release floors.
- **Hazard mode `needy_preset`**: spec 066's second registry entry;
  active iff any seat is `needy`.
- **Teacher eligibility**: the per-behaviour answer the collector
  reads; false only for `needy`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: With no needy seat, a full run at a fixed seed is
  byte-identical to the pre-feature engine on every readable surface,
  the full suite is green with zero golden, pin or fixture re-cuts, and
  the defaults stamp is unchanged.
- **SC-002**: Across any two generations of a world at the same seed
  and config, every needy seat's onset ticks, need sets and releases
  are identical; adding a needy seat to a roster leaves the master
  stream and every other kitty's private draw sequence byte-identical.
- **SC-003**: In a scratch world with one needy seat at the default
  parameters, run for its first ten episodes: every masked need rises
  monotonically (apart from engine floors) from onset to release; the
  kitty takes zero actions that relieve a masked need; every offered
  relief for a masked need is refused; every onset and release tick
  equals the schedule's declared tick.
- **SC-004**: Over a declared number of long worlds at the default
  parameters, every stratum of the coverage design (each value of m
  the weights allow, crossed with each of the six needs, crossed with
  short and long history at onset) reaches the declared minimum
  episode count, and the observed mix over m matches the weights within
  sampling noise.
- **SC-005**: The lab recorder's record for a needy seat agrees with
  the schedule on every tick of SC-003's run (mask, ordinal, phase);
  the record for every non-needy seat is byte-identical to the
  pre-feature record.
- **SC-006**: Spec 066's seven validation shapes, both sweeps and the
  server hand check all pass with `needy_preset` as the mode: an
  unacknowledged needy seat fails to load naming the kitty; an
  acknowledged one loads; the sweeps refuse it outside `experiments/`;
  the server refuses without the switch and serves with it, naming the
  mode on all three surfaces.
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
  choice.** FR-007: law-named words only; calling stays on (pending
  Q2), because a cat that wants, calls and refuses relief is the
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

Three questions the owner's words and the Professor's design leave
open; each changes the parameter space or the recorded signature.

- **Q1 (FR-004)**: "All but one" — the largest masked set. A: m up to
  5 of the six needs, her words taken literally (the top stratum masks
  everything but one need). B: m up to 4, the Professor's coverage cap
  (all-but-one read as "most needs", keeping two needs serviced so the
  kitty stays mobile and the pattern separable). C: both as config, cap
  declared per set.
- **Q2 (FR-005)**: the mask's reach. A: servicing only — the kitty
  still calls the matching law-named want (recommended by the
  Professor; the realistic signature; the message block is in the
  probe's input). B: servicing and calling — a silent sufferer, the
  harder read.
- **Q3 (FR-004)**: the release rule's shape. A: one preset, both
  parameters (release level and hold limit) as config, with "hold until
  the limit" expressed by a release level the needs cannot reach. B:
  two presets, one releasing at level and one holding to the limit. C:
  release at level only, no hold limit.

## Assumptions

- **A1 — The design notes of 2026-10-25 stand** (she said "All
  reasonable"; recorded, not redone): the rule-12 paragraph shape
  above; the per-need hold table — eat, drink, play and sleep are
  relieved only by the actor's own action, so the actor-side mask
  suffices; plain-tile sleep stops at the off-beam sleep floor, so the
  sleep release level must sit above it; cuddle is lowered on both cats
  by a partner's co-sleep or cuddle and bath by a friend's groom, so for
  those two the target-side refusal is load-bearing. "Grave" is the
  probe's lab band, not an engine term; any set imports its threshold
  from the probe's declaration.
- **A2 — The Professor's four later design changes bind here where
  named, pending the full text** (held by Experiments for her word to
  forward; substance as Experiments named it 2026-10-26): (a) history
  length at onset is the PRIMARY stratum, with a clock-free wide onset
  range of five or more levels — FR-004's first-onset range and SC-004's
  history stratum are written to that shape and the exact levels wait
  for the text; (b) the episode ordinal is logged — FR-012; (c) the
  set's doubled role, instrument versus training source, is named —
  FR-015; (d) the natural-rows half of the tie-back — a consumer-side
  read in Experiments' declaration, not a mechanism here; recorded so
  the declaration can cite it. When the text arrives, this section is
  updated and any binding difference goes through `/speckit-clarify`.
- **A3 — Base preset**: outside the mask the needy kitty decides as the
  `teacher` preset (every rung on), the Gen 2 corpus demonstrator, so
  the only behavioural difference between a needy world and a teacher
  world is the mask. The alternative (`needs_driven` as base) would
  confound the read with the compat presets' silence.
- **A4 — Default parameters are a coverage design**: weights over m
  such as (0.5, 0.2, 0.15, 0.15), a release level such as 90 (crossings)
  with 95 or "hold" as the sustained-grave variant (Q3), a hold limit
  and rest gap long enough for several episodes per 20,000-tick world,
  per-need floors from the engine; exact numbers are the plan's, read
  per stratum (play gets its own cell: the weakest named need in F-068
  at 0.783). The spec declares the shape; no default is a model of the
  world.
- **A5 — Spec 066 is the only hazard machinery**: no new switch, table
  or sweep rule; the second registry entry plugs into what landed in
  PR #469, and the registry list is tied to the enum at this touch
  (the N4 note from #469's review).
- **A6 — Scope boundaries**: observation emission for builtin seats
  (so a scripted seat could be recorded through the observation path)
  is separable and NOT asked (the rl episode's recorder path); the
  served viewer shows nothing new; `docs/deploy/` is untouched.
- **A7 — Downstream**: Experiments' needy world set, its declaration
  and welfare-cost line wait for her word after this spec lands; its
  reads (per stratum, the anticipation read, the tie-back) are theirs.
