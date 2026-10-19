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
