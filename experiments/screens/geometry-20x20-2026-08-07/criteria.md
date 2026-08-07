# 20×20 screen: the owner's chosen shrink — criteria, fixed before the run (2026-08-07)

Exploratory screen, not a certification. Registered **before any eval
ran**, same discipline as the [22×22 geometry](../geometry-22x22-2026-08-05/criteria.md)
and [scarcity](../scarcity-2026-08-05/criteria.md) screens.

## Question

The owner picked a 20×20 world at water 7, chow 5, bug 3, sunbeam 4,
greeble 1 — **"optD"** — after viewing four candidates live. Does the
deployed policy `e003-m0-g998-s3` stay well on it, and how does it
compare with the served 24×24?

## What actually changes

| element | control 24×24 | optD 20×20 | |
|---|---|---|---|
| water | 8 | 7 | −1 |
| chow | 8 | **5** | **−3** |
| bug | 4 | 3 | −1 |
| sunbeam | 5 | 4 | −1 |
| greeble | 1 | 1 | — |
| **standing tiles** | **26** | **20** | −23% |

Area falls 31% (576 → 400) while elements fall 23%, so **element density
*rises* 11%** (4.51% → 5.00%) and free space per cat falls 31%
(136.5 → 94.0). The measured walk mostly improves, though: mean
Chebyshev steps to the nearest water −12%, chow −8%, sunbeam −22%, but
**bug +14%** — the only element that gets harder to reach.

Both configs are the served config with the policy seats neutralized and
no `[rl.policy.*]` blocks; the artifact is seated by `--artifact`, per
the prior screens' pattern. Kitty starts scale with the world (Biscuit
begins at (20,18), off a 20-wide board otherwise).

## Two named risks, registered in advance

1. **Chow takes the deepest cut (−37%), and eat is the failure mode this
   generation actually has.** exp-003's §9.2 analysis found six of nine
   candidates whose entire blemish was brief eat-timing lapses, and eat
   dominated every collapse
   ([grid-2026-08-07.md](../../exp-003-water-schema/results/grid-2026-08-07.md)).
   The shorter walk to chow (−8%) offsets some of it. This is the number
   most likely to move.
2. **Bugs get 14% farther** and are the play/chase targets carrying the
   strongest cooperative credit signal (F-015: play/chase rose 6.3×
   post-025 and is the largest class). Recorded, not gated — this screen
   has no instrument for cooperative credit, and inventing one after
   seeing the data would be worthless.

## Design

Paired, single-variant-cluster (geometry and element budget move
together — that is the product change; this screen cannot attribute a
result to either alone, and does not try).

- Artifact: `policies/e003-m0-g998-s3.ckpolicy` (`756aa680…`) — the
  deployed policy, i.e. the thing that will actually run.
- Worlds: `configs/{control-24x24,optd-20x20}.toml`.
- Shape: `--seeds 770001..770030 --ticks 20000 --roster both`.
- **Seed disjointness**: 770k is unused. Training ≥ 1e6; collection
  600_001–614_004; in-training probes 40_001–3; exp-003 shapes
  700k–730k; water band 740k; cross-world diagnostic 750k; water-tile
  check 760k; exp-002 shapes 100k–320k; earlier screens 330k/340k;
  exp-001/002 collection 400k/500k.

## Pass criteria (all must hold on the 20×20 world)

1. **Welfare bounds PASS in all runs**, both rosters.
2. **Zero guardrail incidents on the variant**: `max_low_streak` 0,
   `low_share` 0.00%, `floor_touches` 0, `fallback_count` 0,
   `max_distress_age` 0. The bar is "no worse than today" — this policy
   scores a clean zero on the served world across 30 seeds and both
   deployment shapes, so any nonzero value here is a regression caused
   by the world change, not a brittle threshold. *(If the **control**
   shows a nonzero value the screen is void and the instrument is the
   suspect, not the geometry.)*
3. **Direction holds**: AllSubject delta positive in ≥ 27 of 30 seeds.
4. **No collapse in delta**: optD mean AllSubject delta ≥ control mean
   − 0.010 (the margin both prior screens used).
5. **No material welfare erosion**: optD mean AllSubject **subject team
   welfare** ≥ control mean − 0.005 absolute. Delta alone is
   insufficient — a smaller world moves the baseline too, so a flat
   delta could hide everyone being worse off. This is the criterion the
   scarcity screen came closest to failing (76% of its allowance).
6. **Instrument sane**: the `needs_driven` baseline on the **control**
   lands in **0.9039–0.9054**, the band re-baselined for this engine on
   2026-08-06. *(The old 0.906–0.908 band belongs to a world that no
   longer exists; using it would void this screen on a healthy
   instrument.)*

## Also recorded (not pass/fail)

- **The water band on the 20×20 world**, measured with the §9.1
  instrument. exp-003 certified this policy at 24×24 with 8 water tiles;
  optD has 7 in a smaller world. Registered prediction: **in-water share
  rises**, because the world is denser in water per unit area (1.75% of
  tiles vs 1.39%) even though the count falls. If it rises past
  `1.5 × B` measured *on the same world*, that is a finding about the
  geometry, not about the policy.
- Distress by need on both worlds, so criterion 2's outcome can be read
  against risk 1 rather than guessed at.
- Realized element counts and lake presence on both worlds.

## Verdict rule

All six hold → optD is safe for the deployed policy and the choice is a
product one. Any failure → report which, and do not ship on the strength
of the live viewing alone. **A `--fresh` is required either way**
(geometry and element changes invalidate the snapshot), which also
retires the 11-tile lake-retrofit artifact the current world carries.
