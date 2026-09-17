# The meow census after 0.3.0: 2026-09-16

Twenty-five minutes of the served world, 1,875 ticks, **9,375 cat-ticks** —
near-identical to the 2026-08-31 window's 9,380, so the comparison is
like-for-like. Five `fog-gen1-*` seats, vision radius 4,
`announce_threshold` 20, world `--fresh` that morning. Instruments:
`meow-census.mjs` + `meow-analyze.mjs`. Raw is gitignored, as this lane's
raws always are.

This is the re-census the 2026-08-31 report left standing orders for:
*"⚠ RE-VERIFY TRIGGER: re-cut this census after the next generation seats."*

**Read on a settled world**, and settling was demonstrated rather than
declared: mean unmet need oscillated 4.8–9.0 with no trend across twenty
minutes, and an early window (ticks 373–2252) agrees with the banked one
(4003–5880) on group count to 0.01 and roster cohesion to 0.1%.

---

## ⚠ THE INSTRUMENT TRAP. Read this before quoting any number below.

**The gape and the bubble are different code paths and always were.**

- `meowFor` drives the **mouth**. It gates on `VIEW.meowPoses` and spends a
  per-cat `meowCooldownMs`.
- `drawBubbles` draws the **text**. It reads `world.recent_meows` directly.
  No pose gate. No cooldown.

Every bubble figure computed through `meowFor`'s pipeline is wrong, and this
census computed several that way before catching it. Real bubble occupancy
was **1.89 of five cats**, not the 0.90 first reported — more than double.
Check which path a number belongs to before repeating it.

Two more instrument notes:

- `meow-analyze.mjs` hard-codes **800ms in three places** while the server
  serves `world.tick_ms`. Correct today; silently wrong the day that moves.
- `recent_meows` spans the **digest** window (`digest_window_ticks`, 30), not
  the recent window (10). `anim.js` says "lingers about ten" and is wrong.
  Measured: entries linger a median 30 ticks.

---

## The headline: 13.6x more speech

                              2026-08-31      2026-09-16
    cat-ticks                      9,380           9,375
    speech events                    147           1,998
    per cat-tick                  0.0157           0.213
    per 1,000 decisions               16             213

Lab prior for comparison (Experiments, `fog-gen1-cert/RESULTS.md` §Rule 10):
the lesson arms ran 278–361 meows per 1,000 decisions plus 128–151
here-words, against 152–156 on the no-lesson arms. The served roster lands
inside that prior.

**The owner's framing, which matters more than the number:** 88.8/hr — the
pre-fog drawn rate — is **not** a healthy baseline to restore. It was too
sparse, and more organic communication is what fog was *for*. Do not anchor
on it.

## By category

    here    1,135   56%   here_water 427, here_food 403, here_sunbeam 172, here_critter 133
    sound     682   33%   mew 350, chirp 315
    want      219   11%   want_eat 60, want_drink 56, want_cuddle 55,
                          want_bath 21, want_sleep 19, want_play 6
    purr      226         (a glyph since 2026-08-14, never a bubble)

## `reply` is served on every meow, and the client ignored it

    here    56% reply (637 of 1,135)
              here_sunbeam 65%, here_food 64%, here_water 57%, here_critter 21%
    want     0% reply
    sound    0% reply
    purr     0% reply

**Nothing but a here-word is ever a reply.** More than half the `here` volume
is cats answering each other — one announces, two or three chorus back. That
is `announce_here` and `reply_intensity_floor 0.20` doing what 0.3.0 seated
them to do, and it is why `here` is 56% of all speech.

Of the 637 replies, **49% follow the matching `want_*` from another cat**
within ten ticks (`here_food` after `want_eat`, and so on), and 457 of 637
land exactly **one tick** after the thing they answer. These are tight
exchanges, not ambient noise.

`intensity` is served too, and is **0.0 on every single here-word** while
wants run 0.2–0.4. So intensity cannot rank here-words against each other,
but it does cleanly separate an ask from an announcement.

## Per cat, and why the spread is protected

Drawn calls per hour under the gape's own gate and cooldown:

    Biscuit 319/hr (71% of the 450/hr ceiling)   Clementine 281 (62%)
    Pumpkin 274 (61%)   Kittybear 252 (56%)   Miso 230 (51%)

The old roster was one loud seat and four quiet ones — Biscuit drew 29 of 37.
**All five now sit at 51–71% of ceiling.** The ceiling is per *cat*, so an
evenly-chatty roster spends five ceilings instead of one.

---

## What shipped (#383)

Owner's rulings, 2026-09-16:

1. **An unprompted here-word gets no bubble; a REPLY keeps one.** "A cat
   announcing they want food and a friend saying 'food is here, friend!'"
2. **A bubble only where the mouth can move** — `VIEW.meowPoses`, gating on
   the pose `drawKitty` actually drew, not a second `poseFor` call.
3. **The gape's cooldown is NOT borrowed for the bubble.** It exists so an
   800ms gape cannot re-trigger on itself; applied to text it also flattens
   the roster to within 1.26x. Gate alone leaves Biscuit at 31% of its ticks
   against Miso's 19%; gate plus cooldown puts every cat at 11–14%. The
   variation is character — *"charming to have cats with personality, and
   chattiness is a very visible and parseable way to do that."*

Text over a cat: **37.8% of cat-ticks → 17.7%**, from 1.89 of five cats
carrying a bubble at any instant to 0.89.

What each stage costs, all measured on this window:

    everything (main before #383)        4,886/hr   37.8%   1.89 of 5
    non-reply here cut only              3,691/hr   29.4%   1.47
    pose gate only                       3,053/hr   24.9%   1.24
    BOTH (what #383 ships)               2,155/hr   17.7%   0.89
    gate + cooldown (rejected)           1,469/hr   13.0%   0.65

## Rejected, with numbers, so nobody re-derives them

**Rate limits — DISCARDED (owner), do not re-propose unless she raises it.**
A per-cat limit on *sounds* saturates at 8s (roster 2,155 → 1,954/hr; 10s and
12s add ~1% more) because sound bursts are tight. A per-cat limit on *all*
bubbles reaches 1,212/hr at 8s but compresses the spread from 2.18x to 1.58x.

**`BUBBLE_TICKS` dwell — considered and dropped.** The bubble lasts 2,400ms
against the gape's 800ms, so dwell is a real lever on occupancy; but for the
call/response legibility it was reached for, delay between the two bubbles
is acceptable (owner), so it buys little.

---

## Call/response visibility — TABLED for later investigation

**93% of answerable asks get answered.** The world does this constantly. A
complete exchange reaching a viewer is much rarer:

    asks that CAN be answered (eat/drink/sleep/play)   141    338/hr
      ...that got at least one reply                   131    314/hr   93%
      ...where the ASK is drawn                        101    242/hr
      ...and a REPLY is drawn too                       90    216/hr   one every 17s
         both cats in one frame, desktop                57             one every 26s
         both cats in one frame, PHONE                  42             one every 36s

Where it goes:

- **78 of 219 wants can never be answered at all.** `want_cuddle` and
  `want_bath` have no `here_*` counterpart in the vocabulary.
- The **pose gate** silences ~41 of 131 exchanges. That is the price of
  ruling 2 above, and this is where it lands.
- The **camera** costs ~48 more — both cats in one frame only 54% of the
  time on a phone. This is the largest single loss, and no camera criterion
  has ever measured "both parties to a conversation in shot".

**The owner's proposed fix, for when the ring buffer lands:** allow a
call/response PAIR through even where one or both ends fail pose
eligibility. The gate exists so the client never asserts speech it cannot
show; in a pair the viewer has already seen one end, so the other is
contextualised rather than unexplained. Nothing else here is clean.

---

## Standing re-verify trigger

Re-cut after the next roster seats, as 2026-08-31 said and this census
honoured. Both the rate and the category mix are **roster-bound**: `here` at
56% of speech is a property of these five minds under `announce_here`, not
of the client.
