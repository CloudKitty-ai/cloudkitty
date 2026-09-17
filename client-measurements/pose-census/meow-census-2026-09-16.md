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
is cats answering each other — one announces, two or three chorus back.

⚠ **Do NOT attribute this to `reply_intensity_floor`** (Experiments,
2026-09-17, recorded in `fog-gen1-cert/RESULTS.md` §"Meow re-census" at
`81f4c76`). That knob governs the *scripted* reply ladder only, and all five
served seats are policies. The 56% reply share is **learned behaviour**, with
the floor a bystander.

Of the 637 replies, **98% pair with at least one asker** under the engine's
own rule (below), and 457 land exactly one tick after a matching want. These
are tight exchanges, not ambient noise.

⚠ An earlier cut of this census said **49%**, using a ten-tick lookback. The
digest window is **thirty**. The window was the whole error; nothing about
the world changed.

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

---

# Call and response: what a fix would cost, 2026-09-17

Measured against the **real `Camera`**, not a distance proxy: the shipped
`Camera` driven over the banked positions at each viewport width, asking
whether both parties were actually in frame.

Of 131 answered asks in the settled 25-minute window:

|                                              | desktop 1000px | phone 380px |
|---|---|---|
| both cats in the camera frame at reply time  | 48 (37%)       | **20 (15%)** |
| **shows as a pair today**                    | 30 — 63%       | 8 — **40%** |
| + rescue the reply's pose                    | 35 — 73%       | 12 — 60% |
| + rescue the ask via 1-tick lookahead        | **41 — 85%**   | **18 — 90%** |

## The owner's rule, and which half of it is reachable

> Ideally I'd like any call/response where both cats are visible to show. If
> one is silenced due to cooldown or otherwise, both should be.

**"Show both when both are visible" — reachable today.** At reply time the
renderer holds the frame and both positions, so "both visible" is a fact it
has. Rescuing the reply past its pose gate follows. Phone: 40% → 60% of
in-frame pairs.

**"If one is silenced, both are" — not reachable symmetrically.** The ask is
drawn before the reply exists, so suppressing an ask because its reply will
be silenced means knowing the future at ask time.

**Except partly, via the delay line.** `Pacer` holds `paceTargetDepth` and
gives one genuine tick of lookahead — the same mechanism that fixed the wake
stretch in #376. The reply lands on the very next tick in **13 of 20**
in-frame pairs on the phone, so for those the ask's fate IS knowable when the
ask is promoted. Both rescues together reach **90% phone / 85% desktop**.

The residual 10–15% are replies 2–10 ticks later whose ask's pose fails:
genuinely unknowable without the engine.

## How the client should pair a call with its response

**Mirror the engine's answers-me rule.** Experiments confirmed the shape
(2026-09-17), and it is what the minds themselves observe
(`rl/src/observe.rs:610`, spec 049 FR-041):

> For a `reply: true` here_X at tick t from cat S, pair it with **every**
> other cat A whose freshest audible paired want_Y has `tick < t` and
> `t - tick < digest_window_ticks`.

Every field needed is already on `recent_meows` — `kitty_id`, `kind`,
`tick`, `reply` — and the window is served. Drawing this is drawing the
world's own notion of an exchange rather than a client invention.

**It is many-to-one.** One here-word answers 1.20 askers on average; 106 of
637 replies answer two cats and 10 answer three. A pair renderer has to
expect a reply belonging to several asks at once.

Measured on the settled window: **625 of 637 replies (98%)** pair with at
least one asker, giving **751 (ask, reply) pairs in 25 minutes**.

A stronger "this really was a response" signal exists if it is ever wanted,
also from Experiments: the here law is *"referent adjacent OR
reply_condition"* (`meow.rs:237–256`), so a `reply: true` here whose stamped
`pos` is **not adjacent to its referent** was legal *only* because of the
want. Still does not name the asker, but it separates a genuine answer from
an ambient announcement that happened to land while a want was audible.

## What a fix buys, on the corrected pairing

Real `Camera`, both parties actually in frame at reply time:

|                                        | desktop | phone |
|---|---|---|
| pairs with both cats in frame          | 314 (42%) | **174 (23%)** |
| shows as a pair today                  | 194 — 62% | **102 — 59%** |
| + rescue the reply's pose              | 244 — 78% | 132 — 76% |
| + ask rescued via 1-tick lookahead     | 252 — 80% | **140 — 80%** |

So a viewer on a phone already sees ~102 complete pairs per 25 minutes — one
every 15 seconds — and the rescue would take that to 140, a **37% gain**.

⚠ "Shows as a pair" counts both halves drawn, at any gap up to the 30-tick
window. Whether a 24-second gap still *reads* as an exchange is a judgement
nobody has made; the owner has said some delay is fine, but not how much.
Worth settling before building.

## ⚠ REVIEW TRIGGER: half 2, when the PACER buffer gets deeper

**Two different buffers, do not confuse them.** #385 bounded the *meow
record* (`meowSeen`) by age — that is a memory of what has been drawn and has
nothing to do with lookahead. What half 2 needs is the **pacer's delay line**,
`VIEW.camera`-adjacent `paceTargetDepth`, which is what gives the client any
view of the next served state at all.

**Half 2** is the mirror rescue: drawing an *ask* whose pose fails, because a
reply is already visible in the delay line. Ruled 2026-09-17 as NOT BUILT, for
two reasons:

1. At `paceTargetDepth: 1` it reaches only replies landing on the very next
   tick — about **two pairs per 25 minutes** on either viewport.
2. Its justification inverts half 1's. Half 1 says "you already saw the ask,
   so this answer makes sense". Half 2 puts words over a silent cat *before*
   the thing that explains them — the exact failure the pose gate exists to
   prevent, with a weaker excuse.

**Re-open it when the delay line is deeper.** Owner, 2026-09-17: *"Half 2
we'll save for when we have a longer (and free of initial page load latency)
buffer."*

The costing already exists, in `client-measurements/README.md` under the
0.3.0 camera baseline: `paceTargetDepth: 2` closes the lookahead gap
completely (empty-buffer promotions 0.9% → 0.0%) but runs the first ~12
seconds of every page load **17% slow** instead of 10%, because the pacer
fills by *playing slow*. It was declined on that warmup alone.

**So the unlock is not the depth, it is the fill.** The warmup cost is a
page-LOAD problem, not a steady-state one. A pacer seeded at load — buffering
a couple of states before the loop starts, rather than earning depth by
running slow — would make depth 2+ free, and half 2 becomes worth revisiting
at the same time. Nobody has costed that seeding; it is the piece of work
this trigger is really pointing at.

Re-measure half 2's yield on a settled window before building: at depth 2 it
should reach replies 1–2 ticks out rather than 1, and the numbers above are
for depth 1.

## The one ask that is NOT Client's to make

### A camera that knows about conversations

**The dominant loss.** Both cats are in frame for only **23% of pairs on a
phone**. A perfect pair rule still leaves three-quarters of real exchanges
off-screen, because the shot picker has no idea two cats are talking.

Every criterion in spec 038 is about counts and framing; none is about
holding a live exchange. A shot that widened to keep both parties in frame
while one is running would recover more than everything else here combined.
That is a shot-grammar feature, wants a spec, and is judged on screen.

The camera is **healthy on its own criteria** (`client-measurements/
README.md`, the 0.3.0 baseline). This is a new criterion, not a regression.

### WITHDRAWN: "serve the reply's referent"

An earlier draft proposed asking Product to stamp the meow with the want it
answers, on the reasoning that the engine already selects one. **That
reasoning was wrong** (Experiments, 2026-09-17):

- The stamp is *existential* — `reply_condition` is an `.any()` over the
  buffer. It asserts that a matching want was audible; it selects nothing.
- There is no single referent even internally. The scripted ladder
  (`reply_candidate`, `behavior/mod.rs:548`) picks by max **intensity**;
  `freshest_audible` (`meow.rs:491`) picks by max **tick**. Two rules, two
  possible answers.
- All five served seats are **policies**, which pick a here-word off the
  network's message head under `legal_message_mask`. No referent is selected
  at all — the mind just says a legal word.
- The engine's own pairing (the answers-me bits) is derived per **listener**
  and is many-to-one. No engine state records "which".

So serving a referent would be a **new engine rule for Product to spec**,
not an existing selection exposed — and it is unnecessary, because mirroring
answers-me client-side already pairs 98%.
