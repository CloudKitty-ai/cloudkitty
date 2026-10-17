# Contract: Draw Law v1 (FR-003, FR-004, FR-005, FR-011)

This document is the FR-011 artifact: precise enough that an independent
implementation, given only (seed, dimensions, shares, roster), reproduces the
engine's exact positions. The golden-vector file (§6) is the normative anchor
where prose could be misread. Any change to anything below is a versioned
break: bump `STARTS_LAW_VERSION` and the domain tag together (FR-012).

## 1. Geometry (the coverage instrument's, verbatim)

For a world of `width` w, `height` h (both ≥ 3, enforced at load), a tile
(x, y) with x ∈ [0, w), y ∈ [0, h):

- `on_x_edge` = (x == 0 or x == w−1); `on_y_edge` = (y == 0 or y == h−1)
- **Corner** = on_x_edge AND on_y_edge (exactly 4 tiles)
- **EdgeRing** (non-corner edge) = (on_x_edge OR on_y_edge) AND NOT corner
- **Interior** = NOT (on_x_edge OR on_y_edge)

The three categories are disjoint and cover the grid. (coverage_read.py's
edge-ring *count* includes corners; the draw's EdgeRing category is the
non-corner remainder — the probabilities below reconcile the two exactly as
FR-005 states.)

## 2. Canonical tile order

Everywhere a tile list is enumerated: row-major, y ascending outer, x
ascending inner (linear index y·w + x ascending). Each category's tile list
is the grid in this order, filtered to the category. Removing occupied tiles
preserves this order.

## 3. The sub-stream

```text
seed_bytes[0..8]   = world.seed (u64), little-endian
seed_bytes[8..20]  = the 12 ASCII bytes "ck-starts-v1"
seed_bytes[20..32] = zero
rng = ChaCha8Rng::from_seed(seed_bytes)
```

ChaCha8 as specified by rand_chacha 0.3 (stream 0, block counter from 0).
`next_u64()` = two consecutive 32-bit keystream words, first word = low half
(rand_core's little-endian convention). The engine's master world stream is
never touched: a knob-on world and a knob-off world with explicit starts
equal to the drawn ones are byte-identical over a full run (SC-003).

## 4. The draw

Inputs: shares (f64, as parsed from the toml), the roster sorted by kitty id
ascending, the explicit-start occupied set.

```text
occupied = { (x, y) of every explicit-coordinate kitty }
for kitty in roster (id ascending):
    if kitty has explicit coordinates: continue      # consumes NO draws
    v1 = rng.next_u64()
    u  = (v1 >> 11) as f64 × 2⁻⁵³                    # u ∈ [0, 1)
    category = Corner    if u < corner_share
             = EdgeRing  else if u < edge_ring_share
             = Interior  otherwise
    free = category tile list (canonical order) minus occupied
    if free is empty: FAIL naming category, kitties drawn into it, capacity
    v2 = rng.next_u64()
    tile = free[v2 mod len(free)]
    occupied += tile
```

Properties the law fixes (each is a test):

- Every drawn kitty consumes exactly two u64 draws, in kitty-id order;
  explicit kitties consume zero. So the draw is independent of roster FILE
  order, and pinning a kitty explicit never shifts any other kitty's draws
  (it consumes nothing) — it only changes the occupied set.
- P(Corner) = corner_share; P(EdgeRing) = edge_ring_share − corner_share;
  P(Interior) = 1 − edge_ring_share — per kitty, i.i.d. (SC-001's binomial
  check).
- Collision handling is drawing from the CURRENT free list — uniform within
  the category conditioned on earlier placements, terminating by
  construction (the spec's "resample within the category" stated as the
  equivalent closed form).
- `v2 mod len(free)`: modulo over the raw u64 is the law. The ~2⁻⁶⁴·len bias
  is accepted and exactly reproducible; auditability over an immeasurable
  uniformity gain.

## 5. Determinism claims

Same (seed, width, height, shares, roster ids + explicit coords, engine
build) → same positions, any machine, any build mode: the law is integer and
IEEE-754 f64 comparison arithmetic only. File order of `[[kitty]]` tables is
irrelevant (the loop sorts by id). Changing any input changes the draw freely
— only stream isolation (§3) is claimed across configs.

## 6. Golden vectors

`contracts/golden-draws.json`, emitted by an engine test (never hand-written
— recorded real payloads, rule 5): a small set of (seed, dimensions, shares,
roster) cases, each with the expected sequence of raw u64 draws and the final
(kitty, x, y, category) list. A port validates against this file; the
engine's own CI asserts it stays byte-stable, so any accidental law change
reddens before it ships (FR-012's "never silently").
