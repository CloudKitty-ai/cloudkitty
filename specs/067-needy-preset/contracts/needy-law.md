# The Needy Law, v1

Spec 067. The one place the schedule, the mask and the verdict are
pinned; `core/src/needy.rs`, `behavior/needy.rs`, `World::needy_verdict`,
`World::advance_needy` and `invariants::check` implement it. A change to
any numbered rule is a law change: bump the domain tag (`ck-needy-v1` →
`v2`) and this file's version together.

## §1 Seats and names

Two builtin presets: `needy` (release at level or limit, whichever
first) and `needy_hold` (release at limit only). Seated by
`[[kitty]] behavior = "<name>"`. Each is a spec-066 hazard mode of the
same name; registry order `initial_needs`, `needy`, `needy_hold`.
Neither teaches (`Behavior::teaches() == false`). A kitty carries needy
state exactly when its CONFIGURED behaviour is one of the two names
(an engine invariant, checked every tick; the binding's control map and
the server's resume refuse a roster that would break it).

## §2 The sub-stream

`seed[0..8] = world_seed LE; seed[8..12] = kitty_id LE;
seed[12..23] = b"ck-needy-v1"; rest 0` → `ChaCha8Rng`. Every draw
below is from this stream, in this order, and from nothing else. The
master stream and every other kitty's stream are untouched.

## §3 Draws

One conversion, the init-law §5 recipe: `u = (next_u64() >> 11) / 2^53`
in [0, 1), one `u` per draw.

1. **First onset** (at generation): level index = the first i with
   `cumulative_weight(i) > u · total`; tick within `[lo, hi)` =
   flat `lo + floor(u · (hi − lo))`, or log-uniform
   `floor(exp(ln lo' + u · (ln hi − ln lo')))` with `lo' = max(lo, 1)`,
   clamped into `[lo, hi)`.
2. **Episode set** (at generation for the first, at each release for
   the next): m = index + 1 by `mix` (as in 1); then m distinct needs
   by partial Fisher–Yates over `NeedKind::ALL`: for i in 0..m,
   `j = i + floor(u · (N − i))`, swap.
3. **Gap** (at each release): `min + floor(u · (max − min + 1))`.

## §4 Phases (advanced once per tick in Phase 4, after needs rise)

`t` is the tick about to be published (`world.tick + 1`).

- `Resting{next_onset}` → `Held{onset: t, masked: next}` when
  `t >= next_onset`: ordinal += 1; the onset sweep (§5b) runs.
- `Held{onset, masked}` → released by **Level** (`needy` only) when
  every masked need ≥ `release_level` on the post-rise needs, checked
  first; by **Limit** (both presets) when `t − onset >= hold_ticks`. On
  release, in one step: `last_release = {t, by}`, draw §3.3, draw §3.2
  for the next episode, phase = `Resting{next_onset: t + gap}`.
- The mask is the `Held` set; empty in `Resting`. At most one
  transition per step.

## §5 Enforcement (engine law)

### §5a The verdict (apply slot, after the consent gate, both sites)

A validated proposal resolves to `Idle` iff (a) `proposer_relief` of
the action meets the PROPOSER's mask, or (b) it names a partner or
target whose mask meets `partner_relief` of the action:

| action | proposer relief | partner relief |
|--------|-----------------|----------------|
| Eat / Drink | eat / drink | — |
| Sleep{None} | sleep | — |
| Sleep{Some p} | sleep, cuddle | cuddle |
| Rest{None} | — | — |
| Rest{Some p} | cuddle | cuddle |
| Groom{None} | bath | — |
| Groom{Some p} | cuddle | bath |
| Play{None / element} | play | — |
| Play{Kitty p} | play | play |
| Chase, Move, Idle, Meow, Purr | — | — |

Recorded as a refusal (spec 046) with reason `needy_masked`; no new
record type. The tables are cross-checked against the effects by test.

### §5b The onset sweep

On the onset tick, before any decision reads the mask: the needy
kitty's own activity ends if its continuation's proposer relief meets
the mask (a social-play duet ends for both); a friend's groom of the
needy kitty ends if bath is masked; a friend's social play with it ends
if play is masked; a friend's rest or co-sleep WITH it drops to solo
posture (companion cleared, clock untouched) if cuddle is masked.
`available_friend_in`, validation, the legal mask and the effects arms
are untouched: the mask is hidden state, read only at the apply slot
and in this sweep.

## §6 The preset's own choice

Mask empty: `Teacher::GEN2` verbatim (the same `decide`). Mask
non-empty: the same ladder on a view with masked needs read as 0 and a
forked copy of the turn's stream; a chosen action whose proposer relief
meets the mask, or a Chase while play is masked, becomes `Sleep{None}`
when it was `Sleep{Some}` under a cuddle-only mask and `Idle`
otherwise. The message channel is the teacher's on the UNMASKED view:
calling stays on, law-named words only.

## §7 Surfaces

- `Kitty.needy` in the saved world and the server's state for a needy
  seat: `hold`, `ordinal`, `phase` (`resting {next_onset}` or `held
  {onset, masked}` with `masked` as need names), `next` (need names),
  `last_release` (`tick`, `by`), `rng`; absent for every other kitty;
  blanked in every OTHER kitty's view of the world (`fog_for`), so it
  never reaches an observation, a plugin request or a trace.
- Binding: `ParallelEnv.needy()` → `[(kitty_id, [names], ordinal,
  phase)]`, phase ∈ `resting | held | released_level | released_limit`
  (the released names on the release tick only).
- Config: `[needy]` serializes when written (`GET /config`); absent
  otherwise.
- Hazard: 066's boot line, `GET /config` and settings row name the
  modes as 066 renders them.
- Refusal records: reason `needy_masked`.

## §8 Errors (`ConfigError::Invalid`, field / expected)

`<N>` is `NeedKind::ALL.len()`; `<names>` is `NeedKind::ALL` joined by
", " — never a literal.

| field | expected |
|-------|----------|
| `[needy].mix` | `exactly <N> weights, one per masked-need count from 1 to <N>` |
| `[needy].mix` | `finite, non-negative weights with at least one above zero` |
| `[needy].release_level` | `a need level in [0, 100] strictly above the off-beam sleep floor (<f>)` |
| `[needy].hold_ticks` | `at least 1 tick` |
| `[needy].gap` | `1 <= min <= max` |
| `[needy].onset_levels` | `at least 6 strictly increasing tick edges (5 levels)` |
| `[needy].onset_weights` | `one finite, non-negative weight per level (<L>), at least one above zero` |

Resume and control errors (not config): the server refuses a saved
world whose needy state disagrees with the configured roster, naming
the kitty; `Episode::new` refuses a control entry that disagrees with
the config seat about needy-ness, naming the kitty.
