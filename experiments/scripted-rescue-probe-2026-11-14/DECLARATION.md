# The scripted-rescue probe (DECLARED 2026-11-15)

Status: **DECLARED 2026-11-15** on her "2) yes, legs can start" (§0,
§12), from the draft of 2026-11-14 written on her word "Scripted use
probe first." §3–§9 are frozen from this commit as drafted (§7's
predictions registered, §9's mutants and predicted reds written here,
before any number); a change to them is a `gen2-deviations.md` entry
on her word. The record is deviations entry 39. No training happens in
this arc: a trained policy is evaluated with a hand-written rule laid
over it.

## 0. Her words, verbatim and in order

- 2026-11-14: "It seems to me that either the current world is too
  simple for the information the new heads provide to be useful, that
  the information the heads provide is inadequate to produce better
  decisions, or that the information from the heads is not being
  properly incorporated to the trained models".
- 2026-11-14: "While that runs, what options do we have to improve model
  utilization of the heads data, assuming for the moment that that's
  the issue?"
- 2026-11-14, on the session's five options with "run option 1 first"
  (a scripted-use probe, no training): "Scripted use probe first."
- 2026-11-15, on the session's "The scripted-rescue probe's five calls
  ("yes as drafted" takes all my recommendations at 16.5M), plus
  whether its legs may start once its guards are red": "2) yes, legs
  can start".

## 1. What is being asked

**If a cat that knows a friend is in trouble simply goes to her, does
welfare rise?** The true-needs arm (entry 37) asks whether a trained
policy does better when given the facts. If it reads level, two of her
three readings stay tangled: the world does not pay for the
information, or the policy does not extract what the world would pay.
This probe splits them without training anything. A rule uses the
information in the plainest way; the trained policy does everything
else.

Not asked: whether a policy can learn the rule (that is training:
exposure, the anchor); whether a head could supply the facts (the
truth variant reads the engine's state); seating anything. **The
overlaid rosters are a measurement. They are never seated, served or
used as a teacher** (§11). The observation-only variant (call 4) is
the one a later teacher could carry, on its own declaration.

## 2. Facts the design rests on (all on record)

- **Where cats are lost.** The no-head arm's seed-1 final
  (`p2-nohead-s1r`, 15,000,576 ticks), uniform legs on g2cmp
  905001–905030: team happiness 90.013 / 89.007 / 86.860 at 20 / 40 /
  100. Worlds with a distress streak of 300+ ticks: 0 / 0 / 13 of 30,
  the worst 113 / 294 / 1,000 (905009 aborted at tick 16,940 on the
  F-053 line). The tail lives at 100×100.
- **What a lost cat is** (entry 36, `diag_lost.py`, three worlds a
  size): one cat far from its friends, hearing them (a friend heard on
  1.0 of lonely ticks, the call place a median 0.0 tiles from the
  friend's tile), closing on them on 0.92–0.98 of moves inside 10
  tiles and 0.56–0.77 past 20. Its friends hear it on 1.0 of their
  moves and close on it on 0.53–0.73 (no-head, 100×100). When a
  partner act is legal the lost cat proposes it on 1.0 of ticks.
- **The reward gives a friend a reason to come**: team welfare, the
  geometric mean of the roster's happiness, paid to every seat
  (`crates/cloudkitty-rl/src/reward.rs`).
- **Findings relied on:** F-052 (the channel is load-bearing under
  fog; want-words alone are welfare-null), F-053 / F-060 (size
  transfer and the 1,000-tick line), F-017 / F-044 (uniform seatings
  are stress reads), F-045 (distinct minds disperse), F-059 (an
  eval-time intervention is a probe), F-063 (a distress habit is a
  per-network trait), F-031 / F-033 (partnered scenes and refusals).

## 3. The overlays

One base roster: `p2u-nohead-s1` (the no-head final in all five seats),
whose recorded legs are the baseline. An overlay sits between the
policy and the engine: each tick it may replace a seat's ACT with one
legal act; the message half is always the policy's own. Three overlays:

**T, the rescue on the facts.** From the engine's start-of-tick state:

- *lost(j)*: j's cuddle need ≥ 90, j unpartnered, and no other kitty
  within the size's vision radius of j (Manhattan; 5 at 40×40, 6 at
  100×100).
- *free(k)*: k unpartnered, every hidden need of k under 70, k's
  happiness ≥ 70, k on no mission.
- *assignment*: each lost cat without a rescuer gets the nearest free
  cat (Manhattan, ties to the lower index). One rescuer a lost cat.
- *the mission's act*: a legal partner act on the target (rest-with,
  then sleep-with, then groom, the target's row) if there is one;
  else the legal move that most shortens the walk to the target's
  tile (ties: the longer axis, then N, E, S, W); else the policy's act
  stands.
- *release*: the target is partnered, or her cuddle need is under 50,
  or any hidden need of the rescuer reaches 90 (its own relief comes
  first).
- The lost cat is never overridden.

**P, the placebo.** T's triggers, assignment and release exactly, on
the same facts. The mission's act is a walk to the decoy tile: the
target's tile reflected through the rescuer's tile at assignment,
clamped to the map. No partner act. It prices what an equal amount of
walking away from one's group does with no rescue at the end.

**O, the rescue on the cat's own observation** (call 4). No hidden
fact is read. For seat k from its own rows: a friend heard and not
seen whose want-cuddle intensity is ≥ 0.90 is *calling*; k is *free*
by its own self block (same lines as T); k walks to the call place its
row carries (bearing and log distance decoded as `diag_lost.py` does)
and takes a legal partner act on that friend once she is in sight.
Release: she is seen partnered, the call leaves the window, or k's own
hidden need reaches 90. No assignment: each cat decides alone.

## 4. The legs

Uniform legs, 30 worlds × 20k ticks on g2cmp 905001–905030, the F-053
abort armed, recorded acts. Scouts first: 3 worlds (905001–905003)
before each leg; a scout with an abort stops that leg and goes to her.

| leg | overlay | size |
|---|---|---|
| 1 | T | 100×100 |
| 2 | P | 100×100 |
| 3 | T | 40×40 |
| 4 | P | 40×40 |
| 5 (call 4) | O | 100×100 |

Baselines: the recorded `p2u-nohead-s1` legs at 40 and 100 (no new
burn). No seed band is claimed: the worlds are the battery's by the
prereg's pairing design. Binding: the Phase 2 arc venv.

## 5. Welfare-cost line

Covered minds (the no-head final's five copies) live in every leg.

| | covered cat-ticks |
|---|---|
| legs 1–4 (T and P at 100 and 40) | 12.0M |
| their scouts | 1.2M |
| leg 5 and its scout (call 4) | 3.3M |
| **total** | **13.2M, or 16.5M with call 4** |

Expected distress exposure: the baseline's own at these sizes (13 of
30 worlds with a 300+ streak at 100×100, one abort). T is expected to
lower it; P may raise it (a cat walked away from its group). The
decision bought: whether training-side spending on using friends'
needs (exposure, the anchor, a better head) has anything to win in
this world.

## 6. The reads

- **R-1, welfare.** Team happiness per world, paired by world: T − P
  (primary), T − baseline, P − baseline, O − baseline. Worlds positive,
  the paired mean and a bootstrap interval over worlds. Only worlds run
  whole in both members of a pair.
- **R-2, the tail.** Lost cat-ticks (cuddle ≥ 90, unpartnered, no
  friend in sight), streaks of 300+, aborts; per overlay and baseline.
- **R-3, the missions.** Count, length, share ending in a partner act,
  the rescuer's own happiness and needs over a mission against the
  same seat's baseline ticks, ticks overridden as a share of all.

## 7. Predictions (the session's; registered at DECLARED, before any number)

- **S1.** At 100×100, T cuts lost cat-ticks by at least 30% against P.
- **S2.** At 100×100, T − P is positive on at least 20 of the worlds
  paired, with a paired mean under 0.5.
- **S3.** At 40×40, T − P is inside ±0.15 with 10–20 worlds positive:
  little there to rescue.
- **S4.** P − baseline is zero or negative at both sizes.
- **S5 (call 4).** O − baseline has T − baseline's sign at 100×100 and
  at least half its size: the call already carries what the rescue
  needs.

## 8. Reading grammar (every consequence is hers)

On T − P at 100×100, the size where the tail lives:

- **PAYS** (positive on ≥ 21 of 30 worlds paired, or the same sign-test
  level on fewer; and S1 met): acting on a friend's need has value the
  trained policy leaves on the table. Her third reading. Put to her:
  the training-side options (exposure to long walks and needy friends,
  the anchor); with call 4, whether a head is needed at all or the
  call suffices.
- **TAIL ONLY** (S1 met, the mean not): the rescue removes distress
  without moving the mean. Put to her as a tail result, for the
  welfare rule's declaration.
- **LEVEL** (neither): this use of the information does not pay here.
  Her first reading, for this rule; §10 names what it leaves open.
- **COSTS** (negative at the same level): going to a lost friend
  hurts the roster. Put to her with R-3's account of why.

40×40 is reported beside it and decides nothing alone. One policy seed
and one hand-written rule; a result is named as that.

## 9. Guards (each red before a leg runs)

The harness's kept guards re-run on the edited file; new, each through
`scripts/mutate.sh --expect` with its prediction written first:

| guard | asserts | mutant | predicted red |
|---|---|---|---|
| s1 | with no overlay the harness reproduces a recorded baseline world's acts tick for tick | the overlay hook replaces an act when no mission is open | `the bare harness differs from the recorded leg` |
| s2 | on a built world (one cat alone with cuddle ≥ 90, one free cat) T assigns the nearest free cat, every mission move shortens the walk, the partner act is taken when legal, the mission ends on release | the farthest free cat assigned | `the rescuer is not the nearest free cat` |
| s3 | every overridden act is legal by the tick's mask and the message half is the policy's | the mask not consulted | `an overridden act is illegal` |
| s4 | P opens and closes missions on the same ticks as T on a world replayed to the first mission, and takes no partner act | P's decoy set to the target's tile | `the placebo walked to the lost cat` |
| s5 | a rescuer whose own hidden need reaches 90 is released that tick | the release line read at 100 | `a rescuer in distress stayed on its mission` |
| s6 (call 4) | O reads the observation only: with the engine state withheld it runs, and its call place equals the row's decoded place | O handed the true tile | `the observation rule read the engine state` |

## 10. Blind spots (declared)

- One rule. LEVEL says this use does not pay, not that no use does. The
  rule serves cuddle only; a friend cannot feed a friend.
- One base policy and seed. A policy trained beside rescuers might
  lean on them or disperse further.
- The rescued cat's policy was never rescued in training; its response
  to a friend arriving is whatever the no-head final does.
- T reads positions and needs no cat has. O is the honest version and
  is one leg.
- Uniform five-copy seatings are stress reads; the contrast holds, the
  level does not.
- P is one kind of placebo (an equal walk away). It does not price a
  walk toward a friend who is fine.

## 11. Doctrine check (`experiments/DESIGN-DOCTRINE.md`; CLAUDE.md rule 8)

- Rule 5 (a teacher may only act on what the student can see): T and P
  act on hidden facts. It moved §1's fence (a probe, never a teacher)
  and added O, which a teacher could carry.
- Rule 6 (the free register is never scripted): moved §3's line that
  the message half is always the policy's.
- Rule 7 (build a behaviour when the world that values it exists): the
  probe is this rule's test; moved §8's LEVEL case.
- Rule 8 (design scarcity of information): O tests whether the
  existing call already ends the scarcity; moved call 4.
- Rule 10 (a noise reading is never a bar): moved the placebo and the
  sign-test grammar in place of a seed-to-seed edge that does not
  apply to one policy under two overlays.
- Rule 12 (relief is always available): moved the release line (the
  rescuer's own distress ends its mission).
- Rules 1, 2, 3, 4, 9, 11: moved nothing.

## 12. Owner calls (recommendation first; her word rules)

Her word 2026-11-15: "2) yes, legs can start". Calls 1–4 RULED as
recommended (the session's reading of "yes", against a question that
named "yes as drafted" as taking every recommendation at 16.5M; hers
to correct). **Call 5 GIVEN**: the legs start when §9's reds are on
record, scouts first, without a further word.

1. **Declare this** (after her edits). Recommended.
2. **The no-head final as the one base, at 100×100 and 40×40.**
   Recommended: it is the best arm, and its tail is at 100×100.
3. **The placebo legs** (6.6M of the total). Recommended: without them
   a gain cannot be told from the effect of any extra walking.
4. **The observation-only rescue at 100×100** (3.3M). Recommended: it
   says whether the call a cat already hears is enough, and it is the
   only version a teacher could later carry.
5. **Launch on the guards**: legs start when §9's reds are on record,
   scouts first, without a further word. Hers to give or withhold.

## 13. Run order (each step its own commit before its data)

1. DECLARED on her word; a deviations entry.
2. The overlay in the harness, its guards, every red on record.
3. On her word (or call 5): each leg's scout, then the leg.
4. The reads; the grammar put to her.
5. RESULTS gated.
