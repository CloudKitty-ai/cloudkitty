# Contract: Interaction Range

**Date**: 2026-07-20 | **Spec**: [spec.md](../spec.md) | **Plan**: [plan.md](../plan.md)

The engine-facing contract for what "in range" means after 009. `validate`
(`action.rs`) is Article IV's entire enforcement surface; this contract states
what it must accept and refuse per action, and what the outside world sees.

## Range rule

A target is **in range** of a kitty iff `manhattan(kitty, target) <= 1`:
the kitty's own tile or one of its four compass neighbors. Diagonal tiles are
out of range for every interaction, with no exceptions.

## Per-action contract

| Proposal | In-range requirement | Out-of-range / invalid result |
|----------|----------------------|-------------------------------|
| `Eat` | a stocked chow bowl in range | Idle |
| `Drink` | a water element in range | Idle |
| `Play { target: element }` | the critter exists **and** is in range | Idle |
| `Play { target: kitty }` | partner conscriptable: in range **and** idle | Idle (apply additionally downgrades a lost partner to solo play, unchanged) |
| `Play { target: none }` (solo) | none — always legal | — |
| `Rest { with }` | partner conscriptable: in range **and** idle | Idle |
| `Sleep { with }` | partner available: in range | Idle |
| `Groom { target }` | partner available: in range | Idle |
| `Chase(target)` | none at proposal time (chasing is walking); the eventual **catch** is a `Play` proposal and takes the `Play` row's range | — |
| `Move`, `Meow`, `Idle`, `Purr` | no range concept — unchanged | unchanged |

Continuation and ending of scenes use the same range rule: the per-tick
counterpart checks (`world.rs`) treat a counterpart that is out of range
exactly like a vanished one, ending the scene gracefully at its minimum-
duration rules. This is also the compatibility path for pre-009 snapshots.

## What the API serves

**No shape change.** Every payload (`/world`, `/kitties`, `/kitties/{id}`,
`/events/*`, `/config`, `/ws`) keeps its exact schema. The contract is
observable only behaviorally: no served world state will ever show a kitty in
an element-targeted scene whose element is diagonal to it (beyond the single
grace tick in which a stranded pre-009 scene is ending).

## Determinism contract

Same seed + same config + same tick count → same world, as always (Article V).
All nearest-target and playmate orderings remain total orders of
`(manhattan distance, [tag,] id)`. No RNG draw is added, removed, or reordered
by this feature.
