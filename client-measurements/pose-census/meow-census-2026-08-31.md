# Where a served meow lands, after spec 041: 2026-08-31

Twenty-five minutes of the live world, 1,876 ticks (1,107,x window), 9,380
cat-ticks, 0 fails. Instruments: `meow-census.mjs` + `meow-analyze.mjs`. Raw
is gitignored, as this lane's raws always are.

The question, held open since 2026-08-27: `loaf` was added to the meow gate
ahead of the behaviour that would make loafing ordinary. Spec 041 reprices the
cuddle economy, so the floor was expected to move.

**Read on a SETTLED world.** A first cut was taken 17 minutes after the 041
restart and is kept below as a warning, not as a result: it read nearly twice
the truth. The owner's cuddle fix followed, and this window opens 20 minutes
after that, with mean unmet need oscillating 5.3-9.3 against the 6.2 that held
before 041 — a real steady state rather than a world still falling into one.

**The comparison is like-for-like.** The pre-041 figure is not the 40/hr banked
on 2026-08-25: that was computed when the gate was `walking`/`idle` and before
the analyzer modelled the cooldown. Both windows were re-cut with today's
instrument, so the only thing differing is the world.

## The answer

**73 -> 89 animated meows per hour, roster-wide.** One every 41 seconds against
one every 49. A modest move, and much smaller than the transient promised.

                              pre-041 (438k)   settled (1,107k)   [transient]
    cat-ticks                          3,375              9,380         5,340
    speech events                         30                147           295
    per cat-tick                      0.0089             0.0157        0.0552
    landing on a gated pose               17                 73            72
    DRAWN, after the cooldown             11                 37            45
    per hour                            73.3               88.8         189.6

## Rest did not become ordinary

    resting, share of cat-ticks   0.59%  ->  0.64%

That is the headline finding and it is a negative one. The gate entry `loaf`
was a bet that 041 would make loafing common; on the settled world it is where
it was. `loaf` took **3 of 147** speech events, two per cent, against 5 of 295
on the transient. Adding it to the gate bought almost nothing, and the reason
is not that the meow gate is wrong -- it is that the cats still do not rest.

⚠ **Rest was never a true zero.** The standing note said rest was chosen by no
seat, so its census zero was true rather than thin. It was not zero before
041 either: 20 of 3,375 cat-ticks. The instrument could always emit it.

## What DID move, and by how much

`want_cuddle` went from **absent** to 43 of 147 speech events (29%), which is
the repricing speaking: riders went partial, so the need runs higher and the
cats say so. It is the whole of the increase. Everything else is roughly where
it was.

    pre-041 kinds   mew 13, here_water 7, want_eat 5, want_drink 4, want_bath 1
    settled kinds   want_cuddle 43, want_eat 31, mew 27, want_drink 25,
                    here_water 10, want_play 5, here_critter 3, want_bath 2,
                    here_sunbeam 1

## The cooldown is doing real work now

`meowCooldownMs` is 20s per cat, and it drops **36 of 73** eligible calls
(49%), against 6 of 17 (35%) before. The ceiling without it is 175/hr. Biscuit
alone accounts for 29 of the 37 drawn: it is the loudest seat by a wide margin
and the roster rate is not a per-cat rate.

    Biscuit 29 drawn, Kittybear 5, Clementine 2, Pumpkin 1, Miso 0

`pouncing` is the largest gated bucket at 48 of 147 -- more than walking and
idle together -- which is what the 2026-08-25 record predicted when it was
added to the gate.

## The transient reading, kept as a warning

The first cut of this census, 17 minutes after the 041 restart:

    189.6 animated meows per hour, resting 1.55%, want_cuddle 107 of 295

Both figures are about double the settled truth, because the world was still
falling toward its new equilibrium with mean unmet need at 12-21 against a
settled 5.3-9.3. **A census opened inside a deploy transient is not a census.**
The direction was right and the magnitude was wrong by 2x, which is exactly
the error that would have been banked had it merged.

## Instrument fixes made for this run

- `GOOD_POSES` was a literal `['walking', 'idle']` while the shipped gate had
  grown `pouncing` (2026-08-25) and `loaf` (2026-08-27). It scored every meow
  on those two as a miss -- for `loaf`, precisely the question this census
  exists to answer. It now reads `VIEW.meowPoses`. Run against this same raw,
  the stale version reports 15% and 52.8/hr where the truth is 50% and 88.8.
- The analyzer reported only what the gate ADMITS. What a viewer sees is what
  survives the per-cat cooldown, and the two now diverge by half.
