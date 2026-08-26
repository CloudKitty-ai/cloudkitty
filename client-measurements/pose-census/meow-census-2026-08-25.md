# Where a served meow lands: 2026-08-25

Nine minutes of the live world, 675 ticks (354,x window), 3,375 cat-ticks,
1,294 polls, 0 fails. Instruments: `meow-census.mjs` + `meow-analyze.mjs`.
Raw is gitignored, as this lane's raws always are.

The question: the owner judged that the extracted meow animation "really only
looks good on idle/walk", and asked what frequency that gate would leave.

## The answer

**40 animated meows per hour roster-wide, one every 1.5 minutes**, if the
animation is gated on walking-or-idle with a visible face.

    meow events                            168
      purrs (drawn as a glyph, never speech) 138
      speech                                  30
    speech landing on walking/idle with a face  6   = 20%

## What the gate costs

    speech by pose   pouncing 11, walking 6, sleep-curl 6, drinking 2,
                     eating 2, grooming 2, grooming-other 1
    speech by view   side 25, front 5, back 0

**Pouncing is the largest bucket and the gate throws all of it away** — 11 of
30, nearly twice walking's 6. If a call reads acceptably on a pounce the
animated rate roughly triples. It is now on the lab card's pose dial for
exactly that reason.

**Idle contributed ZERO.** So "walking or idle" is, in this window, just
"walking". Consistent with F-032: idle ticks are refused-play remnants, and a
cat that has just been refused is not the one asking for food.

No meow was lost to the rear view here (back 0), though a north-bound walk
would be — `paintCat` draws no face on a rear view by design.

## Per cat, and why not to trust it

    Kittybear  18 speech ->  4 animated  (26.7/hr)
    Biscuit     9 speech ->  2 animated  (13.3/hr)
    Pumpkin     2 speech ->  0
    Clementine  1 speech ->  0
    Miso        0 speech ->  0

n=30 is small and this split is noise. Pumpkin measured 2 here against the
94.7 meows/1k Experiments recorded on the same seat in a different window. The
owner's own framing — "the level of verbosity on meows is extremely variable
with model" — is what this table shows. **Trust the roster rate, not a row.**

## The trap this cost

The first analyser returned ZERO and would have been believed. `recent_meows`
is a rolling window: an entry first appears the tick AFTER it was spoken and
lingers about ten, so `worldTick - meowTick` is never 0 and a
`m.tick === w.tick` filter matches nothing. 169 real events read as none.

Straight F-029 — an absent category is not evidence of absence until the
instrument is shown able to emit one. It was caught by checking the raw for
any entry at all before believing the zero, which is the only reason this
record exists.

## Not measured

Whether `Action::Meow` still fires: it cannot. Spec 028 took the meow off the
activity menu, `action::validate` rejects the proposal outright, and a stray
one resolves to Idle. `app.js:1496` still carries a `case 'meow'` for the
action shape, which is now unreachable — reported, not touched.
