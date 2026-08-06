# Contract: Worldgen Guarantees (spec 027)

What the world promises about element placement from this spec
forward. "Promise" means test-pinned and relied upon by watchers,
learners, and Experiments' measurement stack alike.

## G1 — The lake guarantee

- A world whose configured water minimum is ≥ 4 contains, whenever
  room has allowed, at least one 2×2 square of water tiles. At
  generation, room always allows (an empty board bigger than 2×2).
- Below the threshold the guarantee is **silently inactive** — never a
  validation error. Frozen exams with sparse water (`scarcity.toml`,
  min 1) validate and run exactly as before.
- The guarantee is maintained, not just installed: if configured water
  TTLs break the square, the restock path re-forms it — preferring to
  *complete* the damaged square over building a new one elsewhere —
  under the same carry-over semantics as unmet minimums.
- Lake tiles are ordinary water: passable (wading semantics and
  Article I reachability unchanged), one element per tile, priced by
  the 026 wet-fur charge like any wet tile, drawn by the pond renderer
  like any adjacent water.

## G2 — The interior preference

- Ordinary spawn placement penalizes perimeter candidates by
  `edge_penalty` (config, default 2.0 tiles) inside the existing
  best-of-N scoring. It is a preference: some candidate always wins,
  and a spawn still lands on the perimeter when the perimeter is all
  that's free or its spread advantage outweighs the penalty.
- `edge_penalty = 0` restores pre-027 placement **exactly** — same
  RNG draws, same tie rule, same tiles.
- The Article I safeguard path is outside this contract's blast
  radius: untouched, unweighted-by-lake, and never blockable.

## G3 — Determinism and the draw sequence

- Every placement draw flows through the master RNG; same seed + same
  config → same world, lake position included.
- The per-spawn draw *count* in ordinary placement is a function of
  config alone (`spread_candidates`), never of world contents. The
  lake step is the exception: a standing lake draws nothing, so its
  per-phase draw count is a deterministic function of world state —
  determinism holds because that state is itself a pure function of
  seed and config, not because the count is fixed. Replay tooling
  must not assume a fixed per-phase draw budget in timed-water worlds.
- Relative to pre-027 engines, seeded worlds differ (the lake step
  consumes draws; the penalty changes selections). This is a
  documented generation break, re-baselined once for the whole batch
  (handoff §4) — not a regression, and the exp-002 family
  byte-stability flag it trips is expected.

## G4 — Configuration surface

- `[elements] spread_candidates / ttl_jitter / edge_penalty` exist,
  carry the documented defaults (8 / 100 / 2.0), validate their bounds
  at startup (count ≥ 1; penalty finite ≥ 0), and appear on
  `GET /config`.
- Element `rule.max` remains validation-only, now documented as such
  where operators read; `min` is the population knob. No budget value
  changes in this spec.

## Not contracted

- Lake count (at least one; more may arise by chance), lake position,
  or lake persistence at a fixed location across re-forms.
- Any perimeter-share number beyond "measurably below area share at
  defaults" — the magnitude is a tunable, not a promise.
- Rivers, geometry changes, budget changes — out of scope (spec §Out
  of Scope).
