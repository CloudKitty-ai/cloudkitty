# Brainstorm: the communication generations (owner riff, 2026-08-13)

**Status: brainstorm-grade design inputs — NOT a spec request, NOT a
prereg.** Captured from an owner design session so the threads survive
until their generations open. Each generation still gets its own
design-inputs pass and prereg; where this doc and a frozen prereg
disagree, the prereg wins. Context that motivated it: the exp-004
post-deploy findings (purr = contact call; FollowMe = "I'm coming";
want-words atrophied on-policy) and the attention arc (spec 030 in
flight, entity tokens validated).

## The organizing idea

Communication emerges from information gradients, and the current
world has none: nearest-N slots give every cat the same knowledge of
essentials, so the on-policy channel evolved *social* words (the only
private state is internal state) and the want-words atrophied. Each
generation below adds one information gradient and one capability to
exploit it. Sequence chosen so each generation's learned skill is the
next one's foundation.

Fact checked 2026-08-13: hearing is ALREADY global — `freshest_audible`
has no range gate, only the recency window. Fog changes vision only.

## Gen A (in flight): entity attention, schema 3, current world

Spec 030 + PPO on the attention clone. No world change. The
architecture that does relational binding at all — prerequisite for
everything below.

## Gen B: the estimator generation (global vision + fifth cat)

**Owner's design**: an auxiliary head predicting every other cat's
need vector (slotted or not) — trained supervised (the simulator knows
ground truth), riding the attention policy.

- **Why it needs the fifth cat**: at roster 4 / 3 kitty slots, every
  other cat is always slotted and its needs are directly visible —
  want-meows are informationally redundant and an estimator has
  nothing to estimate. At roster 5, someone is ALWAYS unslotted; the
  want-meows become the only carrier of that cat's state. Pairs with
  the long-parked Clementine rollout (ROADMAP.md; family already
  5-kitty base, critic 5-padded).
- **Why global vision helps learning** (owner's point): sight labels
  sound — a heard meow is frequently followed by direct observation
  of the meower's needs, dense natural verification for learning the
  meow→need mapping. Learn the decoder where supervision is cheap;
  it becomes existential under fog (Gen C).
- **Chicken-and-egg resolution**: the aux loss makes hearing
  informative to the *loss* before any behavior uses it, so
  representations encode meow semantics for the policy gradient to
  find — the standard fix for referential-communication fragility,
  and the exp-004 imitability principle in trainer clothing.
- **Measurement for free**: prediction error on the unslotted cat,
  digest intact vs zeroed — a continuous per-tick version of the
  "does the channel pay" ablation.
- **Priced cost to carry into the prereg**: F-014 — a 5th kitty
  halves cooperative credit signal (S 0.090 → 0.041). Known trade.
- This IS the parked JEPA/predict-the-neighbors design input
  (memory: attention-architecture-arc), first concrete target.

## Gen C: the fog generation (schema 4)

**The substrate (one design, pinned together):**

- **Vision radius X**: cats see entities within X tiles; hearing
  stays global. Creates private information about resources — the
  gradient referential communication needs.
- **Variable entity tokens**: "entities within X" gives schema 4's
  variable-length token sets a principled semantics (locality)
  instead of arbitrary slot caps. Attention consumes it natively;
  F-010's retest becomes a normal condition (sparse region = few
  tokens), not an OOD pattern.
- **Per-kitty memory tokens (owner's design)**: the ENGINE remembers
  — per kitty, the last chow (and water) that left its vision:
  `[present, dx, dy, ticks-since-seen, servings-at-last-sight]`.
  One slot each, most-recent-sighting-wins, written by SIGHT ONLY
  (testimony — meows writing memory — deliberately staged as a
  follow-on so personal vs communicated knowledge stay separable in
  the data). Honest under the law: the token asserts the sighting,
  never present truth. Deterministic, snapshot-persisted. No
  recurrent policy needed — this is the digest pattern pointed at
  sight. The staleness-inference problem (P(still there) from age,
  observed cats, their hunger) is relational binding across tokens —
  the attention architecture's home turf — and the Gen-B aux head
  extends naturally ("is the remembered chow still there?" — ground
  truth known at training time).
- **Recurrence trigger condition (pipeline hygiene)**: if probes show
  cats systematically returning to wrong remembered locations
  because one slot is insufficient, THAT is the measured need the
  parked recurrence step has been waiting for. Not before.

**The experimental arms (choose, don't pin):**

- **Vocabulary fork**: meow law grounds words in the SPEAKER's need
  state, which forbids altruistic reference ("food here, I'm fine").
  Either FollowMe overloads into a general deictic "come here" —
  interesting in itself — or the generation adds WORLD-grounded
  words (FoundEat/FoundDrink, legal only while at/seeing the
  resource; meow law stays honest, reference becomes possible).
  Candidate registered comparison for the prereg.
- The prediction auxiliary on/off (if not already settled by Gen B).

**Known wrinkles, flagged early:**

- **BC bootstrap under fog** (the methodological crux): scripted
  demonstrators decide from the full snapshot — omniscient teachers,
  fogged students, labels conditioned on invisible state. Options:
  fog the demonstrators (engine work; needs_driven under fog is a
  different animal) or curriculum (clone at full vision, anneal X
  during PPO). F-007 says BC cannot be skipped at our budget. Design
  this, don't improvise it.
- **Density coupling**: 20×20 with chow 6 / water 7 is dense — a
  modest X usually still contains a resource. Real information
  asymmetry likely wants a bigger/sparser world → couples to the
  world-scale thread; makes Gen C a world generation, not just a
  schema generation.
- Welfare during training generations under fog: screens sized for
  it; the constitution guarantees relief exists, not that a fogged
  learner finds it early in training.

**Registered prediction worth writing into that prereg**: fog is the
selection pressure under which FollowMe's DESIGNED meaning ("follow
me to the resource") could beat the emergent "I'm coming" meaning
measured in `exp-004-meow-channel/results/followme-2026-08-11/`.

## Discipline note

Gen C accumulates axes fast (fog, density, vocabulary, memory,
auxiliaries). The change-one-thing rule: substrate pinned as one
design, arms chosen explicitly, everything else inherited. And the
sunbeam shared-warmth change (design input sent to Product
2026-08-13) rides whichever pre-generation re-baseline comes first —
it is independent of all of this.

## Addendum 2026-08-14: gaze/foresight design notes (owner side-thread)

Client wants anticipatory gaze/ear animation ("walking toward X").
Decisions from the discussion, on record:

- **Foresight source = the CLIENT BUFFER, not server simulation.**
  Extending the Pacer's buffer to ~5 ticks gives the actual future
  (exact even under future nondeterministic deciders, zero engine
  cost) at the price of ~4s uniform viewing delay — fine for a
  watch-only sanctuary. Server-side k-tick preview (~0.2% tick
  budget, but a spec + a cloned-RNG correctness trap) stays unbuilt
  unless a latency-free consumer appears. Client-thread work.
  Caveat noted: interactive features, if ever, must remember the
  viewer runs ~4s behind.
- **Tier 3 (attention gaze)**: spec-030 extension to surface per-cat
  top-attended entity / pointer logits in the WS frame — covers
  desire-without-action, ambivalence (near-tied pointers),
  goal-collapse beats, hearing-without-acting. MUST be validated
  before animation: does top-attended entity at t predict the entity
  reached by t+k? (offline probe vs logged rollouts / the buffer
  stream as ground truth).
- **Tier 4 (intent head)**: Gen-B rider — hindsight-labeled "which
  entity will I touch next + confidence"; extends foresight past the
  buffer horizon probabilistically. Chase targets are already
  engine-explicit today (tier 1) and need none of this.

## Addendum 2026-08-15: Found-word honesty is emission-time only
(owner's insight during the 033 review)

Bowls despawn when drained and respawn elsewhere — so "announce then
eat the rest" leaves hearers trekking to bare grass. Registered
framing: this is F-011's SIBLING — the engine guarantees the word was
true when spoken, never that the speaker preserves the referent;
"don't announce what you'll devour" is a team-reward equilibrium to
be LEARNED, per generation, and fingerprint-measurable. Fog-era
prereg items this creates:
- Measure announcement courtesy: P(speaker consumes final serving |
  announced within window, hearer en route); does it fall with
  training?
- Watch for HOSTING (the positive form): announce + stay by the bowl
  while others eat. Digest semantics make this structurally favored —
  Found* entries keep standard emitter-tracking (decision for spec
  033: NO pinned-location variant; a pinned waypoint can point at a
  despawned bowl — the staleness lie through the back door — while
  emitter-tracking degrades gracefully and makes staying-near-the-
  food the only way the word stays useful).
- 033 spec text should state the emission-time-truth-only guarantee
  explicitly (the F-011 docs pattern).

## Addendum 2026-08-15 (final): the adjacency invariant (owner ruling)

Spec 033 FR-002 carries the owner's family-wide invariant, binding on
all Found* kinds including future amendments: **a Found expression
requires ADJACENCY to its referent; visibility, under any vision
regime present or future, is never sufficient grounding.** This
pre-answers the fog-era loosening question (Found* does NOT relax to
sight) and fixes the semantic architecture of the whole channel:
Found-words are PRESENT-TENSE and PROXIMATE ("here, with me"),
memory tokens are PAST-TENSE and honest-about-staleness ("I saw it
there"), and never the twain — reference-at-a-distance can only ever
enter the language as a distinct, explicitly stale-marked form. The
fog prereg's vocab-fork comparison inherits this grounding pinned.

**Rename note (owner, 2026-08-15): the Found* family shipped as
HERE* (HereFood/HereWater/HereCritter/HereSunbeam) — 'here' is the
adjacency invariant as a word. Earlier mentions of Found*/FoundEat in
this doc refer to the same kinds under their draft name.**

**Final vocabulary architecture (owner, 2026-08-15): two-tier naming
— law-named grounded words (Want*/Here*/Purr) vs SOUND-NAMED free
register (mew = renamed follow_me; chirp active at phase 1;
trill + ekekek reserved, config-OFF). The post-fog
LANGUAGE-CAPACITY experiment (marginal value of a word) runs as pure
config over the reserves — arms enable 2/3/4 free words, measuring
semantic differentiation (distinct contexts/flip-signatures) and
welfare. The fog FollowMe-revival prediction re-registers under MEW.
Client renders sound-words as-is (owner: 'that's cute').**

## Addendum 2026-08-18: the bootstrap doctrine for new communication
behaviors (owner design session, settled)

The question: how do NEW words come alive — continue BC from
previous-gen lineages we like, or found a fresh lineage from an
enhanced scripted demonstrator? The answer fell out of the two-tier
vocabulary doctrine itself; the two options serve different halves.

**The facts the strategy respects**: demonstrations seed the channel,
exploration doesn't — but channel-ALIVENESS transfers and specific
words can be born later (F-022: exp-003's channel-empty minds stayed
mute; e004's channel-alive minds invented FollowMe on a free label
from zero demonstrations). Culture is unreproducible from scripted
(F-025). Nobody currently speaks Here* or chirp, and the expansion
design makes the carried minds provably mute in them; pre-fog the
new words are welfare-inert (F-026), so RL has no adoption gradient
until fog creates one.

**The doctrine split**:
- **Law-named words (Here*) are scripted-seedable, cleanly** — the
  law IS the meaning, so a scripted behavior emitting under the
  grounded predicate demonstrates the true meaning by construction
  (the engine enforces honesty at emission). Every word that ever
  came alive started as a scripted seed (purr, the want-words).
- **Sound-named words (chirp/trill/ekekek) must NEVER be scripted**
  — scripting imposes meaning on a word designed for the cats to
  author (law by the back door). Their bootstrap IS the lineage:
  RL filling free labels inside channel-alive cultures (the
  mew/FollowMe precedent).

**The settled strategy (owner-approved 2026-08-18)**:
1. **Lineage BC for culture** — the house default for personalities
   and cultures we like: collect from the minds themselves (frozen
   artifacts replay forever), clone-and-leash per F-019. Fog-gen
   collection happens POST-cutover from the EXPANDED minds on the
   new surface (expansion preserves minds exactly — new-surface
   demonstrations with culture intact, nothing to collect before
   cutover).
2. **The enhanced scripted is a TEACHER SEAT, not an ancestor** — a
   Product-specced behavior (fog-window work) speaking Here* under
   the grounded predicates, courtesy dials designed per F-023 (the
   teacher's chattiness is a listener-population choice). It
   contributes vocabulary rows to the corpus; it founds nothing.
3. **Delivery mechanisms become fog-prereg ARMS, not arguments**:
   (i) mixed-corpus BC (teacher rows + lineage rows, one clone;
   risk: averaging two demonstrators), (ii) **the vocabulary
   lesson** — clone the lineage wholesale, then a head-selective
   second BC stage: trunk + activity head FROZEN, message head
   finetuned on teacher rows only (the ride-along architecture
   exists to allow exactly this), (iii) the no-seeding control
   (pure lineage; RL must invent under fog). This upgrades the
   registered fog comparison to: seeded grounded words vs invented
   grounded words vs FollowMe-overloading, one information
   gradient.

**The vocabulary-lesson SMOKE EXPERIMENT (registered intent — runs
before the fog prereg commits to mechanism ii)**: no teacher
behavior needed — construct a SYNTHETIC teacher corpus from already-
collected states by relabeling rows where the grounded predicate
holds (the mask itself says where here_* is legal), then run the
head-selective finetune on a phase-1 clone and measure (a) Here*
acquisition on held-out legal contexts, (b) activity-policy
invariance (frozen-trunk parity on the action head), (c) whether the
frozen trunk carries the features the message head needs — the one
real technical risk. Cheap (one BC-stage run), zero engine work,
zero Product dependency.

Division of labor: teacher-behavior spec = Product, fog window (no
action now); corpus construction, lessons, arms, smoke = Experiments.
