# Data Model: Parameterized Teacher Rework (spec 059)

No schema version moves: OBSERVATION 6, GLOBAL_STATE 2, ACTION/MASK 3
all hold (058 wall). No new serialized Kitty state. The model below is
behavior-layer and config-layer only.

## Entities

### Teacher (new, `behavior/teacher.rs`)

The one scripted brain. Stateless across ticks (reads
`Kitty::last_relief_tick` for the slack gate). Fields (per instance,
frozen at registration):

| field | type | values |
|---|---|---|
| `preset` | `Preset` | NeedsDriven, Playful, Teacher |
| rung toggles | bool × 3 | wander, groom_response, luxury (see contracts/presets-and-dials.md) |

Per-decision inputs (never stored): the four dial groups via
`ctx.config.need_rate_for / comfort_slack_for / consent_line_for /
favourite_weight_for (me.id)`; world `[behavior]` keys
(`playful_comfort`, `comfort_weight`, `reply_intensity_floor`,
`response_commitment_ticks`); the digest via `FogView`.

Ladder (order is normative — byte-equality depends on it):
1. finish_what_you_started
2. take_what_is_here (no proposer-side consent — gate is engine-side)
3. groom_response *(toggle)*
4. response rungs: cuddle_response / play_response valuation terms
   enter the pursuit value table (not a separate return — see
   contracts/cue-answer.md)
5. luxury entry *(toggle)*: `weighted_pressure < playful_comfort` AND
   slack gate open → scored_play_action
6. wander *(toggle)*: `pressure < 20 && rng.gen_bool(0.4)` — exact
   order and short-circuit preserved
7. pursue(choose)

### Preset registration rows

Three registry entries, all `Teacher` instances
(`with_builtins`, behavior/mod.rs:141-146):
`needs_driven` (wander ✓, groom ✓, luxury ✗),
`playful` (✗, ✗, ✓), `teacher` (✓, ✓, ✓).
Dial defaults: none — the accessors' world fallbacks ARE the preset
defaults (research R1). Fallback brain = the `needs_driven` instance.

### Response term (transient, per decide)

| field | source |
|---|---|
| kind | WantCuddle → partnered rest; WantPlay → friend play |
| caller | the winning call's `kitty_id` (names the answered partner) |
| intensity | `Meow::intensity` (stamped need/100 at emission) |
| d | Manhattan(me, caller pos at call) |
| window_remaining | `digest_window_ticks − (now − call.tick)` |
| score | `intensity − k·d` (see contracts/cue-answer.md for k, feasibility, h) |

Expiry is digest visibility; no term persists.

### Consent refusal (engine)

- Gate location: after `action::validate` in
  `run_applied_phases_from_decisions` (world.rs:352-376) and
  `apply_slot_verdict` (world.rs:580-595). Conscripting proposals
  only (`Play{Kitty}`).
- Predicate (spec 047 semantics, per-kitty line):
  `top_non_play(target) > consent_line_for(target) &&
  top_non_play(target) > target.needs.get(Play)`, strict >, line ≤ 0
  short-circuits to open.
- `RefusalReason::ConsentDeclined` — new variant (events.rs:93-104);
  snake_case wire name `consent_declined`. RefusalEvent shape
  otherwise unchanged; `absorbed` semantics unchanged.
- The RL mask does NOT evaluate the gate (mask stays consent-blind;
  guard test pins it).

## Config changes

| key | kind | default | validation |
|---|---|---|---|
| `[behavior] response_commitment_ticks` | new f32 (ticks) | 3.0 | finite, ≥ 0, joins the shared finite-non-negative loop (validate.rs) |

Relocations (no value change): `COMFORT_SLACK_NORMALISER` (40.0) and
new `Config::slack_cell_for(kitty_id)` into cloudkitty-core;
`observe.rs` consumes them; rl re-exports the constant for the schema
pins.

Removed from the behavior layer: `consent_blocks`, the `_consenting`
variants (`take_what_is_here_consenting`, `choose_consenting`);
`top_non_play` moves to the engine consent step.

## State transitions

- Slack gate: closed from a relief event until
  `now − last_relief_tick ≥ slack_cell_for(me) × 40`; open otherwise;
  slack 0 → always open (both presets).
- Response incumbency: within one decide, the FR-016 winner is
  recomputed from the snapshot; the commitment margin h applies when
  an incumbent exists (the previously answered caller is derivable
  from `me.activity`/pursuit target — no new stored state).

## Derived quantities (one home each, contracts/cue-answer.md)

`I_min = announce_threshold/100` · `I_max = 1.0` ·
`HANDSHAKE_TICKS = 2` · `D_w = digest_window_ticks − HANDSHAKE_TICKS`
· `k = (I_max − I_min)/D_w` · `h = k × response_commitment_ticks`.
