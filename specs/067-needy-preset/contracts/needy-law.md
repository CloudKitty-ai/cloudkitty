# The Needy Law, v1

Spec 067. The one place the schedule, the mask and the verdict are
pinned; `core/src/needy.rs`, `behavior/needy.rs`, `World::needy_verdict`,
`available_friend_in` and `action::partner_relief` implement it. A
change to any numbered rule is a law change: bump the domain tag
(`ck-needy-v1` → `v2`) and this file's version together.

## §1 Seats and names

Two builtin presets: `needy` (release at level or limit, whichever
first) and `needy_hold` (release at limit only). Seated by
`[[kitty]] behavior = "<name>"`. Each is a spec-066 hazard mode of the
same name; registry order `initial_needs`, `needy`, `needy_hold`.
Neither teaches (`Behavior::teaches() == false`).

## §2 The sub-stream

`seed[0..8] = world_seed LE; seed[8..12] = kitty_id LE;
seed[12..23] = b"ck-needy-v1"; rest 0` → `ChaCha8Rng`. Every draw
below is from this stream, in this order, and from nothing else. The
master stream and every other kitty's stream are untouched.

## §3 Draws (each one `u32`/`f32` from the stream, in this order)

1. **First onset** (at generation): level index by `onset_weights`
   (cumulative over one `f32` in [0,1)); tick within `[edge_i, edge_i+1)`
   — flat: `lo + u·(hi−lo)`; log-uniform: `exp(ln(max(lo,1)) +
   u·(ln hi − ln max(lo,1)))`; floored to a tick, one `f32`.
2. **Episode set** (at generation for the first, at each release for
   the next): m = index+1 by `mix` (cumulative over one `f32`); then m
   distinct needs by partial Fisher–Yates over `NeedKind::ALL` (m
   `u32` draws, `gen_range_u32(i, N)`).
3. **Gap** (at each release): flat in `[gap.min, gap.max]`, one `u32`.

## §4 Phases (advanced once per tick in Phase 4, after needs rise)

- `Resting{next_onset}` → `Held` when the tick about to be published
  equals `next_onset`: ordinal += 1; the kitty's own activity ends if
  its governing need is in the set.
- `Held` → `Releasing{by: Level}` (`needy` only) when every masked need
  ≥ `release_level` on the post-rise needs; → `Releasing{by: Limit}`
  (both presets) when `tick − onset ≥ hold_ticks`. Level is checked
  first.
- `Releasing` → `Resting{next_onset = released_at + gap}` on the next
  step, drawing §3.3 then §3.2 for the next episode.
- The mask is the `Held` set; empty otherwise.

## §5 The verdict (engine law, apply slot, after the consent gate)

A validated proposal resolves to `Idle` iff
(a) its activity's governing need is in the PROPOSER's mask, or
(b) it names a partner or target whose mask contains
`partner_relief(action)`: Groom→Bath, Play→Play, Rest→Cuddle,
Sleep→Cuddle. Recorded as a refusal (spec 046), no new record type.
A kitty whose mask contains a duet's partner-relief need is not an
available partner for that duet (`available_friend_in`), so an
in-progress duet or groom stops delivering to it on the onset tick.

## §6 The preset's own choice

Outside the mask: `Teacher::GEN2` exactly. Under the mask: the same
ladder on a view with masked needs read as 0; a chosen action whose
governing need is masked falls to the wander rung (or Idle). The
message channel is the teacher's on the UNMASKED view: calling stays on,
law-named words only.

## §7 Surfaces

- `Kitty.needy` in every snapshot for a needy seat: `hold`, `ordinal`,
  `phase` (with `masked` as need names), `next_onset`; absent for every
  other kitty.
- Binding: `ParallelEnv.needy()` → `[(kitty_id, [names], ordinal,
  phase)]`, phase ∈ `resting | held | released_level | released_limit`.
- Config: `[needy]` serializes when written (`GET /config`); absent
  otherwise.
- Hazard: 066's boot line, `GET /config` and settings row name the
  modes as 066 renders them.

## §8 Errors (`ConfigError::Invalid`, field / expected)

| field | expected |
|-------|----------|
| `[needy].mix` | `exactly <N> weights, one per masked-need count from 1 to <N>` |
| `[needy].mix` | `finite, non-negative weights with at least one above zero` |
| `[needy].release_level` | `a need level in [0, 100] above every reachable floor (sleep floor <f>)` |
| `[needy].hold_ticks` | `at least 1 tick` |
| `[needy].gap` | `1 <= min <= max` |
| `[needy].onset_levels` | `at least 6 strictly increasing tick edges (5 levels)` |
| `[needy].onset_weights` | `one finite, non-negative weight per level (<L>), at least one above zero` |
| `[needy].floors.<key>` | `a known need name (eat, drink, sleep, play, cuddle, bath)` |
| `[needy].floors.<need>` | `a need level in [0, 100]` |
