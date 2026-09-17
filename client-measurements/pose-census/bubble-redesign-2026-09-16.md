# Icon bubbles: the design state when we paused, 2026-09-16

**PAUSED.** The owner is watching the bubble work land before reopening
this. Shipped since it was written, and worth re-reading against: #383 (the
non-reply `here` cut and the pose gate), #385 (the meow record), #386
(camera mode on by default) and #387 (the reply rescue). None of them touch
the bubble's ART, so everything below still stands — but the *volume* it was
reacting to is lower now, and the redesign should be judged against what
ships today rather than against the 1.89-of-five-cats figure that prompted
it. Everything
below is worked out but nothing is built. Pick up at "Open questions".

## The brainstorm, in the owner's words

Kept close to verbatim, because the reasoning is the part worth re-reading
and several of these are still live options rather than settled decisions.

**The opening move:**

> Cuter bubbles with more icons and fewer words. I think the amount of text
> is part of what seems overwhelming.
>
> Initial thoughts: make our own cute stylized art, that way it reads as
> more of a treat than a chore (enjoy cute cats vs reading lots of text).
> Animations can be simple (static or 2-4 frames) so we can do cel/drawn art
> rather than svg. The big thing to figure out is how to denote want vs.
> here, and how to depict the 4 meow sounds.

**On want vs. here — two proposals, neither yet ruled out:**

> I was thinking an icon for want (cute big eye begging kitty maybe?) and one
> for here: a cat standing in a "pointing" pose and holding out a paw. Then
> we can have icons for food, water, bug, sleep, cuddle, bath, and can convey
> any of those with two icons.
>
> Alternatively we could do a different color/art style bubble for want vs.
> here.

**On sounds — explicitly unresolved:**

> I was thinking each of the sounds could have an artistic rendering, need to
> think that over more though.

**The shape observation that moved the whole design:**

> Bubble can grow. A lot of them are flat and wide, which wouldn't look as
> good as rounder, which also creates space for icons.

**The decision it led to:**

> I think what we're looking at is replacing speech bubbles with thought
> bubbles. I think having three different bubble styles (for want, here,
> sound) will also help make them immediately parseable by type.

## Cel art vs procedural — argued, not settled

The owner's instinct is hand-drawn cel art, few frames, for charm. Two
things argue for staying procedural, and they should be re-examined rather
than assumed:

- **The camera zooms 50–113px per tile.** A raster sprite sheet baked at 3x
  softens at the top of that range; a canvas path scales free. Every other
  overlay in this client is a path for that reason.
- **There is no build step.** Raster means assets under `client/`, which
  rsyncs wholesale to the box and is publicly fetchable — workable, but it
  is a new pipeline (2x/3x variants, versioning) where today there is none.
- **Phase animation is already solved.** `drawHeart` and `drawSleepZs` take
  a `phase`, so the 2–4 frames the owner wants is a pattern props.js
  already uses.

Counter-argument, which is real: the existing icons are hand-drawn-*looking*
but they are still paths, and there is charm in drawn art that paths reach
for and miss. **Suggested resolution: build the first pass procedurally in
the lab card, and if it reads as chore rather than treat, the raster case is
then made with evidence rather than in advance.**

## Why the geometry pushed it that way

**The speech bubble is the only overlay in the client pinned to fixed CSS
pixels** — `height 18`, `font 11px`, `padding 6`. It does not scale with the
tile, so as you zoom in it stays put while the cat grows, and it is
proportionally *largest on a phone*, which is exactly where the text felt
overwhelming.

The **thought bubble already is** what the redesign wants: a circle at
`r = tile * 0.34`, tile-scaled, carrying a `drawNeedIcon` at `r * 1.5`.

    tile  50px (phone)  -> bubble 34px across, icon 25px,   908 px^2
    tile  72px          -> 49px,  icon 37px,              1,883 px^2
    tile 113px (zoomed) -> 77px,  icon 58px,              4,637 px^2

    speech bubble today: 66 x 18 px = 1,184 px^2, FIXED at every zoom
    (frequency-weighted across the kinds actually drawn)

So on a phone an icon bubble is **smaller than today's wide text bar**, and
it grows only when the viewer has chosen to zoom in. **Icons are what make
tile-scaling possible; text is why the current bubble cannot.**

Area arithmetic that killed the two-icon layout at fixed size, kept here
because it stops being binding once the bubble is tile-scaled:

    one 20px icon    32 x 26 =   832 px^2    70% of today
    one 24px icon    36 x 30 = 1,080 px^2    91%
    two 20px icons   56 x 26 = 1,456 px^2   123%
    two 24px icons   64 x 30 = 1,920 px^2   162%

## The art already exists

Every subject is drawn somewhere in the client today, all in one ink weight:

| subject | art | where |
|---|---|---|
| eat / food | bowl, takes a `servings` count | `props.js drawBowl` |
| drink / water | water drop | `props.js drawNeedIcon` |
| sleep | Zs | `props.js drawSleepZs` |
| cuddle | heart | `props.js drawHeart` |
| play | yarn ball | `props.js drawNeedIcon` |
| bath | (a branch of) | `props.js drawNeedIcon` |
| critter / bug | butterfly | `props.js drawButterfly` |
| sunbeam | | `render.js drawSunbeam` |

**The only new art is the three bubble styles, and whatever the sounds get.**
`drawNeedIcon`'s six already cover the six `want_*` kinds exactly, and they
take a `phase`, so the 2–4 frame motion the owner wants is a pattern props.js
already uses. That is also the argument for staying procedural rather than
going to raster cel art: the camera zooms 50–113px per tile and a sprite
sheet softens at the top of that range, while a path scales free — and there
is no build step in this client.

## What each style must carry

    want   19% of bubbles   6 icons   the needy one
    here   50% of bubbles   4 icons   food, water, sunbeam, bug -- the big one
    sound  31% of bubbles   2 served  mew, chirp (trill/ekekek unserved)

Silhouette has to do the work; colour is the second, redundant cue. The
meadow background varies and colour alone fails for colour-blind viewers.

**Sounds are the one category where small size is not a problem.** They are
abstract, so they want abstract marks — a note, a double beat, a squiggle, a
jagged burst — which read at 12px where a cat face does not.

## ⚠ THE CONFLICT TO RESOLVE FIRST

**`drawThought` IS the distress cue.** It fires when a need has gone unmet for
`distressPatienceTicks` (60 ticks, 48s) and shows *that need's icon*. A
`want_eat` meow bubble would show **the same bowl, in the same round bubble,
on the same cat**, meaning almost the same thing: "I have wanted food for a
while" versus "I just asked for food".

They are also placed to coexist — `drawThought` offsets itself `tile * 1.05`
right and `tile * 0.55` up specifically to stay clear of the speech bubble.
Two round bubbles of similar size and style over one cat would read as one
confusing pair.

Three ways out, owner's call:

1. **Merge them.** The distress cue becomes the want bubble's persistent
   form — same icon, held longer or drawn heavier when the wait is long.
2. **Separate hard.** Distress keeps the dotted-trail cloud; wants get a
   different silhouette. Costs a style, keeps "suffering" distinct from
   "spoke".
3. **Drop the distress cue**, on the grounds that a chatty roster says it
   aloud 338 times an hour now. Cheapest and most likely wrong — it exists
   for cats who are *not* speaking.

## Options for want vs. here, all still on the table

Four ways to carry the distinction, in the order they came up:

1. **A second icon** — the begging kitty / pointing paw, beside the subject.
   Explicit and learnable, and the most charming. Costs a whole slot: two
   24px icons is 162% of today's bubble area at fixed size, though that
   constraint largely dissolves once the bubble is tile-scaled. Also
   **redundant on 52% of bubbles** — only food and water are genuinely
   ambiguous between want and here, since sleep/sunbeam and play/critter
   already have different subjects and cuddle/bath have no here-counterpart
   at all. It does real work on the other 48%, which is not a small case.
2. **Bubble colour / art style** (the owner's own alternative). Zero space
   cost, works at any size, read pre-attentively rather than parsed. Weak
   alone — the meadow background varies and colour fails for colour-blind
   viewers — but strong as a second, redundant cue.
3. **The modifier in the tail.** The bubble already draws a tail; make it
   the modifier. A paw points for `here`; the thought bubble trails dots for
   `want`. Keeps the owner's cat-shaped idea, costs *zero* content area, and
   gives the same visual family two different punctuations.
4. **Fill state.** `drawBowl` already takes `servings`: an empty bowl is "I
   want food", a full one is "food is here". Free if the icons carry it, and
   it is the one option that needs no new art at all.

These compose. The likely shape is 3 + 2 (tail plus fill tint) with 4 where
the icon supports it, keeping 1 in reserve if the distinction does not read.

## Three styles: what might distinguish them

Comic convention already maps cleanly onto the three types, which is worth
exploiting because viewers arrive knowing it:

    want   a thought cloud, scalloped and soft   -- a desire, internal
    here   a speech balloon with a pointing tail -- spoken, about the world
    sound  a burst or a small mark cluster       -- a noise, not a statement

Silhouette has to do the work; colour is the second cue. **Sounds are the
one category where small size is not a problem** — they are abstract, so
they want abstract marks (a note, a double beat, a squiggle, a jagged
burst), and those read at 12px where a cat face does not. That also makes
them the cheapest art in the set, which is worth weighing against the
standing argument that they should have no bubble at all.

## Open questions

1. The distress collision above — which of the three.
2. Do sounds get art at all, or does the gape carry them? They are 31% of
   the text and the only category where the bubble repeats what the
   animation already showed.
3. Is the subject vocabulary 6 or 8? The owner listed food, water, bug,
   sleep, cuddle, bath — but `here_sunbeam` is **10% of bubbles**, the third
   most common kind, and a sun is not a Z.
4. Does a `here` bubble show its subject *as found* (full bowl) or does the
   style alone say it?
5. Does the bubble keep a text fallback for an unknown kind? Today an
   unmapped kind renders as `'…'` rather than crashing.

## Build order

1. **A gallery lab card first** — three styles x eight subjects x the zoom
   band, judged at phone scale against a real meadow. That is how every art
   dial in this client has been settled, and it is cheap to throw away.
2. The owner's rulings on the questions above.
3. The renderer change, which is small once the art is decided: `drawBubbles`
   already picks one meow per cat and the icon vocabulary is a lookup.

Numbers throughout come from `meow-census-2026-09-16.md` — read its
instrument warning before quoting any of them.
