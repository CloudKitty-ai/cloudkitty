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

### Camera logic: what it aims at, and the trip in between (added 2026-08-18; Client thread)

Owner's call, 2026-08-18: **accepted as-is for spec 037, dialled when camera
logic is improved.** Not to be implemented alongside 037.

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

Not to be confused with the anchor **hysteresis**, which was a different
small-viewport fault (restlessness, 036 SC-006) and is fixed — 1.5 → 2.5 in
PR #245.

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
bundle itself lives at `deletemewhendone/design_handoff_art_uplevel/` and is
gitignored and temporary — everything below is the part worth keeping.

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
that needs the lab's occlusion strip.

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
the shipped code. The handoff itself is landed; what follows is what it
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

### The walk contradicts itself travelling north/south (added 2026-08-08; Client thread)
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
