# Cross-world cost reads — declaration

Declared and run 2026-09-26 on the owner's word ("Yes please,
incorporate all of this into our plan"), from the Professor review
memo `../2026-09-26-free-time-arc.md` findings 2 and 7. Batteries
only; no training; nothing here is a screen with gates — it is the
measurement that puts objective-side and world-side welfare costs on
one footing for the rule-1 discussion.

## Question

F-054's "shaping costs 0.75–1.98 happiness" was measured on the
floor-0 world, where beam-seeking has no welfare function; tier 5's
"shallow ground costs ~1.5 to a mind that has learned it" was
measured on floor worlds. Two numbers, two worlds (memo finding 2).
These legs read both mind families on both worlds.

## Already closed without collection (finding 7)

The memo asked for a β = 0 all-arm leg; it exists — tier 2's pkg
arms' all-arm legs are recorded
(`../beam-world-screen-2026-09-19/results-raw/tier2/battery/pkg-s*/`):
team happiness 91.931 (pkg-s1) / 92.563 (pkg-s2) against gen1-A's
recorded 92.320. The recipe itself is ~free with a ±0.3–0.4
training-seed band; shaped-arm deficits are measured against that
band, not against zero.

## Legs (all 30 × 20,000, eval band 870001, served clock, greedy,
`--abort-streak 1000`, all-arm composition)

1. sg15-s1 and sg15-s2 (tier-5 floor-trained minds) on
   `package.toml` (floor 0) — what the floor-world habit costs where
   the world does not pay it. CERT_ARTS = the beam screen's
   artifacts.
2. The six F-054 shaped arms (hard/cvx/lam × s1/s2) on
   `shallow-15.toml` (floor 15) — what the shaped habit pays where
   the world does pay it. CERT_ARTS = the reward screen's artifacts.
3. gen1-A on `shallow-15.toml` — the unshaped comparator on the
   floor world (the recorded tier-5 sg-arm batteries stay the
   floor-trained reference; not re-run).

## Expectations (reads, not gated predictions)

- sg15 on floor 0: happiness below gen1-A's 92.320 by roughly the
  tier-5 gap if the cost is mind-side (carried habit) rather than
  world-side.
- Shaped arms on floor 15: the beam habit should help where naps
  need beams — deficits vs gen1-A-on-floor-15 expected to shrink
  relative to their floor-0 deficits, most for the hard arms.
- Decision relevance: feeds the rule-1 cost comparison (owner's
  fork) and the Gen 2/3 session; no branch executes from these
  numbers without her word.

## Welfare practice

Eval-only exposure on covered minds; worlds previously run by
covered minds (tier 5 trained and read on the shallow floors; the
package world's history is long) — no scout owed; every leg
`--abort-streak 1000`; expected distress at baseline scale (tier-5
recorded batteries carried no harm-rule events at floor 15). What
the read buys: the one-footing cost comparison before any rule-1
ruling leans on cross-world numbers. Fences untouched (size/rows
only).

## Regeneration

### Collect

`run_legs.sh` (nine legs, sequential, `--workers 4` to stay gentle
beside the stage-A training waves).

### Read

The numbers are the legs' team-happiness means vs the recorded
comparators; read with `read_cross.py --out results-raw/cross-read.json`
(written with the legs; deterministic paths inside).
