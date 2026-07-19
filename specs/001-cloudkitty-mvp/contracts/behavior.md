# Contract: Behavior Interface

**Feature**: CloudKitty MVP | **Date**: 2026-07-18
**Crate**: `cloudkitty-core::behavior`

The pluggable-behavior boundary (Article IV: behaviors are untrusted advisors; the
engine is the law). This contract must survive unchanged when external behaviors
(script / HTTP / local service) are added post-MVP (FR-029).

## Trait

```rust
#[async_trait]
pub trait Behavior: Send + Sync {
    async fn decide(&self, ctx: &DecisionContext) -> Action;
    /// Built-ins return true; external implementations return false.
    /// Governs wall-clock timeout exemption (spec clarification 2026-07-18).
    fn is_builtin(&self) -> bool { false }
}
```

- `decide` receives a **read-only** context and returns exactly one proposed
  `Action`. It must not (and cannot — no mutable access) alter the world.
- The async signature is the external-extension point; built-ins return
  immediately without awaiting.

## DecisionContext (input)

| Field | Contents |
|-------|----------|
| `me` | the deciding kitty's full state (needs, happiness, position, activity, cooldowns) |
| `world` | start-of-tick snapshot: all kitty positions/states, all elements **including greebles**, recent meows (last 10 ticks) |
| `rng` | a per-kitty RNG stream derived from the master RNG in stable kitty-id order **before** any decision runs — the only permitted randomness source |
| `constants` | relevant configured constants (thresholds, effect magnitudes) |

All kitties in a tick receive contexts built from the **same** snapshot; decisions
cannot observe each other's outcomes within the tick.

Feature 004 additions: `me` now also carries engine-authored `pursuit`,
`abandoned_chases`, `last_relief` and `distress_since`, and `Play`'s target is
optional (no target = solo play, always legal). See the
[004 behavior delta](../../004-fix-happiness-lockin/contracts/behavior-delta.md).

## Engine obligations (the law)

1. **Concurrent gather**: all `decide` futures run concurrently against the same
   snapshot (`join_all`).
2. **Time budget** — external behaviors only: each external `decide` is wrapped in
   `tokio::time::timeout` with budget = `behavior.budget_fraction_of_tick ×
   tick_ms` (default 0.5 × 800 ms = 400 ms; config validation guarantees budget <
   tick). Built-ins (`is_builtin() == true`) are exempt and run to completion
   synchronously — this keeps Article V determinism unconditional.
3. **Fallback chain**: timeout, panic, or error in `decide` → the engine substitutes
   the `NeedsDriven` decision for that kitty this tick. (`NeedsDriven` itself cannot
   fail: it is total over all context states.)
4. **Validation**: every returned proposal — from any behavior — is validated
   against the rules and current world state before application. Invalid or illegal
   proposals resolve to `Idle`. Never an error state, never a rule violation, never
   a kitty harmed by its advisor.
5. **Isolation**: a slow/failed behavior affects only its own kitty's decision that
   tick; the tick loop cadence is never delayed beyond the budget by any behavior.

## Shipped implementations

| Name (config string) | Type | Contract |
|----------------------|------|----------|
| `needs_driven` | built-in, fallback | picks an action addressing the highest-pressure need (move-toward resource, then consume/perform), with mild RNG-based tie-breaking/randomness; total (always returns a valid-shaped action); deterministic given ctx |
| `playful` | built-in | over-weights Play/Chase: prefers chasing/playing with bugs, greebles, friends even when other needs are higher, reverting to needs-driven choices at extreme need pressure; deterministic given ctx |

Test-only implementations (dev): `always_invalid` (adversarial — proposes illegal
actions every tick), `chaos` (random possibly-illegal actions from ctx.rng),
`sleepy_slow` (delays past budget; exercises the timeout path).

## Registry

Behavior names resolve via a registry map `&str → Arc<dyn Behavior>` at world
construction; unknown behavior names in config are a startup validation error
(FR-007). Adding a future external behavior = registering one new implementation;
no engine changes (FR-029 acceptance).

## Contract tests

1. Proposal-only: a behavior returning any `Action` never mutates world state
   directly (type-level guarantee; asserted by API shape).
2. Invalid proposal → applied action is `Idle`; world remains invariant-clean.
3. `sleepy_slow` external behavior times out → kitty acts on `NeedsDriven`'s
   decision; tick duration unaffected (within tolerance).
4. Panicking behavior → same fallback, no crash, no missing turn.
5. Same seed ⇒ identical decisions from built-ins across runs and across
   save/restore (determinism).
