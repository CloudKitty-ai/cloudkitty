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
  Certification and the report protocol run on the default world, where
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
