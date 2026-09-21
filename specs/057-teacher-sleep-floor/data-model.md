# Data model: teacher sleep rule reads the floor

No new persistent state, no new config key, no schema change. The
feature is a pure function of values that already exist.

## Inputs (all existing)

| Value | Source | Notes |
|---|---|---|
| `need` | `ctx.me.needs.get(NeedKind::Sleep)` | 0–100, Article I bounds |
| `floor` | `ctx.config.actions.sleep_floor_off_beam` | spec 056 key; serde default 0.0; validated `0 ≤ floor < needs.distress` |
| on-beam | `ctx.world.element_at(me.pos) == Sunbeam` | observation-derived |
| conducted | `warm_friend_beside(ctx)` | T092 / spec 031 |
| beam in reach | `sunbeam_worth_walking(ctx)` | priced ≤ `behavior.sunbeam_reach` |

## Derived values (new, decision-time only, never stored)

- **warm option in play**: on-beam OR conducted OR beam-in-reach.
- **effective sleep pressure**: `need` when a warm option is in play,
  else `max(need − floor, 0)`.

## State transitions

None. The rule changes which action the teacher proposes at a decision
point; the world's sleep relief, scene endings, need dynamics, and
announcements are all untouched (specs 056, 028, 031 own them).

## Invariants

- Effective pressure ∈ [0, need]; never negative, never above the raw
  need.
- `floor == 0` ⇒ effective pressure ≡ need on every branch (FR-004).
- The skip gate (research D5) can only fire when `floor > 0`.
