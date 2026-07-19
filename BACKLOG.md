# CloudKitty Backlog

Prioritized future work. Everything here was deliberately kept out of the MVP
(see `specs/001-cloudkitty-mvp/spec.md`, "Out of Scope") or added since. Per the
constitution, none of it may violate Articles I–VI, and each feature goes through
the spec-first flow (`/speckit-specify` → plan → tasks) when it is picked up —
this file records priority and intent, not design.

Priorities: **P1** quick wins, next up · **P2** the bigger pieces, for a proper
sitting · **P3** simulation depth · **P4** world-scale ambitions.

## P1 — quick wins, next up

### Fix low-happiness lock-in (needs RCA, 2026-07-18)
Kitties get stuck in low-happiness episodes (observed: 200–500 ticks below
happiness 45; all three cats touched the floor of 5 in a 6,000-tick window).
Root cause, confirmed against a live state file and reproduction run: when
play becomes unattainable, `needs_driven`'s hard safeguard lock ("pursue only
the most pressing need") starves every other need — including bath and sleep,
which are satisfiable on the spot — and the fixed tie-break order at the
100-clamp turns into a starvation queue (bath, last in the order, can never
win a tie). Play is the trigger because its relief throughput is too low for
an isolated cat: critters always exist, so the friend-play fallback is dead
code; greebles outrun cats; bug chases die to TTL. Improvements, in impact
order:

1. Replace the hard safeguard lock with proportional urgency — always weigh
   distance, with pressure counting more above the safeguard threshold.
2. Raise play throughput: opportunistic play in `take_what_is_here`, play
   targets chosen by distance across critters *and* friends, give up on
   futile chases (especially greebles).
3. Solo play as a backstop (pouncing on nothing), so every need is
   self-satisfiable in the limit — restoring the Article I assumption that
   play is always satisfiable.
4. Break pressure ties by longest-since-relief instead of `NeedKind::ALL`
   order.
5. Observability: per-kitty time-in-distress (the unresolved play distress
   sat visible-but-unwatched for 216 ticks).

<!-- shipped P1 items are removed once merged; see git history -->

## P2 — the bigger pieces, for a proper sitting

### Graphics refresh: Make even cuter!
All in `client/` — no engine changes. Candidate directions: real sprites (or
better emoji composition) instead of single glyphs, smooth movement tweening
between ticks, idle animations (tail flicks, ear twitches), softer
grass/water/sunbeam textures, more expressive sleeping and cuddling poses.
The viewer stays a pure view (Article V): cuteness only, no simulation logic.
Deliberately P2: worth unhurried design time rather than a quick pass.

### External behavior plugins (ScriptBehavior / HttpBehavior)
The payoff of Article IV's design: the async `Behavior` trait, wall-clock
budget, validation, and `NeedsDriven` fallback all exist so an out-of-process
brain can drop in with zero engine changes. Ship one reference implementation
(local script or HTTP endpoint) plus docs. This is the door to "an LLM decides
what the kitty does." Test scaffolding (`sleepy_slow`, `panicky`,
`always_invalid`) already covers the hostile cases. Deliberately P2: the
highest-value non-cosmetic item, held for a proper sitting rather than a
squeezed-in version.

### Friendship / relationship tracking (+ friend-proximity preference)
The foundational social feature. Kitties develop preferences from shared
history (play, co-sleeping, grooming); "friend" stops meaning "any other kitty"
and starts meaning *that* kitty; proximity preference makes bonded pairs drift
together. Unlocks meaning for "Follow me!" and most future communications.
Design care: relationship state must serialize into snapshots and stay
deterministic.

### Age / fur / eye stats
Cosmetic identity: fur colors and patterns, eye color, age. Sequenced with the
graphics refresh — fur is worth modeling when the renderer can show it. Age
must never become a health mechanic (Article II: no decline, no death; cats
may age into *distinguished*, never into frail).

### Day–night cycle and moonbeams
A world clock, dawn/dusk lighting in the viewer, moonbeams as the nighttime
sunbeam. Kitties are crepuscular — behaviors could weight sleep by hour.
Sequenced after the graphics refresh so lighting lands on the new look.

## P3 — simulation depth

### Food types and desirability (+ water-near-food rules)
Different chow kinds with desirability modifiers; cats prefer better food and
dislike water adjacent to their bowl. One food-system design covering both
spec items. The safeguard guarantee (Article I) must hold regardless of
desirability — a picky cat still gets fed.

### Ear / tail affect
Ears and tail express mood in the viewer (content, curious, grumpy). Pure
rendering on top of existing state; depends on the graphics refresh.

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
