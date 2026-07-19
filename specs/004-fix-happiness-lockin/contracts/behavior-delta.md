# Behavior Contract Delta: Fix Low-Happiness Lock-In

**Base contract**: [001 behavior.md](../../001-cloudkitty-mvp/contracts/behavior.md).
The `Behavior` trait, decision budget, fallback, and validation pipeline are
unchanged. This delta covers what behaviors can now read and propose.

## DecisionContext additions (read-only, engine-authored)

Via `ctx.me` (the kitty's own state):

| Field | Meaning for a behavior author |
|-------|-------------------------------|
| `pursuit` | Your current chase, as the engine saw it actually happen: target, the tick it started, best distance achieved, and `improved_at` — when that best was last bettered. Patience runs from the last improvement, so a chase that keeps closing never expires. Survives one-tick detours; cleared by catching the target, chasing something else, the target dying, or abandonment. You cannot write it — only chasing does. |
| `abandoned_chases` | Targets you recently gave up on, each excluded until its `until` tick. Engine-pruned. The built-ins refuse to re-select these while excluded (FR-006); your behavior should too. |
| `last_relief` | Tick each need last received relief, however it arrived. Useful for fairness heuristics; the built-ins use it to break selection ties. |
| `distress_since` | Tick each active distress began. Lets a behavior notice "this has been bad for a while" without keeping its own memory. |

External behaviors (future P2 plugins) receive these fields in the same
snapshot JSON — no side channel, no behavior-kept state required for give-up
logic.

## Action changes

- `Play` target is now optional. Proposing `Play` **without** a target is
  solo play: always legal, relieves the proposer's play need by
  `actions.solo_play_relief` (smaller than social `play_relief`). Social play
  validation is unchanged (adjacent critter, or available adjacent kitty).
  Emit a *complete* target or none at all — a partial one
  (`{"action":"play","target":"element"}` with no `id`) is rejected at parse
  time, not quietly read as solo play. Your kitty then gets the usual
  fallback, never free relief for a malformed proposal.
- `Chase` is unchanged. Note the engine now *records* applied chases into
  `pursuit`; a rejected chase proposal (resolved to `Idle`) clears the
  pursuit instead of extending it.

## Built-in selection contract (reference for plugin authors)

Both built-in profiles now select needs with one shared, deterministic rule
(see [research.md §R1–R3](../research.md)):

```
score(kind) = pressure + urgency_weight × max(0, pressure − safeguard)
              − tile_cost × travel_distance(kind)
```

ties → longest since relief → `NeedKind::ALL` order. Play travel distance
counts the nearest **viable** partner (critter or kitty), where a target is
non-viable while it sits in `abandoned_chases` or while `pursuit` shows
`chase_patience_ticks` elapsed since it last gained ground. When no viable
partner is within `solo_play_reach` and play ≥ safeguard, the built-ins
propose solo play.

External behaviors are free to ignore all of this — the engine validates
proposals, not philosophies — but the built-ins' rule is the recommended
starting point, and it is what the fallback does to your kitty when your
behavior times out.

## Compatibility

- All tunables above come from `ctx.config` (`behavior.*`, `actions.*`,
  `thresholds.*`) — plugin authors must read them from the config rather
  than hard-coding, same as built-ins (Article VI).
- Snapshots and decision payloads from pre-004 releases lack the new fields;
  they deserialize to `None`/empty and behaviors must treat missing as
  "no pursuit / never relieved / no active distress ages".
