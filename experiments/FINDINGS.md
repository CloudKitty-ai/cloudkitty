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
| F-011 | superseded → F-018 | Meow restraint is a reward-structure equilibrium, not an engine guarantee |
| F-012 | active · **promoted** | Channel use is context-dependent; measure in policy company, not solo |
| F-013 | active | The 024 batch rewired the credit landscape; the served world gained a cooperative band |
| F-014 | active | Post-024 world search: the served world wins as it stands; knob landscape flat |
| F-015 | active | Pooled probes dilute under heterogeneous class amplitudes; condition by class |
| F-016 | active | Raising bath_gain increases scripted on-water time via the grooming channel |
| F-017 | active | The multi-copy collapse is largely a symmetry artifact; sampling dissolves it |
| F-018 | active | The channel is two-layer: legality is engine law, meaning is reward economics |
| F-019 | active | Clone-then-leash preserves visible personality; unleashed welfare-RL erases it |
| F-020 | active | Trait prices are social prices: the cost order inverts between scripted and policy company |
| F-021 | active | Seeing beats pricing: one observation bit bought the water behavior no reward dial could |
| F-022 | active | The channel comes alive through demonstration, then the policies author its meanings |
| F-023 | active | Channel dials are listener-population properties; no composition-free optimum exists |
| F-024 | active | Entity attention: welfare parity, 40% fewer params, structural robustness, wider expression space |
| F-025 | active | Same recipe, different seed: dialects and cultures, mutually intelligible, welfare-coupled |
| F-026 | active | Under global vision the channel is welfare-redundant — the measured baseline fog must overturn |
| F-027 | active | Twin-seating one artifact creates dyadic self-interaction attractors |
| F-028 | active | Census raws are attributable only if the instrument records its own provenance |
| F-029 | active | A reader rule copied from the wrong contract shape reports a category that cannot exist |
| F-030 | active | Per-event shaping of a social behavior buys initiation churn; the KL leash does not prevent it |
| F-031 | active | A partnered scene runs its minimum only if the counterpart is pinned; grooming is the exception |
| F-032 | superseded → F-033 | Biscuit's idle read as the legality funnel refusing a partnered ask (inference; narrowed to 45% of idle) |
| F-033 | active | Every seat pays a partnered-action refusal tax in its own currency; for Biscuit under half her idle, the rest chosen (pre-048 bars retired by F-039) |
| F-034 | active | Here* vocabulary cloning is a cliff between 5.6% and 8.2% corpus share, not near 1% |
| F-035 | active | The waterline charge is a magnet before it is a fence: charge-blind arms drift toward the edge |
| F-036 | active | The needflow model is not a proxy for the scripted teacher; three engine gates invert the sleep niche |
| F-037 | active | The collapse detector names a lock but trails the watchdog by 48–147 ticks; healthy margin 0.07 |
| F-038 | active | Comfort buys food promptness linearly and pays in element play, never duets; t_partner 5 halves roster duets |
| F-039 | active | Live refusal tax is Biscuit's alone and it is partner play (5.13%); other seats under 2.3% in groom and move |

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

*(Bar status, 2026-08-16 review: the engine-indexed world-count bar is
UNMEASURED on the post-wall stamp `5d293c67…` — the 150+/truncated-S
bar above is a 028-engine number. Re-derive it as part of the phase-1
class-credit re-baseline (queued, phase1-design-inputs.md §4) before
any post-wall probe claim leans on it.)*

*(RE-DERIVED 2026-08-17 on the post-wall stamp, phase-1 collection
base —
[class-credit-2026-08-17.md](exp-006-character-gen/results/class-credit-2026-08-17.md):
eat/drink S(.998)≤600 replicates within **1.28×** across three
disjoint 150-world bands (875k seeds); the bar stands as 150+
worlds / ≤600 truncated S. The floor-class warning re-fired in the
same campaign: play/chase batch A read 4–9× above its own B/C
replications (late-k peaks, diffusion tail) — the second
single-batch play/chase excursion withdrawn by replication, now a
standing presumption for that class.)*

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

*(Trigger status, 2026-08-16 review: FIRED in spirit at the attention
generation — the policy class changed (EntityPolicy, spec 030) with
recipe and budget held — and the from-scratch control seed has never
run on the new class: BC-necessity is carried as a recipe default, not
re-established. Two reasons it likely still holds, neither a
measurement: the budget is unchanged (the claim is budget-indexed),
and F-022 adds an independent necessity argument (the channel only
comes alive through demonstrations — a scratch policy would be mute
regardless of welfare). The control seed remains cheap (~one PPO run)
if the phase-1 prereg wants the register claim re-established on the
current class; owner's call, flagged not queued.)*

*(RE-ESTABLISHED on the attention class, 2026-08-16 — in a STRONGER
form than the original claim. The scratch control (`--scratch`: random
init, KL identically 0, recipe otherwise held; exp-005 trainer commit
89594c4, trip recorded as its D-002) collapsed below the recipe's
§9.6 welfare stop within 149 of 6,510 updates: probe nash 0.70 at
init → 0.36 and falling, entropy RISING 1.69 → 1.90 (drifting toward
noise, not learning). The matched clone-init run at the same beta
endpoint (exp-005 β∞=0) trains cleanly to nash 0.953. So at this
recipe and budget, BC init is not merely necessary to beat the
baseline — it is necessary for the run to survive its own safety
rule. Channel note: the scratch policy emitted 300–500 meows/1k of
mask-random babble — volume without meaning, which is F-022's
distinction, not a counterexample to it. One seed; the collapse
margin (0.36 vs 0.95) is far past any seed-noise reading.)*

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

*(Trigger FIRED at the attention generation, 2026-08-13/14: the
encoding changed (entity tokens, spec 030). Addressed operationally,
not by a dedicated retest — the certification battery's stress shapes
(iii/r3/r5, the §9.2 bar-225 gate) bake vacancy patterns into every
candidate screen, and the attention-era candidates passed with no
catatonia; roster 5 with `kitty_slots` 3 makes someone-always-unslotted
a *designed* condition of the phase-1 world. The encoding-level retest
proper folds into phase 2, where variable entity tokens make absence a
normal input (ROADMAP).)*

## F-011 · superseded by F-018 · Meow restraint is a reward-structure equilibrium, not an engine guarantee

Held from spec 023 (no engine rate limit; restraint priced by the
turn cost and team reward) until spec 028 removed the turn cost
(ride-along head) and returned the cooldown as mask legality — law,
not manners. The reward-structure half survives in F-018. Full text:
[FINDINGS-ARCHIVE.md](FINDINGS-ARCHIVE.md).

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

*(Promoted 2026-08-16 → [README.md § Measurement
discipline](README.md): measure social behavior in the deployment
composition. The trigger wording above is era-stale — the discipline
has re-confirmed at every level since: selection (exp-003/004
screens), the dial level (F-023), the welfare level (F-025), and the
exp-005 fingerprint probes measure in the demonstration composition
by prereg rule. The standing form binds all future measurement; this
entry stays as provenance.)*

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

*(Trigger FIRED repeatedly since: the served world moved to 20×20
(PR #127, 2026-08-08) and the engine stamp through `cba976da…` →
`412d00e2…` → `5d293c67…` (026/027, 028, the 031+033 wall). The band
quantities and the 24×24 location claims above are historical; the
class-conditioned re-measurements of 2026-08-09 (see F-015's note) are
the most recent credit reference, and a full re-baseline on the
post-wall stamp is queued as phase-1 re-baseline work
(phase1-design-inputs.md §4). The two-channel structure has
re-confirmed at every re-measurement.)*

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

*(Same fired-trigger status as F-013 — served config and engine both
moved (20×20, stamps through `5d293c67…`). The search's negative
result (no knob beats the served shape) was re-affirmed in spirit by
the 2026-08-15 world-size screen (proportional 22×22 bought nothing,
zero-distress at 20×20 with five bodies; trait-screen results.md),
but trait spreads — explicitly unsearched above — enter the phase-1
family per its design inputs.)*

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

*(Trigger FIRED AGAIN, 2026-08-16 review: the 031+033 wall moved the
stamp to `5d293c67…` with no class-credit re-measurement since. Queued
as the phase-1 class-credit re-baseline (phase1-design-inputs.md §4);
the dilution mechanism itself is instrument-generic and stands.)*

*(RE-VERIFIED 2026-08-17 on the post-wall stamp, phase-1 collection
base (sheets + playful demonstrator) —
[class-credit-2026-08-17.md](exp-006-character-gen/results/class-credit-2026-08-17.md):
pooled all-action at the floor again (64 sig ticks, fp = 60, ≤600 S
0.0124) while eat/drink carries 0.0391 and groom/sleep/rest 0.0419
on the truncated statistic; densities match the 028-era table to
two decimals, so the wall + composition change moved amplitudes,
not decision frequencies — and the stable classes barely at that
(eat/drink ≤600 within 11% of its 028-era band values). Play/chase
produced its second single-batch excursion, withdrawn by B/C
replication (see the F-004 annotation). The flag clears; triggers
stand.)*

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

*(Status note, 2026-08-16 review: the bath dials themselves are
unchanged through the 033 wall (the stamp moves came from other
fields), and the point-3 prediction remains unmeasured — schema-2+
policies have existed since exp-003, but no paired policy-side dial
measurement has run. Standing, not fired.)*

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

*(Trigger FIRED and absorbed into operating practice, 2026-08-08/09:
the exp-004 groundwork closed sampled selection for the served world
(greedy stays), and the §9.2 respec this finding demanded became the
bar-225 gate (max(1, floor(0.05n)) exceedances, stress shapes
iii/r3/r5) — the identical-copies stress is now a standing battery
condition rather than a disqualifying surprise. The "principled
resolution" implication came true: exp-004-era policies are
meow-equipped and use the channel (~100/1k vs the 0.01–0.41 measured
above), and the attention-era candidates pass the iii shape within the
bar. Heterogeneous per-seat traits (phase 1) de-symmetrize the roster
further by construction.)*

---

## F-018 · active · The channel is two-layer by design: legality is engine law, meaning is reward economics (supersedes F-011)

Settled across specs 028 and 033 (2026-08-09 → 2026-08-15) and
measured through exp-004 and the attention generation. The channel's
architecture split F-011's single "economics" story into two layers
with different guarantors:

1. **The legality floor is law.** The cooldown lives in the mask
   (per-cat-per-kind — an illegal meow cannot be selected, not
   merely discouraged); law-named kinds (Purr, Here* 9–12) carry
   grounded predicates the engine verifies at emission (adjacency
   family-wide, purr_earned); the naming law (033 FR-002b) forbids a
   kind's name asserting meaning its predicate doesn't enforce. spec
   028 also removed F-011's central cost mechanism: the ride-along
   head means a meow no longer costs a turn, and measured channel
   rates rose accordingly (~100/1k vs the old ~0.1% — the turn-cost
   economics F-011 leaned on are gone).
2. **Everything above the floor is still equilibrium.** The engine
   guarantees EMISSION-TIME truth only (owner pin, spec 033):
   referent preservation, listening, restraint beyond the cooldown,
   and the meaning of the sound-named free register (mew, chirp,
   trill, ekekek) are learned team-reward equilibria with no engine
   mechanism — docs/meows.md carries this as its non-guarantees
   section. F-011's surviving clause carries forward verbatim: **any
   per-kitty or competitive reward term voids this layer** (this is
   why exp-004 used team-level potential shaping only, and why the
   leash is a constraint, never an objective — F-019).

**Scope**: the post-028 two-head decision surface, any policy class;
layer 1 is engine law wherever the mask/legality path is used
(bc-collect, PPO env, serving); layer 2 assumes the cooperative team
reward.

**Evidence**: spec 028 + exp-004 results (rates, responder gate,
imitability design records); spec 033 (naming law, grounded
predicates, emission-time-truth pin); docs/meows.md non-guarantees;
F-011's archived record for the pre-028 world.

**Implications**: channel claims must name their layer — "cats can't
spam HereFood at a bare tile" is law; "cats don't announce food they
intend to abandon" is an equilibrium to *measure*, never assume
(hosting/courtesy measurement duties are registered for the fog era).
Certification watches layer-2 quantities (channel rates, listening)
because nothing else enforces them.

**Would invalidate**: an engine mechanism that enforces meaning
(would collapse the layers — flagged in 033 as deliberately rejected:
pinned coordinates were refused to keep emitter-tracking honest); a
cooperative-reward policy sustaining channel saturation *within*
legality (would show the floor too low, echoing F-011's original
invalidation clause).

**Re-verify when**: any reward-structure change; any legality-flag or
vocabulary change (the reserves arming, fog-era Here* activation);
the first plugin/LLM seat (whose proposals bypass training economics
entirely — only layer 1 constrains it).

## F-019 · active · Clone-then-leash preserves visible personality; unleashed welfare-RL erases it (exp-005, the dose-response)

Measured 2026-08-16 on the frozen exp-005 design (β∞ ∈ {0, 0.05,
0.2} × 2 seeds, A1 recipe, playful-Biscuit clone as init AND anchor,
fingerprints in the demonstration composition per F-012).

1. **The erosion is real and total at β∞=0**: both control seeds
   collapse the fingerprint (play_share −68%/−61% relative,
   bug_over_meal → 0, duets → 5%, near-critters → a quarter) while
   gaining ~14 happiness — the sunbeam/want-word pattern, now
   measured end to end on a registered design.
2. **A held KL floor stops it**: at β∞=0.05 the fingerprint is
   substantially anchor-grade and welfare still recovers +5–7; at
   0.2 the fingerprint is anchor-grade and welfare recovers ZERO —
   the strong leash is expensive cloning. The knee of the trade is
   at-or-below 0.05; decision metrics saturate between 0.05 and 0.2.
3. **The leash bound trajectories, not just decisions** (the
   registered H4 risk did NOT materialize): time_near_critters stays
   anchor-grade at both doses under global vision.
4. **The most welfare-expensive expression erodes first, with seed
   lottery**: duet initiation is the most eroded and most
   seed-variable metric at every dose (−56/−42% at 0.05, −54/−20% at
   0.2). A dose alone cannot secure a social-play identity claim;
   the fingerprint gate needs a floor on the specific expression,
   and candidates will vary against it seed to seed.

**Scope**: EntityPolicy on the pre-wall 197 surface, global vision,
the A1 recipe with β0=0.5 annealed over 20% then held, one
personality (playful) and one methodological anchor at pre-rebalance
traits. Dose numbers are recipe- and personality-conditional; the
qualitative structure (collapse at zero, knee near the low end,
first-eroded = most-expensive expression) is the claim.

**Evidence**: [dose-response](exp-005-leash/results/dose-response-2026-08-16.md);
[clone + probe](exp-005-leash/results/clone-2026-08-15.md); prereg
with D-001 extension (β∞ 0.03/0.04, descriptive, pending at
registration of this finding).

**Implications**: the lineage doctrine for phase 1 — clone from
healthy-composition demonstrations, PPO with a held-β∞ leash chosen
from this curve's low end, fingerprint-gate every candidate
per-expression (duet floors explicitly), expect and budget for seed
lottery (train several, gate, keep the passers). H4's trajectory
concern stays registered for the fog era, where the information
geometry changes.

**Would invalidate**: a personality whose fingerprint collapses at
doses that preserve this one (would make the curve
personality-specific in structure, not just magnitude); trajectory
collapse at a fingerprint-preserving dose under fog (H4's return).

**Re-verify when**: phase-1 lineage arms (production anchors,
post-rebalance traits, roster-5 world); any recipe change to the
anneal shape; the fog generation.

*(D-001 extension measured, 2026-08-17 — claim 3 NARROWED and the
entry's most important nuance found below the frozen doses: H4's
failure mode is REAL and dose-located. At β∞=0.03, both seeds hold
decision-level play (play_share .54–.56, duets near-anchor at
159–167/1k) while time_near_critters collapses to 55–63% of anchor
and bug_over_meal erodes — the personality RELOCATES to the
welfare-cheaper venue (kitty play by the pile) rather than fading:
every decision metric can pass while the visible character changes.
The trajectory cliff sits in (0.03, 0.04); β∞=0.04 is the measured
knee (trajectory held .35–.39, decisions anchor-adjacent with the
curve's tightest seed agreement, +8.2/+8.3 happiness) and is the
lineage-dose recommendation. Consequence for gates: lineage
fingerprints carry time_near_critters AND bug_over_meal floors, not
just decision shares. Full table:
[dose-response extension](exp-005-leash/results/dose-response-2026-08-16.md).)*

## F-020 · active · Trait prices are social prices: the cost order inverts between scripted and policy company (the exchange table)

Measured 2026-08-15 (trait-screen stages 1–2 + direct verifications:
6 needs × 4 factors, 10 paired seeds × 20k per cell, carrier-seat
design, scripted company then deployed roster-B company).

1. **The whole [0.5×, 2×] envelope is constitution-safe** in both
   companies (zero distress in 250+ runs) — the measured floor
   behind the ≥0.5× discount rule.
2. **The price order inverts with company.** Scripted: cuddle is the
   priciest axis (relief needs a willing adjacent partner; scripted
   cats rarely cosleep). Policy: the social needs halve (cuddle
   −58%, play −51%, sleep/bath −34/35%) while the consumables hold
   or rise (eat unchanged, drink +16% — contested water). Resource
   physics does not adapt; affection economics does. Discounts also
   buy less under policy (adapted cats have less slack to harvest).
3. **Additivity holds at design magnitudes**: 8-for-8 verified
   vectors within ~0.1 happiness of their marginal-sum predictions —
   the exchange table works as a design tool, derive-then-verify.
4. **Volatility is forecastable by need structure**: pack-need rates
   (cuddle/bath/sleep) are society-mortal — they move with who's
   seated; travel-need rates (eat/drink) are physics-stable, moved
   only by contention. Re-measure pack rows first at each
   re-derivation; travel rows and all structural PAIRINGS carry.

**Scope**: served 20×20 geometry, engine `412d00e2…`, carrier-seat
instrument (rates are carrier-conditional — measured with the
cuddler carrying), scripted and roster-B policy brackets. All rates
are bracket- and generation-mortal by design (stage 3 re-derives
under the spread-trained generation); the structural claims (2) and
(4) are the durable layer.

**Evidence**: [trait-screen results](trait-screen-2026-08-15/results.md)
(both brackets, verification tables, the five locked sheets);
character-design brainstorm (need-structure taxonomy, verified
against engine source).

**Implications**: trait characters are designed from the CURRENT
bracket's table and re-derived each generation (the config rider's
pins carry the owner's stage-3-mortality note); pairing rules are
rate-free and survive re-derivation (match discount structure to
signature structure); Clementine's cuddle-0.7 design is a bet on
policy-company prices — her scripted reading is expected-low
(confirmed: 90.61, lowest healthy seat in the post-wall anchor).

**Would invalidate**: additivity breaking at larger dial magnitudes
or higher dial counts; a policy bracket where consumable prices
adapt (would show the physics/economics split is company-specific,
not structural).

**Re-verify when**: any generation change (stage-3 re-derive, pack
rows first); world geometry or element-economy changes; the fog era
(vision changes the partner-finding economics that price pack
needs).

---

## F-021 · active · Seeing beats pricing: a single self-observation bit bought the water behavior no reward dial could (exp-003)

Measured 2026-08-07 on the post-026/027 engine (stamp `cba976da…`).
exp-002 falsified the pricing route: no wet-fur dial setting bought
deployed water avoidance at welfare-neutral cost (its gates
extrapolated to dial 4.8–5.6, 3–4× shipped). exp-003 fixed the dial
at 3.5/60, added ONE bit — the in-water self-observation flag (obs
182→183, schema 1→2) — and registered no dial arm and no escalation
clause.

1. **The bit worked where the dial could not**: 7/9 candidates
   inside the registered water band, 9/9 under the in-water ceiling
   (1.5×B = 5.15%), 9/9 above the drink floor; both misses were
   lounging only. The selected candidate is *drier than scripted* —
   in-water 2.79% vs B 3.44%, lounging 0.62% vs 1.50% — at +0.042
   welfare over needs_driven.
2. **The F-016 loop dissolves under observability**: scripted cats
   groom *more* on water as the dial rises (wetness raises Bath, a
   needs_driven cat bathes where it stands); policy candidates
   groom-on-water at 0.12–0.75% — a policy that can see it is wet
   does not do that. F-016 point 3's prediction (scripted and
   learned move oppositely on this channel), confirmed.
3. **Routing, not luck**: the lake-retrofit accident enlarged served
   water 8→11 tiles; scripted B *rose* 3.44→3.66% while the policy
   *fell* 2.91→2.83% — policy water use is insensitive to water
   availability.
4. Methodology that carried: band bounds registered as MULTIPLES of
   the same-engine scripted baseline B, never absolutes — B is
   re-measured whenever the stamp moves, so thresholds keep their
   meaning across engines.

**Scope**: MLP policy class on obs schema 2, served world, dials
fixed at 3.5/60; 10 seeds × 20k (band), 30 × 20k (welfare). The
principle — make the cost observable rather than raising it — is
the generalizable claim; the shares are engine-mortal.

**Evidence**:
[grid-2026-08-07.md](exp-003-water-schema/results/grid-2026-08-07.md)
(§9.1, the standout, the lake section);
[water-band summary](exp-003-water-schema/results/water-band-2026-08-07/);
exp-003 prereg §1–§3 (the registered refusal to escalate the dial).

**Implications**: when a behavior needs steering, reach for
observability before reward surgery — the bit is schema-versioned,
priced once, and F-011-safe, where a dial fights adaptation forever.
(exp-003's other headline — H5's 0/9 zero gate — is not a finding
about these policies: F-017 showed the gate conflated coordination
with competence, and its respec became the bar-225 battery.)

**Would invalidate**: a dial setting matching the bit's water profile
at welfare-neutral cost; a schema bit failing to move a behavior the
policy demonstrably attends to.

**Re-verify when**: B re-measures on any stamp move (standing, by
construction); fog-era vision changes what "observable" means.

## F-022 · active · The channel comes alive through demonstration, then the policies author its meanings (exp-004)

Measured 2026-08-09/11 on the 028 surface (197 obs, ride-along head,
stamp `412d00e2…`). All five registered hypotheses supported; 15/15
runs passed the respecified §9.2 gate (vs exp-003's 0/9 under the
overtight zero gate).

1. **Demonstrations seed the channel; exploration does not.**
   exp-003's near-empty channel (0.2% of dataset decisions, three of
   six kinds; clone predicted meows at 0.0000 accuracy) never came
   alive — greedy meow/1k 0.01–0.41 after 20M PPO ticks. exp-004's
   purr-rich v4 demonstrations cloned at 104.66/1k and certified at
   ~170/1k. Same recipe family, same reward; the difference was
   what the clone had seen.
2. **Once seeded, the policies author meanings.** Purr: deliberate
   on both ends (declines ~24 of 25 legal chances; erasing it flips
   6.3% of hearer activity decisions, 450× the null; answered
   society-wide +21pp within 10 ticks) and semantically a CONTACT
   CALL — emitted at excursion apogee, redirecting approach *away*
   ("I'm fine out here"), with the meet-lift speaker-driven.
   FollowMe: **zero demonstrations, pure RL invention** — 255
   emissions whose erasure flips 9.7%/19.3% of hearer decisions
   (39× null), with semantics inverted from the spec's name to "I'm
   coming" (speaker closes the gap; hearers are *released* from
   approaching). The policies re-derived WaitForMe's designed
   meaning — the one word spec 012 excluded — on a free label.
3. **The channel needs no scripted anchor** (D1 diagnostic):
   self-play arms kept it alive; mixing bought only its usual
   welfare cost. And team-potential shaping (A1, c=0.5,
   F-011/F-018-compliant) neither helped nor hurt — a registered
   tie at the 0.002 margin, safe but not necessary at this budget.
4. **Grounded legality makes the channel need-state-honest**: at
   0.95 welfare the want-words go dormant (needs never reach the
   announce threshold) and the hum that remains is Purr — "dormant,
   not dead," with the census-first rule registered before any
   threshold-lowering rollout.

**Scope**: MLP on the 028 surface, cooperative team reward,
20M-tick runs; purr/FollowMe pragmatics are screen-grade probes
(F-004/F-009 bounds; FollowMe subgroup rows are dozens). Meanings
are per-generation equilibria (see F-025), never engine guarantees
(F-018 layer 2).

**Evidence**:
[grid + verdicts](exp-004-meow-channel/results/grid-2026-08-09.md);
[purr-deliberateness](exp-004-meow-channel/results/purr-deliberateness-2026-08-10/results.md);
[purr-semantics](exp-004-meow-channel/results/purr-semantics-2026-08-10/results.md);
[followme](exp-004-meow-channel/results/followme-2026-08-11/results.md);
exp-003's null: [grid-2026-08-07.md](exp-003-water-schema/results/grid-2026-08-07.md)
+ [bc-clone-2026-08-06.md](exp-003-water-schema/results/bc-clone-2026-08-06.md).

**Implications**: lineage anchors are also *channel* anchors — what
a generation's demonstrations speak is what its clones will speak
(the imitability principle, operating); a vocabulary word's designed
meaning is a hypothesis the cats may overturn (mew's history made
this law-visible: the wall renamed it to a sound). Free-register
words are cheap experiments — RL fills them.

**Would invalidate**: a channel coming alive from exploration alone
under this reward class; an authored meaning failing to replicate in
its own generation's re-probe.

**Re-verify when**: each new generation (meanings are equilibria —
re-probe, don't assume); the fog era (F-026's condition changes the
channel's payoff landscape entirely).

## F-023 · active · Channel dials are listener-population properties; no composition-free optimum exists (the threshold curve)

Measured 2026-08-09, four announce thresholds T ∈ {15, 20, 25, 30}
under three listener populations (same engine, same worlds).

1. Scripted company: lowering T *helps* (+0.0018 ± 0.0004 at the
   T20 nominal peak; 9/10 seeds).
2. All-policy company: flat at zero for T ≥ 20; T15 −0.0011.
3. **Mixed 2+2 (the deployed shape): smooth convex HARM** —
   −0.0010 → −0.0067 → −0.0187 as T drops, every seed down at T15,
   ~9× the certification margin, distress ticks 88 → 3,833.
4. Want-traffic scales near-identically in all three (scripted
   59→214/1k, policy 0.7→10.8) — the harm is not the traffic, it is
   what each listener class *does* with it: scripted listeners
   respond usefully, mistrained-on-quiet policy listeners respond
   badly, and mixed company compounds both.

The registered insight: **the optimal threshold is a property of
the listener population, not the channel** — F-012's lesson
(measure in the company you deploy) promoted from measurement to
dial-setting.

**Scope**: e004-era policies + scripted needs_driven, 10 seeds ×
20k per cell, engine `412d00e2…`. The curve's numbers are
generation-mortal; the composition-dependence structure is the
claim.

**Evidence**:
[threshold-15-probe](exp-004-meow-channel/results/threshold-15-probe/results.md);
[threshold-curve](exp-004-meow-channel/results/threshold-curve-2026-08-09/results.md).

**Implications**: serving keeps T30 while dataset v5 collects at
T15 — collection-time and serving-time dials may legitimately
differ, because the collection's listeners are future (trained on
the chatty data) while serving's listeners are present. Any dial
whose effect routes through other agents' responses gets this
treatment: set per composition, never globally.

**Would invalidate / registered prediction**: v5-trained listeners
(raised on chatty company) should FLATTEN the mixed/policy curves
toward the scripted shape — re-measure at exactly T {15,20,25,30}
when they exist. If the curves don't flatten, listener mistraining
was the wrong mechanism.

**Re-verify when**: the v5-listener generation (the registered
prediction above); any announce-dial or cooldown change.

## F-024 · active · Entity attention: welfare parity, 40% fewer parameters, structural robustness, and a wider expression space (the architecture arc)

Measured 2026-08-12/13, all three stages recipe-identical to their
MLP baselines with only the model swapped.

1. **Critic**: EntityCritic val EV 0.555 vs MLP 0.53 at −36% params
   (74.6k vs ~117k) — read as parity-at-least (one run each).
2. **Clone**: activity top-1 79.9% vs 72.7% (+7.2pp) at −40% params
   (77,083 vs ~128k), message head parity. The gain concentrates in
   the multimodal classes (move 55.3→70.1, idle 39.3→45.3) — where
   a dense head has to average, attention can attend.
3. **PPO**: welfare parity — both classes saturate the ~0.95 band
   this world supports. **The architectural difference is the
   communication space**: five MLP seeds converged into a tight
   86–154 meow/1k band; three attention seeds spread 167/355/808 at
   no welfare cost — the class supports a much wider family of
   channel equilibria (the raw material of F-025's cultures).
4. **The F-010 answer, by construction**: identity lives in content
   (shared type embeddings), never slot position; permutation
   equivariance exact (8.3e-07 float noise); vacancy handled by
   key-padding mask, shifting value smoothly instead of
   extrapolating on an unseen zero pattern. Pointer heads (per-slot
   menu logits from that slot's embedding) carry to schema 4's
   variable rosters unchanged.

**Scope**: obs schema 3 / 197 surface, A1 recipe, d64/4h/2L; critic
and clone are single runs (no seed replication — margins are one
draw), PPO three seeds. F-007's mask-violation fingerprint reads
differently for pointer heads (vacant-slot logits are mask-owned).

**Evidence**:
[attn-critic results](attn-critic-2026-08-12/results.md);
[attn-clone results](attn-clone-2026-08-12/results.md);
[attn-ppo results](attn-ppo-2026-08-13/results.md).

**Implications**: the attention generation seats on merit (certified
2026-08-14) and phase 1 trains EntityPolicy by default; the
schema-4/fog design leans on properties this arc demonstrated
(vacancy-by-mask, variable tokens) rather than hoping for them.

**Would invalidate**: seed replication erasing the clone margin; a
schema-4 world where the pointer-head design fails to transfer.

**Re-verify when**: schema 4 lands (the variable-roster claim meets
reality); any trunk change.

## F-025 · active · Same recipe, different seed: dialects and cultures — mutually intelligible, kin-biased, welfare-coupled (the meow economies)

Measured 2026-08-14 across homogeneous and mixed rosters of the
three attention seeds (probe band, seat-rotation so traits never
confound model identity).

1. **Dialects**: s1 purrs at above-baseline separation (2.87 emit
   vs 2.53 declined — a contact call at excursion apogee, the
   deployed generation's dialect); s3 at below-baseline (2.54 vs
   3.73 — a proximity hum). Same word, opposite spatial deixis,
   both stable equilibria differing only in RNG seed.
2. **No devaluation at volume**: s3 purrs 4× as often as s1 (794 vs
   192/1k) with undiminished per-purr causal potency (7.6% vs 6.5%
   act-flip) — the channel does not saturate at measured volumes
   (79% duty cycle).
3. **Mutual intelligibility with kin bias**: cross-model act-flip
   7.3–7.4% vs same-model 7.8–8.9% (action semantics transfer);
   answering is kin-biased (same-model echo 20–26% vs cross 16–18%);
   voices stable in mixed company.
4. **Culture, welfare-coupled**: s3 is a groomer culture (GroomKitty
   12.0% of decisions vs 0.14/0.45% siblings — an 85× spread on
   classes dead in every pre-v4 generation). In mixed company it
   keeps giving unreciprocated, asks quadruple, drifts peripheral —
   and its welfare tracks its audience: 94.87 among kin → 93.93
   alone (−0.94), with kin recovering ~60% of the deficit. F-012's
   audience-dependence, surfacing at the welfare level for the
   first time.

**Scope**: three seeds of one recipe on one surface; screen-grade
(pooled probe seeds, no per-world clustering; the dose-response is
stated because it is consistent across all three mixed compositions
and both instruments). Certification of a heterogeneous roster must
run the battery on THAT composition — the homogeneous numbers do
not transfer (F-009).

**Evidence**:
[meow economies](attn-meow-econ-2026-08-14/results.md);
[valence results](attn-meow-econ-2026-08-14/valence-results.md).

**Implications**: seating is culture-pairing, not just
skill-selection — roster composition is a welfare variable for
cultured policies (the cross-gen roster's seat-paired accounting
absorbs this; the doter kin pair exists because of it). The
purrsonality register documents dialects per generation; lineage
work (F-019) is how a chosen culture survives one.

**Would invalidate**: dialects failing to replicate within their
own generation's re-probe; per-purr potency collapsing at higher
duty cycles.

**Re-verify when**: each generation (dialects are seed-born — new
seeds, new dialects); any roster/seating change involving a
culture-carrying policy.

## F-026 · active · Under global vision the channel is welfare-redundant — the measured baseline the fog generation must overturn

Measured 2026-08-15 (digest ablation, deployed roster B, hearer-side
per-kind digest zeroing, 4 arms × 10 seeds × 10k).

1. **Deafening moves nothing**: team happiness intact 94.887,
   purr-deaf 94.876, followme-deaf 94.873, both-deaf 94.900 — flat
   within ±0.015, an order of magnitude inside the parity band.
   Contact, cosleep, and grooming rates unmoved. The channel has
   measured *function* (deafening removes the answer-driven ~15% of
   purr volume — the chorus dies) without measurable *fitness*.
2. The mechanism was already visible in the want-words: WantEat is
   honest but inert (emitted 5.5–7.5 tiles from everyone —
   under global vision it tells hearers nothing their eyes don't).
   Everything a purr tells a hearer, the hearer already sees.
3. **The registered whisper, not a claim**: distress ticks double
   purr-deaf (37 → 78, 0.02% absolute). If fog-era ablations
   reproduce it at scale, the purr's value was tail-risk insurance,
   not mean welfare — the thing to look for first.

**Scope**: frozen minds (a generation *trained* deaf could differ —
the ablation removes input, not the training pressure);
screen-grade, 10 seeds, global vision, 0.95-welfare abundance.
This finding is deliberately a BASELINE: ROADMAP phase 2's
registered comparison (does grounded reference beat
FollowMe-overloading when fog creates an information gradient)
is powered by having this null on record first.

**Evidence**:
[digest-ablation results](digest-ablation-2026-08-15/results.md);
[meow economies addendum](attn-meow-econ-2026-08-14/results.md)
(want-word pragmatics).

**Implications**: no channel-value claims for the current
generation beyond culture and welfare-neutrality (client-facing
copy included); the Here* family's expected pre-fog inertness
(phase-1 rider) is this finding's prediction, not a surprise;
fog-era experiments inherit a clean before/after design.

**Would invalidate**: a same-generation composition where deafening
moves welfare outside the parity band (would mean the ablation
missed a load-bearing path).

**Re-verify when**: the fog generation (the entire point); any
same-generation ablation at scale that can power the
distress-doubling whisper.

**Confound note (2026-08-21, SC-005)**: the bugs-2.0 world change
(spec 039: roam tether, critter ttl 600, pounce, greeble dart,
play_relief_bug 28) landed between this baseline and any fog-era
re-measurement. The redundancy reading above is a property of the
pre-039 world; fog-generation comparisons against it span TWO
changes (economy + vision), so a fog-era channel-fitness delta must
be decomposed before attribution — re-run the deafening ablation on
the post-039/pre-fog world first, and treat THAT as the fog
generation's baseline. Play-relevant calls are the likely coupling
(hunt/duet coordination now pays differently); the F-025 dialect
comparisons are within-generation and unaffected.

---

## F-027 · active · Twin-seating one artifact creates dyadic self-interaction attractors

Found 2026-08-20 by trace forensics on the exp-006 phase-1 battery's
G2a/r5 failure (family-11, five seats, stress band).

1. **The mechanism is a mutual loop, not scarcity**: the attn-a1-s3
   pair (same artifact at Pumpkin and Kittybear) settled on adjacent
   tiles and each chose SleepWithKitty at the other for 2151/2200 and
   2084/2200 decisions while eat and drink saturated at 100 —
   a 2331-tick distress streak with water standing 37 tiles away and
   chow abundant throughout. Co-sleep services sleep and cuddle, so
   the two needs the loop feeds stay low while every other need
   starves. Each wake tick, the policy observes an adjacent sleeping
   twin and re-chooses co-sleep: the same mind holds both seats, so
   both make the same wrong choice and each renews the other's
   context.
2. **It follows the pair, not the composition**: the reference
   composition (no new-generation mind) failed the same world through
   the same loop with the same twins (worst 465). Solo-seating s3
   removed the failure class entirely: 0 bar exceedances, worst
   streak 159, and that 159 is directed travel on the 26-tile map.
3. **The world modulates persistence, not existence**: 2.4M
   cutover-config ticks (20×20, water 7–9, stimulus-dense) never
   showed the loop; family-11's quiet far corner and single pond gave
   it room. Hence the recruited tail benchmark
   (`tail-benchmarks/family-11-r5`).
4. **The tail is the price of a paid-for benefit**: two s3 seats were
   a deliberate welfare choice (the 08-14 kin dose-response, 94.87
   kin / 93.93 alone). Solo with cuddle-forward company recovers
   about half the kin gap (−0.50 vs −0.94, cross-surface). Kin is not
   clone: the culture-pairing benefit (F-025) and the symmetric-lock
   tail arrive in the same seating decision.

5. **Same-day refinement (E-arm fill cell)**: the attractor family is
   not twin-exclusive. With s3 seated once and ppo-E0-s1 replacing
   the scripted fill, a heterogeneous pile formed (solo s3 choosing
   SleepWithKitty 382/435 while ppo-L-04-s1 groomed the sleeper
   366/435, the E arm half-adhered) and held 435 ticks — over the
   225 bar, self-breaking where the twin lock was self-renewing
   (2331). The same seed under scripted fill read mda 0. Twins make
   the lock symmetric and stable; policy company makes piles
   available; scripted seats act as perturbation sources that break
   them. Each scripted seat replaced by a policy mind removes a
   stabilizer.

**Scope**: greedy serving/eval mode — deterministic symmetric argmax
sustains the lock; sampled action selection is untested. Observed
with one artifact pair (attn-a1-s3); the e004-a1-s2 pacing seen in
the same runs is a separate solo pathology, not dyadic. Engine note:
the Article I safeguard is supply-side only (guarantees relief
exists, not that it is taken), so nothing in the engine interrupts
the loop.

**Evidence**:
[r5 forensics](exp-006-character-gen/results/r5-forensics-2026-08-20.md)
(mechanism, choice histograms, partner fields, follow-up cells);
[battery record](exp-006-character-gen/results/battery-2026-08-20.md);
[tail benchmark](tail-benchmarks/README.md).

**Implications**: seating multiples of one artifact requires
tail-benchmark coverage for the dyadic class; the serving-side
max_distress_age watchdog and the backlogged distress-gated
intervention (disabled in testing, enabled on the server — owner,
2026-08-20) are the operational complements; welfare readings of a
twin-seated roster carry a tail its means don't show (F-009's point,
in the seating dimension).

**Would invalidate**: a twin-seated composition surviving extended
family-11-class exposure with no lock (would localize the attractor
to s3's groomer culture rather than twin-seating as such); a
cross-mind pile matching the twin lock's self-renewing duration
(point 5's piles broke an order of magnitude earlier — parity would
collapse the twin/heterogeneous distinction the entry rests on).

**Re-verify when**: any new artifact is seated in multiple; any move
off greedy serving; the distress-gated intervention lands (it
truncates the observable, so streak-based detection must move
upstream of the override).

## F-028 · active · Census raws are attributable only if the instrument records its own provenance

Found 2026-08-21 when the bugs-2.0 acceptance record failed
byte-reproduction during SC-007 (owner approved registration same
day).

1. **The event**: every chase-census raw produced on the afternoon
   of 2026-08-21 — acceptance grid 1 (a5e1aba), re-grid 2 (7e95b8f),
   the sticker sweep, and the b044827 final-config census — differs
   from reruns on instruments rebuilt from committed sources at
   their recorded commits, same configs, same tick counts.
2. **The elimination trail** (bugs2-sc007-2026-08-21.md §Provenance):
   engine drift excluded (intervening commits diffed, docs-only);
   tool drift excluded (worktree census source byte-identical to
   main @ e39079e, unchanged since 13:46); config drift excluded
   (mtimes predate the runs; header paths match); seed choice
   excluded (tool default 1..=10 equals the rerun list);
   toolchain excluded (rustc installed 2026-07-18); nondeterminism
   excluded (back-to-back reruns byte-identical); snapshot resume
   excluded (World::generate, no persistence path). The surviving
   hypothesis — uncommitted working-tree state in the instrument
   worktree during the runs — is uninspectable after the fact,
   which is the finding.
3. **The cost was borne at the thinnest margin**: no g20 verdict
   moved, but the sweep's g26 bar-1 pass at sticker 28 (banked
   10.1, flagged "+0.1, inside seed noise" the same hour) reads
   9.7 reproduced. A record that cannot be re-attributed converts
   a noise-flagged pass into an unanswerable question.

**Practice adopted**: a census raw must carry enough to re-create
its instrument — engine commit, working-tree dirty state, tool
source sha — in the output header, stamped by the tool itself, not
the operator's notes. Until the header exists, results docs record
those three facts beside every run. Reruns supersede raws that
cannot be attributed; today's rebuilt instrument is canonical for
the bugs-2.0 record.

**Would invalidate**: a reproduction of any afternoon raw from
committed sources (would relocate the cause from lost working-tree
state to something still latent and shared — worse, and worth the
hunt).

**Re-verify when**: the census header lands (check the stamp against
a deliberate dirty-tree run); any future raw fails byte-repro with
the stamp present.

**THE HEADER LANDED, 2026-08-23** — `experiments/census_provenance.py`,
wired into `live_census.py`, `pose_census.py` and (through
`cert_harness6.provenance`) the whole exp-006 lab family;
`playful_anchor.py` already carried its own compliant stamp. Every raw
now carries commit, **working-tree dirty state with the modified paths
named**, tool sha256, and — lab side — the config sha, the binding, and
`rustc -V`, which is the fact this finding's elimination trail could
only assert from an operator's note. Live raws additionally stamp the
served world (config sha, roster with the behavior string per seat,
tick), since the instrument's own commit says nothing about the box.

The re-verify clause is satisfied both ways: `test_census_provenance.py`
drives clean/dirty/unreadable in a throwaway repo (`OLD=1` replays the
pre-patch header and goes red on four of five), and the first real raws
were taken deliberately from a dirty tree and named all five modified
files. **The guard earned itself on the first run**: the path parser
sliced a fixed column offset, and stripping the porcelain output ate the
leading space of ` M path` lines — so tracked-file paths came out
missing their first character while untracked `?? path` lines looked
fine. A header that misnames what was dirty is only marginally better
than one that cannot say.

**THE PIN LANDED** the same day — `rust-toolchain.toml` at channel
1.97.1 (Product, PR #305, main 9f40c47), after this Mac, the build box
and CI's Linux were each shown to resolve the identical build hash
`8bab26f4f`. The header now stamps `toolchain_pin` beside `rustc`, so
what the repo REQUIRES and what a run HAD are comparable rather than
assumed. The trail's toolchain exclusion is checkable from here on.

**And the pin exposed a live instance of the thing this finding is
about.** The lab's compiled binding was two engine commits stale and
would have been stamped with a PATH compiler that never built it. Worse,
the drift — spec 040's `[watchdog]` ForeignTable — meant the binding
*rejected the repo's own root config* under `deny_unknown_fields`, and
nothing had failed only because every exp-006 config predates 040.
Rebuilt and verified byte-continuous (identical 2,000-tick state-trace
digest across changed binding bytes): `exp-006-character-gen/results/
binding-rebuild-2026-08-23.md`, instrument `binding_continuity.py`.
The lab stamp now also carries `binding_artifacts` (sha256 of the `.so`)
— the one fact that cannot drift from what actually ran.

**Correction to Experiments' own handoff** (Product falsified it
directly, 2026-08-23): `rustup default stable` in a CI workflow does NOT
override a `rust-toolchain.toml`. Rustup ranks `+toolchain` >
`RUSTUP_TOOLCHAIN` > directory override > toolchain file > default, so
the pin was never at risk from those lines; removing them was right only
because they downloaded a second toolchain nobody would use. The real
silent-inert mode is a `cargo` that is not a rustup shim, which ignores
the file without a word — guarded now by an assertion in both blocking
CI jobs.

## F-029 · active · A reader rule copied from the wrong contract shape reports a category that cannot exist

Found 2026-08-22, minutes after the Biscuit 2.0 deploy, when the
owner said she could see substantial critter play and the G5 census
reported `kitty 625 / solo 4` for that seat — no critters at all.
The owner was right and the instrument was wrong.

1. **The bug**: `live_census.py`'s play classifier branched on
   `act.get("id")`, per the 001 http-api contract's action shape
   `{"action":"chase","target":"element","id":12}`. But
   `/events/activity` carries the ACTIVITY shape, where the target
   is nested: `{"state":"playing","target":{"target":"element",
   "id":11449}}`. `act.get("id")` is therefore always None, the
   element branch was dead code, and `target is not None` swept
   every element play into the `kitty` bucket. The instrument could
   not emit a bug or greeble count under any world state — the
   category it was built to measure was unreachable.
2. **What it falsified**: the "zero critter play" line carried from
   2026-08-18 through the bugs-2.0 freeze packet. Re-cutting the
   retained raw events with the fixed rule shows element play in
   EVERY re-cuttable census: 18 events (22037), 15 (25325), 22
   (26221 — the freeze packet), 20 (27089), 14 (27729). The freeze
   packet's headline "bug 0/greeble 0 ALL seats" is false, and its
   companion claim "Clementine kitty-partnered 87/87 — duet outbids
   bug, designed ordering" inverts: in that window scripted
   Clementine played 14 element vs 12 kitty.
3. **What survived**: the finding the zero was recruited to support
   — that welfare-learners barely hunt — holds in the corrected
   numbers (learner seats: 0–6 element events per window against
   40–105 solo-play events), and the skill-moat EV analysis came
   from a different instrument (the engine-native chase census) and
   is untouched. The direction of the post-seating result is
   unchanged and larger than first reported: Biscuit 2.0 reads 448
   element vs 177 kitty in its first census — ~197 element plays
   per 1k ticks against ~3 for the seat's predecessor.
4. **The generalization**: an absent category in a summary is not
   evidence of absence until the instrument has been shown able to
   emit it. A zero that a tool structurally cannot exceed reads
   exactly like a measured zero, and it survives review because
   every downstream reader sees a plausible number. Sibling of the
   client-side lesson: when a measurement says "impossible" and the
   owner can see the thing, measure the other end of the function.

**Guard**: the classifier now has a synthetic red/green unit check
(element → kind, expired element, kitty, solo) that fails on the old
rule; element ids resolve through a running id→kind map because bugs
expire out of `/world` mid-census.

**Re-verify when**: any engine change touches the activity JSON
shape; any future census reports a flat zero in a category (re-run
the unit check before banking the claim).

## F-030 · active · Per-event shaping of a social behavior buys initiation churn, and the KL leash does not prevent it

Measured 2026-08-22 by exp-006a's F-duet arm (prereg §3), the single
shaped arm in a four-arm wave whose other three arms differ only in
dose. Registered with the arm's own report-only guard as the
detector.

**The design**: λ = 0.1 added to the TRAINING reward for each seat
transitioning INTO kitty-partnered play — a per-event bonus on the
start, not on time spent partnered. State-stream detection, no
penalties, telemetry unshaped. The prereg's sizing rationale argued
the term was self-limiting at roughly 1% of per-tick return; at the
measured scripted-anchor rate it was nearer 2%.

1. **The policy farmed the event, because the event was what paid.**
   Duet starts began at 30.3 per 1k seat-ticks — below the scripted
   anchor's 40.49 (`derive_duet_anchor.py`, the trainer's own
   detector) — crossed the pre-registered 3× grind threshold (121.5)
   at update 981 / 3.0M ticks of 20M, and climbed monotonically to
   201.1 final, peak 263.5. 81.6% of all telemetry rows flagged. The
   fingerprint confirms it out-of-loop at 420.3 starts per 1k
   decisions, **2.34× the scripted anchor**. Short duets, restarted
   constantly, maximize a count that pays per start.
2. **It was paid for out of the venues that paid nothing.**
   Critter proximity fell to 0.33× anchor and bug-hunting to 0.15×,
   against G3 floors of 0.70× — the arm fails character on exactly
   the two dimensions the shaping never touched, while play share
   *rose* to 1.07×. The shaped behavior did not add; it displaced.
3. **The leash did not constrain it.** Final KL-to-anchor was 0.597,
   squarely in family with the unshaped siblings (L-04-s3 0.604,
   F-dose 0.513/0.549) — decision-level proximity to the anchor was
   indistinguishable while the behavioral rate ran to 2.34×. This
   extends F-019's structure: a KL leash bounds the policy
   distribution per decision, not the emergent rate of a composite
   behavior assembled from many in-distribution decisions.
4. **It was not even good for the cat.** Subject happiness 85.12,
   lowest of the wave (the two G3 passers read 88.48 and 86.65), and
   the arm's greedy probe nash finished 0.8813 against 0.93+ for
   every sibling. A ~2%-of-return shaping term bought a large
   behavioral distortion and negative welfare.
5. **The cheap report-only guard was the whole defence.** A
   pre-registered threshold on a metric nobody gated fired at 15% of
   training and its verdict was later confirmed by an independent
   instrument (the G3 fingerprint's venue floors). Report-only
   telemetry with a number declared in advance costs nothing and
   converts a post-hoc argument into an observation.

**Scope of validity**: one seed, one λ (0.1), one shaped behavior
(partnered-play start), 20M ticks, dataset v6 on the bugs-2.0 world,
BC-init + leashed PPO. This is a single point, not a dose-response —
it does not establish that a smaller λ, or shaping *time partnered*
rather than *starts*, carries the same defect. The general shape it
supports is about per-event bonuses on repeatable social acts.

**What would invalidate it**: a λ-sweep in which the churn signature
disappears below some dose while retention holds (would narrow this
to "λ ≥ 0.1"); or a duration-shaped arm (reward per tick partnered)
that reproduces the venue collapse anyway (would move the cause from
event-vs-state to shaping social behavior at all).

**Re-verify when**: any future arm shapes a countable behavior;
before adopting shaping as a retention tool in place of the leash;
and if a duet-time-shaped arm is ever run, compare its venue
retention against this arm's directly.

## F-031 · active · A partnered scene runs its minimum only if the counterpart is pinned; grooming is the exception

Found 2026-08-24 by Product while checking the waterline proposal's
priors, corroborated independently here. Registered on the owner's word
the same day.

**The instrument matters as much as the number.** Polled snapshots
cannot measure scene length — the final tick of a scene clears the clock
it stamped (`api.rs:95-97`) — and `activity.state` is a one-tick
resolution flag for play, eat and drink besides. `GET /events/activity`
records the true span, **inclusive: `ended - started + 1`**
(`events.rs:30-42`). Both threads dropped the `+1` on first reading and
saw every activity quit a tick early; the arithmetic now lives in
`live_census.py` beside its citation.

1. **Measured spans, 1000 scenes, live world**, against the config
   windows they were drawn from:

   | scene | n | mean span | config |
   |---|---|---|---|
   | cosleep | 79 | 6.00 | sleep 6-12 |
   | sleep-solo | 80 | 6.01 | sleep 6-12 |
   | groom-solo | 39 | **4.00** | bath 4-8 |
   | groom-other | 113 | **3.37** | bath 4-8 |
   | duet | 99 | 2.00 | play 2-5 |
   | play-solo | 103 | 2.00 | play 2-5 |
   | play-element | 136 | 1.74 | play 2-5 |

2. **The controlled comparison is groom-solo against groom-other**:
   one activity, one config window, differing only in whether a
   counterpart exists who can leave. Solo lands exactly on its minimum;
   partnered runs 0.63 ticks short. Everything else lands exactly on
   its minimum.
3. **The mechanism is which activities pin their partner.**
   `prune_dead_activity` (`world.rs:476`) ends a partnered groom through
   `is_available_friend`, and the groomed cat is never in an activity —
   it stays free to walk away mid-scene. Duets and cuddles lock both
   parties via `reciprocal_duet`; sleepers do not move. Grooming is the
   only partnered activity whose counterpart is unpinned, and it is the
   only one that dies early.
4. **play-element's 1.74 reproduces the banked bug `mlen` of 1.8**
   through a different endpoint than the Rust chase census that produced
   it — an independent check on the critter-play EV work, which the
   `bugs2-grid-analyze.ev()` docstring already warns must use measured
   rather than nominal lengths. Same lesson, second instrument.

**Why it is worth a number**: every EV that prices a partnered scene
multiplies by its length, and nominal config bounds overstate grooming
by 15%. It also predicts where a rule that reshapes pairing could show
up as a *duration* effect rather than a count effect — grooming is the
only partnered activity with slack.

**Scope**: served world, current roster, one 1000-scene window per
thread. Says nothing about scripted-only compositions, and the gap size
is a function of how mobile the groomed cat is, so a calmer roster
should show a smaller one.

**What would invalidate it**: a groom-other mean at or above 4.00 on any
roster (would mean the counterpart-gone rule is not what shortens it);
or a duet mean below 2.00 (would mean `reciprocal_duet` does not pin
what it appears to pin).

**Re-verify when**: any change to the friend helpers, `prune_dead_activity`,
or the duration config; and before pricing any partnered scene in an EV.

## F-032 · superseded by F-033 · The most social policy pays a turn tax: `Idle` in `last_action` is the legality funnel refusing an ask

Claimed from served-world evidence that Biscuit's `idle` ticks were
`action::validate` refusing a partnered-play proposal rather than the
policy choosing to idle — flagged at registration as an inference,
because proposals are not observable from outside the engine. The
settling experiment it specified was run the next day and **narrowed
it: the refusal is real, large and uniquely Biscuit's, but it is 45% of
the seat's idle, not all of it.** The majority is a genuine idle
proposal. Full text in [FINDINGS-ARCHIVE.md](FINDINGS-ARCHIVE.md);
the measured split, and the part that survives, are F-033.

## F-033 · active · Every seat pays a partnered-action refusal tax, in its own currency — but for Biscuit that is under half its idle; the rest it chooses

*Bars retired 2026-09-02 by F-039 (live stamp read, post-048): the 4.7% and 3.5% figures below are seam-probe history; the mechanism stands.*

Settles the inference [F-032](FINDINGS-ARCHIVE.md) registered and could
not test. Run 2026-08-25 on the owner's word — the experiment F-032
itself specified. Cites [F-031](#f-031--active--a-partnered-scene-runs-its-minimum-only-if-the-counterpart-is-pinned-grooming-is-the-exception)
for the unpinned-counterpart mechanics it lands on.

**Why the served world could not answer it.** `last_action` carries the
ENFORCED action (`world.rs:338`), so a chosen idle and a refused ask are
spelled identically. Three actions exist per tick — `proposed`,
`validated`, `applied` (`seam.rs:212`) — and the served surface shows
only the last.

**Method**: all five served artifacts seated as external agents on the
certification config (`phase1-cutover-bugs2.toml`), greedy argmax under
the engine's own mask — the served decision rule (`behavior.rs:14`,
"argmax over masked logits, ties to the lowest index"; no served seat
enables sampling). Eval band 870001–870010, 10 seeds × 20,000 ticks =
200,000 ticks per seat. Instrument
`exp-006a-biscuit-corner/idle_rewrite_probe.py`.

1. **Of the ticks whose applied action is idle:**

   | seat | applied idle | CHOSE idle | was REFUSED into it | idle rate |
   |---|---|---|---|---|
   | **Biscuit** (e006a-L-04-s3) | **21,047** | **11,668 (55%)** | **9,379 (45%)** | **10.5%** |
   | Clementine | 4,196 | 12 | 4,184 | 2.1% |
   | Kittybear | 3,490 | 0 | 3,490 | 1.7% |
   | Pumpkin | 3,040 | 0 | 3,040 | 1.5% |
   | Miso | 1,873 | 6 | 1,867 | 0.9% |

   Counted two independent ways — from `survived` (`validated ==
   proposed`) and from decoding the proposal against the fixed menu —
   which agree to the unit on every seat.

2. **F-032 was 45% right, which means it was wrong as stated.** "Biscuit
   isn't idling, it's being refused" does not survive: the majority of
   its idle is a genuine idle proposal that passed validation. The
   register's own caveat — that a chosen idle fits the same served data —
   was the live possibility, and it was the larger half.

3. **The refusal is real, and it is partnered play specifically.** Of
   Biscuit's 9,379 refusals into idle, **9,187 (98%) were `play_kitty`** —
   a duet proposal naming a partner slot. Not solo play, not critter
   play. Duet legality is `is_conscriptable_friend`: the partner must be
   free.

4. **The tax is not Biscuit's alone — it is the general shape, and each
   seat pays it in its own currency.** Every seat's refusals are
   dominated by partnered actions whose counterpart can leave:

   | seat | top refused proposals (into idle) |
   |---|---|
   | Biscuit | `play_kitty` 9,187 · move 113 |
   | Clementine | `groom_kitty` 2,402 · move 1,277 · `sleep_kitty` 418 |
   | Kittybear | `groom_kitty` 1,958 · move 1,122 · `sleep_kitty` 286 |
   | Pumpkin | move 1,367 · `groom_kitty` 1,246 · `sleep_kitty` 201 |
   | Miso | move 1,091 · `sleep_kitty` 619 · eat 96 |

   The groomers are refused on grooming exactly as F-031 predicts —
   grooming is the partnered activity whose counterpart is never pinned.
   Biscuit is refused on duets because it is the only seat that proposes
   them at volume. (`move` refusals are a different rule: walking into
   an occupied tile.)

5. **Biscuit is the only seat that ever chooses idle** — 11,668 against
   0–12 for every other seat. The character-trained policy learned to
   propose a do-nothing turn; the four older policies essentially never
   do. That is a fact about the training, not the enforcement, and
   F-032 missed it entirely.

6. **The mechanism is structural, not a policy flaw.** The mask probes
   the FROZEN start-of-tick snapshot while enforcement runs in the
   kitty's apply slot, after earlier kitties' turns have applied —
   `meow.rs:167`, "probing shares the RULE, not the MOMENT", which states
   the activity mask probes `validate` the same way. A partner
   conscriptable at start-of-tick can be gone by the apply slot. No
   policy could avoid this by choosing better.

**Instrument warnings, each of which cost a wrong answer first:**

- **`survived == 0` is not a synonym for "refused"**, and reading it as
  one overstates by ~2×. It is `validated != proposed` and reflects
  `validate` ONLY; `enforce_durations` runs afterwards and normalizes a
  continuing proposal to the continuation action (`world.rs:487`).
  Biscuit's 21,121 rewrites split 9,379 into idle and 9,756 into `play`,
  the latter being scenes already running.
- **`survived == 1` does not mean applied == proposed**, for the same
  reason. An earlier version of this probe learned the menu from those
  ticks and had index 25 report as both `play` and `groom`.
- **The activity menu is a fixed 34-entry table** (codec v2, spec 028);
  schema 3 widened only the message head (`codec.rs:54`, "the 34-entry
  activity menu did NOT move"). The probe pins
  `ACTION_SCHEMA_VERSION == 3` and asserts alignment the engine
  guarantees: `validate` has `Action::Idle => true`, so a proposed idle
  can never be rewritten, and a misaligned table would show one.

**Scope**: certification config, greedy, the five served artifacts, one
eval band. The served world is a different config and this was not
re-derived there; the lab's 10.5% applied-idle rate against the served
15% is supporting, not proof. F-032's served-side
77%-of-scene-endings statistic was NOT re-measured here.

**What would invalidate it**: a seat proposing partnered actions at
volume with few partnered refusals (would break the concentration);
Biscuit's choice/refusal split moving materially on the served config or
another band; or a served-side replay showing the in-engine behavior
does not use the greedy masked argmax this assumed.

**Re-verify when**: any change to `is_conscriptable_friend`, the
`validate` legality arms, the mask's probe moment, or duet duration
config — and before pricing any partnered action in an EV, where the
refusal rate is a real cost that current EVs omit for grooming as well
as for play.

**What it opens**: the Biscuit 3.0 question is two questions, not one.
The refusal half (4.6% of ticks) is addressable — `Play { target: None }`
is always legal, so a solo-pounce fallback keeps the ask and drops the
tax, and the same argument extends to the groomers' `groom_kitty`
refusals via `Groom { target: None }`. The chosen half (5.8% of ticks)
is not a bug but a trained behaviour to understand, and it is the
larger one. Whether either moves a seat's happiness is still
unmeasured: that needs a needs-servicing count per turn, not this probe.

## F-034 · active · Here* vocabulary cloning is a cliff, and the cliff sits between 5.6% and 8.2% corpus share — not near 1%

The here-word density screen's Half A
(`here-word-screen/RESULTS.md`, run 2026-08-31 on the owner's
2026-08-30 word; plan pre-registered @ 8c50fda with the spec-043
FR-006 amendment). Extends [F-022] from two far-apart anchor points
(0.2% → mute; purr-rich ≈10% → fluent) to a bracket on the boundary
itself. Method: four paired-seed corpora on the anchor composition at
`announce_here` off/1/4/16 (realized here-share 0 / 8.18 / 5.56 /
2.36% of decisions), one V4 clone each under the verbatim
`train_clone6.py` recipe, readouts conditioned on the here-kinds per
[F-015].

1. **The cliff.** Opportunity-use (kind legal, no want spoken): A1 =
   .58–.80 by kind, msg@1 on here-rows .8748, predicted emission
   84.5/1k tracking its source's 82.4/1k per kind. A2 and A3: ≤ .0033
   use, ~0.3/1k — functionally mute at 5.6% and 2.4% corpus share.
   Nothing in between: the middle of the dial belongs to the mute
   side.

2. **The vocabulary is free where it works.** act@1 .7986–.8037
   across all four arms (no action-learning cost at any density), and
   reward streams byte-identical across arms at all 25 paired seeds —
   the welfare charge is exactly zero by gate-zero construction
   ([F-026]'s report-only expectation, satisfied at equality).

3. **Qualifier that keeps this honest**: "mute at 5.6%" is a claim
   about the registered recipe's budget (20 epochs, patience 3); A2's
   val loss was still falling at the cap. Epoch-extension on A2 is
   the registered follow-up before treating the cliff's location as
   an asymptote. Emission is offline masked-argmax on held-out
   states; live-rollout confirmation wants the lab binding gate.

**What it changes**: fog corpus seeding uses `announce_here = 1` as a
collection parameter, not a swept dial (per-kind cooldowns cap the
ceiling near 8%, so period 1 is the only workable setting); the
parked Here*-teacher likely collapses into "the scripted behaviors
with the knob armed" (plan §8, owner's read pending); and exp-003's
0.2% channel sat 40× under the cliff, not 5× — its failure was never
a near-miss.

**A1b addendum (2026-08-31, owner-routed, declared before
collection)**: a fifth arm at period 2 (realized share 7.61% — the
cooldown compression again) lands mid-transition: emission RATE
fluent (73.6/1k vs source 76.9) but placement half-right
(opportunity-use .35–.56, msg@1 on here-rows .691). So the shape is a
steep transition, not a pure step: mute ≤ 5.6%, half-fluent at 7.6%,
fluent at 8.2% — the whole rise inside ~2.6 points of corpus share.
A 0.57-point share difference (A1b→A1) buying +.14–.24 of use hints
raw share may not be the only driver (period 1 is also the most
regular context); one clone per arm, so the shape is the claim, not
the decimals. Decision unchanged: period 1 dominates — period 2's
corpus is barely smaller and strictly worse placed. act@1 .8009
(flat), rewards byte-identical (gate zero holds for the fifth arm at
all 25 paired seeds).

**Extension addendum (2026-08-31, owner-routed, decision rule
pre-declared)**: fresh 60-epoch/patience-10 runs on A1/A1b/A2 (the
qualifier in point 3, discharged). Verdict: **the cliff is
density-shaped, not budget-shaped** — 3× budget moved opportunity-use
by noise (A1 .60–.81, A1b .39–.54, A2 still mute at ≤ .027 with
here_critter exactly 0; no plateau-then-jump anywhere in the
histories). The 20-epoch recipe stands for vocabulary seeding.
Separate fact the probe surfaced: the budget DOES buy action
fidelity — act@1 +1.6–2.0 points on every arm (.80 → .82) at 3×
cost; whether that trade is taken for Fog Gen 1's BC stage is an
owner call at the fog prereg.

## F-035 · active · The waterline charge is a magnet before it is a fence: charge-blind arms drift TOWARD the water's edge, and only a charge-aware chooser turns the price into avoidance

The water's-edge avoidance smoke
(`edge-avoidance-smoke-2026-09-01/RESULTS.md`; prereg @ 978b436,
addendum @ 0049a70, both before collection; engine main @ dfa4b6b —
044 charge + both 045 dials). Six arms × three paired seeds, scripted
needs-driven lab worlds at the canonical economy.

1. **The magnet.** Cross-waterline adjacency (share of adjacent
   pair-ticks) rises with a blind charge: no-charge 6.61% → blind
   factor 1.0 = 11.84% → blind factor 10 = 13.70%. Mechanism: the
   charge raises bath need, and bath-relief seeking sends cats to the
   water. A welfare price whose payers cannot see it CONCENTRATES the
   population at the priced boundary.

2. **The fence needs eyes.** The charge-aware ladder reverses the
   drift: aware factor 1.0 lands at 7.66% (option_a) / 8.07%
   (bidirectional) — ~4 pp below blind at the same factor — and the
   10× positive control drops to 4.84%, ≤ half its drift-matched
   blind twin in pooled share and below it in every seed pair.

3. **Membership does not matter to behavior at factor 1.0**:
   |option_a − bidirectional| = 0.41 pp under the aware ladder, no
   consistent per-seed ordering, and the play channel obeyed the
   reciprocity prediction (C ≈ D, the pricing-bug canary stayed
   quiet). The step-4 bidirectional call gets clean data: no
   meaningful edge-avoidance difference between the rules.

**Ruling on this data (owner, 2026-09-01)**: no contagion for Gen 1
(`contagion-shelved-2026-09-01.md`). Point 1 is the argument: a Gen 1
learner cannot see a wet neighbour, so an armed charge trains arm B's
world. The wet-side vector (wet cats keeping away from dry friends) is
unpriced under BOTH membership rules — the wet member never pays
contagion — so it is not learnable in this economy at all. F-035 is
Gen 2 pricing input; reopen triggers are in the ruling doc.

**Scope**: scripted choosers only (BC clones imitate the teacher —
this is exactly the corpus-side question); canonical
`groom_cuddle_relief` 0.5; the 10× arms run a disclosed nonstandard
budget (ceiling 25 / safeguard 98 / distress 99), directional only.
**Invalidated by**: changes to the charge formula, the ladder value
shape, or E_ticks bounds; fog changing what a cat can see near water
(step-5 shakeout re-checks). **Re-verify when**: any proposal to arm
`contagion_aware_ladder` on a SERVED world — the groom collapse down
the aware arms (pair-ticks 1,893 blind → 527 aware-bidirectional) and
the two low Clementine happiness samples say the decline seam
redistributes relief in exactly the population 041 burned.

## F-036 · active · The needflow model is not a proxy for the scripted teacher: three engine gates it lacks invert the sleep niche and make relief dials invisible to `needs_driven` decisions

Needflow lab validation (`needflow-lab-validation-2026-09-01/RESULTS.md`;
prereg @ af4c5ea, scorer @ 261bbb7, both before collection; engine
main @ 055dc5b). Six 20k-tick `needs_driven` runs, three paired seeds
at `groom_cuddle_relief` 0.5 (canonical) and 2.0 (served bump).

1. **The 041 rest niche is wide open under scripted seats.** Rest is
   the largest scene class at 29.7/1k cat-ticks (model 12.8), 707–772
   scenes per 5,000-tick sub-window in every seed, both tiers emitting
   (mutual ≥1,392, drip ≥2,270 scenes per run). The emit gates the
   timeline asked for pass with room.

2. **Cosleep : solo sleep is 0.32 : 1, not the model's 5.6 : 1.**
   Engine cosleep routing (`needs_driven.rs:193`, spec 028 FR-020)
   opens only at cuddle ≥ `cuddle_real_threshold` (15.0); the 041 rest
   economy holds standing cuddle at ~14.2, so 1,153 of 1,513 naps in
   one run went solo. needflow offers cosleep to any adjacent pair
   ungated, and cosleep strictly dominates solo sleep there. Rest is
   eating cosleep's demand; whether that is the intended sleep niche
   is an owner design question.

3. **Relief dials are invisible to scripted decisions.** The bump moved
   groom-other −11%, groom-self +4%, rest −1%, bath −1% (model +76 /
   −62 / −55 / −34%). `groom_cuddle_relief` enters the engine only as
   payout and in the inert 045 exposure seam; kitty-grooms are
   initiated solely by `groom_response` to an audible bath meow (lab
   groom-other 2.4/1k vs model 15.8). A relief-pricing proxy predicts
   swings that neither scripted seats nor the frozen roster can
   produce; only a learner trained under the dial can answer a
   reprice.

**Scope**: scripted `needs_driven` seats on the served 20×20 world,
no fog, contagion shelved. needflow's calibration subject was the
POLICY roster; this is the first measurement of the scripted chooser
against it, and the bands it produced are the Gen 1 BC teacher's own
mix, which is why they (not the model's) are step 5's reference.
**Invalidated by**: changes to `cuddle_real_threshold`, the
`groom_response` seam, the 041 relief dials, or fog changing what a
sleepy cat sees within `sunbeam_reach` (step 6 re-derives the bands).
**Re-verify when**: needflow is next used to predict a scripted or
BC-clone mix — add the gates first, or don't use it for that.

## F-037 · active · The action-shape collapse detector names a lock but does not lead the watchdog: on every recorded starving lock it fires 48–147 ticks after the distress alarm would, and its healthy margin is 0.07

Collapse detector v0 (`collapse-detector-v0/RESULTS.md`; prereg,
detector and guard @ 72ca108 before any trace was read). Trailing
W = 200 share of one partnered activity (resting/sleeping/grooming
with partner flag) > 0.50 sustained D = 200, per seat; mutual-pair
share the same, per pair; need spread report-only. Run on all 19
exp-006 forensics traces.

1. **Validated as pinned.** 3/3 MUST-FIRE locks fire (880030 twins,
   880008 twins, 880015 triadic), the SHOULD-FIRE pile fires, 11/11
   MUST-SILENT traces stay silent. The discriminating negative holds:
   solo-s3-880013's watchdog equivalent fires at tick 6,585 on directed
   travel while the detector sits at 0.32. That is the one case the
   welfare instrument cannot separate and this one can.

2. **Not an early warning.** Detector first fire vs watchdog equivalent:
   4619/4566, 1368/1221, 3717/3669, 591/514. A ~300-tick lock is needed
   to cross-and-sustain, and every recorded lock had a need in distress
   within ~120 ticks of onset. The ROADMAP's "fires earlier because
   needs must starve first" premise is wrong for these locks. What
   survives is the naming (seat, family, pair) and the untested claim
   about welfare-quiet locks — no such lock exists in the trace set.

3. **The bar is on a knife edge on the healthy side.** Realized lock
   share is 0.82–0.83 (F-027's 98% was the action HEAD's share; the
   re-entry idle tick between naps takes ~17%), healthy peak 0.43 (a
   51-tick partnered sleep run at tick ~11.5k in solo-s3-e1s1-870003).
   Mutual-pair share confirms twins (0.58–0.67) but misses the triadic
   pile (0.38). Need spread reaches 93/82/73 on silent traces and stays
   report-only.

**Scope**: sleeping-with-partner locks only (every positive is one);
exp-006 trace format; 200k healthy ticks, not the ROADMAP's untraced
2.4M. **Invalidated by**: W/D/bar changes (v0.1 with its own prereg
line); a lock class outside the three partnered families.
**Re-verify when**: H4 is pinned at step-5 kickoff — the owner picks
the bar with the 0.43/0.82 numbers in hand, and a live v1 re-runs this
set before it watches a seating.

## F-038 · active · Scripted Biscuit's comfort dial buys food promptness linearly and pays in element play, never duets; a food-only weight band keeps play by leaving cuddle (her highest need) unserved; the spec-042 score at t_partner 5 refuses nearly every friend and halves the roster's duets

Biscuit 3.0 comfort sweep (`biscuit3-comfort-sweep-2026-09-01/RESULTS.md`;
prereg + tooling @ 893cd48 before collection). Scripted `playful`
Biscuit with four `needs_driven` seats, canonical 041 economy
(`groom_cuddle_relief` 0.5), 20k measured ticks × 2 seeds per arm,
20/20 runs valid, watchdog quiet throughout.

1. **The comfort curve is smooth, no free lunch.** Eat time-above-30
   0.455 / 0.362 / 0.236 / 0.132 at comfort 55 / 45 / 35 / 30 (in-run
   scripted floor 0.100); eat p50 88 / 56.5 / 26.5 / 10.5 ticks;
   hungry-play share 0.65 → 0.15. Total play 1.00 / 0.93 / 0.76 / 0.70x.
   Every play point lost is element play (162 → 96/1k); duets hold at
   67–79/1k in all arms. Seeds agree to two digits. Biscuit happiness
   77 → 85, demand price 22.7 → 15.2.

2. **The weights arm passed P3 by leaving cuddle unserved (corrected
   2026-09-01).** w35 (eat/drink/sleep at 35, bath/cuddle at 55) closes
   0.51 of the eat time>30 gap vs flat c35's 0.62 and keeps 209 vs 179
   play/1k, so P3 passes as pinned. But cuddle is Biscuit's highest
   elevated need at c55 (mean 30.8, 50% of polls ≥30; roster 16.5/13%),
   above eat (28.3/45%). w35 leaves it at 27.0/42% while c35 takes it to
   20.7/26%. The play w35 "saved" is play she did while wanting a
   cuddle. Bath is the one need genuinely fine at 55 (15.6, 7% ≥30; 1%
   at c30), so a weight band covering everything but bath is within
   noise of flat comfort. Welfare has to be read on all five needs;
   P3 as pinned read only eat. Weights are not recommended.

3. **The spec-042 candidate dials are not shippable.** With `t_partner
   5.0` against a realized mean partner play need of 4.3 at duet
   start, Biscuit's duets fall 72.6 → 8.9/1k at every comfort; she
   substitutes elements (total play flat, +4–9%) and the four other
   seats lose 51–57% of their duets. Partner need at duet start rises
   4.3 → 10–12 as designed. Food unmoved. The next campaign sweeps
   `t_partner` and `w_serious` with this as baseline.

4. **Two prereg measures failed as bars.** Armed excursions per 1k
   RISES as comfort drops (6.3 → 8.2): a meal resets eat to ~0
   (35/tick × ~2 ticks), so meals per 1k ∝ 1 ÷ eating level (6.6 at
   mean 48.5, 9.5 at 30.3), and an excursion is a meal that started
   above 30. The floor seats' 4–5/1k comes from eating at 21–27, below
   the line 70–85% of the time. The count measures how often a cat
   gets hungry enough to cross 30, not how late she is. "Low-need play" (scenes
   starting with food needs < 30) rises 1.6–2.9x for the same reason a
   fed cat lives below 30. Neither can serve as a bar again.

5. **Addendum 1 (c25 / c20, 2026-09-01): parity reached, play halves,
   meows vanish.** Both arms reach roster-parity welfare on all five
   needs (Biscuit's share ≥30 within 0 of the roster at c25, below it
   at c20); total play 0.58x / 0.45x of c55 (predicted 0.55–0.65 /
   0.40–0.55); duets begin to fall below 30 (67 → 56 → 54/1k) after
   holding 67–79 from 55 to 30; roster duets slide to 0.88x / 0.85x
   (bar 0.85x). Excursions per 1k turned over as point 4 predicted
   (8.2 → 3.15 → 2.02, under the floor). Her announce share fell to the
   roster's at c25 (0.39 → 0.19): below the announce threshold she
   leaves play before arming, so the hungry-Biscuit meow disappears
   from the client. c30 already met parity within +0.04 on the main
   raws.

6. **Addendum 1b (c32 / c28, 2026-09-01): the bracket fails on opposite
   sides.** c32 misses parity on eat, sleep and cuddle (+0.07–0.09,
   both seeds) at 0.76x play; c28 passes (+0.02–0.03) at 0.65x. Welfare
   and play are monotone over 35/32/30/28/25 (eat ≥30 0.23 → 0.18 →
   0.13 → 0.10 → 0.06; play 0.76 → 0.76 → 0.70 → 0.65 → 0.58) with one
   flat step: c32 keeps c35's play at a third less time hungry. Between
   32 and 28 each 2 points of comfort cost ~0.05x of c55 play and buy
   ~0.025 of every gap; duets hold 63–67/1k down to 28. Report-only:
   one c28 seed carried a 250-tick one-sided cosleep (Biscuit `resting
   with_friend` Miso while Miso idle, cuddle 82 → 100, happiness 25.4,
   watchdog quiet, self-resolved), the same shape as the served soak's
   Miso event; a roster mechanic a seed exposed, not a comfort effect.

7. **Addendum 2 (the spec-047 consent gate at c30, 2026-09-01): the
   gate works and costs a quarter of her duets plus parity.** On the
   f45a880 binary, `consent_line` absent reproduces the old c30 run
   tick for tick (15,355 / 15,144 events, all shared: C1 at the event
   level). At `consent_line = 30`, the share of her duets that
   conscript a friend with a non-play need over 30 falls 0.21 → 0.01
   (C2), but duets fall 67.3 → 49.0/1k (0.73x, bar 0.90x, predicted
   60–64) and the lost duets go to elements (95.7 → 117.3/1k, total
   play 1.02x), not to the idle eligible friend the offline pricing
   put within 2 tiles in 84% of blocked starts. Roster duets 0.83x is
   entirely her lost duets counted on their side (roster-roster starts
   34.8 → 35.7/1k, flat). Her E1 gaps widen +0.006–0.028 (cuddle most,
   both seeds) and E1 flips to MISS at c30 (+0.05–0.06 vs 0.05); the
   roster's shares improve 0.006–0.014. Partnered refusal tax 4.9% →
   3.4% of her ticks (scripted; the 4.9% matches F-033's policy 4.7%).
8. **Addendum 3 Half A (2026-09-02): a `w_value` re-admission dial
   cannot buy the duets back.** At `w_value` 0.25 / 0.5 (`w_busy` =
   1/`w_value`) under the gate, duets move 49.0 → 53.6 / 51.2 per 1k
   while element play falls 117.3 → 49.5 / 31.4 and SOLO play appears
   from zero (54.8 / 67.3 per 1k); loiter share (idle beside a busy
   friend) rises 0.137 → 0.18 / 0.20. Any `w_value` > 0 also switches
   on mid-scene friend admission (`selection.rs:499`), and
   `expected_wait` prices a resting or past-minimum friend at zero, so
   a settled rester out-scores every critter; Biscuit walks over,
   cannot conscript, and the solo backstop fires beside it. R7 / R8
   unmoved.

**Decision (prereg rule)**: middle case, owner's call on the curve. If
Biscuit is to be fed, use flat comfort; the food-only weight band is
withdrawn (point 2). Owner's lean 2026-09-01: c30 viable ("0.7x play
with solid element play is still very Biscuit"). Addendum 1's rule
(highest comfort passing parity with play ≥ the owner's 0.70x) lands
on **c30**, and the 32/28 bracket confirms it (c32 fails parity, c28
fails the play line); c25 is the next point on the curve (parity exact,
0.58x, half the meows), not a candidate under that line. **Addendum 2
(prereg rule)**: C2 passes, C3 / C4 / C5 miss → report the price, owner
call: ship c30 + consent with E1 at +0.05–0.06, or re-pin comfort with
the gate on (c28 / c26 + consent bracket; c28 passed E1 at +0.02–0.03
without it). **OWNER RULED 2026-09-02: the anchor is c30 +
`consent_line 30`, no re-admission mechanic** (C3 / C4 / C5 / E1
overridden on the record, RESULTS §Owner ruling). The gate binds the
scripted selector only; the RL menu picks partners directly and the
reward does not price consent, so the trained kitty inherits consent as
a teacher habit. Step 7 trains Biscuit 3.0 with `consent_line` 30 and 0
to read the transfer (RULED 2026-09-02 after Half B; `w_value`
re-admission SHELVED indefinitely, solo play is not a targeted
behaviour). **Scope**: scripted anchor only; a clone's
transfer is the training's to show. **Invalidated by**: an economy
change to `eat_relief` or the 041 rest dials; a `t_partner` re-sweep.
**Re-verify when**: the owner pins a comfort value (re-run that arm
against the then-served economy before the lineage retrain).

## F-039 · active · On the served world the refusal tax is Biscuit's alone and it is partner play: 5.13% of her ticks, 94% `play:kitty`; every other seat pays under 2.3% in grooming and movement

Live refusal baseline (`refusal-baseline-2026-09-02/RESULTS.md`; prereg
+ instrument @ 5831cde before collection). First read off the 046
stamp (`/events/refusal`) on the 2026-09-02 deploy (046 + 047 inert +
048; contagion disabled): 15,134 ticks, 95 polls, zero ring gaps,
served config `275a3d7b…bbed0`.

1. **Taxed share per seat** (refused, turn resolved to Idle): Miso
   0.70%, Biscuit 5.13%, Pumpkin 1.86%, Kittybear 1.91%, Clementine
   2.30%. No seat near the step-5 INVESTIGATE line (10%).
2. **Biscuit's currency is partner play**: 734 of 777 taxed rows. The
   other seats' taxed play rows are 3–23 across the window; they pay in
   `groom:kitty` (150–252) and `move` (64–89).
3. **Absorbed refusals** (heard mid-scene, tick serviced) outnumber
   taxed 3,258 to 1,801. Miso absorbs the most (5.20%, 448 `sleep:with`
   from inside a sleep); Biscuit absorbs 785 play asks on top of the
   734 taxed, so about half her asks land while she is in a scene.
4. **Retention**: combined density 0.334/tick, 1.45× the taxed-only
   figure the 6,000 default was sized on; 15k-tick floor 5,014, the
   default stands.

Retires [F-033](#f-033--active--every-seat-pays-a-partnered-action-refusal-tax-in-its-own-currency--but-for-biscuit-that-is-under-half-its-idle-the-rest-it-chooses)'s
4.7% and the 3.5% INVESTIGATE line as bars: those were seam-probe reads
on a pre-048 engine that counted dead-scene rows b9f9c00 removed. That
the stamp reads 5.13% after 048 took rows away says the seam probe
undercounted, not that 048 did nothing. F-033's mechanism claim (the
tax is partnered, per-seat currency) holds unchanged. **Scope**: the
2026-09-02 deploy's roster and economy. **Invalidated by**: any deploy
touching the selector, the play economy, or the roster. **Re-verify
when**: the Biscuit 3.0 cutover lands (step 7); one window, same
instrument.
