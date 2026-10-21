# Gen 2 cert battery — step 8 results (2026-10-20)

Declaration: `DECLARATION.md` (committed before data). Departure:
`../gen2-deviations.md` entry 4 (seating-level abort stop not
enforced; OPEN, owner-routed). Rows the declared stop would have
prevented are marked POST-STOP and are not gate evidence until she
rules.

## Gate read (paired by seed vs the vision-law comparator, 30 × 20k)

| seating | size | trained | paired Δ | seeds + | Δ range | worst streak mean / max | aborts | verdict |
|---|---|---|---|---|---|---|---|---|
| g2-s1 | 20 | 87.314 | +5.393 | 30/30 | [4.573, 6.837] | 6.5 / 77 | 0 | PASS |
| g2-s1 | 40 | 86.142 | +4.507 | 30/30 | [3.760, 5.626] | 23.9 / 219 | 0 | PASS |
| g2-s1 | 100 | 83.889 | +7.266 | 30/30 | [3.240, 10.301] | 125.3 / 467 | 0 | characterize |
| g2-s2 | 20 | 87.257 | +5.336 | 30/30 | [3.818, 7.037] | 66.9 / 1000 | 1 | PASS (F-053 event) |
| g2-s2 | 40 | 86.012 | +4.378 | 30/30 | [3.645, 5.446] | 19.5 / 120 | 0 | POST-STOP |
| g2-s2 | 100 | 82.800 | +6.176 | 29/30 | [−1.626, 9.861] | 377.3 / 1000 | 5 | POST-STOP |
| g2-s4 | 20 | 87.746 | +5.826 | 30/30 | [5.020, 7.355] | 19.6 / 535 | 0 | PASS |
| g2-s4 | 40 | 86.499 | +4.865 | 30/30 | [4.182, 5.901] | 70.8 / 687 | 0 | PASS |
| g2-s4 | 100 | 83.800 | +7.177 | 30/30 | [2.926, 10.520] | 641.2 / 1000 | 11 | characterize (post-stop after 1st abort) |

Comparator (prereg §7 pins): 20×20 81.921, streak 178/401; 40×40
81.634, 197/626; 100×100 76.623, 443/716; zero F-053 events at
every size.

Reading. On happiness, the trunk beats the scripted teacher roster
at every size, in every seed at the gated sizes (+4.4 to +5.8 at
20/40). The welfare tail is the open question, and it does not
follow happiness. s1 is the only seating that is fully in-protocol
and tail-clean: zero aborts at any size, gated worst streaks 77 and
219, both under the comparator's maxima. s2 reached the F-053 line
once at the served 20×20 (seed 905008, tick 18949), which is the
seating's declared stop. s4 is clean at the gated sizes but
reached the line in 11 of 30 worlds at 100×100. Four of those
aborts land at tick 1128 or 1224 across different seeds; that
repeat is noted and not investigated. Dispersion columns are in the
raws and not yet read.

## Read (gate; seconds; stdlib python3, repo root)

```
cd experiments/gen2-cert-battery-2026-10-20 && python3 -B gate_read.py --out gate-read.json
```

## s2 stop investigation (2026-10-20; owner "Let's investigate s2's stop first")

Seed 905008, served 20×20, g2-s2 roster. Deterministic replay
(`diag_s2_905008.py`, stopped at tick 18300 to limit re-exposure)
reproduced every seat's distress onset exactly: 18001 / 17950 /
17956 / 17983 / 18010, continuous after onset.

**Mechanism: a five-cat co-sleep pile, F-027's twin lock at roster
scale.** Through tick ~17400 the roster plays and roams normally
(mean pairwise distance 7.5 tiles). Over the next 550 ticks the cats
drift together (4.5) and switch toward SleepWith / RestWith partner
actions. From onset they hold adjacent tiles at the bottom edge
(pairwise 1.8; positions x 9–10, y 17–19). In the locked window
60% of chosen actions are sleep/rest-with a packmate, 20% chase a
packmate, 19% groom one, and 1 of 1,755 is a move. Eat, drink and
play climb to 100 on every cat while cuddle sits near 0 and sleep
holds at the 15 floor (sleeping off-beam buys no further relief,
yet the cats keep choosing it). Several call WantEat and do not go.
Chow was 5 tiles and water 8 tiles from the pile in the world's
tick-0 layout. Whether Move was legal on each locked tick was not
recorded; chase actions, which move the cat, were legal and chosen.

The same world is distress-free under g2-s1 and g2-s4 (worst streak
0), and the scripted roster's worst streak there is 348. F-027's
scope note carries over: greedy argmax sustains a symmetric lock and
sampled action selection is untested; the engine's relief guarantee
is supply-side only, so nothing interrupts the loop.

## Read (s2 stop; ~1 min replay + seconds; lab venv, repo root)

```
cd experiments/gen2-cert-battery-2026-10-20 && VIRTUAL_ENV=/Users/elizabethkelly/ai/cloudkitty/experiments/exp-006-character-gen/.venv /Users/elizabethkelly/ai/cloudkitty/experiments/exp-006-character-gen/.venv/bin/python3 -B diag_s2_905008.py --out diag-s2-905008.npz
```

```
cd experiments/gen2-cert-battery-2026-10-20 && VIRTUAL_ENV=/Users/elizabethkelly/ai/cloudkitty/experiments/exp-006-character-gen/.venv /Users/elizabethkelly/ai/cloudkitty/experiments/exp-006-character-gen/.venv/bin/python3 -B - <<'EOF2'
import sys, numpy as np
sys.path.insert(0, "../gen2-trunk-training-2026-10-18/trainer"); sys.path.insert(1, "../attn-oracle-2026-08-15")
from data_g2 import ACTION_NAMES
z = np.load("diag-s2-905008.npz"); t = z["tick"]
assert z["onset"].tolist() == [18001, 17950, 17956, 17983, 18010]
def pw(a, b):
    P = z["pos"][(t >= a) & (t < b)]
    return round(float(np.mean([np.abs(P[:, i] - P[:, j]).sum(1).mean() for i in range(5) for j in range(i + 1, 5)])), 2)
assert (pw(16000, 17400), pw(17400, 17950), pw(17950, 18301)) == (7.46, 4.45, 1.78)
names = [ACTION_NAMES[x] for x in z["act"][t >= 17950].ravel()]
n = len(names)
w = sum(s.startswith(("SleepWith", "RestWith")) for s in names)
assert n == 1755 and round(w / n, 2) == 0.60
assert sum(s.startswith("Move") for s in names) == 1
assert sum(s in ("Eat", "Drink") for s in names) == 0
last = z["needs"][-1]
assert (last[:, 0] >= 0.995).all() and (last[:, 1] >= 0.995).all() and (last[:, 3] >= 0.995).all()
print("s2 stop fence: all cells match")
EOF2
```

## 100×100 stops, row-level read (informational only; owner: "the 100x100 runs are informative only, not a gate")

No replay; read from the recorded rows. A seat whose distress-tick
count equals its longest single-need streak spent all its distress
in one continuous run, which fixes its onset at abort − count + 1.

**g2-s2 (5 aborts): roster-wide, the 20×20 pile signature.** In
every aborted world all five seats carry long streaks (713–1000).
Seed 905024 matches the 20×20 stop exactly: five continuous runs
with onsets 6447–6734.

**g2-s4 (11 aborts): one cat alone.** In 8 of 11 aborted worlds a
single seat carries the streak and every other seat stays under 100
ticks. Four abort early with an isolated cat: seeds 905008 and
905012 (seat 4, onset tick 129) and 905015 and 905022 (seats 2
and 3, onset tick 225). Each of those cats has together_share 0.0:
it never stood adjacent to another cat for the whole run. The
identical onset ticks across different seeds are unexplained and
not investigated. Which need ran out is not in the rows.

## Read (100×100 stops; seconds; stdlib python3, repo root)

```
python3 - <<'EOF2'
import json
d = "experiments/gen2-cert-battery-2026-10-20/results-raw/"
def ab(s):
    rs = [json.loads(l) for l in open(d + f"{s}/legs/size100/{s}-g2cmp-30x20000.jsonl").read().splitlines()[1:]]
    return {r["seed"]: r for r in rs if "aborted_streak" in r}
s2, s4 = ab("g2-s2"), ab("g2-s4")
assert len(s2) == 5 and len(s4) == 11
assert all(min(r["max_distress_age_seat"]) >= 713 for r in s2.values())
r = s2[905024]; at = r["aborted_streak"]["at_tick"]
assert r["dist_ticks"] == r["max_distress_age_seat"]
assert sorted(at - x + 1 for x in r["dist_ticks"]) == [6447, 6450, 6491, 6522, 6734]
solo = [s for s, r in s4.items() if sum(x > 100 for x in r["max_distress_age_seat"]) == 1]
assert len(solo) == 8
for seed, seat, onset in ((905008, 4, 129), (905012, 4, 129), (905015, 2, 225), (905022, 3, 225)):
    r = s4[seed]
    assert r["dist_ticks"][seat] == r["max_distress_age_seat"][seat] == 1000
    assert r["aborted_streak"]["at_tick"] - 1000 + 1 == onset
    assert r["dispersion"]["together_share"][seat] == 0.0
print("100x100 fence: all cells match")
EOF2
```

## Mixed-roster test (2026-10-20/21; owner "Let's do a mixed roster test with the 3 models we have first")

Declaration `MIXED-DECLARATION.md` (9336e573); instruments and guards
492ed69d (the per-roster leg stop, armed this time); reader 538980a6.
All six legs ran, 30 × 20k each, paired with the comparator and the
uniform battery on band g2cmp. No stops fired.

| roster (Miso…Clementine) | size | team | vs scripted | company effect (worlds +) | worst streak mean / max | aborts |
|---|---|---|---|---|---|---|
| mix1 s1 s1 s2 s2 s4 | 20 | 87.436 | +5.516 (30/30) | −0.001 (11/29) | 1.7 / 38 | 0 |
| mix2 s2 s4 s1 s4 s1 | 20 | 87.513 | +5.592 (30/30) | +0.034 (18/29) | 3.2 / 66 | 0 |
| mix3 s4 s2 s4 s1 s2 | 20 | 87.508 | +5.587 (30/30) | +0.015 (18/29) | 21.0 / 165 | 0 |
| mix1 | 40 | 86.168 | +4.533 (30/30) | −0.018 (14/30) | 10.3 / 90 | 0 |
| mix2 | 40 | 86.240 | +4.606 (30/30) | −0.023 (11/30) | 16.2 / 173 | 0 |
| mix3 | 40 | 86.217 | +4.583 (30/30) | −0.057 (11/30) | 36.3 / 177 | 0 |

Company effect = a cat's happiness in the mixed roster minus the same
network's happiness at the same seat in the same world under uniform
seating, averaged per world. The 20×20 rows exclude world 905008,
whose uniform s2 baseline aborted (flagged pairs). Uniform s2 at
40×40 is post-stop data (entry 4), so s2 seats are excluded at 40×40;
those 150 pairs average +0.036 and are reported only.

Per network, pooled over its seat-worlds: s1 +0.001 (20), −0.027
(40); s2 +0.074 at 20 (+0.157 with the flagged world); s4 −0.018
(20), −0.037 (40). Pooled: +0.018 at 20×20 (445 seat-worlds; +0.047
with the 5 flagged pairs), −0.032 at 40×40 (300).

Worst streak per network at the same seats, mixed vs uniform: 20×20
s1 66 vs 77, s2 87 vs 1000, s4 165 vs 535; 40×40 s1 142 vs 219, s4
147 vs 687 (s2 177 vs a post-stop uniform 120). Dispersion barely
moved: together-share 0.519–0.527 mixed vs 0.523–0.530 uniform at
20×20 (pooled Δ −0.005; −0.003 at 40×40), group count within +0.03.

Predictions as declared. P1 held (+0.018 inside [−1.5, +0.5]); the
bracket was centred on a cost from the Gen 1 kin effect (−0.94), and
no cost appeared. P2 held in direction only (−0.005: half a
percentage point of time adjacent, far from Gen 1's F-045 gap). P3
held: no F-053 event in 180 worlds.

Reading. Mixing the three networks cost no measurable mean welfare at
either gated size; every pooled and per-network company effect is
under a tenth of a happiness point. The tail improved: the worst
stretch for s2 cats fell from 1,000 to 87 ticks at the served size
and for s4 cats from 535 to 165. Every mixed roster beat the scripted
roster in all 30 worlds at both sizes. Limits: each roster still
seats two twin pairs; 30 worlds per leg cannot bound a 1-in-30 event
(s2's lock was exactly that rate); the five-network roster is
untested; mini-models do not exist yet.

## Read (mixed roster; seconds; stdlib python3, repo root)

```
cd experiments/gen2-cert-battery-2026-10-20 && python3 -B mixed_read.py --out mixed-read.json
```

```
python3 - <<'EOF2'
import json
B = "experiments/gen2-cert-battery-2026-10-20/"
d = json.load(open(B + "mixed-read.json"))
s20, s40 = d["by_size"]["20"], d["by_size"]["40"]
exp = {("20", "g2-mix1"): (87.436, 5.516, -0.001, 11, 1.7, 38), ("20", "g2-mix2"): (87.513, 5.592, 0.034, 18, 3.2, 66),
       ("20", "g2-mix3"): (87.508, 5.587, 0.015, 18, 21.0, 165), ("40", "g2-mix1"): (86.168, 4.533, -0.018, 14, 10.3, 90),
       ("40", "g2-mix2"): (86.24, 4.606, -0.023, 11, 16.2, 173), ("40", "g2-mix3"): (86.217, 4.583, -0.057, 11, 36.3, 177)}
for (z, m), (t, v, c, cp, sm, sx) in exp.items():
    R = d["by_size"][z]["rosters"][m]
    assert (R["team_mean"], R["vs_scripted"]["mean"], R["vs_scripted"]["positive"]) == (t, v, 30), (z, m)
    assert (R["company_effect_unflagged"]["mean"], R["company_effect_unflagged"]["positive"]) == (c, cp), (z, m)
    assert (R["worst_streak_mean"], R["worst_streak_max"], R["aborts"]) == (sm, sx, []), (z, m)
N20, N40 = s20["networks"], s40["networks"]
assert (N20["s1"]["company_effect_unflagged"]["mean"], N20["s2"]["company_effect_unflagged"]["mean"],
        N20["s2"]["company_effect"]["mean"], N20["s4"]["company_effect"]["mean"]) == (0.001, 0.074, 0.157, -0.018)
assert (N40["s1"]["company_effect"]["mean"], N40["s4"]["company_effect"]["mean"], N40["s2"]["company_effect"]["n"]) == (-0.027, -0.037, 0)
assert (s20["pooled_company_effect_unflagged"]["mean"], s20["pooled_company_effect_unflagged"]["n"]) == (0.018, 445)
assert (s20["pooled_company_effect"]["mean"], s40["pooled_company_effect"]["mean"], s40["pooled_company_effect"]["n"]) == (0.047, -0.032, 300)
assert round(sum(x["delta"] for x in s40["post_stop"]) / len(s40["post_stop"]), 3) == 0.036 and len(s40["post_stop"]) == 150
w = {n: (N20[n]["worst_seat_streak_mixed"], N20[n]["worst_seat_streak_uniform_same_seats"]) for n in N20}
assert w == {"s1": (66, 77), "s2": (87, 1000), "s4": (165, 535)}, w
w = {n: (N40[n]["worst_seat_streak_mixed"], N40[n]["worst_seat_streak_uniform_same_seats"]) for n in N40}
assert w == {"s1": (142, 219), "s2": (177, 120), "s4": (147, 687)}, w
assert (s20["pooled_together_share_delta"], s40["pooled_together_share_delta"]) == (-0.005, -0.003)
P = d["predictions"]
assert P["P1_company_effect_20_in_bracket"] and P["P2_together_share_delta_20_negative"] and P["P3_zero_aborts_20_40"]
assert P["legs_run"] == P["legs_declared"] == 6
def tog(s, z):
    rs = [json.loads(l) for l in open(B + f"results-raw/{s}/legs/size{z}/{s}-g2cmp-30x20000.jsonl").read().splitlines()[1:]]
    return round(sum(sum(r["dispersion"]["together_share"]) / 5 for r in rs) / 30, 3)
assert sorted(tog(m, 20) for m in ("g2-mix1", "g2-mix2", "g2-mix3")) == [0.519, 0.52, 0.527]
assert sorted(tog(s, 20) for s in ("g2-s1", "g2-s2", "g2-s4")) == [0.523, 0.529, 0.53]
print("mixed-roster fence: all cells match")
EOF2
```
