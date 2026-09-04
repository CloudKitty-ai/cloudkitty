# CloudKitty Backlog

Prioritized future work. Everything here was deliberately kept out of the MVP
(see `specs/001-cloudkitty-mvp/spec.md`, "Out of Scope") or added since. Per the
constitution, none of it may violate Articles I–VI, and each feature goes through
the spec-first flow (`/speckit-specify` → plan → tasks) when it is picked up —
this file records priority and intent, not design.

Priorities: **P1** quick wins, next up · **P2** the bigger pieces, for a proper
sitting · **P3** simulation depth · **P4** world-scale ambitions.

## P1 — quick wins, next up

### `evals/v3`: the four wide exams re-cut at roster 5 (added 2026-09-04; Product thread; owner ruled "option 1")

Spec 049's permanent by-id kitty rows make the observation width a
function of the roster (`kitty_slots = roster − 1`), so `evals/v2`'s
`scale` (8 cats, 597 floats) and `mixed-roster-{guest,half,host}` (6
cats, 471) refuse a served-width (408) Gen 1 mind at artifact load —
`kitty-eval --suite evals/v2 --artifact <policy>` dies before a tick on 4
of 6 exams (`/code-review high 049` finding 1; PR flag 5). v2 is frozen
by its manifest, so the fix is `evals/v3`: the same six designs with the
four wide exams re-cut at roster 5 (`scale` = 5 cats on the 48×48 world,
keeping the dilution half of the question; mixed-roster cells 4 + 1,
3 + 2, 1 + 4), `heterogeneity` and `scarcity` carried unchanged, new
manifest hashes, the identity thresholds re-derived from the new roster
shares by the existing manifest unit test, `kitty-eval`'s default suite
→ v3, v2 listed in `config-sweep-exclusions.txt` as the record. Own
spec; lands after the 049 PR and before the step-7 seating smoke.

<!-- shipped P1 items are removed once merged; see git history -->

### ~~Critter play gets one grace tick when the critter slips away~~ — DROPPED 2026-08-23 (owner: "let's keep it as is")

Costed, then dropped the same day: the charm gain (the kitty keeps
playing for a beat after the critter escapes) did not justify the change
surface. Kept here because the mechanism is worth not re-deriving, and
because a future census WILL surface these numbers again.

**The behaviour is intended, not a defect.** `World::prune_dead_activity`
(world.rs:464) ends an element play scene when the element is gone **or
no longer adjacent**, and pruning runs before the duration minimum is
enforced. Critters move on alternate ticks (`(tick + id) % 2`) and play's
`min` is 2, so every critter play scene contains exactly one move
opportunity; when it breaks adjacency the scene dies at one tick. The
600-tick ttl is NOT the cause — measured scene expiry is 0.3% (15 in
5,244) against a ~20% cut rate.

**It is already priced.** The chase-census measures mean scene length
directly and `ev()` multiplies `scenes x mlen`, so the sticker corridor
was set against the real numbers: bug 1.8 · greeble 1.5 · duet 2.0. The
live served world reproduces the bug figure independently (20% of Biscuit
2.0's scenes ran one tick; 0.8x2 + 0.2x1 = 1.8).

**Why it was dropped rather than deferred**: implementing it needed two
coupled changes, not one — relax the prune AND add an adjacency check to
the relief arm, since `action.rs:769` resolves relief by element id and
kind alone and would otherwise pay the full sticker on the grace tick
instead of the ruled `solo_play_relief`. And the lift lands unevenly:
+11% bug EV against **+33% greeble** (greebles dart), pushing the
constrained side of the G1 bar. The note for future censuses now lives in
`experiments/bugs2-grid-analyze.py::ev`. Measurements:
`experiments/exp-006a-biscuit-corner/live-play-2026-08-23.md`.

### Serving welfare watchdog: max_distress_age on the served world (added 2026-08-20; owner-approved)

The engine already computes `distress_since` per (kitty, need); nothing
watches it continuously on the served world — the G6 soak watches were
stopped after the pass, by design. The exp-006 r5 forensics showed why a
standing watch matters: the co-sleep deadlock (F-027) ran a 2331-tick
distress streak while the engine's only safeguard (supply-side,
`spawn::safeguard`) was structurally blind to it — relief existed, nobody
went. Alarm line: the constitutional 150. This is the serving-side
detection layer; the offline layer is the tail-benchmark roster
(`experiments/tail-benchmarks/`). Detection only — intervention is the
separate P2 entry below.

### No harness drives the v2 cat through the RENDERER — MOSTLY CLOSED 2026-08-22

A structural coverage hole, found while gating the settle, and it has already
let one feature ship inert.

`render.js` branches on `v2Motion = typeof drawCatTween === 'function'`.
**Neither harness ever takes that branch.** `test-meadow` evals every file into
one scope, where render.js's bare `drawCat` binds to **cat.js's v1** function
(cat.js is eval'd first and its declaration wins), so `v2Motion` is false;
`test-motion` calls `CatV2.drawCat` directly and never goes through the
renderer at all.

So everything render.js does *around* a v2 cat is unguarded: the
`!v2Motion` guard on `canvasSettle`, the `settle` opt it passes, the eyes and
ears it overrides. Mutating `canvasSettle` to wrap v2 cats in the old canvas
squash — the exact mechanism that made the ear and tail outlines vanish —
**changes nothing in either suite.**

Cost to close: the harnesses would need cat-v2's symbols to win the bare-name
binding, which is the same globals trap recorded in 'every cat-v2 symbol the
page reads bare is actually installed'. Not attempted here; it is a harness
change, not a feature change, and it wants doing on its own rather than inside
an art PR.

**Closed 2026-08-22 for the three mechanisms named above.** `test-meadow`
gained a SECOND scope — everything `src` loads except cat.js, which is how
every lab already runs and what index.html's `Object.assign(window,
CatV2)` achieves for the page — plus four checks that drive real frames
through it: the scope is v2 and not the hybrid; the v1 canvas squash never
reaches a v2 cat (detected by ANISOTROPY, since cat-v2 does its own
uniform `scale(size, size)`); the settle arrives as a pose deformation
matching the tween; and the v1 ears boolean does not reach a v2 cat. All
four mutation-verified — including the one this entry said changed
nothing: flipping `canvasSettle` to wrap v2 is now red.

Two notes for whoever picks up the rest:

- **The original scope is still the hybrid, deliberately.** The meadow
  checks want v1 present for vocabulary comparisons; the v2 scope sits
  beside it rather than replacing it. Putting cat.js back in front of the
  v2 scope is a load-time SyntaxError (the install's `const drawCat`
  collides with cat.js's declaration), so the two cannot quietly merge.
- **Remaining slice: the EYES.** `render.js` also does
  `if (v2Motion && motion.blinkLid !== undefined) { lid = motion.blinkLid;
  if (eyes === 'closed') eyes = undefined; }` — the eased lid replacing the
  snap blink. Nothing asserts that yet. The fixture is the cheap part now:
  `v2Frame()` exists, and a frame taken mid-blink (see the slow-blink
  schedule in test-motion) would show `lid` present and `eyes` cleared.

### The give-up droop is EARS ONLY — SHIPPED 2026-08-20

Owner reported half-closed eyes on cats that were **walking**, in every
direction, lasting longer than a tick — then, decisively: *"ears go down with
the half closed eyes as well."* That pairing is the signature.

`render.js`'s `sad` beat set `ears`, `earsHold` AND `eyes = 'half'`. It is
applied **after** the pose, so it overrode a walk, and `sadBeatMs` is **1600 —
two full ticks**. It fires when a cat abandons a chase, and such a cat is
usually still moving, so it landed exactly where it was most visible.

**Nothing in the pose system could produce it**, which is why four separate
paths came back clean and cost an hour: the walk layout is always `'open'` in
all three views (proven by draw-log identity against a forced-open cat),
`motionFor` returns before the blink block for `'walking'` (0 lids in 400
samples, against 7.8% for idle), and the tween switches eyes at the midpoint so
a blend gives closed or open, never half. **A beat painted over the pose is
invisible to every question you can ask the pose.**

Owner: *"keep the ears, drop the half-lid."* Which is the hunter-eyes decision
again — the ear channel carries what the eyes were being asked to. `lid =
undefined` went with it: it existed only so a deep blink could not promote the
FORCED half-lid into the happy closed arcs.

**The guard is blunt on purpose.** `test-meadow` binds render.js's bare
`drawCat` to cat.js's **v1**, so the opts cannot be intercepted — but v1 draws a
half-lidded eye with fewer primitives than an open one (118 vs 128), so op
count discriminates. It needs a POSITIVE CONTROL to mean anything: op count
cannot see the ears, so "droop fired, eyes untouched" and "no droop at all" are
the same number. Verified by renaming the beat's kind, which passed until the
control existed.

### The cat's eyes and Clementine's coat (added 2026-08-20; owner's queue)

Four items the owner queued after the landscape arc, in her order. They are
listed together because three of them are the same underlying cause: **the art
was dialled when a cat was ~31px and camera mode now draws her at 57–103px**,
so decisions that were invisible economies at low resolution are legible
choices at high one.

1. **~~Clementine's fur dial~~ — CLOSED by owner ruling, 2026-08-21
   ("Clementine is done"), same day the `--fresh` seated her generation.**
   The per-cat white override was never written and the owner ruled the
   shipped coat stands; the deadline is discharged by decision, not by
   code. Kept struck rather than deleted so nobody re-derives the
   "designed white cat" intent from the trait sheet and reopens it.

2. **~~Deprecate the hunter eyes~~ — SHIPPED 2026-08-20 as a substitution.**
   The reason is better than "it did not read", and worth keeping: *"the v1
   hunter eyes read cute at low res, but as we get higher and higher res the
   'fierce' hunting behaviour is not the chill cute vibe we're going for — I'm
   fine with the chasing kitties behaviour being the default for everything."*
   The face was not drawn badly; it was **off-brief, and low resolution had
   been hiding it.**

   Gone: `expressionFor`, `PURSUING_ACTIONS`, `hunterGateTiles`, the view
   passthrough and the renderer's expression term — all of which existed for
   this and nothing else. Kept: `pursuitDistanceFor` (tested, three separated
   outcomes, and the queued gaze work wants it) and the DRAWING —
   `FOCUS_VARIANTS` plus `eyesOverride: 'focused'` are still dialled and still
   exercised by the gallery and by v1. **Retiring the world's route to a face
   is not the same as deleting the vocabulary**; those 79 lines of owner-judged
   values are a separate decision.

   It also drops "hunting kitties do not blink" (owner, 2026-08-02),
   deliberately — the point is that a hunt is drawn the way play already is,
   and players blink.

   Superseded original entry: **a SUBSTITUTION, not a deletion.** Owner,
   2026-08-20: *"they don't read well any more and we've seen repeated
   behavioural issues so we'll just disable them going forward"*, then, asked
   whether the hunt should become invisible: *"the ear/gaze of play/chase
   kitties looks good, so we should keep that for chasing prey — i.e. same
   behaviour for chasing prey as for chasing kitties."*

   So the rule is **one chase expression, not two**. What goes is the
   hunter-specific eye variant (`FOCUS_VARIANTS`); what a cat chasing a bug
   does instead is exactly what a cat chasing a kitty already does. That is a
   unification, and it is worth more than the deprecation: the two cases were
   the same behaviour wearing different faces, which is how one of them got to
   be wrong without the other noticing.

   **This resolves the conflict with the animation residue's follow-up 1**
   ("ears forward on the hunt", below). Ears-forward is NOT deprecated — the
   chase expression already carries it, and unifying the two cases delivers it
   for prey without a new channel. Do not implement follow-up 1 separately;
   check whether this item has already done it.

   The hunter face has checks pinning that it does not outlive its quarry.
   Expect them red, and point them at the chase expression rather than
   deleting them — the invariant they encode still holds, it just has one
   subject now instead of two.

3. **~~Replace the half-closed eyes in RESTING poses~~ — SHIPPED 2026-08-20.**
   Owner: they *"read fine during transitions — slow blink, falling asleep —
   but don't look great as a resting pose at our new higher resolution"*, and
   *"fully closed eyes replace the lid."*

   **Two poses, and it was the existing convention rather than a new one:**
   eating, grooming and sleep-curl already closed; `drinking` and `loaf` were
   the two that missed it, from when a cat drew at ~31px and a lid and an arc
   were the same two pixels. `stretch` keeps its half-lid deliberately — it is
   a transition, already resolving to closed at the top of its push — and that
   exemption is now pinned so it reads as a decision.

   The lid position was never wrong; its PERSISTENCE was. Passed through in
   200ms a half-lid is a blink; held at 57–103px it is a sleepy cat.

4. **Design output for the settle-in-place and north/south walk animations —
   DELIVERED, and queued for tomorrow.** Both are done and owner-approved, in
   `design-handoffs/design_handoff_camera_pass/`. The third item of that brief
   (four legs on groom/stand) is specified but **not started**, so it stays
   with item 3 of the eye work rather than arriving with these two.

   The bundle's `client/` files are our own sources edited in place, not mocks
   to reimplement, and the dialled values in `AXIAL`, `AXIAL_ENDS.back` and
   `AXIAL_CAMERAS.elevation` are **owner-approved shipped values, not
   starting points**. `review/` is not for the repo. `SETTLE-EDITS.md` carries
   the settle as a standalone edit list.

   **THE MERGE HAZARD, and it is not hypothetical.** The bundle forks from
   `main` at **`95958ca`** (PR #266). We have landed #267–#270 since, and they
   touch two of the five files it ships:

   - `client/anim.js` — +64 lines. Their copy has no `ceilingRows` at all, so a
     wholesale copy silently reverts the landscape row cap to nothing.
   - `client/test-motion.mjs` — +197 lines. Their copy predates the row-cap
     guards, the recorded landscape layout, the outcome check and the
     control-pin check.

   Their README says it outright — *"diff against that commit rather than
   against tip before copying"* — and that is the instruction to follow:
   `git diff 95958ca <bundle>/client/<file>` gives THEIR delta; apply that,
   never the file. `index.html` is not in the bundle, so the sundial work is
   not at risk.

   The north/south work still has a measured, costed entry in this file. Read
   it before accepting the proposal, not because the proposal is suspect but
   because "do nothing" was a legitimate answer there and the owner chose it
   once — the entry says what changed her mind is worth knowing.

   **Missing from the bundle:** `NEXT-SESSION.md` opens *"`HANDOVER.md` is the
   reference for the vocabulary itself … Read it first"*, and there is no
   `HANDOVER.md` in it. Ask Design for it before starting, or work from
   `README.md` and `SETTLE-EDITS.md` and expect to be missing the *why*.

   **THE SETTLE SHIPPED 2026-08-20**, wired from the bundle by hand: `anim.js`
   `settleMs` 400 → 460 and the `settle`/`sy` emission, `render.js`'s canvas
   squash narrowed to the **v1 path only**. Their `anim.js` delta carried a
   revert of `minTiles` 7 → 6 in the same file; only the two settle hunks were
   applied. The `SETTLE` amplitudes are the owner's lab values, confirmed
   identical to the shipped block across all 11 keys.

   **The lab card is in `gallery-v2.html`, and how it drives matters**: each
   cat WALKS and then ARRIVES, because `drawCat` runs
   `applyRig(applySettle(L, settle), rig)` and the head lag and tail
   follow-through come from the RIG reacting to the stop — `applySettle` only
   drops the head 0.04 of a box. A first version handed a static cat a settle
   amount with no rig; the owner spotted it immediately as "more dramatic, and
   there's no head motion", which is exactly what a deformation with nothing
   riding it looks like.

   4a. **The ear and tail outlines vanish and reappear during the settle —
   an ACCEPTANCE CRITERION of 4, not a follow-on. GATED 2026-08-20.** Owner, 2026-08-20: *"we
   need to verify that is squashed when we implement the new settle."* So the
   settle does not land until this is checked; it is not something to notice
   afterwards.

   **It is almost certainly NOT deliberate**, which the owner suspected it was.
   The mechanism is `render.js:1729`:

   ```js
   ctx.scale(1 + (1 - tween.sy) * 0.7, tween.sy);
   ```

   An **anisotropic canvas transform** wrapped around the whole cat drawing.
   Canvas2D scales STROKE WIDTHS with the transform, so compressing vertically
   (`sy < 1`) thins horizontal strokes — a hairline ear or tail outline falls
   under a device pixel, disappears, and returns as `sy` relaxes. That is a
   side effect of the cheat, not a choice. It read acceptably at a 22px tile
   because the outlines were already sub-pixel there and the silhouette carried
   the shape; at 103px the outline IS the drawing.

   **The new settle removes the mechanism by construction rather than tuning
   it**: the canvas squash runs on the v1 path only (`canvasSettle = !v2Motion
   && …`) and v2 deforms in pose space. So the expected outcome is that this
   is already fixed — which is exactly why it needs asserting rather than
   assuming.

   **The check, at the cheapest layer:** drive a v2 settle through the harness
   at rest and at the curve's peak, and assert the outline stroke widths are
   IDENTICAL — the mock ctx already records every draw argument. Equivalent and
   simpler: assert no `scale` is applied on the v2 path at all during a settle.
   Assert on the stroke width, not on the absence of a call, if only one can be
   had: the width is the thing that vanished.

   If it somehow survives the rework, the remaining candidates are a z-order
   flip or an alpha term — they look identical at 31px and nothing alike at
   103px, so judge at the large size.

### One palette key for every cache that bakes one (added 2026-08-17; Client thread)
`applyTheme` now publishes `renderer.paletteKey`, and the pond layers carry it
in their own signature. The ground cache is still invalidated the other way,
by an explicit `renderer.groundCache = null` in that same function. Both are
correct; together they are two mechanisms for one rule, and the next cache
that bakes a palette colour gets forgotten exactly as the pond layers were.

End state: both caches carry `paletteKey` in their own staleness check and
`applyTheme` stops nulling anything. **Deliberately not done alongside the
pond fix**, because it rewrites a working ground cache to repair a broken
pond one, and `render.js` has already shipped an incident where a cache guard
mismatched every frame and rebaked the whole ground at 60fps (the note lives
in `resizeFor`). Pick it up when the ground cache is open anyway — camera
mode (spec 036) reworks it to bake at a camera tile.

### The ground bake outruns its budget at high dpr (added 2026-08-18; Client thread)

`bakeTileFor`'s comment and 037's contract invariant 6 both promise every
per-frame ground blit is a downscale. **It is not, above dpr ~2.05**, and it
was not before 037 either. `GROUND_BAKE_MAX_PX` is 4096 **device** px, so the
budget is `4096 / dpr`; a 100px floor tile on a 20-tile world wants a 2000 CSS
px bake and gets clamped to 1365 at dpr 3, leaving `this.tile / bakeTile` at
1.46x — a magnified ground under crisp vector cats, in steady state at the zoom
floor.

`tile / bakeTile`, main → this branch:

| map | dpr 2 | dpr 2.625 | dpr 3 |
|---|---|---|---|
| 620px | 1.00 → 1.00 | 1.00 → **1.28** | 1.00 → **1.46** |
| 1000px | 1.00 → 1.00 | 1.28 → 1.28 | 1.46 → 1.46 |
| 1200px | **1.17 → 1.00** | **1.54 → 1.28** | **1.76 → 1.46** |

037 **improves the worst case** (1.76 → 1.46, because the floor tile stops
growing with the display) and **widens the affected band downward** — from maps
≥800px to ≥460px at dpr 3. Offscreen memory grows with it: a 620px map at dpr 2
goes 25 MB → 64 MB.

Three ways out, none of them free:

- **Cap the camera's floor by the bake budget** — never zoom in past the tile
  the cache can carry at this dpr. Keeps the invariant honest at the cost of a
  little zoom on high-dpr displays, and couples two things that are currently
  independent.
- **Raise `GROUND_BAKE_MAX_PX`.** 4096 is a conservative texture bound; the
  memory is the real cost, and 64 MB of offscreen is already sizeable.
- **Accept it and say so.** The clamp's own comment already budgeted for
  "magnifies slightly" — this is that, at a magnitude nobody measured. Both
  docs now state the caveat rather than the promise.

**No camera-on test exercises dpr > 2** (`test-motion.mjs` pins dpr 2 at
cssWidth 1200, which is the one combination that just clears the budget), so
whichever way this goes it wants a check that varies dpr.

Found in review of PR #246. Not a 037 remediation — it spans 036's cache design
and 037's floor, and the fix is a decision rather than a repair.

**SETTLED 2026-08-19 — "measure F, accept C."** The owner took the third option
now and asked for a measurement before spending anything on the first two.

- **C is DONE.** `render.js` and `specs/037-camera-zoom-targets/contracts/zoom.md`
  both state the caveat instead of the promise. Nothing is blocked on what
  follows; this is an optimisation on a working, honestly-documented state.
- **F is the fourth option, and measuring first narrowed it sharply:**
  **camera-OFF can never blow the budget** — it bakes at the whole-world tile,
  so the offscreen is exactly `cssWidth`, capped at 1200. Every clamped case is
  camera-ON. So F is *"keep the bake for camera-off, draw the ground live only
  in camera mode"*, and the identity path 036 worked so hard for is untouched.
- **The measurement is `client/bench-ground.html`** (this PR). Headless says the
  JS side is free at 0.10ms, but it **cannot** measure rasterisation, and 3,529
  draw ops per frame is the open question.

**MEASURED 2026-08-19 — F PASSES on BOTH legs, and by an order of magnitude.**
Owner ran `bench-ground.html` on the dpr-3 handset, the worst case in the table:

| map | visible | bake (once) | blit /frame | live /frame | share of 16.67ms |
|---|---|---|---|---|---|
| 640px | 14x14 | 0.7ms | 0.00ms | 0.20ms | 1% |
| 840px | 15x15 | 1.3ms | 0.00ms | 1.45ms | 9% |
| 1000px | 15x15 | 1.7ms | 0.00ms | 0.65ms | 4% |
| 1200px | 15x15 | 1.0ms | 0.00ms | 1.30ms | 8% |

Highest across several runs: **1.6ms**. Every reason to trust it points the same
way:

- **dpr 3 is the worst case.** The clamp binds above dpr 1.81; a dpr-2 laptop is
  barely inside it.
- **Measured at the CEILING**, which is the most tiles the camera ever shows —
  ~15x15 = 225 tiles against the floor's 6x6 = 36. Same rasterised area, six
  times the ops.
- **Run on a contended box** (four PPO arms). Per the asymmetric reading, a fast
  result under load is trustworthy: idle can only be faster.
- **The live number OVERSTATES the delta.** The bench draws `cover: true`, but
  the real bake is `cover: false` — ground cover is already drawn per frame,
  sorted against the cats. So part of what was timed is work today already pays,
  and the true marginal cost is *below* the figure above.

**One caveat, which does not threaten the conclusion.** The 840/1000/1200 rows
have IDENTICAL op counts (all 15x15) and should rise monotonically with tile
size; they came back 1.45 / 0.65 / 1.30, a 2.2x spread on identical work. That
is noise, consistent with the contended machine. It is far smaller than the ~10x
margin to the frame budget, so the magnitude is robust even though the individual
rows are not.

**HOW TO BUILD F — read this before picking it up; it is NOT a flag.**
Investigated 2026-08-19 by reading the drawing path, after the measurement
passed and before any code was written. The plan implied a switch in
`render.js`; there isn't one.

**Two things make `drawMeadowGround` world-anchored, and both bite.**

1. **It hashes on its loop indices.** `smoothNoise(x, y, salt, cells)` and every
   `tileHash(x, y, …)` in `drawGroundDetail` take the loop counters, which ARE
   world coordinates. Call it with a smaller `width`/`height` to draw "just the
   visible part" and it draws tiles 0..n of the WRONG PART OF THE WORLD, anchored
   to the viewport. The meadow's tone, jitter, patches, tufts, flowers and shrubs
   would then slide underneath the camera as it pans. Very visible, and it would
   not show up in a still screenshot.
2. **`blurredLayer` allocates a scratch canvas sized to the whole field**
   whenever the radius clears 0.05 — and the radius is
   `groundBlurTiles * tile` with `groundBlurTiles: 0.32`, so it always does.
   Drawing the world live at the camera's floor tile means
   **113 x 20 = 2260 CSS px, x dpr 3 = 6780 device px square, ~184 MB, every
   frame** — and it blows the same 4096 bound this whole entry is about. A naive
   live draw is strictly WORSE than the bake it replaces.

**So the irreducible core of F is a world-coordinate REGION parameter** on
`drawMeadowGround`, e.g. `view = {x0, y0, x1, y1}` in integer world tiles,
defaulting to the whole world so today's callers are byte-identical. The
benchmark already assumed this — it passed `visible x visible`, which is why
**1.6ms is a faithful target and not an optimistic one**.

**Four things have to be threaded, and the last two are the easy ones to get
wrong:**

- **The tone loop** — bound to the region, still hashing on world `(x, y)`.
- **`blurredLayer`** — sized to the REGION, not the field, with the `paint`
  callback offset by `-x0 * tile` / `-y0 * tile` so world coordinates still land
  correctly inside the smaller scratch. This is the change that actually buys
  the memory back; getting the offset wrong shifts the whole mosaic.
- **The field-wide sun wash** — its gradient MUST stay anchored to the world
  field (`w`, `h` from world dims), because it is keyed to `shadowLean` so the
  light cannot disagree with itself across the map. Only the `fillRect` narrows
  to the region. Re-anchoring the gradient to the region would make the sun
  move with the camera.
- **`drawGroundDetail` and `driftField`** — same region bounds, same world-coord
  hashing. `driftField` builds a `width x height` field; it must stay
  world-sized (it is only ~400 entries) or the drifts re-roll as the camera
  moves.

**The invariant to protect above all else: camera-OFF must stay byte-identical.**
036 SC-007 and SC-012 say the camera-off view is indistinguishable from the
build before camera mode existed, and the whole bake path is what they were
written against. F keeps the cache for camera-off and draws live ONLY in camera
mode; the default-region path must produce the same pixels it does today.

**A cheaper variant that needs the SAME region parameter**, if per-frame ever
proves too dear: cache the visible WINDOW instead of the world and re-bake only
when the integer tile window changes (roughly once per tile crossed, ~1/s while
panning). The scratch is then viewport-sized rather than world-sized, so the
4096 bound is never in play. Not needed at 1.6ms, but it means the region
parameter is not wasted work under either design.

**No existing helper to reuse.** `bushesFor` builds a whole-world list every
frame, which is cheap because it is list-building rather than rasterisation, so
it is not the region pattern F needs.

**Test plan, at the layer each bug actually occurs:**

- A region draw and a full draw must paint the SAME TILES THE SAME WAY — draw
  both, compare the ops for the overlapping tiles. This is the check that
  catches the sliding-mosaic bug, and it must be seen red by hashing on loop
  index instead of world coordinate.
- The offscreen must never exceed the viewport in camera mode. Assert on the
  scratch canvas's dimensions, not on a timing.
- Camera-off must still bake, and bake the same thing. The existing identity
  checks cover the second half; the first needs asserting explicitly or F could
  silently switch camera-off to the live path and still look right.
- **Do this in the same pass as the `resizeFor` fixture below.** F opens exactly
  that neighbourhood, and the two are one careful sitting rather than two.

**Where that leaves the four options:** capping the camera's floor by the bake
budget and raising `GROUND_BAKE_MAX_PX` are both **moot** — F costs a tenth of a
frame and removes the magnification instead of trading against it. C stays as the
honest description of what ships until F does.

**THE dpr-2 LEG, 2026-08-19 — the one that actually decides this, because it
is the only hardware where the defect exists:**

| map | visible | bake (once) | live /frame | share of 16.67ms |
|---|---|---|---|---|
| 640px | 14x14 | 0.3ms | 0.10ms | 1% |
| **840px** | 15x15 | 0.7ms | **0.35ms** | **2%** |
| 1000px | 15x15 | 0.7ms | 0.35ms | 2% |
| 1200px | 15x15 | 0.7ms | 0.40ms | 2% |

**Read the 840 row: the owner's desktop lays out a 760px map** (recorded, not
assumed — `client-measurements`). So the fix costs **2% of a frame exactly
where the softness is**.

**And it refutes the prediction that sent us looking for this number.** I
argued the phone's 1.6ms would not transfer, because a dpr-2 desktop at a
large map rasterises 5.76 Mpx against the phone's 1.3 — 4.4x the pixels. It
transfers the other way: the desktop is **4x CHEAPER than the phone despite
4.4x the pixel load.** Hardware dominates pixel count, and a Mac is simply not
an iPhone. Pixel-count arithmetic predicts the ORDER of cost within one
device; it says nothing useful across devices, and I used it as though it did.

Note also this run is clean where the phone's was not: 0.10 / 0.35 / 0.35 /
0.40 rises monotonically with map size, against the phone's 1.45 / 0.65 / 1.30
on identical op counts. The phone's spread was thermal, not measurement error
in the harness.

**So F is settled on both legs: it costs 2% of a frame on the hardware that
needs it, and the hardware that would cost most to draw (the phone, 1.6ms)
never clamps and does not need it at all.**

**The earlier laptop figure came in at 0.4ms peak** — four times faster than the phone,
and that is the number that retires the whole "wait for a quiet box" concern.
The laptop IS the box carrying the four PPO arms; the phone carries none. So
the slower device was slower on hardware, not on contention, and the contended
machine turned in the better figure. The asymmetric reading held: a fast result
under load is trustworthy because idle can only be faster, and we never needed
to spend Experiments' campaign on it.

**Why the phone was the right leg to run first.** The budget is `4096 / dpr`
against a need of `floorTile × world.width`; at `floorPx` 113 that is 2260 CSS
px, so the clamp binds above **dpr 1.81**.

**CORRECTED TWICE, 2026-08-19. Both earlier readings were wrong; this one is
computed from `bakeTileFor` and `limitsFor` directly, not from the dpr
threshold.** The clamp does not key on dpr alone — it keys on
`bakeTile x 20 > 4096 / dpr`, and `bakeTile` is `cssWidth / floorTiles`, so the
MAP SIZE is half the condition. Where it actually binds:

| dpr | binds from a map of |
|---|---|
| 1 | never, at any map up to the 1200 cap |
| 2 | **615px upward** |
| 3 | 410px upward |

**On the hardware the owner actually has:**

| device | dpr | map | magnification |
|---|---|---|---|
| phone 16 Pro | 3 | 380 | **1.00x — clean** |
| WQHD | 1 | 1200 | **1.00x — clean** |
| laptop retina | 2 | 1200 | **1.10x — soft** |
| 4K at 2x | 2 | 1200 | **1.10x — soft** |

**So the defect is dpr-2-DESKTOP-only, not phone-only.** The phone never reaches
the clamp because `minTiles` holds the floor, which keeps the bake tile small.
**`minTiles` is therefore a hidden input to this clamp**, and it has since
moved: at 6 a 380px map wanted 1267 CSS px of bake against a 1365 budget — a 7%
margin, and a 420px map would not have fitted at all. **At `minTiles: 7`
(shipped 2026-08-19) the same map wants 1086 of 1365, a 20% margin, and the
420px case now fits too** (1200 of 1365). Lowering it to 5 would push the phone
over. The direction is worth remembering: **more tiles means a smaller bake**,
so the dial that costs apparent size buys bake headroom.

**And it moves where the BENCHMARK has to be run.** Live-draw cost scales with
device pixels rasterised, `(map x dpr)^2`: the phone is 1140^2 = 1.3 Mpx, a
dpr-2 desktop at a 1200px map is 2400^2 = **5.76 Mpx, 4.4x the phone**. The
1.6ms phone figure does not transfer. **The binding measurement is dpr 2 with a
large map, and we do not have it yet** — the 0.4ms "laptop" run may well have
been the dpr-1 WQHD, which is the one display with nothing wrong with it.

### Camera logic: what it aims at, and the trip in between (added 2026-08-18; Client thread)

**RESOLVED by spec 038 (camera shot picker, 2026-08-21).** The aim-chase is
gone: the camera decides a shot per tick and moves in latched, snapping
episodes, so the easing tail this entry diagnosed is structurally impossible
rather than damped — the "snap the aim within an epsilon" fix named below
grew into the whole episode engine. The empty eased frames measured here are
closed by 038 SC-002 (the subject is always kitties, and a break re-frames
before the count reaches zero). The measurements and the roster caveat stay
below because they are the record 038's numbers are judged against.

Owner's call, 2026-08-18: **accepted as-is for spec 037, dialled when camera
logic is improved.** Not to be implemented alongside 037.

**Every "of 5" below is the roster AFTER the cutover, not the one serving
today.** The trace was recorded against a 5-kitty world; the live world runs
**four** until the exp-006 certification run passes and the config goes to five
(owner, 2026-08-19). That is not an error in the measurements — it is the
roster they will be true of — but it has a direction worth knowing: fewer
kitties means a smaller spread, so the camera is bound LESS often today than
the 76% measured, and this problem gets **worse at cutover, not better**.
Anyone comparing these figures against the live world will find them
pessimistic until Clementine is seated.

Under 037's pixel ceiling a 340px map frames ~6.8 tiles while the clowder
spans a median 16.2, so a phone shows **2.81 of 5 kitties** against 4.12
today, and sees all five 5% of the time against 44%. It also draws **3 empty
frames per 1500 ticks**, which 036 SC-005 says never happens. Measured in
`client-measurements/037-zoom/sc006-2026-08-18.md`.

The cause is precise and worth not re-deriving: **the target frame is never
empty — the easing is.** 0 empty targets against 3 empty eased frames. The
anchor guarantees a kitty where the camera is heading, and 036 FR-008 forbids
cutting so it must travel there; once the frame is ~7 tiles the trip between
two anchors crosses more empty grass than the frame is wide.

Owner's directions, to investigate rather than take as settled:

- **Aim at the largest group when not following**, rather than at the kitty
  nearest the centre of mass. Today's anchor is a centrality choice
  (`anchorFor`), not a cluster choice, and on a split clowder the most central
  kitty can be the one standing alone between two groups.
- **Cut, rather than pan, between groups.** This is the easy fix for the empty
  frame — and note it **contradicts 036 FR-008 as written** ("The camera MUST
  NOT cut. Every change of aim and of width is eased"). That is not a blocker,
  it is a requirement to amend deliberately: the client already has precedent
  for a deliberate discontinuity in `Presentation.pushState`, which treats a
  >1-tile move or a non-consecutive tick as a jump rather than easing a lie.
  Whoever picks this up should amend FR-008 with the exception rather than
  quietly ship a cut against it.

  **Refined by the owner, 2026-08-19:** "must not cut" was right for the
  baseline, and the exception is narrow — **a deliberate, occasional transition
  to recentre on a larger out-of-frame group**. The MECHANISM is open: "could be
  a fast pan instead". A fast pan is probably the better answer — it keeps
  continuity, and it makes FR-008 an easing-RATE exception rather than a hole in
  "never cut", which is a far smaller amendment to defend.
- **Close in when nobody is on the periphery — SETTLED 2026-08-19, and it is
  the highest-value item here.** The owner's evidence: "zooming out to the
  ceiling to show a 4th cat if 3 are already in frame is probably not ideal",
  and "multiple instances where zoom was at or near ceiling with two cats in
  frame, and the composition would have been much better zoomed in".

  **Measured on the recorded world at a 1100px map, and it is worse than it
  sounds:** the camera is at its ceiling **76% of ticks**; while there it shows
  **3.53 of 5** kitties and is down to **one or two 10% of the time**; and it
  spends **13.3 tiles to frame cats that span only 10.8** — it could zoom to
  **81% of the width and lose nobody**, making those cats ~23% bigger.

  **The mechanism, which makes the rule obvious:** once `bound` is true the fit
  has ALREADY failed — the frame cannot hold everyone whatever it does — but the
  width stays pinned at the ceiling, because `across = min(max(fit…), ceiling)`
  and the fit is enormous. The camera pays the full zoom-out price for a fit it
  never achieved.

      while the fit governs, size to everyone, as now.
      once it CANNOT, stop trying — size to the group the camera actually chose.

  That is the "ignore the outliers" reading, not a feedback loop on the frame.
  It delivers all three of her observations at once, and it needs no new dial —
  the anchor choice already exists and simply starts carrying the WIDTH decision
  as well as the aim.

  **PR #247 made this the main case, not a corner:** tightening the ceiling took
  `bound` from 19% of ticks to 76%, so "what should the camera do when it cannot
  fit everyone" is now three-quarters of the experience.

**These three are one feature, not three.** Aiming at the largest group and
sizing to the cluster are the same decision seen from the aim and the width;
cutting is what makes that decision affordable, because a cluster-aimed camera
moves further when it moves at all. Speccing them separately would produce
three dials that fight.

Not to be confused with the anchor **hysteresis**, which was a different
small-viewport fault (restlessness, 036 SC-006) and is fixed — 1.5 → 2.5 in
PR #245.

### ~~Dissolve the map's edge in CAMERA MODE ONLY~~ — DROPPED 2026-08-20

**Owner: "we can forget about the camera edge dissolve for the foreseeable
future, our recent map border/landscape changes make it moot."** Deferred on
2026-08-19, dropped the next day, and the reason is the interesting part: the
question it existed to answer was *what should the map's edge be when the
camera is cropping an arbitrary window rather than showing the world's
boundary*. The hairline answered it by being thin enough not to assert
anything, and the landscape work then made the edge mostly leave the screen —
the canvas fills the viewport, so on a phone the top and bottom edges are
scrolled past rather than looked at. The original reasoning is kept below in
case Fog or a resizable window brings the question back.

Owner's call after the edge-treatment lab, 2026-08-19: **the hairline ships now
(phone), the dissolve is a later item.** Not a rejection — a deferral with a
reason worth keeping.

**The idea.** Fade the meadow's outermost ~14px to transparent instead of
ending it on a line. The map keeps every pixel of its size; only the last band
stops being opaque.

**Why it is a camera-mode question and not a styling one.** The edge means
different things in the two modes, and only one of them is a lie:

- **Camera off**, the edge IS the world boundary. The meadow really does stop
  there. A hard edge is the truth, and dissolving it would say "there is more
  beyond" about a world that has no more.
- **Camera on**, the edge is an arbitrary crop and there IS more meadow past
  it. A hard line there says the world ends where the viewport does.

Same reasoning that made the letterbox right: tell the renderer what is
actually true rather than what is convenient.

**What the lab settled, so it is not re-derived:**

- The natural edge is **not a constant** — grass-to-page swings from **ΔL* 0.1
  at dusk to 18.5 at dawn**, a factor of 180 across one day. So a dissolve does
  its most visible work at dawn, where the edge is already loud, and is a
  **no-op at dusk**, where grass and paper are the same lightness. Any dissolve
  that ships needs a per-hour answer, not one radius.
- It **softens the horizon the sky dial pins to** (`bottom: calc(100% -
  var(--stage-pad))`, owner 2026-07-23: "exact wins"). The dial has to be
  settled first; the owner sequenced it that way deliberately.

**Open, and not answerable from a still frame:**

- **Motion.** A kitty walking through a fading band is a different question
  from a fading band holding still. A half-faded cat at the boundary may read
  as a bug rather than an effect.
- **Cost.** Drawn in-canvas it is per-frame work on a budget already under
  question (see the high-dpr bake above); drawn as a CSS mask it forces a
  compositing layer. Neither is free and neither is measured.

### Phone portrait: the horizontal gap beside the map — SHIPPED (PR #248, 2026-08-19; Client thread)

Owner, 2026-08-19: "a bit of a horizontal gap around the map in portrait that
could get us another free tile or so." **Shipped the same day as option F —
body sides 10px → 2px, mat 5px → 4px, 12px of total chrome.** The measurement
is kept below because the `minTiles` decision still ahead reads it, and
because the step arithmetic outlives these particular numbers. Measured, not
estimated — and it is **two gaps, only one of which is anyone's to reclaim.**

On a phone `body` pays `padding: … 10px` and `.stage` a 5px mat, so the width
budget is `viewport − 30`. Then `resizeFor` floors the tile, and a 20-tile
world throws away everything the budget carries past a multiple of 20. The
stage is `width: max-content`, so that remainder does not sit inside the mat —
it appears as extra cream **outside** the stage's rounded edge, which is why it
reads as one gap rather than as rounding.

On the owner's 16 Pro (402 CSS px): **16px of cream each side — 10 of padding
and 6 of quantisation.**

Chrome is the reclaimable half; the quantisation is not, and cutting chrome
**moves pixels into it** until the budget crosses the next multiple of 20:

| viewport | budget now | tile | map | slack | body 10→6 | body+mat → 8px |
|---|---|---:|---:|---:|---:|---:|
| 360 small Android | 330 | 16 | 320 | 10 | 320 | **340** |
| 375 SE / 8 | 345 | 17 | 340 | 5 | 340 | **360** |
| 393 iPhone 12–15 Pro | 363 | 18 | 360 | 3 | 360 | **380** |
| **402 iPhone 16 Pro** | 372 | 18 | 360 | **12** | **380** | 380 |
| 412 Pixel / Galaxy | 382 | 19 | 380 | 2 | 380 | **400** |

So the free tile the owner saw **is real and is specific to her handset**: the
16 Pro is the one width whose budget sits just under a multiple of 20, and
trimming the body padding to 6 takes it 360 → 380 (+5.6%) with the slack going
to zero. **No other listed handset gains anything from that same edit.** The
360px Android snaps at 20px total chrome (body 6 + mat 4); 375, 393 and 412 all
need the map taken to the screen edge before they move at all.

**Why it is worth more than 5.6%: it lands on the `minTiles` decision.** The
camera's floor tile is `cssWidth / minTiles` once `minTiles` binds, so the map
width is the phone's cat size, one for one:

| map | `minTiles` 6 | `minTiles` 7 |
|---|---:|---:|
| 320 | 53.3 | 45.7 |
| 340 (today, SE) | 56.7 | **48.6** |
| 360 (today, 16 Pro) | 60.0 | **51.4** |
| 380 | 63.3 | 54.3 |

The 48.6px that makes `minTiles: 7` cost the 50px bar **is the 340px map, not
"the phone"** — on the 16 Pro `minTiles: 7` already clears 50 today. Reclaim
the gap and a 375 viewport reaches 360 too, at 51.4px. So the question changes
shape: not "state a phone exception to the 50px rule" but "keep 50 with no
exception on every listed handset except the 360px Android, and pay for it out
of the bezel". **Do the two together**, or `minTiles` gets decided against a
floor that was about to move.

Note the same 340 is written into 037's **SC-001** — "the smallest cat in the
range is fixed at 340/`minTiles` = 56.7px … so the spread is simply
`floorPx / 56.7`", which is what caps `floorPx` at 113. At a 360px map that
becomes 60px and the cap moves to 120. SC-001 is being discarded (owner,
2026-08-19), so this is not a reason to act — but it is the second criterion
found resting on an undeclared 340, and if anything ever re-derives a floor
target from "the smallest supported map", **that number is a measurement of the
CSS, not a constant.**

**The decision this needs, which is the owner's:** the body padding is shared —
`body` is the flex column, so zeroing its sides pushes the *cards* to the screen
edge as well. Reclaiming it for the map alone means moving that padding onto
`header`/`.panel`/`footer` and letting the stage run to the edge, which is a
look, not a refactor. The mat itself is already an owner-set number (16 → 6 on
2026-08-05, "6px is kitten.me's mat width exactly"), and `#sky-dial` pins to
`--stage-pad`, so changing the mat moves the horizon with it — by design, and
worth re-checking by eye at the new value rather than trusting the variable.

**What shipped, and what is still open.** Option F (12px chrome) was chosen
over the cheaper 20px step because **it is the only one that moves the 50px
bar**: at `minTiles` 7 the 20px step clears 50 on 3 of 5 handsets, exactly as
today, while 12px clears it on 4 of 5. The 16px option is **strictly
dominated** — identical maps to 20px everywhere. Still open: whether the
CARDS should keep an inset while the map runs to the edge, which needs the
padding moved onto `header`/`.panel`/`footer` and is a look, not a refactor.
**A guard exists as of PR #260**: `client/test-motion.mjs` drives the real
`resizeFor` against four layouts recorded off real devices, so the chrome
arithmetic is no longer only checked by eye. It does not cover the *choice* of
chrome, only that the measurement is faithful.

**RESOLVED 2026-08-19 — `minTiles: 7` shipped.** The pairing worked as the
entry argued: with the gap reclaimed first, 7 clears the 50px bar on 4 of 5
listed handsets (the 360px Android is the one exception, at 48.6px) rather than
being decided against a floor that was about to move. Two consequences that the
tables above do NOT show, both measured off the shipped `Camera` rather than
derived:

- **It is not a phone-only dial.** The break-even is `minTiles × floorPx` =
  791px, so every map *below* that loses apparent size at full zoom — a 640px
  map goes 106.7px → 91.4px per tile, a 760px map 113px → 108.6px. Maps at or
  above 791px do not move at all.
- **At 340px the zoom range goes to nothing.** The floor asks for 7 tiles while
  the ceiling's own 50px target asks for 6.8, so the ceiling is raised to meet
  the floor and that map pans without ever zooming. Zoom range first appears at
  a 351px map, against 301px before. Accepted under the ruling that zoom range
  is instrumental, not a goal.

037's **SC-001 was the casualty**, and it fired rather than failed — its own
margin note had predicted this exact trade. Withdrawn on the owner's 2026-08-19
call and replaced by the per-device bar it stood in for; see the spec. Note the
knock-on: SC-001 was what capped `floorPx` at 113, and **that cap is gone with
it**.

**Durable vs perishable:** the arithmetic
is durable — the wasted remainder is `budget mod world.width`, and the phone's
cat size is `map / minTiles`. **Every number in both tables is perishable**: they
assume the 20-tile served world (`cloudkitty.toml`), and a wider world under Fog
re-rolls which handsets sit just under a boundary. Re-run the arithmetic against
the world that is actually served before spending a design decision on it.

### Connect-time frame backlog — SPEC PARKED (added 2026-08-15; Product thread)
Spec 032 is written, decisions settled, implementation deliberately parked
(owner). The live socket gains an opt-in connect-time backlog of recent
frames so the viewer's deepened delay line — the anticipatory-gaze lookahead —
is full at first paint instead of after ~15s of visible slow motion, and
reconnects heal at full depth. **Do not re-derive the design**: every settled
call (socket over `/history`, opt-in default-0, ring inside `Published`
sharing the once-per-tick serialization, strictly-increasing ticks,
empty-after-restart, cap 16 as a config dial) plus the quantified costs and
the client-boot simplification live in `specs/032-ws-backlog/spec.md` +
`design-inputs.md`. Pickup = `/speckit-plan` from there. Related demand
logged there too: a served travel goal (Client should wire gaze to the
existing `pursuit` field first).

### Manual pan/zoom controls for camera mode (added 2026-08-21; owner's ask at the T026 judging; Client thread)

The owner, on shipping spec 038: "later on I'd like to add manual
pan/zoom controls." Scope sketch, to be specced when picked up:

- **Interacts with the shot grammar**: a manual gesture must suspend the
  grammar (a viewer override, like the follow pin) and hand back cleanly
  — the release path is the design's hard part, not the gesture.
- **Standing rulings that bear on it**: pinch zoom is a FALLBACK, never
  the default requirement (owner, 2026-08-19); zoom range is
  instrumental and becomes a scored feature only if manual zoom lands
  (same ruling); the 037 band should probably still clamp manual zoom's
  extremes.
- **Prior art in-repo**: the follow pin (FR-014) is the template for a
  viewer override with camera-owned state; `limitsFor` already provides
  the legal zoom band; wheel/pinch/drag listeners would be app.js's
  first camera gestures (the cards' tap plumbing is the nearest code).
- Spec-first when picked up (engine untouched; client-only, but it is a
  public interaction surface — new spec, not an 038 amendment).

### ~~Custom north/south groom animations~~ — DONE, owner ruling 2026-08-24

Owner: *"already done, it was in the handover."* It landed with the
GROOM-OTHER-EDITS pass and has been live since.

The check behind that ruling was run on 2026-08-24 — `GROOM_OTHER` byte-equal
to the handover's on all 25 dials, the axial branch differing only in comment
wording. It is **not re-runnable today**: `design-handoffs/` was a local drop
and was never committed, so the comparison cannot be repeated from this tree.
Recorded as history rather than as something a reader can verify.

The guidance below is kept because it is still the map for whoever touches
that branch next — the coupling note in particular has cost three rounds.

### The original entry (added 2026-08-22)

Social grooming shipped v1 with a real end-on treatment, not a fallback —
`grooming-other` is in `AXIAL_POSES`, and the axial branch in `applyAxial`
carries its own seated body, the near/far head-size depth cue, four legs
and the two tail routings. That is where a custom drawing lands when
Design delivers: replace the branch's geometry, keep `clampAxialHead`'s
two floors (skull share above the shoulders, tail tip clear of the
finished head) unless the new drawing makes them moot.

Read the coupling note in `GROOM_OTHER` before touching any of it:
`axialTailUpY`, `axialTailClearHead`, `axialHeadWide` and `axialHeadShow`
interact, and three separate rounds lost the rear tail cue to exactly
that. The lab's groom-other card draws all three views at once for this
reason. N/S is the MAJORITY case (54% of groom targets), so it is worth
the custom art.

Also still first-cut and dialable after a live look: `VIEW.groomLean`
(0.22 tiles, 450ms) — judged in the lab at full lean, never yet watched
easing in and out on the served world.

### Four paws at phone sizes: the seated poses need a haunch mass (added 2026-08-22; from GROOM-OTHER-EDITS; owner's call)

Design measured it at the delivered defaults: the seated poses hold four
readable paws from roughly 70px up, and below that the leg band merges
into one mass (side hind 2.1–2.8px and a 1.0px margin at 50px, against
lab floors of 6px to read as a leg and 3px as a paw). Four limbs have to
fit in 0.17 of a box between where the hind pair clears the body and
where the chest ends — the one-ellipse seat's ceiling, not an untuned
dial. Separating them at 50px needs a haunch mass so the belly can sit
higher, which is an addition rather than a tweak. Self-grooming hit the
same wall. NOT resolved silently: the owner decides whether the phone
band is worth the new geometry.

### SIT.hindX leaves two illegible legs (added 2026-08-22; from GROOM-OTHER-EDITS; owner's call)

Carried over from the sit pass and unresolved: at `SIT.hindX 0.5` two of
sit's legs measure 2.5px and 3.7px at 120px. Design reports 0.53–0.54
buys them back. The current value was judged by eye, so moving it is the
owner's call rather than a fix.

### `L.seated` — a declared seat flag, HELD 2026-08-23 (from GROOM-OTHER-EDITS-update; owner: "hold it and bank it")

Design's follow-up to the groom-other handoff proposed a third seated
signal. Verified scope with `diff GROOM-OTHER-EDITS-update.md
GROOM-OTHER-EDITS.md`: the 31KB update is identical to the pass shipped
in #293 apart from one idea, in three places — `L.seated = true` in the
side `grooming-other` pose, `seated: late.seated` in `blendLayouts`
(switched, not lerped), and prose asking for the same line beside the
`seatCy` call in `grooming` and `sit`.

**The principle is right and the code already holds it.** A seated pose
is a KIND of pose, not a tilt magnitude — and `cat-v2.js:1391` already
declares exactly that as `L.axialSeated`, read by `clampAxialHead` at
`cat-v2.js:1584`. That is the only place in the client that asks whether
a pose is seated, and it already reads a declaration rather than
thresholding anything.

Held for three reasons, none of them about the idea:

1. **Nothing reads `L.seated`.** No consumer in the update doc, none in
   the client. Written in three poses, carried through the blend, never
   asked about — so no check can defend it. Delete the line and the
   suite stays green by construction. The comment above the insertion
   point already says this about `earsUpright`: "Dropping it changes no
   drawing, which is why the check below it cannot see it."
2. **The threat it names does not exist.** The comment justifies the
   declaration because a `rot` threshold "sweeps up `eating` (0.07) and
   `drinking` (0.05)". There is no `rot` threshold in `cat-v2.js`,
   `render.js` or `anim.js` — checked for all four comparison forms and
   `Math.abs`. Nothing infers seatedness from tilt today.
3. **The `sit` hunk cannot be applied as written.** `seatCy` has exactly
   two call sites, `cat-v2.js:3165` (`grooming`) and `cat-v2.js:3246`
   (`grooming-other`). `sit` does not call it; it states `cy: 0.665`
   against `rot: -0.4` at `cat-v2.js:3347`.

**When a consumer appears, widen — do not add.** The likeliest triggers
are a shared shadow, or Design's N/S groom work needing the side view to
know it is seated. The cheap shape then is to rename `axialSeated` to
`seated` (two sites) and set it in the side poses too — one field rather
than two names for one fact. Checked safe: `grooming` and `sit` are not
in `AXIAL_POSES`, so they can never reach `clampAxialHead`, and widening
the flag cannot change its behaviour.

Two details worth keeping if it is ever built. `seated: late.seated` as
a midpoint switch is correct in kind — half-seated is not a thing — and
matches `tailBehind`/`pawUp`/`view`; it becomes load-bearing the moment
a PAINTER reads the flag, because `blendLayouts` silently drops what it
forgets (that is the `view` bug's whole story, documented at the
insertion point). And `axialSeated` deliberately needs no blend carrier:
`clampAxialHead` runs inside `catLayout` (`cat-v2.js:3412`), before any
blend sees the layout.

`design-handoffs/` is gitignored, so this entry is the durable record —
the update doc itself lives only in the working copy.

### Phone controls get the developer-menu treatment — DEFERRED 2026-08-22 (owner: "let's leave the phone as is for now")

The desktop footer now hides its developer toggles behind `d` (greebles,
grid, happiness, buffering, kitty version, theme — cards/purr/d stay).
The owner wants the PHONE controls reevaluated the same way once the
desktop version has settled: what the touch footer shows by default, and
how a keyboardless device reaches the developer set at all (the g/l/p
keys are keyboard-only by design — mobile-debug-toggles ruling). Scope
when picked up.

**Owner's ruling, 2026-08-22: leave the phone as is.** Not withdrawn —
the desktop `d` menu shipped and settled (PR #290) and the reasoning
above still holds whenever this is picked up again. Nothing about the
phone footer is believed wrong today; it simply is not worth a pass
right now.

### The pounce is the loudest pose the action-first rule extends (parked 2026-08-23; owner: revisit at the next model generation)

Not a bug and not queued — parked with a ruling, so it is not re-derived.

The owner read the post-cutover world as pounce-heavy ("almost excessive,
very little walking"). Measured and answered in
`client-measurements/pose-census/recensus-2026-08-23.md`: the drawing is
faithful, the rate is the roster, and `pounceGateTiles` went 4 -> 3 (#303)
for a 0.8-point trim.

What remains is a shape, not a rate. Reading `last_action` ahead of
`activity.state` — the 2026-08-13 fix for cats standing idle on the last
tick of every scene — extends every action by the tail of its engagement.
For eating that is a head-down cat held a beat longer, which nobody
notices. For play it is a crouch, a launch and spec 039's lunge held a
beat longer, which everybody does. The measured ratios say the rule is
even-handed and the POSE is not: play 1.88x, eat 1.99x, drink 2.01x.

So the lever, if it is ever wanted, is a **lower-energy tail pose for a
play engagement with the full lunge reserved for the catch** — design
work, judged in the gallery first, never a dial. Do NOT reach for the
pose ORDERING: reverting action-first puts cats bolt upright at the end
of every meal, nap and groom (drink was drawn idle 49.8% of its ticks,
eat 50.0%).

**Owner's ruling 2026-08-23: "we wanted more play and we got more play …
we'll see what happens with the next gen of models and I'll worry about
it then if it still looks excessive."** Do not re-open before then.

### A mutation runner that snapshots by construction (added 2026-08-23; tooling, LOW priority)

Every red-first pass this session hand-rolled a `mutate-*.sh` that edits a
source file, runs the suite, and restores it — and one of them restored by
`git checkout`, which ate uncommitted harness work and cost a rebuild.
CLAUDE.md rule 5 now carries the lesson ("Undo means revert: commit first,
or keep a copy to restore from"), but the rule is a discipline where a tool
would be a guarantee.

Shape: take a file, a list of (find, replace) mutations and a command;
`cp` the file aside FIRST, apply one mutation, run, record pass/fail,
restore from the copy, repeat; refuse to start on a dirty tree for the
target file. The value is that the restore path cannot consult git, so it
cannot widen to files the run never touched. Small — an afternoon — and it
retires a script that has been rewritten from scratch at least six times
(`mutate-groom.sh`, `mutate-size.sh`, `mutate-lick.sh`, `mutate-dial.sh`,
`mutate-v2render.sh`, …).

### Real heatmaps replace the worn paths (added 2026-08-21; owner's ask; LOW priority)

The spec-008 worn-paths overlay is shipped UNAVAILABLE as of 2026-08-21
(`VIEW.meadow.paths: false`, both homes; the owner: "disable worn paths
for the time being"). Visitors never saw it (`showPaths` defaults off,
008 FR-009) — this also inerts the p-key debug overlay. The successor
she wants is a real heatmap: presumably occupancy-weighted colour over
the ground rather than per-tile bare-earth patches. The 008 machinery
(`pathHeat`, decay, `wornPaths()`) still runs underneath and is the
obvious data source; the work is the presentation. No deadline.

### Lookahead for the camera — spec 032, revisited 2026-08-20 (Client thread)

**The idea (owner):** use 032's buffer for smoother camera pan and zoom, not
just for the gaze. Render frame n−10 while holding the newer 10, and the
camera has a 10-frame lookahead.

**Why it fits the camera better than it fits the gaze.** The camera eases at
`panRate` 0.06 / `zoomRate` 0.05, so it structurally LAGS the group, and the
only lever today is raising those rates — which trades lag for jumpiness. A
lookahead breaks that trade: aim where the group WILL be and the camera arrives
WITH the cats at the same easing rate. It lands directly on the queued
"transition fast between groups — a fast pan may beat a cut", because knowing
the destination early is what lets a pan start early and finish on time.

**LATENCY IS NOT A COST, and two sessions have now got this wrong in a row.**
Every pixel is derived from the frame being rendered — meows, need bars, the
tick readout, and `drawSkyDial(world.tick)`, which is the frame's tick and not
a wall clock. A deeper line moves all of it together, so there is no reference
left to notice it against. At depth 10 the meadow runs 8s behind live and
nobody can tell. **Do not re-raise a latency objection**; the reasoning and its
one boundary condition live at `paceTargetDepth` in `anim.js`, which is where
the decision is actually made.

**So the cost is the FILL, and 032 is exactly that.** A deep line fills by
running slow — ~14.6s of visible slow motion at depth 5 — on every page load
AND every reconnect. That is not a cold-start footnote at these depths; it is
the whole user experience of the feature, which makes **032 required to ship a
lookahead camera, not an optimisation on top of one.** 032's ring is
server-side (inside `Published`, cap 16); the delay line is client-side. Both
pieces are needed, and a 10-frame lookahead fits under the cap with headroom.

**Sequencing, and it matters.** The camera's measured defect is a SIZING
decision — bound 76% of ticks, 13.3 tiles for cats spanning 10.8 — not lag, and
lookahead does not help pick a better subject. Do the camera-logic work first,
lookahead second, or the judging is confounded: a lookahead will want
`aimDeadzoneTiles` and `panRate` re-dialled and you cannot dial those against a
camera whose aim is still changing.

**Judging is client-only; shipping is not.** `paceTargetDepth` is a client dial,
so the question "does lookahead visibly improve the pan" can be answered by
raising it, waiting out the fill once, and watching — no Product cycle, no
reviving a parked spec. Worth testing 5 as well as 10: the lag being fixed is
about one easing time-constant, which may not need ten ticks of warning.

**Blocked on the wall either way.** 032 is a socket change, and only
`update.sh --client-only` deploys are safe until phase 1 certifies and seats —
the same gate as Clementine's palette.

### The gaze — TABLED for a longer session (added 2026-08-10; Client thread)
Owner's call: the look wants a proper sitting, not a dial pass wedged into
another arc. Turned OFF on the card meanwhile — `VIEW.cardScanWeight: 0`, its
12 weight parked in `cardRestWeight`, so no other beat's rate moved. Turning it
back on is one number.

**It is already ONE gesture — do not "merge" it.** `gaze` is a single rig
channel and the pupils, the head and the ears all come off it
(`RIG.gazePupil` / `gazeHead` / `gazeEar`). The design intent is intact; what
is wrong is the magnitude.

**The measurement, at full deflection, so it is not re-derived:**

| channel | @31px (map) | @47px (portrait) | dial |
| --- | --- | --- | --- |
| ear tip | 1.25px | **1.90px** | `gazeEar: 0.2` |
| pupil | 0.48px | 0.73px | `gazePupil: 0.36` |
| head follow | 0.35px | **0.53px** | `gazeHead: 0.05` |

For scale: the body bob was reverted at 0.56px peak-to-peak. (The whiskers
were cut twice at ~0.8px and then shipped at it — see the closed entry
below; a stroke width alone does not settle whether a feature reads.) So
**only the ears clear the floor** — the cue reads as ears turning rather
than as a head turn, which is the thing to fix.
`gazeHead` 0.10 gives 1.06px at 47, 0.14 gives 1.48px.

**The lab surface already exists**: `gallery-v2.html`, the card "The look —
gaze, and what follows it". It draws a real scan (the shipped envelope through
the shipped rig) at 31px, 47px and 3x together, with the per-channel travel in
the readout. These are `RIG` values, so they are the MAP's too — the tread
needed a per-context split for exactly this reason and the gaze may as well.

**Not in scope, and not the same thing:** the separate `ears` beat is a one-ear
TWITCH (asymmetric, `earFar` at -0.35) — a flick, not a look. It stays.

#### The SOURCES are a separate axis from the magnitudes (audited 2026-08-13)

Everything above is about how far the gaze moves. This is about how often it
moves at all, and it is the cheaper half. Measured by running the renderer's
own logic over a 668-tick capture of the live world — 4 cats, e004-a1-s2,
2,672 cat-ticks.

**Two independent sources, and they barely overlap.**

- **Served** — `gazeTargetFor` (`render.js`): the cat looks at whatever
  `last_action` names. Any pose, and it survives reduced motion, because it
  is served state rather than motion. **5.3%** of cat-ticks.
- **The idle scan** — one of five beats in `motionFor`'s slot machine
  (blink 30 / ears 26 / rest 24 / scan 14 / yawn 6). Only `idle` and `loaf`
  reach it: walking returns early on stride, the four action poses on
  progress, sleepers just breathe. Weighted by the real pose mix, **2.3%**
  of frames for the scan and **1.1%** for the ear twitch.

| pose | share of ticks | has a gaze today |
| --- | --- | --- |
| walking | 28.9% | 0% |
| sleep-curl | 19.1% | 0% |
| idle | 18.7% | 0% |
| **pouncing** | 11.8% | **44.8%** |
| grooming | 11.2% | 0% |
| drinking | 6.0% | 0% |
| eating | 4.4% | 0% |

Chasing is the only thing that reliably makes a cat look at something.

**Why: `last_action` names a target in three shapes and the client reads one.**

```
chase / targeted play   {target: 'kitty'|'element', id: 4}   read      5.3%
groom                   {target: 4}                          IGNORED  14.0%
sleep                   {with: 3}                            IGNORED  21.1%
eat / drink             {action: 'eat'}  — no target at all           20.7%
```

`gazeTargetFor` requires `ref.id` and treats `target` as a KIND string. On a
groom, `target` IS the id, so it bails at the first guard. Verified against
the capture: a groom target is always another cat (reciprocal pairs 4↔2 and
1↔3, never self — a self-groom serves `target: null`), and 350 of 385 are one
tile away, so it is a strong sideways look.

Ranked by what it would buy:
1. **Grooming, 14.0%** — a shape fix, not a feature. Roughly triples the
   served gaze. `target: null` already means "don't".
2. **Eating and drinking, 20.7%** — needs a client-side resolve of the
   adjacent element (chow within one tile on 159 of 234 eats, water on 315 of
   319 drinks). Reading the present, not predicting.
3. **Sleeping, 21.1%** — skip it. `with` names a real co-sleeper but the eyes
   are shut and `sleep-curl` returns before the beats.

**There is no staleness to design around, and it was checked because it
looked like there was.** `last_action` is the action applied on THAT tick, not
a sticky most-recent: it changes tick to tick, and a two-tick action simply
repeats. An earlier count of "22% stale, up to 4s of held stare" was measuring
`last_action.action` disagreeing with `activity.state`, which is a different
thing (see the note to Product below). The gaze is recomputed per frame from
live positions, so a quarry is tracked as it moves.

**Owner's decision, 2026-08-13 — the gaze gets NO MEMORY.** When the current
action names nothing, the cat's gaze goes to its default rather than holding
the last target. This is worth writing down because it rules out an approach:
remembering the last target is the obvious way to raise that 5.3%, and it is
not what we want.

**One refinement to the table above.** Its ear row measures something other
than the drawn ear tip. Measured off the drawing, a full gaze moves the ear
**apex 2.30px at 31px and 3.48px at 47px**, against the table's 1.25/1.90 —
while the head row reproduces exactly (0.35 / 0.53), which is what says the
difference is specific to the ear row's method rather than a change in the
code. It strengthens the entry's conclusion rather than softening it: the ears
are further clear of the floor than recorded, and are carrying the cue almost
alone at map size.

**Sequencing.** Fix the sources now (cheap, and it pays off at today's tile
through the ears); let camera mode re-judge the three magnitudes, since
head-follow at 0.35px and pupil at 0.48px only become legible zoomed in.
Re-dialling them against a tile we are about to change is wasted.

**Product answered, 2026-08-13.** All four shapes are contract and documented
— `specs/001-cloudkitty-mvp/contracts/http-api.md` for the kitty object and
`last_action` ("the action the engine actually applied last tick,
post-validation"), `specs/004-fix-happiness-lockin/contracts/http-api-delta.md`
for the play shapes, `specs/006-action-durations/contracts/http-api-delta.md`
for multi-tick behaviour. Changes are additive by doctrine and go through a
spec, so reading them is safe.

- The type asymmetry is deliberate and guaranteed at the source. `Chase` and
  `Play` can name a kitty OR an element, so they carry the discriminated
  `{target: kind, id}`. `Groom { target: Option<KittyId> }` can only ever name
  a kitty, so it is a bare id. **Reader rule: if `id` is present, `target` is
  the kind; if not, `target` is a kitty id or null.**
- `groom.target` and `sleep.with` are `Option<KittyId>` — never an element, so
  the id-overlap worry does not apply. Both serialise `null` (self-groom, solo
  sleep); expect nulls on `with` even though this capture had none.
- Eat resolves its bowl through `adjacent_stocked_chow`, so a stocked bowl IS
  within one tile at scene start. The 159/234 gap is despawn: a bowl's last
  serving despawns it that same tick, and an emptied bowl leaves the cat
  licking it clean for the rest of the scene. Water never depletes — hence
  315/319.
- Serialising the element id is possible but belongs in the ACTIVITY payload,
  not `last_action` (which doubles as the plugin proposal wire). Additive, and
  it needs a spec and the owner's word.

#### The client draws the wrong pose on the last tick of every scene

Not Product's bug — ours, and it was found by asking about theirs. **17.4% of
every cat-tick draws a cat standing idle when it actually ate, drank, groomed
or slept that tick.**

`activity.state` is the scene IN PROGRESS as of end-of-tick. The engine applies
every action, then clears scenes that met their end condition, in that order,
before the frame publishes. So the final serviced tick of every scene reports
`last_action` = the action (true, its effects landed) and `state` = idle (also
true, the scene is over). Both are correct; the client reads the wrong one.

| the cat did | the client draws | | share of that action's ticks |
| --- | --- | --- | --- |
| drinking | idle | 159 | 49.8% |
| eating | idle | 117 | 50.0% |
| grooming | idle | 85 | 22.1% |
| sleep-curl | idle | 104 | 16.9% |

**The panel already contradicts the drawing.** `doingFor` in `app.js` follows
`last_action` (`case 'eat': return 'eating 🍥'`), which is the documented
pattern — "the doing line follows last_action". `poseFor` in `render.js`
follows `activity.state`. On the last tick of a meal the card says *eating*
while the cat stands there doing nothing, and a nap ends with the sleeper
sitting up for 600ms before the next thing starts.

**The shape, settled with the owner 2026-08-13.** Read the ACTION first for
the five scene poses, and keep `activity` as the fallback:

```
action → sleep-curl | loaf | grooming | eating | drinking     (sleep/rest/groom/eat/drink)
action → pouncing                                             (play, and chase behind its gate)
else activity.state → the same five                           (covers idle/purr/meow, which name no pose)
else water → swim, moved → walking, else idle
```

Keeping the fallback is what makes this **strictly additive**: `Idle`, `Purr`
and `Meow` name no pose, and for those the scene still decides exactly as
today. Replayed over the capture, **465 cat-ticks change and nothing else
does** — all four are `idle → the thing the cat actually did`. A non-scene
action never once co-occurred with a live scene activity (0 of 2,672), so no
special case is written for it; if it ever happens the fallback yields today's
answer, which is the safe direction to fail in.

`rest → loaf` stays in the map on the owner's call even though no `rest`
action was served in the capture — the `Rest { with }` variant is in the
engine's enum, and the sunbeam work may start surfacing it.

Not mechanical, so it takes its own pass and its own tests rather than riding
along with the gaze edit. Scene spans, if ever needed exactly, are on
`GET /events/activity`; snapshots cannot show them by construction.

#### `gazeTargetFor` measures from two different moments

Found while auditing the above, same family of mistake. The looking cat's
position is the DRAWN one (passed in as `pos`); the target's is the SERVED
one, read straight off `world`. So a cat looks at where its quarry will be at
the end of the tick, which on screen is grass.

Measured: of 133 gaze-firing ticks with a kitty target, the target moved on
**68** — half. Mid-segment the angular error is a median of **8.1°** and a
maximum of **26.6°**, and it is worst up close: at two tiles or nearer, median
18.4°.

Three precedents in the same file say to use the drawn position — the wade
pose keys on "the tile under the DRAWN cat, not the served destination",
`submersionFor` is "sampled from WHERE IT IS", and the depth layer sorts
critters by `elementPosFor`. It is also on the wrong side of the Article V
line quoted directly above the function: a moving cat's served position IS its
destination for that tick, so looking at it is the prediction that rule
forbids. The asymmetry carries no comment in a heavily commented file.

Fix is ~3 lines — pass `view` and use `view.posFor` / `view.elementPosFor`,
both of which already exist and are what the renderer draws those objects at.
Still frames are unchanged by construction, since `posFor` returns the served
position there anyway. **Do it inside the gaze pass, not standalone:** it is
subtle at today's rate and scales with both things about to change — seven
times more gaze, and camera zoom, where 26° on a cat two tiles away stops
being subtle.

#### The sources were built and PARKED — the cue is what is missing (2026-08-14)

Everything in the section above was implemented (#221) and taken back out
(#222) after the owner watched it on a live world. Keep the diagnosis; the
reader is recoverable from #221.

Reading `groom`'s bare id and resolving eat/drink took the gaze from 5.2% of
cat-ticks to **36.5%**, and it did not read. **The gaze is a 2-D fact
delivered through a 1-D channel.** `earNear = ears.x + gaze.x * gazeEar`
uses the HORIZONTAL component only; `gaze.y` goes to the head (0.35px) and
the pupil (0.48px, and hidden entirely while a cat eats or drinks with its
eyes shut). Of the 976 ticks the fuller gaze fired on:

| | | what the ears did |
| --- | --- | --- |
| 531 | 54.4% | **nothing** — the target was due north or south |
| 265 | 27.2% | leaned toward it, the intended read |
| 180 | 18.4% | leaned away from the cat's facing |

Per action, the share that read as intended: chase **43%**, drink 35%,
eat 29%, **groom 14%**. Grooming was the largest coverage win and the worst
legibility — cats groom side by side, so their partner is usually straight
up or down.

**So more sources cannot help until `gaze.y` has somewhere to go.** That is
cat art, not plumbing: an ear ROTATION rather than a lean, or a head dip,
judged at camera zoom where the pupil and head follow stop being sub-pixel.
Owner's call: a full pass on ear and eye position AFTER camera mode, with
play and chase left as they are because they already read.

**Camera mode is now built (spec 036), so the "after" has arrived.** The
condition these were parked on was a tile big enough to judge them at, and
the camera holds a nominal 10 tiles across on a 20-tile world, which puts
the tile near 62px against the 31px they were measured at. The magnitudes
that read as sub-pixel then — head-follow 0.35px, pupil 0.48px — are
roughly double now, and the `MENISCUS` dials and the whiskers were parked
on the same condition. Judge them at the camera's scale, not the gallery's.

Kept from #221: the gaze aims at where a target is DRAWN. That was a real
defect in the chase gaze — up to 26.6° off — and it is the one that reads.

Not to be re-derived: eyes are SHUT during eat and drink and the owner does
not want that changed, so the pupil channel is unavailable there whatever
the tile size.

**The most promising way back in is a TRAVEL goal, not more activities**
(owner, 2026-08-14 — going to Experiments). Upcoming policies may surface
planning behaviour, and a cat walking toward food, water or a friend has a
gaze target that fixes exactly what broke this:

| target distance | share with NO horizontal component |
| --- | --- |
| adjacent | **58.1%** |
| 2–3 tiles | 16.8% |
| 4–7 tiles | 9.7% |
| 8+ tiles | 4.4% |

Every source parked above is ADJACENT by nature — you groom a cat you are
touching, you eat from a bowl you stand beside — and a neighbour is due north
or south more than half the time. A travel goal is far by definition, so the
same one-axis cue reads 90–96% of the time instead of 42%. Two more things
agree: a walking cat's FACING already aligns with its travel, so the lean is
the forward one that reads as intent; and walking is 28.9% of cat-ticks with
0% gaze today, the largest pose bucket and the emptiest.

**Measured 2026-08-14, and it reverses the cheap-first instinct.** The
obvious saving — drive the ears from `velocityFor`, which the client already
has, and skip the buffer entirely — does not work, and the same numbers size
the buffer that does:

| driven by | ears dead (no horizontal component) | ear direction flips tick-to-tick |
| --- | --- | --- |
| this tick's step (velocity) | 50.2% | 40.8% |
| position 5 ticks ahead | 29.1% | 27.1% |

Velocity is no better than the parked adjacent sources on the dead axis, and
it is far worse on noise: cats zigzag, **63% of unbroken runs in one
direction last a single tick** (median 1, mean 1.7). The rig reaches full
deflection inside one tick, so a velocity gaze would waggle the ears at up to
1.25Hz. That is a twitch, not intent. Aiming at a POSITION five ticks ahead
is better but still flips on 27% of ticks.

**So the target must be the ENTITY the cat arrives at, never a position** —
an entity is stable until the cat picks a new goal, which is what makes the
cue read as purpose. Experiments' design already says this ("which element/cat
they land on"); the measurements say it is not optional.

**Which sizes the buffer.** How often an arrival is inside the horizon, so
the entity can be named at all:

| buffer depth | foresight | walking ticks with a nameable entity |
| --- | --- | --- |
| 3 | 2.4s | 69.9% |
| **5** | **4.0s** | **85.3%** |
| 8 | 6.4s | 94.4% |
| 12 | 9.6s | 97.8% |

Experiments' proposed 5 is a good knee. Going 5 → 8 buys 9 points for 2.4s
more delay; 8 → 12 buys 3.4 for another 3.2s. Past 8 is waste, and the tail
belongs to the intent head (Tier 4), not to a deeper buffer.

**The rule that falls out: gaze only when the entity is nameable, otherwise
nothing.** Never aim at a bare position. That keeps the cue stable, and it
composes with the owner's no-memory decision rather than fighting it.

The client cannot infer this (Article V) — `move` serves only
`{action, direction}`. It would need the goal ON THE WIRE, and Product's
guidance on the analogous eat/drink case applies: the activity payload, not
`last_action`, which doubles as the plugin proposal wire. Two questions
decide whether it works: **how stable a goal is tick to tick** (one that
changes every tick smears through the rig's spring rather than reading as
purpose), and whether a served goal is the cat's actual destination or a
step target.


#### Order of work, agreed 2026-08-13

1. `poseFor` — the 17.4% correctness bug, on its own, with its own tests.
2. The gaze sources (groom shape, then eat/drink resolve) with the
   drawn-position correction folded in — same function, same tests.
3. Magnitudes stay parked for camera mode.

### Graphics v2 follow-on: face-group pitch (added 2026-07-29; Client thread)
The one v2 piece still unbuilt (vocabulary, motion wiring, and swim all
shipped — see git history / PR #92). Slide eyes+nose+mouth together
up/down the head to simulate head tilt (looking down to eat/drink, up
at a bug). Shape agreed: a per-pose scalar (e.g. `L.pitch`) blended
through `blendLayouts` (the motion wiring's `Presentation.tweenFor`
seam makes this free), consumed in `drawFace` as one shared y-offset on
eyes and nose (mouth anchors to the nose and follows). **Trap:** the
tuxedo/seal-point head masks are anchored to the `NOSE` tunables — they
are fur markings and must NOT move with pitch; pin them to the static
baked values. **Dead end, do not rebuild:** pupil-shift gaze was built
and reverted — max travel ~0.24px at world size, unreadable; pitch
replaces it. House method: judge in `gallery-v2.html` (dials +
readout), bake on the owner's paste.

### Water cues: occlude the cat's lower body — SHIPPED 2026-08-07 (PR #124)
Clipping the cat against the waterline, so a cat on a water tile is
visibly half-submerged whatever pose it is wearing. Solved the
water+action case in one stroke, as the entry predicted: a cat keeps its
*drinking* or *grooming* pose (which `poseFor` lets outrank the wade) and
still reads as standing in water — no second pose, no per-activity
special-casing.

Built exactly on the groundwork the entry named: it consumes
`Presentation.wetFor`, so the surface rises and falls with a shoreline
crossing (measured 0.88 → 0.72 and back, symmetric over `wetFadeMs`)
rather than popping, and the shadow, the ripple and the waterline can
never disagree.

**Waterline 0.72**, owner-picked from six depths rendered through the
shipping path at live tile size; it crosses the bottom of the body so the
cat is clearly *in* the pond, while the pose stays legible. 0.62 —
matching `SWIM`'s own surface, which would have given wading and swimming
cats one shared water level — was rejected because a standing cat then
looks like it is swimming. The swim pose opts out of clipping entirely:
it is already drawn sunk.

The deferral condition was met by v3 Phase 1's larger tile, as planned.

**The entry's second half is resolved too, and verified rather than
assumed.** It said a single water tile rendered as a rounded blue square,
because `shoreRounding` was a flat 0.45 tiles applied to a 1×1 blob. The
shoreline pipeline was rewritten in the 2026-08-07 meadow round — arcs
first (`sampleRoundedLoop`), wobble riding the finished curve, rounding
0.8 — and an isolated water tile now draws as a rounded organic blob.
Checked on interior 1×1 ponds in the preview world at high zoom, not
inferred from the dial change.

That leaves the river case, which is NOT covered: rounding is still a
flat constant rather than clamped by local channel width, so a 1-wide
channel would still bead into lozenges, and `groupWaterTiles` still
floods 4-adjacent only. Both are recorded in the v3 plan's Phase 5.

### Pond restyle — give the pond a bottom (added 2026-08-09; Client thread)
The design handoff's **spec 02**, plus the deltas we measured against it. The
bundle was gitignored and temporary, as its original `deletemewhendone/` name
said, and the owner **deleted it on 2026-08-20** — so everything below is no
longer "the part worth keeping", it is the only record. Do not go looking for
`design_handoff_art_uplevel/`; nothing in it was tracked, so it is not in the
history either.

**The proposal, in one line:** a blurred copy of the pond's own silhouette is a
distance-to-shore field, so one blur buys depth without a distance transform.
Composite a pale shore over a deep base inside the existing clip, add a damp
"lip" ring outside the water, replace the per-tile shimmer with a caustic net,
and swap the hardcoded 1.5px `pondRim` for a tile-proportional meniscus. It
leaves `buildPondPath`, `groupWaterTiles` and the shore dials alone, adds seven
tunables plus `pondDeep`/`pondLip` per theme, and bakes into the existing
`pondCache`. Its own house-rules section is accurate — dual-home rule, Article
V/VI, no assets, gallery-meadow as the lab.

**Three deltas we measured, which the spec could not have known:**

1. **The caustics cost claim is inverted for our world.** It argues "8 polylines
   per pond instead of 2 strokes per tile", justified with a fifteen-tile pond.
   We have **7 water tiles in 4 blobs — one 2x2 lake and three lone tiles**.
   Today that is 14 shimmer strokes total; the proposal is 32 polylines, ~416
   segments. A ~3x increase, not a saving. Cheap either way, but `causticLines`
   wants to scale with blob area rather than being a flat 8 per pond.
2. **Build the shared offscreens from the start.** The spec offers two canvases
   *per pond* and notes in its own risks that 3+ blobs should share one pair. We
   have 4. At WQHD that is ~19MB per offscreen: **~153MB per-pond against ~38MB
   shared**.
3. **Our world is dominated by the spec's own hardest case.** Its acceptance
   criterion 1 says a lone tile is harder, because at `pondDepthBlurTiles = 0.95`
   it is almost entirely "shore". **Three of our four ponds are lone tiles.** Judge
   those first, and expect the blur to want clamping by blob size.

4. **Caustic count comes from AREA; the spacing comes from HEIGHT — so a long
   thin pond is double-dense.** `lines` is
   `round(tileCount * causticLinesPerTile)`, capped, but the lines are seated at
   `(i + 0.5) / lines` across the *bounding-box height*. A 4-tile river and a
   4-tile lake therefore both ask for 6 lines, and the river has half the
   vertical room. Each line wanders `±1.9 * causticAmplitude` (0.9 drift + 1.0
   wave), so lines collide once `height / lines` closes on that. Minimum gap
   between adjacent lines, sampled over 40s at a 31px tile:

   | values | lone 1x1 | 2x2 lake | river 4x1 |
   |---|---|---|---|
   | spec (amp 0.08, cap 8) | 6.7px | 1.5px | **-3.7px, crossing** |
   | shipped (amp 0.025, cap 4) | 11.9px | 11.9px | 4.2px |
   | shipped amp, cap 6 | 11.9px | 6.7px | 1.6px |

   The owner found this by eye on exactly the two shapes it predicts, and fixed
   it by lowering the cap. So **`causticLinesMax` is currently standing in for a
   density rule**: 4 is chosen by the river, the shape with the least height per
   tile, and it is what holds the lake's count down too. If ponds ever get
   bigger or longer, scale the count by bounding-box height instead of tile
   count and let the cap go back to being a safety net.

**Owner decisions already taken, ahead of the work:**
- **The cat's wet ripple is already off** (`VIEW.ambient.wetRipple`, 2026-08-09).
  The spec proposes keeping and recolouring those rings; we overrode it — two sets
  of rings, the cat's and the water's, read as a mistake rather than as depth.
- **Zero the shore wobble as part of this**, not before it. `shoreWobble: 0` in
  BOTH homes (dual-home rule). Measured at our pond sizes the irregular edge is
  nearly invisible — a lone tile is identical with it on or off — so it costs
  almost nothing, and the new lip and meniscus take over the job of softening the
  edge. `wobbleAlong` short-circuits cleanly at 0. **Not independent of
  `shoreOverdraw`**: the wobble biases the outline inward by
  `0.25 * amp * (1 - bulgeEase)`, which at the shipped values is 0.005 tile off a
  0.1 tile spill, so zeroing it returns that and the pond grows by a hair.

**Also in the bundle:** spec 03 (meadow drifts — clustered cover instead of
independent per-tile rolls, and the `grassTones` lattice), and a parked spec 01
(cat lighting) the owner deferred. Recommended order 02 then 03; 03 is the one
that needs the lab's occlusion strip. **02 and 03 both shipped** (#177, and
#189/#191).

**Spec 01 is CLOSED, not parked (owner, 2026-08-20):** *"I didn't actually like
the way that lighting pass looked, we'd be better off just starting from
scratch."* The document went with the bundle. What it was reaching for is still
a real gap and is worth restating in one line, because the observation outlives
the proposal: `MEADOW.shadowLean` and `shadowLength` swing the ground shadows
through the day, and the cats standing in that light never answer it — flat
`furBase` inside a `furShade` outline, every pose, every hour. Any future
attempt starts from the meadow's own sun, not from that draft.

### Ambient whole-body float — CLOSED, not doing (2026-08-09; Client thread)
Graphics v3 Phase 4 listed a slow whole-body y-bob for every cat, borrowed
from kitten.me, on top of the breathing we already have. **Closed by the
owner** rather than deferred, and the reasoning generalises so it is worth
keeping: the walk's body bob was built, measured and reverted the same day
(branch history, `56b071c`) because at our tile size a few tenths of a pixel
of vertical motion on a rigid body reads as **edge shimmer, not life** — the
body travelled 0.56px peak-to-peak at a 56px tile against a foot's 9.52px
fore–aft.

The same arithmetic applies to an ambient float, and worse: an idle cat has no
lateral motion to hide behind. If it ever comes back it should come back as
the *whole-cat* mechanism from that revert (head, tail and limb pivots riding
the body, grounded feet held), not as a torso sliding against a welded head —
and only at an amplitude that clears a pixel.

### Animation handoff — the residue, re-reviewed 2026-08-14 (Client thread)

Re-read `design-handoffs/design_handoff_animation_upgrade/README.md` against
the shipped code. That bundle survives (gitignored, 2026-08-20) and its
`support.js` now sits at its root rather than in the art bundle that was
deleted — the review labs load `./support.js`, so they need it beside them, and
their other paths assume the HTML sits at the handoff root rather than in
`review/`. `MANIFEST.json` lists the labs and `cat-v2-baseline.js` as
`notForRepo`. The handoff itself is landed; what follows is what it
listed as not-done and nobody wrote down, plus two things the review turned
up that it did not.

**Done, so not carried:** both tests it asked for exist (rig at rest, still
frame gaze); the test-pass list is worked through; card portraits got the
idle vocabulary AND the rig, with the world's wake-stretch deliberately
excluded and the measurement for that written at the call site; invariants
1, 2, 4, 5 and 6 have coverage.

**Its three optional follow-ups, none done, none previously recorded:**

1. **Ears forward on the hunt.** The handoff's own words: "the one cue still
   readable at 31px when the eyes are not. The rig already has the channel."
   That is exactly what this session measured from the other end — at a 31px
   cat the ear tip travels 2.30px against 0.83px of pupil and 0.35px of head,
   so the ears are the only visible channel. **Do this with the ear/eye pass
   after camera mode, not before**; it wants judging beside the vertical ear
   response below.
2. **Gradual pupil dilation.** Instant with the pose today. Needs a spring
   channel, so it is larger than it sounds — and it is a camera-mode feature,
   since the pupil is 0.83px at the live tile.
3. **Irregular groom and drink rhythms.** Both still nod on a single sine
   (`0.008 * Math.sin(phase * 3 * TAU)` for drinking). Real lapping comes in
   bursts with pauses. Cheap to author, and unlike the other two it reads at
   map scale, because it moves the whole head.

**Two the review found:**

4. **`EYE.focusedScale` and `EYE.focusedHeight` are dead dials, and they are
   still on the Face card with their own `FOCUSED = {...}` readout block.**
   Measured: moving them 0.5 → 2.0 changes not one drawing operation. The
   handoff flagged them as dead and kept them *because* the lab named them,
   which is backwards — a live slider over dead code is the same trap as
   `SWIM.tailUpright` (dialled a whole session, never printed) and `tipFur`
   (inert over 70% of its travel). Either wire them to the `EYE.focus*` set
   that replaced them or take them off the card; do not leave them dialable.
5. **Invariant 3 — "neither focused lid may cross the pupil" — has no
   explicit guard**, and it governs `FOCUS_VARIANTS.intense.focusLidTilt`,
   which the handoff calls "the one knob the owner expects to revisit"
   (0.20 ships, 0.34 read as evil). The tests around it prove the variants
   are no longer frozen; none proves the lid stays clear of the pupil. Worth
   adding before that dial is next touched, not after.

### Whiskers — CLOSED, they shipped (2026-08-13; Client thread)
Shipped on in #215 at the whole-world tile, without camera mode and without
clearing the sub-pixel floor. This entry said the stroke lands near **0.8px**
and that a bigger tile had not been enough, and both of those are still true —
the stroke is pinned at exactly the 0.8px floor at the live tile.

**The premise was wrong, not the measurement.** kitten.me's whiskers sit at
the same 0.8px below a 44px cat, so stroke width was never what made theirs
read. What does is **opacity** — at 0.25 a hairline is a soft hint rather than
an aliased dotted line — and **length**, running past the head so most of the
whisker falls against background rather than fur. Sub-pixel geometry can carry
a feature if it is not asked to look solid.

Worth remembering when the next feature is costed at a pixel width: that is
one of at least three things setting whether it reads.

### ~~The walk contradicts itself travelling north/south~~ — SHIPPED 2026-08-20 (PR #275)

Design's rebuild landed, over five owner rounds, and it took **none of the
four options costed below**. The diagnosis under them was wrong.

The fault was never the gait. The axial chest's underside sat BELOW the
ground line — re-checked against the commit before #275, `AXIAL.bodyY` 0.7
plus `bodyRy` 0.185 is 0.885 against a `CAT_GROUND` of 0.88 — so the body was
buried and there were about **two pixels of visible leg** at a 120px tile (the
pixel figure is #275's measurement, carried). Every note here about sweeps,
planting and cadence was describing legs nobody could see. Once the body cleared the ground, the step
could travel in DEPTH on the same `gaitStep` curve the side walk already
uses — which none of the four options proposed, because none of them
suspected the ground line.

The entry is kept rather than deleted because the CENSUS is the durable part:
717 east/west frames against 394 north/south, about 10% of all frames. That
measurement still holds and would still be the thing to re-derive. The
options are history; the number is not.

Kept too because "do nothing is a legitimate answer" was the right standing
answer for two years, and stopped being right at the moment the tile got big
enough to see the problem. Worth remembering the next time an entry here
carries a costed do-nothing.

### The original entry (added 2026-08-08; Client thread)
Our cat is a **side profile**, so it encodes a heading. The legs sweep
fore–aft — horizontally on screen — whatever way the cat is actually
going, and that sweep is the entire basis of the planted foot: a stance
paw drifts backward at exactly the rate the ground passes under it, so
it holds still against a mark.

Travelling east or west that cancels: 9.5px of paw sweep against 56px of
travel per tick, same axis. Travelling **north or south the axes are
perpendicular** — the paw still sweeps 9.5px sideways while the cat
carries it 56px vertically, so every foot, planted or not, slides across
the ground at full walking speed. Nothing cancels. `dx === 0` also keeps
the previous facing (`anim.js`), so the cat is a profile sliding sideways
up the screen.

**Measured, not guessed** (9-minute live census, `client-measurements/`):
717 east/west moves against 394 north/south, so **35.5%** of walking is in
the mode where the planting does nothing. Walking is ~28% of frames, so
this is about **10% of all frames** — which is the budget any fix has to
fit inside, and it rules out a new art vocabulary on its own.

This is a consequence of the gait work succeeding, not a regression: with
the old pegs the feet slid in every direction, so nothing was claimed and
nothing was contradicted. **Doing nothing is a legitimate answer** and is
what ships today (owner's call, 2026-08-08 — deferred in favour of higher
value work).

Options, costed, so this does not get re-derived:
- **Front/rear-facing vocabulary** — the only true fix, and out of all
  proportion: two more views of body, head, ears, face, tail, legs and
  every pattern mask, for every pose, plus something sane when a cat turns
  from east to north (a snap pops, a blend needs in-between views).
- **Rotate the profile toward travel** — cheap, but a rotated side view
  reads as a cat climbing a hill, not walking away.
- **Isometric projection**, so north has a horizontal component — that is
  the whole world (tiles, ponds, shadows, elements), and camera work is
  already deferred until after the art.
- **Damp the sweep by the horizontal share of travel**, `|dx|/(|dx|+|dy|)`
  — about five lines, the renderer already has the delta. Risk: still legs
  read as an escalator, and the factor pops at direction changes unless
  smoothed across a tick.
- **Swap the motion instead of killing it**: for vertical travel replace
  the fore–aft sweep with a small alternating *piston*, paws stepping
  under the body rather than past it — the old sprite-game convention for
  "walking toward/away from you". ~30 lines, entirely inside the walking
  case, no new vocabulary. **Best value of the list if this is picked up.**

Suggested shape if revisited: one dial, 0 = today's full sweep, 1 = full
piston, damping as the midpoint, judged in the lab on a card that walks a
cat north and south — with "do nothing" as a fourth thing in the
comparison, not as the absence of one.

### Stationary poses have no axial drawing (added 2026-08-12; Client thread)

`AXIAL_POSES` is `{walking, idle, swim}`. Every other pose falls back to a
side view, so a cat facing north that stops to drink is drawn in profile
for that tick and then faces away again once it steps. A side-on cat shows
its face, so the excursion reads as the cat turning to look at you and
turning back. The owner reported it twice, most recently at the waterline
(2026-08-12).

It concentrates at ponds because that is where cats drink and groom, not
because water is involved in the mechanism.

**Measured** (668-tick live feed, four cats, driven through the real
renderer):

- 148 stops after a north/south walk. 130 of them are the cat arriving to
  do something: eating 47, drinking 42, grooming 22, pouncing 19, loaf 9.
- Of the genuinely idle stops, 5 of 9 keep the axial view. The #198 lock
  holds the other 4 side-on, which is that fix working.
- 170 view changes with the served facing UNCHANGED over the same feed,
  71 of them reversing inside a tick.
- `eating` + `drinking` + `grooming` alone would cover 111 of the 148.

**Ruled out, so it is not re-investigated.** It is not the facing memory,
not the axial lock, not `turnFacing`, and not the swim gate: the drawn view
never changes between promotions, measured at 0 across 128,260 attributed
draws with the pacer and arrival jitter in the loop. Poses do change
mid-tick (162, mostly `swim` to `walking` at the waterline) and the view
holds through every one. What looks sub-tick is a one-tick excursion.

PR #198 already took the cheap half: once a pose without an axial
drawing turns a cat side-on it stays there until the cat steps, which cut
within-a-tick reversals from 295 to 81. What remains has a real pose change
behind it, so no lock can remove it.

Options, costed:

- **Author axial drawings for the stationary poses** — the true fix, and
  the only one that does not lie about what the cat is doing. `drinking`,
  `eating` and `grooming` cover 111 of 148. Design's, roughly the size of
  the swim pose (#199), and it wants the same treatment: both directions
  drawn, judged side by side in the lab at the live tile before either
  ships.
- **Reuse the axial `idle` with a head dip** for the head-down poses,
  rather than drawing three new ones. Much cheaper. Risk: at 31px a dipped
  head may read as a cat staring at the ground in all three cases, which
  loses the distinction the poses exist for.
- **Hold the axial view through a short non-axial episode.** Cheap, and
  wrong in a way worth naming: it draws a swimming or drinking cat in a
  pose it is not in, and it delays a legitimate turn by a tick. It also
  contradicts the #198 rule that the drawing turns when the cat turns.
- **Do nothing.** Ships today, and the owner has accepted it once already
  (2026-08-12: "I'm ok with that for now, what we have looks way more
  natural already").

## P2 — the bigger pieces, for a proper sitting

### Fog hot-loop allocations in the training tick (added 2026-09-04; Product thread, from `/code-review high 049` findings 8–10)

Three per-tick allocation sites spec 049 added, all LOW and none
measured; the plan's stated goal was "no per-tick allocation growth
beyond the views", and these exceed it:

- `world.rs` message enforcement and `action.rs` `emit_message` each
  build `self.snapshot()` (every kitty, element and the meow buffer) and
  then `fog_for` keeps one disc — two whole-world clones per speaking cat
  per tick, on top of `decision_jobs`' one view per cat. Fix shape: a
  live-world `fog_for` that filters without the intermediate clone, and
  (review 3, 2026-09-04) ONE view per apply slot threaded into
  `apply_message` rather than `emit_message` rebuilding it.
- `observe.rs` `row_state` calls `heard_unseen` (allocates; scans roster ×
  buffer) once per kitty row; with the message block (15 passes per row)
  and answers-me (8 more), on the order of 100 buffer scans per 408-float
  observation. Fix shape: one pre-pass grouping meows by (kitty, kind).
- `needs_driven.rs` `groom_response` clones `recent_meows` into a `Vec`
  per cat per tick to reuse `freshest_audible`'s slice signature; the
  filter + max can run in place over the borrowed slice.

Bill: measure first (ticks/s on the served roster all-scripted, and the
bc-collect / PPO rollout rate). The buffers are small (5 cats, ~25
elements, ≤ ~50 meows), so the win may be modest — do it if step-5
throughput reads short, not before.

### Distress-gated intervention — the behavioral safeguard (added 2026-08-20; owner-approved for investigation)

Owner, 2026-08-20: "worth investigating, let's add it to the backlog to
dig into after we finish this generation (definitely before fog lands).
Disabled in testing, enabled on the server."

The shape: when a need's distress age crosses a line, the engine
overrides that kitty to `needs_driven` until the need is relieved, then
hands control back. It is the behavioral complement to Article I's
supply-side safeguard — the engine currently guarantees relief *exists*
past need 75 (`spawn::safeguard`), but nothing guarantees it gets
*taken*; the F-027 co-sleep deadlock sat at need 100 for 2331 ticks with
water standing. Certification measures the raw policy (disabled in
testing); the served world gets the net (enabled on the server).

**Framing correction (owner, 2026-08-23)**: the pathology was not that
relief went untaken, it was **deadlock** — two cats locked in a mutual
activity that neither would break. Read the shape above as an example of
a fallback, not as the settled design.

Design conversation 2026-08-23 (owner posed: rely on scripted as-is /
upgrade the scripted logic / build a dedicated fallback model):

- **Do NOT upgrade `needs_driven`'s ACTION ladder.** It is the project's
  measurement anchor — the scripted team anchor (0.9077), thermostat
  parity (90.71), the character price, and spec 017's eval-suite
  baseline all rest on it being fixed. A better thermostat has to arrive
  as a NEW named behavior, never as an edit. (Its MESSAGE channel is a
  different matter and is separable — see the here-word density screen.)
- **One cat is enough to break a dyad.** Past an activity's minimum a
  different action lawfully interrupts and ends a duet **for both
  sides**, so the intervention only needs to touch one member.
- **A fourth option worth costing: mask, don't override.** Make
  continuation of a partnered activity illegal while one of that cat's
  needs is in distress. The cat keeps its own policy and character; it
  simply cannot choose to keep cuddling while starving. Engine legality
  rather than behavior swap.
- **The trade-off is guarantee versus character.** `needs_driven`
  override = guaranteed relief, character visibly interrupted. Masking =
  character preserved, relief NOT guaranteed, and it puts the policy
  off-distribution where F-010's catatonia lives.
- **Recommended shape: a two-stage ladder**, matching the two-layer
  welfare-gate philosophy. Stage 1 masks the pathological continuation
  and lets the mind re-decide; stage 2, if the need keeps climbing,
  overrides to `needs_driven` as the terminal guarantee. Most incidents
  resolve at stage 1 with character intact, and the stages give
  different defect signals — stage 1 means "needed a nudge", stage 2
  means "broken here", which a single mechanism cannot distinguish.
- **Vocabulary stays out of the safety path.** A safety net and a
  teaching mechanism have opposite frequency requirements: a good
  fallback almost never fires, which makes it a poor vocabulary vehicle,
  and tuning it to fire often enough to teach would make routine policy
  failure a design assumption. The fallback inherits whatever
  `needs_driven` says anyway, so scripted vocabulary work belongs in the
  density screen, not here.

Design questions still open for the sitting: the trigger line(s) and
hand-back condition; how the override interacts with streak-based
detection (an enabled override truncates the observable — F-027's
re-verify note); whether the served world logs every firing (it should —
each one is a policy defect report). Engine change: spec-first flow when
picked up.

**Sequenced (owner, 2026-09-03, spec-049 clarify item 3)**: own spec on
the 3.0 line, landing before the step-7 `--fresh` cutover (override
state is a snapshot field), not inside 049. Every firing is stamped on
the event stream and the live instruments read the stamp. Design
constraint for the spec: a per-seat fallback chain, each rung =
(behavior, descend trigger, hand-back condition), snapshot = current
rung + entry tick; Gen 1 builds two rungs (masked policy →
`needs_driven`), and a later LLM → attention model → scripted tier is a
prepended rung. Ruling text:
`experiments/fog-gen1-timeline-2026-08-26.md` step 4.
Origin: `experiments/exp-006-character-gen/results/r5-forensics-2026-08-20.md`.

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
exists, alongside whatever else v2 wants (owner note, 2026-07-25) —
**that condition is now met** (s3/s6 certified clean 2026-07-30), but
the suite is in active exp-003 service; hold until that experiment
closes. Natural pairing: the small-world exams entry below (P2).
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

**Top three: all SHIPPED** as specs 018/019/020 (2026-07-26, tagged
v2.4, PRs #56–#58) — kitty-eval/suite dedup via `cli_support`, the
compiler-enforced need→relief pairing in `behavior/relief.rs`, and the
`config/{mod,defaults,validate}.rs` split. Each verified bit/byte-
identical; the specs and git history hold the detail.

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

### ~~Welfare pinned-streak Cuddle false-positive~~ RETIRED 2026-08-01 — premise falsified
Not a bug: busy adjacent neighbors ARE lawful cuddle relief, so the
metric is correct as written and narrowing it would be a tighten-only
regression. Authoritative rule table:
[docs/cuddle-relief-semantics.md](docs/cuddle-relief-semantics.md).
Tombstone kept because the stale premise recruited a reader once.

### Dynamic element populations (added 2026-07-20 — ideate with the owner first)
Environmental elements are effectively static: `ensure_minimums`
(`spawn.rs`) tops every type back to its configured min on the very next
environment phase, only Article I safeguard spawns ever exceed it, and
the configured max is nearly dead config — so worlds sit pinned at min
counts forever. **That was never the intended behavior.** Spec 027
(2026-08-05) took the first bites: the guaranteed 2×2 lake (water's
spatial character, maintained by the restock path), the interior spawn
preference, and `ttl_jitter`/`spread_candidates`/`edge_penalty` in
config. **Still open — the actual dynamics**: populations wandering
between min and max, expiry gaps that linger a little instead of
refilling the same tick, time-varying spawn pressure (bug flushes, chow
deliveries), water spawning adjacent to water beyond the lake. Hard
constraints unchanged: never frustrating for the kitties — the Article
I safeguard's instant relief spawn is untouchable, and min still means
min; fully deterministic through the seeded RNG; tunables named in
config (Article VI). **Design not settled — start with an ideation
conversation, as the 008 direction was.**

### Rendering a meow REPLY (added 2026-09-03; Client thread — after Fog Gen 1, owner)

Owner's ruling, relayed from the Experiments thread: the fog timeline's
step-4 coverage pass, item (iv)
(`experiments/fog-gen1-timeline-2026-08-26.md`, main `26504ac`). Spec 049
gives the `Meow` record two additive engine-stamped fields: `reply`, a
bool saying this `here_*` word answers an audible `want_*` from another
cat, and `pos`, where the speaker stood when it spoke. Both reach
`/world` and the meow event stream. Nothing is specced on the client side
and nothing is needed for 049. The open question is whether a reply earns
its own treatment: a distinct bubble, or a drawn link from replier back
to caller.

Two independent paths draw a meow today, and a reply treatment lands in
both.

The BUBBLE (`render.js:2065`, `drawBubbles`) reads `world.recent_meows`
straight off the served world, keeps what was spoken in the last
`BUBBLE_TICKS` (3, `render.js:100`), takes one per cat with the newest
winning, looks its copy up in `MEOW_TEXT`, and draws at the cat's
interpolated position, so the bubble rides along with a walking cat.

The GAPE (`anim.js:1776`, `meowFor`) is the mouth. It gates on the pose
(`VIEW.meowPoses`), plays once from the frame the meow arrived, and
allows one drawn call per cat per `VIEW.meowCooldownMs` (8s since PR
#335). It already returns the `kind` alongside the gape, so a `reply` bit
rides that channel with no new plumbing.

Three things to settle before speccing:

1. **The two paths disagree about rate.** The cooldown holds the mouth
   and not the bubble, so a reply drawn as a bubble sits outside the
   ceiling that exists to keep the Fog generation's chatter from reading
   as a tic. A call-and-answer pair is also the case where drawing half
   is worse than drawing neither, and both paths keep exactly one slot
   per cat with the newest winning (`anim.js:1423`, and the `said` map in
   `drawBubbles`), so a reply can evict the call it answers.
2. **A link between two cats is a claim the viewer reads.** FR-002b's
   naming law is why the free register renders its sound-words as-is
   (`render.js:49-59`). `reply` is an engine-stamped fact rather than an
   invented meaning, so drawing it should be legal, but the shape of a
   link asserts something about the pair and wants checking against the
   law rather than assuming.
3. **`pos` is worth taking even if no link is drawn.** A meow first
   appears the tick after it was spoken and lingers about ten
   (`anim.js:1406-1411`), so the speaker has moved by the time it is on
   screen. Today the bubble follows the cat; `pos` is what would make
   leaving it where the word was said possible at all.

### Cover colour variance — wants a full treatment (added 2026-08-13; Client thread)

Every clump takes the same two palette entries, `MEADOW.bush` and
`MEADOW.bushHi`, so a meadow of sixteen clumps is sixteen copies of one
colour. Raised while dialling the trees, and **deliberately not done as a
slight per-clump tint**: the owner's read was that a small lightness jitter
is a lot of plumbing for very little, and that this is worth doing properly
or not at all (2026-08-13).

**What "properly" might mean**, none of it decided:

- Colour that means something rather than noise — the drift/fertility field
  already says where the ground is good, so cover could be greener where it
  thrives and drier at the edges of a drift. That reads as a meadow with
  soil in it rather than as randomised shrubs.
- Per-species palettes, so the trees are their own colour rather than the
  bushes' colour on a trunk.
- A second entry per species (body and highlight) so the variance survives
  the shading, instead of one hue nudged two ways.

**Effort, measured rather than guessed.** The mechanical part is that
`MEADOW.bush` and `MEADOW.bushHi` appear at about **20 sites** across every
style branch of `drawBushAt`. A per-clump colour means resolving both once
at the top and threading them through all of them. The risk is missing one:
a clump with a tinted canopy and an untinted highlight reads as a seam, and
nothing in the suite would catch it today. A source check that no raw
`MEADOW.bush`/`MEADOW.bushHi` survives inside `drawBushAt` makes the
substitution safe, and is the same shape as the existing check that
meadow.js never calls `shadeHex`.

**The trap, if this is picked up:** palette entries are `rgb()` strings
mid-crossfade, not hex, so any tint must go through `mixPaletteColor`.
`shadePalette` already does. Getting this wrong is what turned the shrubs
black in #191, and the crossfade check would catch a regression.

About an hour for the slight-tint version that was declined; a full
treatment is bigger and wants the lab's ground-cover card to show a spread
of clumps side by side, which it does not today.

### Meadow finishing touches: grass detail + world edge (deferred from 008; Client thread)
The meadow itself shipped in 008 (PR #13: organic ground, ponds,
sunbeam glow, worn paths, grid demoted to `l` toggle). Three pieces
were built or attempted, judged, and scrapped for a proper art pass:

1. **Grass detail** — two attempts at scattered flora accents both read
   as sparse/odd noise. Next attempt should try denser micro-texture
   (blade clusters, mottling) rather than discrete per-tile accents,
   judged at multiple tile sizes (16×16 renders at 45px, 64×64 at 11px).
2. **A world edge** — the grass-fringe frame never landed. Consider a
   low hedge or picket frame in the cats' outline style instead.
3. **Grass sway** — removed 2026-07-22: fixed-pixel geometry read as
   stray diagonal lines at mobile tile sizes. Any return must be
   tile-proportional.

Scaffolding stands ready: `tileHash` in `client/meadow.js`
(deterministic per-tile scatter, no served data), tunables homes,
harness in `client/test-meadow.mjs`. All new grass work is judged under
all three palettes (day / golden hour / night) and at multiple tile
sizes; any new color belongs in every `MEADOW_*` set.

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

### Kitty "brain" indicator in the viewer (added 2026-08-01; Client thread — no server work needed)
Show which brain drives each kitty — scripted profile (`needs_driven`,
`playful`) vs. a seated policy (`policy:s6`) — as a client toggle, now
that the served world mixes them. Its 2026-08-01 blocker (the swim
animation) shipped in PR #92. **Corrected 2026-08-06: the "small server
API addition" this entry once called for already exists** — `GET
/config` serializes the whole `Config`, `kitties[].behavior` included
verbatim, and the client already fetches `/config` (app.js:573). So
this is pure client work: map kitty id → behavior string from the
response already in hand, draw a thin overlay. Follow the debug-toggle
conventions (`g`/`l`/`p` keys, keyboard-only by design, off by
default); display the config string verbatim so the label can never
drift from the seating truth.

### evals/v2 — small-world exams for the certification path (added 2026-08-06, from the consumed pre-exp-003 handoff)
Post-exp-003, Product-owned. The owner tests 20×20 and 22×22 geometry
after exp-003 and picks a new default then; every frozen `evals/v1`
exam is ≥28×28, so a small-world default would leave certification
blind exactly where the served world lives. Design question the sitting
must settle before any exam is written: `evals/v1` is frozen by sha
pins plus a CI guard, and the held-out doctrine (017 FR-007) voids
results if an exam appeared in training — so v2 needs its own
freeze-and-guard story and a clean answer to "what was this exam's
provenance" before the first candidate is scored against it. Context
that shaped this: F-014 (22×22 is sub-floor on welfare *signal*, not
just size) and the world-tuning screens (landed, re-runnable).

## P3 — simulation depth

### expected_wait prices settled scenes at zero — latent spec-042 admission bug (filed 2026-09-02)
`expected_wait` (selection.rs) returns 0 for a boundless activity and 0
past a scene's minimum — its own doc concedes it is exact only for scenes
that hold their minimum. Combined with the mid-scene admission switch
being welded to `w_value > 0` (selection.rs:499), any live `w_value`
admits a settled RESTING friend as a zero-wait partner that out-scores
every critter yet can never be conscripted; the cat walks over and the
solo backstop fires beside it. Proven in the Biscuit 3.0 Addendum 3 Half
A sweep (element play handed to solo play, loiter share 0.137 → 0.20;
Experiments RESULTS @ 35b1248). **Latent at identity dials** — no shipped
config sets `w_value`, and the owner ruled the Gen 1 anchor carries no
re-admission mechanic (2026-09-02, "anything further risks
over-engineering"). Reopen trigger (owner-ruled 2026-09-02): fix this
if we ever enable the `w_value` dial — no plans to do that soon. Fix
shapes on record: either decouple admission from `w_value` (own switch)
or treat boundless / past-minimum scenes as inadmissible rather than
free.

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

### ~~Chases route around friends~~ SHIPPED in spec 024 (2026-08-01)
Design detail and the axis-aligned-lane correction live in
`specs/024-wet-fur-batch/contracts/chase-sidestep.md`. Still live:
pre-024 chase-statistic baselines must be re-measured before comparing
across the break (Experiments' calibration probe is the natural place).

### Trait-scaled routing with the charge off (added 2026-08-01)
`selection::bath_ratio` scales the `water_step_cost` surcharge even when
`[water] bath_gain = 0` (identity for shipped rosters, every ratio 1.0;
documented at the definition). Two open ends, opportunistic only:
whether an ablation lever should restore flat pre-024 routing for
trait-override rosters too, and whether an extreme bath-rise override
deserves a clamp so route pricing cannot become effectively prohibitive
(the "preference, never prohibition" doctrine holds today only because
shipped ratios stay near 1).

### Cats jump over cats — the boxed-cat escape (added 2026-08-31)
Owner's note, from a question during spec 044 planning. Today a cat with
kitties on all four cardinal neighbors (or 2–3 at a corner/edge) has zero
legal moves that turn: `Move` is cardinal, one step, and occupancy-blocked
(`action.rs:367-370`). Transient and harmless — blockers are autonomous,
an illegal move degrades to Idle, relief doesn't require moving — but
during the boxed ticks Article I's "reachable" clause is technically
false. The engine already travels 2 tiles in one tick (spec 039's final
pounce: chase step + lunge, `action.rs:587-609`), so the owner's idea:
allow a jump *over* an adjacent cat to the empty tile beyond, and the
boxed state stops existing entirely. When it comes, the real bill is
surface, not physics: a new legality arm (middle tile occupied, landing
tile empty and in-bounds) touching `Action::Move` or a new action variant
— which means the RL mask, the wire-compatible action surface, and
whatever a policy retrain prices. Dig in properly before speccing.

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

### ~~Rethink how water works for learned cats~~ SHIPPED as spec 024 wet fur (2026-08-01)
The charge law, the original 1.5/50 dial derivation, and the 3.5/60
re-decision (spec 026, 2026-08-05 — which supersedes the "final value
is a prereg'd exp-002 decision" note this entry used to carry) now
live in [docs/wet-fur-pricing.md](docs/wet-fur-pricing.md), alongside
the hard doctrine **water is a cost, never a wall** (owner, 2026-07-31;
pinned by spec 010's wade tests and Article I). The guaranteed-lake
companion shipped as spec 027; the organic water-adjacency variant
remains with *Dynamic element populations* (P2). Trait-scaled routing
residuals keep their own entry above.

### ~~Swim pose for wading kitties~~ SHIPPED (PR #92, merged 2026-08-04)
`poseFor` water arm + v2 `swim` layout (v1 keeps normal standing per
the owner's call); values live in `CatV2.SWIM` on main. Whether a final
owner value-judging pass in `gallery-v2.html` closes this fully is the
Client thread's call — otherwise done.

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
