# Mini-friend Phase 1d — RESULTS (read 2026-10-24 UTC)

Declaration: `DECLARATION.md` (owner 2026-10-24 "Let's run those in
three in the order you listed", after the Professor's review of Phase
1c; deviations entry 13). Prereg basis frozen 18f06f84, §8 items 3–4.
Binding: Phase 1's arc venv (`../minifriend-phase1-2026-10-22/
BINDING.md`; engine a2e8d044). No new rollout: 0 covered cat-ticks;
no belief head trained; the cap (8,445) not moved. Every read is
descriptive (doctrine rule 10) except the one decision rule declared
before any fit, applied below. Every MSE and bias cell of F-064,
F-065 and F-066 is unchanged by construction: read 1 touches no
weights and read 2 fits 25 parameters on top of frozen states whose
own output reproduces 1b's committed predictions (R2d(b)).

## Headline

**Outcome A by the declared rule: the histogram did not make the
probability.** A 25-parameter logistic read of "the true stratum is
GRAVE" on the frozen NF-h24 states reaches, in sight on the per-cat
worlds, a mean P(grave) on grave samples of 0.583 ± 0.015 against
SD width 16's 0.474 ± 0.115 (Δ = −0.109 with the combined seed spread
s = 0.116, so |Δ| ≤ s: within the spread). Its Brier score is lower
(0.00054 against 0.00064), its mean on common samples lower (0.0003
against 0.0005), and under fog it is well ahead (0.720 ± 0.010 against
0.500 ± 0.046; Brier 0.00119 against 0.00185). SD keeps its reliability
above p = 0.7, closer to the diagonal (above-0.7 gap 0.019 against
0.057; the probe's top bins realise 0.760 and 0.882 where they say
0.854 and 0.959), and a lower mean on adjacent samples (0.183 against
0.265). On the DR-h24 states the same probe
reads 0.577 ± 0.037 in sight with an above-0.7 gap of 0.022. All three
heads rank grave against non-grave almost perfectly (AUROC 0.998–0.999
in every version); what separates them is confidence, not
discrimination. The Professor's registered prediction P2 is met (0.583
≥ 0.40 on grave, 0.0003 ≤ 0.002 on common). By the declaration's text,
the hybrid (a Phase 1 head plus one sigmoid; 7,832 parameters here) is
the candidate shape for a probability-reading Phase 2 consumer, and the
SD line closes.

**The filter smears, exactly as the arithmetic says (R1d).** Pushed n
ticks at a rate whose fractional part is f, a delta belief under 1c's
drift operator has standard deviation √(n f (1 − f)) bins: the
implementation matches the closed form to 2.3 × 10⁻⁸ bins over the 79
rows whose top-bin mass is under 10⁻¹², and after 100 ticks at
every run's initial rate (0.4 points per tick, f = 0.08) the sd is
2.708 bins = 13.5 need points, the Professor's 2.7. At the learned
width-16 median cells (0.124–0.181 points per tick) it is 1.56–1.87
bins (7.8–9.3 points) after 100 ticks, while the engine's need rises
with no uncertainty. The mechanism stands; whether it is the cause of
F-066's residual share is an ablation this arc did not run
(§Limitations).

## Decision rule, applied

Domain as declared: group P evaluation worlds (P1..P5, 4,000,000
samples), in sight (1,927,130 samples; 2,527 grave), every covered
sample pooled, mean of seeds 1–3; comparator SD width 16 from 1c's
committed read (pinned, guard t4); base head NF-h24.

| quantity | value | source |
|---|---|---|
| m_SD, mean P(grave) on GRAVE, SD-w16 | 0.474 ± 0.115 (seeds 0.379 / 0.442 / 0.601) | R2d(a) in sight = 1c's R4c |
| m_NF, the same, NF-h24+p | 0.583 ± 0.015 (seeds 0.571 / 0.600 / 0.578) | R2d(a) in sight |
| Δ = m_SD − m_NF | −0.109 | derived |
| s = √(s_SD² + s_NF²) | 0.116 | derived |
| above-0.7 gap, SD-w16 / NF-h24+p | 0.019 / 0.057 | R2d(a) in sight |
| rule | \|Δ\| ≤ s → **A** | DECLARATION §Read 2 |

A: "the histogram bought nothing the consumer needs; the hybrid (a
Phase 1 head plus one sigmoid) is the candidate shape for a
probability-reading Phase 2 consumer and the SD line closes." Two
things the rule does not say and the read does: the probe sits ABOVE
SD on the grave mean in every version, not merely within its spread
(s is 0.116 because SD's three seeds span 0.379 to 0.601; the probe's
span 0.571 to 0.600), and SD's better cells in sight are the above-0.7
gap (the B clause's second condition, moot once Δ is negative), a
lower mean on ADJACENT samples (0.183 against 0.265) and reliability
nearer the diagonal below p = 0.5 (gaps 0.075–0.106 against 0.101–0.243
in the four bins from 0.1 to 0.5); the gap enters only the Δ > s
branches of the rule (B, and C's first branch), which Δ < 0 rules
out, C's other branch (Δ < −s) is excluded by |Δ| ≤ s, and the other
two cells do not enter the rule.
Brier and fog are context, as declared.

**Predictions scored.** Professor P2 ("the frozen-state logistic read
on NF-h24 reaches mean P(grave) on grave samples ≥ 0.40 (SD-w16:
0.474) and ≤ 0.002 on common samples, in sight"): read 0.583 / 0.0003,
**met**. This arc's
(outcome A with m_NF between 0.35 and 0.60): A, m_NF 0.583, **met**.
Professor P1 (a longer-cap SD re-run stays READ over 1 with the
signature on ≥ 4 friends): not scorable here, carried forward. R1d's
reading rule (closed form within 1e-6 bins; 100-tick initial-rate sd
within 0.1 of 2.7): **both hold**; its third clause (the learned
width-16 median rates give a 100-tick sd below the initial-rate
figure in proportion to √(f (1 − f))): 1.558 / 1.703 / 1.870 bins
against 2.708, each equal to 10.00 × √(f (1 − f)), **holds**.

## Data

Phase 1b's split byte for byte (`split.json`; guard t4): 74 training,
17 validation, 69 evaluation worlds; raws symlinked (L, W, G from
Phase 1; P1..P5 from 1b). The probe's training samples are every
(world, observer, friend, tick) of the training worlds: 8,400,000, of
which the true stratum is GRAVE on 0.00300; validation 1,800,000. The
reads are on group P's 50 evaluation worlds: 4,000,000 samples,
1,927,130 in sight and 2,072,870 under fog; grave samples 2,527 in
sight (168 happiness-only), 8,977 under fog (1,112), 11,504 in all
(1,280). Base heads: 1b's NF-h24-s{1,2,3} and DR-h24-s{1,2,3}
(`head-best.pt`, 7,807 params; sha256 equal to their `done.json` and
to the probe manifests, before and after the fits). SD comparator:
1c's `SD-s{1,2,3}` belief files, re-read here through the same
instrument and equal to 1c's committed R4c cells (Brier, mean p on
GRAVE, mean p on COMMON; in sight and all; guard t4 also checks the
per-seed reliability counts).

## R1d — the filter's spread under pure drift

A delta at bin 2, no relief, no residual, 1c's `shift_matrix` in
double precision; sd in bins (× 5 = need points); "cf" the closed form
√(n f (1 − f)); "clamp" = top-bin mass above 10⁻¹² (the closed form
is exact only before any mass reaches the top; a row just past the
threshold still matches it to about 10⁻⁸; the top-bin mass is in the
JSON).

| rate (points per tick) | n = 1 | n = 10 | n = 50 | n = 100 | n = 500 |
|---|---|---|---|---|---|
| initial 0.40 (every run's start; f = 0.08) | 0.271 (cf 0.271) | 0.858 (cf 0.858) | 1.918 (cf 1.918; clamp, 1.7 × 10⁻⁷) | 2.708 (cf 2.713; clamp, 2.4 × 10⁻³) | 0.005 (all mass at the top) |
| SD-s1 w16 median cell 0.149 (f = 0.030) | 0.170 | 0.539 | 1.204 | 1.703 (clamp) | 2.781 (clamp) |
| SD-s2 w16 median cell 0.124 (f = 0.025) | 0.156 | 0.493 | 1.102 | 1.558 (clamp) | 3.124 (clamp) |
| SD-s3 w16 median cell 0.181 (f = 0.036) | 0.187 | 0.591 | 1.322 (clamp) | 1.870 (clamp) | 1.938 (clamp) |
| SD-s1 w16 min cell 0.030 | 0.077 | 0.245 | 0.547 | 0.774 | 1.730 (clamp) |
| SD-s1 w16 max cell 1.187 | 0.426 | 1.346 | 2.866 (clamp) | 0.488 (clamp) | 0.000 (clamp) |

Every unclamped cell equals its closed form at the printed precision;
the rule's figure is the maximum absolute difference over the 79
unclamped rows of the 140 read, 2.31 × 10⁻⁸ bins. Three readings:

- **The smear is the operator's, not the training's.** At the initial
  rate a belief that starts as a point is 2.7 bins wide (13.5 points)
  after 100 ticks and has swept into the top bin by 500. Nothing in
  the engine's need law is uncertain over that span.
- **Lower rates smear less, in proportion to √(f (1 − f)).** The
  learned width-16 median cells (0.124–0.181 points per tick, f =
  0.025–0.036) give 1.56–1.87 bins after 100 ticks; the smallest
  cells (Kittybear's play at every width-16 seed, 0.030–0.033 points
  per tick, about a tenth of the 0.30–0.40 empirical play step F-066
  reports) give 0.77–0.81 bins. A rate under the
  empirical step buys the filter a sharper belief and hands the drift
  to the residual, which is the direction F-066's R5c recorded.
- **Large cells overrun.** The largest learned cells (1.05–1.39 points
  per tick, 0.21–0.28 bins per tick) move a belief 21–28 bins in 100
  ticks: the mass piles into the top bin and the sd collapses (0.133
  to 1.021 at n = 100 across the six width-16 and width-32 runs; the
  width-8 maxima of 0.66–0.78 points per tick are still mid-sweep at
  2.52–2.94); by 500 ticks every maximum cell's belief is "≥ 95" with
  no width at all (sd 0.000).

One relief step (a delta at bin 12 under one down-shift by the learned
relief size): the eat relief of 35.0–35.9 points at width 16 (7.0–7.2
bins) adds sd 0.07–0.38 bins depending on its fractional part; the
nine runs' 45 relief cells span 0.00–0.50 bins (the sd of one
Bernoulli step, √(f (1 − f)), at most 0.5).

## R2d(a) — the grave probability, group P (mean ± SD over three seeds)

SD-w16: P(grave by need) = 1 − ∏(1 − grave mass_i), 1c's R4c cells.
NF-h24+p and DR-h24+p: the probe's sigmoid. Above-0.7 gap = the mean
over the bins with lower edge ≥ 0.7 of |seed-mean p − seed-mean
realised fraction|. "hap-only" = grave samples whose five hidden needs
are all under 90 (grave by happiness alone).

### In sight (1,927,130 samples; 2,527 grave, 168 hap-only)

| head | Brier | mean p GRAVE | mean p COMMON | mean p ADJACENT | mean p hap-only GRAVE | above-0.7 gap | AUROC |
|---|---|---|---|---|---|---|---|
| SD-w16 | 0.00064 ± 0.00010 | 0.474 ± 0.115 | 0.0005 ± 0.0002 | 0.183 ± 0.026 | 0.445 ± 0.055 | 0.019 | 0.999 ± 0.001 |
| NF-h24+p | 0.00054 ± 0.00004 | 0.583 ± 0.015 | 0.0003 ± 0.0000 | 0.265 ± 0.002 | 0.676 ± 0.087 | 0.057 | 0.999 ± 0.001 |
| DR-h24+p | 0.00055 ± 0.00010 | 0.577 ± 0.037 | 0.0003 ± 0.0001 | 0.234 ± 0.002 | 0.783 ± 0.022 | 0.022 | 0.999 ± 0.001 |

Reliability in sight, the bins with lower edge ≥ 0.5 (seed-mean p →
seed-mean realised grave fraction; counts per seed in the read):

| bin | SD-w16 | NF-h24+p | DR-h24+p |
|---|---|---|---|
| [0.5, 0.6) | 0.548 → 0.623 | 0.549 → 0.621 | 0.550 → 0.555 |
| [0.6, 0.7) | 0.649 → 0.704 | 0.650 → 0.672 | 0.651 → 0.641 |
| [0.7, 0.8) | 0.748 → 0.795 | 0.751 → 0.751 | 0.750 → 0.749 |
| [0.8, 0.9) | 0.851 → 0.851 | 0.854 → 0.760 | 0.854 → 0.816 |
| [0.9, 1.0) | 0.947 → 0.936 | 0.959 → 0.882 | 0.957 → 0.929 |

Below p = 0.5 all three heads are under-confident (the realised
fraction above the stated p in every bin from 0.1 to 0.5; e.g. the
[0.1, 0.2) bin realises 0.251 for SD, 0.388 for NF-h24+p, 0.247 for
DR-h24+p). Above 0.7 SD is nearest the diagonal on the gap (0.019;
its [0.8, 0.9) and [0.9, 1.0) bins realise 0.851 and 0.936 for 0.851
and 0.947) and NF-h24+p is over-confident in its two top bins;
DR-h24+p sits between (0.022). The probe
puts more of its grave samples in the top bin (NF-h24+p 871 / 537 /
725 grave samples per seed in [0.9, 1.0), the bin's count times its
realised fraction, against SD's 124 / 255 / 669), which is where its
higher grave mean comes from.

### Under fog (2,072,870 samples; 8,977 grave, 1,112 hap-only)

| head | Brier | mean p GRAVE | mean p COMMON | mean p ADJACENT | mean p hap-only GRAVE | above-0.7 gap | AUROC |
|---|---|---|---|---|---|---|---|
| SD-w16 | 0.00185 ± 0.00006 | 0.500 ± 0.046 | 0.0012 ± 0.0005 | 0.282 ± 0.031 | 0.422 ± 0.015 | 0.025 | 0.999 ± 0.000 |
| NF-h24+p | 0.00119 ± 0.00002 | 0.720 ± 0.010 | 0.0005 ± 0.0001 | 0.354 ± 0.032 | 0.760 ± 0.026 | 0.032 | 0.998 ± 0.001 |
| DR-h24+p | 0.00138 ± 0.00018 | 0.685 ± 0.042 | 0.0010 ± 0.0003 | 0.325 ± 0.020 | 0.765 ± 0.066 | 0.024 | 0.999 ± 0.000 |

Under fog the probe's advantage widens: 0.720 against 0.500 on the
grave mean, Brier lower by about a third (0.00119 / 0.00185 = 0.65),
the common mean lower (0.0005 against 0.0012), with the above-0.7 gaps
close (0.032 against 0.025). SD's fog reliability runs above the
diagonal from 0.2 to 0.7 (e.g. [0.5, 0.6) realises 0.739, [0.6, 0.7)
0.779): under fog the histogram's grave mass understates how often the
friend is grave.

### All samples (4,000,000; 11,504 grave, 1,280 hap-only)

| head | Brier | mean p GRAVE | mean p COMMON | mean p ADJACENT | mean p hap-only GRAVE | above-0.7 gap | AUROC |
|---|---|---|---|---|---|---|---|
| SD-w16 | 0.00127 ± 0.00008 | 0.494 ± 0.061 | 0.0008 ± 0.0004 | 0.254 ± 0.029 | 0.425 ± 0.018 | 0.016 | 0.999 ± 0.000 |
| NF-h24+p | 0.00088 ± 0.00002 | 0.690 ± 0.009 | 0.0004 ± 0.0000 | 0.328 ± 0.023 | 0.749 ± 0.033 | 0.036 | 0.998 ± 0.001 |
| DR-h24+p | 0.00098 ± 0.00014 | 0.661 ± 0.040 | 0.0007 ± 0.0002 | 0.299 ± 0.014 | 0.768 ± 0.057 | 0.024 | 0.999 ± 0.000 |

### Happiness-only grave samples

SD's need histograms cannot represent a grave state carried by
happiness alone; the grave probability they report on those samples
(0.445 in sight, 0.422 under fog) comes from mass over 90 on needs
that are in fact below 90,
which is the near-grave neighbourhood those samples sit in. The probe
reads the state that feeds the happiness output and puts 0.676 (NF)
and 0.783 (DR) on them in sight, 0.760 and 0.765 under fog — higher
than on grave samples as a whole for both probes in every version.

### Discrimination

AUROC against the grave label is 0.9981–0.9993 for every head in
every version (SD-w16 0.9985 / 0.9989 / 0.9990 in sight / fog / all;
NF-h24+p 0.9988 / 0.9981 / 0.9983; DR-h24+p 0.9993 / 0.9990 / 0.9992).
The ranking of grave against non-grave samples is near-perfect for all
three; the heads differ in how much probability they commit, which is
what the calibration columns read.

## R2d(b) — runs

| probe | params (hybrid) | best / stop epoch | best val BCE | train GRAVE freq | 1b prediction reproduced to |
|---|---|---|---|---|---|
| NF-h24-s1+p | 25 (7,832) | 73 / 83 | 0.004758 | 0.00300 | 3.9 × 10⁻⁷ |
| NF-h24-s2+p | 25 (7,832) | 89 / 99 | 0.004859 | 0.00300 | 4.5 × 10⁻⁷ |
| NF-h24-s3+p | 25 (7,832) | 81 / 91 | 0.005906 | 0.00300 | 3.7 × 10⁻⁷ |
| DR-h24-s1+p | 25 (7,832) | 64 / 74 | 0.005101 | 0.00300 | 3.0 × 10⁻⁷ |
| DR-h24-s2+p | 25 (7,832) | 100 / 110 | 0.004969 | 0.00300 | 2.4 × 10⁻⁷ |
| DR-h24-s3+p | 25 (7,832) | 102 / 112 | 0.006016 | 0.00300 | 3.6 × 10⁻⁷ |

Every fit stopped on the relative plateau rule (ten epochs without a
0.1% gain), none at the 200-epoch cap; the state extraction took 9 s
per run and the whole fit with its 69 evaluation-world predictions 60
to 79 s of wall clock, the six in parallel at three threads each. The
base heads' `head-best.pt` hashes are unchanged after the fits
(`done.json` `base_sha256_after`). The hybrid's 7,832 parameters are
under the 8,445 cap.

## Limitations

- **The rule's spread is SD's.** s = 0.116 is almost entirely SD's
  between-seed spread on the grave mean (0.115 against the probe's
  0.015). "Within the spread" is therefore a weak statement about a
  comparison whose direction holds in every version and on Brier
  (one SD seed, 0.601, sits above the probe's mean of 0.583). The rule was declared
  and is applied as declared; the stronger reading is reported, not
  ruled on.
- **The probe is calibrated on the training distribution and read on
  the evaluation worlds.** Its under-confidence below p = 0.5 and
  over-confidence in the top two bins in sight are read on group P;
  no temperature or recalibration was fitted (none was declared).
- **Nothing was tuned.** One learning rate, one batch size, one
  stopping rule, no weight decay; the states were trained for a
  squared-error mean, not for this read. A probe fitted jointly with
  its GRU could differ in either direction; that is the Phase 2 head,
  not this read.
- **The quantities compared are not the same object.** SD's P(grave)
  is derived from five need histograms under an independence
  assumption and cannot carry the happiness-only edge; the probe's is
  one direct output trained on the stratum label. The declaration
  chose this comparison because the consumer would read one number
  either way.
- **R1d is arithmetic on the operator, not an ablation of the
  training.** It confirms that the drift smears as √n and by how much
  at the learned rates; it does not by itself show that the smear is
  what made the residual carry half the fit (F-066 R6c). That
  attribution would need a non-diffusing filter trained under the
  same rule, which outcome A does not call for.
- **Discrimination saturates.** With AUROC above 0.998 for every head,
  this read cannot separate the heads on ranking; what it separates
  is how much probability each commits, which a consumer reading the
  number sees and a consumer ranking by it would not (a shared fixed
  threshold would still land at different operating points, since the
  calibrations differ).
- **Group P, offline, no consumer.** Nothing here is a welfare claim
  or a Phase 2 result; the Phase 2 head choice is the owner's.

## Not read

Any MSE or bias cell (unchanged by construction); group G; the Phase
2 consumer; any joint fit; P1 (no longer-cap SD run exists).

## Regeneration

Phase 1's arc venv (`A=experiments/minifriend-phase1-2026-10-22`,
`Dd=experiments/minifriend-phase1d-2026-10-24`, run from the
repository root; `VIRTUAL_ENV=$PWD/$A/.venv` on every line;
`MINIFRIEND_ARC=$PWD/$Dd` points Phase 1's modules at this arc's
`split.json` and `results-raw/`). Raws: `$Dd/results-raw/probe/
{NF,DR}-h24-s{1,2,3}+p/` (the six probe runs read here: `pgrave-*.npz`,
`run-manifest.json`, `done.json`, `metrics.jsonl`, `probe.pt`);
`$Dd/results-raw/{L,W,G}` → symlinks to Phase 1's raws; `$Dd/results-raw/
P{1..5}` → symlinks to 1b's; `$Dd/results-raw/heads/{NF,DR}-h24-s{1,2,3}`
→ symlinks to 1b's runs (the base heads); `$Dd/results-raw/heads/
SD-s{1,2,3}` (and `SD-h8-*`, `SD-h32-*`) → symlinks to 1c's runs (R1d
reads their `head-best.pt`; R2d reads SD-s*'s `belief-*.npz`).

### Collect

```sh
# no rollout; the symlinks, then the six probe fits (about 80 s each, six in parallel)
(cd $Dd && for s in L W G; do ln -s ../../minifriend-phase1-2026-10-22/results-raw/$s results-raw/$s; done; for k in 1 2 3 4 5; do ln -s ../../minifriend-phase1b-2026-10-23/results-raw/P$k results-raw/P$k; done; for h in NF DR; do for s in 1 2 3; do ln -s ../../../minifriend-phase1b-2026-10-23/results-raw/heads/$h-h24-s$s results-raw/heads/$h-h24-s$s; done; done; for r in SD-s1 SD-s2 SD-s3 SD-h8-s1 SD-h8-s2 SD-h8-s3 SD-h32-s1 SD-h32-s2 SD-h32-s3; do ln -s ../../../minifriend-phase1c-2026-10-23/results-raw/heads/$r results-raw/heads/$r; done)
(cd $Dd && mkdir -p results-raw/probe && caffeinate -s ./run_probe.sh > results-raw/probe/run.log 2>&1)
```

### Read

```sh
MINIFRIEND_ARC=$PWD/$Dd VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/python3 -B $Dd/read_phase1d.py --out $Dd/phase1d-read.json --md > $Dd/phase1d-read.md   # ≈ 10 s (stdout is the markdown; the 'wrote' line goes to stderr); R1d runs inside it (filter_spread.read_all)
```

Guards (plain-assert runner, Phase 1's venv): `$Dd/test_phase1d.py` 4
(t1–t4; about 6 s). Reds on record via `scripts/mutate.sh` in the
declaration's §Instrument.

Accuracy gate: **PASS**, 2026-10-24, round 4 (fresh subagent per
round; every round regenerated the read byte-identically, matched the
sample counts and the 4-guard count; no round found a number wrong
beyond one range and one rounding). Round 1 FAILED on an AUROC range
whose stated lower bound excluded two of its own values, a WEAK claim
inside the decision section ("SD's one better cell" when the read
shows three) and a Professor quotation with an unmarked cut; round 2
FAILED on one WEAK clause in the decision section ("none of the three
enters the rule" when the gap is a condition of B and C) plus a
rounding (9.4 for 9.35) and two weak wordings; round 3 FAILED on one
WEAK clause in the decision section (Δ < 0 said to rule out C, whose
second branch needs |Δ| ≤ s) plus four weak wordings; round 4 PASS:
about 180 reader-backed cells, about 110 prose numbers and about 40
derived figures matched, about 20 provenance and threshold items
located, 44 characterisations supported, one undecidable (the
"near-grave neighbourhood" of the happiness-only samples, which round
3 had measured read-only at a median largest need of 87.2 in sight),
no rounding. After the verdict, without a number changing: "as low"
→ "lower" on the common mean. Raw-dir hashes (`scripts/rawdir-hash.sh`
refuses symlinks, so the bundle is stamped per probe directory; the
base heads, SD runs and world raws are symlinks to 1b's, 1c's and
Phase 1's bundles, stamped in their RESULTS): NF-h24-s1+p
`v1:6b4fa4e97b7eee07`, NF-h24-s2+p `v1:98b24abc49bbaeba`, NF-h24-s3+p
`v1:1369d056ccb744ca`, DR-h24-s1+p `v1:7b83ae4fae0c997d`, DR-h24-s2+p
`v1:9c85cdc2f6d1ddff`, DR-h24-s3+p `v1:43946a66feced14c` (each
`scripts/rawdir-hash.sh
experiments/minifriend-phase1d-2026-10-24/results-raw/probe/<run>`).
