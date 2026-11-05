# Act-head calibration — results (read 2026-11-04; zero collection)

Declared 2026-11-04 at 2d111f51 on her word "Sounds good, let's get
started"; guards c1–c7 red on record at 9d048366; the fit and
reliability reads ran on that commit (`seconds` in their JSON: 135 and
117); the score read was re-run after gate round 1 with the corrected
`read_score` (per-head tempering rule, R-3), which is committed with
this write-up. The
heads are the act arc's committed B10-s1..3 and B30-s1..3
(`minifriend-act-2026-11-03/results-raw/heads/`, sha256 in each
`done.json`). Every arm figure is the seed mean ± SD over three heads;
the per-head bins are printed for seed 1. 0 covered cat-ticks.

## Headline

The act head's confidence is honest, and it is informative inside a
regime. At T = 1 B10's top-probability ECE is 0.0057 ± 0.0033 in sight
and 0.0149 ± 0.0079 heard; the temperatures fitted on the validation
split lie in 0.97–1.03 for every non-silent regime (the silent regime,
1,348 thinned samples, fits 0.79–0.97 at y0 and is not applied), so the
NLL-optimal tempering is within three grid steps of none. Confidence
tracks regime (mean top-prob 0.737 in sight against 0.537 heard; P29
MET) and, inside the in-sight cell, entropy separates right ticks from
wrong ones with AUROC 0.860 ± 0.001 (P30 MET): for seed 1 the lowest
entropy bin (0.36 of in-sight ticks) is right 0.996 of the time and the
two highest under 0.3. Heard, the same AUROC is 0.657 ± 0.002. B30's entropy ranks
correct over incorrect ticks within the declared 0.02 of B10's (seen
−0.0002; heard +0.0079, about three seed SDs), so P31 is MET and, by the
rule as declared, B20 is not registered in Phase 2. The rule's declared
rationale, "its log-loss gain is what a temperature supplies for free",
is contradicted by R-2: B30's validation NLL is about 0.047 under B10's
and a temperature recovers at most 0.0003 of it. B30's gain is more correct
answers (top-1 +0.013) and lower log-loss (1.090 → 1.042); its
certainty ranking sharpens only heard, by 0.0079. Whether that earns B20 a registered Phase 2 prediction anyway is hers.
The seen and heard temperatures differ by 0.010 (P32 NOT MET) and the
rule adopts the global temperature, applied per head on this thread's
reading of "a head" (chosen after the read; her word confirms or
overrides; the per-arm reading differs only on B10-s2): B10 frozen at 1.01 / 1.00 / 1.02 (seed 2's fitted 0.99
raised its own ECE in both registered cells and reverts to 1; 0.99 per
arm), B30 at 1.00 / 1.00 / 1.00 (seed 1's 0.98 raised its heard ECE).

## What ran

| read | worlds | samples per head (y0) | seconds |
|---|---|---|---|
| fit (C3a), Phase 1e validation split, covered-friend pairs, every 10th tick after the forward | 52 | 372,000 (seen 189,526, heard 181,126, silent 1,348 — under the floor, takes the global T) | 135 |
| reliability (C1 / C2 / C3b), needy tuning half, covered friends | 180 | 9,864,000 (seen 5,153,794, heard 4,677,151, silent 33,055) | 117 |

Definitions as declared (§2): regimes from `data_act.row_state`; top-prob
bins [0, .2), …, [.9, 1]; normalised entropy −Σ p log p / log 11 in bins
of 0.1; ECE on the top label; AUROC of a certainty score for top-1
correctness from 400-bin histograms, ties half, at T = 1 only; the
temperature grid 0.50–3.00 step 0.01. Cross-checks: every cell's top-1
and log-loss at T = 1 equal the act arc's `reads/accuracy.json` cells
(B10 all 0.634 / 1.090, seen 0.734 / 0.772, heard 0.522 / 1.443; B30
all 0.647 / 1.042); the regimes' counts sum to all.

## R-1 — reliability by regime (`reads/reliability.md`, y0)

| head | regime | n | top-1 | mean top-prob | mean entropy | ECE T = 1 | ECE global T | ECE regime T | AUROC 1 − entropy | AUROC top-prob |
|---|---|---|---|---|---|---|---|---|---|---|
| B10 | all | 9,864,000 | 0.634 ± 0.001 | 0.642 ± 0.006 | 0.443 ± 0.007 | 0.0096 ± 0.0051 | 0.0078 ± 0.0012 | 0.0072 ± 0.0011 | 0.782 ± 0.001 | 0.789 ± 0.000 |
| B10 | seen | 5,153,794 | 0.734 ± 0.001 | 0.737 ± 0.003 | 0.316 ± 0.004 | 0.0057 ± 0.0033 | 0.0048 ± 0.0022 | 0.0049 ± 0.0020 | 0.860 ± 0.001 | 0.864 ± 0.001 |
| B10 | heard | 4,677,151 | 0.522 ± 0.001 | 0.537 ± 0.009 | 0.584 ± 0.011 | 0.0149 ± 0.0079 | 0.0122 ± 0.0041 | 0.0111 ± 0.0027 | 0.657 ± 0.002 | 0.665 ± 0.002 |
| B10 | silent | 33,055 | 0.834 ± 0.002 | 0.841 ± 0.017 | 0.246 ± 0.036 | 0.0240 ± 0.0064 | 0.0252 ± 0.0097 | 0.0252 ± 0.0097 | 0.767 ± 0.016 | 0.767 ± 0.014 |
| B30 | all | 9,864,000 | 0.647 ± 0.003 | 0.651 ± 0.006 | 0.429 ± 0.007 | 0.0056 ± 0.0030 | 0.0072 ± 0.0008 | 0.0067 ± 0.0022 | 0.784 ± 0.001 | 0.792 ± 0.001 |
| B30 | seen | 5,153,794 | 0.745 ± 0.004 | 0.747 ± 0.009 | 0.303 ± 0.009 | 0.0054 ± 0.0013 | 0.0047 ± 0.0022 | 0.0045 ± 0.0021 | 0.860 ± 0.001 | 0.864 ± 0.001 |
| B30 | heard | 4,677,151 | 0.537 ± 0.002 | 0.545 ± 0.003 | 0.569 ± 0.006 | 0.0082 ± 0.0021 | 0.0106 ± 0.0022 | 0.0094 ± 0.0038 | 0.665 ± 0.003 | 0.675 ± 0.002 |
| B30 | silent | 33,055 | 0.837 ± 0.002 | 0.836 ± 0.016 | 0.255 ± 0.030 | 0.0179 ± 0.0025 | 0.0169 ± 0.0017 | 0.0169 ± 0.0017 | 0.770 ± 0.006 | 0.769 ± 0.005 |

Mean top-prob sits within 0.015 of top-1 in every registered cell (B10
seen 0.737 against 0.734, heard 0.537 against 0.522; B30 0.747 against
0.745, 0.545 against 0.537): the heads are slightly over-confident on
the tuning half (B10 by 0.003 in sight and 0.015 heard), more so heard. The temperature fit minimises validation
NLL, not this gap; one grid step of 0.01 moves a cell's mean top-prob by
about 0.002 in sight (B10-s1 0.7384 → 0.7361 at T 1.01) and 0.004
heard (B10-s1 0.5338 → 0.5299 at 1.01; B10-s3 0.5473 → 0.5395 at
1.02), and the NLL-optimal temperatures sit at 0.97–1.03 (R-2), so
most of the residual over-confidence survives tempering: the fit
targets NLL on the validation split, not the ECE on this half, and
which of the two (objective or split) leaves the residue is not
separated here. The silent cell is confident and right (top-1 0.834, mean top-prob
0.841) with the largest ECE, on 33,055 samples; four of its nine top-prob bins are
thin for seed 1 and no prediction rests on it.

**B10-s1, y0, in sight: top-prob reliability (T = 1), then accuracy by entropy.**

| top-prob bin | n | mean conf | accuracy | | entropy bin | n | accuracy |
|---|---|---|---|---|---|---|---|
| [0, 0.2) | 556 thin | 0.192 | 0.174 | | [0, 0.1) | 1,831,911 | 0.996 |
| [0.2, 0.3) | 187,180 | 0.272 | 0.266 | | [0.1, 0.2) | 258,619 | 0.923 |
| [0.3, 0.4) | 550,435 | 0.351 | 0.339 | | [0.2, 0.3) | 406,915 | 0.820 |
| [0.4, 0.5) | 506,421 | 0.448 | 0.427 | | [0.3, 0.4) | 510,187 | 0.745 |
| [0.5, 0.6) | 394,371 | 0.549 | 0.535 | | [0.4, 0.5) | 503,344 | 0.651 |
| [0.6, 0.7) | 457,783 | 0.653 | 0.653 | | [0.5, 0.6) | 607,211 | 0.505 |
| [0.7, 0.8) | 565,823 | 0.750 | 0.741 | | [0.6, 0.7) | 763,499 | 0.379 |
| [0.8, 0.9) | 436,871 | 0.846 | 0.838 | | [0.7, 0.8) | 268,649 | 0.290 |
| [0.9, 1] | 2,054,354 | 0.985 | 0.989 | | [0.8, 0.9) | 3,459 | 0.219 |

Every non-thin bin's accuracy is within 0.021 of its mean confidence.
The entropy column falls monotonically from 0.996 to 0.219 across the
nine populated bins: inside the in-sight regime, the head's own spread
says how often it is right.

**B10-s1, y0, heard.**

| top-prob bin | n | mean conf | accuracy | | entropy bin | n | accuracy |
|---|---|---|---|---|---|---|---|
| [0, 0.2) | 579 thin | 0.192 | 0.221 | | [0, 0.1) | 14,519 | 0.981 |
| [0.2, 0.3) | 178,060 | 0.274 | 0.271 | | [0.1, 0.2) | 47,849 | 0.934 |
| [0.3, 0.4) | 784,064 | 0.355 | 0.351 | | [0.2, 0.3) | 137,000 | 0.849 |
| [0.4, 0.5) | 1,063,756 | 0.451 | 0.443 | | [0.3, 0.4) | 227,795 | 0.758 |
| [0.5, 0.6) | 1,161,996 | 0.550 | 0.536 | | [0.4, 0.5) | 598,618 | 0.652 |
| [0.6, 0.7) | 891,426 | 0.644 | 0.624 | | [0.5, 0.6) | 1,209,445 | 0.566 |
| [0.7, 0.8) | 341,273 | 0.744 | 0.723 | | [0.6, 0.7) | 1,524,529 | 0.459 |
| [0.8, 0.9) | 190,304 | 0.843 | 0.839 | | [0.7, 0.8) | 880,424 | 0.352 |
| [0.9, 1] | 65,693 | 0.937 | 0.944 | | [0.8, 0.9) | 36,972 | 0.269 |

Heard, the bins are as reliable one by one (every non-thin bin within
0.021) while the cell's ECE is larger (B10-s1 0.0118 against 0.0079 in
sight), and the mass has moved: 0.87 of heard ticks sit in top-prob bins under
0.7, against 0.41 in sight, and the entropy curve is the same shape over
a narrower range. The head knows less out of sight and says so; the
0.657 AUROC is what remains to separate right from wrong once the regime
is known.

## R-2 — the temperature fit (`reads/temperature.md`, Phase 1e validation split, y0)

| head, seed | T all | T seen | T heard | NLL at T = 1 → at fit (all) |
|---|---|---|---|---|
| B10-s1 | 1.01 | 1.02 | 1.01 | 1.0797 → 1.0796 |
| B10-s2 | 0.99 | 0.99 | 0.99 | 1.0821 → 1.0821 |
| B10-s3 | 1.02 | 1.01 | 1.03 | 1.0761 → 1.0758 |
| B30-s1 | 0.98 | 0.97 | 0.98 | 1.0360 → 1.0358 |
| B30-s2 | 1.00 | 1.01 | 1.01 | 1.0396 → 1.0396 |
| B30-s3 | 1.00 | 1.00 | 1.00 | 1.0220 → 1.0220 |

Every non-silent fitted temperature lies in 0.97–1.03 (y0 and y10);
the fit lowers the validation NLL by at most 0.0003 with the regimes
pooled, 0.0006 for one regime fit (B10-s3 heard, 1.4132 → 1.4126). The silent regime (1,348 thinned
samples per head) is under the 10,000 floor and takes the global T
(declared §2); its own y0 fits ranged 0.79–0.97 across the six heads and
are printed in `reads/temperature.md` for the record. The B10 seen and heard
temperatures differ by 0.01 / 0.00 / 0.02 per seed (mean 0.010).

## R-3 — the temperings applied to the tuning half (`reads/score.json`, y0)

The declared rule drops a HEAD to T = 1 when its adopted tempering raises
a registered cell's ECE over T = 1. This thread reads "a head" as one trained
seed (the declaration names the heads B10-s1..3 and B30-s1..3 and says
"the fit did not transfer", and each fit is per seed), so the rule is
applied per head; the same paragraph also says "per head and seed" and
§3 registers the cells per arm, so the per-arm reading is tenable, and the
reading was chosen after the numbers were read. Both are printed; her
word confirms or overrides (the only value at stake is B10-s2, 1.00 per
head against 0.99 per arm). P32 not met makes the adopted tempering the
global T.

| head | T global (fit) | ECE seen T = 1 → global | ECE heard T = 1 → global | frozen for Phase 2 |
|---|---|---|---|---|
| B10-s1 | 1.01 | 0.0079 → 0.0069 | 0.0118 → 0.0079 | 1.01 |
| B10-s2 | 0.99 | 0.0019 → 0.0026 | 0.0090 → 0.0125 | 1.00 (both cells worsened) |
| B10-s3 | 1.02 | 0.0073 → 0.0048 | 0.0238 → 0.0162 | 1.02 |
| B30-s1 | 0.98 | 0.0047 → 0.0025 | 0.0057 → 0.0132 | 1.00 (heard worsened) |
| B30-s2 | 1.00 | 0.0047 → 0.0047 | 0.0092 → 0.0092 | 1.00 |
| B30-s3 | 1.00 | 0.0070 → 0.0070 | 0.0095 → 0.0095 | 1.00 |

Read per arm on the seed means (`arm_view`), the same rule gives B10
the global T (seen 0.0057 → 0.0048, heard 0.0149 → 0.0122; the regime T
0.0049 / 0.0111) and B30 T = 1 (seen 0.0054 → 0.0047 but heard 0.0082 →
0.0106; regime T 0.0045 / 0.0094): the two readings differ only on
B10-s2. Per-head movements run from none (B30-s2, s3 at 1.00) to 0.0076
(B10-s3 heard, 0.0238 → 0.0162) and 0.0075 the other way (B30-s1 heard,
0.0057 → 0.0132); B10-s1 heard falls 0.0118 → 0.0079 and B10-s2 heard
rises 0.0090 → 0.0125. Reader correction
after gate round 1: `read_score` had applied the rule per arm; it now
applies it per head with the arm view kept beside; no guard covers the
score step, so the change is recorded here.

## Predictions scored (DECLARATION §6)

- **P29 MET.** B10 mean top-prob y0: seen 0.737 − heard 0.537 = 0.200
  ≥ 0.10 (per seed 0.7384 / 0.7337 / 0.7390 against 0.5338 / 0.5293 /
  0.5473).
- **P30 MET.** B10 in-sight AUROC of 1 − entropy for y0 correctness
  0.860 ≥ 0.70 (per seed 0.861 / 0.859 / 0.860).
- **P31 MET.** B30 − B10 AUROC of 1 − entropy, y0: seen 0.860 − 0.860 =
  −0.0002, heard 0.665 − 0.657 = 0.0079; both < 0.02.
- **P32 NOT MET.** |T_seen − T_heard| for B10 y0 = 0.010 (per seed
  0.01 / 0.00 / 0.02) < 0.10.
- No registered cell is UNDECIDABLE (the smallest holds 4,677,151
  samples against a floor of 10,000).

Unscored expectations, reported: ECE at T = 1 under 0.05 in sight
(0.0057) and larger heard (0.0149) — as expected; the heard temperature
above 1 — PARTLY: 1.01 / 0.99 / 1.03 for B10 and 0.98 / 1.01 / 1.00 for
B30 straddle 1; the tuning-half over-confidence (0.015 of top-prob heard)
is not what a validation NLL fit targets; y10 flatter than y0
in every regime (mean entropy 0.707 against 0.443 for B10 all) with the
lower AUROC (0.609 against 0.782) — as expected; the silent cell's bins
mostly thin — PARTLY: 4 of 9 top-prob bins under 1,000 for B10-s1, the
mass in [0.9, 1] (18,954 of 33,055); top-prob's AUROC within 0.02 of entropy's —
as expected (0.789 against 0.782 all; 0.864 against 0.860 seen; 0.665
against 0.657 heard).

## Decision rules applied (DECLARATION §6)

- **Tempering for Phase 2's certainty cells.** P32 not met → the global
  temperature, applied per head on this thread's reading of "a head"
  (R-3; chosen after the read, her word confirms or overrides): B10
  frozen at 1.01 / 1.00 / 1.02 (seed 2's fitted 0.99 raised its ECE in
  both registered cells → T = 1; per arm it would stay 0.99, the one
  value at stake), B30 at 1.00 / 1.00 / 1.00 (seed 1's 0.98 raised its
  heard ECE → T = 1; seeds 2 and 3 fitted 1.00). Phase 2 declares the
  confirmed values verbatim and never refits.
- **The B20 question.** P31 met → B20 is not registered in Phase 2,
  as declared. The rule's stated rationale — "its log-loss gain is what
  a temperature supplies for free" — is contradicted by R-2 (a
  temperature recovers at most 0.0003 of B30's roughly 0.047 NLL
  advantage on the validation split; B30's tuning top-1 is 0.013 higher).
  The rule is applied as written; whether B30's real gain earns
  B20 a registered Phase 2 prediction after all is her call, reported.
  B10 stands as declared (F-074).
- **The certainty cells.** P30 met → entropy and top probability are
  Phase 2's two certainty scalars and the declaration may call them so.
  The in-sight AUROCs are 0.860 and 0.864; heard 0.657 and 0.665. The
  11-way distribution itself is the act input (her design), not a
  certainty cell.
- **P29 met.** Not a declared branch (the rule speaks to "not met");
  reported: the regime discount is available from the head's own
  confidence as well as from the row's seen / heard / silent cells.
- **FINDINGS.** P31's answer stands alone — the ranking question about
  the act head's size the record could not otherwise settle — and the
  calibration result is the first measured certainty of a Gen 2 head's
  act channel: F-075.

## What stands alone

F-075: the act head's stated confidence is right to within 0.006 (in
sight) and 0.015 (heard) of ECE at T = 1 with non-silent fitted
temperatures of 0.97–1.03; its entropy ranks correct over incorrect
in-sight ticks with AUROC 0.860 (heard 0.657); and tripling its parameters
improves that ranking by less than the declared 0.02 (−0.0002 seen,
+0.0079 heard) while adding 0.013 of top-1 and lowering log-loss 1.090
→ 1.042, a gain a temperature does not supply. Domain: Gen 2 rot2
behaviour on the needy set's tuning half, read by the committed heads;
the temperatures from Phase 1e's validation worlds. Invalidation: a
Phase 2 rollout read in which B10's in-sight ECE at the frozen
temperature exceeds 0.05 or its in-sight entropy AUROC falls under 0.70
— the same drift monitor the Professor asked for on F-074's accuracy,
extended to its certainty.

## Guards and reds

c1–c7 (DECLARATION §7) green at 2d111f51 and RED CONFIRMED at
9d048366, each at the predicted first assertion. Four first cycles (c2 /
c3 / c4 / c7) were no-ops from regex escapes in plain-string
replacements and were re-run with plain strings; c4's second cycle then
went red for the wrong reason (exit 7: argmax lands on T 0.5, the sharp
end of the grid, not 3.0), its prediction was corrected and its third
cycle RED CONFIRMED. No file changed.

## Limitations

1. The temperature fit minimises validation NLL; the tuning-half
   over-confidence (mean top-prob over top-1 by 0.002–0.015 in the
   registered cells) is a different quantity on a different split. A
   grid step moves mean top-prob by about 0.002 in sight and 0.004
   heard, so the grid could have removed it and the NLL did not ask it
   to. ECE at T = 1 is under 0.015 in every registered cell on seed
   means (per head, up to 0.0238: B10-s3 heard).
2. AUROC is a ranking measure within a regime; it says nothing about
   how a policy should weight certainty across regimes, which the row's
   state cells and P29's confidence gap supply separately.
3. The silent regime's fits rest on 1,348 thinned validation samples
   and are not applied; its tuning-half ECE (0.024 for B10) is reported
   on 33,055 samples with thin bins.
4. These are the tuning half's covered friends under rot2 behaviour; a
   policy that reacts to the head changes the acts it predicts (F-074's
   re-verify clause), and calibration can drift with accuracy — hence the monitor.
5. The memoryless row-only baseline over each cell's full row
   (Professor's sharpening 2) is not in this read; it is her ruled Phase
   2 side read.
6. P31's 0.02 bar was justified as the seed-spread scale of these
   AUROCs; the measured seed SDs are 0.0007–0.0027, between a seventh and a
   thirtieth of it. The bar stands as declared; the heard gain of 0.0079 is about
   three SDs and is reported as a real, small improvement in ranking.
7. DECLARATION §3 estimated about 2M thinned fit samples per head and
   horizon; the count is 372,000 (seen 189,526, heard 181,126). The
   estimate was wrong; the smaller registered fit cell is 18× the floor
   and no bar is affected.

## Regeneration (reads)

```
### Read (the gate runs these; fresh outputs to its scratchpad, never over reads/)
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $C/calib_act.py fit         --out <scratch>/temperature.json --md --quiet   # about 3 min; Phase 1e validation worlds
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $C/calib_act.py reliability --out <scratch>/reliability.json --md --quiet   # about 2 min; reads $C/reads/temperature.json
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $C/calib_act.py score       --out <scratch>/score.json       --md           # seconds; reads $C/reads/{temperature,reliability}.json
```

(`A` = `experiments/needy-set-2026-10-28`, `C` =
`experiments/minifriend-act-calib-2026-11-04`, absolute paths in use.
`reliability` and `score` read the committed `reads/` files as inputs; a
fresh `fit` equal leaf for leaf to `reads/temperature.json` verifies
those inputs.)

**Accuracy gate: PASS 2026-11-04, round 7** (rounds 1–6 FAIL on wording
and provenance only; every regenerated number equal in all seven rounds:
the three reads' JSON leaf-equal to `reads/` but for `seconds`, the md
files byte-identical, 52 + 180 worlds and every cell count equal, the six
heads' sha256 equal to their done.json). Round 7: 228 reader-backed
table cells and about 70 prose figures all SUPPORTED (8 ROUNDING, each
one unit off the raw value and equal to the reader's printed digits), 11
thresholds all sourced, about 25 characterisations with 1 WEAK outside
the fail zones (a bin count scoped to seed 1 after the pass), about 22
provenance checks all passed, 1 UNDECIDABLE (the Professor's note lives
outside the repo). Post-pass copy words, applied before the commit:
"0.010" for the P32 mean in F-075 and the timeline; "for seed 1" on the
silent bin count; "§3 registers the cells" in R-3. What the six failing
rounds caught, in order: a units error (a temperature step against a
probability gap); a decision rule's rationale restated as the finding
when the data contradicted it; a per-unit rule applied at the arm where
the declaration says head; "every regime" over a regime the fit
excluded; "ran on that commit" over a read re-run on a corrected reader;
"tripling its width" for tripled parameters at doubled width; and a
pending owner word written as settled. Raw-dir hash of the heads:
`v1:5b29e9a2736a84f7` (`scripts/rawdir-hash.sh`).
