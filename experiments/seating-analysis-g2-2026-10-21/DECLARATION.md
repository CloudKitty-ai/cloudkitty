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
want-words; no gated v1 printout changed). Guards: 4 here (the
collector held EQUAL to the certified harness on the same world for a
policy and a scripted roster; the Latin property; play share) plus
v1's 12, with declared mutate reds confirmed for the stride, the
clock write, the play set, the rotation and the label table. (The
holding guards moved with the metric to the certification side.)

## Metrics

v1's eleven families verbatim (`read_leg`, one home), with v1's
conventions: contact ≤ 1 tile, company ≤ 4 (the vision radius at
20×20 under the law). Speech is null for engine-driven seats. Added:

12. **Play-proposal share**: per cat, the share of ticks whose chosen
    action is a PlayKitty proposal (policy seats only).
13. **Distress streak**: per cat, the longest per-(cat, need)
    distress-flag streak, the battery's max_distress_age convention.
Group holding is NOT in this analysis. Owner, 2026-10-21, verbatim:
"That's a great metric, but for our certification process, not the
personality/behavior analysis". It moved to the certification harness
(`../gen2-cert-battery-2026-10-20/ROSTER-DECLARATION.md` §Amendment).

**Refusals per pair: not included** (her condition). The lab
binding's `survived` flag mixes real refusals with engine rewrites of
a proposal that still applied as the same menu action (measured
2026-10-21 on s1, seed 905001, 1,500 ticks: about 190 partner-play
proposals ended as Idle while more than 700 applied unchanged in the
menu yet read not-survived). Separating them needs the engine's
refusal reasons in the lab binding. Deferred, as in v1.

## Rollup and the seat proposal

Per roster: team happiness (mean and SD over seeds), worst-cat
happiness p5 (mean and SD), worst-cat gap, longest distress streak.
Per network × seat cell and per network across seats.

Proposal rule, fixed now: Experiments proposes ONE of the five
measured rotation rosters (a whole measured composition, never an
unmeasured recombination of cells). (1) Exclude any roster with an
abort. (2)
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

## Amendment 1 (2026-10-21): exact re-collection of rot2

Authorization: owner, 2026-10-21, verbatim: "1 for gen 2", choosing
between Experiments' two options (1: re-run the five rot2 worlds with
the applied action recorded, exact numbers on every bar; 2: no new
runs, eat and drink exact, play and idle as ranges) after her question
"Those eat and drink numbers look suspiciously low (e. g. 0.007 for
biscuit)". Gen 1's page takes option 2. Committed before any of this
amendment's data.

Why. The collector reads each cat's activity and partner from the
end-of-tick global state, after `resolve_activity_ends` has closed
every scene that finished that tick, so a scene's last tick reads Idle
with no partner (the F-031 instrument rule; v1 had it and the port
kept it). A meal that takes a bowl's last serving ends on its first
tick and never shows. Measured on the rotation's rot2 streams: eat
shown 0.007–0.012 of ticks against 0.018–0.030 with those ticks
counted; play up to about double; idle about half. Every metric built
on the activity flag (activity shares, entropies, routine, eat and
drink cadence, element play, beam sleep, water directness) or on the
partner flag (partnered share, pairs, concentration, top partner,
reciprocity) is affected. Happiness, distress, speech, positions and
the play-proposal share read neither.

Collector change. After every step the collector reads each cat's
`last_action`, the engine's record of the action it applied that tick
(continuation ticks included), through the binding's
`decision_request`, which renders without moving the episode and
covers scripted seats too. Two new streams: `applied` (T, R) int8,
the action's wire name as an index into the reader's `APPLIED_NAMES`,
and `applied_with` (T, R) int8, the partner's seat (rest or sleep
`with`, groom `target`, play at a kitty) or −1. Nothing else changes.

Definition (the reader). A cat's activity on tick t is the end-of-tick
flag when the flag shows a scene (v1's definition, unchanged); when
the flag shows Idle, it is the activity of the action the cat applied
that tick (rest, sleep, eat, drink, play and groom carry their
activity; move, chase, idle, purr and meow are Idle). Its partner is
the flag's partner when the flag shows one, otherwise the applied
action's partner. This adds exactly the ticks the flag hides and
leaves every visible tick as v1 read it, so Gen 1's visible ticks stay
comparable.

Runs. rot2 (Miso s2, Biscuit s4, Pumpkin s6, Kittybear s7, Clementine
s1) on 905001–905005 × 20,000 ticks, the five worlds the rotation
already ran, into `results-raw/g2-rot2-applied/`; and the scripted
reference on the same worlds into `results-raw/scripted-applied/` (no
covered minds; a second roster for the method check). The original
`results-raw/g2-rot2/` and `results-raw/scripted/` stay as they are.

Same-world check (a stop). Every stream the original collection
recorded (pos, activity, msg, act, needs, hap, partner, distress, nash,
elements) must be byte-identical to the original file for that seed.
A mismatch means the recording moved the world: that roster stops,
nothing from it is read, and it goes to the owner.

Reads, declared now:

1. The certified roster's standing analysis re-read from the new
   streams with the definition above (v1's reader and printer, as
   before). RESULTS gets a correction section that quotes each
   corrected sentence; the Gen 2 page is republished from it.
2. The stream-only method for Gen 1, checked against the exact counts
   on both new rosters. Eat: flag ticks, plus the tick after each Eat
   flag run that ends in Idle, plus one-tick meals (an eat-need drop
   with no Eat flag on that tick or the one before). Drink: flag ticks
   plus the tick after each Drink run that ends in Idle. Every other
   activity: a range from its flag count (a floor) to the flag count
   plus the tick after each of its runs that ends in Idle (a ceiling).
   Reported per activity: exact share, estimate or range, and the
   error. Gen 1's page then gets eat and drink from the method and the
   other bars as ranges.
3. The battery's two reads that use the activity flag (streak shape
   and holding), re-classified on these five worlds with the corrected
   activity and partner: the share of classified ticks that change.
   Report-only.

Stops and welfare:

- `--abort-streak 1000` on every world (the collector's default).
- Welfare-cost line: 5 covered minds × 5 worlds × 20,000 ticks =
  500,000 cat-ticks, replaying worlds this roster already ran with no
  distress onset (happiness 86.8–88.2 by cat); the scripted reference
  has no covered minds. It buys exact behavior numbers for the
  certified roster's baseline. No scout: 20×20 is the served size and
  these exact worlds already ran clean.
