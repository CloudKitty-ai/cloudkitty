"""Purr semantics from the census purr-log.

Row: [id, x, y, happiness, [eat,drink,sleep,play,cuddle,bath], act,
cosleep, purred, legal]. Purr at tick t was DECIDED from state at t-1;
all conditioning uses the t-1 row (the legal flag already does).

A. emitter state: emission vs declined-legal ticks
B. event-triggered trajectories around emission (dist to nearest, contact,
   cosleep), offsets -30..+30
C. answer structure: latency to another cat's purr within the 10-tick
   window, pair matrix, matched baseline from declined-legal ticks
D. P(enter cosleep within 25 | not cosleeping now): purr vs declined-legal
"""
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

SP = Path(__file__).parent / "t15" / "purr-log"
ACT = ["Idle", "Resting", "Sleeping", "Eating", "Drinking", "Playing",
       "Grooming"]
NEEDS = ["eat", "drink", "sleep", "play", "cuddle", "bath"]
WINDOW = 10
HORIZON = 25
TRAJ = 30

stateA = {"emit": defaultdict(float), "declined": defaultdict(float)}
countA = {"emit": 0, "declined": 0}
actA = {"emit": Counter(), "declined": Counter()}
traj = {k: np.zeros(2 * TRAJ + 1) for k in ("dist", "contact", "cosleep")}
traj_n = np.zeros(2 * TRAJ + 1)
answered = {"purr": 0, "purr_n": 0, "base": 0, "base_n": 0}
latency = Counter()
pair_answers = Counter()
cosleep_soon = {"purr": [0, 0], "declined": [0, 0]}  # [entered, n]

for f in sorted(SP.glob("seed-*.jsonl")):
    ticks = []          # per tick: {id: row}
    purr_events = []    # (tick_index, id)
    with open(f) as fh:
        for line in fh:
            d = json.loads(line)
            row = {k[0]: k for k in d["k"]}
            ticks.append(row)
            for kid, k in row.items():
                if k[7]:
                    purr_events.append((len(ticks) - 1, kid))
    T = len(ticks)
    ids = list(ticks[0].keys())

    def dist(a, b, i):
        ra, rb = ticks[i][a], ticks[i][b]
        return abs(ra[1] - rb[1]) + abs(ra[2] - rb[2])

    def nearest(kid, i):
        return min(dist(kid, o, i) for o in ids if o != kid)

    # A + C-baseline + D rows: walk every (tick, kitty) with legality.
    for i in range(2, T):
        for kid, k in ticks[i].items():
            legal, purred = k[8], k[7]
            if not legal and not purred:
                continue
            prev = ticks[i - 1][kid]
            key = "emit" if purred else "declined"
            countA[key] += 1
            s = stateA[key]
            s["happiness"] += prev[3]
            for j, n in enumerate(NEEDS):
                s[n] += prev[4][j]
            s["dist_nearest"] += min(
                abs(prev[1] - ticks[i - 1][o][1])
                + abs(prev[2] - ticks[i - 1][o][2])
                for o in ids if o != kid)
            s["in_contact"] += any(
                abs(prev[1] - ticks[i - 1][o][1])
                + abs(prev[2] - ticks[i - 1][o][2]) <= 1
                for o in ids if o != kid)
            pprev = ticks[i - 2][kid]
            s["moving"] += (prev[1], prev[2]) != (pprev[1], pprev[2])
            actA[key][ACT[prev[5]]] += 1
            # C baseline / C numerator: another cat purrs in (i, i+W]?
            ans = None
            for j in range(i + 1, min(T, i + WINDOW + 1)):
                hit = [o for o, r in ticks[j].items() if o != kid and r[7]]
                if hit:
                    ans = (j - i, hit[0])
                    break
            if purred:
                answered["purr_n"] += 1
                if ans:
                    answered["purr"] += 1
                    latency[ans[0]] += 1
                    pair_answers[(kid, ans[1])] += 1
            else:
                answered["base_n"] += 1
                answered["base"] += ans is not None
            # D: cosleep entry within HORIZON, among not-cosleeping-now.
            if not k[6]:
                cs = cosleep_soon[key if key != "emit" else "purr"]
                cs[1] += 1
                cs[0] += any(ticks[j][kid][6]
                             for j in range(i + 1, min(T, i + HORIZON + 1)))

    # B: trajectories around emission.
    for (i, kid) in purr_events:
        if i - TRAJ < 0 or i + TRAJ >= T:
            continue
        for off in range(-TRAJ, TRAJ + 1):
            j = i + off
            k = ticks[j][kid]
            traj["dist"][off + TRAJ] += nearest(kid, j)
            traj["contact"][off + TRAJ] += nearest(kid, j) <= 1
            traj["cosleep"][off + TRAJ] += k[6]
            traj_n[off + TRAJ] += 1
    print(f"{f.name}: {T} ticks, {len(purr_events)} purrs")

out = {"A_state": {}, "A_activity": {}, "B_traj": {}, "C": {}, "D": {}}
for key in ("emit", "declined"):
    n = max(1, countA[key])
    out["A_state"][key] = {k: v / n for k, v in stateA[key].items()}
    out["A_state"][key]["n"] = countA[key]
    out["A_activity"][key] = {a: c / n for a, c in actA[key].most_common()}
n = np.maximum(traj_n, 1)
out["B_traj"] = {k: (v / n).round(4).tolist() for k, v in traj.items()}
out["C"] = {
    "p_answered_within_10": answered["purr"] / max(1, answered["purr_n"]),
    "p_baseline_other_purr_within_10":
        answered["base"] / max(1, answered["base_n"]),
    "latency_hist": dict(sorted(latency.items())),
    "pair_matrix": {f"{a}->{b}": c
                    for (a, b), c in sorted(pair_answers.items())},
}
out["D"] = {k: {"p_cosleep_within_25": v[0] / max(1, v[1]), "n": v[1]}
            for k, v in cosleep_soon.items()}
print(json.dumps({k: v for k, v in out.items() if k != "B_traj"}, indent=1))
for k, v in out["B_traj"].items():
    print(f"traj {k}: t-30 {v[0]:.3f}  t-10 {v[20]:.3f}  t-3 {v[27]:.3f}  "
          f"t0 {v[30]:.3f}  t+3 {v[33]:.3f}  t+10 {v[40]:.3f}  "
          f"t+30 {v[60]:.3f}")
Path(__file__).with_name("purr_semantics.json").write_text(
    json.dumps(out, indent=1) + "\n")
