# Camera mode — design notes

Working notes, not a spec. Written to be argued with before `speckit.specify`
turns it into spec 035.

Sources: kitten.me's camera (`meadow.js` ~735–805, `site.js` 14–30), read
2026-08-16; the owner's calls in session the same day; and the numbers in our
own renderer.

## The idea, in one line

The camera always tries to hold the group at a legible scale, and **following
a cat changes only where it aims**, never how it fits.

That is the owner's call and it collapses what looked like two features into
one. Follow-a-cat and hold-the-group differ by a single value — which cat is
the anchor — so there is one code path, one set of dials, and no handoff
between modes to get wrong.

## How kitten.me's camera works

Three moves, and the third is the one worth stealing.

**Fit.** Bounding box of all cats, plus a 2.6-tile margin. The vertical extent
is corrected by aspect (`fitY × w/h`) so the box fits in both dimensions. The
nominal width is a floor, so a huddled group does not zoom in past comfort.

**Ceiling.** The fit may zoom out only so far — `maxAcross = across × 1.5`.
Past that it stops fitting and lets a wanderer leave the frame. Their comment
is the thesis: *"This is a window, not a map."* On a 24×24 world with cats 15
tiles apart, an uncapped fit makes them 30px specks. They chose a legible cat
over a complete census and let the roster account for whoever is off-screen.

**Anchor.** Once the ceiling binds, the camera needs a point. It uses neither
the bounding-box midpoint nor the centre of mass, because **both are usually
empty ground**. It aims at the cat *nearest* the centre of mass: an occupied
spot, and inside the largest cluster when there is one.

Two details carry the feel:

- **Hysteresis on the anchor.** Keep watching the current cat until another is
  clearly more central — `hd < bd × 2.25`, which is 1.5× in real distance
  since the comparison is squared. Without it, the camera flicks between cats
  at opposite ends of the meadow. Four lines.
- **Nothing ever cuts.** They deleted a "target moved 7+ tiles, snap" rule
  after it fired several times a minute. However far the target jumps, ease.

Easing is frame-rate corrected — `1 - (1-rate)^(dt/16.67)` — because a rate
written per-frame at 60Hz eases twice as fast at 120Hz. Pan eases at 0.06,
zoom at 0.05, so zoom lags the pan slightly. Reduced motion sets the rate to
1: instant, no easing.

## Our numbers

Ours differ enough that theirs cannot be copied across.

| | kitten.me | CloudKitty |
| --- | --- | --- |
| World | 24×24 | 20×20 |
| Cats | 4 | 5 at the phase-1 seating |
| Whole-world view | not offered | the default today |
| Nominal camera width | 12 tiles (8 on phone) | **10 tiles** (owner: 2× zoom) |
| Zoom-out ceiling | 1.5× nominal = 18 tiles | **1.5× nominal = 15 tiles** |

Our map is `tile × 20` CSS pixels, where `tile = floor(min(widthBudget/20,
heightBudget/20, 1200/20))`. Live it lands at **31px**, so the map is about
620px and the binding constraint is the height budget, not `MAP_MAX_PX`.

At 2× zoom the camera shows 10 tiles across the same 620px, so **the tile
becomes about 62px**.

### The ceiling: 1.5× nominal, and the whole world is the *off* state

Owner's call, 2026-08-16: the ceiling is **1.5× nominal**, kitten.me's own
ratio — 15 tiles across, tile ~41px on the live map. And **turning camera
mode off returns the whole-world view**.

That second half is what makes the first half safe. This note had argued for
a whole-world ceiling on a "never worse than today" property; the toggle
delivers that property better, because the whole-world view becomes something
the viewer *chooses* rather than something the camera falls into when the
cats scatter. Camera mode stays a window at all times, the existing render
path stays the off path, and there is no intermediate scale that exists only
as a failure mode.

It also keeps the frame worth looking at. A ceiling at the whole world would
mean one wanderer in a corner silently cancels the zoom for everyone; at 1.5×
the wanderer leaves the frame and the roster accounts for her, which is the
call kitten.me made and the reason their camera feels deliberate.

Our ceiling will bind **more often than theirs**: a tighter world with more
cats, and a tighter ratio band (10–15 tiles, not 12–18). So the anchor path
is the common case, not the fallback, and its hysteresis matters
proportionally more.

## The `fine` threshold is already crossed, and that is good news

A first draft of this note claimed the 62px tile would cross `fine`
(`cat-v2.js`: `const fine = size >= 44`) for the first time, and called it a
hazard: unjudged art switching itself on. **The owner fact-checked it and it
was wrong twice over.**

**The card portraits have always been above it.** `PORTRAIT_CAT` is 47 and is
passed straight to `drawCat` as `size`. Four portraits, every frame, in
production. The comment beside `PORTRAIT_W` says as much: the portrait is
"the one place the fine detail (the tabby stripes, the new eye colour and its
limbal ring) has the pixels to read".

**And the meadow crosses it on large displays.** The tile is
`floor(min(widthBudget/20, heightBudget/20, 60))`, so it varies by viewport:

| display | tile | `fine` |
| --- | ---: | --- |
| laptop, 900px tall | 21–26px | off |
| 1080p | 30–35px | off |
| WQHD 1440 | 48–53px | **on** |
| 4K | 60px (capped by `MAP_MAX_PX`) | **on** |

So the fine detail is not dead code and camera mode is not a frontier. At
62px it brings the meadow to a scale the portraits have been at all along,
and one the meadow itself already reaches on a WQHD monitor. That art has
been looked at, on this project, at this size.

Two consequences for the plan:

- **Camera mode owes no art review for what `fine` reveals.** That work is
  done. It should still be *looked at* in motion, but as confirmation.
- **The tile already varies by a factor of nearly three across viewports**
  (21px to 60px), which is worth holding on to: a camera that recomputes the
  tile per frame is less of a departure than it sounds, because nothing in
  the renderer has ever been entitled to assume a fixed tile.

### One consequence of a fixed ceiling: `fine` can now toggle mid-session

With the band pinned at 10–15 tiles, `fine` is no longer just on or off per
display — on some displays the camera crosses it while running. The canvas
keeps its size; the camera tile is `mapWidth / tilesAcross`, so `fine`
(`size >= 44`) flips at `mapWidth / 44` tiles across:

| display | map | flips at | across the 10–15 band |
| --- | ---: | ---: | --- |
| laptop, 900px tall | 420–520px | 9.5–11.8 tiles | off nearly throughout |
| 1080p | 600–700px | 13.6–15.9 tiles | **crosses mid-band** |
| WQHD 1440 | 960–1060px | 21.8–24 tiles | on throughout |
| 4K | 1200px | 27 tiles | on throughout |

So on a 1080p display the fine detail switches on and off as the group
gathers and scatters. What actually pops is small — in v2 `fine` gates the
tabby forehead stripes (two of the eight palettes), the bowl's fish decal,
and the butterfly antennae. Worth knowing about, not worth pre-solving:
hysteresis on the threshold is four lines if it reads badly, and it may well
not read at all at 44px. Judge it in motion.

Note the 1.5× ceiling *narrows* this compared with a whole-world ceiling,
which would have swept 10–20 tiles and crossed on every display.

What *is* still parked and genuinely unjudged: the ear and eye magnitudes
(head-follow 0.35px, pupil 0.48px at a 31px tile), the parked gaze sources,
the `MENISCUS` dials, and the whiskers. Those were deferred to this moment
and want judging at the camera's scale.

## What the camera changes underneath

Today `tile` is a property of the world and the viewport. With a camera it
becomes an *output of the camera*, recomputed per frame. Everything keyed to
it needs review:

- **The ground cache** is baked at canvas size and invalidated on resize and
  theme change. A per-frame tile invalidates it every frame unless the bake
  is keyed to a quantised scale and the fractional part handled at blit time.
  This is the single largest piece of work in the feature.
- **The pond path cache** is keyed on the water tiles' position signature and
  built at a fixed tile.
- **The drift normaliser is world-size dependent** and solved per world, not
  baked — it must keep seeing the *world*, not the visible window.
- **Sprite depth sorting** is unaffected; it sorts by ground contact in world
  space.
- **`resizeFor` currently derives the tile from the world size.** That
  inverts: the tile comes from the camera, and the canvas stays put.

## Interaction, as decided

- **Click a cat to follow; click again to unfollow.** Tap is the same event,
  so phones get follow for free — no pinch, no pan, no gesture conflict with
  page scrolling.
- **A camera-mode toggle** that follows the group organically, in kitten.me's
  manner. **Off is the whole-world view we ship today** — the same fixed
  tile, no easing, no anchor. Sits **right of the sky dial** on desktop.
  Mobile placement is open; the dial is pinned to the map's top edge with an
  exact `bottom: calc(100% - 16px)` that a previous session already found is
  load-bearing, so anything placed beside it inherits that constraint.
- **Clicking a cat while camera mode is off turns it on.** Assumed, not yet
  confirmed: following without the camera is meaningless, and making the
  viewer flip two controls to follow a cat would be a small cruelty.
  Unfollowing leaves camera mode *on*, holding the group; the toggle is the
  only way back to the whole world.
- **A followed cat is marked on her card**: an indicator around the card plus
  *following* in italics beside or beneath her name. Which of the two
  positions reads better is a layout judgement, to be tried both ways.
- No free pan or zoom. Not ruled out forever; simply not this.

## Settled

- **Zoom-out ceiling: 1.5× nominal.** Off returns the whole world.
- **Sleep needs no special handling.** Owner: sleep is never more than a few
  ticks, and a bored viewer clicks another cat. So following has exactly one
  rule — aim at the followed cat — with no idle timeout, no drift-away, and
  no auto-unfollow. That also means the *anchor* hysteresis is group-mode
  only; a followed cat is the anchor unconditionally.
- **Following does not tighten the frame.** Same nominal width, same
  ceiling; follow moves the anchor and nothing else, so nearby cats stay in
  shot.

## Open questions for the owner

1. **Mobile placement of the camera toggle.** Desktop is settled (right of
   the sky dial). Phone is not, and the dial's exact pin makes the space
   beside it the awkward option.
2. **Does the toggle survive a reload?** The theme toggle persists; this
   could reasonably go either way. If it does persist, the *followed cat*
   probably should not — a cat id is not stable across a world reset.
