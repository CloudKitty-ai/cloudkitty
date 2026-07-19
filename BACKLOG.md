# CloudKitty Backlog

Prioritized future work. Everything here was deliberately kept out of the MVP
(see `specs/001-cloudkitty-mvp/spec.md`, "Out of Scope") or added since. Per the
constitution, none of it may violate Articles I–VI, and each feature goes through
the spec-first flow (`/speckit-specify` → plan → tasks) when it is picked up —
this file records priority and intent, not design.

Priorities: **P1** quick wins, next up · **P2** the bigger pieces, for a proper
sitting · **P3** simulation depth · **P4** world-scale ambitions.

## P1 — quick wins, next up

### Per-kitty need rates
Small, high-personality win: per-kitty overrides for need rise rates on top of
the global defaults (a perpetually hungry cat, a sleepy one). Config schema
addition + one lookup change; per-kitty values validated like the globals.

### Auto-backup the old world on `--fresh`
Today `--fresh` ignores the existing snapshot at startup, but the new world
overwrites it at the next save — the old world quietly dies unless the
operator remembered to copy the file first. That is the wrong default for a
sandbox whose whole ethos is that worlds are never lost by accident. Before a
fresh world takes over an existing snapshot path, move the old file aside
(e.g. `snapshot.json` → `snapshot-<tick>-<timestamp>.json.bak`, or a
`worlds/` archive directory) and log where it went. Considerations: the
rename must be atomic like every other snapshot operation; a `--fresh
--no-backup` escape hatch for operators who truly mean it; and a note in
`--help` and the README so the behavior is discoverable. Pairs with the
existing `--snapshot <path>` flag, which already allows keeping many worlds
deliberately.

### Display each cat's current action in its panel card
The kitty card currently has a single "mood" line doing two jobs: `moodFor()`
in `client/app.js` returns *activity* text when the cat is sleeping or
resting ("fast asleep", "cuddling") and only otherwise falls through to
*happiness* text ("delighted", "content", "wants something"). The two
overwrite each other — a napping cat's happiness description disappears, and
an awake cat shows no activity at all. Fix by splitting the card into two
separate, always-present fields:

- **Mood** — happiness-derived only ("delighted" … "needs a bit of help"),
  never masked by what the cat happens to be doing.
- **Doing** — the cat's current action ("eating 🍥", "chasing a bug",
  "grooming Biscuit", "meowing: I want to play!", "fast asleep",
  "cuddling with Miso"), covering every action, not just the two multi-tick
  activities visible today.

Small engine component required: applied actions are discarded after the
apply phase, so the engine must record each kitty's last applied action (the
post-validation one, so the panel shows what actually happened — an illegal
proposal reads honestly as idle) and expose it on the kitty in the wire
snapshot, e.g. `last_action`. Rendering stays a pure view (Article V): the
client formats what the server states, computes nothing. Friendly names for
targets (kitty names, element kinds) rather than raw ids.

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
