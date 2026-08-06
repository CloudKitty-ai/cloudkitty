# Data Model: Worldgen Placement (spec 027)

## 1. New configuration keys (`[elements]` table scalars)

| Key | Type | Default | Bounds (validated) | Meaning |
|---|---|---|---|---|
| `spread_candidates` | integer | 8 | ≥ 1 | best-of-N width for every spawn placement draw (was code constant `SPREAD_CANDIDATES`) |
| `ttl_jitter` | integer (ticks) | 100 | ≤ 2147483646 (must fit the 32-bit RNG draw; floor-at-1 math is otherwise total) | ± half-width applied to every timed spawn's TTL (was code constant `TTL_JITTER`) |
| `edge_penalty` | number (tiles) | 2.0 | finite, ≥ 0 | subtracted from a perimeter candidate's spread score; 0 disables the interior preference exactly |

Serde-defaulted: every existing config (including all frozen exams)
parses unchanged. All three serialize → `engine_defaults_sha256`
moves (planned, batch-wide).

## 2. The lake invariant

**Active** iff `elements.water.min >= 4`.

**Invariant**: at the end of any environment phase in which room
allowed, at least one anchor position `(x, y)` exists with water
elements on all of `(x,y) (x+1,y) (x,y+1) (x+1,y+1)`.

**Placement step** (inside `ensure_minimums`, before the water
top-up):

1. If a 2×2 all-water square exists → done (the default-world steady
   state: permanent water, one cheap check per phase).
2. Valid anchors = positions whose 2×2 square contains only
   water-or-free tiles (square must fit inside the map).
3. Candidates = every anchor overlapping existing water (appended
   deterministically, zero RNG cost — a damaged lake is always in the
   running) plus `spread_candidates` fresh anchors sampled via master
   RNG. Score by (fewest missing tiles, then — only while
   `edge_penalty > 0` — fewer perimeter tiles, ties → earliest draw).
   Spawn water onto the winner's free tiles.
4. No valid anchor → obligation carries to the next phase (identical
   semantics to an unmet minimum; nothing evicted or stacked).

**Non-entities**: no lake object, no new element kind, no flag on
water elements — the lake is a *pattern* of four ordinary, passable,
one-per-tile water elements. Observation slots, pathing, wading, and
the 026 wet-fur charge see plain water.

**Interactions**: lake spawns count toward the water minimum (they are
water), so the ordinary top-up places `min − 4` further spread tiles
at defaults. `safeguard` is unchanged and runs after — it can only
ever find *more* water present, never less.

## 3. Spread scoring (one rule, was two branches)

```
score(candidate) = gap(candidate) − (edge_penalty if on perimeter else 0)
gap = nearest same-type Chebyshev distance   (unchanged)
    = equal-for-all when no same-type exists (absorbs today's early return)
winner = max score, ties → earliest drawn    (unchanged tie rule)
```

Perimeter = the outermost tile ring (x or y at 0 or the far edge).
Draw discipline unchanged: exactly `spread_candidates` unconditional
draws per spawn, so `edge_penalty = 0` reproduces today's selection
draw-for-draw — pinned by an identity test.

## 4. Documentation corrections riding along (FR-007)

| Site | Was | Becomes |
|---|---|---|
| `cloudkitty.toml` above `[elements.water]` | "at most floor(width * height / 32) -- 32 for this world" | the arithmetic plus the true current value (18 at 24×24), phrased to survive the next resize |
| `ElementRule.max` docs (`config/mod.rs`) | silent | states `max` is read only by validation; `ensure_minimums` tops to `min` and no further — the standing population IS the minimums; `min` is the real knob |

## 5. Unchanged shapes (asserted, not assumed)

- `ElementRule` fields, all shipped `min`/`max` values, `hard_max =
  area/32` — untouched.
- `Config::fingerprint` — none of the new keys join it; every saved
  world resumes.
- Snapshot format — untouched (elements serialize as before; a lake
  is just four water rows).
- `GET /config` — gains the three keys automatically with the rest of
  `[elements]`.
