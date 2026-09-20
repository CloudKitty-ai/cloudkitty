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

## The conditions

Edit the list at the bottom of `probe.js`. Each takes flags:

| flag | what it does |
|---|---|
| `bakes: false` | refuse the null that forces a rebake — **the ceiling** |
| `pond: false` | pin `paletteKey`, freezing the POND alone (the ground still rebakes) |
| `flat: true` | same canvas, same size, one `fillRect` instead of the art — separates drawing from upload |
| `device: N` | clamp the bake to N device px per side |
| `scale: k` | scale the bake tile by k |
| `reuse: true` | pool the disposable canvases instead of allocating |
| `blur: false` | zero the blur *radii* ⚠ this still assigns `ctx.filter`, so it does NOT rule blur out |
| `xfade: true` | the two-layer cross-fade, ground and pond |
| `warm: 'burst' \| 'spread'` | build the cross-fade layers all at once, or one per frame |

⚠ **Verify the meadow still draws before trusting a treatment's timings.**
Two conditions here mutate the renderer (the canvas pool hands back shared
buffers; the cross-fade rebuilds the ground from cached layers). Screenshot
the row and look at it. A broken draw is fast.
