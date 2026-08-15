# Design brief: the kitty cards

A review request, not a spec. We think the card panel has outgrown the way it
was built and we would like an outside read before it grows again.

## The ask

The cards were built one decision at a time over about six weeks. Each
decision was sound on its own and nobody has ever looked at the whole. A card
now says six things in a chip about 226px wide, and it is about to say a
seventh.

Three questions, in the order we care about them:

1. **What should a card say first?** It currently carries a live portrait, a
   name, a "doing" line, a mood word, a purr lamp, a reserved distress line,
   and (unreleased) a link to that cat's traits. That is a lot of hierarchy
   for a small surface.
2. **Where does depth belong?** We built the traits view as a modal dialog.
   The alternative is the card expanding in place. We are not confident the
   dialog is right, and it is the first dialog on the site, so whatever we do
   sets a precedent.
3. **Should the About card read as a sibling of the kitty cards, or as
   deliberately apart?** We built it apart. That is a judgement worth someone
   second-guessing.

Anything else you see is welcome. These three are what we are stuck on.

## Getting the code

The client is plain scripts with no build step. Serve `client/` over HTTP and
open `index.html`; nothing needs installing. Load order is
`cat.js → cat-v2.js → props.js → meadow.js → render.js → anim.js → app.js`.

| What | Where |
| --- | --- |
| Card markup, built per cat | `client/app.js`, `buildKittyCard` (~line 1054) |
| Panel rebuild and in-place update | `client/app.js`, `renderPanel` (~line 712) |
| Which column a card lands in | `client/app.js`, `placeCards` (~line 790) |
| Card CSS | `client/index.html`, `.kitty-card` (~line 547) |
| Panel markup | `client/index.html`, `<section class="panel">` (~line 936) |
| About card | `client/index.html`, `<aside class="about-card">` (~line 954), CSS ~line 350 |
| Traits dialog markup | `client/index.html`, `<dialog id="traits">` (~line 973), CSS ~line 250 |
| Traits data and dialog | `client/app.js`, `traitsFor` / `openTraitsDialog` (~line 1341) |
| Portrait sizing, and why | `client/app.js`, `PORTRAIT_W` (~line 866) |

Line numbers drift. The names do not.

**To see the unreleased traits view:** press `t`, then use the `traits` link
that appears on each card. It ships off (`TRAITS = { on: 0 }`).

## Constraints you cannot infer from the code

These are the ones that have bitten us. None is precious; all are load
bearing, so if a proposal needs to break one, say so explicitly and we will
weigh it.

- **The map is height-bound.** `resizeFor` subtracts the header and footer
  from the map's height budget, and the tile is `floor(budget / rows)`. At a
  20-row world, about 20px of chrome costs a whole pixel of tile, and a pixel
  of tile is 20px off each edge of the map. Anything that grows the header is
  paid for in map.
- **Collapse is all-or-none.** Clicking any card collapses every card. That is
  the owner's rule, not an implementation accident, and a card that expanded
  alone would break it.
- **The portrait has a floor around 30px.** Below it the ears, eyes and
  stripes stop separating and the cat is a blob. The original 22px version
  died there. It currently draws at 47px, which is the first size where a slow
  blink reads as a blink rather than a smudge.
- **The portrait is a live canvas**, drawn by the same code as the meadow, on
  the same frames. It is not an image and it is not free.
- **The distress line is reserved whether or not it speaks**, so a card that
  has nothing to report still ends in a proper margin. The card's top and
  bottom padding are deliberately uneven because of it.
- **The panel splits across two columns by height** and flanks the map on wide
  screens; below the breakpoint the columns dissolve and the cards wrap under
  the map.
- **Four colour tokens invert across the day.** `--ink`, `--ink-soft`,
  `--patience-ink` and `--card` swap rather than blend at a phase boundary.
  A colour written as a literal is wrong for half the day. Everything reads
  from tokens; please keep it that way.
- **Reduced motion is honoured**, and `body.reduced-motion { transition: none }`
  reaches the body only. Anything with its own transition needs its own rule.

## State of play, so you review the right thing

- **The About card is finished** and its copy is the owner's, verbatim. Layout
  is ours to change; the words are not.
- **The traits dialog is unfinished.** The prose is lorem, and it is waiting
  on end-user-friendly descriptions of the algorithm behind each cat. Please
  review its shape, not its text.
- **The trait numbers are half real.** `config.needs` is the world's baseline
  need-rise rate; `config.kitty[].needs` overrides it for one cat. That is
  already how the engine reads it and how the training side defines a trait
  (`rate / reference_need_rate`). One cat, Pumpkin, has a real +100% eat rate
  today. The other three are placeholders from a table marked for deletion,
  drawn at lower opacity so a stub never reads as a measurement.
- **Traits will not sum to zero.** Do not design anything that implies balance.
- **Camera mode is next for us** and changes the meadow, not the cards: the
  portraits draw at their own size, independent of the map tile. The two do
  not collide.

## How to hand back

Your previous bundles have worked well for us, and the shape we can act on
fastest is the one you used for the animation upgrade: a README that explains
the reasoning, plus either edited source or a spec precise enough to
implement. What we most want is the *why* — the pond-depth handoff's
blurred-silhouette-as-distance-field is the kind of idea we would never have
had, and it arrived because the reasoning came with it.

Two practical notes. We work value-by-value: art constants are judged in
`client/gallery-v2.html` with live dials and pasted back, so numbers you want
us to tune are more useful as dials than as fixed values. And we test the
client headlessly (`node client/test-motion.mjs`, `node client/test-meadow.mjs`),
so anything with a structural claim behind it can be guarded.

If something here is wrong or out of date, tell us. This brief was written
against the repo on 2026-08-15.
