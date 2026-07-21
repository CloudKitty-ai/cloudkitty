# Data Model: Approach Etiquette

**Date**: 2026-07-20 | **Spec**: [spec.md](./spec.md)

No new state, no config, no schema change. One vocabulary entry and one rule.

## Vocabulary

| Kind | Wire | Text | Cooldown class | Emitted by |
|------|------|------|----------------|------------|
| `MessageKind::WaitForMe` | `wait_for_me` | "Wait for me!" | base (no related need) | the yield rule only |

## The yield rule (pure function of context)

```text
yield ⇔ target is a fellow kitty
      ∧ manhattan(me, target) == 2
      ∧ my id > target id
      ∧ world tick is even
```

On yield: propose `Meow { WaitForMe }` (turn spent stationary either way).
Otherwise: walk/chase exactly as today.

## Invariants (pinned by tests)

- Mutual approach at distance 2 resolves into the interaction within 2 ticks.
- A yield never repeats on consecutive ticks (parity) — passive-partner cost
  is at most 1 tick.
- "Wait for me!" never occurs outside a yield.
- No RNG; identical seeds replay identically.
