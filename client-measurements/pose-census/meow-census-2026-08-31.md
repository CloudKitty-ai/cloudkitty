# Where a served meow lands, after spec 041: 2026-08-31

Fourteen minutes of the live world, 1,068 ticks (1,092,x window), 5,340
cat-ticks, 1,928 polls, 0 fails. Instruments: `meow-census.mjs` +
`meow-analyze.mjs`. Raw is gitignored, as this lane's raws always are.

The question, held open since 2026-08-27: `loaf` was added to the meow gate
ahead of the behaviour that would make loafing ordinary. Spec 041 reprices
the cuddle economy, so the floor was expected to move. This measures it.

**The comparison is like-for-like.** The pre-041 figure is not the number
banked in the 2026-08-25 record — that was computed when the gate was
`walking`/`idle` and before the analyzer modelled the cooldown. Both windows
below were re-cut with today's instrument, so the only thing that differs is
the world.

## The answer

**73 -> 190 animated meows per hour, roster-wide.** One every 50 seconds,
where it used to be one every 82.

                              pre-041 (438k)   post-041 (1,092k)
    cat-ticks                          3,375               5,340
    speech events                         30                 295
    per cat-tick                      0.0089              0.0552
    landing on a gated pose               17                  72
    DRAWN, after the cooldown             11                  45
    per hour                            73.3               189.6

## It is not the loaf

`loaf` took **5 of 295** speech events. Adding it to the gate bought under
two per cent, and that is the honest answer to the question the gate entry
was betting on.

The floor moved for a different reason. `want_cuddle` went from **absent** to
the largest speech category on the board:

    pre-041 kinds   mew 13, here_water 7, want_eat 5, want_drink 4, want_bath 1
    post-041 kinds  want_cuddle 107, want_eat 60, want_play 52, mew 39,
                    want_drink 26, want_bath 6, here_water 4, here_critter 1

Riders went partial in 041 — co-sleep and the groomer's warmth contribute to
the cuddle need without finishing it — so the need runs high and the cats say
so. The meow animation now fires mostly because cats are asking to be cuddled.

## Two corrections to earlier claims

**Rest was NOT a true zero before.** The standing note said rest was chosen by
no seat, so its census zero was true rather than thin. In this raw it is not
zero: 20 of 3,375 cat-ticks, 0.59%. It rises to 83 of 5,340, 1.55% — a real
increase, and about 2.6x, but from a floor that already existed.

**The old 40/hr figure is not the pre-041 baseline for today's gate.** Re-cut
with the shipped four-pose gate, the same era measures 113/hr before the
cooldown and 73/hr after.

## The cooldown is binding now

`meowCooldownMs` is 20s per cat, and it drops **27 of 72** eligible calls
(38%), against 6 of 17 (35%) before. It was always clipping; it is now
clipping a much larger stream. The per-hour figures above are after it, and
the ceiling without it would be 303/hr.

    Biscuit 26 drawn, Clementine 10, Kittybear 7, Pumpkin 2, Miso 0

## Instrument fixes made for this run

- `GOOD_POSES` was a literal `['walking', 'idle']` while the shipped gate had
  grown `pouncing` (2026-08-25) and `loaf` (2026-08-27). It scored every meow
  on those two as a miss — for `loaf`, precisely the question this census
  exists to answer. It now reads `VIEW.meowPoses`.
- The analyzer reported only what the gate ADMITS. What a viewer sees is what
  survives the per-cat cooldown, and the two diverge exactly when the world
  gets chatty, which is what 041 did. The cooldown is now modelled.

## What this reading is not

The world restarted onto 041 at 22:35 UTC and this window opens 17 minutes
later. It is a post-deploy transient, not a settled state: mean unmet need ran
6.2 before the deploy and oscillated 12-21 across the window, with cuddle
between 22 and 34. The welfare watchdog stayed quiet (threshold 150, no
entries). **Re-cut this when the world has settled** — the direction is not in
doubt, the magnitude is.
