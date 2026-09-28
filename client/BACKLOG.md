# Client backlog

Future work for the viewer (`client/`), moved out of the root `BACKLOG.md`
on 2026-09-28 at the owner's direction: "Let's add a client/BACKLOG.md,
extract any entries from the main BACKLOG and put them there". Entries moved
verbatim, in their original priority sections and order; shipped and dropped
entries came too, because they carry rulings that stop a question being
re-derived. The root `BACKLOG.md` stays Product's.

Priorities as in the root file: **P1** quick wins, next up · **P2** the bigger
pieces, for a proper sitting · **P3** depth.

## P1 — quick wins, next up

### No harness drives the v2 cat through the RENDERER — MOSTLY CLOSED 2026-08-22

Closed 2026-08-22: `test-meadow` gained a second scope (everything `src`
loads except cat.js) plus four mutation-verified checks driving real
frames through render.js's v2 branch. Two notes for whoever picks up the
rest:

- **The original scope is still the hybrid, deliberately.** The meadow
  checks want v1 present for vocabulary comparisons; the v2 scope sits
  beside it. Putting cat.js back in front of the v2 scope is a load-time
  SyntaxError, so the two cannot quietly merge.
- **Remaining slice: the EYES.** `render.js` replaces the snap blink with
  the eased `motion.blinkLid` for v2 cats and nothing asserts it. The
  fixture is cheap now: `v2Frame()` exists, and a frame taken mid-blink
  (see test-motion's slow-blink schedule) shows `lid` present and `eyes`
  cleared.

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
   The reason is better than "it did not read": *"the v1 hunter eyes read
   cute at low res, but as we get higher and higher res the 'fierce'
   hunting behaviour is not the chill cute vibe we're going for — I'm
   fine with the chasing kitties behaviour being the default for
   everything."* Off-brief, and low resolution had been hiding it. Gone:
   `expressionFor` and everything that existed only for it. Kept:
   `pursuitDistanceFor` (tested; the queued gaze work wants it) and the
   `FOCUS_VARIANTS` drawing — retiring the world's route to a face is not
   deleting the vocabulary. Full accounting: this entry's git history
   (condensed 2026-09-11).

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

Owner, 2026-08-20: *"if we want to look at it in the future, our recent
map border/landscape changes make it moot."* The question it existed to
answer — what should the map's edge be when the camera crops an
arbitrary window — was answered by the hairline being thin enough not to
assert anything, and the landscape work then moved the edge mostly off
screen. Kept as one line in case Fog or a resizable window brings the
question back; the full idea (fade the outer ~14px, why it is a
camera-mode question) is in this entry's git history (removed
2026-09-11).

### Phone portrait: the horizontal gap beside the map — SHIPPED (PR #248, 2026-08-19; Client thread)

Shipped; what stays is the durable arithmetic the `minTiles` decision
still reads: the wasted remainder is `budget mod world.width`, and the
phone's cat size is `map / minTiles`. **Every derived number in the old
tables was perishable** — they assumed the 20-tile served world, and a
wider world under Fog re-rolls which handsets sit just under a boundary.
Re-run the arithmetic against the world actually served before spending
a design decision on it. Tables and the SC-001 history: this entry's git
history (removed 2026-09-11).

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

Owner: *"already done, it was in the handover."* Live since the
GROOM-OTHER-EDITS pass. The 2026-08-24 byte-equal check against the
handover is not re-runnable (`design-handoffs/` was a local drop, never
committed) — history, not something a reader can verify. For whoever
touches the axial groom branch next: **read the coupling note in
`GROOM_OTHER` first** — `axialTailUpY`, `axialTailClearHead`,
`axialHeadWide` and `axialHeadShow` interact, and three separate rounds
lost the rear tail cue to exactly that (the lab's groom-other card draws
all three views at once for this reason). Still first-cut and dialable:
`VIEW.groomLean` (0.22 tiles, 450ms), judged in the lab, never yet
watched easing on the served world.

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

### Real heatmaps replace the worn paths (added 2026-08-21; owner's ask; LOW priority)

The spec-008 worn-paths overlay is shipped UNAVAILABLE as of 2026-08-21
(`VIEW.meadow.paths: false`, both homes; the owner: "disable worn paths
for the time being"). Visitors never saw it (`showPaths` defaults off,
008 FR-009) — this also inerts the p-key debug overlay. The successor
she wants is a real heatmap: presumably occupancy-weighted colour over
the ground rather than per-tile bare-earth patches. The 008 machinery
(`pathHeat`, decay, `wornPaths()`) still runs underneath and is the
obvious data source; the work is the presentation. No deadline.

**Re-asked 2026-09-27** (owner, verbatim): "let's add a backlog entry to
replace it with a real, high quality heatmap". The bar is quality, not
just existence: judge it in a gallery lab card at true size against the
real meadow, day and night, before it goes near the map. When it lands it
takes over the `p` key, which is inert today; docs/viewer.md marks `p`
unavailable and the on-page legend omits it, so both change with it.

**Plan, owner 2026-09-27: a static heatmap generated at seating.** Not
the live per-session accumulation, and no server change. The owner: "we
can pre-calculate the heatmap on the laptop by running the world in
headless mode, and just render a static heatmap overlay", and "A
per-seating heatmap could be useful data as well, so I'll make that part
of our seating process." The next generation breaks schema and needs a
`--fresh` anyway, so the first heatmap comes from clean data.

- What it shows: where this roster, on this map, tends to spend its time
  over a long headless run. Not the live world's own history, which a run
  from the seed does not retrace. F-045 (lab dispersal reproduces live)
  and F-042 (battery means within 0.25 of live) are the evidence that
  the lab picture transfers.
- Producer: the seating process (Experiments' lane, her call). Consumer:
  the client draws it as a static overlay behind the `p` key.
- ⚠ Staleness is the trap (cf. the OG card). The file must carry what it
  was generated from (world fingerprint, config hash, the seated
  policies), and the client must check that against the served `/config`,
  hiding or labelling the overlay on a mismatch rather than drawing a
  heatmap of a world that no longer exists.
- Per-kitty and per-activity layers are nearly free from the same run.

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

Closed by the owner, and the reasoning generalises: the walk's body bob
was built, measured and reverted the same day (branch history,
`56b071c`) because at our tile size a few tenths of a pixel of vertical
motion on a rigid body reads as **edge shimmer, not life** (0.56px
peak-to-peak at a 56px tile, against a foot's 9.52px fore–aft). An idle
float is worse — no lateral motion to hide behind. If it ever returns it
returns as the whole-cat mechanism from that revert, at an amplitude
that clears a pixel.

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

Shipped. The lesson outlives them: what makes sub-pixel geometry read is
**opacity** (0.25 turns a hairline into a soft hint, not an aliased
dotted line) and **length** (run past the head so most of the whisker
falls against background). Worth remembering when the next feature is
costed at a pixel width — that is one of at least three things setting
whether it reads.

### ~~The walk contradicts itself travelling north/south~~ — SHIPPED 2026-08-20 (PR #275)

Design's rebuild landed and took none of the four options costed here —
the diagnosis under them was wrong. The fault was never the gait: the
axial chest's underside sat below the ground line (`AXIAL.bodyY` 0.7 +
`bodyRy` 0.185 = 0.885 against `CAT_GROUND` 0.88), so there were ~two
pixels of visible leg at a 120px tile and every note about sweeps and
cadence described legs nobody could see.

Two durable parts, kept: the **census** — 717 east/west frames against
394 north/south, ~10% of all frames; that measurement holds and is what
to re-derive. And the standing lesson: this entry's costed **do-nothing
was the right answer for two years and stopped being right the moment
the tile got big enough to see the problem** — remember that the next
time an entry here carries a costed do-nothing. The four options and the
original gait analysis: this entry's git history (removed 2026-09-11).

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

### Debug option: show the vision radius (added 2026-09-10; Client thread — after the fog shakeout, owner)

Owner's ask, verbatim: **"debug option: show vision radius. Notes: each cat
should have a different color, and the colors should overlap in a way that is
still aesthetically appealing even when all 5 cats are together."**

What gets drawn is Fog Gen 1's sight: the Euclidean disc of `vision.radius`
tiles a cat sees kitties and elements inside
(`crates/cloudkitty-core/src/config/mod.rs:108-122`).

**The radius is served — read it, never hardcode it.** Spec 052 (key
settings, #364) puts it on `GET /settings`:

    { "group": "vision", "key": "radius", "value": 5, "source": "toml" }

A client-side copy of an engine value is the failure owner call #362 was
opened for. `/settings` reaches the box on the next server update; checking
the live box before then finds no vision field and says nothing about whether
the surface exists.

`v` is the only free debug key (`b`, `d`, `g`, `h`, `l`, `p` and `r` are
taken); the toggle mold is in `client/app.js`.

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

## P3 — depth

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

### ~~Swim pose for wading kitties~~ SHIPPED (PR #92, merged 2026-08-04)
`poseFor` water arm + v2 `swim` layout (v1 keeps normal standing per
the owner's call); values live in `CatV2.SWIM` on main. Whether a final
owner value-judging pass in `gallery-v2.html` closes this fully is the
Client thread's call — otherwise done.
