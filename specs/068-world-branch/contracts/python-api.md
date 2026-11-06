# Contract: Python surface for the World Branch API (spec 068)

The binding is `cloudkitty` (pyo3). Existing methods are unchanged in
signature and output (FR-015). Agent names are `"kitty_N"`; every kitty
argument below accepts the int id or the agent name, as
`decision_request` does.

## ParallelEnv

### `snapshot() -> bytes`

Returns the complete episode state between steps as an opaque byte
string (RNG, next decision seeds, episode position, truncation, reward
baselines, current seed) with its identity (engine commit, config
fingerprint, control map).

- Before the first `reset()`: `ValueError("snapshot(): reset first ...")`.
- Poisoned episode: `RuntimeError` carrying the original panic message.
- Legal after truncation (the snapshot restores truncated).

### `restore(data: bytes) -> (obs, infos)`

Replaces the environment's episode state with the snapshot's and returns
what `reset()` returns: `{agent: observation}` and `{agent: info}` for the
external seats at the restored tick. `infos[agent]["decision_seed"]`
equals the original's at the snapshot tick (FR-004).

- Legal before the first `reset()` (stands in for it) and in every other
  state; heals a poisoned environment; a truncated snapshot restores
  truncated and `step()` then raises until `reset()`, as today.
- Identity mismatch: `ValueError` naming the component and both values
  (shipped wording): `restore(): engine_commit differs: snapshot
  5928b7ca…, this environment 4464488e…` / `restore(): config_digest
  differs: snapshot <sha256>, this environment <sha256>` / `restore():
  control differs: snapshot kitty_2=needy, this environment
  kitty_2=external` (the first differing seat; `<absent>` for a seat one
  side lacks — a seat left unnamed is normalized to `external`, so two
  spellings of one control map are one identity). The environment is left
  exactly as it was.
- Bytes that do not parse, or parse into a world this environment cannot
  lawfully run (the world's own fingerprint is not this config's, the
  roster differs, or a constitutional invariant fails — the checks the
  server's load path runs): `ValueError("restore(): not a snapshot: …")`;
  environment untouched.
- Drops any pending override.

### `fork() -> ParallelEnv`

A new environment of the same config and control map, restored from
`self.snapshot()`. Inherits every refusal of `snapshot()`.

### `override(kitty, action=None, message=None) -> None`

Records a one-tick proposal substitution for an engine-decided seat
(builtin preset or needy preset). `action` is a menu index in the seat's
start-of-tick target table (the same vocabulary `step()` takes for a
policy seat); `message` is a message-head index (`0` = Silent). Each half
is independent; an unnamed half stays the seat's own behaviour's proposal
for that tick. The next `step()` consumes it; the engine's law rules on
the proposal at the apply slot exactly as on any other.

The override does not consult the legal mask: it may name a mask-illegal
act, and the engine then rules at the apply slot (a refusal stamp where a
mask-legal act would have applied). A reader comparing a branch against a
baseline that chose mask-legal acts must branch on the baseline's
mask-legal action, not the raw class.

- `kitty` externally controlled: `ValueError("override(): kitty_N:
  externally controlled; supply its action through step()")`.
- Unknown kitty: `ValueError("override(): kitty_N: not in the roster")`.
- Neither half given: `ValueError("override(): kitty_N: name an action, a
  message, or both")`.
- A pending override already set for the seat: `ValueError("override():
  kitty_N: already has a pending override; step() first")`.
- `action`/`message` out of range or negative: `IndexError` (the class
  `step()` raises for the same fault), naming the kitty, index and length.
- No decision window — before `reset()` or after truncation:
  `ValueError("override(): kitty_N: no decision window (reset first)")`;
  poisoned: `RuntimeError`, as for `step()`.
- Cleared by `reset()` and `restore()`; a `step()` refused for a bad
  external action leaves it standing.

### `tick_records() -> dict[str, dict]`

For EVERY roster kitty (scripted seats included), the last step's record:
`proposed_action_name`, `validated_action_name`, `applied_action_name`,
`proposed_message`, `applied_message`, `provenance`, `decision_seed`,
`survived` (see data-model.md). After `reset()` or `restore()` the
action, message and provenance fields are `None`. Read-only; never an
observation. `provenance` values: `"policy"`, `"fallback"`,
`"substituted_idle"`, `"overridden_act"`, `"overridden_message"`,
`"overridden_both"`.

## VectorEnv

### `snapshot(world: int) -> bytes`
### `restore(world: int, data: bytes) -> (obs, infos)`
### `override(world: int, kitty, action=None, message=None) -> None`
### `tick_records(world: int) -> dict[str, dict]`

The single-world semantics above, addressed to one world (`IndexError`
for a negative index or `world >= num_worlds`), with the single-world
refusals per world: `snapshot(world)` is `ValueError("reset first")`
until that world was established by a fully successful `reset()` or by
`restore(world, …)`; `override(world, …)` is `ValueError("reset first")`
with no decision window — before the first `reset()`, after that world
truncated, or after a partial step failure desynchronized the batch.
`restore(world, …)` returns that one world's `{agent: observation}` /
`{agent: info}` (not stacked). The other worlds are untouched (FR-008).
The batch's reset requirement is unaffected: before the first `reset()`,
or after a partial step failure, `step()` still refuses until a full
`reset()` even if some worlds were restored. A restored world keeps the
snapshot's episode position, so it runs off the batch's horizon cycle: it
truncates on its own tick, and a truncated restore makes the next
`step()` a partial failure (that step's transitions discarded, full
`reset()` required). After a partial step failure `tick_records(world)`,
like `state()`, stays at the pre-step tick for every world. No `fork()`
on `VectorEnv`.

A snapshot taken from a `ParallelEnv` restores into a `VectorEnv` world
of the same identity and vice versa (FR-005).

## Docstring text carried by snapshot / restore / fork / override (FR-017)

Verbatim in substance, present in each of the four docstrings:

> Branch depth k > 1 — where a component's predictions drive successive
> branch states — is a named marker-review trigger
> (experiments/WELFARE-STANDING.md text (b);
> experiments/gen2-prereg-2026-10-17.md §A2′ item 5). The API is
> depth-unlimited; the doctrine, not the API, caps its use.

`snapshot` additionally: "A snapshot is a transient token for the binding
that produced it: no format version, no compatibility across engine
commits; the raws are the durable artifact and any snapshot is
re-derivable by replay."

## Module constants

Unchanged: `ENGINE_COMMIT`, `OBSERVATION_SCHEMA_VERSION`,
`ACTION_SCHEMA_VERSION`, `MASK_SCHEMA_VERSION`,
`GLOBAL_STATE_SCHEMA_VERSION`, `COLUMN_MAPS`.
