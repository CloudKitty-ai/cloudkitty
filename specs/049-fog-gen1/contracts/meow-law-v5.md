# Contract: Meow law under fog (spec 049, FR-036–FR-046)

One rule per tier in `message_legal(kitty, kind, tick, config, view)`; the RL message mask probes it over the fog view, enforcement calls it over the live world filtered for the emitter. Every meow-derived clause reads only meows with `m.tick < tick` (start-of-tick buffer, research R5).

## Pairs (const `WANT_HERE_PAIRS`, `meow.rs`)

| want | here | referent | visible-from-speaker test |
|---|---|---|---|
| `want_eat` | `here_food` | chow | a STOCKED chow element (`servings > 0`) inside the speaker's disc — presence alone is not food: empty bowls are not a world state, but within phase 2 an emptied bowl lingers in the element list until the environment phase despawns it, and enforcement runs there (T097; the adjacency arm has always read stocked) |
| `want_drink` | `here_water` | water | any water element inside the disc |
| `want_sleep` | `here_sunbeam` | sunbeam | any sunbeam inside the disc |
| `want_play` | `here_critter` | critter (bug or greeble) | any critter inside the disc |
| `want_cuddle`, `want_bath` | — | — | no here word, no reply |

## Want tier — legal iff ALL of

1. `[meow.vocabulary]` flag on; per-kind cooldown clear (unchanged).
2. Grounding need armed: `announce_armed` contains it (`announce_threshold` + `announce_hysteresis`, unchanged; served 30/5, step-5 screens {10, 15, 20, 30}).
3. The need is the cat's **top need**: `needs.highest_pressure()` (strictly greater wins; `NeedKind::ALL` order keeps the earlier kind on exact ties). *Announcements only — `want_bath` is exempt (T087, below).*
4. **No known relief** (`known_relief(kind, view)` is false). *Announcements only.*

| kind | known relief |
|---|---|
| eat | a chow element visible ∨ `memory[Chow]` present |
| drink | a water element visible ∨ `memory[Water]` present |
| cuddle | an **idle friend visible**: `idle_friend_in_view(view)` — a friend inside the disc with `activity_clock.is_none()` (no scene, not asleep); adjacency not required. Heard-unseen friends never enter the gate (owner ruled 2026-09-03). |
| bath | **never** — an ASK (owner ruled 2026-09-03, T087): clauses 3 and 4 do not apply; legal iff clauses 1 and 2. Its relief is self-grooming; the partnered groom is the groomer's to start on hearing the word. `LawEra::PreFog` (`MeowConfig.law_era`, `#[serde(skip)]`, test-side) replays the 2.x armed-only law for every kind — SC-004a. |
| play | (the cuddle clause) ∨ (a critter visible ∨ `memory[Bug]` ∨ `memory[Greeble]` present) — i.e. the word is legal only when neither an idle friend is in view nor a critter is known |
| sleep | never known — no knowledge gate (need-only-when-top) |

Radius-edge flicker on clause 4 is accepted (owner ruling v); no hysteresis.

Targeting is a different question from the gate (owner ruled 2026-09-03, clarify item 1): built-in friend targeting takes heard-unseen friends **unconditionally** at their stamped position and checks idleness only on sight (research R10); the gate reads visible rows only.

**The scripted groom response** (`needs_driven::groom_response`; owner ruled 2026-09-03, T087): acts only on a `want_bath` with age ≤ `recent_window_ticks` (inclusive — the 2.x rule; audibility stays `digest_window_ticks`, the rung declines stale asks); on sight, declines a caller whose bath need < `announce_threshold` (`PreFog` keeps the 2.x rung, which groomed on the word alone). Both imitable: recency is a digest cell, the seen row carries bath.

## Here tier — legal iff

vocabulary on ∧ cooldown clear ∧ ( **adjacent(referent)** — today's law, the corresponding action's own predicate — ∨ **reply_condition** ).

`reply_condition(kind)` = a meow of the paired want from another cat with `tick − m.tick < digest_window_ticks` and `m.tick < tick` exists ∧ the referent is visible from the speaker (food: a stocked bowl, per the pairs table).

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
