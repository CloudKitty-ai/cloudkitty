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
