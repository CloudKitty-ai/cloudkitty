# Data Model: Refusal Stamp (spec 046)

## RefusalEvent (new, `crates/cloudkitty-core/src/events.rs`)

| Field      | Type      | Meaning                                                        |
|------------|-----------|----------------------------------------------------------------|
| `kitty_id` | `KittyId` | The kitty whose proposal was refused                           |
| `proposed` | `Action`  | The proposal verbatim — `with`/`target` included when named    |
| `tick`     | `u64`     | The tick the refusal was heard                                 |
| `absorbed` | `bool`    | `false` = the turn resolved Idle (taxed tick, the F-033 count); `true` = duration enforcement continued a scene (refusal heard, nothing lost). Always serialized — no skip-at-false (research R5) |

- Derives `Debug, Clone, PartialEq, Serialize, Deserialize` (+ `Copy` if
  `Action: Copy` holds — verify at implementation).
- Emitted iff `proposal != Action::Idle && validate(...) == Action::Idle`
  (FR-001), recorded after `enforce_durations` with
  `absorbed = (enforced != Action::Idle)` (research R1). Never for
  chosen Idle, duration overrides of *legal* proposals, or message
  downgrades.
- Within a tick, events append in turn order.

## RefusalLog (new alias)

`pub type RefusalLog = EventLog<RefusalEvent>;` — the existing bounded
ring (newest kept, oldest dropped, capacity floor 1).

### EventLog::set_capacity (new method)

`set_capacity(&mut self, capacity: usize)` — re-stamps capacity
(`.max(1)` floor like `new`), trimming oldest-first if the ring holds
more than the new capacity. Used by the persist load path (research R3).

## World (modified, `world.rs`)

| Field         | Change                                                            |
|---------------|-------------------------------------------------------------------|
| `refusal_log` | new: `pub refusal_log: RefusalLog`, `#[serde(default)]` on read — pre-046 saves load with an empty capacity-0 ring (degrades to one) which the server load path immediately re-stamps from config |

- `World::generate`: `refusal_log: RefusalLog::new(config.events.refusal_retention)`.
- Struct-literal sites (tests, `world.rs:163` default block): add the
  field; compile errors enumerate them (E0063, the 045 experience).

## EventsConfig (modified, `config/mod.rs`)

| Field               | Change                                                                 |
|---------------------|------------------------------------------------------------------------|
| `refusal_retention` | new `usize`; `#[serde(default = "default_refusal_retention", skip_serializing_if = "is_default_refusal_retention")]`; default **4000** |

- Validation: `validate_events` gains the row
  `("[events] refusal_retention", self.events.refusal_retention)` —
  rejected at 0 with the spec 020 D2 shape (US2-3).
- Stamp guard: `refusal_retention` joins
  `roam_cell_stays_out_of_the_default_serialization` (a dropped skip
  attribute reddens).
- `Default for EventsConfig` gains the field; `Copy` retained.

## Server state (modified, `cloudkitty-server`)

| Surface       | Change                                                                  |
|---------------|--------------------------------------------------------------------------|
| `sim_task.rs` | snapshot state gains `refusals: Arc<Vec<RefusalEvent>>` from `world.refusal_log.to_vec()` (sibling of `activity_ends`) |
| `api.rs`      | `get_refusals` handler, sibling of `get_activity_ends`                   |
| `lib.rs`      | `.route("/events/refusal", get(api::get_refusals))`                      |
| `persist.rs`  | after fingerprint check: `world.refusal_log.set_capacity(config.events.refusal_retention)` |

## Invariants

- The ring never exceeds its capacity; capacity ≥ 1 always.
- No engine read of `refusal_log` exists outside recording and serving
  (Article I: signal, never punishment — same clause as the distress
  ring's header comment).
- `WorldSnapshot` is untouched: no ring fields today, none added.
