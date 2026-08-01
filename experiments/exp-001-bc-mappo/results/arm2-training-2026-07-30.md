# Arm 2 — MAPPO fine-tune: training + certification record (2026-07-30)

Six runs per prereg §7.4 (γ ∈ {0.995, 0.998} × training seeds 1–3;
settings per §5 + deviation 30), 20M env-ticks each, trained overnight on
this machine with the owner's authorization. Trainer at branch commit
82287e9; BC warm start from the Arm 1 clone (PR #69), critics from the
γ-matched pretrains. **All six runs' full diagnostics are in
`artifacts/arm2-*/metrics.jsonl`; all six certifications in
`artifacts/arm2-*/certification.{json,txt}`.** Artifacts are gitignored
and regenerable: `train_ppo.py --gamma <γ> --seed <s>` is deterministic
per (γ, seed, segmentation); segment boundaries are in the metrics logs.

## Training diagnostics (§10.1) — all six runs

Uniformly healthy during training: entropy declined gradually from the
softened-clone level (~0.93 → 0.30–0.36 at end, no cliff); KL-to-clone
grew smoothly through the leash decay and settled at 1.1–1.4 nats after
release at 20% (no explosion — RL discovered real behavior change);
critic EV held 0.98–0.99 through the training phase, dipped to ~0.1–0.7
at the default-world anneal transition (the transfer gap made visible
through the roster-4 state adapter) and recovered to 0.66–0.94; clip
fraction 0.01–0.03 throughout; training-world episode returns rose from
clone level to 0.91–0.94 vs the 0.881–0.883 `needs_driven` anchor.
Default-world 2k-tick probes plateaued at 0.937–0.943 for **every** run.
Mask-violation rate of the unmasked argmax stayed ~0.6–0.8 (the policy
still leans on the mask crutch; noted, §10.1 watch item).

## Certification (§8: seeds 1–10, 20k ticks, both rosters, greedy)

Aggregate paired deltas vs `needs_driven` (full per-seed tables in the
JSONs):

| Run | AllSubject Δ | Mixed Δ | Bound-violation lines | Zero fallbacks |
|---|---|---|---|---|
| γ=0.998 s1 | **+0.0112** | +0.0071 | 7 | ✓ |
| γ=0.998 s2 | **−0.366** (0.31–0.90 welfare, 9/10 seeds negative) | −0.002 | 185 | ✓ |
| γ=0.998 s3 | **+0.0212** (10/10 seeds positive) | +0.0096 (10/10) | 4 | ✓ |
| γ=0.995 s1 | +0.0055 (8/10) | +0.0050 (9/10) | 58 | ✓ |
| γ=0.995 s2 | **+0.0157** (10/10) | +0.0081 (10/10) | 6 | ✓ |
| γ=0.995 s3 | −0.0325 (one −0.49 seed; 9/10 positive) | +0.0087 (10/10) | 25 | ✓ |

Artifact sha256 (deploy identity): 0.998 s1 `02b60306…`, s2 `1f7549b4…`,
s3 `bbaf5f8b…`; 0.995 s1 `3774e1aa…`, s2 `d0a44a33…`, s3 `0f0cb995…`.

## Reading (against §2/§9 — preliminary; report protocol still owed)

1. **The primary endpoint is achievable**: 4 of 6 runs beat the baseline
   on aggregate AllSubject Nash, best +0.0212 with every certification
   seed positive both rosters (γ=0.998 s3). This is the first policy to
   exceed `needs_driven` on its own turf. H0a (RL adds nothing) is not
   the outcome; neither is H0b (no run fell below clone level on Mixed).
2. **No run passes certification as-is**: the zero-violation must-pass
   gate fails everywhere. The best runs (0.998-s3: 4 lines; 0.995-s2: 6)
   fail on short least-happy streaks (45–134 ticks below 45) and
   distress ages slightly over limit (178–208 vs 150) in a minority of
   seeds. Per §9.4 this diagnoses as a **fairness/attention residual**,
   not a travel-timing failure — the bounds that fire are least-happy
   streaks, not journey-related.
3. **A long-horizon instability mode exists that training diagnostics
   cannot see**: 0.998-s2 and 0.995-s3 carry catastrophic AllSubject
   seeds (welfare 0.31–0.69) while their 2k-tick probes read a healthy
   ~0.94 — the failure develops beyond the probe horizon. Echo of the
   probe-length lesson (600→1,200 ticks, handoff decision 2): horizons
   keep needing to be longer than assumed. Mixed rosters are immune in
   all six runs (scripted teammates arrest the spiral).
4. Seed variance is the dominant effect (−0.37 to +0.02 spans the same
   hyperparameters) — the prereg's all-seeds reporting rule is doing
   exactly the work it was written for.

## Not yet done

- §8 report protocol (seeds 1..30, Wilcoxon + effect size, per-seed
  table) — the registered endpoint analysis.
- §11 deadline-binge check; policy-seated twin probe (F-003/F-006
  triggers are now armed: a policy exceeds `needs_driven`).
- Register updates (FINDINGS.md) — nothing recorded until the owner
  reviews this record.

**Figure (added 2026-08-01):**
[figures/seed-lottery.png](figures/seed-lottery.png) — all 15 Arm 2/3
training curves, certified winners highlighted.
