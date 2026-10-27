# Data Model: Welfare-Hazard Acknowledgement Guard

## Config entities

### WelfareHazardConfig (the `[welfare_hazard]` table)

| Field | Type | TOML spelling | Rules |
|-------|------|---------------|-------|
| `acknowledged` | `Vec<String>` | `acknowledged = ["initial_needs"]` | Required inside the table; each name must be a registered mode; no duplicates; the set must equal the active set exactly |

- `deny_unknown_fields`.
- `Config.welfare_hazard: Option<WelfareHazardConfig>`,
  `#[serde(default, skip_serializing_if = "Option::is_none")]`:
  absent → not serialized (stamp and `GET /config` unmoved); present →
  serialized, empty list included.
- Not read by `Config::fingerprint()`.

### HazardMode (the registry, engine-side, closed)

| Variant | `name()` | Active when | Activating site text |
|---------|----------|-------------|----------------------|
| `InitialNeeds` | `initial_needs` | Any governing initial-need setting (roster-wide table or any per-kitty override, any need) is a value > 0 or a range with max > 0 | The first such setting, in `validate_initial_needs` order: `[initial_needs].<need> = <v>` or `[[kitty]] '<name>' (id <id>) initial_needs.<need> = <v>` |

- `HazardMode::ALL` is the iteration order for the validator, the
  sweeps and the boot line.
- `Config::active_hazards() -> Vec<(HazardMode, String)>` — the modes
  active in this config with their activating site; empty for every
  pre-feature config and for a distressed-start section with every need
  at zero.
- No teacher-eligibility field (owner ruling; the needy-preset spec adds
  it with its first reader).

## Validation (one call in `Config::validate`, after `validate_initial_needs`)

Inputs: `acknowledged` (absent → empty, with `absent` remembered for
the error's value), `active` from the registry, `known` = every
`HazardMode::ALL` name.

| Shape | Condition | Error names |
|-------|-----------|-------------|
| unknown | a name not in `known` | the name |
| duplicate | a name listed twice | the name |
| missing (incl. partial) | an active mode not in `acknowledged` | every missing mode, its activating site, and the exact line to add |
| stale | an acknowledged mode not active | every stale name |
| exact / nothing-to-acknowledge | sets equal (both possibly empty) | — (Ok) |

Checked in that order; the first failing shape is the error. All
errors are `ConfigError::Invalid { field: "[welfare_hazard]
acknowledged", value, expected }`.

## Server entities

### Start-up intent switch

`--allow-welfare-hazard`, bare, parsed into `Args.allow_welfare_hazard:
bool`; documented in HELP. Accepted and inert on a config with no
acknowledged mode.

### Gate

`welfare_hazard::gate(config, allowed) -> Result<()>`: Err iff
`config.welfare_hazard` names ≥ 1 mode and `!allowed`; the message
names the modes and the switch. Runs after `validate`, before any
registry, snapshot or world.

### Key-settings row (spec 052 block)

| group | key | value | default | source | present when |
|-------|-----|-------|---------|--------|--------------|
| `welfare_hazard` | `acknowledged` | JSON array of the acknowledged names | none | `toml` | the list is non-empty |

Position: last entry. Text rendering:
`welfare_hazard.acknowledged = ["initial_needs"] [toml]`.

## State transitions

None: the feature adds no runtime state. A world is created or resumed
exactly as before once the config has loaded and the gate has passed.

## Migration data

Seven files, each: original bytes unchanged + `\n[welfare_hazard]\n
acknowledged = ["initial_needs"]\n`. Pre-retrofit sha256s: Experiments'
`experiments/gen2-deviations.md` entry 14. Post-retrofit sha256s:
Experiments record after landing.
