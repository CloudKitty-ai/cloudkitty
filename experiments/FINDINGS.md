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

## F-002 · reserved (candidate, unverified) · `needs_driven` under-uses the non-binding cuddle routes

Reserved: exp-001's prereg deviation of 2026-07-27 names this claim
"candidate F-002" — `needs_driven` under-uses `Sleep{with}`/`Groom{target}`
for Cuddle relief beside busy friends (the 38 events spec 021 miscounted as
false positives were real refusals). The pre-retune count is stale evidence;
the claim registers here, under this id, if a post-retune recount verifies
it. Until then it grounds no design decisions.

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
