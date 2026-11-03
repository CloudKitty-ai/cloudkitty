# Mini-friend Phase 1e — RESULTS (collected, trained and read 2026-11-02 UTC)

Declaration: `DECLARATION.md`, RULED 2026-11-01 (owner "As
recommended" to all five §12 calls: fresh seeds, 23 + 8 worlds per
block, start-drop tolerance 0.95, the false-run-matched operating
point, from scratch); deviations entry 16. Observer-stream ruling
2026-10-27 (B + amendments) is the basis. Amendment 1 RULED 2026-11-02 (owner: "Rather than run additional
tests, let's open the door to accepting a potentially higher false
positive rate. We should judge based on welfare impact, not arbitrary
numbers."): the operating point S is her pick, t0.05-B2, the false-run
bound retired as a selector, the price reported in welfare units. Reds
e1–e7 on record (DECLARATION §7). Welfare line: 2,920,000 covered cat-ticks, S1 on the
covered seats only; no weight any acting policy uses changes.

## Collection (§11 step 3; `collect_1e.py run`, 2026-11-02 UTC, 905 s)

155 worlds, 2,920,000 covered cat-ticks, 0 aborts, S1 held in every
world (worst covered single-need streak 636, TN3 seed 1096731, against
the 1,000 line). The needy arc's venv and binding (ENGINE_COMMIT
5928b7ca). Burn order TE then TN. Record `reads/collect.json` /
`reads/collect.md` (committed 5e9056c2):

| kind | worlds | ticks | covered cat-ticks | covered mean happiness over worlds (mean / min / max) | worst covered streak | worlds with a covered grave tick | scripted friend: mean grave ticks per world, episodes, first crossings by stratum |
|---|---|---|---|---|---|---|---|
| TE | 40 | 1,000 | 160,000 | 86.33 / 73.19 / 88.26 | 245 | 4 | 137.2, 60, H1 29 / H2 10 / H3 1 |
| TN | 115 | 6,000 | 2,760,000 | 86.38 / 80.73 / 87.63 | 636 | 65 | 669.7, 594, H2 26 / H3 58 / H4 31 |

Beside the needy set's record (its RESULTS step 5): arm N's scripted
friend was grave 644.7 ticks a world there against 669.7 here; covered
mean happiness 86.43 there against 86.38; arm E 146.9 grave ticks per
800-tick world against 137.2 per 1,000 here. The training set holds
the first-crossing count the declaration expected (about 110: 115
here, every TN world crossing before 6,000) with the strata leaning
to H3 (58 against the tuning half's 45), and 594 scripted grave
episodes in TN (about five a world) plus 60 in TE. One TE world's
covered mean happiness is 73.19 (its S1 streak under the line; the
read's per-world minimum, on the obs-aligned truth stream; the
collection log's per-world print, on the post-step stream, reads
73.17 for TE4 1096971). Raw-dir hashes
(`scripts/rawdir-hash.sh`): TE1 v1:4201bcfce2dd7dfb, TE2
v1:4aa8002afda9d354, TE3 v1:b6a6caca623b5440, TE4 v1:b651116f534f0217,
TE5 v1:1b790dd5582ef19d, TN1 v1:ce2d4e4c53d2a076, TN2
v1:9fb7ee20393e2ba1, TN3 v1:7995bebceb4cc042, TN4 v1:fef89ee929ea604c,
TN5 v1:74450f352db0069b.

Smoke after collection (§11 step 4, 2026-11-02): `train_1e.py --seed 1
--smoke` with all eighteen sets present (2 train / 1 val worlds per
set, 2 epochs) and `probe_1e.py --seed 1 --smoke` ran clean; the
smoke runs are named `-smoke` under results-raw and are never read.

### Regeneration (collection record)

```
### Collect (never run by the gate)
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $P/collect_1e.py run > $P/results-raw/collect.log 2>&1
### Read (about 5 s)
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $P/collect_1e.py read --out $P/reads/collect.json --md > $P/reads/collect.md
```

(`A` = `experiments/needy-set-2026-10-28`, `P` =
`experiments/minifriend-phase1e-2026-11-01`, absolute paths in use.)
This section is gated with the read write-up below.

## Headline

The late-history miss was a coverage gap in the training data, not a
property of the recipe. Phase 1's natural-frequency head at width 24,
trained again from scratch with late-history graves in its training
worlds (a late-grave set of 115 arm-N-shaped and 40 arm-E-shaped
worlds, 120 of them training and 35 validation, beside 1b's), and
Phase 1d's probe refit on its states, detects the needy set's
confirming crossings at her pick (0.05 / B = 2) in 0.920 / 0.880 /
0.863 of N-H2 / N-H3 / N-H4 observer-episodes against the frozen
probe's 0.596 / 0.444 / 0.421 by the same reader on the same worlds
(gains +0.324 / +0.436 / +0.442, mean +0.401; P16 MET), E-H1 in 0.786
against 0.489 and T-H0 in 1.000 (P17 MET), with the median latency at
the crossing itself (0.0 ticks in every E and N stratum; the frozen
probe's 23.7–36.7 in E-H1 / N-H2 / N-H3; T-H0 is 2.0 for both heads,
the first alarmable tick at B = 2) and an anticipation run started
before the crossing, past the first alarmable tick, in 0.843 / 0.871 /
0.892 of N-stratum observer-episodes (the frozen probe's 0.253 / 0.211
/ 0.275). The lift reaches a covered friend's rows: on F-070's splice
at 0.10 the retrained head detects 0.598 after 100 clean ticks against
0.358, 0.988 at H = 0, and the junction control fires in at most 0.013
of junctions (P18 MET); the estimate holds (group-P mind-visible
grave mse5 0.846× the frozen head's, common-state cells 1.02–1.03×
worse; P20 MET); and on the lived evaluation worlds the false runs at the
pick are 0.94× the frozen probe's on group P and 1.60× on L / W / G
(P19 MET). The price is on the needy set itself: beside the refusing
friend the retrained head's false runs on covered friends are 2.40
per 10,000 observer-ticks against 0.63 (3.80×) — in welfare units
0.72 false runs per observer per 1,000 ticks of 17.8 ticks each
(0.19 of 12.9 for the frozen probe), 42.7 observer-ticks under a
false alarm per 10,000 against 8.1 — and on the scripted friend after
its first mask 5.37 against 1.47 per 10,000. The logit on clean 20,000-tick
slices carries no clock over t ≥ 300 (slope 0.001 logits per 1,000
ticks; it rises 3.6 logits between tick 10 and tick 100, then is flat). F-072
minted.

## What ran (§11 steps 4–5)

Three heads (`run_1e.sh`, 2026-11-02 07:09–07:34 UTC, three torch
threads each in parallel): 194 training worlds (74 of 1b's, 120 new)
and 52 validation worlds (17 + 35), 3,400 training and 900 validation
sequences, 17,520,000 training samples, about 20 s an epoch. Plateaus
by Phase 1's rule at best epochs 66 / 60 / 49 (epochs run 76 / 70 /
59), validation loss 0.005988 / 0.006000 / 0.006434 on this arc's
validation worlds (not 1b's set: no comparison to its 0.0046 is made).
Probes (`probe_1e.py`): best epochs 44 / 41 / 51, validation BCE
0.01378 / 0.01471 / 0.01366; the training samples' grave frequency
0.01821 (1b's probe fit saw 0.00300). Reads: `tuning` 26 s, then
`splice`, `lived`, `estimate` before amendment 1, then `confirming`
(S = t0.05-B2 written to `reads/S.json`), `lived` and `splice` again
with S present, `score`. First-episode status, confirming half (both
heads, the same worlds): T {H0: 25}; E {H1: 23, H2: 11,
released_no_crossing: 1, unreleased: 5}; N {H2: 26, H3: 64, H4: 20,
released_no_crossing: 5}.

## R-A1, the tuning grid (`reads/tuning.json`; the 12 declared cells; seed mean ± SD)

| cell | E-H1 det | N-H2 det | N-H3 det | N-H4 det | mean N det | FA covered N /10k | FA scripted-from-mask N /10k |
|---|---|---|---|---|---|---|---|
| t0.02-B0 | 0.920 ± 0.006 | 0.971 ± 0.019 | 0.943 ± 0.003 | 0.977 ± 0.000 | 0.964 | 4.5709 ± 1.6612 | 6.2531 ± 2.9760 |
| t0.02-B2 | 0.920 ± 0.006 | 0.971 ± 0.019 | 0.943 ± 0.003 | 0.977 ± 0.000 | 0.964 | 4.0604 ± 1.8298 | 6.2531 ± 2.9760 |
| t0.05-B0 | 0.865 ± 0.028 | 0.952 ± 0.027 | 0.918 ± 0.006 | 0.943 ± 0.027 | 0.938 | 3.3039 ± 1.2037 | 4.8720 ± 1.9975 |
| t0.05-B2 | 0.865 ± 0.028 | 0.952 ± 0.027 | 0.918 ± 0.006 | 0.943 ± 0.027 | 0.938 | 2.7971 ± 1.2584 | 4.8720 ± 1.9975 |
| t0.10-B0 | 0.812 ± 0.042 | 0.929 ± 0.045 | 0.844 ± 0.000 | 0.901 ± 0.024 | 0.891 | 2.0894 ± 0.9604 | 3.6906 ± 1.3360 |
| t0.20-B0 | 0.722 ± 0.037 | 0.867 ± 0.061 | 0.757 ± 0.054 | 0.833 ± 0.030 | 0.819 | 1.4670 ± 0.6692 | 2.6920 ± 0.8331 |
| t0.30-B0 | 0.653 ± 0.024 | 0.821 ± 0.050 | 0.694 ± 0.029 | 0.776 ± 0.030 | 0.764 | 1.1349 ± 0.4353 | 2.1097 ± 0.4790 |
| t0.50-B0 | 0.549 ± 0.032 | 0.762 ± 0.027 | 0.615 ± 0.036 | 0.682 ± 0.004 | 0.686 | 0.7110 ± 0.2440 | 1.5288 ± 0.3198 |

T-H0 is 1.000 ± 0.000 in every cell. The B = 2 rows equal the B = 0
rows in every detection column and in the N-stratum anticipation
columns printed at every threshold (E-H1's anticipation differs
between B = 0 and B = 2 from 0.02 to 0.30: 0.840 against 0.754 at
0.05, in the JSON), and in the false-run columns from 0.10 up: on the
needy set's tuning half the retrained head has no first-tick false
run above 0.05 (on the lived worlds it has some at 0.10 / B = 0, R-C);
the B = 2 rows for 0.10–0.50 are in the JSON. The frozen pick's tuning-half figures by the ladder: 0.536
/ 0.459 / 0.409 at 0.7077 covered and 1.4965 scripted-from-mask per
10,000. **The declared selection: no candidate.** The top cell, 0.50,
sits at 0.7110 and 1.5288, over the bound by 0.0033 and 0.0323 per
10,000; S = None by the rule. Amendment 1 (DECLARATION §13) set S to
her pick instead of extending the grid; the confirming half was read
after it, at two cells.

## R-A2, the confirming half at her pick and the registered point (`reads/confirming.json`; both heads, the same reader, the same 180 worlds)

Strata by the crossing's offset from the slice's first tick (needy set
§4): H0 [0, 2), H1 [2, 100), H2 [100, 300), H3 [300, 1,250), H4
[1,250, 6,000) — a crossing after 100–300 / 300–1,250 / 1,250–6,000
ticks of lived history. Detection and anticipation (anticipation = a
run starting inside [mask onset, crossing) past the first alarmable
tick; median lead from that run), seed mean ± SD; the frozen probe's rows at the pick equal
R5's as the reader asserts:

| head, cell | T-H0 | E-H1 | N-H2 | N-H3 | N-H4 | N-H2 antic (lead) | N-H3 antic (lead) | N-H4 antic (lead) |
|---|---|---|---|---|---|---|---|---|
| retrained, t0.05-B2 | 1.000 ± 0.000 | 0.786 ± 0.082 | 0.920 ± 0.006 | 0.880 ± 0.006 | 0.863 ± 0.000 | 0.843 ± 0.053 (43.3) | 0.871 ± 0.030 (50.3) | 0.892 ± 0.014 (49.8) |
| frozen, t0.05-B2 | 1.000 ± 0.000 | 0.489 ± 0.022 | 0.596 ± 0.092 | 0.444 ± 0.110 | 0.421 ± 0.134 | 0.253 ± 0.059 (30.0) | 0.211 ± 0.077 (35.2) | 0.275 ± 0.108 (23.8) |
| retrained, t0.10-B0 | 1.000 ± 0.000 | 0.717 ± 0.071 | 0.897 ± 0.011 | 0.832 ± 0.017 | 0.783 ± 0.038 | 0.766 ± 0.040 | 0.796 ± 0.037 | 0.817 ± 0.040 |
| frozen, t0.10-B0 | 1.000 ± 0.000 | 0.409 ± 0.025 | 0.526 ± 0.081 | 0.392 ± 0.094 | 0.383 ± 0.135 | 0.199 ± 0.087 | 0.152 ± 0.075 | 0.167 ± 0.076 |

Latency at the pick (median over detected observer-episodes, seed
mean; p90; share detected within 10 ticks of the crossing over all
observer-episodes): retrained E-H1 0.0 / 7.0 / 0.721, N-H2 0.0 / 9.0
/ 0.827, N-H3 0.0 / 0.2 / 0.836, N-H4 0.0 / 0.1 / 0.821; frozen E-H1
36.7 / 138.9 / 0.163, N-H2 23.7 / 157.4 / 0.253, N-H3 35.0 / 174.7 /
0.195, N-H4 2.3 / 54.7 / 0.317 (the within-10 shares 0.72–0.84
against 0.16–0.32; T-H0's median latency is 2.0 for both heads). The
N-stratum median leads above are 43–50 ticks against 24–35. In sight
at the crossing against under fog, retrained: N-H2 0.921 / 0.918,
N-H3 0.871 / 0.893, N-H4 0.878 / 0.833 (0.87–0.92 in sight, 0.83–0.92
under fog; frozen 0.582 / 0.612, 0.501 / 0.359, 0.429 / 0.405).
E-H2 (arm E's late crossings, not a primary stratum, 11 episodes):
0.894 against 0.386.

**The price** (arm N, confirming half, per class; seed means; the
observer-tick classes are the ladder's; "per observer per 1,000
ticks" counts a covered observer's three covered friends or its one
scripted friend):

| head, cell | class | false runs per 10k observer-ticks | mean run length | observer-ticks under a false alarm per 10k | false runs per observer per 1,000 ticks |
|---|---|---|---|---|---|
| retrained, t0.05-B2 | covered friends | 2.4002 ± 1.0702 | 17.8 | 42.7 | 0.7201 |
| frozen, t0.05-B2 | covered friends | 0.6308 ± 0.2269 | 12.9 | 8.1 | 0.1892 |
| retrained, t0.05-B2 | scripted friend from its first mask | 5.3708 ± 2.0587 | 16.6 | 89.0 | 0.5371 |
| frozen, t0.05-B2 | scripted friend from its first mask | 1.4714 ± 0.6489 | 10.5 | 15.4 | 0.1471 |
| retrained, t0.05-B2 | scripted friend before its first mask | 0.7223 | 4.3 | 3.1 | 0.0722 |
| frozen, t0.05-B2 | scripted friend before its first mask | 0.3844 | 4.6 | 1.8 | 0.0384 |
| retrained, t0.10-B0 | covered friends | 1.8635 ± 0.8257 | 15.8 | 29.4 | 0.5590 |
| frozen, t0.10-B0 | covered friends | 1.4783 ± 0.9831 | 4.7 | 7.0 | 0.4435 |
| retrained, t0.10-B0 | scripted friend from its first mask | 4.2376 ± 1.4270 | 14.2 | 60.0 | 0.4238 |
| frozen, t0.10-B0 | scripted friend from its first mask | 1.0901 ± 0.4363 | 9.0 | 9.8 | 0.1090 |

At the pick the retrained head's covered-friend false runs are 3.80×
the frozen probe's and its scripted-friend false runs after the mask
3.65×; at the registered point (B = 0) the covered ratio is 1.26×,
because the frozen probe's first-tick transient is counted there
(its scripted-before-mask class at 0.10 / B = 0 is 10.1350 per
10,000, runs of 1.0 tick). The covered-friend rate at the pick by arm:
arm T 0.1222 against 0.0722, arm E 3.559 against 1.0156, arm N 2.4002
against 0.6308 — the excess sits in the arms whose friend refuses
help; where the scripted friend is a teacher (arm T) it is 0.05 per
10,000, and on the lived worlds below 0.94× and 1.60×.

## R-B, the splice and the clock (`reads/splice.json`)

F-069 / F-070's splice (200 covered donors, 60 clean recipients, the
junction control), seed mean ± SD over the retrained heads; the
frozen probe's committed rows beside:

| H | retrained at 0.10: detected | control fired | median latency | retrained at 0.05: detected | control fired | frozen committed at 0.10: detected | control |
|---|---|---|---|---|---|---|---|
| 0 | 0.988 ± 0.003 | 0.000 | 1.0 | 0.993 | 0.302 | 0.995 | 0.678 |
| 1 | 0.988 ± 0.003 | 0.000 | 2.0 | 0.988 | 0.000 | 0.978 | 0.010 |
| 2 | 0.982 ± 0.014 | 0.000 | 2.3 | 0.982 | 0.000 | 0.970 | 0.000 |
| 5 | 0.962 ± 0.037 | 0.000 | 3.0 | 0.967 | 0.000 | 0.852 | 0.000 |
| 10 | 0.913 ± 0.025 | 0.000 | 4.0 | 0.938 | 0.000 | 0.658 | 0.000 |
| 20 | 0.778 ± 0.129 | 0.000 | 5.3 | 0.835 | 0.000 | 0.537 | 0.000 |
| 50 | 0.597 ± 0.033 | 0.002 | 14.0 | 0.680 | 0.007 | 0.362 | 0.000 |
| 100 | 0.598 ± 0.033 | 0.013 | 16.5 | 0.657 | 0.022 | 0.358 | 0.000 |
| 500 | 0.542 ± 0.050 | 0.002 | 22.7 | 0.607 | 0.007 | 0.287 | 0.000 |
| 2000 | 0.520 ± 0.070 | 0.000 | 20.0 | 0.617 | 0.002 | 0.288 | 0.000 |

The splice has no burn-in, so the H = 0 control at 0.05 is a
first-tick transient at a world's start (the retrained seed mean 0.302
is one seed's 0.905, the other two 0.000; the frozen probe's 0.678 at
0.10); from H = 1 the retrained head's control is
at most 0.022 at both thresholds. The retrained head's splice curve
flattens near 0.52–0.60 from H = 50 on at 0.10 (0.61–0.68 at 0.05),
above the frozen probe's plateau of 0.29 and under its own natural-row
figures at the pick (0.86–0.92): the splice's donors are young
covered graves jumped into, not crossings, and the retrained head
anticipates a crossing it can watch arrive. The clock read on L's 60
clean 20,000-tick evaluation slices: the mean logit −7.37 / −9.99 /
−11.07 / −12.63 / −12.96 / −12.45 / −10.26 / −9.38 / −9.35 / −9.66 at
ticks 0 / 1 / 2 / 5 / 10 / 25 / 50 / 100 / 300 / 1,000 (the frozen
head's −1.83 / −4.06 / −9.37 at 0 / 1 / 10), the per-slice slope over
t ≥ 300 0.0042 / −0.0024 / 0.0016 logits per 1,000 ticks by seed
(mean 0.001), the within-slice SD 1.04 / 1.19 / 1.17 (the frozen
head's 0.94 ± 0.08). No upward drift over t ≥ 300 (the profile rises
3.6 logits between tick 10 and tick 100, then stays flat).

## R-C, the lived evaluation worlds (`reads/lived.json`; Phase 1d's R4d reader, B applied to every slice's first B ticks)

| group | cell | head | reset detected | false runs per 10k observer-ticks (all) | mid-world runs per 10k |
|---|---|---|---|---|---|
| P (50 worlds, 4.0M observer-ticks) | t0.05-B2 | retrained | 0.988 ± 0.003 | 0.243 ± 0.119 | 0.243 ± 0.119 |
| P | t0.05-B2 | frozen | 0.985 ± 0.000 | 0.258 ± 0.141 | 0.258 ± 0.141 |
| P | t0.10-B0 | retrained | 0.988 ± 0.003 | 0.331 ± 0.275 | 0.175 ± 0.064 |
| P | t0.10-B0 | frozen | 0.995 ± 0.009 | 1.607 ± 0.805 | 0.072 ± 0.003 |
| L / W / G (19 worlds) | t0.05-B2 | retrained | 0.983 ± 0.008 | 0.876 ± 0.191 | 0.876 ± 0.191 |
| L / W / G | t0.05-B2 | frozen | 1.000 ± 0.000 | 0.546 ± 0.070 | 0.546 ± 0.070 |
| L / W / G | t0.10-B0 | retrained | 0.990 ± 0.010 | 0.812 ± 0.144 | 0.676 ± 0.128 |
| L / W / G | t0.10-B0 | frozen | 1.000 ± 0.000 | 0.795 ± 0.185 | 0.277 ± 0.099 |

At the pick the retrained head's false runs are 0.94× the frozen
probe's on group P and 1.60× on L / W / G (P19's clause: at most 2×
on each). Reset detection on P's 200 covered reset episodes 0.988
against 0.985 at the pick. The frozen probe's 1.607 at 0.10 / B = 0 on
P is its first-tick transient (1d); about half of the retrained
head's 0.331 there is first-tick (0.175 mid-world).

## R-D, the estimate (`reads/estimate.json`; Phase 1's reader on the 1b evaluation worlds; pooled mse5 in points², seed mean ± SD; ratio = retrained over frozen on the seed means)

| group | version | class | retrained | frozen | ratio |
|---|---|---|---|---|---|
| P | visible | COMMON | 26.09 ± 0.44 | 25.34 ± 0.52 | 1.029 |
| P | visible | DA | 660.81 ± 46.18 | 773.25 ± 20.58 | 0.855 |
| P | visible | GRAVE | 767.82 ± 60.38 | 908.10 ± 33.43 | 0.846 |
| P | all | COMMON | 34.70 ± 0.57 | 33.68 ± 0.54 | 1.030 |
| P | all | GRAVE | 821.07 ± 47.35 | 894.45 ± 21.77 | 0.918 |
| L / W / G | visible | COMMON | 26.78 ± 0.41 | 26.18 ± 0.61 | 1.023 |
| L / W / G | visible | DA | 525.67 ± 26.12 | 550.26 ± 9.97 | 0.955 |
| L / W / G | visible | GRAVE | 599.43 ± 64.63 | 603.31 ± 18.40 | 0.994 |
| L / W / G | all | DA | 602.31 ± 60.21 | 553.02 ± 6.70 | 1.089 |
| L / W / G | all | GRAVE | 633.13 ± 82.24 | 561.13 ± 5.00 | 1.128 |

The scored cells (P20): group P's mind-visible GRAVE 0.846, L / W /
G's mind-visible COMMON 1.023, both under 1.10. Reported beside them:
L / W / G's all-samples GRAVE cell is 1.128 (the L / W / G fog rows,
not split by world type; a seed SD of 82 against 5) and its
all-samples DA 1.089; group P's mind-visible grave happiness error
154.7 against 198.4. The P "all" DA row is in the JSON (0.924).

## Predictions, scored (`reads/score.json`; S = t0.05-B2 by amendment 1)

| | bar | figure | verdict |
|---|---|---|---|
| P16 | each N stratum above the frozen pick's confirming figure and mean gain ≥ 0.15 | 0.920 / 0.880 / 0.863 against 0.596 / 0.444 / 0.421; gains +0.324 / +0.436 / +0.442, mean +0.401 | MET |
| P17 | E-H1 ≥ 0.489 − 0.05; T-H0 ≥ 0.95 | 0.786; 1.000 | MET |
| P18 | splice at 0.10: H = 100 > 0.358, H = 0 ≥ 0.95, control ≤ 0.05 at every H ≥ 2 | 0.598; 0.988; max 0.013 | MET |
| P19 | lived-world false runs at S ≤ 2× the frozen probe's at the pick, P and L / W / G | 0.94× and 1.60× | MET |
| P20 | group-P visible GRAVE mse5 and L / W / G visible COMMON mse5 ≤ 1.10× | 0.846 and 1.023 | MET |

Unscored expectations: anticipation at S above the frozen pick's —
yes, 0.84–0.89 against 0.21–0.28 in the N strata; median latency
under the frozen's — yes, 0.0 against 2.3–35.0 in the N strata; the logit at tick 10
above −9 — no, −12.96 (the retrained head sits lower on clean slices,
not higher; its slope is zero); TE's early crossings detected like
arm E's — E-H1 0.786 on the confirming half against the tuning half's
0.865.

## Decision rules, applied

P16 and P18 met, with P17, P19 and P20: by DECLARATION §6 the
retrained head NF1e-h24+p is the Phase 2 candidate, and the Phase 2
declaration cites the confirming figures at her pick (1.000 / 0.786 /
0.920 / 0.880 / 0.863 at T-H0 / E-H1 / N-H2 / N-H3 / N-H4, covered
false runs 2.40 per 10,000 observer-ticks in arm N). Whether it feeds
anything that acts stays on her new ruling (the observer-stream
ruling's last clause). Under amendment 1 the price is hers to weigh
in welfare units, not a bar: beside a refusing friend, 0.72 false
runs per observer per 1,000 ticks of 17.8 ticks each (the frozen
probe's 0.19 of 12.9); on lived worlds with no refusing friend, 0.94×
and 1.60× the frozen probe's. What a false run costs a cat that acts
on it is the Phase 2 declaration's to measure with an acting consumer.
Her words "reevaluate model architecture if that doesn't work" are not
reached: it worked. Recommendation 6 (reopening SD) stays closed.

## What stands alone

F-072 minted: the frozen NF-h24+p's late-history miss (F-069, F-070,
F-071) was a coverage gap in its training data, closed by the same
recipe with late-history graves in the training worlds — confirming
detection 0.92 / 0.88 / 0.86 at the pick against 0.60 / 0.44 / 0.42,
the splice at H = 100 0.60 against 0.36 with the junction control at
most 0.013, the estimate held, and the false runs beside a refusing
friend 3.8× the frozen probe's. F-071's "history curve is the head's, not the
splice's" stands; this arc says which part of the head: the data it
saw.

## Guards and reds

e1–e7 red on record before any collection (DECLARATION §7; e3 one
re-red after a wrong tie-break prediction). The readers' guards of
construction held in the reads themselves: the frozen probe at the
pick on the confirming half reproduced R5's five figures to three
decimals (asserted in `score_confirming`); the lived read reproduces
the sweep's committed row and the estimate read 1b's 908.10 cell by
the same functions the guards e7 and e6 hold; the splice reader's
reproduction of the committed H = 100 rows per seed is guard e5 (the
splice read loads the committed rows, it does not re-run the frozen
head). The confirming half was read at
two cells (the pick and the registered point) by two heads, after the
probe-rise read's three cells.

## Limitations

1. The friend is scripted and refuses help (`needy` at 90). The
   detection figures are of a scripted friend's crossing; the covered
   evidence is the splice (R-B), whose donors are young graves jumped
   into after H clean ticks, where the retrained head reaches 0.52–0.60
   from H = 50 on at 0.10, not its natural-row 0.86–0.92.
2. The false-run excess is concentrated where a friend refuses help
   (arms E and N; arm T 0.1222 against 0.0722; the lived worlds 0.94×
   and 1.60×); what those alarms are is not read here (no mechanism claim). In this
   composition covered friends do reach grave in some worlds (65 of
   the 115 TN training worlds held a covered grave tick), so some
   covered alarms may sit near real distress without touching a grave
   tick; the confirming half's own count is not read here.
3. One recipe, one width, three seeds; the training set follows arm
   N's schedule; S is her pick, not a tuned point; the grid's 0.50 cell
   (0.762 / 0.615 / 0.682 on the tuning half at 0.711 covered false
   runs) was not read on the confirming half; no cell beyond the pick
   and the registered point was.
4. The L / W / G all-samples GRAVE cell rose to 1.128× (its fog rows,
   not split by world type); not a scored cell, reported.
5. The 2× clause of P19 and the 0.15 of P16 are this thread's bars,
   declared before the data; the welfare judgment on the price is hers
   (amendment 1).
6. The design does not separate late-grave coverage from more data:
   the training set grew from 74 to 194 worlds and the probe's grave
   frequency from 0.00300 to 0.01821 together. "Coverage gap" names
   the data the frozen head lacked; a same-size control set without
   late graves was not run.

## Regeneration (reads)

```
### Collect and Train (never run by the gate): DECLARATION §11
### Read (the gate runs these; fresh outputs to its scratchpad, never over reads/)
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $P/collect_1e.py read --out <scratch>/collect.json --md                 # about 5 s
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $P/read_1e.py tuning     --out <scratch>/tuning.json --md --quiet       # about 30 s
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $P/read_1e.py confirming --out <scratch>/confirming.json --md --quiet   # about 60 s; S from reads/S.json (amendment 1)
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $P/read_1e.py splice     --out <scratch>/splice.json --md --quiet       # about 10 s
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $P/read_1e.py lived      --out <scratch>/lived.json --md --quiet        # about 15 s
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $P/read_1e.py estimate   --out <scratch>/estimate.json --md --quiet     # about 10 s
```

(`A` = `experiments/needy-set-2026-10-28`, `P` =
`experiments/minifriend-phase1e-2026-11-01`, absolute paths in use;
`score` gathers from `reads/` and is a copy, not a read.)

**Accuracy gate: PASS 2026-11-02, round 3** (rounds 1 and 2 FAIL on
wording only; every regenerated number equal in every round). Round 3
claims: about 560 arithmetic (557 SUPPORTED, 3 ROUNDING), 9 threshold
(all sourced, all correct), 34 characterisation (32 SUPPORTED, 2 WEAK
reworded after the pass), about 45 provenance (all SUPPORTED), 1
UNDECIDABLE (e5 is a guard, not a read; reworded). Raw-dir hashes:
the ten `v1:` values in §Collection by `scripts/rawdir-hash.sh`,
recomputed by the gate. Raw-dir
hashes of the training set are in §Collection; the heads and probes
are under `results-raw/heads/NF1e-h24-s<k>/` and
`results-raw/probe/NF1e-h24-s<k>+p/` (sha256 in their `done.json`).
