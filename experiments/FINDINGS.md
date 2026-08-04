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

---

## F-001 · superseded by F-003 · Credit in CloudKitty is two-channel: fast self, slow teammate

*(Superseded 2026-07-27: the companionship retune — PR #60, cf82007 —
changed the happiness weights and social relief rates these numbers were
measured under. The two-channel structure survives; the quantities do not.
See F-003.)*

An action's effect on the actor's own happiness is front-loaded (~60% of
significant signal mass within 18 ticks — direct relief); its effect on
teammates has near-zero early mass (0.3% within 18 ticks) and lives in a
50–200-tick band peaking around k≈106 — contention and coordination
consequences propagating through others' welfare. The team reward inherits
the slow channel (90% of significant mass within 200 ticks; last
significant tick 380).

**Scope**: measured on `training.toml` (24×24, 5 kitties, heterogeneous
traits) under **`needs_driven` dynamics for every kitty**, substitution
ticks 100–1100, 1,000 samples. Not yet measured: trained-policy dynamics,
the default world's geometry, larger rosters.

**Evidence**: [exp-001 twin-probe result](exp-001-bc-mappo/results/twin-probe-2026-07-25.md)
(bit-reproducible; regeneration commands inside).

**Implications**: γ = 0.995 registered as exp-001's predicted sweep winner
(preserves 0.59 of the discounted team signal vs 0.38 at γ = 0.99, whose
horizon bisects the cooperative band); λ stays 0.95 (no GAE setting
bridges a 100-tick gap); cooperative credit is carried almost entirely by
the critic — critic explained-variance is the watch-first training
diagnostic, and the MAPPO privileged global state is empirically
motivated, not merely conventional.

**Would invalidate**: the teammate band failing to appear on other
geometries; or shifting below ~50 ticks under trained-policy dynamics
(coordinated cats may propagate consequences faster than scripted ones).

**Re-verify when**: the first policy artifact exceeds `needs_driven` on
the paired Nash aggregate (or passes SC-004 certification, whichever
comes first) — re-run the twin probe with that policy seated, in both
all-policy and mixed rosters, and compare the teammate band; supersede or
narrow this finding accordingly. Also due regardless: a default-world
geometry repeat and by-action-class conditioning (the 1k sample mix is
move-dominated).

---

## F-002 · refuted · Non-binding cuddle-route under-use is real but carries no material headroom

Resolved 2026-07-27 (was reserved for exp-001's prereg-named candidate).
The census (`cuddle-census`, engine-predicate classification, 5 seeds ×
20k ticks per config) splits the claim: the **mechanical under-use is
confirmed** — `needs_driven` takes `Sleep{with}`/`Groom{target}` in 0.7%
of moderate-need busy-only opportunities and never when a binding rest
duet is available — but the **headroom hypothesis is refuted**: post-
retune, high-need (≥80) opportunities beside friends occur ~1–2 per 100k
ticks on both the frozen and default worlds, because the heavier cuddle
weight makes the scripted cat service the need early. The 38 pre-retune
events described a world that no longer exists. Not a channel for beating
`needs_driven`; the prereg's interpretation rule (trained-policy Cuddle
pinned streaks beside busy friends = real skill gap) stands unchanged.

**Evidence**: [frozen-world addendum §2](exp-001-bc-mappo/results/frozen-world-addendum-2026-07-27.md).

**Re-verify when**: happiness weights or relief rates change again
(check `engine_defaults_sha256`), or a trained policy shows Cuddle
pinned streaks (then the routes' availability matters, not their
scripted-cat usage).

---

## F-003 · superseded by F-013 · The companionship retune tripled the credit horizon; channels unchanged

*(Superseded 2026-08-02: the 024 wet-fur batch — this finding's own
"any engine-defaults change" trigger — moved every quantity again,
exactly as the retune did to F-001. The two-channel structure
re-confirms on the post-024 engine (early self band reproduces in all
six re-verification runs); the band edges, peak locations, and
retention decimals below are pre-024 history. See F-013.)*

Supersedes F-001's quantities on the retuned baseline (PR #60, cf82007:
happiness weights eat/drink→0.20, cuddle/bath→0.15; groom/play relief→20,
cuddle→15). The two-channel structure holds — self credit front-loaded,
teammate credit slow — but every band moved out ~2–4×: the spillover band
is now ~230–430 ticks (peak k≈406, was ~50–200 peaking k≈106), the team
reward peaks at k≈230 with only 16% of significant mass within 200 ticks
(was 90%), and a diffuse-but-real tail (≈2.5× chance rate of significant
ticks) persists past k=1,000. Mechanism: slower social relief lengthens
scenes, so contention/coordination consequences propagate later and wider.
Decision-point density also fell 0.86→0.72 (more mid-scene ticks where an
idle substitution is rewritten back).

**Scope**: `training.toml` (24×24, 5 kitties, heterogeneous traits) on
post-retune compiled defaults (main 758ec28), `needs_driven` dynamics for
every kitty, substitution ticks 100–1100, 1,000 samples, 1,200-tick traces
(600 is now too short — the first pass truncated live signal at its edge).
Not yet measured: trained-policy dynamics, default-world geometry, larger
rosters, per-action-class structure.

**Evidence**: [exp-001 retuned twin-probe result](exp-001-bc-mappo/results/twin-probe-2026-07-27-retuned.md)
(bit-reproducible; commands inside).

**Implications**: discounted team-signal retention is now 0.10 at γ=0.99,
0.20 at γ=0.995, 0.45 at γ=0.998 — γ=0.99 ends before the cooperative band
*begins* and is empirically dead for the cooperative hypothesis;
recommendation to the owner is to amend exp-001's sweep to {0.995, 0.998}
(prereg amendment, owner's call). Cooperative-credit-is-critic-carried is
strengthened (even less signal inside any reachable GAE window); λ=0.95
and fragment 256 stand.

**Would invalidate**: another engine-defaults change touching happiness
weights, relief rates, or scene durations (check the suite's
`engine_defaults_sha256` stamp); the band failing to reproduce on other
geometries; trained-policy dynamics compressing propagation.

**Re-verify when**: any engine-defaults change (immediately — this finding
died once already that way, as F-001); or the first policy artifact
exceeding `needs_driven` / passing certification — policy-seated probe in
both roster modes, per F-001's original trigger. Still due regardless:
default-world repeat, by-action-class conditioning (mix is 72% move).

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

**Would invalidate**: a demonstration that within-world sample
correlation is negligible at some horizon (it is not, at k > ~50, on
current evidence).

**Re-verify when**: n/a — this is a statistics discipline, not an
environment measurement; revisit only if the probe's sampling design
changes (e.g., one world per sample).

---

## F-005 · superseded by F-013 · Training-world knobs move detectable cooperative signal weakly; scarcity×tempo is the one replicated improver

*(Superseded 2026-08-02: on the post-024 engine the frozen
scarcity×tempo world's paired-seed signal halved and fell below the
false-positive floor — the mechanism reads as the chase sidestep
dissolving the stall-fed queueing consequences this world's gain was
made of. The knob search was honest for the engine it measured; that
engine is gone. See F-013.)*

Across 10 candidate worlds (scarcity, tempo, grid size, combinations)
measured under F-004 discipline, most knobs do nothing or hurt: shrinking
the grid raises chaotic mixing and drowns signal, tempo ×1.75 overshoots
(noise outruns signal — tempo has a sweet spot), scarcity alone is a
wash. The current environment's team-reward counterfactual signal beyond
the early self-mediated band (k ≤ ~14) sits at the false-positive
detection floor even at 3,000 samples / 300 worlds. The single
replicated improvement: **scarcity + tempo ×1.5** (water/chow 3–4,
sunbeams 2, rates ×1.5) — S(.998) 1.5–1.8× base in three disjoint world
batches, with dr and spillover bands co-occurring at k ≈ 730–940, the
signature of queueing/turn-taking consequences. Frozen as `training.toml`
2026-07-27; `needs_driven` holds 0.881–0.883 there (bounds pass,
0.10 above the 0.78 feasibility floor).

**Scope**: `needs_driven` dynamics, 5-kitty heterogeneous roster, the
knob ranges actually searched. Says nothing about trained-policy
dynamics, other rosters, or knobs not searched (durations, trait
spreads, roster size).

**Evidence**: [world-search result](exp-001-bc-mappo/results/world-search-2026-07-27.md).

**Implications**: exp-001 trains on the frozen scarcity×tempo world; the
searched-and-rejected table is the recorded H0a contingency (harden from
the measured Pareto set, don't invent). The near-floor absolute signal
sharpens the experiment's framing: single-action counterfactual reward
effects are marginal, so learnable cooperation, if it exists, is carried
by state-mediated credit (critic bootstrapping through visible
intermediate states) — critic EV remains the make-or-break diagnostic.

**Would invalidate**: engine-defaults changes (check
`engine_defaults_sha256`); a knob outside the searched ranges proving a
large improver; trained-policy dynamics changing the signal landscape.

**Re-verify when**: H0a is observed in exp-001 (re-run the search with
fresh budget before choosing the hardening step); or any engine-defaults
change (with F-003).

---

## F-006 · superseded by F-013 · The default world carries no detectable cooperative credit

*(Superseded 2026-08-02: both of this finding's own re-verify
conditions arrived at once — an engine-defaults change (024) and a
default-config change (the #86 24×24 cutover). On the current served
world the claim is inverted: a replicated cooperative band exists at
k ≈ 230–330. The 32×32 measurement below remains correct for the
world it measured. See F-013.)*

Measured 2026-07-27 (product thread, at the owner's request; verified
bit-exact by the experiments thread): on `cloudkitty.toml` (32×32, 4
kitties, element minimums 8, post-retune defaults), 1,000 samples over
150 disjoint worlds under F-004 statistics, the fast self channel
reproduces (contiguous k = 0–11 band) while **team-reward and spillover
significance sit below the false-positive floor** (13 and 10 ticks vs
~60 expected by chance). The teammate band F-003 measured on the
training world does not exist here — detectable team credit is ~7×
smaller than the frozen training world's and statistically absent.

**Scope**: `needs_driven` dynamics on the default world as configured at
post-retune defaults. **Confounded by design**: geometry, roster size,
and scarcity all differ from the training world at once; this finding
says the default world is signal-free, not which knob makes it so (the
scarcity-only deconfound at fixed geometry is cheap via family-gen and
unrun). Trained-policy dynamics unmeasured, as everywhere.

**Evidence**: [default-world twin-probe result](exp-001-bc-mappo/results/twin-probe-2026-07-27-default-world.md)
(regeneration verified bit-identical by a second session).

**Implications**:
- The training-world selection (F-005) was load-bearing and is now
  corroborated from outside its searched set: training on the default
  world would have optimized against a signal that is not measurably
  there.
- **Certification is a welfare gate, not a cooperation instrument.**
  *(Correction 2026-07-30: this bullet conflated two "default worlds".
  F-006's measurement is of `cloudkitty.toml` — correct and unchanged —
  but exp-001's certifications to that date had actually run on the
  compiled 3-kitty default, a different world; see deviation 31, which
  fixes §8's world to `cloudkitty.toml` and makes the point below
  apply as intended.)* Certification and the report protocol run on the default world, where
  single-action cooperative credit is undetectable — a policy's paired
  Nash gain there must come from policy-level behavioral differences
  compounding over the run, not from the marginal credit the probe
  measures. This sharpens H0c (transfer) risk for exp-001: cooperation
  learned in the contended gym must survive in a roomy world where
  coordination moments are rare. The design already carries the
  mitigations (default-world anneal, mixed-roster exam as the
  cooperation instrument); this finding is why they matter.
- F-003's "default-world repeat" follow-up is closed by this entry.

**Would invalidate**: signal appearing on the default world under
trained-policy dynamics (coordinated cats may *create* the contention
scripted cats avoid — that would narrow this to needs_driven dynamics);
default-config changes (check `engine_defaults_sha256`).

**Re-verify when**: the policy-seated probe runs (F-003's trigger) —
run it on BOTH worlds; and after any engine-defaults change.

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

> **Supersession note (2026-07-30)**: forensics
> ([collapse-forensics-2026-07-30.md](exp-001-bc-mappo/results/collapse-forensics-2026-07-30.md))
> identified the mechanism and found this entry's framing wrong on both
> counts. The mode is not long-horizon (collapse is visible *within*
> 2,000 ticks on the world that triggers it) and not a coordination
> instability (a single fragile policy collapses alone). It is
> **roster-OOD input fragility** — see F-010. The observations below
> were real; their interpretation was an artifact of certification
> accidentally running the compiled 3-kitty world (deviation 31) while
> probes ran `cloudkitty.toml`. Kept for the record.

In exp-001 Arm 2, 2 of 6 runs (γ=.998 s2, γ=.995 s3) carry seeds whose
all-policy rosters collapse (welfare 0.31–0.69) at 20,000-tick
evaluation while the same policies' 2,000-tick default-world probes read
a healthy ~0.94 — indistinguishable from the runs that certify positive.
The failure needs > 2k ticks to compound, and it never appears in Mixed
rosters (all six runs are Mixed-positive or Mixed-neutral): scripted
teammates arrest the spiral. Training-time diagnostics (§10.1 full set)
were uniformly healthy in the failing runs — this mode is currently
invisible until certification-length all-policy evaluation.

**Scope**: exp-001 Arm 2 policies on the default world, greedy seating.
Mechanism unknown (investigation deliberately parked); plausibly a
self-reinforcing coordination failure among five copies of the same
policy.

**Evidence**: [Arm 2 record](exp-001-bc-mappo/results/arm2-training-2026-07-30.md)
(probe-vs-certification divergence); per-seed tables in the report
protocol result.

**Implications**: **no deployment-soak or shipped-candidate decision may
rest on sub-certification-length or mixed-roster evidence alone** —
candidate selection requires the full 20k all-policy run. Trainer
validation probes at 2k ticks measure transfer, not stability. The
Mixed-roster immunity is a concrete lead for exp-002's
partner-population-curriculum item.

**Would invalidate**: the mechanism turning out to be an evaluation
artifact (e.g. a specific eval-seed interaction) rather than a policy
property — the parked investigation decides.

**Re-verify when**: the instability investigation runs; or any new
policy lineage (exp-002) reaches candidate stage — screen it with
full-length all-policy runs before any other claim.

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
candidate stage.
