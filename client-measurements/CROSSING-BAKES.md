# Crossing bakes

**The design record for what a time-of-day crossing costs to draw**, why it
lags Safari, and the shape of the fix. Read it before touching
`applyTheme`, `blitGround` or `buildPondLayers`.

Diagnosed 2026-09-19/20 against Safari on four displays and an iPhone.
Nothing in `client/` has changed; this is the case for a change.

---

## 1. What happens today

`applyTheme` (app.js) runs once per **blend step**. On each step it does two
things that invalidate caches:

```js
renderer.groundCache = null;   // app.js — explicit
renderer.paletteKey = key;     // ...and this is in the pond signature
```

The pond is the one that hides. `render.js:1552` signs the pond cache
`${paletteKey}|${bakeTile}|${water}`, so moving the key rebuilds the pond
layers as surely as nulling the ground rebuilds the ground.

A crossing is **24 ticks at 192 steps** (or 16 at 128) — either way the
100 ms `BLEND_MAX_STEP_MS` bound binds, so it is **10 steps a second for
~19 seconds**. Measured on the live page: **184 ground bakes in one
crossing, against 8 when the light is settled.**

Per step that is **six canvas allocations and nine `filter: blur()`
passes** — one canvas and one blur for the ground, one padded scratch for
its blur, four canvases and two blurs per pond for the pond layers.

**A colour change is invalidating a geometry cache.** The noise field, the
scatter, the pond paths and the blur radii owe nothing to the palette. Only
the colours do.

---

## 2. What it costs

Frames slower than 20 ms, over one day → dusk crossing, Safari:

| | as shipped | pond frozen | + ground cross-fade | frozen (ceiling) |
|---|---|---|---|---|
| iPhone, dpr 3 | 47–54% | 8.6% | 1.1% | 0.3% |
| 4K, dpr 2 | 14.3% | 0.1% | 0.1% | 0.0% |

Chrome, for contrast, drops **6 frames of 1251** on the same crossing and
none over 33 ms. This is a Safari problem, and the iPhone — the primary
target — is 3–4× worse than any desktop.

### The two traps that cost me three wrong conclusions

**Safari's JS timers cannot see this cost.** Safari records 2D canvas
commands and rasterizes them in the shared GPU process. Measured on the same
crossing, Safari reported **113 ms** inside the bake functions where Chrome
reported **273 ms** — while dropping 78 frames over 33 ms that Chrome did
not drop. *Judge by dropped frames. Never by time inside the draw call.*

**Shrinking the bake canvas is a confounded test.** It cuts rasterization
and texture upload together, so "faster when smaller" does not mean the
upload was the cost. The condition that separates them is a **flat bake** —
same canvas, same size, one `fillRect` instead of the art. Flat is clean on
every device, so the cost is the drawing and the upload is nearly free.
I asserted the opposite from the confounded result.

**And cost here is not proportional to work.** The pond's canvases are
*smaller* than the ground's (2048 vs 4096 device px) and its JS time is
comparable, yet on the desktop it causes **all** of the jank. Four
allocations and eight blurs per step trip something that one and one does
not. ⚠ Which of the two is untested: an earlier probe "cleared" blur by
setting the blur *radius* to zero, which still assigns `ctx.filter`. That
proved nothing. Blur has never actually been ruled out.

---

## 3. What was ruled out, and by whom

- **Coarser blend steps for the ground.** Owner, 2026-09-19: the stepping is
  visible at slower paces, and "ground is most of what we're looking at".
- **Permanently lower bake resolution.** Half resolution is a mean 0.144 L\*
  difference with 98.7% of pixels under a JND — but the 1.3% that moves is
  all `drawGroundDetail`, and at 1:1 the grass blades visibly soften. Judged
  and rejected on the crops, not on the statistic.
- **Lowering `GROUND_BAKE_MAX_PX` 4096 → 2048.** The curve has no knee:
  2048 still leaves 206 janky frames. Dead.
- **Accelerating or simplifying the drawing.** Helps the desktop (bound by
  fill area) and not the phone (bound by command count — ~1200 fills, which
  a smaller canvas does not reduce).
- **Static object shadows.** 41.56% → 41.04% of pixels over a JND. It
  removes the worst *spikes* (max 42 → 18 channel units, the blades stop
  rotating) and nothing else.
- **Pooling the six canvases.** No effect, and it made >33 ms frames worse —
  reusing a buffer the GPU may still be reading stalls on a sync.

**Read the phone, not the desktop.** Freezing the pond alone is already
clean on the 4K, which says the ground does not matter. On the phone the
ground is worth another 8.6% → 1.1%. I generalised from the desktop twice
and the phone contradicted it both times.

---

## 4. The fix

**Bake each theme once into static layers; cross-fade them.** 184 bakes per
crossing become 2.

This is exact for colour, and that is provable rather than hopeful: every
meadow colour is a per-channel lerp (`mixPaletteColor`), canvas compositing
is affine in the colour operands at fixed alpha, and blur is a linear
operator — so `bake(mix(A,B,t))` equals `mix(bake(A),bake(B),t)` pixel for
pixel. The two bakes share geometry, so their alpha masks are identical and
the cross-fade is a true per-pixel lerp.

### `MEADOW.shadowLean` is the sole exception

It is **geometry, not colour**, and it lerps only because `mixPalettes`
lerps any number. It drives four things:

| | |
|---|---|
| `meadow.js:803` | the sun wash gradient's **direction** |
| `meadow.js:868` | `bladeLean` — the grass blades **rotate** |
| `meadow.js:937` | a bloom's stem offset |
| `meadow.js:1322` | bush shadow lean |

Rotating geometry cannot cross-fade: two gradients at different angles do
not blend into one at the intermediate angle. Measured, worst crossing, % of
pixels over 1 L\*:

| | over 1 L\* |
|---|---|
| today (lean lerps everywhere) | 41.6% |
| static object shadows only | 41.0% |
| wash drawn per frame, **on top** | 13.2% |
| lean pinned everywhere | 7.5% |

The wash is nearly all of it; the object shadows are ~0.5 points.

⚠ **The wash is baked UNDER `drawGroundDetail`.** Drawing it per frame *on
top* tints the flowers and bushes, which is why 13.2% is worse than pinning.
That ordering is why the ground splits in two.

### The shape

Per theme, two static ground layers and one pond pair:

⚠ **`drawGroundCover` is NOT in the bake.** `render.js:1478` bakes with
`cover: false` — shrubs are drawn per frame at `this.tile` and sorted against
the cats so they can pass behind them (`render.js:1274`). So the `over` layer
is `drawGroundDetail` ONLY. Getting this wrong puts shrubs behind cats.
It also means the sharpest things on screen — shrubs, cats, bubbles, the pond
meniscus — are drawn per frame at full resolution and **no bake cap can touch
them**. What a cap softens is only the tone field (blurred already) and the
detail scatter.

```
under = tone + jitter + blur          (everything below the wash)
[ the sun wash, drawn per frame at the live lean ]
over  = ground detail + cover         (everything above it)
pond  = shore + lip                   (cross-fades as-is; no lean in it)
```

A step composites `under_A`/`under_B`, draws the wash, composites
`over_A`/`over_B`, and composites the pond pair. No allocation, no blur,
nothing rebaked. **The sun sweep stops being quantised into 192 steps and
becomes continuous — better than today, not merely equal.**

### Measured, in Safari, on the real client

| | as shipped | cross-faded | ceiling |
|---|---|---|---|
| iPhone, dpr 3 | 47–54% janky, 66 bad, 518 ms in canvas | **3.1%, 2 bad, 24 ms** | 0.3%, 1 bad |
| 4K, dpr 2 | 14.3% janky, 3 bad, 67 ms in canvas | **0.4%, 2 bad, 7 ms** | 0.0%, 0 bad |

---

## 5. The decisions, ruled 2026-09-20

### 5a. When to bake, and how many to hold

The bakes have to happen somewhere. Lazily, at the first step of a crossing,
they land in **one frame**: worst frame **310 ms on the phone**, 65 ms on the
4K. That is a visible stall — smaller than today's, and rarer, but sharper.

**Spreading the bake over frames does not work.** Measured on the phone,
2026-09-20: the six units (2 themes × {ground under, ground over, pond pair})
built back to back give a worst frame of **424 ms**; built one per frame with
two frames of yield between, **388 ms**. An 8% difference across a six-way
split. Safari batches the rasterization on the GPU thread whatever the main
thread does — the same reason its JS timers cannot see this cost, and the
same reason pooling the canvases did nothing. Finer chunking will not help;
layer granularity was the coarsest useful test and it showed nothing.

So the bake is a **~400 ms main-thread stall on the phone, once per theme
pair**, and the only ways out are to move it off the main thread entirely
(OffscreenCanvas in a worker — but `blurredLayer` and `buildPondLayers` both
call `document.createElement`, so that is a real refactor of meadow.js), to
make it smaller (not splitting the ground roughly halves it — see 5b), or to
place it where a freeze is cheapest. Note the cadence: four crossings per
600-tick day is **one stall every ~2 minutes**, against today's 19 seconds of
stutter on the same cadence.

Owner's proposal (2026-09-20): bake on load instead, where 1–2 seconds is
forgivable. Right instinct; **all four themes is the version that breaks.**
Resident canvas memory:

| | today | 2 themes, split | 4 themes, split |
|---|---|---|---|
| iPhone (dpr 3) | 72 MB | 226 MB | **452 MB** |
| 4K (dpr 2) | 96 MB | 320 MB | **640 MB** |
| laptop (dpr 1) | 51 MB | 142 MB | **284 MB** |

Mobile Safari caps total canvas area and **hands back a blank canvas** past
it — the failure `GROUND_BAKE_MAX_PX` already exists to prevent
(`render.js:17`, "a correctness bound and not a tuning knob"). A blank
meadow on phones is a worse bug than the lag.

**RULED: hold two.** You only ever need the theme you are in and the
one you are crossing to. Bake the current theme on load — it is baked today
anyway — and bake the next during the lull: day runs 280 ticks and only the
last 24 fade, so there are ~256 ticks (≈3.4 minutes) of nothing happening
before each crossing. Roll forward, evict behind.

⚠ `bakeTile` moves on **resize and dpr change** (not on camera zoom — the
bake is sized for the tightest camera on purpose). A rotation or a window
drag invalidates every held theme at once. Needs a rebake path that does not
stall; probably the same lull mechanism, seeded by the resize.

### 5b. Whether to split the ground at the wash — RULED: split it

The split costs 2x the ground memory. At full resolution that was 81 MB against
40 MB per theme on the phone, which made it a real trade against the sun sweep.
**At the 2048 cap it is 16 MB against 8 MB**, and the pond (already capped at
2048) dominates either way — so the split costs ~32 MB rather than ~90 MB.

Ruled: **split**, and keep the continuous sun sweep. The cap is what made it
affordable.

### 5c. The bake resolution — RULED: cap at 2048

`GROUND_BAKE_MAX_PX` is **already 4096** and already binds on a 4K (the 4096
in the probe panel *is* the cap). The phone bakes 3257, under it. So "cap at
4K" is a no-op; the ruling is to lower it.

Lowering was dismissed earlier in this investigation and that dismissal is
void: it was judged against the *per-step* jank, where 2048 left 206 janky
frames. The cross-fade removes the per-step problem entirely, and what is
left — the one-off stall and the resident memory — **both scale with pixels**,
which is exactly what the cap controls.

| cap | linear | phone stall | 2 themes resident |
|---|---|---|---|
| 4096 (today) | 100% | ~400 ms | 226 MB |
| 2560 | 79% | ~247 ms | 164 MB |
| **2048** | 63% | **~158 ms** | **128 MB** |
| 1536 | 47% | ~89 ms | 100 MB |

**Judged on the art, at 1:1 and at 3:1, against the blooms** — which are the
finest thing in the bake, located by scanning the detail layer for opaque ink
rather than picked by eye:

- **At 1:1, at maximum zoom, all three caps are the same picture.** The
  flower reads as a flower at every one. Owner: "the difference is pretty
  marginal."
- At 3:1 the ranking is clear — 2560 slightly soft, 2048 blurs petals into
  each other.

Since 1:1 is the only size anyone sees, 2048 is ruled. 1536 is where it
starts to show even in the tone field, so it is the floor, not a candidate.

⚠ The constant is documented as a **correctness** bound (mobile Safari caps
total canvas area and returns a BLANK canvas past it). Lowering it is safe in
that direction, but it now serves two masters and the comment must say so.

### 5d. Interpolating the upscale — nothing better is available

Canvas 2D upscaling is bilinear. `imageSmoothingQuality` is the only knob and
in most engines it affects *downscaling*; bicubic or Lanczos would need
`getImageData` per-pixel work, which is the cost being escaped. **The client
never sets it at all**, so today's blit is default `'low'` — set it to
`'high'` because it is one free line, and expect nothing from it.

**SHELVED, with the numbers already taken: split resolution.** Because the
ground is split for the wash anyway, the halves can carry *different* caps —
`under` is blurred and has no high frequencies to lose, `over` (the blooms) is
the only thing that suffers. `under 1536 + over 3257` is **49 MB** per theme
against 81 MB. Chrome prices the two layers at 50/50, but that is a
command-count measure and the wrong instrument; in Safari the tone field
touches 100% of pixels and the scatter perhaps 5-10%, so `under` should
dominate far more. Not built: it adds a second resolution dial to protect
detail the owner cannot distinguish at 1:1. Reach for it if blooms ever
bother you at some future zoom.

## 6. The design, as ruled

1. **Bake each theme once** into two static ground layers (`under`, `over`)
   plus its pond pair. 184 bakes per crossing become 2.
2. **Cap the bake at 2048 device px** per side (`GROUND_BAKE_MAX_PX`).
3. **Hold two themes** — the current and the next, both baked on demand.

   > **Reversed 2026-09-21, and the code removed.** This originally read
   > "bake the next during the lull (~256 quiet ticks before each fade)",
   > which item 6 justified. Measured with the prewarm stubbed, so the bake
   > lands inside a frame that is also compositing the crossing: **17 ms,
   > against that same row's p99 of 20 ms.** A frame carrying a full
   > two-layer 2048 bake was better than the row's ordinary bad frames, and
   > the sustained share barely moved (0.9% with, 0.8% without). The cache
   > holds two themes as before; nothing schedules the second one.
4. **Draw the sun wash per frame**, between `under` and `over`, at the live
   lean. The sweep becomes continuous rather than quantised into 192 steps.
5. **Set `imageSmoothingQuality = 'high'`** on the blit.
6. ~~Accept one stall per theme pair, placed on load and in the lull.~~
   **WITHDRAWN 2026-09-21 — there is no stall.** A bake costs 18 ms against a
   control's 17 (§7, §9). Both the "~158 ms" this item was ruled on and the
   "~400 ms" that corrected it were the `worst` column of a crossing row
   reading the device's outlier tail; the same runs show 305–375 ms frames
   with nothing baking. Nothing is accepted because nothing is paid.
   > "A worker would fix it" is unverified and the evidence now runs against
   > it -- 8-17 ms of that frame is inside the draw calls, so relocating the
   > JavaScript relocates 2-4% of the cost.

Expected, from the measured cross-fade at full resolution, with the cap
making the stall and the memory smaller again:

| | as shipped | ruled design (expected) | **measured** (§9) |
|---|---|---|---|
| iPhone, frames >20 ms | 47–54% | ~3% | **0.5–0.8%** |
| iPhone, frames >33 ms | ~61 | — | **1** |
| 4K, frames >20 ms | 14.3% | ~0.4% | not re-run |
| phone stall | n/a (continuous jank) | ~158 ms, twice | **~400 ms, twice** |
| resident canvas | 72 MB | ~128 MB | not measured |

## 7. Still open

- **The blade-lean residual.** With the wash out of the bake, the blades are
  the only lean-driven geometry left. Never isolated. Measure it before
  believing the cross-fade is clean; if it shimmers, static blades are the
  cheap answer (they cost ~0.5 points of fidelity and buy the rest). This is
  a FIDELITY question, not a cost one: the blades are inside the baked `over`
  layer and cost nothing per frame.

- ~~**What the ~400 ms stall actually is.**~~ **CLOSED 2026-09-21: there is no
  stall.** Measured directly on the phone, 12 repetitions per condition, the
  frame that bakes a theme costs **18 ms against a control's 17** (max 22 vs
  19), and bake-plus-first-draw is **33-34 ms in every condition including the
  control**. A full two-layer 2048 bake is a couple of milliseconds.

  The ~400 ms never existed. It was the `worst` column -- one sample out of
  ~660 frames -- reading this device's own outliers, which the same run puts
  at 122-177 ms with *nothing baking*. Everything built on it is void: the
  cap "bought 13%", one theme "cost the same as two", the 310 ms first-bake
  frame in §4, and the Safari-defers-rasterization hypothesis that was going
  to explain it all. Blitting each layer at bake time moves ~2 ms from the
  draw into the bake (D 15 -> 13, W 18 -> 20), which is the predicted
  direction and a thousandth of the predicted size. **Not worth shipping.**

  ⚠ The caveat, stated: the forced draw goes into a 1x1 scratch, and Safari
  may rasterize a downsampled version of a 2048 source more cheaply than a
  full-size composite would. The crossing rows bound that independently --
  the whole crossing runs 2 frames over 33 ms against the frozen ceiling's 1,
  and its worst frame (122 ms) is *lower* than the ceiling's (177 ms).
  Whatever the first full-size draw costs, it is not hundreds of
  milliseconds.

  **The lesson, which cost three sessions: `worst` is an order statistic over
  one run.** It cannot be read as a treatment effect on a device with a heavy
  outlier tail, and every conclusion this document drew from it was wrong in
  the same direction. Judge sustained jank by the share of frames; judge a
  single-frame cost by repeating it against a control.

- **The pond's tighter bound is now vacuous.** §6.2 dropped
  `GROUND_BAKE_MAX_PX` to 2048, which is exactly `POND_BAKE_MAX_PX`, so
  `pondBakeTileFor` can no longer bind -- the ground is as coarse as the
  pond, and the asymmetry the bound exists for ("a blurred band carries a
  coarse bake better than grass does") is gone. Restoring it means lowering
  the pond ceiling, which changes shipped art. **Owner's call.** The equality
  is pinned in test-motion so moving either ceiling reddens.

- **Detail double-draws at mid-fade.** `over` is transparent glass, and the
  composite draws the near hour at full alpha then the far hour at the step.
  That is exact where the ink is opaque and slightly over-inks the
  anti-aliased edges. Measured against the old renderer at four points
  through a day->dusk fade: the settled hour is essentially identical (mean
  channel delta 0.56/255, which is the rig's own noise floor), and the three
  points inside the fade run a mean of 1.19-1.42/255 -- under a JND -- with
  localised maxima of 56-67 on ~6% of pixels, at detail edges. The instrument
  is `crossing-shots/` (below); those are its numbers, reproducible.
- **Why the pond is disproportionate.** Four allocations vs one, eight blurs
  vs one, on smaller canvases. The cross-fade removes both so it stopped
  mattering, but nobody knows which.
- **Whether the pond needs the wash treatment too.** It has no `shadowLean`
  in it, so probably not, but it was never checked at every blend position.

## 8. The rigs

**[crossing-probe/](crossing-probe/)** — committed, because every number above
came out of it and it is the acceptance test for the implementation.


Everything above was measured with a probe in the session scratchpad: a node
server that serves the worktree's `client/` with a captured `/world`, stubs
the WebSocket so the world clock is driven locally, and walks a real crossing
under each condition while counting dropped frames.

Two things it taught, worth keeping whatever happens to this design:

- **Bracket every treatment with a repeated baseline.** This machine runs
  training jobs; conditions are not independent and run order drifts. Two
  runs disagreed 20× on the same bake size until the baselines went in.
- **Write probe pages async.** A synchronous test page blocks its own CDP
  polling, so the driver reads an empty document and reports nothing. Put
  `await new Promise(r => setTimeout(r, 0))` between steps.


### `crossing-shots/` — the second rig, for the picture rather than the clock

`crossing-probe/` answers "does it drop frames". It cannot answer "does it
still look right", and the two questions failed in opposite directions here:
the design's arithmetic guaranteed the colour and said nothing about the
anti-aliased edges. `crossing-shots/run.mjs` serves two worktrees with no
injection, photographs both at four points through one crossing and subtracts
them. Its README carries the reading rules; §9's fidelity numbers are its
output.

⚠ It pins the app clock by stubbing `requestAnimationFrame`, and asserts the
**blend** afterwards rather than the tick. Under a live clock the tick stays
exactly where it is put while the blend has already moved — the app
re-derives the fade from its own timebase — so a tick-only guard passes while
the image is wrong. Two capture runs were invalid before this landed, and
both produced plausible pictures of the wrong moment.

### The run that closed it (owner's iPhone, Safari, dpr 3, 2026-09-21)

Bake at the 2048 cap, 12 repetitions per row. W is the frame that bakes; D is
the next frame, the first to draw from what was baked.

| condition | W median | W max | D median | D max | W+D median |
|---|---|---|---|---|---|
| control (no bake) | 17ms | 19ms | 17ms | 19ms | 34ms |
| bake, draw next frame | 18ms | 22ms | 15ms | 16ms | 33ms |
| bake + blit, draw next frame | 20ms | 22ms | 13ms | 16ms | 34ms |

And the sustained rows from the same run, which is the result that holds:

| condition | frames >20ms | >33ms | worst |
|---|---|---|---|
| baseline (the shipped cross-fade) | 0.6% | 2 | 122ms |
| FROZEN (the ceiling) | 0.3% | 1 | 177ms |

The guard matters here: a row whose bake was a cache hit throws rather than
reporting a fast frame, so those 12 bakes per row are real bakes.

### ⚠ The ~400ms stall did not exist (2026-09-21)

Every number this document gives for the stall — the 490/428/407ms in §6.6,
the "fixed cost per burst" — is the `worst` column of a crossing row: a single
maximum over ~660 frames. A phone run on 2026-09-21 shows that column cannot
carry the claim. Its baselines climbed 171 -> 232 -> 243 -> 353ms, which is
the rig's own stop condition, and **the FROZEN row, with nothing baking and
nothing compositing, produced a 351ms frame.**

So the device emits outliers the size of the effect, and none of the earlier
readings were bracketed against a frozen row's *worst*. The stall may be
smaller than believed, or may not exist as a distinct phenomenon at all. What
is NOT in doubt is the sustained jank, which is measured as a share of
hundreds of frames: 32-47% over 20ms became 0.5-0.8%.

`crossing-probe` now measures the bake frame directly and repeatedly against a
control. **That run happened the same day and closed it: the bake costs 18 ms
against a control's 17.** See §7's first item for the numbers and the lesson.
§6.6's stall figures are withdrawn -- not adjusted, withdrawn; the instrument
that produced them cannot measure a single frame on this device.

## 9. What the implementation runs measured

Three runs on **the owner's iPhone, Safari, dpr 3, bake 3257 px, 2026-09-20**,
driven from `crossing-probe`. The device is hers and the runs are not
repeatable from this session, so the numbers live here rather than in a
scratch file. Each treatment is bracketed by repeated baselines. Baseline bad-frame counts held at 60-68 throughout, so
the runs are comparable; the baseline PERCENTAGES drift only because the
baseline delivers ~150 frames where a treatment delivers ~650.

| condition | frames | >20 ms | >33 ms | worst |
|---|---|---|---|---|
| baseline (as shipped) | 136-197 | 32-47% | 60-68 | 163-225 ms |
| cross-fade, 3257 px | 642-651 | 5.5-10.7% | 1-2 | 371-490 ms |
| cross-fade + 2048 cap | 649-650 | **0.5-0.8%** | **1-2** | 363-438 ms |
| cross-fade + cap, ONE theme | 652 | **0.2%** | 1 | 407 ms |
| rebakes FROZEN (the ceiling) | 665-692 | 0.3-0.8% | 0-1 | 21-159 ms |

Three levers were tried against the stall and none of them moved it:

- **The cap.** 490 ms -> 428 ms, where the pixel ratio predicts 171 ms.
- **Halving the work.** Baking one theme against a warm cache cost 407 ms
  against two themes' 428 ms -- 5%, inside the run's noise. The recurring
  lull bake is NOT half the cold one.
- **Spreading it over frames.** 401 ms against 432 ms burst on the phone,
  388 against 424 on the desktop. One canvas is already the whole cost, so
  there is nothing below it to spread to (§5a).

Two rig defects were found and fixed while measuring, both of which had
already produced numbers:

- `prewarm` keyed its layers on `o.tile` but read the PREVIOUS condition's
  opts, so every size-changing condition prewarmed at the wrong size and the
  burst happened again inside the crossing. The first 2048 reading (438 ms)
  is that, not a prewarm stall.
- The fix for it waited 32 ms, which spans a frame in Chrome and does not on
  a phone where a baseline frame runs 20-170 ms. It waits on the draw now.
  The panel prints the size the prewarm actually baked at and flags a
  mismatch in red, which is what caught the second bug.
