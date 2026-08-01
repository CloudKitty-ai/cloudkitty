# Contract: the `[water]` section

```toml
[water]
bath_gain = 1.5           # bath need per occupied tick, before trait scaling; 0 disables
bath_gain_ceiling = 50.0  # pre-charge bath at/above which the charge stops
```

## Charge law (engine, needs phase)

Each tick, for each kitty standing on a water tile, **after** ambient
need accrual and **before** the same-tick happiness recompute:

```
if bath(pre-charge) < bath_gain_ceiling:
    bath += bath_gain × need_rate_for(kitty, Bath) / needs.bath
```

- Gate is on the **pre-charge** value → bounded overshoot of at most one
  scaled charge, budgeted by the validation invariant.
- The divisor is the loaded config's global `[needs] bath` — the ratio is
  1.0 for a kitty without an override, and equals the BACKLOG's
  `bath_rise / 0.2` framing at shipped defaults.
- Movement, action legality, drinking (adjacency), and every other need
  are untouched. No RNG is drawn. `Need::add` clamps to [0, 100].

## Validation contract

Rejected at load, with the field named:

| Condition | Error field |
|---|---|
| `bath_gain` non-finite, < 0, or > 100 | `[water] bath_gain` |
| `bath_gain_ceiling` non-finite or outside [0, 100] | `[water] bath_gain_ceiling` |
| `ceiling + gain × max_roster_ratio ≥ thresholds.safeguard` | `[water] bath_gain_ceiling` (message shows the arithmetic and the offending kitty) |
| `needs.bath == 0` while `bath_gain > 0` | `[needs] bath` |

`validate_water` appends to the spec-contract validation order (spec 020
FR-004); the order-guard fixture is updated in the same change.

## Compatibility guarantees

- Absent `[water]` section → defaults (old configs parse unchanged).
- Frozen exam configs remain byte-identical and valid (no
  `deny_unknown_fields` on `Config`; hash pins untouched).
- Config fingerprint unchanged → pre-batch snapshots keep loading.
- `engine_defaults_sha256` **moves** — the designed, visible mark of the
  batch's one comparability break.
