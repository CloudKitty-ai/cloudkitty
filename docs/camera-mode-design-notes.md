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
| Zoom-out ceiling | 1.5× nominal = 18 tiles | **open** — see below |

Our map is `tile × 20` CSS pixels, where `tile = floor(min(widthBudget/20,
heightBudget/20, 1200/20))`. Live it lands at **31px**, so the map is about
620px and the binding constraint is the height budget, not `MAP_MAX_PX`.

At 2× zoom the camera shows 10 tiles across the same 620px, so **the tile
becomes about 62px**.

### The ceiling is the one number still open

The owner set the *zoom* at 2× and asked to revisit once it is live. The
*zoom-out ceiling* is a separate dial and this note recommends leaving it
until then too, but the shape matters now because it decides how often the
anchor path runs:

- **Ceiling at 1.5× nominal** (kitten.me's ratio) = 15 tiles across, tile
  ~41px. Below the `fine` threshold — see the hazard below.
- **Ceiling at the whole world** = 20 tiles, tile 31px, i.e. the camera can
  always fall back to exactly the view we ship today. Tidy, and it means
  camera mode never shows the viewer anything less than the current default.

The second is more attractive than it first looks: it makes camera mode a
*strict improvement* on the existing view, with the whole-world view as its
own floor. It also means a scattered group degrades to something already
judged and shipped, rather than to a new intermediate scale nobody has seen.

Our ceiling will bind **more often than theirs**: a tighter world with more
cats. So the anchor path is the common case, not the fallback, and its
hysteresis matters proportionally more.

## The hazard nobody has looked at yet

**At a 62px tile the cats cross the `fine` threshold** (`cat-v2.js`: `const
fine = size >= 44`). That gate has never once been true in production — the
whole-world tile has always been below it. Crossing it switches on the tabby
forehead stripes and the bowl's fish decal, which are effectively **dead code
that has never been seen live**.

That is mostly upside: it is detail already paid for. But it is unjudged at
this scale, and it arrives automatically rather than by choice. Camera mode
should treat "what `fine` turns on" as art to be reviewed, not as a free win.

The same applies to everything parked behind camera mode: the ear and eye
magnitudes (head-follow 0.35px and pupil 0.48px at the current tile), the
parked gaze sources, the `MENISCUS` dials, and the whiskers. All of them were
deferred *to* this moment and all of them want judging at 62px.

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
  manner. Sits **right of the sky dial** on desktop. Mobile placement is
  open; the dial is pinned to the map's top edge with an exact `bottom:
  calc(100% - 16px)` that a previous session already found is load-bearing,
  so anything placed beside it inherits that constraint.
- **A followed cat is marked on her card**: an indicator around the card plus
  *following* in italics beside or beneath her name. Which of the two
  positions reads better is a layout judgement, to be tried both ways.
- No free pan or zoom. Not ruled out forever; simply not this.

## Open questions for the owner

1. **The zoom-out ceiling** — 1.5× nominal, or the whole world? This note
   leans to the whole world, for the "never worse than today" property.
2. **What does following do when the followed cat sleeps for 200 ticks?**
   Nothing, presumably — but a camera locked on a curled cat for three
   minutes is a different experience from one that drifts.
3. **Does the toggle survive a reload?** The theme toggle persists; this
   could reasonably go either way.
4. **Does following imply a tighter frame?** The owner's call is that seeing
   nearby cats is a benefit even when following, which is why follow only
   moves the anchor. Worth confirming that also means follow uses the *same*
   nominal width, with no extra zoom-in on the subject.
