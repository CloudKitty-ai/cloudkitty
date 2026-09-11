# Research: Groom-other reprice (spec 054)

All Technical Context unknowns resolved. Decisions below; code citations
verified on this branch (08eb1ed base).

## R1 — Curve form

- **Decision**: Clamped linear ramp `c(x) = min(ceiling, floor + slope·x)`,
  defaults 0.25/3.5/2.0, `x = delivered/groom_relief ∈ [0, 1]`.
- **Rationale**: Owner ruling 2026-09-11 (after Experiments discussion).
  Pure add/mul/min — the tick path's native arithmetic class — so Article V
  determinism and cross-platform goldens hold with no table, no tolerance
  regime; exact 0.25 floor restores design rule 1's strict reading; exact
  saturation at x = 0.5; one-line numpy replication for lab work.
- **Alternatives considered**: the original logistic (exp() would be the
  first transcendental in the tick path; platform libm differs ~1 ulp
  mac/linux — rejected); sampled table of the logistic (workable but
  dominated — table machinery for no design gain); √-based algebraic
  sigmoid (bit-exact and smooth but needs a refit moving the owner's
  tiers).

## R2 — Config surface and the legacy key

- **Decision**: Three new `ActionEffects` fields — `groom_cuddle_floor`
  (0.25), `groom_cuddle_slope` (3.5), `groom_cuddle_ceiling` (2.0) — with
  `serde(default = ...)` and normal serialization. `groom_cuddle_relief`
  stays as a field but becomes `#[serde(default, skip_serializing)]` and
  is read by no code: recognised so `deny_unknown_fields` holds on every
  existing config, invisible to `/config` and the stamp.
- **Rationale**: The ForeignTable precedent (`config/mod.rs` ~L87–100:
  `[rl]`/`[plugins]`/`[watchdog]` "recognised here only so
  deny_unknown_fields can hold... never serialize"). Keeping the field
  live-but-unread (serializing) would serve a dead dial through `/config`
  forever; deleting it breaks frozen evals/v2 AND current evals/v3.
- **Alternatives considered**: delete the key (breaks v2/v3 — ruled out);
  reinterpret as ceiling override (silent meaning drift on 2.0/15.0/0.5
  pins — ruled out by owner Q2 ruling).
- **Consequence (declared)**: `/config` loses `groom_cuddle_relief` and
  gains the three dials; `engine_defaults_sha256` moves once, by exactly
  this delta. SC-007's byte-diff check pins it.

## R3 — Where the one curve definition lives

- **Decision**: `impl ActionEffects { pub fn groom_cuddle_pay(&self,
  delivered_bath: f32) -> f32 }` in `config/mod.rs` — clamps
  `delivered_bath` by `self.groom_relief`, normalizes, applies the ramp.
- **Rationale**: Both live readers already hold the actions config:
  `action.rs:794` via `effects`, `needs_driven.rs:418` via
  `ctx.config.actions`. One definition, two call sites — FR-008's
  no-drift-between-readers requirement becomes structural.
- **Alternatives considered**: free function in action.rs (the scripted
  seam would import across module intent); duplicating the arithmetic at
  each site (the exact drift FR-008 forbids).

## R4 — Delivered relief at the effect site

- **Decision**: In `apply_activity_effects`'s `Grooming { Some(friend) }`
  arm (`action.rs:783–796`), read the target's bath need BEFORE
  `lower_need(.., NeedKind::Bath, groom_relief)`:
  `delivered = target_bath_before.min(groom_relief)`; then pay
  `groom_cuddle_pay(delivered)` to the groomer.
- **Rationale**: `lower_need` (`action.rs:972`) applies `needs.add(need,
  -amount)` with clamping inside `Needs::add` — the *requested* relief is
  `groom_relief` but the *delivered* relief is bounded by the dirt that
  exists, which is precisely the spec's earning basis (FR-001, FR-006).
  Reading before applying keeps the payment and the relief on the same
  tick's same state, in the engine's existing application order (fairness
  untouched).
- **Multi-groomer note**: two groomers on one target in one tick settle in
  the fair per-tick application order; the second sees the remaining dirt.
  Deterministic, and consistent with "paid only for dirt that exists".

## R5 — The scripted seam's basis

- **Decision**: `needs_driven.rs:418` (the single kitty-groom initiation
  path — spec 045 seam 3 and the meow-response gate are the same line)
  replaces `+ ctx.config.actions.groom_cuddle_relief` with
  `+ ctx.config.actions.groom_cuddle_pay(emitter.needs.get(NeedKind::Bath))`.
- **Rationale**: The seam prices the scene's value as "bath pressure +
  groomer's expected relief"; the expected relief is now the curve at the
  emitter's current bath — the first groomed tick's actual pay. The 045
  pinned sensitivity tests (~L1859–1901) re-point: the "decline bar tracks
  the configured dial" property now tracks the curve dials (slope/ceiling
  in the generous case).
- **Alternatives considered**: scene-total expected income over projected
  scene length (speculative modelling the seam never did for the flat
  price; out of scope).

## R6 — Key-settings surface (spec 052)

- **Decision**: In `cloudkitty-server/src/settings.rs`, replace the
  `("actions", "groom_cuddle_relief")` entry with three entries for
  floor/slope/ceiling (value + default + presence-based source, as every
  entry). Key-name goldens move 19→21 (two-seat fixture) and 18→20
  (minimal), each a predicted red first.
- **Rationale**: FR-011; spec 052's curation lists every dial an operator
  would ask "was it on?" about — a reprice's dials are exactly that.

## R7 — f32 precision

- **Decision**: No special handling. 0.25, 3.5, 2.0 are exactly
  representable; the ramp is two correctly-rounded IEEE ops plus min; the
  spec-052 `num()` shortest-round-trip lesson applies to the /settings
  rendering of the new dials (already generic).

## R8 — Shipped TOMLs and their guard test

- **Decision**: Scrub `groom_cuddle_relief` from `cloudkitty.toml` (was
  pinned 2.0) and `training.toml` (was 15.0); pin no new dials — both
  serve the engine defaults, so `/settings` shows the three dials
  `[default]`. Update `tests/shipped_configs.rs` (~L119–131), which
  currently asserts the served 2.0 pin ("TEMPORARILY absent from the
  rider loop"): that assertion retires with the flat dial; its replacement
  asserts the served config carries no legacy key and inherits the curve
  defaults.
- **Rationale**: Owner Q2 ruling scrubs served/training; the defaults ARE
  the owner's chosen values, so pinning them would only add stamp-drift
  surface. Anchor/arm configs under `experiments/` are Experiments' and
  are not touched (frozen-tree rule).

## R9 — Schema and reward unchanged (FR-007 proof shape)

- **Decision**: No file under observation/reward encoding is touched; the
  guard is SC-005 (schema 5 = 408 floats asserted by existing tests
  staying green) plus the review checklist. Relief → needs → happiness is
  the only propagation path, which is world dynamics, not reward terms.

## R10 — Merge sequencing

- **Decision**: Build → converge → PR → CI green → **HOLD MERGE**. The
  owner merges at the reseat sitting (FR-013). Recorded in plan
  §Sequencing; the #332 revert is discharged by retirement of the flat
  dial (spec Assumptions), to be confirmed at that sitting.
- **Rationale**: A box deploy (the 052 key-settings first print) is owed
  while the roster is still frozen; anything on main rides that deploy.
