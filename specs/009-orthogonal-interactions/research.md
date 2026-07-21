# Research: Orthogonal-Only Interactions

**Date**: 2026-07-20 | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

Eight decisions (R1–R8), grounded in a full call-site inventory of
`chebyshev_distance` and `is_adjacent` across `cloudkitty-core` (grep of every
use, read of every surrounding function). Two anchors: **movement is already
strictly 4-way** (`Direction` is N/E/S/W and `Position::step` is the only
mover), so nothing reachable can become unreachable; and **`is_adjacent` is
already the single shared adjacency predicate** for validation, world helpers,
behaviors, and the property suite — which makes the safest implementation a
redefinition, not an addition.

## R1 — Redefine `is_adjacent`, don't fork it

**Decision**: `Position::is_adjacent` changes meaning in place: from
`chebyshev_distance <= 1` to `manhattan_distance <= 1` (own tile + four
compass neighbors). A new `Position::manhattan_distance` (`dx + dy`) joins the
grid vocabulary. Every one of the ~20 `is_adjacent` call sites — `validate`'s
Eat/Drink/Play arms via `adjacent_element`/`adjacent_stocked_chow`/
`is_available_friend`/`is_conscriptable_friend`, the counterpart-gone checks,
the behaviors' opportunism and pursuit arms, and the welfare long-run's
assertions — inherits the new range with zero per-site edits. The grid
module's doc comment (which currently *documents* Chebyshev adjacency as
matching the spec) is rewritten to document the 009 rule.

**Rationale**: "adjacent" has exactly one meaning in this codebase — "close
enough to interact with" — and the feature changes that meaning globally.
Redefining the predicate makes drift impossible: no call site can be missed,
because there is nothing to migrate. FR-001/FR-002 land in one function.

**Alternatives considered**: a new `in_interaction_range` beside the old
predicate (leaves a loaded gun — any future caller of `is_adjacent` silently
reintroduces diagonals); per-site Manhattan checks (30 edits, 30 chances to
drift).

## R2 — Manhattan everywhere a decision looks, Chebyshev nowhere near one

**Decision**: every `chebyshev_distance` call *outside `spawn.rs`* becomes
`manhattan_distance`. Inventory: `world.rs` — `adjacent_element` tie-break,
both `nearest_element`s, `nearest_critter`, `nearest_friend`, and
`update_pursuit`'s closing distance; `selection.rs` — `distance_given`'s
nearest lookups, `sleep_travel_distance`, `play_travel_distance`,
`nearest_viable_playmate`'s ordering, `play_action_with`'s reach test,
`adjacent_playmate`'s tie-breaks; `needs_driven.rs` — the sunbeam-reach test,
the free-friend ordering in the cuddle arm, `seek_element`'s usable tie-break.

**Rationale**: FR-005 — with 4-way movement, Manhattan *is* the walk. The 004
lesson (encoded in `sleep_travel_distance`'s doc comment) is that the score
and the walk must never disagree; leaving Chebyshev in any scoring path while
the walk costs Manhattan recreates exactly that class of bug. One metric for
every decision, tie-breaks keep their `(distance, tag, id)` shapes.

**Alternatives considered**: migrating only the sites the backlog named
(`selection.rs`, `needs_driven.rs`) — leaves `world.rs`'s nearest-target
resolution disagreeing with the behaviors that call it; scoring in Chebyshev
"because the differences are small" — small is how 004's lock-in started.

## R3 — `step_toward` simplifies to pure Manhattan progress

**Decision**: the greedy stepper's two-part progress score
`(chebyshev, manhattan)` collapses to plain Manhattan. Its own comment says
why the pair exists: "Chebyshev alone cannot see progress on a diagonal" —
with Manhattan as the metric the patch is unnecessary. A step is progress when
it lowers `dx + dy`; the sidestep-rather-than-freeze fallback fires when
`manhattan > 1` (previously `chebyshev > 1`), which correctly keeps a kitty
maneuvering when it stands diagonal to its target (Manhattan 2 — *not*
arrived under the new rules) with its progress steps blocked.

**Rationale**: FR-004 — the walk must terminate at an orthogonal neighbor,
never rest diagonal-and-stuck. Greedy Manhattan descent with 4-way steps
always has an improving step when one is unoccupied, and the existing sidestep
fallback covers the blocked case. Net code is *simpler* than today.

**Alternatives considered**: keeping the pair ordered `(manhattan, chebyshev)`
(the second component is now pure noise); teaching `step_toward` an explicit
"arrived" concept (callers already gate on `is_adjacent` before walking — R1
handles it).

## R4 — Chase: patience judges in Manhattan; the chase step is already right

**Decision**: `update_pursuit`'s closing distance (world.rs) moves to
Manhattan like every other decision distance (R2). The chase *step* in
`action.rs`'s apply arm — `Direction::toward`, dominant-axis, 4-way — is
verified correct and left alone, as is `Direction::toward` itself (its
dominant-axis tie rules are deterministic and sensible for closing Manhattan
distance).

**Rationale**: spec US2 scenario 2 — a kitty one tile diagonal from its quarry
(Chebyshev 1, Manhattan 2) that steps to an orthogonal neighbor (Chebyshev 1,
Manhattan 1) has made *real, catch-enabling* progress; measured in Chebyshev
the patience clock sees a stall and can condemn a chase at the very moment it
becomes winnable — the same bug shape `a_long_chase_is_not_abandoned_at_the_
moment_it_arrives` already guards against, one metric further out.

**Alternatives considered**: leaving pursuit in Chebyshev (spuriously
abandoned chases, verified against the patience rule above); rewriting chase
stepping to route around blockers like `step_toward` (out of scope — chase
stalls against a blocker today by design, "the spec turns blocked movement
into idling").

## R5 — Config: reinterpret, never rename, zero diffs

**Decision**: no configuration change of any kind. `tile_cost`,
`solo_play_reach`, `sunbeam_reach`, `worth_a_detour` keep names and values;
their documented unit was always "tiles of travel", which under 4-way movement
simply *is* Manhattan steps now that the code agrees. The shipped config
files (including the owner's staged 16/48 worlds) are not touched.

**Rationale**: FR-006/SC-005 and Article VI — the constants were named
honestly; it is the code's metric that was dishonest. Values shift meaning
only at far diagonals (spec edge case, accepted by the owner in the spec's
Assumptions).

**Alternatives considered**: rescaling reaches (×~1.4) to preserve the old
*effective* areas — false precision, new diffs in her tuned worlds, and it
would preserve exactly the dishonest geometry the feature removes.

## R6 — Snapshots: no schema change, one transient quirk accepted

**Decision**: snapshot schema untouched. Old saves load as-is; stranded
diagonal activities end on the first tick via the counterpart-gone rule,
which inherits R1 (it checks through `adjacent_element` / `is_adjacent` /
duet reciprocity). One documented transient: a `Pursuit` restored from an
old save carries a `closest` measured in Chebyshev; compared against
Manhattan distances (always ≥), the patience clock may run slightly early on
that one restored chase — worst case, one chase is abandoned early once,
then everything is native. No migration code.

**Rationale**: FR-003/SC-003 — the counterpart-gone rule was built for
exactly this ("a vanished counterpart" and "an out-of-range counterpart" are
the same case to it); a one-shot pursuit quirk on cross-version restore is
far below the cost of versioned snapshot migration for a QoL change.
Determinism within a rules version (Article V) is unaffected.

**Alternatives considered**: clearing `pursuit` on load (touches
serialization for a cosmetic transient); snapshot version bump + migration
(machinery this project has deliberately avoided; nothing here warrants
starting).

## R7 — Verification: tighten the guards that already exist, add two

**Decision**: (1) `grid.rs` unit tests rewritten for the new semantics
(diagonal is *not* adjacent; same tile and compass neighbors are; Manhattan
arithmetic). (2) `action.rs` validation tests gain the diagonal-refusal
cases: Eat/Drink/Play-at-element proposed from a diagonal resolve to Idle
(FR-002). (3) `needs_driven.rs` gains the walk-around test: a kitty diagonal
to its bowl steps to an orthogonal neighbor and eats next tick, never stalls
(FR-004). (4) `world.rs` pursuit tests gain the diagonal→orthogonal
progress case (R4). (5) `welfare_longrun.rs` gains a per-tick assertion that
every kitty in an eating/drinking scene has its element within Manhattan 1 —
SC-001's "zero diagonal interactions" enforced over tens of thousands of
randomized ticks, riding the suite that already replays hostile behaviors.
(6) Existing behavior tests re-derived where positions were diagonal by
construction. Rust suite + clippy + fmt green before merge (standing CI
gate); no client tests affected.

**Rationale**: R8 of 008 said it: the automatable core is the derivation
logic. Here the derivation logic *is* the feature, so the property suite is
the star witness — SC-001/SC-002 map one-to-one onto (5).

**Alternatives considered**: a standalone integration test crate for
adjacency (the welfare long-run already drives randomized worlds — a new
harness would duplicate its machinery to watch the same ticks).

## R8 — Scope guard: what deliberately does not change

**Decision**: recorded as non-goals, verified by `git diff` at review time:
`spawn.rs` (spread sampling keeps Chebyshev — spacing aesthetics, spec
Assumptions), `Direction`/`Position::step`/movement validation (already
4-way), the client (`client/` untouched, FR-009), all config files (R5), the
server crate, and the API schema. `chebyshev_distance` itself stays in
`grid.rs` with a doc comment naming spawn spread as its remaining consumer.

**Rationale**: SC-005/FR-009, and the 008 SC-007 habit — a clean
"nothing else moved" diff is itself a review artifact.

**Alternatives considered**: deleting `chebyshev_distance` and inlining a
local copy in `spawn.rs` (hides a legitimate geometric tool; a doc comment
scopes it just as well without churn).
