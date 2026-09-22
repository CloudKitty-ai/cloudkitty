# Handover to Product: the scripted teacher's sleep rule under the floor

Written by Experiments 2026-09-21 on the owner's word ("6 beams, send
the teacher sleep spec to product"). A relay, not a kickoff: the spec
starts when the owner says go in the Product session. BACKLOG.md is
Product's to update when it does.

## The world it serves (owner rulings on #390)

The Gen 2 world package is fully ruled: `actions.sleep_floor_off_beam
= 15` ("Ruled 15", 2026-09-20), beam `ttl` 3,000 and off-beam relief 3
("a) yes, b) yes-3000", 2026-09-18), count 6 ("6 beams", 2026-09-21).
The served world stays at floor 0. The Gen 2 corpus is recorded from
the scripted `needs_driven` teacher on that package world (rule 9 on
the shelf, `fog-gen1-shakeout/GEN2-INPUTS.md`), and this spec is the
prerequisite the shelf names before that recording.

## The problem, measured

Under a floor a plain-tile nap relieves sleep only down to the floor
(`action.rs`, spec 056), and a nap begun at or under it relieves
nothing. `needs_driven` does not read this. Its sleep rule is unchanged
from floor 0: cosleep with a friend if cuddle is real, sleep in place if
on a beam, cosleep beside a warm friend, walk to a beam within
`sunbeam_reach` (priced), otherwise nap on the spot
(`behavior/needs_driven.rs`, the `ReliefSource::Sunbeam` arm). The
sleep score prices the walk (`selection.rs` `sleep_travel_distance`)
but reads the full need as the pressure, never the relief a nap here
would deliver (`scored`).

On the floor-15 package world (beam-world screen tiers 5 and 6, 30
seeds × 20k):

| | floor 0 | floor 15, count 6 |
|---|---|---|
| teacher placement (naps begun on a beam) | 0.458 | 0.341 |
| teacher sleep share of ticks | 0.088 | 0.118 |
| teacher mean sleep need at nap start | 17.8 | 18.5 |
| teacher happiness | 86.9 | 86.2 |

The teacher naps on the spot when no beam is within reach, the nap ends
at the floor after the six-tick minimum, the need regrows past the
threshold, and it naps again. The ground naps dilute its placement
(0.46 → 0.34 at count 6; 0.25 at floor 25) and the corpus teaches that
loop to the clone. Tier 5 read the same loop in the frozen Gen 1 minds
(sleep share up to 0.40 at floor 25). The learned arms escaped it only
through PPO; the Gen 2 clone should not have to.

## The ask

**`needs_driven` reads the floor when it decides whether and where to
sleep.** Two changes, both small, both reading a config key the engine
already validates:

1. **Pressure is the relief a nap would deliver.** In the sleep score,
   when no warm option is in play (not on a beam, no warm friend beside,
   no beam within reach), the pressure term is `max(need − floor, 0)`
   instead of `need`. A nap that would relieve nothing scores nothing
   and loses to whatever else the cat needs; a nap at need 18 scores 3.
   With a warm option reachable the pressure stays the full need, since
   that nap clears it. This is the rule-2 shape: the teacher reads what
   the world pays, no nudge.
2. **The walk is worth more under a floor.** `sunbeam_worth_walking`
   gates on `sunbeam_reach` alone. Under a floor the beam is the only
   tile that clears the need, so the comparison the reach gate stands
   for (a beam nap's extra relief against the walk's cost) has changed.
   Experiments' recommendation is to leave `sunbeam_reach` at 8 and
   change nothing here for the first Gen 2 corpus: the shelf's declared
   pre-PPO read (teacher placement on the new corpus against a ~0.4
   bar) decides whether reach moves, and a corpus under the bar moves
   reach or count before any training. Product may prefer to put the
   floor into the walk's price now; if so the spec should say what the
   reach means under a floor so the read is interpretable.

Out of scope: the cosleep routing (spec 028 FR-020), the warm-friend
rule (T092), the free register, the served world. Nothing deploys; the
served floor is 0 and the rule at floor 0 is byte-identical (the floor
term is zero).

## Acceptance (what Experiments will check on the branch)

- **Floor 0 byte-identical**: the regression pin spec 056 used
  (`actions.sleep_floor_off_beam = 0` leaves every action unchanged on
  the served seeds) holds for the teacher too. The all-scripted cert leg
  on `anchor-b3.toml` must exact-match `kitty-eval --brain
  needs_driven` as before (validation (a) of the 006 protocol).
- **The loop is gone on the floor-15 package world**: the teacher's
  sleep share falls toward its floor-0 value and naps begun at or under
  the floor with no warm option go to zero. Experiments reads it with
  the tier 5 comparator leg (`cert_harness_fog.py scripted eval --config
  shallow-15.toml`, 30 × 20k) beside the numbers above; placement is
  reported, not gated here, since the ~0.4 bar belongs to the corpus
  read.
- **Welfare not worse**: teacher happiness and distress crossings on
  the same leg within the seed spread of today's (86.2, 0 over 150).
- `mutate.sh` red on the new score term (rule 5): a mutation that
  reads `need` instead of `need − floor` must go red on a floor-15
  fixture, and stay green at floor 0.
- Doctrine check (rule 8): rule 2 moves the shape (a state of the
  world, priced); rule 9 is why this precedes the re-record; rule 7's
  worked example (DESIGN-DOCTRINE) gets a line when the corpus read is
  in.
