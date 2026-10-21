# Seating analysis v2 (Gen 2 port) — declaration (2026-10-21)

Authorization: owner, 2026-10-21, verbatim: "Port+fixes approved. Re:
Additions, how can the pile signature distinguish health 3 cat
clustering from unhealthy behavior? Play proposal share, scripted
reference roseter for baseline, and refusals per pair approved
(assuming refusals don't require additional work to surface). I
approve the five-roster rotation as well". Design record:
`../seating-analysis-inputs-2026-09-28.md`; v1 instrument and Gen 1
baseline: `../seating-analysis-2026-09-28/`. Committed before any
rotation data.

Purpose: describe the five-network candidate roster (s1, s2, s4, s6,
s7; deviations entries 4–6) network by network and seat by seat, so
Experiments can propose the seat order that Phase C certifies
(`../gen2-cert-battery-2026-10-20/ROSTER-DECLARATION.md`).
Descriptive under doctrine rule 10: nothing here is a bar.

## Rosters and worlds

- Scripted reference: the comparator roster (every seat the scripted
  teacher). No covered minds.
- `g2-rot1`…`g2-rot5`: a cyclic Latin square, seat order Miso,
  Biscuit, Pumpkin, Kittybear, Clementine. rot1 = s1 s2 s4 s6 s7,
  rot2 = s2 s4 s6 s7 s1, rot3 = s4 s6 s7 s1 s2, rot4 = s6 s7 s1 s2
  s4, rot5 = s7 s1 s2 s4 s6. Every network sits in every seat exactly
  once.
- World `g2leg-20.toml` (the served Gen 2 20×20); seeds 905001–905005
  (the first five worlds of band g2cmp, the same worlds as every Gen 2
  battery row; not a new burn); 20,000 ticks; greedy on both heads; no
  clock input.
- Prerequisite: s6 and s7 finish eligible (plateau or cap) and pass
  Phase B. Otherwise the rotation waits and the question goes to the
  owner.

## Instrument changes from v1

Collector `seating_collect_g2.py`: global-state stride keyed off the
live width (Gen 2's 40, never v1's 32); no clock write (schema 6 has
no clock input); seating and config as inputs, provenance through the
harness; Gen 2 head sizes; plus the chosen-action stream and
all-scripted rosters through the engine's own seats. Message labels
corrected to the engine's HEAD_KINDS (d38a2e95; v1 mislabeled four
want-words; no gated v1 printout changed). Guards: 6 here (the
collector held EQUAL to the certified harness on the same world for a
policy and a scripted roster; the Latin property; play share; holding
on the real s2 trace and an analytic eating case) plus v1's 12;
declared mutate reds confirmed for all seven changes.

## Metrics

v1's eleven families verbatim (`read_leg`, one home), with v1's
conventions: contact ≤ 1 tile, company ≤ 4 (the vision radius at
20×20 under the law). Speech is null for engine-driven seats. Added:

12. **Play-proposal share**: per cat, the share of ticks whose chosen
    action is a PlayKitty proposal (policy seats only).
13. **Distress streak**: per cat, the longest per-(cat, need)
    distress-flag streak, the battery's max_distress_age convention.
14. **Group holding — PROPOSED, enters only on the owner's word before
    any read.** A cat is *held* on a tick when it is in a walk-adjacent
    group of three or more (Manhattan ≤ 1, transitive), its eat or
    drink need is at or above 75 (spec 061's armed line, pinned at the
    Gen 2 freeze), and it is not eating or drinking. Reported: per cat
    the share of time in a 3+ group (character, not a concern), the
    held share, and the longest held stretch; per roster the longest
    stretch with two or more cats held at once. The scripted reference
    gives the healthy baseline on the same worlds.

**Refusals per pair: not included** (her condition). The lab
binding's `survived` flag mixes real refusals with engine rewrites of
a proposal that still applied as the same menu action (measured
2026-10-21 on s1, seed 905001, 1,500 ticks: about 190 partner-play
proposals ended as Idle while more than 700 applied unchanged in the
menu yet read not-survived). Separating them needs the engine's
refusal reasons in the lab binding. Deferred, as in v1.

## Rollup and the seat proposal

Per roster: team happiness (mean and SD over seeds), worst-cat
happiness p5 (mean and SD), worst-cat gap, longest distress streak,
longest shared hold (if 14 enters). Per network × seat cell and per
network across seats.

Proposal rule, fixed now: Experiments proposes ONE of the five
measured rotation rosters (a whole measured composition, never an
unmeasured recombination of cells). (1) Exclude any roster with an
abort, and, if 14 enters, any shared hold of 100 ticks or more. (2)
Rank by worst-cat happiness p5, equity first (her welfare-shape
family). (3) Then team happiness. Differences inside the larger of the
two rosters' per-seed SDs are ties, and ties go to the owner. Phase C
runs on her word.

## Stops and welfare

- `--abort-streak 1000` (the F-053 line) on every world. A roster's
  five worlds run in parallel, so a roster with an abort is reported
  to the owner (nothing of it remains to stop); the other rosters run,
  each its own composition.
- Welfare-cost line: 5 rotation rosters × 5 worlds × 20,000 ticks × 5
  covered minds = 2.5M cat-ticks, plus the scripted reference (no
  covered minds). It buys the seat-order decision on measured
  compositions. Each world is bounded at the line.

## Read

```
cd experiments/seating-analysis-g2-2026-10-21 && VIRTUAL_ENV=/Users/elizabethkelly/ai/cloudkitty/experiments/exp-006-character-gen/.venv /Users/elizabethkelly/ai/cloudkitty/experiments/exp-006-character-gen/.venv/bin/python3 -B seating_read_g2.py --raws results-raw/*/streams-*.npz --out seating-read-g2.json --md
```
