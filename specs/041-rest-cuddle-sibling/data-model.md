# Data Model: Rest becomes co-sleep's sibling

Four surfaces move: the rest activity's shape, the relief dial family,
per-scene tier state, and the activity-end event. Everything else
(menu, `KITTY_SLOT`, message head, snapshot layout otherwise) is
frozen by FR-003.

## 1. Activity: `Resting { with_friend }` (shape change, no layout change)

The enum variant and its serialized form are unchanged; what changes
is its semantics, to `Sleeping { with_friend }`'s exact contract:

| aspect | today (conscripted duet) | after (sibling) |
|---|---|---|
| legality (`validate`) | `is_conscriptable_friend` — partner free | `is_available_friend` — partner adjacent, any state |
| partner binding | partner forced into mirrored `Resting`, same clock | none — partner keeps its own activity/clock |
| partner-side stamp | `stamp_serviced(friend)` each tick | none |
| partner exit | impossible (bound) | per-tick re-filter drops to `with_friend: None` (solo) |
| relief | flat `cuddle_relief` both parties | tier-resolved per serviced tick, both parties |
| solo rest | posture only | unchanged — posture only |

State transitions per serviced tick (mirrors the sleeping arm):
re-filter partner by availability → resolve tier by the shared mutual
predicate → pay both parties the tier rate → increment the matching
tier counter. A wandered partner yields a solo tick: no relief, no
counter increment.

**Pre-change snapshots** (FR-009): a bound duet is two kitties each in
`Resting { with_friend: Some(other) }` with live clocks — under the
new effects arm this is simply two synchronized resters, each paying
mutual from its own slot. No migration, no heal.

## 2. Relief dial family (config)

| dial | engine default | served 2.x, after commit 1 | after commit 3 | site |
|---|---|---|---|---|
| `rest_mutual_relief` | 15.0 (classic) | 8.0 | 8.0 | rest, mutual tier |
| `rest_drip_relief` | 0.0 | 0.0 | 0.25 | rest, drip tier |
| `groom_cuddle_relief` | 15.0 (classic) | 8.0 | 0.5 | groomer's warmth |
| `cosleep_mutual_relief` | (existing) | 8.0 | 0.6 | co-sleep, mutual |
| `cosleep_drip_relief` | (existing) | 3.0 | 0.25 | co-sleep, drip |
| `cuddle_relief` | 15.0, **inert** | present, inert | present, inert | none (deprecated) |

Rules: `cuddle_relief` parses and validates but feeds nothing;
unknown-field rejection stays strict; drip < mutual within each
activity is a comment-carried convention (no validation); all six
appear in the nan-validation table (the inert key keeps its entry —
a nan is still a malformed config). Tier order and value provenance
documented in the toml comments (contract: `contracts/relief-dials.md`).

## 3. Per-scene tier counters (kitty state)

Two `u32` counters carried beside the activity clock, reset when a
scene starts, incremented on serviced ticks of partnered rest and
co-sleep (mutual or drip respectively), `#[serde(default)]` so
pre-change snapshots load as zeros.

Invariant (test-guarded): `mutual_ticks + drip_ticks ≤` serviced-tick
count of the scene; equality exactly when no serviced tick was solo.

## 4. `ActivityEnd` (event, additive)

Existing: `{ kitty_id, activity, started, ended }`, one event per
finished scene, `span = ended − started + 1` (F-031).

Added: `mutual_ticks`, `drip_ticks` — copied from the per-scene
counters at scene end; `#[serde(default)]` on read,
skip-serialized when zero on write (walks and solo naps serialize
exactly as today). One event per scene — span semantics and scene
counting untouched. Contract: `contracts/activity-event-tier.md`.

## 5. The shared mutual predicate (new named function, one definition)

Extracted from `apply_sleep_relief`'s inline check: *the partner is
itself sleeping or resting* (activity matches `Sleeping | Resting`).
Callers after this feature: co-sleep tier pricing, spec-031 warmth
conduction, rest tier resolution. Designated future caller: the
step-3 waterline contagion (with `Activity::partner()` as the partner
surface) — it references this function, never redefines it.
