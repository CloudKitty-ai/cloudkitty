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

## Would the served stuck detector catch the s2 lock? (offline replay, 2026-10-21)

The battery ran without spec 061's stuck detector: it is a
server-side table the engine never sees, shipped dark (mode off), so
every certification number above is free of it. To see whether it
would catch the s2 pile, spec 061's own rule
(`specs/061-stuck-detector/stuck_rule_replay.py`, `run_stream`, its
synthetic-pacer self-test passing first) was replayed over the saved
pile trace (`diag-s2-905008.npz`, ticks 16000–18300). No new exposure.
Relief is read pessimistically as in the replay's arm B (resting and
grooming clear nothing), which can only make fires earlier.

At the shipped settings (window 30, armed line 75) it fires on all
five cats, 48 to 286 ticks after each one's distress onset: Miso
18091 (+90), Biscuit 18091 (+141), Pumpkin 18242 (+286), Kittybear
18031 (+48), Clementine 18089 (+79). The armed needs were already at
100 when it fired. It is late because co-sleep and grooming scenes
pause the armed count, and the locked cats spent most ticks in those
scenes. A fire replaces one proposal with the scripted brain's choice
and re-arms only after a fresh window; whether that breaks a
self-renewing lock is untested (that needs the detector in the loop).
Reading: the detector is a late backstop for this shape, not a fix.

## Read (stuck-detector replay; seconds; lab venv, repo root)

```
cd experiments/gen2-cert-battery-2026-10-20 && VIRTUAL_ENV=/Users/elizabethkelly/ai/cloudkitty/experiments/exp-006-character-gen/.venv /Users/elizabethkelly/ai/cloudkitty/experiments/exp-006-character-gen/.venv/bin/python3 -B - <<'EOF2'
import sys
import numpy as np
sys.argv = ["x"]
sys.path.insert(0, "../../specs/061-stuck-detector")
import stuck_rule_replay as sr
sr.selftest()
z = np.load("diag-s2-905008.npz")
t, pos, needs, act = z["tick"], z["pos"].astype(int), z["needs"] * 100.0, z["act_state"]
first, counts = [], []
for k in range(5):
    rows = [(int(t[i]), (int(pos[i, k, 0]), int(pos[i, k, 1])),
             dict(zip(sr.NEED_ORDER, needs[i, k].tolist())), bool(act[i, k] != 0),
             sr.ARM_B_RELIEVES[int(act[i, k])], {"seat": sr.SEATS[k]}) for i in range(len(t))]
    fires = []
    sr.run_stream(rows, 30, 75.0, "s2-905008", fires)
    first.append(fires[0]["tick"]); counts.append(len(fires))
assert first == [18091, 18091, 18242, 18031, 18089], first
assert counts == [3, 2, 1, 2, 2], counts
assert [f - o for f, o in zip(first, z["onset"].tolist())] == [90, 141, 286, 48, 79]
print("stuck-detector replay fence: all cells match")
EOF2
```

## Group holding: scripted baseline (2026-10-21; ROSTER-DECLARATION §Amendment)

The scripted comparator re-ran at 20, 40 and 100 with the holding
account (`results-raw/holding-baseline/`). Every pinned comparator
field reproduces exactly (team happiness 81.921 / 81.634 / 76.623,
worst streaks 401 / 626 / 716): the harness change moved nothing it
already measured.

| size | time in a 3+ group | largest per-cat held share | longest held stretch | longest shared hold | worlds with a shared hold |
|---|---|---|---|---|---|
| 20 | 0.4287 | 0.0355 | 220 | 196 | 23/30 |
| 40 | 0.3376 | 0.0306 | 219 | 249 | 25/30 |
| 100 | 0.2905 | 0.0893 | 351 | 297 | 30/30 |

The teacher holds routinely. What it is doing while held, from the
per-tick scripted-reference streams of worlds 905001 and 905002 (the
seating analysis's declared reference collection; the per-tick
reconstruction matches the rows' per-cat longest stretches exactly):
idle on 88% and 85% of held cat-ticks, partnered on 10% and 9%,
moving on 3% and 6%, hottest need at a median of 92 and 100. Food was
on the map (six chow) with the nearest a median 5 and 6 tiles away,
and water a median 3 and 10 tiles away; under 1% of held ticks were
within a tile of either. Most held stretches ended in eating or
drinking within 60 ticks (63 of 76; 40 of 55).

Reading: the teacher's holds are not the social lock s2 showed. They
look like search failures under fog, with hungry cats idling together
while food sits just beyond the 4-tile vision radius. The measure
registers the welfare state (grouped, hungry or thirsty, not tending)
whatever its cause, so this envelope is a lenient anchor for a bar.

## Read (holding baseline; seconds; stdlib python3, then lab venv; repo root)

```
cd experiments/gen2-cert-battery-2026-10-20 && python3 -B holding_read.py results-raw/holding-baseline/legs/size20/scripted-g2cmp-30x20000.jsonl results-raw/holding-baseline/legs/size40/scripted-g2cmp-30x20000.jsonl results-raw/holding-baseline/legs/size100/scripted-g2cmp-30x20000.jsonl --out holding-baseline-read.json
```

```
python3 - <<'EOF2'
import json
B = "experiments/gen2-cert-battery-2026-10-20/"
r = json.load(open(B + "holding-baseline-read.json"))
cells = [(x["group3_share_mean"], x["held_share_max_cat"], x["held_longest_max"], x["shared_hold_longest_max"], x["worlds_with_shared_hold"]) for x in r]
assert cells == [(0.4287, 0.03545, 220, 196, 23), (0.3376, 0.03055, 219, 249, 25), (0.2905, 0.0893, 351, 297, 30)], cells
C = "experiments/gen2-comparator-legs-2026-10-14/results-raw/"
for z, p in ((20, C + "legs/size20"), (40, C + "vision5-40/legs/size40"), (100, C + "vision-law-100/legs/size100")):
    old = {x["seed"]: x for x in (json.loads(l) for l in open(p + "/scripted-g2cmp-30x20000.jsonl").read().splitlines()[1:])}
    new = {x["seed"]: x for x in (json.loads(l) for l in open(B + f"results-raw/holding-baseline/legs/size{z}/scripted-g2cmp-30x20000.jsonl").read().splitlines()[1:])}
    assert set(old) == set(new) and len(new) == 30
    assert all(old[s][k] == new[s][k] for s in old for k in ("mean_happiness", "max_distress_age", "max_distress_age_seat", "low_share", "floor_touches", "ticks", "nash_state")), z
print("holding baseline fence: all cells match")
EOF2
```

```
cd experiments && VIRTUAL_ENV=/Users/elizabethkelly/ai/cloudkitty/experiments/exp-006-character-gen/.venv /Users/elizabethkelly/ai/cloudkitty/experiments/exp-006-character-gen/.venv/bin/python3 -B - <<'EOF2'
import json, sys
import numpy as np
sys.path.insert(0, "fog-gen1-cert")
import cert_harness_fog as H
def sizes_of(p):
    out = []
    for k in range(5):
        seen, todo = {k}, [k]
        while todo:
            i = todo.pop()
            for j in range(5):
                if j not in seen and abs(int(p[i][0]) - int(p[j][0])) + abs(int(p[i][1]) - int(p[j][1])) <= 1:
                    seen.add(j); todo.append(j)
        out.append(len(seen))
    return out
rows = {x["seed"]: x for x in (json.loads(l) for l in open("gen2-cert-battery-2026-10-20/results-raw/holding-baseline/legs/size20/scripted-g2cmp-30x20000.jsonl").read().splitlines()[1:])}
want = {905001: (0.88, 0.10, 0.03, 92, 5.0, 3.0, 63, 76), 905002: (0.85, 0.09, 0.06, 100, 6.0, 10.0, 40, 55)}
for seed, w in want.items():
    z = np.load(f"seating-analysis-g2-2026-10-21/results-raw/scripted/streams-{seed}.npz")
    et = json.loads(str(z["meta"]))["element_types"]
    pos, needs, act, partner, els = z["pos"], z["needs"], z["activity"], z["partner"], z["elements"]
    T = len(act); acc = H.hold_acc(5); held = np.zeros((T, 5), bool)
    for t in range(T):
        before = list(acc["held_ticks"])
        H.hold_update(sizes_of(pos[t]), needs[t, :, 0].tolist(), needs[t, :, 1].tolist(), act[t].tolist(), acc)
        held[t] = np.array(acc["held_ticks"]) > np.array(before)
    assert acc["held_longest"] == rows[seed]["holding"]["held_longest"]
    moving = np.r_[np.zeros((1, 5), bool), np.abs(np.diff(pos.astype(int), axis=0)).sum(2) > 0]
    df, dw = [], []
    for t, k in zip(*np.nonzero(held)):
        p = pos[t, k]
        ch = els[t][els[t][:, 0] == et["Chow"]][:, 1:]; wa = els[t][els[t][:, 0] == et["Water"]][:, 1:]
        if needs[t, k, 0] >= 75: df.append(int(np.abs(ch - p).sum(1).min()))
        if needs[t, k, 1] >= 75: dw.append(int(np.abs(wa - p).sum(1).min()))
    ends = tend = 0
    for k in range(5):
        h = held[:, k]
        for t in np.flatnonzero(h[:-1] & ~h[1:]):
            ends += 1; tend += bool(np.isin(act[t + 1:t + 61, k], (3, 4)).any())
    got = (round(float((act[held] == 0).mean()), 2), round(float((partner[:, :, 0][held] == 1).mean()), 2),
           round(float(moving[held].mean()), 2), round(float(np.median(np.maximum(needs[:, :, 0], needs[:, :, 1])[held]))),
           float(np.median(df)), float(np.median(dw)), tend, ends)
    assert got == w, (seed, got)
    assert (np.array(df + dw) <= 1).mean() < 0.01
print("held-scripted-behavior fence: all cells match")
EOF2
```

## Phase B: s6/s7 uniform battery (2026-10-21; ROSTER-DECLARATION.md)

Each new network in all five seats, band g2cmp, 30 × 20k, scouts-first
at 40×40, leg stop and holding armed. s5 was skipped as a
welfare-stopped run (entry 6). No stop fired.

| seating | size | trained | paired Δ | seeds + | Δ range | worst streak mean / max | aborts | gate |
|---|---|---|---|---|---|---|---|---|
| g2-s6 | 20 | 86.692 | +4.771 | 30/30 | [3.883, 6.354] | 1.8 / 54 | 0 | PASS |
| g2-s6 | 40 | 85.468 | +3.833 | 30/30 | [3.116, 4.970] | 2.9 / 29 | 0 | PASS |
| g2-s7 | 20 | 88.063 | +6.143 | 30/30 | [5.331, 7.545] | 35.3 / 226 | 0 | PASS |
| g2-s7 | 40 | 86.734 | +5.099 | 30/30 | [4.199, 6.220] | 173.0 / 641 | 0 | PASS |

Holding, the first trained rows with the account: s6's longest held
stretch is 10 ticks at 20×20 and 5 at 40×40, with no shared hold; s7's
is 12 and 24, with one shared hold of 7 ticks at 20×20. The scripted
roster on the same worlds: 220 and 219, with shared holds up to 196
and 249 in 23 and 25 of 30 worlds.

Reading. Both networks pass both gates in every world. s6 carries the
lightest tail of the six networks (worst streak 54 and 29). s7 posts
the largest gain of any seating (+6.143 at 20×20) and the heaviest
gated tail (40×40 mean 173.0, max 641: above the scripted maximum of
626, below the F-053 line). Holding rules out a group trap there
(s7's longest held stretch at 40×40 is 24), so it is a solitary
distress run, cause unread, like s4's 40×40 tail. Seated with copies
of themselves, the trained cats almost never hold. On this axis the
learners are far ahead of the teacher, a first answer (uniform seating
only) to the follow-up's step-0 question.

## Read (Phase B; seconds; stdlib python3, repo root)

```
cd experiments/gen2-cert-battery-2026-10-20 && python3 -B gate_read.py --seatings g2-s6,g2-s7 --sizes 20,40 --out gate-read-phaseB.json && python3 -B holding_read.py results-raw/g2-s6/legs/size20/g2-s6-g2cmp-30x20000.jsonl results-raw/g2-s6/legs/size40/g2-s6-g2cmp-30x20000.jsonl results-raw/g2-s7/legs/size20/g2-s7-g2cmp-30x20000.jsonl results-raw/g2-s7/legs/size40/g2-s7-g2cmp-30x20000.jsonl --out holding-phaseB-read.json
```

```
python3 - <<'EOF2'
import json
B = "experiments/gen2-cert-battery-2026-10-20/"
g = json.load(open(B + "gate-read-phaseB.json"))
exp = {"g2-s6/20": (86.692, 4.771, [3.883, 6.354], 1.8, 54), "g2-s6/40": (85.468, 3.833, [3.116, 4.97], 2.9, 29),
       "g2-s7/20": (88.063, 6.143, [5.331, 7.545], 35.3, 226), "g2-s7/40": (86.734, 5.099, [4.199, 6.22], 173.0, 641)}
for k, (t, d, rng, sm, sx) in exp.items():
    r = g[k]
    assert (r["trained_mean"], r["paired_mean_delta"], r["delta_range"], r["worst_streak_mean"], r["worst_streak_max"]) == (t, d, rng, sm, sx), k
    assert r["positive"] == 30 and r["aborted_seeds"] == [] and r["gate"] == "PASS", k
h = json.load(open(B + "holding-phaseB-read.json"))
assert [(x["held_longest_max"], x["shared_hold_longest_max"], x["worlds_with_shared_hold"]) for x in h] == [(10, 0, 0), (5, 0, 0), (12, 7, 1), (24, 0, 0)], h
print("Phase B fence: all cells match")
EOF2
```

## s7 streak investigation (2026-10-21; owner "Can you investigate the S7 streak cause?")

Reader `diag_s7_streaks.py`, committed before results (68c0298e). Part
1 read the rotation's recorded streams (no new exposure). Part 2
replayed Phase B s7 uniform 40×40, world 905029, in one pass with the
collector's distress abort at 100. Only Pumpkin's 622-tick run could
reach it (every other cat's longest there is 31 or less), so the
replay stopped 100 ticks into that run: about 100 re-exposed distress
ticks for one cat instead of 622.

**Cause: water parking.** In every case read, a cat that is
effectively alone sits at water and keeps choosing Drink while not
thirsty, and its distressed need goes untended. That need is one only
leaving can fix: company or food.

| case | need in distress | chose Drink | thirst (mean) | moving | alone |
|---|---|---|---|---|---|
| rotation rot1, Clementine, 121 ticks | cuddle | 111 of 121 | 0.6 | 4% | 96% |
| rotation rot1, Clementine, 84 ticks | cuddle | 79 of 84 | 0.5 | 0% | 96% |
| rotation rot3, Pumpkin, 94 ticks | eat | 42 of 94 | 2.4 | 42% | 42% |
| Phase B uniform 40×40, Pumpkin (first 100 of 622 ticks) | cuddle | 100 of 100 | 0.4 | 0% | 100% |

In the one eat case, chow was a median 8 tiles away and in sight on
only 4% of the run; the cat paced north and south (MoveS 20, MoveN 18)
and ate once it reached food. The cuddle cases never moved toward a
friend.

It is s7's own habit, learned, not inherited. Across the rotation's
streams, drinking while sated (thirst under 10) during distress filled
234 of s7's 322 distress ticks (73%, 3 of 25 cat-worlds), and no tick
for s1, s2, s4 or s6; the teacher did it on 8 of 3,917 distress ticks.
(This comparison was added after parts 1 and 2 had been read.)

It concentrates on two seats without being confined to them. Of s7's
33 Phase B streaks of 100 ticks or more (both sizes, among copies), 15
sit at Pumpkin (fastest hunger, 0.6) and 9 at Clementine (fastest
cuddle need, 0.7), with 6 at Biscuit, 3 at Miso and none at Kittybear;
the three longest (641, 622, 323) are Pumpkin and Clementine. In the
rotation s7's only streaks of 50 or more were the three above
(Clementine twice, Pumpkin once). Only the four cases read are
confirmed water parking; the rest are unread. Company shortens it:
s7's worst in mixed company was 121, against 641 among copies at
40×40.

The holding read cannot see this shape (the cat is alone), and the
teacher does not share it, so it does not belong to the teacher fix in
the vision follow-up. For an eat case it is a trained cousin of the
out-of-sight failure: relief beyond vision, and no search.

## Read (s7 streaks; part 1 seconds, part 2 about a minute; lab venv, repo root)

```
cd experiments/gen2-cert-battery-2026-10-20 && VIRTUAL_ENV=/Users/elizabethkelly/ai/cloudkitty/experiments/exp-006-character-gen/.venv /Users/elizabethkelly/ai/cloudkitty/experiments/exp-006-character-gen/.venv/bin/python3 -B diag_s7_streaks.py --part 1 --out diag-s7-part1.json && VIRTUAL_ENV=/Users/elizabethkelly/ai/cloudkitty/experiments/exp-006-character-gen/.venv /Users/elizabethkelly/ai/cloudkitty/experiments/exp-006-character-gen/.venv/bin/python3 -B diag_s7_streaks.py --part 2 --out diag-s7-part2.json
```

```
cd experiments && VIRTUAL_ENV=/Users/elizabethkelly/ai/cloudkitty/experiments/exp-006-character-gen/.venv /Users/elizabethkelly/ai/cloudkitty/experiments/exp-006-character-gen/.venv/bin/python3 -B - <<'EOF2'
import json, glob
import numpy as np
p1 = json.load(open("gen2-cert-battery-2026-10-20/diag-s7-part1.json"))["part1"]
p2 = json.load(open("gen2-cert-battery-2026-10-20/diag-s7-part2.json"))["part2"]
got = [(c["roster"], c["seed"], c["seat"], c["need"], c["length"], dict(c["chosen_top"]).get("Drink"),
        round(c["moving_share"], 2), round(c["alone_share"], 2)) for c in p1]
assert got == [("g2-rot1", 905002, "Clementine", "cuddle", 121, 111, 0.04, 0.96),
               ("g2-rot1", 905005, "Clementine", "cuddle", 84, 79, 0.0, 0.96),
               ("g2-rot3", 905002, "Pumpkin", "eat", 94, 42, 0.41, 0.41)], got
assert p1[2]["relief"]["nearest_median"] == 8.0 and p1[2]["relief"]["in_sight_share"] == 0.043 and p1[2]["ended_by_tending_within_30"]
assert (p2["seat"], p2["need"], p2["length"], p2["chosen_top"], p2["moving_share"], p2["alone_share"], p2["span"][0]) == \
       ("Pumpkin", "cuddle", 100, [["Drink", 100]], 0.0, 1.0, 353), p2
tot = {}
for p in sorted(glob.glob("seating-analysis-g2-2026-10-21/results-raw/*/streams-*.npz")):
    z = np.load(p); meta = json.loads(str(z["meta"]))
    fl = np.unpackbits(z["distress"][:, :, None].astype(np.uint8), axis=2, bitorder="little")[:, :, :6].astype(bool)
    for k, spec in enumerate(meta["seats"]):
        n = "scripted" if spec == "scripted" else spec.split("-")[-1]
        dis = fl[:, k, :].any(1)
        drink = (z["act"][:, k] == 20) if spec != "scripted" else (z["activity"][:, k] == 4)
        hit = dis & (z["needs"][:, k, 1] < 10) & drink
        t = tot.setdefault(n, [0, 0, 0]); t[0] += int(dis.sum()); t[1] += int(hit.sum()); t[2] += int(hit.sum() >= 10)
assert tot["s7"] == [322, 234, 3] and tot["scripted"][:2] == [3917, 8], tot
assert all(tot[n][1] == 0 for n in ("s1", "s2", "s4", "s6")), tot
from collections import Counter
cats = ["Miso", "Biscuit", "Pumpkin", "Kittybear", "Clementine"]
long_ = [(cats[k], s) for zz in (20, 40) for r in (json.loads(l) for l in open(f"gen2-cert-battery-2026-10-20/results-raw/g2-s7/legs/size{zz}/g2-s7-g2cmp-30x20000.jsonl").read().splitlines()[1:])
         for k, s in enumerate(r["max_distress_age_seat"]) if s >= 100]
assert len(long_) == 33 and Counter(c for c, _ in long_) == Counter({"Pumpkin": 15, "Clementine": 9, "Biscuit": 6, "Miso": 3}), Counter(c for c, _ in long_)
assert sorted(long_, key=lambda x: -x[1])[:3] == [("Pumpkin", 641), ("Pumpkin", 622), ("Clementine", 323)]
print("s7 streak fence: all cells match")
EOF2
```

## Phase C: the five-network roster rot2 is certified (2026-10-21)

Roster (owner's ruling, "Rot 2"): Miso s2, Biscuit s4, Pumpkin s6,
Kittybear s7, Clementine s1. Band g2cmp, 30 × 20k per size,
scouts-first at 40 and 100, F-053 abort and leg stop armed. No stop
fired at any size.

| size | trained | paired Δ vs scripted | seeds + | Δ range | worst streak mean / max | aborts | gate |
|---|---|---|---|---|---|---|---|
| 20 | 87.487 | +5.566 | 30/30 | [4.716, 7.055] | 16.2 / 267 | 0 | **PASS** |
| 40 | 86.229 | +4.594 | 30/30 | [3.935, 5.549] | 16.5 / 128 | 0 | **PASS** |
| 100 | 83.810 | +7.187 | 30/30 | [3.460, 10.309] | 304.6 / 859 | 0 | characterize-only |

Company effect against each network's own uniform roster: +0.067 at
20×20 (+0.048 without the flagged s2 world) and +0.025 at 40×40; no
welfare cost from mixing, as in the mixed-roster test. At 100×100
the roster had no abort, where uniform s2 and s4 had 5 and 11.
Holding, a read (her ruling): longest held stretch 7 / 13 / 19 ticks,
longest shared hold 0 / 0 / 5.

Streak shape, every streak of 100 ticks or more. At the gated sizes
there are four. At 20×20 both are Pumpkin (s6) on the move (eat 267,
97% moving; drink 152, 77%): searching, not parked. At 40×40,
Kittybear (s7) carries a cuddle run of 128 split parked 42% / idle
46%, the water-parking mix, and Clementine (s1) a cuddle run of 106,
84% moving. At 100×100 there are 43: 27 moving-dominant, 15
parked-dominant, 1 idle. All 15 parked runs are Kittybear's, the seat
s7 holds, including the worst of the leg (cuddle, 859 ticks: parked
40%, idle 35%, moving 25%). That is the shape of s7's water parking,
which mixed company and the Kittybear seat kept short at 20×20, on
the big map where company is scarce. The shape read does not record
which relief the cat stood at, so drinking-while-sated is consistent
with these runs, not confirmed for them.

## Read (Phase C; seconds; stdlib python3, repo root)

```
cd experiments/gen2-cert-battery-2026-10-20 && python3 -B gate_read.py --seatings g2-rot2 --sizes 20,40,100 --out gate-read-phaseC.json && python3 -B holding_read.py results-raw/g2-rot2/legs/size20/g2-rot2-g2cmp-30x20000.jsonl results-raw/g2-rot2/legs/size40/g2-rot2-g2cmp-30x20000.jsonl results-raw/g2-rot2/legs/size100/g2-rot2-g2cmp-30x20000.jsonl --out holding-phaseC-read.json && python3 -B shape_read.py results-raw/g2-rot2/legs/size20/g2-rot2-g2cmp-30x20000.jsonl results-raw/g2-rot2/legs/size40/g2-rot2-g2cmp-30x20000.jsonl results-raw/g2-rot2/legs/size100/g2-rot2-g2cmp-30x20000.jsonl --out shape-phaseC-read.json && python3 -B mixed_read.py --mixes g2-rot2 --out mixed-read-phaseC.json
```

```
python3 - <<'EOF2'
import json
from collections import Counter
B = "experiments/gen2-cert-battery-2026-10-20/"
g = json.load(open(B + "gate-read-phaseC.json"))
exp = {"g2-rot2/20": (87.487, 5.566, [4.716, 7.055], 16.2, 267, "PASS"), "g2-rot2/40": (86.229, 4.594, [3.935, 5.549], 16.5, 128, "PASS"),
       "g2-rot2/100": (83.81, 7.187, [3.46, 10.309], 304.6, 859, "characterize-only")}
for k, (t, d, rng, sm, sx, gate) in exp.items():
    r = g[k]
    assert (r["trained_mean"], r["paired_mean_delta"], r["delta_range"], r["worst_streak_mean"], r["worst_streak_max"], r["gate"]) == (t, d, rng, sm, sx, gate), k
    assert r["positive"] == 30 and r["aborted_seeds"] == [], k
h = json.load(open(B + "holding-phaseC-read.json"))
assert [(x["held_longest_max"], x["shared_hold_longest_max"]) for x in h] == [(7, 0), (13, 0), (19, 5)], h
s = json.load(open(B + "shape-phaseC-read.json"))
st20, st40, st100 = (x["streaks"] for x in s)
assert [(x["seat"], x["need"], x["length"], round(x["moving"], 2)) for x in st20] == [("Pumpkin", "eat", 267, 0.97), ("Pumpkin", "drink", 152, 0.77)]
assert [(x["seat"], x["need"], x["length"], round(x["parked"], 2), round(x["idle"], 2)) for x in st40][0] == ("Kittybear", "cuddle", 128, 0.42, 0.46)
assert (st40[1]["seat"], st40[1]["length"], round(st40[1]["moving"], 2)) == ("Clementine", 106, 0.84)
assert len(st100) == 43 and s[2]["by_dominant"] == {"parked": 15, "moving": 27, "idle": 1}
assert Counter(x["seat"] for x in st100 if x["dominant"] == "parked") == Counter({"Kittybear": 15})
w = st100[0]
assert (w["seat"], w["need"], w["length"], round(w["parked"], 2), round(w["idle"], 2), round(w["moving"], 2)) == ("Kittybear", "cuddle", 859, 0.4, 0.35, 0.25)
m = json.load(open(B + "mixed-read-phaseC.json"))["by_size"]
assert (m["20"]["pooled_company_effect"]["mean"], m["20"]["pooled_company_effect_unflagged"]["mean"], m["40"]["pooled_company_effect"]["mean"]) == (0.067, 0.048, 0.025)
print("Phase C fence: all cells match")
EOF2
```

## Owed reads on the certified roster (2026-10-21; timeline "post-cert analysis plan", owner "Recommendation accepted")

Three reads the prereg or this battery's declaration owed, all on rows
already recorded (`dispersion_read.py` → `dispersion-read.json`).
Nothing new was collected. Thirty worlds per size (905001–905030),
paired by seed throughout.

### §9.5, the dispersion read at all three sizes (character, not a bar)

| size | together-share, rot2 by seat (Miso Biscuit Pumpkin Kittybear Clementine) | groups per tick | Δ vs the scripted teacher | Δ vs each seat's own network seated five times |
|---|---|---|---|---|
| 20 | 0.522 0.544 0.505 0.537 0.564 | 3.353 | no field in the comparator rows | +0.002 −0.002 −0.013 −0.002 −0.000 |
| 40 | 0.427 0.457 0.418 0.445 0.481 | 3.692 | no field in the comparator rows | +0.012 +0.009 −0.014 −0.009 +0.001 |
| 100 | 0.356 0.387 0.353 0.375 0.414 | 3.922 | −0.085 −0.072 −0.059 −0.087 −0.045; groups +0.371 | −0.007 (Miso, s2) −0.020 (Biscuit, s4) −0.012 (Clementine, s1); Pumpkin (s6) and Kittybear (s7) have no 100×100 leg |

At 20 and 40 the vision-law comparator rows predate the field (this
battery's DECLARATION), so the pairing there is the mixed read's: each
seat against its own network seated five times. Every such delta is
within 0.0141 of zero (the largest, Pumpkin at 40×40, −0.01406). At 100×100 the holding-baseline scripted re-run carries
the field, so rot2 is paired against the teacher: every seat is
together less (−0.045 to −0.087 of ticks) and the roster runs 0.37 more
groups per tick. Together-share falls with size for the roster
(0.505–0.564 → 0.418–0.481 → 0.353–0.414). INVESTIGATE row, as the
prereg files it: on the big world the trained roster spreads out more
than its teacher, which sits beside Phase C's water-parking tail
(Kittybear's, the seat s7 holds) without explaining it.

### §8.5, the declared future read: does the gap move with size?

The paired team-happiness gap, trained minus scripted: +5.566 ± 0.623
at 20×20, +4.594 ± 0.451 at 40×40 (the cert legs), +7.187 ± 1.704 at
100×100 (the characterize leg); 30 of 30 worlds positive at each size,
no aborts. Between the two cert legs the gap falls by 0.97, more than
either leg's per-seed SD and about 8.5 times the SE of the per-seed
paired difference between the two legs (SD 0.625, n 30); it rises again
at 100. The prereg's trigger ("if the trained-vs-scripted
gap moves with size across cert legs, one displaced-size radius cell
runs, scouts-first") names no margin, so the record is the numbers: the
gap is not flat across sizes. Whether the radius cell runs is the
owner's call; none runs from this reading.

### §9.8, the F-050 revisit: beam placement and welfare under floor 15

In-beam = on-beam sleep ticks over sleep ticks, conducted = conducted
sleep ticks over sleep ticks, pooled over the 30 worlds as the
beam-world screen read them (`screen_read.py`).

| size | roster | in-beam by seat (Miso Biscuit Pumpkin Kittybear Clementine) | in-beam pooled | conducted pooled | team happiness |
|---|---|---|---|---|---|
| 20 | rot2 | 0.413 0.440 0.383 0.432 0.404 | 0.416 | 0.138 | 87.487 |
| 20 | scripted | 0.310 0.426 0.486 0.424 0.417 | 0.387 | 0.055 | 81.921 |
| 40 | rot2 | 0.547 0.544 0.484 0.568 0.496 | 0.533 | 0.109 | 86.229 |
| 40 | scripted | 0.390 0.519 0.548 0.513 0.513 | 0.472 | 0.054 | 81.634 |
| 100 | rot2 | 0.650 0.622 0.589 0.661 0.513 | 0.613 | 0.084 | 83.810 |
| 100 | scripted | 0.444 0.586 0.668 0.567 0.581 | 0.538 | 0.049 | 76.623 |

The Gen 2 roster keeps 0.416 / 0.533 / 0.613 of its sleep on beams at
20 / 40 / 100 against the teacher's 0.387 / 0.472 / 0.538, and conducts
1.7–2.5× as much (0.138 / 0.109 / 0.084 against 0.055 / 0.054 / 0.049).
Placement rises with size for both rosters. Two seats sit below their
teacher at every size: Pumpkin (0.383 vs 0.486, 0.484 vs 0.548, 0.589
vs 0.668) and Clementine (0.404 vs 0.417, 0.496 vs 0.513, 0.513 vs
0.581); Miso is the largest gain at every size (0.413 vs 0.310 at
20×20). Welfare
under floor 15 is the certificate's: 87.49 / 86.23 / 83.81 against
81.92 / 81.63 / 76.62. One half of the revisit stays open: Gen 2 ran
one beam density (the sunbeam count scales with area, 6–7 / 24–28 /
150–175 at 20 / 40 / 100, 1.5–1.75 per hundred tiles throughout), so
the density half is unmeasured. F-050's re-verify condition (the
teacher re-recorded under the floor) is met by construction: spec 057
(the sleep rule reads the floor) merged 2026-09-22, before the Gen 2
comparators were recorded, so the scripted side here is the
floor-reading teacher. F-050, doctrine rule 7's worked example and the
GEN2-INPUTS shelf entry carry a dated addendum with these numbers.

## Read (owed reads; seconds; stdlib python3, repo root)

```
cd experiments/gen2-cert-battery-2026-10-20 && python3 -B dispersion_read.py --out dispersion-read.json
```

```
python3 - <<'EOF2'
import json
J = json.load(open("experiments/gen2-cert-battery-2026-10-20/dispersion-read.json"))
G, D, B = J["gap_by_size"], J["dispersion"], J["beam"]
r3 = lambda x: round(x, 3)
assert [(r3(G[z]["mean"]), r3(G[z]["sd"]), G[z]["positive"], G[z]["aborts"], G[z]["n"]) for z in ("20", "40", "100")] == \
    [(5.566, 0.623, 30, 0, 30), (4.594, 0.451, 30, 0, 30), (7.187, 1.704, 30, 0, 30)]
assert r3(G["20"]["mean"] - G["40"]["mean"]) == 0.972
assert [r3(m["mean"]) for m in D["20"]["trained"]["together_share"]] == [0.522, 0.544, 0.505, 0.537, 0.564]
assert [r3(m["mean"]) for m in D["100"]["trained"]["together_share"]] == [0.356, 0.387, 0.353, 0.375, 0.414]
assert [r3(D[z]["trained"]["mean_group_count"]["mean"]) for z in ("20", "40", "100")] == [3.353, 3.692, 3.922]
assert D["20"]["vs_scripted"] is None and D["40"]["vs_scripted"] is None
assert [r3(m["mean"]) for m in D["100"]["vs_scripted"]["together_share_delta"]] == [-0.085, -0.072, -0.059, -0.087, -0.045]
assert r3(D["100"]["vs_scripted"]["mean_group_count_delta"]["mean"]) == 0.371
for z in ("20", "40"):
    assert D[z]["vs_matched_uniform"]["seats_with_uniform"] == [0, 1, 2, 3, 4]
    assert max(abs(m["mean"]) for m in D[z]["vs_matched_uniform"]["together_share_delta"].values()) <= 0.0145
assert D["100"]["vs_matched_uniform"]["seats_with_uniform"] == [0, 1, 4]
assert [r3(m["mean"]) for m in D["100"]["vs_matched_uniform"]["together_share_delta"].values()] == [-0.007, -0.020, -0.012]
for z, tr, sc, ct, cs, ht, hs in (("20", 0.416, 0.387, 0.138, 0.055, 87.487, 81.921),
                                  ("40", 0.533, 0.472, 0.109, 0.054, 86.229, 81.634),
                                  ("100", 0.613, 0.538, 0.084, 0.049, 83.810, 76.623)):
    assert (r3(B[z]["trained"]["in_beam_pooled"]), r3(B[z]["scripted"]["in_beam_pooled"])) == (tr, sc), z
    assert (r3(B[z]["trained"]["conducted_pooled"]), r3(B[z]["scripted"]["conducted_pooled"])) == (ct, cs), z
    assert (r3(G[z]["trained_team"]), r3(G[z]["scripted_team"])) == (ht, hs), z
    assert {k for k in range(5) if B[z]["trained"]["in_beam"][k] < B[z]["scripted"]["in_beam"][k]} == {2, 4}, z
    assert max(range(5), key=lambda k: B[z]["trained"]["in_beam"][k] - B[z]["scripted"]["in_beam"][k]) == 0, z
assert [r3(x) for x in B["20"]["trained"]["in_beam"]] == [0.413, 0.440, 0.383, 0.432, 0.404]
assert [r3(x) for x in B["20"]["scripted"]["in_beam"]] == [0.310, 0.426, 0.486, 0.424, 0.417]
print("owed-reads fence: all cells match")
EOF2
```

Accuracy gate (owed reads): **PASS** 2026-10-21 after round 3 (round 1
FAIL: three characterisations; round 2 FAIL: one leftover "two halves"
sentence; round 3: the section PASS, 34 arithmetic, 15 characterisations
SUPPORTED, 0 UNDECIDABLE; the doctrine companion's one word "served" →
"scripted" fixed after the round, no number touched). Companions
copy-checked: F-050's dated note, doctrine rule 7's worked example, the
GEN2-INPUTS shelf entry. Raws are the battery's existing rows (hash per
the Phase C stamp); the reader adds no raw.

## s4/s7 tail reads (2026-10-22; owner "Run the tail reads")

Reader `diag_tails.py`, declared in its docstring and committed before
any replay (cedcd37b). Six uniform-seating worlds (s4's from the step-8
battery, s7's from Phase B), seven cat-runs: every streak of 300 ticks
or more in s4's and s7's 20×20 and 40×40 legs that no read had touched (the s7 investigation read 905029 at 40×40; the s2
stop and the 100×100 rows were read separately). Each pass replays
each world once with the seating collector on its leg's config with the
distress stop watching the target seat alone at 100 ticks
(`abort_seat`, added for this read), so the replay stops 100 ticks into
the target's run. Controls passed in all six: the stopping seat is the
target at exactly 100, and every other seat's longest streak in the
replay is at or under its recorded row maximum. The recorded run was
the cat's only one in six of seven cases (distress ticks equal the
longest streak); Pumpkin in 905004 had 804 distress ticks against a
641 streak, so its window is a run of 100 or more there, not
necessarily the 641.

The replays ran twice: the first pass completed all six and then lost
them to a serialisation error in the reader's final write (a numpy
integer in the controls), so the target cats' re-exposure was at least
2 × (6 × 100 + 25) = 1,250 distress ticks (the windows; Pumpkin's
earlier distress before its window in 905004, up to 163 ticks per
pass, is not recorded) against the 3,645 recorded over the seven runs, and the other seats twice re-experienced only
what precedes each stop (stops at ticks 324, 228, 16,463, 324, 6,910
and 228). The reader now writes after every world.

| world | cat | recorded streak | need | chosen, top three | Drink while thirst < 10 | moving | alone | in 3+ group | shape |
|---|---|---|---|---|---|---|---|---|---|
| s4 20×20 905029 | Miso | 535 | drink | SleepWithKitty0 30, PlayKitty0 23, SleepWithKitty3 18 | 0 | 0.17 | 0.11 | 0.62 | held |
| s4 20×20 905029 | Biscuit (same window, last 25 ticks) | 468 | drink | RestWithKitty0 24, SleepWithKitty0 1 | 0 | 0.00 | 0.00 | 1.00 | held |
| s4 40×40 905017 | Clementine | 687 | cuddle | Drink 22, MoveS 21, MoveN 18 | 22 | 0.60 | 1.00 | 0.00 | pacing |
| s4 40×40 905002 | Biscuit | 602 | cuddle | Drink 47, SleepSolo 12, GroomSelf 8 | 47 | 0.24 | 1.00 | 0.00 | parked mix |
| s4 40×40 905025 | Miso | 389 | cuddle | MoveE 35, MoveW 35, SleepSolo 25 | 0 | 0.70 | 1.00 | 0.00 | pacing |
| s7 40×40 905004 | Pumpkin | 641 | eat | Drink 100 | 100 | 0.00 | 1.00 | 0.00 | parked |
| s7 40×40 905015 | Clementine | 323 | cuddle | Drink 100 | 100 | 0.00 | 1.00 | 0.00 | parked |

The reader's own three-way placement (moving ≥ 0.5 → searching;
Drink-while-sated ≥ half the window and moving ≤ 0.2 → parked; else
other) gives other / searching / other / searching / parked / parked
for the six targets in table order and other for Biscuit's companion
run; the "shape"
column above names what the numbers show within "other" and
"searching", as read here.

**s7's two are water parking, pure.** Pumpkin (eat) and Clementine
(cuddle) each chose Drink on all 100 ticks with thirst at 0.4, never
moved, and were alone throughout; Pumpkin's chow sat a median 7 tiles
away (24 chow tiles on the map) and was never in sight at radius 5.
With the four cases of the s7 investigation (three rotation runs of
84–121 ticks and the 622) that makes six of six s7 distress runs read
water parking, both sizes, two needs (eat and cuddle); every s7 run of
300 or more (641, 622, 323) now has a read, the 641's subject to the
window caveat above.

**s4's four are not that habit.** None is a still cat choosing Drink
throughout:

- The 20×20 tail is a HOLD. Miso, thirst at or past 90 the whole
  window, spent 62% of it in a walk-adjacent group of three or more,
  11% alone, and chose SleepWithKitty0, PlayKitty0, SleepWithKitty3 and
  RestWithKitty0 (77 of 100 ticks) with water a median 10 tiles away
  and never in sight at radius 4. Biscuit's 468-tick run begins 75
  ticks later in a group of three or more throughout, choosing
  RestWithKitty0 on 24 of its 25 ticks (rest activity on 20); kitty
  slots are fixed by id (spec 049 FR-011) and Miso is id 1, so slot 0
  from Biscuit is Miso. By the holding account's definition (3+ group,
  eat or drink ≥ 75, not eating or drinking) Miso's 62% of the window
  in a 3+ group and Biscuit's whole window are held ticks; s4's rows
  predate the account (its step-8 rows carry no `holding` field), so
  it was never printed for them. This is the
  shape the vision follow-up's teacher fix is aimed at, on a trained
  seat.
- Two 40×40 cuddle tails are pacing alone: Clementine (687) moved on
  60% of the window with MoveS 21 against MoveN 18, Miso (389) on 70%
  with MoveE 35 against MoveW 35, each with every other need low
  (Clementine eat 8.6, drink 15.2; Miso eat 38.5, drink 29.0, sleep
  8.0) and no cat walk-adjacent on any tick (sight is not recorded by
  this reader). Clementine also chose Drink on 22 ticks while sated,
  with drink activity on 11.
- The third 40×40 cuddle tail, Biscuit (602), is the parked mix:
  alone, choosing Drink while sated on 47 of 100 ticks (drink activity
  on 23), moving 24%, SleepSolo 12 and GroomSelf 8 — the parked-idle
  mix Phase C read on Kittybear at 40×40 (parked 42% / idle 46% there;
  this reader prints no such split), here on an s4 seat.

Every s4 tail is a cat whose relief needs another cat or a tile it
cannot see: cuddle with no cat adjacent at 40×40 (three cases), or
water out of sight while the group holds (one case, two cats). No
window ended in tending (the stop comes first; the five s4 windows
stopped 289–587 ticks short of their recorded runs; Clementine's s7
window 223 short, Pumpkin's 541 if its window is the 641 run). Descriptive (rule 10): nothing here is a bar
and the certificate stands; s4 sits in rot2 at Biscuit's seat.

## Read (tail reads; about a minute of replays; lab venv, repo root)

```
cd experiments/gen2-cert-battery-2026-10-20 && VIRTUAL_ENV=/Users/elizabethkelly/ai/cloudkitty/experiments/exp-006-character-gen/.venv /Users/elizabethkelly/ai/cloudkitty/experiments/exp-006-character-gen/.venv/bin/python3 -B diag_tails.py --out /private/tmp/diag-tails.json
```

```
python3 - <<'EOF2'
import json
res = json.load(open("/private/tmp/diag-tails.json"))
assert [(c["seating"], c["size"], c["seed"], c["target"], c["recorded_longest"], c["recorded_dist_ticks"]) for c in res] == [
    ("g2-s4", 20, 905029, "Miso", 535, 535), ("g2-s4", 40, 905017, "Clementine", 687, 687),
    ("g2-s4", 40, 905002, "Biscuit", 602, 602), ("g2-s4", 40, 905025, "Miso", 389, 389),
    ("g2-s7", 40, 905004, "Pumpkin", 641, 804), ("g2-s7", 40, 905015, "Clementine", 323, 323)]
assert all(c["controls"]["target_streak_is_100"] and c["controls"]["others_within_row"] for c in res)
assert [c["controls"]["stopped_at"] for c in res] == [324, 228, 16463, 324, 6910, 228]
runs = [r for c in res for r in c["runs"]]
got = [(r["seat"], r["need"], r["length"], r["chosen_top"][:3], r["drink_while_sated"], r["moving_share"], r["alone_share"], r["group3_share"], r["shape"]) for r in runs]
assert got == [
    ("Miso", "drink", 100, [["SleepWithKitty0", 30], ["PlayKitty0", 23], ["SleepWithKitty3", 18]], 0, 0.17, 0.11, 0.62, "other"),
    ("Biscuit", "drink", 25, [["RestWithKitty0", 24], ["SleepWithKitty0", 1]], 0, 0.0, 0.0, 1.0, "other"),
    ("Clementine", "cuddle", 100, [["Drink", 22], ["MoveS", 21], ["MoveN", 18]], 22, 0.6, 1.0, 0.0, "searching"),
    ("Biscuit", "cuddle", 100, [["Drink", 47], ["SleepSolo", 12], ["GroomSelf", 8]], 47, 0.24, 1.0, 0.0, "other"),
    ("Miso", "cuddle", 100, [["MoveE", 35], ["MoveW", 35], ["SleepSolo", 25]], 0, 0.7, 1.0, 0.0, "searching"),
    ("Pumpkin", "eat", 100, [["Drink", 100]], 100, 0.0, 1.0, 0.0, "parked"),
    ("Clementine", "cuddle", 100, [["Drink", 100]], 100, 0.0, 1.0, 0.0, "parked")], got
m, b = runs[0], runs[1]
assert m["span"] == [224, 323] and b["span"] == [299, 323] and m["need_at_start_end"][0] == 90.0
assert sum(n for a, n in m["chosen_top"] if a in ("SleepWithKitty0", "PlayKitty0", "SleepWithKitty3", "RestWithKitty0")) == 77
assert m["relief"]["nearest_median"] == 10.0 and m["relief"]["in_sight_share"] == 0.0
p = runs[5]
assert p["relief"] == {"kind": "Chow", "count_median": 24, "nearest_median": 7.0, "nearest_first_last": [7, 7], "in_sight_share": 0.0}
assert all(r["other_needs_mean"]["drink"] == 0.4 for r in (runs[5], runs[6]))
assert runs[2]["other_needs_mean"]["eat"] == 8.6 and runs[2]["other_needs_mean"]["drink"] == 15.2
assert runs[4]["other_needs_mean"]["eat"] == 38.5 and runs[4]["other_needs_mean"]["drink"] == 29.0 and runs[4]["other_needs_mean"]["sleep"] == 8.0
assert all(r["ended_by_tending_within_30"] in (None, False) for r in runs)
assert 535 + 468 + 687 + 602 + 389 + 641 + 323 == 3645 and 2 * (6 * 100 + 25) == 1250
print("tail reads fence: all cells match")
EOF2
```

Guards: `test_diag_tails.py` (2; lab venv): t1 the shape placement
follows the declared thresholds on the recorded reads; t2
`drink_while_sated` equals an independent per-tick count on a recorded
rot2 stream. Reds on record via `scripts/mutate.sh`, predicted then
confirmed, restored at 2 passed: the searching threshold 0.5 → 0.9 →
t1 (Clementine at 0.60 becomes other); thirst < 10 → < 100 → t2. The
collector's `abort_seat` guard (`test_seating_g2.py`, 9) went red on
`abort_due` reading the roster max (predicted, confirmed, restored at
9 passed; recorded in the commit message of this section).

Accuracy gate (tail reads): **PASS** 2026-10-22 after round 3 (round 1
FAIL: placement order, "three needs", phase labels, two chosen-vs-activity
counts, "in sight", an unscoped shortfall; round 2 FAIL: the round-1
slot correction was itself wrong (kitty slots are by id, FR-011), plus
five WEAK; round 3: ~96 arithmetic matched, 7 threshold sourced, 21 of 22
characterisations SUPPORTED, 1 WEAK fixed after the round (the 641's
read is subject to the window caveat), 1 UNDECIDABLE = the abort_due red,
recorded in this section's commit message; 13 provenance). Round 1
re-ran the Read fence (a third replay pass, fresh JSON deep-identical to
the recorded); rounds 2 and 3 reused that fresh JSON rather than replay
again, for the covered minds' sake. Raws are the battery's existing rows
(hash per the Phase C stamp); the reader adds no raw, and the replay
streams are not kept.
