# Research: Worldgen Placement (spec 027)

Phase 0 output. Every anchor verified in this worktree (branch
`027-worldgen-placement` at f602114, stacked on 026). The three
mechanism decisions the plan commits to, plus the verified facts that
ground them.

## R1 — The lake is an obligation of `ensure_minimums`, formulated as square-completion

**Decision**: `ensure_minimums` gains a water-specific first step,
running before the ordinary top-up whenever
`config.elements.water.min >= 4`: if no 2×2 all-water square exists,
choose an **anchor** — a position whose 2×2 square consists only of
tiles that already hold water or are free — and spawn water onto the
square's free tiles. Anchor choice (revised per analyze finding U1):
every anchor overlapping existing water joins the candidate set
deterministically (consuming no RNG draws), so a damaged lake is
always in the running and in-place completion is structural, not
luck-of-the-sample; `spread_candidates` fresh anchors are then sampled
through the master RNG. The best candidate wins by (fewest missing
tiles, then — only while `edge_penalty > 0` (analyze finding I2) —
fewer perimeter tiles, ties by earliest draw). If no valid anchor
exists, the obligation carries to the next environment phase, exactly
like an unmet minimum. Lake spawns are ordinary water
elements and count toward the minimum the ordinary top-up then
completes.

**Rationale**:
- `World::generate` (world.rs:117) and `environment_phase`
  (world.rs:734) both already route through `ensure_minimums`, so one
  home covers generation and TTL re-formation with zero new call
  sites.
- *Square-completion* (tiles may be water-or-free, spawn only the
  missing ones) is what makes re-formation natural: a TTL lake that
  lost one tile is completed in place (its anchor has 1 missing tile,
  beating fresh 4-missing anchors), instead of a second lake
  materializing elsewhere while three orphaned tiles linger. At
  generation every anchor is 4-missing and the choice falls to the
  interior preference — the same rule serves both moments.
- Carry-over reuses the existing "no room means no spawn" semantics
  (`spawn.rs:20-23` break) rather than inventing a second obligation
  mechanism.
- The safeguard path (`spawn.rs:35-48`) is not touched; Article I
  relief cannot be delayed by lake work (it runs after
  `ensure_minimums` in the same phase, and lake spawns can only *add*
  water, never consume the safeguard's options).

**Alternatives considered**:
- *A lake flag in worldgen only* (no maintenance): simpler, but a
  TTL-water world silently loses the guarantee the spec states, and
  the restock path is where population obligations already live.
- *A multi-tile lake element*: rejected in the handoff itself — it
  would touch element identity, observation slots, and pathing for no
  behavioral gain over four adjacent ordinary elements.
- *Exhaustive best anchor (no sampling)*: deterministic and simple,
  but biases the lake to a fixed scan order's first-best and does more
  work; sampling through the master RNG matches the house pattern and
  keeps the lake's position seed-varied.

**Threshold fact**: engine-default water min is **5**
(`config/mod.rs:369`, not the shipped TOML's 8), so both the engine
default and the shipped world activate the guarantee; the frozen
`scarcity.toml` (min 1) never does — verified, its water rules at
evals/v1/scarcity.toml:63.

## R2 — The interior preference is a score penalty, not a draw change

**Decision**: `best_spread` scoring becomes
`score = gap − edge_penalty` for perimeter candidates (gap unchanged
for interior ones), where `gap` is today's nearest-same-type Chebyshev
distance and `edge_penalty` is the new config knob (f32 tiles,
default 2.0, 0 disables). The "no same-type elements yet" early return
(`pick_spread_tile:132-135`) joins the same scoring with gap treated
as equal for all candidates — so with a zero penalty the earliest draw
still wins (today's exact behavior), and with a positive penalty the
first *interior* draw wins.

**Rationale**: the candidate draw at `pick_spread_tile:117-123` is
deliberately unconditional — the comment says the RNG draw count must
not depend on world contents, and Article V leans on that. A scoring
penalty consumes zero draws, so seed-reproducibility of the draw
sequence is structurally preserved and `edge_penalty = 0` is
*provably* identical to today (same draws, same tie rule — pinned by
a dedicated identity test). A rejection/re-draw scheme would both
spend draws contents-dependently and be able to fail; a hard filter
would violate preference-never-constraint.

**Default = 2.0, and how it was sized**: on the shipped 24×24 world
the perimeter is 92/576 ≈ 16% of tiles; typical nearest-same-type
gaps at the shipped populations (5–10 elements of a type) run well
above 2, so a 2-tile penalty flips ties and near-ties toward the
interior without overriding a strong spread advantage — drift, not
cordon, per the spec's assumption. The magnitude is config, explicitly
owner-tunable, and `experiments/screens/` measures its welfare effect
on the merged engine before anything else leans on it. SC-002's
aggregate perimeter-share test is the empirical check that 2.0
actually moves the distribution.

## R3 — The dials move to `[elements]` table scalars

**Decision**: `ElementsConfig` gains three fields —
`spread_candidates: usize` (default 8), `ttl_jitter: u64` (default
100), `edge_penalty: f32` (default 2.0) — serde-defaulted so every
existing config parses unchanged. `pick_spread_tile` and
`jittered_ttl` take the values from config (spawn.rs's two `const`s
deleted); the fixed-size candidate array becomes a small Vec sized by
the knob. Validation: `spread_candidates >= 1` (0 would select from
nothing), `edge_penalty` finite and `>= 0`, `ttl_jitter` bounded to fit the
32-bit RNG draw (2·jitter+1 ≤ u32::MAX — a bound the old `const 100`
never needed but a free u64 knob does; the floor-at-1 math is
otherwise total). Lake feasibility check: when the guarantee is active,
`width >= 2 && height >= 2` — explicit even though existing
world-size floors already imply it, so the invariant survives a
future floor change.

**Rationale**: all three knobs govern element placement/expiry — the
section an operator already reads. Table-level scalars beside the
per-type sub-tables are valid TOML and mirror how `[behavior]` mixes
scalars. Keeping defaults identical (8, 100) preserves draw counts
and values bit-for-bit; the only behavioral deltas in this spec are
the lake step and a nonzero default `edge_penalty` — both intended.

**Alternatives considered**: a new `[spawn]` section — cleaner
taxonomy, but it splits element-placement knobs across two sections
and forces every reader to learn a new heading for three keys;
rejected as footprint over function.

## R4 — What the stamp and the family-stability check will do (facts)

`ElementsConfig` is `Serialize`, so three new fields move
`engine_defaults_sha256` (the 026 review already recorded the batch
re-baseline plan; this is the second and final move). The exp-002
family byte-stability check will flag regenerated worlds — the lake
and any nonzero edge penalty change the master-RNG consumption per
spawn even at identical dial values. Expected, documented in the spec,
and pinned to the old engine's results; nobody re-runs those.

## R5 — What stays deliberately untouched

- `safeguard` (spawn.rs:35): byte-untouched.
- Element budgets: every `min`/`max` in every shipped config —
  untouched (handoff §3d; screens first).
- Item 3b: not built; the spread *preference* design note in
  `pick_spread_tile`'s doc comment stays authoritative.
- `best_spread`'s tie determinism ("earliest drawn candidate wins",
  spawn.rs:141-143): preserved under the new scoring, and the
  existing tie test keeps passing unmodified.
