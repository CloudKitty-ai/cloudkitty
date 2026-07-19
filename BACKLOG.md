# CloudKitty Backlog

Prioritized future work. Everything here was deliberately kept out of the MVP
(see `specs/001-cloudkitty-mvp/spec.md`, "Out of Scope") or added since. Per the
constitution, none of it may violate Articles I–VI, and each feature goes through
the spec-first flow (`/speckit-specify` → plan → tasks) when it is picked up —
this file records priority and intent, not design.

Priorities: **P1** quick wins, next up · **P2** the bigger pieces, for a proper
sitting · **P3** simulation depth · **P4** world-scale ambitions.

## P1 — quick wins, next up

### A legal config can still strand a cat (`tile_cost = 0`)
The lock-in fix (spec 004) is safe under the shipped defaults, but its
scoring can be switched off by configuration. `[behavior] tile_cost = 0`
passes validation (which only requires finite and ≥ 0) and zeroes the travel
term entirely — which also cancels the large sentinel distance that stands in
for "there is no way to relieve this at all". A need with no relief anywhere
then wins on pressure alone, and `pursue` has nothing to do about it: in a
world momentarily without chow, a hungry cat idles at high pressure while
bath and sleep sit free. That is the shape of the original lock-in, reachable
through a config an operator might reasonably try.

Two candidate fixes, the second preferred: require `tile_cost > 0`, or stop
encoding unreachability as a distance at all — skip needs with no relief path
during selection, so no weight can cancel the fact. The sentinel
(`UNREACHABLE = u32::MAX / 2` in `behavior/selection.rs`) is the smell.

P1 because it is the only open review finding that can actually leave a kitty
stranded, and because the fix is small and well understood.

<!-- shipped P1 items are removed once merged; see git history -->

## P2 — the bigger pieces, for a proper sitting

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

### Loose ends from the 004 review
Three low-severity findings from the post-merge review, none of which can
harm a kitty — grouped because they are all one sitting's work:

1. **Sleep is scored as free but may cost a walk.** `travel_distance` reports
   Sleep as distance 0, while `pursue(Sleep)` will walk up to 8 tiles to a
   sunbeam, so selection can pick sleep as "free" and then commit the cat to
   an 8-tick trek past food it nearly chose. That radius is also a hardcoded
   `<= 8` in `needs_driven.rs` — an Article VI magic number that survived the
   sweep which promoted `WORTH_A_DETOUR` and `TILE_COST` out of the same
   file, and a silent duplicate of the new `behavior.solo_play_reach`.
2. **A stale exclusion hard-fails a resume.** An expired `abandoned_chases`
   entry is a load-time constitutional violation, so a snapshot carrying one
   is refused outright ("start a new one with `--fresh`") over bookkeeping the
   next tick would prune harmlessly. Its sibling `distress_since` was
   deliberately given a self-heal path; this asymmetry is accidental. Prune
   on load, or make the invariant self-healing.
3. **The playmate scan runs twice per decision.** `choose_need` computes
   `nearest_viable_playmate` while scoring Play, then `play_action`
   immediately recomputes the identical result. Hand the target down instead
   of discarding it.

### Graphics refresh: Make even cuter!
All in `client/` — no engine changes. Ideation done (2026-07-18); direction
chosen: **procedural vector cats** over pixel sprite sheets. The deciding
arguments: fur patterns, eye color, and ear/tail affect all want *parameters*,
not frames (a sprite sheet multiplies facings × poses × moods × patterns until
it dies); continuous parameter easing composes with the interpolation clock
below, while frame-swapping fights it; and at 22px tiles the sprite quality
advantage mostly evaporates. Known risk: the aesthetic floor — a procedural
cat that reads as clip-art would be a step *down* from the emoji. De-risk
first: a static cat-portrait gallery page (all fur variants, all poses, no
animation) as the opening task, judged before anything builds on it; fallback
is sprites or emoji-faces-on-vector-bodies.

Scope, in build order (each phase ships a visibly cuter viewer on its own):

1. **Interpolation clock** — a `requestAnimationFrame` loop easing between
   the last two server frames, replacing draw-once-per-WS-frame. Position
   tweening plus a local clock for idle cycles. Still a pure view (Article
   V): the client never predicts, only eases between states the server sent.
   Tween duration from the tick interval via `/config`, not hard-coded.
2. **Vector cats** — `drawCat(params)`: bezier body/ears/tail, per-kitty
   deterministic palette (fur + eye color from kitty id, stable identity),
   left/right or 4-way facing derived from the last move.
3. **Action + idle animations** — pounce arc with squash-and-stretch for
   play/chase, eat chomp, drink ripples, groom licks, slow curl into sleep;
   idle tail flicks, ear twitches, blinks on the local clock.
4. **Dramatize data the viewer already receives** — solo play gets an
   imaginary sparkle to bat at (no greeble-secrecy issue: there is genuinely
   no target); chase abandonment gets its sad beat (sit, ear droop);
   `pursuit` gets determined eyes; sharp need drops get a brief relief
   sparkle; the distress cue gets an in-world thought-bubble twin using the
   same `viewer.distress_patience_ticks`.
5. **Ambient life** — water shimmer, sunbeam glow pulse + dust motes, grass
   sway, drifting cloud shadows; plus juice on existing elements (bubble
   pop-in, kibble level in the bowl, tweened canvas happiness bars).

Hygiene, same spec: respect `prefers-reduced-motion` (fall back to per-tick
snapping) and pause the rAF loop when the tab is hidden.

Explicitly deferred: day–night lighting (own entry below, lands on the new
look), ear/tail affect as mood display (P3, though vector cats make it nearly
free), zoom/camera work (unless worlds grow). Deliberately P2: worth
unhurried design time rather than a quick pass.

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
Cosmetic identity: fur colors and patterns, eye color, age. Sequenced with the
graphics refresh — fur is worth modeling when the renderer can show it, and
the vector-cat renderer shows it as parameters (fill colors, clipped pattern
overlays) rather than per-variant art. Age
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
rendering on top of existing state; depends on the graphics refresh — which
chose vector cats partly for this: ears and tail are already animatable
parameters there, so this item shrinks to mood-to-parameter mapping.
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
