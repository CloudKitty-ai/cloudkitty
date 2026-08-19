# PPO port + wave-1 launch record (2026-08-19)

Everything pre-wave from the frozen prereg is complete; this doc
records the instruments built for the waves, the numbers banked
before them, and the wave-1 launch state. Recipe discretion values
are in prereg D-002 (the pre-training note); this doc holds the
measurements.

## Instruments

**`trainer/train_ppo6.py`** — the exp-005/A1 recipe forked to the
post-wall surface (obs 225 / activity 34 / message head 16). Deltas
from exp-005 are model plumbing plus the frozen §4 arm table and the
E1 estimator aux head; every PPO quantity is the recipe's (D-002
restates them). Committed at `f3b813e`.

**`trainer/train_critic6.py`** — the attn-critic recipe retrained on
dataset v5 cell B (the training family's data). γ 0.998, censored MC
targets (min_future 1500), 585,090 train / 117,018 val states.
Result: **best epoch 2, val EV 0.7271** (pre-wall comparables on
record: MLP 0.53, attn 0.555 — this is the strongest critic fit we
have banked; plausibly the roster-strata padding plus trait spreads
make value more state-identifiable, but that reading is unverified).
Artifact
`critic6-0p998.pt` sha256 `29348315…`; stats committed at
`results-raw/critic6-0p998-stats.json`. The fast convergence then
overfit (val MSE rises after epoch 2) is best-state-saved; the PPO
loop keeps training it online.

**Smoke record** (all on subset ticks, exempt per the freeze note):
all three arm shapes (E1/E0/L-04) ran end to end on 4 worlds ×
fragment 64 with short horizons exercising truncation; the wall-limit
checkpoint + `--resume` path continued a run across a segment
boundary with the seed chain re-based as designed. Deliberate reds:
the calibration instrument returned exactly 0 on aligned estimates,
caught a one-target roll, and counted no padded pairs (unit
red/green); the init-key assert was driven red through the real
trainer path with an extra-key checkpoint (`AssertionError:
['bogus']`) — the first red attempt failed for the wrong reason
(torch's shape check fired upstream), so the assert was re-redded on
a shape-compatible checkpoint.

## E-arm init banked (clone-spread)

`probe-spread` resumed past its 20-epoch price-probe cap to the
patience-3 plateau (identical recipe/data/seed; the cap was a
fairness device for the §3e comparison, not a recipe term):
**best epoch 33, val 0.8822, act@1 0.8229, msg@1 0.9994** — act@1
+0.76pp over the capped probe clone. Artifact `clone-spread.pt`
sha256 `0d1c68b0…`.

**Fingerprint** (fingerprint_probe6, band 985001–010, demonstration
composition on `collect-config.toml`, greedy; committed at
`results-raw/fingerprint-clone-spread.json`), ratios to the scripted
anchor:

| metric | clone-spread | scripted anchor | ratio |
|---|---|---|---|
| play_share | .6918 | .638 | 1.08× |
| time_near_critters | .4540 | .430 | 1.06× |
| bug_over_meal | .2925 | .302 | 0.97× |
| duet_initiation/1k | 214.88 | 179.7 | 1.20× |
| subject_happiness | 79.43 | 79.64 | — |
| team_happiness | 88.29 | 88.35 | — |

Near-identical to the anchor clone's fingerprint (play .686, duets
214.9), as two greedy V4 clones of the same scripted family should
be. Context only for the E arms — G3 formally gates lineage
candidates — but every G3 floor clears pre-PPO here too.

## Wave 1 launched

Four runs, one per §4 arm, seed 1, 20M ticks each, at git
`f3b813e`, started 2026-08-19:

| run | seed_base | first probe (u49) |
|---|---|---|
| ppo-E1-s1 | 100,000,000 | nash .8870, meow/1k 43.8 |
| ppo-E0-s1 | 140,000,000 | nash .8864, meow/1k 44.2 |
| ppo-L-04-s1 | 180,000,000 | nash .8868, meow/1k 43.1 |
| ppo-L-05-s1 | 220,000,000 | nash .8909, meow/1k 39.5 |

Health at launch verification: EV 0.97–0.99 from the pretrained
critic, KL-to-anchor ~0.02–0.03, episode returns .87–.88 on the
spread family (stress cells run under the served-world ~0.90 by
design), E1 aux MSE 0.243 → 0.021 within 80 updates. Pace ~8.2
s/update with four concurrent → ~15 h/run; wave 2 (the seed-2 four)
launches when wave 1 drains. Per-run stdout is buffered until exit
(a tail-piping mistake at launch, again); `artifacts/ppo-*/`
`metrics.jsonl` is the live record and carries everything, including
the E1 per-pair calibration rows.

## Regeneration

```
cd experiments/exp-006-character-gen
# critic
.venv/bin/python trainer/train_critic6.py --threads 6
# E-arm init (resume probe-spread past cap under the production name)
mkdir -p artifacts/clone-spread && cp artifacts/probe-spread/ckpt.pt artifacts/clone-spread/
.venv/bin/python trainer/train_clone6.py --name clone-spread --data-root raw/v5-spread --resume --epochs 40 --threads 8
# fingerprint
.venv/bin/python fingerprint_probe6.py --subject artifacts/clone-spread/clone-spread.pt --name clone-spread
# waves (one per arm x seed)
.venv/bin/python trainer/train_ppo6.py --arm E1 --seed 1 --threads 4
```

## Housekeeping note (shared checkout)

Untracked/staged Client-thread camera and zoom files were found
sitting staged on the main checkout and were swept into an aborted
local commit during this launch's push; they are preserved verbatim
on branch `rescue/client-wip-staged-on-main-2026-08-19` (never
pushed as part of exp-006 history) and appear to duplicate work
already merged via Client PRs. Reconciling or deleting that branch
belongs to the Client thread/owner, not Experiments.
