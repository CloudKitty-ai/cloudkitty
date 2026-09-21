# crossing-probe

**The instrument behind [CROSSING-BAKES.md](../CROSSING-BAKES.md).** It serves
the worktree's own `client/` against a captured world, stubs the WebSocket so
the world clock is ours, and walks a real day→dusk crossing under each
condition while counting dropped frames.

```sh
curl -s https://kitties.ai/world  > client-measurements/crossing-probe/world.json
curl -s https://kitties.ai/config > client-measurements/crossing-probe/config.json
node client-measurements/crossing-probe/serve.mjs
```

Then open `http://127.0.0.1:8911/` — or the machine's LAN address for a
phone, which is the reading that matters. It self-starts and prints a panel
top-left; it needs ~11s per row and the screen kept awake.

The two captures are gitignored: they are raw samples, and the two curls
above rebuild them.

## Reading it

**Judge by dropped frames, never by `in canvas`.** Safari records 2D canvas
commands and rasterizes them in the shared GPU process, so a
`performance.now()` bracket around the draw cannot see this cost — measured,
Safari reported 113ms where Chrome reported 273ms on the same crossing while
dropping 78 frames over 33ms that Chrome did not.

**Every treatment is bracketed by a repeated baseline.** This machine runs
training jobs and conditions are not independent; two early runs disagreed
20x on the same bake size before the baselines went in. Compare a treatment
to the baselines *either side of it*, and read the baselines against each
other first — if they climb, the run drifted and the treatments are not
comparable.

**Chrome cannot answer any of these questions.** Its baseline is already
clean, so every row lands at 0-3 janky frames and nothing separates. Use it
to check the rig renders correctly, then measure on Safari.

## What it measures now

The cross-fade has landed, so **the no-flag baseline is the shipped
renderer**: two bakes per crossing, composited per frame. The sustained jank
this rig was built to find is gone — 32–47% of frames over 20ms became
0.5–0.8%, against a frozen ceiling of 0.3–0.8%.

What is left is **one stall, ~400ms, when a theme is baked**, and nothing
shrinks it: the 2048 cap bought 13%, baking one theme instead of two bought
5%, spreading it over frames bought nothing. §6.3 moves it into the lull
before a crossing, which puts it somewhere harmless without removing it.

The current conditions test §7's hypothesis: **Safari defers an offscreen's
rasterization until something draws FROM it.** If that is right, the bake in
the lull is cheap and the stall is really the first blit, landing wherever the
crossing first composites — and the fix is to blit each layer once, in the
lull, on purpose.

| condition | what it is |
|---|---|
| `baseline N` | the shipped renderer, untouched |
| `LULL BAKE (as shipped)` | one theme baked inside the counter against a warm cache — §6.3's recurring cost |
| `LULL BAKE + blit each layer once` | the same, plus one full-canvas blit into a 1×1 scratch per layer |
| `FROZEN (the ceiling)` | `blend` pinned null, both layer providers memoized: nothing bakes, nothing composites |

**Read `worst` on the two lull rows against each other**, then both against the
baselines either side. If the blit row's stall moves to the blit and the
crossing comes out clean, §7 is right and the fix is four lines in `app.js`.

## To measure the defect instead

Run this rig at `9b06c4f`, before the cross-fade. That version simulated the
fix from outside the renderer (`xfade`, `wash`, `warm`, and separate
`bakes`/`pond` freezes); all of it is gone here, because against a renderer
that really cross-fades the simulation just double-bakes. The old flags
attributed cost between the ground and the pond, which is a closed question —
both mattered, and the fix removed both.

## The conditions

Edit the list at the bottom of `probe.js`. Each takes flags:

| flag | what it does |
|---|---|
| `lull: 'plain' \| 'blit'` | evict the incoming theme, then bake it inside the counter — with or without the forced blit |
| `freeze: true` | the ceiling: `blend` pinned null, layer providers memoized |
| `flat: true` | same canvas, same size, one `fillRect` instead of the art — separates drawing from upload |
| `device: N` | clamp the bake to N device px per side |
| `scale: k` | scale the bake tile by k |
| `reuse: true` | pool the disposable canvases instead of allocating |
| `blur: false` | zero the blur *radii* ⚠ this still assigns `ctx.filter`, so it does NOT rule blur out |
| `transitions: false` | drop the CSS token transitions |

## Traps this rig has already fallen into

⚠ **Settle on a QUIET hour, never on the first tick of the fade.** Tick 256 is
already `day>dusk@0`, so the renderer holds both themes by the time the
counter starts and the lull bake is a cache *hit* — every row then measures
the same nothing, convincingly. The settle now lands at 248 and a lull row
that baked nothing **throws** instead of reporting a number.

⚠ **`app.js` prewarms the next phase during a lull**, so settling quietly
warms the incoming theme too. The lull conditions evict it on purpose; that
eviction is the measurement.

⚠ **Wait for the draw, never for a duration.** `device`/`scale` move the bake
tile, and warming against a stale tile keys every layer at the wrong size —
the burst is thrown away and happens again, lazily, inside the crossing. A
fixed delay is a guess about frame time, and frame time is the subject: 32ms
spanned a frame in Chrome and did not on the phone, where a baseline frame
runs 20–170ms.

⚠ **Verify the meadow still draws before trusting a treatment's timings.** A
broken draw is fast.

⚠ **`in canvas` is not the judge, and this is why.** A full two-layer 2048
bake measures **~1ms** of time inside the draw calls in Chrome. The work is
real; it is simply not happening where a `performance.now()` bracket can see
it. Judge by dropped frames.
