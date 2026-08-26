# The cuddle economy — spec input (2026-08-25)

**Status: owner-directed brainstorm, no decision taken.** Nothing here is
pre-registered and no dial has moved. Written down because the reasoning
is dense, several early conclusions were wrong, and re-deriving it would
cost more than reading it.

## The observation that started it

`Resting` — actual cuddling — **never runs on the live roster.** Zero
scenes in 869 ticks (owner) and zero in an independent 605-tick census
(`live-census-354254.json`: no `rest` in any seat's activity budget, none
in `scene_spans`). Nobody notices cuddling because it does not happen.

## Why: rest is dominated three ways, and it is structural

`cuddle_relief` has exactly two call sites (`action.rs:762`, `797-798`):
`Grooming{target}` pays the **groomer**, `Resting{with}` pays **both**.
Co-sleep is priced separately (`cosleep_drip_relief` 3.0 /
`cosleep_mutual_relief` 8.0). Cuddle has **no solo route at all** —
`action.rs:800` says it outright: *"Solo rest is posture, not relief."*

1. **Payoff**: mutual co-sleep pays the same 8.0 cuddle to both parties
   **plus** Sleep. Strict domination.
2. **A third route**: grooming a friend also pays cuddle (to the groomer)
   **plus** the friend's Bath, at `groom_relief` 20.0 — the largest
   social payout in the config.
3. **Legality cost**: `Rest{with}` validates on
   `is_conscriptable_friend` (the partner must be **free**), while
   `Sleep{with}` and `Groom{target}` use `is_available_friend` and bind
   nobody. Rest is the only cuddle route that pays F-033's refusal tax.

**The domination is forced, not a pricing slip.** Because cuddle cannot
be serviced alone, the design had to make it reachable without a willing
partner — so cuddle became a rider on the two activities that bind
nobody. Repricing treats the symptom.

## Measured need levels — and a stale constant

55 distinct ticks × 5 seats, live, 2026-08-25:

| need | mean | median | p90 | max | % > 23.2 |
|---|---|---|---|---|---|
| sleep | 5.0 | 4.2 | 10.6 | **17.1** | **0%** |
| cuddle | 5.1 | 2.8 | 15.6 | 27.2 | 1% |
| play | 5.5 | 4.4 | 12.3 | 20.0 | 0% |
| eat | 8.6 | 7.5 | 17.4 | 25.8 | 3% |
| drink | 5.3 | 4.0 | 11.6 | 23.2 | 0% |
| bath | 4.8 | 3.7 | 10.4 | 22.2 | 0% |

⚠ **The config's "mean cuddle need of 11.6" (comment on `cuddle_relief`)
is STALE** — measured 5.1 mean / 2.8 median, roughly half. Every
back-of-envelope in this file was re-derived after that was caught.
Anything anchored on 11.6 is wrong by ~2×.

## Two arithmetic facts that govern everything here

**1. Relief clamps at the need, and activities run their `min`
regardless.** So over a minimum-length activity the totals are
**need-bounded, not rate-bounded**. Co-sleep's 6 ticks × 8.0 = 48
capacity against a cuddle need of ~5 is ~10× oversupply. Therefore
**lowering `cosleep_mutual_relief` from 8.0 does nothing** until it falls
below roughly `need / min` ≈ 1. There is no "slight reduction" — it is a
no-op or it is a qualitative change that stops co-sleep servicing cuddle
at all.

**2. The crossover.** With cuddle delivered `C`, play delivered `D`,
rest minimum `m`, rest beats mutual co-sleep while the sleep need
`S < 6(C+D)/m − C`. **At equal durations (m = 6) this collapses to
`S < D`** — rest wins exactly when the sleep need is below the play a
rest would deliver. No threshold to tune, and self-correcting: if rest
crowds out sleeping, `S` rises and co-sleep reclaims the cat.

## The package (three levers)

1. **Cuddle relief for a cat resting beside a sleeping friend.**
   Currently when A rests and B co-sleeps beside A, **B collects the
   mutual 8.0 and A collects 0** — although the config's own principle
   is *"one price for 'both parties actively resting together'
   everywhere it happens."* **This is a symmetry fix, not a repricing.**
   Keys on adjacency, not conscription: no refusal tax, binds nobody, no
   new pinning surface, and **no observation-schema change** (a
   neighbour's activity one-hot is already in `KITTY_SLOT`).
2. **A play drip on rest duets — duet only** (owner's ruling; a sleeping
   partner is not playing). This is the structural fix: it gives rest
   its **own second need**, putting it on the same footing as co-sleep
   (sleep+cuddle) and grooming (cuddle+bath) instead of handicapping it.
   Yields the clean `S < D` relation above. Two-tier ladder, mirroring
   co-sleep's own drip/mutual shape:

   | | pays |
   |---|---|
   | rest beside a sleeper | cuddle only |
   | rest duet, both awake | cuddle + play drip |

3. **`cosleep_mutual_relief` cut — optional, and deep-or-nothing.** See
   fact 1. The deep version (below ~1) makes rest *necessary* rather
   than merely preferred and weakens F-027's two-for-one; it is also a
   real change to an incentive the owner says worked well.

**Duration stays near 6.** An earlier draft made `cuddle` min 6 → 2 the
load-bearing change; that was wrong once lever 2 existed. The cut was
only load-bearing while rest paid a single need, and stacking both
overshoots badly — at min 2 the crossover lands at 23–41 against a sleep
need that **never exceeded 17.1 in 275 samples**, i.e. rest would win
100% of the time and co-sleep would become the dead activity instead. A
modest trim to 4–5 is defensible for the shorter pin and a snappier read
on screen; 2 is not.

## Explicitly dropped (do not re-derive)

- **A true solo-cuddle floor** — owner: solo cuddle does not make sense.
- **A cuddle→sleep relief bonus** — needs a self-block +1 (so it waits
  for the fog wall), and would have to clear **7.5/tick** merely to tie
  co-sleep's 30-in-6, above even the sunbeam rate of 7.0.
- **"2-tick cuddle then 4-tick sleep"** — you cannot beat a parallel
  two-for-one with a serial composition of the same two things. Six
  ticks of co-sleep delivers cuddle + up to 30 sleep; 2+4 delivers
  cuddle + up to 20. Ties below a sleep need of 20, loses above, and
  needs a conscriptable partner for phase one. **Co-sleep already *is*
  cuddle-before-sleep, done in parallel** — which is why rest is empty.
- **Raising `cuddle_relief`** — one field serves both the rest duet
  (both parties) and the groomer's rider (initiator only), so it cannot
  be moved for rest alone without splitting it; and rest only overtakes
  grooming at `cuddle_relief > 20`.
- **A one-shot cuddle→sleep bonus as anti-cycling** — re-resting re-arms
  it at no cost. More importantly, **F-027 was not reward-driven**: that
  pair cycled for 2,200 decisions with sleep and cuddle already at the
  floor (so relief was clamping to nearly nothing) while eat and drink
  sat at 100. Reward shaping cannot prevent a policy attractor the
  reward was already maximally opposed to. Defend with the parked
  behavioural-collapse detector, not with prices.

## The open risk: what this does to play

Lever 2 adds a play source, and the play economy is a deliberately swept
corridor — `solo 10 < duet-each 20 < bug 28 < greeble 35 < team-duet 40`
(spec 039, owner pre-merge ask, `bugs2-grid2-2026-08-21.md`), ruled
"change nothing" when the freeze lifted.

- **At 2–3/tick the drip is not a trickle — it is a full substitute.**
  Over a 6-tick minimum that is 12–18 capacity against a play need of
  ~5.5, so a rest duet would service play *completely*, exactly as a
  play duet does. Rest duet would then strictly dominate play duet
  (same play, plus cuddle).
- **The threat to hunting is need exhaustion, not rate competition.**
  Hunting still wins on play-per-tick at any drip considered. But
  Biscuit hunts at 280/1k **because it has a standing play need**; if
  rest keeps play at zero, there is nothing left for a bug to relieve.
  The seat whose entire certified character is critter play (83% critter
  share) is the one most exposed.
- **F-030 is the measured precedent**: when exp-006a shaped social play,
  the policy farmed it and **bug-hunting fell to 0.15× anchor, critter
  proximity to 0.33×**. Different mechanism (training reward vs engine
  economy), same lesson — a cheaper social play route gets paid for out
  of hunting.
- **Sizing rule that follows**: keep **delivered** play well below the
  play need so rest is a partial top-up. `drip × min < ~2.5` leaves
  headroom; at min 6 that is **≈0.4/tick**, not 2–3. And since
  `S* = D` at equal durations, D doubles as the sleep level below which
  rest wins — pick the share of occasions you want rest to take, and D
  falls out.
- **The config's ladder comment would silently stop describing the
  economy**, since the drip changes effective value without touching any
  rate the comment names.

## Gates before any of this moves

- All of it is behaviour economics, so it **rides a retrain**. Levers 1
  and 2 need no schema change, so they do not have to wait for the fog
  wall.
- **`tail-benchmarks/family-11-r5` before a roster** — anything touching
  co-sleep or adding a two-for-one to a conscripting, both-pinning
  activity goes past the known-positive for dyadic lock-in first.
- Spec-first, and re-baseline before freeze.

## Separate, not part of this

**Biscuit's welfare gap.** Owner's read: high idle from rejected play is
likely a major culprit, possibly fixable in Biscuit 3.0. F-033 puts the
refused half at 4.6% of its ticks, so the mechanism is plausible — but
the finding deliberately left **the happiness link unmeasured**. Worth a
needs-servicing count per turn before Biscuit 3.0 commits to the
solo-pounce fallback, or you may fix 4.6% of turns and find the welfare
gap barely moves.
