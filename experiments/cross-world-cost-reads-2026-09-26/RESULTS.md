# Cross-world cost reads — results

Collected 2026-09-26 20:40–21:06Z under `DECLARATION.md` (nine legs,
30 seeds × 20,000 ticks requested, eval band 870001, served clock,
`--abort-streak 1000`; no training). **One abort fired**: the
lam-s1-on-floor15 leg, seed 870015, stopped at tick 16,027 when a
distress streak reached the 1,000-tick line — the declared
welfare-practice stop working as ruled; details and the owner's fork
in the reading below. Raws in `results-raw/` (gitignored).

## The table (cross-read.md, from `results-raw/cross-read.json`)

Comparators: gen1-A floor0 (recorded tier 1 cell) 92.320; gen1-A
floor15 (fresh leg) 89.811; the β = 0 recipe band on floor 0 (tier
2's pkg all-arm legs) 91.931 / 92.563.

| leg | happiness | paired delta | worse/30 |
|---|---|---|---|
| sg15-s1-on-floor0 | 91.458 | -0.862 | 30/30 |
| sg15-s2-on-floor0 | 91.380 | -0.941 | 30/30 |
| hard-s1-on-floor15 | 90.325 | +0.514 | 1/30 |
| hard-s2-on-floor15 | 90.735 | +0.924 | 0/30 |
| cvx-s1-on-floor15 | 90.472 | +0.661 | 0/30 |
| cvx-s2-on-floor15 | 90.573 | +0.762 | 0/30 |
| lam-s1-on-floor15 | 90.505 | +0.694 | 1/30 |
| lam-s2-on-floor15 | 90.108 | +0.297 | 2/30 |

Pairing: sg15 legs against the recorded gen1-A floor-0 cell; shaped
legs against the fresh gen1-A floor-15 leg; same 30 seeds
throughout.

## The reading: cost is world-relative, and the comparison stays confounded with training world

The two declared expectations, scored:

- **The floor-trained habit costs on floor 0**: sg15 arms pay
  −0.862 / −0.941 (worse on 30/30), both below even the β = 0
  band's floor (91.931). The declaration expected "roughly the
  tier-5 gap" (~1.5); the measured cost is about 60% of that. Same
  scale as F-054's shaped-arm floor-0 deficits (0.75–1.98; F-055's
  bonus arms paid 0.729–0.839 on the same world, a scale
  comparison only — that channel is enrichment, not beam shaping).
- **The shaped habit transfers positively to floor 15**: every
  F-054 arm lands ABOVE unshaped gen1-A there, +0.297 to +0.924,
  better on 28–30 of 30 seeds — the declaration expected shrunken
  deficits and got surpluses, largest swing on the hard arms as
  expected (floor-0→floor-15 swing 2.50/2.49 hard, 2.07/2.18
  convex, 1.44/1.42 lam). MECHANISM NOT SEPARATED: placement does
  not track the surplus (hard-s1 at 0.931 placement gains +0.514;
  lam-s1 at 0.356 gains +0.694), and the shaped arms sleep far
  less than gen1-A there (0.085–0.177 vs 0.285) on a world where
  ground naps relieve nothing — skipping worthless naps could
  carry the surplus by itself. This read measures happiness only.

What the one-footing comparison actually shows, pairing each MIND
with itself across the two worlds (same 30 seeds): the floor-15
world's cost depends on the mind. It costs the hard arms
essentially nothing (−0.012 / −0.020), the convex arms −0.44/−0.33,
the lam arms −1.07/−1.09, the floor-trained sg15 arms −0.60/−0.25,
and unadapted gen1-A −2.51. So the gaps to the floor-0 92.320 are
mostly MIND-side: the beam habit makes the floor world nearly free,
and sg15's home-world gap (1.46/1.19) is majority carried habit
(0.86/0.94 of it already present on floor 0) with a 0.25–0.60
world remainder — consistent with the declaration's own mind-side
expectation and the ~60% score above. And on both
worlds the world-side-trained minds do better than the shaped ones:
sg15 on floor 15 pays +1.047/+1.314 over gen1-A (0/30 worse), above
every shaped arm's +0.297–0.924; on floor 0, sg15's 0.86–0.94 cost
sits under the shaped arms' AVERAGE cost (1.37), though inside
their 0.75–1.98 range — lam-s1 (−0.749) beats both sg15 arms there. The direction of the
measured gap favors world-side pressure — BUT every such comparison
is home-world vs transfer (the shaped arms trained on floor 0, the
sg arms on their own floors), so the gap is confounded with
training world, not a clean form verdict. The honest rule-1 input:
the floor-0 cost numbers were the price of a habit on the world
that does not pay it, not an intrinsic price of objective-side
pressure; a clean gap needs same-world training, which no current
pair provides. F-054's dose confound (register caveat) is untouched
by this read.

**Distress, reported per the welfare practice**: the declaration
expected baseline-scale exposure; seven of the eight cross-world
legs ran above the fresh comparator's 458 distress ticks — lam-s1
7,976 (six seeds with streaks over 150), lam-s2 5,248, cvx-s2
4,368, sg15-s2 4,015, hard-s1 3,819, cvx-s1 2,394, sg15-s1 1,485
(the two sg15 legs ran on floor 0, where the same-config fresh
comparator carries 360) — while hard-s2 ran BELOW it at 347, and hard-s1 ran
cooler than its own floor-0 home leg (3,819 vs 4,737). (The
recorded floor-0 gen1-A cell predates the distress counter; the
fresh same-config leg in the enrichment screen carries 360.) One
abort fired: lam-s1 seed 870015 hit the 1,000-tick line at tick
16,027. That truncated seed stays in the mean above (its paired
delta −1.823 is lam-s1's one worse seed; excluding it would read
+0.78 instead of +0.694 — both numbers here so the choice is
visible; without that seed lam-s1's distress total, 4,094, sits
below lam-s2's and cvx-s2's). The fork is the owner's: the lam
arms run hottest on the floor world, lam-s1 past the line once;
this weighs on any future floor-world legs of those arms, and none
run without her word.

Feeds the rule-1 cost comparison this read was declared for (memo
finding 2; the fork is F-054's rule-1 structural question, RESULTS
§Decision rules there) and, indirectly, the finding-4 framing fork
in the gen3 inputs doc — both land at the Gen 2/3 session. No
F-entry:
this is a comparator read that re-scopes F-054's cost claim; the
scoping lives in F-054's register caveat, which points here.

## Regeneration

### Collect

`run_legs.sh` (nine legs, sequential; log `results-raw/legs.log`,
markers `== sg15 on floor-0` 20:40:27Z → `== cross-reads done`
21:05:39Z). Never run by the gate.

### Read

Runtime: under 10 seconds. No environment variables required.

```
cd /Users/elizabethkelly/ai/cloudkitty
experiments/exp-006-character-gen/.venv/bin/python experiments/cross-world-cost-reads-2026-09-26/read_cross.py \
  --out experiments/cross-world-cost-reads-2026-09-26/results-raw/cross-read.json \
  --md experiments/cross-world-cost-reads-2026-09-26/results-raw/cross-read.md
```

Gate: **PASS** 2026-09-26 (four rounds — numbers clean throughout;
round 1 caught an unreported abort, a misattributed tier-5 range,
and an over-drawn "no measured gap"; round 2 the fork pointer and a
range-vs-mean slip; round 3 replaced the world-cost narrative with
same-mind pairs and fixed a false universal in the distress report)
· claims: ~50 arithmetic, 1 threshold, ~10 characterisations (1
non-failing WEAK), 8 provenance, 0 UNDECIDABLE · raws audited 30 ×
20,000 on every leg except the one reported abort row.
