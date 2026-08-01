# Data Model: Retire the Engine-Enforced Meow Cooldown (spec 023, Phase 1)

## Meow bookkeeping (demoted from law to record)

| Element | Before | After |
|---|---|---|
| `Kitty::meow_cooldowns` (BTreeMap kind → ready tick) | stamped at emission; **gates** emission (swallow) | stamped at emission identically; gates **nothing** |
| `Kitty::can_meow(kind, tick)` | engine enforcement + behavior consult | behavior courtesy consult only (docs updated to say so; the name stays — renaming a public consult is churn with no semantic gain) |
| `Kitty::set_meow_cooldown` | stamp | stamp (unchanged) |
| `cooldown_for(kind, need, base, urgent, threshold)` | enforcement arithmetic | stamp-time arithmetic (unchanged function; docs updated) |
| Purr kind entry | stamped by purr starts (pre-022) | never stamped, never read (settled by 022's implementation; guard test here) |
| Restored legacy snapshots with stamps | enforced | harmless record — at most delays a scripted kitty's next consult |

No snapshot schema change. No observation change: digest layout, decay, and
`LEARNED_MEOWS` untouched (WaitForMe was never in the digest).

## MeowConfig (config `[meow]`)

| Key | Type | Default | Validation row | Notes |
|---|---|---|---|---|
| `courtesy_ticks` | `u64` | **10** (renamed; was `cooldown_ticks` = 15) | urgent ≤ base | scripted base courtesy; = digest window (refresh-on-expiry) |
| `urgent_courtesy_ticks` | `u64` | **5** (renamed; was `urgent_cooldown_ticks` = 5) | (paired above) | applied at/above `urgent_need_threshold`, at stamp and consult |
| `urgent_need_threshold` | `f32` | 75.0 (unchanged) | existing | unchanged semantics |
| `recent_window_ticks` | `u64` | 10 (unchanged) | existing | digest/viewer retention |
| `cooldown_ticks` | sentinel `Option<u64>` | — | **`Some` ⇒ load error** naming `courtesy_ticks` | deserialize-only |
| `urgent_cooldown_ticks` | sentinel `Option<u64>` | — | **`Some` ⇒ load error** naming `urgent_courtesy_ticks` | deserialize-only |

Posture change (deliberate, research D2): all real fields gain per-field
serde defaults — partial `[meow]` tables become legal and default-filled,
matching `[purr]`'s documented posture, and letting old-key configs reach
validation where the retirement error can explain itself.

## Scripted emitters (all three consult, FR-004)

| Emitter | Site | Consult today | Change |
|---|---|---|---|
| Urgent needs announcer | behavior/needs_driven.rs:41 | yes | none (reads renamed keys via `cooldown_for` stamps) |
| Playful play announcer | behavior/playful.rs:59 | yes | none |
| Approach-etiquette yield ("Wait for me!") | behavior/selection.rs `wait_for_them`, called from needs_driven.rs:203 and selection.rs:336 | **no** (leans on the swallow) | gains `ctx` + consult; on courtesy → `Action::Idle` (silent stand; tick-parity guarantee preserved) |

## Emission path (`emit_meow`, action.rs)

```text
before: gate (can_meow? else swallow) → cooldown_for → stamp → push
after:                                   cooldown_for → stamp → push
```

Every validated meow action emits; turn cost unchanged; recent-meow pruning
and digest clamping unchanged (the bounded-chatty-advisor posture).
