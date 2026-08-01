# Contract: welfare ↔ validation equivalence

**The law being guarded**: for every need kind and every world, the
welfare layer's `zero_distance_relief_exists(world, kitty, kind)` must
agree with "at least one lawful action relieving `kind` validates for
that kitty" (`cloudkitty_core::action::validate`, public API). The
engine is authoritative; the metric must never imagine relief the engine
would refuse, nor deny relief the engine would grant.

## Fixture matrix

| Axis | Values |
|---|---|
| Need kind | Eat, Drink, Sleep, Play, Cuddle, Bath (all six) |
| Neighbor | adjacent + free · adjacent + busy (mid-duet) · absent |
| Relief element | present adjacent · absent · present-but-consumed (chow: zero servings) |

Impossible combinations are skipped explicitly (the matrix constructor
documents each skip). Relieving-action sets come from the public
spec-019 relief mapping; worlds are built with public constructors only
— the measuring layer must not import behavior-layer knowledge
(`mask_oracle.rs` precedent: engine as oracle, no carve-outs).

## Known reconciliations (this batch)

- **Eat**: predicate tightened to adjacent **stocked** chow, matching
  `validate`'s `adjacent_stocked_chow`. Pre-batch, an empty adjacent
  bowl counted as zero-distance relief while `Eat` was illegal — the
  divergence class this guardrail exists to catch, found during
  planning. Pinned-streak accounting inherits the honest predicate.
- **Cuddle**: busy neighbors ARE lawful relief (adjacency suffices —
  `docs/cuddle-relief-semantics.md`, the spec 021 lesson); the matrix's
  adjacent-busy column asserts *agreement on true*, pinning the doctrine
  against regression in either layer.

## Perturbation check (SC-005, development-time)

During development, each side is deliberately perturbed once (predicate
loosened / validate arm carve-out) to demonstrate the test goes red in
both directions; the perturbations are then removed. The shipped test
asserts agreement only.
