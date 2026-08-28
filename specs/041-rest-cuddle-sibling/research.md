# Phase 0 Research: Rest becomes co-sleep's sibling

No NEEDS CLARIFICATION markers survive the two clarify sessions; this
file consolidates the decisions the plan builds on, with rationale and
rejected alternatives. Sources: the handoff doc (f4b3708+), the
need-flow model, F-027/F-029/F-031/F-033, two clarify sessions
(2026-08-26, 2026-08-28), and in-session verification of every cited
engine surface.

## D1 — Legality and binding shape: mirror `Sleep{with}` exactly

**Decision**: Rest-with-friend validates via `is_available_friend`
(adjacency only), binds nobody, stamps nobody; the partner is
re-filtered every serviced tick exactly as `Sleeping` re-filters its
companion (`action.rs:808`).

**Rationale**: deletes rest's share of the F-033 refusal tax
structurally; co-sleep is the proven template (spec 028), and
"sibling" means one shape, not a third pattern.

**Alternatives**: keeping conscription and patching refusals
(rejected — patches the symptom, keeps the tax); a prune-based
partner exit like grooming's (`world.rs:476`) (rejected — sleep's
per-tick re-filter is the sibling's own idiom and needs no prune
entry).

## D2 — Tier resolution: one shared mutual predicate

**Decision**: extract the "partner is itself sleeping or resting"
check that `apply_sleep_relief` evaluates once above both its uses
(`action.rs:834-841`) into a single named function; co-sleep pricing,
spec-031 warmth conduction, and rest tier resolution all call it.

**Rationale**: FR-002's no-disagreement requirement, and the
owner-approved waterline definition hook — the step-3 contagion will
reference this function plus `Activity::partner()` rather than define
"partnered" again.

**Alternatives**: duplicating the matches! in the rest arm (rejected —
the exact drift the existing comment warns against).

## D3 — Tier observability: per-tier serviced-tick counters (owner: A)

**Decision**: two additive fields on `ActivityEnd`
(`events.rs:34`) — `mutual_ticks`, `drip_ticks` — `#[serde(default)]`,
`skip_serializing_if` zero, riding every event (zero on non-tiered
activities). Accumulated in per-scene state alongside the activity
clock, reset at scene start, copied into the event at scene end.
Invariant: `mutual_ticks + drip_ticks ≤ span()`; the shortfall is
exactly the solo (posture-only) serviced ticks.

**Rationale**: one event per scene keeps F-031 span semantics and
scene counting intact; nonzero `drip_ticks` anywhere is SC-004's
emit-proof; serde defaults keep FR-009 (pre-change snapshots and JSON
consumers load unchanged). Experiments concurred independently.

**Alternatives**: single tier field (rejected — a scene has no single
tier; final-tier reporting is the F-029 artifact class); per-tier
event segments (rejected — shreds scene counting and spans);
separate transition ring (rejected — new surface for no gain).

## D4 — Dial split lands at the classic value, byte-identical

**Decision**: commit 1 adds `rest_mutual_relief` and
`groom_cuddle_relief`, both defaulting to the classic
`cuddle_relief` value (engine default 15.0, `config/mod.rs:588`;
served toml 8.0/8.0), swaps the two call sites
(`action.rs:762`, `:797-798`), and proves byte-identical world
evolution. `cuddle_relief` launched accepted-but-inert here;
**superseded 2026-08-28 (owner's noisy-failure ruling, commit 4)**:
presence is now a loud validation error with the migration map, and
all 181 committed configs were migrated, each inheriting its own
value into the split dials — so they keep loading, faithfully.

**Rationale**: spec 028's own launch pattern (`defaults.rs:42-43`);
continuity is checkable before any value moves.

**Alternatives**: delete the key (rejected by owner — breaks F-029
re-cuts with current tools; 3.0 deletes it at the wall instead);
split+reprice in one commit (rejected — conflates a provable no-op
with an economy change).

## D5 — Engine-sibling commit changes legality/binding only: drip = 0.0

**Decision** (owner: A): `rest_drip_relief` launches at 0.0 in both
engine defaults and the served toml at the engine commit; the reprice
diff sets 0.25.

**Rationale**: the engine commit's observable change is confined to
legality, binding, tiers, and events; every price movement lives in
one reviewable config diff. A busy-partner rest scene paying nothing
mirrors solo rest.

**Alternatives**: 0.25 at the engine commit (rejected — economy moves
in two places).

## D6 — Reprice values (model-derived, owner-pinnable)

**Decision**: served toml diff — `cosleep_drip_relief` 3.0 → 0.25,
`cosleep_mutual_relief` 8.0 → 0.6, `groom_cuddle_relief` 8.0 → 0.5,
`rest_drip_relief` 0.0 → 0.25, `rest_mutual_relief` stays 8.0. Stale
comments corrected in the same diff (the "11.6" claim — measured 5.1
mean / 2.8 median — and both saturating-delivery cosleep comments);
the play ladder comment untouched. Tier order drip < mutual is a
comment-carried convention, no load-time validation (owner-ratified).

**Rationale**: the need-flow model's validated starting points; the
per-scene (not per-pair) caveat and the reciprocal double-pay are
priced into its predictions.

**Alternatives**: validation-enforced tier order (rejected by owner —
the cosleep pair's existing covenant, nothing speculative); mutual
≤ 0.42 for per-pair non-saturation (deliberately not taken — no
preemptive retune, the acceptance census decides).

## D7 — No RL-crate code change

**Decision**: no edits in `cloudkitty-rl`. The `rest_kitty` mask bits
change meaning automatically because the mask probes `validate`
(the no-carve-outs doctrine); menu layout (34 entries, `codec.rs`),
`KITTY_SLOT`, and the message head are untouched; the mask does not
feed observations (verified: `observe.rs` has zero mask references —
masks gate selection in `behavior.rs` only).

**Rationale**: FR-003; one rule, no parallel definition — the change
propagates by construction.

## D8 — Sequencing and operations (owner-ruled)

- **One retrain**: 041 rides the wall retrain; no dedicated pre-obs
  retrain (throwaway work). Scripted seats respond to the 2.x deploy
  immediately and are the clean pre-wall read; pre-declared incumbent
  expectation is zero rest scenes, so the deploy soak watches
  welfare/watchdog, not rest counts.
- **One PR, three commits**: split (byte-identical) → engine sibling
  (drip 0.0) → reprice (config diff + comments).
- **Stamp movement**: the split adds config fields, so
  `engine_defaults_sha256` moves at commit 1. Accepted — SC-007
  already requires the re-baseline before any certification bar;
  world-evolution byte-identity (SC-001) is the continuity claim,
  not stamp identity.
- **Out of scope, handed to the wall**: 3.0 deletion of the retired
  key's `Option` field + rejection arm (the key becomes a plain
  unknown field — the loud-retirement amendment already removed its
  effect) and the FR-009 bound-duet tolerance (both marked for the
  config-hygiene sweep); eval-suite v2 + FromConfig; the census
  shared helper (ruled YES, lane assigned at bundle plan time).

## D9 — Test strategy (rule 5/6 discipline)

**Must go red (guards of the change)**: the conscription-legality
arm for rest (`action.rs:375-378` behavior), partner-binding and
partner-stamp assertions (`action.rs:~2245`, `:2613-2673` — several
assert the classic `cuddle_relief` value by name), `suite.rs:1512`
(sweep bumps the dial), the nan-validation table
(`config/mod.rs:~1829`), and the two config sweeps any root-toml
key addition reddens.

**Must stay green (kept behavior)**: co-sleep pricing and warmth
conduction, grooming, play (no dial moves), durations, determinism
(golden evolution digest for commit 1's byte-identity), Article I–V
property suites.

**New guards, each shown red first**: availability legality (busy
partner legal, non-adjacent illegal), no binding/no stamp, per-tick
tier resolution incl. mid-scene flap, both-parties payment, counter
accumulation + the sum-≤-span invariant (drive red via a solo-tick
shortfall), snapshot resume of a pre-change bound duet, deprecated
key retired loudly (as amended) + unknown-key rejection still
strict, drip 0.0 at the
engine commit paying nothing.
