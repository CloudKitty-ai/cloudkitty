# Contract: the chase sidestep

Applies to the Chase apply arm only (`action::apply`, the stall branch).
Validation of Chase proposals is unchanged (target-existence only).

## Step law

```
dest = straight step toward target (Direction::toward)
if dest is lawful (in-bounds, kitty-free):   move there        # unchanged
else:
    closing = lawful steps (excluding dir and its reverse) with
              Manhattan(target) < current      # the other axis, diagonal case
    arcing  = lawful steps (excluding dir and its reverse) otherwise
              # perpendicular, +1 -- the axis-aligned lane case
    pool = closing if non-empty, else arcing
    if pool non-empty:  move to a uniform master-RNG choice from pool
    else:               stall in place                          # unchanged
```

*(Amended during implementation: the first-draft rule "Manhattan ≤
current" had an empty pool in exactly the headline case — a blocker
squarely in an axis-aligned lane, where both perpendicular steps are +1.
Routing around a lane-blocker necessarily arcs before it passes; the
behavior-side FR-008 sidestep fires on non-closing steps for the same
reason. The reverse direction is never a candidate: arcing is routing,
walking backwards is retreat.)*

## Guarantees

- **Deterministic**: the draw comes from the seeded master world RNG at
  apply time, in the tick's fair apply order (the spec 022
  deliberate-purr pattern). Same seed → same sidesteps, always.
- **Never synchronized**: two blocked kitties draw successive stream
  values — no shared computable pick, the livelock family's root cause
  (`behavior/mod.rs` note). Spec FR-006's guarantee, delivered
  engine-side (spec amendment recorded in research R5).
- **Draw shape**: a draw occurs iff (blocked ∧ pool non-empty) — a
  world-state condition. No config key changes draw shape (the
  fixed-shape rule constrains config, not state).
- **Never reverses**: the opposite of the chase direction is never a
  candidate; closing steps are preferred, and a perpendicular arc (+1
  Manhattan) is taken only when nothing closes. A fully boxed-in chase
  stalls exactly as today and the patience clock
  (`chase_patience_ticks`, staleness from last *progress*) governs
  unchanged — an arcing chase that never re-closes is still abandoned
  on schedule.
- **Preference-free**: the engine expresses no dry-tile preference — a
  sidestep through water is lawful and pays the wet-fur occupancy charge.
  Water preferences remain behavior style (Article IV doctrine).

## Bookkeeping interaction

`update_pursuit` is unchanged. A perpendicular sidestep does not improve
Manhattan distance, so it does not reset the patience clock — a chase
that only ever sidesteps still gets abandoned on schedule. Expectations
tied to stall-fed abandonment statistics are re-baselined in this batch,
documented (spec FR-007).
