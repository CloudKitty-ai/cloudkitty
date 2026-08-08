# Experiment 004 — Pre-registration: the message head and the price of presence

**STATUS: DRAFT — NOT FROZEN.** This document is editable until the
freeze. Freeze preconditions, in order: (1) the Product spec batch
lands and its stamp is recorded; (2) the dial-pricing pilot prices the
cosleep dials; (3) the re-baseline measures `B` on the new engine —
**re-baseline first, never freeze first**; (4) the owner authorizes.
**The freeze lands when clone training starts** (smoke runs on subset
data exempt, recorded as deviations). After freeze the registered text
does not change; outcomes and deviations are recorded, never edited in,
and no criterion is weakened after the fact.

Every unresolved value is marked **[AT FREEZE: …]**. A freeze with an
unfilled blank is invalid.

**Frozen against**: engine **[AT FREEZE: sha]**, engine-defaults stamp
**[AT FREEZE: stamp — it moves with this batch by design; record via
the release-honest gate]**; family seed **[AT FREEZE]**, manifest
sha256 **[AT FREEZE]**; family-gen **v5**.
**Predecessor**: [exp-003](../exp-003-water-schema/prereg.md).
**Carry-forward register**:
[exp-004-design-inputs.md](../exp-004-design-inputs.md) — every item
there is adopted and cited below, consciously rejected, or deferred.
**Evidence base**:
[needs-analysis-2026-08-08](../needs-analysis-2026-08-08/results.md),
[contact-baseline-2026-08-08](../contact-baseline-2026-08-08/results.md),
[distress-census-2026-08-08](../exp-003-water-schema/results/distress-census-2026-08-08.md).

---

## 1. Background and motivation

exp-003 proved an observation can buy what no dial could: the in-water
bit put 7/9 candidates inside a band no blind policy reached, and the
deployed winner is drier than the scripted ladder itself. It also
proved, by measurement, that **the meow channel is dead**: the v3 BC
clone predicts meows at 0.0000 accuracy and never emits one; trained
candidates sit at 0.01–0.41 meows/1k under greedy selection. The
channel was not discovered from exploration in 20M ticks, and F-011
says the restraint is a reward equilibrium — the problem is too much
restraint, not too little.

The 2026-08-08 design work located the deadness precisely and resolved
the mechanism (design inputs §1):

- **A meow costs a whole turn** — the only cost a policy pays, and a
  full activity forgone. Resolved: the action factors into
  **(activity, message)** — two heads, zero marginal cost, one
  DecisionRng draw split, never a second decision.
- **Grounding was impossible**: `urgent_need_threshold` 75 sits above
  the lived range of every cat measured — scripted occupancy ≤ 0.02%,
  policy p99s 13–29. Resolved: **grounded legality** (the Purr
  pattern) at announce dials **30 / 5** with cooldown in the mask
  (= `recent_window_ticks`), priced from 1.9M scripted rows and a
  policy-side census of the deployed artifact.
- **Two of six needs had no message**; the demonstrator channel
  (GroomKitty) is empty — **0 ticks in 800k** at tick level. Resolved:
  `WantBath` + `WantSleep` land; scripted responders key on the
  **meow**, never on privileged need-reads (the imitability
  principle); scripted deciders announce **while acting**.
- **Cosleep pays 15/tick into a need averaging 11.6** — presence is
  economically instantaneous; the typical contact run is 3 ticks.
  Resolved: **B+C pricing** — a dedicated drip for the passive
  companion, the full/bonus rate for mutual engagement — plus the
  napper routing change. Dial values come from the pilot, not
  judgment.

This is a generation wall (observation schema 2 → 3, action/mask codec
v2): warm starts are void, every candidate is BC-then-PPO from
scratch, and no cross-generation artifact comparison exists.

## 2. Hypotheses

- **H1 (imitation seeds the channel)**: the BC v4 clone emits meows.
  Registered floor: in policy company on the served world (F-012
  geometry), the clone's meow rate ≥ **0.5/1k kitty-ticks** — against
  the v3 clone's hard zero. Direction and floor registered; the
  magnitude and kind mix are exploratory. Basis: dataset v4 carries
  announcement rows **by construction** (scripted emitters at the
  30/5 dials; predicted scripted rates ≈ 14/1k needs_driven,
  ≈ 200/1k playful on the pre-batch engine — re-measured at
  re-baseline, **[AT FREEZE: re-baselined predictions]**).

- **H2 (the demonstrated response transfers)**: trained candidates
  respond to the channel. Registered direction: P(approach-and-groom
  the emitter | WantBath heard ∧ own cuddle ≥ responder region)
  exceeds the same policy's rate absent the meow, measured by paired
  census on matched seeds. Registered floor: GroomKitty ticks > 0 in
  policy company at certification (v3 tick-level truth: exactly 0).
  Magnitudes exploratory — exp-003's lesson is that overtight gates
  on a first-generation behaviour measure the gate, not the policy.

- **H3 (priced presence buys duration)**: under the pinned cosleep
  dials, candidates hold **mean contact duration ≥ [AT FREEZE:
  pilot-informed target]** ticks (baseline on the unpriced engine:
  **3.0**, median 3, p90 5). Mutual share and cosleep rate reported,
  not gated (baseline: mutual 31.5% of serviced ticks, cosleep 4.9%
  of sleep).

- **H4 (welfare non-inferiority)**: subject team welfare on the served
  world ≥ `B_welfare` + 0.02, `B` re-measured on this engine in the
  same run — the exp-003 construction, unchanged.

- **H5 (stability under the settled gate)**: at least one candidate
  passes §9.2 as registered below. The gate was designed against all
  31 historical candidates and admits every forensically-healthy one;
  a 0/N outcome under it is a result about this generation's
  training, not the gate.

- **Anchors (registered predictions, values pinned at freeze)**:
  - `needs_driven` team welfare band on the served world:
    **[AT FREEZE: re-baseline]**.
  - Scripted water shares `B_inwater` / `B_lounge`: **[AT FREEZE]**
    (the scripted updates move both — F-016's loop gains a
    groom-response path; the relative-`B` construction absorbs it).
  - Scripted meow rates by kind at 30/5: **[AT FREEZE]**.
  - Healthy distress-tick share band: 0.0001–0.015% (retro-replayed
    history, 810 runs); collapse begins ≥ 0.06%.

## 3. Arms

| arm | init | mix | γ | shaping | seeds | selection |
|---|---|---|---|---|---|---|
| A0 | BC v4 clone | 0% (self-play) | 0.998 | off | **[AT FREEZE: N ≥ 3]** | eligible |
| A1 | BC v4 clone | 0% (self-play) | 0.998 | **on** (c = 0.5, γ_Φ = 0.998) | **[AT FREEZE: N ≥ 3]** | eligible |
| D1 | BC v4 clone | 33% | 0.998 | off | 3 | **ineligible — diagnostic only** (owner confirmed 2026-08-08) |

**A0/A1 are the experiment.** γ fixed at 0.998 — exp-003's γ = 0.995
arm lost on every axis; no γ sweep this generation (registered
exclusion, reaffirmed by the owner 2026-08-08: spare capacity goes to
**seeds, not sweeps** — per-seed lottery noise, not per-cell effects,
dominated both prior grids). **A0 and A1 seed counts are equal by
construction** (the on/off contrast stays balanced whatever N the
freeze picks); N is a per-experiment resource choice, declared here
per F-009, and owes no consistency to other experiments' N — training
seeds are never pooled across generations, and every standardized
instrument parameter (gate n = 30/shape, screen seeds, bands) is
registered on the eval side independent of it. A higher-γ (0.9985/0.999) follow-up is
*named but not run*: exp-002's 0.9985 cell added nothing and its
critic pretrained worst, so it re-enters only if A0/A1 show
horizon-limited channel signatures.

**A1 — potential-based shaping, on-vs-off (owner, 2026-08-08).**
`Φ(s) = −c × (active distress entries / roster)`, FR-009, enabled for
the first time in any run. Registered values: **c = 0.5** — derivation:
one cat entering distress costs 0.125 at roster 4, roughly half a
healthy tick's team reward (0.87 measured) — salient against per-tick
noise, unable to dominate the welfare objective; and
**`ShapingConfig::gamma` = 0.998, pinned equal to the training γ** —
the compiled default is 1.0 and the policy-invariance guarantee
requires them matched; an unmatched γ_Φ voids the arm. Shaping exists
only at training; the theorem preserves the optimum, so A1 candidates
are deployment-eligible on identical criteria. Registered direction
(secondary): A1 produces ≥ as many §9.2-passing candidates as A0 at no
welfare cost — "does invariant shaping help in finite time" is the
measured question. D1 runs shaping-off for comparability with A0.

**D1 is a diagnostic, not a contender** (owner confirmed 2026-08-08:
keep, 3 seeds, ineligible). The falsified mixing-welfare question
stays closed (two generations, no benefit). What is new is the
channel: scripted company now emits live, grounded meow traffic
during training, so D1 tests whether that **anchors channel
semantics** against self-play drift (private codes, channel silence)
— and it is the control that makes an A0/A1 channel collapse
*interpretable*: quiet-everywhere means imitation or reward; quiet
self-play beside a live D1 means company anchors the channel. Its
registered readouts are channel metrics against A0/A1's — rates per
kind, response behaviour, class-conditioned credit — never welfare,
and it cannot be selected for deployment regardless of its numbers.

**Registered exclusions**: no γ sweep (above); no announce-dial arm
(30/5 are shipped config defaults; if the channel stays quiet that is
a result about imitation and reward, not an invitation to lower the
bar — and the dial retunes by config rollout, not by experiment); no
reward-penalty or meow-bonus arm (F-011: shaping the channel *price*
is the dead-end already walked — A1's Φ prices distress, never the
channel).

## 4. Fixed factors (identical across arms)

The single registered per-arm difference is A1's `[rl.reward.shaping]`
block (§3) and D1's mix rate; everything below is shared.

- Engine **[AT FREEZE: sha + stamp]**. Any engine change
  mid-experiment voids the affected runs (§11).
- Announce dials **30 / 5**; cooldown = `recent_window_ticks` = 10;
  the courtesy trio retired (spec batch).
- Cosleep dials **[AT FREEZE: drip, mutual — from the pilot]**;
  `cuddle_relief` (grooming actor, rest duet) untouched at 15.
- Message head **Silent + 8**; `WaitForMe` yield-only; digest 8 kinds
  × (recency, dx, dy, intensity) = 32 values; observation width
  **[AT FREEZE: from the landed spec]**; action codec v2 (activity
  34 + message 9), mask schema v2, `Silent` never masked.
- Family: **15 variants**, family-gen **v5**, regenerated on the new
  engine, family seed **[AT FREEZE]**. Stratification carried from
  exp-003 verbatim: geometry {20, 22, 24, 26} (18×18 excluded and
  test-guarded, reserved held-out); water minimum cycle giving 3
  lakeless of 15; roster {3, 4, 5}, all (roster, water) pairs
  distinct. **New registered requirement: every variant's roster
  includes ≥ 1 `playful`** — the demonstrator emitters (needs
  analysis: playful cats produce ~14× the announcement traffic) must
  exist in every training world, or the imitation seed thins to
  needs_driven's near-silence.
- Dims read from the data, never declared (§11).

## 5. Pre-registered hyperparameters

Inherited from exp-003 §5 except where the two-head action forces a
choice:

- Policy MLP **[obs] → 256 → 256 → 43** (34 activity + 9 message
  logits), ReLU, raw logits, heads split by convention from one output
  vector.
- BC: **two masked CEs, summed** — activity head against `label.npy`,
  message head against `label_msg.npy`, each with legal-only label
  smoothing ε = 0.05 over its own mask. Adam 3e-4, batch 4096,
  plateau stop on the **summed** masked val objective; per-head val
  top-1 reported. Split by rollout.
- PPO: factored policy — log-probs and entropies **sum across heads**,
  one shared advantage; fragment 256, GAE λ = 0.95, clip 0.2, entropy
  0.01 → 0.001 applied to the summed entropy, 4 epochs × 4
  minibatches, KL-to-init leash annealed to 0 over the first 20%.
  Training-time channel babble from the entropy bonus is expected and
  welcome (it exercises the channel); convergence behaviour is what
  §9.4 judges.
- Critic: MC targets at γ = 0.998, states ≥ 1500 ticks realized
  future, normalized, mean/std frozen.
- Total ticks per run: **20M** [AT FREEZE: confirm].

## 6. Pre-experiment measurements (complete pre-freeze)

- [ ] **Product spec batch landed**; new stamp recorded through the
      release-honest gate; changelog markers `[obs-schema]`
      `[rng-sequence]` `[stamp]`; distress-tick counter reproduces the
      810-run acceptance target; resume test passes (no `--fresh`).
- [ ] **Client rendering entries** for `WantBath`/`WantSleep` queued
      (rollout dependency, not a freeze blocker).
- [ ] **pyo3 binding rebuilt** and schema-checked against the live gym.
- [ ] **Dial-pricing pilot** (scripted-only, F-016 instrument + contact
      census, 10 seeds × 20k paired, drip {1,2,3,5,15} × mutual
      {off,on}, routing change held constant) → **drip and mutual
      pinned into §4**.
- [ ] **Re-baseline `B` on the new stamp**: welfare band, water shares,
      contact metrics, scripted meow rates by kind (the §2 anchors),
      distress-tick baseline. Instruments: `scripted_water_baseline`
      geometry, `contact-census`, `needs-census`, the landed counter.
- [ ] **Welfare margin derivation on the new `B`**: control
      seed-to-seed sd → SE of the 30-seed mean → margin ≈ 10× SE (the
      0.002-on-24×24 method; the number is re-derived, never
      inherited).
- [ ] **Family v5 generated**, manifest committed, variants byte-stable
      under regeneration, playful-per-variant verified from the
      manifest.
- [ ] **F-015 re-verify + F-004 world-count re-derivation** — the
      standing first-probe obligation (FINDINGS): twin-probe
      class-conditioned credit re-measured on this engine before any
      probe-based claim; F-004's world-count bar re-derived.
- [ ] **Seed-band ledger opened**: every band this document uses
      declared here at freeze, disjoint from all prior bands (1–10,
      40k, 100k, 310–320k, 600–614k, 700–730k, 740k, 770k, 800k,
      820k) and from each other; training / collection / eval /
      stress / deployed-screen bands separately named
      **[AT FREEZE: bands]**. Per F-009, the band is a declared
      dimension of every claim.

## 7. Training protocol

Per arm × seed: BC v4 clone → critic pretrain → PPO 20M against the
frozen family (D1 with per-episode mix draws). Long runs in a
dedicated worktree; commits land before any destructive verification.
**The prereg freezes when clone training starts.**

## 8. Evaluation protocol

Three deployment shapes × stress rosters as exp-003 §8, plus the
deployed composition (policy at Miso + Kittybear beside scripted
Biscuit/Pumpkin — the shape that ships, built by the census tools
since no `--roster` flag constructs it). Evaluate-once ledger; eval
seeds disjoint from training and each other. Certification through
the frozen suite on the strict loader. No cross-generation artifact
comparison exists (schema wall); every comparison is same-engine
scripted `B` or between exp-004 candidates.

## 9. Decision rules (pre-registered)

### 9.1 The water band — carried guard

The exp-003 construction, unchanged and re-anchored: every bound is a
multiple of `B` measured by the same instrument in the same seats on
this engine. Ceiling `≤ 1.5 × B_inwater`, floor `≥ 0.5 × B_inwater`,
lounging `≤ B_lounge`; grooming-on-water split out and reported, never
gated (F-016 — and the groom-response channel gives bath relief a
second path this generation, so the split is the diagnostic that shows
it). `B` values **[AT FREEZE: re-baseline]**. No escalation clause.

### 9.2 Stability — the settled gate (owner, 2026-08-08)

Stress probe: rosters **3, 4/iii, 5**, **n = 30 runs per shape**,
20k ticks, declared band **[AT FREEZE]**. A candidate **fails** iff
any shape shows:

1. **Incident rate**: more than `max(1, floor(0.05 × n))` runs with
   `max_distress_age` > the incident bar, where the bar =
   `thresholds.distress / need rise rate` computed from the frozen
   config (**225** at 90 / 0.4 — the formula is registered, the
   constant is derived);
2. **Severity backstop**: any kitty-run with `low_share` > 5%;
3. **Floor**: any `floor_touches`.

Everything below the incident bar is **reported, never gated** —
including per-need distress-tick shares from the landed counter.
Validation provenance: designed against all 31 exp-002/exp-003
candidates (`gate_check.py`); known accepted admits A0-s2 /
M33-998-s3 documented in the design inputs.

**Deployment certification is separate**: on the deployed composition,
30 seeds on the declared band, zero incidents at the same bar,
welfare per §9.3, water per §9.1. A second disjoint band is run and
**reported as a drift alarm, not gated** (F-009: zero is a property
of the instrument, and the second band says how far).

### 9.3 Welfare — H4

Subject team welfare ≥ `B_welfare` + 0.02 on the served world, same
engine, same run. The derived margin **[AT FREEZE]** governs
equivalence claims in reporting; +0.02 is the gate.

### 9.4 The channel — H1/H2

All channel measurements in policy company (F-012), attribution
class-conditioned where used (F-015, post re-verify). Gates —
deliberately minimal:

1. **Clone floor (H1)**: BC v4 clone meow rate ≥ 0.5/1k in company.
   Fails → the imitation seed did not take; PPO arms still run, but
   the H1 wording stands falsified as registered.
2. **Candidate channel-alive**: selected-candidate meow rate ≥
   **[AT FREEZE: floor, ~0.5/1k]** in company at certification.
3. **Response existence (H2)**: GroomKitty ticks > 0 across the
   certification battery.

Reported, not gated: rates by kind; the paired heard-vs-unheard
response delta (H2's direction); kind-conditioned response latency;
D1-vs-A0 channel divergence; digest-intensity input relevance (no
registered hypothesis — it is unexercised infrastructure this
generation, and silence about it is not a negative result).

### 9.5 Contact — H3

Selected-candidate mean contact duration ≥ **[AT FREEZE:
pilot-informed]** on the served world (paired seeds, census
instrument). Cosleep rate, mutual share, cuddle time-above-threshold
reported against the committed baseline.

### 9.6 Stop rule

Welfare < 0.5 on 3 consecutive probes halts the run for
investigation.

## 10. Diagnostics

Per update: masked entropy **per head**, mask-violation rate under
unmasked argmax per head, message-head emission rate. Per probe: §9.1
water metrics with grooming split, §9.5 contact metrics, meow rates
by kind, served-world Nash, welfare, distress-tick share.

**Registered watches**: (a) F-016's second path — scripted grooming
now has a meow-keyed cross-cat channel; the wet-fur loop may move in
either direction and `B` absorbs it; (b) nap-pile check — under
mutual-tier pricing, do all-policy rosters converge to a pile except
when hungry (bounded by design: sleep services neither eat nor
drink); (c) partner-selection symmetry on cosleep (baseline:
near-uniform).

## 11. Threats-to-validity checklist (verify before run 1)

- [ ] Engine pinned; stamp recomputed independently and matching the
      batch's recorded stamp.
- [ ] Frozen suite loads on the strict loader post-batch.
- [ ] Binding rebuilt; trainer checks its init against the live gym.
- [ ] `bc-collect` two-channel: `label_msg.npy` present, widths from
      the engine, every message label legal against the message mask,
      `Silent` never masked (structural check).
- [ ] **The two-channel FR acceptance check at collection**: activity
      distribution conditioned on message ≠ Silent matches the
      unconditioned distribution to first order — announcing cats are
      mid-errand. A skew toward Idle voids the collection.
- [ ] No meow-*turn* rows exist in v4 (the shape is retired).
- [ ] Family manifest committed; byte-stable; playful-per-variant
      verified.
- [ ] Eval seeds disjoint; evaluate-once ledger opened.
- [ ] Long runs in a dedicated worktree.
- [ ] No pending Product batch scheduled to land mid-experiment —
      owner confirmed at freeze **[AT FREEZE]**.
- [ ] Probe configs named explicitly on every probe claim
      (`training.toml` remains the lakeless control; an unqualified
      probe run is not admissible evidence).

## 12. Reading list

Design inputs (the carry-forward register, incl. the settled gate and
spec-review responses); F-011 (restraint is reward-shaped), F-012
(channel use is context-dependent — company, not solo), F-013 (credit
band the drip is designed into), F-015 (**re-verify fired** — first
probe obligation), F-016 (the grooming loop, now with a second path),
F-017 (symmetry artifacts; the D1 diagnostic's frame),
F-004/F-009 (measurement discipline: clustering, declared
dimensions); needs-analysis-2026-08-08; contact-baseline-2026-08-08;
distress-census-2026-08-08; specs [AT FREEZE: batch spec numbers].

## Appendix: Deviations

*(none — the appendix opens at freeze and is append-only)*
