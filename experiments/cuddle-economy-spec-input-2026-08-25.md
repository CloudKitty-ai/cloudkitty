# The cuddle economy — spec input for review

**2026-08-25. Status: owner-directed brainstorm, consolidated for review.
No decision taken, no dial moved, nothing pre-registered.**

Banked because the reasoning is dense, several intermediate conclusions
were wrong and were corrected mid-thread, and re-deriving it would cost
more than reading it.

---

## TL;DR — the decision to make

`Resting` (actual cuddling) **never runs**: zero scenes in 869 ticks
(owner) and zero in an independent 605-tick census.

The reason is not that rest is mispriced against one competitor. It is
that **the cuddle need is saturated from three directions at once**, and
the weakest of those three already does it alone. Rest is not the
fourth-best route to cuddle; it is a fourth route to an
already-satisfied need.

So the choice is between two packages:

- **Small** — fix the one real asymmetry (§5 lever A) and add rest's
  missing second need (lever B). Cheap, no schema change, defensible on
  principle. **Will probably not clear "non-zero"** while three routes
  saturate cuddle.
- **Real** — the above, plus bringing every cuddle route below
  saturation (levers C and D). This is a **repricing of the whole cuddle
  economy**, touches an incentive the owner says worked well, and needs
  the shared `cuddle_relief` dial split first.

Everything below is the evidence for that framing.

---

## 1. The engine facts

`cuddle_relief` has exactly two call sites (`action.rs:762`, `797-798`):
`Grooming{target}` pays the **groomer**; `Resting{with}` pays **both**.
Co-sleep is priced separately (`cosleep_drip_relief` 3.0 /
`cosleep_mutual_relief` 8.0). Cuddle has **no solo route at all** —
`action.rs:800` says it outright: *"Solo rest is posture, not relief."*

Rest is dominated three ways, and it is **structural, not a pricing
slip**:

1. **Payoff** — mutual co-sleep pays the same 8.0 cuddle to both parties
   **plus** Sleep.
2. **A third route** — grooming a friend pays the groomer cuddle **plus**
   the friend's Bath at `groom_relief` 20.0, the largest social payout in
   the config.
3. **Legality cost** — `Rest{with}` validates on
   `is_conscriptable_friend` (partner must be **free**), while
   `Sleep{with}` and `Groom{target}` use `is_available_friend` and bind
   nobody. **Rest is the only cuddle route that pays F-033's refusal
   tax.**

Because cuddle cannot be serviced alone, the design had to make it
reachable without a willing partner — so cuddle became a rider on the
activities that bind nobody. The domination is a consequence of that
requirement.

## 2. Measured need levels — and a stale constant

Live, 2026-08-25, 50 distinct ticks × 5 seats:

| need | mean | median | p90 | max |
|---|---|---|---|---|
| sleep | 5.0 | 4.2 | 10.6 | **17.1** |
| cuddle | 5.1 | **2.8** | 15.6 | 27.2 |
| play | 5.5 | 4.4 | 12.3 | 20.0 |
| eat | 8.6 | 7.5 | 17.4 | 25.8 |
| drink | 5.3 | 4.0 | 11.6 | 23.2 |
| bath | 4.8 | 3.7 | 10.4 | 22.2 |

⚠ **The config's "mean cuddle need of 11.6" (comment on `cuddle_relief`)
is STALE** — measured 5.1 mean / 2.8 median, roughly half. Every
estimate here was re-derived after that was caught; anything anchored on
11.6 is wrong by ~2×. It invalidated an entire earlier draft (§7).

Note the median cuddle need of **2.8** is low *because* the need is being
saturated — see §3. It is not evidence that cats do not want closeness.

## 3. THE FINDING: cuddle is saturated from three directions

Relief applies **every tick**, clamps at the need, and an activity runs
its `min` regardless. So each route's delivery is
`min(need, rate × min_ticks)`. Against a cuddle need of ~5.1:

| route | capacity over its minimum | saturates? |
|---|---|---|
| co-sleep **passive** drip (3.0 × 6) | 18 | **yes** |
| co-sleep mutual (8.0 × 6) | 48 | **yes** |
| groom a friend (8.0 × 4) | 32 | **yes** |
| *(rest duet, if it ran: 8.0 × 6)* | *48* | *yes* |

Three consequences:

1. **The co-sleep drip/mutual ladder has no behavioural effect at
   current need levels.** Both tiers deliver the entire need. The
   distinction the config carefully documents is inert.
2. **Lowering `cosleep_mutual_relief` alone is a no-op** — not because
   8.0 is too high, but because the 3.0 tier beneath it already
   saturates. Any fix must move **both** tiers.
3. **Grooming saturates it too**, and grooming's cuddle is the *shared*
   `cuddle_relief` field that also pays the rest duet. Lowering
   grooming's saturation lowers rest's payload with it, so **the dial
   must be split before it can be tuned.**

**Non-saturation threshold**: `rate < need / min`. At need ≈ 5.1 that is
**< 0.85/tick** for the 6-tick activities, **< 1.28/tick** for grooming.

## 4. The two arithmetic facts that govern the design space

**(a) Totals are need-bounded, not rate-bounded.** Consequence: the
relief dials are nearly inert over their minimums, and the only
meaningful moves are large ones (§3) or duration changes.

**(b) The crossover.** With cuddle delivered `C`, play delivered `D` and
rest minimum `m`, rest beats mutual co-sleep while the sleep need
`S < 6(C+D)/m − C`. **At equal durations (m = 6) this collapses to
`S < D`** — rest wins exactly when the sleep need is below the play a
rest duet would deliver. No threshold to tune, and **self-correcting**:
if rest crowds out sleeping, `S` rises and co-sleep reclaims the cat.

Measured sleep-need CDF (250 samples), i.e. how often rest would win:

| `D` (delivered play) | drip at m=6 | share of time `S < D` |
|---|---|---|
| 1.0 | 0.17/tick | 30% |
| 1.6 | 0.27/tick | 39% |
| 2.4 | 0.40/tick | 49% |
| 4.0 | 0.67/tick | 64% |

The CDF is static; the self-correction pulls realized share **below**
these. Recommend starting at **0.2–0.3/tick** and measuring — raising it
later is easy.

`Need` is `f32` (`needs.rs:48`), so fractional rates are native; live
values already show sub-integer resolution. NaN is the only guarded case
and config validation rejects it.

## 5. The levers

**A. Cuddle relief for a cat resting beside a sleeping friend.**
Today when A rests and B co-sleeps beside A, **B collects the tier and A
collects 0** — though the config's own principle is *"one price for
'both parties actively resting together' everywhere it happens."*
**This is a symmetry fix, not a repricing.** Keys on adjacency, not
conscription: no refusal tax, binds nobody, no new pinning surface, and
**no observation-schema change** (a neighbour's activity one-hot is
already in `KITTY_SLOT`).

**B. A play drip on rest duets — duet only** (owner's ruling; a sleeping
partner is not playing). The structural fix: it gives rest its **own
second need**, putting it on the same footing as co-sleep (sleep+cuddle)
and grooming (cuddle+bath) rather than handicapping it. Two-tier ladder,
mirroring co-sleep's own shape:

| | pays |
|---|---|
| rest beside a sleeper | cuddle only |
| rest duet, both awake | cuddle + play drip |

**C. Both co-sleep tiers below saturation** (§3). Must preserve tier
order — if mutual goes to 0.5, passive goes under it, e.g. 0.2.
*Owner's caution, and it is the right one*: co-sleep's edge over **solo**
sleep **is** its delivered cuddle. At mutual 0.5 that edge is 3.0
need-units against 5.1 today — 59% of current, meaningfully reduced but
not erased. Some solo sleep appears; owner has said a little is fine.

**D. Split `cuddle_relief`** into a rest-duet dial and a groom-rider
dial, then bring the groom rider below saturation. Prerequisite for
tuning either without moving the other.

**Duration stays near 6.** A modest trim to 4–5 is defensible for the
shorter conscription pin and a snappier read on screen. **Not 2** — see
§7.

## 6. The open risk: what this does to play

The play economy is a deliberately swept corridor —
`solo 10 < duet-each 20 < bug 28 < greeble 35 < team-duet 40` (spec 039,
owner's pre-merge ask, `bugs2-grid2-2026-08-21.md`), ruled *"change
nothing"* when the freeze lifted.

- **At 2–3/tick a play drip is not a trickle — it is a full
  substitute.** Over a 6-tick minimum that is 12–18 capacity against a
  play need of ~5.5, so a rest duet would service play *completely*,
  exactly as a play duet does. Rest duet would then strictly dominate
  play duet (same play, plus cuddle). This is the same stale-constant
  error as §2.
- **The threat to hunting is need exhaustion, not rate competition.**
  Hunting still wins on play-per-tick at any drip considered. But
  Biscuit hunts at 280/1k **because it has a standing play need**; if
  rest keeps play at zero, a bug has nothing to relieve. The seat whose
  certified character is 83% critter play is the most exposed, and that
  character is what exp-006a was built to produce.
- **F-030 is the measured precedent**: when exp-006a shaped social play,
  the policy farmed it and **bug-hunting fell to 0.15× anchor, critter
  proximity to 0.33×**. Different mechanism (training reward vs engine
  economy), same lesson — a cheaper social play route gets paid for out
  of hunting.
- **The config's ladder comment would silently stop describing the
  economy**, since a drip changes effective value without touching any
  rate the comment names. If that corridor moves, it should move
  visibly.

## 7. Explicitly dropped — do not re-derive

- **A true solo-cuddle floor** — owner: solo cuddle does not make sense.
- **Cutting `cuddle` duration to 2** — was the load-bearing lever in an
  earlier draft, and is wrong once lever B exists. It was only
  load-bearing while rest paid a single need; stacking both overshoots
  badly. At min 2 the crossover lands at 23–41 against a sleep need that
  **never exceeded 17.1 in 275 samples** — rest would win 100% of the
  time and co-sleep would become the dead activity instead.
- **A cuddle→sleep relief bonus** — needs a self-block +1 (so it waits
  for the fog wall) and would have to clear **7.5/tick** merely to tie
  co-sleep's 30-in-6, above even the sunbeam rate of 7.0.
- **"2-tick cuddle then 4-tick sleep"** — you cannot beat a parallel
  two-for-one with a serial composition of the same two things. Six
  ticks of co-sleep delivers cuddle + up to 30 sleep; 2+4 delivers
  cuddle + up to 20. Ties below a sleep need of 20, loses above, and
  needs a conscriptable partner for phase one. **Co-sleep already *is*
  cuddle-before-sleep, done in parallel** — which is why rest is empty.
- **Raising `cuddle_relief`** — shared dial (§3); rest only overtakes
  grooming above 20.
- **A one-shot cuddle→sleep bonus as anti-cycling** — re-resting re-arms
  it at no cost. More importantly **F-027 was not reward-driven**: that
  pair cycled for 2,200 decisions with sleep and cuddle already at the
  floor (relief clamping to nearly nothing) while eat and drink sat at
  100. Reward shaping cannot prevent a policy attractor the reward was
  already maximally opposed to. Defend with the parked
  behavioural-collapse detector (ROADMAP parking lot), not with prices.

## 8. Gates before anything moves

- All of it is behaviour economics, so it **rides a retrain**. Levers A
  and B need no schema change, so they need not wait for the fog wall.
- **`tail-benchmarks/family-11-r5` before a roster** — anything touching
  co-sleep, or adding a two-for-one to a conscripting both-pinning
  activity, goes past the known-positive for dyadic lock-in first.
- Spec-first; re-baseline before freeze.
- If the play corridor moves, update the ladder comment in the same PR.

## 9. Separate, not part of this

**Biscuit's welfare gap.** Owner's read: high idle from rejected play is
likely a major culprit, possibly fixable in Biscuit 3.0. F-033 puts the
refused half at 4.6% of its ticks, so the mechanism is plausible — but
that finding deliberately left **the happiness link unmeasured**. Worth
a needs-servicing count per turn before Biscuit 3.0 commits to the
solo-pounce fallback, or you may fix 4.6% of turns and find the welfare
gap barely moves.

---

## 10. Addendum 2026-08-26 — the first-principles reframe and the model

Brainstorm round two reframed the objective as **behavioral diversity**:
every intended activity needs a non-empty *niche* (a region of need-space
where it strictly wins) that the dynamics visit recurrently. Two failure
modes: **empty niche** (rest today — its need-set is a strict subset of
co-sleep's, so no price fixes it) and **absorbing niche** (F-027/F-030 —
the collapse detector's job, not the economy's). Rest's deficits are
three and orthogonal: no unique value (lever B), **no standing demand**
(saturated riders — levers C+D), no access (conscription — lever A /
sibling restructure).

Design rules that fell out: **within each need, one saturating
specialist; every rider partial** (a byproduct priced like the main
product kills the main product — and pointed the other way, this is the
play protection); separate same-need activities by *state*, not price
(grooming's template); volume belongs to `[needs]` rise rates, not
relief dials; solo niches are created by persistent separation, so map
density changes move the mix before relief dials do.

**The need-flow model** (`cuddle-economy-model/needflow.py`, results in
`cuddle-economy-model/RESULTS.md`) validated against the live mix, then
predicted: A+B ≈ no-op (0.3 rest/1k, Small package confirmed dead);
riders-partial alone lifts rest to ~12.5/1k with play essentially
unmoved; **the play drip adds ~0.5/1k — lever B is dropped from the
recommendation**, which removes §6's risk surface entirely. Cost: ~1
happiness point of standing cuddle demand; cert anchors re-derive.
Revised recommendation: **riders-partial (C+D) is the load-bearing
package; the sibling restructure (availability two-tier rest) rides on
F-033's refusal-tax evidence, not the model.**
