# Experiment 002 — Pre-registration: mixed-population fine-tuning on the wet-fur engine

**STATUS: FROZEN 2026-08-03** (drafted 2026-08-02; owner-reviewed
2026-08-03). Frozen at the start of the first model-training compute —
the scratch-BC clone + per-γ critic pretrains on dataset v2, engine
main @ `0fd551d`. Smoke runs on subset data were exempt, as in
exp-001. One registered conditional survives the freeze: the wet-fur
dial (§9.1), resolved by the pilot under a rule written here before
any run. Post-freeze changes go to the Deviations appendix.

Owner decisions folded in (2026-08-02): three teammate-mix conditions
{0%, 33%, 67%}; all main arms warm-start from s6; one scratch-BC
control; 20M ticks × 3 seeds per cell; dial decided after a pilot.

## 1. Background and motivation

exp-001 produced s6/s3 — BC-initialized MAPPO policies that beat
`needs_driven` on the served world (F-007) but trained pure self-play
and deployed into scripted company. That transfer gap is implicated in
the two defining post-deployment surprises: roster-OOD catatonia
(F-010) and latent channel use (F-012). Meanwhile the 024 wet-fur
batch rewired the credit landscape (F-013): the served world now
carries the strongest replicated cooperative band measured in this
project, and the old scarcity×tempo gym lost its edge (F-014). This
generation therefore trains **deployment-shaped**: on a family around
the served world, with scripted teammates as an explicit experimental
factor, fine-tuning from the deployed s6 rather than from scratch.

Carry-forward register: [../exp-002-design-inputs.md](../exp-002-design-inputs.md)
(§§1–3; every item there is adopted, rejected, or deferred by this
document — nothing silently dropped). Findings relied on: F-004,
F-007, F-009, F-010, F-011, F-012, F-013, F-014.

## 2. Hypotheses

- **H1 (mixed-population transfer)**: arms trained with scripted
  teammates (33%, 67%) outperform pure self-play (0%) on the
  1-agent and partial-agent deployment shapes (§8), without
  significant loss on the full-agent shape. Direction registered;
  33-vs-67 ordering is exploratory.
  > **H1 NOT SUPPORTED 2026-08-03**
  > ([results/grid-2026-08-03.md](results/grid-2026-08-03.md)): mixing
  > buys ≤ +0.0009 on the 1-agent shape (γ=0.995 only) and costs
  > 0.004–0.015 on the full-agent shape — the "without significant
  > loss" clause fails. See the shape-i geometry note (Deviation 2).
- **H2 (wet-fur learning)**: trained policies reduce water-lounging
  relative to frozen s6 on the pinned engine (§4) — success signature
  per the [water baseline](../exp-001-bc-mappo/results/water-baseline-2026-08-01.md):
  Sleeping/Grooming/Resting-on-water collapses toward scripted
  levels, Idle transit survives, Drinking unharmed.
  > **H2 FALSIFIED 2026-08-03 — see Deviation 1.** Neither registered
  > dial reaches the §9.1 gates; the wet-fur dial does not buy deployed
  > water avoidance at welfare-neutral cost. Registered text above is
  > unchanged; the result is recorded, not the criterion.
- **H3 (meow preservation)**: warm-start arms retain functional
  channel use, measured **in policy company** (F-012): digest-zeroing
  changes ≥ 3% of digest-active decisions for at least one seed per
  warm-start cell (s6 anchor re-measured post-025: **13.26% of
  heard**, per-seed 11.79–15.17%, scripted company — the pre-024
  8.18% lapsed with the engine; audibility fell 62.4% → 10.7%, so
  per-run flip-rate estimates carry more variance — see the
  [meow-listening doc](../exp-001-bc-mappo/results/meow-listening-2026-07-31.md)
  post-025 addendum).
  > **H3 CONFIRMED 2026-08-03**
  > ([results/grid-2026-08-03.md](results/grid-2026-08-03.md)): every
  > warm-start cell passes with every seed ≥ 10% of heard (threshold
  > 3%), measured in policy company beside frozen s6 after the
  > forensics_replay labeling fix (Deviation 2).
- **H4 (roster robustness)**: with roster 3–5 in the training family,
  no candidate exhibits F-010 catatonia on any deploy-surface roster
  (3/4/5) at certification length.
  > **H4 PARTIALLY FALSIFIED 2026-08-03** (grid doc): 17/22 candidates
  > pass the distress-age gate on all three rosters; 5 fail, worst the
  > scratch control (3/30 seeds catatonic). Failures are per-training-
  > seed, not per-cell — the family did not eliminate F-010, but the
  > gate catches it and the roster is screened, which is what §9.2
  > consumes.
- **Anchors (registered predictions)**: γ=0.998 ≥ γ=0.995 within each
  mix condition (F-013 band position); the scratch-BC control ends at
  or below its warm-start twin cell (F-007); `needs_driven` holds
  0.88–0.91 team welfare on family worlds (F-014 gate measurements).

## 3. Arms

| Arm | Mix | γ | Seeds | Init | Ticks |
|---|---|---|---|---|---|
| M0-g995 / M0-g998 | 0% | .995 / .998 | 3 each | s6 warm-start | 20M |
| M33-g995 / M33-g998 | 33% | .995 / .998 | 3 each | s6 warm-start | 20M |
| M67-g995 / M67-g998 | 67% | .995 / .998 | 3 each | s6 warm-start | 20M |
| C-scratch | 33% | .998 | 1 | fresh BC clone (dataset v2) | 20M |
| P-pilot | 33% | .998 | seed 1 | s6 warm-start | 20M |

18 main runs + control. **The pilot IS run M33-g998-seed1**: if the
dial resolves to 1.5 (§9.1), the pilot's run stands as that cell's
first seed; if the dial escalates, the pilot is discarded (recorded,
not cited) and the full grid runs at the new dial.

**γ sweep** = {0.995, 0.998} (F-013/F-014: the served-world band at
k ≈ 230–330 sits inside 0.998's horizon). γ = 0.9985 is consciously
rejected as a default arm and carried as a **dormant conditional**:
it enters (replacing 0.998's role in a follow-up cell) only if the
frozen family's measured dr band peak lands past k ≈ 500 under the
§6 class-conditioned probe — the F-013 decision rule, registered.
> **TRIGGER FIRED 2026-08-02**
> ([results/class-credit-2026-08-02.md](results/class-credit-2026-08-02.md)):
> the family base's band peak is k=948 (5-kitty worlds carry credit
> late, per F-014's roster result). Per the clause: **one follow-up
> cell F-9985 (33% mix, γ=0.9985, 3 seeds, 20M) runs after the main
> grid.** The 18-run grid is unchanged; roster-4 family members keep
> their band inside 0.998's horizon.

**Mix semantics** (registered definition): per episode, with
probability = the arm's mix, all non-subject seats run their family
config behaviors (`needs_driven`, and `playful` where the family
declares it — the deploy surface includes a playful cat, F-012's
emitter); otherwise all seats are self-play copies. The subject seat
is drawn uniformly over the roster per episode.

## 4. Fixed factors (identical across arms)

- **Engine**: the one-engine rule — train and evaluate on the engine
  pinned at freeze (currently main @ `0fd551d`, spec 025 per-target
  play relief; re-pinned 2026-08-03 from `6d955ab` after the
  registered pre-freeze re-baseline —
  [results/class-credit-2026-08-03-post025.md](results/class-credit-2026-08-03-post025.md));
  any engine change after freeze is a deviation with a re-baseline
  inventory.
- **No schema changes**: observation 182-dim, action codec 40 rows,
  mask semantics — frozen (protects the warm start; spec 024 kept
  this invariant deliberately).
- **Training family**: family-gen v3, **base = the served-world shape**
  (F-014): `cloudkitty.toml` values with the two policy seats
  neutralized to `needs_driven`, plus Clementine (id 5, needs_driven,
  cuddle 0.7) so roster stratification 3/4/5 has a 5-kitty base.
  N = 15 variants (5 per roster size), `--family-seed 20260802`,
  `--water-gain` per §9.1's resolution. The quantified trade is
  accepted: the 5-kitty variants carry roughly half the credit signal
  (F-014: S .090 → .041) as the price of F-010 coverage.
- **Reward**: team Nash (level mode, p=0, ε=0.01), horizon 2000 —
  unchanged from exp-001. F-011's economics premise holds (any
  per-kitty or competitive reward voids it — none here).
- **Architecture**: MLP 182→256→256→40 (policy);
  critic on the privileged global state **padded to the 5-kitty
  layout** (absent kitties = zero blocks, mirroring the observation's
  empty-slot convention; the zero pattern encodes roster size).
- **Statistics discipline**: any probe-derived claim uses
  cluster-robust statistics on **150+ worlds** (F-004 addendum).

## 5. Pre-registered hyperparameters

MAPPO settings inherit exp-001 §5 + deviation 2026-07-30 verbatim
(fragment 256, λ=0.95, clip, entropy, minibatching — cite that
appendix; do not re-derive), except:

- **Fine-tune learning rate 1e-4** (⅓ of scratch) for warm-start
  arms; C-scratch keeps 3e-4. Rationale: protect the s6 prior
  (H3) while leaving room to learn wet-fur avoidance (H2).
- **Warm-start init**: `policies/s6.ckpolicy`
  (sha256 `8030b94d…`, the deployed artifact) loaded via the artifact
  contract; critic initialized from the γ-matched critic pretrain on
  dataset v2 (never reused across γ).
- **Dataset v2** (collection precedes freeze): scripted rollouts on
  all 15 family variants (3 rollouts each, 45 total) driven by the
  **family config behaviors** — needs_driven plus the deploy
  surface's playful seat (Biscuit), matching the dynamics every F-014
  measurement ran; **plus 15 s6-seated rollouts** (1 per variant, s6
  at every seat, greedy, chosen-action labeling — see
  `collect_s6_rollouts.py`) so critic pretrain sees policy-like state
  distributions and the scratch clone's data contains meow labels
  (§1 lever 4). Same invariants and split-by-rollout discipline as
  exp-001 §4.
  **COLLECTED 2026-08-02, RECOLLECTED 2026-08-03** on the re-pinned
  engine `0fd551d` (spec 025 changed dynamics, so the pre-025
  collection was invalidated by design): 60 rollout dirs, 1,908,182
  decisions, all labels legal, dims 182/40 everywhere; scripted drop
  rates 0.69%/0.13% (bc-v1-comparable); s6 data carries 774
  channel-row decisions (rows 34/38/39) where bc-v1 had none.
  `raw/bc-v2/` is gitignored; the exact regeneration (determinism
  verified on the 08-02 collection — identical label bytes on
  rerun):
  ```
  ./experiments/tools/bc-collect/target/release/bc-collect \
    --family-dir experiments/exp-002-mixed-population/family/v2-dial1.5 \
    --rollouts 3 --ticks 8000 --seed-base 400001 \
    --out-dir experiments/exp-002-mixed-population/raw/bc-v2
  trainer/.venv/bin/python \
    experiments/exp-002-mixed-population/collect_s6_rollouts.py
  ```
  Per-rollout metas stamp per-kitty demonstrator provenance
  (`"experts"`; the family seats a playful Biscuit) and the episode
  horizon read from each config.
  **Split (by rollout, F-004; fixed at freeze)**: val =
  `rollout-02` of every variant (one held-out world seed per config,
  scripted) **plus** `s6-rollout-00` of configs 12/13/14 (one per
  roster size, so policy-like states and channel rows appear in val);
  the other 42 rollouts train. World seeds are disjoint by
  construction (scripted `400001 + ci·1000 + r`, s6
  `500001 + ci·1000`).

## 6. Pre-experiment measurements (all complete or gated pre-freeze)

Done, with results docs: pre-wet-fur water baseline (now-or-never,
2026-08-01); wet-fur calibration at dial 1.5 (2026-08-02); post-024
probe re-verification (F-013); post-024 world search (F-014);
**post-025 re-baseline 2026-08-03** (spec 025 per-target play
relief, the generation's second and final planned comparability
break — every measurement below refreshed on `0fd551d`,
[results/class-credit-2026-08-03-post025.md](results/class-credit-2026-08-03-post025.md)).

Remaining before freeze:
1. ~~Class-conditioned probe on the family base~~ **DONE 2026-08-02,
   REFRESHED post-025 2026-08-03**
   ([results/class-credit-2026-08-03-post025.md](results/class-credit-2026-08-03-post025.md)):
   the registered spec-025 prediction confirmed — play/chase rose
   off its 0.1× floor (S(.998) 0.0039 → 0.0245, band peak k=301,
   inside 0.998's horizon). §10.1 diagnostics watch eat/drink (now
   the largest channel, 0.0709), groom/sleep/rest, **and**
   play/chase. Method note: the pooled all-action probe went
   sub-floor by dilution (F-015) — class-conditioned absolute S is
   the comparable quantity. Late bands persist past k≈500 → the §3
   dormant-γ trigger stays fired (follow-up cell F-9985 registered
   there).
2. ~~Dataset v2 collection + invariant checks~~ **DONE 2026-08-02,
   RECOLLECTED post-025 2026-08-03** (§5). Family frozen at dial
   1.5: `family/v2-dial1.5/` (15 variants, seed 20260802, manifest
   committed; byte-identical under regeneration on `0fd551d` —
   relief values live in engine defaults, not configs; regenerated-
   if-§9.1-escalates, which also invalidates and recollects dataset
   v2).
3. Owner review of this draft.

## 7. Training protocol

1. Dataset v2 → scratch clone + per-γ critic pretrains (parity checks
   and artifact export per the exp-001 contract; clone's honest
   kitty-eval numbers recorded but NOT a registered arm this time).
2. **Pilot** (M33-g998-seed1 at dial 1.5) → §9.1 resolution → family
   regeneration if escalated.
3. Main grid, foreground monitoring, checkpoints every 1M ticks;
   2k-tick validation probes during training are **transfer
   telemetry only** — they cannot see certification-horizon failures
   (F-009/F-010; the gate is §8).
4. Run order interleaves cells (one seed of every cell before second
   seeds) so an engine-drift surprise damages all cells equally.

## 8. Evaluation protocol (the three-world matrix × rosters)

Every candidate (each seed of each cell) at 20,000 ticks, greedy
seating, evaluate-once discipline:

- **Shape i — 1-agent**: candidate at one seat, all other seats
  scripted (served config behaviors), served world. Primary transfer
  measure; paired Nash vs all-scripted baseline, 30 eval seeds.
- **Shape ii — partial-agent**: candidate seated beside frozen s6
  (Seating-B geometry). Doubles as the channel-use screen (F-012):
  meow emission/attribution + digest-zeroing flip rate (H3).
- **Shape iii — full-agent**: every seat the candidate. The F-010
  stability gate runs here on rosters 3, 4, and 5 (the compiled
  3-kitty world remains the named secondary screen, deviation 31).

Certification bounds, fallback-zero, and distress-age limits inherit
the eval-suite v1 definitions. Wet-fur signature (H2) measured by the
`water_calibration.py` instrument with the candidate seated (shape
ii geometry, 10 seeds — the calibration doc's "after" side becomes
this experiment's per-candidate readout).

## 9. Decision rules (pre-registered)

### 9.1 The wet-fur dial (the registered conditional)

Pilot completes → seat the pilot policy at Miso+Kittybear on the
served world (water_calibration instrument, 10 seeds × 20k). Two
metrics, averaged over the two seats (anchors from the
[calibration doc](../exp-001-bc-mappo/results/water-calibration-2026-08-02.md),
re-verified post-025: frozen agents 4.14% / 9.21%, scripted
0.31% / 1.63% — post-024 values 4.22% / 9.42% and 0.32% / 1.65%,
within noise):

1. **Lounging-on-water share** = (Sleeping + Grooming + Resting ticks
   on water) / total ticks. **Pass: ≤ 1.0%** (~83% of the
   frozen-policy excess unlearned).
2. **Total in-water share** = all on-water ticks / total ticks.
   **Pass: ≤ 3.0%** (owner target, 2026-08-02: lounging and
   idle-loitering gone, residual lawful on-tile drinking tolerated;
   legitimate floor ≈ 1.1% transit — scripted parity would be ≈ 2%).

- **Both pass** → the dial freezes at 1.5; pilot stands as
  M33-g998-s1.
- **Either fails** → dial escalates to 2.5 — rerun the calibration
  probe at 2.5, regenerate the family (`--water-gain 2.5`), discard
  the pilot, rerun. **One escalation maximum**; a second failure is a
  deviation and an owner conversation, not another silent turn of the
  dial.

> **RESOLVED BY DEVIATION 1 (2026-08-03).** Both dials failed; the
> escalation clause is exhausted and the owner conversation it
> requires was held. Outcome: H2 falsified, dial set to 1.5, grid
> proceeds on H1/H3/H4. Full record:
> [results/dial-resolution-2026-08-03.md](results/dial-resolution-2026-08-03.md).

### 9.2 Selection and comparison

- **Primary**: paired Nash vs scripted baseline on shapes i and iii
  (Wilcoxon, 30 seeds, exp-001 convention), gated by H4's stability
  screen on all three rosters. A candidate failing any roster's gate
  is out regardless of Nash.
- **Secondary (registered, §1 lever 5)**: among statistical ties,
  prefer the candidate with functional channel use (H3's screen) —
  the owner's stated product preference, written down as selection
  criterion rather than post-hoc taste.
- H1 is evaluated per-shape by comparing cell means (mix conditions)
  at matched γ; the winner deploys only after the full F-010 screen.

### 9.3 Stop rules

A run whose validation probes show sustained collapse (welfare < 0.5
on 3 consecutive probes) is halted and investigated before its cell
continues — deviation entry either way. Training-time diagnostics
uniformly healthy in a failing run is a known blind spot (F-008
history): no candidate claim rests on training curves.

## 10. Diagnostics and visualization

- **10.1**: exp-001's per-update curve set, plus: mask-violation rate
  under unmasked argmax (the F-007 lineage fingerprint), channel-use
  rate (meows/1k decisions) per seed, lounging-on-water share at each
  checkpoint (H2 trajectory), all-seeds-overlaid, never best-seed.
- **10.2**: per-shape paired-delta tables; wet-fur activity tables
  (baseline-doc format) per candidate; channel attribution (pair-
  screen format) for shape ii.
- **10.3**: every figure/run stamps engine sha, served-config sha,
  family manifest (generator version, family seed, water gain), init
  artifact sha, dataset v2 manifest, seed, and instrument versions.

## 11. Threats-to-validity checklist (verify before run 1)

- [x] Engine pinned (`0fd551d`); `engine_defaults_sha256`
      `12bf38624186…` recorded (2026-08-03, matches the spec-025
      record); no pending Product batch scheduled to land
      mid-experiment — **owner confirmed 2026-08-03** (possible
      client-only work; no engine impact).
- [x] Family manifest committed; variants byte-stable under
      re-generation (verified 2026-08-03). Regenerate-if-escalated
      re-checked at §9.1 resolution before the grid starts.
- [x] Dataset v2 invariants pass (2026-08-03: 1,908,182 decisions,
      all labels legal vs mask, dims 182/40, row counts match all 60
      metas; split is by rollout per §5).
- [x] s6 artifact sha matches the deployed `policies/s6.ckpolicy`
      (`8030b94d…`, verified 2026-08-03).
- [ ] Eval seeds disjoint from training family seeds and from each
      other across shapes; evaluate-once ledger opened. *(At eval
      time — before the first shape-i evaluation.)*
- [x] Probe claims all cite 150+-world batches (F-004 addendum;
      post-025 re-baseline used 150-world batches throughout).
- [ ] Long runs execute in a dedicated worktree (shared-checkout
      hazard); commits land before any destructive verification.
      *(At pilot start — the clone/critic pretrains are short,
      foreground, on committed code.)*
- [x] F-011 premise check: reward is cooperative team Nash (it is) —
      re-read spec 023's backstop note if that ever changes.

## 12. Reading list

FINDINGS F-004, F-007, F-009 → F-015 (F-015: class-conditioned
absolute S, never class-vs-all ratios); the register
(exp-002-design-inputs.md, all sections); results docs: water
baseline 2026-08-01, wet-fur calibration 2026-08-02 (+ post-025
addendum), post-024 probe re-verification, post-024 world search,
**post-025 class credit**
([results/class-credit-2026-08-03-post025.md](results/class-credit-2026-08-03-post025.md)
— the current credit landscape; the 08-02 doc is superseded),
meow-listening 2026-07-31 (+ post-025 re-anchor);
docs/cuddle-relief-semantics.md (before any welfare-Cuddle claim);
exp-001 prereg §5 + deviations 2026-07-30 (inherited
hyperparameters), §9.1 soak protocol.

## Appendix: Deviations

### Deviation 1 — §9.1 exhausted; H2 falsified; dial set to 1.5 (2026-08-03)

**Trigger.** §9.1's registered escalation ran in full and both dials
failed the gates (lounging ≤1.0%, in-water ≤3.0%), averaged over the
Miso+Kittybear seats on the served world, 10 seeds × 20k:

| Pilot | lounging | in-water |
|---|---|---|
| M33-g998-s1 @ dial 1.5 | 3.73% | 7.72% |
| M33-g998-s1 @ dial 2.5 | 2.89% | 6.58% |

The escalation was executed as registered before the second reading
was taken: calibration probe rerun at 2.5, family regenerated
`--water-gain 2.5` at the same family seed, dataset v2 invalidated and
recollected on it, clone and both critics retrained, the dial-1.5
pilot discarded, the pilot rerun. §9.1 caps escalation at one turn and
names a second failure a deviation and an owner conversation. No third
dial turn was taken and no threshold was moved.

**Owner decision (2026-08-03).** Accept **H2 as falsified for this
generation** and run the grid on the science that does not depend on
the dial. H1, H3 and H4 are untouched by this result.

**Dial set to 1.5.** With H2 resolved, the dial carries no remaining
decision rule, so the training family takes the value that matches the
deployment shape this generation is built around: 1.5 — the served
world's value and the engine default. Training at 2.5 while evaluating
on a 1.5 served world would open a train/deploy dynamics gap inside
H1's own subject matter. `family/v2-dial1.5` and its dataset v2, clone
and critics (all retained) are the grid's inputs; the 2.5 family,
dataset, clone and critics are retained beside them as the escalation
record.

**Pilots.** Both pilot runs are recorded as pilots and **neither is
cited as a grid seed**. §3's "the pilot IS run M33-g998-seed1" clause
would arguably reinstate the 1.5 pilot now that the dial resolves to
1.5, but that pilot was discarded under the escalation branch, and
un-discarding a run because its dial later won is a researcher degree
of freedom this document exists to spend. All 18 grid runs execute
fresh; M33-g998-s1 is trained again from the registered init.

**Why H2 failed (measured, not speculated).** The dial does move what
it should — grooming-on-water fell 60% and idle loitering a third
across the two dials — but sleeping-on-water barely responds and now
dominates the residual, and it is not sunbeam napping (elements cannot
share a tile). The behavior costs ≈0.002 team Nash, so PPO has no
gradient to remove it, and the 130-probe series is flat after ≈2M
ticks in both runs, so the runs are converged rather than undertrained.
The gates are reachable in principle — the scripted ladder achieves
0.31% / 1.63%.

**Carried to exp-003 (owner, 2026-08-03).** Two changes to try
together next generation: extend the observation schema so a kitty can
see it is standing in water (today sunbeam occupancy has a dedicated
self-block flag and water occupancy must be inferred from a
nearest-water slot at distance 0 — a §4-forbidden schema change here
because it voids the warm start), and raise the bath penalty
substantially rather than incrementally.

### Deviation 2 — evaluation-instrument notes (2026-08-03)

Recorded after the grid evaluation; none changes a registered
criterion.

1. **Shape-i geometry substitution.** §8 registered the 1-agent shape
   as "candidate at one seat, all other seats scripted (served config
   behaviors)". The available instrument — kitty-eval's `Mixed`
   roster — seats the subject at the first kitty and rewrites every
   other seat to `needs_driven`, so Biscuit's `playful` was not in
   company. No harness mode matches the registered geometry (the
   `FromConfig` mode would run the config's `policy:` seats). Shape-i
   results are honest paired measurements in all-needs_driven
   company; cell contrasts share the geometry, so H1's evaluation
   stands with that reading. A harness extension is Product's call.
2. **forensics_replay labeling fix.** The shape-ii screen initially
   appeared untrustworthy; the cause was probe columns labeled
   positionally instead of by agent name (candidate at kitty_4
   printed as "kitty_2"). Fixed and re-verified before any H3 number
   was recorded; the H3 screen ran after the fix. The real trap —
   omitting `--config` silently probes the compiled 3-kitty world and
   re-measures frozen s6 — is documented in the grid doc.
3. **Evaluate-once footnote.** M33-γ.998-s1's shape i ran once as a
   pre-ledger timing check (identical protocol and seeds) and again
   in the sweep; results identical, one recorded.
4. **H2 per-candidate water readout skipped** for all grid candidates
   under Deviation 1 (H2 falsified; the dial carries no remaining
   decision rule this generation).
