# Contract: Meow law under fog (spec 049, FR-036–FR-046)

One rule per tier in `message_legal(kitty, kind, tick, config, view)`; the RL message mask probes it over the fog view, enforcement calls it over the live world filtered for the emitter. Every meow-derived clause reads only meows with `m.tick < tick` (start-of-tick buffer, research R5).

## Pairs (const `WANT_HERE_PAIRS`, `meow.rs`)

| want | here | referent | visible-from-speaker test |
|---|---|---|---|
| `want_eat` | `here_food` | chow | any chow element inside the speaker's disc |
| `want_drink` | `here_water` | water | any water element inside the disc |
| `want_sleep` | `here_sunbeam` | sunbeam | any sunbeam inside the disc |
| `want_play` | `here_critter` | critter (bug or greeble) | any critter inside the disc |
| `want_cuddle`, `want_bath` | — | — | no here word, no reply |

## Want tier — legal iff ALL of

1. `[meow.vocabulary]` flag on; per-kind cooldown clear (unchanged).
2. Grounding need armed: `announce_armed` contains it (`announce_threshold` + `announce_hysteresis`, unchanged; served 30/5, step-5 screens {10, 15, 20, 30}).
3. The need is the cat's **top need**: `needs.highest_pressure()` (strictly greater wins; `NeedKind::ALL` order keeps the earlier kind on exact ties).
4. **No known relief** (`known_relief(kind, view)` is false):

| kind | known relief |
|---|---|
| eat | a chow element visible ∨ `memory[Chow]` present |
| drink | a water element visible ∨ `memory[Water]` present |
| cuddle, bath | an *available* friend visible ∨ heard-unseen (`heard_unseen()` non-empty after the availability filter where the partner-availability predicate can be evaluated; a heard friend's availability is unknown and counts as available) |
| play | (the cuddle/bath clause) ∧ (a critter visible ∨ `memory[Bug]` ∨ `memory[Greeble]` present) — i.e. legal only when neither friend nor critter is known |
| sleep | never known — no knowledge gate (need-only-when-top) |

Radius-edge flicker on clause 4 is accepted (owner ruling v); no hysteresis.

## Here tier — legal iff

vocabulary on ∧ cooldown clear ∧ ( **adjacent(referent)** — today's law, the corresponding action's own predicate — ∨ **reply_condition** ).

`reply_condition(kind)` = a meow of the paired want from another cat with `tick − m.tick < digest_window_ticks` and `m.tick < tick` exists ∧ the referent is visible from the speaker.

## Purr, free register, WaitForMe — unchanged.

## Reply stamp (`emit_message`)

`Meow { kitty_id, kind, tick, intensity, pos: kitty.pos, reply }` with `reply = kind ∈ HERE_KINDS ∧ reply_condition(kind)`; `false` for every other kind. Stamped once, immutable, additive on `/world`, `/kitties` (via the snapshot) and the meow event stream. Purr's engine-motor emission stamps `pos` too, `reply = false`.

## Observation readings (see observation-v5.md)

- Want intensity cells (row 52–57): the friend's last stamped `intensity` for its freshest call of that want kind inside the window.
- Answers-me bits (row 58–61): 1 iff the friend's freshest here of kind h inside the window has `tick` greater than my own freshest matching want inside the window. Derived; no engine state.

## Scripted side (`behavior/mod.rs::announce` → the ladder)

Order: **WaitForMe** (from the activity ladder, unchanged) > **{reply, own want}** > **ambient here** (`announce_here` phase ticks, unchanged rule) > **Silent**.

- **Reply candidate**: exists iff `[behavior] reply_intensity_floor` is set, and among audible wants from other cats (start-of-tick, inside the window) with a paired here kind that is *legal for me now* (referent visible from me, cooldown clear, flag on) there is one with `intensity ≥ floor`. Choose the highest intensity; ties → freshest; then lower kitty id. The reply is the paired here kind.
- **Own-want candidate**: the top-need want if legal (the want tier above; `announce()`'s existing scan collapses to it).
- **Resolution**: own want iff `own_need > caller_intensity × 100` (raw need both sides); ties → reply. The loser waits (cooldowns count from the last emission; never bypassed).
- **Message-only**: the replier's action is whatever the activity ladder chose.
- **Caller side**: a built-in does nothing with a reply it hears; here words are never consumed by built-ins (043 gate-zero guard stands).
- **Floor unset**: no reply candidate ever exists — launch state byte-identical to the no-reply engine.

## Config keys touched

`[meow] digest_window_ticks` (window for audibility, rate denominator via `/ recent_window_ticks`, `recent_meows` retention); `[meow] recent_window_ticks` (cooldown, unchanged value); `[behavior] reply_intensity_floor` (optional); `[meow] announce_threshold` / `announce_hysteresis` (unchanged values, screened at step 5).
