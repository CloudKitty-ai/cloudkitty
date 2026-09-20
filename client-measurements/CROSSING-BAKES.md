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

## 5. The two open decisions

### 5a. When to bake, and how many to hold

The bakes have to happen somewhere. Lazily, at the first step of a crossing,
they land in **one frame**: worst frame **310 ms on the phone**, 65 ms on the
4K. That is a visible stall — smaller than today's, and rarer, but sharper.

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

**Recommended: hold two.** You only ever need the theme you are in and the
one you are crossing to. Bake the current theme on load — it is baked today
anyway — and bake the next during the lull: day runs 280 ticks and only the
last 24 fade, so there are ~256 ticks (≈3.4 minutes) of nothing happening
before each crossing. Roll forward, evict behind.

⚠ `bakeTile` moves on **resize and dpr change** (not on camera zoom — the
bake is sized for the tightest camera on purpose). A rotation or a window
drag invalidates every held theme at once. Needs a rebake path that does not
stall; probably the same lull mechanism, seeded by the resize.

### 5b. Whether to split the ground at the wash

The split costs **2× the ground memory** (81 MB vs 40 MB per theme on the
phone). Not splitting means baking the wash in, which makes the wash
cross-dissolve between two angles instead of sweeping — the "lean pinned"
row, 7.5% of pixels over a JND.

| | ground per theme (phone) | the wash |
|---|---|---|
| split | 81 MB | exact, continuous, better than today |
| single layer | 40 MB | cross-dissolves between two angles |

Owner's call. It is the sun sweeping across the meadow at dusk against
roughly 90 MB on a phone.

---

## 6. Still open

- **The blade-lean residual.** With the wash out of the bake, the blades are
  the only lean-driven geometry left. Never isolated. Measure it before
  believing the cross-fade is clean; if it shimmers, static blades are the
  cheap answer (they cost ~0.5 points of fidelity and buy the rest).
- **Why the pond is disproportionate.** Four allocations vs one, eight blurs
  vs one, on smaller canvases. The cross-fade removes both so it stopped
  mattering, but nobody knows which.
- **Whether the pond needs the wash treatment too.** It has no `shadowLean`
  in it, so probably not, but it was never checked at every blend position.

## 7. The rig

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
