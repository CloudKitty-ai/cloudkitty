# Gen 2 Phase 2 entry gate — results (read 2026-11-06 UTC, the evening of 2026-11-05 local; zero collection)

Declared 2026-11-05 at ec67845a on her words "Agreed" (the five steps)
and "Let's do it" (gate by replay); guards g1–g7 red on record at
b5b6c9a4; the four reads ran on her "Go" (`run_gate.sh`: sample 06:11,
act 06:17, needs 06:19, verdict 06:19 UTC). Two reporting fixes landed
after that first run (DECLARATION §7, "After the first read"; 7b7459f2
and e1ed7605, each red through g5): the act read was re-run and its rows
checked equal to the first run's; the verdict was re-derived from them.
No rule, pin, prediction, sample or row value changed. The needy set's
TUNING half: 180 worlds (T 25, E 40, N 115), covered observers reading
covered friends. 0 covered cat-ticks; every branch discarded.

## Headline

**GATE: FAIL, on the needs head.** Both act heads pass: neither B10 nor
B15 carries the ostrich shape in the act currency, pooled, in either
version (P34 MET). The needs head NF1e-h24+p fails Phase 1's signature on
both versions: a grave friend in sight is read 3.17 need points less needy
than she is while a common one is read 0.07 points MORE needy (lift 43.8,
gap −3.24 points; the all-ticks version −2.71 / +0.09, gap −2.80). That is
an 88% cut from the frozen NF-h24+p on the same rows (−26.86 in sight,
P35 MET) and the shape is still there, so by the frozen rule Phase 2 does
not enter on NF1e as its needs head. Per DECLARATION §5 the next step is a
Phase 1f composition arm on the needs head, on her word. The frequency
predictor F, a reference never gated, DOES show the act signature (grave
+0.327 vs common +0.077 in sight, lift 4.2; all-ticks lift 5.4): the
instrument sees the shape where it should and not in the heads.

Two of this thread's predictions failed. The one-tick price is not sparse
at the predicted level: of the points that branched, 0.36–0.71 moved
happiness by stratum, against the predicted "under 0.30" (P36 NOT MET).
And the arm heads' price is NOT larger in GRAVE than in COMMON — three of
the four arm × version cells have it smaller (P37 NOT MET for the arms;
MET for F). The arms' errors are pessimistic everywhere: substituting the
predicted act leaves the friend 0.06–0.20 happiness points WORSE off than
her recorded act, in every stratum, both versions; the needs read moves
the same way (branch needs higher by 0.05–0.20 points).

Open-loop B10 vs B15: no stratum shows B15's price under B10's beyond the
seed SD (the largest gap is 0.013 points at COMMON in sight against SDs of
0.026 and 0.014), so by §5 the Phase 2 declaration records the B10
comparator arm's expected result as a null; the arm count stays hers.

## What ran

`gate_screen.py sample | act | needs | verdict` (DECLARATION §4) on the
pinned binding (engine 5928b7ca), never a collect. Heads: B10-s1..3 and
B15-s1..3 from the act arc's store (8,182 / 12,438 parameters, frozen,
B15 registered through the ladder arc); NF1e-h24-s1..3+p through the
Phase 1e diagnostics' `heads("new")` and NF-h24-s1..3+p through
`heads("frozen")`. Worlds: `needy-set-2026-10-28/results-raw/set/`,
tuning seeds; configs resolve in the needy-set arc, then Phase 1b's. The
act read replayed 163 worlds (the ones holding sampled points), 3,417
replays for 12,600 rows (1,800 points × 7 predictors); the needs read
walked all 180 worlds with the six heads.

## R-0 — branch points (`reads/sample.md`)

| stratum / version | candidates | sampled | insufficient (< 200) |
|---|---|---|---|
| GRAVE / visible | 21,688 | 300 | no |
| GRAVE / all | 32,931 | 300 | no |
| ADJACENT / visible | 84,287 | 300 | no |
| ADJACENT / all | 118,299 | 300 | no |
| COMMON / visible | 5,047,625 | 300 | no |
| COMMON / all | 9,710,610 | 300 | no |

Every cell is covered a hundredfold over the min-n floor; no INSUFFICIENT
verdict arises. The unscored expectation "GRAVE/visible candidates
between 200 and 2,000" was wrong by an order of magnitude: 180 worlds
hold 21,688, from a heavy tail (the one N world smoked, 353, sits at the
89th percentile of worlds; the N-world median is 27, the maximum 2,001;
the T worlds hold none). GRAVE
sampled points by friend (B15-s1 rows, in sight / all): Clementine 92 /
97, Pumpkin 80 / 73, Miso 63 / 58, Kittybear 43 / 46, Biscuit 22 / 26.

## R-1 — the act branches (`reads/act.md`; signed divergence = branch − record; happiness points, hidden-need points; seed mean ± SD per arm)

In sight (the observer sees the friend at t):

| stratum | predictor | n | mean Δhap | mean Δneed | mean \|Δhap\| | branched | moved |
|---|---|---|---|---|---|---|---|
| GRAVE | B10 | 300 | −0.128 ± 0.018 | +0.144 | 0.192 | 0.210 | 0.111 |
| GRAVE | B15 | 300 | −0.140 ± 0.008 | +0.157 | 0.192 | 0.226 | 0.117 |
| GRAVE | F | 300 | +0.327 | −0.468 | 0.504 | 0.773 | 0.323 |
| ADJACENT | B10 | 300 | −0.161 ± 0.003 | +0.135 | 0.164 | 0.172 | 0.079 |
| ADJACENT | B15 | 300 | −0.162 ± 0.004 | +0.136 | 0.163 | 0.154 | 0.074 |
| ADJACENT | F | 300 | +0.464 | −0.695 | 0.667 | 0.773 | 0.393 |
| COMMON | B10 | 300 | −0.144 ± 0.010 | +0.142 | 0.194 | 0.263 | 0.151 |
| COMMON | B15 | 300 | −0.129 ± 0.022 | +0.133 | 0.181 | 0.254 | 0.144 |
| COMMON | F | 300 | +0.077 | −0.165 | 0.345 | 0.420 | 0.330 |

All ticks:

| stratum | predictor | n | mean Δhap | mean Δneed | mean \|Δhap\| | branched | moved |
|---|---|---|---|---|---|---|---|
| GRAVE | B10 | 300 | −0.059 ± 0.028 | +0.054 | 0.128 | 0.229 | 0.096 |
| GRAVE | B15 | 300 | −0.090 ± 0.006 | +0.082 | 0.121 | 0.219 | 0.079 |
| GRAVE | F | 300 | +0.498 | −0.674 | 0.561 | 0.773 | 0.387 |
| ADJACENT | B10 | 300 | −0.197 ± 0.017 | +0.193 | 0.237 | 0.234 | 0.094 |
| ADJACENT | B15 | 300 | −0.197 ± 0.009 | +0.198 | 0.235 | 0.238 | 0.094 |
| ADJACENT | F | 300 | +0.464 | −0.689 | 0.756 | 0.817 | 0.413 |
| COMMON | B10 | 300 | −0.168 ± 0.021 | +0.145 | 0.272 | 0.297 | 0.210 |
| COMMON | B15 | 300 | −0.163 ± 0.015 | +0.141 | 0.264 | 0.292 | 0.194 |
| COMMON | F | 300 | +0.091 | −0.195 | 0.427 | 0.467 | 0.430 |

`branched` is the share of the 300 points whose predicted class differed
from the applied class AND mapped to a legal menu action (so a replay
ran); `moved` is the share of the 300 whose happiness changed at all.
The share of BRANCHED points that moved is the ratio: arms 0.36–0.71 by
cell (in sight GRAVE 0.53 / 0.52, ADJACENT 0.46 / 0.48, COMMON 0.57 /
0.57 for B10 / B15; all ticks 0.42 / 0.36, 0.40 / 0.40, 0.71 / 0.67), F
0.42–0.92. Pooled over the 1,800 points, each arm head predicted the
applied class on 0.729–0.742 of them (F on 0.137: it always predicts
`play`, which is applied on 246 of 1,800). 669 of the 12,600 rows had a
predicted class with no legal menu entry at t and idle illegal too, so
the record stood (predicted `play` 443, `move` 110, `idle` 95, `sleep`
14, `rest` 6, `groom` 1; F 347 of them, each arm seed 51–59). The
branched points whose class had more than one legal entry (§8 item 2;
within-class choice by the friend's own policy): in sight GRAVE 0.262 /
0.305 (B10 / B15), ADJACENT 0.401 / 0.424, COMMON 0.691 / 0.659, F
0.724 / 0.711 / 0.389 by stratum; all ticks GRAVE 0.370 / 0.466,
ADJACENT 0.527 / 0.524, COMMON 0.558 / 0.567, F 0.642 / 0.637 / 0.264.
So a quarter to a half of the arms' grave branches, and over half of
their common ones, rest on the thread's within-class choice.

The act signature (§5): lift = |GRAVE mean Δhap| / |COMMON mean Δhap|
with the GRAVE mean POSITIVE.

| arm / version | GRAVE | COMMON | lift | grave mean | signature |
|---|---|---|---|---|---|
| B10 in sight | −0.128 | −0.144 | 0.89 | negative | no |
| B15 in sight | −0.140 | −0.129 | 1.09 | negative | no |
| B10 all | −0.059 | −0.168 | 0.35 | negative | no |
| B15 all | −0.090 | −0.163 | 0.55 | negative | no |
| F in sight | +0.327 | +0.077 | 4.24 | positive | YES (reference) |
| F all | +0.498 | +0.091 | 5.44 | positive | YES (reference) |

(F's lifts from the unrounded means.) Per friend, "investigate" only
(§5): for B10 and B15 no friend shows the signature in either version;
two friend cells have a lift over 1.5 for both arms with a NEGATIVE grave
mean, pessimism, not the ostrich: Kittybear in sight (4.5 / 5.5; grave
−0.224 / −0.246) and Pumpkin over all ticks (3.5 / 3.1; −0.092 /
−0.115). For F
the signature holds on four of five friends in sight (all but Biscuit,
whose grave and common means are equal at +0.20) and on all five over
all ticks.

Direction of the arms' errors. Every arm cell has a negative mean Δhap
and a positive mean Δneed: when the head's class is wrong, the class it
names leaves the friend slightly worse off one tick later than what she
actually did. The recorded act is her own policy's choice on her own
state; a reader's wrong guess, mapped to a legal act of that class, is
not better than it, and the largest prices sit on the need-serving acts
the heads missed (move predicted where a grave friend drank: 22 rows at
−5.65 points). F's errors run the other way: `play` for a grave
friend who in fact idled, moved or rested (267, 109 and 31 of F's
branched grave rows in sight and all ticks together, at +0.39, +1.10 and
+0.17 points) raises her happiness in the one tick and lowers her need
mean (−0.47 / −0.67 points pooled) — rosier on both currencies, the
ostrich shape in the dumb predictor. Where she in fact ate or drank the
substitution is pessimistic (2 rows at −6.35, 7 at −1.83), the unscored
expectation's own case ("F's GRAVE mean Δhap negative"), but those rows
are few and the pooled mean is positive: the expectation was wrong.

## R-2 — the needs head's step 2 (`reads/needs.md`; bias = predicted − true hidden needs, need points, mean of five; negative = read less needy than she is)

| head | version | GRAVE (n) | COMMON (n) | gap | lift | signature |
|---|---|---|---|---|---|---|
| NF1e-h24+p | in sight | −3.17 (21,688) | +0.07 (5,047,819) | −3.24 | 43.83 | YES |
| NF1e-h24+p | all | −2.71 (32,931) | +0.09 (9,712,770) | −2.80 | 28.93 | YES |
| NF-h24+p (frozen) | in sight | −26.86 (21,688) | −0.33 (5,047,819) | −26.52 | 80.70 | YES |
| NF-h24+p (frozen) | all | −24.11 (32,931) | −0.30 (9,712,770) | −23.81 | 79.31 | YES |

Seed mean of the three heads' per-seed means; no seed's GRAVE cell is
under 200 (INSUFFICIENT false everywhere). The needs read counts every
covered (k, j, t) including t = 0 while the branch candidates start at
t = 1 (§4 R-0), so its COMMON n runs 2,160 rows over the candidate count
on all ticks (180 worlds × 12 covered pairs, one t = 0 row each, every
one COMMON: the GRAVE counts are equal) and 194 over in sight.

Per friend (NF1e, grave / common bias; Phase 1's signature per friend):
in sight Miso −2.55 / −0.15 SIG, Biscuit −10.51 / +0.42 SIG, Pumpkin
+0.36 / −0.10 no, Kittybear −0.60 / +0.74 no, Clementine −5.88 / −0.54
SIG — three of five; all ticks Miso −2.88 / −0.08 SIG, Biscuit −10.67 /
+0.46 SIG, Pumpkin +0.77 / −0.08 no, Kittybear +0.98 / +0.79 no,
Clementine −6.05 / −0.62 SIG — three of five. The frozen head: five of
five in both versions (grave −12.33 to −39.18). Biscuit carries the
largest NF1e bias and the fewest grave rows (1,455 in sight).

Reading the lift. NF1e's COMMON bias sits near zero (+0.07 / +0.09), so
the lift's denominator is small and 43.8 / 28.9 overstate the shape's
size; the gap, −3.24 / −2.80 need points, is the magnitude to carry. The
rule is Phase 1's verbatim (`read_phase1.ostrich`, LIFT 1.5) and the
GRAVE bias alone is far from zero; the verdict does not turn on the
denominator. For scale: Phase 1b read the frozen NF-h24 at −10.10 in
sight on group P's worlds; on this set (a different world set; grave
depth is not measured here) the same frozen head reads −26.86, and NF1e
cuts that to −3.17 (12% of the frozen magnitude) without removing the
sign.

## R-3 — verdict (`reads/verdict.md`; §5 applied)

| head | role | verdict | in sight: grave / common / lift / sig | all: grave / common / lift / sig |
|---|---|---|---|---|
| B10 | comparator arm | **PASS** | −0.13 / −0.14 / 0.89 / no | −0.06 / −0.17 / 0.35 / no |
| B15 | Phase 2 act head (her pick) | **PASS** | −0.14 / −0.13 / 1.09 / no | −0.09 / −0.16 / 0.55 / no |
| NF1e | Phase 2 needs head | **FAIL** | −3.17 / +0.07 / 43.83 / YES | −2.71 / +0.09 / 28.93 / YES |

**GATE: FAIL** (fail-closed; min-n 200, lift 1.5). The gate passes only
if B15 and NF1e both pass (§5); B15 passes, NF1e does not.

## Predictions scored (DECLARATION §6)

- **P34 MET.** Neither B10 nor B15 shows the act signature, pooled, in
  either version: every arm × version lift is under 1.5 (0.35–1.09) AND
  every GRAVE mean is negative.
- **P35 MET.** NF1e's pooled in-sight GRAVE bias (−3.17) is smaller in
  magnitude than the frozen head's on the same rows (−26.86). Whether it
  clears the signature was not predicted: it does not (lift 43.8, grave
  negative).
- **P36 NOT MET.** Predicted under 0.30 of the BRANCHED points moving
  happiness in every stratum; observed 0.36–0.71 by arm × stratum ×
  version (the smallest, B15 GRAVE all ticks, 0.36). The move → rest zero
  of the re-step probe was two ticks of two worlds, both in common
  states, and holds in its own stratum only: the same substitution,
  rest predicted where she moved, moves happiness on 0 of 12 arm COMMON
  rows but on 0.27 of 15 GRAVE rows and 0.50 of 8 ADJACENT rows. Among
  the arms' branched GRAVE rows the near-zero pairs include idle
  predicted where she moved (256 of 795, 0.06 moved), move where she
  idled (90, 0.12) and move or idle where she chased (23 and 21, 0.00);
  idle predicted where she rested, slept or groomed moves happiness on
  0.79 / 1.00 / 1.00 of rows, move predicted where she played on 0.92.
- **P37 NOT MET for the arms, MET for F.** Mean |Δhap| GRAVE vs COMMON:
  B10 in sight 0.1922 vs 0.1941, B15 in sight 0.1923 vs 0.1809, B10 all
  0.1280 vs 0.2717, B15 all 0.1208 vs 0.2641 (unrounded means; one of
  four arm cells larger in GRAVE, by 0.011); F 0.504 vs 0.345 and 0.561
  vs 0.427. The grounds ("a grave friend has more to lose from a misread
  tick") did not hold for the heads: the commonest grave misread is idle
  predicted where she moved (256 of the arms' 795 branched GRAVE rows,
  mean |Δhap| 0.018), while the commonest common misreads are play
  predicted where she chased or moved (242 of 996, 0.36–0.40), and in
  COMMON more of the points branch (0.25–0.30 vs 0.21–0.23). The rule's
  design, differential and signed, is unaffected: it was chosen so that
  a price difference alone could not fail a head, and here it would have
  passed one.

Unscored expectations: B15's mean |Δhap| at or under B10's in every cell
— five of six cells under (by 0.001–0.013), GRAVE in sight over by 0.0001
(0.1923 vs 0.1922), all within the seed SD; F's GRAVE mean Δhap negative
— WRONG, positive in both versions (+0.327 / +0.498); GRAVE/visible
candidates 200–2,000 — WRONG, 21,688.

## Decision rules applied (DECLARATION §5)

- **Act head (B15; B10 beside).** No cell under 200 candidates; the
  signature holds in neither version → **PASS** for B15 and for B10.
- **Needs head (NF1e).** No seed's GRAVE cell under 200; Phase 1's
  signature holds in both versions → **FAIL**.
- **The gate FAILS.** Per §5: "FAIL on NF1e → Phase 2 does not enter; the
  next step is a Phase 1f composition arm on the needs head (her word)."
  The INSUFFICIENT remedy is not reached. Per-friend signatures are
  reported above as "investigate", never as the verdict.
- **B10 vs B15, open-loop.** No stratum shows B15's price under B10's
  beyond the seed SD (differences 0.0001–0.013 against SDs 0.004–0.026)
  → "the Phase 2 declaration records that the B10 comparator arm's
  expected result is a null; the arm count stays her call ('three arms'
  is the default)."

## What this says, and what it does not

The act heads' errors carry no welfare direction by state: the gate's
instrument, which finds the ostrich shape in F at lift 4–5, finds none
in B10 or B15, and their errors run pessimistic in every stratum. A
policy fed B15's beliefs is not fed a rosier picture of grave friends on
the act channel. The needs head is a different matter: Phase 1e's
retraining with late graves (F-072) cut the grave bias by 88% on this
set and left its sign and its differential shape, on three of five
friends, with Biscuit at −10.5 points. Phase 1e's own reads never put
the ostrich metric on NF1e (the prereg reads it "on BOTH estimates, per
phase"; this is the first read on this head), so the shape was not
hidden, only unread.

What this read does not say: how a Phase 2 policy would use either head
(§8 item 1: one tick never prices visitation shift or compounding); the
observer's own welfare under a wrong belief (§8 item 3); or anything
about the heads on the confirming half, which stays unread. The tuning
half is out-of-sample for every head (the act heads trained on Phase 1e's
194 training worlds; the needy set's seeds are test-only) but it is the
half on which the arm picks were made.

## Guards and reds

g1–g7 green (7 passed) at ec67845a and red on record at b5b6c9a4
(DECLARATION §7: g2 / g4 / g5 / g6 / g7 at the predicted first assertion;
g1 / g3 red at a different assertion than first predicted, re-predicted
and re-run red). The two post-read reporting fixes each added an
assertion to g5 and each went red at the predicted line (7b7459f2:
`KeyError: 'branched'`; e1ed7605: the multi-entry seed mean 1.0 against
0.5); both are in the DECLARATION §7 addendum. No guard was weakened. The
re-run's 12,600 rows equal the first run's, in order, on (cell, world,
k, j, t, predictor, pred, applied, same, action, branched, d_hap,
d_need); 3,417 replays both times (388 s, then 401 s). The re-run's rows
add `legal_in_class` on the 4,386 rows whose predicted class differed
from the applied one; the committed `reads/act.json` is the re-run's.

## Limitations

1. The class → menu mapping is this thread's (§8 item 2): within the
   predicted class the friend's own policy chose. The price where a
   class had several legal entries would move under another choice; the
   share of such points is reported above.
2. One tick (§8 item 1), k = 1 pinned. The price is small in absolute
   terms (0.06–0.20 happiness points for the arms) because most
   substitutions change little in one tick; the rule is differential and
   signed for that reason, and the gate's teeth show in F's lift of 4–5.
3. The lift metric's denominator is the COMMON bias; where that bias is
   near zero (NF1e, +0.07) the lift is large regardless of the grave
   magnitude. The gap is reported beside it; the rule is Phase 1's
   verbatim and the GRAVE bias is 3 points on its own.
4. The needs read is a reader on recorded rows (no replay); it reads the
   heads' bias, not a counterfactual.
5. 669 of 12,600 rows could not branch (no legal entry in the predicted
   class and idle illegal) and stood as the record at zero divergence;
   they dilute the arms' means by about 3% of rows per seed (51–59 of
   1,800) and F's by 19% (347).

## Regeneration (reads)

```
### Read (the gate runs these; fresh outputs to its scratchpad, never over reads/)
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $C/gate_screen.py sample  --out <scratch>/sample.json  --md            # seconds; 180 worlds
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $C/gate_screen.py act     --out <scratch>/act.json     --md --quiet    # about 7 min; 3,417 replays; reads $C/reads/sample.json
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $C/gate_screen.py needs   --out <scratch>/needs.json   --md --quiet    # about 1.5 min; six heads x 180 worlds
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $C/gate_screen.py verdict --out <scratch>/verdict.json --md            # seconds; reads $C/reads/{sample,act,needs}.json
```

(`A` = `experiments/needy-set-2026-10-28`, `C` =
`experiments/minifriend-phase2-gate-2026-11-05`, absolute paths in use.
`act` reads the committed `reads/sample.json` as its points and
`verdict` the committed `reads/{sample,act,needs}.json`; a fresh `sample`
leaf-equal to the committed one and fresh `act` / `needs` leaf-equal but
for `seconds` verify the inputs. Heads: `minifriend-act-2026-11-03/
results-raw/heads/{B10,B15}-s{1,2,3}/head-best.pt`, sha256 in each
`done.json`; NF1e-h24-s<k>+p and NF-h24-s<k>+p through the Phase 1e
diagnostics' loaders. Raw dirs: the needy set's `results-raw/set`
`v1:973e5cf5a4541ba5` (as the needy-set RESULTS' later stamps), the act
arc's heads store `v1:4171820c2260bed7` (as the ladder addendum's stamp);
`scripts/rawdir-hash.sh`.)

**Accuracy gate: PASS 2026-11-06 UTC (2026-11-05 local), round 3**
(rounds 1–2 FAIL on wording only; every regenerated number equal in all
three rounds: the four reads' JSON leaf-equal to `reads/` but for
`seconds`, sample.md and verdict.md byte-identical, act.md / needs.md
identical but for the seconds line, every count equal — six cells'
candidates and 300 sampled, 12,600 rows, 3,417 replays, the needs n per
head and version; the six act heads' sha256 equal to their done.json;
engine 5928b7ca). Round 3: about 267 arithmetic claims (162 table cells
by script, about 105 prose figures by hand) with 0 mismatch and 0
ROUNDING; 6 thresholds all sourced (§5 / `MIN_N` / `LIFT`, P36's 0.30,
§6's 200–2,000, §4's 300); about 32 characterisations, none CONTRADICTED
or WEAK in the fail zones (the "out-of-sample for every head", Phase 1b
−10.10 and "never read on NF1e" claims SUPPORTED against their source
docs); 1 UNDECIDABLE (her "Go" has no repo record outside this commit);
about 16 provenance checks all passed; companions (deviations 21 Status,
the timeline block, the DECLARATION Status and §7 addendum) copy-check
PASS. What rounds 1–2 caught: the title's UTC date (the run crossed
midnight UTC: 2026-11-06, the evening of 2026-11-05 local); "rested, ate
or idled" for F's rosier grave rows when the 2 rows where she ate are
pessimistic (−6.35); "353 was typical" when 353 sits at the 89th
percentile of worlds; a fix that called the re-step probe "one tick of
one world" when it was two, and cited the reverse substitution pair.
Raw dirs `v1:973e5cf5a4541ba5` (set) and `v1:4171820c2260bed7` (heads
store), `scripts/rawdir-hash.sh`.
