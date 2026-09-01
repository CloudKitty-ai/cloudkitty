# Waterline contagion: shelved for Gen 1
## (2026-09-01, owner ruling after the water's-edge smoke; Experiments' record of the discussion)

**Ruling: no contagion for Gen 1.** Supersedes the 2026-08-30 ruling
(contagion IN at factor 1.0, flip after the 041 soak). Specs 044 and
045 stay in tree inert; nothing deploys; the step-4 membership call is
closed without a decision because the question no longer applies to
Gen 1. F-035 becomes Gen 2 pricing input.

## Served state at the ruling (read off the box, not memory)

`/opt/cloudkitty/cloudkitty.toml` has no `[water]` section and the
cloudkitty unit's journal contains no "waterline contagion" boot line.
The served binary predates 044 (last deploy = PR #332, the
`groom_cuddle_relief` bump, before 044 merged at 74537e4). The next
deploy will carry 044/045 code with the charge disabled by default;
the boot log must then read "waterline contagion disabled". That line
is the verification, every deploy.

## What the smoke established (F-035, `edge-avoidance-smoke-2026-09-01/`)

Scripted `needs_driven` seats in every arm; this was forced, not
chosen. The charge-aware ladder is a dial on the chooser, and the
served roster's policies are frozen networks that never saw the charge
(the legality mask does not feed observations). Only the scripted
chooser has a value function that can be made charge-aware today.

1. Unseen, the charge is a magnet. Cross-waterline adjacency 6.61%
   (no charge) → 11.84% (blind, factor 1.0) → 13.70% (blind, 10×). The
   charge raises bath need; bath relief is in the water.
2. Seen, it is a fence. The aware ladder lands 7.66% / 8.07% at 1.0
   and 4.84% at 10×, under half its drift-matched blind twin.
3. Membership is behaviorally irrelevant at 1.0: |option_a −
   bidirectional| = 0.41 pp, no consistent per-seed ordering; the play
   reciprocity prediction (C ≈ D) held.
4. Serving the aware ladder has a cost: groom pair-ticks collapse
   1,893 → 527 down the aware arms, and C/D each show one low
   Clementine happiness sample (77.4 / 68.5). Groom-decline is her
   known sensitive channel (the 041 futile-loop population).

## The discussion

**Two learning vectors, one priced.** Learning could handle wetness
two ways: dry cats avoiding the shoreline, or wet cats keeping away
from dry friends. Only the first is priced. Under both shipped
membership rules the wet member pays occupancy only, never contagion
(spec 045 acceptance #4, membership-independent). "Bidirectional"
widens which DRY cats pay (the dry cat referenced by a wet cat's
activity, not only the one naming a wet partner); it never charges the
wet side. No cat in the current economy has an incentive to keep its
wetness away from a dry friend, so no learner can discover one. The
smoke could not have seen a wet-side effect regardless: adjacency is
symmetric and the raws do not record who named whom. The indirect path
(dry cats decline wet partners, so a wet cat gets refused more) teaches
"dry off first" or "seek wet partners", not "protect the dry cat".
Pricing the wet side would be a THIRD membership option with its own
needflow pass; wet cats already carry occupancy and the two banked
tables do not cover stacking contagion on them.

**Why shelve rather than flip.**

- A Gen 1 learner cannot see a wet neighbour. The neighbour-in-water
  observation float is the piece that "wants the wall" and is out of
  Gen 1 scope. Trained under an armed charge, Gen 1 would live in arm
  B's world: bath rises for no visible reason, go to water, get wet,
  spread it. The smoke says that is a magnet. A price the payer cannot
  see trains the wrong lesson.
- The only chooser that can see it is the aware ladder, and teaching
  from it or serving it carries item 4 above. Not a thing to fold into
  a shakeout round whose purpose is fog.
- Half the mechanism is unpriced (the wet-side vector). Shipping the
  existing half would set Gen 1's baseline around an incomplete rule,
  to be repriced under Gen 2 anyway.
- It costs nothing on the schema lock. 044/045 are config dials with no
  observation change; the flip stays available to Gen 2 without a
  wall.

**Sunk work is banked, not lost.** 044/045 code and guards stay in
tree inert (750+ tests, stamp and golden unmoved). F-035, the needflow
tables (Option A + bidirectional, both economies), the smoke driver
and instrument extensions, and the boxed-cat backlog item are all
reusable when contagion reopens.

## What changes on the timeline (`fog-gen1-timeline-2026-08-26.md`)

- Step 2: the smoke's outcome recorded as ruling input; Biscuit 3.0's
  comfort sweep loses its last pre-fog engine-change blocker and can
  run once the owner calls the 041+bump soak.
- Step 3: waterline contagion OUT for Gen 1 (was IN). The
  neighbour-in-water float and the scene-age float still wait for the
  wall, unchanged.
- Step 3.5: the v2.10 train shortens to soak verdict → refusal-stamp
  fast-follow → tag. No flip deploy, no second soak.
- Step 4: the bidirectional decision point closes. The post-flip
  `waterline_exposure.py` sanity pass is dropped; the pre-flip baseline
  (on-water 3.02%, cross-adjacency 6.20%) stays banked as a reference.
- Step 5: the edge-behavior watch item under fog is dropped.

## Reopen trigger (both, Gen 2 items)

1. The neighbour-in-water observation float ships, so a learner can
   see the thing it is being charged for.
2. The wet-side membership question is priced (third option, needflow
   pass), so the rule being trained under is the whole rule.

At reopen: F-035 stands as pricing input only if the charge formula,
ladder value shape, and E_ticks bounds are unchanged; otherwise the
smoke reruns (its prereg, driver, and configs are committed).

## Plumbing the wet-side vector needs (owner asked 2026-09-01)

For a wet learner to understand the price of interacting with a dry
friend, three pieces, the first being the hard one.

1. **An incentive that can be collected.** The wet member is exempt
   today, so there is nothing to learn. The obvious third membership
   option (charge the wet cat's bath for pairing with a dry friend) has
   a collection problem: the wet cat already pays occupancy and sits
   near the bath ceiling, and the ceiling gate zeroes any charge at bath
   ≥ ceiling (045's "never price what can't be collected"). A wet-side
   bath charge prices at zero for exactly the soaked cat it should
   deter. Alternatives, each needing its own needflow pass and a
   `validate_water`-style budget: land it on a different need (cuddle
   or happiness, stretching the wet-fur semantics), or a prosocial
   reward term (the partner's bath delta enters the actor's training
   reward). The reward term has no served surface, so it is invisible
   to the watchdog and the census and shapes only learners, never
   scripted seats. Price-not-law stands either way; the legality funnel
   and mask do not move.
2. **Observability.** Half exists: the self block carries a
   tile-derived in-water flag (schema 2,
   `crates/cloudkitty-rl/src/observe.rs`), so a wet learner knows it is
   wet. The other half is the neighbour-in-water float on `KITTY_SLOT`
   (wall-gated; reopen trigger 1). One float serves both directions: a
   dry cat reads a wet neighbour as 1, a wet cat reads a dry neighbour
   as 0. Without it, dryness is only inferable by comparing a
   neighbour's relative position against the water slots, too weak to
   learn from.
3. **A teacher that does it.** BC clones imitate the scripted chooser,
   and 045's aware ladder prices only the dry side's seams (selection,
   play_score, groom-decline, cosleep pick). A wet-side seam is needed
   (wet groomer declines a dry groomee, wet cat skips a dry cosleep
   pick) or the corpus carries no wet-side avoidance to copy, and the
   clones inherit the teacher's blindness however the reward is shaped.

Mitigating fact: wetness is wet-now, tile-derived, no timer. A wet cat
that wants a dry friend just steps out first, so any wet-side price
mostly teaches "leave the pond before you groom", which is likely the
behavior wanted anyway.
