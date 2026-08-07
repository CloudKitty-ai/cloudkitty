# Experiment 003 — Pre-registration: the in-water observation bit

**STATUS: FROZEN 2026-08-06** (owner authorization, PR #115). This
commit is the freeze. From here the registered text does not change —
outcomes and deviations are *recorded*, never edited in, and no
criterion is weakened after the fact. The exp-002 precedent holds: a
falsified hypothesis keeps its original wording with the result quoted
beneath it.

**Frozen against**: engine `5a6a3f5`, engine-defaults stamp
`cba976dae4b88703…`; family seed `20260807`, manifest sha256
`3be3578daa969c8d…`; family-gen v4.

**Engine**: pinned at `5a6a3f5`, engine-defaults stamp
`cba976dae4b88703f5cff8028a54db24efde6a5cfe8d79dcdbb3948151751b03`.
**Predecessor**: [exp-002](../exp-002-mixed-population/prereg.md).
**Carry-forward register**: [exp-003-design-inputs.md](../exp-003-design-inputs.md)
— every item there is adopted and cited below, consciously rejected, or
deferred.
**Re-baseline**: [rebaseline-2026-08-06/results.md](../rebaseline-2026-08-06/results.md).

---

## 1. Background and motivation

exp-002 falsified H2: no setting of the wet-fur dial bought deployed
water avoidance at welfare-neutral cost. One dial unit (1.5 → 2.5) bought
−0.84pp lounging, and linear extrapolation put the registered gates near
dial 4.8–5.6 — three to four times shipped. The escalation clause was
exhausted and the owner conversation held.

The diagnosis was not "turn the dial harder". It was that **the policy
cannot see that it is wet.** Sunbeam occupancy has an explicit self-block
flag; water occupancy had to be inferred from a nearest-water slot
reading zero. A policy asked to avoid a state it cannot observe is being
asked to learn a proxy.

exp-003 adds the flag. That is a §4-forbidden schema change — observation
width 182 → 183, schema 1 → 2 — which voids every warm start and is why
this is a new generation rather than an amendment.

**What changed underneath, and why it reframes the hypothesis.** Three
things landed with the schema bump (specs 026/027): the bit, the dial at
3.5/60, and a guaranteed 2×2 lake with edge-avoiding placement. The
re-baseline then found something nobody predicted (**F-016**): raising
the gain 1.5 → 3.5 *increases* scripted on-water time. Resting, sleeping
and playing on water all fall as intended, but grooming-on-water rises
61% and swallows them, because grooming relieves the Bath need
(`kitty.rs:165`, `action.rs:699`) and the wet-fur charge raises it — a
wet cat wants a bath, a `needs_driven` cat takes it where it stands, and
standing there keeps charging.

Two consequences this document is built around:

1. **The scripted baseline moved up, not down.** Scripted `needs_driven`
   in the policy seats now sits at **1.50% lounging / 3.44% in-water**
   (was 0.31% / 1.63% at dial 1.5 pre-lake). exp-002's registered
   ceiling of ≤ 3.0% in-water is now *below the scripted baseline* —
   carrying it forward would demand the policy out-avoid the ladder it
   is measured against.
2. **In-water share is not one number.** It pools a channel the dial
   suppresses with a channel the dial amplifies. Gated as a single
   scalar, it is uninterpretable.

## 2. Hypotheses

- **H1 (the bit buys what the dial could not)**: with the in-water flag
  observable, trained policies land inside the water band registered in
  §9.1 — which no dial setting achieved for a blind policy (exp-002,
  falsified H2). Direction registered; the margin is exploratory.
  > **H1 SUPPORTED 2026-08-07** ([results/grid-2026-08-07.md](results/grid-2026-08-07.md)): 7/9 candidates inside the band,
  > 9/9 clear of the in-water ceiling, and the best are drier than the
  > scripted ladder itself (2.79% against B of 3.44%). Both failures are
  > the lounging criterion alone. The observation bit bought what no
  > dial setting could.

- **H2 (water behaviour preserved, not eliminated)**: the same band's
  **floor** holds. A policy that never touches water fails H1. Registered
  because the owner's stated preference is explicit and because there is
  no structural floor to rely on: `Activity::Drinking` ends on
  *adjacent* water (`world.rs`) — cats drink from the bank — so
  near-zero water contact is reachable and nothing in the engine
  prevents it.
  > **H2 HOLDS 2026-08-07** ([results/grid-2026-08-07.md](results/grid-2026-08-07.md)): 9/9 above the floor, none close to
  > it. The one-sided-gate failure mode this clause was written against
  > did not occur.

- **H3 (welfare non-regression)**: candidates do not buy water avoidance
  with welfare. Subject team welfare on the served world ≥ the
  same-engine `needs_driven` baseline + 0.02 (the exp-001 certification
  margin was +0.041; +0.02 is half of it, registered as the floor a
  candidate must clear to be considered at all).
  > **H3 SUPPORTED 2026-08-07** ([results/grid-2026-08-07.md](results/grid-2026-08-07.md)): 8/9 at +0.0266 to +0.0423. The
  > one failure (A0-m33-g998-s3, −0.1103) is the run that also collapses
  > under H5.

- **H4 (meow preservation)**: warm-start... **not applicable this
  generation.** The schema change voids warm starts, so every candidate
  is BC-then-PPO from scratch. Channel use is measured and reported
  (F-012: in policy company, not solo), but no threshold is registered —
  there is no predecessor to preserve it *relative to*.
  > **REPORTED 2026-08-07** ([results/grid-2026-08-07.md](results/grid-2026-08-07.md)): greedy `meow/1k` 0.01–0.41 across
  > all nine — the channel was not discovered from exploration in 20M
  > ticks. The reason H4 was dropped is confirmed, not merely assumed.

- **H5 (roster robustness)**: with roster 3–5 stratified in the family,
  no candidate exhibits F-010 catatonia on any deploy-surface roster
  (3/4/5) at certification length. Carried forward from exp-002's H4,
  which was *partially* falsified — the family did not eliminate F-010,
  but the gate caught it. The gate, not the family, is what §9.2
  consumes.
  > **H5 NOT SUPPORTED 2026-08-07** ([results/grid-2026-08-07.md](results/grid-2026-08-07.md)): 0/9 under the registered
  > gate. The gate is satisfiable — `needs_driven` scores 0/0/0 and
  > exp-002 met it with 9 of 22 candidates — so it is not an unmeetable
  > criterion. But the failures are bimodal: six candidates show only
  > trace eat-timing lapses (3–212 threshold-ticks in 100,000), three
  > collapse outright. World shape is ruled out as the cause; the engine
  > route cannot be tested, because schema-1 artifacts do not load here.

- **Anchors (registered predictions)**:
  - `needs_driven` holds **0.9039–0.9054** team welfare on the served
    world (re-baselined 2026-08-06; supersedes the 0.906–0.908 band,
    which no longer describes this engine).
  - Scripted water in the policy seats holds **1.50% / 3.44%** ±
    seed noise (sd 0.34pp on in-water).
  - Per F-016, **the scripted floor and a learned policy are predicted
    to move oppositely on the grooming channel** — exp-002 saw a
    policy's grooming-on-water fall 60% between dials while scripted
    grooming rises with the dial. First same-engine opportunity to test
    this; registered as a prediction, not a gate.

## 3. Arms

Warm starts are impossible, so the exp-002 arm structure (init × mix)
collapses. Registered arms:

| arm | init | mix | γ |
|---|---|---|---|
| A0 | BC clone (schema 2) | 33% | 0.998 |
| A1 | BC clone (schema 2) | 33% | 0.995 |
| A2 | BC clone (schema 2) | 0% (self-play) | 0.998 |

Three seeds per arm. Mix 33% rather than 67% on F-013/exp-002 evidence
(mixing bought ≤ +0.0009 and cost 0.004–0.015 on the full-agent shape);
0% is retained as the control that isolates whether mixing matters at
all under the new observation.

**Registered exclusion**: no dial arm. The dial is fixed at 3.5/60 by
spec 026. If H1 fails, that is a result about the observation bit, not
an invitation to turn the dial — exp-002 spent its escalation clause
proving where that road ends, and F-016 now explains why raising the
gain would be actively counterproductive.

## 4. Fixed factors (identical across arms)

- Engine `5a6a3f5`, stamp `cba976da…`. Any engine change mid-experiment
  voids the affected runs (§11).
- Wet-fur dials **3.5 / 60**, pinned into every family variant by
  family-gen from `WaterConfig::default()`.
- Family: **15 variants**, family-gen **v4**, base
  `experiments/exp-002-mixed-population/family/base.toml`
  (sha256 `603ded13…`), family seed **20260807**, manifest sha256
  `3be3578daa969c8d…`. Stratified, not sampled:
  - geometry cycled over **{20, 22, 24, 26}** — 20×20 is the deployment
    candidate Client designs against;
  - **18×18 excluded** and test-guarded — it is the reserved held-out
    downward exam for a future `evals/v2`, and FR-007 voids a suite
    whose exam appeared in training;
  - water minimum cycled over **{3, 4, base−1, base, base+1}**, giving
    exactly 3 lakeless variants of 15, so the family spans the
    lake/no-lake feature that frozen `scarcity.toml` (min 1) exercises;
  - roster cycled over {3, 4, 5} (F-010).
  All 15 (roster, water) pairs are distinct, so lakelessness is not
  confounded with roster size. The manifest records whether each world
  *actually grew* a lake, observed by generating it.
- Observation schema 2, action/mask schema 1. Dims read from the data,
  never declared (§11).

## 5. Pre-registered hyperparameters

Inherited verbatim from exp-001 §5 + deviation 2026-07-30, except where
the schema change forces a choice:

- Policy MLP **183 → 256 → 256 → 40**, ReLU, raw logits.
- BC: masked CE, legal-only label smoothing ε = 0.05, Adam 3e-4, batch
  4096, plateau stop on masked val top-1, split **by rollout**.
- Critic: MC targets per γ, states ≥ 1500 ticks of realized future,
  targets normalized (mean/std recorded and frozen).
- PPO: fragment 256, GAE λ = 0.95, clip 0.2, entropy 0.01 → 0.001,
  4 epochs × 4 minibatches, KL-to-init leash annealed to 0 over the
  first 20%.
- Total ticks per run: 20M.

## 6. Pre-experiment measurements (complete pre-freeze)

- [x] **Re-baseline on `cba976da…`** —
      [rebaseline-2026-08-06/results.md](../rebaseline-2026-08-06/results.md).
      needs_driven band, scripted water shares, the dial decomposition,
      and F-016.
- [x] **Tooling cleared** (PR #112): npy headers checked against their
      buffers with widths from the engine; both trainers read dims off a
      live observation; exporter and zero-artifact stamp from engine
      constants; family-gen requires `--base` and defaults its dials
      from `WaterConfig::default()`.
- [x] **Config strictness** (PR #114): a misspelt or misplaced dial is
      now a load error, and every shipped TOML is swept through both
      config surfaces.
- [x] **Family generated and manifest committed** (2026-08-06, seed
      `20260807`). Stratification verified from the manifest, not
      asserted: geometry 20/22/24/26 at 4/4/4/3 with **18×18 absent**;
      water minimum 3/4/7/8/9 at three each → **12 lake / 3 lakeless**;
      roster 3/4/5 at five each; all 15 (roster, water) pairs distinct.
      Dials pinned 3.5/60 from the engine.
- [ ] **Dataset v3 collected and invariants checked** — after freeze
      (collection is not training; it may run pre-freeze only under a
      recorded deviation).

## 7. Training protocol

Per arm × seed: BC clone → critic pretrain (γ-matched) → PPO 20M ticks
against the frozen family with per-episode mix draws. Long runs in a
dedicated worktree; commits land before any destructive verification.

**The prereg freezes when clone training starts.** Smoke runs on subset
data are exempt, recorded in the deviations appendix.

## 8. Evaluation protocol

Unchanged in shape from exp-002 §8 — the three deployment shapes ×
rosters, evaluate-once ledger, seeds disjoint from training and from
each other. Certification through `evals/v1` on the strict loader
(re-verified passing 2026-08-06).

**One change forced by the generation wall**: there is no cross-generation
comparison. Schema-1 artifacts exit 1 on this binary, so exp-001's and
exp-002's winners cannot be re-scored here. Every comparison is against
same-engine scripted baselines or between exp-003 candidates. The retired
anchors are listed in the design-inputs register §5.

## 9. Decision rules (pre-registered)

### 9.1 The water band — H1 and H2

Instrument: `experiments/rebaseline-2026-08-06/scripted_water_baseline.py`
geometry with the candidate seated at **both** policy seats (Miso +
Kittybear), scripted Biscuit playful / Pumpkin needs_driven, served
world, 10 seeds × 20k ticks, pinned clock (deploy semantics).

**Every bound is expressed relative to `B`, the same-engine scripted
baseline measured in the same seats by the same instrument.** This is the
central registered decision of this document, and it is a direct
consequence of what the re-baseline found: an absolute threshold silently
changes meaning when the engine moves, and exp-002's did — from a
demanding target into an unsatisfiable one. `B` is re-measured whenever
the stamp moves; today `B_inwater = 3.44%`, `B_lounge = 1.50%`.

Three registered criteria, all on the pooled policy seats:

1. **Ceiling — `inwater ≤ 1.5 × B_inwater`** (today: ≤ 5.16%).
   Rationale: the tightest multiple that still lets a
   baseline-behaving policy pass, and a genuine tightening on every
   ratio a policy has ever achieved — the frozen s6+s3 pair ran 5.6× its
   scripted baseline and exp-002's winner 3.2×.
2. **Floor — `inwater ≥ 0.5 × B_inwater`** (today: ≥ 1.72%). H2. Below
   this the policy has solved the task by refusing to enter water at
   all, which is not what was asked for.
3. **Lounging — `lounge_water ≤ B_lounge`** (today: ≤ 1.50%), where
   `lounge_water` = (Resting + Sleeping + Grooming) on water. The
   policy must not out-lounge a scripted cat. This is the criterion
   carrying the owner's actual complaint.

**Reported, explicitly not gated:**

- **Grooming-on-water, split out.** F-016 shows this channel is driven
  by an engine feedback loop that the dial *amplifies*; gating it would
  penalise the policy for the engine's behaviour. It is the sharpest
  diagnostic in the set — if the bit works, this is where it shows.
- **Forced vs discretionary occupancy**: crossings where water was the
  only route, versus occupancy with a dry alternative available. The
  true floor is measured, not inferred.
- Resting / Sleeping / Playing / Drinking / Idle on water, separately.

**No escalation clause.** If the band is missed, that is the result.
The dial does not move (§3).

### 9.2 Roster robustness — H5

Zero F-010 catatonia on rosters 3/4/5 at certification length:
`max_distress_age` 0, `floor_touches` 0, `fallback_count` 0. Any
nonzero value disqualifies the candidate outright.

### 9.3 Welfare — H3

Subject team welfare ≥ `needs_driven` baseline + 0.02 on the served
world, measured on the same engine in the same run.

### 9.4 Stop rule

Welfare < 0.5 on 3 consecutive probes halts the run for investigation.

## 10. Diagnostics

Per update: masked entropy, mask-violation rate under unmasked argmax,
channel-use rate. Per probe: the §9.1 water metrics with grooming split
out, served-world Nash, welfare.

**Registered watch**: F-016 predicts scripted grooming-on-water rises
with the dial while a policy's falls. Both are measured here on one
engine for the first time.

## 11. Threats-to-validity checklist (verify before run 1)

- [x] Engine pinned (`5a6a3f5`), stamp `cba976da…` recomputed
      independently 2026-08-06 after PR #114 and **unchanged**.
- [x] Frozen suite loads on the strict loader; mixed-roster PASS.
- [x] Trainer binding rebuilt (`maturin develop --release`) — it was
      reporting observation schema 1 three commits after the engine
      moved. `train_ppo_v2` now checks its init against the live gym at
      startup and names this case.
- [x] `bc-collect` cannot write an npy header that disagrees with its
      buffer; widths come from `observation_len()` / `ActionCodec::len()`.
- [x] `family-gen` requires `--base`; dials default from the engine.
- [x] `export_artifact.py` stamps schema from the binding.
- [x] Family manifest committed; variants **byte-stable** under
      re-generation (regenerated into a scratch tree and diffed:
      identical, 2026-08-06).
- [ ] Dataset v3 invariants: all labels legal vs mask, dims **183/40**
      read from headers, row counts match every meta. *(At collection.)*
- [ ] Eval seeds disjoint; evaluate-once ledger opened. *(At eval time.)*
- [ ] Long runs in a dedicated worktree. *(At training start.)*
- [x] No pending Product batch scheduled to land mid-experiment —
      **owner confirmed 2026-08-06** (Product queue clear; Client work
      is client-only and cannot reach the engine).

**Probe configs must be named explicitly.** `twin-probe` and
`cuddle-census` default to `training.toml`, which runs `water.min = 3` —
**lakeless**, while the served world always holds a lake. Registered
decision: **`training.toml` is left at 3.** It is F-013's and F-014's
control arm, and changing it would silently break comparability with
both for a property the family already covers by stratification. Any
probe claim in this experiment names its config on the command line;
an unqualified probe run is not admissible evidence.

## 12. Reading list

F-016 (the grooming loop), F-010 (roster OOD), F-013/F-014 (credit
landscape and the knob search — both still carry re-verify triggers on
this stamp; neither is cited numerically here), F-009 (horizon bounds
what a measurement can see), spec 017 FR-007 (held-out doctrine) and
FR-012 (suite freeze), specs 026/027.

## Appendix: Deviations

### Deviation 1 — deploying a candidate §9.2 did not certify (owner, 2026-08-07)

**No criterion is changed by this entry.** §9.2 stands exactly as
frozen, H5 stands as not supported, and no candidate is certified.
What is recorded here is a *deployment* decision, which is the owner's
to make and downstream of what the experiment may claim.

**Decision**: `A2-m0-g998-s3` is promoted to
`policies/e003-m0-g998-s3.ckpolicy` (sha256 `756aa680…`, byte-identical
to the evaluated artifact) and seated at both policy seats, superseding
`e001-a2-s6` and `e002-m0-g998-s1`.

**What it fails**: §9.2, by `max_distress_age` 3 — three ticks of
eat-need on one seed of the roster-5 *family* world. The gate admits no
nonzero value and admitted no candidate at all, from nine.

**What it passes, and why the owner judged that decisive**:

- **§9.1**: 2.79% in-water, 0.62% lounging — the driest of the nine and
  **below the scripted baseline** on both (3.44% / 1.50%). This is the
  behaviour exp-002 proved no dial setting could buy, and the water
  behaviour was the owner's sole note from the stage-1 soak.
- **§9.3**: +0.0420 against `needs_driven`.
- **The actual deployment condition**: the served world at roster 4, 30
  seeds × 20k, both shapes — `max_distress_age` **0**, `floor_touches`
  **0**, `fallback_count` **0**.

**The honest shape of the disagreement**: §9.2 was written to catch
F-010 catatonia and does — `A0-m33-g998-s3` saturates five needs with
161,314 floor touches. The same rule cannot distinguish that from three
ticks. The failures are bimodal with two orders of magnitude between the
populations ([grid-2026-08-07.md](results/grid-2026-08-07.md)). That is
an argument for a *better-specified* criterion in exp-004, and
explicitly **not** a reason to reread this one now — designing a gate
around the run that motivated it is how a gate stops meaning anything.

**Alternative considered and rejected**: rolling out with both seats
scripted (`needs_driven`, main's parked configuration). It requires no
policy decision, but it is *worse on the axis that prompted the
rollout* — scripted cats sit at 3.44% / 1.50% against this candidate's
2.79% / 0.62%.
