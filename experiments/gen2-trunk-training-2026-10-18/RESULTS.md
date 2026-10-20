# Gen 2 trunk training — results

Arc home for the frozen prereg's §5 trunk recipe
(`gen2-prereg-2026-10-17.md`): BC clone, critic, then PPO at three
seeds. Trainer package in `trainer/` (committed 29e430fa, c9c2c2fe,
bdca5d82); artifacts land in `artifacts/` (gitignored — never delete).
Corpus = `../gen2-collection-driver-2026-10-14/results-raw/full-100/`
(100 rollouts, 9,960,292 decisions, collection gates in that arc's
RESULTS.md).

## BC clone (trunk-clone) — readout 2026-10-18

train_clone_g2.py on the full corpus: EntityPolicyV6 (obs 399 →
35 activities + 16 messages, 84,450 params), two-head masked CE
(eps 0.05 over the legal set), Adam 3e-4, batch 4096, plateau
patience 10 on summed val loss, epoch cap 200, seed 20261018.
Split: 90 train / 10 val rollouts (every rNN ending in 3), i.e.
8,964,180 train / 996,112 val rows. Consent swap per frozen §4:
136,699 refusal rows took the proposed label; 389 kept applied
(off-menu residual, `gen2-deviations.md` entry 1, RULED).

Stopped by plateau at epoch 112. Best epoch 102:

| metric | value |
|---|---|
| val loss (summed) | 0.8330 |
| val act loss / msg loss | 0.5198 / 0.3132 |
| act@1 | 0.8608 |
| msg@1 | 0.9763 |
| H(act) / H(msg) | 0.5233 / 0.3121 |

Per-group val accuracy (val counts in parentheses; groups per
data_g2.ACTION_GROUPS):

| group | acc | n |
|---|---|---|
| move | 0.8748 | 325,411 |
| rest/sleep | 0.9652 | 238,775 |
| groom-self | 0.9415 | 15,174 |
| groom-kitty | 0.9842 | 31,497 |
| eat/drink | 0.9833 | 38,890 |
| play/chase | 0.8402 | 293,604 |
| idle | 0.2300 | 52,761 |

Notes, measured not interpreted:

- Idle is the one group far below the rest (0.2300 on 52,761 val
  rows); the smallest activity class is ChaseCritter1 (n=101,
  acc 0.1980). No frozen bar names a clone top-1; this readout is
  the record and the pin's basis, and PPO reshapes the policy from
  here.
- The free registers never appear as val labels — Mew, Purr, Chirp,
  Trill, Ekekek all n=0 — consistent with the §8.1 chatter floor
  (0 free-register emissions in all 9,960,292 corpus decisions;
  `../gen2-comparator-legs-2026-10-14/RESULTS.md` §Chatter floor).
  Silent is 746,121 of 996,112 val labels (74.9%).

PIN: `train_ppo_g2.PINS["init_clone"]` =
`artifacts/trunk-clone/trunk-clone.pt` (sha256
dbe912eb4e9ec3028fe5b02ca8de5da454fb9d00ac6470ff60b6fce464c5d430);
the launcher re-hashes it at launch. Critic and PPO launch stay
behind their own gates: probe-then-accept for the critic and the
PPO launch card, both on the owner's word.

### Regeneration (BC clone)

#### Collect (~6.2 h: 112 epochs × ~190 s; writes artifacts/trunk-clone/)

```
cd experiments/gen2-trunk-training-2026-10-18/trainer
caffeinate -s ../../exp-006-character-gen/.venv/bin/python -B train_clone_g2.py \
  --name trunk-clone \
  --data-root ../../gen2-collection-driver-2026-10-14/results-raw/full-100 \
  --consent-rows ../../gen2-collection-driver-2026-10-14/results-raw/consent-rows-full-100.json \
  > ../artifacts/trunk-clone-train.log 2>&1
```

#### Read (seconds; stdlib python3 only)

```
python3 - <<'EOF'
import json
m = json.load(open("experiments/gen2-trunk-training-2026-10-18/artifacts/trunk-clone/trunk-clone-metrics.json"))
assert m["params"] == 84450 and m["best_epoch"] == 102 and m["stopped_by"] == "plateau"
assert m["consent_swap_rows"] == 136699 and m["consent_unswappable_rows"] == 389
assert sorted(m["val_rollouts"]) == [f"r{i}3" for i in range(10)]
v = m["val"]
print({k: round(x, 4) for k, x in v.items()})
groups = {g: (round(d["accuracy"], 4), d["count"]) for g, d in m["activity_groups"].items()}
assert sum(c for _, c in groups.values()) == 996112
print(groups)
cc1 = next(c for c in m["activity_classes"] if c["name"] == "ChaseCritter1")
print("ChaseCritter1", cc1["count"], round(cc1["accuracy"], 4))
free = {c["name"]: c["count"] for c in m["message_classes"]
        if c["name"] in ("Mew", "Purr", "Chirp", "Trill", "Ekekek")}
assert set(free.values()) == {0}, free
sil = next(c for c in m["message_classes"] if c["name"] == "Silent")
print("Silent", sil["count"], round(sil["count"] / 996112, 3))
EOF
```


## Critic (critic-g2) — readout + acceptance probe 2026-10-18

train_critic_g2.py, same corpus and consent JSON (the swap moves
activity labels only; the loader's integrity asserts run identically
for every consumer): EntityCriticV2 over the 237-wide global state
(75,073 params), censored MC returns (γ 0.998, min_future 1500,
exp-001 deviation 27c), normalized targets, Adam 1e-3, batch 4096,
plateau patience 5, seed 20261018. 1,665,090 train / 185,010 val
states; target mean 417.08, std 16.87. Stopped by plateau at epoch 8;
best epoch 3: **val MSE 0.0537, val EV 0.8351**. (Gen 1's fog critic
had EV ~0 on its flat anchor corpus; the Gen 2 corpus has return
signal and the critic captures most of it on-distribution.)

### Acceptance probe (#365 "Probe then accept") — FAIL

critic_probe_g2.py (committed 27fa06fe before the run, bars carried
verbatim from the Gen 1 probe): random-legal policy on the trunk
config, 3 worlds × 4,000 ticks (one continuous episode per world,
horizon override; world seeds 870004 / 1870004 / 2870004 off the
shared battery eval band), 7,503 pooled states.

| bar | reading | verdict |
|---|---|---|
| finite | all | PASS |
| in band [0, 834.17] | pred [236.09, 409.83] | PASS |
| Spearman ≥ 0.3 | **−0.026** | **FAIL** |

Shape, measured (per-world stats in `critic-probe.json`): the random
policy tanks returns as designed (probe target range [214.9, 303.9],
mean 243.1, vs corpus mean 417.1), and the critic does not follow —
predictions stay at 236–410, mostly near the corpus mean, so it
overestimates every probe state. Per-world rho 0.189 / 0.378 /
−0.058; the pooled rank washes out further because world-level
offsets anti-align (the world with the lowest targets gets the
highest predictions). Deterministic: the re-run reproduces pooled
rho −0.0257 exactly.

Reading: on-distribution EV 0.8351 with rank-blind extrapolation on
far-off-distribution states — the failure mode the probe exists to
surface. Two facts that bear on acceptance: PPO starts from the BC
clone (act@1 0.8608), so early PPO states are near-distribution, and
train_ppo_g2 keeps training the critic in the loop (opt_v) — the pin
is a warm start, not a frozen evaluator. Acceptance is the owner's
word per #365; ROUTED 2026-10-18, PENDING.

### Regeneration (critic)

#### Collect (~5 min train + ~3 min probe; writes artifacts/critic-g2/)

```
cd experiments/gen2-trunk-training-2026-10-18/trainer
caffeinate -s ../../exp-006-character-gen/.venv/bin/python -B train_critic_g2.py \
  --data-root ../../gen2-collection-driver-2026-10-14/results-raw/full-100 \
  --consent-rows ../../gen2-collection-driver-2026-10-14/results-raw/consent-rows-full-100.json \
  > ../artifacts/trunk-critic-train.log 2>&1
caffeinate -s ../../exp-006-character-gen/.venv/bin/python -B critic_probe_g2.py \
  --out ../artifacts/critic-g2/critic-probe.json > ../artifacts/critic-probe.log 2>&1
```

#### Read (seconds; stdlib python3 only)

```
python3 - <<'EOF'
import json
d = "experiments/gen2-trunk-training-2026-10-18/artifacts/critic-g2/"
s = json.load(open(d + "critic-g2-0p998-stats.json"))
assert s["params"] == 75073 and s["best_epoch"] == 3
assert (s["gamma"], s["min_future"]) == (0.998, 1500)
print("train/val states", s["train_states"], s["val_states"])
print("target mean/std", round(s["target_mean"], 2), round(s["target_std"], 2))
print("best val MSE/EV", round(s["best_val_mse"], 4), round(s["best_val_ev"], 4))
v = json.load(open(d + "critic-probe.json"))
assert v["verdict"] == "FAIL" and v["finite"] and v["in_band"]
assert (v["ticks"], v["worlds"], v["states"]) == (4000, 3, 7503)
assert v["world_seeds"] == [870004, 1870004, 2870004]
print("band", [round(x, 2) for x in v["band"]],
      "pred", round(v["pred_min"], 2), round(v["pred_max"], 2))
print("pooled rho", round(v["spearman"], 4))
print("probe targets", round(v["target_min"], 1), round(v["target_max"], 1),
      "mean", round(v["target_mean_probe"], 1),
      "corpus mean", round(v["target_mean_corpus"], 1))
for w in v["per_world"]:
    print(w["name"], round(w["rho"], 3),
          [round(x, 1) for x in w["pred_range"]],
          [round(x, 1) for x in w["target_range"]])
EOF
```

## Critic investigation reads (owner "Run the investigation reads", 2026-10-18)

Professor's advisory (second opinion relayed on her word; their note:
`~/ai/professor/notes/for-experiments-critic-probe-opinion-2026-10-18.md`)
read the FAIL as cause (a) — narrow corpus return span, welfare
features never bound — with (c), a real encoding gap, as the
alternative worth excluding, and called the pooled-Spearman instrument
mostly wrong while the declared FAIL stands (no post-hoc re-scoring;
an amended instrument is declared here for the NEW reads only). Two
reads, declared before running:

**Read 1 — feature sensitivity** (`trainer/critic_sensitivity_g2.py`):
20,000 corpus val states (seeded sample), each perturbed per kitty
block — distress flags → 1, needs → 0.20, happiness → 0.20, and all
three combined — and the critic's raw-unit prediction delta read per
variant. Layout offsets asserted in-run on the raw sample. Reference
scale: the corpus-to-probe target gap is ~174 raw units (417.1 →
243.1). Reading rule: deltas a small fraction of that gap = features
unbound, (a) confirmed and (c) dissolved; a large wrong-direction
delta = encoding issue, named before PPO.

**Read 2 — ε-on-clone re-probes** (`trainer/critic_probe_g2.py
--epsilon`, PPO's actual early visitation): per seat-tick the clone's
greedy legal action, random-legal with probability ε. Two runs, ε 0.1
at seed-base 870007 and ε 0.3 at seed-base 870010 (fresh bases off
the shared battery eval band; 3 worlds × 4,000 ticks each, one
continuous episode per world). Declared bars for THESE reads
(amended, per-world, so world offsets cannot wash the rank out):
finite and in-band unchanged as hard bars; benign line = EVERY
world's Spearman ≥ 0.3; a world whose target std is under 2 raw
units is reported as uninformative, not passed. These are
investigation reads, not acceptance gates — acceptance stays the
owner's word either way.

### Investigation results (run 2026-10-18, instruments at 228a8134)

**Read 1 — feature sensitivity** (20,000 val states, baseline mean
prediction 417.9; reference gap ~174 raw units):

| perturbation | Δmean | Δp5 | Δp95 |
|---|---|---|---|
| distress flags → 1 | **+17.54** | −2.15 | +23.63 |
| needs → 0.20 | −0.30 | −2.12 | +0.86 |
| happiness → 0.20 | −7.35 | −19.59 | −2.89 |
| all three | +11.74 | −6.53 | +19.04 |

The welfare features are essentially unbound: needs are inert
(−0.30), happiness moves 4% of the gap in the right direction, and
the distress flags move the prediction the WRONG way (+17.5, ~10% of
the gap — flipping every kitty to distressed makes the critic predict
a better future). Cause (a) confirmed with a mild perverse edge on
the distress flags; no evidence of a bound-but-wrong encoding beyond
that small wrong-sign component. The wrong-sign edge is consistent
with the failed probe's anti-aligned world offsets.

**Read 2 — ε-on-clone re-probes** (declared bars: finite + in-band
hard; benign = every world ρ ≥ 0.3; target std < 2 = uninformative):

| run | pooled ρ | per-world ρ | per-world target std | target mean |
|---|---|---|---|---|
| ε 0.1 (870007) | 0.179 | +0.013 / +0.226 / +0.143 | 5.8 / 10.2 / 7.2 | 408.8 |
| ε 0.3 (870010) | 0.114 | +0.033 / −0.165 / +0.284 | 7.4 / 5.6 / 12.2 | 399.5 |

Finite and in-band PASS on both; every world's target std ≥ 2
(informative). **The benign line is NOT met** — best world ρ 0.284,
one world negative. Context the numbers carry: at PPO's early
visitation the worlds do not tank (target means 408.8 / 399.5 vs
corpus 417.1, spans narrow), prediction ranges overlap the target
ranges, so the magnitude error is modest there — the failure is rank
signal, not calibration collapse.

**Fork resolution per the Professor advisory**: the ε-probe did not
come back benign, so the advisory's recommendation lands on MITIGATE
— mix fresh ε-random rollouts into critic pretraining (training and
probe data disjoint), re-probe on fresh seeds under the amended
per-world instrument. Whether to mitigate (a deviations-ledger
candidate: frozen §5 carries the critic recipe, and widening its
training data departs from it), accept as warm start with the
keeping-up monitor, or hold is the OWNER'S call — routed 2026-10-18,
PENDING.

#### Read (investigation; seconds; stdlib python3 only)

```
python3 - <<'EOF2'
import json
d = "experiments/gen2-trunk-training-2026-10-18/artifacts/critic-g2/"
s = json.load(open(d + "critic-sensitivity.json"))
assert s["states_sampled"] == 20000 and s["seed"] == 20261018
print("baseline", round(s["baseline_mean"], 1))
for k, v in s["variants"].items():
    print(k, round(v["delta_mean"], 2), round(v["delta_p5"], 2),
          round(v["delta_p95"], 2))
for tag, eps, base in (("eps01", 0.1, 870007), ("eps03", 0.3, 870010)):
    v = json.load(open(d + f"critic-probe-{tag}.json"))
    assert v["epsilon"] == eps and v["seed_base"] == base
    assert v["finite"] and v["in_band"] and v["states"] == 7503
    print(tag, "pooled", round(v["spearman"], 3),
          "tgt mean", round(v["target_mean_probe"], 1))
    for w in v["per_world"]:
        assert w["target_std"] >= 2.0, (tag, w)
        print(" ", w["name"], round(w["rho"], 3), round(w["target_std"], 1))
EOF2
```

## Critic mitigation — results (2026-10-18; declaration MITIGATION.md)

Coverage, achieved (vs declared targets): post-mix below-45 2.647%
(≥ 1.5), 45–70 6.835% (≥ 6), return mass to 156.0 (≤ 220 — and below
the fresh random probe's own floor 209.1, so no residual
extrapolation gap remains at the span edge), contrast pairs per kind
eat 3,500 / drink 1,896 / sleep 2,129 / play 2,328 / cuddle 4,311 /
bath 243 (all ≥ 200). Rungs used: (i) harvest 84 rollouts + (iii-ext)
suite 116 rollouts (R-cuddle3 the richest: 28.6% below-45, returns to
156); rungs (iv)/(v) not fired (occupancy targets met first).

Retrain (artifacts/critic-g2-ext/): 2,757,290 train states (200
extension rollouts, train-only), ORIGINAL val split. Best epoch 4:
val MSE 0.0112, **val EV 0.8249 — no-regression PASS** (band ≥ 0.80;
pre-mix 0.8351). Target std 16.87 → 38.15 (the span widening, as
designed).

Acceptance reads (fresh seeds as declared; amended instrument at
9fe6d214):

| leg | bar | reading | verdict |
|---|---|---|---|
| random 870013 | every world ρ ≥ 0.3 | 0.061 / 0.281 / 0.457 (pooled 0.418) | **FAIL** |
| ε 0.1 870016 | block null p99 | observed 0.283 > p99 0.173 (2 qualifying) | PASS |
| ε 0.3 870019 | block null p99 | observed 0.019 < p99 0.309 (worlds +0.481/−0.220/−0.254) | **FAIL** |
| mechanism | distress Δmean ≤ 0 | **−1.65** (was +17.54); needs −0.75, happy −4.35, all −19.23 | PASS |

Reading: the mitigation repaired what it targeted — the wrong-sign
distress binding is gone (the one defect the contrast pairing was
built to fix), the extrapolation clamp loosened (random-leg
predictions now reach down to 276.5 and pooled rank 0.418 would clear
the ORIGINAL #365 pooled bar that failed at −0.026), and the
deployment-matched ε 0.1 leg passes its calibrated null. What still
misses: one random-leg world carries no rank (0.061), and ε 0.3 —
the mid-drift regime — is rank-dead in two of three worlds. Rung
(iv), the declared deployment-matched data rung, was never fired and
is the natural next mix for exactly that regime; a second re-probe
round would need fresh declared seed bases. Acceptance is not met as
declared; the accept/iterate/hold decision is OWNER-ROUTED
(probe-then-accept, #365), PENDING.

### Read (mitigation results; seconds; stdlib python3)

```
python3 - <<'EOF2'
import json
d = "experiments/gen2-trunk-training-2026-10-18/artifacts/"
cv = json.load(open(d + "suite-coverage.json"))["postmix"]
assert round(cv["b45_frac"] * 100, 3) == 2.647
assert round(cv["f4570_frac"] * 100, 3) == 6.835
assert round(cv["span_min"], 1) == 156.0
cp = json.load(open(d + "contrast-pairs.json"))
assert all(cp["met"].values()) and cp["pairs"]["bath"] == 243
s = json.load(open(d + "critic-g2-ext/critic-g2-0p998-stats.json"))
assert s["extension_rollouts"] == 200 and s["best_epoch"] == 4
print("EV", round(s["best_val_ev"], 4), "std", round(s["target_std"], 2))
for tag in ("reprobe-random", "reprobe-eps01", "reprobe-eps03"):
    v = json.load(open(d + f"critic-g2-ext/{tag}.json"))
    print(tag, v["amended"], "pooled", round(v["spearman"], 3),
          [round(w["rho"], 3) for w in v["per_world"]],
          v.get("block_null", {}).get("observed"))
m = json.load(open(d + "critic-g2-ext/mechanism-test.json"))
for k, x in m["variants"].items():
    print(k, round(x["delta_mean"], 2))
assert m["variants"]["distress_on"]["delta_mean"] <= 0
EOF2
```

## Critic mitigation — round 2 (2026-10-19; iteration ruled "We'll wait for 065 to land, and go with iteration")

Second mix, on top of round 1: rung (iv) ε-mixture 40 rollouts (ε 0.1
seeds 1095201–1095220, ε 0.3 1095221–1095240) + true rung (ii) 50
manufactured-init rollouts on the UNALTERED trunk config via spec 065
(landed 5fb27cfb; IN-wide 0–90 seeds 1095241–1095265, IN-grave 60–95
1095266–1095290; tick-0 draws verified in-state). Post-mix-2 coverage
still met: below-45 2.464% (≥ 1.5), 45–70 6.670% (≥ 6), span 156.0
(≤ 220); IN-grave alone runs 1.758% below-45 with returns to 245.8.

Retrain (artifacts/critic-g2-ext2/): 2,982,380 train states (290
extension rollouts, train-only), ORIGINAL val split. Best epoch 4:
val MSE 0.0117, **val EV 0.8286 — no-regression PASS** (band ≥ 0.80;
round 1 0.8249, pre-mix 0.8351). Target mean 400.84, std 36.87.

Acceptance reads (fresh bases as declared 952e6009; amended
instrument unchanged at 9fe6d214):

| leg | bar | reading | verdict |
|---|---|---|---|
| random 870022 | every world ρ ≥ 0.3 | −0.204 / 0.551 / 0.108 (pooled 0.533) | **FAIL** |
| ε 0.1 870025 | block null p99 | observed −0.025 < p99 0.412 (2 qualifying; worlds +0.183/−0.480/+0.144) | **FAIL** |
| ε 0.3 870028 | block null p99 | observed 0.371 > p99 0.179 (3 qualifying; worlds +0.054/+0.372/+0.696) | PASS |
| mechanism | distress Δmean ≤ 0 | **−29.87** (round 1 −1.65); needs −0.49, happy −5.10, all −33.00 | PASS |

Reading: the mix repaired what it targeted and nothing it didn't.
ε 0.3 — the mid-drift regime rung (iv) was aimed at — went from
rank-dead to a clean null pass, and the distress binding deepened by
an order of magnitude (−1.65 → −29.87). But the two previously-better
legs moved the other way: ε 0.1, which passed round 1 at base 870016,
fails its null outright at 870025 (pooled −0.132 with one world at
−0.480), and the random leg's pooled rank keeps climbing (−0.026 →
0.418 → 0.533) while the strict per-world bar fails on a different
world each round (0.061 at 870013, now −0.204 at 870022). The
flip-flop across independent world triples at matched geometry reads
as marginal instrument power on the near-teacher legs — ε 0.1 target
std sits at 4.7–6.3 raw, straddling the qualifying line — not as a
corpus gap a third mix would obviously fill. Acceptance is not met as
declared (2 of 4 legs); the accept/iterate/hold decision is
OWNER-ROUTED (probe-then-accept, #365), PENDING.

### Read (round 2; seconds; stdlib python3)

```
python3 - <<'EOF2'
import json
d = "experiments/gen2-trunk-training-2026-10-18/artifacts/"
cv = json.load(open(d + "mix2-coverage.json"))
p2 = cv["postmix2"]
assert round(p2["b45_frac"] * 100, 3) == 2.464
assert round(p2["f4570_frac"] * 100, 3) == 6.670
assert round(p2["span_min"], 1) == 156.0 and p2["kt"] == 18760000
g = cv["per_group"]["IN-grave"]
assert round(g["b45_frac"] * 100, 3) == 1.758
assert round(g["ret_min"], 1) == 245.8
s = json.load(open(d + "critic-g2-ext2/critic-g2-0p998-stats.json"))
assert s["extension_rollouts"] == 290 and s["best_epoch"] == 4
assert s["train_states"] == 2982380
print("EV", round(s["best_val_ev"], 4), "mean", round(s["target_mean"], 2),
      "std", round(s["target_std"], 2))
for tag in ("reprobe-random", "reprobe-eps01", "reprobe-eps03"):
    v = json.load(open(d + f"critic-g2-ext2/{tag}.json"))
    print(tag, v["amended"], "pooled", round(v["spearman"], 3),
          [round(w["rho"], 3) for w in v["per_world"]],
          [round(w["target_std"], 1) for w in v["per_world"]],
          v.get("block_null", {}).get("observed"),
          v.get("block_null", {}).get("null_p99"))
m = json.load(open(d + "critic-g2-ext2/mechanism-test.json"))
for k, x in m["variants"].items():
    print(k, round(x["delta_mean"], 2))
assert m["variants"]["distress_on"]["delta_mean"] <= 0
EOF2
```

## Critic round 3 — instrument repair + adequate-power reads (2026-10-19; ruled "Ruled as recommended by Professor")

Instrument repair per MITIGATION.md §Round 3 (declared before any
measurement): per-world block nulls measured on all six probe legs to
date (every recorded ρ reproduced to 1e-6 before a null was read;
artifacts/neff-measurement.json), the null-width ceiling (0.3)
applied. Retroactive labels: round-2 ε0.1 FAIL → UNINFORMATIVE (its
own p99 0.412), round-1 ε0.3 FAIL → UNINFORMATIVE (0.309); both
historical PASSes survive (0.173 / 0.179) — with the labels, every
INFORMATIVE ε read through round 2 was a PASS, and the "flip-flop"
was the instrument. Round-2 random w0 (−0.204) sits inside its own
per-world null band (p99 0.292): noise. Bars resized from the
measurement (per-world SE 0.1658): (m, k) = (10, 7), power 0.907 at
true ρ 0.45, false-pass 7.4e-9; pooled ≥ 0.3 kept; random leg gains
its pooled block null; ε qualifying guard scales to ⌈2m/3⌉.

Round-3 reads, 10 fresh worlds per leg (bases declared in the
addendum; critic unchanged = artifacts/critic-g2-ext2):

| leg | bar | reading | verdict |
|---|---|---|---|
| random 870031 | ≥7/10 worlds ρ ≥ 0.3, pooled ≥ 0.3, null pass | 4/10 at bar; pooled raw 0.202; null 0.218 > p99 0.167 | **FAIL (informative)** |
| ε 0.1 870034 | block null p99 | observed 0.108 < p99 0.177 (7/10 qualifying) | **FAIL (informative)** |
| ε 0.3 870037 | block null p99 | 6/10 qualifying < 7 | UNINFORMATIVE (re-runs) |
| mechanism | distress Δmean ≤ 0 | −29.87 (round-2 read; same critic artifact, no retrain since) | PASS |

Reading: the instrument question is answered and the answer moves the
defect back into the object. At n_eff ~195 (random) and ~173 (ε0.1)
— tight, informative nulls — the critic's within-world rank signal is
real but far under the bars: a 4-of-10 world count against a bar with
0.907 power for a true-0.45 critic is a confident miss, not a coin
flip. The new fact the 10-world geometry exposes is world-level
heterogeneity of binding: per-world ρ spans +0.778 to −0.363 (random)
and +0.587 to −0.519 (ε0.1) against a per-world SE of 0.166 — spreads
of ~6 SE, genuine, not sampling noise. The critic ranks well in some
trunk worlds and anti-ranks in others; which worlds and why is now
the question (Professor's registered prediction named exactly this
branch: still-failing at measured-adequate power = a real corpus
question, their "tail" lean wrong on the defect/tail call at the
leg level — though right on the single w0 datum). The ε0.3
UNINFORMATIVE is a qualifying-count miss (6 < 7); by declaration it
re-runs at fresh worlds and is owed before any accept — moot while
two legs informatively fail. Acceptance not met; accept / iterate /
hold OWNER-ROUTED (probe-then-accept, #365), PENDING.

### Read (round 3; seconds; stdlib python3)

```
python3 - <<'EOF2'
import json
d = "experiments/gen2-trunk-training-2026-10-18/artifacts/"
n = json.load(open(d + "neff-measurement.json"))
assert n["ceiling"] == 0.3
labels = {k: v["pooled"]["informative"] for k, v in n["legs"].items()}
assert labels == {"r1-random": False, "r1-eps01": True, "r1-eps03": False,
                  "r2-random": True, "r2-eps01": False, "r2-eps03": True}
assert round(n["legs"]["r2-eps01"]["pooled"]["null_p99"], 3) == 0.412
assert round(n["legs"]["r2-random"]["per_world"][0]["null_p99"], 3) == 0.292
r = json.load(open(d + "critic-g2-ext2/round3-random.json"))
assert r["amended"] == {"mode": "random", "pass": False,
                        "uninformative": False, "worlds_at_bar": 4,
                        "k_of_m": [7, 10]}
assert round(r["spearman"], 3) == 0.202 and r["block_null"]["pass"]
rhos = [round(w["rho"], 3) for w in r["per_world"]]
assert max(rhos) == 0.778 and min(rhos) == -0.363
e1 = json.load(open(d + "critic-g2-ext2/round3-eps01.json"))
assert not e1["amended"]["pass"] and not e1["amended"]["uninformative"]
assert round(e1["block_null"]["observed"], 3) == 0.108
assert round(e1["block_null"]["null_p99"], 3) == 0.177
e3 = json.load(open(d + "critic-g2-ext2/round3-eps03.json"))
assert e3["amended"]["uninformative"] and \
    e3["amended"]["qualifying_worlds"] == 6
m = json.load(open(d + "critic-g2-ext2/mechanism-test.json"))
assert round(m["variants"]["distress_on"]["delta_mean"], 2) == -29.87
print("round-3 fence: all cells match")
EOF2
```
