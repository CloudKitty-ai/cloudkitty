# crossing-shots

Photographs two builds of the client through one day→dusk crossing and
subtracts them, pixel by pixel.

```
node client-measurements/crossing-shots/run.mjs <baseline-root> <change-root> [out-dir]
```

Both arguments are worktree roots — the directory holding `client/`. Both
sides are served with **no probe injection**: the shipped page, the shipped
renderer, and the same captured world (`crossing-probe/world.json` +
`config.json`), so the only difference between the two images is the code.
Each root must therefore be at or after the probe merge `9b06c4f`, or the run
stops and says so.

## Why it exists

The cross-fade (`CROSSING-BAKES.md` §6) replaces a per-step rebake with two
baked layers blended per frame. The argument that this is visually equivalent
is arithmetic — `bake(mix(A,B,t)) == mix(bake(A),bake(B),t)`, because
`mixPalettes` is a per-channel lerp and canvas compositing is affine at fixed
alpha — and arithmetic is worth nothing here until something photographs it.

## Reading the table

```
 tick | mean d | max d | % over 2/255
  256 |   0.56 |    36 |         0.5
  262 |   1.30 |    56 |         6.4
  266 |   1.19 |    59 |         5.4
  272 |   1.42 |    67 |         6.6
```

That is the run behind §9, reproduced 2026-09-20 with baseline `9b06c4f` and
`client-crossing-xfade` at `402eee4`.

- **Tick 256 is a settled hour** (blend 0) — the two builds drawing the same
  thing. It is the rig's own noise floor, and it is not zero: 0.56 mean with a
  max of 36 is dithering and antialiasing, not a difference in the art.
- **262/266/272 are inside the fade** (blend 0.25, 0.42, 0.67), the only place
  a cross-fade can differ from a rebake. Mean stays near 1/255, well under a
  just-noticeable difference.
- **The maxima are localised and they are the point of the `% over` column.**
  ~6% of pixels move more than 2/255, and the worst move ~60 — those are
  detail edges (blade tips, flower centres) where the two paths land on
  opposite sides of a rounding, not a visible shift in the field.

Judge the mean and the share. A max of 60 on its own says nothing.

## The trap this rig is built around

**The app drives its own clock.** Setting `latestWorld.tick` and waiting does
not pin it: the render loop reschedules at the bottom of every frame and walks
the state back under you. Cancelling the pending frame is not enough. The
scheduler itself has to be stubbed *first*, and only then is the tick yours.

Two full capture runs were invalid before that landed, and both looked
completely plausible — the shots came out, they were just not of the ticks
they were named after. One of them produced a confident report of a
meadow/chrome mismatch that did not exist.

**A delay is a guess about frame time, and here frame time is the subject.**
The same bug class was fixed in the probe in `7726adc`.

So the rig never trusts a delay to establish app state. After the settle it
re-reads and asserts, and it refuses the run loudly rather than writing a
plausible picture. Verified by removing the stub: the guard fires on the first
tick.

⚠ **Assert the blend, not the tick.** Under a live clock the tick sat exactly
where it was put (256) while the blend had already moved to 0.042 — the app
re-derives the fade from its own timebase, so a tick-only guard passes while
the image is wrong.

The residual `PRESENT_MS` settle is for the compositor presenting a frame and
nothing else; app state is never left to it.

## Other things worth knowing

- **dpr 2, 900×900.** The bake is capped in *device* pixels, so a dpr-1 shot
  would compare an upscale path neither the phone nor the laptop walks.
- **The diff samples the meadow interior only** (14–85% × 13–92%). Page chrome
  cannot differ, and including it dilutes the mean with a large dead field.
- **A browser does the subtraction** because nothing in node's standard
  library decodes a PNG.
- Servers and Chrome both bind port 0 and report back, so a run cannot collide
  with whatever else is listening on this machine.
