# Research: Relief Memory Margin (spec 050)

No `[NEEDS CLARIFICATION]` markers remain (owner ruled 2026-09-04; two clarifications 2026-09-05). Each decision below was verified against the worktree HEAD (`52b4023`, off main `9e0ab5e`).

## R1 — The key is an `Option<u32>` on `MeowConfig`, skip-serialized when absent

- **Decision**: `MeowConfig.relief_memory_margin: Option<u32>` with `#[serde(default, skip_serializing_if = "Option::is_none")]`, exactly the `reply_intensity_floor` pattern (`config/mod.rs:1105`). Absent = `None` = today's unbounded rule. `Config::default()` leaves it `None`.
- **Rationale**: the 039-D5 stamp discipline — `engine_defaults_sha256` hashes the default config's serialized JSON, so a value nobody set must not appear as a key; the existing `roam_cell_stays_out_of_the_default_serialization` test gains one `!json.contains("relief_memory_margin")` line (red if the skip attribute is dropped). `u32` refuses a negative value at parse ("invalid value: integer `-1`, expected u32" — a load error naming the key), which is the spec's "refused at config validation"; there is no upper bound, so `validate_meow` needs no new clause. `MeowConfig` is `deny_unknown_fields`, so the key must exist on the struct before any TOML can carry it — the served TOML edit lands in the same change.
- **Alternatives considered**: a `u32` with default 0 (rejected: 0 is not "today" — 0 is the served value that changes the law; the absence default must be the unchanged engine per US2); placing the key under `[vision]` beside `radius` and `memory_timeout_ticks` (rejected: the owner's words put it under `[meow]`, and it is a want-LAW knob, not a perception knob; the served comment says the reach reads the `[vision]` radius).

## R2 — The reach lives in `known_relief`'s `remembered` closure; the margin is a parameter

- **Decision**: `known_relief(want, kitty, view, margin: Option<u32>)`. The closure becomes: a slot is remembered relief iff it is `Some` and, when `margin` is `Some(m)`, `kitty.pos.manhattan_distance(&slot.pos) <= view.radius.saturating_add(m)`. `message_legal` passes `config.meow.relief_memory_margin`. Eat, drink and play (bug, greeble) all go through the same closure, so FR-004's "one rule" is structural: there is no per-kind branch to drift.
- **Rationale**: `FogView.radius` is "the configured `[vision] radius`" (`world.rs:1630`), so the seam needs no `[vision]` read; `Position::manhattan_distance` exists (`grid.rs:35`). Passing the bare margin rather than `&Config` keeps the predicate's inputs exactly the spec's recomputable set (position, memory tile, radius, margin — FR-006 / prereg A14) and keeps the two existing unit-test callers a one-argument edit. `saturating_add` makes the "very large margin" edge case (≥ width + height ≡ absent) safe at `u32::MAX`.
- **Alternatives considered**: a separate `within_reach` free function called from three match arms (rejected: three call sites is how per-kind drift starts; the closure is the one rule); filtering the memory at `fog_for` time so the view's kitty carries only in-reach slots (rejected: navigation must keep reading the full memory — FR-005 — and the observation's memory cells must keep encoding the real slot).

## R3 — Navigation is untouched by construction

- **Decision**: no change to `behavior/selection.rs` (`priced_nearest_element`'s remembered arm) or `needs_driven.rs`. A cat may walk toward a remembered pool it is simultaneously asking about.
- **Rationale**: the spec's edge case "navigation is not the law"; the T092 remembered-beam occupancy filter and the exploration ladder read memory for targeting, which is a different question from the gate (the 2026-09-03 targeting-vs-gate ruling). Verified: `known_relief` is called only from `message_legal` and its own unit tests.

## R4 — Guards: unit fixture, independent property, served-roster count

- **Decision**: three layers.
  1. **Unit (meow.rs tests, SC-001/002/006)**: the axis-aligned fixture — kitty 1 at (8, 8) on the 16×16 stage, radius `r` from the test config (set to 5 for these tests), memory slot at `(8 + r + 1, 8)`; the test asserts `!visible_from` for the slot (outside the disc — clarification 2); margin 0 → legal, margin 1 → silent, `None` → silent. Same fixture for chow (`want_eat`) and bug (`want_play`, no critter and no idle friend in view). Water IN VIEW → silent at margins 0, 1, 8 and `None`. Cuddle / bath / sleep verdicts equal across margins. The margin-0 arm is the red-first case: on the unchanged engine the remembered slot silences, so "legal at 0" fails.
  2. **Property (meow_law_fog.rs, new test)**: draws `radius 2..=8`, `margin in prop::option::of(0u32..=4)`, random memory slots (random tiles, random `Some`/`None`), needs; oracle computes relief from `me.pos`, `slot.pos`, `radius`, `margin` with its own Manhattan arithmetic and compares to `message_legal`. The existing `the_law_holds_over_random_worlds` is not edited (SC-003: key absent, untouched, green).
  3. **Integration (new `tests/relief_memory_margin.rs`, SC-004)**: served `cloudkitty.toml` all-scripted (the four-file house pattern: read, retarget behaviours to `needs_driven`, validate), radius asserted 5, `drive_tick` × 1,000; count new meows per tick by kind. Assert `want_drink > 0` on the served config verbatim. Second run with `reply_intensity_floor = Some(0.01)` (any value > 0 — clarification 1; 0.01 so the floor's value cannot starve the count and 0.30 is not encoded): assert `here_water` with `reply == true` > 0. Print drink and eat counts as the F-040 reading. The red for this guard is the engine with the key parsed but unread (the field lands before the predicate) → 0 drink calls.
- **Rationale**: CLAUDE.md rule 5 (red seen first), the owner's explicit ask for the margin 0/1 pair on one fixture, and A14 (the property's oracle is a second derivation of the rule from observable quantities).

## R5 — Which pins move, and which do not

- **Move (served TOML gains the key = 0)**: `fog_continuity::reply_floor_unset_is_byte_identical` — `served_all_scripted()` loads `cloudkitty.toml`; at r = 5 the message stream gains `want_drink` rows (and the action stream may move where the announce rung's choice changes). Re-record ONCE with the ignored `record_preladder_r5_streams`; record the first divergence tick and the justification in the test's doc comment and in `redden-list.md`. The served welfare readings (`welfare_longrun::served_world_fog_r5_welfare_reading_with_global_vision_control`, ignored) are re-taken and the numbers written into the gate's comment (SC-007).
- **Do not move**: `world_covering_radius_diverges_only_by_the_named_causes` (SC-004b, served TOML at r = 40): on a 20×20 world every tile is within Manhattan 38 ≤ 40 + 0, so every remembered slot stays in reach — verdicts unchanged; predicted green, verified at cycle time. Evolution golden, strip witness, run_json golden, joint-action parity, the compiled welfare gate, `binding_continuity` (exp-006 config): all keyed on `Config::default()` or their own fixture TOML → key absent → unchanged. `refusal_reasons` prints a reading and asserts nothing. `fog_visibility`'s served property and the two config sweeps stay green (the key is optional and loads).
- **Rationale**: the spec's assumption ("compiled default absent so compiled goldens unmoved; served pins move once"); listing the predictions here is the 048 cycle-A lesson.

## R6 — The served comment block (FR-007)

- **Decision**: under `[meow]`, after `announce_hysteresis`: `relief_memory_margin = 0` with a comment that says (a) what it is — a remembered element is known relief only within `[vision] radius + margin` Manhattan tiles of the cat; (b) why 0 — at 0 memory never silences a want (Manhattan ≤ r is inside the disc), so the served law is "visible relief only", which revives `want_drink` (F-040: water is permanent and never forgotten, so the old rule silenced it for good); (c) key absent = the unbounded 2026-09-04 rule; (d) the step-5 prereg screens 0 and 1. The `[meow]` head comment's "nothing visible or remembered" gains "within reach".
- **Rationale**: SC-005 (the served diff is one key plus its comment) and the changelog/migration practice of naming the key where it lands.

## R7 — Records

- **Decision**: `specs/049-fog-gen1/contracts/meow-law-v5.md` known-relief table — eat, drink, play rows gain "∨ `memory[kind]` present **within reach** (Manhattan(pos, tile) ≤ radius + `[meow] relief_memory_margin`; unbounded when the key is absent — spec 050)"; `config-3.0-migration.md` new-keys table gains the row (optional, absent default, served 0); `docs/meows.md` law paragraph: "a bowl visible or remembered within reach" with one sentence defining reach; CHANGELOG Unreleased one-liner (a served-dynamics move; no `[stamp]`, no `[obs-schema]` — the marker legend is re-read at implement time per changelog-practice).
- **Rationale**: FR-009. `experiments/FINDINGS.md` F-040 is Experiments' file and is not edited here; the merge ping tells them the key landed.

## R8 — Hand-off after merge (Experiments' side, not this arc's)

- **Decision**: the merge ping to Experiments names: `anchor.toml` gains `relief_memory_margin = 0`; re-smoke `schema_check.py` A1/A9 and the relief sweep; drop the `want_drink` group from `declared_constant.json`; add the key to the PREREG config rule (served `cloudkitty.toml` with the groom bump reverted now carries it). Nothing in this arc edits those files.
- **Rationale**: the spec's assumptions; the thread-delineation rule (relay, never implement another thread's queue).
