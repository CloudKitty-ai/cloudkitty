# Handover to Product: shallow ground sleep (one world law, one config key)

Written by Experiments 2026-09-20 on the owner's word: "Shallow ground
sounds good. Let's try 10/15/20/25." The spec starts on her word to
Product; this file is the ask and the reasons.

## Why (RESULTS.md §Addendum, tiers 1–4)

A nap runs `[actions.durations] sleep = { min = 6, max = 12 }` and ends
early once the need clears. The served Gen 1 minds begin naps at a
sleep need of 7–9, so six ticks on the ground already clear them; the
beam's higher rate has nothing to relieve, so a beam is worth zero
ticks to these minds, β 0.04 PPO correctly drops the walk to it (tier
2), and a hand-written beam order recovers placement at no welfare
change (tiers 3, 4). For a beam to matter, it must change the outcome
of a nap the cat actually takes. Shallow ground does that at every need
level without touching when or how long cats sleep.

## The law

**Off-beam sleep relieves sleep need only down to a floor; sleep on a
beam, or conducted beside a partner on a beam (spec 031), clears it
fully.** A cat that naps on the ground wakes a little tired, every time;
only a beam gives real rest.

- One config key, proposed `actions.sleep_floor_off_beam` (name is
  Product's), a need level 0–100, default **0** = today's law, so the
  served world and every shipped and frozen toml are unchanged and the
  config sweeps stay green.
- In `apply_sleep_relief` (`action.rs`): when neither `in_sunbeam` nor
  `partner_warm`, the relief never takes sleep need below the floor
  (`max(floor, need − relief)`; a need already under the floor is left
  where it is, never raised).
- **The early-end rule must be settled in the spec.** Today a scene
  ends early once `min` is met and the need is "finished". Off-beam
  under a floor the need never reaches zero, so unless "finished" means
  "at the floor this tile can reach", every ground nap would run to the
  12-tick cap, which is a different law (restless ground) from the one
  asked for. Experiments' reading: finished = no further relief
  possible on this tile.
- Validate: `0 ≤ floor < needs.distress` (90). The floor sits under the
  want-word `announce_threshold` (20) for the 10 and 15 levels and at or
  above it for 20 and 25, which is a consequence to state, not a guard:
  see below.

## Consequences the spec should state

- **Want words.** With a floor ≥ `announce_threshold` (20 served), a
  cat that sleeps on the ground stays armed for `want_sleep` between
  naps, so the meadow's `want_sleep` / `here_sunbeam` traffic rises at
  the 20 and 25 levels (F-049's reply flurry). Under the fog this is
  the channel carrying a real fact (where the rest is), which rule 8
  asks for; it is also a loud meadow. The screen reads meow rates per
  level so the owner can see the trade.
- **Distress.** Floors under 30 sit far below `distress` (90); the
  watchdog is untouched.
- **The scripted teacher.** `needs_driven` walks to a beam within
  `sunbeam_reach` and naps on the spot otherwise; its choice does not
  read relief, so the corpus does not change under a floor. The floor
  acts on the RL reward, which is the point of the test.
- **Client.** Nothing to draw; a cat's need is not shown.

## What Experiments runs on it (PREREG-tier5.md, declared)

Four floors, 10 / 15 / 20 / 25, on the tier 2 package world, PPO from
the existing package clone (no new corpus: the beam-price screen's
design, which isolates the world change), two seeds per floor, eight
arms, one night. Read: the tier 2 swap legs (placement, tick share,
welfare) per floor, plus the scripted teacher and gen1-A on each floor
world for the comparators, plus meow rates per floor. The finding is
whether beam placement survives the fine-tune once the tile changes the
nap's outcome.

## Acceptance (what Experiments will check on the branch)

- A test that a ground nap under a floor leaves the need at the floor,
  a beam nap clears it, a conducted nap clears it, and a need already
  under the floor is not raised; `mutate.sh` reds on each.
- The early-end behaviour under a floor as the spec settles it, tested.
- Default 0 byte-for-byte equivalent: an existing action test or the
  seam check (a pinned seed, action for action) on the served toml.
- One doc line in `cloudkitty.toml`'s `[actions]` comments and the
  key in `/settings`.

## Not asked

No change to durations, thresholds, prices, the teacher, the client or
the wire. No served deploy: the served world keeps floor 0 until the
owner rules otherwise after the screen.
