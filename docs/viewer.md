# The viewer

A tour of the browser window onto the world. The viewer is a window, not
a control surface — every endpoint it reads is read-only (Article V), and
everything on this page is a rendering choice the engine knows nothing
about.

## The meadow keeps its own day

Day, golden hour, night, and back — 600 ticks around, eight minutes at
the served 800ms tick. The spans are deliberate: a long day (280 ticks),
brisk twilights (65 each), a real night (190), with the fades tuned so
twilight is approached slowly and handed over briskly. The hour is a pure
function of the served tick, so every viewer sees the same sky, and a
restart resumes mid-day exactly where the snapshot left off. The engine
knows nothing about any of it — no behavior, need, or spawn reads the
clock.

## Footer toggles

- **Time of day**: cycles the world's cycle → Always Day → Always
  Twilight → Always Night. Only an explicit choice is remembered (per
  browser); the default is always the world's own cycle.
- **Art vocabulary**: switches the cats between the two drawing styles —
  v2 is the default, the original v1 one click away — likewise
  remembered per browser only on an explicit choice.

## Debug keys

All three start hidden on every load, and all three are keyboard-only by
design — a phone viewer stays clean.

- <kbd>g</kbd> — **greebles**: fast, erratic critters that are always in
  the world and always in the API but are never drawn. Their
  invisibility is a rendering rule in the client, never a filter in the
  API — which is why you will sometimes see a kitty pounce on absolutely
  nothing.
- <kbd>l</kbd> — the tile grid lines.
- <kbd>p</kbd> — **worn paths**: faint trails where the kitties have
  walked this session, fading with time and kept entirely in the
  browser.
