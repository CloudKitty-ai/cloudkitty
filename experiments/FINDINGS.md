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

## F-001 · active · Credit in CloudKitty is two-channel: fast self, slow teammate

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
