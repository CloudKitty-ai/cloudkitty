# Contract: Water Step Cost

**Date**: 2026-07-20 | **Spec**: [spec.md](../spec.md) | **Plan**: [plan.md](../plan.md)

## Configuration contract

```toml
[behavior]
# Extra tiles of effort a kitty ascribes to stepping onto water. Dry routes
# win when they cost less than the splash; a kitty still wades when water is
# the only way forward -- preference, never prohibition (spec 010).
water_step_cost = 4.0
```

- **Absent key**: default 4.0 applies; every pre-010 config file starts
  unmodified (SC-005).
- **Invalid value** (negative, NaN, ±∞): startup rejection in the standard
  voice, e.g. `config error: [behavior] water_step_cost is -1; must be a
  finite number >= 0`.
- **Zero**: legal; disables the preference entirely (behaves exactly like
  pre-010).

## Behavioral contract

| Situation | Guaranteed outcome |
|-----------|-------------------|
| Dry and wet steps both close distance | the dry step is taken (cost ordering; ties by direction order) |
| Only a wet step closes distance | the kitty wades — crossing is never refused by the preference |
| Nothing closes distance, kitty not beside target | sidestep fallback prefers a dry free tile over a wet one |
| Kitty standing on water | dry options win at equal progress; the kitty gets out |
| Choosing among same-type targets | minimum `(priced travel, id)` — a bowl across a pond competes at its true detour price, and the chosen target is the one walked to |
| A need's only relief lies across water | still selected and still pursued — pricing reorders, never removes |

## What does not change

`Move` validation (terrain-blind, Article IV), chase stepping, spawn
placement, snapshot schema, every API payload, the client. The swim pose
remains a separate backlog item.

## Determinism contract

Same seed + config + ticks → same world (Article V). The preference adds no
randomness; all orderings remain total and deterministic.
