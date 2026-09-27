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

- **Cards**: expands or collapses every kitty card at once, remembered
  per browser.
- **Vision** and **greebles**: show or hide those two overlays (see the
  keys below). They are the two debug overlays with a button as well as
  a key, so a phone can reach them. The button reads `hide` while its
  overlay is up, and neither is remembered: every load starts hidden.
- **Time of day**: cycles the world's cycle → Always Day → Always
  Twilight → Always Night. Only an explicit choice is remembered (per
  browser); the default is always the world's own cycle.
- **Art vocabulary**: switches the cats between the two drawing styles —
  v2 is the default, the original v1 one click away — likewise
  remembered per browser only on an explicit choice.

Time of day and art vocabulary sit in the developer group, which
<kbd>d</kbd> reveals.

## Debug keys

Every overlay starts hidden on every load, and nothing a key does is
remembered. The keys work whether or not the developer group is showing.

- <kbd>g</kbd> — **greebles**: fast, erratic critters that are always in
  the world and always in the API but are never drawn. Their
  invisibility is a rendering rule in the client, never a filter in the
  API — which is why you will sometimes see a kitty pounce on absolutely
  nothing. Also a footer button.
- <kbd>v</kbd> — **vision**: what each kitty can see. Sight is not a
  circle: a tile counts when its squared distance is within the radius
  squared, so the region stair-steps. Also a footer button.
- <kbd>r</kbd> — **purr hearts**: a heart over each purring kitty.
- <kbd>h</kbd> — **happiness bars**: a bar under each kitty. The cards
  carry the same number, so the bars are off by default.
- <kbd>l</kbd> — the tile grid lines.
- <kbd>b</kbd> — turns the arrival buffer off, and back on. The viewer
  normally holds world updates briefly so movement plays back evenly;
  with it off each update draws the moment it arrives, which is for
  driving a world far faster than it runs in production.
- <kbd>d</kbd> — shows or hides the developer group in the footer.
- <kbd>p</kbd> — **worn paths**, currently unavailable: the overlay was
  switched off in 2026-08 because visitors never saw it, so the key does
  nothing. It is left out of the on-page legend for that reason.

An overlay without a button announces itself in the footer while it is
up, so an unusual view never looks broken.
