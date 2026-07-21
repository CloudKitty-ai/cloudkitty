# Research: Approach Etiquette

**Date**: 2026-07-20 | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

Grounded in the verified reproduction (period-2 corner orbit, 145 ticks with
the meow lottery silenced) and its root cause: simultaneous decisions against
the same snapshot re-diagonalize a mutually-approaching pair forever under
009's orthogonal range. Five decisions.

## R1 — Break symmetry with identity and parity, not randomness

**Decision**: the higher-id kitty of the pair yields, and only on even world
ticks. Rationale: id order is the codebase's universal deterministic
tie-break; parity guarantees progress against a passive partner (a yield can
never repeat two ticks running), bounding the cost at one tick. RNG was
rejected: it is the current *accidental* mechanism (urgent-meow lottery) and
is exactly what makes the dance visible today.

## R2 — The yield *is* a meow, and the meow is a new word

**Decision**: the held turn is spent proposing `Meow { WaitForMe }` — the
owner's design. A dedicated kind (rather than the need meow originally
floated) is immune to need-meow cooldowns: nothing else ever spends it, so
the bubble is essentially always available at the moment it matters; and
when a rapid second dance does catch its base cooldown, the turn is still
spent standing (FR-003) — audibility is charm, stillness is the mechanism.
`related_need` is `None` (base cooldown class, like FollowMe): urgency
should not shorten a word whose whole meaning is patience.

## R3 — Guard the two kitty-approach paths, through one helper

**Decision**: a shared `should_wait_for(ctx, friend_id, friend_pos) -> bool`
in `selection.rs`, consulted by the cuddle arm (`needs_driven::pursue`)
before `step_toward`, and by `play_action_with` before returning
`Chase(kitty)`. These are the only two paths where a kitty walks at a kitty;
grooming and co-sleeping have no walk. One helper, no drift.

## R4 — Trigger at exactly Manhattan 2

**Decision**: the guard fires only at distance exactly 2 — the verified
orbit's radius, and the only distance where simultaneous steps can swap a
pair around a corner forever. Farther out, mutual approaches shrink distance
by two per tick and cannot cycle; at 1 the interaction fires. Wider triggers
would tax every approach for no failure mode.

## R5 — Verification

**Decision**: (1) vocabulary units in meow.rs (ALL of 7, wire name, text,
base cooldown class). (2) yield-guard units: higher id at d2 even tick →
WaitForMe; odd tick → step; lower id → step; d≠2 → untouched. (3) a new
`tests/approach_etiquette.rs` pinning the reproduction: mutual cuddle pair
resolves ≤ 6 ticks with a WaitForMe recorded, identical with need meows on
cooldown, and a mutual play-chase variant; plus the passive-partner bound.
(4) full workspace suite. Alternatives: folding the regression into
welfare_longrun.rs (kept separate — this is a behavior contract, not a
welfare bound).
