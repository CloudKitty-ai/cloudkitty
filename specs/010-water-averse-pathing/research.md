# Research: Water-Averse Pathing

**Date**: 2026-07-20 | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

Seven decisions (R1–R7), grounded in the post-009 code: `step_toward`'s
pure-Manhattan greedy walk with its occupied-filter and sidestep fallback,
`selection`'s scored pass with the 004 score/walk-agreement rule, and the
engine facts that water elements are permanent (no ttl) and `Move` validation
is terrain-blind by design.

## R1 — The preference lives in the stepper's ordering, never in its options

**Decision**: `step_toward` keeps its exact candidate set and progress rule
(a step is progress when it lowers Manhattan distance) and changes only the
*ordering among improving steps*: choose the minimum of
`distance(dest) + water_step_cost × is_water(dest)`, ties to direction order
as today. When the only improving step is wet, it is still chosen — the
kitty wades. The sidestep fallback (fires when nothing improves and the
kitty is not beside its target) now prefers the first *dry* free direction,
falling back to the first free direction of any kind; this same preference
is what walks a kitty off a water tile it finds itself standing on (FR-005 —
staying wet loses to an equal dry option).

**Rationale**: anti-stuck by construction, provably: the set of steps the
kitty is willing to take is identical to today's, so every termination and
welfare property of the 009 stepper carries over untouched — only *which*
improving step wins changes. FR-001/FR-002 in one function.

**Alternatives considered**: treating the surcharge as a veto below a
threshold (creates layouts where no acceptable step exists — the stuck risk
the owner explicitly excluded); full cost-field comparison including
non-improving steps (a dry sidestep can then beat a wet improving step,
and two adjacent tiles can each prefer the other — a deterministic
oscillation trap).

## R2 — Skirting emerges from Manhattan geometry; wading is the honest floor

**Decision**: no lookahead, no route memory. When both axes have distance to
close (dx > 0 and dy > 0) there are *two* improving directions, and R1's
ordering picks the dry one — that is the skirt, and it is the common case
against blob-shaped ponds. When the pond blocks the *sole* improving
direction (target dead ahead), the kitty wades rather than dithering at the
shore.

**Rationale**: the spec pre-accepted exactly this edge ("kitties keep their
existing step-by-step navigation... a kitty may occasionally wade where a
perfect navigator would have found a long dry way — never worse than
today's always-wade"). Every stronger behavior needs either memory
(oscillation risk, behavioral state the architecture deliberately lacks) or
a planner (out of scope by spec Assumption).

**Alternatives considered**: A*/BFS route planning (explicitly out of
scope); one-tile lookahead (moves the dithering one tile out and doubles
the decision surface for a marginal case the spec already accepts).

## R3 — One priced estimate, shared by score and walk

**Decision**: a new `priced_travel(from, to, world, config)` helper in
`selection.rs`: Manhattan distance plus `water_step_cost` per water tile on
the deterministic dominant-axis-first L-path from `from` to `to`, endpoint
excluded (a kitty never needs to stand on its target — interactions are
orthogonal since 009). Used for: (a) **eat/drink target choice** —
`seek_element` and `distance_given` both pick the element minimizing
`(priced_travel, id)`, replacing raw `nearest_element`, so the bowl chosen
and the bowl walked to are the same bowl under the same arithmetic (the 004
agreement rule); (b) the **sleep** estimate and the `sunbeam_reach`
comparison in `pursue`, which must stay mirror images; (c) the **cuddle**
travel estimate. **Playmates stay unpriced**: they move every tick, chases
re-evaluate continuously, and pricing a moving target's momentary L-path
would add noise, not honesty (recorded as a scope decision).

**Rationale**: FR-004 with the approximation latitude the spec grants ("may
approximate... deterministic... never make an only-option target
unreachable or unpickable" — a finite surcharge can reorder choices but
never skip a need). The L-path is the natural straight-line proxy for the
greedy walk and is exactly reproducible.

**Alternatives considered**: true cheapest-path pricing (a planner by the
back door); pricing only the score but not the target choice (kitty scores
the detour then walks to the wet bowl anyway — the visible mismatch US2
exists to prevent); bounding-box water counting (overcounts water beside
the path and double-charges wide ponds).

## R4 — One config field, serde-defaulted, validated, documented three times

**Decision**: `water_step_cost: f32` joins `BehaviorConfig` in the
established mold: `#[serde(default = "default_water_step_cost")]` returning
**4.0** (a wet step reads as five tiles of effort — 1 walk + 4 reluctance),
startup validation rejecting non-finite or negative values with the standard
naming-the-field error, and a commented line added to all three shipped
world files. Existing configs without the key keep working (FR-003/SC-005).

**Rationale**: Article VI and the `playful_comfort`/`tile_cost` precedent —
same file, same macro pattern, same error voice. Default 4.0 makes a
2-wide pond worth an 8-step detour, which reads right at watching pace and
is trivially tunable at the gate if it doesn't.

**Alternatives considered**: `u32` (the `tile_cost` family is f32; keep the
arithmetic uniform); a `[behavior.tile_cost]` sub-table (one key does not
justify a schema);
zero default (ships the feature off — pointless).

## R5 — The engine is deliberately absent

**Decision**: no change to `Move` validation, `world.rs`, `spawn.rs`, or
chase stepping (`Direction::toward` in the `Chase` apply arm — chases stay
terrain-blind: their targets are fleeing critters, the pursuit re-aims every
tick, and a chase that splashes through a puddle is charming, not a bug;
recorded as a scope decision like playmates in R3).

**Rationale**: the spec's anti-stuck argument *is* this absence (FR-002);
every line of engine change would need an Article IV justification this
feature does not have.

**Alternatives considered**: engine-side move costs (Article IV violation —
the engine would be expressing preference); pricing chase steps (fleeing
targets make the L-path stale before it is walked).

## R6 — Nothing new to store, nothing new to serve

**Decision**: no snapshot or API change of any kind. The preference is a
pure function of (position, world, config) evaluated at decision time.

**Rationale**: FR-008; behaviors are stateless by architecture and this
feature keeps them so.

**Alternatives considered**: none serious.

## R7 — Verification: prove the ordering, the pricing, and the guarantees

**Decision**: (1) `needs_driven.rs` unit tests for the stepper: dry beats
wet when both improve; wet is taken when it alone improves; the fallback
prefers dry; a kitty standing on water steps off given an equal dry option.
(2) `selection.rs` unit tests for `priced_travel` arithmetic (L-path,
endpoint exclusion) and the US2 acceptance case: bowl 4 steps away across
water loses to a bowl 6 dry steps away with the default cost, and remains
chosen when it is the only bowl. (3) `config.rs` tests: default applied
when absent, negative/NaN rejected with the field named. (4) A crafted
skirt/wade integration test in `welfare_longrun.rs`: a pond the kitty walks
around when geometry offers a dry improving path, and wades through when the
target is dead ahead — both deterministic. (5) The full welfare/property
suite re-run (Article I under the default config), plus clippy/fmt and the
untouched-surface diff (engine files, client). (6) Live look on the demo
world.

**Rationale**: same three-tier shape as 009; the automatable core is the
ordering and the arithmetic, and the welfare suite already drives hostile
randomized worlds over the default (water-bearing) config.

**Alternatives considered**: a dedicated water-heavy property config
(worth adding only if the default-config suite ever proves too gentle —
the crafted integration test covers the sharp geometry deliberately).
