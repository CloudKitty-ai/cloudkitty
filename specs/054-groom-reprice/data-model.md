# Data Model: Groom-other reprice (spec 054)

No new entities, no persistence, no schema change. The model is three
config dials, one derived quantity, and one legacy field.

## Config dials (`[actions]`, `ActionEffects`)

| Field | Default | Validation | Meaning |
|---|---|---|---|
| `groom_cuddle_floor` | `0.25` | finite, ≥ 0, ≤ ceiling | Cuddle pay/tick at zero delivered relief — the charm tier, calibrated to `rest_drip_relief` at anchor |
| `groom_cuddle_slope` | `3.5` | finite, ≥ 0 | Pay gained per unit of delivered fraction (monotonicity: ≥ 0 keeps "dirtier pays more") |
| `groom_cuddle_ceiling` | `2.0` | finite, ≥ floor | Saturation pay/tick; with defaults, reached exactly at x = 0.5 |
| `groom_cuddle_relief` *(legacy)* | `0.0` (unused) | none (ignored) | Recognised so `deny_unknown_fields` holds on existing configs; `skip_serializing`; read by no code |

State transitions: none (dials are load-time constants; no runtime
mutation surface).

## Derived quantities (per groomed tick, kitty-directed grooming only)

- **delivered**: `min(target_bath_before_tick, groom_relief)` — the bath
  relief the target actually receives this tick. Bounds: `[0,
  groom_relief]`.
- **x** (delivered fraction): `delivered / groom_relief`. Bounds: `[0, 1]`
  by construction (no out-of-range behavior needed).
- **pay**: `c(x) = min(ceiling, floor + slope · x)` — the groomer's cuddle
  relief this tick, applied through the existing `lower_need` path
  (bounded needs, `last_relief` stamped).

Invariants (test-pinned):

1. `c` strictly increasing on x ∈ [0, x_sat), constant at ceiling after
   (`x_sat = (ceiling − floor)/slope`, 0.5 at defaults).
2. `c(0) = floor` exactly; floor = drip tier at anchor values.
3. `c(x) ≤ ceiling` always; ceiling per party per tick = ¼ of
   `rest_mutual_relief`-per-party at anchor (rule 2 dominance).
4. Evaluation uses add/mul/min only (FR-002a) — bit-identical across
   platforms.
5. Cumulative above-floor pay over a scene ≤ what the opening dirt can
   deliver (per-tick delivered cap, FR-006).

## Relationships

- One curve definition: `ActionEffects::groom_cuddle_pay(delivered_bath)`.
- Readers: `apply_activity_effects` (Grooming{Some} arm, pays) and
  `needs_driven` groom-response seam (prices expected first-tick pay at
  the emitter's current bath). No third reader may appear without reading
  the same function (FR-008).
- Solo grooming (`Grooming { None }`): outside the model — no cuddle pay,
  unchanged.
