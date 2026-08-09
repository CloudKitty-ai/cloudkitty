# Findings register

Distilled, generalizable research conclusions — the claims that outlive any
one experiment. Results files under `exp-*/results/` are the immutable
evidence; this register is the evolving knowledge layer on top of them.

**Rules:**

- Entries are edited **by supersession, never in place**: a finding that is
  narrowed, overturned, or replaced gets its status changed and a new entry
  — so any past experiment's design can be read against what was believed
  at the time.
- Statuses: `active`, `superseded by F-NNN`, `refuted`.
- Every entry states its **scope of validity** (the conditions it was
  measured under) and **what would invalidate it** — findings stay
  falsifiable, matching the pre-registration culture.
- **Re-verify when** carries the standing trigger for re-testing a finding
  whose scope is expected to shift. This register — not BACKLOG.md — is
  where research re-checks live; the backlog is the product's register.
- New pre-registrations MUST cite the F-ids they rely on.
- Findings that survive across contexts get **promoted**: the claim
  graduates into operating defaults (docs/rl-training.md, reference
  configs, the prereg conventions) with its F-id cited as provenance.
  Promotion is the point; a register that only accumulates is a graveyard.
- Superseded and refuted entries keep only a **stub** here (id · status ·
  claim · why it fell); their full text moves verbatim to
  [FINDINGS-ARCHIVE.md](FINDINGS-ARCHIVE.md) under the same `## F-NNN`
  header, so citations keep resolving. Do the move as part of the
  superseding edit. Promoted findings keep status `active` plus a
  promotion note naming where the operating default now lives.

---

## Index

| id | status | claim |
|---|---|---|
| F-001 | superseded → F-003 | Two-channel credit: fast self, slow teammate (pre-retune quantities) |
| F-002 | refuted | Non-binding cuddle routes carry no material headroom |
| F-003 | superseded → F-013 | The retune tripled the credit horizon; channels unchanged |
| F-004 | active · **promoted** | Cluster probe statistics by world; replicate on disjoint worlds |
| F-005 | superseded → F-013 | Scarcity×tempo was the one replicated training-world improver |
| F-006 | superseded → F-013 | Pre-024 default world carried no detectable cooperative credit |
| F-007 | active | BC initialization is necessary for MAPPO to beat the baseline at exp-001's budget |
| F-008 | superseded → F-010 | All-policy collapse read as long-horizon coordination instability |
| F-009 | active · **promoted** | Every dimension an instrument holds fixed bounds the failures it can detect |
| F-010 | active | Roster-OOD fragility: an empty kitty slot can collapse an exp-001 policy |
| F-011 | active | Meow restraint is a reward-structure equilibrium, not an engine guarantee |
| F-012 | active | Channel use is context-dependent; measure in policy company, not solo |
| F-013 | active | The 024 batch rewired the credit landscape; the served world gained a cooperative band |
| F-014 | active | Post-024 world search: the served world wins as it stands; knob landscape flat |
| F-015 | active | Pooled probes dilute under heterogeneous class amplitudes; condition by class |
| F-016 | active | Raising bath_gain increases scripted on-water time via the grooming channel |
| F-017 | active | The multi-copy collapse is largely a symmetry artifact; sampling dissolves it |

---

## F-001 · superseded by F-003 · Credit in CloudKitty is two-channel: fast self, slow teammate

Claimed the two-channel credit structure (fast self, ~60% of mass within
18 ticks; slow teammate, 50–200 ticks peaking k≈106) on the pre-retune
engine. The structure survived every engine since; these quantities died
with the companionship retune (PR #60). Chain: F-001 → F-003 → F-013.
Full text: [FINDINGS-ARCHIVE.md](FINDINGS-ARCHIVE.md).

---

## F-002 · refuted · Non-binding cuddle-route under-use is real but carries no material headroom

The mechanical under-use was confirmed, but the headroom hypothesis was
refuted post-retune: high-need opportunities beside friends occur ~1–2
per 100k ticks (the heavier cuddle weight services the need early), so
the route cannot beat `needs_driven`. The prereg's interpretation rule —
trained-policy Cuddle pinned streaks beside busy friends = real skill
gap — stands. Full text: [FINDINGS-ARCHIVE.md](FINDINGS-ARCHIVE.md).

---

## F-003 · superseded by F-013 · The companionship retune tripled the credit horizon; channels unchanged

Re-measured F-001 on the retuned engine: two-channel structure held,
every band moved out 2–4× (spillover ~230–430, team peak k≈230, live
tail past k=1,000). Killed by its own registered trigger when the 024
wet-fur batch moved the quantities again — the same death as F-001.
See F-013. Full text: [FINDINGS-ARCHIVE.md](FINDINGS-ARCHIVE.md).

---

## F-004 · active · Probe statistics must cluster by world; few-world batches produce phantoms

Twin-probe samples that share a world share long-lived state, so for the
slow cooperative channel the effective sample size is the number of
**worlds**, not the number of substitution samples. Per-sample 2·SE
testing on 20-world batches produced a 3× phantom "winner" in the
training-world search that collapsed to nothing on 20 disjoint seeds;
cluster-robust per-tick statistics (mean/SE over per-world mean traces)
on 100+ worlds eliminated it. Ranking differences smaller than ~2× on
100-world batches still flip between batches — replicate on disjoint
worlds before acting on one.

**Scope**: any across-sample statistic over twin-probe traces (or any
future rollout-derived statistic with shared world seeds). Applies
retroactively as a margin-of-error note on F-001/F-003, whose datasets
used 20 worlds: their per-sample significance overstates confidence for
the late bands specifically; their structural claims (two channels,
post-retune lengthening) are paired-comparison results on shared seeds
and survive, but their absolute band edges and retention decimals carry
world-batch noise.

**Evidence**: [world-search result](exp-001-bc-mappo/results/world-search-2026-07-27.md)
(the phantom, its collapse, and the fix are all reproducible from the
archived first-pass rows).

**Implications**: `search.py`'s cluster-robust `channel_metrics` is the
reference implementation; every future probe analysis uses it (the
original `analyze.py` per-sample method is superseded for significance
claims). Probe runs default to 100+ worlds.

*(Addendum 2026-08-02: the post-024 engine's flatter amplitudes moved
the power bar — three disjoint 100-world batches produced three
different search leaders with 5× swings, while 150-world batches
replicate cleanly (served world: 0.089/0.109/0.090). Probe claims on
the post-024 engine use 150+ worlds; see the post-024 world search.)*

*(Promoted 2026-08-08 → [README.md § Measurement
discipline](README.md): the discipline — cluster-robust by world,
replicate on disjoint worlds before acting. The **world-count bar is
not promoted** and stays here, engine-indexed: 100+ pre-024, 150+
post-024, post-026/027 unmeasured — re-derive it at the next probe
campaign rather than trusting either number.)*

*(Re-derived 2026-08-09 on the 028 engine, v5 family base —
[class-credit-2026-08-09.md](exp-004-rebaseline-2026-08-09/class-credit-2026-08-09.md):
three disjoint 150-world eat/drink batches replicate to **1.24× on
S(.998)≤600** but swing **1.68× on full-horizon S** (the spread is
k>600 diffusion-tail mass, batch-specific). Bar for 028-engine probe
claims: **150+ worlds, compare on the ≤600 truncated S**; full-S
differences under ~2× are batch noise. The replication discipline is
unchanged. **Class-dependence, same day**
([play-share.md](exp-004-rebaseline-2026-08-09/play-share/play-share.md)):
the 1.24× bar was derived on eat/drink (per-tick amplitude ~0.009) and
does NOT transfer to floor-amplitude classes — play/chase (~0.002)
swings 3.1× between disjoint 150-world bands and dissolves when pooled
to 300. Small-amplitude class claims require disjoint-band agreement
before they are claims at all.)*

**Would invalidate**: a demonstration that within-world sample
correlation is negligible at some horizon (it is not, at k > ~50, on
current evidence).

**Re-verify when**: n/a — this is a statistics discipline, not an
environment measurement; revisit only if the probe's sampling design
changes (e.g., one world per sample).

---

## F-005 · superseded by F-013 · Training-world knobs move detectable cooperative signal weakly; scarcity×tempo is the one replicated improver

Across 10 candidate worlds most knobs did nothing or hurt; scarcity +
tempo ×1.5 was the one replicated improver and became the frozen
training world. On the post-024 engine its gain fell below the
false-positive floor (the chase sidestep dissolved the queueing
consequences it fed on). The search was honest for an engine that is
gone. See F-013. Full text: [FINDINGS-ARCHIVE.md](FINDINGS-ARCHIVE.md).

---

## F-006 · superseded by F-013 · The default world carries no detectable cooperative credit

On the pre-024 32×32 default world, team/spillover significance sat
below the false-positive floor — the training-world selection was
load-bearing. Both of its re-verify conditions arrived at once (024 +
the 24×24 cutover) and the claim inverted: the served world now carries
a replicated cooperative band at k≈230–330. The 32×32 measurement
remains correct for the world it measured. See F-013.
Full text: [FINDINGS-ARCHIVE.md](FINDINGS-ARCHIVE.md).

---

## F-007 · active · BC initialization is necessary for MAPPO to beat the baseline at exp-001's budget

Measured 2026-07-30 (exp-001 Arms 1–3, deviation 30b). With identical §5
settings, worlds, seeds, and a 20M-tick budget, BC-initialized MAPPO
produced three maximal-significance wins over `needs_driven` (best
+0.0212 paired Nash AllSubject, 30/30 eval seeds, W=0, p=1.9e-09), while
**all six from-scratch runs finished at or below the BC clone's own
level** (−0.127 to −0.168, 0/30 seeds, both γ) despite genuine learning
(probes 0.21 → ~0.79 plateau). Diagnostic signature of the from-scratch
ceiling: unmasked-argmax mask-violation rate converges to 0.99–1.00 —
without a BC prior the policy leans wholly on the mask crutch and never
internalizes action legality. The clone alone is 0/30 (−0.120) — so
neither ingredient suffices: BC provides the floor RL climbs from, RL
provides the entire +0.13 above it.

**Scope**: exp-001's fixed factors (§4/§5 + deviations 30/30b): MLP
182→256→256→40, level Nash reward, 20M ticks, the frozen scarcity×tempo
training family, mixed control 33%. Says nothing about 10×+ budgets,
other architectures, or curriculum/objective variants.

**Evidence**: [report-protocol result](exp-001-bc-mappo/results/report-protocol-2026-07-30.md);
[Arm 2 record](exp-001-bc-mappo/results/arm2-training-2026-07-30.md).

**Implications**: the BC stage (dataset → clone → critic pretrain) is
load-bearing and stays in every exp-002 design; "more RL instead of BC"
is not a live hypothesis at this compute scale. The mask-violation rate
doubles as a cheap fingerprint distinguishing BC-lineage policies from
scratch-trained ones.

**Would invalidate**: a from-scratch run reaching baseline under a
larger budget or a different algorithm (that would narrow this to
"necessary at 20M ticks with PPO", which is still the operative claim).

**Re-verify when**: any exp-002 arm changes the training algorithm or
raises the budget ≥ 5×; then one from-scratch control seed is cheap
insurance against over-crediting BC.

---

## F-008 · superseded by F-010 (2026-07-30) · A long-horizon all-policy instability mode exists that short probes cannot detect; scripted teammates arrest it

Read a 20k-tick all-policy collapse (invisible to 2k probes) as a
long-horizon coordination instability that scripted teammates arrest.
Forensics found both halves wrong: the mode is **roster-OOD input
fragility** — visible within 2k ticks on the world that triggers it,
collapsing a single policy alone; the framing was an artifact of
certification accidentally running a different world than the probes
(deviation 31). See F-010.
Full text: [FINDINGS-ARCHIVE.md](FINDINGS-ARCHIVE.md).

---

## F-009 · active · House rule: a measurement's horizon bounds the failures it can detect

Methodological, promoted from two independent bites in one experiment:
(1) the 600-tick twin-probe traces truncated live cooperative signal
mid-band and had to be extended to 1,200 (F-003's history); (2) 2,000-
tick validation probes rated two long-horizon-unstable policies as
indistinguishable from certifiable ones (F-008). In both cases the
instrument was honest about what it measured and silent about everything
past its own horizon, and in both cases the miss was discovered only by
a longer measurement that already existed in the protocol.

*(Nuance, 2026-07-30: forensics showed bite (2) was really a
world-identity miss, not a horizon miss — the probes ran a world where
the failure's trigger never occurs, and on the triggering world the
collapse is visible within the probe's own 2k horizon (F-010,
deviation 31). The rule generalizes rather than weakens: every
dimension an instrument holds fixed — horizon, world, roster — bounds
the failures it can detect. State all of them with the claim.)*

*(Third bite, 2026-08-07, folded in at promotion: the **seed band** is
one of those dimensions. Three independent signs in one week — exp-003's
§9.2 admitting none of nine candidates, the bimodal failure split, and a
[screen that voided itself](screens/geometry-20x20-2026-08-07/results.md)
because its control showed 241-tick distress on a band where the same
artifact on the same world had scored zero; the criterion had
generalized one band's zero into a policy property. `max_distress_age
== 0` is a property of policy × world × seed band. State the band with
the claim.)*

*(Promoted 2026-08-08 → [README.md § Measurement
discipline](README.md): every criteria/prereg measurement section must
declare its instrument's held-fixed dimensions — horizon, world, roster,
seed band, selection mode. This entry stays as provenance.)*

**Scope**: any instrument whose readings feed a decision — probes,
validation curves, smoke evals, forensic re-checks.

**Evidence**: F-003 (probe extension), F-008 (probe-vs-certification
divergence); the general pattern is the point.

**Implications**: when designing any measurement, state the horizon of
the *claim* it supports and check the instrument covers it; when a
shorter instrument is used for economy (2k probes during training),
record what it cannot see and gate decisions on the full-length
instrument. Companion to F-004 (which is the same discipline for sample
*structure* rather than sample *length*).

**Would invalidate**: n/a — a discipline, not an environment
measurement; revisit only if it stops paying for its enforcement cost.

**Re-verify when**: n/a.

---

## F-010 · active · Roster-OOD fragility: an empty kitty slot can collapse an exp-001 policy into idle catatonia (supersedes F-008)

Measured 2026-07-30 (collapse forensics + served-world re-measurement,
deviation 31). Observations carry three proximity-sorted kitty slots;
exp-001's training family (5 kitties) and anneal world (4 kitties) keep
them always full. The compiled 3-kitty default world — which every
pre-deviation-31 certification unknowingly ran — leaves one slot
permanently empty: an input outside training support. On it, **3 of 9
Arm 2 training seeds collapse into an idle attractor** (85% Idle
post-onset, zero eat/drink, all kitties in permanent distress, welfare
≈ 0.31), tipped by element layout (the same policy is healthy on
another eval seed; a robust policy is healthy on the "collapsing"
seed). Collapse is visible within 2,000 ticks on the triggering world
(seed 8: welfare 0.58 at t=2000, first unresolved distress t≈769). The
same policies on the served world (`cloudkitty.toml`, slots full):
certification-clean — max distress age 0 across 60 runs, deltas +0.04.

Re-reading F-008's observations: "scripted teammates arrest it" = in
Mixed rosters only the lone subject idles while competent scripted
kitties keep the world afloat; "invisible to 2k probes" = the probes
ran a world (served) where the trigger never occurs. Env-chain replay
reproduces the engine's certified numbers exactly given the same
config.

**Scope**: exp-001's policy class (MLP on slot-structured obs, BC
lineage, frozen family). The *mechanism* — undefined extrapolation on
slot patterns absent from training — plausibly generalizes to any
slot-structured encoding; the 1/3 seed rate is specific to this class.

**Evidence**: [collapse forensics](exp-001-bc-mappo/results/collapse-forensics-2026-07-30.md);
[served-world re-measurement](exp-001-bc-mappo/results/served-world-remeasure-2026-07-30.md);
tool `trainer/forensics_replay.py`.

**Implications**:
- **exp-002's primary robustness target**: make empty-slot patterns
  in-distribution (roster 3–5 coverage in the training family — the
  bill for family-v1's deferred roster variation — or absent-slot
  masking in the encoding).
- **Candidate screening**: certify-length runs on every roster the
  deploy surface can present (3, 4, 5). The compiled 3-kitty world is
  retained as an explicitly-named secondary robustness screen
  (deviation 31), never the primary gate.
- The partner-population-curriculum hypothesis is weakened as the fix
  for *this* mode (it is not self-play resonance) but not dead.

**Would invalidate**: the collapse reproducing on a full-slot world
(would reopen a genuine coordination-instability reading); roster-
covered exp-002 policies still collapsing on 3-kitty worlds (would
implicate something beyond slot support).

**Re-verify when**: exp-002 candidates reach screening; any change to
the obs slot encoding or slot count.

## F-011 · active · Design premise: meow restraint is a reward-structure equilibrium, not an engine guarantee (spec 023)

Spec 023 retired the engine-enforced meow cooldown ("manners, not
law"): learned agents face no rate limit on the channel. The spam
backstop is now *economics under the cooperative team reward* — a
meow costs a turn, misleading teammates lowers the shared objective,
and an always-on signal devalues its own contrast in the presence
digest. Evidence the equilibrium is real: s6 settled at ~0.1% meow
rate with functional listening on the receiving end, under no
compulsion beyond the (old) cooldown.

**Scope**: any training or serving configuration using CloudKitty's
cooperative team reward. The premise is the *reward structure*, not
the policy class.

**Evidence**: issue #84 (design record); spec 023;
[meow-listening probe](exp-001-bc-mappo/results/meow-listening-2026-07-31.md);
[s6 promotion record](exp-001-bc-mappo/results/s6-promotion-2026-07-30.md).

**Implications**:
- **Any per-kitty or competitive reward design voids the premise.**
  Revisit spec 023 before training under such a reward — a
  self-interested agent may find channel manipulation or saturation
  profitable, and the engine will not stop it.
- Scripted behaviors are not covered by the economics; their restraint
  is the behavior-level courtesy values (`[meow] courtesy_ticks`),
  which any new scripted behavior must also consult.

**Would invalidate**: a cooperative-reward policy learning sustained
channel saturation that survives training (would show the economic
argument insufficient even under shared reward).

**Re-verify when**: any reward-structure change; exp-002 candidate
screening (check channel-use rates alongside welfare).

## F-012 · active · Channel use is context-dependent: solo probes underestimate a policy's meow behavior

s3 — silent in every solo measurement (certifications, forensics,
the "s6 is the only meower among nine seeds" survey) — emits FollowMe
meows and the occasional WantCuddle as soon as its world contains
another *policy* kitty. The rate is **bursty, not steady** (correction
2026-08-01; the original "7–16 per seed" was the two arms' means):
Seating B per-seed FollowMe over seeds 1–10 is 0, 1, 0, 1, 3, 19, 5,
13, 112, 5 — eight near-silent seeds and two carrying the bulk, seed 9
alone 112 of 159. The behavior was latent: never expressed among
scripted neighbors, unmasked by policy company — and when expressed,
episodic.
s6's behavior also shifts in the pair world (deliberate purrs down,
WantDrink up), consistent with two-way channel traffic.

**Scope**: exp-001's policy class; plausibly any policy whose training
population (self-play siblings) differs from its evaluation population
(scripted cats) — the behavior was learned *for* an audience that solo
evaluation removes.

**Evidence**: [pair-screen record](exp-001-bc-mappo/results/pair-screen-2026-07-31.md)
(attribution tables); prior null:
[meow-listening probe](exp-001-bc-mappo/results/meow-listening-2026-07-31.md).

**Implications**:
- Channel-use surveys for selection or preservation (exp-002 §1's
  levers) must measure candidates **in policy company**, not solo —
  the 1/9 "meower base rate" is a solo-context floor, not the truth.
- The mixed-model roster is likely to be chattier than any solo
  measurement predicts; viewer-facing meow volume should be assessed
  on the actual roster.
- Latent-behavior logic generalizes: any social behavior (grooming,
  duets) may be under-counted by solo probes.

**Would invalidate**: attribution showing FollowMe emission is an
artifact of the seat (a scripted-behavior interaction) rather than
s3's policy — checkable by seating s3 with scripted-only rosters at
the same seats (it was silent there in certification Mixed runs,
which *is* that control: same seats, scripted neighbors, no meows).

**Re-verify when**: exp-002 candidate screening; any channel-use
selection measurement.

## F-013 · active · The 024 batch rewired the credit landscape: the served world gained a cooperative band, the frozen gym lost its edge (supersedes F-003/F-005/F-006 quantities)

Measured 2026-08-02, the fired engine-defaults triggers executed
(six probe runs, cluster-robust per F-004, replication batches
included). Three coupled results:

1. **The current served world (`cloudkitty.toml`, 24×24, post-#86
   cutover) carries a replicated cooperative band at k ≈ 230–330** —
   dr 82/111 significant ticks on two disjoint 150-world batches
   (floor ≈ 60), 25–43-tick contiguous runs, peak amplitude ~0.003–
   0.005, S(.998) ≈ 0.09–0.11 — 3.4–4× the frozen gym's best pre-024
   showing. Spillover co-locates (peak k=311).
2. **The frozen scarcity×tempo gym lost its signal on paired seeds**
   (3001–3150, engine-only change): 68 → 36 significant dr ticks
   (sub-floor), S(.998) 0.026 → 0.011, surviving mass pushed to the
   k≈930 queueing remnant. Consistent mechanism: the chase sidestep
   dissolves the stall-queueing consequences that were the gym's
   measured advantage (F-005's own k≈730–940 signature).
3. **Geometry deconfound**: on the post-024 engine, the served config
   at 32×32 (F-006's shape) is borderline (57 ticks, S(.998)=0.036);
   at 24×24 it is clear. The 24×24 cutover is the dominant factor,
   the engine's new water economics a plausible contributor — the
   contention mechanism of F-005/F-006, now working in the served
   world's favor.

The two-channel *structure* (F-001→F-003 lineage) re-confirms
everywhere: early self band (k ≤ ~16) in every run, team credit slow.

**Scope**: `needs_driven` dynamics, post-024 engine (`6d955ab`),
current served config and frozen `training.toml`; 1,000 samples ×
1,200-tick traces per run. Trained-policy dynamics unmeasured (as
always). Class-conditioned structure (the play/chase 3.6× prior)
unmeasured on this engine.

**Evidence**: [post-024 re-verification](exp-001-bc-mappo/results/twin-probe-2026-08-02-post024.md)
(all six runs, dense retention curves, regeneration commands).

**Implications**:
- **exp-002's training-world choice is reopened and inverted**:
  training on a family centered on the served world is the
  evidence-backed default hypothesis (family-gen v3 already centers
  24×24); the frozen gym is no longer self-recommending. A slimmed
  post-024 world search should confirm before the prereg freezes.
- **γ**: the served-world band sits inside γ=0.998's horizon; 0.995's
  horizon ends before the band begins. Sweep {0.995, 0.998} stands;
  0.9985 only as a conditional arm if the chosen world's band peak
  lands past k ≈ 500.
- Certification on the served world is no longer credit-blind —
  paired-Nash gains there may partially reflect marginal cooperative
  credit (F-006's welfare-gate-only framing is retired with it).
- Every pre-024 probe quantity is design-dead; re-measure
  class-conditioning on the chosen world before citing it.

**Would invalidate**: the served-world band failing to reproduce on
further disjoint batches or dissolving under trained-policy dynamics;
a future engine or config change (this finding inherits the same
mortality as its predecessors).

**Re-verify when**: any engine-defaults or served-config change; the
first exp-002 policy artifact reaches candidate stage (policy-seated
probe, both worlds, per the F-001→F-003 standing trigger).

## F-014 · active · Post-024 world search: the served world wins as it stands; the knob landscape is flat at 100-world power

Measured 2026-08-02 (F-013's recommended slimmed search, executed:
nine served-centered candidates + the gym incumbent, three disjoint
100-world rounds + a 150-world finalist wave, welfare-gated).

1. **No searched knob beats the served world.** At 150-world power:
   served S(.998) = 0.0896 (its *third* independent 150-world
   replication: 0.089/0.109/0.090 — the strongest replication record
   any world has held here); tempo125 0.066; roster5 0.041; size22
   sub-floor; gym 0.017 (third sub-floor batch). Scarcity and tempo —
   the pre-024 winners — now *hurt* or do nothing.
2. **The knob landscape is flat at 100-world power**: three disjoint
   100-world rounds produced three different leaders with 5× swings
   (incl. a one-batch tempo125 early-band phantom). The pre-024
   amplification regime (scarcity×tempo 1.5–1.8×, replicated at this
   exact instrument) does not exist on the new engine.
3. **Roster is a real signal knob**: adding a 5th kitty halves the
   served world's S (0.090 → 0.041, mass spreads later) — more cats,
   more chaotic mixing. The family's F-010 roster stratification is
   therefore a quantified signal-for-robustness trade.

**Scope**: needs_driven/playful scripted dynamics (policy seats
neutralized), post-024 engine (`6d955ab`), the searched knob ranges
(sizes 22/26, scarcity two notches, tempo ×1.25, roster ±1). Not
searched: durations, trait spreads, element ratios, tempo below 1×.

**Evidence**: [world-search-2026-08-02-post024.md](exp-001-bc-mappo/results/world-search-2026-08-02-post024.md);
driver `experiments/tools/world-search/search_post024.py`.

**Implications**: exp-002's family base = the served world shape
(family-gen v3 jitter as the variation envelope; 5-kitty base variant
for roster stratification carries the quantified signal cost);
γ sweep {0.995, 0.998} confirmed (the served band sits inside 0.998's
horizon — F-013's conditional 0.9985 rule stays dormant unless the
family's realized band peak moves past k ≈ 500); probe claims on this
engine use 150+ worlds (F-004 addendum).

**Would invalidate**: a knob outside the searched ranges beating the
served base at 150-world power; trained-policy dynamics reshaping the
landscape (the standing caveat everywhere).

**Re-verify when**: any engine-defaults or served-config change;
exp-002 candidate stage (policy-seated probe re-ranks the worlds that
matter).

## F-015 · active · Pooled all-action probes dilute under heterogeneous class amplitudes; class-conditioned batches carry the credit signal

Measured 2026-08-03 on the exp-002 family base, post-025 engine
(`0fd551d`), 150 worlds per batch (F-004 addendum), identical recipe
and seeds as the post-024 measurement it pairs with.

1. **The registered spec-025 prediction confirmed** (registered
   2026-08-02 in the handoff + census doc, before the change
   landed): the per-target play-relief gradient lifted the
   play/chase credit class off its post-024 floor — S(.998)
   0.0039 → 0.0245 (6.3×), significant ticks 8 → 43, real bands,
   peak k=301 (inside 0.998's horizon). Eat/drink doubled
   (0.0333 → 0.0709, now the largest class); groom/sleep/rest
   roughly held (0.0334 → 0.0399).
2. **The methodological finding: the pooled all-action batch went
   sub-floor while every class rose** (S 0.0387 → 0.0099, 30
   significant ticks against fp ≈ 60). Verified mechanism is
   dilution, not cancellation: all classes are positive-signed, but
   play/chase decision points are the most abundant in the pool
   (density 0.71) with the smallest per-tick amplitude (+0.0003 vs
   eat/drink's +0.0087), so the pooled per-tick mean drops below the
   2·SE bar. A pooled probe's "all-action" S is a
   composition-weighted average, NOT a ceiling or a denominator —
   post-024's convenient "class ÷ all" ratio framing only worked
   because amplitudes happened to be comparable.

**Scope**: the twin-probe substitution instrument with cluster-robust
per-tick means; scripted dynamics on the family base. The dilution
mechanism is instrument-generic (any pooled mean over heterogeneous
subpopulations), so assume it wherever decision-type frequencies and
effect sizes are inversely related.

**Evidence**: [class-credit-2026-08-03-post025.md](exp-002-mixed-population/results/class-credit-2026-08-03-post025.md)
(supersedes the post-024 table's ratios, not its record).

**Implications**: credit claims compare class-conditioned absolute S
values, never class-vs-all ratios; an all-action batch still runs as
a composition read (its density and sign structure), not a credit
score. Prereg §10.1 diagnostics watch eat/drink, groom/sleep/rest,
AND play/chase (re-entered post-025). The §3 dormant-γ trigger
outcome (F-9985 follow-up cell) survives the refresh: late bands
persist past k ≈ 500 in the class batches.

**Re-verify when**: any engine-defaults change; when policy-seated
(rather than scripted) probes become available at the exp-002
candidate stage. *(Trigger FIRED, 2026-08-08 review: the 026/027 batch
moved the engine to stamp `cba976da…` and no re-measurement has run —
the class amplitudes and densities above are stale on the current
engine. Queued as exp-004's first probe obligation; the dilution
mechanism itself is instrument-generic and stands.)*

*(RE-VERIFIED 2026-08-09 on the 028 engine, v5 family base, identical
recipe —
[class-credit-2026-08-09.md](exp-004-rebaseline-2026-08-09/class-credit-2026-08-09.md):
pooled all-action sub-floor again (33 sig ticks, fp ≈ 60) while
eat/drink carries S(.998) 0.0663 (4.5× pooled) and groom/sleep/rest
0.0398 (2.7×); same mechanism, dilution not cancellation (play/chase
density 0.69, amplitude 0.0020 vs eat/drink 0.0091, all positive).
The 2026-08-03 base cannot load post-028 (courtesy trio), so the new
table is a fresh record, not a paired comparison. The flag clears; the
trigger conditions stand unchanged. The initially-flagged play/chase
"halving" (0.0245 → 0.0125) was investigated same-day and **withdrawn
as a batch artifact** — an identical-config disjoint-band replication
swung 3.1× and pooling dissolved significance entirely; play/chase
credit is below reliable measurement at standard batch sizes on this
engine
([play-share.md](exp-004-rebaseline-2026-08-09/play-share/play-share.md)).)*

---

## F-016 · active · The wet-fur dial subsidises the behaviour it prices: raising bath_gain increases scripted on-water time through the grooming channel

Measured 2026-08-06 on the post-027 engine
(`cba976dae4b88703…`), served world, all four seats scripted, 10 seeds
× 20k ticks, paired across identical seeds.

1. **Raising `bath_gain` 1.5/50 → 3.5/60 *increases* total scripted
   in-water share**, in all four splits measured: policy seats
   +0.333pp (8/10 seeds) at `edge_penalty` 2.0 and +0.682pp (9/10) at
   0; the historical reference seats +0.218pp and +0.211pp (7/10
   each).
2. **The mechanism is grooming, and it is a feedback loop.**
   Decomposed by activity, every avoidance the dial was aimed at
   happens — resting on water −0.043pp, sleeping −0.044pp, playing
   −0.024pp — while **grooming-on-water rises +0.414pp (+61%)** and
   swallows the rest. `Activity::Grooming => Some(NeedKind::Bath)`
   (`kitty.rs:165`) with `groom_relief` applied to Bath
   (`action.rs:699`), and the wet-fur charge *raises* Bath per
   occupied water tick: being wet makes a cat want a bath, a
   `needs_driven` cat takes it where it stands, and standing there
   keeps charging. A higher gain engages the loop sooner.
3. **A scripted floor and a learned policy move oppositely on this
   lever.** exp-002's §9.1 dial resolution found a *policy's*
   grooming-on-water fell ~60% between dials while its sleeping-on-water
   was stubborn. Same channel, opposite sign, different decider — so a
   scripted baseline is not a conservative proxy for policy behaviour
   here, in either direction.
4. **`edge_penalty` does not move water occupancy at this power**:
   4/10, 3/10, 5/10, 5/10 seeds positive across the same four splits,
   signs disagreeing, every delta inside its own seed spread. Its
   effect is on welfare (+0.00049, 7/10), which is what it was for.

**Scope**: scripted `needs_driven`/`playful` dynamics on the served
24×24 world with a guaranteed lake, dials 1.5/50 vs 3.5/60,
`edge_penalty` 0 vs 2.0, 10 seeds × 20k ticks. Says nothing about
learned policies on this engine — none can run on it yet (observation
schema 1 artifacts are rejected outright). The mechanism is structural
rather than dial-specific, so expect it wherever a cost raises a need
whose relief activity is location-indifferent.

**Evidence**: [rebaseline-2026-08-06/results.md](rebaseline-2026-08-06/results.md);
instrument `experiments/rebaseline-2026-08-06/scripted_water_baseline.py`.

**Implications**: exp-003 cannot register "in-water share" as a single
gated number — it pools a channel the dial suppresses with one it
amplifies. Split grooming out, and set H2's band against the
same-engine scripted measurement (policy seats: 1.50% lounging / 3.44%
in-water), noting that exp-002's registered ≤3.0% in-water ceiling now
sits *below* the scripted baseline in those seats. If the goal is to
price lingering rather than bathing, the lever to reach for is the
ceiling (which caps the accumulated need, and so caps how often the
grooming loop re-arms) rather than the gain.

**Re-verify when**: engine defaults change; `groom_relief`, the bath
happiness weight, or the wet-fur charge move; and — first opportunity —
when a schema-2 policy exists, since point 3 predicts it will not
follow the scripted direction.

---

## F-017 · active · The multi-copy collapse is largely a symmetry artifact: identical greedy policies deadlock over contested resources, and sampled selection dissolves it

Measured 2026-08-07 on the post-027 engine (`cba976da…`), all nine
exp-003 candidates, roster-5 world, 30 seeds × 20k, `--roster
all-policy`, greedy vs `--sample` on matched seeds.

1. **Breaking the tie removes the catastrophe.** `floor_touches`
   **108,584 → 0** across the sweep; worst `max_distress_age`
   **16,027 → 1,020**. The two collapsing candidates fall 300× and 15×,
   and their welfare recovers from 0.9126 / 0.8681 to ~0.921 — into the
   band the healthy candidates already occupied. Fallbacks zero in both
   modes.
2. **The mechanism is symmetry, not incapacity.** Four identical
   deterministic policies observing similar states select the same
   action, converge on the same resource tile, and deadlock; the
   worst-off cat starves while the whole roster degrades. (Mechanism
   *inferred* — from the greedy-vs-sampled contrast, the failing-need
   signature, and the chow-tile geometry result; the committed JSON is
   outcome-level, no position traces.) Eat leads the failing needs in
   every §9.2 probe, drink usually second — the contested consumables —
   and adding a single chow tile to a 20×20 world independently moved
   incident runs 9/60 → 1/60
   ([geometry-20x20-optE screen](screens/geometry-20x20-optE-2026-08-07/results.md)).
   Two different interventions on contention, same direction.
3. **Very little noise is required.** End-of-training policy entropy is
   **0.31–0.39 nats** (uniform over the 40-action menu would be 3.69),
   so `--sample` is near-greedy — it mostly agrees with the argmax. The
   tie is fragile; breaking it is cheap.
4. **Mixed and self-play arms respond oppositely**: mixed worst-case
   mean **5,494.7 → 213.2** (26× better), self-play **80.0 → 135.7**
   (slightly worse). Self-play trains entirely under self-contention and
   has already learned to break symmetry behaviourally, so randomisation
   only adds noise; mixed arms spent a third of training with no
   self-contention and never learned it. This is a second, independent
   line of evidence for the same mechanism as the mixing gradient
   (exp-002's monotone 0/33/67 replication).
5. **Not a free win**: incident *counts* fall only 92/270 → 69/270, and
   the improvement is not uniform — by worst distress two candidates
   worsen (A2-s1, A2-s3), by incident count three do (a different set:
   A0-s2, A1-s1, A2-s1). Sampling trades a rare catastrophic tail for
   slightly more frequent small wobbles.

**Scope**: exp-003's schema-2 MLP policies on the roster-5 family world
at four occupied seats. Says nothing about deployment, which seats two
policies among two scripted cats and shows **zero** distress under
greedy selection either way. The symmetry argument is generic to
identical deterministic agents sharing scarce indivisible resources, so
expect it wherever policy share is high; the *magnitudes* are specific
to these policies and this world.

**Evidence**: [selection-symmetry-2026-08-07.md](exp-003-water-schema/results/selection-symmetry-2026-08-07.md);
per-run JSON committed beside it, seed band 810k.

**Implications**: an all-policy collapse is weak evidence about policy
*quality* — it conflates a coordination failure with a competence
failure, which matters directly for respecifying exp-003 §9.2's roster
gate (it admitted none of nine). For exp-004, symmetry-breaking rises up
the knob list in two forms: cheap and behavioural (sampled selection, or
a per-seat identity feature letting copies specialise) and principled
(the meow channel — signalling intent is the designed resolution for
resource contention, `WantEat` already exists, and these policies never
learned to use it: greedy `meow/1k` 0.01–0.41). Nothing here licenses
switching the served world to sampled selection: every §9.1 water figure
— and the deployment record itself (Deviation 1: deployed, **not**
certified) — is greedy, so a switch needs re-measurement rather than
assumption.

**Re-verify when**: policy entropy at convergence moves materially (the
effect depends on distributions being sharp); a policy trained with any
explicit symmetry-breaking or coordination mechanism exists; or the
action menu changes such that resource targets stop being indivisible.
