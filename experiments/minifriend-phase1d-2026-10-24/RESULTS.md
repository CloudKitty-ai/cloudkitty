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

## Addendum — which need, and how soon (owner 2026-10-24 "Agreed, let's proceed. First the breakdown by need and latency read")

Two reads on the same outputs (DECLARATION §Addendum and its post-read
addition; 0 new cat-ticks). Group P, seeds 1–3, mean ± SD. The
committed R1d / R2d blocks are pinned unchanged by the reader.

### Headline

**The base head names the grave need, and the probe's probability is
over 0.2 before a mid-world grave episode begins in most cases; a
consumer reading the means against 90 misses half or more of what
starts in front of it.** In sight,
NF-h24's five means name a grave need on 0.871 ± 0.031 of the
need-grave samples (top-2 0.969; the always-name-drink baseline
0.353), DR-h24's on 0.872 ± 0.010; SD's grave mass on 0.739 ± 0.043 and
SD's mean on 0.687 ± 0.031. Under fog NF-h24 holds at 0.867 and DR-h24
at 0.885. The 288 grave episodes over observer slices (72
friend-episodes × 4 observers) split by how they begin: 200 are RESET
episodes (the friend is grave at the world's first tick, which is
group P's per-cat grave-start design; a crossing there is the head's
prior, not a detection), 20 begin mid-world with the friend in the
observer's sight and 68 mid-world under fog. On the 68 mid-world
fog-onset episodes NF-h24+p at P(grave) ≥ 0.2 detects 0.946 ± 0.042 at
a median latency of 0 ticks and is already over the threshold at the
tick before onset as well in 0.931 of them; on the 20 mid-world in-sight
episodes 0.850 ± 0.087, median latency 0, anticipated in 0.833. Across
all onsets (the declared rule's domain) it detects 0.912 ± 0.051 of the
34 in-sight-onset and 0.966 ± 0.016 of the 254 fog-onset episodes.
False-alarm runs are 0.90 ± 0.30 per 10,000 observer-ticks in all,
0.07 ± 0.02 once the runs that start at the world's first tick are set
aside (the world-start transient of a state initialised at zero). The
mean-reading rule (max of the five means ≥ 90) on the same head
detects 0.367 ± 0.058 of the mid-world in-sight episodes and 0.490 ±
0.090 of the mid-world fog ones (0.490 ± 0.045 and 0.686 ± 0.065 over
all onsets, 3 ticks late at the median); on SD's means 0.294 and 0.177
over all onsets, 11 and 34 ticks late. Both declared reading rules
hold as declared (which-need 0.871 with the weakest need, play, at
0.783; in-sight-onset detection 0.912 at median latency 0) and the
registered prediction that the mean rule detects under half of the
in-sight-onset episodes holds on the seed mean (0.490), so the verdict
as declared is "enough for detection and naming, on this evidence";
beside it, disclosed, rule (ii)'s detection on the 20 mid-world
in-sight episodes alone is 0.850 (15 / 18 / 18 per seed), under the
0.90 bar, and the mean rule's per-seed in-sight-onset detections are
17 / 15 / 18 of 34, one seed exactly at half.

### R3d — which need


Domain: samples in stratum GRAVE with some hidden need ≥ 90 (the
happiness-only grave samples are excluded). Named need = argmax of the
head's five per-need scores; correct when it is one of the sample's
grave needs. In sight 2,359 such samples per seed, of which 1,021 have
two or more grave needs; under fog 7,865 (2,559); all 10,224 (3,580).
Per-need accuracy is over the samples where THAT need is grave and
counts any grave need named; the confusion shows which need was
named. Baseline: always name drink, the most frequent grave need on
the training worlds' truth streams (drink 2,305 grave kitty-ticks,
cuddle 1,938, eat 1,261, sleep 1,256, play 1,100).

| in sight | accuracy | top-2 | eat (716) | drink (832) | sleep (500) | play (753) | cuddle (807) |
|---|---|---|---|---|---|---|---|
| SD-w16 grave mass | 0.739 ± 0.043 | 0.876 ± 0.037 | 0.732 | 0.900 | 0.815 | 0.799 | 0.744 |
| SD-w16 mean | 0.687 ± 0.031 | 0.865 ± 0.011 | 0.666 | 0.880 | 0.829 | 0.726 | 0.717 |
| NF-h24 mean | 0.871 ± 0.031 | 0.969 ± 0.007 | 0.986 | 0.898 | 0.913 | 0.783 | 0.873 |
| DR-h24 mean | 0.872 ± 0.010 | 0.959 ± 0.010 | 0.946 | 0.927 | 0.867 | 0.878 | 0.850 |
| baseline (drink) | 0.353 | | | | | | |

| under fog | accuracy | top-2 | eat (1,204) | drink (1,976) | sleep (1,612) | play (2,375) | cuddle (3,993) |
|---|---|---|---|---|---|---|---|
| SD-w16 grave mass | 0.665 ± 0.029 | 0.859 ± 0.005 | 0.588 | 0.745 | 0.740 | 0.600 | 0.757 |
| SD-w16 mean | 0.582 ± 0.024 | 0.785 ± 0.049 | 0.499 | 0.862 | 0.831 | 0.453 | 0.629 |
| NF-h24 mean | 0.867 ± 0.006 | 0.953 ± 0.004 | 0.914 | 0.877 | 0.866 | 0.783 | 0.938 |
| DR-h24 mean | 0.885 ± 0.004 | 0.952 ± 0.006 | 0.860 | 0.835 | 0.891 | 0.867 | 0.959 |
| baseline (drink) | 0.251 | | | | | | |

All samples: NF-h24 mean 0.868 ± 0.012 (top-2 0.957), DR-h24 mean
0.882 ± 0.005, SD grave mass 0.682 ± 0.030, SD mean 0.606 ± 0.017,
baseline 0.275. Play is the weakest need for NF-h24 in every version
(0.783, with the largest seed spread, ± 0.119 in sight); its
confusion row in sight (counts summed over seeds, 2,259 play-grave
samples) names sleep 511, drink 474 and eat 354 times against play
661 and cuddle 259, so a grave play need is mostly named as some
other need, which is a grave need too in the multi-grave samples and
a miss otherwise. Eat is the strongest (0.986 in sight: 1,756 of 2,148
named eat, 321 sleep). Every per-need cell has n ≥ 500 per seed, so
none fails closed.

### R4d — latency

Episodes: maximal runs of stratum GRAVE on the truth stream per
(world, friend), one per observer: 288 over the observer slices, 72
distinct friend-episodes each seen by four observers. Onset class:
RESET = the episode begins at the world's first tick (200 of 288; 50 of
the 72 friend-episodes, one per world: group P's per-cat grave starts);
mid-world in sight (20); mid-world under fog (68). The declared splits
"onset in sight" (34 = 14 reset + 20 mid-world) and "onset under fog"
(254 = 186 reset + 68 mid-world) are kept beside them. Episode length:
median 30 ticks overall, 90th percentile 80 (reset 40 / 87, mid-world
in sight 12 / 23, mid-world fog 20 / 70). Latency = first tick at or
over the threshold within the episode minus the onset tick (0 = at
onset; median and 90th percentile among detected episodes);
"anticipated" = over the threshold at onset and at the tick before
it, within the same observer slice (a reset episode has no such
tick); detected fraction over all episodes of the split; false alarms = runs over threshold containing
no grave tick, per 10,000 observer-ticks (4,000,000 in the group),
reported for all runs and excluding runs that begin at the world's
first tick.

| mid-world, onset in sight (20) | detected | median / p90 latency | within 10 | anticipated |
|---|---|---|---|---|
| SD-w16 P ≥ 0.2 | 0.867 ± 0.029 | 0.0 / 0.8 | 0.850 | 0.817 |
| SD-w16 P ≥ 0.5 | 0.700 ± 0.087 | 0.0 / 0.0 | 0.700 | 0.650 |
| NF-h24+p ≥ 0.2 | 0.850 ± 0.087 | 0.0 / 0.0 | 0.850 | 0.833 |
| NF-h24+p ≥ 0.5 | 0.650 ± 0.050 | 0.0 / 3.3 | 0.650 | 0.450 |
| DR-h24+p ≥ 0.2 | 0.683 ± 0.076 | 0.0 / 0.9 | 0.683 | 0.600 |
| DR-h24+p ≥ 0.5 | 0.500 ± 0.000 | 0.0 / 0.3 | 0.500 | 0.450 |
| SD-w16 mean ≥ 90 | 0.333 ± 0.252 | 1.8 / 6.8 | 0.300 | 0.183 |
| NF-h24 mean ≥ 90 | 0.367 ± 0.058 | 0.0 / 4.3 | 0.350 | 0.250 |
| DR-h24 mean ≥ 90 | 0.300 ± 0.050 | 0.0 / 3.9 | 0.283 | 0.250 |

| mid-world, onset under fog (68) | detected | median / p90 latency | within 10 | anticipated |
|---|---|---|---|---|
| SD-w16 P ≥ 0.2 | 0.961 ± 0.017 | 0.0 / 0.0 | 0.956 | 0.956 |
| SD-w16 P ≥ 0.5 | 0.765 ± 0.106 | 0.0 / 13.4 | 0.686 | 0.520 |
| NF-h24+p ≥ 0.2 | 0.946 ± 0.042 | 0.0 / 0.0 | 0.946 | 0.931 |
| NF-h24+p ≥ 0.5 | 0.877 ± 0.022 | 0.0 / 0.0 | 0.877 | 0.824 |
| DR-h24+p ≥ 0.2 | 0.926 ± 0.053 | 0.0 / 0.1 | 0.926 | 0.882 |
| DR-h24+p ≥ 0.5 | 0.745 ± 0.034 | 0.0 / 6.8 | 0.711 | 0.652 |
| SD-w16 mean ≥ 90 | 0.147 ± 0.039 | 20.7 / 31.0 | 0.059 | 0.015 |
| NF-h24 mean ≥ 90 | 0.490 ± 0.090 | 0.0 / 3.8 | 0.466 | 0.377 |
| DR-h24 mean ≥ 90 | 0.554 ± 0.081 | 0.0 / 8.5 | 0.510 | 0.348 |

| reset (200; the first crossing after the world starts) | detected | median / p90 latency | within 10 |
|---|---|---|---|
| SD-w16 P ≥ 0.2 | 1.000 ± 0.000 | 0.0 / 0.0 | 1.000 |
| SD-w16 P ≥ 0.5 | 0.722 ± 0.048 | 11.0 / 29.3 | 0.320 |
| NF-h24+p ≥ 0.2 | 0.975 ± 0.009 | 1.0 / 1.3 | 0.968 |
| NF-h24+p ≥ 0.5 | 0.965 ± 0.013 | 1.0 / 2.7 | 0.948 |
| DR-h24+p ≥ 0.2 | 0.997 ± 0.006 | 0.0 / 0.0 | 0.997 |
| DR-h24+p ≥ 0.5 | 0.982 ± 0.006 | 1.0 / 3.3 | 0.968 |
| SD-w16 mean ≥ 90 | 0.192 ± 0.028 | 36.3 / 69.2 | 0.017 |
| NF-h24 mean ≥ 90 | 0.752 ± 0.066 | 4.0 / 21.9 | 0.627 |
| DR-h24 mean ≥ 90 | 0.788 ± 0.094 | 5.3 / 19.0 | 0.563 |

| all onsets, the declared splits | in sight (34) detected / median lat | under fog (254) detected / median lat | all (288) detected / median lat | FA / 10k all runs (median len) | FA / 10k excluding world-start runs (median len) |
|---|---|---|---|---|---|
| SD-w16 P ≥ 0.2 | 0.922 ± 0.017 / 0.0 | 0.990 ± 0.005 / 0.0 | 0.981 ± 0.005 / 0.0 | 2.20 ± 0.14 (2.7) | 0.20 ± 0.14 (9.0) |
| SD-w16 P ≥ 0.5 | 0.676 ± 0.059 / 0.0 | 0.738 ± 0.067 / 9.5 | 0.730 ± 0.063 / 8.3 | 0.10 ± 0.03 (6.5) | 0.09 ± 0.03 (7.2) |
| NF-h24+p ≥ 0.2 | 0.912 ± 0.051 / 0.0 | 0.966 ± 0.016 / 0.7 | 0.959 ± 0.010 / 0.7 | 0.90 ± 0.30 (1.3) | 0.07 ± 0.02 (5.5) |
| NF-h24+p ≥ 0.5 | 0.794 ± 0.029 / 0.0 | 0.940 ± 0.012 / 1.0 | 0.922 ± 0.012 / 1.0 | 0.20 ± 0.21 (1.3) | 0.06 ± 0.01 (3.2) |
| DR-h24+p ≥ 0.2 | 0.814 ± 0.045 / 0.0 | 0.978 ± 0.014 / 0.0 | 0.958 ± 0.015 / 0.0 | 2.06 ± 0.17 (1.3) | 0.16 ± 0.08 (2.3) |
| DR-h24+p ≥ 0.5 | 0.706 ± 0.000 / 0.0 | 0.917 ± 0.014 / 1.0 | 0.892 ± 0.012 / 1.0 | 0.21 ± 0.13 (1.3) | 0.08 ± 0.03 (4.7) |
| SD-w16 mean ≥ 90 | 0.294 ± 0.135 / 11.3 | 0.177 ± 0.031 / 34.0 | 0.191 ± 0.044 / 30.7 | 0.02 ± 0.01 (3.7) | 0.02 ± 0.01 (3.7) |
| NF-h24 mean ≥ 90 | 0.490 ± 0.045 / 3.0 | 0.686 ± 0.065 / 3.0 | 0.663 ± 0.060 / 3.0 | 0.06 ± 0.00 (3.0) | 0.06 ± 0.00 (3.0) |
| DR-h24 mean ≥ 90 | 0.490 ± 0.034 / 3.7 | 0.727 ± 0.091 / 4.3 | 0.699 ± 0.079 / 4.3 | 0.09 ± 0.01 (3.3) | 0.09 ± 0.01 (3.3) |

Four readings:

- **On a mid-world onset the probability is already up.** On the 68
  mid-world fog-onset episodes every probability head at 0.2 detects
  over nine in ten (SD-w16 0.961, NF-h24+p 0.946, DR-h24+p 0.926) with
  a median latency of 0, and in 0.88–0.96 of them the probability was
  over 0.2 at the tick before the onset: the belief rises with the
  friend's state and crosses before the stratum does. On the 20
  mid-world in-sight episodes NF-h24+p detects 0.850 ± 0.087 (15 / 18 /
  18) and SD-w16 0.867; DR-h24+p 0.683.
- **Reset episodes are the prior, and the probes recover from it in
  a tick.** On the 200 reset episodes SD-w16's P(grave) is over 0.2 at
  the first tick for every friend, grave or not (its prior); NF-h24+p
  and DR-h24+p cross at a median of 1 and 0 ticks and the world-start
  transient is where almost all of their false-alarm runs are: the
  rate falls from 0.90 to 0.07 (NF-h24+p) and from 2.06 to 0.16
  (DR-h24+p) per 10,000 observer-ticks once runs that begin at the
  world's first tick are set aside, and the remaining runs are longer
  (median 5.5 and 2.3 ticks).
- **A mean-reading consumer misses half or more of what starts in
  front of it.** The ≥ 90 rule on NF-h24's means detects 0.367 of the
  mid-world in-sight episodes and 0.490 of the mid-world fog ones
  (0.490 and 0.686 over all onsets, 3 ticks late at the median and
  15–18 at the 90th percentile); on SD's means 0.333 and 0.147
  mid-world (0.294 and 0.177 over all onsets, 11 and 34 ticks late).
  This is F-066's −15.01 pooled grave bias on SD and F-065's −10.10 on
  NF as a missed-detection rate: the ostrich in the consumer's terms.
- **Raising the threshold to 0.5 costs mid-world detection and
  costs SD its reset recovery.** On the mid-world episodes NF-h24+p
  loses 0.20 (in sight) and 0.07 (fog) of detection, SD-w16 0.17 and
  0.20, DR-h24+p 0.18 and 0.18; on the reset episodes SD-w16's median
  latency at 0.5 is 11 ticks against NF-h24+p's 1: SD's grave
  probability climbs slowly from its prior (§R2d(a): its reliability
  bins below 0.7 realise more grave than they state), which is what
  the 0 → 9.5 median in the declared fog-onset split reads.

### Reading rules and predictions, applied (declared in §Addendum; not gates)

(i) NF-h24 mean which-need in sight: 0.871 ≥ 0.80, every per-need cell
(all n ≥ 500) above 0.60 (minimum play 0.783) → holds; the registered
prediction "(i) holds" is met. (ii) NF-h24+p ≥ 0.2, onset in sight (34
episodes as declared, reset included): detected 0.912 ≥ 0.90 (per seed
0.853 / 0.941 / 0.941 = 29 / 32 / 32), median latency 0.0 ≤ 10 →
holds; the registered prediction "(ii) holds at 0.2" is met. Disclosed
beside it, not a rule: on the 20 mid-world in-sight episodes alone
detection is 0.850 (0.750 / 0.900 / 0.900 = 15 / 18 / 18), under the
bar. Registered prediction (the mean ≥ 90 rule detects under half of
the same episodes): 0.490 on the seed mean → holds; per seed 0.500 /
0.441 / 0.529 (17 / 15 / 18 of 34), one seed exactly at half and one
over. Verdict as declared: "enough for detection and naming, on this
evidence".

### Limitations of the addendum

- **Reset episodes are over two thirds of the sample.** Group P starts
  every world with one grave friend, so 200 of 288 observer-episodes
  begin at tick 0 and the declared splits count a head's prior as a
  detection there. The reset / mid-world split was added after gate
  round 1 (DECLARATION, post-read addition); the declared rules are
  scored as declared and the mid-world numbers stand beside them.
- **Twenty and sixty-eight episodes.** The mid-world in-sight split
  rests on 20 observer-episodes (one is 0.05 of the detected
  fraction) and the mid-world fog split on 68 (0.015). Rule (ii) as
  declared clears its bar by less than one of its 34 episodes.
- **The which-need read is the base head's means, not the probe's.**
  The probe emits one number. A hybrid that names a need does so from
  the five means it already carries; a per-need probability output is
  a design choice for the Phase 2 declaration, not read here.
- **Multi-grave samples inflate per-need accuracy.** 43% of the
  in-sight need-grave samples have two or more grave needs, and
  naming any one counts; the confusion rows quoted above show the
  named need and the pooled accuracy counts a sample once.
- **Episodes are the truth stream's, not the consumer's.** An
  observer under fog cannot act on a friend it cannot see; the
  fog-onset detection says the belief knows, not that the cat can
  reach. The false-alarm rate counts runs per tick; at the 0.2 rows
  most runs are one to three ticks (NF-h24+p's median 1.3), at SD's
  0.5 rows they are longer (median 6.5); what a run costs depends on
  the consumer.
- **One group, offline, three seeds.** As §Limitations above.

## Addendum 2 — the operating-point sweep (owner 2026-10-24 "Let's run the read and see what we find")

One read on the same six probe runs (DECLARATION §Addendum 2 and its
two post-read additions; 0 new cat-ticks; no weight touched): R4d's
latency instrument at eight thresholds, on group P and on the held-out
evaluation worlds of Phase 1's L, W and G, with two post-read
additions (four columns: non-grave ticks at or over the threshold;
where the false-alarm runs start). Seeds 1–3, mean ± SD. NF-h24+p's 0.20 and
0.50 rows on group P are asserted equal to the committed R4d rows by
the reader before it writes. Descriptive: no reading rule was declared and none is applied;
the pick is hers.

### Headline

**Between 0.05 and 0.50 the threshold costs NF-h24+p detections all
the way up, and from 0.10 up nine in ten or more of the false-alarm
runs it counts start inside a slice's first 100 ticks: the world-start
transient of a zero-initialised state is about a hundred ticks long,
not the one tick R4d set aside.** On group P, NF-h24+p's mid-world in-sight detection
falls from 0.950 ± 0.050 at 0.05 to 0.850 ± 0.087 at 0.20 and 0.650 ±
0.050 at 0.50 (20 episodes), its mid-world fog detection from 0.971 ±
0.039 to 0.946 ± 0.042 to 0.877 ± 0.022 (68). Its mid-world
false-alarm runs (R4d's definition: at or over the threshold, no grave
tick, not starting at the slice's first tick) stay between 0.059 and 0.092
per 10,000 observer-ticks over the whole ladder (0.092 ± 0.028 at
0.05, 0.073 ± 0.021 at 0.20, 0.064 ± 0.008 at 0.50), but 0.718 ± 0.204
of them at 0.05, 0.958 ± 0.072 at 0.20 and 1.000 at 0.50 start within
the slice's first 100 ticks; the runs starting after tick 100 are
0.027 ± 0.025, 0.003 ± 0.006 and 0.000 per 10,000 observer-ticks. On
the L / W / G evaluation worlds the detections fall the same way
(mid-world in-sight 0.985 ± 0.026 → 0.833 ± 0.052 → 0.606 ± 0.139 on
22 episodes; fog 0.983 ± 0.020 → 0.915 ± 0.027 → 0.701 ± 0.053 on 78),
the mid-world run rate is higher (0.274 ± 0.084 at 0.05, 0.281 ± 0.088
at 0.20, 0.407 ± 0.022 at 0.50), 0.847 ± 0.067 / 0.980 ± 0.034 / 0.994
± 0.010 of those runs start within the first 100 ticks, and the runs
starting after tick 100 are 0.038 ± 0.005 / 0.007 ± 0.012 / 0.002 ±
0.004 per 10,000. The L / W / G rate's rise from 0.25 up is
world-start runs whose first tick falls under the threshold, so they
begin at offset 1 and escape R4d's first-tick exclusion: runs starting
at tick 1 number 0.0 per seed at 0.05–0.10, 0.3 at 0.15, 6.0 at 0.20,
20.0 at 0.25 and 44.3 at 0.50 (W's worlds). Over-threshold ticks are a
subset of those over a lower threshold, and the non-grave tick column
falls monotonically on both sets (L / W / G 27.94 → 17.28 → 9.24 per
10,000; P 13.23 → 7.98 → 4.47). The all-runs false-alarm rate, which
includes the runs starting at the first tick, falls steeply (P 2.089 ±
0.032 → 0.898 ± 0.305 → 0.198 ± 0.208). Reset episodes are detected at
every threshold (P 0.965–1.000) at a median latency of 0–1 ticks.
DR-h24+p on group P is behind NF-h24+p in mid-world in-sight detection
and in mid-world false-alarm runs at every threshold (0.683 ± 0.076
and 0.159 ± 0.076 at 0.20, the runs 2.2 × NF's; its run rate does fall
with the threshold, 0.392 ± 0.265 → 0.082 ± 0.030), level with NF in
fog detection at 0.05–0.10 and behind from 0.15 up; on L / W / G it is
within 0.05 of NF in in-sight detection at every threshold, behind in
fog detection from 0.15 up (by 0.013 and 0.009 at 0.15 and 0.20, by
0.030–0.038 at 0.25–0.40, and 0.577 ± 0.068 against 0.701 ± 0.053 at
0.50) and higher in false-alarm runs at every threshold (0.401 ± 0.076
against 0.281 ± 0.088 at 0.20). For NF-h24+p no threshold on the
ladder improves detection: on both sets the lowest threshold has the
highest detection in every split. What the low end pays, column by
column: the all-runs rate, whose extra at the low end is the
first-tick runs (P 2.089 against 0.198 at 0.50; L / W / G 0.850 against
0.477); the mid-world
run rate on P (0.092 ± 0.028 against 0.064 ± 0.008, within one seed SD
of the 0.05 row; on L / W / G 0.274 is below 0.407); the runs per 100
detected on P (42.9 against 35.3; on L / W / G 78.3 against 168.2) —
these two columns have a shallow minimum at 0.15 on both sets (P 0.059
and 29.0 ± 8.9; L / W / G 0.256 and 77.3 ± 27.8), within the 0.15
cell's own seed SD; the median run length on L / W / G (6.5 against
4.7 ticks; on P 3.8 against 3.2, inside the seed SD); and the runs starting after tick 100 (0.027
against 0.000 per 10,000 on P, 4 / 6 / 22 runs per seed at 0.05 against
0 / 0 / 0 at 0.50; 0.038 against 0.002 on L / W / G, 9 / 11 / 12
against 0 / 2 / 0).

### Expectations stated before the read, scored

Three were stated (DECLARATION §Addendum 2), none a prediction to
score for a rule. (1) Mid-world detection non-increasing in the
threshold: held on every head × set × split (for NF-h24+p on P,
in-sight 0.950 / 0.900 / 0.867 / 0.850 / 0.817 / 0.767 / 0.717 / 0.650;
fog 0.971 / 0.956 / 0.951 / 0.946 / 0.946 / 0.936 / 0.897 / 0.877). (2)
Mid-world false-alarm runs non-increasing: did NOT hold — on group P
the NF-h24+p rate goes 0.092 / 0.072 / 0.059 / 0.073 / 0.074 / 0.068 /
0.068 / 0.064, up from 0.15 to 0.20 within the seed SD (0.017 and
0.021), and on L / W / G it goes 0.274 / 0.277 / 0.256 / 0.281 / 0.298 /
0.338 / 0.355 / 0.407, flat within the seed SD to 0.25 and rising
after, the rise being the tick-1 runs above; the two post-read additions
(a tick count, monotone by construction; the run-start detail) were
made for it. (3) The declaration's "between 0.15 and 0.30 the
mid-world false-alarm rate moving by less than the seed spread of the
mid-world in-sight detected fraction" compared a rate per 10,000 ticks
with a fraction's SD and is malformed as written; the rate moves by
0.009 per 10,000 on group P (0.059 → 0.068) and by 0.082 on L / W / G
(0.256 → 0.338) between those two rows, reported without a bar.

### R5d — the tables (`phase1d-sweep.md`, verbatim)

Columns: `mw-sight det` / `mw-fog det` the detected fraction of the
mid-world in-sight / mid-world fog episodes; `antic` the fraction over
the threshold at onset and at the tick before, within the slice; `p90
lat` the 90th-percentile latency among detected (ticks); `reset det` /
`reset med lat` the reset episodes' detected fraction and median
latency; `mw FA /10k` runs at or over the threshold containing no grave tick
and not starting at the slice's first tick, per 10,000 observer-ticks,
`mw FA len` their median length; `all FA /10k` the same count with the
first-tick runs included; `mw FA per 100 det` mid-world false-alarm
runs per 100 detected mid-world episodes (a ratio of counts per seed,
then averaged); `non-grave ticks ≥ t /10k` non-grave ticks at or over
the threshold per 10,000 observer-ticks (a tick count, not a
false-alarm rate: it counts the ticks before, during the settling and
after episodes alike); `mw FA start ≤ 100` the fraction of the
mid-world false-alarm runs starting within the slice's first 100 ticks
(offset ≤ 100); `mw FA at tick 1` the number of them per seed starting
at offset 1; `late FA /10k (start > 100)` the runs starting after tick
100 per 10,000 observer-ticks. The last three are post-read columns
(DECLARATION §Addendum 2, second post-read addition); 100 is a
reporting constant chosen after gate round 1 showed the start-offset
distribution, not a declared burn-in.

#### P (P1, P2, P3, P4, P5; 4,000,000 observer-ticks) — NF-h24+p
episodes 288 (72 friend-episodes): reset 200, mid-world in sight 20, mid-world under fog 68
per set: P1 reset 40 / mid-world 8; P2 reset 40 / mid-world 16; P3 reset 40 / mid-world 28; P4 reset 40 / mid-world 20; P5 reset 40 / mid-world 16

| P ≥ | mw-sight det | antic | p90 lat | mw-fog det | antic | p90 lat | reset det | reset med lat | mw FA /10k | mw FA len | all FA /10k | mw FA per 100 det | non-grave ticks ≥ t /10k | mw FA start ≤ 100 | mw FA at tick 1 | late FA /10k (start > 100) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.05 | 0.950 ± 0.050 | 0.900 ± 0.050 | 0.0 ± 0.0 | 0.971 ± 0.039 | 0.961 ± 0.045 | 0.0 ± 0.0 | 1.000 ± 0.000 | 0.0 ± 0.0 | 0.092 ± 0.028 | 3.8 ± 1.8 | 2.089 ± 0.032 | 42.9 ± 11.8 | 13.23 ± 0.96 | 0.718 ± 0.204 | 0.0 ± 0.0 | 0.027 ± 0.025 |
| 0.10 | 0.900 ± 0.050 | 0.883 ± 0.029 | 0.0 ± 0.0 | 0.956 ± 0.053 | 0.951 ± 0.047 | 0.0 ± 0.0 | 0.995 ± 0.009 | 0.3 ± 0.6 | 0.072 ± 0.003 | 4.2 ± 0.8 | 1.607 ± 0.805 | 35.0 ± 2.5 | 10.51 ± 0.21 | 0.905 ± 0.135 | 0.0 ± 0.0 | 0.007 ± 0.009 |
| 0.15 | 0.867 ± 0.058 | 0.867 ± 0.058 | 0.0 ± 0.0 | 0.951 ± 0.047 | 0.936 ± 0.034 | 0.0 ± 0.0 | 0.987 ± 0.015 | 0.3 ± 0.6 | 0.059 ± 0.017 | 5.3 ± 2.3 | 1.469 ± 0.787 | 29.0 ± 8.9 | 9.29 ± 0.17 | 0.933 ± 0.063 | 0.0 ± 0.0 | 0.003 ± 0.003 |
| 0.20 | 0.850 ± 0.087 | 0.833 ± 0.076 | 0.0 ± 0.0 | 0.946 ± 0.042 | 0.931 ± 0.031 | 0.0 ± 0.0 | 0.975 ± 0.009 | 1.0 ± 0.0 | 0.073 ± 0.021 | 5.5 ± 2.5 | 0.898 ± 0.305 | 36.3 ± 11.0 | 7.98 ± 0.59 | 0.958 ± 0.072 | 0.0 ± 0.0 | 0.003 ± 0.006 |
| 0.25 | 0.817 ± 0.058 | 0.767 ± 0.029 | 0.3 ± 0.5 | 0.946 ± 0.042 | 0.926 ± 0.029 | 0.0 ± 0.0 | 0.972 ± 0.003 | 1.0 ± 0.0 | 0.074 ± 0.018 | 4.5 ± 1.8 | 0.557 ± 0.119 | 36.9 ± 9.3 | 7.04 ± 0.80 | 0.946 ± 0.093 | 0.0 ± 0.0 | 0.004 ± 0.007 |
| 0.30 | 0.767 ± 0.029 | 0.733 ± 0.029 | 0.0 ± 0.0 | 0.936 ± 0.034 | 0.922 ± 0.031 | 0.0 ± 0.0 | 0.970 ± 0.005 | 1.0 ± 0.0 | 0.068 ± 0.009 | 3.0 ± 1.0 | 0.439 ± 0.196 | 34.2 ± 4.8 | 6.40 ± 0.83 | 0.976 ± 0.041 | 0.0 ± 0.0 | 0.002 ± 0.003 |
| 0.40 | 0.717 ± 0.029 | 0.650 ± 0.000 | 0.4 ± 0.7 | 0.897 ± 0.025 | 0.858 ± 0.022 | 0.0 ± 0.0 | 0.967 ± 0.010 | 1.0 ± 0.0 | 0.068 ± 0.025 | 3.0 ± 1.0 | 0.311 ± 0.224 | 36.1 ± 12.3 | 5.35 ± 0.62 | 0.964 ± 0.062 | 0.0 ± 0.0 | 0.003 ± 0.004 |
| 0.50 | 0.650 ± 0.050 | 0.450 ± 0.100 | 3.3 ± 3.3 | 0.877 ± 0.022 | 0.824 ± 0.015 | 0.0 ± 0.0 | 0.965 ± 0.013 | 1.0 ± 0.0 | 0.064 ± 0.008 | 3.2 ± 1.6 | 0.198 ± 0.208 | 35.3 ± 4.1 | 4.47 ± 0.51 | 1.000 ± 0.000 | 0.0 ± 0.0 | 0.000 ± 0.000 |

#### P (P1, P2, P3, P4, P5; 4,000,000 observer-ticks) — DR-h24+p
episodes 288 (72 friend-episodes): reset 200, mid-world in sight 20, mid-world under fog 68
per set: P1 reset 40 / mid-world 8; P2 reset 40 / mid-world 16; P3 reset 40 / mid-world 28; P4 reset 40 / mid-world 20; P5 reset 40 / mid-world 16

| P ≥ | mw-sight det | antic | p90 lat | mw-fog det | antic | p90 lat | reset det | reset med lat | mw FA /10k | mw FA len | all FA /10k | mw FA per 100 det | non-grave ticks ≥ t /10k | mw FA start ≤ 100 | mw FA at tick 1 | late FA /10k (start > 100) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.05 | 0.917 ± 0.029 | 0.883 ± 0.076 | 0.0 ± 0.0 | 0.975 ± 0.008 | 0.971 ± 0.000 | 0.0 ± 0.0 | 1.000 ± 0.000 | 0.0 ± 0.0 | 0.392 ± 0.265 | 2.0 ± 1.7 | 2.392 ± 0.265 | 184.5 ± 124.2 | 29.71 ± 8.96 | 0.887 ± 0.058 | 0.0 ± 0.0 | 0.034 ± 0.015 |
| 0.10 | 0.867 ± 0.029 | 0.783 ± 0.076 | 0.8 ± 1.4 | 0.961 ± 0.017 | 0.936 ± 0.037 | 0.0 ± 0.0 | 1.000 ± 0.000 | 0.0 ± 0.0 | 0.269 ± 0.170 | 2.5 ± 1.8 | 2.267 ± 0.169 | 131.2 ± 84.4 | 20.13 ± 4.67 | 0.876 ± 0.182 | 0.0 ± 0.0 | 0.015 ± 0.014 |
| 0.15 | 0.783 ± 0.076 | 0.667 ± 0.076 | 1.5 ± 2.0 | 0.931 ± 0.045 | 0.912 ± 0.064 | 0.0 ± 0.0 | 1.000 ± 0.000 | 0.0 ± 0.0 | 0.198 ± 0.123 | 2.5 ± 0.9 | 2.177 ± 0.128 | 101.8 ± 64.8 | 15.12 ± 2.78 | 0.848 ± 0.244 | 0.0 ± 0.0 | 0.013 ± 0.017 |
| 0.20 | 0.683 ± 0.076 | 0.600 ± 0.050 | 0.9 ± 0.8 | 0.926 ± 0.053 | 0.882 ± 0.092 | 0.1 ± 0.1 | 0.997 ± 0.006 | 0.0 ± 0.0 | 0.159 ± 0.076 | 2.3 ± 0.6 | 2.055 ± 0.170 | 84.6 ± 43.5 | 12.26 ± 1.69 | 0.942 ± 0.066 | 0.0 ± 0.0 | 0.007 ± 0.006 |
| 0.25 | 0.617 ± 0.029 | 0.550 ± 0.000 | 0.3 ± 0.5 | 0.892 ± 0.075 | 0.858 ± 0.084 | 0.0 ± 0.0 | 0.995 ± 0.009 | 0.0 ± 0.0 | 0.116 ± 0.057 | 2.3 ± 0.6 | 1.669 ± 0.505 | 65.2 ± 35.5 | 10.08 ± 1.29 | 0.862 ± 0.137 | 0.0 ± 0.0 | 0.011 ± 0.007 |
| 0.30 | 0.567 ± 0.029 | 0.533 ± 0.029 | 0.0 ± 0.0 | 0.863 ± 0.096 | 0.809 ± 0.074 | 0.0 ± 0.0 | 0.985 ± 0.000 | 0.7 ± 0.6 | 0.099 ± 0.045 | 3.7 ± 0.6 | 1.076 ± 0.549 | 58.1 ± 28.8 | 8.31 ± 0.91 | 0.952 ± 0.053 | 1.0 ± 1.0 | 0.003 ± 0.003 |
| 0.40 | 0.567 ± 0.029 | 0.483 ± 0.029 | 0.3 ± 0.5 | 0.809 ± 0.059 | 0.711 ± 0.075 | 2.3 ± 4.0 | 0.982 ± 0.006 | 1.0 ± 0.0 | 0.089 ± 0.031 | 2.8 ± 1.8 | 0.388 ± 0.238 | 54.3 ± 20.2 | 6.05 ± 0.41 | 0.970 ± 0.026 | 0.3 ± 0.6 | 0.003 ± 0.003 |
| 0.50 | 0.500 ± 0.000 | 0.450 ± 0.000 | 0.3 ± 0.3 | 0.745 ± 0.034 | 0.652 ± 0.066 | 6.8 ± 9.4 | 0.982 ± 0.006 | 1.0 ± 0.0 | 0.082 ± 0.030 | 4.7 ± 2.8 | 0.210 ± 0.132 | 53.9 ± 19.8 | 4.71 ± 0.14 | 1.000 ± 0.000 | 0.0 ± 0.0 | 0.000 ± 0.000 |

#### LWG (L, W, G; 2,800,000 observer-ticks) — NF-h24+p
episodes 296 (74 friend-episodes): reset 196, mid-world in sight 22, mid-world under fog 78
per set: W reset 36 / mid-world 52; G reset 160 / mid-world 48; L 0 / 0

| P ≥ | mw-sight det | antic | p90 lat | mw-fog det | antic | p90 lat | reset det | reset med lat | mw FA /10k | mw FA len | all FA /10k | mw FA per 100 det | non-grave ticks ≥ t /10k | mw FA start ≤ 100 | mw FA at tick 1 | late FA /10k (start > 100) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.05 | 0.985 ± 0.026 | 0.970 ± 0.052 | 0.0 ± 0.0 | 0.983 ± 0.020 | 0.974 ± 0.013 | 0.0 ± 0.0 | 1.000 ± 0.000 | 0.0 ± 0.0 | 0.274 ± 0.084 | 6.5 ± 1.3 | 0.850 ± 0.092 | 78.3 ± 25.5 | 27.94 ± 0.52 | 0.847 ± 0.067 | 0.0 ± 0.0 | 0.038 ± 0.005 |
| 0.10 | 0.955 ± 0.079 | 0.909 ± 0.079 | 0.6 ± 1.0 | 0.949 ± 0.044 | 0.927 ± 0.032 | 0.0 ± 0.0 | 1.000 ± 0.000 | 0.0 ± 0.0 | 0.277 ± 0.099 | 4.7 ± 0.8 | 0.795 ± 0.185 | 83.0 ± 34.7 | 22.57 ± 0.69 | 0.925 ± 0.089 | 0.0 ± 0.0 | 0.017 ± 0.016 |
| 0.15 | 0.909 ± 0.045 | 0.833 ± 0.026 | 0.1 ± 0.2 | 0.944 ± 0.041 | 0.906 ± 0.027 | 0.0 ± 0.0 | 1.000 ± 0.000 | 0.0 ± 0.0 | 0.256 ± 0.080 | 5.0 ± 1.0 | 0.751 ± 0.141 | 77.3 ± 27.8 | 19.58 ± 0.78 | 0.962 ± 0.050 | 0.3 ± 0.6 | 0.012 ± 0.018 |
| 0.20 | 0.833 ± 0.052 | 0.773 ± 0.000 | 0.2 ± 0.2 | 0.915 ± 0.027 | 0.880 ± 0.027 | 0.0 ± 0.0 | 1.000 ± 0.000 | 0.0 ± 0.0 | 0.281 ± 0.088 | 4.3 ± 1.5 | 0.667 ± 0.134 | 88.4 ± 30.5 | 17.28 ± 0.47 | 0.980 ± 0.034 | 6.0 ± 10.4 | 0.007 ± 0.012 |
| 0.25 | 0.818 ± 0.045 | 0.758 ± 0.026 | 0.1 ± 0.2 | 0.889 ± 0.045 | 0.825 ± 0.032 | 0.0 ± 0.0 | 0.995 ± 0.009 | 0.0 ± 0.0 | 0.298 ± 0.066 | 6.3 ± 2.5 | 0.575 ± 0.131 | 96.0 ± 23.9 | 15.41 ± 0.29 | 0.992 ± 0.014 | 20.0 ± 25.7 | 0.002 ± 0.004 |
| 0.30 | 0.788 ± 0.026 | 0.742 ± 0.026 | 0.2 ± 0.3 | 0.859 ± 0.038 | 0.761 ± 0.020 | 0.2 ± 0.2 | 0.988 ± 0.021 | 0.3 ± 0.6 | 0.338 ± 0.051 | 5.7 ± 2.1 | 0.562 ± 0.141 | 112.4 ± 17.7 | 13.94 ± 0.42 | 0.996 ± 0.007 | 28.0 ± 32.1 | 0.001 ± 0.002 |
| 0.40 | 0.727 ± 0.079 | 0.652 ± 0.095 | 0.7 ± 0.7 | 0.765 ± 0.045 | 0.675 ± 0.058 | 3.5 ± 3.8 | 0.973 ± 0.012 | 0.3 ± 0.6 | 0.355 ± 0.041 | 5.0 ± 1.0 | 0.521 ± 0.153 | 132.2 ± 23.0 | 11.45 ± 0.39 | 0.996 ± 0.007 | 37.0 ± 22.1 | 0.001 ± 0.002 |
| 0.50 | 0.606 ± 0.139 | 0.500 ± 0.157 | 3.9 ± 3.4 | 0.701 ± 0.053 | 0.594 ± 0.049 | 8.2 ± 10.1 | 0.956 ± 0.016 | 0.7 ± 0.6 | 0.407 ± 0.022 | 4.7 ± 0.6 | 0.477 ± 0.075 | 168.2 ± 9.0 | 9.24 ± 0.33 | 0.994 ± 0.010 | 44.3 ± 3.8 | 0.002 ± 0.004 |

#### LWG (L, W, G; 2,800,000 observer-ticks) — DR-h24+p
episodes 296 (74 friend-episodes): reset 196, mid-world in sight 22, mid-world under fog 78
per set: W reset 36 / mid-world 52; G reset 160 / mid-world 48; L 0 / 0

| P ≥ | mw-sight det | antic | p90 lat | mw-fog det | antic | p90 lat | reset det | reset med lat | mw FA /10k | mw FA len | all FA /10k | mw FA per 100 det | non-grave ticks ≥ t /10k | mw FA start ≤ 100 | mw FA at tick 1 | late FA /10k (start > 100) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.05 | 1.000 ± 0.000 | 0.985 ± 0.026 | 0.0 ± 0.0 | 0.987 ± 0.022 | 0.987 ± 0.022 | 0.0 ± 0.0 | 1.000 ± 0.000 | 0.0 ± 0.0 | 0.375 ± 0.058 | 5.0 ± 1.0 | 0.948 ± 0.060 | 106.2 ± 18.0 | 42.01 ± 0.49 | 0.918 ± 0.043 | 0.0 ± 0.0 | 0.032 ± 0.019 |
| 0.10 | 0.939 ± 0.052 | 0.924 ± 0.026 | 0.0 ± 0.0 | 0.970 ± 0.041 | 0.957 ± 0.045 | 0.0 ± 0.0 | 1.000 ± 0.000 | 0.0 ± 0.0 | 0.440 ± 0.082 | 5.0 ± 1.0 | 1.023 ± 0.078 | 128.5 ± 26.4 | 32.61 ± 0.26 | 0.932 ± 0.025 | 0.0 ± 0.0 | 0.031 ± 0.015 |
| 0.15 | 0.894 ± 0.026 | 0.864 ± 0.045 | 0.0 ± 0.1 | 0.932 ± 0.052 | 0.902 ± 0.041 | 0.0 ± 0.0 | 1.000 ± 0.000 | 0.0 ± 0.0 | 0.400 ± 0.043 | 4.8 ± 0.8 | 0.987 ± 0.029 | 121.1 ± 8.8 | 26.95 ± 0.33 | 0.951 ± 0.031 | 0.0 ± 0.0 | 0.019 ± 0.013 |
| 0.20 | 0.879 ± 0.026 | 0.848 ± 0.026 | 0.0 ± 0.0 | 0.906 ± 0.061 | 0.825 ± 0.041 | 0.1 ± 0.1 | 1.000 ± 0.000 | 0.0 ± 0.0 | 0.401 ± 0.076 | 5.3 ± 1.2 | 0.961 ± 0.068 | 124.5 ± 20.2 | 22.95 ± 0.26 | 0.936 ± 0.024 | 4.7 ± 6.4 | 0.026 ± 0.013 |
| 0.25 | 0.818 ± 0.045 | 0.788 ± 0.069 | 0.1 ± 0.2 | 0.850 ± 0.066 | 0.782 ± 0.080 | 0.0 ± 0.0 | 0.998 ± 0.003 | 0.0 ± 0.0 | 0.454 ± 0.084 | 5.0 ± 0.5 | 0.883 ± 0.116 | 149.9 ± 16.9 | 19.82 ± 0.25 | 0.964 ± 0.029 | 14.7 ± 15.6 | 0.015 ± 0.011 |
| 0.30 | 0.773 ± 0.045 | 0.742 ± 0.069 | 0.0 ± 0.0 | 0.829 ± 0.083 | 0.744 ± 0.077 | 0.6 ± 0.6 | 0.991 ± 0.006 | 0.3 ± 0.6 | 0.480 ± 0.070 | 5.3 ± 0.6 | 0.756 ± 0.129 | 164.9 ± 23.2 | 17.09 ± 0.40 | 0.973 ± 0.031 | 28.0 ± 18.3 | 0.012 ± 0.013 |
| 0.40 | 0.697 ± 0.026 | 0.621 ± 0.026 | 0.0 ± 0.0 | 0.735 ± 0.133 | 0.590 ± 0.090 | 4.1 ± 3.3 | 0.969 ± 0.018 | 0.7 ± 0.6 | 0.494 ± 0.047 | 4.7 ± 0.6 | 0.575 ± 0.082 | 191.2 ± 8.9 | 12.78 ± 0.79 | 0.972 ± 0.016 | 41.0 ± 5.0 | 0.014 ± 0.009 |
| 0.50 | 0.591 ± 0.091 | 0.530 ± 0.069 | 0.2 ± 0.3 | 0.577 ± 0.068 | 0.432 ± 0.096 | 14.9 ± 13.9 | 0.951 ± 0.019 | 1.0 ± 0.0 | 0.462 ± 0.092 | 4.3 ± 0.6 | 0.493 ± 0.093 | 221.6 ± 25.6 | 9.47 ± 0.88 | 0.983 ± 0.021 | 35.0 ± 3.5 | 0.008 ± 0.011 |

### Composition of the sets

Group P: five sets of ten evaluation worlds (4,000,000 observer-ticks;
4,000-tick slices); every set carries 40 reset episodes (its per-cat
grave start, four observers each on ten worlds) and 8 / 16 / 28 / 20 /
16 mid-world episodes (P1–P5). L / W / G: the evaluation worlds of
Phase 1's three groups (3 + 8 + 8 worlds; 2,800,000 observer-ticks;
slices of 20,000 / 6,000 / 4,000 ticks); W (wide starts, all six needs
started in 0–90) carries 36 reset and 52 mid-world episodes, G (grave
starts, all six needs started in 60–95) 160 reset and 48 mid-world,
and L (the lived distribution) none at all. The declaration expected
grave to be rare on L / W / G; it is not, because G is a grave-start
group by design, and the first post-read addition says so. The 296
L / W / G episodes are 74 friend-episodes × 4 observers; the 288 group P
episodes are 72 × 4.

### Limitations of the sweep

The mid-world in-sight cells rest on 20 (P) and 22 (L / W / G)
observer-episodes, one of which is 0.05 (P) or 0.045 (L / W / G) of
the detected fraction; the mid-world fog cells on 68 and 78; the runs-after-tick-100 cells on 0–22
runs per seed (NF-h24+p on P at 0.05: 4 / 6 / 22). The same six probes and the same instrument produce
every row, so the two sets are two reads of one head, not two heads. A
threshold picked here from group P and read again in Phase 2 on group P
re-reads the same 20 episodes; L / W / G is the set a pick can rest on
without that, and its distribution (G's all-needs-high starts, W's
wide starts, no lived world with an episode) is not group P's. R4d's
"mid-world" false-alarm column excludes only the first-tick runs; this
sweep shows the settling transient runs on for about a hundred ticks,
so that column understates how much of the false-alarm count is
start-up — the start-offset columns carry the correction, with 100 a
post-read reporting constant. False alarms are counted as runs, and
what a run costs depends on the consumer. Platt scaling is monotone:
it relabels the thresholds on this curve and moves no row's position
relative to another. Nothing here is about reach, action or welfare;
it is the belief as an alarm, offline, three seeds.

## Addendum 3 — the burn-in (owner 2026-10-25 "Agreed, let's start with 0.10. Run the burn in")

One read on the three NF-h24+p probe runs (DECLARATION §Addendum 3 and
its two post-read additions; 0 new cat-ticks; no weight touched): the alarm
forced off for the first B ticks of every observer slice (B = 0, 25,
50, 100, 150, 200, 300) and R4d's latency instrument run unchanged on
the masked signal, at the sweep's eight thresholds, on group P and on
the L / W / G evaluation worlds; two cross-sections printed (the burn-in
ladder at her threshold 0.10; the threshold ladder at a burn-in of
100), the full grid in `phase1d-burnin.json`. Seeds 1–3, mean ± SD.
Three identities are asserted by the reader before it writes: the B = 0
cells equal the committed sweep's NF-h24+p cells at every threshold on
both sets; onsets at or after B keep their B = 0 latency; at B = 100
the false-alarm run count equals the sweep's runs-after-tick-100 plus
the runs beginning at offset 100. Descriptive: no reading rule was
declared and none is applied. Her threshold ruling is recorded in the
declaration; the burn-in length is hers.

### Headline

**No grave episode in either evaluation set begins after a slice's
hundredth tick, so a burn-in of 100 ticks removes nearly all the false
alarms and the whole onset-detection task with them; the trade-off the sweep drew —
onset detection against false alarms after the start-up — does not
exist in this data, and the comparison that does exist, the alarm's
discrimination inside the start-up window, favours a higher threshold.**
On group P the 88 non-reset onsets fall at offsets 8–72 (median 25.5;
44 at or under 25 ticks, 68 at or under 50), and all 88 are in a slice
that also holds a reset episode: they are the grave-start friend
crossing back into grave during the start-up, not a second friend going
grave mid-world. Of 1,000 slices, 200 have a grave tick in the first
100 ticks and 8 have one after it (736 grave ticks, the tail of
episodes that began earlier). On L / W / G the 100 non-reset onsets fall
at 3–90 (median 24.0; 60 / 84 at or under 25 / 50), 76 of them in a
slice with a reset episode; 220 of 380 slices have grave in the first
100 ticks, 32 after (7,796 grave ticks, the tails of episodes that
began earlier; no onset is later than offset 90). The
burn-in's columns follow from that. At 0.10 on group P the all-runs
false-alarm rate goes 1.607 ± 0.805 per 10,000 observer-ticks at B = 0
(830 / 271 / 828 runs per seed, of which 800 / 242 / 800 begin at the
slice's first tick) → 0.102 ± 0.004 at 25 → 0.187 ± 0.001 at 50 →
0.024 ± 0.013 at 100 (4 / 14 / 11 runs, 4 / 13 / 4 of them beginning
at the boundary and 4 / 12 / 4 cut from a run that held a grave tick) →
0.003 ± 0.006 at 300; on L / W / G 0.795 ± 0.185 →
0.530 ± 0.020 → 0.240 ± 0.021 → 0.019 ± 0.015 (4 / 2 / 10 runs) →
0.006 ± 0.010. The rate is not monotone in B on group P (0.102 at 25,
0.187 at 50), and the two boundary columns say what the rise is: 12.3
± 0.6 runs begin at offset 25 and 54.0 ± 3.6 at offset 50, of which
12.0 ± 1.0 and 49.3 ± 1.5 (11 / 13 / 12 and 51 / 49 / 48 per seed) are
cut from a run that held a grave tick — the declaration's truncation
case, a detection run of the grave-start friend that the mask turns
into a false alarm — while the remaining runs number 30 / 29 / 27 per
seed at 25 and 24 / 26 / 26 at 50; the reset episodes still running at
the boundary are at least 0.618 at 25 and 0.407 at 50 (the reset
detected fraction, a lower bound on them). What the same burn-in costs: by
B = 25 the onsets inside the burn-in are 44 of 88 on P (still caught,
1.000, at a median latency of 6.0 ticks) and 56 of 100 on L / W / G
(0.143 caught); by 50, 68 and 84 (0.451 ± 0.034 and 0.048 caught); by
100, every onset on both sets, caught after the burn-in in 0.000 of
cases on P and 0.153 ± 0.012 on L / W / G (median latency 26.0 ± 1.7);
the mid-world in-sight detected fraction at 0.10 goes 0.900 → 0.900 →
0.450 → 0.000 on P and 0.955 → 0.621 → 0.136 → 0.045 on L / W / G
across B = 0 / 25 / 50 / 100, and the reset detected fraction 0.995 →
0.618 → 0.407 → 0.033 and 1.000 → 0.422 → 0.197 → 0.082 (a reset
episode is caught no earlier than B, so only those still running at B
are caught: median reset length 40.0 ticks on P, 20.0 on L / W / G).
The blind fraction is 0.025 of observer-ticks at B = 100 on P (4,000-tick
slices) and 0.014 on L / W / G. At B = 100 the threshold ladder has
nothing left to detect on P (0.000 in every mid-world cell at every
threshold) and 0.045 in sight / 0.158–0.192 in fog on L / W / G; its
false-alarm rate falls 0.049 ± 0.023 → 0.024 ± 0.013 → 0.003 ± 0.004
on P and 0.055 ± 0.009 → 0.019 ± 0.015 → 0.002 ± 0.004 on L / W / G at
0.05 / 0.10 / 0.50. The start-up split, read without a burn-in: among
group P's 200 slices with a grave tick in the first 100 ticks the alarm
fires inside that window in 0.995 ± 0.009 at 0.10 and 0.978 ± 0.006 at
0.50; among the 800 slices with none it fires in 0.767 ± 0.403 at 0.10
(1.000 / 0.302 / 1.000 per seed — two of the three probes sit at or
over 0.10 on the first tick of every slice) and 0.067 ± 0.102 at 0.50
(0.016 / 0.185 / 0.000); the ladder between runs 0.999 / 0.767 / 0.705
/ 0.412 / 0.241 / 0.186 / 0.121 / 0.067 on the clean slices against
1.000 / 0.995 / 0.992 / 0.987 / 0.983 / 0.982 / 0.980 / 0.978 on the
grave ones. On L / W / G the clean slices (160: L's 60 and 100 of W's 160; every
one of G's 160 slices has grave in the window) fire in 0.885 ± 0.198 at 0.10 and 0.412 ± 0.025
at 0.50, the grave slices (220) in 1.000 and 0.959 ± 0.016. So inside
the window where every onset in these sets occurs, raising the
threshold from 0.10 to 0.50 costs 0.017 of the grave slices on P and
0.041 on L / W / G and lowers the fraction of clean slices that alarm
by 0.700 and 0.473. The sweep's detection curve (§Addendum 2) is built from onsets
inside this window, and its runs-after-tick-100 column from the ticks
outside it; read together they compared a start-up detection with a
post-start-up false-alarm rate. The recommendation for the low end that
this thread drew from them and gave the owner on 2026-10-25, before
this read, does not stand.

### Expectations stated before the read, scored

Three were stated (DECLARATION §Addendum 3), none a prediction to score
for a rule. (1) False-alarm runs per 10,000 non-increasing in B at a
fixed threshold: did NOT hold on group P at 0.10 (0.102 at B = 25,
0.187 at 50, then 0.024 / 0.011 / 0.007 / 0.003) — over the full grid
the 25 → 50 rise is there at six of the eight thresholds on P (0.05
through 0.30) and at none on L / W / G — held on L / W / G at 0.10
(0.795 / 0.530 / 0.240 / 0.019 / 0.013 / 0.013 / 0.006); the rise is
the truncation case the declaration named, in full: the runs cut from
a run that held a grave tick go 11 / 13 / 12 → 51 / 49 / 48 per seed
between B = 25 and 50 while all other runs go 30 / 29 / 27 → 24 / 26 /
26 (the second post-read addition's column, made for this). (2) At B = 100 and 0.10 the false-alarm rate on
group P within 0.05 per 10,000 of the sweep's late-runs column (0.007):
held, 0.024 ± 0.013 (identity 3 makes it the late runs plus the 4 / 13
/ 4 boundary runs per seed). (3) Reset detection delayed to a median
latency of B on every cell with B > 0: did NOT hold as stated. The
median is at or over B in every non-empty cell, exactly B in 27 of the
40 non-empty cells on P and 43 of the 48 on L / W / G, and over B in
the rest by up to 19.7 ticks on P (169.7 at B = 150 / 0.20) and 20.3
on L / W / G (320.3 at B = 300 / 0.30) — cells where the caught reset
episodes' first tick at or over the threshold came after the boundary;
the printed cells read 100.0 at B = 100 on both sets at 0.10,
100.0–102.5 across the threshold ladder on P and 100.0 on L / W / G;
at B = 300 on P no reset episode is detected at any threshold (eight
empty cells). The detected fraction falls as stated above.

### R6d — the tables (`phase1d-burnin.md`, verbatim)

Columns: `blind` the fraction of observer-ticks inside a burn-in;
`mw-sight det` / `mw-fog det` and `p90 lat` as in the sweep, on the
masked signal; `mw onsets in burn-in` the mid-world episodes whose onset
offset is under B, `their det` / `their med lat` their detected fraction
and median latency (from onset) under the burn-in; `reset det` / `reset
med lat` the reset episodes; `FA /10k` all false-alarm runs (at or over
the threshold, no grave tick) per 10,000 observer-ticks — under a
burn-in there is no first-tick run, so this is the false-alarm read, and
at B = 0 it is the sweep's all-runs column; `FA len` their median length;
`FA at boundary` the runs beginning exactly at offset B (at B = 0, the
first-tick runs); `of them cut from a grave run` those whose unmasked
run began before B and held a grave tick; `FA per 100 mw det` all runs
per 100 detected mid-world episodes. The per-set line gives slices,
observer-ticks and slices with a grave tick in the first 100 ticks by
evaluation set. The start-up split counts slices (one friend seen by
one observer), not episodes.

## P (P1, P2, P3, P4, P5; 4,000,000 observer-ticks): episodes 288, reset 200, mid-world 88
mid-world onset offsets: n 88, min 8, median 25.5, max 72; at or under 25 / 50 / 100 ticks: 44 / 68 / 88; in a slice that also has a reset episode: 88. Slices 1000: with a grave tick in the first 100 ticks 200, with a grave tick after tick 100 8 (736 grave ticks). Per set (slices / observer-ticks / slices with grave in the window): P1 200 / 800,000 / 40; P2 200 / 800,000 / 40; P3 200 / 800,000 / 40; P4 200 / 800,000 / 40; P5 200 / 800,000 / 40.

### start-up split: slices whose alarm fires within the first 100 ticks
| P ≥ | slices with grave in window | fired, given grave | slices without | fired, given none |
|---|---|---|---|---|
| 0.05 | 200 ± 0 | 1.000 ± 0.000 | 800 ± 0 | 0.999 ± 0.002 |
| 0.10 | 200 ± 0 | 0.995 ± 0.009 | 800 ± 0 | 0.767 ± 0.403 |
| 0.15 | 200 ± 0 | 0.992 ± 0.008 | 800 ± 0 | 0.705 ± 0.397 |
| 0.20 | 200 ± 0 | 0.987 ± 0.003 | 800 ± 0 | 0.412 ± 0.151 |
| 0.25 | 200 ± 0 | 0.983 ± 0.008 | 800 ± 0 | 0.241 ± 0.051 |
| 0.30 | 200 ± 0 | 0.982 ± 0.006 | 800 ± 0 | 0.186 ± 0.094 |
| 0.40 | 200 ± 0 | 0.980 ± 0.005 | 800 ± 0 | 0.121 ± 0.103 |
| 0.50 | 200 ± 0 | 0.978 ± 0.006 | 800 ± 0 | 0.067 ± 0.102 |

### burn-in ladder at P ≥ 0.10
| burn-in | P ≥ | blind | mw-sight det | p90 lat | mw-fog det | p90 lat | mw onsets in burn-in | their det | their med lat | reset det | reset med lat | FA /10k | FA len | FA at boundary | of them cut from a grave run | FA per 100 mw det |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 0.10 | 0.000 ± 0.000 | 0.900 ± 0.050 | 0.0 ± 0.0 | 0.956 ± 0.053 | 0.0 ± 0.0 | 0 ± 0 | — | — | 0.995 ± 0.009 | 0.3 ± 0.6 | 1.607 ± 0.805 | 1.3 ± 0.6 | 614.0 ± 322.2 | 0.0 ± 0.0 | 764.9 ± 366.2 |
| 25 | 0.10 | 0.006 ± 0.000 | 0.900 ± 0.050 | 2.3 ± 0.5 | 0.956 ± 0.053 | 15.0 ± 0.0 | 44 ± 0 | 1.000 ± 0.000 | 6.0 ± 0.0 | 0.618 ± 0.003 | 25.0 ± 0.0 | 0.102 ± 0.004 | 7.0 ± 1.0 | 12.3 ± 0.6 | 12.0 ± 1.0 | 49.1 ± 4.2 |
| 50 | 0.10 | 0.013 ± 0.000 | 0.450 ± 0.050 | 9.0 ± 0.0 | 0.574 ± 0.076 | 39.8 ± 1.4 | 68 ± 0 | 0.451 ± 0.034 | 35.0 ± 1.7 | 0.407 ± 0.003 | 50.0 ± 0.0 | 0.187 ± 0.001 | 8.0 ± 0.0 | 54.0 ± 3.6 | 49.3 ± 1.5 | 157.0 ± 19.1 |
| 100 | 0.10 | 0.025 ± 0.000 | 0.000 ± 0.000 | — | 0.000 ± 0.000 | — | 88 ± 0 | 0.000 ± 0.000 | — | 0.033 ± 0.012 | 100.0 ± 0.0 | 0.024 ± 0.013 | 2.8 ± 0.8 | 7.0 ± 5.2 | 6.7 ± 4.6 | — |
| 150 | 0.10 | 0.037 ± 0.000 | 0.000 ± 0.000 | — | 0.000 ± 0.000 | — | 88 ± 0 | 0.000 ± 0.000 | — | 0.020 ± 0.000 | 150.0 ± 0.0 | 0.011 ± 0.010 | 10.0 ± 9.9 | 1.7 ± 2.1 | 1.7 ± 2.1 | — |
| 200 | 0.10 | 0.050 ± 0.000 | 0.000 ± 0.000 | — | 0.000 ± 0.000 | — | 88 ± 0 | 0.000 ± 0.000 | — | 0.018 ± 0.003 | 200.0 ± 0.0 | 0.007 ± 0.009 | 5.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | — |
| 300 | 0.10 | 0.075 ± 0.000 | 0.000 ± 0.000 | — | 0.000 ± 0.000 | — | 88 ± 0 | 0.000 ± 0.000 | — | 0.000 ± 0.000 | — | 0.003 ± 0.006 | 8.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | — |

### threshold ladder at burn-in 100
| burn-in | P ≥ | blind | mw-sight det | p90 lat | mw-fog det | p90 lat | mw onsets in burn-in | their det | their med lat | reset det | reset med lat | FA /10k | FA len | FA at boundary | of them cut from a grave run | FA per 100 mw det |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 100 | 0.05 | 0.025 ± 0.000 | 0.000 ± 0.000 | — | 0.000 ± 0.000 | — | 88 ± 0 | 0.000 ± 0.000 | — | 0.040 ± 0.000 | 100.0 ± 0.0 | 0.049 ± 0.023 | 4.3 ± 0.6 | 9.0 ± 7.8 | 8.0 ± 6.1 | — |
| 100 | 0.10 | 0.025 ± 0.000 | 0.000 ± 0.000 | — | 0.000 ± 0.000 | — | 88 ± 0 | 0.000 ± 0.000 | — | 0.033 ± 0.012 | 100.0 ± 0.0 | 0.024 ± 0.013 | 2.8 ± 0.8 | 7.0 ± 5.2 | 6.7 ± 4.6 | — |
| 100 | 0.15 | 0.025 ± 0.000 | 0.000 ± 0.000 | — | 0.000 ± 0.000 | — | 88 ± 0 | 0.000 ± 0.000 | — | 0.033 ± 0.012 | 100.3 ± 0.6 | 0.020 ± 0.013 | 2.0 ± 0.0 | 6.7 ± 4.6 | 6.7 ± 4.6 | — |
| 100 | 0.20 | 0.025 ± 0.000 | 0.000 ± 0.000 | — | 0.000 ± 0.000 | — | 88 ± 0 | 0.000 ± 0.000 | — | 0.033 ± 0.012 | 100.5 ± 0.9 | 0.018 ± 0.014 | 4.2 ± 4.2 | 6.0 ± 3.5 | 6.0 ± 3.5 | — |
| 100 | 0.25 | 0.025 ± 0.000 | 0.000 ± 0.000 | — | 0.000 ± 0.000 | — | 88 ± 0 | 0.000 ± 0.000 | — | 0.033 ± 0.012 | 100.7 ± 1.2 | 0.017 ± 0.015 | 2.7 ± 2.9 | 5.3 ± 3.2 | 5.3 ± 3.2 | — |
| 100 | 0.30 | 0.025 ± 0.000 | 0.000 ± 0.000 | — | 0.000 ± 0.000 | — | 88 ± 0 | 0.000 ± 0.000 | — | 0.028 ± 0.020 | 100.8 ± 1.4 | 0.011 ± 0.010 | 3.0 ± 3.5 | 3.7 ± 3.1 | 3.7 ± 3.1 | — |
| 100 | 0.40 | 0.025 ± 0.000 | 0.000 ± 0.000 | — | 0.000 ± 0.000 | — | 88 ± 0 | 0.000 ± 0.000 | — | 0.028 ± 0.020 | 101.2 ± 2.0 | 0.007 ± 0.013 | 1.0 | 2.0 ± 3.5 | 1.7 ± 2.9 | — |
| 100 | 0.50 | 0.025 ± 0.000 | 0.000 ± 0.000 | — | 0.000 ± 0.000 | — | 88 ± 0 | 0.000 ± 0.000 | — | 0.025 ± 0.022 | 102.5 ± 3.5 | 0.003 ± 0.004 | 1.0 | 1.0 ± 1.7 | 0.3 ± 0.6 | — |

## LWG (L, W, G; 2,800,000 observer-ticks): episodes 296, reset 196, mid-world 100
mid-world onset offsets: n 100, min 3, median 24.0, max 90; at or under 25 / 50 / 100 ticks: 60 / 84 / 100; in a slice that also has a reset episode: 76. Slices 380: with a grave tick in the first 100 ticks 220, with a grave tick after tick 100 32 (7796 grave ticks). Per set (slices / observer-ticks / slices with grave in the window): L 60 / 1,200,000 / 0; W 160 / 960,000 / 60; G 160 / 640,000 / 160.

### start-up split: slices whose alarm fires within the first 100 ticks
| P ≥ | slices with grave in window | fired, given grave | slices without | fired, given none |
|---|---|---|---|---|
| 0.05 | 220 ± 0 | 1.000 ± 0.000 | 160 ± 0 | 1.000 ± 0.000 |
| 0.10 | 220 ± 0 | 1.000 ± 0.000 | 160 ± 0 | 0.885 ± 0.198 |
| 0.15 | 220 ± 0 | 1.000 ± 0.000 | 160 ± 0 | 0.838 ± 0.189 |
| 0.20 | 220 ± 0 | 1.000 ± 0.000 | 160 ± 0 | 0.677 ± 0.053 |
| 0.25 | 220 ± 0 | 0.997 ± 0.005 | 160 ± 0 | 0.571 ± 0.103 |
| 0.30 | 220 ± 0 | 0.989 ± 0.018 | 160 ± 0 | 0.531 ± 0.097 |
| 0.40 | 220 ± 0 | 0.980 ± 0.011 | 160 ± 0 | 0.498 ± 0.091 |
| 0.50 | 220 ± 0 | 0.959 ± 0.016 | 160 ± 0 | 0.412 ± 0.025 |

### burn-in ladder at P ≥ 0.10
| burn-in | P ≥ | blind | mw-sight det | p90 lat | mw-fog det | p90 lat | mw onsets in burn-in | their det | their med lat | reset det | reset med lat | FA /10k | FA len | FA at boundary | of them cut from a grave run | FA per 100 mw det |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 0.10 | 0.000 ± 0.000 | 0.955 ± 0.079 | 0.6 ± 1.0 | 0.949 ± 0.044 | 0.0 ± 0.0 | 0 ± 0 | — | — | 1.000 ± 0.000 | 0.0 ± 0.0 | 0.795 ± 0.185 | 4.3 ± 3.2 | 145.0 ± 34.0 | 0.0 ± 0.0 | 236.7 ± 68.1 |
| 25 | 0.10 | 0.003 ± 0.000 | 0.621 ± 0.026 | 1.1 ± 0.6 | 0.466 ± 0.007 | 1.3 ± 0.6 | 56 ± 0 | 0.143 ± 0.000 | 1.0 ± 0.0 | 0.422 ± 0.003 | 25.0 ± 0.0 | 0.530 ± 0.020 | 8.8 ± 1.0 | 94.3 ± 4.7 | 57.3 ± 7.0 | 296.7 ± 11.0 |
| 50 | 0.10 | 0.007 ± 0.000 | 0.136 ± 0.000 | 21.0 ± 0.0 | 0.218 ± 0.000 | 13.8 ± 6.5 | 84 ± 0 | 0.048 ± 0.000 | 21.0 ± 0.0 | 0.197 ± 0.013 | 50.0 ± 0.0 | 0.240 ± 0.021 | 5.8 ± 1.3 | 50.0 ± 5.3 | 36.7 ± 0.6 | 336.7 ± 28.9 |
| 100 | 0.10 | 0.014 ± 0.000 | 0.045 ± 0.000 | 24.0 ± 0.0 | 0.184 ± 0.015 | 37.0 ± 0.0 | 100 ± 0 | 0.153 ± 0.012 | 26.0 ± 1.7 | 0.082 ± 0.000 | 100.0 ± 0.0 | 0.019 ± 0.015 | 4.0 ± 2.6 | 0.7 ± 1.2 | 0.3 ± 0.6 | 36.3 ± 31.0 |
| 150 | 0.10 | 0.020 ± 0.000 | 0.045 ± 0.000 | 74.0 ± 0.0 | 0.141 ± 0.000 | 87.0 ± 0.0 | 100 ± 0 | 0.120 ± 0.000 | 74.0 ± 0.0 | 0.041 ± 0.000 | 150.0 ± 0.0 | 0.013 ± 0.017 | 2.8 ± 0.4 | 0.0 ± 0.0 | 0.0 ± 0.0 | 30.6 ± 39.4 |
| 200 | 0.10 | 0.027 ± 0.000 | 0.045 ± 0.000 | 124.0 ± 0.0 | 0.090 ± 0.000 | 124.0 ± 0.0 | 100 ± 0 | 0.080 ± 0.000 | 117.0 ± 0.0 | 0.041 ± 0.000 | 200.0 ± 0.0 | 0.013 ± 0.017 | 2.8 ± 0.4 | 0.0 ± 0.0 | 0.0 ± 0.0 | 45.8 ± 59.1 |
| 300 | 0.10 | 0.041 ± 0.000 | 0.045 ± 0.000 | 224.0 ± 0.0 | 0.090 ± 0.000 | 224.0 ± 0.0 | 100 ± 0 | 0.080 ± 0.000 | 217.0 ± 0.0 | 0.020 ± 0.000 | 300.0 ± 0.0 | 0.006 ± 0.010 | 5.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 20.8 ± 36.1 |

### threshold ladder at burn-in 100
| burn-in | P ≥ | blind | mw-sight det | p90 lat | mw-fog det | p90 lat | mw onsets in burn-in | their det | their med lat | reset det | reset med lat | FA /10k | FA len | FA at boundary | of them cut from a grave run | FA per 100 mw det |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 100 | 0.05 | 0.014 ± 0.000 | 0.045 ± 0.000 | 24.0 ± 0.0 | 0.192 ± 0.000 | 37.4 ± 0.7 | 100 ± 0 | 0.160 ± 0.000 | 27.0 ± 0.0 | 0.082 ± 0.000 | 100.0 ± 0.0 | 0.055 ± 0.009 | 4.7 ± 2.5 | 4.7 ± 3.2 | 3.0 ± 2.6 | 95.8 ± 15.7 |
| 100 | 0.10 | 0.014 ± 0.000 | 0.045 ± 0.000 | 24.0 ± 0.0 | 0.184 ± 0.015 | 37.0 ± 0.0 | 100 ± 0 | 0.153 ± 0.012 | 26.0 ± 1.7 | 0.082 ± 0.000 | 100.0 ± 0.0 | 0.019 ± 0.015 | 4.0 ± 2.6 | 0.7 ± 1.2 | 0.3 ± 0.6 | 36.3 ± 31.0 |
| 100 | 0.15 | 0.014 ± 0.000 | 0.045 ± 0.000 | 24.7 ± 1.2 | 0.175 ± 0.020 | 37.0 ± 0.0 | 100 ± 0 | 0.147 ± 0.015 | 27.0 ± 3.0 | 0.082 ± 0.000 | 100.0 ± 0.0 | 0.013 ± 0.020 | 2.8 ± 0.4 | 0.3 ± 0.6 | 0.0 ± 0.0 | 23.4 ± 34.1 |
| 100 | 0.20 | 0.014 ± 0.000 | 0.045 ± 0.000 | 25.7 ± 2.9 | 0.171 ± 0.020 | 37.6 ± 1.0 | 100 ± 0 | 0.143 ± 0.015 | 27.0 ± 3.0 | 0.082 ± 0.000 | 100.0 ± 0.0 | 0.008 ± 0.014 | 3.0 | 0.3 ± 0.6 | 0.0 ± 0.0 | 14.6 ± 25.3 |
| 100 | 0.25 | 0.014 ± 0.000 | 0.045 ± 0.000 | 28.7 ± 8.1 | 0.162 ± 0.027 | 44.7 ± 7.5 | 100 ± 0 | 0.137 ± 0.021 | 29.3 ± 6.8 | 0.082 ± 0.000 | 100.0 ± 0.0 | 0.004 ± 0.006 | 3.0 | 0.3 ± 0.6 | 0.0 ± 0.0 | 6.2 ± 10.8 |
| 100 | 0.30 | 0.014 ± 0.000 | 0.045 ± 0.000 | 32.7 ± 15.0 | 0.162 ± 0.027 | 50.4 ± 11.9 | 100 ± 0 | 0.137 ± 0.021 | 29.3 ± 6.8 | 0.082 ± 0.000 | 100.0 ± 0.0 | 0.002 ± 0.002 | 4.0 ± 2.8 | 0.3 ± 0.6 | 0.0 ± 0.0 | 4.6 ± 4.1 |
| 100 | 0.40 | 0.014 ± 0.000 | 0.045 ± 0.000 | 35.0 ± 19.1 | 0.158 ± 0.030 | 66.0 ± 29.0 | 100 ± 0 | 0.133 ± 0.023 | 29.5 ± 6.7 | 0.082 ± 0.000 | 100.0 ± 0.0 | 0.001 ± 0.002 | 8.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 2.8 ± 4.8 |
| 100 | 0.50 | 0.014 ± 0.000 | 0.045 ± 0.000 | 39.7 ± 19.1 | 0.158 ± 0.030 | 84.3 ± 44.8 | 100 ± 0 | 0.133 ± 0.023 | 37.8 ± 16.6 | 0.078 ± 0.006 | 100.0 ± 0.0 | 0.002 ± 0.004 | 6.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 5.6 ± 9.6 |

### Limitations of the burn-in read

Everything here is a property of two evaluation sets in which every
grave onset is a start-up one: group P's per-cat grave starts, W's wide
starts and G's all-needs-high starts put every onset inside the first
hundred ticks, and L, the lived worlds under the certified roster, has
no episode at all in its 60 slices of 20,000 ticks (1,200,000
observer-ticks). Whether a Gen 2 friend ever goes grave mid-world under
the certified policy is not settled here: L could have shown one and
did not, which is evidence of rarity, not of absence, and a set in
which mid-world onsets are known to occur would have to be built (its
welfare cost declared) before any mid-world detection number can be
claimed. The start-up split is a slice-level read at one window
width (100 ticks, the declared cross-section): it says whether the
alarm fired at all inside the window, not when, and a probe that fires
on the first tick of every slice (two of three seeds at 0.10) is counted
as firing. The mid-world in-sight cells rest on 20 and 22
observer-episodes and the runs-after-burn-in cells on 0–14 runs per
seed at 0.10 (B ≥ 100) and 0–26 across the printed B = 100 ladder (P at
0.05: 9 / 24 / 26). The sweep's late-runs column, the identities and the pin all hold;
what changed is what they mean.

## Addendum 4 — history and state (owner 2026-10-25 "Let's do another threshold sweep rather than choosing an arbitrary value. Maybe 0.1,0.3.,0.5 to start so we can get a feel for the trade-off. Zero-collection reads first. …"; "Yes on splice test. Yes on relay to product. Confirm 3")

Five reads on arrays already on disk (DECLARATION §Addendum 4 and its
post-read addition; 0 new cat-ticks; no weight touched): the frozen
NF-h24 heads re-run with the Phase 1d probes exactly as the probe fit
walked them (zero state at the slice start, carried across 500-tick
chunks), and the re-run P(grave) checked equal to the committed
`pgrave-*.npz` on the first group-P evaluation world per seed, before
that seed's re-run head is used (0.0e+00 on every seed). (a) The state's step and drift and
the logit's trend on L's 60 clean evaluation slices; (b) the splice —
group P's 200 covered reset-grave episodes (the friend's 58-cell rows
over the episode, length 5 / 40 / 238 min / median / max, 14 in sight
at onset) placed after 100 / 500 / 2,000 clean L ticks with the
recipient observer's own self block continuing, a junction control
with a default-start friend's rows over the same ticks, NF-h24+p and
SD width 16, H = 0 the donor episode in its own slice on the committed
signal (pinned to the sweep's reset rows at 0.10 / 0.50 and to R4d's
SD row at 0.50), and — post-read — H = 0 with the recipient's self
block; (c) burn-ins 0 / 2 / 5 / 10 through §Addendum 3's grid (B = 0
pinned to the sweep) and the warm start, every evaluation slice re-run
from h̄ (the mean state over ticks 1,000 … 19,999 of L's clean slices,
per seed) and read through the same grid at B = 0; (d) the self-block
swap on group P's 200 grave-start slices (the (observer, grave-start
seat) row beside the next observer's self block, from the zero state)
against the unswapped committed signal on the same slices; (e) every
table at P(grave) ≥ 0.10 / 0.30 / 0.50; and — post-read — (f) the grave
ticks and onsets of the fitted worlds by offset from the world start,
per role. Seeds 1–3, mean ± SD. Descriptive: no reading rule was
declared and none is applied; the Professor's P3 / P4 / P5 / P8 are
scored below with the declaration's operationalisations. Decision 3
(the threshold) is reopened by her words above; no burn-in is ruled.

### Headline

**The probe's grave detection is a property of the young state. The
same covered grave rows that it detects in 0.995 ± 0.009 of episodes
at a median latency of 0.3 ticks when they arrive at a world's start
are detected in 0.358 ± 0.175 after 100 clean ticks of history (0.540
/ 0.345 / 0.190 per seed) at a median latency of 26.5 ± 12.4 ticks,
and in 0.287 ± 0.143 and 0.288 ± 0.132 after 500 and 2,000; SD width
16 goes 1.000 → 0.275 → 0.282 → 0.287 on the same splices. The
junction control never fires after a history (0.000 ± 0.000 at H =
100 / 500 / 2,000 at every threshold for NF+p; at H = 0 with the
recipient's self block it fires 0.678 ± 0.553 at 0.10, the zero-state
transient on clean rows). The self block is not in it: H = 0 with the recipient's
self block detects 0.995 / 0.972 / 0.968 at 0.10 / 0.30 / 0.50, the
H = 0 row to within 0.003. And the training worlds hold no grave after
offset 322: 6,301 grave ticks over 74 worlds, the latest at offset 322,
182 episode onsets, the latest at 171, 1 after tick 100 (the validation
worlds, which early-stopped the fits, hold 1,960 ticks to offset 601
and 42 onsets to 93; the evaluation worlds 6,778 ticks to 779 and 146
onsets to 90).** The warm start says the same on the real episodes:
run from h̄ instead of zero, the reset detected fraction at 0.10 on
group P falls 0.995 ± 0.009 → 0.592 ± 0.066 (0.650 / 0.520 / 0.605 per
seed) and its median latency 0.3 → 14.7 ± 2.1 ticks, the re-entries
0.900 → 0.350 in sight and 0.956 → 0.765 in fog, while the first-tick
runs go 614.0 ± 322.2 → 0.0 and the clean slices' firing inside the
start-up window 0.767 ± 0.403 → 0.000 ± 0.000 (0.885 → 0.019 on
L / W / G); its all-runs false-alarm rate is 0.078 ± 0.028 per 10,000.
The state on a clean slice does not settle in the sense the declaration
assumed: the median step ‖h_t − h_{t−1}‖ is 0.0480 ± 0.0009 in ticks
[1, 100) and rises to 0.0571 ± 0.0024 from tick 1,000 on, the drift
from h_100 sits between 0.80 and 0.89 (seed means) in every window, and the logit has no
trend (slope 0.0001 ± 0.0021 logits per 1,000 ticks against a
within-slice SD of 0.9387 ± 0.0775; drift-to-scatter 0.032 ± 0.021).
What does change is the first few ticks: the mean logit on a clean
slice is −1.829 ± 0.598 at tick 0 (−1.530 / −2.517 / −1.439 per seed,
P(grave) 0.178 / 0.075 / 0.192: the two probes that sit over 0.10 on
the first tick of every slice in §Addendum 3), −4.059 at tick 1,
−9.371 at tick 10 and −9.29 by tick 1,000. The small burn-ins price
that transient on group P at 0.10: all-runs false alarms 1.607 ± 0.805
per 10,000 at B = 0 → 0.136 ± 0.063 at 2 → 0.073 ± 0.001 at 5 → 0.072
± 0.004 at 10, the reset detected fraction 0.995 → 0.980 → 0.960 →
0.798 (reset episodes are as short as 5 ticks) and the re-entries
untouched at 0.900 / 0.956 through B = 10; on L / W / G the same
burn-ins leave 0.538 → 0.521 → 0.577 per 10,000 (73.0 ± 2.6 runs still
running at the boundary at B = 2, median run length 10.0 ± 3.0 there)
and cost reset detection 1.000 → 0.997 → 0.867 → 0.750. The swap moves
little: on the 200 grave-start slices the reset detected fraction at
0.10 goes 0.995 ± 0.009 → 0.992 ± 0.014, the re-entries 0.900 → 0.883
in sight and 0.956 → 0.951 in fog, false alarms 0.342 → 0.308 per
10,000, the mean P(grave) on grave ticks 0.690 → 0.689. On the
three-point ladder after a clean history, 0.10 detects the most and
the control fires at none of the three (H = 100: 0.358 / 0.228 / 0.162
detected at 0.10 / 0.30 / 0.50, median latency 26.5 / 34.0 / 45.2); at
a world's start the ladder is the start-up split of §Addendum 3 (grave
slices 0.995 / 0.982 / 0.978, clean slices 0.767 / 0.186 / 0.067 on
group P). The one condition the Professor named for reopening SD —
NF+p degrading with history where SD does not — is not met: both
collapse between H = 0 and H = 100 and both are flat from 100 to
2,000; the SD line stays closed. Nothing in this read says whether a
covered friend's slow crossing into grave after a long clean history
would be seen; it says the response to a covered friend's grave rows
depends on how long the state has watched the friend be fine, and that
no grave in the training worlds sits after offset 322 (none in the
validation worlds after 601).

### Predictions scored (the Professor's, 2026-10-25 note §Q6; operationalised in DECLARATION §Addendum 4)

- **P3** ("On L's clean slices the frozen NF-h24 GRU's step size `d_t`
  reaches a stationary band within 300 ticks and the probe logit `z_t`
  shows no monotone trend from tick 300 to the end of the slice (slope
  indistinguishable from zero against its within-slice scatter, pooled
  over slices).") — **not met as operationalised**, on every seed: the band clause holds (the median
  step in [300, 1,000), 0.0543 ± 0.0020, is within a factor of 2 of
  the median from 1,000 on, 0.0571 ± 0.0024) and the trend clause
  holds (drift-to-scatter 0.009 / 0.051 / 0.038 per seed, under 1); the
  operationalisation's third clause, both under the median step of
  ticks [1, 100), fails because that first window has the smallest
  step of all (0.0480 ± 0.0009). The declaration assumed a step that
  starts large and decays; the measured step is near-constant and
  grows slightly with the slice.
- **P4** ("Detection fraction and median latency of a covered start-up
  grave signature spliced after 100 / 500 / 2,000 clean L ticks differ
  across the three history lengths by less than the seed SD, for
  NF-h24+p at 0.10. (If P3 fails, P4 is expected to fail with it; score
  both.)") — **met**: the range of the seed-mean detected
  fraction over the three histories is 0.0717 against a mean seed SD of
  0.1501, the range of the median latency 2.83 ticks against 11.06. The
  prediction's range begins at 100 ticks; the fall from H = 0 (0.995)
  to H = 100 (0.358) lies outside it and is the headline above. The
  coupling the prediction expected did not occur: P3 failed on the
  operationalisation's third clause and P4 held.
- **P5** ("A burn-in of 5 ticks at 0.10 on P brings the all-runs
  false-alarm rate from 1.607 to at most 0.20 per 10,000 observer-ticks
  while keeping reset detection at or above 0.90. A warm-started `h_0`
  at B = 0 does at least as well on both.") — **not met**: the burn-in half holds
  (0.073 ± 0.001 per 10,000; reset detection 0.960 ± 0.005), the
  warm-start half does not (false alarms 0.078 ± 0.028, over 0.073 by
  0.005; reset detection 0.592 ± 0.066 against 0.960).
- **P8** ("On P, swapping the self block across observers within a
  world changes NF-h24+p's mid-world in-sight and fog detected fractions
  at 0.10 by less than the seed SD.") — **met**: Δ
  −0.0167 against an unswapped SD of 0.0500 in sight, Δ −0.0049
  against 0.0530 in fog.

This thread's expectations, not predictions: the junction control
fires in under 0.05 of junctions at 0.10 at every H — holds (0.000 at
100 / 500 / 2,000); the warm start removes at least nine in ten of the
first-tick runs at 0.10 on group P — holds (614.0 → 0.0); the swap moves
the reset detected fraction at 0.10 by under 0.05 — holds (−0.0033).

### R7d tables (the reader's markdown, verbatim; `phase1d-history.json` holds the per-seed cells)

reproduces the committed P(grave) on the first P evaluation world to: s1 0.0e+00, s2 0.0e+00, s3 0.0e+00

### R7d (a) convergence on L's 60 clean slices × 20,000 ticks
| window | median step ‖h_t − h_t−1‖ | median drift ‖h_t − h_100‖ |
|---|---|---|
| [1, 100) | 0.0480 ± 0.0009 | 0.8045 ± 0.1130 |
| [100, 300) | 0.0516 ± 0.0024 | 0.8201 ± 0.1119 |
| [300, 1000) | 0.0543 ± 0.0020 | 0.8814 ± 0.1351 |
| [1000, 5000) | 0.0571 ± 0.0025 | 0.8399 ± 0.1034 |
| [5000, 20000) | 0.0571 ± 0.0024 | 0.8529 ± 0.1134 |
median step over [1000, 20000) (the P3 band's reference): 0.0571 ± 0.0024
logit slope after tick 300: 0.0001 ± 0.0021 logits per 1,000 ticks (SD over slices 0.0097 ± 0.0010); within-slice SD of the logit 0.9387 ± 0.0775; drift-to-scatter ratio 0.032 ± 0.021
mean logit by tick: t=0 -1.829 ± 0.598, t=1 -4.059 ± 1.145, t=2 -5.463 ± 1.479, t=5 -7.917 ± 1.916, t=10 -9.371 ± 2.722, t=25 -10.264 ± 3.398, t=50 -9.244 ± 1.320, t=100 -8.371 ± 0.915, t=300 -9.336 ± 0.652, t=1000 -9.290 ± 0.412
P3 per seed: s1 band True / under-start False / ratio<1 True → False; s2 band True / under-start False / ratio<1 True → False; s3 band True / under-start False / ratio<1 True → False; all seeds met: False

### R7d (b) the splice — 200 covered reset-grave donors (length 5 / 40 / 238 min / median / max; 14 in sight at onset) onto 60 clean L recipients; H = 0 is the committed signal in the donor's own slice

#### NF-h24+p
| H | P ≥ | episodes | detected | median lat | p90 lat | within 10 | in-sight det | fog det | anticipated | FA in history /10k | control fired |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 0.10 | 200 ± 0 | 0.995 ± 0.009 | 0.3 ± 0.6 | 0.7 ± 1.2 | 0.990 ± 0.017 | 1.000 ± 0.000 | 0.995 ± 0.009 | 0.000 ± 0.000 | — | — |
| 0 | 0.30 | 200 ± 0 | 0.970 ± 0.005 | 1.0 ± 0.0 | 2.3 ± 0.6 | 0.957 ± 0.006 | 1.000 ± 0.000 | 0.968 ± 0.005 | 0.000 ± 0.000 | — | — |
| 0 | 0.50 | 200 ± 0 | 0.965 ± 0.013 | 1.0 ± 0.0 | 2.7 ± 0.6 | 0.948 ± 0.020 | 1.000 ± 0.000 | 0.962 ± 0.014 | 0.000 ± 0.000 | — | — |
| 0 (recipient self block) | 0.10 | 200 ± 0 | 0.995 ± 0.009 | 0.3 ± 0.6 | 0.7 ± 1.2 | 0.990 ± 0.017 | 1.000 ± 0.000 | 0.995 ± 0.009 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.678 ± 0.553 |
| 0 (recipient self block) | 0.30 | 200 ± 0 | 0.972 ± 0.003 | 1.0 ± 0.0 | 2.3 ± 0.6 | 0.968 ± 0.006 | 1.000 ± 0.000 | 0.970 ± 0.003 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| 0 (recipient self block) | 0.50 | 200 ± 0 | 0.968 ± 0.008 | 1.0 ± 0.0 | 3.3 ± 0.6 | 0.950 ± 0.009 | 1.000 ± 0.000 | 0.966 ± 0.008 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| 100 | 0.10 | 200 ± 0 | 0.358 ± 0.175 | 26.5 ± 12.4 | 49.4 ± 18.3 | 0.038 ± 0.062 | 0.238 ± 0.251 | 0.367 ± 0.170 | 0.000 ± 0.000 | 47.368 ± 36.574 | 0.000 ± 0.000 |
| 100 | 0.30 | 200 ± 0 | 0.228 ± 0.119 | 34.0 ± 12.5 | 60.8 ± 35.0 | 0.003 ± 0.006 | 0.119 ± 0.149 | 0.237 ± 0.119 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| 100 | 0.50 | 200 ± 0 | 0.162 ± 0.098 | 45.2 ± 24.8 | 68.3 ± 34.6 | 0.000 ± 0.000 | 0.095 ± 0.109 | 0.167 ± 0.101 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| 500 | 0.10 | 200 ± 0 | 0.287 ± 0.143 | 29.3 ± 8.3 | 60.6 ± 30.2 | 0.000 ± 0.000 | 0.190 ± 0.149 | 0.294 ± 0.144 | 0.000 ± 0.000 | 12.667 ± 9.781 | 0.000 ± 0.000 |
| 500 | 0.30 | 200 ± 0 | 0.193 ± 0.095 | 37.2 ± 10.9 | 67.9 ± 29.8 | 0.000 ± 0.000 | 0.119 ± 0.149 | 0.199 ± 0.097 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| 500 | 0.50 | 200 ± 0 | 0.153 ± 0.105 | 48.3 ± 23.9 | 81.3 ± 25.9 | 0.000 ± 0.000 | 0.071 ± 0.071 | 0.159 ± 0.110 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| 2000 | 0.10 | 200 ± 0 | 0.288 ± 0.132 | 28.0 ± 12.5 | 58.3 ± 32.2 | 0.003 ± 0.006 | 0.214 ± 0.189 | 0.294 ± 0.128 | 0.000 ± 0.000 | 3.381 ± 2.610 | 0.000 ± 0.000 |
| 2000 | 0.30 | 200 ± 0 | 0.223 ± 0.113 | 34.8 ± 12.0 | 62.3 ± 33.7 | 0.000 ± 0.000 | 0.095 ± 0.109 | 0.233 ± 0.115 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| 2000 | 0.50 | 200 ± 0 | 0.165 ± 0.102 | 47.5 ± 22.8 | 80.1 ± 25.7 | 0.000 ± 0.000 | 0.095 ± 0.109 | 0.170 ± 0.105 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |

#### SD-w16
| H | P ≥ | episodes | detected | median lat | p90 lat | within 10 | in-sight det | fog det | anticipated | FA in history /10k | control fired |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 0.10 | 200 ± 0 | 1.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 | 0.000 ± 0.000 | — | — |
| 0 | 0.30 | 200 ± 0 | 0.998 ± 0.003 | 0.0 ± 0.0 | 0.1 ± 0.2 | 0.997 ± 0.006 | 1.000 ± 0.000 | 0.998 ± 0.003 | 0.000 ± 0.000 | — | — |
| 0 | 0.50 | 200 ± 0 | 0.722 ± 0.048 | 11.0 ± 1.0 | 29.3 ± 5.5 | 0.320 ± 0.054 | 0.643 ± 0.189 | 0.728 ± 0.056 | 0.000 ± 0.000 | — | — |
| 0 (recipient self block) | 0.10 | 200 ± 0 | 1.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 1.000 ± 0.000 |
| 0 (recipient self block) | 0.30 | 200 ± 0 | 0.995 ± 0.009 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.992 ± 0.014 | 1.000 ± 0.000 | 0.995 ± 0.009 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.958 ± 0.064 |
| 0 (recipient self block) | 0.50 | 200 ± 0 | 0.707 ± 0.068 | 11.0 ± 1.0 | 27.9 ± 2.5 | 0.318 ± 0.033 | 0.619 ± 0.149 | 0.713 ± 0.075 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.002 ± 0.003 |
| 100 | 0.10 | 200 ± 0 | 0.275 ± 0.097 | 36.8 ± 4.6 | 82.4 ± 41.4 | 0.025 ± 0.005 | 0.167 ± 0.149 | 0.283 ± 0.100 | 0.000 ± 0.000 | 69.169 ± 1.186 | 0.007 ± 0.008 |
| 100 | 0.30 | 200 ± 0 | 0.193 ± 0.068 | 41.3 ± 2.8 | 95.9 ± 49.2 | 0.013 ± 0.003 | 0.119 ± 0.109 | 0.199 ± 0.069 | 0.000 ± 0.000 | 67.571 ± 1.046 | 0.000 ± 0.000 |
| 100 | 0.50 | 200 ± 0 | 0.137 ± 0.025 | 51.2 ± 2.9 | 108.0 ± 50.9 | 0.008 ± 0.008 | 0.048 ± 0.041 | 0.143 ± 0.025 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| 500 | 0.10 | 200 ± 0 | 0.282 ± 0.108 | 33.3 ± 3.3 | 83.7 ± 42.9 | 0.037 ± 0.010 | 0.167 ± 0.149 | 0.290 ± 0.111 | 0.000 ± 0.000 | 18.925 ± 0.470 | 0.002 ± 0.003 |
| 500 | 0.30 | 200 ± 0 | 0.195 ± 0.062 | 33.3 ± 3.8 | 93.7 ± 45.0 | 0.033 ± 0.013 | 0.071 ± 0.071 | 0.204 ± 0.063 | 0.000 ± 0.000 | 18.314 ± 0.660 | 0.000 ± 0.000 |
| 500 | 0.50 | 200 ± 0 | 0.158 ± 0.041 | 42.2 ± 2.3 | 103.4 ± 50.6 | 0.013 ± 0.023 | 0.071 ± 0.071 | 0.165 ± 0.040 | 0.000 ± 0.000 | 0.092 ± 0.159 | 0.000 ± 0.000 |
| 2000 | 0.10 | 200 ± 0 | 0.287 ± 0.105 | 35.0 ± 6.6 | 81.5 ± 32.1 | 0.028 ± 0.010 | 0.167 ± 0.149 | 0.296 ± 0.110 | 0.000 ± 0.000 | 5.116 ± 0.180 | 0.007 ± 0.012 |
| 2000 | 0.30 | 200 ± 0 | 0.200 ± 0.066 | 38.2 ± 9.8 | 93.1 ± 40.6 | 0.013 ± 0.013 | 0.119 ± 0.109 | 0.206 ± 0.066 | 0.000 ± 0.000 | 4.888 ± 0.176 | 0.000 ± 0.000 |
| 2000 | 0.50 | 200 ± 0 | 0.158 ± 0.036 | 43.2 ± 10.2 | 96.7 ± 41.9 | 0.005 ± 0.009 | 0.095 ± 0.082 | 0.163 ± 0.037 | 0.000 ± 0.000 | 0.024 ± 0.042 | 0.000 ± 0.000 |

P4 (NF+p at 0.10): detected-fraction range over H 0.0717 vs mean seed SD 0.1501 → True; median-latency range 2.83 vs mean seed SD 11.06 → True; met: True
SD width 16, the same arithmetic: detected range 0.0117 vs 0.1031 → True; latency range 3.50 vs 4.84 → True

### R7d (c) small burn-ins and the warm start

#### P: plain (zero state) at B ∈ [0, 2, 5, 10]; warm (h_0 = h̄) at B = 0
| start | B | P ≥ | blind | reset det | reset med lat | mw-sight det | mw-fog det | FA /10k | FA len | first-tick runs | FA at boundary | grave slices fired in 100 | clean slices fired in 100 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| plain | 0 | 0.10 | 0.000 ± 0.000 | 0.995 ± 0.009 | 0.3 ± 0.6 | 0.900 ± 0.050 | 0.956 ± 0.053 | 1.607 ± 0.805 | 1.3 ± 0.6 | 614.0 ± 322.2 | 614.0 ± 322.2 | 0.995 ± 0.009 | 0.767 ± 0.403 |
| plain | 0 | 0.30 | 0.000 ± 0.000 | 0.970 ± 0.005 | 1.0 ± 0.0 | 0.767 ± 0.029 | 0.936 ± 0.034 | 0.439 ± 0.196 | 1.0 ± 0.0 | 148.7 ± 75.1 | 148.7 ± 75.1 | 0.982 ± 0.006 | 0.186 ± 0.094 |
| plain | 0 | 0.50 | 0.000 ± 0.000 | 0.965 ± 0.013 | 1.0 ± 0.0 | 0.650 ± 0.050 | 0.877 ± 0.022 | 0.198 ± 0.208 | 1.3 ± 0.6 | 53.7 ± 82.0 | 53.7 ± 82.0 | 0.978 ± 0.006 | 0.067 ± 0.102 |
| plain | 2 | 0.10 | 0.001 ± 0.000 | 0.980 ± 0.005 | 2.0 ± 0.0 | 0.900 ± 0.050 | 0.956 ± 0.053 | 0.136 ± 0.063 | 2.0 ± 1.7 | 0.0 ± 0.0 | 25.3 ± 25.5 | 0.995 ± 0.009 | 0.767 ± 0.403 |
| plain | 2 | 0.30 | 0.001 ± 0.000 | 0.968 ± 0.006 | 2.0 ± 0.0 | 0.767 ± 0.029 | 0.936 ± 0.034 | 0.070 ± 0.011 | 3.0 ± 1.0 | 0.0 ± 0.0 | 1.0 ± 1.7 | 0.982 ± 0.006 | 0.186 ± 0.094 |
| plain | 2 | 0.50 | 0.001 ± 0.000 | 0.963 ± 0.013 | 2.0 ± 0.0 | 0.650 ± 0.050 | 0.877 ± 0.022 | 0.064 ± 0.008 | 3.2 ± 1.6 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.978 ± 0.006 | 0.067 ± 0.102 |
| plain | 5 | 0.10 | 0.001 ± 0.000 | 0.960 ± 0.005 | 5.0 ± 0.0 | 0.900 ± 0.050 | 0.956 ± 0.053 | 0.073 ± 0.001 | 4.0 ± 1.0 | 0.0 ± 0.0 | 0.7 ± 1.2 | 0.995 ± 0.009 | 0.767 ± 0.403 |
| plain | 5 | 0.30 | 0.001 ± 0.000 | 0.947 ± 0.003 | 5.0 ± 0.0 | 0.767 ± 0.029 | 0.936 ± 0.034 | 0.069 ± 0.010 | 3.0 ± 1.0 | 0.0 ± 0.0 | 0.7 ± 0.6 | 0.982 ± 0.006 | 0.186 ± 0.094 |
| plain | 5 | 0.50 | 0.001 ± 0.000 | 0.945 ± 0.000 | 5.0 ± 0.0 | 0.650 ± 0.050 | 0.877 ± 0.022 | 0.066 ± 0.008 | 3.3 ± 1.5 | 0.0 ± 0.0 | 0.7 ± 0.6 | 0.978 ± 0.006 | 0.067 ± 0.102 |
| plain | 10 | 0.10 | 0.003 ± 0.000 | 0.798 ± 0.008 | 10.0 ± 0.0 | 0.900 ± 0.050 | 0.956 ± 0.053 | 0.072 ± 0.004 | 4.3 ± 0.6 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.995 ± 0.009 | 0.767 ± 0.403 |
| plain | 10 | 0.30 | 0.003 ± 0.000 | 0.787 ± 0.003 | 10.0 ± 0.0 | 0.767 ± 0.029 | 0.936 ± 0.034 | 0.077 ± 0.015 | 4.0 ± 0.0 | 0.0 ± 0.0 | 3.7 ± 2.3 | 0.982 ± 0.006 | 0.186 ± 0.094 |
| plain | 10 | 0.50 | 0.003 ± 0.000 | 0.783 ± 0.003 | 10.0 ± 0.0 | 0.650 ± 0.050 | 0.877 ± 0.022 | 0.082 ± 0.012 | 4.0 ± 2.6 | 0.0 ± 0.0 | 7.0 ± 1.7 | 0.978 ± 0.006 | 0.067 ± 0.102 |
| warm | 0 | 0.10 | 0.000 ± 0.000 | 0.592 ± 0.066 | 14.7 ± 2.1 | 0.350 ± 0.180 | 0.765 ± 0.078 | 0.078 ± 0.028 | 6.3 ± 4.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.838 ± 0.050 | 0.000 ± 0.000 |
| warm | 0 | 0.30 | 0.000 ± 0.000 | 0.413 ± 0.056 | 21.8 ± 1.6 | 0.250 ± 0.132 | 0.451 ± 0.111 | 0.056 ± 0.020 | 4.7 ± 3.2 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.605 ± 0.073 | 0.000 ± 0.000 |
| warm | 0 | 0.50 | 0.000 ± 0.000 | 0.295 ± 0.083 | 26.3 ± 3.1 | 0.217 ± 0.126 | 0.275 ± 0.114 | 0.022 ± 0.012 | 3.7 ± 1.5 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.423 ± 0.123 | 0.000 ± 0.000 |

#### LWG: plain (zero state) at B ∈ [0, 2, 5, 10]; warm (h_0 = h̄) at B = 0
| start | B | P ≥ | blind | reset det | reset med lat | mw-sight det | mw-fog det | FA /10k | FA len | first-tick runs | FA at boundary | grave slices fired in 100 | clean slices fired in 100 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| plain | 0 | 0.10 | 0.000 ± 0.000 | 1.000 ± 0.000 | 0.0 ± 0.0 | 0.955 ± 0.079 | 0.949 ± 0.044 | 0.795 ± 0.185 | 4.3 ± 3.2 | 145.0 ± 34.0 | 145.0 ± 34.0 | 1.000 ± 0.000 | 0.885 ± 0.198 |
| plain | 0 | 0.30 | 0.000 ± 0.000 | 0.988 ± 0.021 | 0.3 ± 0.6 | 0.788 ± 0.026 | 0.859 ± 0.038 | 0.562 ± 0.141 | 5.7 ± 2.1 | 62.7 ± 51.0 | 62.7 ± 51.0 | 0.989 ± 0.018 | 0.531 ± 0.097 |
| plain | 0 | 0.50 | 0.000 ± 0.000 | 0.956 ± 0.016 | 0.7 ± 0.6 | 0.606 ± 0.139 | 0.701 ± 0.053 | 0.477 ± 0.075 | 4.7 ± 0.6 | 19.7 ± 15.2 | 19.7 ± 15.2 | 0.959 ± 0.016 | 0.412 ± 0.025 |
| plain | 2 | 0.10 | 0.000 ± 0.000 | 0.997 ± 0.003 | 2.0 ± 0.0 | 0.955 ± 0.079 | 0.949 ± 0.044 | 0.538 ± 0.108 | 10.0 ± 3.0 | 0.0 ± 0.0 | 73.0 ± 2.6 | 1.000 ± 0.000 | 0.885 ± 0.198 |
| plain | 2 | 0.30 | 0.000 ± 0.000 | 0.968 ± 0.013 | 2.0 ± 0.0 | 0.788 ± 0.026 | 0.859 ± 0.038 | 0.482 ± 0.070 | 6.0 ± 1.0 | 0.0 ± 0.0 | 70.7 ± 3.2 | 0.989 ± 0.018 | 0.531 ± 0.097 |
| plain | 2 | 0.50 | 0.000 ± 0.000 | 0.932 ± 0.024 | 2.0 ± 0.0 | 0.606 ± 0.139 | 0.701 ± 0.053 | 0.440 ± 0.059 | 4.5 ± 0.9 | 0.0 ± 0.0 | 63.3 ± 4.0 | 0.959 ± 0.016 | 0.412 ± 0.025 |
| plain | 5 | 0.10 | 0.001 ± 0.000 | 0.867 ± 0.005 | 5.0 ± 0.0 | 0.955 ± 0.079 | 0.949 ± 0.044 | 0.521 ± 0.098 | 8.3 ± 2.5 | 0.0 ± 0.0 | 70.7 ± 1.2 | 1.000 ± 0.000 | 0.885 ± 0.198 |
| plain | 5 | 0.30 | 0.001 ± 0.000 | 0.837 ± 0.018 | 5.0 ± 0.0 | 0.788 ± 0.026 | 0.850 ± 0.045 | 0.430 ± 0.062 | 4.7 ± 1.2 | 0.0 ± 0.0 | 58.3 ± 2.3 | 0.989 ± 0.018 | 0.531 ± 0.097 |
| plain | 5 | 0.50 | 0.001 ± 0.000 | 0.793 ± 0.043 | 5.0 ± 0.0 | 0.606 ± 0.139 | 0.684 ± 0.082 | 0.379 ± 0.047 | 3.7 ± 1.2 | 0.0 ± 0.0 | 49.7 ± 2.1 | 0.959 ± 0.016 | 0.412 ± 0.025 |
| plain | 10 | 0.10 | 0.001 ± 0.000 | 0.750 ± 0.005 | 10.0 ± 0.0 | 0.864 ± 0.079 | 0.872 ± 0.044 | 0.577 ± 0.064 | 8.2 ± 2.8 | 0.0 ± 0.0 | 90.3 ± 6.5 | 1.000 ± 0.000 | 0.885 ± 0.198 |
| plain | 10 | 0.30 | 0.001 ± 0.000 | 0.716 ± 0.024 | 10.0 ± 0.0 | 0.742 ± 0.026 | 0.782 ± 0.046 | 0.406 ± 0.036 | 7.0 ± 1.7 | 0.0 ± 0.0 | 55.3 ± 12.0 | 0.989 ± 0.018 | 0.531 ± 0.097 |
| plain | 10 | 0.50 | 0.001 ± 0.000 | 0.665 ± 0.044 | 10.0 ± 0.0 | 0.561 ± 0.139 | 0.624 ± 0.063 | 0.324 ± 0.030 | 5.3 ± 1.5 | 0.0 ± 0.0 | 40.3 ± 10.3 | 0.959 ± 0.016 | 0.412 ± 0.025 |
| warm | 0 | 0.10 | 0.000 ± 0.000 | 0.287 ± 0.083 | 16.8 ± 3.2 | 0.182 ± 0.164 | 0.286 ± 0.211 | 0.149 ± 0.095 | 5.3 ± 2.5 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.386 ± 0.203 | 0.019 ± 0.000 |
| warm | 0 | 0.30 | 0.000 ± 0.000 | 0.165 ± 0.065 | 27.0 ± 3.8 | 0.091 ± 0.079 | 0.162 ± 0.149 | 0.048 ± 0.064 | 4.0 ± 1.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.197 ± 0.160 | 0.002 ± 0.004 |
| warm | 0 | 0.50 | 0.000 ± 0.000 | 0.105 ± 0.056 | 37.5 ± 7.4 | 0.045 ± 0.079 | 0.094 ± 0.131 | 0.017 ± 0.026 | 4.5 ± 2.1 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.121 ± 0.108 | 0.000 ± 0.000 |

P5 (P, B = 5, 0.10): FA 0.073 per 10k (bar ≤ 0.2), reset det 0.960 (bar ≥ 0.9) → True; warm at B = 0: FA 0.078, reset det 0.592 → at least as good: False; met: False

### R7d (d) the self-block swap on group P's 200 grave-start slices (800,000 observer-ticks)
| P ≥ | input | reset det | reset med lat | mw-sight det | mw-fog det | FA /10k | first-tick runs | grave slices fired in 100 | clean slices fired in 100 |
|---|---|---|---|---|---|---|---|---|---|
| 0.10 | unswapped | 0.995 ± 0.009 | 0.3 ± 0.6 | 0.900 ± 0.050 | 0.956 ± 0.053 | 0.342 ± 0.047 | 0.0 ± 0.0 | 0.995 ± 0.009 | — |
| 0.10 | swapped | 0.992 ± 0.014 | 0.3 ± 0.6 | 0.883 ± 0.076 | 0.951 ± 0.034 | 0.308 ± 0.051 | 0.0 ± 0.0 | 0.995 ± 0.009 | — |
| 0.30 | unswapped | 0.970 ± 0.005 | 1.0 ± 0.0 | 0.767 ± 0.029 | 0.936 ± 0.034 | 0.337 ± 0.045 | 0.0 ± 0.0 | 0.982 ± 0.006 | — |
| 0.30 | swapped | 0.970 ± 0.005 | 1.0 ± 0.0 | 0.733 ± 0.076 | 0.931 ± 0.042 | 0.379 ± 0.120 | 0.0 ± 0.0 | 0.982 ± 0.008 | — |
| 0.50 | unswapped | 0.965 ± 0.013 | 1.0 ± 0.0 | 0.650 ± 0.050 | 0.877 ± 0.022 | 0.321 ± 0.040 | 0.0 ± 0.0 | 0.978 ± 0.006 | — |
| 0.50 | swapped | 0.970 ± 0.005 | 1.0 ± 0.0 | 0.550 ± 0.087 | 0.882 ± 0.000 | 0.342 ± 0.080 | 0.0 ± 0.0 | 0.977 ± 0.008 | — |
mean P(grave) on grave ticks: unswapped 0.690 ± 0.009, swapped 0.689 ± 0.008; on common ticks: 0.0011 ± 0.0001 / 0.0012 ± 0.0001
P8 (at 0.10): mid-world in-sight Δ -0.0167 vs SD 0.0500 → True; fog Δ -0.0049 vs SD 0.0530 → True; met: True

### R7d (f) post-read: where grave sits in the fitted worlds (per world × friend, every set)
| role | worlds | grave ticks | max tick offset | ≤ 100 | ≤ 300 | ≤ 500 | ≤ 1000 | onsets | max onset offset | onsets after 100 |
|---|---|---|---|---|---|---|---|---|---|---|
| train | 74 | 6,301 | 322 | 5,641 | 6,279 | 6,301 | 6,301 | 182 | 171 | 1 |
| val | 17 | 1,960 | 601 | 1,204 | 1,659 | 1,859 | 1,960 | 42 | 93 | 0 |
| eval | 69 | 6,778 | 779 | 4,655 | 5,722 | 6,243 | 6,778 | 146 | 90 | 0 |

### R7d expectations (this thread's, not scored predictions)
junction control fired at 0.10 per H: H=100 0.000, H=500 0.000, H=2000 0.000 (bar < 0.05) → holds True
first-tick runs on P at 0.10: plain 614.0, warm 0.0, fraction left 0.000 (bar ≤ 0.1) → holds True
swap's reset-detection delta at 0.10: -0.0033 (bar < 0.05) → holds True

Column legend for the splice: "episodes" the 200 donor episodes;
"detected" the fraction whose P(grave) reaches the threshold inside the
donor segment (for H = 0, inside the episode in its own slice); latency
from the junction (from the onset at H = 0); "in-sight det" / "fog det"
split the 200 by the donor's in-sight bit at onset (14 / 186);
"anticipated" over the threshold at the junction and at the tick before
it; "FA in history /10k" the over-threshold runs holding no grave tick
over the spliced index (the recipient's first H ticks, which hold the
start-up transient of §Addendum 3, per 10,000 ticks of an index that is
H + the episode length per slice — not a mid-world false-alarm rate);
"control fired" the fraction of the 200 junction controls whose alarm
reaches the threshold inside the control segment (for H = 0 with the
recipient's self block, the control runs from the zero state, so its
firing is the start-up transient on clean rows). For the burn-in and
swap tables the columns are §Addendum 3's (blind fraction, reset and
re-entry detection, all-runs false alarms per 10,000 and median run
length, runs beginning at the slice's first tick, runs beginning at
offset B, the start-up split); "warm" rows run from h̄ at B = 0. The
fitted-worlds table counts per world × friend over every set (L, W, G,
P1–P5) in the role: grave ticks by offset from the world start and
grave episodes by onset offset. Two structural zeros and one constant:
"anticipated" is 0 on every H = 0 row (a reset episode has no tick
before its onset inside the slice); the start-up split in the burn-in
tables is read on the unmasked signal, so its two columns do not change
with B; and the H = 0 rows print no control and no history false-alarm
rate (the committed signal in the donor's own slice has neither).

### Limitations

- The splice junction is a jump into a covered friend's grave, not a
  crossing: the donor's rows are the first ticks of its own world
  (scene age, spatial group and answers-me are the donor observer's),
  set beside a recipient self block from another world. The read
  licenses the dependence of the response on the state's history for
  a covered grave signature as recorded; it says nothing about a slow
  crossing from below, which no set on disk contains.
- 14 of the 200 donors are in sight at onset; every in-sight cell of
  the splice rests on 14 episodes (the burn-in and swap tables' mid-world
  in-sight cells on group P rest on 20).
- h̄ is the mean state over L's clean slices from tick 1,000, per seed:
  one warm start, not a search over them. A warm start is a change to
  the consumer's state at the world's start; the policy's input is
  untouched.
- The fitted-worlds table is a fact about the data the head and the
  probe were fitted on (its train and val rows; the eval row is the
  evaluation worlds beside them), per world × friend; the reads above do not
  measure whether the collapse after a clean history is learned from
  it. That is a question for a head fitted on worlds that hold grave
  after a long clean history, which no set on disk is.
- The self-block swap separates the self block from the state only at
  the zero state (read (d)) and at H = 0 (the post-read splice row); a
  swap under a long history was not read.

## Addendum 5 2026-10-26: the knee — the §Addendum 4 splice at 1 … 50 clean ticks (owner, "Run the knee read now")

Owner-requested, 2026-10-26, on the walkthrough of the outstanding items
after §Addendum 4's report ("Run the knee read now"; DECLARATION
§Addendum 5, committed before the read). R8d: `history_read`'s splice
unchanged — the same 200 covered reset-grave donors of group P (the
friend's 58-cell rows over the episode, 14 in sight at onset) onto the
same 60 clean L recipients, the recipient's self block continuing from
the junction, the head from the zero state, the junction control
(default-start rows of the same length) beside — at H ∈ {1, 2, 5, 10,
20, 50}, NF-h24+p seeds 1–3 and SD width 16 seeds 1–3, every table at
0.10 / 0.30 / 0.50; H = 100 re-run and equal to the committed
§Addendum 4 rows per seed and threshold (asserted by the reader). The
knee as declared: the first H at which the seed-mean detected fraction
at 0.10 is at or under the midpoint between the committed H = 0 reset
detection and the committed plateau (the mean of H = 500 and 2,000). 0
new cat-ticks; no weight touched. Reader `knee_read.py`, 8 s.

### Headline

The fall is gradual, not a step, and most of it is over by 20 ticks.
On NF-h24+p at 0.10 the same covered grave rows are detected in 0.978 ±
0.003 of episodes after 1 clean tick of history, 0.970 ± 0.009 after 2,
0.852 ± 0.038 after 5, 0.658 ± 0.096 after 10, 0.537 ± 0.063 after 20
and 0.362 ± 0.070 after 50, against the committed 0.995 at a world's
start and 0.358 / 0.287 / 0.288 at 100 / 500 / 2,000; the junction
control fires in 0.010 ± 0.017 of junctions at H = 1 and in 0.000 from
H = 2 on. By the declared midpoint (0.641) the knee is at H = 20
(0.537), with H = 10 just above it (0.658). Median latency from the
junction grows with the history as detection falls: 1.0 / 1.3 / 3.7 /
11.3 / 16.3 / 24.7 ticks at H = 1 … 50 against 26.5 at 100. At 0.30 and
0.50 the curve sits lower throughout (H = 10: 0.482 / 0.378; H = 50:
0.250 / 0.185). SD width 16 at 0.10 sits lower on the seed means at every
H ≥ 5 (0.762 ± 0.185 at H = 5, 0.487 ± 0.332 at 10, 0.403 ± 0.306 at
20, 0.297 ± 0.165 at 50; knee at H = 10), with one of its three seeds
above every NF seed at H = 10 and 20; and its small-H rows carry its
own start-up transient: its control fires in 1.000 / 0.985 of junctions
at H = 1 / 2, in 0.122 ± 0.211 at H = 5 (0.000 / 0.000 / 0.365 per
seed), and is under 0.05 only from H = 10. Read against decision 3 as ruled
(0.10 with a 2-tick burn-in): on this splice, 2 clean ticks of history
cost 2.5 points of detection (0.995 → 0.970), and the seed-mean
detection is 0.852 at 5 ticks; the burn-in sits well inside
the window in which the head sees a covered grave.

### Prediction scored (the Professor's P9, verbatim from the note's §"Registered predictions, added 2026-10-26"; operationalised in DECLARATION §Addendum 5)

- **P9** ("On the splice at 0.10, NF-h24+p, seed-mean detection at H =
  10 is below 0.70, and detection at H = 20 is within one seed SD of H
  = 100's 0.358.") — **not met as operationalised**: clause (i) holds
  (0.658 at H = 10, under 0.70); clause (ii) does not (0.537 at H = 20
  against the committed 0.358 ± 0.175 at H = 100, |Δ| 0.178, over the
  SD by 0.003). The miss is at the margin of the bar and the direction
  is the substantive point: at 20 ticks the head still sees about half
  of what it sees at the start, and the fall to the plateau continues
  to 50.

This thread's expectation, not a prediction: the junction control at
0.10 fires in under 0.05 of junctions at every H ≥ 5 — holds (0.000 at
5 / 10 / 20 / 50 / 100).

### R8d tables (the reader's markdown, verbatim; `phase1d-knee.json` holds the per-seed cells)

reproduces the committed P(grave) on the first P evaluation world to: s1 0.0e+00, s2 0.0e+00, s3 0.0e+00
H = 100 re-run and equal to the committed rows per seed and threshold (asserted); 200 donors, 60 recipients

#### NF-h24+p
| H | P ≥ | episodes | detected | median lat | p90 lat | within 10 | in-sight det | fog det | FA in history /10k | control fired |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.10 | 200 ± 0 | 0.978 ± 0.003 | 1.0 ± 0.0 | 2.7 ± 1.2 | 0.968 ± 0.016 | 1.000 ± 0.000 | 0.977 ± 0.003 | 136.112 ± 104.075 | 0.010 ± 0.017 |
| 1 | 0.30 | 200 ± 0 | 0.960 ± 0.010 | 1.3 ± 0.6 | 4.3 ± 2.3 | 0.933 ± 0.020 | 0.976 ± 0.041 | 0.959 ± 0.008 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| 1 | 0.50 | 200 ± 0 | 0.913 ± 0.038 | 2.0 ± 1.0 | 6.6 ± 4.6 | 0.860 ± 0.083 | 0.905 ± 0.109 | 0.914 ± 0.034 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| 2 | 0.10 | 200 ± 0 | 0.970 ± 0.009 | 1.3 ± 0.6 | 4.0 ± 1.7 | 0.948 ± 0.018 | 0.976 ± 0.041 | 0.970 ± 0.006 | 144.037 ± 111.214 | 0.000 ± 0.000 |
| 2 | 0.30 | 200 ± 0 | 0.897 ± 0.032 | 2.3 ± 1.5 | 7.3 ± 4.2 | 0.822 ± 0.088 | 0.810 ± 0.082 | 0.903 ± 0.028 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| 2 | 0.50 | 200 ± 0 | 0.820 ± 0.083 | 3.8 ± 2.4 | 15.2 ± 5.8 | 0.660 ± 0.165 | 0.667 ± 0.109 | 0.832 ± 0.081 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| 5 | 0.10 | 200 ± 0 | 0.852 ± 0.038 | 3.7 ± 1.5 | 13.2 ± 1.9 | 0.695 ± 0.082 | 0.714 ± 0.124 | 0.862 ± 0.036 | 135.568 ± 104.674 | 0.000 ± 0.000 |
| 5 | 0.30 | 200 ± 0 | 0.653 ± 0.070 | 11.3 ± 2.1 | 26.1 ± 2.0 | 0.302 ± 0.103 | 0.476 ± 0.149 | 0.667 ± 0.067 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| 5 | 0.50 | 200 ± 0 | 0.520 ± 0.100 | 16.7 ± 3.5 | 36.0 ± 3.0 | 0.127 ± 0.095 | 0.405 ± 0.082 | 0.529 ± 0.102 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| 10 | 0.10 | 200 ± 0 | 0.658 ± 0.096 | 11.3 ± 3.1 | 24.4 ± 5.6 | 0.303 ± 0.165 | 0.476 ± 0.082 | 0.672 ± 0.099 | 123.468 ± 95.332 | 0.000 ± 0.000 |
| 10 | 0.30 | 200 ± 0 | 0.482 ± 0.104 | 17.3 ± 4.7 | 37.5 ± 4.0 | 0.107 ± 0.106 | 0.333 ± 0.041 | 0.493 ± 0.109 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| 10 | 0.50 | 200 ± 0 | 0.378 ± 0.101 | 22.3 ± 3.8 | 47.3 ± 4.2 | 0.033 ± 0.058 | 0.286 ± 0.000 | 0.385 ± 0.108 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| 20 | 0.10 | 200 ± 0 | 0.537 ± 0.063 | 16.3 ± 7.4 | 34.3 ± 3.6 | 0.163 ± 0.202 | 0.357 ± 0.071 | 0.550 ± 0.070 | 104.766 ± 80.892 | 0.000 ± 0.000 |
| 20 | 0.30 | 200 ± 0 | 0.380 ± 0.105 | 22.7 ± 9.3 | 45.5 ± 4.1 | 0.072 ± 0.124 | 0.286 ± 0.000 | 0.387 ± 0.113 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| 20 | 0.50 | 200 ± 0 | 0.262 ± 0.078 | 30.7 ± 10.6 | 51.0 ± 6.2 | 0.025 ± 0.043 | 0.167 ± 0.082 | 0.269 ± 0.083 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| 50 | 0.10 | 200 ± 0 | 0.362 ± 0.070 | 24.7 ± 5.9 | 49.6 ± 17.1 | 0.010 ± 0.009 | 0.238 ± 0.109 | 0.371 ± 0.067 | 72.034 ± 55.619 | 0.000 ± 0.000 |
| 50 | 0.30 | 200 ± 0 | 0.250 ± 0.078 | 32.8 ± 8.5 | 62.3 ± 31.1 | 0.000 ± 0.000 | 0.143 ± 0.071 | 0.258 ± 0.084 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| 50 | 0.50 | 200 ± 0 | 0.185 ± 0.077 | 38.8 ± 9.3 | 69.7 ± 31.0 | 0.000 ± 0.000 | 0.095 ± 0.109 | 0.192 ± 0.079 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| 100 (pin) | 0.10 | 200 ± 0 | 0.358 ± 0.175 | 26.5 ± 12.4 | 49.4 ± 18.3 | 0.038 ± 0.062 | 0.238 ± 0.251 | 0.367 ± 0.170 | 47.368 ± 36.574 | 0.000 ± 0.000 |
| 100 (pin) | 0.30 | 200 ± 0 | 0.228 ± 0.119 | 34.0 ± 12.5 | 60.8 ± 35.0 | 0.003 ± 0.006 | 0.119 ± 0.149 | 0.237 ± 0.119 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| 100 (pin) | 0.50 | 200 ± 0 | 0.162 ± 0.098 | 45.2 ± 24.8 | 68.3 ± 34.6 | 0.000 ± 0.000 | 0.095 ± 0.109 | 0.167 ± 0.101 | 0.000 ± 0.000 | 0.000 ± 0.000 |
committed §Addendum 4 rows at 0.10, detected: H=0 0.995 ± 0.009, H=0r 0.995 ± 0.009, H=100 0.358 ± 0.175, H=500 0.287 ± 0.143, H=2000 0.288 ± 0.132
knee at 0.10: top (H = 0 reset) 0.995, plateau (500 / 2,000) 0.287, midpoint 0.641 → first H at or under it: 20 (detected 0.537); control under 0.05 from H = 1

#### SD-w16
| H | P ≥ | episodes | detected | median lat | p90 lat | within 10 | in-sight det | fog det | FA in history /10k | control fired |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.10 | 200 ± 0 | 1.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 | 0.000 ± 0.000 | 1.000 ± 0.000 |
| 1 | 0.30 | 200 ± 0 | 0.925 ± 0.005 | 1.7 ± 2.9 | 9.7 ± 2.1 | 0.855 ± 0.040 | 0.952 ± 0.082 | 0.923 ± 0.008 | 108.110 ± 22.059 | 0.410 ± 0.113 |
| 1 | 0.50 | 200 ± 0 | 0.655 ± 0.100 | 14.5 ± 2.6 | 30.4 ± 5.2 | 0.207 ± 0.033 | 0.524 ± 0.109 | 0.665 ± 0.109 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| 2 | 0.10 | 200 ± 0 | 0.995 ± 0.009 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.990 ± 0.017 | 1.000 ± 0.000 | 0.995 ± 0.009 | 3.124 ± 5.410 | 0.985 ± 0.026 |
| 2 | 0.30 | 200 ± 0 | 0.775 ± 0.068 | 7.7 ± 1.2 | 21.3 ± 9.8 | 0.565 ± 0.189 | 0.667 ± 0.149 | 0.783 ± 0.082 | 191.934 ± 12.422 | 0.015 ± 0.026 |
| 2 | 0.50 | 200 ± 0 | 0.582 ± 0.162 | 17.0 ± 4.4 | 42.7 ± 21.6 | 0.118 ± 0.083 | 0.452 ± 0.041 | 0.591 ± 0.171 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| 5 | 0.10 | 200 ± 0 | 0.762 ± 0.185 | 9.7 ± 7.1 | 23.5 ± 16.0 | 0.487 ± 0.406 | 0.667 ± 0.297 | 0.769 ± 0.176 | 167.581 ± 49.225 | 0.122 ± 0.211 |
| 5 | 0.30 | 200 ± 0 | 0.543 ± 0.203 | 18.7 ± 8.5 | 39.4 ± 24.6 | 0.210 ± 0.252 | 0.357 ± 0.189 | 0.557 ± 0.208 | 188.815 ± 7.921 | 0.002 ± 0.003 |
| 5 | 0.50 | 200 ± 0 | 0.438 ± 0.209 | 24.3 ± 7.6 | 52.3 ± 23.0 | 0.080 ± 0.071 | 0.286 ± 0.124 | 0.450 ± 0.220 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| 10 | 0.10 | 200 ± 0 | 0.487 ± 0.332 | 20.2 ± 14.3 | 43.0 ± 28.8 | 0.323 ± 0.422 | 0.310 ± 0.322 | 0.500 ± 0.336 | 172.260 ± 10.821 | 0.047 ± 0.081 |
| 10 | 0.30 | 200 ± 0 | 0.400 ± 0.286 | 20.7 ± 8.9 | 75.6 ± 54.6 | 0.135 ± 0.147 | 0.262 ± 0.251 | 0.410 ± 0.292 | 171.962 ± 7.214 | 0.000 ± 0.000 |
| 10 | 0.50 | 200 ± 0 | 0.340 ± 0.248 | 31.5 ± 14.0 | 81.6 ± 52.1 | 0.062 ± 0.055 | 0.190 ± 0.180 | 0.351 ± 0.255 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| 20 | 0.10 | 200 ± 0 | 0.403 ± 0.306 | 21.3 ± 10.7 | 67.9 ± 47.9 | 0.185 ± 0.225 | 0.238 ± 0.251 | 0.416 ± 0.313 | 147.430 ± 6.996 | 0.043 ± 0.075 |
| 20 | 0.30 | 200 ± 0 | 0.332 ± 0.247 | 27.3 ± 9.3 | 82.9 ± 56.8 | 0.083 ± 0.068 | 0.167 ± 0.180 | 0.344 ± 0.253 | 146.420 ± 5.319 | 0.008 ± 0.014 |
| 20 | 0.50 | 200 ± 0 | 0.262 ± 0.220 | 34.7 ± 12.0 | 100.9 ± 72.5 | 0.043 ± 0.024 | 0.119 ± 0.149 | 0.272 ± 0.226 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| 50 | 0.10 | 200 ± 0 | 0.297 ± 0.165 | 37.2 ± 11.9 | 75.7 ± 31.2 | 0.037 ± 0.020 | 0.167 ± 0.180 | 0.306 ± 0.167 | 105.186 ± 1.804 | 0.000 ± 0.000 |
| 50 | 0.30 | 200 ± 0 | 0.208 ± 0.102 | 40.7 ± 11.6 | 96.5 ± 57.7 | 0.020 ± 0.010 | 0.095 ± 0.082 | 0.217 ± 0.108 | 102.756 ± 1.591 | 0.000 ± 0.000 |
| 50 | 0.50 | 200 ± 0 | 0.153 ± 0.071 | 54.7 ± 14.0 | 107.8 ± 68.0 | 0.008 ± 0.008 | 0.024 ± 0.041 | 0.163 ± 0.073 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| 100 (pin) | 0.10 | 200 ± 0 | 0.275 ± 0.097 | 36.8 ± 4.6 | 82.4 ± 41.4 | 0.025 ± 0.005 | 0.167 ± 0.149 | 0.283 ± 0.100 | 69.169 ± 1.186 | 0.007 ± 0.008 |
| 100 (pin) | 0.30 | 200 ± 0 | 0.193 ± 0.068 | 41.3 ± 2.8 | 95.9 ± 49.2 | 0.013 ± 0.003 | 0.119 ± 0.109 | 0.199 ± 0.069 | 67.571 ± 1.046 | 0.000 ± 0.000 |
| 100 (pin) | 0.50 | 200 ± 0 | 0.137 ± 0.025 | 51.2 ± 2.9 | 108.0 ± 50.9 | 0.008 ± 0.008 | 0.048 ± 0.041 | 0.143 ± 0.025 | 0.000 ± 0.000 | 0.000 ± 0.000 |
committed §Addendum 4 rows at 0.10, detected: H=0 1.000 ± 0.000, H=0r 1.000 ± 0.000, H=100 0.275 ± 0.097, H=500 0.282 ± 0.108, H=2000 0.287 ± 0.105
knee at 0.10: top (H = 0 reset) 1.000, plateau (500 / 2,000) 0.284, midpoint 0.642 → first H at or under it: 10 (detected 0.487); control under 0.05 from H = 10

P9 (NF-h24+p at 0.10): (i) detected at H = 10 0.658 < 0.7 → True; (ii) detected at H = 20 0.537 vs committed H = 100 0.358 ± 0.175, |Δ| 0.178 → False; met: False

#### expectation (this thread's, not a scored prediction)
junction control fired at 0.10 for H ≥ 5: H=100 0.000, H=5 0.000, H=10 0.000, H=20 0.000, H=50 0.000 (bar < 0.05) → holds True

Legend: *detected*, *median lat*, *p90 lat*, *within 10*, *in-sight det*,
*fog det* as in §Addendum 4's splice tables (the episode is the donor
segment from the junction; in-sight / fog by the donor's bit at onset,
14 / 186 of 200); *FA in history /10k* counts the alarm runs that
start inside the H history ticks, per 10,000 ticks of the whole spliced
index (200 splices × (H + the donor segment): 9,204 + 200 H ticks, so
9,404 at H = 1 and 29,204 at H = 100) — for NF every such run is a
recipient start-up firing (runs at reset equal runs), and the column is
not comparable to the per-10,000 rates of §Addendum 3, whose
denominator is the full slices;
*control fired* is the fraction of the 200 junctions whose alarm fires
inside the control segment; *(pin)* marks the re-run H = 100 row, equal
to the committed one.

### Limitations

The §Addendum 4 limitation stands: the junction is a jump into a
covered friend's grave, not a crossing. At H = 1 and 2 the NF control
fires 0.010 and 0.000, so the NF rows there are detection and not the
recipient's transient; SD's rows at H = 1 and 2 are its transient
(control 1.000 / 0.985), and at H = 5 one seed's is (control 0.365 on
seed 3, 0.000 on the others), so SD's curve is read from H = 10, where
its control is under 0.05. One ladder of six H values, three seeds per
head; the seed SD at H = 10 (0.096) is a third of the fall between 5
and 20. The false-alarm column's denominator is the whole spliced index,
mostly donor-segment ticks; it is a count of recipient start-up runs
in disguise, not a rate comparable across addenda.
The knee's definition (a midpoint) is one declared convention; the
curve is the result.


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
MINIFRIEND_ARC=$PWD/$Dd VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/python3 -B $Dd/read_phase1d.py --out $Dd/phase1d-read.json --md > $Dd/phase1d-read.md   # ≈ 25 s (stdout is the markdown; the 'wrote' line goes to stderr); R1d runs inside it (filter_spread.read_all); the addendum's R3d / R4d run inside it too and the reader asserts the committed R1d / R2d blocks unchanged
MINIFRIEND_ARC=$PWD/$Dd VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/python3 -B $Dd/sweep_threshold.py --out $Dd/phase1d-sweep.json --md > $Dd/phase1d-sweep.md   # ≈ 5 s; §Addendum 2's R5d (with the post-read columns); asserts NF-h24+p's 0.20 / 0.50 group-P rows equal the committed phase1d-read.json R4d rows
MINIFRIEND_ARC=$PWD/$Dd VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/python3 -B $Dd/burnin_read.py --out $Dd/phase1d-burnin.json --md > $Dd/phase1d-burnin.md   # ≈ 10 s; §Addendum 3's R6d (NF-h24+p; full grid in the JSON, two cross-sections and the start-up split in the markdown); asserts the B = 0 cells equal the committed phase1d-sweep.json NF-h24+p cells and the B = 100 run identity
MINIFRIEND_ARC=$PWD/$Dd VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/python3 -B $Dd/history_read.py --out $Dd/phase1d-history.json --md > $Dd/phase1d-history.md   # ≈ 40 s; §Addendum 4's R7d (the frozen heads re-run on the saved observation streams: convergence on L, the splice with its control, NF+p and SD width 16, burn-ins 0 / 2 / 5 / 10 and the warm start, the self-block swap, the fitted worlds' grave offsets); asserts the re-run P(grave) equals the committed pgrave file on the first P evaluation world, H = 0 equals the sweep's reset rows at 0.10 / 0.50, SD's H = 0 equals R4d's row at 0.50, and the B = 0 cells equal the sweep's
MINIFRIEND_ARC=$PWD/$Dd VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/python3 -B $Dd/knee_read.py --out $Dd/phase1d-knee.json --md > $Dd/phase1d-knee.md   # ≈ 8 s; §Addendum 5's R8d (the §Addendum 4 splice at H ∈ {1, 2, 5, 10, 20, 50}, NF-h24+p and SD width 16); asserts the re-run P(grave) on the first P evaluation world and that the re-run H = 100 rows equal the committed phase1d-history.json rows per seed and threshold
```

Guards (plain-assert runner, Phase 1's venv): `$Dd/test_phase1d.py` 10
(t1–t10; about 30 s). Reds on record via `scripts/mutate.sh` in the
declaration's §Run order (t1–t4), §Addendum (t5–t6, and the extended
t6), §Addendum 2 (t7, and its two extensions), §Addendum 3 (t8, and
its two extensions), §Addendum 4 (t9, and its extension) and
§Addendum 5 (t10).

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

Accuracy gate (§Addendum): **PASS**, 2026-10-24, round 2 (fresh
subagent per round; both rounds regenerated the read byte-identically
and matched the counts and the 6-guard count). Round 1 FAILED on one
WEAK clause naming an F-number (SD's slow climb attributed to "F-067's
under-confident bins below 0.7", which F-067 does not say; now
§R2d(a)) and surfaced the structural fact the section had not
disclosed: 200 of the 288 episodes begin at the world's first tick
(group P's per-cat grave starts), so a crossing there is a head's
prior; the reader gained the reset / mid-world split, slice-relative
anticipation and the world-start false-alarm split (DECLARATION
post-read addition; t6 extended with its red), the declared rules
stayed scored as declared with the mid-world numbers disclosed, and
every table was rebuilt from the regenerated read. Round 2 PASS: 372
table cells, about 170 prose numbers and about 30 derived figures
matched, about 15 provenance and threshold items located, 28
characterisations supported, 4 weak outside the failing zones (the
extended t6's red unrecorded in the declaration → recorded; the
"anticipated" definition missing "at onset" → stated in full here and
in the reader's header; the headline's "half or more" unscoped →
scoped; "two thirds" for 0.69 → "over two thirds"), one rounding
(a 12.5 median printed 12), one section pointer corrected. The F-068
copy check ran as three copy-only rounds (round 1 four dropped
qualifiers and labels, round 2 PASS with three advisories, round 3
PASS after the split with five advisories applied). Raw-dir hashes
unchanged from the stamp above (no new raw; the addendum reads the
same six probe directories, 1c's SD-s{1,2,3} belief files and 1b's
NF/DR-h24 prediction files).

Accuracy gate (§Addendum 2): **PASS**, 2026-10-24, round 3 (fresh
subagent per round; every round regenerated `phase1d-sweep.json` and
`.md` byte-identically, matched the episode, sample and seed counts
and the 7-guard count; no table cell was wrong in any round). Round 1
FAILED on two mechanism claims a read-only test on the saved outputs
contradicted — the L / W / G rise named as "run splitting" (it is
world-start runs that begin at offset 1 once their first tick falls
under the threshold) and the non-grave over-threshold ticks glossed as
"anticipation" (most sit after an episode or in the start-up) — and on
an unmarked word change inside a quotation; the round also measured
that nearly every "mid-world" false-alarm run starts within a slice's
first hundred ticks, which became the second post-read addition (the
run-start columns, guard t7 extended, red at 2d7bfbff) and the
section's headline. Round 2 FAILED on an "only" clause that ignored
four false-alarm columns and on a per-seed range (0–11) filled from
the seed mean (0–22 per seed); five WEAK scopings applied. Round 3
PASS: about 512 table cells, about 150 prose numbers and about 35
derived figures matched, 14 provenance items located (the owner quote,
the expectation quotation, three reds, the pin's scope, Phase 1's
group table), 30 characterisations supported, 3 weak outside any
failing zone (applied after the verdict without a number changing:
"whose extra at the low end is the first-tick runs"; "within the 0.15
cell's own seed SD"; the run-length cost scoped to L / W / G), three
roundings of one unit, no undecidable (the "W's worlds" attribution
was measured read-only). Raw-dir hashes unchanged from the stamp above
(no new raw; the sweep reads the same six probe directories' saved
P(grave) and the symlinked world raws).

Accuracy gate (§Addendum 3): **PASS**, 2026-10-25, round 3 (fresh
subagent per round; every round regenerated `phase1d-burnin.json` and
`.md` byte-identically, matched the episode, sample, seed and slice
counts and the 8-guard count; no table cell or prose number was wrong
in any round). Round 1 FAILED on a mechanism claim a read-only test
contradicted — the 25 → 50 false-alarm rise called "one part …
unmeasured" truncation when it is the truncation case in full (now the
second post-read addition's column, red at 49137bf9) — on the clean
slices' composition (L's 60 and W's 100, not G's), on L's dimensions
and on an unscoped per-seed range; four WEAK applied. Round 2 FAILED
on one wording in expectation (3) ("moot where none is running" where
the overshoot cells are exactly ones with reset episodes still running;
rescored as not held as stated, with the full-grid counts); three WEAK
applied (the detected fraction a lower bound on episodes still running;
the curve never said "pick low"; L is lived worlds and its empty ticks
are evidence of rarity). Round 3 PASS: about 590 table cells, about
150 prose numbers and 18 derived figures matched, both full-grid
expectation claims re-derived, 9 provenance items located (the owner
quotation, three reds, Phase 1's group descriptions), 22
characterisations supported with the mechanism claims tested read-only
(the re-entries follow their slice's reset episode by 1–53 ticks; every
cut run's unmasked run overlaps a reset episode), 1 weak outside any
failing zone (applied after the verdict without a number changing:
"the whole onset-detection task"), 1 undecidable (the date and fact of
this thread's low-end recommendation, which no file records), no
rounding. Raw-dir hashes unchanged from the stamp above (no new raw;
the read uses the three NF-h24+p probe directories' saved P(grave) and
the symlinked world raws).

Accuracy gate (§Addendum 4): **PASS**, 2026-10-26, round 2 (fresh
subagent per round; both rounds regenerated `phase1d-history.json` and
`.md` byte-identically, matched the seed, threshold, history, burn-in,
sample, donor, recipient, slice and per-role world counts and the
9-guard count; no table cell or prose number was wrong in either
round). Round 1 FAILED on four provenance misses — the Professor's
P3 / P4 / P5 / P8 paraphrased inside quotation marks (now verbatim
from the note's §Q6) — and one CONTRADICTED sentence (the fitted
worlds "hold no grave beyond a world's first 322 ticks", refuted by
the validation and evaluation rows it listed; now scoped to the
training worlds, no grave after offset 322, with the validation worlds
to 601 and the evaluation worlds to 779 beside it); five WEAK applied
(the junction-control sentence scoped to H = 100 / 500 / 2,000 with
the H = 0 recipient row's 0.678 named; the reproduction check's
timing stated per seed; the 14-episode caveat scoped to the splice,
the burn-in and swap in-sight cells on 20; the fitted-worlds table's
eval row named; the drift range 0.80–0.89 as seed means), one rounding
(0.8814 printed inside 0.80–0.88), one undecidable (the note's hash
moved after receipt: the Professor appended a relay-status block; now
noted in the declaration), three advisories applied (the P3 → P4
coupling noted as not having occurred; the structural zeros and the
unmasked start-up split named in the legend). Round 2 PASS: about
1,000 table cells (the pasted block diff-empty against the fresh
markdown), about 95 prose numbers and about 15 derived figures
matched, 9 threshold claims sourced, 18 provenance items located
(the four prediction quotations character-identical to §Q6, the
owner quotation, the operationalisations, two reds, the reproduction
figure, the in-sight splits), 30 characterisations supported with the
mechanism claims tested read-only (seeds 1 and 3 at or over 0.10 at
tick 0 on every P and L / W / G slice; every L / W / G boundary run at
B = 2 already over the threshold at tick 1; the validation role
early-stops both fits; no onset in any role follows a climb), no
undecidable, no rounding. Two advisories applied after the verdict
without a number changing (a trailing cut in the owner quotation
marked with "…"; the H = 0 rows' missing history rate named in the
legend). Raw-dir hashes unchanged from the stamp above (no new raw;
the read uses the three NF-h24+p probe directories' `probe.pt` and
saved P(grave), 1b's NF-h24 `head-best.pt`, 1c's SD-s{1,2,3}
`head-best.pt` and belief files, and the symlinked world raws'
observation streams).
