# Feature Specification: Say-Surface Finalization

**Feature Branch**: `033-say-surface`

**Created**: 2026-08-15

**Status**: Draft

**Input**: User description: "The phase-1 wall's engine item (owner-approved
requirements, Experiments 2026-08-15, reviewed and reconciled by Product;
vocabulary architecture locked by the owner the same night): finalize the
meow channel's say-surface as the codec's last move before the character-era
freeze. The vocabulary becomes a closed two-tier language — law-named words
whose grounding predicate IS their meaning (Want*, the new Here* family,
Purr), and a sound-named free register whose names claim nothing (mew, née
follow_me; chirp; and two reserves, trill and ekekek) so the cats decide
what they mean. Grounding stays honest (a Here word requires its referent
adjacent), vocabulary is config-armable so experiments never fork the
engine, the observation digest widens to carry fifteen kinds, the artifact
loader gates the generation honestly, and the language gets its living
documents: the refreshed encodings contract and the meows.md field guide.
One wall, one re-baseline; the live world is untouched until the phase-1
generation seats."

## Clarifications

### Session 2026-08-15 (pre-spec, settled with the owner and Experiments)

- Q: Final vocabulary architecture? → A: Owner-locked, two tiers, fifteen
  speakable kinds. **Law-named** (enforced semantics — the grounding
  predicate IS the meaning): the six Want kinds, Purr, and the four new
  Here kinds. **Sound-named** (the free register — names denote the
  vocalization, claim nothing about meaning; the cats decide): mew (renamed
  from follow_me), chirp, and reserves trill and ekekek. The FollowMe
  lesson made law: its designed meaning ("come along") was overwritten by
  the cats ("I'm coming, stay put"), so free words now carry names that
  cannot be contradicted.
- Q: Why rename follow_me → mew? → A: The name asserted a meaning the cats
  rejected; a sound-name cannot lie. Same head index (3), same digest
  column, full history carried over: meows.md records "I'm coming, stay
  put" as mew's current observed meaning, and the fog-era
  designed-meaning-revival prediction re-registers under mew.
- Q: Why reserves in the layout now? → A: The post-fog language-capacity
  experiment ("what is the marginal value of a word?") becomes pure
  config: arms enable 2/3/4 free words by flag with no codec move, so the
  say-surface freeze stays airtight. Active-vs-reserve is only the flag
  default; nothing structural distinguishes chirp from trill from ekekek.
- Q: Here* naming? → A: Renamed by the owner from the drafting name Found*
  (HereFood, HereWater, HereCritter, HereSunbeam; wire `here_food` /
  `here_water` / `here_critter` / `here_sunbeam`). Her rationale: "here"
  IS the adjacency invariant as a word — present-tense, proximate, cannot
  connote stale discovery; it matches emitter-tracking (the beacon points
  at the speaker: here); a hosting cat re-announcing states a still-true
  fact; and it completes the channel's grammar — Want (I lack) / Here (I
  have, come share) / Purr (state) / free sounds (the cats' own) /
  Silent. Referents are resource-named (HereFood, not HereEat): the word
  points at the resource, not the act.
- Q: Here* grounding — what does "here" mean pre-fog? → A: The referent is
  adjacent to the speaker. For Food/Water/Critter: the exact predicate of
  the corresponding *adjacency-gated* action. For Sunbeam: an explicit
  adjacency predicate (the one stated exception — no sunbeam action exists
  to share; see FR-002).
- Q: HereCritter via "Chase-or-Play legal"? → A: Play only (owner ruling,
  2026-08-15: "play predicate only — adjacency is a requirement for all of
  the Found expressions, not just visibility"). Chase legality is
  distance-unbounded — legal whenever the critter exists anywhere — which
  would make the word vacuous pre-fog and misleading under
  emitter-tracking. Play-critter legality already requires adjacency. The
  family-wide rule: every Here kind requires ADJACENCY to its referent —
  seeing is never enough, in any vision regime.
- Q: Sound-word grounding? → A: None, by design — the free register is
  cooldown-gated only (exactly follow_me's existing law: `can_meow` alone;
  verified in `message_legal`, so mew's law is unchanged by its rename).
  The adjacency invariant governs the Here family; sound-words are free.
- Q: How do viewers see sound-words? → A: As-is ("mew!", "chirp!",
  "ekekek!") — viewers hear what the cats hear; meaning lives in
  meows.md's observed column for the curious. Display translation is
  explicitly OUT of engine scope (client work, arrives with the wall
  kickoff).
- Q: Does the action menu widen? → A: No. Messages ride the separate
  message head; the 34-entry activity menu is unchanged.
- Q: Do Here* digest entries pin the resource location? → A: No — standard
  emitter-tracking, never pinned coordinates (owner pin).
- Q: Does the engine preserve the announced referent? → A: No — the
  guarantee is emission-time truth only; preservation is a learned
  equilibrium (owner pin).
- Q: FoundKitty[id] (historical drafting name; would be HereKitty)? → A:
  Rejected with citable rationale (owner-reviewed): it roster-couples the
  head (a fifth cat would resize the codec) or requires factored
  kind+target messages (a different architecture, its own future
  generation); third-party reference cannot ride the emitter-tracking
  digest; pack-location under fog is the purr contact-call's designed
  destiny. Typed critter variants (bug/greeble) likewise rejected: the
  hearer's approach disambiguates, and greeble referents are
  viewer-invisible.
- Q: Pumpkin/Clementine/sunbeam values? → A: Config rider PR, outside this
  spec (owner-valued: Pumpkin eat 0.6/sleep 0.2/bath 0.1; Clementine
  cuddle 0.7/play 0.3/bath 0.1; sunbeam 7.0).
- Q: What does the digest's intensity column carry for the seven new
  kinds? → A: **0.0 for all seven** (owner verdict, discussed with
  Experiments): the social-word rule extends uniformly — intensity remains
  exclusively "the speaker's need pressure," carried by want-kinds only.
  The want-kind precedent does not license a Here* richness stamp because
  the rot runs in opposite directions: a stamped need-value ages
  conservatively (hunger only rises post-emission, so the stale float
  UNDERSTATES — the ask is always at least as urgent as advertised), while
  a stamped richness would age anti-conservatively (servings only fall,
  possibly eaten by the announcer, so the stale float OVERSTATES — worst
  exactly under contention). Safe rot vs lying rot. Supporting: the
  one-freshest-emitter-per-kind digest structure means no hearer ever
  compares two offers, so richness's use-case is structurally absent; a
  HereSunbeam richness would smuggle beam-expiry information in via a
  float; and 0.0 preserves a richness stamp as a FUTURE option at any
  generation boundary (a stamp-semantics change, no schema move) —
  registered revisit trigger: fog-era hosting measurements showing cats
  declining trips richness would have saved.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A cat can announce what is here (Priority: P1)

A cat standing at a resource can now say so: four new law-named kinds — the
**Here family** — join the spoken vocabulary. HereFood at a stocked bowl,
HereWater beside water, HereCritter beside a scurrying bug (or greeble),
HereSunbeam on or beside a live beam. Each announcement is grounded — legal
exactly when the referent is *adjacent to the speaker* — so the meow law
stays honest: a cat can never announce what is not at its whiskers. Hearers
receive the announcement through the existing message digest, tracking the
**speaker** (who stays audible where they are), never a map coordinate. For
the first time the channel carries altruistic reference — "there is food,
here, with me" — rather than only need.

**Why this priority**: This is the wall's reason to exist, and the words
cover every referent class through the fog era: consumables (food, water),
the churn class memory tokens won't cover (critters), and the non-rival
convening resource (sunbeam — the announcer keeps warm while sharing, so
announce-and-host is its natural move, and it is the convening mechanism
the shared-warmth piles of spec 031 lack under fog).

**Independent Test**: In a test world, place a cat adjacent to each referent
in turn; the matching Here kind is legal there and illegal on bare grass;
after emission, every other cat's next observation carries the announcement
in the digest with the speaker's live offset; the meow event appears in
`recent_meows` like any other kind.

**Acceptance Scenarios**:

1. **Given** a cat for whom Eat is legal (adjacent stocked bowl), **When**
   it proposes HereFood, **Then** the message is accepted, broadcast, and
   appears in other cats' digests tracking the speaker's position.
2. **Given** a cat on bare grass (no referent adjacent), **When** it
   proposes any Here kind, **Then** the message downgrades to Silent with
   the paired activity untouched (spec-028 enforcement, unchanged).
3. **Given** a cat beside a bowl whose servings have run out, **When** it
   proposes HereFood, **Then** the message downgrades to Silent — an empty
   bowl is not "food here" (the shared predicate excludes it, exactly as
   it excludes Eat).
4. **Given** a cat adjacent to a critter, **When** it proposes HereCritter,
   **Then** the message is accepted — and **Given** the only critter in the
   world is across the map (Chase would be legal; Play would not), **Then**
   HereCritter downgrades to Silent: the word means here, with me — never
   "exists somewhere".
5. **Given** a cat on or beside an unexpired sunbeam, **When** it proposes
   HereSunbeam, **Then** the message is accepted; on a beamless tile it
   downgrades to Silent.
6. **Given** a cat that honestly announced HereFood and then ate the last
   servings itself, **When** the bowl despawns, **Then** no engine rule was
   violated: the guarantee is emission-time truth only (see FR-016).

---

### User Story 2 - The cats get words of their own (Priority: P2)

The channel gains a **free register**: sound-named words that carry no
grounding predicate and no designed meaning — the engine enforces only the
cooldown, and what the word means is the cats' to decide. The register's
first member is **mew**, the renamed follow_me (same position, same
history — its law was already cooldown-only, so nothing changes but the
name that used to claim a meaning the cats had overwritten). **chirp** joins
as the second free word, active at phase 1. **trill** and **ekekek** enter
the layout as reserves — config-flag off, never-legal, zero training
presence — so the post-fog language-capacity experiment ("what is the
marginal value of a word?") is pure configuration: arms enable 2, 3, or 4
free words by flag, no codec move, the freeze intact.

**Why this priority**: The FollowMe lesson, made law. Designed meanings die
on contact with the cats; the free register stops pretending otherwise, and
the reserves make the next generation's central experiment possible without
touching the engine again.

**Independent Test**: mew and chirp are legal for any cat off cooldown
regardless of world state; trill and ekekek are never legal under default
config but become legal when their flags are enabled; observation and mask
shapes are identical in all cases; renaming left mew's head index, digest
column, and legality byte-identical to follow_me's.

**Acceptance Scenarios**:

1. **Given** any cat off cooldown on bare grass, **When** it proposes mew
   or chirp, **Then** the message is accepted — no grounding applies to the
   free register.
2. **Given** the default configuration, **When** any cat proposes trill or
   ekekek, **Then** the proposal downgrades to Silent on every tick (the
   reserve flags default off); **Given** a config enabling them, **Then**
   they behave exactly as chirp does.
3. **Given** the rename, **Then** mew occupies follow_me's head index (3)
   and digest column, with legality unchanged (cooldown only), and the
   wire name is `mew`.

---

### User Story 3 - Experiments arm vocabulary by config, never by fork (Priority: P2)

An experimenter turning vocabulary on or off for a training arm edits the
world configuration, not the engine: every speakable kind has an enable
flag under the meow section. A disabled kind is simply never legal — its
mask entry is always off, proposals downgrade to Silent — while every
layout (digest width, head width, mask width, menu) is **schema-fixed and
identical whatever the flags say**. Two configs with different vocabularies
produce observations of identical shape; only legality differs.
Active-vs-reserve is nothing more than the flag's default value.

**Why this priority**: The roadmap's say-surface stability principle:
vocabulary semantics are config-gated legality, so the phase-1, phase-2,
and post-fog experiment grids vary words by flag while every artifact
speaks one schema.

**Independent Test**: Boot two worlds differing only in one kind's flag;
observation lengths and mask lengths are identical; the kind is emittable
in one and never-legal in the other; an unknown key in the meow section
still refuses to load (strict-config posture unchanged).

**Acceptance Scenarios**:

1. **Given** a config disabling HereFood, **When** a cat at a stocked bowl
   proposes it, **Then** the proposal downgrades to Silent and the mask
   entry for HereFood is false on every tick.
2. **Given** two configs differing only in enable flags, **Then**
   observation, mask, and digest dimensions are identical between them.
3. **Given** a config omitting the flags entirely, **Then** the defaults
   apply — every kind enabled except the reserves (trill, ekekek), which
   default off — and the config loads (defaults documented, echoed on the
   config endpoint).
4. **Given** a config with a misspelled flag key, **Then** startup refuses
   with an error naming the field (deny-unknown-fields posture, PR #114).

---

### User Story 4 - The generation gate is honest on both sides (Priority: P2)

The observation digest widens to carry fifteen kinds, so the observation,
action-encoding, and mask schema versions all advance. A policy artifact
built for the new schemas loads and serves; every existing artifact (which
pins the old schemas) is refused at startup with an error naming the
mismatched pin — never a shape accident, never a silent misread. The CI
parity gate continues to run on every pass against a new oracle fixture at
the new layout, so the hand-rolled forward can never drift from checkpoint
semantics across the bump.

**Why this priority**: The wall's safety property. Spec 030's loader
machinery already dispatches on version and pins; this story is the
controlled turn of those dials — and the last action-encoding turn before
the freeze.

**Independent Test**: A new-schema v3 fixture loads and serves a kitty; the
committed spec-030 oracle (old pins) is refused naming
`observation_schema`; the new oracle fixture passes parity ≤ 1e-4 with
greedy-argmax agreement in CI.

**Acceptance Scenarios**:

1. **Given** a v3-format artifact whose header pins the new schema
   versions, **When** the server boots with it seated, **Then** it
   validates, logs its content hash, and serves.
2. **Given** any artifact pinning the previous observation, action, or mask
   schema, **When** the server boots with it seated, **Then** startup fails
   with an error naming the artifact, the pin, and the expected value.
3. **Given** the new oracle fixture and parity rows, **When** CI runs,
   **Then** the parity gate passes at the existing tolerance (≤ 1e-4,
   exact greedy argmax) with ≥ 100 rows including vacancy-stress rows and
   rows where the new kinds (and the reserves in particular) are
   never-legal.
4. **Given** the wall lands on main before any new-schema artifact is
   certified, **Then** main's shipped configuration seats no policy
   behaviors (scripted seats, spec-028-wall precedent) and every
   shipped-config CI gate passes.

---

### User Story 5 - The language has a field guide (Priority: P3)

A reader — the owner, a plugin author, a future contributor — opens
`docs/meows.md` and finds the kitty grammar: what every word of the meow
channel means. It is the companion to `docs/plugins.md` (how outside minds
talk to the engine) and `policies/purrsonality.md` (who the minds are);
this one is what the words MEAN. It opens with the grammar in one breath —
Want (I lack) / Here (I have, come share) / Purr (I'm content) / the free
sounds (the cats' own words) / Silent — and states the two-tier naming
doctrine: law-named words mean what their predicate enforces; sound-named
words mean whatever the cats make them mean. Then every word gets three
columns: **the law** (when it is legal: grounding predicate, cooldown,
per-kind flag; what the engine guarantees: emission-time truth, the
adjacency invariant), **the intent** (what the word was designed to mean —
for sound-words, explicitly "none; the name is the sound"), and **the
observed meaning** (what the cats actually use it for, with evidence links
— where the doc gets its soul, because designed and learned meanings
diverge: purr was designed as contentment and became a contact call; mew,
as follow_me, was designed as "come along" and became "I'm coming, stay
put" — the divergence that named the free register; the doter dialect
inverted purr's spatial meaning). WaitForMe gets its footnote as the
engine's own word — the yield rule speaks it, policies cannot. The doc is
born at the freeze, complete at fifteen words, with the Here* and chirp
observed-meaning cells honestly marked: law fixed (or free), meaning awaits
the cats — and the reserves marked "not yet spoken anywhere."

**Why this priority**: The vocabulary freeze is the one moment the doc can
be born complete, and the observed-meaning column is the project's most
charming empirical fact — designed meanings and learned meanings divide,
and only a maintained document can keep telling that story as fog rewrites
it.

**Independent Test**: The doc exists with an entry per speakable word plus
Silent and the WaitForMe footnote; every law cell matches this spec's
predicates and the config's dials; every observed-meaning claim carries an
evidence link that resolves; the unwritten cells say so.

**Acceptance Scenarios**:

1. **Given** the merged wall, **Then** `docs/meows.md` exists covering all
   fifteen speakable kinds plus Silent, each with law / intent / observed
   columns; the law cells agree with FR-002's predicates and FR-002b's
   free-register rule verbatim; the unwritten observed cells are marked
   awaiting the cats.
2. **Given** the doc's digest section, **Then** a plugin author can write a
   listening cat from it (what hearers receive: freshest emitter per kind,
   live position, the freshness window) without reading engine source.
3. **Given** a future spec that changes the vocabulary, **Then** its task
   list must include updating `docs/meows.md` (the rule is stated in the
   doc's own preamble and in FR-021).

---

### Edge Cases

- **Announce-then-consume**: a speaker may honestly announce HereFood and
  then eat the remaining servings; hearers may arrive at bare grass.
  Lawful by design — see FR-016. Preservation ("hosting") is a learned
  equilibrium, measured by Experiments in the fog era, never an engine
  rule. (HereSunbeam is the family's exception by nature, not by rule: the
  beam is non-consumable and its warmth is pile-non-rival under spec 031,
  so the announcer loses nothing by hosting.)
- **The referent leaves**: a bowl drains, a critter scurries, a beam
  expires while the announcement is still fresh in the digest. The entry
  tracks the *speaker*, so it can never point at a stale location —
  hearers find whatever the speaker is now near. This is the
  emitter-tracking choice doing its job (FR-005).
- **Emitter walks away**: the digest tracks the speaker's live offset, so a
  Here* entry points wherever the speaker now is. Deliberate: it
  structurally favors announce-and-host over announce-and-abandon.
- **Cooldown**: the per-cat-per-kind cooldown (spec 028) applies to every
  new kind — law-named and sound-named alike — with no new machinery; for
  the free register it is the ONLY law.
- **The rename and old data**: MessageKind serializes by name, so
  pre-wall serialized worlds and event fixtures containing `follow_me` do
  not load on the new binary. Acceptable by construction: the served box
  never crosses the wall with its save (the phase-1 cutover is a fresh
  world for roster reasons regardless), and repo test fixtures are updated
  in the arc. The rename is part of the same generation gate the schema
  pins already enforce.
- **WaitForMe stays out of the head**: it remains emitted by the yield
  rule only; the speakable vocabulary is Silent + 15, and WaitForMe is not
  among them. (It stays in the message enum and the wire, and is not
  renamed — it is the engine's word, and the engine means what it says.)
- **Never all-silent**: Silent remains structurally legal on every tick
  (mask index 0 always true), flags notwithstanding.
- **Digest at rest**: a world where no new kind is ever spoken carries
  all-zero entries in the seven new digest columns — vacancy encoding
  unchanged. The reserve columns are all-zero in every world until the
  post-fog experiment arms them.
- **Greebles**: HereCritter over a greeble is lawful (greebles are
  critters a cat can play with); the viewer's greeble secrecy is a
  rendering rule and unaffected — one more reason the typed-variant design
  was rejected.
- **Roster growth interplay**: the observation's kitty slot count stays 3
  even when the roster grows to 5 (the phase-1 config rider). Someone
  always unslotted is the next generation's design thesis — the slot
  count is a deliberate constant of schema 4, not an omission to fix.
- **Existing digest columns**: existing kinds keep their digest positions
  (mew keeps follow_me's); the seven new columns append. No existing field
  moves.

## Requirements *(mandatory)*

### Functional Requirements

**The vocabulary**

- **FR-001**: The message vocabulary MUST reach its final two-tier form:
  (a) follow_me is RENAMED **mew** (enum Mew, wire `mew`), keeping its
  head index (3), digest column, and cooldown-only legality byte-for-byte;
  (b) four law-named kinds append — HereFood, HereWater, HereCritter,
  HereSunbeam (wire `here_food`, `here_water`, `here_critter`,
  `here_sunbeam`), head indices 9–12; (c) three sound-named kinds append —
  chirp, trill, ekekek (wire `chirp`, `trill`, `ekekek`), head indices
  13–15. Every existing kind keeps its normative position (the spec-028
  append pattern); HEAD_KINDS reaches fifteen and the speakable head
  becomes Silent + 15. This set is FINAL through the fog era: the
  say-surface freeze declared by the roadmap is complete with this spec,
  and the rejected alternatives are recorded in Clarifications with their
  rationale so a future proposal must argue against it.
- **FR-002**: Here* legality is the corresponding *adjacency-gated*
  action's own predicate, evaluated by the same code path — never a
  parallel definition: HereFood ⇔ Eat legal (adjacent stocked bowl; an
  empty or absent bowl is not "food here"); HereWater ⇔ Drink legal
  (adjacent water); HereCritter ⇔ critter-Play legal (adjacent live
  critter — deliberately NOT Chase legality, which is distance-unbounded
  and would make the word mean "exists somewhere" instead of "here, with
  me"). HereSunbeam is the family's ONE stated exception: no sunbeam
  action exists to share, so its predicate is explicit — the speaker's own
  tile or an adjacent tile holds an unexpired sunbeam element — the same
  shape as Drink's adjacency, stated plainly rather than laundered through
  a fabricated action. The family invariant, binding on every kind
  including future amendments (owner ruling, 2026-08-15): a Here
  expression requires ADJACENCY to its referent; visibility — under any
  vision regime, present or future — is never sufficient grounding.
- **FR-002b**: The free register (mew, chirp, trill, ekekek) carries NO
  grounding predicate: legality is the per-cat-per-kind cooldown and the
  enable flag, nothing else — exactly follow_me's existing law. The
  two-tier naming doctrine is normative: law-named kinds MUST have their
  meaning enforced by their predicate; sound-named kinds MUST NOT have any
  meaning enforced, claimed, or implied by the engine. A future kind
  whose name asserts a meaning its predicate does not enforce is a
  naming-law violation.
- **FR-003**: All new kinds MUST pass through the existing message
  enforcement unchanged: an illegal proposal downgrades to Silent with the
  paired activity untouched; the per-cat-per-kind cooldown applies; Silent
  remains always legal.
- **FR-004**: New-kind announcements MUST broadcast, appear in the served
  `recent_meows`, and land in hearers' message digests exactly as existing
  kinds do — same audibility, same freshness window, same per-kind
  columns. All seven new kinds stamp **intensity 0.0** (the spec-028
  social-word rule, extended uniformly): the digest's intensity column
  means the speaker's need pressure and belongs to want-kinds only. A
  future richness stamp for Here* is a stamp-semantics change available at
  any generation boundary without a schema move; it must answer the
  rot-direction argument recorded in Clarifications.
- **FR-005**: Here* digest entries MUST track the emitter (live offset to
  the speaker), identically to every other kind — NEVER a pinned resource
  coordinate. Rationale, binding on future amendments: a pinned waypoint
  can outlive its referent (bowls despawn when drained and respawn
  elsewhere; critters expire; beams end), which would reintroduce the
  staleness lie the digest design exists to prevent; emitter-tracking
  keeps the word useful only while the speaker stays near the referent.
  Any future proposal to pin coordinates must refute this paragraph in a
  spec of its own.

**Config-armed vocabulary**

- **FR-006**: The meow configuration MUST gain one enable flag per
  speakable kind (all fifteen), as named fields validated under the
  strict-config posture and echoed by the configuration endpoint.
  Defaults: enabled for the thirteen active kinds; DISABLED for the
  reserves (trill, ekekek). Active-vs-reserve is only this default;
  nothing structural distinguishes them.
- **FR-007**: A disabled kind MUST be never-legal (mask false every tick,
  proposals downgrade to Silent). Flags MUST NOT affect any layout:
  observation length, digest width, head width, mask width, and menu are
  identical across all flag settings — flags gate legality only. (This is
  what makes the reserves free: they sit in every schema-4 observation at
  zero, at zero training presence, until an experiment arms them by
  config.)

**Schemas and the generation gate**

- **FR-008**: The message digest MUST widen from 8 to 15 kind-columns
  (appended; 60 floats), moving the observation length from 197 to 225
  with no existing field relocated. The observation schema version MUST
  advance (3 → 4).
- **FR-009**: The action-encoding schema version MUST advance (2 → 3) for
  the message head widening (9 → 16). The 34-entry activity menu is
  UNCHANGED — same entries, same indices, same encode/decode — and the
  encodings contract MUST state this explicitly so no consumer hunts for a
  phantom menu delta. This is the codec's final move before the
  character-era freeze (roadmap principle: the say-surface holds through
  phase 2 and — by the reserve mechanism — through the post-fog
  language-capacity experiments; only the observation schema moves at the
  fog wall).
- **FR-010**: The mask schema version MUST advance (2 → 3): the message
  mask widens 9 → 16; the activity mask stays 34. The never-all-zero
  guarantees are unchanged.
- **FR-011**: The kitty slot count MUST remain 3 under observation schema
  4, independent of roster size. (Someone-always-unslotted is the next
  generation's thesis; the slot count is a schema constant, not derived
  from the roster.)
- **FR-012**: The artifact loader MUST accept v2- and v3-format artifacts
  whose headers pin the new schema versions (dimensions already derive
  from header and slot configuration — this is the spec-030 pin turn, not
  new machinery), and MUST refuse any artifact pinning superseded schema
  versions with an error naming the artifact path, the pin, and the
  expected value. Version-set rejection semantics (spec 030) are
  unchanged.
- **FR-013**: The CI parity gate MUST remain un-ignored and passing across
  the bump: a new oracle fixture and parity file at the new layout
  (225-wide observations, 50 policy logits: dense 11 + kitty-pointer 15 +
  critter-pointer 8 + message head 16), ≥ 100 rows including
  vacancy-stress rows and rows where new kinds — the reserves especially —
  are never-legal, at the existing tolerance (≤ 1e-4 max absolute logit
  error, exact greedy argmax). The fixture is exported by Experiments
  through the certified export path mid-arc (the spec-030 handshake);
  implementation pauses at that handoff.
- **FR-014**: The wall PR MUST leave main's shipped configuration seating
  no policy behaviors (scripted seats, the spec-028 wall precedent) so
  every shipped-config CI gate passes while no new-schema artifact exists.
  The served box keeps its current binary and world untouched; during the
  wall window only client-only deploys are safe (documented in the deploy
  script). Re-seating arrives with the phase-1 generation's own
  certification, outside this spec.
- **FR-015**: The engine-defaults stamp is expected to move (new config
  fields with defaults); the wall carries ONE re-baseline, coordinated
  with the config rider PR (Clementine, Pumpkin, sunbeam re-pin — valued
  by the owner, outside this spec), and the CHANGELOG wall entry carries
  the compatibility markers ([obs-schema], [stamp]).

**The honesty boundary**

- **FR-016**: The engine's guarantee for Here* is EMISSION-TIME truth
  only: the predicate held when the word was spoken. The engine MUST NOT
  enforce speaker-side preservation of the referent (no reservation, no
  consumption lock, no penalty): a speaker may lawfully announce and then
  consume the last servings. Preservation is a team-reward equilibrium to
  be learned, per the established no-reward-shaping-of-manners doctrine
  (F-011; the spec-023 documentation treatment applies — the boundary is
  stated here so it is citable, not folklore).

**The living documents**

- **FR-017**: This spec MUST deliver a refreshed encodings contract as a
  living document superseding spec 014's frozen encodings contract:
  versioned sections covering observation v3 and v4 (full field tables
  with normalizations), the action menu v2 with message head (old and new
  widths), mask layouts, the message digest, global-state v1, and the
  bc-collect dataset format. Experiments' committed draft is raw material;
  every row MUST be verified against code before it becomes contract, with
  the draft's flagged uncertainties (direction ordering, element-type
  ordering) resolved authoritatively.
- **FR-018**: The old contract MUST remain in place with a pointer to its
  successor (specs are history; the living document says where truth
  moved).
- **FR-019**: The contract MUST state, in its own preamble, the standing
  rule: any future spec that moves an observation, action, or mask schema
  version updates this contract as a required deliverable of that spec.
  This spec is the rule's first subject.

**The field guide (owner request, 2026-08-15)**

- **FR-020**: This spec MUST deliver `docs/meows.md` — the maintained
  language reference for the meow channel, in the house voice (the
  README/CHANGELOG register: warm, deadpan, precise — a field guide
  written by someone who loves the animals). Structure: the grammar in one
  breath (Want / Here / Purr / the free sounds / Silent) and the two-tier
  naming doctrine; one entry per word with three columns — the law
  (grounding predicate or free-register rule, cooldown, per-kind flag,
  emission-time truth, the adjacency invariant for Here*), the intent
  (designed meaning; for sound-words explicitly "none — the name is the
  sound"), and the observed meaning (measured use, each claim linked to
  its evidence in the experiment results or the purrsonality register:
  purr-as-contact-call, mew's "I'm coming, stay put", the doter dialect's
  spatial inversion); the engine's non-guarantees (restraint, referent
  preservation, courtesy — learned equilibria, citing FR-016 and the
  F-011/spec-023 doc treatments); and a digest paragraph sufficient for a
  plugin author to build a listening cat. WaitForMe is footnoted as the
  engine's own word (yield-rule-only; policies cannot speak it; not
  renamed — the engine means what it says). Sound-words are noted as
  rendered AS-IS by viewers ("mew!", "ekekek!") with display translation
  out of engine scope. The unwritten observed-meaning cells (Here*,
  chirp) are born empty on purpose, marked "law fixed (or free); meaning
  awaits the cats"; the reserves are marked "not yet spoken anywhere."
- **FR-021**: `docs/meows.md` joins the living-document rule: any future
  spec that changes the vocabulary (kinds, names, grounding, flags, digest
  semantics) MUST update it as a required deliverable, with the rule
  stated in the doc's own preamble — the same enforceability as FR-019.
  Observed-meaning entries update from Experiments' measured results as
  they land (fog is expected to rewrite several); those updates are doc
  maintenance, not spec events.

### Key Entities

- **Message kind**: one word of the meow vocabulary; carries a normative
  head index and digest column that never change once assigned, and a tier
  — law-named (predicate-enforced meaning) or sound-named (free).
- **Here announcement**: a grounded, emission-time-true claim that a
  referent is adjacent to the speaker; carried by the existing
  broadcast/digest machinery, tracked by speaker.
- **Free-register word**: a sound-named kind with cooldown-only law; its
  meaning is the cats' emergent property, recorded (never enforced) in
  the field guide.
- **Reserve**: a free-register word whose enable flag defaults off — in
  every layout, in no training run, until an experiment arms it.
- **Vocabulary flag**: per-kind config boolean; gates legality, never
  layout.
- **Schema pin**: an artifact header's declared observation/action/mask
  versions; the loader's generation gate.
- **Encodings contract / field guide**: the living documents; every
  schema- or vocabulary-moving spec's required deliverables.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a probe world with defaults, all five new active kinds
  (four Here*, chirp) are emittable by scripted probes and received in
  hearers' digests within the freshness window — Here* only at their
  referents, chirp anywhere off cooldown; the reserves produce zero
  emissions over any horizon; with flags off, zero emissions of any new
  kind while observation shapes stay byte-identical.
- **SC-002**: Grounding holds under property tests: across randomized
  worlds, no Here* emission is ever accepted from a speaker whose
  adjacency predicate is false at that tick (zero violations over
  thousands of ticks) — including the HereCritter distance case (a
  far-away critter never grounds the word) — and no free-register emission
  is ever refused for any reason except cooldown or flag.
- **SC-003**: Every pre-wall artifact is refused at startup with an error
  naming the stale pin; the new-schema fixture loads and serves; the CI
  parity gate passes at ≤ 1e-4 with exact greedy argmax on ≥ 100 rows.
- **SC-004**: The 34 existing activity-menu indices and the 8 existing
  head/digest positions are provably unchanged — mew answering for
  follow_me's position and legality byte-for-byte (encode/decode
  round-trip tests pass for the existing range with only the name
  updated).
- **SC-005**: The full workspace suite and shipped-config gates are green
  on the wall PR with main's seats scripted; the served world's binary and
  save are untouched by the merge.
- **SC-006**: The refreshed encodings contract exists with every
  current-version row verified against code; both draft-flagged orderings
  are resolved and stated.
- **SC-007**: `docs/meows.md` exists with an entry per speakable word plus
  Silent and the WaitForMe footnote; every law cell agrees with
  FR-002/FR-002b and the shipped config's dials; every observed-meaning
  claim resolves to its evidence; the unwritten cells say so.

## Assumptions

- The two-tier vocabulary, the mew rename, the reserve mechanism, and the
  as-is display rule are the owner's locked decisions (2026-08-15 night);
  the HereCritter play-only grounding and the family-wide adjacency
  invariant are her explicit ruling the same night. The set is closed: the
  design covers every referent class and the free register's capacity
  experiment, so there is nothing left to name.
- mew's law being byte-identical to follow_me's is verified against
  `message_legal` (cooldown-only today); the rename changes a name, not a
  law. Purr's law-named status likewise matches code (`purr_earned`).
- The two wall consequences are owner-accepted: the generation wall
  reopens at merge (scripted seats, client-only deploy window, fresh
  oracle mid-arc), and the later phase-1 seating cutover is a fresh-world
  rollout because the roster gains a fifth kitty (outside this spec). The
  mew wire rename adds a third, smaller one: pre-wall saves and fixtures
  containing `follow_me` do not parse on the new binary — subsumed by the
  fresh-world cutover; repo fixtures update in the arc.
- The config rider (Clementine `[[kitty]] id 5` cuddle 0.7/play 0.3/bath
  0.1; Pumpkin eat 0.6/sleep 0.2/bath 0.1; `sleep_relief_sunbeam` 7.0) is
  a separate PR in the same wall window, no spec required; its CHANGELOG
  note records the owner's caveat that trait rates are stage-3-mortal
  pins, re-derived under the phase-1 world.
- Experiments exports the new oracle before any phase-1 training exists —
  a re-tokenized clone or pattern-weight checkpoint through the certified
  export path at the final layout (225-wide observations, 50 logits).
- Client-side items riding the wall kickoff (not this spec): the fifth
  cat's rendering and white-cat palette override, and sound-words rendered
  as-is.
- Trait-envelope config validation is deferred to the lineage generation
  (owner-accepted).
- The digest keeps 4 columns per kind and the freshness/cooldown window
  semantics of spec 028; the seven new kinds add columns, not machinery.
- Fog-era measurement obligations (announcement-courtesy rate, hosting
  emergence, HereSunbeam's convening role, the language-capacity
  experiment over the free register, mew's designed-meaning-revival
  prediction) are Experiments', registered in the comms brainstorm
  addendum; they are not requirements of this spec.
- `docs/meows.md` joins the maintained doc stack on the owner's word,
  folded into this spec rather than its own arc because the vocabulary
  freeze is the doc's one chance to be born complete.
