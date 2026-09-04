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

Every word obeys the same per-kind cooldown (`meow.recent_window_ticks`,
served 10: after speaking a kind a cat may not speak it again for that
many ticks) and stays audible for the digest window
(`meow.digest_window_ticks`, served 30 — a positive multiple of the
cooldown, so "three calls in a window" is exact). Every word can be
disabled by the world's `[meow.vocabulary]` config. Flags gate legality
only; no flag ever changes what an observation looks like.

## The words

Each entry: **law** (when the engine allows it), **intent** (the designed
meaning), **observed** (what the cats use it for, with the evidence).

### The Want family — law-named: I lack

**want_eat · want_drink · want_play · want_cuddle · want_bath ·
want_sleep**

- **Law** (spec 049 FR-036, the knowledge-gated want law): legal while
  the matching need is armed (at or above `announce_threshold`, with
  hysteresis so the word doesn't flicker mid-errand), that need is the
  cat's **top need** (`NeedKind::ALL` order breaks exact ties), the cat
  has **no known relief** for it, and the cooldown is clear. Known
  relief, per word: `want_eat` — a bowl visible or remembered;
  `want_drink` — water visible or remembered; `want_cuddle` — an **idle
  friend in view** (no scene, not asleep; adjacency not required; a
  friend the cat can only hear never silences the word); `want_play` —
  that friend clause, or a critter visible or remembered; `want_sleep` —
  never (need-only-when-top); `want_bath` — never, and no top-need clause
  either: it is an **ask**, armed-only (owner ruled 2026-09-03, spec 049
  T087) — its relief is self-grooming, and the partnered groom only a
  groomer starts, on hearing the word, so an idle friend in view is a
  groomer to be asked, not relief the caller can execute. So under fog an
  announcement says "I am in need and I cannot see the answer", which no
  observation row carries, and the ask says "come and groom me". The
  scripted groom response answers a `want_bath` only while the ask is no
  older than the cooldown and, on sight, only a caller still above the
  announce threshold (T087) — a still-needy caller re-emits every
  cooldown, so nothing is lost and nobody walks to a cat already groomed. The emission stamps the need's value as the call's intensity
  and the speaker's position: a listener hears how hungry, and where
  from. One predicate, `message_legal` over the cat's fog view, judges
  the RL mask and the built-in announce alike. Consequences the owner
  ruled: at a world-covering radius the element wants go silent in a
  world that always has chow and water, and a cat that has ever seen a
  pond never says `want_drink` again.
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

- **Law** (spec 033, widened by spec 049 FR-037): legal when the
  referent is ADJACENT to the speaker (own tile counts) — each word the
  matching action's own predicate: `here_food` is Eat's stocked-bowl
  adjacency (an empty bowl is not food here), `here_water` is Drink's,
  `here_critter` is Play-critter's (deliberately not Chase's, which is
  legal at any distance), `here_sunbeam` explicit adjacency to a live
  beam — **or** when the word is a reply: a matching want from another
  cat is audible in the speaker's start-of-tick buffer AND the referent
  is visible from the speaker (anywhere in its disc). The pairs:
  `want_eat ↔ here_food`, `want_drink ↔ here_water`, `want_sleep ↔
  here_sunbeam`, `want_play ↔ here_critter`; cuddle and bath have no
  here-word. Every recorded here carries an engine-stamped `reply` bit —
  1 exactly when that reply condition held at emission, whatever
  triggered the word (an ambient here landing while a want is audible is
  a reply too), 0 for adjacency-only heres and for every non-here kind —
  and a `pos`. A same-tick reply is impossible (everyone decides against
  the start-of-tick snapshot): want → here → heard is three ticks at
  best. The guarantee is emission-time truth ONLY — see the
  non-guarantees below.
- **Scripted replies** (spec 049 FR-042–FR-046): a built-in cat answers
  audible wants by *want*-listening only (the groom-response precedent);
  no built-in ever consumes a here-word (the 043 gate-zero guard stands).
  With `[behavior] reply_intensity_floor` set, it replies with the paired
  here-kind when it can see the referent, its cooldown is clear, and the
  caller's stamped intensity reaches the floor — the most urgent caller
  first (ties to the fresher call, then the lower id); its own want wins
  the turn when its raw need exceeds the caller's intensity × 100; the
  loser waits at most one tick. Unset (the served value) = no replies,
  byte-identical to the no-reply engine.
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

Since the fog wall (spec 049, observation schema 5) there is no global
digest: repetition and insistence are **per-speaker fields on each
friend's permanent row**. For every friend, per kind, a hearer's
observation carries two numbers about that friend's own calls inside the
digest window — recency (1.0 fresh, fading linearly to 0 over
`digest_window_ticks`) and rate (calls in the window over the most the
cooldown allows: three at the served 30/10) — and, for the six want-kinds,
the intensity stamped on its freshest call (the speaker's need level at
emission, /100; here-kinds and the free register carry none). A call is
inside the window while its age is strictly less than it, and only calls
from earlier ticks count: nobody hears a same-tick word. The observer's
own row carries the same recency/rate pair for its own calls (no
intensity — its needs are already there), so a memoryless mind can tell
"I already asked" from "I have not". Five `here_water` calls and one no
longer produce the same observation, and a second simultaneous speaker
of a kind is no longer inaudible.

Where a call came FROM is a stamp, not a live position: every recorded
meow carries the speaker's `pos` at emission. A friend the hearer can
see has its live position on its row; a friend it can only hear has the
position of that friend's last audible meow (its row's dx/dy/distance
point there, its knowledge fields read zero), and the recency cell says
how stale that is. A `here_food` from an unseen cat therefore points
where the speaker was when it spoke — useful exactly while the speaker
stayed near the food — never at a bowl the hearer cannot confirm. The
answers-me bits (per here-kind, on friend rows) say whether that friend's
latest here of the kind came after the hearer's own matching want. Full
field table: `docs/encodings.md`.

Historical (schema 4, spec 033): one global digest per kind — the single
freshest audible emitter's recency, LIVE dx/dy and intensity — which the
fog made both a leak (a moving unseen cat's position, every tick) and a
bottleneck (one emitter per kind for the whole meadow).
