# Phase 1 data model: Stuck Detector

All types live in `crates/cloudkitty-server/src/stuck.rs` unless noted.
Field lists are the WHAT; exact Rust shapes are implementation's choice
where unstated. Source requirements in parentheses.

## StuckConfig (FR-010)

The `[stuck_detector]` server-owned TOML table (watchdog loader shape,
`deny_unknown_fields`, defaults documented in doc comments).

| Field | Type | Default | Validation |
|---|---|---|---|
| `mode` | enum `off` / `observe` / `enforce` | `off` | one of the three literals |
| `window` | u64 ticks | `30` | ≥ 2 (a 1-tick window is noise) |
| `armed_line` | f64 need value | `75.0` | in (0, 100] |
| `radius` | u32 Manhattan tiles | `1` | ≥ 1 (1 is the replay-verified value; others unverified, doc-commented) |
| `recent_fires` | usize ring capacity | `256` | ≥ 1 |

Defaults are the measured choices of research.md R4; absent table =
these defaults (mode off ⇒ shipped dark, FR-009). Mind-class seats are
wrapped in every mode, off included — the wrapper forwards when idle —
so mode changes gate behavior, never code paths.

## SeatSignature (FR-001, FR-002, FR-007) — per tracked seat

Observer-owned window state, keyed by `KittyId`, existing only for
mind-class seats (FR-003; untracked seats have no entry by construction).

| Field | Meaning |
|---|---|
| `anchor` | the window-anchor tile (`Pos`); `None` before first observation |
| `confined` | consecutive ticks never outside Manhattan `radius` of `anchor` |
| `streaks` | per-`NeedKind` count of armed scene-free ticks |

### Transitions (per observed tick, per seat — the verified FR-002 rule)

1. Position outside `radius` of `anchor` (or no anchor) → `anchor` :=
   current tile, `confined` := 1, `streaks` cleared.
   Else `confined` += 1.
2. Per need: in a scene whose `governing_need()` == that need AND the
   scene relieves the SEAT's own need (grooming with a target governs
   the friend's bath — not the groomer's streak; solo rest governs
   nothing) → streak cleared. In any other scene → streak unchanged
   (pause). Scene-free and need ≥ `armed_line` → streak += 1.
   Scene-free and below the line → streak cleared.
3. Signature complete when `confined ≥ window` AND some need's streak ≥
   `window` → emit a FirePlan for the NEXT tick and reset
   `anchor`/`confined`/`streaks`. The reset IS FR-007's stand-down: a
   refire needs a fresh full window by construction (replay parity —
   the verification instrument fires every `window` ticks on the
   synthetic pacer, `200 // n` fires; no extra stand-down field).
4. Strict any-scene-resets semantics are wrong by measurement
   (verification-2026-10-13.md); the pause form above is the contract,
   re-verified 2026-10-15 under this governing-need relief rule.

## FirePlan — observer → wrapper, keyed by (tick, seat)

The next-tick fire set entry the guard wrapper consumes.

| Field | Meaning |
|---|---|
| `target_tick` | the tick the substitution applies on |
| `seat` | `KittyId` |
| `signature` | window length, measured confinement span, armed need + its value at completion |

Unconsumed entry (benched seat, served path only): expires at
`target_tick + 1`. The signature state was reset at emission, so a
still-stuck episode re-accumulates and fires again after a fresh full
window — an undelivered fire delays the intervention by up to one
window (research.md R2 residual; the bench fallback applied the
scripted brain anyway). Never re-emitted for the same completion.

## FireRecord (FR-011) — one per fire, full attribution

| Field | Source |
|---|---|
| `tick` | target tick |
| `seat` / kitty name | wrapper ctx |
| `mode` | `observe` or `enforce` (an off detector records nothing) |
| `window`, `anchor`, `confined_span` | FirePlan signature (FR-011: the anchor tile and ticks confined) |
| `armed_need`, `need_value` | FirePlan signature |
| `proposal_replaced` | the inner advisor's decision (activity + message); the literal `"none"` when the inner `try_decide` yielded no proposal (observe then returns `None` so the engine fallback runs as ever) |
| `substitute` | the scripted brain's decision (enforce: applied; observe: computed for the record, not applied) |

Emitted as one structured tracing event (WARN enforce / INFO observe)
and pushed to the bounded ring. Zero anonymous or partial records
(SC-003): every field is mandatory at construction.

## StuckStatus (FR-012) — the `/stuck` surface

| Field | Meaning |
|---|---|
| `mode`, `window`, `armed_line` | live config echo |
| `per_seat` | per-seat fire counts since boot (enforce and observe counted separately) |
| `recent` | the FireRecord ring, newest last |
| `armed` | per-seat live trigger state: current confined count and hottest streak (the exposed trigger condition the deferred distress intervention keys on — forward hook only) |

Published on a `watch` channel from `sim_task` (the `welfare` pattern)
into `AppState`.

## Relationships

```text
StuckConfig ──owns──> StuckDetector (observer: SeatSignature per mind seat)
StuckDetector ──emits──> FirePlan (next-tick fire set, shared Mutex state)
StuckGuard (Behavior wrapper, one per REGISTERED mind-class behavior;
            a shared instance serves every seat naming it, resolved
            per call via ctx.me) ──consumes──> FirePlan
StuckGuard ──produces──> FireRecord ──> tracing line + ring
StuckDetector/ring ──publishes──> StuckStatus ──> /stuck, /settings rows
Seat class rule (policy:* ∪ plugin class=mind) ──bounds──> what is wrapped/tracked
```

Engine-side: zero new state. The one core edit is the config
passthrough field (research.md R7), carrying no data into the engine.
