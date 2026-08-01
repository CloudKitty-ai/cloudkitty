# Data Model: Deliberate Purring & the Quiet Motor (spec 022, Phase 1)

## Kitty purr state

| Field | Type | Serde | Meaning |
|---|---|---|---|
| `purring_until` | `Option<u64>` | existing (`default`, skip if `None`) | tick the current purr ends; `Some` = purring (either origin — origin is never stored) |
| `purring_duration` | `Option<u64>` | **new** (`default`, skip if `None`) | the drawn length of the current purr; set at start, consumed at end for the factor cooldown, then cleared. `None` at end-time ⇒ pre-022 snapshot ⇒ treat as `min_ticks` (FR-012 convention) |
| `purr_cooldown_until` | `u64` | existing (`default`) | earliest tick the **motor** may start again; stamped at purr end as `tick + ⌈factor × duration⌉`; never consulted by the deliberate purr (FR-005) |

Notes:
- The pair (`purring_until`, `purring_duration`) is set/cleared together;
  an invariant test asserts they are `Some`/`None` in lockstep after this
  change (legacy snapshots may briefly violate it until the in-flight purr
  ends — the convention covers exactly that window).
- Both fields are additive on the served kitty state (API/client see one
  new optional field; client renders nothing from it — no client change).
- The Purr entry of `meow_cooldowns` is no longer stamped by any purr path
  (FR-008); the map itself is untouched (023's territory).

### State transitions

```text
              earned ∧ motor off cooldown            tick ≥ purring_until
  NotPurring ────────────────────────────► Purring ────────────────────────► NotPurring
      │        (motor: purr phase;            │       stamp motor cooldown
      │         draws duration, announce)     │       = ⌈factor × duration⌉
      │                                       │       (factor drawn here)
      │  earned (deliberate: apply phase;     │
      └─────── draws duration; always ────────┘   deliberate purr while
               announces; ignores cooldown)       Purring: silent no-op
                                                  (turn consumed, no draw)
```

- "earned" (both edges, identical): `happiness > thresholds.purr ∨
  happiness_rose`.
- Unearned deliberate proposal never reaches apply: `validate()` resolves
  it to `Idle` (Article IV); the mask row is off for policy kitties.

## PurrConfig (config `[purr]`)

| Key | Type | Default | Validation row | Notes |
|---|---|---|---|---|
| `min_ticks` | `u64` | **8** (was 6) | ≥ 1, ≤ `max_ticks` (existing rows) | duration draw lower bound, both origins |
| `max_ticks` | `u64` | **13** (was 15) | (paired above) | duration draw upper bound |
| `announce_probability` | `f32` | **0.0** (new) | finite, 0 ≤ p ≤ 1 | spontaneous-start announce chance; drawn once per start regardless of value |
| `cooldown_factor_min` | `f32` | **1.75** (new) | finite, > 0, ≤ max | per-end factor draw lower bound |
| `cooldown_factor_max` | `f32` | **2.75** (new) | finite (paired above) | per-end factor draw upper bound; equal bounds = fixed factor |
| `cooldown_ticks` | `Option<u64>` sentinel | — | **`Some` ⇒ load error** naming the retired key and both replacements | deserialize-only; never serialized; retired (was 30) |

Defaults live in `config/defaults.rs` (the one findable home, spec 020
FR-003); rows in `validate_purr` (config/validate.rs:361).

## Announcement (unchanged shape)

`Meow { kitty_id, kind: MessageKind::Purr, tick }` pushed directly to
`recent_meows` — deliberate starts always; spontaneous starts iff the
announce draw succeeds. Never gated, never stamping (FR-008). `MessageKind`
stays 7 variants; `LEARNED_MEOWS` stays 6; digest layout untouched (FR-014).

## Action row 38 (unchanged encoding, new semantics)

| Property | Value |
|---|---|
| Menu index | 38 (`Meow(Purr)`) — unchanged, no codec bump |
| Wire form | `{"action":"meow","message":"purr"}` — unchanged |
| Legality | earned rule (was: always legal) — the one earned-gated meow row |
| Effect | start purr phase + announce (was: emit-or-swallow message) |
| Turn cost | whole turn, including no-op case — unchanged |
| Legacy `Action::Purr` (`{"action":"purr"}`) | still refused → `Idle` (unchanged; shape B rejected) |

## New RNG primitive

`SeededRng::gen_f32(&mut self) -> f32` in `[0, 1)` — 24-bit mantissa from
`next_u64`, the same recipe as `DecisionRng::gen_f32` (rng.rs:108). Used
only for the factor draw; one call per purr end.
