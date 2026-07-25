# Experiment 001 — Pre-registration: BC-initialized MAPPO vs `needs_driven`

**Status**: Pre-registered (frozen before first training run)
**Date**: 2026-07-25
**Owner**: Elizabeth Kelly
**Depends on**: spec 014 stack (v2.1), `training.toml`, spec 017 eval suite (exam configs optional for this experiment)

This document is frozen once the first training run starts. Deviations are
recorded in a "Deviations" appendix, never edited into the body. Results are
written against this document, whichever way they land.

---

## 1. Background and motivation

`needs_driven` is a per-kitty greedy heuristic near the achievable ceiling on
*mean* happiness in the default world. Nobody in the current meadow optimizes
the *team* objective (Nash welfare — the geometric mean of unclamped
happiness), and no hand-written cat ever trades a cheap personal gain for the
roster's least-happy member. The feasible RL win is therefore a **fairness and
coordination** win, not a mean-happiness win: yielding contested resources,
duet scheduling (the odd-one-out rotation), and prioritizing whoever drags the
geometric mean.

## 2. Hypotheses

- **H1**: A parameter-shared masked MLP trained with BC-initialized MAPPO
  achieves a higher paired Nash-welfare aggregate than `needs_driven` on the
  default world, with the gain concentrated in least-happy-kitty happiness
  rather than mean happiness.
- Distinguishable null outcomes (each triggers a different follow-up, §10):
  - **H0a**: candidate ≈ BC clone > random — imitation succeeded, RL added
    nothing (signal problem).
  - **H0b**: candidate < BC clone — fine-tuning destroyed the clone
    (BC-collapse).
  - **H0c**: candidate ≈ baseline everywhere — transfer problem
    (gym-to-default-world gap).

## 3. Arms

| Arm | Policy | Role |
|---|---|---|
| 0 | Uniform-random over masked actions | Sanity floor; plumbing check |
| 1 | BC clone of `needs_driven` | Control: isolates what RL adds |
| 2 | BC init → MAPPO fine-tune | Candidate |
| 3 (optional) | MAPPO from scratch | Was BC necessary? Run if budget allows |

Three training seeds per learning arm. **All three are reported**; best-seed
reporting is a protocol violation.

## 4. Fixed factors (identical across arms)

- **Policy net**: MLP 182→256→256→40, masked categorical head. Must remain
  exportable via the policy-artifact format (deployment constraint — verify
  shapes against `contracts/policy-artifact.md` *before* training).
- **Critic** (arms 2–3): separate MLP on the global state (`env.state()`);
  discarded at export.
- **Reward**: level Nash (`p = 0`, `epsilon = 0.01`), no shaping. Never
  changed mid-experiment.
- **Episodes**: horizon 2,000, truncation-only. Value targets bootstrap at
  truncation (see §11 checklist).
- **Training worlds**: `training.toml` family (5-kitty 24×24 center;
  roster/size variants per the config-family generator). Training seeds drawn
  from ≥ 1,000 — **disjoint from eval seeds** (certification 1..10,
  reporting 1..30).
- **Mixed control**: 25–50% of vectorized envs run 1–2 scripted kitties.
- **Anneal**: final ~15% of training steps on the default-world config.
- **Budget**: 20–50M env steps per run; 8–16 vectorized worlds.

## 5. Pre-registered hyperparameters

Swept: **γ ∈ {0.99, 0.995}** — the one sweep, narrowed or confirmed by the
twin probe (§6) before spending compute. Everything else fixed:

| Setting | Value | One-line rationale |
|---|---|---|
| GAE λ | 0.95 | Direct-credit window γλ ≈ 18 ticks; validated against probe bulk |
| PPO clip | 0.2 | Canonical; not tuned first |
| Entropy coef | 0.01, linear anneal → 0.001 floor | Priced certainty; BC init arms the collapse trap |
| Learning rate | 1e-4 + warmup | BC init: good policy + rough critic = gentle steps |
| KL-to-clone | annealed to 0 over first 20% of steps | Leash while critic calibrates; dissolves so policy can surpass teacher |
| Critic pretrain | MC returns from BC rollouts, before any PPO step | Cheapest insurance against BC-collapse |
| BC softening | label smoothing / temperature so clone entropy > 0 at init | A zero-entropy start is pre-collapsed |
| Rollout fragment | 256 steps | ≫ 18-tick direct window; GAE bootstraps at fragment edge |

## 6. Pre-experiment measurement: the counterfactual twin probe

Before any training: measure the environment's credit horizon empirically.

**Procedure**: replay a recorded rollout through the joint-action seam twice,
identical except one forced substitution (idle instead of the chosen action)
at tick t for one kitty. Diff the twin reward trajectories. Sample a few
dozen (t, kitty, world-seed) cells across the training family; plot per-sample
divergence traces and the median/95% envelope.

**Decision rules**:
- The envelope **tail** (longest ticks with non-noise divergence) sets γ: tail
  ≤ ~100 ticks licenses γ = 0.99; a fairness tail past ~300 supports 0.995.
- The envelope **bulk** (where most divergence mass sits) validates the γλ
  direct window (~18 ticks at defaults); bulk under 5 ticks licenses λ = 0.9.

Report the envelope plot alongside experiment results regardless of outcome.

## 7. Training protocol

1. **BC dataset**: mixed-control rollouts of `needs_driven` across the
   training family; 1–2M kitty-decisions; record (observation, mask, expert
   action index via the codec's `encode`; drop inexpressible actions —
   log the drop rate, expect < 1%).
2. **Clone**: masked cross-entropy to plateau on masked top-1 accuracy, with
   softening (§5). Record accuracy, entropy at convergence, and the clone's
   full evaluation (it is Arm 1).
3. **Critic pretrain**: fit to discounted MC returns of the BC rollouts.
4. **PPO fine-tune** (Arm 2): settings per §5; mixed-control fraction per §4;
   default-world anneal for the final 15%.
5. Export each finished policy as an artifact; record content hash.

## 8. Evaluation protocol

- **Certification** (pass/fail, run once per finished arm×seed, never inside
  a tuning loop): `kitty-eval` as shipped — 20,000 ticks, seeds 1..10,
  default world, both roster modes, all welfare bounds, zero fallbacks.
- **Report protocol** (statistics): seeds 1..30, paired per-seed differences
  (arm − `needs_driven`, same seed), Wilcoxon signed-rank + effect size,
  full per-seed table published.
- **During training** (cheap validation, not certification): periodic
  2,000-tick runs on the default world tracking Nash aggregate and distress
  age (the transfer-gap curve).

**Endpoints** — primary: paired Nash-welfare aggregate. Secondary:
least-happy kitty mean, distress age, plain mean happiness. **Guardrails**
(must-pass, not scores): all welfare bounds, zero fallback-taken decisions,
determinism self-check.

## 9. Decision rules (pre-registered)

1. Arm 2 > baseline on primary, guardrails pass → deployment soak (one policy
   kitty in the served world, days).
2. Arm 2 ≈ Arm 1 > Arm 0 (H0a) → harden the training family (rates,
   scarcity); do **not** touch the objective.
3. Arm 2 < Arm 1 (H0b) → stronger KL anchor / slower LR; not more steps.
4. Guardrail failure with good endpoints → diagnose by *which* bound:
   distress-age → travel-timing transfer; least-happy → fairness failure;
   mixed-roster-only failure → more mixed-control training.

## 10. Diagnostics and visualization (for the evaluation harness)

Everything below should be logged/plotted by default. For each: the plot,
the question it answers, and what pathology looks like.

### 10.1 Training-time (logged per update; plotted as curves, all 3 seeds overlaid — never best-seed)

| Metric / plot | Question it answers | Healthy | Pathology |
|---|---|---|---|
| Nash return per episode (training world) | Is learning happening? | Gradual rise from clone level | Flat at clone level (H0a forming); cliff after leash release (H0b) |
| Validation curve: Nash + distress age on default world (2k-tick probes) | Is the gym transferring? | Tracks training curve with small gap | Growing gap = transfer problem forming |
| Min-kitty happiness + per-kitty spread | Is the fairness win happening? | Spread narrows over training | Spread widens: policy farms easy kitties |
| **Masked** policy entropy | Premature certainty? | Starts at softened-clone level, declines gradually | Cliff-drop early (collapse); flat-high forever (coef too high) |
| KL to frozen clone | Is RL discovering anything? | Grows steadily after leash anneals | ≈0 after leash gone → RL adds nothing; explosion at release → LR too hot |
| Critic explained variance (EV) | Can we trust bootstrapping/GAE handoff? | Rises to > 0.7 and stays | Low + sluggish learning: fix critic before touching λ |
| Advantage mean/std (pre-normalization) | Estimator stability | Std stable within phase | Wild swings: too much Monte Carlo in the mix |
| Clip fraction, grad norm, value loss | Standard PPO health (37-details) | Clip fraction ~0.1–0.3 | Clip fraction ≈0 (dead updates) or ≈1 (steps too big) |
| Mask-violation rate of *unmasked* argmax | Has the policy internalized legality? | Declines over training | Stays high: policy leans wholly on the mask crutch |
| Journey-length distribution vs `needs_driven` (histogram, periodic) | Myopia detector (γ too low) | Similar or longer journeys | Truncated right tail: under-invests in travel |
| Distress events per training episode | Welfare during learning | Declines to ≈ baseline | Persistent spikes localized to one kitty: fairness failure forming |

### 10.2 Evaluation-time (harness outputs, per arm)

| Plot | Question it answers | Notes for the harness |
|---|---|---|
| Paired per-seed difference plot (arm − baseline Nash, seed on x, CI band) | The primary endpoint, honestly | The single most important figure; per-seed table alongside |
| Least-happy-identity histogram (which kitty was least happy, per seed) | Is unhappiness *systematic*? | Concentration on one kitty (esp. a scripted one in mixed mode) = exploitation signature |
| Per-kitty happiness percentile bands over the 20k run (P5/P25/P50) | Distributional welfare, not just means | Overlay baseline's bands, same seed |
| Welfare-bounds panel (existing suite metrics × arms) | Guardrail summary | Reuse `kitty-eval` report fields verbatim |
| Mixed vs all-policy roster comparison (paired) | Ad-hoc teamwork gap | Guest-welfare differential if 017's mixed exam lands in time |
| Twin-probe divergence envelope (per-sample traces + median/95%, log-y) | The credit-horizon measurement (§6) | Annotate 1/(1−γλ) and 1/(1−γ) as vertical reference lines |
| Fallback count (must be zero) + determinism check status | Guardrails | Nonzero fallback = failed run, full stop |

### 10.3 Reproducibility manifest (attached to every figure and run)

Code commit, config path + content hash, generator version + sampler seed
(for family variants), artifact hash, eval seed set, γ value, training seed.
A figure without a manifest line is not evidence.

## 11. Threats-to-validity checklist (verify before run 1)

- [ ] Truncation bootstrapped (episode cut ≠ termination) — in GAE too
- [ ] Mask applied consistently: sampling, log-probs, **and** entropy
- [ ] Training seeds ≥ 1000; eval seeds 1..30 never trained on
- [ ] Clone entropy > 0 at PPO start (softened BC)
- [ ] Critic pretrained before first PPO update
- [ ] Certification runs kept out of any tuning loop
- [ ] Episode-clock feature: pinned 0 at deploy — check the policy doesn't
      exploit horizon proximity (compare behavior in first vs last 200
      episode ticks; a "deadline binge" pattern predicts deployment weirdness)
- [ ] Artifact export verified for the exact layer shapes before training

## 12. Reading list

Sutton & Barto ch. 1/3/13; Spinning Up (PPO); Schulman et al. 2017 (PPO,
arXiv:1707.06347); Schulman et al. 2016 (GAE, arXiv:1506.02438); Yu et al.
2022 (MAPPO, arXiv:2103.01955); Huang et al. 2022 (*The 37 Implementation
Details of PPO*); Huang & Ontañón 2020 (invalid-action masking,
arXiv:2006.14171); Ng et al. 1999 (potential-based shaping); Ross et al.
2011 (DAgger); Schmitt et al. 2018 (kickstarting); Andrychowicz et al. 2020
(*What Matters in On-Policy RL*).

---

## Appendix: Deviations

*(append entries here, never edit the body)*

### 2026-07-25 — §6 analysis method refined (pre-training)

Recorded before any training run (the freeze has not yet bitten), in the
appendix anyway so the prereg body and the first result read consistently.

- **Sample size**: "a few dozen (t, kitty, world-seed) cells" → 1,000
  valid samples. The probe turned out cheap (~35 s), so there was no
  reason to stay small.
- **Statistic**: per-sample divergence traces with median/95% envelope →
  across-sample mean of *signed* diffs with per-tick significance
  testing (|mean| > 2·SE). Rationale: chaotic diffusion is
  sign-symmetric and only cancels in the signed mean; single-trace |Δ|
  overstates persistence — an exploratory envelope-style exponential fit
  produced a nonsense τ ≈ 4,900 and is superseded (methodology cautions
  in the result doc).
- **Decision-rule mapping**: §6's envelope "tail" is read as the last
  contiguous significant band (isolated late blips judged against the
  multiple-testing base rate); the "bulk" is read as significant-mass
  fractions. Applied in
  [results/twin-probe-2026-07-25.md](results/twin-probe-2026-07-25.md):
  tail lands between the two thresholds → the γ sweep proceeds, with
  0.995 registered as the predicted winner.
- The §6 envelope plot is still owed as a figure (see the result doc's
  follow-ups); the decision rules were exercised on the significance
  bands, not the envelope.
