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
<!-- (pyo3 advisory upgrade shipped 2026-07-23, spec 015 — the
     do-before-more-RL-work gate is retired) -->

## P2 — the bigger pieces, for a proper sitting

### Suite reporting/visualization tooling — standing constraint (added 2026-07-25)
No such tooling exists yet; this entry records a **binding design
constraint** for whenever it is built (dashboards, experiment trackers,
report renderers — anything that consumes `kitty-eval --suite` JSON).
The mixed-roster exam's per-kitty **sign test** (spec 017 FR-015,
research R12) defaults to *warn*: a triggered exploitation signature
exits 0 and lives only in the report and the JSON `sign_test` block.
That tier's entire value is visibility — a warn that can be missed is a
gate that silently stopped existing, and we have the scar to prove it
(the PettingZoo conformance step failed silently under
`continue-on-error` for months). Therefore: **any reporting or
visualization surface MUST display a triggered sign-test warning
prominently** — top-level, not buried in a table — alongside the
doctrine that a signature on a real candidate prompts a strict rerun
(`--enforce sign-test`) before the result is quoted. When the tooling
is specced, this constraint goes in its FRs on day one.

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
3. **Grass sway** — the 005-era ambient blades were removed 2026-07-22:
   their geometry was fixed-pixel (5.5px blades, 2.2px sway), which read
   as subtle grass at desktop's 22px tiles but as stray diagonal lines
   at mobile's ~10px tiles. Any return should be tile-proportional and,
   like the rest of this entry, judged at multiple tile sizes.

The 008 scaffolding stands ready: `tileHash` in `client/meadow.js` is the
deterministic scatter source (per-tile hash of (x, y) — stable across
reloads, density proportional to area, no new served data), palette and
tunables homes established, harness in `client/test-meadow.mjs`. Note
since 2026-07-22: the meadow renders under three palettes (day / golden
hour / night, PRs #37–#39), so new grass work must be judged in all
three, and any new color belongs in every `MEADOW_*` set.

<!-- "Harden the whole proposal boundary" and "External behavior plugins
(ScriptBehavior)" both shipped 2026-07-23 as one sitting (spec 016): strict
parse_proposal per action shape with round-trip + rejection suites, Article
IV amended to v1.2.0 (fallback and idle both named safe, fallback default),
ScriptBehavior with docs/plugins.md and the livelock warning. -->

### HttpBehavior — the remote plugin transport
The second transport for external behavior plugins, deliberately deferred
from spec 016 (clarified 2026-07-23): build it once ScriptBehavior has
proven satisfying in practice. Everything hard already exists and was kept
transport-agnostic on purpose — the hardened proposal wire, the
`DecisionRequest`/reply-envelope JSON bodies, `try_decide`, the budget /
breaker / fallback stack. This is a thin second speaker of the same
contract: the same request and correlated envelope over HTTP POST to a
configured endpoint. Spec'd as User Story 3 / FR-007 in
`specs/016-behavior-plugins/` — start there, not from scratch.

### ScriptBehavior transport residuals (from spec 016 review, 2026-07-23)
Three bounded, low-severity residuals the deep review of PR #45 surfaced
and accepted as not-blocking. Fold these in when ScriptBehavior is next
opened (likely the HttpBehavior sitting, which shares the exchange
machinery):
1. **Grandchild pipe-inheritance thread leak.** The per-child I/O thread
   reads the plugin's stdout; killing the plugin on timeout does *not*
   close that pipe if a grandchild inherited fd 1 (a shell wrapper, a
   leftover subprocess), so `read_until` never returns and the detached
   thread lives until the grandchild exits — one stuck OS thread per
   killed process, unbounded across relaunch cycles. The common wedge
   (no grandchild) is already fixed. Deeper fix: spawn each plugin in its
   own process group (`process_group(0)` on unix) and kill the whole
   group, so grandchildren die and the pipe closes. Also correct the
   `PluginChild::drop` comment, which currently claims the thread is
   "gone the moment the stream closes" — true only absent a surviving
   grandchild. `crates/cloudkitty-core/src/behavior/script.rs`.
2. **Shared-plugin mutex burst.** The instance mutex is held across
   `recv_timeout`, so when a shared plugin wedges, every sibling kitty's
   `spawn_blocking` thread parks on `self.lock()` for up to
   `exchange_timeout_ms` (default 1000) during the one relaunch+timeout
   tick per cooldown window. Bounded and self-limiting (siblings
   fast-fall-back once the first kitty marks the process Dead), strictly
   better than the pre-fix infinite hang. Mitigation today is a lower
   `exchange_timeout_ms` when many kitties share a process — already noted
   in `docs/plugins.md`'s shared-plugin caveat. Only revisit if per-kitty
   processes or a shorter default prove wanted in practice.
3. **Exec-bit precision.** Startup validation checks `mode & 0o111`
   (executable by *anyone*), not executability by the server's effective
   user, so a script executable only by another owner/group passes
   startup then fails every spawn. The common case (forgot `chmod +x`
   entirely) is caught; closing the gap fully needs an effective-uid/gid
   check, likely more than it's worth. Minimum: a doc note that the check
   means "executable by someone", not "by us".
   `crates/cloudkitty-server/src/lib.rs`.

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

## P3 — simulation depth

### Kitties learn each other's traits — anticipatory cooperation (added 2026-07-21)
A 014 follow-on, deliberately out of scope until the trained meadow is
proven working well (owner decision, 2026-07-21; recorded in 014's "Not in
this feature"). Today a policy kitty's observation carries its *own* static
traits (per-need rise rates, 014 FR-005) but neighbors appear in the kitty
slots with only their live state. Adding neighbors' traits to the slots
would let a policy anticipate — "Biscuit's metabolism runs hot, leave them
the bowl" — before the need is even high, instead of reacting to the
slots' current needs (the live form of the same signal, and v1's answer).
When it comes: an observation-schema version bump per 014's extensibility
doctrine, slot width paid per kitty slot, and worth pairing with a
training-ablation check that the traits actually earn their vector space.

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

### Cuddle puddles (added 2026-07-22)
More than two kitties cuddling or sleeping together in one pile. Low
priority, but touches real machinery when it comes: today's duets are
strictly pairwise (`Activity` carries one `duet_partner`, spec 006's
conscription and one-sided-end rules assume two), so puddles need a group
activity concept — join/leave semantics (a puddle of three survives one
kitty leaving; the last pair falls back to a duet), conscription that
doesn't let one kitty chain-conscript the meadow, and adjacency geometry
(tiles are exclusive, so a puddle is a connected blob of neighbors).
Naturally rewards warmth: cuddle relief might scale gently with puddle
size. Interplay to watch: 012's approach etiquette around a growing pile,
and 014's action menu — a join-puddle proposal is a codec version bump
under the extensibility doctrine. Viewer gets the fun part: a pile of
cats drawn as a pile.

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

### Crepuscular rewards — time-of-day enters the engine (added 2026-07-22)
The engine half of the world's sky. The viewer's full day–night cycle
shipped cosmetic-only (PRs #37–#39, owner call 2026-07-22): the hour is
a pure client function of the served tick (`hourForTick`, app.js) and
the engine knows nothing. When the trained meadow wants more challenge,
promote the hour into the engine and vary RL rewards by it — kitties
are crepuscular, so dawn and dusk could pay a premium for activity
while deep night favors sleep, teaching policies a daily rhythm instead
of a flat routine. Design cares when picked up: the hour must derive
from tick arithmetic in the engine so rollouts stay deterministic and
bit-reproducible; adding it to observations is a schema version bump
under 014's extensibility doctrine; the long-run welfare bounds must
hold at every hour — variable rewards may never starve a need (Article
I outranks the reward function); and the client's `hourForTick` retires
in favor of a served hour, keeping viewer and engine on one clock.
Sequencing: the pyo3 advisory upgrade that once gated RL work shipped
2026-07-23 (spec 015) — nothing blocks this but priority. (Replaces
the old P2 "Day–night cycle and moonbeams" entry, whose viewer half
is fully shipped.)

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
