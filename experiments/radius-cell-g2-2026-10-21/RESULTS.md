# Displaced-size radius cell, Gen 2 — results (2026-10-22)

Declaration: `DECLARATION.md` (committed cd846eac before any cell data;
owner 2026-10-21 "Call 1: run it"). Cell ran 2026-10-22T05:07–05:09Z:
scripted then rot2, scouts (3 worlds) then legs (30 worlds), band g2cmp
905001–905030, 20,000 ticks, 40×40 at `[vision] radius = 4` (config
`g2leg-40-r4.toml`, sha256 87f4cb2e…, one line off the law config).
Every scout and leg clean: no abort, no row at the F-053 line. Raws:
`results-raw/` (never deleted). Read: `radius-read.json`.

## Summary

The 0.97 fall in the trained-vs-scripted gap between the two cert legs
(20×20 +5.566, 40×40 +4.594) travelled with the radius, not the size,
and it is the scripted side that moved. At 40×40 with the radius held
one step below the law, the paired gap is +5.800 ± 0.860 (30 of 30
worlds positive), above the 20×20 gap. Across the one radius step the
scripted teacher gains 1.294 ± 0.958 happiness from the wider radius
(the comparator arc's own law-vs-v4 number, reproduced here on the
armed config) while the certified roster gains 0.088 ± 0.122; the gap
difference is +1.206 ± 0.941 (SE 0.172, 28 of 30 worlds). The roster's
team happiness at 40×40 is 86.229 at radius 5 and 86.140 at radius 4.

Reading per the declaration: the gap at (40×40, radius 4) sits near
the 20×20 gap, not near the 40×40 law gap, so the fall between the cert
legs is a radius effect; and the mechanism on the record is that the
vision law buys the scripted teacher about 1.3 happiness at 40×40 and
buys the frozen roster almost nothing. Descriptive (rule 10): no bar,
no gate; the certificate stands as issued. Rule 9 scope: this is how
the frozen roster transfers across one radius step at 40×40, not what
a roster trained at radius 4 would do; the vision law stays as ruled.

## R1. The 2 × 2 (team happiness; 30 worlds, same seeds in every cell)

| cell | team happiness | sd over worlds |
|---|---|---|
| scripted, radius 5 (law; recorded) | 81.634 | 0.451 |
| rot2, radius 5 (law; recorded) | 86.229 | 0.060 |
| scripted, radius 4 (this cell) | 80.341 | 0.869 |
| rot2, radius 4 (this cell) | 86.140 | 0.089 |

| paired quantity (30 worlds) | mean | sd | se | positive/30 |
|---|---|---|---|---|
| gap rot2 − scripted, radius 5 (law) | +4.594 | 0.451 | 0.082 | 30 |
| gap rot2 − scripted, radius 4 | +5.800 | 0.860 | 0.157 | 30 |
| radius 4 − radius 5, scripted | −1.294 | 0.958 | 0.175 | — |
| radius 4 − radius 5, rot2 | −0.088 | 0.122 | 0.022 | — |
| gap at 4 − gap at 5 | +1.206 | 0.941 | 0.172 | 28 |

The 20×20 cert-leg gap, printed beside and not recomputed: +5.566 ±
0.623 (`../gen2-cert-battery-2026-10-20/RESULTS.md` §"§8.5, the
declared future read"; the §Phase C table prints the mean alone). The
roster's between-world SD is 5–10× smaller than the teacher's in both
cells (0.060 / 0.089 against 0.451 / 0.869): the networks' team
happiness barely varies with the world draw at 40×40, the teacher's
does, and more so at the narrower radius.

## R2. Per seat

| seat | scripted r5 | rot2 r5 | scripted r4 | rot2 r4 | gap r5 | gap r4 | gap r4 − r5 (sd) |
|---|---|---|---|---|---|---|---|
| Miso (s2) | 82.141 | 86.322 | 80.689 | 86.265 | +4.180 | +5.576 | +1.396 (0.963) |
| Biscuit (s4) | 81.846 | 86.516 | 80.596 | 86.595 | +4.669 | +6.000 | +1.330 (0.882) |
| Pumpkin (s6) | 81.555 | 85.784 | 80.166 | 85.654 | +4.228 | +5.488 | +1.260 (1.084) |
| Kittybear (s7) | 82.439 | 86.995 | 81.330 | 86.737 | +4.556 | +5.406 | +0.850 (0.947) |
| Clementine (s1) | 80.190 | 85.527 | 78.922 | 85.452 | +5.336 | +6.529 | +1.193 (1.365) |

Every seat's gap widens at radius 4 (+0.850 to +1.396); the effect is
not carried by one or two seats. Every scripted seat loses 1.1–1.5
happiness at the narrower radius; every network seat moves by less
than 0.26 (Biscuit +0.079, the others −0.056 to −0.259). Clementine's
seat keeps the widest gap at both radii (the owed reads print no
per-seat happiness gap; their Clementine line is beam placement).

## R3. Welfare beside

| cell | worst distress streak, mean over worlds | max | rows ≥ 1,000 | aborts |
|---|---|---|---|---|
| scripted, radius 5 | 197.4 | 626 | 0 | 0 |
| rot2, radius 5 | 16.5 | 128 | 0 | 0 |
| scripted, radius 4 | 257.4 | 570 | 0 | 0 |
| rot2, radius 4 | 37.8 | 296 | 0 | 0 |

Scouts: scripted worst 238, rot2 worst 0 (the three worlds' max
distress age; `results-raw/run.log`). The roster's worst streaks at
radius 4 are longer than at radius 5 (mean 37.8 vs 16.5, max 296 vs
128): about a seventh of the teacher's mean at the same radius (37.8
against 257.4) and half its max (296 against 570); nothing near the
line.

## R4. Instrument check

The new scripted radius-4 row (vocabulary armed, config 87f4cb2e…)
against the pre-law v4 scripted row (vocabulary unarmed, config
84bc50b5…; `../gen2-comparator-legs-2026-10-14/results-raw/legs/size40/`):
30 of 30 worlds equal in team happiness to three decimals, and every
seat's mean happiness byte-equal as recorded. The comparator arc's
finding that the arming flags are inert for scripted seats holds on
these rows, so the R1 scripted radius effect −1.294 is the comparator
arc's law-vs-v4 +1.294 with the sign turned, on the armed config.

Provenance of the four cells, disclosed: the S5 row is the
comparator's pinned law row, which ran on the vision PROBE config
(sha256 9ce23824…, radius 5, vocabulary unarmed) under the earlier
binding 6bb78efd… (engine a297d580); V4 ran under that binding too.
S4, R4 and R5 ran on binding e3bcc79a… (ENGINE_COMMIT b5aaa8cd), R5 on
the law config f45a5183…. So the scripted radius effect crosses the
arming flags and the binding as well as the radius. Both are inert on
these rows: the comparator arc's vocab-armed re-run of the law row
(config f45a5183…, binding e3bcc79a…, R5's own config and binding) is
byte-equal to S5 in every seat's mean happiness on all 30 worlds, and
S4 is byte-equal to V4 the same way across the same two changes. The
reader prints both checks.

## Scope

- Descriptive throughout; n = 30 worlds per cell, paired by seed; the
  per-world SD is the spread over worlds, the SE is SD/√30.
- One radius step, one displaced size. Radius 3 (the S§6 arm's declared
  off-law probe) and 100×100 were not run; nothing here extrapolates to
  them.
- Rule 9: the roster is frozen. What a roster trained at radius 4
  would do is a trained-at-radius question; the prereg's radius-axis
  arm (§8 item 5, ruled S§6) asks it at the served 20×20 over radii
  {3, 4, 5}, and no arm trains at 40×40.
- Not read: play, speech, dispersion, beam placement. The harness rows
  carry `dispersion` and `beam` fields for a later reader.

## Regeneration

### Collect (minutes; two seatings, scouts then legs; from the lab venv)

```
cd /Users/elizabethkelly/ai/cloudkitty/experiments/radius-cell-g2-2026-10-21 && caffeinate -s bash run_cell.sh > results-raw/run.log 2>&1
```

### Read (seconds; stdlib python3 from the lab venv)

```
cd /Users/elizabethkelly/ai/cloudkitty/experiments/radius-cell-g2-2026-10-21 && VIRTUAL_ENV=/Users/elizabethkelly/ai/cloudkitty/experiments/exp-006-character-gen/.venv /Users/elizabethkelly/ai/cloudkitty/experiments/exp-006-character-gen/.venv/bin/python3 -B radius_read.py --out /private/tmp/radius-read.json --md
```

### Verification (seconds; stdlib python3, repo root; reads the JSON the Read fence wrote)

```
python3 - <<'EOF2'
import json
o = json.load(open("/private/tmp/radius-read.json"))
r1, r2, r3 = o["r1"], o["r2"], o["r3"]
R = lambda x, n=3: round(x, n)
assert [R(o["team"][k]["mean"]) for k in ("S5", "R5", "S4", "R4")] == [81.634, 86.229, 80.341, 86.140]
assert [R(o["team"][k]["sd"]) for k in ("S5", "R5", "S4", "R4")] == [0.451, 0.060, 0.869, 0.089]
g5, g4, d = r1["gap_radius5"], r1["gap_radius4"], r1["gap_difference_4_minus_5"]
assert (R(g5["mean"]), R(g5["sd"]), R(g5["se"]), g5["positive"]) == (4.594, 0.451, 0.082, 30)
assert (R(g4["mean"]), R(g4["sd"]), R(g4["se"]), g4["positive"]) == (5.800, 0.860, 0.157, 30)
assert (R(d["mean"]), R(d["sd"]), R(d["se"]), d["positive"]) == (1.206, 0.941, 0.172, 28)
assert (R(r1["radius_effect_scripted"]["mean"]), R(r1["radius_effect_scripted"]["sd"])) == (-1.294, 0.958)
assert (R(r1["radius_effect_rot2"]["mean"]), R(r1["radius_effect_rot2"]["sd"])) == (-0.088, 0.122)
assert R(r1["context_20x20_gap"]["mean"]) == 5.566
dd = {s: r2[s]["difference"]["mean"] for s in r2}
assert min(dd, key=dd.get) == "Kittybear" and max(dd, key=dd.get) == "Miso"
assert all(0.850 <= R(v) <= 1.396 for v in dd.values())
assert all(R(r2[s]["team"]["S4"] - r2[s]["team"]["S5"]) <= -1.1 for s in r2)
assert all(abs(r2[s]["team"]["R4"] - r2[s]["team"]["R5"]) < 0.26 for s in r2)
assert R(r2["Biscuit"]["team"]["R4"] - r2["Biscuit"]["team"]["R5"]) == 0.079
assert [(R(r3[k]["worst_streak_mean"], 1), r3[k]["worst_streak_max"], r3[k]["at_or_over_line"], r3[k]["aborts"])
        for k in ("S5", "R5", "S4", "R4")] == [(197.4, 626, 0, 0), (16.5, 128, 0, 0), (257.4, 570, 0, 0), (37.8, 296, 0, 0)]
assert o["r4"]["identical"] and o["r4"]["worlds_compared"] == 30 and o["r4"]["mismatches"] == [] and o["r4"]["mean_happiness_exact"]
assert o["r4_s5_vs_armed_rerun"]["identical"] and o["r4_s5_vs_armed_rerun"]["mean_happiness_exact"]
c, b = o["config_sha256"], o["binding_sha256"]
assert c["S4"][:8] == c["R4"][:8] == "87f4cb2e" and c["V4"][:8] == "84bc50b5" and c["S5"][:8] == "9ce23824" and c["R5"][:8] == c["A5"][:8] == "f45a5183"
assert b["S5"][:8] == b["V4"][:8] == "6bb78efd" and b["S4"][:8] == b["R4"][:8] == b["R5"][:8] == b["A5"][:8] == "e3bcc79a"
print("radius fence: all cells match")
EOF2
```

Guards: `test_radius.py` (3; `python3 -B test_radius.py` from the lab
venv). Reds on record, each via `scripts/mutate.sh`, predicted then
confirmed, restored green at 3 passed: M1 `team()` reads the max seat →
g1 (AssertionError: 4.4928…); M2 `paired()` zips the second row set in
reversed seed order → g2 (the mean survives mispairing, the per-world
assert does not); M3 `identity()` compares means → g3 (the rolled rows
pass as identical). Driver guard `test_run_legs.py` untouched (10).

Accuracy gate: **PASS**, 2026-10-22, round 2 (fresh subagent; Read fence re-run, fresh JSON identical to the recorded; ~126 arithmetic matched, 0 rounding; 3 threshold; ~19 characterisations SUPPORTED; 3 UNDECIDABLE = the mutate reds, which leave no log; ~22 provenance matched). Round 1 FAIL on a fraction word, a citation, two attributions and an undisclosed row provenance (TRIALS 2026-10-22). Raw-dir hash `scripts/rawdir-hash.sh results-raw` = `v1:0b3fe19c4623b1c0`.
