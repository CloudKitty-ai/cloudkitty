# Behavioural-collapse detector v0 — results
## (2026-09-01, Experiments; prereg.md + detector.py + guard pinned @ 72ca108 before the first trace was read; 19 exp-006 forensics traces; raw output `results-raw/run-2026-09-01.txt`, uncommitted, reproduced by `python3 detector.py ../exp-006-character-gen/traces/trace-*.npz`)

## Verdict

**v0 VALIDATED** on the prereg's pinned labels: all three MUST-FIRE
traces fire, all eleven MUST-SILENT traces stay silent, the SHOULD-FIRE
trace fires. Two findings the ROADMAP design did not anticipate, both
reported below rather than tuned: the detector fires 48–147 ticks
*after* the watchdog equivalent on every recorded lock (the "fires
earlier" claim does not hold for starving locks at W = D = 200), and
signal (a)'s healthy margin is 0.07, under the prereg's 0.10
knife-edge line.

## Per-trace

| trace | label | verdict | first fire (signal, seat, family, episode) | watchdog eq. | max a / b / c |
|---|---|---|---|---|---|
| candidate-r5-880030 | MUST FIRE (twins, 2,331) | FIRE | 4619 (a, Kittybear, sleeping, 2260) | 4566 | 0.83 / 0.67 / 100 |
| reference-r5-880008 | MUST FIRE (twins, ~500) | FIRE | 1368 (a, Pumpkin, sleeping, 314) | 1221 | 0.82 / 0.64 / 100 |
| candidate-r5-880015 | MUST FIRE (triadic, ~475) | FIRE | 3717 (a, Kittybear, sleeping, 398) | 3669 | 0.82 / 0.38 / 100 |
| solo-s3-e0-880017 | SHOULD FIRE (pile, 435) | FIRE | 591 (a, Pumpkin, sleeping, 438) | 514 | 0.83 / 0.58 / 100 |
| candidate-r5-880001 | MUST SILENT (seed lottery) | silent | — | none | 0.32 / 0.13 / 43 |
| solo-s3-880013 | MUST SILENT (directed travel) | silent | — | **6585** | 0.32 / 0.15 / 82 |
| reference-870005 | MUST SILENT (mda 87) | silent | — | none | 0.35 / 0.20 / 73 |
| candidate-clone-870001 | MUST SILENT | silent | — | none | 0.32 / 0.24 / 48 |
| val-scripted-870001 | MUST SILENT | silent | — | none | 0.23 / 0.19 / 24 |
| solo-s3-e1s1-870001/2/3 | MUST SILENT | silent ×3 | — | none | 0.31–**0.43** / 0.16–0.22 / 23–33 |
| solo-s3-e1s1-swap-870001/2/3 | MUST SILENT | silent ×3 | — | none | 0.30–0.34 / 0.21–0.26 / 17–21 |
| solo-s3-e1s2-870001/2/3 | MUST SILENT | silent ×3 | — | none | 0.30–0.35 / 0.20–0.25 / 21–23 |
| candidate-880013 | REPORT (brief twin events) | silent | — | none | 0.33 / 0.26 / 93 |

Every fire is signal (a) on a sleeping seat; (b) fired on none of the
four positives as the *first* signal and did not fire at all on the
triadic 880015. The discriminating negative held: solo-s3-880013's
watchdog equivalent fires at tick 6,585 on directed travel and the
detector stays at 0.32, which is the case the welfare instrument
cannot separate and this one can.

## Margin (prereg §Margin)

- **(a)**: healthy maximum 0.43 (solo-s3-e1s1-870003, Miso sleeping,
  51 ticks over 0.40 around tick 11,481) against the 0.50 bar; lock
  minimum 0.82. Margin on the silent side is **0.07 — under the 0.10
  line**. The positive side has 0.32 of room. So H4's step-5 pin
  should not inherit ">50% sustained" unexamined: a bar in the 0.55–0.65
  range would keep every positive here and double the healthy margin,
  but that is a v0.1 with its own prereg line, not a change made now.
- **(b)**: healthy maximum 0.26, lock range 0.38–0.67. The bar
  separates twins from health (margin 0.24) but misses the triadic pile
  (0.38): three cats piling means no single pair is mutual more than
  ~40% of the window. (b) is a twin confirmer, not a lock detector.
- **(c)**: 100 on all four positives, but 93 (candidate-880013), 82
  (solo-s3-880013) and 73 (reference-870005) on silent traces. It would
  false-positive on travel and on the brief-twin 20×20 world. Stays
  report-only, as pinned.

Why the lock share is 0.82–0.83 and not F-027's 98%: F-027's number
was the action head's chosen-action share; this is realized activity.
Inside 880030's lock Kittybear spends 1,846 of 2,300 ticks sleeping
partnered and 400 idle unpartnered, the re-entry tick between naps.
Partner is Pumpkin 1,694 ticks and Miso 156, which is why (b) tops out
at 0.67 on a lock that (a) sees at 0.83.

## Latency vs the watchdog

| trace | detector first fire | watchdog eq. | detector later by |
|---|---|---|---|
| 880030 | 4619 | 4566 | 53 |
| 880008 | 1368 | 1221 | 147 |
| 880015 | 3717 | 3669 | 48 |
| 880017 | 591 | 514 | 77 |

The ROADMAP's "fires earlier (needs must starve first)" premise is
wrong for these locks. A trailing-200 share crossing 0.5 needs ~100
ticks of lock, then D = 200 more to sustain: ~300 ticks after onset.
The watchdog needs a distress flag to hold 150 ticks, and in every
recorded lock a need was already in distress within ~120 ticks of
onset (880017's pile began with one already in distress: watchdog 514,
pile from 365). The detector's remaining value is the other two claims: it
names the seat, family and (for twins) the pair, and it would fire on
a welfare-quiet lock. No welfare-quiet lock exists in the trace set,
so that second claim is untested here, not supported.

Fire-and-onset arithmetic checks: 880030's F-027 onset was ~4,300 and
the episode is 2,260 of a 2,331-tick lock; 880017's pile ran 365–800
and the episode is 438.

## Consequences

- **Timeline step 2**: the detector item closes; H4's row gets the
  measured numbers (positives ≥0.82, healthy ≤0.43, bar 0.50, margin
  0.07) and a note that the detector is a namer, not an early warning.
- **ROADMAP parking lot**: v0 done; "fires earlier" struck; v1 = live
  transport off `/world` (activity, partner, needs per tick), a
  transport change only.
- **Gap recorded**: the ROADMAP's "silent across 2.4M cutover-config
  ticks" is not checkable — those runs were not traced. Ten
  cutover-config traces (200k ticks) stand in.
- **Invalidated by**: any change to W, D or the bars (that is v0.1 with
  a prereg line); a new lock class that is not sleeping-with-partner
  (every positive here is); a trace format change in
  `global_state.rs`.

## v0.1: (a) bar 0.65 (owner ruled 2026-09-01; prereg §v0.1 @ f204edc before the re-run)

Raw: `results-raw/run-v01-2026-09-01.txt`, reproduced by the same
command with `SHARE_BAR_A = 0.65`. Guard 6/6 (the mutual-lock pin
repointed 399/499 → 429/439 after going red at 0.65; the two new pins
red at 0.50).

**Prediction missed on one MUST-FIRE.** Eleven MUST-SILENT stay silent
(healthy peak 0.43, margin now 0.22). Three positives fire later, as
predicted: 880015 3717 → 3768 (episode 398 → 297, named seat flips
Kittybear → Pumpkin, the other twin), 880030 4619 → 4673 (2260 → 2146),
880017 591 → 633 (438 → 354). **reference-r5-880008 (twins, MUST FIRE)
goes silent**: its share peaks at 0.82 like the others, but the lock
ramps, and it holds above 0.65 for only 148 (Pumpkin) / 160 (twin)
consecutive ticks, under D = 200. Above 0.50 it held 314.

Bar sweep on the four positives, D = 200 (`first tick / episode`):

| bar | 880015 | 880030 | 880008 | 880017 |
|---|---|---|---|---|
| 0.50 | 3717 / 398 | 4619 / 2260 | 1368 / 314 | 591 / 438 |
| 0.55 | 3735 / 368 | 4643 / 2218 | 1380 / 290 | 609 / 402 |
| 0.58 | 3748 / 348 | 4657 / 2191 | 1387 / 276 | 617 / 387 |
| 0.60 | 3753 / 338 | 4661 / 2176 | silent | 621 / 378 |
| 0.65 | 3768 / 297 | 4673 / 2146 | silent | 633 / 354 |

So the recorded data does constrain the bar from above: 0.58 is the
highest that keeps all four (healthy margin 0.15, lock-side 0.24);
anything ≥ 0.60 drops the ~500-tick twins lock. The premise "the one
scenario we have was well over 50%" holds for the peak, not for the
sustained window: peak and D interact, and the shorter the lock the
lower the bar it needs.

Owner's options, on the record: (i) keep 0.65 and accept that a
ramping ~500-tick twins lock is the watchdog's to catch (H1 fired at
1221 on that trace, 147 ticks ahead of v0's detector anyway); (ii)
0.58, the data's ceiling; (iii) 0.65 with D lowered (160 catches only
one twin, knife edge; not recommended). **detector.py stays at 0.65 as
ruled until the owner says otherwise**; v0.1's verdict is 3/4 positives
(2/3 MUST-FIRE), 11/11 silent, i.e. NOT validated on the prereg's
labels at this bar.
