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

## F-003 · active · The companionship retune tripled the credit horizon; channels unchanged

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

**Would invalidate**: a demonstration that within-world sample
correlation is negligible at some horizon (it is not, at k > ~50, on
current evidence).

**Re-verify when**: n/a — this is a statistics discipline, not an
environment measurement; revisit only if the probe's sampling design
changes (e.g., one world per sample).

---

## F-005 · active · Training-world knobs move detectable cooperative signal weakly; scarcity×tempo is the one replicated improver

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

## F-006 · active · The default world carries no detectable cooperative credit

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

**Re-verify when**: n/a.
