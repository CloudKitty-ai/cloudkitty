# Experiment 002 — Pre-registration: mixed-population fine-tuning on the wet-fur engine

**STATUS: DRAFT (2026-08-02).** Freezes when the first model-training
compute starts (the scratch-BC clone or the pilot, whichever is first);
smoke runs on subset data are exempt, as in exp-001. One registered
conditional survives the freeze: the wet-fur dial (§9.1), resolved by
the pilot under a rule written here before any run.

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
- **H2 (wet-fur learning)**: trained policies reduce water-lounging
  relative to frozen s6 on the post-024 engine — success signature
  per the [water baseline](../exp-001-bc-mappo/results/water-baseline-2026-08-01.md):
  Sleeping/Grooming/Resting-on-water collapses toward scripted
  levels, Idle transit survives, Drinking unharmed.
- **H3 (meow preservation)**: warm-start arms retain functional
  channel use, measured **in policy company** (F-012): digest-zeroing
  changes ≥ 3% of digest-active decisions for at least one seed per
  warm-start cell (s6 anchor: 8.18%).
- **H4 (roster robustness)**: with roster 3–5 in the training family,
  no candidate exhibits F-010 catatonia on any deploy-surface roster
  (3/4/5) at certification length.
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

**Mix semantics** (registered definition): per episode, with
probability = the arm's mix, all non-subject seats run their family
config behaviors (`needs_driven`, and `playful` where the family
declares it — the deploy surface includes a playful cat, F-012's
emitter); otherwise all seats are self-play copies. The subject seat
is drawn uniformly over the roster per episode.

## 4. Fixed factors (identical across arms)

- **Engine**: the one-engine rule — train and evaluate on the engine
  pinned at freeze (currently main @ `6d955ab`); any engine change
  after freeze is a deviation with a re-baseline inventory.
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
  all 15 family variants (3 rollouts each, 45 total, all-`needs_driven`
  control — the exp-001 lineage recipe) **plus 15 s6-seated rollouts**
  (1 per variant, s6 at every policy-capable seat) so critic pretrain
  sees policy-like state distributions and the scratch clone's data
  contains meow labels (§1 lever 4 of the register). Same invariants
  and split-by-rollout discipline as exp-001 §4.

## 6. Pre-experiment measurements (all complete or gated pre-freeze)

Done, with results docs: pre-wet-fur water baseline (now-or-never,
2026-08-01); wet-fur calibration at dial 1.5 (2026-08-02); post-024
probe re-verification (F-013); post-024 world search (F-014).

Remaining before freeze:
1. **Class-conditioned probe on the family base** (`--only-action`
   play/chase vs eat/drink vs groom/sleep/rest, 150 worlds) — the
   pre-024 play/chase 3.6× prior is dead (F-013); refresh it so
   §10.1's diagnostics read against a measured prior.
2. Dataset v2 collection + invariant checks (§5).
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
served world (water_calibration instrument, 10 seeds × 20k). Compute
**lounging-on-water share** = (Sleeping + Grooming + Resting ticks on
water) / total ticks, averaged over the two seats.

- Anchors: frozen s6 ≈ 4.0% (post-024 calibration); scripted
  needs_driven ≈ 0.5%.
- **If lounging ≤ 1.5%** (≥ ~60% of the frozen-policy excess
  unlearned): the dial freezes at 1.5; pilot stands as M33-g998-s1.
- **If lounging > 1.5%**: dial escalates to 2.5 — rerun the
  calibration probe at 2.5, regenerate the family
  (`--water-gain 2.5`), discard the pilot, rerun. **One escalation
  maximum**; a second failure is a deviation and an owner
  conversation, not another silent turn of the dial.

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

- [ ] Engine pinned; `engine_defaults_sha256` recorded; no pending
      Product batch scheduled to land mid-experiment (ask).
- [ ] Family regenerated-if-escalated and manifest committed BEFORE
      the grid starts; variants byte-stable under re-generation.
- [ ] Dataset v2 invariants pass (label legality, split-by-rollout,
      row counts vs manifests).
- [ ] s6 artifact sha matches the deployed `policies/s6.ckpolicy`.
- [ ] Eval seeds disjoint from training family seeds and from each
      other across shapes; evaluate-once ledger opened.
- [ ] Probe claims all cite 150+-world batches (F-004 addendum).
- [ ] Long runs execute in a dedicated worktree (shared-checkout
      hazard); commits land before any destructive verification.
- [ ] F-011 premise check: reward is cooperative team Nash (it is) —
      re-read spec 023's backstop note if that ever changes.

## 12. Reading list

FINDINGS F-004, F-007, F-009 → F-014; the register
(exp-002-design-inputs.md, all sections); results docs: water
baseline 2026-08-01, wet-fur calibration 2026-08-02, post-024 probe
re-verification, post-024 world search; docs/cuddle-relief-semantics.md
(before any welfare-Cuddle claim); exp-001 prereg §5 + deviations
2026-07-30 (inherited hyperparameters), §9.1 soak protocol.

## Appendix: Deviations

*(none yet — the draft is unfrozen)*
