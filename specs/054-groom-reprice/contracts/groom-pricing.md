# Contract: Groom-other pricing surface (spec 054)

The operator-visible contract of the reprice. Anything here is a breaking
change if moved later; everything else is implementation.

## The curve

```
x    = min(target_bath_before, groom_relief) / groom_relief      # ∈ [0,1]
c(x) = min(groom_cuddle_ceiling,
           groom_cuddle_floor + groom_cuddle_slope · x)
```

- Paid to the **groomer only**, as Cuddle relief, per serviced groomed
  tick of kitty-directed grooming. The **groomee's** bath relief is
  untouched by this spec. Solo grooming pays no cuddle relief (unchanged).
- Defaults `0.25 / 3.5 / 2.0`: exact floor at the drip-rest anchor tier,
  exact saturation 2.0 from x = 0.5. Guaranteed properties: strictly
  monotone below saturation; never negative; never above ceiling;
  evaluated in plain add/mul/min arithmetic (deterministic on every
  platform, replicable as one line of numpy).

## Configuration (`[actions]`)

| Key | Default | Notes |
|---|---|---|
| `groom_cuddle_floor` | `0.25` | 0 ≤ floor ≤ ceiling |
| `groom_cuddle_slope` | `3.5` | ≥ 0 |
| `groom_cuddle_ceiling` | `2.0` | ≥ floor |
| `groom_cuddle_relief` | *(legacy)* | Accepted and ignored — existing configs keep loading; not served, not stamped, not a key setting |

Validation failures are startup config errors, same class as every relief
dial (finite, non-negative, plus the two ordering rules above).

## Served surfaces (declared one-time delta)

- `GET /config`: loses `groom_cuddle_relief`, gains the three dial keys.
- `engine_defaults_sha256`: moves once, by exactly the serialized-defaults
  delta above.
- `GET /settings` + boot block + update.sh section (spec 052): the flat
  entry is replaced by three entries, each value + default + source.
- Observation/reward schema: **no change** (schema 5, 408 floats).

## Behavioral contract for the scripted brain

The built-in groom-response path values a prospective groom scene's
groomer side at `c(emitter's current bath)` — the actual first-tick pay —
in its contagion-exposure decline comparison (spec 045 seam 3). Gate-off
worlds (contagion inert, the Gen 1 posture) are unaffected: exposure is
zero before any arithmetic.

## Compatibility

- Frozen `evals/v2/*` and current `evals/v3/*` load **byte-unchanged**
  (legacy key accepted-ignored); their worlds run under the new pricing,
  as any engine-behavior change at a generation boundary implies.
- `cloudkitty.toml` / `training.toml` ship scrubbed of the legacy key and
  pin none of the new dials (engine defaults serve).
- Landing rule: merged only at the Gen 1 reseat sitting; never deployed to
  a world whose roster was trained under the flat price (FR-013).
