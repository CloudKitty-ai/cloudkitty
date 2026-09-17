# Meow gates — what the client says out loud, and why

Every filter between a served meow and something a viewer can see, in the
order it runs, with the ruling and the measurement behind each one. Written
2026-09-17, at the end of the density arc that produced #383, #387 and the
nearest-reply branch.

**The point of this file is to make the next re-tune cheap.** Almost every
number below is *roster-bound* — a property of the five fog Gen 1 minds under
`announce_here`, not of the client — so Gen 2 will move them. What should
survive Gen 2 is the *shape*: which gate exists, which dial moves it, and
which rulings are the owner's rather than mine. See
[When Gen 2 lands](#when-gen-2-lands) for the short version.

Companion reading: `pose-census/meow-census-2026-09-16.md` is the measurement
record this file summarises, and `docs/meows.md` is the engine-side field
guide to what the words mean.

---

## The one-line version

A meow is drawn if **`meowIsSpoken(meow, world)`** says so, and then the mouth
and the text each apply their own timing on top. Before 2026-09-17 there was
no such function and the two paths decided separately, which is where every
bug in this arc came from.

---

## The paths

Two, and they are genuinely different code with genuinely different jobs.

| | the **mouth** | the **text** |
|---|---|---|
| entry point | `anim.js` `Presentation.meowFor(id, now, pose)` | `render.js` `WorldRenderer.drawBubbles(world, view)` |
| what it draws | the gape — the cat's jaw opening | the speech bubble |
| how long | 800ms (`meowOpenMs + meowHoldMs + meowCloseMs`) | 3 ticks (`BUBBLE_TICKS`), ~2.4s |
| source | `this.meowAt`, stamped in `pushState` | `world.recent_meows`, read direct |
| per-cat limit | one meow per cat (`meowAt` overwrites) | one bubble per cat (`said`, newest wins) |

**They share exactly one thing: `meowIsSpoken`.** Everything else is
independent, and deliberately so.

> ⚠ **The instrument trap, still live.** A figure computed through one path
> does not describe the other. This has produced a wrong number in this repo
> at least twice — a bubble occupancy computed through `meowFor`'s pipeline
> read 0.90 of five cats when the real figure was 1.89. Before quoting any
> meow number, establish which path it came from.

---

## Gate 0 — the engine, before the client sees anything

Not Client's to tune, but it sets the ceiling for everything below.

- **`announce_here`** (spec 043) decides whether cats emit here-words at all.
  Gate zero in-tree is a standing CI check.
- **`digest_window_ticks`** (30) is how long a meow stays in `recent_meows`.
  The client reads it from `/config` via `anim.setMeowWindow(...)` and falls
  back to `VIEW.meowWindowFallback: 30`. **Never hard-code it.**
- **`recent_window_ticks`** (10) is a **per-cat-per-KIND** cooldown in the
  engine (`Kitty::set_meow_cooldown` keys a map by `MessageKind`). It is *not*
  a per-cat rate limit, and reasoning that treats it as one is wrong — that
  mistake is what made the client's own cooldown floor argue for 8s.
- The **`reply` flag** is served on every meow, and is **existential over the
  30-tick digest window**: it means "some ask this could answer was audible",
  not "this answered that". Measured: of 637 stamped replies, 18% answered an
  ask inside the display window, 20% were losing siblings of one, and **62%
  answered nothing at all**. The client does not trust it alone.

---

## Gate 1 — `meowIsSpoken`: is this worth saying at all?

`anim.js`, and the **only** rule both paths share.

```js
function meowIsSpoken(meow, world) {
  if (meow.kind === 'purr') return false;
  if (!meow.kind.startsWith('here_')) return true;
  return pairedAsksFor(world).map.has(meowKey(meow));
}
```

### 1a. A purr is never speech

Ruled 2026-08-14. A purr is a mood, not something a viewer can act on, and
drawing it as a bubble meant **98% of bubbles said nothing**. It draws as a
glyph instead (`PURR` in `props.js`), keyed on `purring_until` — the *state*,
which runs 9–13 ticks — not on the one-tick meow that announces it.

### 1b. A here-word earns its voice by answering something

Ruled by the owner 2026-09-17: *"Let's drop unpaired entirely for now."*

Here-words are **56% of everything said** on this roster. An unprompted one is
a cat narrating the map — "Here drink!" for the four-hundredth time. The same
words answering "I want to drink!" are a friend helping, and that exchange is
what the fog generation was bred for.

So: **only the chosen answer to an ask is spoken.** Everything else in the
here family is silent — no bubble, and since 2026-09-17, no gape either.

This replaced two narrower cuts, both of which are gone and should not be
re-derived:

- **`reply !== true`** (#383) used the engine's flag as a proxy for "was
  prompted". Too loose — see Gate 0 above.
- **Keeping every stamped reply** put 2–4 simultaneous true answers on screen
  for **54% of answered asks**. All correct, none legible.

---

## Gate 2 — `pairedAsksFor`: which cat gets to answer

`anim.js`. Pure function of `world.recent_meows`, memoised **on the world
object** — never on `world.tick`, because a tick number is not an identity and
the harness builds many distinct worlds at tick 12.

For each ask, at most one reply survives:

- must be a different cat, a matching here-kind (`WANT_FOR_HERE`), and land
  **after** the ask within **`VIEW.meowPairWindowTicks: 7`**
- of those, the **nearest** wins — Chebyshev distance between the two meows'
  own engine-stamped `pos` (where each cat *was when it spoke*, a served fact,
  not an inference)
- ties break to the earlier tick, then the lower id, so the choice is stable
  across frames and across both callers

### Why nearest, not soonest

The owner asked for *"the one closest cat to respond"* and I initially argued
for "soonest visible, fallback nearest" on rescue count. **Her criterion won
on the data.** Of chosen repliers:

| | nearest | soonest |
|---|---|---|
| within 4 tiles | **40%** | 23% |
| within 6 tiles | **57%** | 40% |
| reply still overlaps the ask's bubble | 58% | **67%** |

Soonest wins only on promptness, and the 7-tick pairing window already bounds
lateness — so timing was not the discriminator. Nearest shipped.

**Result:** here-bubbles fall from **1,226/hr to 271/hr**, below the rate of
the asks they answer.

---

## Gate 3 — the pose gate (both paths, one dial)

**`VIEW.meowPoses: ['walking', 'idle', 'pouncing', 'loaf']`** — the poses the
owner judged a call reads on.

- The **mouth** takes the pose it is being drawn at.
- The **text** takes the pose `drawKitty` *actually drew* (`this.drawnPose`),
  not a second `poseFor` call — a copy there would drift.

A call spoken mid-groom is **skipped, never queued**: a call drawn late is a
cat mouthing at nothing.

`loaf` is in the gate and its eyes are already closed, so `meowSquint` is
inert there. That is the owner's intent ("keep eyes closed"), not a gap, and a
test pins it so a future squint change cannot silently open an eye.

### The one deliberate asymmetry: the reply rescue

**Bubbles only.** A reply whose speaker is in an illegal pose still gets its
text, if *all three* of these present-tense facts hold:

1. it is the chosen answer to an ask (Gate 2), and
2. this renderer actually drew that ask's bubble (`bubbleDrawn`), and
3. both cats are in the viewport **now**

The pose gate exists so the client never asserts speech it cannot show; a
reply is the one case where the words are already explained by something the
viewer just watched. There is no gape equivalent, because a pose with no mouth
has no mouth to move.

**The mirror rescue — drawing an ASK because a reply is coming — is
deliberately absent.** It would put words over a silent cat *before* the thing
that explains them, and the delay line only reaches one tick, worth about two
pairs per 25 minutes. See the half-2 review trigger in the census.

---

## Gate 4 — the cooldown (mouth only)

**`VIEW.meowCooldownMs: 1600`**, per cat.

This is an **animation** constraint, not a rate limit: it stops an 800ms gape
re-triggering on top of itself. Its floor is therefore one gape —

```js
assert(V.meowCooldownMs >= V.meowOpenMs + V.meowHoldMs + V.meowCloseMs);
```

— and **not** the engine's `recent_window_ticks`. An earlier version of that
guard argued the engine's window was the floor, on the grounds that a shorter
cooldown "would redraw calls the world itself rate-limits." That premise is
false (see Gate 0): the engine's window is per-cat-per-*kind*, so the world
never emits the same word twice inside it. The floor was re-argued and the
dial moved 8000ms → 1600ms on 2026-09-17.

Two properties, both owner-requested and both pinned by tests:

- **Spent on DRAW, not on hearing.** A call skipped for its pose or silenced
  by Gate 1 costs nothing, and the next real call is free. *(Owner, explicitly,
  2026-09-17: "ensure the suppressed gape+bubble does not consume a cooldown
  as well.")*
- **The verdict is latched.** Gate 1 is asked once, on the first frame, and
  the answer is held on `m.drawn`. The chosen answerer can lose its pairing a
  tick later to a cat replying from closer; a bubble popping out from under a
  cat is ruled acceptable, a mouth snapping shut mid-yawn is not.

### The cooldown is NOT borrowed for the bubble

Ruled 2026-09-16, and the reason is character. Applying it to text flattens
the roster to within 1.26×:

| | Biscuit | Miso |
|---|---|---|
| pose gate alone | 31% of its ticks | 19% |
| gate + cooldown | 11–14% | 11–14% |

> *"The variance is ok, it's charming to have cats with personality, and
> chattiness is a very visible and parseable way to do that."*

---

## What each stage costs

**Bubbles**, 25-minute window, 1,998 speech events, 2026-09-16 (main before
#383 at the top):

    everything                          4,886/hr   37.8% of cat-ticks   1.89 of 5 cats
    non-reply here cut only             3,691/hr   29.4%                1.47
    pose gate only                      3,053/hr   24.9%                1.24
    BOTH (#383)                         2,155/hr   17.7%                0.89
    gate + cooldown (REJECTED)          1,469/hr   13.0%                0.65

**Gapes**, per cat per hour under the pose gate and cooldown, 2026-09-16:

    Biscuit 319/hr (71% of ceiling)   Clementine 281 (62%)   Pumpkin 274 (61%)
    Kittybear 252 (56%)               Miso 230 (51%)

The ceiling is per *cat*, so an evenly-chatty roster spends five ceilings
instead of one. The old pre-fog roster was one loud seat and four quiet ones
(Biscuit drew 29 of 37); all five now sit at 51–71%.

---

## The two-path mismatch, measured

The reason this file exists. Both figures are **cat-frames** — on-screen time,
not events — taken from the live world through the proxy, 120s per run,
hooking `meowFor` and `drawBubble` and correlating per frame.

| | with the cut on text only | after `meowIsSpoken` |
|---|---|---|
| gape **and** bubble | 28.8% | **47.4%** |
| gape, **no** bubble | 27.3% | **0%** |
| bubble, **no** gape | 43.8% | 52.6% |

Put the other way: **48.7% of the frames with a cat's mouth open had no text
over them**, and every one was an unpaired here-word (here_water 760,
here_food 622, here_sunbeam 432, and nothing else at all). That read worse
than the 61%-of-bubbles-over-a-still-mouth it replaced, because a moving mouth
draws the eye harder than text does.

### The residual 52.6% is not a bug

Two structural causes, neither worth fixing:

1. **Duration.** A bubble lasts 3 ticks and a gape 800ms, so even a perfectly
   matched pair spends ~two thirds of its frames as text over a shut mouth.
2. **The reply rescue** (Gate 3), which draws text over a cat whose pose has
   no mouth to move — by design.

Before proposing a fix here, check the figure against those two first.

---

## Every dial, and where it lives

All in `client/anim.js` `VIEW` unless noted. The gallery stand-in in
`gallery-meadow.html` mirrors some of these and a parity test catches
omissions — it has caught two.

| dial | now | what it moves |
|---|---|---|
| `meowPoses` | `walking, idle, pouncing, loaf` | Gate 3, both paths |
| `meowPairWindowTicks` | `7` | Gate 2 — how late an answer can be |
| `meowCooldownMs` | `1600` | Gate 4 — mouth only |
| `meowOpenMs / meowHoldMs / meowCloseMs` | `340 / 260 / 200` | gape shape; their sum is the cooldown's floor |
| `meowSquintByPose` | `{ pouncing: 0 }` | eye narrowing during a gape |
| `meowWindowFallback` | `30` | only if `/config` omits `digest_window_ticks` |
| `bubblePopShare` | `0.35` | share of a tick a fresh bubble spends popping in |
| `BUBBLE_TICKS` (`render.js`) | `3` | how long text stays up |
| `MEOW_TEXT` (`render.js`) | — | the words themselves; owner's copy, **ships verbatim** |

To make the world **quieter**: tighten `meowPairWindowTicks`, or extend Gate 1
to a want-kind. To make it **louder**: the here family is the only large
suppressed population — relax Gate 1b before touching anything else.

---

## When Gen 2 lands

Assume every number above is stale. In order:

1. **Re-run the census.** `client-measurements/pose-census/meow-census.mjs`,
   then `meow-analyze.mjs`. Both rate *and* category mix are roster-bound:
   `here` at 56% of speech is a property of these five minds under
   `announce_here`, not of the client.
2. **Re-check Gate 1b's premise before keeping it.** The whole argument for
   silencing unprompted here-words is that they are 56% of speech and mostly
   noise. If Gen 2 speaks a different mix — fewer here-words, or here-words
   that actually track need — the cut may be wrong rather than merely
   re-tunable. This is the one gate whose *justification* is roster-bound, not
   just its numbers.
3. **Re-measure the two-path split** with the frame-correlation rig (hook
   `meowFor` and `drawBubble`, bucket per frame). Gape-without-bubble should
   stay at 0; anything above that means a path has drifted apart again.
4. **Re-read the cooldown against the new gape rate**, not against the engine.
5. **Re-time `announce_here` questions to Experiments**, not to Client. The
   `here_sunbeam` clustering flag is theirs.

### Measurement gotchas that will bite again

- **Measure client behaviour on the SOCKET.** `/events/activity` is off by a
  tick, which once turned a real 27.2% into a reported 4.1%.
- **`meow-analyze.mjs` hard-codes 800ms in three places** while the server
  serves `world.tick_ms`. Correct today, silently wrong the day that moves.
- **`recent_meows` spans the digest window (30), not the recent window (10).**
  An old comment in `anim.js` said "lingers about ten" and was wrong.
- **`anim.redraw()` hands a STILL view to `onFrame`**, and `anim.rafId` reads
  0 for the whole frame body — neither is usable as a "is this a real frame"
  test.

---

## Open, not resolved

- **Meow sounds.** Queued by the owner behind the density work and not yet
  looked at. `mew` and `chirp` are 33% of speech and the largest remaining
  bubble-only group (1,774 cat-frames in the 120s run). They already gape
  correctly, so the question is purely *what they say*, not when.
- **The icon bubble redesign** — "cuter bubbles with more icons and fewer
  words". Banked in `pose-census/bubble-redesign-2026-09-16.md`. The open
  design question is how to denote *want* vs *here*, and how to depict the
  four sounds; the `drawThought` distress collision has to be resolved first.
- **Half-2 of the pair rescue** — drawing an ask from the delay line — needs a
  deeper, load-seeded pacer buffer before it is worth anything. Review trigger
  is recorded in the census.
