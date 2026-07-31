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

### 2026-07-27 — v2.4 accepted; Cuddle diagnosis flipped; baseline retune (pre-training)

Recorded before any training run, in the appendix per the precedent above.
Three developments, in the order they landed:

**1. Product handover accepted (refactor arc 018–020, tagged v2.4).** The
"Depends on" line's v2.1 reads as v2.4: bit/byte-identical refactors only,
verified from this side by review. The seat-0 convention (Mixed mode always
seats the subject at kitty index 0) is noted as fair for paired comparison;
seat rotation is a v2 nicety, not a threat.

**2. Cuddle diagnosis corrected (spec 021 withdrawn 2026-07-27).** Planning
around this experiment briefly carried a "welfare Cuddle bound produces
false positives beside busy friends" premise. It is false: busy neighbors
*are* lawful cuddle relief — `Sleep{with}` and `Groom{target}` validate on
adjacency alone and bind nobody, and both routes sit in the 40-action menu
and are masked-in on adjacency. No confound note enters this prereg and no
certification gate exists. The standing interpretation rule instead: **a
trained arm showing Cuddle pinned streaks beside busy friends failed to
learn the non-binding social routes** — a real skill gap the certification
bound correctly punishes, diagnosed under decision rule §9.4 as a fairness/
transfer failure, never as an eval bug. (Candidate finding F-002 —
`needs_driven` itself under-uses these routes; the 38 events spec 021
miscounted as false positives were real refusals — awaits a recount on the
retuned baseline below before any registration.)

**3. Baseline retune ([PR #60](https://github.com/CloudKitty-ai/cloudkitty/pull/60),
cf82007, 2026-07-27).** Owner rebalance toward companionship: happiness
weights eat/drink 0.25→0.20 and cuddle/bath 0.10→0.15; `groom_relief`→20,
`play_relief` 25→20, `cuddle_relief` 20→15 — applied to the compiled
defaults, which `training.toml` and the frozen `evals/v1` exams inherit.
Consequences for this prereg:

- **F-001's quantities are stale for this experiment.** The two-channel
  numbers behind §5/§6 (teammate band 50–200 peaking k≈106; discounted
  team-signal retention 0.59 at γ=0.995 vs 0.38 at γ=0.99) were measured
  pre-retune. The probe re-runs on the retuned baseline before any compute
  is spent on the γ sweep; γ=0.995 stands as the *predicted* winner — the
  retune plausibly strengthens it (slower social relief lengthens scenes;
  cuddle/bath weigh 1.5× more in the reward), but the decision inputs are
  the fresh run's, whichever way they land. F-001 gets a confirm-or-
  supersede verdict in FINDINGS.md from that run.
- The planned bit-identical regeneration diff of the committed probe data
  against v2.4 is superseded: trajectories moved deliberately with the
  retune, so a byte diff no longer verifies anything.
- `needs_driven` anchor on the retuned defaults: 3-seed 20k-tick
  certification probe means ≈ 90.2–90.6 (PR #60 verification note). §1's
  "near the achievable ceiling" reads against these numbers now.
- Pre- and post-retune suite results are not comparable even though the
  frozen exam hashes still validate. Suite reports now stamp
  `engine_defaults_sha256`
  ([PR #61](https://github.com/CloudKitty-ai/cloudkitty/pull/61)); every
  result written against this prereg must come from a stamped post-retune
  run, and the §10.3 reproducibility manifest gains that stamp as a
  required field.
- The retuned baseline sits untagged at time of writing; results cite the
  merge commit until Product tags it (v2.5 recommended).

### 2026-07-27b — γ sweep amended; training world frozen by measurement (pre-training)

Still pre-freeze; recorded with the owner's approval of the probe-guided
search plan ("reduce element count… improve the ability to train").

- **§5 amendment — the swept γ set is {0.995, 0.998}** (was {0.99, 0.995}).
  Basis: F-003 (post-retune credit horizon: γ=0.99's horizon ends before
  the cooperative band begins, retaining 0.10 of team signal — sweeping
  it would spend a third of the compute proving an arm blind by
  construction) and F-005 (the frozen world's replicated band is late,
  k ≈ 730–940, favoring 0.998; 0.995 covers state-mediated credit
  arriving earlier than probe-visible reward effects). λ, clip, entropy,
  LR, KL-to-clone, fragment length: unchanged.
- **§4 amendment — `training.toml` is the probe-searched scarcity×tempo
  world** (rates ×1.5 of engine defaults, water/chow 3–4, sunbeams 2),
  frozen 2026-07-27 after a 10-candidate search under cluster-robust
  statistics with disjoint-world replication (F-004 discipline; F-005
  result; full method and table in
  [results/world-search-2026-07-27.md](results/world-search-2026-07-27.md)).
  `needs_driven` anchor on the frozen world: team welfare 0.881–0.883,
  all welfare bounds pass (3 seeds × 20k). The §8 evaluation protocol is
  untouched — certification and reporting stay on the default world.
- **§6 note**: probe significance analysis now clusters by world seed
  (F-004); `analyze.py`'s per-sample method is superseded for
  significance claims. The §6 decision rules were re-exercised on the
  frozen world under the new statistics.
- H0a contingency sharpened (decision rule §9.2): hardening steps come
  from the search's measured Pareto table with fresh measurement, not
  ad hoc.

### 2026-07-27c — critic-pretrain targets made truncation-aware (pre-training)

Episode length stays 2,000 (bootstrapping decouples the credit window
from the episode boundary, and resets are cheap state diversity). But the
critic-pretraining step (§7.3) fits **Monte-Carlo** targets, which have no
bootstrap: a state 500 ticks before rollout end is missing γ^500 ≈ 37% of
its return scale at γ = 0.998, and with the frozen world's slow band at
k ≈ 730–940 that censoring lands exactly on the cooperative consequences
the critic must learn. Amendment to §7:

- **BC-dataset rollouts run long** (6,000–10,000 ticks) rather than
  episode-length.
- **Pretraining targets are fit only on states with ≥ 1,500 ticks of
  realized future**; later states are dropped from the regression (they
  remain in the BC classification dataset — the censoring bites value
  targets, not action labels).

PPO fine-tuning itself is unchanged (horizon 2,000, fragment 256,
bootstrap at every cut).

### 2026-07-29 — BC-clone discretionary settings pinned; freeze reading (pre-training)

§5 leaves the clone's own optimization knobs to trainer's discretion
("masked CE to plateau", softening amount unspecified). Recorded here
*before* the first full clone run so the freeze has a clean edge:

- **Freeze reading**: "the first training run" = the first full-dataset
  clone run (Arm 1 is a registered result). Debug smoke runs on subset
  data, whose outputs feed nothing downstream, do not bite the freeze.
  The first full run starts immediately after this entry.
- **Clone**: Adam lr 3e-4, batch 4096, ≤ 20 epochs with patience-3
  plateau stop on masked val top-1, seed 20260729. Label softening:
  ε = 0.05 spread uniformly over each row's *legal* actions only
  (smoothing never fights the mask; converged entropy > 0 by
  construction, per §11).
- **Split**: by rollout, never by row (rows within a rollout share one
  long-lived world — F-004's correlation logic applied to BC).
  Validation = `rollout-04` of every config (9/45 rollouts ≈ 20%): all
  9 family variants appear in both splits, no world seed shared.
- **Critic pretrain**: Adam lr 1e-3, batch 4096, ≤ 60 epochs with
  patience-5 plateau stop on val MSE; one critic per γ ∈ {0.995, 0.998};
  targets per deviation 27c, normalized on train-split statistics
  (mean/std recorded in the artifact and stats JSON).
- Implementation: `trainer/` (PyTorch — the repo's first ML framework
  dependency, confined to `experiments/`), verified pre-training by a
  numpy-forward parity check against the exported artifact and a seated
  smoke run through `kitty-eval`.

### 2026-07-29b — clone epoch cap raised 20 → 60 (post-freeze)

The first full clone run hit the 20-epoch cap pinned above with val top-1
still climbing (0.7493 at epoch 20, +0.5 pt over epoch 19 — no plateau).
§7.2's frozen criterion is "masked CE **to plateau** on masked top-1
accuracy"; the discretionary cap contradicted the body and loses. Cap
raised to 60, patience-3 stop and every other setting unchanged, rerun
from the same seed (epochs 1–20 reproduce identically, training then
continues to the §7.2 plateau). Recorded before the extended run started;
the 20-epoch checkpoint was not evaluated further and feeds nothing.

### 2026-07-29c — clone epoch cap removed; the patience criterion terminates (post-freeze)

Epoch 60 was still not a plateau (val top-1 0.8013, ~+0.04 pt/epoch and
decelerating; val loss still falling — no overfitting signal, and the
patience stop keeps the best-val epoch regardless). Same lesson as 29b
one level up: any hand-picked cap is a guess that fights §7.2. The cap is
removed (set far above reach at 300); the pinned patience-3 / 1e-4 stop
on masked val top-1 — which *is* §7.2's plateau criterion made
executable — terminates the run. All other settings unchanged, rerun
from the same seed; epochs 1–60 of the prior runs reproduced exactly
(deterministic), so this extends rather than replaces them. The 60-epoch
checkpoint feeds nothing.

### 2026-07-30 — Arm 2 (MAPPO) discretionary settings pinned (post-freeze, pre-Arm-2-run)

§4/§5 pin the architecture, γ set, λ, clip, entropy schedule, LR, leash,
fragment, world/mixed-control bands, and budget band; the remaining knobs
are recorded here *before the first Arm 2 training run* (smoke runs on
toy settings exempt, per deviation 29's precedent). Trainer:
`trainer/ppo_env.py` + `trainer/train_ppo.py`.

- **Env step** = one tick of one world; **20M per run** (bottom of §4's
  20–50M band). Fragment 256 × 12 worlds = 3,072 ticks/update.
- **Worlds (12)**: 8 all-external cycling `training.toml` + the family-v1
  variants; 2 with one scripted kitty, 2 with two (scripted = lowest ids,
  `needs_driven`) → 33% mixed-control, inside §4's 25–50% / 1–2 band.
- **Seeds**: world seed base 1,000,000 + training-seed×100,000
  (+1,000/resume segment, +50,000 in the anneal phase), bare-reset chains
  thereafter — ≥1,000 and disjoint from eval seeds per §11. Validation
  probes use 40,001–40,003 (never trained on, not eval seeds): greedy,
  3 × 2,000 ticks on the default world, every 50 updates.
- **PPO internals**: 4 epochs × 4 minibatches per update; advantages
  normalized per update batch (pre-normalization stats logged per §10.1);
  no value clipping; value coef 0.5; grad clip 0.5; actor and critic
  updated by decoupled Adam optimizers, both on §5's 1e-4 with linear
  warmup over the first 2% of updates. KL-to-clone leash starts at
  β = 0.5 (β0 discretionary; §5 pins the anneal-to-0-by-20% schedule).
- **Critic warm start**: pretrain normalizer (mean/std) frozen; value
  regression stays in normalized space; GAE denormalizes.
- **Default-world anneal** at progress ≥ 0.85 (§4's "final ~15%"), mixed
  structure retained; the roster-4 state is adapted to the critic's
  5-kitty layout by splicing a zeroed phantom-kitty block before the
  element tail (layout per `global_state.rs`).
- **Diagnostics as built** (§10.1): Nash return/episode, default-world
  validation curve, masked entropy, KL-to-clone, critic EV, advantage
  mean/std, clip fraction, grad norm, value loss, mask-violation rate of
  unmasked argmax — all per update to `metrics.jsonl`. **Not implemented
  in-training**: journey-length distribution, distress events, min-kitty
  happiness/spread — the Python binding exposes none of these; they are
  covered eval-side (§10.2) instead. Recorded as a known gap, not
  silently dropped.
- **Long-run mechanics**: checkpoint + resume. World state cannot be
  serialized through the binding, so each resumed segment re-seeds its
  envs deterministically; segment indices are logged in `metrics.jsonl`
  and are part of the run record.

### 2026-07-30b — Arm 3 interpretation pinned (post-freeze, pre-Arm-3-run)

§3 lists Arm 3 as "MAPPO from scratch. Was BC necessary? Run if budget
allows." Budget allows (a 20M-tick run costs ~25 minutes on this
machine). Interpretation recorded before the first Arm 3 run:

- **"From scratch" = the whole BC stage removed**: random policy init,
  random critic init, no KL-to-clone leash (there is no clone to leash
  to; β = 0). This tests BC's full contribution — dataset, clone init,
  and critic pretrain together — which is the reading that answers "was
  BC necessary."
- Everything else identical to Arm 2 (deviation 30): same §5 settings,
  same worlds/mixed structure, same seeds, same 20M budget, same anneal.
- **Value normalizer** (Arm 2 inherits the BC pretrain's mean/std, which
  a from-scratch run must not touch): calibrated instead from a
  pre-training rollout — 2,000 ticks of the random policy on the
  training worlds, discounted MC returns on ticks with ≥ 1,000 realized
  future, mean/std frozen from those, worlds rebuilt from the same seeds
  afterward so training still starts at the registered world state.
- Prediction, for the record (owner may disagree; recorded by the
  session running the experiment): Arm 3 fails to reach baseline —
  the zero-artifact's behavior suggests how hostile the environment is
  to uninitialized policies. Whichever way it lands, it calibrates how
  much of Arm 2's result BC bought.

### 2026-07-30c — Arm 2 fresh seeds at 40M ticks; evaluation rule fixed in advance (post-freeze)

**Context, stated honestly**: this is an outcome-dependent decision.
The first Arm 2 cohort (seeds 1–3, 20M ticks) produced three maximal
endpoint wins but zero certification passes — the near-misses failing on
rare transient incidents (forensics in
[report-protocol-2026-07-30.md](results/report-protocol-2026-07-30.md)).
The owner chose the **fresh-seeds** route over extending already-
evaluated runs, precisely because extension would adapt on evaluated
results. Recorded before any new run starts:

- **Cohort**: training seeds 4, 5, 6 (never run before), **γ = 0.998
  only** (two of the three maximal wins including the best; F-003's
  retention analysis favors it), **40M ticks** (within §4's 20–50M
  band). Every other setting identical to deviation 30. Schedules are
  progress-relative, so all phases (warmup, leash release at 20%,
  anneal at 85%) double in absolute length with the budget.
- **Evaluation rule, fixed now**: each finished run is certified once
  (§8, seeds 1–10) and reported once (seeds 1–30, Wilcoxon), whatever
  the outcome. **No extension, no re-run, no further cohort based on
  these results without a new deviation recorded first** — there is no
  extend-until-pass path. All three runs are reported.
- These seeds do not replace seeds 1–3 in the registered Arm 2 record;
  they are an additional cohort answering one question: do the
  transient guardrail incidents wash out with more optimization, or are
  they a property of this policy class at any budget?

### 2026-07-30d — §8's "default world" clarified; served-world re-measurement scoped (post-hoc discovery, pre-re-measurement)

**Context, stated honestly**: forensics
([collapse-forensics-2026-07-30.md](results/collapse-forensics-2026-07-30.md))
discovered that `kitty-eval` invoked without `--config` — as every §8
certification and report run in this experiment was — runs the
**compiled default config (3 kitties, state 133)**, not
`cloudkitty.toml` (4 kitties, 165, the served world). The trainer's §4
anneal phase and §10.1 validation probes targeted `cloudkitty.toml`
throughout: we annealed to one world and certified on another, without
knowing it. **Owner decision (2026-07-30): §8's "default world" means
`cloudkitty.toml` — the world the kitties actually live in. The
compiled default was an accident, not a design choice.**

Recorded before any re-measurement run starts:

- **Rule going forward**: every §8 certification and report-protocol
  invocation passes `--config cloudkitty.toml` explicitly. (A product
  ask is filed to make `kitty-eval`'s bare default non-ambiguous.)
- **One-time served-world re-measurement, winners-first scope**: the
  three maximal-Wilcoxon-win artifacts — arm2-g0p998-s3 (20M), s4 and
  s6 (40M) — are certified once (§8, seeds 1–10) and reported once
  (seeds 1–30, Wilcoxon) on `cloudkitty.toml`. Paired `needs_driven`
  baselines are internal to `kitty-eval` and run on the same config.
  Whether the remaining artifacts (other Arm 2 seeds, clone, Arm 0
  anchors) are re-measured is decided *after* these results and
  recorded as a further note — the winners-first split is the owner's
  scoping call, made before seeing any served-world number.
- **Relation to deviation 30c's evaluate-once rule**: not a re-run.
  The intended measurement has never been taken; each artifact gets
  exactly one evaluation per world. The compiled-world numbers stay in
  the registered record as what they are — measurements of the compiled
  3-kitty world, reinterpreted as an out-of-roster robustness screen
  (one obs kitty-slot empty: an input outside training support).
- **The compiled world is retained** as an explicitly-named secondary
  robustness screen (roster-OOD), never again the primary gate.
