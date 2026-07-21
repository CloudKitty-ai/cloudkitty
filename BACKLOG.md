# CloudKitty Backlog

Prioritized future work. Everything here was deliberately kept out of the MVP
(see `specs/001-cloudkitty-mvp/spec.md`, "Out of Scope") or added since. Per the
constitution, none of it may violate Articles I–VI, and each feature goes through
the spec-first flow (`/speckit-specify` → plan → tasks) when it is picked up —
this file records priority and intent, not design.

Priorities: **P1** quick wins, next up · **P2** the bigger pieces, for a proper
sitting · **P3** simulation depth · **P4** world-scale ambitions.

## P1 — quick wins, next up

<!-- shipped P1 items are removed once merged; see git history -->

*Empty — the 2026-07-20 QoL batch (PR #16, specs 009–012) shipped all
three queued items: orthogonal-only interactions, water-averse pathing,
and sustained purring, plus the approach-etiquette / livelock fixes the
batch surfaced. The swim pose parked inside the water entry moved to P3.*

## P2 — the bigger pieces, for a proper sitting

### Dynamic element populations (added 2026-07-20 — ideate with the owner first)
Environmental elements are effectively static: `ensure_minimums`
(`spawn.rs`) tops every type back to its configured min on the very next
environment phase, only Article I safeguard spawns ever exceed it, and
the configured max is nearly dead config — so worlds sit pinned at min
counts forever. **That was never the intended behavior.** Goal: organic
ebb and flow that a viewer can feel — populations wandering between min
and max, expiry gaps that linger a little instead of refilling the same
tick, maybe time-varying spawn pressure (bug flushes, chow deliveries)
or spatial character (water spawning adjacent to water, which the 008
pond renderer would immediately reward with real merged ponds). Hard
constraints: never frustrating for the kitties — the Article I
safeguard's instant relief spawn is untouchable, and min still means
min; fully deterministic through the seeded RNG; tunables named in
config (Article VI). **Design not settled — this entry records intent
only; start with an ideation conversation, as the 008 direction was.**

### Meadow finishing touches: grass detail + world edge (deferred from 008)
**Shipped in 008** (PR #13, merged 2026-07-20 — "Beautification II, step 2:
the meadow itself", gate approved after two revision rounds):

- **Organic ground** — the checkerboard retired for four close grass tones
  plus barely-visible brightness jitter, all from a pure per-tile hash
  (identical across reloads, any world size, zero served data).
- **Ponds** — contiguous water merged into smooth wavy-shored blobs with an
  inner shallows band; lily pads on larger ponds; purely visual.
- **Sunbeams as light** — radial warm glow bleeding past tile bounds, under
  the unchanged 005 pulse and motes.
- **Worn paths** — session-local trail memory (`p` toggle, off by default),
  fading on a half-life, cleared on reload/discontinuity, never served.
- **Grid demoted** — the tile lattice is now a debug overlay (`l` toggle).

Two pieces were built, judged at the gate, and scrapped at the owner's
call for a proper art pass later:

1. **Grass detail** — scattered flora accents. Two attempts (tiny
   accents, then bigger/denser weighted tufts/clover/flowers) both read
   as sparse/odd noise rather than a living meadow. Next attempt should
   explore a different vocabulary: denser micro-texture (blade clusters,
   mottling) rather than discrete per-tile accents, judged at multiple
   tile sizes (16×16 renders at 45px, 64×64 at 11px).
2. **A world edge** — the grass-fringe frame (single row, then two-row
   hem) never landed. Consider the other 2026-07-20 ideation option: a
   low hedge or picket frame in the cats' outline style instead of
   blades.

The 008 scaffolding stands ready: `tileHash` in `client/meadow.js` is the
deterministic scatter source (per-tile hash of (x, y) — stable across
reloads, density proportional to area, no new served data), palette and
tunables homes established, harness in `client/test-meadow.mjs`. Day–night
lighting remains its own entry below and lands on top of this look.

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
boundary** above, which is the same sitting's prerequisite. Plugin docs must
also carry the multi-agent livelock warning (`behavior/mod.rs`): all kitties
decide against the same snapshot, so a deterministic external brain that
mirrors another kitty's moves can dance forever — advise symmetry-breaking
via the per-kitty seeded rng or id-based right-of-way, as the built-ins do
since 010/012. Deliberately P2:
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

### Chases route around friends (added 2026-07-20)
The one walk with no route-around: a chase step is applied engine-side via
the straight `Direction::toward`, and a friend standing in the lane stalls
the chase in place (`action.rs`, the Chase apply arm). Bounded, not a
livelock — the patience clock abandons a chase that stops closing — but a
kitty visibly frozen mid-pounce for up to `chase_patience_ticks` behind a
bystander is the same *flavor* of jank as the 2026-07-20 dance family.
Candidate fix: give blocked chase steps the seeded-shuffle sidestep the
behavior stepper got in 012 FR-008 (deterministic per Article V, never
synchronized). Design care: stalls currently *feed* the abandon/exclusion
tuning — more persistent chases shift how often greebles get written off,
so re-baseline `chase_patience_ticks` expectations in the same change.
Polish, not urgent; see `behavior/mod.rs`'s multi-agent livelock note for
the family history.

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

### Swim pose for wading kitties (parked 2026-07-20, from the 010 spec)
A kitty standing on a water tile shows a `swim` pose — pure view
(`poseFor` in `client/render.js` plus one new `cat.js` pose), with its own
mini gallery gate like the other cat art. Wading is deliberately rare
since 010 (kitties skirt ponds and paddle only when water is the only way
forward), which is exactly why this is low priority — but the paddling
fallback deserves its art when we are next in the cat-pose neighborhood.

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
