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
