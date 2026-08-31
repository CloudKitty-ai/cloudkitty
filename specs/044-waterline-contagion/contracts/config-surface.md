# Contract: the `[water] contagion_factor` config surface (spec 044)

## TOML surface

```toml
[water]
bath_gain = 3.5          # existing
bath_gain_ceiling = 60.0 # existing
contagion_factor = 0.0   # NEW — 0.0/absent = off (launch state); 1.0 = Gen 1 ruling
```

- Absent and `0.0` are indistinguishable everywhere: behavior, stamp,
  serialized output (identity-skip).
- `deny_unknown_fields` on `WaterConfig` continues to reject typos.

## Acceptance / rejection matrix (validate_water)

| Config | Verdict |
|---|---|
| factor absent or 0.0, any previously-valid `[water]` | accept (bit-identical to the old check) |
| factor 1.0, previously-valid `[water]` | accept (budget unchanged: `max(1, 1.0) = 1`) |
| factor f > 1.0 with `ceiling + f × gain × max_ratio < safeguard` | accept |
| factor f > 1.0 with `ceiling + f × gain × max_ratio ≥ safeguard` | reject — error names the keys and remedies (lower factor/gain/ceiling, or the cat's bath rise) |
| factor negative or non-finite (even with `bath_gain = 0`) | reject |

## Behavioral contract (engine, factor > 0)

Per tick, for each kitty K with bath below `bath_gain_ceiling`
(pre-charge):

- K on a water tile → occupancy charge `bath_gain × bath_ratio(K)`
  (unchanged).
- K NOT on water, and K's **own** activity is Resting/Sleeping with a
  friend, Playing with a kitty, or Grooming a kitty, and that named
  partner IS on a water tile → contagion charge
  `contagion_factor × bath_gain × bath_ratio(K)`.
- Otherwise → no water charge. In particular: a cat merely *referenced*
  by someone else's activity pays nothing (Option A); a wet cat never
  pays contagion; critter play never prices.

Stability promises: no legality/mask/refusal change; no RNG; no new
persisted state; per-tick worst case unchanged for factor ≤ 1.0.
