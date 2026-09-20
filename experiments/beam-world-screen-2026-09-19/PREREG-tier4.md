# Beam-world screen, tier 4: the friend order — prereg, 2026-09-20

Declared before the legs. Owner's word 2026-09-20: "What if we create a
stronger planner that will trigger when a friend sleeps on a beam
within 3 tiles and preferentially cosleep adjacent as well?", then
"1) agreed, 2) agreed. Since Nash dropped a bit with the current rule,
maybe try dropping to walk up to 5 tiles for solo sleep?" Tier 3
(RESULTS.md) showed the solo beam order completes 91% of the time at no
welfare cost the battery can see and reaches 9% of naps, because most
of these minds' naps are cosleeps. Tier 4 adds the order that reaches
them.

## The seat (`beam_plan.py`, guard `test_beam_plan.py` on rows recorded under the planner)

Two standing orders over the seat's own Gen 1 mind, both gated on the
mind's own nap decision (agreed: no cat sleeps because a friend is
warm), the friend order winning when both apply (agreed):

- **Friend order.** Starts when the mind picks a nap, solo or with
  anyone, the cat is not on a beam and not already asleep, and a
  visible friend is asleep on a beam within `FRIEND_REACH` 3 (Chebyshev;
  read from the friend row's activity and sunbeam bit). Executes as one
  forced legal move a tick that reduces the Manhattan distance to the
  friend (adjacency in the engine is Manhattan 1), re-aimed each tick;
  when the mask says cosleeping with that friend is legal, one forced
  `SleepWith` that friend. Gives up when the friend is no longer asleep
  on a beam, after 3 stalled ticks (no reducing step, or adjacent with
  the cosleep still illegal), after 30 ticks, or on any distress flag.
- **Beam order.** Tier 3's rule with `REACH` lowered 6 → 5 (owner):
  solo nap off a beam, known unoccupied beam within 5, walk, nap.
- **Release on distress flags** (both orders): tier 3 released on eat or
  drink need ≥ 60 and never fired once while two seeds crossed age 150;
  the observation carries the cat's six distress flags, so any flag now
  ends an order. Parameters otherwise tier 3's (`MAX_TICKS` 30,
  `MAX_STUCK` 3, `MEM_FRESH` 20 ticks). Pinned here.

Spec 031 conducts the beam rate to a mutual cosleeper beside a partner
on a beam, so the friend order's cat is warmed without lying on the
beam tile. The headline therefore changes.

## Runs

As tier 3: all five gen1-A seats under `plan:`, package world
(`package.toml`) and served anchor (`fog-gen1-cert/anchor-b3.toml`),
30 seeds × 20k, eval band, served clock. Comparators: tier 1's gen1-A
legs (package: placement 0.068, tick share 0.063, conducted 0.016,
happiness 92.32, Nash 0.923; anchor: 0.046, 0.046, 0.012, 92.49, 0.925)
and tier 3's legs (package: 0.153, 0.144, happiness 92.25, Nash 0.922;
anchor: 0.112, 0.111, 92.39, 0.924).

## Measures

- **Warm share** (headline) = sleeping ticks on a beam plus sleeping
  ticks conducted (off-beam beside a direct partner on a beam), over
  sleeping ticks. The harness's beam block carries both.
- Placement and tick share as before, so tiers 3 and 4 read side by
  side; per seat.
- Welfare, sleep share, start-need bins, distress ages and crossings,
  as before.
- Planner counters per order kind: orders as a share of nap starts,
  arrivals, give-ups (stuck, long, gone), distress releases, forced
  ticks.

## Predictions

1. **Warm share rises past the solo order.** Package: from about 0.17
   (tier 3's 0.144 + conducted) to ≥ 0.30; anchor: from about 0.13 to
   ≥ 0.20. Biscuit's seat, flat under tier 3 (placement 0.028), moves
   most in warm share: ≥ 0.20 on the package world.
2. **Welfare holds.** Roster happiness within 0.3 and Nash within 0.005
   of tier 1's gen1-A on each world. The lower solo reach recovers part
   of tier 3's 0.07–0.10 happiness cost; direction predicted, size not.
3. **Both orders mostly complete.** Arrivals ≥ 0.6 of orders for each
   kind; forced ticks under 3% of cat-ticks.
4. **No farming.** Nap starts under sleep need 5 within 0.05 of the
   comparator (both triggers are the mind's own nap).
5. **Distress.** The flag release fires at least once (tier 3's never
   did); seeds over age 150 reported by name, prediction none beyond
   the comparators' (package max 133, anchor 49).

## Decision rules

- Prediction 1 holding is the finding: two standing orders above the
  frozen minds recover beam-rate sleep for the cosleeping majority; it
  goes to #390, the Gen 2 shelf, and the LLM lab-seat notes as the
  executor baseline.
- A distress crossing at a seat where the friend order fires most is
  reported with that order's counters; nothing is tuned to hide it.
- Any further parameter move is a new tier on the owner's word.

## Doctrine check

As tier 3's, with rule 4 carried by the agreed trigger gate and rule 6
untouched (the message head is the mind's). Rule 3: the friend order
rides on spec 031's conduction, which is the served law, not a new
relief.
