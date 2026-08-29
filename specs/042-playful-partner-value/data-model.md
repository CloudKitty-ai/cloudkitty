# Data Model: Playful 2.0 — partner-value play selection

No persisted state, no events, no schema. Three computed quantities,
one candidate pipeline, and twelve config dials.

## 1. Per-candidate quantities (computed per decision tick, never stored)

| quantity | friends | critters |
|---|---|---|
| `value` | `play_need − w_busy·expected_wait − w_serious·top_non_play_pressure` | — (no needs) |
| `score` | `w_value·value − distance` | `critter_appeal − distance` (standalone, unscaled) |
| `expected_wait` | `(scene_min − elapsed).max(0)` from the partner's ActivityClock; 0 if free | — |
| `top_non_play_pressure` | max pressure over eat/drink/sleep/cuddle/bath (play excluded) | — |

`distance` = Manhattan distance as f32 (exact for grid sizes).

## 2. The candidate pipeline (replaces the min-by-distance pick)

1. **Admission**: free friends + critters always (today's exact set);
   mid-scene friends iff `w_value > 0` (plan §Complexity; research
   D2). Chase-excluded and stalled-pursuit targets never admitted
   (unchanged `is_viable` bookkeeping).
2. **Eligibility (friends only — clarify ruling 1)**: all friends
   dropped when own `play_need < t_self`; each friend dropped when
   its `value < t_partner`. Critters are never filtered here.
3. **Ranking**: max by `score` (`f32::total_cmp`); ties by the
   existing ascending `(distance, tag 0=critter/1=friend, id)`.
4. **Empty result** → the existing solo backstop.

At all-identity defaults: admission = today's set, no friend
filtered, every score = `−distance` → today's order bit-for-bit.

## 3. Acting on the pick (`play_action_with`)

| pick state | action |
|---|---|
| adjacent + free (or critter) | `play_with` (proposal — only ever toward free partners, FR-004) |
| adjacent + mid-scene kitty | `play_solo` this tick — waiting is spent playing, never proposing, never idle (research D5) |
| non-adjacent | `Chase` (unchanged, incl. etiquette/urgent-solo rules) |
| none | `play_solo` |

## 4. The weighted get-serious trigger (playful only)

`max over NeedKind::ALL of comfort_weight(kind) · pressure(kind) >= playful_comfort`
— replaces the unweighted `highest_pressure()` comparison at
`playful.rs:56-64`. Trigger-only: the serious cat's selection, every
other behavior, and all engine welfare machinery read unweighted
needs (verified: the need identity was already discarded there).

## 5. The dial family (all on `[behavior]`, all skip-at-identity — stamp unmoved)

| dial | identity default | meaning | validation |
|---|---|---|---|
| `w_value` | 0.0 | friend value multiplier in score; also the busy-friend admission switch (> 0) | finite, ≥ 0 |
| `w_busy` | 0.0 | expected-wait penalty per tick | finite, ≥ 0 |
| `w_serious` | 0.0 | top non-play pressure penalty | finite, ≥ 0 |
| `t_self` | 0.0 | own play need floor for bothering any friend | finite, ≥ 0 |
| `t_partner` | 0.0 | per-friend value floor for eligibility | finite, ≥ 0 |
| `critter_appeal` | 0.0 | standalone critter score offset | finite (either sign) |
| `comfort_weight.{eat,drink,sleep,play,cuddle,bath}` | 1.0 each | per-need multiplier inside the playful get-serious trigger only | finite, ≥ 0 |

Serialization: every field `skip_serializing_if` at its identity, so
`Config::default()` serializes byte-identically to today and
`engine_defaults_sha256` does not move (spec-039 pounce discipline).
Served `cloudkitty.toml`: commented documentation block only, no keys.
