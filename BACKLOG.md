# CloudKitty Backlog

Prioritized future work. Everything here was deliberately kept out of the MVP
(see `specs/001-cloudkitty-mvp/spec.md`, "Out of Scope") or added since. Per the
constitution, none of it may violate Articles I–VI, and each feature goes through
the spec-first flow (`/speckit-specify` → plan → tasks) when it is picked up —
this file records priority and intent, not design.

Priorities: **P1** quick wins, next up · **P2** the bigger pieces, for a proper
sitting · **P3** simulation depth · **P4** world-scale ambitions.

## P1 — quick wins, next up

### Beautification II, step 1: vector props (retire the remaining emoji)
The 005 refresh gave the cats a parametric look; the world's furniture is
still platform emoji: chow `🍥`, bug `🐛`, greeble `👻`, the `💤` wisp and
`💗` heart, and the thought-bubble need icons. Draw them the way the cats
are drawn (direction chosen 2026-07-20): parametric canvas in the same
chibi/outline vocabulary, living beside `drawCat` so the gallery grows a
props section judged under the same approval gate that vetted the cats.
Why procedural over image assets: emoji render differently per platform,
sourced art fights the crisp-at-22px problem and licensing, and drawn
props inherit everything 005 built — retina-crisp, palette-consistent,
animatable. Greeble secrecy is untouched: the ghost only ever appears
under the `g` toggle, whatever it looks like.

Style direction (agreed 2026-07-20, judged at the gallery gate like all
looks):

- **Chow bowl** — squat terracotta cat bowl (the existing kibble-brown
  family), darker rim band; the kibble is a drawn mound that shrinks with
  servings, so the food level *is* the data display, replacing the meter.
- **The bug becomes a butterfly** (owner decision): two chubby upper
  wings, small lower lobes, dash body, thread antennae; wings flap on
  phase. Airborne read comes from a gentle hover-bob plus a small
  *detached* shadow beneath — which also masks the engine's one-tile hops
  far better than a crawler would. **Per-individual colorways** from the
  stable element id (soft lavender / pale lemon / peachy-white — hues the
  meadow doesn't use), so each butterfly is *that* butterfly; a butterfly
  that is the target of a served pursuit flaps faster (no new data).
  FR-009 note: with real butterflies in the world, the solo-play
  *imaginary* plaything firmly stays the golden twinkling star.
- **Greeble** — a drawn wisp: teardrop blob, wavy skirt, hollow eyes, the
  existing 55% alpha, slow bob; softer, slightly dashed outline — the one
  thing drawn as not-quite-there. (Open at the gallery: blank ghost vs. a
  tiny mischievous grin.)
- **Sleep wisp** — three hand-drawn rounded Zs, staggered, drifting up
  and fading on phase; static ladder under reduced motion.
- **Cuddle heart** — plump drawn heart, blush pink, dark outline, one
  highlight, soft heartbeat pulse on phase.
- **Thought-bubble icons** — mini-props in one ink weight: the bowl
  (reused), a water drop, the Zs, a yarn ball for play, the heart, and
  three glinting soap bubbles for bath (a tub is mud at 15px).

Props get a small curated palette block of world-adjacent hues so one
hand appears to have drawn everything; the gallery's props section shows
states (bowl at 5/3/1/0 servings, flap phases, greeble alpha). Panel
prose emoji ("eating 🍥") are text in sentences and stay for now.

P1 because it is one drawing file, a gallery section, and render swaps —
a contained sitting sequenced ahead of the map work below.

## P2 — the bigger pieces, for a proper sitting

### Beautification II, step 2: the meadow itself
Make the map as lovely as its residents (ideation 2026-07-20; direction
agreed). The scaling principle that anchors every piece: all decoration
derives from a per-tile hash of (x, y) — pure presentation, deterministic
across reloads like cat identity, density naturally proportional to area,
so any world size gets a stable non-repeating meadow and nothing needs new
served data (Article V untouched). Build order, each piece independently
shippable:

1. **Organic grass** — retire the checkerboard: 3–4 close grass tones by
   tile hash plus sparse hash-placed tufts, clover, tiny flowers; the grid
   line becomes debug-only (joins the `g` family). Plus barely-visible
   per-tile brightness jitter — the cheap fix for flat-color fields.
2. **Ponds** — merge contiguous water tiles into one smooth-shored blob
   (marching squares over the water tiles); lily pad on larger ponds.
3. **A world edge** — taller grass fringe or a low hedge/picket frame in
   the outline style, so any size world reads as a garden instead of
   stopping mid-lawn.
4. **Sunbeams as light** — a radial warm gradient bleeding softly past the
   tile bounds under the existing pulse and motes.
5. **Worn paths** — a client-side presentational heat-map of where cats
   have walked this session, fading slowly, so trails emerge where the
   cats actually live. **Decided 2026-07-20: a keyboard toggle in the `g`
   mold** — off by default, one key reveals it, footer hint alongside the
   greeble note. Pure view: local accumulation, cleared on reload and on
   discontinuity, never served.

Hygiene as in 005: ambient rules apply (subtle, individually toggleable
`VIEW` flags, absent under reduced motion where motion is involved; static
decoration stays). Day–night lighting remains its own entry below and
lands on top of this look.

### Harden the whole proposal boundary (do this *with* the plugin work)

### Harden the whole proposal boundary (do this *with* the plugin work)
The strict play-target parsing that shipped in PR #5 fixed one instance of a
general problem: a malformed proposal was silently reshaped into a legal,
*rewarded* action instead of reaching the engine as something to reject.
`chase`, `move`, `meow`, `rest`, `sleep` and `groom` have never had the same
scrutiny — nobody has asked what each does with a missing field, a wrong
type, an unknown enum value, or an extra key, because until now every
proposal was constructed in-process by a built-in.

That stops being true the moment an out-of-process brain can propose. This
belongs in the same sitting as **External behavior plugins** below — writing
the plugin transport without first pinning down what the wire accepts is how
you end up with the flatten bug in five more places. Deliverable: a
round-trip and rejection test per action shape (the play tests are the
template), plus a documented rule that malformed proposals resolve to the
fallback, never to a legal action. `Action`'s serde surface is the contract;
treat it like one.

### External behavior plugins (ScriptBehavior / HttpBehavior)
The payoff of Article IV's design: the async `Behavior` trait, wall-clock
budget, validation, and `NeedsDriven` fallback all exist so an out-of-process
brain can drop in with zero engine changes. Ship one reference implementation
(local script or HTTP endpoint) plus docs. This is the door to "an LLM decides
what the kitty does." Test scaffolding (`sleepy_slow`, `panicky`,
`always_invalid`) already covers the hostile cases — but only *behavioural*
hostility, not malformed input: pair this with **Harden the whole proposal
boundary** above, which is the same sitting's prerequisite. Deliberately P2:
the highest-value non-cosmetic item, held for a proper sitting rather than a
squeezed-in version.

### Friendship / relationship tracking (+ friend-proximity preference)
The foundational social feature. Kitties develop preferences from shared
history (play, co-sleeping, grooming); "friend" stops meaning "any other kitty"
and starts meaning *that* kitty; proximity preference makes bonded pairs drift
together. Unlocks meaning for "Follow me!" and most future communications.
Design care: relationship state must serialize into snapshots and stay
deterministic.

### Age / fur / eye stats
Cosmetic identity: fur colors and patterns, eye color, age. The vector-cat
renderer (shipped in 005) already shows fur as parameters — `appearanceFor`
in `client/cat.js` is the single documented override point when served
appearance data arrives, so this item is engine modeling plus palette
wiring, not new art. Age
must never become a health mechanic (Article II: no decline, no death; cats
may age into *distinguished*, never into frail).

### Day–night cycle and moonbeams
A world clock, dawn/dusk lighting in the viewer, moonbeams as the nighttime
sunbeam. Kitties are crepuscular — behaviors could weight sleep by hour.
The 005 refresh has shipped, so lighting lands on the vector look.

## P3 — simulation depth

### Food types and desirability (+ water-near-food rules)
Different chow kinds with desirability modifiers; cats prefer better food and
dislike water adjacent to their bowl. One food-system design covering both
spec items. The safeguard guarantee (Article I) must hold regardless of
desirability — a picky cat still gets fed.

### Ear / tail affect
Ears and tail express mood in the viewer (content, curious, grumpy). Pure
rendering on top of existing state; the 005 refresh shipped vector cats
partly for this — ears and tail are already animatable parameters
(`earsBack`, tail curves in `client/cat.js`), so this item shrinks to
mood-to-parameter mapping.
Deliberately kept out of the 005 refresh (2026-07-18): the bar here is
*true-to-life* — real feline ear/tail vocabulary (tail-up greeting, airplane
ears, slow flicks of irritation), worth its own unhurried design pass with
reference study, not a quick mapping bolted onto the refresh.

### Dynamic in-game speed changes
⚠️ Architectural string attached: the MVP API is read-only and the spec fixes
tick rate at startup. Live speed control needs a control surface (an operator
endpoint or console) and a spec amendment distinguishing *operator controls*
from *simulation mutation* — the viewer must remain unable to touch the world.
Determinism note: tick duration affects nothing in the simulation itself (only
the external-behavior wall-clock budget), so speed changes are replay-safe for
built-in behaviors.

### Additional communications
More meow vocabulary. Most valuable once relationships exist to talk about;
each new message needs a cooldown severity mapping like the existing six.

## P4 — world-scale ambitions

### Kittens
⚠️ Constitution note: adding kitties is lawful — Article II forbids removal,
not arrival — but population then only ever grows. Needs a birth-rate design
with a population cap tied to world capacity, or sequencing with expanding
worlds. Kittens are small, quick, and never in danger (Article I applies from
the first tick).

### Expanding worlds
Worlds that grow at the edges as the population does. Big engine change
(spawn bounds, snapshot compatibility, viewer viewport); enables kittens
long-term.

### State sharing between worlds
Kitties visiting other worlds / servers. Largest and least-defined item;
cross-world determinism and snapshot identity are open design problems. Last
on purpose.
