# Beam-world screen, tier 3: a planner over the Gen 1 minds, for beams — prereg, 2026-09-20

Declared before collection. Owner's word 2026-09-20: "Let's try the
planner/executor for beams as an extension to the work we're currently
doing on beam sleep." Tier 2 (RESULTS.md, letter (a)) showed the clone
holds the teacher's beam placement in full and β 0.04 PPO removes it on
both the package and the floor5 world. Tier 3 asks the cheapest version
of the planner question: with the served Gen 1 minds unchanged, does one
standing order above them, walk to a known beam before a solo nap,
recover the placement, and at what cost to the rest of the cat's life.
No model is involved; the planner is hand-written. Findings this rests
on: F-042, F-045, F-047, and tier 2.

## The seat

`plan:<slot>` in `fog-gen1-cert/cert_harness_fog.py` wraps `ppo:<slot>`
with `beam_plan.BeamPlanner` (this directory; guard `test_beam_plan.py`
on rows recorded from gen1-A on the package world). The seat's own mind
decides every tick, message head included. The order:

- **Starts** on a tick where the mind picks a solo nap (`SleepSolo`,
  menu 9), the cat is not on a beam and not already asleep, a known
  unoccupied beam sits within reach, and a legal step toward it exists.
  Known = a visible beam slot (the observation's nearest two) or the
  sunbeam memory slot while it is under 20 ticks stale.
- **Executes** as one forced legal move a tick, the one that most
  reduces (Chebyshev, Manhattan) distance to the nearest known beam,
  re-aimed each tick; on arrival, one forced solo nap if legal.
- **Gives up** after 30 ticks in the order, after 3 consecutive ticks
  with no distance-reducing legal move, when no beam is known any more,
  or when eat or drink need reaches 60.
- Parameters: `REACH` 6 tiles (the scripted teacher's priced reach is
  8), `MAX_TICKS` 30, `MAX_STUCK` 3, `MEM_FRESH` 20 ticks, `EMERGENCY`
  0.60. Pinned here; a change is a new tier.

Forcing is a large bonus on one legal index under the harness's masked
argmax, so an illegal forced action falls to the mind's own choice.
Cosleep (`SleepWith`) is never intercepted: the pair's social value and
spec 031's conduction stay the mind's.

## Runs

Two worlds, the planner on all five seats of gen1-A (`--seat
k=plan:<that seat's slot>`), 30 seeds × 20,000 ticks on the shared eval
band, served clock, the beam block and the planner's own counters
(orders, arrivals, give-ups by kind, forced ticks):

- **package** (`package.toml`, tier 2's world): comparator = tier 1's
  gen1-A leg on the same world and seeds (placement 0.068, tick share
  0.063, happiness 92.32, Nash 0.923).
- **served anchor** (`fog-gen1-cert/anchor-b3.toml`, 4 beams, 300
  ticks, floor 5): comparator = tier 1's `s5-b7-t300-n4` gen1-A leg
  (placement 0.046, tick share 0.046, happiness 92.49, Nash 0.925).
  This is what the live world would do with the planner and nothing
  else changed.

Two legs, minutes each. Paired reads on the same seeds.

## Predictions

1. **Placement recovers.** Package: naps begun on a beam ≥ 0.30 (from
   0.068). Anchor: ≥ 0.20 (from 0.046). The teacher under reach 8 sits
   at 0.458 and 0.313; the planner's reach 6, its solo-only trigger and
   the minds' cosleep habit (57–93% of sleeping polls with a friend)
   keep it under the teacher.
2. **The cat's life is otherwise unchanged.** Roster mean happiness
   within 0.3 of the comparator and Nash within 0.005 on each world;
   sleep share within 0.01.
3. **The order mostly completes.** Arrivals ≥ 0.6 of orders; give-ups
   split reported (stuck, long, gone, emergency). Forced ticks under 3%
   of cat-ticks.
4. **No farming.** Share of nap starts under sleep need 5 within 0.05
   of the comparator (the trigger is the mind's own nap decision).
5. **No new distress.** Seeds over age 150 reported by name; the
   prediction is none beyond the comparator's (package 133 max, anchor
   49 max, none over the line).

## Decision rules

- Prediction 1 holding on both worlds is the finding: a standing order
  above a frozen mind recovers what PPO loses, at the welfare cost
  prediction 2 reports. It goes to #390 and the Gen 2 shelf as the
  planner's first number, and to the LLM lab-seat notes as the executor
  baseline a model planner is read against.
- Prediction 1 failing on the package world means the reach-6 window or
  the give-up rules bind; the give-up split says which, and a second
  tier with one parameter moved is the owner's call.
- Prediction 2 failing (happiness down more than 0.3) is reported as
  the walk's price; nothing is tuned to hide it.

## Doctrine check (DESIGN-DOCTRINE.md)

- Rule 2: no price moves; the worlds are tier 1's and the served one.
- Rule 4: the farming read is declared (prediction 4) before the charm
  reading.
- Rule 5: the planner reads the fog view and the legal mask, what the
  mind reads, nothing more.
- Rule 6: the free register is untouched; the message head is the
  mind's.
- Rule 7: this is a behaviour built where the world values it (the
  package world) and read on the served world beside it.
- Rule 9: no frozen mind is asked to answer a reprice; the planner seat
  is a new seat and is read as one (its own battery legs).
- Rules 1, 3, 8, 10: checked, moved nothing.

## Not in this tier

A model in the planner's place; any order other than the beam walk;
intercepting cosleep; a served deployment (owner's word, and a Product
change: the planner would live in the seam or a plugin).
