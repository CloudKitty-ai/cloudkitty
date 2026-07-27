# Research: Need→Relief Mapping (spec 019)

All unknowns from Technical Context resolved. Line references are to main
at `c6fbeae` (post-018 merge), this feature's pre-refactor baseline.

## D1 — Centralize the pairing as a shape enum, not the logic

**Decision**: one crate-internal enum in `behavior/relief.rs`:

- `Element { kind: ElementType, use_it: Action }` — Eat→Chow→`Eat`,
  Drink→Water→`Drink`
- `Sunbeam` — Sleep (terrain, priced through `sunbeam_worth_walking`)
- `Playmate` — Play (deliberately unpriced, targeting owned by `selection`)
- `Friend` — Cuddle (nearest-free-friend, conscription etiquette)
- `InPlace { use_it: Action }` — Bath→`Groom { target: None }`

plus one authoritative `impl NeedKind { pub(crate) fn relief(self) ->
ReliefSource }` — exhaustive over `NeedKind`, so a new need without a
correspondence fails the build (FR-003).

**Rationale**: the survey's mirror is precisely the *pairing*, not the
per-shape logic. The three consumers agree on which resource/action a
need maps to but legitimately differ in what they do with it (pricing vs
walking vs adjacent-grabbing) and per shape (adjacency for elements,
standing-on for sunbeams, conscription rules for friends). Centralizing
the pairing and letting consumers match on the five shapes moves exactly
the drift-prone knowledge (spec: "moves knowledge, not logic") — and it
makes the spec's SC-005 walkthrough literal: a new need reusing an
existing shape is one `relief()` arm, with every consumer's handling
arriving through the already-written shape arm.

**Alternatives considered**: (a) a single mega-function returning
closures/behavior per need — rejected: flattens the genuine differences
the spec's edge case forbids flattening, and would have to thread
`DecisionContext` through the definition; (b) per-need method trio
(`relief_element()`, `relief_action()`, …) — rejected: three partial
functions re-create the mirror as three lists; (c) extending the engine's
`Activity::governing_need` (kitty.rs) into a bidirectional map — rejected:
that mapping is engine law about activities in progress, this one is
advisor policy about what to seek; coupling them crosses the
Article IV layer boundary the spec scopes away.

## D2 — Where the definition lives: `behavior/relief.rs`, inherent impl

**Decision**: new ~70-line `behavior/relief.rs` holding `ReliefSource`
and the `impl NeedKind` block; module registered crate-internal
(`mod relief;` — nothing outside the crate sees it).

**Rationale**: Rust permits inherent impls in any module of the defining
crate, so the method can live on `NeedKind` (the house pattern — the
spec names kitty.rs's centralized `Activity` mappings) while the file
sits in the behavior layer where the policy belongs. Putting it in
`needs.rs` (the data layer) would leak advisor policy into the engine's
core types; putting it in `selection.rs` would bury a definition meant
to be findable in a 991-line scoring file. The clarify pass flagged this
exact choice as plan-level; this resolves it.

**Alternatives considered**: `needs.rs` (wrong layer, above);
`selection.rs` top (findability); an extension trait (indirection with
no benefit inside one crate).

## D3 — The emergency ladder becomes an explicit ordered constant

**Decision**: `take_what_is_here`'s hardcoded sequence (Eat, Drink,
Sleep, Play — needs_driven.rs:97–127) is rewritten as iteration over
`const OPPORTUNISM_LADDER: [NeedKind; 4]` declared beside it, each need
consulting `relief()` and matching shapes: `Element` → adjacency check →
`use_it`; `Sunbeam` → standing-on check → `Sleep { with: None }`;
`Playmate` → `adjacent_playmate` → `play_with`; `Friend`/`InPlace` →
skip (not opportunistic today, exactly as now — Cuddle and Bath do not
appear in the current ladder).

**Rationale**: the order is load-bearing ("the emergency ladder: food
and water first…" — the comment moves onto the constant) and the
evaluation order of threshold checks is observable behavior (spec edge
case 3). An explicit ordered constant preserves it bit-for-bit while
removing the three same-shaped per-need blocks the survey flagged. The
`worth_a_detour` threshold comparison stays exactly one per rung, same
order, same predicates.

**Alternatives considered**: keeping four literal blocks but sourcing
element kinds from `relief()` — rejected: leaves the repeated shape the
survey flagged; iterating `NeedKind::ALL` filtered by shape — rejected:
changes the ladder's order authority from explicit to derived, and ALL's
order (needs.rs) is not the ladder's order.

## D4 — Consumer rewrites preserve every predicate and tie-break verbatim

**Decision**: `distance_given` (selection.rs:109–131) and `pursue`
(needs_driven.rs:135–192) become shape matches whose arm bodies are the
*current* bodies, moved untouched: pricing arms keep
`priced_nearest_element`/`sleep_travel_distance`/`play_travel_distance`/
`nearest_friend`+`priced_travel`/`Some(0.0)`; pursuit arms keep
`seek_element`, the sleep arm's standing-on short-circuit +
`sunbeam_worth_walking` fallback, `play_action_with`, the cuddle arm's
free-friend filter + `(manhattan, id)` min + etiquette + idle fallback,
and `Groom { target: None }`. The existing shared helpers
(`sunbeam_worth_walking`, `priced_nearest_element`,
`adjacent_playmate`, `play_action_with`) remain the single homes of
their logic — this feature adds no second copy of anything.

**Rationale**: FR-004's bit-identical bar plus the spec's
"knowledge, not logic" boundary. The mirror comments retire per FR-007:
"the mirror the 004 review demanded" (selection.rs:179–180) and
"Mirrors `pursue`'s sleep arm exactly" (selection.rs:188–190) are
replaced by documentation at the `relief()` definition stating the
invariant now held structurally — the score/walk agreement *within* a
shape continues to rest on the shared helpers, which the new docs also
name.

**Alternatives considered**: none — any arm-body change would breach
FR-004.

## D5 — Verification baseline and procedure

**Decision**: pre-refactor binaries build from main at `c6fbeae` (the
018 merge + feature.json repoint; no tag — the byte-comparison needs a
commit, not a release). Bit-identical decisions are verified by the
existing determinism suite and welfare gates (`cargo test --workspace`,
zero assertion changes, FR-005); the eval-instrument recheck (FR-006)
reruns one suite evaluation and one certification run against baseline
outputs, all four comparisons byte-identical — the same four-way
procedure 018 proved out, foreground with generous timeouts. The SC-005
new-need walkthrough is recorded in quickstart (edit-site enumeration
before/after; no need is actually added, FR-008/FR-009 of spec 020 do
not apply here).

**Rationale**: the default cat is the eval suite's counterfactual
anchor; byte-identical reports are the end-to-end proof the measuring
stick didn't move. The 018 procedure is now house practice.

**Alternatives considered**: tagging a v2.3.x baseline — rejected:
tags mark owner-called releases (v2.3 was cut for the arc), and a
commit hash pins the comparison equally well.
