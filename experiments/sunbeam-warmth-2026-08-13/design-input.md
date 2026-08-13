# Design input: shared sunbeam warmth (owner request, 2026-08-13)

**The ask (Elizabeth, for Product to spec):** when cosleeping partners
share a pile and either one's tile holds a sunbeam, BOTH receive the
sunbeam sleep-relief rate. One rule, no new elements, no geometry
change — it makes the sunbeam a placement target for the cosleep
behavior the world already loves, instead of a competitor to it.

## The facts that motivate it (probe 2026-08-13, committed here)

`sunbeam_probe.py`, all-policy e004-a1-s2 ×4, served config, seeds
820001–005 × 6,000 ticks = 120,000 kitty-ticks:

- Sleeping is 21.8% of all decisions — 19.1% cosleep, 2.7% solo.
  Cosleep dominates 7:1.
- Sleeping-in-sunbeam is **0.15%** of kitty-ticks (185 ticks), and
  145 of those are cosleeps that happen to overlap a beam tile by
  accident. Effectively zero deliberate use.
- The scripted demonstrators DO seek sunbeams (`needs_driven`'s
  sunbeam walk rule), so the behavior was in the BC data; RL
  optimized it away — rationally: a solo sunbeam nap pays Sleep 8,
  a mutual cosleep pays Sleep 5 + Cuddle 8 to each of two cats, and
  Cuddle has almost no other relief channel.

## The rule (three pins, suggested answers)

1. **Conduction**: the sunbeam rate applies to a sleeper when its
   tile holds a sunbeam (today's rule) OR its **direct cosleep
   partner** is in the pile — same mutual definition as spec 028
   FR-014/FR-015 (partner Sleeping or Resting) — on a sunbeam tile.
   Direct partner only: no chaining through a third cat.
2. **Symmetry, no stacking**: either-on-beam → both at the sunbeam
   rate; two beams is still just the sunbeam rate.
3. **One dial**: reuse `sleep_relief_sunbeam` as the shared rate —
   one number meaning "sunbeam-grade sleep." (An asymmetric
   beam-cat/partner split is expressible but adds a second dial to
   justify; not requested.)

## The dial value: screen {6, 7, 8}, owner's opening preference 7

Estimated per-nap effect (rise ≈ 0.3/tick, solo relief 5):

| rate | partner net drain | partner nap vs solo-rate | beam-cat nap vs today's 8 |
|---|---|---|---|
| 8 | 7.7 | ≈ −39% | unchanged |
| 7 | 6.7 | ≈ −30% | ≈ +15% longer |
| 6 | 5.7 | ≈ −18% | ≈ +35% longer |

The trade is steering gradient (+3/+2/+1 per tick per cat over
off-beam cosleep) against dwell (shorter naps at higher rates — the
relief-dial paradox: throughput buys choice, not lingering). Screen
with scripted probes at all three (world-tuning-screens pattern,
F-016 discipline: measure the channels, don't assume the dial's
aim), read welfare + cosleep-on-beam dwell, let the numbers pick.

## Scope and safety notes

- **Engine-rules change only.** No observation schema change (the
  policy sees sunbeam positions and partner positions in schema 3
  already; steering piles onto beams is derivable geometry) — so no
  §4 warm-start voiding rides along.
- **Scripted decision paths untouched**: `sunbeam_worth_walking` is
  distance-gated (`sunbeam_reach`), not relief-derived — instruments
  keep their behavior; only their welfare rates shift where the rule
  fires. Re-baseline before the next generation's family freeze, as
  the pipeline order already requires.
- **Negligible effect on the live world**: the deployed policies are
  frozen and won't seek the bonus; the 145 accidental overlap ticks
  start paying the partner, which is noise. The payoff arrives with
  the next trained generation — for which the relational bind
  (sunbeam token ↔ partner token) is exactly the shape the entity-
  attention architecture handles natively.
- Constitution-safe: relief only ever increases; no cost, no new
  need pressure.

## Registered expectations (to check when the next generation trains)

- Cosleep-on-beam becomes a deliberate, measurable behavior (census
  needs a small extension: sunbeam positions alongside the existing
  position/cosleep tracking).
- Prediction worth watching for, not gating: a cat that finds a beam
  and calls its partner over (the FollowMe "I'm coming" word running
  in reverse — "come here" pragmatics) would be the emergent-behavior
  jackpot; the channel machinery for it exists.

## Explicitly parked (recorded, NOT requested)

A situational happiness term ("sun-warmth": happiness bonus while
sleeping/resting in a beam) — the dwell knob the relief dial cannot
be. It touches the happiness function itself (first non-need input to
the welfare currency; couples to purr legality via happiness_rose),
so it is its own decision with its own screen, only if shared relief
alone leaves sunny piles too brisk on screen.
