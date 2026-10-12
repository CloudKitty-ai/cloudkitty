# Mini-friend doctrine: Experiments assessment of the Professor relay, plus two pre-sitting reads

Owner ask, this session, 2026-10-11: "Can you review the relayed
material from Professor, and for each recommendation: Assessment
(worth doing?) / Level of effort (implementation) / Additional
difficulties it would impose on us / Sequencing (gen 2, gen 3,
later)", then "Commit, and run the pre-sitting reads now". The relay
under review is Professor's philosophy-feedback review
(`~/ai/professor/notes/for-experiments-philosophy-feedback-review-2026-10-10.md`,
their receipt 93afbe70). Everything assessed here BANKS until her
word; this note is decision input for the Gen 2 freeze sitting, not a
ruling record. The two reads are measurement notes: no hypotheses, no
decision rules, existing raws only, nothing changed.

## The six recommendations, assessed

**1. Approach-propensity differential** (behavioral blindness;
conditional on the harness-computed best-placed feasible host; team
attendance read; proposals read via the refusal log).
Worth doing — the one real gap. The conjunction failure (accurate
mini, averted path) is uncovered: min-n fail-closed catches sample
thinning but the probe remedy certifies under forced looking, and the
welfare watch is aggregate and unattributable. Effort: medium, the
largest item here — matched-control construction, a harness-side
reimplementation of spec 059's best-placed computation, refusal-log
joining. Read 1 below settles the data question: lived rollout raws
carry everything the read needs (ground-truth needs, positions,
distress flags in the state channel; want-calls in the label
channel), so no collector change is required for a passive version.
Difficulties: grave-encounter thinness (measured below — the
observer-own-need control axis starves above mild severity); a
consequence role would need a welfare declaration with cost line and
asymmetric-stop shape. Sequencing: design pinned at the Gen 2 freeze
sitting; run DIAGNOSTIC (no stop role) in Gen 2 Phase 2, where the
host-trains/mini-frozen asymmetry switches the risk on; promote to a
consequence role in Gen 3 if the Gen 2 read validates.

**2. Gradient/decision-flow trigger beside k>1, plus the two-line
reward-provenance pre-commitment.** Worth doing and cheap: the
depth-1 imagined-reward gap is real and verified against our records
(nothing on record pins the POLICY's reward provenance). Effort: near
zero — doctrine text; her sitting time is the cost. One wording trap:
the declared correction follow-up arm feeds mini output to the policy
as INPUT FEATURES, and the trigger text must say plainly that
observation-feature consumption with ground-truth reward does not
trip it (Professor's own round-3 analysis places the attractor at
reward/decision COMPUTED FROM predictions, not at conditioning on
them) — otherwise the already-ruled follow-up arm convenes a review
nobody intended. Sequencing: rider at the Gen 2 freeze sitting;
default-closed text is cheapest before any flow architecture is
proposed. The fuller flow-sitting agenda banks for the 1.2/1.3 era.

**3. Fixed probe battery plus the certificate-scope line.** Worth
doing. The scope line costs nothing and prevents the over-claim the
probe remedy invites — Professor's wording is verbatim-able: "the
battery number licenses 'the mini is calibrated on battery B', never
'hosts are not blind to friends'". Effort: small-to-medium (battery
assembly from replay slices plus scripted probe worlds for
undersampled strata; freezing it is our standard prereg pattern).
Difficulties: battery composition is itself a blank for her to pin;
scripted probe worlds carry manufactured-seated-state cost lines per
the 2026-09-26 practice. Sequencing: Gen 2 freeze sitting — the
calibration certificate is a Phase-1/2 gate.

**4. Lived-vs-probe error gap as the shift signature.** Worth doing;
it directly answers her Phase-2 host-adaptation question, and the
divergence itself alarming is the honest signal that the policy is
steering the distribution. Effort: small — a derived comparison
between two reads that exist once item 3 does, plus a declared alarm
threshold. Difficulty: no prior to set the threshold from; the first
generation likely runs it alarm-advisory while its noise floor is
learned. Sequencing: Gen 2, with item 3.

**5. Relief-latency tail-quantile discriminator plus the resolution
rule** (alarm resolves through the outcome read; unresolvable at
min-n resolves conservatively to demotion; absent an alarm, thin
strata never auto-demote). Worth doing — this makes item 4 actionable
and the substitution-vs-abandonment distinction is correct. Effort:
small-to-medium (latency is register ground truth; per-stratum tail
quantiles are the work). The difficulty is the statistics, now
measured: read 2 below shows that at scripted collection density only
the cuddle strata power a p90 read, so a conservatively-resolving
rule over lived data alone is a demotion machine for every other
stratum — the "absent an alarm, thin strata never auto-demote" guard
is load-bearing, and the quantile and min-n have to be pinned
together against the numbers below. Sequencing: pins at the Gen 2
freeze sitting, informed by read 2.

**6. Probe-cost ordering (replay > scripted probe worlds > synthesis)
and the instrument-hierarchy/preamble text.** Worth doing, zero
controversy: the ordering matches the 2026-09-26 practice, and the
hierarchy keeps leading-indicator stops undemoted while making the
attributable outcome read primary for evidence. Effort: text only.
Sequencing: Gen 2 freeze sitting.

Net: items 2–6 are freeze-sitting material at modest cost. Item 1 is
the one real build — diagnostic in Gen 2, teeth in Gen 3. The
systemic cost is freeze-sitting scope growth plus sample-size
pressure: matched controls, tail quantiles, and per-friend min-n all
eat the same data, and the reads below say how much of it exists.

## Read 1 — grave-encounter density at scripted collection density

Question: does LIVED rollout data power a matched-control approach
read, or does it starve? Data: all 40 bc-corpus rollouts of the
fog-gen1 shakeout (scripted roster of 5, observation schema 5, 20,000
ticks each = 800,000 world-ticks; the `idx*` real dirs, deduped by
realpath). Ground truth comes from the per-tick `state.npy` channel
(global-state v1 layout, verified in-situ: positions land on the
20×20 integer grid and the distress flags equal `need >= 0.9`
everywhere, matching `distress = 90.0` in the shakeout anchor.toml).
Severity thresholds: >= 90 is the engine distress line (sourced
above); 45 and 70 are this note's read-time choices, borrowing the
numbers of the ruled semantic edges ("happiness 45/70, the 90
distress edge", gen2-sitting-rulings-2026-10-08.md §3(d)) but
applying them to NEED pressure, which that ruling does not pin —
only the 90 edge carries over with its meaning intact. "Signalling" = the kitty's own matching
want-call audible under the 30-tick digest window. Distance bands
(Manhattan) and the observer-own-need control axis (>= 0.70) are
read-time choices, not pins; the 0–4 band proxies the collector's
`vision_radius = 4`.

At the 0.45 tier everything fat-tailed is readable: eat 6.362% of
kitty-ticks, drink 3.986%, sleep 4.359%, cuddle 8.972%, with
near-band cold-observer cells at medians 3,181–15,315 per rollout,
all 40 rollouts nonzero. Play (0.022%) and bath (0.113%) are low at
every tier — the scripted experts hold them down. The table gives the
0.70 and 0.90 tiers (encounters = potential-observer pairs in the 0–4
band; "cold/hot cell" = that band split by observer own-need < / >=
0.70, per-rollout median and nonzero-rollout count; hot cells give
the pooled total, they are too thin for medians):

| stratum | % kitty-ticks | episodes | signalling % | enc 0–4 | cold cell med (nz/40) | hot cell total (nz/40) |
|---|---|---|---|---|---|---|
| eat@0.70 | 0.251 | 468 | 61.28 | 10,747 | 236.5 (40) | 287 (19) |
| eat@0.90 | 0.026 | 39 | 58.29 | 1,314 | 0.0 (19) | 16 (2) |
| drink@0.70 | 0.083 | 161 | 34.59 | 2,031 | 38.5 (30) | 63 (4) |
| drink@0.90 | 0.010 | 13 | 43.39 | 361 | 0.0 (6) | 32 (1) |
| sleep@0.70 | 0.067 | 109 | 30.96 | 1,829 | 44.5 (35) | 21 (4) |
| sleep@0.90 | 0.007 | 10 | 44.49 | 306 | 0.0 (9) | 0 (0) |
| play@0.70 | 0.000 | 2 | 84.62 | 0 | 0.0 (0) | 0 (0) |
| cuddle@0.70 | 1.007 | 1,451 | 85.54 | 87,068 | 2,124.0 (40) | 632 (23) |
| cuddle@0.90 | 0.257 | 343 | 85.63 | 22,947 | 569.0 (40) | 208 (12) |
| bath@0.70 | 0.000 | 2 | 100.0 | 36 | 0.0 (2) | 0 (0) |

play@0.90 and bath@0.90 have zero kitty-ticks above threshold. The
instrument can emit them (same channel as the rest), so zero is
evidence of absence here, not an emission gap.

Reading:

- **The grave-signalling population exists.** Above threshold,
  kitties are audibly calling the matching want 31–86% of the time
  (bath's 100% is n=2). The approach read has a subject; "signalling"
  does not need a new channel.
- **Lived data powers the differential for cuddle at every severity
  including grave** (cold cells median 569 per rollout at 0.90, all
  40 rollouts nonzero), **and for eat at moderate severity**. Drink
  and sleep are thin at 0.70 (per-rollout medians 38.5/44.5 with
  zero-rollouts present); every non-cuddle grave tier has a
  per-rollout median of 0.
- **The observer-own-need control axis starves above the 0.45 tier**
  (pooled hot-cell totals 0–632 across 800k world-ticks). A matched
  design that stratifies on observer state needs either pooling
  across the whole collection, demotion of that axis to a covariate,
  or probe-generated encounters.

## Read 2 — relief-latency tail-quantile power

Question: at realistic stratum sizes, is a declared tail quantile of
relief latency readable per stratum, and at what n does it
discriminate a degradation? Episodes are runs of `need >= threshold`
per (kitty, need) in the same state channel; latency = run length in
ticks; runs still open at rollout end are censored and excluded (the
density read's episode counts include them: cuddle@0.70 is 1,447
complete + 4 censored = its 1,451; runs already above threshold at
tick 0 are start-truncated but counted complete, identically in both
readers). Power: bootstrap (1,000 draws, seeded) relative CI
half-width of p90, and power to detect a +25% latency shift at p90
against the null bootstrap reference, alpha 0.05 one-sided, on a
subsample curve. The reference design treats the baseline as known,
so the printed powers are optimistic — a true two-sample read at the
same n is weaker, which strengthens the thinness conclusion below.
CI half-width is quoted at the full observed n; power at the largest
subsample n the stratum reaches.

| stratum | n (censored) | median | p90 | p90 CI half-width @ full n | power for +25% @ n |
|---|---|---|---|---|---|
| cuddle@0.70 | 1,447 (4) | 19.0 | 63.0 | 7.9% | 0.94 @ 500 |
| cuddle@0.90 | 340 (3) | 20.5 | 65.0 | 14.7% | 0.77 @ 200 |
| eat@0.70 | 465 (3) | 16.0 | 43.0 | 18.6% | 0.45 @ 200 |
| drink@0.70 | 161 (0) | 15.0 | 44.0 | 18.2% | 0.46 @ 100 |
| sleep@0.70 | 109 (0) | 13.0 | 61.0 | 25.4% | 0.12 @ 100 |
| eat@0.90 | 38 (1) | 18.5 | 57.2 | 42.0% | 0.09 @ 20 |
| drink@0.90 | 13 (0) | 20.0 | 61.0 | 40.8% | — |
| sleep@0.90 | 10 (0) | 18.5 | 65.2 | 42.9% | — |
| play@0.70 | 2 (0) | 6.5 | 10.1 | — | — |
| bath@0.70 | 2 (0) | 4.5 | 5.7 | — | — |

play@0.90 and bath@0.90: zero episodes.

Reading:

- **A p90 discriminator needs hundreds of episodes per stratum, and
  episode count alone is not enough.** The cuddle curves need
  200–500 (power 0.71–0.77 at 200, 0.94 at 500); eat@0.70 reaches
  465 episodes yet only 0.45 power at 200 — its latency distribution
  is less favourable — and at or below 100, power never clears 0.49
  anywhere. In 800k scripted world-ticks, only the cuddle strata
  reach a usable read.
- **Per-friend splits make it worse.** Episodes concentrate in one or
  two roster members (eat@0.90: 31 of 38 in a single kitty — the
  identity dials differ by design), so per-friend × stratum min-n at
  the grave tier is unreadable from lived data for every non-cuddle
  need.
- **Implication for the pins**: a conservatively-resolving rule
  (unreadable → demotion) over lived data alone demotes everything
  except cuddle. The pins have to pair the quantile with a min-n that
  most strata can actually meet — pooling friends per stratum,
  reading non-cuddle needs at 0.70 rather than 0.90, or feeding the
  read probe-generated episodes with their cost lines — and the
  "absent an alarm, thin strata never auto-demote" guard is doing
  real work, not belt-and-braces.

## Read 3 — happiness mass at the ruled edges (added 2026-10-12)

Owner ask, 2026-10-12 (the bins discussion): where do the ostrich
bins' happiness edges come from, and should training vs trained get
different values? Edge provenance, verified in source: 45 =
`LOW_HAPPINESS` (`crates/cloudkitty-rl/src/welfare.rs:20`), 70 =
`MIN_MEAN_HAPPINESS` (`welfare.rs:31`) — the welfare-gate constants
(specs 004/006 lineage, tighten-only compile-time asserts at
`welfare.rs:40-44`); 70 was defined as a bar on each kitty's
run-MEAN happiness (one check per kitty, `welfare.rs:314`), borrowed
by the S§3(d) ruling onto a per-state axis. The occupancy
question is measurable, same corpus and state channel as reads 1–2
(happiness at block offset 6, scale /100):

| | scripted bc-corpus, 4,000,000 kitty-ticks |
|---|---|
| mean / p5 / p50 / p95 / min | 85.1 / 71.1 / 87.0 / 93.8 / 28.8 |
| below 45 | 0.0236% |
| 45 to 70 | 3.95% |
| at least 70 | 96.027% |

For the trained side, the committed cert record
(`experiments/fog-gen1-cert/RESULTS.md`): the gen1-A gate table puts
every certified seat's mean happiness +4.36 to +6.56 points above
the scripted cat in that seat on the paired band (+4.30 to +6.67 on
the eval band), no seed below at any seat; §Report-only swaps adds
"Every arm at every seat beats the scripted cat in that seat on all
30 seeds" (the swaps' under-one-point spread is arm-vs-arm, not
trained-vs-scripted).

Trained-tail addendum (2026-10-12, same day; restated after a gate
FAIL caught the first version comparing across corpora): the
below-45 tail of the certified roster is already measured in the
committed battery raws — the scorecards carry `low_share`, the
cert harness's share of ticks strictly below 45
(`cert_harness_fog.py:432`, its `LOW_HAPPINESS = 45.0` mirroring
`welfare.rs:20`), per seat per seed. The battery also holds
SAME-WORLD all-scripted legs (same config_sha256, same seed base;
same harness file, though the trained-eval leg's tool sha differs —
stamped mid-edit, and only the current harness's strict `< 45`
definition is byte-checkable), so the trained-vs-scripted tail read
is paired, 30 seeds × 20,000 ticks × 5 seats per leg:

| band | trained low ticks /3M | scripted low ticks /3M | ratio | worst cell: trained / scripted |
|---|---|---|---|---|
| eval | 1 | 61 (0.00203%) | 61.0 | 5e-05 / 0.0016 |
| stress | 6 | 51 (0.0017%) | 8.5 | 0.0003 / 0.0006 |
| pooled | 7 | 112 | 16.0 | |

Training thins the below-45 tail about 1.2 orders pooled (61× on
the eval band, 8.5× on stress), cell-to-cell the trained worst
(0.03%) sits below the scripted worst (0.16% eval / 0.06% stress),
and 149 of 150 trained cells per band are exactly 0. Read 1-3's
bc-corpus scripted rate (0.0236%) is a DIFFERENT corpus and config
— itself about 12× the cert-band scripted rate — so it is
collection-density context, never the training comparator. The
trained 45–70 occupancy stays unmeasured (the scorecards carry the
below-45 share, the mean, floor touches and distress ages — no
45–70 field) until the ostrich metric's own bin-occupancy read,
first available at Phase 1 on the frozen-trunk rollouts (the
skeleton's "Phase-1 offline heads" leg), with insufficient-coverage
first-class per S§3(d). Owner, 2026-10-12: no dedicated
trained-seat rollout pre-sitting — "we'll skip the rollout".

Reading: the below-45 bin is already near-empty at scripted
(= BC-start) density (0.0236% on bc-corpus, 0.0017–0.00203% on the
cert bands), the 45–70 bin small but readable at collection density
(3.95%, about 158k of the 4M bc-corpus ticks), trained seats sit
4–7 happiness points above scripted in-seat, and training thins the
below-45 tail about 16× in the paired same-world read. For 45–70
the thinning is still an inference from the mean shift. It is an
occupancy problem, not an edge
problem: era-relative edges would keep bins full by relabeling
ordinary ticks as grave, and every cross-era comparison the
instruments make (Phase-1 certificate vs Phase-2 lived, lived vs
probe) depends on "grave" naming the same state on both sides. The
fixed probe battery, not the edges, is the era knob. Candidate pin
lines drafted into the skeleton's §9 item 2 slot travel with this
read.

## Caveats

- **Gen 1 scripted config, no answering teacher.** Gen 2 collection
  runs the spec 059 cue-answering teacher and trained seats; the
  teacher relieves cuddle wants faster, so the one data-rich kind
  should get poorer. Direction known, magnitude not — these numbers
  are the Gen 1 scripted floor-plan, not a Gen 2 prediction.
- **Read-time definitions are not pins**: distance bands, the
  observer-own-need line at 0.70, the +25% shift size, and p90 itself
  are this note's choices so the power question could be asked at
  all. The sitting pins its own.
- Both reads share one state channel and one episode definition, so
  their counts cross-check (the 1,447 + 4 = 1,451 identity above).

## Regeneration

### Read

```
cd /Users/elizabethkelly/ai/cloudkitty && \
experiments/exp-006-character-gen/.venv/bin/python \
  experiments/minifriend-presitting-2026-10-11/grave_density_read.py \
  --out <scratch>/grave-density.json
# runtime ~5 seconds; no env beyond the venv interpreter
```

```
cd /Users/elizabethkelly/ai/cloudkitty && \
experiments/exp-006-character-gen/.venv/bin/python \
  experiments/minifriend-presitting-2026-10-11/relief_latency_read.py \
  --out <scratch>/relief-latency.json
# runtime ~1 second; bootstrap is seeded (20261011), output deterministic
```

```
cd /Users/elizabethkelly/ai/cloudkitty && \
experiments/exp-006-character-gen/.venv/bin/python \
  experiments/minifriend-presitting-2026-10-11/happiness_mass_read.py \
  --out <scratch>/happiness-mass.json
# runtime ~5 seconds; no env beyond the venv interpreter
```

```
cd /Users/elizabethkelly/ai/cloudkitty && \
experiments/exp-006-character-gen/.venv/bin/python \
  experiments/minifriend-presitting-2026-10-11/trained_tail_read.py \
  --out <scratch>/trained-tail.json
# runtime ~1 second; reads the two committed gen1-A battery jsonl
# scorecards, not the bc-corpus bundle
```

Recorded outputs: `grave-density.json`, `relief-latency.json`,
`happiness-mass.json` and `trained-tail.json` beside this file. All
readers print every derived column the doc uses.

Raw-dir hashes (`scripts/rawdir-hash.sh`, per real idx dir; the
canonical recipe refuses `flat/`'s symlinks, so the bundle is the
nine real dirs — recomputed 2026-10-11, byte-identical to the
spec059-fr016-overlap stamp):
idx00-02 v1:2f4e0c795cbdc767 · idx03 v1:d47382a69b1d4d20 ·
idx04-12 v1:45a55c949a4831ce · idx13 v1:9f9451c5750b8a90 ·
idx14-22 v1:294492bac80d54d2 · idx23 v1:7276669ad40902a2 ·
idx24-32 v1:821f811c01db5836 · idx33 v1:30413d82efd5e7f5 ·
idx34-39 v1:dafc7b2ce880bb27

Accuracy gate: PASS 2026-10-11 — arithmetic ~134 (all match, no
rounding cases), threshold 8 (7 sourced or declared; 1 unsourced
found: "45/70/90 pinned bins", fixed post-gate — the ruling pins
happiness 45/70 + the 90 distress edge, so 45/70 on need pressure
are now labeled read-time choices here and in both docstrings),
characterisation 14 (11 supported, 3 weak fixed post-gate: the
200–500 range restated in power terms with eat@0.70 as the
counterexample; the power design relabeled
reference-not-two-sample, optimistic direction stated; the CI
column unified at full n), undecidable ~12 (judgement items and the
conversation-only ask), provenance 13 (all verified, incl. the
Professor quote verbatim, nine raw-dir hashes recomputed, state
layout re-derived over all 40 rollouts, flag-cell total 11,976
cross-channel identity). Fresh JSONs byte-identical to recorded,
re-verified after the post-gate docstring edits.

Accuracy gate, Read 3 addendum + skeleton [CANDIDATE] copy check:
PASS 2026-10-12 — arithmetic 11 (all match), provenance 9 (8
verified incl. the welfare.rs constants at :20/:31, asserts
:40-44, the S§3(d) edges; 1 weak fixed post-gate: "population
MEAN" → each kitty's run-mean, welfare.rs:314), characterisation 3
(3 weak, all fixed post-gate: "near-empty" scoped to the below-45
bin; "slightly above" replaced with the gate table's +4.36..+6.56
paired / +4.30..+6.67 eval per-seat deltas — the swaps
under-one-point spread is arm-vs-arm, not trained-vs-scripted;
"thins the low bins" marked as an inference from per-seat means,
tail unmeasured). Fresh happiness-mass.json byte-identical to
recorded. Same raw bundle and hashes as above.

Accuracy gate, trained-tail addendum: FAIL r1 2026-10-12 — the
first version compared the trained tail against the bc-corpus
scripted rate (cross-corpus; the battery's own same-world scripted
legs give 16× pooled where the cross-corpus framing implied ~100×)
and put a worst cell beside a mean. Restated against the paired
legs; PASS r2 same day — 20/20 numbers, pairing verified
(config_sha256 782f9690… and seed bases shared across all four
legs), harness low_share definition verified strict < 45 at
cert_harness_fog.py:400/:432/:45; one weak fixed post-gate ("same
harness" softened to same harness file, trained-eval tool sha
stamped mid-edit). The trained-tail JSON here reads the four
battery jsonl scorecards, not the bc-corpus bundle.
