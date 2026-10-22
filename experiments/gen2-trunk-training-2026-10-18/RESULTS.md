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

## World-heterogeneity diagnosis — declaration (2026-10-19, owner "run it"; results below after the run)

Question: what separates the worlds the round-3 critic ranks from the
worlds it anti-ranks? Groups are fixed by the ROUND-3 recorded
per-world ρ before any diagnostic is read: RANKING ρ ≥ 0.3, ANTI
ρ ≤ −0.1, MID the rest — random leg (870031) and ε0.1 leg (870034),
10 worlds each, series regenerated seed-exactly with the recorded-ρ
reproduction assert (the §Round 3 measurement's regeneration rule).
No new collection; no bars — this is diagnosis, not acceptance.

Declared reads, one JSON per leg (diag_hetero_g2.py →
artifacts/diag-hetero.json):

1. **Outcome profile** per world: censored-target mean/std/min/max,
   happiness occupancy below-45 and 45–70 (HCOLS convention),
   per-need distress-flag tick rates (kitty offsets 20–25).
2. **Temporal structure** per world: Spearman(target, tick) and
   Spearman(prediction, tick) — the drift-mis-tracking test. If
   anti-ranking is drift mis-tracking, sign(ρ_world) tracks
   sign(corr_t(pred) · corr_t(target)).
3. **Identity composition** per world: mean of each identity-dial
   column (kitty offsets 26–39), plus across-world Spearman of
   ρ_world against every scalar in reads 1 and 3 (n = 10 per leg,
   descriptive only).

Competing mechanisms the reads separate (predictions declared):
corpus-type gap → ANTI worlds' outcome profiles sit outside the
extension corpus's supervised envelope; drift mis-tracking → read 2's
sign relation holds; identity-driven value variance → read 3's dial
scalars correlate with ρ_world while reads 1–2 are flat.

### Diagnosis results (reads 1–3) + read 4 declared (2026-10-19)

Read 2 answers it: **drift mis-tracking** — in every world where the
prediction drifts at all (|corr_t(pred)| ≥ 0.05, 16 of 20),
sign(ρ_world) = sign(corr_t(pred) · corr_t(target)) or ρ is under
0.1; the four no-drift worlds carry only small ranks (|ρ| ≤ 0.217)
that drift does not explain (correction 2026-10-19: the first write
of this sentence claimed "20 of 20" with no drift qualifier; its own
fence caught ε0.1 w7 — corr_t(pred) −0.0002, ρ −0.217 — and the
recount found four no-drift worlds, not one). Across worlds ρ tracks
corr_t(pred) at −0.952 (ε0.1) / −0.527 (random). Reads 1 and 3 are
flat: no outcome-profile or identity-dial scalar reaches |0.5|
against ρ_world. The critic ranks a world when its state-driven
prediction drift happens to co-move with the target's time trend and
anti-ranks when it drifts the other way.

Why targets trend: the censored-MC construction on a finite 4,000-tick
episode bakes in a deterministic remaining-horizon ramp — at γ 0.998
the discounted-sum factor falls from (1−γ^4000) to (1−γ^1500), a 4.9%
decline ≈ 20.6 raw units on the ε legs' ~417 mean. A linear ramp of
that range has std ≈ 5.9 — the ε worlds' observed target stds are
3.5–7.6, i.e. the ε targets are plausibly MOSTLY ramp, a component no
stationary state-only critic can represent (the corpus training
targets barely contain it: on 20k-tick rollouts ~89% of kept states
sit beyond any material ramp). If that holds, the ε legs at this
geometry never measured welfare ranking at all — round 1's ε0.1 PASS
included.

**Read 4, declared before running**: per world, with R_t =
(1−γ^(4000−t))/(1−γ) the deterministic ramp — (a) ramp share of
target variance (R² of target on R_t), (b) detrended ρ̃ =
Spearman(resid(pred | R_t), resid(target | R_t)). Diagnosis only,
never an acceptance bar (bar changes are the owner's on the ledger).
Predictions: ε worlds show ramp R² > 0.6 in most worlds; if the
mitigation's welfare binding is real, random-leg ρ̃ stays positive
after detrending (the genuine welfare-collapse component survives);
ε-leg ρ̃ tells us whether any rankable welfare signal exists at this
geometry at all.

### Read 4 results: the ramp owns the ε legs; genuine binding survives on random (2026-10-19)

artifacts/diag-detrend.json (seed-exact regeneration, recorded ρ
reproduced per world before any read):

- **ε0.1**: ramp R² of target variance 0.70–0.96 in 8 of 10 worlds
  (the other two 0.31 / 0.54); residual std collapses to 1.3–4.7 raw.
  Detrended ρ̃ scatters on zero (−0.369 … +0.187). The ε targets at
  this geometry are MOSTLY the deterministic censoring ramp — a
  quantity no stationary state-only critic can represent — and once
  it is removed there is essentially nothing left to rank. Every ε
  verdict to date, round-1's PASS included, measured accidental
  ramp-tracking, not welfare ranking.
- **random**: ramp R² 0.00–0.50 in 9 of 10 worlds (one at 0.77) —
  genuine welfare-collapse variance dominates — and detrended ρ̃ is
  POSITIVE in 9 of 10 worlds (+0.119 … +0.742; the one exception
  −0.010, flat). Both round-3 anti-ranking worlds flip sign when the
  ramp comes out: w4 −0.363 → +0.261, w3 −0.137 → +0.153. The
  world-level "heterogeneity of binding" was the ramp component
  flipping per-world reads; the critic's genuine welfare ranking is
  uniformly non-negative.

Conclusion (diagnosis, no bars moved): the mitigation did what it
claimed — distress binding repaired (−29.87) and genuine within-world
welfare rank positive everywhere it is measurable — and every
acceptance FAIL from round 1 through round 3 traces to a
target-construction artifact: exp-001/002's censored-MC recipe, built
for 20k-tick rollouts where the ramp touches ~11% of kept states, was
inherited into a 4k-tick probe where it spans the entire window
(prevention-trio pattern: an inherited RECIPE, not just an inherited
constant, re-derived at the geometry it meets). Detrended magnitudes
are honest but modest: random-leg ρ̃ mean +0.29, 4 of 10 worlds
≥ 0.3. Whether a detrended instrument becomes the acceptance bar — and
what level — is a deviations-ledger decision on the owner's word,
with Professor review the natural route.

### Read (diagnosis; seconds; stdlib python3)

```
python3 - <<'EOF2'
import json
d = "experiments/gen2-trunk-training-2026-10-18/artifacts/"
h = json.load(open(d + "diag-hetero.json"))
na = []
for leg in ("random", "eps01"):
    for w in h["legs"][leg]["per_world"]:
        if abs(w["corr_t_pred"]) < 0.05:   # no prediction drift: relation n/a
            na.append(abs(w["rho"]))
            continue
        prod = w["corr_t_pred"] * w["corr_t_target"]
        assert (w["rho"] > 0) == (prod > 0) or abs(w["rho"]) < 0.1, (leg, w)
assert len(na) == 4 and max(na) < 0.22  # small unexplained ranks only
assert round(h["legs"]["eps01"]["rho_vs_scalar"]["corr_t_pred"], 3) == -0.952
assert round(h["legs"]["random"]["rho_vs_scalar"]["corr_t_pred"], 3) == -0.527
t = json.load(open(d + "diag-detrend.json"))
assert round(t["ramp_range_raw"], 1) == 24.7 or t["ramp_range_raw"] > 20
e = t["legs"]["eps01"]["per_world"]
assert sum(w["ramp_r2_target"] > 0.6 for w in e) == 8
r = t["legs"]["random"]["per_world"]
assert sum(w["rho_detrended"] > 0 for w in r) == 9
assert round(r[4]["rho"], 3) == -0.363
assert round(r[4]["rho_detrended"], 3) == 0.261
assert round(r[3]["rho_detrended"], 3) == 0.153
mean_rt = sum(w["rho_detrended"] for w in r) / 10
assert round(mean_rt, 2) == 0.29
print("diagnosis fence: all cells match")
EOF2
```

## Extension-ramp check — declaration (2026-10-19, owner "Agreed on both"; Professor's refinement ask)

The 290 extension TRAINING rollouts were collected at 4k ticks, so
the censoring ramp sits in their targets (the 20k base corpus is ~89%
flat; the extension is 0% flat). Question: did extension data source
the prediction drift read 2 measured? Two reads, zero new collection
(ext_ramp_check_g2.py → artifacts/ext-ramp-check.json):

1. **Training-target contamination by rung**: per extension rollout,
   ramp R² of its censored targets (vs its own length's ramp curve)
   and Spearman(target, tick); aggregated by source rung (harvest
   groups / suite / ε / IN). The harvest rollouts have their own
   lengths; each uses its own T.
2. **Drift across checkpoints**: the round-3 random (870031) and ε0.1
   (870034) legs regenerated once, predictions from all three
   on-disk checkpoints — critic-g2 (round 0, NO extension),
   critic-g2-ext (200 ext), critic-g2-ext2 (290 ext) — per-world
   corr_t(pred) each. If drift grows with extension exposure, the
   extension data is the source; if round 0 drifts equally, the
   drift predates the mix.

Predictions declared: the 4k rungs (suite/ε/IN) show high target
ramp R² (the geometry guarantees it); checkpoint drift ordering is
the open question — EITHER monotone in extension exposure (extension
is the source; collection geometry joins the amendment) OR flat
(drift is intrinsic state-drift; collection geometry still moves to
6k/3500 for future rungs on cost-of-correctness grounds, but no
salvage question arises for the existing 290).

### Extension-ramp check — results (2026-10-19)

artifacts/ext-ramp-check.json. Record correction first: MITIGATION's
"extension rollouts collected fresh run 4,000 ticks" was true of the
round-2 rungs and the suite PILOTS; the suite FILL rollouts ran 8,000
ticks (seeds.json allocs; e.g. C10 pilot ticks 4000 / fill 8000).

Training-target contamination by rung (ramp R² / corr_t, each rollout
vs its own length's curve): the 4k rungs are heavily contaminated —
ε0.1 0.694/−0.679, IN-wide 0.607/−0.561, ε0.3 0.521/−0.542, IN-grave
0.417/−0.459, SCwater-pilot 0.809 — harvest (mixed lengths, mean
5,619) 0.557/−0.541, while the 8k suite fills are mild (0.053–0.303).

Checkpoint drift (same regenerated probe series, three critics):
NEITHER declared branch cleanly — round0-noext already drifts (random
mean|corr_t(pred)| 0.312 vs ext200 0.337 vs ext290 0.238; drift is
partly intrinsic state-drift), but the ε leg jumps exactly at ext290
(0.226 / 0.225 / 0.359, mean swinging to −0.235, ramp-shaped
downward) — the checkpoint that added the 90 heavily-ramped 4k
rollouts. Suggestive of added ramp-following on the near-teacher leg;
not decisive.

Consequence under the owner's ruling ("Assuming this works, let's
recollect rather than trying to salvage the 4k runs"): contamination
is confirmed and material in the 4k rungs → those rungs RECOLLECT at
honest geometry (ε 40 + IN 50 + SCwater-pilot 2 = 92 rollouts at
6k/3500, fresh seeds); the 8k suite fills and the harvest enter the
retrain under the uniform remaining-horizon censoring instead
(declared in MITIGATION §Round 4). No salvage of 4k data.

### Read (ext-ramp check; seconds; stdlib python3)

```
python3 - <<'EOF2'
import json
d = "experiments/gen2-trunk-training-2026-10-18/artifacts/"
c = json.load(open(d + "ext-ramp-check.json"))
p1 = c["part1_by_rung"]
assert round(p1["eps01"]["mean_ramp_r2"], 3) == 0.694
assert round(p1["IN-wide"]["mean_ramp_r2"], 3) == 0.607
assert round(p1["harvest"]["mean_ramp_r2"], 3) == 0.557
assert p1["harvest"]["n"] == 84 and round(p1["harvest"]["mean_len"]) == 5619
assert all(v["mean_ramp_r2"] < 0.31 for k, v in p1.items()
           if k.startswith("suite:") and k != "suite:SCwater")
assert round(p1["suite:SCwater"]["mean_ramp_r2"], 3) == 0.809
p2 = c["part2_drift"]
assert round(p2["random"]["round0-noext"]["mean_abs"], 3) == 0.312
assert round(p2["eps01"]["ext290"]["mean_abs"], 3) == 0.359
assert round(p2["eps01"]["ext200"]["mean_abs"], 3) == 0.225
assert round(p2["eps01"]["ext290"]["mean"], 3) == -0.235
print("ext-ramp fence: all cells match")
EOF2
```

## Round 4 — honest-geometry reads (2026-10-19; declaration §Round 4, recollection band 1095301–1095400)

Recollection: 92/92 rollouts at 6k (0 dropped). Baseline re-derived
per §Round 4 (3): round-0 critic val EV at min_future 3500 = 0.8746
(artifacts/baseline-ev-mf3500.json) → band 0.8396. Retrain
(artifacts/critic-g2-ext3; harvest + 8k suite fills + the 6k
recollection, poisoned 4k dirs excluded): best epoch 7, **val EV
0.8818 — no-regression PASS**, and the first mix that IMPROVES
on-distribution EV (rounds 1–2 cost it; the contaminated targets were
why). Reads as scored by the declared instrument:

| leg | reading | verdict as declared |
|---|---|---|
| random 870040 | ALL 10 worlds positive (0.227…0.694), pooled raw 0.522, null 0.470 > p99 0.013 | UNINFORMATIVE (ramp trip: 4 worlds R² > 0.2) |
| ε 0.1 870043 | null 0.180 > p99 0.083 (n_eff ~790); 3/10 qualifying | UNINFORMATIVE (ramp trip; also fails qualifying) |
| ε 0.3 870046 | null 0.141 ≈ p99 0.137; 3/10 qualifying | UNINFORMATIVE (ramp trip; also fails qualifying) |
| mechanism | distress Δmean **−46.09** (round 3: −29.87) | PASS |
| contrast gate | pooled 456/881 = 0.518, CP99 lower 0.478; **play 0.338 on 231 pairs, significantly BELOW chance** | **FAIL** |

**Finding 1 — the ramp trip is mis-specified and the mis-fire is
provable from its own JSONs.** The declared trip reads a
FREE-COEFFICIENT regression R² of target on the ramp curve, which at
honest geometry is a monotone-TREND share, not an artifact share: the
deterministic artifact's amplitude is pinned by γ and geometry (~0.38
raw span, std ~0.11), so its true share of target variance here is
≤ 0.028% (random) / ≤ 0.242% (ε) in EVERY world — three orders of
magnitude under the 0.2 trip. What the free coefficient fit is
genuine within-world welfare drift, the very signal the probe exists
to rank. The guard voided all three legs for carrying the quantity
under test. Intent (deviations entry 2, §Round 4 (2): a KNOWN-
STRUCTURE check) says pinned amplitude; the implementation let the
amplitude float. No verdict is re-scored here: the trip's
re-specification is an owner call on the ledger, recommended below.
For the record, under a pinned-amplitude trip the same JSONs read:
random INFORMATIVE and PASS on every declared bar (all worlds
positive — sign-uniformity clean, pooled 0.522, null passed); both ε
legs UNINFORMATIVE by the QUALIFYING guard (3/10 each) — at honest
geometry near-teacher targets genuinely lack rankable spread (stds
2.2–10, mostly < 5), which is the §Round 4 (6) mechanical demotion
point: ε legs earn descriptive-only status as a fact about the claim,
not a rescue (descriptively, ε0.1's above-null rank 0.180 > 0.083 at
n_eff ~790 is positive).

**Finding 2 — the contrast gate works and caught a real one-kind
inversion.** Pooled 0.518 with CP99 lower 0.478 misses the > 0.5
line, and PLAY is significantly inverted: the critic values
play-flagged states HIGHER in 66% of 231 held-out near-pairs, while
eat 0.558, cuddle 0.607, sleep 0.645 rank correctly and drink sits at
chance (0.482, n=110). The pooled mechanism test (−46.09) perturbs
all six flags at once, so a one-kind wrong sign hides inside it —
the gate exists in deployment currency precisely to see this. Whether
play's inversion is a binding defect or real MDP structure
(play-flagged passages may genuinely precede high-value play relief
in ways eat/drink distress does not) is NOT decided here; it is the
open question routed to the owner with this round's report.

Acceptance not met as declared (gate FAIL + all legs UNINFORMATIVE);
accept / iterate / hold OWNER-ROUTED, with two recommendations on
record: (1) one-commit amendment re-specifying the ramp trip to
pinned-amplitude artifact share (the declaration's own intent),
re-scoring these same JSONs under it; (2) a declared investigation of
the play inversion before any accept.

### Read (round 4; seconds; stdlib python3)

```
python3 - <<'EOF2'
import json
d = "experiments/gen2-trunk-training-2026-10-18/artifacts/"
b = json.load(open(d + "baseline-ev-mf3500.json"))
assert round(b["val_ev"], 4) == 0.8746 and b["min_future"] == 3500
s = json.load(open(d + "critic-g2-ext3/critic-g2-0p998-stats.json"))
assert s["extension_rollouts"] == 290 and s["best_epoch"] == 7
assert round(s["best_val_ev"], 4) == 0.8818
assert s["best_val_ev"] >= b["val_ev"] - 0.035
r = json.load(open(d + "critic-g2-ext3/round4-random.json"))
assert r["amended"]["reason"] == "ramp_contaminated"
rhos = [w["rho"] for w in r["per_world"]]
assert min(rhos) > 0 and round(max(rhos), 3) == 0.694
assert round(r["spearman"], 3) == 0.522 and r["block_null"]["pass"]
for w in r["per_world"]:   # pinned-amplitude artifact share bound
    assert (0.11 / w["target_std"]) ** 2 < 0.001
for leg in ("eps01", "eps03"):
    e = json.load(open(d + f"critic-g2-ext3/round4-{leg}.json"))
    assert e["amended"]["uninformative"]
    assert sum(w["target_std"] >= 5.0 for w in e["per_world"]) == 3
m = json.load(open(d + "critic-g2-ext3/mechanism-test.json"))
assert round(m["variants"]["distress_on"]["delta_mean"], 2) == -46.09
g = json.load(open(d + "contrast-gate.json"))
assert not g["pass"] and g["kinds_below"] == ["play"]
assert g["pooled_pairs"] == 881 and g["pooled_correct"] == 456
assert round(g["per_kind"]["play"]["fraction"], 3) == 0.338
assert round(g["cp99_lower"], 3) == 0.478
print("round-4 fence: all cells match")
EOF2
```

## Round 4 amendment — re-scores, the play read, and the gate's true nature (2026-10-19; amendment 28f57999, instrument d852b933)

Re-scores (beside the originals, per the recording rule; per-world ρ
and target std identity-asserted against the original JSONs):

| leg | amended-trip reading | re-scored verdict |
|---|---|---|
| random 870040 | max pinned artifact share 0.00007; all 10 worlds positive, pooled 0.522, null passed, sign-uniform | **PASS (informative)** |
| ε 0.1 870043 | max share 0.00167; 3/10 qualifying | UNINFORMATIVE (qualifying) — descriptive-only EARNED |
| ε 0.3 870046 | max share 0.00134; 3/10 qualifying | UNINFORMATIVE (qualifying) — descriptive-only EARNED |

Paired play read (declared decision structure, pre-read): 105
in-window pairs, flagged-lower 58 (55.2%), p = 0.165 — realized
returns from play-flagged states are NOT significantly lower (median
edge −0.07 raw against target stds ~10). **The declared benign branch
fires: the critic was right, the gate's uniform direction was the
defect.** The owner's pre-read domain prior (play handled differently
since Biscuit, then consent) and Professor's registered prediction
both land on this branch.

Derived directions (the declared consequence, artifacts/
kind-edges.json): **NO kind has one.** Realized per-pair edges are
null for all six needs (frac-lower 0.537–0.583 at n 12–159, nothing
near p99 either way). The deeper finding: at γ 0.998 with ≥3,500-tick
horizons, a local ±500-tick distress excursion moves the realized
discounted return by less than noise — the quantity the held-out
near-pair gate ranks has NO measurable ground truth at this
granularity, for any kind. Under its own derived-direction rule the
re-scored gate has zero directional kinds (n = 0): the gate is
STRUCTURALLY UNINFORMATIVE at this geometry — recorded as such, not
as a fail, and never silently dropped. Its one finding dissolves with
it: the critic's play lean (0.338) is a lean on a quantity whose
truth is ≈ 0 — descriptive, not a defect; and symmetrically, the
critic's "correct" eat/cuddle/sleep rankings were never
realized-confirmed either. Welfare-relevant state→value binding
remains gated by the MECHANISM test (170+-raw-unit corpus-level
perturbations, where signal exists; −46.09 PASS), which is exactly
where it belongs. A magnitude-calibrated per-kind value read is
banked as a Gen 3 instrument question.

**Acceptance picture under the declared-and-amended instruments**:
coverage MET; no-regression PASS (0.8818 vs re-derived baseline
0.8746); mechanism PASS (−46.09); random leg PASS, informative, every
declared bar; ε legs descriptive-only by their own guard
(descriptively positive at ε 0.1: 0.180 > p99 0.083, n_eff ~790);
contrast gate structurally uninformative at this geometry (recorded).
Every read that CAN be informatively taken passes.
Probe-then-accept remains the owner's word (#365); entry 2 closes
there.

### Read (amendment reads; seconds; stdlib python3)

```
python3 - <<'EOF2'
import json
d = "experiments/gen2-trunk-training-2026-10-18/artifacts/"
for leg in ("random", "eps01", "eps03"):
    o = json.load(open(d + f"critic-g2-ext3/round4-{leg}.json"))
    r = json.load(open(d + f"critic-g2-ext3/round4-{leg}-rescored.json"))
    for wo, wr in zip(o["per_world"], r["per_world"]):
        assert abs(wo["rho"] - wr["rho"]) < 1e-9
        assert wr["artifact_share"] < 0.002
rr = json.load(open(d + "critic-g2-ext3/round4-random-rescored.json"))
assert rr["amended"] == {"mode": "random", "pass": True,
                         "uninformative": False, "wrong_signed_worlds": []}
for leg in ("eps01", "eps03"):
    e = json.load(open(d + f"critic-g2-ext3/round4-{leg}-rescored.json"))
    assert e["amended"]["reason"] == "qualifying_worlds"
p = json.load(open(d + "play-edge-read.json"))
assert p["n_edges"] == 105 and p["flagged_lower"] == 58
assert round(p["p_significantly_lower"], 3) == 0.165
assert p["branch"] == "critic_right_gate_direction_defect"
k = json.load(open(d + "kind-edges.json"))
assert all(v["direction"] == "NONE"
           for v in k["derived_directions"].values())
g = k["gate_rescored"]
assert g["pooled_pairs"] == 0 and g["included_kinds"] == []
print("amendment fence: all cells match")
EOF2
```

## Trunk PPO — seeds s1/s2 readout (2026-10-20; launched on "Launch it" 2026-10-19 at 1318804e)

Both completed by the frozen plateau rule (3 flat 1M-tick bins), no
stop tripped:

| seed | updates | ticks | wall | ep_return first→last | min probe nash | max probe streak |
|---|---|---|---|---|---|---|
| trunk-s1 (idx 96) | 2,604 | 8,002,560 | 3.3 h | 0.8257 → 0.8816 | 0.8170 | 103 |
| trunk-s2 (idx 97) | 2,604 | 8,002,560 | 3.2 h | 0.8258 → 0.8807 | 0.8134 | 195 |

Welfare: clean end to end — every probe streak under the 300 bar,
nash never below 0.81 (line 0.5), lounge/inwater normal. The pinned
critic held through training (live EV mostly 0.6–0.9). Finals:
ppo-g2-trunk-s1/policy-final.pt sha256 a22b8713…,
ppo-g2-trunk-s2/policy-final.pt sha256 4040554a…. trunk-s3 (idx 98)
remains HALTED at u249 under deviations entry 3, owner-routed.
Monitor lesson banked: the watch filter missed the uppercase
"PLATEAU:" terminal line — terminal-state filters are
case-insensitive from here on.

### Read (PPO s1/s2; seconds; stdlib python3)

```
python3 - <<'EOF2'
import json
d = "experiments/gen2-trunk-training-2026-10-18/artifacts/"
for s, last_ret, mn, mx in (("s1", 0.8816, 0.8170, 103),
                            ("s2", 0.8807, 0.8134, 195)):
    rows = [json.loads(l) for l in open(d + f"ppo-g2-trunk-{s}/metrics.jsonl")]
    tr = [r for r in rows if not r.get("probe")]
    pr = [r for r in rows if r.get("probe")]
    assert tr[-1]["update"] == 2604 and tr[-1]["ticks"] == 8002560
    ret = [r for r in tr if r.get("ep_return_mean")]
    assert round(ret[-1]["ep_return_mean"], 4) == last_ret
    assert round(min(p["nash"] for p in pr), 4) == mn
    assert max(p["max_distress_streak"] for p in pr) == mx < 300
print("ppo readout fence: all cells match")
EOF2
```

### Trunk PPO — replacement seed s4 readout (2026-10-20; entry-3 ruling "A")

trunk-s4 (seed 4, idx 99, stripe 2080000000+): plateau-complete at
2,604 updates / 8,002,560 ticks / 2.3 h — the same convergence point
as s1/s2. ep_return 0.8229 → **0.8864** (the best of the three
finals); min probe nash 0.8149; max probe streak **217** — under the
300 bar but the closest approach of the three completed seeds (s1
103, s2 195), consistent with the entry-3 reading that the play-lean
pressure is real and seed-dependent. Final
ppo-g2-trunk-s4/policy-final.pt sha256 69d7248c…. Frozen §5's
three-seed plan is satisfied by s1/s2/s4; deviations entry 3 CLOSES
at this completion per its own ruling text.

### Read (s4; seconds; stdlib python3, repo root)

```
python3 - <<'EOF2'
import json
rows = [json.loads(l) for l in open(
    "experiments/gen2-trunk-training-2026-10-18/artifacts/"
    "ppo-g2-trunk-s4/metrics.jsonl")]
tr = [r for r in rows if not r.get("probe")]
pr = [r for r in rows if r.get("probe")]
assert tr[-1]["update"] == 2604 and tr[-1]["ticks"] == 8002560
ret = [r for r in tr if r.get("ep_return_mean")]
assert round(ret[-1]["ep_return_mean"], 4) == 0.8864
assert round(min(p["nash"] for p in pr), 4) == 0.8149
assert max(p["max_distress_streak"] for p in pr) == 217 < 300
print("s4 fence: all cells match")
EOF2
```

### Play-proposal drift read (2026-10-20; owner "Sounds great, let's do it")

Trace-only read ahead of the step-8 cert battery (no new rollouts,
zero welfare cost): partner-play (PlayKitty*) share of chosen actions
across every training probe, all four trunk seeds
(trainer/play_drift_read_g2.py, declared before results; artifact
artifacts/play-drift-read.json). Positive control reproduced exactly:
s3's halting probe, entry-3 cell (seed 40002, kitty 1), span 820–1136
= 317 rows / 122 play proposals (share 0.385), matching the committed
diag-s3 record.

| run | probes | share u49 | final share | late mean (5) | late max cell (last 5 probes) |
|-----|--------|-----------|-------------|----------------|----------------|
| s1 | 52 | 0.1734 | 0.2076 (u2599) | 0.1903 | 0.2825 @ (40003, 5) u2449 |
| s2 | 52 | 0.1317 | 0.1630 (u2599) | 0.1692 | 0.3375 @ (40003, 2) u2499 |
| s3 | 5 | 0.1556 | 0.1759 (u249) | 0.1558 | 0.2925 @ (40002, 2) u249 |
| s4 | 52 | 0.1382 | 0.1520 (u2599) | 0.1601 | 0.2480 @ (40002, 4) u2499 |

Reading: the pooled play-proposal pressure is **recipe-level, not an
s3 anomaly** — all three completed seeds drift upward (first probe →
late mean: s1 +0.0169, s2 +0.0375, s4 +0.0219; s3's five probes are
too short to read drift, +0.0002), and s3's pooled share at halt
(0.1759) sits inside the survivors' range. What distinguished s3 was
**concentration**: a single cell locking at 0.385 in-window while
multi-need distress ran 317 ticks. The survivors' late max cells
(0.248–0.338 over full 2k probes) show the same pressure diffusing
without locking onto a distressed cell. Two consequences, as assessed for the owner: (1)
training more same-recipe seeds would not remove the pressure — it is
the play-economy question (no value penalty on the play need's
distress), banked for Gen 3; (2) whether diffuse pressure stays
benign at battery scale (30×20k, two sizes) is exactly what step 8
measures — its worst-streak and dispersion columns are the
discriminator. s4, the best final return, carries the lowest late
pooled share (0.1601) and lowest late max cell (0.2480); s2 the
highest late max cell (0.3375).

### Read (play drift; ~1 min; lab venv, repo root)

```
cd experiments/gen2-trunk-training-2026-10-18/trainer && VIRTUAL_ENV=/Users/elizabethkelly/ai/cloudkitty/experiments/exp-006-character-gen/.venv /Users/elizabethkelly/ai/cloudkitty/experiments/exp-006-character-gen/.venv/bin/python3 -B play_drift_read_g2.py --out ../artifacts/play-drift-read.json
```

### Trunk PPO — seating seeds s5/s6/s7 (2026-10-21; deviations entries 5 and 6)

Three seating seeds on the identical pinned recipe and binding (entry
5), launched in parallel. trunk-s5 halted at update 199 / 614,400
ticks on the frozen §6 probe-distress stop (streak 307 on world 40001;
entry 6, ruled "don't replace s5", closed). trunk-s6 plateau-complete
at 2,604 updates / 8,002,560 ticks, ep_return 0.8270 → 0.8774, min
probe nash 0.8129, max probe streak 220 (final sha256 c93a4424…).
trunk-s7 plateau-complete at 2,929 updates / 9,000,960 ticks (one
more flat bin than the others), ep_return 0.8228 → **0.8877**, the best
of the six seeds, min probe nash 0.8182, max probe streak 247 (final
sha256 8ca8a517…). With s1/s2/s4, the five-network roster's networks
are complete: s1, s2, s4, s6, s7.

### Read (s5/s6/s7; seconds; stdlib python3, repo root)

```
python3 - <<'EOF2'
import json
d = "experiments/gen2-trunk-training-2026-10-18/artifacts/"
for s, upd, ticks, first, last, mn, mx in (("s5", 199, 614400, None, None, 0.8109, 307),
                                           ("s6", 2604, 8002560, 0.8270, 0.8774, 0.8129, 220),
                                           ("s7", 2929, 9000960, 0.8228, 0.8877, 0.8182, 247)):
    rows = [json.loads(l) for l in open(d + f"ppo-g2-trunk-{s}/metrics.jsonl")]
    tr = [r for r in rows if not r.get("probe")]
    pr = [r for r in rows if r.get("probe")]
    assert (tr[-1]["update"], tr[-1]["ticks"]) == (upd, ticks), (s, tr[-1]["update"], tr[-1]["ticks"])
    ret = [r for r in tr if r.get("ep_return_mean")]
    if first is not None:
        assert (round(ret[0]["ep_return_mean"], 4), round(ret[-1]["ep_return_mean"], 4)) == (first, last), s
    assert round(min(p["nash"] for p in pr), 4) == mn and max(p["max_distress_streak"] for p in pr) == mx, s
print("s5/s6/s7 fence: all cells match")
EOF2
```

### Trunk PPO — alternate seeds s8/s9/s10/s11 readout (2026-10-22; deviations entries 7, 8 and 9)

Alternates for the swaps digest (owner 2026-10-22 "Train the
additional seeds so we can run the swaps digest"; "Replace s8 just in
case."), identical pinned recipe and binding, launched 05:40Z (s8, s9,
s10 in parallel) and 06:28Z (s11). trunk-s8 halted at update 299 /
921,600 ticks on the frozen §6 probe-distress stop (streak 392
on probe world 40002; entry 8). trunk-s11, its replacement, halted at
update 99 / 307,200 ticks (streak 371 on world 40003; entry 9).
trunk-s9 and trunk-s10 both plateau-complete at 2,604 updates /
8,002,560 ticks: s9 ep_return 0.8290 → 0.8800, min probe nash 0.8096,
max probe streak 227 (final sha256 6feaa9d5…); s10 0.8275 → 0.8782,
min probe nash 0.8169, max probe streak 179 (final sha256 ab194dd5…).
Of eleven same-recipe seeds, four tripped the §6 stop (s3, s5, s8,
s11), every one inside the first 1M ticks; the seven that cleared 1M
all ran to plateau at 8.0–9.0M ticks with max probe streaks 103–247.
Recorded, not interpreted. The digest runs on s9 and s10
(`../gen2-cert-battery-2026-10-20/SWAPS-DECLARATION.md`).

### Read (alternates; seconds; stdlib python3, repo root)

```
python3 - <<'EOF2'
import json
d = "experiments/gen2-trunk-training-2026-10-18/artifacts/"
for s, upd, ticks, first, last, mn, mx in (("s8", 299, 921600, None, None, None, 392),
                                           ("s9", 2604, 8002560, 0.8290, 0.8800, 0.8096, 227),
                                           ("s10", 2604, 8002560, 0.8275, 0.8782, 0.8169, 179),
                                           ("s11", 99, 307200, None, None, None, 371)):
    rows = [json.loads(l) for l in open(d + f"ppo-g2-trunk-{s}/metrics.jsonl")]
    tr = [r for r in rows if not r.get("probe")]
    pr = [r for r in rows if r.get("probe")]
    assert (tr[-1]["update"], tr[-1]["ticks"]) == (upd, ticks), (s, tr[-1]["update"], tr[-1]["ticks"])
    ret = [r for r in tr if r.get("ep_return_mean")]
    if first is not None:
        assert (round(ret[0]["ep_return_mean"], 4), round(ret[-1]["ep_return_mean"], 4)) == (first, last), s
        assert round(min(p["nash"] for p in pr), 4) == mn, s
    assert max(p["max_distress_streak"] for p in pr) == mx, s
print("alternates fence: all cells match")
EOF2
```
