# Seating analysis v2 — the five-network candidate roster (2026-10-21)

Declaration: `DECLARATION.md` (c2566ade), committed before data. The
scripted reference and all five rotation rosters ran on worlds
905001–905005 × 20,000 ticks; no stop fired. Everything here is a
reading (doctrine rule 10), never a bar.

## Rosters (rotation; seat order Miso, Biscuit, Pumpkin, Kittybear, Clementine)

| roster | seats | team happiness (SD) | worst-cat p5 (SD) | worst-cat gap | worst distress streak |
|---|---|---|---|---|---|
| rot1 | s1 s2 s4 s6 s7 | 87.453 (0.11) | 81.05 (0.15) | 7.84 | 121 |
| rot2 | s2 s4 s6 s7 s1 | 87.514 (0.13) | 80.75 (0.36) | 7.73 | 0 |
| rot3 | s4 s6 s7 s1 s2 | 87.473 (0.11) | 80.70 (0.29) | 7.73 | 94 |
| rot4 | s6 s7 s1 s2 s4 | 87.463 (0.10) | 80.83 (0.52) | 7.72 | 29 |
| rot5 | s7 s1 s2 s4 s6 | 87.483 (0.07) | 80.51 (0.36) | 7.72 | 40 |
| scripted | all teacher | 81.964 (0.68) | 67.44 (3.96) | 12.54 | 194 |

**The declared proposal rule ends in a tie.** No roster had an abort.
On worst-cat p5, rot1 leads (81.05), but rot4 (−0.22, inside SD 0.52)
and rot2 (−0.30, inside SD 0.36) are ties by the declared test; rot3
(−0.35 against SD 0.29) and rot5 (−0.54 against SD 0.36) fall
behind. Within the tied three, team happiness is also a tie (largest
difference 0.061 against SD 0.13). Ties go to the owner.

## Model by seat (happiness mean / p5, 5 worlds per cell)

| model | Miso | Biscuit | Pumpkin | Kittybear | Clementine |
|---|---|---|---|---|---|
| s1 | 87.45/81.6 | 87.51/82.0 | 87.08/80.8 | 87.41/81.6 | 86.83/80.7 |
| s2 | 87.72/82.0 | 87.51/81.7 | 87.33/81.2 | 87.54/81.8 | 86.93/80.7 |
| s4 | 87.90/82.3 | 87.88/82.5 | 87.69/81.9 | 87.87/82.4 | 87.20/81.2 |
| s6 | 87.25/81.9 | 87.15/81.6 | 86.91/81.0 | 87.03/81.1 | 86.55/80.5 |
| s7 | 88.15/82.8 | 88.25/82.8 | 87.98/82.1 | 88.23/82.8 | 87.58/81.7 |
| scripted | 82.25/71.4 | 82.10/70.1 | 81.79/69.6 | 82.67/71.6 | 81.02/67.4 |

s7 is first, s4 second and s6 last in every seat, a spread of about
one point; s2 sits above s1 in four seats, and in Biscuit's seat s1
leads by 0.002 (a tie at this precision). Clementine's seat is the
hardest for every model. Model and seat add up with no visible
interaction, which is why seat order barely moves the roster.

## Behavior by model (pooled over its 25 seat-worlds)

| model | idle | rest | sleep | play | groom | contact | partnered | nearest cat (median) | home range | play-proposal share | happiness mean/p5 | worst streak |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| s1 | 0.557 | 0.122 | 0.074 | 0.188 | 0.036 | 0.525 | 0.212 | 1.3 | 221 | 0.162 | 87.26/81.36 | 29 |
| s2 | 0.560 | 0.105 | 0.072 | 0.196 | 0.043 | 0.526 | 0.209 | 1.2 | 222 | 0.156 | 87.41/81.47 | 40 |
| s4 | 0.553 | 0.111 | 0.078 | 0.189 | 0.045 | 0.530 | 0.217 | 1.2 | 216 | 0.166 | 87.71/82.05 | 0 |
| s6 | 0.573 | 0.088 | 0.082 | 0.207 | 0.029 | 0.558 | 0.213 | 1.1 | 218 | 0.183 | 86.98/81.21 | 0 |
| s7 | 0.560 | 0.102 | 0.086 | 0.181 | 0.045 | 0.527 | 0.207 | 1.1 | 223 | 0.145 | 88.04/82.48 | 121 |
| scripted | 0.615 | 0.161 | 0.068 | 0.104 | 0.035 | 0.586 | 0.210 | 1.0 | 223 | n/a | 81.96/70.04 | 194 |

The five networks share one character: idle about 56%, playing
18–21%, in contact with another cat about half the time, the same
territory size, and the same top words (HereSunbeam, then HereWater,
silent about 72%). The differences are small: s6 plays most, proposes
play most (0.183) and sits in contact most, with the lowest happiness;
s7 proposes play least (0.145) with the highest happiness and the one
long streak (121). The teacher idles and rests more, plays about half
as much, and carries a far worse bottom tail (p5 70.04 against
81.2–82.5).

## Read (seconds; stdlib python3, repo root)

```
cd experiments/seating-analysis-g2-2026-10-21 && VIRTUAL_ENV=/Users/elizabethkelly/ai/cloudkitty/experiments/exp-006-character-gen/.venv /Users/elizabethkelly/ai/cloudkitty/experiments/exp-006-character-gen/.venv/bin/python3 -B seating_read_g2.py --raws results-raw/*/streams-*.npz --out seating-read-g2.json --md
```

```
python3 - <<'EOF2'
import json
d = json.load(open("experiments/seating-analysis-g2-2026-10-21/seating-read-g2.json"))
R = d["rosters"]
exp = {"g2-rot1": (87.453, 81.05, 7.84, 121), "g2-rot2": (87.514, 80.75, 7.73, 0), "g2-rot3": (87.473, 80.70, 7.73, 94),
       "g2-rot4": (87.463, 80.83, 7.72, 29), "g2-rot5": (87.483, 80.51, 7.72, 40), "scripted": (81.964, 67.44, 12.54, 194)}
for r, (t, p5, gap, st) in exp.items():
    x = R[r]
    assert (round(x["team_hap"]["mean"], 3), round(x["worst_cat_p5"]["mean"], 2), round(x["gap_mean"], 2), x["distress_streak_max"]) == (t, p5, gap, st), r
    assert len(x["seeds"]) == 5 and x["aborted"] == [], r
sd = {r: round(R[r]["worst_cat_p5"]["sd"], 2) for r in exp}
assert sd == {"g2-rot1": 0.15, "g2-rot2": 0.36, "g2-rot3": 0.29, "g2-rot4": 0.52, "g2-rot5": 0.36, "scripted": 3.96}, sd
C = d["cells"]
k = lambda n, c: f"trunk-{n}@{c}" if n != "scripted" else f"scripted@{c}"
assert [round(C[k("s7", c)]["hap_mean"], 2) for c in ("Miso", "Biscuit", "Pumpkin", "Kittybear", "Clementine")] == [88.15, 88.25, 87.98, 88.23, 87.58]
assert [round(C[k("s6", c)]["hap_mean"], 2) for c in ("Miso", "Biscuit", "Pumpkin", "Kittybear", "Clementine")] == [87.25, 87.15, 86.91, 87.03, 86.55]
for c in ("Miso", "Biscuit", "Pumpkin", "Kittybear", "Clementine"):
    order = sorted(("s1", "s2", "s4", "s6", "s7"), key=lambda n: -C[k(n, c)]["hap_mean"])
    assert order[:2] == ["s7", "s4"] and order[-1] == "s6", (c, order)
    assert (order[2:4] == ["s2", "s1"]) == (c != "Biscuit"), (c, order)
assert round(C[k("s1", "Biscuit")]["hap_mean"] - C[k("s2", "Biscuit")]["hap_mean"], 3) == 0.002
assert all(C[k(n, "Clementine")]["hap_mean"] == min(C[k(n, c)]["hap_mean"] for c in ("Miso", "Biscuit", "Pumpkin", "Kittybear", "Clementine")) for n in ("s1", "s2", "s4", "s6", "s7"))
print("seating analysis v2 fence: all cells match")
EOF2
```

```
python3 - <<'EOF2'
import json
import statistics as st
d = json.load(open("experiments/seating-analysis-g2-2026-10-21/seating-read-g2.json"))
P = {}
for l in d["legs"]:
    for k, spec in enumerate(l["seats"]):
        n = "scripted" if spec == "scripted" else spec.split("-")[-1]
        c = l["cats"][k]
        P.setdefault(n, []).append((c["activity_share"], c["grouped"]["contact"], c["grouped"]["partnered"],
                                    c["nearest_cat"]["median"], c["home_range_tiles"], l["play_share"][k],
                                    c["hap"]["mean"], c["hap"]["p5"], l["distress_streak_max"][k]))
want = {"s1": (0.557, 0.122, 0.074, 0.188, 0.036, 0.525, 0.212, 1.3, 221, 0.162, 87.26, 81.36, 29),
        "s2": (0.560, 0.105, 0.072, 0.196, 0.043, 0.526, 0.209, 1.2, 222, 0.156, 87.41, 81.47, 40),
        "s4": (0.553, 0.111, 0.078, 0.189, 0.045, 0.530, 0.217, 1.2, 216, 0.166, 87.71, 82.05, 0),
        "s6": (0.573, 0.088, 0.082, 0.207, 0.029, 0.558, 0.213, 1.1, 218, 0.183, 86.98, 81.21, 0),
        "s7": (0.560, 0.102, 0.086, 0.181, 0.045, 0.527, 0.207, 1.1, 223, 0.145, 88.04, 82.48, 121),
        "scripted": (0.615, 0.161, 0.068, 0.104, 0.035, 0.586, 0.210, 1.0, 223, None, 81.96, 70.04, 194)}
for n, w in want.items():
    rows = P[n]
    assert len(rows) == 25, n
    m = lambda i: st.mean(r[i] for r in rows)
    act = [st.mean(r[0][j] for r in rows) for j in (0, 1, 2, 5, 6)]
    got = (*[round(a, 3) for a in act], round(m(1), 3), round(m(2), 3), round(m(3), 1), round(m(4)),
           None if rows[0][5] is None else round(m(5), 3), round(m(6), 2), round(m(7), 2), max(r[8] for r in rows))
    assert got == w, (n, got)
print("behavior table fence: all cells match")
EOF2
```
