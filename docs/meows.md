# Meows — a field guide to the kitty grammar

What the words mean. This is the companion to `docs/plugins.md` (how
outside minds talk to the engine) and `policies/purrsonality.md` (who the
minds are). It covers every sound a cat can make on the meow channel: the
law that governs each word, the meaning it was designed to carry, and the
meaning the cats actually gave it — which is not always the same thing,
and the difference is the best part.

**Maintenance rule (spec 033 FR-021): any spec that changes the
vocabulary — kinds, names, grounding, flags, digest semantics — updates
this file as a required deliverable.** Observed meanings update from
measured results as they land; those edits are maintenance, not spec
events. Law cells below restate
`specs/033-say-surface/contracts/say-surface-v3.md`, which is normative.

## The grammar in one breath

**Want** (I lack) · **Here** (I have — come share) · **Purr** (I am
content) · **the free sounds** (the cats' own words) · **Silent**.

Names come in two tiers, and the tier tells you how much to trust the
name. A **law-named** word means what its grounding predicate enforces: a
cat physically cannot say `want_eat` on a full stomach or `here_food` on
bare grass, so the name is a fact. A **sound-named** word (`mew`,
`chirp`, `trill`, `ekekek`) denotes only the vocalization; the engine
enforces nothing about its meaning, and what it comes to mean belongs to
the cats. This split is a lesson learned the honest way: the word once
called `follow_me` was designed to mean "come along," and the cats used
it to mean "I'm coming, stay put." The name lied; the law didn't. Now
free words carry names that cannot lie.

Every word obeys the same cooldown (one live digest entry per kind per
emitter — `meow.recent_window_ticks` is both the audibility window and
the refresh rate), and every word can be disabled by the world's
`[meow.vocabulary]` config. Flags gate legality only; no flag ever
changes what an observation looks like.

## The words

Each entry: **law** (when the engine allows it), **intent** (the designed
meaning), **observed** (what the cats use it for, with the evidence).

### The Want family — law-named: I lack

**want_eat · want_drink · want_play · want_cuddle · want_bath ·
want_sleep**

- **Law**: legal while the matching need is armed (at or above
  `announce_threshold`, with hysteresis so the word doesn't flicker
  mid-errand) and the cooldown is clear. The emission stamps the need's
  value as the digest's intensity: a listener hears how hungry, not just
  that.
- **Intent**: honest requests. Six needs, six words, nothing unsayable
  (spec 028 gave the two silent needs, bath and sleep, their words).
- **Observed**: used as designed, with one lovely elaboration — the
  trained generation answers `want_bath` by walking over and grooming the
  asker (GroomKitty at 93.3/1k decisions where scripted cats managed 0;
  `experiments/exp-004-meow-channel/results/grid-2026-08-09.md`). The
  responder culture proved durable enough that a newer generation was
  seated partly to keep it: the incumbent grooms the newcomers back at
  ~8.7% of its decisions
  (`experiments/attn-cert-2026-08-14/selection-crossgen.md`).

### purr — law-named: I am content

- **Law**: legal only when earned — happiness above the purr threshold or
  rising (`purr_earned`, the spec-022 economics). A purr cannot be faked;
  proposed unearned it resolves to a quiet idle turn.
- **Intent**: a contentment signal. Ambient warmth for whoever is near.
- **Observed**: the cats repurposed it into a **contact call**. A purr in
  the digest reads as "I'm fine out here," and hearers steer AWAY from
  the purring cat rather than toward it — presence information, not an
  invitation (registered as deviation D-002, exp-004 results; not
  collapse, grounded legality held throughout). The doter dialect then
  inverted the spatial meaning again: doters hum close where the founding
  culture pinged far (`policies/purrsonality.md`). Same word, same law,
  three meanings so far. Under fog, the contact call is expected to
  become the pack's location sense — that prediction is registered in
  `experiments/comms-generations-brainstorm-2026-08-13.md`.

### The Here family — law-named: I have, come share

**here_food · here_water · here_critter · here_sunbeam**

- **Law**: legal exactly when the referent is ADJACENT to the speaker
  (own tile counts). Each word uses the matching action's own predicate:
  `here_food` is Eat's stocked-bowl adjacency (an empty bowl is not food
  here), `here_water` is Drink's, `here_critter` is Play-critter's
  (deliberately not Chase's, which is legal at any distance — this word
  means *here with me*, never *exists somewhere*). `here_sunbeam` is the
  family's one stated exception, since no sunbeam action exists to
  borrow from: explicit adjacency to a live beam. The family invariant,
  owner-ruled and binding through every future vision regime: adjacency
  is required; seeing is never enough. The guarantee is emission-time
  truth ONLY — see the non-guarantees below.
- **Intent**: altruistic reference — the channel's first words that point
  at the world instead of at the speaker's needs. `here_sunbeam` is the
  best-behaved of the family: a beam is non-consumable and its warmth
  conducts to adjacent sleepers (spec 031), so the announcer loses
  nothing by hosting.
- **Observed**: the law is fixed; the meanings are now in the cats'
  hands. The phase-1 generation trained with all four words armed and
  holds seats on the served world, so the words are live. Whether they
  are spoken, and what for, is unmeasured: the registered instrument is
  the here-word density screen
  (`experiments/here-word-density-screen.md`, planned), because
  aggregate message rates cannot answer it; most of what a cat says is
  nothing.

### mew — sound-named, the free register's first word

- **Law**: cooldown only. No grounding, no arming, nothing to earn. (This
  is byte-for-byte the law it had under its old name.)
- **Intent**: none — the name is the sound. Its previous name,
  `follow_me`, intended "come along."
- **Observed**: "I'm coming, stay put." The cats overwrote the designed
  meaning thoroughly enough that the word was renamed rather than let the
  name keep lying (spec 033; the finding is recorded in
  `experiments/comms-generations-brainstorm-2026-08-13.md`). The word
  has since moved again. The E1-s1 mind mews close (1.71 tiles from the
  nearest kitty, against a 2.50 all-tick baseline), and the pair
  separates over the next ten ticks (+2.30 tiles, vs +1.27 for matched
  controls): a departure call. The inherited hearer reflex still fits:
  hearing the mew suppresses approach, so the word announces a parting
  and the hearers let it happen. Deafening hearers to the word leaves
  mean welfare flat and grows the distress tail, so its value under
  global vision is insurance rather than mean welfare
  (`experiments/exp-006-character-gen/results/mew-function-2026-08-20.md`).
  Whether the
  original come-along meaning revives under fog — where a moving cat
  genuinely can't be seen — is a registered prediction under this word's
  new name.

### chirp — sound-named, active

- **Law**: cooldown only.
- **Intent**: none — the name is the sound. A second free word, because
  the cats demonstrably fill free registers with meaning.
- **Observed**: *meaning awaits the cats.* Armed in the phase-1
  generation's training and live on the served world; whether any mind
  speaks it is unmeasured.

### trill · ekekek — sound-named, reserves

- **Law**: cooldown only, and their `[meow.vocabulary]` flags ship OFF:
  in every layout, legal in no world, present in no training run.
- **Intent**: none, twice over. They exist so the post-fog
  language-capacity experiment ("what is the marginal value of a word?")
  is pure configuration — arms enable 2, 3, or 4 free words by flag, and
  the codec never moves.
- **Observed**: *not yet spoken anywhere.*

### Silent

Always legal, on every tick, whatever the flags say (mask index 0 is
structural). Most of what a cat says is nothing.

### Footnote: wait_for_me — the engine's own word

The yield rule speaks it (spec 012: the yielding cat of a mutual approach
holds its corner and asks its partner to close the gap); policies cannot,
and no flag governs it. It was not renamed at the freeze — it is the
engine's word, and the engine means what it says. It rides the wire and
`recent_meows` like any meow but appears in no head, digest, or mask.

## What the engine does NOT guarantee

The F-011 family: manners are learned, never enforced, and never paid
for by the reward function.

- **Restraint**: nothing stops a cat spamming a legal word at every
  cooldown expiry. Observed restraint (the spec-023 finding that ended
  the courtesy era) is an equilibrium, and it held.
- **Referent preservation**: a cat may honestly announce `here_food` and
  then eat the last serving (spec 033 FR-016). The announcement was true
  when made; the engine never retracts it, reserves the bowl, or
  penalizes the speaker. If announce-and-host beats announce-and-abandon,
  it will be because the team reward taught it.
- **Courtesy**: answering a want, hosting a find, coming when mewed at —
  all voluntary. The engine's whole contribution is making the words
  honest; what the cats do about them is the experiment.

## The digest — what a listener actually hears

Per kind, a hearer's observation carries the single freshest audible
emitter (freshest tick wins; ties go to the lower kitty id; your own
meows are inaudible to you), as four numbers: recency (1.0 fresh, fading
linearly over `recent_window_ticks`), the emitter's dx and dy — **live
position, recomputed every tick, never a stamped coordinate** — and the
intensity stamped at emission (the speaker's need level for want-kinds;
0.0 for everything else). A plugin author can build a listening cat from
exactly this: for each kind, one emitter, where they are right now, how
fresh the word is, and how urgent, if urgency applies. Full field table:
`docs/encodings.md`.

The live-position rule is the design's quiet teeth: a `here_food` beacon
points at the *speaker*, so it is only useful while the speaker stays
near the food — the digest itself favors hosts over shouters, and can
never point a hearer at a bowl that no longer exists.
