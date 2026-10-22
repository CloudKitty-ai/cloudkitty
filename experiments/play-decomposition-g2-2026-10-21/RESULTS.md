# Play decomposition, Gen 2 — results (2026-10-21)

Declared in `DECLARATION.md` (committed e4b0ae60, before any cell data).
Five scripted cells collected 2026-10-21 23:50Z, five worlds each, no
abort (`results-raw/run.log`); reader `decomp_read.py`, output
`decomp-read.json`. Descriptive under doctrine rule 10: nothing here is
a bar. Five worlds per cell; every pooled number carries its
between-world SD, every paired difference the SD of its five per-world
differences.

## Summary

Where the play came from, pooled over the five cats (share of ticks):

| step | from | to | Δ |
|---|---|---|---|
| Gen 1 roster, trained, on its world (N1, a range) | | 0.074..0.147 | |
| Gen 1 behaviors on the Gen 1 world, Gen 2 dials (C5) | | 0.109 | |
| the world: Gen 1 → Gen 2 (C5 → C3) | 0.109 | 0.106 | −0.004 (unpaired) |
| the behaviors: Gen 1 presets → one teacher, every rung on (C3 → C1) | 0.106 | 0.196 | +0.091 ± 0.007 |
| the training: the served teacher → the certified roster (C1 → N2) | 0.196 | 0.363 | +0.166 ± 0.011 |

(Each cell is rounded on its own; the unrounded values chain exactly:
0.1093 → 0.1056 → 0.1964 → 0.3627.)

Three findings and one reference point.

1. **The world contributes almost nothing**: the Gen 1 behaviors play
   0.004 less on the Gen 2 world than on their own, under either dial
   set (unpaired, about 1.5% of the rise). The rise is teacher and
   training.
2. **Switching the four `needs_driven` seats to the Gen 2 teacher added
   about 0.10–0.17 of play to each of them** (the luxury rung and the
   partner responses they lacked; no cell separates the two) and took
   0.10 from Biscuit, who as `playful` had the luxury rung and nothing
   else; `teacher` gives her wander, the groom response and partner
   responses, which cost her play time.
3. **The trained roster plays 0.166 ± 0.011 more than its own teacher on
   the same worlds**, and lands at 0.363 ± 0.008, within 0.012 of what
   the same teacher does with its play gates loosened (C2: 0.375 ±
   0.007, `playful_comfort` 55 and consent off): 0.012 ± 0.004 short of
   it pooled, below it on all five worlds; by cat, Pumpkin and
   Clementine sit above the loosened teacher and the other three below.
   The two sit under different gates.
   The teacher is held by two: its own comfort rule (`playful_comfort`
   is read only in `teacher.rs`, never by the engine) and the engine's
   consent line. The networks never had the comfort rule; they share
   only the consent line, which binds every proposer. So the served
   teacher is held down 0.179 ± 0.009 by its dials, and the roster, with
   one gate, plays about what the teacher plays with its comfort rule
   loosened and consent off.

Where the networks' extra play went and what it cost: about 0.7 of it
is element and solo play (+0.09 to +0.14 per cat; 0.57–0.77 by cat) and
0.3 kitty play (+0.04 to +0.08); it came out of idle moving (−0.10 to
−0.12) and
rest (−0.04 to −0.07); eat and drink rose slightly, sleep moved up or
inside noise, and groom went both ways (Pumpkin −0.014, Kittybear
+0.039). The networks start play under LESS other-need pressure
than the teacher, not more (R4), so deviations entry 3's reward-side
hypothesis gains no footing at the served size. Of the roster's 5.1–5.8
happiness points over the teacher, play's own need accounts for 14–22%;
the rest is spread across eat, drink, cuddle and sleep, with a little
bath (R5).

## R1. The ladder

Play share, mean over 5 worlds; the pooled column is the five cats'
mean with its between-world SD. N1 is the Gen 1 roster's flag-only
floor..ceiling range (`flag_estimate`).

| cell | Miso | Biscuit | Pumpkin | Kittybear | Clementine | pooled |
|---|---|---|---|---|---|---|
| C1 W2 teacher d2 (served) | 0.190 | 0.233 | 0.201 | 0.216 | 0.142 | 0.196 ± 0.006 |
| C2 W2 teacher d1 | 0.369 | 0.421 | 0.381 | 0.400 | 0.304 | 0.375 ± 0.007 |
| C3 W2 gen1b d2 | 0.053 | 0.335 | 0.055 | 0.046 | 0.039 | 0.106 ± 0.002 |
| C4 W2 gen1b d1 | 0.064 | 0.484 | 0.065 | 0.054 | 0.051 | 0.144 ± 0.004 |
| C5 W1 gen1b d2 (anchor-b3) | 0.056 | 0.347 | 0.058 | 0.047 | 0.039 | 0.109 ± 0.003 |
| C6 W1 gen1b d1 | 0.066 | 0.500 | 0.068 | 0.055 | 0.052 | 0.148 ± 0.003 |
| N2 rot2 (trained, W2) | 0.350 | 0.413 | 0.386 | 0.347 | 0.319 | 0.363 ± 0.008 |
| N1 Gen 1 roster (trained, W1) | 0.036..0.071 | 0.227..0.450 | 0.041..0.080 | 0.035..0.070 | 0.033..0.065 | 0.074..0.147 |

The factor differences (pooled; SD of the per-world differences where
paired; a difference inside its SD would be inside noise, none is):

| difference | pooled | SD | Miso | Biscuit | Pumpkin | Kittybear | Clementine |
|---|---|---|---|---|---|---|---|
| dials on the Gen 2 teacher, C2 − C1 | +0.179 | 0.009 | +0.179 | +0.188 | +0.180 | +0.184 | +0.162 |
| dials on the Gen 1 behaviors, C4 − C3 | +0.038 | 0.004 | +0.011 | +0.149 | +0.010 | +0.008 | +0.012 |
| behaviors at Gen 2 dials, C3 − C1 | −0.091 | 0.007 | −0.137 | +0.102 | −0.146 | −0.170 | −0.103 |
| behaviors at Gen 1 dials, C4 − C2 | −0.231 | 0.007 | −0.305 | +0.063 | −0.316 | −0.346 | −0.253 |
| world at Gen 2 dials, C5 − C3 | +0.004 | unpaired | +0.003 | +0.013 | +0.003 | +0.000 | −0.001 |
| world at Gen 1 dials, C6 − C4 | +0.004 | unpaired | +0.002 | +0.016 | +0.003 | +0.001 | +0.001 |
| training, Gen 2: N2 − C1 | +0.166 | 0.011 | +0.159 | +0.180 | +0.185 | +0.131 | +0.177 |
| training, Gen 1: N1 − C5 | −0.035..+0.038 | unpaired | | | | | |

Readings. The dials act mostly through the luxury rung: on the Gen 1
behaviors Biscuit (the one `playful` seat) moves +0.149 with them while
the four `needs_driven` seats move +0.008 to +0.012 (small but outside
their per-cat SD; consent off plus Biscuit's extra play drawing them in,
which no cell separates). On the Gen 2 teacher every seat gains
0.16–0.19 when its comfort rule is loosened to 55 and consent comes off.
The Gen 1 training effect is inside the
range's width: Gen 1's trained roster played about what its scripted
comparator played; Gen 2's plays 0.166 more than its teacher.

## R2. Composition of the networks' extra play (N2 vs C1, paired)

| cat | kitty N2 | kitty C1 | Δ ± SD | element/solo N2 | C1 | Δ ± SD | scenes per world N2/C1 | scene length N2/C1 |
|---|---|---|---|---|---|---|---|---|
| Miso | 0.133 | 0.097 | +0.036 ± 0.008 | 0.216 | 0.093 | +0.123 ± 0.016 | 1349/800 | 5.18/4.76 |
| Biscuit | 0.168 | 0.120 | +0.048 ± 0.009 | 0.245 | 0.113 | +0.132 ± 0.017 | 1544/1015 | 5.35/4.59 |
| Pumpkin | 0.146 | 0.097 | +0.049 ± 0.012 | 0.240 | 0.104 | +0.136 ± 0.012 | 1447/860 | 5.34/4.69 |
| Kittybear | 0.144 | 0.104 | +0.040 ± 0.017 | 0.203 | 0.112 | +0.091 ± 0.014 | 1445/916 | 4.80/4.72 |
| Clementine | 0.150 | 0.074 | +0.076 ± 0.017 | 0.168 | 0.068 | +0.100 ± 0.017 | 1163/666 | 5.48/4.27 |

More scenes (1.5–1.75×) and slightly longer ones (inclusive, 4.80–5.48
ticks against 4.27–4.76). On 7,181 of the roster's 11,245 kitty-play
starts (0.639) both cats had chosen a PlayKitty action that tick. The
engine's proposer and acceptor roles are not in the streams (the
declaration says why), so that is as far as the split goes.

## R3. Displacement (N2 − C1, share of ticks, paired mean)

| cat | idle | rest | sleep | eat | drink | play | groom | of idle: move | chase | purr | meow |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Miso | −0.130 | −0.056 | −0.003 | +0.006 | +0.012 | +0.159 | +0.013 | −0.100 | +0.002 | +0.000 | +0.000 |
| Biscuit | −0.181 | −0.042 | +0.017 | +0.004 | +0.009 | +0.180 | +0.012 | −0.122 | −0.005 | +0.000 | +0.000 |
| Pumpkin | −0.138 | −0.061 | +0.014 | +0.006 | +0.008 | +0.185 | −0.014 | −0.114 | +0.010 | +0.000 | +0.000 |
| Kittybear | −0.149 | −0.068 | +0.028 | +0.009 | +0.009 | +0.131 | +0.039 | −0.120 | +0.029 | +0.000 | +0.000 |
| Clementine | −0.141 | −0.060 | +0.016 | +0.005 | +0.009 | +0.177 | −0.006 | −0.107 | +0.020 | +0.000 | +0.000 |

The extra play ticks came out of idle, most of it moving (0.68–0.83 of
each cat's idle drop; the move category is not split into wander and
travel), and out of rest. Eat and
drink are up 0.004–0.012 and sleep −0.003 to +0.028 (Miso's −0.003 is
inside its paired SD). Groom is the one tending activity that moved both
ways: −0.014 (Pumpkin) and −0.006 (Clementine) against +0.039
(Kittybear), each outside its paired SD. Purr and meow are exactly zero
on both sides in every world.

## R4. Pressure at onset

Needs one tick before each play start (0–100 scale). C3 is the Gen 1
behaviors on the same worlds, for the shape of a need-driven player.

| cat | cell | starts (5 worlds) | median play need | worst other need > 30 | > 50 |
|---|---|---|---|---|---|
| Miso | N2 | 6742 | 1.6 | 0.028 | 0.000 |
| Miso | C1 | 3997 | 2.3 | 0.038 | 0.012 |
| Miso | C3 | 2087 | 13.3 | 0.048 | 0.009 |
| Biscuit | N2 | 7718 | 4.5 | 0.053 | 0.000 |
| Biscuit | C1 | 5071 | 6.6 | 0.140 | 0.020 |
| Biscuit | C3 | 8280 | 3.0 | 0.043 | 0.005 |
| Pumpkin | N2 | 7229 | 2.0 | 0.047 | 0.000 |
| Pumpkin | C1 | 4293 | 2.8 | 0.065 | 0.022 |
| Pumpkin | C3 | 2245 | 17.6 | 0.081 | 0.017 |
| Kittybear | N2 | 7222 | 1.7 | 0.015 | 0.000 |
| Kittybear | C1 | 4579 | 1.8 | 0.029 | 0.009 |
| Kittybear | C3 | 1925 | 15.3 | 0.055 | 0.013 |
| Clementine | N2 | 5811 | 2.2 | 0.042 | 0.000 |
| Clementine | C1 | 3326 | 2.8 | 0.064 | 0.025 |
| Clementine | C3 | 1653 | 17.9 | 0.141 | 0.057 |

The networks start play with a lower play need than their teacher
(medians 1.6–4.5 against 1.8–6.6) and with less pressure elsewhere: the
share of starts with another need past 30 is 0.015–0.053 for the
networks against 0.029–0.140 for the teacher, and another need past 50
precedes five of the networks' 34,722 starts (0.0000–0.0003 per cat,
none of them Kittybear's; the teacher: 0.009–0.025). The
reward-side hypothesis of deviations entry 3 (play as the one need whose
distress carries no value penalty, so optimization leans there under
multi-need pressure) predicts the opposite sign on this read. At the
served size on these worlds the extra play is slack-time play. The
entry-3 observation came from trunk-s3's training halt, a different
regime; this read neither explains nor contradicts that halt.

The `needs_driven` seats (C3) start play with a play need of 13–18,
the only cell where play waits for its need; Biscuit as `playful` (3.0)
looks like the teacher.

## R5. Where the happiness gain sits (N2 − C1, paired)

Per-need mean deltas weighted by the served happiness weights (eat .20,
drink .20, sleep .15, play .15, cuddle .15, bath .15), in happiness
points; the sum equals the recorded happiness delta (g3 holds the
weights and scale to the engine; no clamp binds on these worlds).

| cat | eat | drink | sleep | play | cuddle | bath | sum | recorded Δ happiness ± SD |
|---|---|---|---|---|---|---|---|---|
| Miso | +1.21 | +1.16 | +0.87 | +0.84 | +1.19 | +0.21 | +5.48 | +5.48 ± 0.93 |
| Biscuit | +1.18 | +1.09 | +0.80 | +1.27 | +1.21 | +0.23 | +5.78 | +5.78 ± 1.02 |
| Pumpkin | +1.34 | +0.99 | +0.60 | +1.01 | +1.17 | +0.00 | +5.12 | +5.12 ± 0.60 |
| Kittybear | +1.34 | +1.03 | +0.96 | +0.78 | +1.16 | +0.30 | +5.55 | +5.55 ± 0.71 |
| Clementine | +1.31 | +1.13 | +0.70 | +1.00 | +1.47 | +0.21 | +5.82 | +5.82 ± 0.78 |

Play's own need carries 14–22% of each cat's gain (0.78–1.27 of
5.12–5.82 points). For Miso, Kittybear and Clementine, eat (+1.21 to
+1.34), drink (+1.03 to +1.16) and cuddle (+1.16 to +1.47) each carry
more than play; for Biscuit play is the largest single term (+1.27
against eat +1.18, cuddle +1.21, drink +1.09), and for Pumpkin play
(+1.01) edges drink (+0.99). Sleep +0.60 to +0.96; bath 0 to +0.30
(Pumpkin's bath, +0.003, is inside noise). The roster is happier than
its teacher on every other need as well, and play's own need is a
minority share of the gain.

## Scope

Served size 20×20, five worlds (905001–905005), 20,000 ticks; the
certified roster rot2 and the scripted cells named above. The dial cells
are diagnostic of a frozen teacher under other dials (rule 9); nothing
here decides a dial, and no network ran under altered dials. The Gen 1
roster enters as a flag-only range (its streams predate the applied
action). Guards g1–g3 (`test_decomp.py`, 3 passed) and the collector's
`--config` guard (`test_seating_g2.py`, 8 passed) each went red once via
`scripts/mutate.sh` (M1 `PLAY` pointed at groom → g1; M2 onset read on
t instead of t − 1 → g2; M3 eat weight 0.20 → 0.15 → g3; the
pass-through dropped → meta names `g2leg-20.toml`) and came back green
with the same counts. The cycle keeps no log; the record is the commit
message that lands this RESULTS.

## Regeneration

### Collect (never run by the gate; about 40 s, no covered minds)

```
cd experiments/play-decomposition-g2-2026-10-21 && bash run_cells.sh
```

### Read (seconds; lab venv, repo root)

```
cd experiments/play-decomposition-g2-2026-10-21 && VIRTUAL_ENV=/Users/elizabethkelly/ai/cloudkitty/experiments/exp-006-character-gen/.venv /Users/elizabethkelly/ai/cloudkitty/experiments/exp-006-character-gen/.venv/bin/python3 -B decomp_read.py --out decomp-read.json --md
```

```
python3 - <<'EOF2'
import json
J = json.load(open("experiments/play-decomposition-g2-2026-10-21/decomp-read.json"))
C, L = J["cells"], J["ladder"]
CATS = ["Miso", "Biscuit", "Pumpkin", "Kittybear", "Clementine"]
r3 = lambda x: round(x, 3)
assert all(C[c]["worlds"] == 5 for c in C)
pooled = {c: (r3(C[c]["pooled"]["mean"]), r3(C[c]["pooled"]["sd"])) for c in ("C1", "C2", "C3", "C4", "C5", "C6", "N2")}
assert pooled == {"C1": (0.196, 0.006), "C2": (0.375, 0.007), "C3": (0.106, 0.002), "C4": (0.144, 0.004),
                  "C5": (0.109, 0.003), "C6": (0.148, 0.003), "N2": (0.363, 0.008)}, pooled
assert [r3(C["N2"]["per_cat"][k]["mean"]) for k in CATS] == [0.350, 0.413, 0.386, 0.347, 0.319]
assert [r3(C["C1"]["per_cat"][k]["mean"]) for k in CATS] == [0.190, 0.233, 0.201, 0.216, 0.142]
assert [r3(C["C3"]["per_cat"][k]["mean"]) for k in CATS] == [0.053, 0.335, 0.055, 0.046, 0.039]
assert (r3(C["N1"]["pooled"]["floor"]), r3(C["N1"]["pooled"]["ceiling"])) == (0.074, 0.147)
d = lambda k: (r3(L[k]["mean"]), r3(L[k]["sd"]) if L[k]["sd"] is not None else None)
assert d("dials_on_teacher C2-C1") == (0.179, 0.009) and d("dials_on_gen1b C4-C3") == (0.038, 0.004)
assert d("behaviors_at_d2 C3-C1") == (-0.091, 0.007) and d("behaviors_at_d1 C4-C2") == (-0.231, 0.007)
assert d("world_at_d2 C5-C3") == (0.004, None) and d("world_at_d1 C6-C4") == (0.004, None)
assert d("training_gen2 N2-C1") == (0.166, 0.011) and d("loosened_teacher_vs_networks C2-N2") == (0.012, 0.004)
assert sorted(k for k, v in L["loosened_teacher_vs_networks C2-N2"]["per_cat"].items() if v < 0) == ["Clementine", "Pumpkin"]
assert [round(x, 3) for x in L["training_gen1 N1-C5"]["range_minus_mean"]] == [-0.035, 0.038]
assert not any(L[k].get("inside_noise") for k in L)
assert r3(L["dials_on_gen1b C4-C3"]["per_cat"]["Biscuit"]) == 0.149 and r3(L["behaviors_at_d2 C3-C1"]["per_cat"]["Biscuit"]) == 0.102
R2 = J["composition"]
kd = [r3(R2[k]["kitty"]["mean"]) for k in CATS]; ed = [r3(R2[k]["element"]["mean"]) for k in CATS]
assert (min(kd), max(kd), min(ed), max(ed)) == (0.036, 0.076, 0.091, 0.136), (kd, ed)
assert (R2["mutual_choice_N2"]["both_chose"], R2["mutual_choice_N2"]["starts"], r3(R2["mutual_choice_N2"]["share"])) == (7181, 11245, 0.639)
assert all(R2[k]["N2"]["scenes"] / R2[k]["C1"]["scenes"] > 1.5 for k in CATS)
R3 = J["displacement"]
mv = [r3(R3[k]["inside_idle"]["move"]["mean"]) for k in CATS]; rs = [r3(R3[k]["rest"]["mean"]) for k in CATS]
assert (min(mv), max(mv), min(rs), max(rs)) == (-0.122, -0.100, -0.068, -0.042), (mv, rs)
assert all(R3[k]["eat"]["mean"] > 0 and R3[k]["drink"]["mean"] > 0 for k in CATS)
R4 = J["onset"]
assert all(R4[k]["N2"]["other_gt50"] < 0.0005 for k in CATS) and sum(R4[k]["N2"]["starts"] for k in CATS) == 34722
assert all(R4[k]["N2"]["other_gt30"] < R4[k]["C1"]["other_gt30"] for k in CATS)
assert all(R4[k]["N2"]["play_need_median"] < R4[k]["C1"]["play_need_median"] for k in CATS)
g30 = [r3(R4[k]["N2"]["other_gt30"]) for k in CATS]; t30 = [r3(R4[k]["C1"]["other_gt30"]) for k in CATS]
assert (min(g30), max(g30), min(t30), max(t30)) == (0.015, 0.053, 0.029, 0.140), (g30, t30)
R5 = J["happiness"]
for k in CATS:
    assert abs(R5[k]["sum_weighted"] - R5[k]["hap_delta_recorded"]["mean"]) < 0.01
share = [R5[k]["weighted_contribution"]["play"] / R5[k]["sum_weighted"] for k in CATS]
assert (round(min(share) * 100), round(max(share) * 100)) == (14, 22), share
assert [round(R5[k]["sum_weighted"], 2) for k in CATS] == [5.48, 5.78, 5.12, 5.55, 5.82]
print("fence green")
EOF2
```

Accuracy gate: **PASS** 2026-10-21, round 3 (rounds 1 and 2 FAIL on
characterisations; every table number matched in all three rounds):
arithmetic 345 table cells + 34 prose figures, characterisation 15
SUPPORTED / 0 WEAK / 0 CONTRADICTED, provenance 6 confirmed + 1
UNDECIDABLE by design (the mutation reds, recorded in the commit message
that lands this file); raws `v1:296560ea8ee1016a`
(`scripts/rawdir-hash.sh experiments/play-decomposition-g2-2026-10-21/results-raw`).
