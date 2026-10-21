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

## Verbosity vs Gen 1 (2026-10-21; owner: "give me a comparison of verbosity vs gen 1")

Gen 1 = the served gen1-A roster's seating analysis (5 worlds × 20,000
ticks on its served world). Gen 2 = rot2, the roster chosen for
certification (5 worlds × 20,000 ticks on the Gen 2 world). Both read
the chosen message head with the same table (the engine's HEAD_KINDS,
corrected 2026-10-21). The worlds differ (Gen 2 has hidden needs, the
sleep floor, six beams and the vision law), so this compares shapes,
not cells (the inputs doc's cross-generation rule).

| | Gen 1 (gen1-A) | Gen 2 (rot2) |
|---|---|---|
| speaks on (share of cat-ticks) | 29.6% (seeds 29.5–29.8%) | 27.7% (seeds 27.2–28.0%) |
| per-seat range | 22.7% (Clementine) – 37.0% (Biscuit) | 27.0% (Biscuit) – 28.3% (Miso) |
| want words, share of spoken | 7.4% | 30.5% |
| here words | 45.4% | 69.5% |
| free register (mew, purr, chirp, trill, ekekek) | 47.2% | 0 |
| top words | Purr 24.3%, HereFood 16.2%, HereWater 16.1% | HereSunbeam 26.0%, HereWater 17.9%, HereFood 16.1% |

Reading. Gen 2 is slightly quieter overall (27.7% against 29.6%, a
gap well outside either generation's seed spread), and it talks about
different things. Want words rose about fourfold (7.4% → 30.5%;
WantSleep 11.9% and WantEat 7.1% lead), the shape hidden needs
predict, since a want-word is now the only way a friend learns what a
cat needs. The free register vanished: no purr, mew, chirp, trill or
ekekek in any of the 2.5M cat-ticks of the five rotations. That is
inherited, not lost: the Gen 2 teacher emits none (0 free words in a
10-rollout sample of the training corpus, about 1M labels, 24.8%
spoken), so the clone had none to copy, and whether free words emerge
unseeded is the prereg's §8.1 arm. Gen 1's seats spoke in distinct
dialects (a 14-point spread across five distinct networks); Gen 2's five networks speak alike (a 1.3-point spread). Gen 2
also talks more when needier (21.0% → 27.1% → 28.5% across own
worst-need bins < 15, 15–25, ≥ 25; Gen 1 flat at 29.0–30.3%), with a
caveat: under the sleep floor Gen 2 cats spend 56% of cat-ticks in the
top bin against Gen 1's 9%, so the bins do not line up across
generations.

## Read (verbosity; seconds; lab venv, repo root)

```
cd experiments && VIRTUAL_ENV=/Users/elizabethkelly/ai/cloudkitty/experiments/exp-006-character-gen/.venv /Users/elizabethkelly/ai/cloudkitty/experiments/exp-006-character-gen/.venv/bin/python3 -B - <<'EOF2'
import glob, sys
import numpy as np
sys.path.insert(0, "seating-analysis-2026-09-28")
import seating_read as v1
N = v1.MSG_NAMES
G = {"want": {"WantEat", "WantDrink", "WantPlay", "WantCuddle", "WantBath", "WantSleep"},
     "here": {"HereFood", "HereWater", "HereCritter", "HereSunbeam"},
     "free": {"Mew", "Purr", "Chirp", "Trill", "Ekekek"}}
def read(pat):
    fs = sorted(glob.glob(pat)); assert len(fs) == 5, fs
    seeds, cats, c, binsn, binsd = [], np.zeros(5), np.zeros(16), np.zeros(3), np.zeros(3)
    for f in fs:
        z = np.load(f); m = z["msg"]; s = m > 0
        seeds.append(s.mean()); cats += s.mean(0) / 5; c += np.bincount(m.ravel(), minlength=16)
        b = np.digitize(z["needs"][:, :, list(v1.GATE_NEED_IDX)].max(2), (15.0, 25.0))
        for i in range(3):
            binsn[i] += s[b == i].sum(); binsd[i] += (b == i).sum()
    sp = c[1:].sum()
    return (round(float(np.mean(seeds)), 3), [round(float(x), 3) for x in (min(seeds), max(seeds))],
            [round(float(x), 3) for x in cats], {g: round(float(sum(c[N.index(n)] for n in S) / sp), 3) for g, S in G.items()},
            [round(float(x), 3) for x in binsn / binsd], round(float(binsd[2] / binsd.sum()), 2), c)
g1 = read("seating-analysis-2026-09-28/results-raw/streams-90050[1-5].npz")
g2 = read("seating-analysis-g2-2026-10-21/results-raw/g2-rot2/streams-90500[1-5].npz")
assert g1[:6] == (0.296, [0.295, 0.298], [0.312, 0.37, 0.31, 0.262, 0.227], {"want": 0.074, "here": 0.454, "free": 0.472}, [0.3, 0.29, 0.303], 0.09), g1[:6]
assert g2[:6] == (0.277, [0.272, 0.28], [0.283, 0.27, 0.278, 0.277, 0.275], {"want": 0.305, "here": 0.695, "free": 0.0}, [0.21, 0.271, 0.285], 0.56), g2[:6]
sp2 = g2[6][1:].sum()
assert [round(float(g2[6][N.index(n)] / sp2), 3) for n in ("HereSunbeam", "HereWater", "HereFood", "WantSleep", "WantEat")] == [0.26, 0.179, 0.161, 0.119, 0.071]
allrot = sum(np.bincount(np.load(f)["msg"].ravel(), minlength=16) for f in glob.glob("seating-analysis-g2-2026-10-21/results-raw/g2-rot*/streams-*.npz"))
assert all(allrot[N.index(n)] == 0 for n in G["free"]) and allrot.sum() == 2_500_000
corp = sum(np.bincount(np.asarray(np.load(f, mmap_mode="r")).ravel(), minlength=16)[:16] for f in sorted(glob.glob("gen2-collection-driver-2026-10-14/results-raw/full-100/r0*/config-*-rollout-*/label_msg.npy")))
assert all(corp[N.index(n)] == 0 for n in G["free"]) and round(float(corp[1:].sum() / corp.sum()), 3) == 0.248
print("verbosity fence: all cells match")
EOF2
```

## The certified roster: standing analysis (2026-10-21; owner: "run the analysis after we certify it")

rot2 (Miso s2, Biscuit s4, Pumpkin s6, Kittybear s7, Clementine s1),
certified in the battery (`../gen2-cert-battery-2026-10-20/RESULTS.md`
§Phase C). The rotation already ran this exact roster on the served
world, 5 worlds × 20,000 ticks; a fresh collection on those seeds
would be byte-identical (the collector is deterministic and held equal
to the harness), so the standing analysis reads those streams. No new
exposure. Read with v1's own reader and printer, so the report sits in
the Gen 1 baseline's format (`../seating-analysis-2026-09-28/RESULTS.md`).

```
nash per seed: [0.8764, 0.8739, 0.8739, 0.8757, 0.8733]
gap mean/p95 per seed: [(7.49, 12.93), (7.79, 13.12), (7.83, 13.55), (7.69, 12.93), (7.84, 13.47)]

| cat | Idle | Rest | Sleep | Eat | Drink | Play | Groom | contact | company | partnered | nearest med/p95 | hap mean/p5 | H bits | transH | home |
| Miso | 0.537 | 0.091 | 0.121 | 0.008 | 0.016 | 0.186 | 0.040 | 0.525 | 0.815 | 0.209 | 1.0/9.8 | 87.7/82.0 | 1.96 | 1.11 | 209 |
| Biscuit | 0.545 | 0.103 | 0.071 | 0.007 | 0.013 | 0.221 | 0.041 | 0.547 | 0.828 | 0.215 | 1.0/9.4 | 87.9/82.5 | 1.89 | 1.11 | 215 |
| Pumpkin | 0.612 | 0.086 | 0.051 | 0.012 | 0.014 | 0.205 | 0.020 | 0.506 | 0.786 | 0.186 | 1.4/11.0 | 86.9/81.0 | 1.70 | 1.06 | 234 |
| Kittybear | 0.551 | 0.094 | 0.080 | 0.010 | 0.013 | 0.185 | 0.066 | 0.530 | 0.805 | 0.199 | 1.0/10.4 | 88.2/82.8 | 1.95 | 1.14 | 228 |
| Clementine | 0.553 | 0.154 | 0.071 | 0.009 | 0.015 | 0.168 | 0.031 | 0.573 | 0.857 | 0.253 | 1.0/8.4 | 86.8/80.7 | 1.90 | 1.11 | 216 |

PAIRS (top five by pair ticks): Biscuit-Clementine 1851 (reciprocity 0.93), Miso-Clementine 1717 (0.93),
Pumpkin-Clementine 1598 (0.84), Kittybear-Clementine 1590 (0.91), Miso-Biscuit 1468 (0.94)
Top partner: Clementine for Miso, Biscuit, Pumpkin and Kittybear; Biscuit for Clementine.
Distress onsets: 0 for every cat in these five worlds.
ROUTINE dominant lag per seed: Miso [995, 58, 60, 59, 59]; Biscuit [115, 107, 110, 112, 109];
Pumpkin [1143, 1676, 165, 1606, 159]; Kittybear [111, 104, 1518, 2163, 917]; Clementine [112, 107, 736, 61, 65]
CONVERGENCE (successive 2,000-tick window JS): first-3 means 0.247-0.406, last-3 means 0.282-0.471
```

Reading:

- **Welfare.** Happiness 86.8–88.2 by cat (p5 80.7–82.8); the
  worst-cat gap averages 7.5–7.8. No distress onset in any of the five
  worlds (the certification legs, 30 worlds per size, carry its tail).
- **Social structure: a hub, not dyads.** Clementine (the cuddle-heavy
  seat) is the top partner of all four other cats and the most
  connected (contact 0.573, partnered 0.253). Biscuit–Clementine is
  the strongest pair and it is mutual, the same pair that led Gen 1;
  Gen 1's other dyad (Pumpkin–Kittybear) and its unpaired Miso do not
  recur. Reciprocity is high everywhere (0.84–0.97).
- **Routine appears.** Biscuit's sleep repeats on a ~110-tick cycle in
  all five worlds (107–115), and Miso's on ~59 in four; Clementine
  sits near 61–112 in four. Gen 1 found no stable routine.
- **Speech.** About 72% silent for every cat, HereSunbeam first for
  each; Miso's third word is WantSleep (see §Verbosity vs Gen 1).
- **Territory.** Home ranges 209–234 tiles; pairwise territory JS
  0.097–0.114, more uniform overlap than Gen 1's.
- **Heatmaps keep moving.** Successive 2,000-tick windows differ by JS
  0.25–0.41 over each world's first three windows and 0.28–0.47 over
  its last three (Gen 1: 0.17–0.22 and 0.16–0.25), and the last-three
  mean sits above the first-three in all five worlds: no settling. A
  Gen 2 heatmap needs a longer horizon than Gen 1's to be
  representative.

Cross-generation notes compare shapes, not cells (different worlds).

## Read (certified roster; under a minute; lab venv, repo root)

```
experiments/exp-006-character-gen/.venv/bin/python -B experiments/seating-analysis-2026-09-28/seating_read.py --raws experiments/seating-analysis-g2-2026-10-21/results-raw/g2-rot2/streams-905001.npz experiments/seating-analysis-g2-2026-10-21/results-raw/g2-rot2/streams-905002.npz experiments/seating-analysis-g2-2026-10-21/results-raw/g2-rot2/streams-905003.npz experiments/seating-analysis-g2-2026-10-21/results-raw/g2-rot2/streams-905004.npz experiments/seating-analysis-g2-2026-10-21/results-raw/g2-rot2/streams-905005.npz --out experiments/seating-analysis-g2-2026-10-21/certified-rot2-read.json && experiments/exp-006-character-gen/.venv/bin/python -B experiments/seating-analysis-2026-09-28/seating_summary.py experiments/seating-analysis-g2-2026-10-21/certified-rot2-read.json
```

```
python3 - <<'EOF2'
import json
import statistics as st
d = json.load(open("experiments/seating-analysis-g2-2026-10-21/certified-rot2-read.json"))
L = d["legs"]
assert [l["seed"] for l in L] == [905001, 905002, 905003, 905004, 905005] and all(l["ticks"] == 20000 for l in L)
assert [round(l["welfare"]["nash_mean"], 4) for l in L] == [0.8764, 0.8739, 0.8739, 0.8757, 0.8733]
cats = ["Miso", "Biscuit", "Pumpkin", "Kittybear", "Clementine"]
hap = [round(st.mean(l["cats"][k]["hap"]["mean"] for l in L), 1) for k in range(5)]
assert hap == [87.7, 87.9, 86.9, 88.2, 86.8], hap
assert all(l["cats"][k]["distress"]["onsets"] == 0 for l in L for k in range(5))
pt = {p: st.mean(l["pairs"][p]["pair_ticks"] for l in L) for p in L[0]["pairs"]}
top = sorted(pt, key=lambda p: -pt[p])[:5]
assert top == ["Biscuit-Clementine", "Miso-Clementine", "Pumpkin-Clementine", "Kittybear-Clementine", "Miso-Biscuit"], top
assert [l["cats"][1]["routine"]["dominant_lag"] for l in L] == [115, 107, 110, 112, 109]
assert [l["cats"][0]["routine"]["dominant_lag"] for l in L] == [995, 58, 60, 59, 59]
f3 = [st.mean(l["convergence_js"][:3]) for l in L]; l3 = [st.mean(l["convergence_js"][-3:]) for l in L]
assert (round(min(f3), 2), round(max(f3), 2), round(min(l3), 2), round(max(l3), 2)) == (0.25, 0.41, 0.28, 0.47), (f3, l3)
assert all(b > a for a, b in zip(f3, l3))
print("certified-roster analysis fence: all cells match")
EOF2
```

## Correction (2026-10-21): every scene's last tick was missing

Owner, 2026-10-21, verbatim: "Those eat and drink numbers look
suspiciously low (e. g. 0.007 for biscuit)". They were low because the
instrument dropped ticks. The collector reads each cat's activity and
partner from the end-of-tick state, after `resolve_activity_ends` has
closed every scene that finished that tick, so a scene's last tick
read as Idle with no partner. That is the F-031 instrument rule; v1
broke it and this port inherited the break. Meals and drinks last two
ticks, so at most one tick of each showed, and a meal that takes a
bowl's last serving ends on its first tick (`out_of_chow` ends a meal
whatever its minimum) and never showed at all. Every activity share,
everything built on one, and every partner-based number read low;
Idle read high. Happiness, distress, speech, positions and the
play-proposal share read neither flag and stand.

Her ruling, verbatim: "1 for gen 2": an exact re-collection for Gen 2,
the flag-only method for Gen 1 (DECLARATION.md Amendment 1, 9920a6f3,
declared before the data). The collector now records each cat's
applied action and partner every tick (855bfc20; eight guards, each
seen red, recorded in 391b43bb). The scripted reference and rot2
re-ran on 905001–905005 × 20,000, and all ten worlds came out
byte-identical to the originals in every stream the first collection
recorded: the same worlds, now read exactly. No stop fired.

### The certified roster, corrected

Replaces the printer output in §The certified roster (the same reader
and printer on the new streams):

```
| cat | Idle | Rest | Sleep | Eat | Drink | Play | Groom | contact | company | partnered | nearest med/p95 | hap mean/p5 | H bits | transH | home |
| Miso | 0.305 | 0.099 | 0.142 | 0.019 | 0.033 | 0.350 | 0.053 | 0.525 | 0.815 | 0.292 | 1.0/9.8 | 87.7/82.0 | 2.28 | 1.17 | 209 |
| Biscuit | 0.295 | 0.111 | 0.084 | 0.018 | 0.025 | 0.413 | 0.055 | 0.547 | 0.828 | 0.315 | 1.0/9.4 | 87.9/82.5 | 2.17 | 1.15 | 215 |
| Pumpkin | 0.375 | 0.093 | 0.060 | 0.030 | 0.029 | 0.386 | 0.026 | 0.506 | 0.786 | 0.274 | 1.4/11.0 | 86.9/81.0 | 2.06 | 1.11 | 234 |
| Kittybear | 0.316 | 0.102 | 0.096 | 0.026 | 0.026 | 0.347 | 0.088 | 0.530 | 0.805 | 0.288 | 1.0/10.4 | 88.2/82.8 | 2.29 | 1.21 | 228 |
| Clementine | 0.337 | 0.168 | 0.084 | 0.022 | 0.030 | 0.319 | 0.040 | 0.573 | 0.857 | 0.350 | 1.0/8.4 | 86.8/80.7 | 2.25 | 1.12 | 216 |

eat / drink cadence (median ticks between session starts): Miso 97/64, Biscuit 100/83,
Pumpkin 55/74, Kittybear 71/87, Clementine 80/73
PAIRS (top five by pair ticks): Biscuit-Clementine 2433 (reciprocity 0.96), Miso-Clementine 2159 (0.93),
Pumpkin-Clementine 2066 (0.88), Kittybear-Clementine 2024 (0.92), Miso-Biscuit 1952 (0.91)
Top partner: Clementine for Miso, Biscuit, Pumpkin and Kittybear; Biscuit for Clementine.
ROUTINE dominant lag per seed: Miso [61, 59, 59, 59, 59]; Biscuit [115, 106, 110, 112, 109];
Pumpkin [1142, 1676, 165, 1606, 159]; Kittybear [110, 104, 1518, 2163, 692]; Clementine [112, 107, 737, 61, 114]
```

How much the flags hid (flag → exact, share of ticks):

| cat | idle | play | eat | drink | rest | sleep | groom | partnered |
|---|---|---|---|---|---|---|---|---|
| Miso | 0.537 → 0.305 | 0.186 → 0.350 | 0.008 → 0.019 | 0.016 → 0.033 | 0.091 → 0.099 | 0.121 → 0.142 | 0.040 → 0.053 | 0.209 → 0.292 |
| Biscuit | 0.545 → 0.295 | 0.221 → 0.413 | 0.007 → 0.018 | 0.013 → 0.025 | 0.103 → 0.111 | 0.071 → 0.084 | 0.041 → 0.055 | 0.215 → 0.315 |
| Pumpkin | 0.612 → 0.375 | 0.205 → 0.386 | 0.012 → 0.030 | 0.014 → 0.029 | 0.086 → 0.093 | 0.051 → 0.060 | 0.020 → 0.026 | 0.186 → 0.274 |
| Kittybear | 0.551 → 0.316 | 0.185 → 0.347 | 0.010 → 0.026 | 0.013 → 0.026 | 0.094 → 0.102 | 0.080 → 0.096 | 0.066 → 0.088 | 0.199 → 0.288 |
| Clementine | 0.553 → 0.337 | 0.168 → 0.319 | 0.009 → 0.022 | 0.015 → 0.030 | 0.154 → 0.168 | 0.071 → 0.084 | 0.031 → 0.040 | 0.253 → 0.350 |

Sentences in §The certified roster that change (quoted, then
corrected):

- "the most connected (contact 0.573, partnered 0.253)": partnered
  0.350, still the most.
- "Reciprocity is high everywhere (0.84–0.97)": 0.88–0.97.
- "Biscuit's sleep repeats on a ~110-tick cycle in all five worlds
  (107–115), and Miso's on ~59 in four; Clementine sits near 61–112 in
  four": Biscuit 106–115 in all five; Miso 59–61 in all five (the
  first world's 995 came from the hidden ticks); Clementine 61–114 in
  four.

The rest of that section stands: welfare, the hub (the same top five
pairs and the same top partners), speech, territory and the heatmaps.

### The model table (§Behavior by model)

Its activity and partnered columns read the rotation's streams, which
carry no applied action, so they hold the same bias. Quoted: "The five
networks share one character: idle about 56%, playing 18–21%". Read
2's method gives each network a range over its 25 seat-worlds: idle
from 0.295–0.307 up to 0.553–0.573, play from 0.181–0.207 up to
0.359–0.410. On the exact rot2 read each network's one seat idled
0.295–0.375 and played 0.319–0.413. The paragraph's comparisons hold
at both ends of every range: s6 plays most (0.207 at the floor, 0.410
at the ceiling), and the teacher idles and rests more and plays about
half as much (exact on the scripted reference: idle 0.435–0.513, rest
0.152–0.228, play 0.142–0.233).

### Read 2: the flag-only method, checked

For Gen 1, whose streams have no applied action. On both re-collected
rosters, pooled over five worlds:

- Drink: the estimate equals the exact count for all ten cats.
- Eat: equal for the five scripted cats; for rot2 off by −9, −2, +1,
  −13 and −11 ticks against about 1,800–3,000 eat ticks per cat. A
  sated cat licking a bowl's last serving lowers no need, so the
  method cannot see that meal.
- Every other exact share lies inside its floor..ceiling. Where it
  sits (0 = floor, 1 = ceiling): sleep 0.998–1.0, partnered 0.93–0.99
  (added beyond the declaration), play 0.88–0.91, groom 0.66–0.97,
  rest 0.45–0.71, Idle 0.09–0.17. Cats rarely walk out of a sleep
  scene and often walk out of rest and grooming, so the tick after a
  run is almost always the scene's own for sleep and least often for
  rest.

### Read 3: the battery's two flag reads

rot2's five worlds hold no distress tick and no held tick, so nothing
moves there. On the scripted reference, 170 of 5,943 distress
cat-need-ticks (2.9%) change class, every one out of idle (154 to
parked, 9 to tending, 7 to other), and held ticks fall from 2,473 to
2,457 (shared 686 to 680). The correction only fills ticks the flag
read as Idle, so it never moves a tick into idle and can only remove
held ticks. The battery's streak shapes would shift a few points from
idle toward parked or tending and its holding would dip slightly; no
reading there changes direction. Its legs did not record the applied
action, so they are not re-read. The certification harness reads the
same flag for its eat and drink tick counts, its sleep and play
accounting, streak shape and holding; its gates read happiness and
distress, which do not use it, so the certificate stands.

### Regeneration

#### Collect (never run by the gate; under a minute)

```
experiments/seating-analysis-g2-2026-10-21/run_applied.sh
```

#### Read (seconds; lab venv, repo root)

```
experiments/exp-006-character-gen/.venv/bin/python -B experiments/seating-analysis-2026-09-28/seating_read.py --raws experiments/seating-analysis-g2-2026-10-21/results-raw/applied/g2-rot2/streams-905001.npz experiments/seating-analysis-g2-2026-10-21/results-raw/applied/g2-rot2/streams-905002.npz experiments/seating-analysis-g2-2026-10-21/results-raw/applied/g2-rot2/streams-905003.npz experiments/seating-analysis-g2-2026-10-21/results-raw/applied/g2-rot2/streams-905004.npz experiments/seating-analysis-g2-2026-10-21/results-raw/applied/g2-rot2/streams-905005.npz --out experiments/seating-analysis-g2-2026-10-21/certified-rot2-exact-read.json && experiments/exp-006-character-gen/.venv/bin/python -B experiments/seating-analysis-2026-09-28/seating_summary.py experiments/seating-analysis-g2-2026-10-21/certified-rot2-exact-read.json
cd experiments/seating-analysis-g2-2026-10-21 && VIRTUAL_ENV=/Users/elizabethkelly/ai/cloudkitty/experiments/exp-006-character-gen/.venv /Users/elizabethkelly/ai/cloudkitty/experiments/exp-006-character-gen/.venv/bin/python3 -B same_world.py scripted && VIRTUAL_ENV=/Users/elizabethkelly/ai/cloudkitty/experiments/exp-006-character-gen/.venv /Users/elizabethkelly/ai/cloudkitty/experiments/exp-006-character-gen/.venv/bin/python3 -B same_world.py g2-rot2 && VIRTUAL_ENV=/Users/elizabethkelly/ai/cloudkitty/experiments/exp-006-character-gen/.venv /Users/elizabethkelly/ai/cloudkitty/experiments/exp-006-character-gen/.venv/bin/python3 -B correction_read.py --out correction-read.json
```

```
python3 - <<'EOF2'
import json
import statistics as st
B = "experiments/seating-analysis-g2-2026-10-21/"
old = json.load(open(B + "certified-rot2-read.json"))["legs"]
new = json.load(open(B + "certified-rot2-exact-read.json"))["legs"]
C = json.load(open(B + "correction-read.json"))
assert [l["seed"] for l in new] == [905001, 905002, 905003, 905004, 905005] and all(l["ticks"] == 20000 for l in new)
assert all(l["activity_source"] == "applied" for l in new) and all(l.get("activity_source", "flag") == "flag" for l in old)
m = lambda L, k, f: round(st.mean(f(l["cats"][k]) for l in L), 3)
want = {  # idle, play, eat, drink, rest, sleep, groom, partnered: (flag, exact)
    0: [(0.537, 0.305), (0.186, 0.350), (0.008, 0.019), (0.016, 0.033), (0.091, 0.099), (0.121, 0.142), (0.040, 0.053), (0.209, 0.292)],
    1: [(0.545, 0.295), (0.221, 0.413), (0.007, 0.018), (0.013, 0.025), (0.103, 0.111), (0.071, 0.084), (0.041, 0.055), (0.215, 0.315)],
    2: [(0.612, 0.375), (0.205, 0.386), (0.012, 0.030), (0.014, 0.029), (0.086, 0.093), (0.051, 0.060), (0.020, 0.026), (0.186, 0.274)],
    3: [(0.551, 0.316), (0.185, 0.347), (0.010, 0.026), (0.013, 0.026), (0.094, 0.102), (0.080, 0.096), (0.066, 0.088), (0.199, 0.288)],
    4: [(0.553, 0.337), (0.168, 0.319), (0.009, 0.022), (0.015, 0.030), (0.154, 0.168), (0.071, 0.084), (0.031, 0.040), (0.253, 0.350)]}
for k, rows in want.items():
    for (fl, ex), i in zip(rows[:7], (0, 5, 3, 4, 1, 2, 6)):
        assert (m(old, k, lambda c: c["activity_share"][i]), m(new, k, lambda c: c["activity_share"][i])) == (fl, ex), (k, i)
    assert (m(old, k, lambda c: c["grouped"]["partnered"]), m(new, k, lambda c: c["grouped"]["partnered"])) == rows[7], k
assert [round(st.mean(l["cats"][k]["eat_cadence"]["median"] for l in new)) for k in range(5)] == [97, 100, 55, 71, 80]
assert [round(st.mean(l["cats"][k]["drink_cadence"]["median"] for l in new)) for k in range(5)] == [64, 83, 74, 87, 73]
pt = {p: st.mean(l["pairs"][p]["pair_ticks"] for l in new) for p in new[0]["pairs"]}
rc = {p: round(st.mean(l["reciprocity"].get(p, 0) for l in new), 2) for p in new[0]["pairs"]}
top = sorted(pt, key=lambda p: -pt[p])[:5]
assert top == ["Biscuit-Clementine", "Miso-Clementine", "Pumpkin-Clementine", "Kittybear-Clementine", "Miso-Biscuit"]
assert [round(pt[p]) for p in top] == [2433, 2159, 2066, 2024, 1952] and [rc[p] for p in top] == [0.96, 0.93, 0.88, 0.92, 0.91]
assert (min(rc.values()), max(rc.values())) == (0.88, 0.97)
assert [st.mode(l["cats"][k]["top_partner"] for l in new) for k in range(5)] == ["Clementine"] * 4 + ["Biscuit"]
lag = lambda k: [l["cats"][k]["routine"]["dominant_lag"] for l in new]
assert (lag(0), lag(1), lag(4)) == ([61, 59, 59, 59, 59], [115, 106, 110, 112, 109], [112, 107, 737, 61, 114])
assert [l["cats"][0]["routine"]["dominant_lag"] for l in old][0] == 995
MR = C["model_ranges (added)"]
assert all(MR[n]["seat_worlds"] == 25 for n in MR)
lo = lambda a, i: round(min(MR[n][a][i] for n in MR), 3)
hi = lambda a, i: round(max(MR[n][a][i] for n in MR), 3)
assert (lo("Idle", 0), hi("Idle", 0), lo("Idle", 1), hi("Idle", 1)) == (0.295, 0.307, 0.553, 0.573)
assert (lo("Play", 0), hi("Play", 0), lo("Play", 1), hi("Play", 1)) == (0.181, 0.207, 0.359, 0.41)
assert max(MR, key=lambda n: MR[n]["Play"][0]) == max(MR, key=lambda n: MR[n]["Play"][1]) == "s6"
assert (MR["s6"]["Play"][0], MR["s6"]["Play"][1]) == (0.207, 0.41)
MC = C["method_check"]
ex = lambda r, a: [c["activities"][a]["exact"] for c in MC[r]]
rng = lambda xs: (round(min(xs), 3), round(max(xs), 3))
assert rng(ex("g2-rot2", "Idle")) == (0.295, 0.375) and rng(ex("g2-rot2", "Play")) == (0.319, 0.413)
assert rng(ex("scripted", "Idle")) == (0.435, 0.513) and rng(ex("scripted", "Rest")) == (0.152, 0.228) and rng(ex("scripted", "Play")) == (0.142, 0.233)
assert all(c["activities"]["Drink"]["error_ticks"] == 0 for r in MC for c in MC[r])
assert [c["activities"]["Eat"]["error_ticks"] for c in MC["scripted"]] == [0] * 5
assert [c["activities"]["Eat"]["error_ticks"] for c in MC["g2-rot2"]] == [-9, -2, 1, -13, -11]
eat_ticks = [c["activities"]["Eat"]["exact"] * c["ticks"] for c in MC["g2-rot2"]]
assert (round(min(eat_ticks), -2), round(max(eat_ticks), -2)) == (1800, 3000)
assert all(c["activities"][a]["inside"] for r in MC for c in MC[r] for a in ("Idle", "Rest", "Sleep", "Play", "Groom"))
assert all(c["partnered (added)"]["inside"] for r in MC for c in MC[r])
pos = lambda a: rng([c["activities"][a]["position"] for r in MC for c in MC[r]])
assert (pos("Sleep"), pos("Play"), pos("Rest"), pos("Idle")) == ((0.998, 1.0), (0.883, 0.914), (0.453, 0.706), (0.092, 0.171))
assert (round(pos("Groom")[0], 2), round(pos("Groom")[1], 2)) == (0.66, 0.97)
assert rng([c["partnered (added)"]["position"] for r in MC for c in MC[r]]) == (0.93, 0.992)
R3 = C["reclassify"]
s, h = R3["scripted"]["shape"], R3["scripted"]["holding"]
assert (s["changed"], s["classified"], s["changed_share"]) == (170, 5943, 0.0286)
assert s["moves"] == {"idle->parked": 154, "idle->tending": 9, "idle->other": 7}
assert (h["held_flag"], h["held_corrected"], h["shared_flag"], h["shared_corrected"]) == (2473, 2457, 686, 680)
assert R3["g2-rot2"]["shape"]["classified"] == 0 and R3["g2-rot2"]["holding"]["held_flag"] == 0
print("activity-flag correction fence: all cells match")
EOF2
```
