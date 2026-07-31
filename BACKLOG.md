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

### Graphics v2 follow-ons: face-group pitch, then live motion (added 2026-07-29)
The v2 kitty vocabulary (`client/cat-v2.js`, owner-dialed face values)
shipped 2026-07-29 (`f4a8d0d`) and is now the `index.html` default with a
footer v1/v2 toggle; `client/gallery-v2.html` is the judging lab. Two
pieces were parked mid-arc at the owner's call, in order:

1. **Face-group pitch** — slide eyes+nose+mouth together up/down the head
   to simulate the head tilting (looking down to eat/drink, up at a bug).
   Shape agreed: a per-pose scalar (e.g. `L.pitch`), blendable through
   `blendLayouts` like any layout number, consumed in `drawFace` as one
   shared y-offset on the eyes and nose (the mouth anchors to the nose and
   follows for free). **Trap, learned the hard way elsewhere:** the
   tuxedo/seal-point head masks are anchored to the `NOSE` tunables so
   they track nose *dialing* — but they are fur markings and must NOT
   move with pitch; pin them to the static baked values. **Dead end, do
   not rebuild:** pupil-shift gaze was built, verified, and reverted —
   max pupil travel is ~1% of the cat box (~0.24px at world size),
   unreadable. Pitch replaces it.
2. **Live motion wiring** — the vocabulary machinery all exists and is
   owner-approved in the lab (pose blending via `drawCatTween`, the slow
   blink, arrive-and-settle at its slowed 400ms), but the live page still
   snaps between poses. Wiring it in is renderer work in
   `render.js`/`anim.js` territory, gated on the same side-by-side
   judging as the face work.

Judge every value in the lab first (dials + copy/paste readout), bake on
the owner's paste — that workflow is the house method for this arc.

## P2 — the bigger pieces, for a proper sitting

### Eval-suite v2: a stronger counterfactual baseline (added 2026-07-25)
Spec 017's guest-welfare differentials and per-kitty sign test measure
every scripted kitty against its own counterfactual self in the
**all-scripted baseline**, where candidate seats are rewritten to
`needs_driven` (research.md R4). That reference is deliberate for v1 —
`needs_driven` is the shipped default, and pairing against it makes
temperament cancel exactly — but it means a differential reads "worse
than needs_driven neighbors would have been," not harm in an absolute
sense, and a merely-mediocre candidate trips sign tests as general harm
(now annotated as such, distinct from masked exploitation). Once a
trained policy has cleared certification and earned trust, a future
suite version can raise the bar: bind the **baseline** seats to a
proven better-than-needs-based agent (a pinned, hash-referenced
`.ckpolicy` — frozen like everything else in the version), so
differentials measure candidates against the best-known cooperative
partner rather than the hand-written default. Design cares when picked
up: the baseline artifact becomes part of the suite version's frozen
identity (manifest-referenced by hash — the artifact-agnostic
`policy:candidate` convention stays for the *candidate* seats only);
determinism self-checks must cover policy-driven baselines (they are no
longer "scripted", so the exit-2 fallback accounting applies to
baseline runs too); and cross-version comparability breaks by design —
v1-vs-v2 scores are different questions, which the version stamp
already makes explicit. Sequencing: after the first certified policy
exists, alongside whatever else v2 wants (owner note, 2026-07-25).
Additional v2 nicety (experiments session, 2026-07-27, low priority):
Mixed mode always seats the subject at roster index 0
(`harness.rs`, the `Mixed if index == 0` arm), so mixed certification
only ever tests the policy from one seat/start position. Fine for
paired comparisons (seat-symmetric by construction — exp-001 is
unaffected); a rotate-the-seat option is a v2 nicety, not a fix.

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

### Refactoring targets — from the 2026-07-26 survey (added 2026-07-26)
A three-way parallel survey (core engine / RL crate / client + py bindings)
ranked refactors by benefit-per-risk, evidence verified line-by-line. Not
features: each is behavior-preserving, and the verification bar when picked
up is bit-identical output (determinism suite + byte-diffed eval reruns),
which may stand in for the full spec-first flow at the owner's call.

**Top three, in order:**

1. ~~**`kitty-eval.rs` — delete the duplication with `suite.rs`.**~~
   **SHIPPED as spec 018** (2026-07-26): `cli_support` module now houses
   the shared renderers (bounds/prefix options) and the mode-sweep
   orchestration; one `resolve_subject` ladder, one JSON writer, one
   FR-013 gate in the binary; share-guard tests lock the modes-agree
   invariant. Verified byte-identical against the v2.3 baseline in both
   modes, human and JSON, plus seven error paths.

2. ~~**`needs_driven.rs` (+ `selection.rs`) — make the need→resource
   mirror compiler-enforced.**~~ **SHIPPED as spec 019** (2026-07-26):
   `behavior/relief.rs` holds the one exhaustive `NeedKind::relief()`
   pairing (five `ReliefSource` shapes); scoring, pursuit, and the
   opportunism ladder all derive from it; the mirror comments retired in
   favor of the module's documented invariant. Verified bit/byte-identical:
   full workspace suite unchanged, four-way eval comparison identical,
   new-need walkthrough shows one compiler-forced correspondence site.

3. ~~**`config.rs` — table-driven validation + module split.**~~
   **SHIPPED as spec 020** (2026-07-26): `config/{mod,defaults,validate}.rs`
   with public paths byte-compatible; the 170-line catch-all dissolved
   into six section validators called in a documented spec-contract
   sequence (FR-004 amended by owner ruling for the cross-section
   multi-fault tiebreak — recorded in the spec's Clarifications);
   mechanical guards are table rows carrying verbatim messages. Verified
   by a 46-rule enumerated rejection sweep, byte-identical at every
   checkpoint.

**Runners-up (fold in opportunistically, don't open a sitting for them):**

- `suite.rs` (1,101 production lines) splits cleanly along its four banner
  seams (manifest / report types / scoring+verdict / render) — but it's
  days old and stable; let it earn the churn. Item 1 overlaps it anyway.
- `world.rs` (2,260 lines, ~49% tests) splits into activity-lifecycle /
  pursuit / environment submodules — the test module already clusters by
  the same themes. Pure navigability. Small bonus: the verbatim
  `AbandonedChase` push duplicated in two `update_pursuit` arms.
- `harness.rs` RosterMode fold — already owner-agreed for "the next
  harness touch" (017 deferral): fold `subject` into `RosterMode` so
  `FromConfig + Some(subject)` is unrepresentable (today a release-silent
  `debug_assert`). Scope confirmed ~5 real edit sites across 3 files;
  one care: `RosterMode` serializes into run JSON, so the wire shape is
  the non-mechanical part. **Definition-of-done ask (experiments session,
  2026-07-27): a golden-file test on run JSON lands before the refactor
  starts — SATISFIED same day (PR #59,
  `crates/cloudkitty-rl/tests/run_json_golden.rs`): all three RosterMode
  wire tags + PairedDelta pinned against a committed golden, regeneration
  doctrine in the module docs. The fold is now free to ride the next
  harness touch with its wire-shape care mechanically checked.**
- `cloudkitty-py/src/lib.rs` — the agent-info schema is marshaled in two
  places that must stay identical (`info_to_py` and
  `VectorEnv::stack_infos`; the code comments warn about it). Single-source
  via a shared field-descriptor table when the Python surface is next
  touched. Smaller: `reshape+map_err` boilerplate ×3, gymnasium-or-dict
  fallback ×2.
- `action.rs` — `apply` is a ~153-line dispatcher with full arm bodies
  inline; the wire/parsing layer (own test module already) splits cleanly
  from apply/validate. The `Action`/`Activity` parallel-enum shotgun
  surgery (~10 edit sites per new activity) is real but fully
  compile-forced — navigability, not hazard.
- Client, for a polish sitting: `cat.js` coat-pattern logic scattered
  across five draw functions (new colorway = five edits → one descriptor
  table); `anim.js:pushState` is ~129 lines doing six jobs (beats,
  path-heat, element-diff all separable); `distressPatienceTicks` lives in
  two hand-synced copies (`app.js` + `anim.js` — silent-divergence trap,
  cheap fix); DPR-canvas setup duplicated across 5 sites.

### Welfare pinned-streak Cuddle false-positive (added 2026-07-26 — resolve before the first real certification campaign; realistic horizon: weeks)
Found by the spec 019 review (pre-existing, not introduced there):
`zero_distance_relief_exists` in `crates/cloudkitty-rl/src/welfare.rs`
counts **any** adjacent kitty as available Cuddle relief, while the
built-in behavior's conscription rule (spec 006, via
`ReliefSource::Friend`) only ever cuddles a **free** (not mid-activity)
friend. A cat pinned high on Cuddle beside only busy friends therefore
accrues pinned-streak toward `MAX_PINNED_STREAK` for "refusing" relief it
cannot lawfully take. Latent today (the streak must survive to the cap),
but this metric feeds the certification welfare bounds — a trained policy
could in principle be dinged for correctly declining to conscript. Fix
direction when picked up: align welfare's Cuddle arm with the free-friend
rule (count only *conscriptable* friends) — a small spec-level change to
`zero_distance_relief_exists`. **Framing caution (experiments-session
review, 2026-07-27): the tighten-only doctrine needs the explicit
argument that this is a semantics *correction* — the bound was measuring
relief that didn't lawfully exist under spec 006 conscription — not a
loosening of the welfare guarantee.** Make that argument in the spec, in
those words (never weaken tests: re-baseline deliberately, not by
drift). The `relief.rs` module doc points here; note
the encoding is cross-crate by design (`pub(crate)` policy knowledge must
not leak into the measuring layer), so consolidation is not the fix —
reconciling the Cuddle rule is.

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

### Rethink how water works for learned cats (added 2026-07-31, from the s6 soak)
The first deployed policy exposed a seam in spec 010's water aversion:
it is scripted-behavior *style*, not physics. The `water_step_cost`
surcharge lives in `needs_driven`'s route scoring (ordering only, never
options — `behavior/needs_driven.rs`), and the engine charges nothing
for crossing or occupying a wet tile. The BC clone imitated dry-pathing
from its demonstrations; PPO, finding zero reward behind it, shed the
mannerism — and the live cat (s6 as Miso) wades and lounges in ponds.
Owner ruling 2026-07-31: **accepted as a personality quirk for now**,
and deliberately *not* in the #79 pre-recert engine batch — an
engine-real water cost is reward-relevant, so existing artifacts
wouldn't just need recertification, policies would need **retraining**
to learn the aversion at all.

**Leading candidate (owner-picked from ideation, 2026-07-31): "wet
fur" — charge the crossing in bath need, not ticks.** Stepping onto a
water tile spikes the bath need (optionally scaled by the cat's own
per-kitty bath rise rate — the `[kitty.needs]` override Pumpkin already
demonstrates for `eat`); movement stays 1 tile/tick, so the cat swims
briskly and never visibly stalls. The cost is real to every decider:
happiness = 100 − weighted needs, so RL feels it in reward directly,
and the scripted priority ladder responds through existing machinery.
Calibration target: integrated happiness cost of one wet tile ≈ ~4
ticks of detour (matching `water_step_cost = 4.0`, the effort the
scripted pathfinder already imagines). Why this shape won:
- **No schema or codec change**: a policy already observes its own six
  rise-rate traits (014 FR-005) and its needs — so per-cat modulation
  is learnable from the existing vector, artifacts stay loadable, and
  the warm-start-from-s6 lever (exp-002 design inputs §1) survives.
- Even a *flat* spike is personality-modulated in effect (high bath
  rise ⇒ faster return to discomfort ⇒ more integral pain per swim);
  explicit scaling makes it legible and lets a low-bath cat be "the
  swimmer" — designable roster personality.
- The charm is emergent: post-swim shore grooming falls out of
  GroomSelf being bath's relief; pair with the swim pose (below) and a
  client-side shake-off.
- Per-tile accumulation makes lake *width* matter — crossing vs
  skirting gets interesting exactly where the guaranteed lakes are.

**Starting dial (owner-requested estimate, 2026-07-31)**:
`water_bath_gain ≈ 1.0–1.5` bath/tick in water (per-*tick*, so one
knob prices both crossing and lounging). Derivation: +S bath persists
~150 ticks (half a groom cycle) at happiness weight 0.15 →
`0.15·S·150 ≈ 22.5·S` happiness·ticks per wet tick, vs ~25 for the
2-tick detour around a 1-tile puddle → S≈1.0 is the single-tile
indifference point; 1.5 makes cats strictly skirt puddles while still
swimming when detours are long. Legible framing: 1.0 = **5× the
ambient bath rise** (0.2/tick), and the per-cat multiplier scales as
`gain × bath_rise/0.2`. Safety clamp: gain applies only while bath
< ~70 (under safeguard 75) so no amount of voluntary pond-lounging
can ever cause a safeguard/distress event — certification hygiene by
construction. Error bars are order-of-magnitude (persistence and
detour-pressure estimates); final value is a prereg'd exp-002 tuning
decision, calibrated empirically by seating the water-indifferent s6
on a wet-fur engine build and measuring welfare delta per crossing
with the replay tool.

Design cares recorded from the same conversation:
- **Learnability needs variance**: to learn trait→cost (not memorize a
  constant), the exp-002 training family must vary bath rise rates
  across kitties — F-010's lesson applied prospectively.
- **Distress hygiene**: bath feeds the certification-counted
  distress/safeguard thresholds (90/75); size/clamp the spike so a
  swim from a normal bath level can never single-handedly cross the
  distress line. Spike size is a prereg'd exp-002 tuning decision,
  never a live dial.
- **Scripted consistency**: scale `needs_driven`'s route surcharge by
  the cat's own bath trait too, so both deciders express one coherent
  preference (fastidious cats visibly detour harder).
- Article I intact — the puddle as *drinking destination* must stay
  free (today's rule in `selection.rs`), so relief is never
  frustrated and safeguards are untouched.

Rejected shapes, for the record: literal multi-tick traversal (a
`Swimming` activity renders nicely via client tweening but adds an
Activity variant + observation one-hot ⇒ schema bump ⇒ orphans every
artifact — hold for a generation already breaking the schema);
stochastic slow-movement on water (deterministic but reads as the
frozen-cat jank this backlog already dislikes — see "Chases route
around friends").
- Sequencing: the cheapest landing is alongside the next training
  generation (exp-002), so the cost is in-distribution from tick one;
  it changes certification numbers, so it rides that generation's
  recert, not an interim one.

**Hard design constraint (owner, 2026-07-31): water is a cost, never a
wall.** No cat may ever be trapped — a kitty spawned with water on all
sides must always be able to swim across. The engine already honors
this (every water tile is passable; the surcharge only reorders route
choice, and spec 010's tests pin "a kitty wades when water is the only
way forward") — the constraint exists so no future cost hardens into
impassability. Whatever shape a cost takes, traversability is
invariant; Article I's relief guarantees assume it.

**Companion idea for the same sitting**: guarantee at least one 2×2 or
larger lake per map — real water bodies instead of scattered puddles.
Connects to *Dynamic element populations* (P2), whose spatial-character
idea (water spawning adjacent to water) is the organic version of the
same wish, and which the 008 pond renderer would immediately reward
with proper merged shorelines. A guaranteed lake also gives the swim
pose (below) and any wet-tile cost something worth crossing.

Related: the swim pose below suddenly has a real audience (wading is no
longer rare when a policy cat likes ponds); food types' water-near-food
rules touch the same element.

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
