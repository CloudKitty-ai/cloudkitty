# Scarcity screen: fewer resources for a less cluttered world — criteria, fixed before the run (2026-08-05)

Exploratory screen, not a certification. Registered **before any eval
ran**, same discipline as the [22×22 geometry
screen](../geometry-22x22-2026-08-05/criteria.md).

## Question

The owner wants the served world visually less cluttered and proposes
lowering element minimums: **water 8 → 6, chow 8 → 6, bug 4 → 3.**
Does the deployed pair — `e001-a2-s6` (Miso) and `e002-m0-g998-s1`
(Kittybear) — stay well on the sparser world?

## Why `min` is the right knob (verified in code before designing this)

`World::generate` calls `spawn::ensure_minimums`, which tops each type
up to `rule.min` **and no further**. `rule.max` is read *only* by config
validation (`max > hard_max`, `min > max`) — no simulation code consults
it. So the world's standing population is exactly the minimums; lowering
`max` would change nothing.

Standing element tiles: **26 → 21** (water 8→6, chow 8→6, bug 4→3,
greeble 1, sunbeam 5 unchanged) — a 19% declutter. The screen verifies
this empirically rather than trusting the arithmetic.

The one thing that can exceed `min` is `spawn::safeguard`, which spawns
food or water when a kitty is actually in need, "deliberately past the
configured maximum if it comes to that." That is the constitutional
backstop, and it is why this change cannot starve anyone — but it also
means a too-sparse world shows up as *more safeguard firing and more
travel*, not as famine. Welfare erosion is the thing to watch, not
collapse.

## Design

Paired and single-variable, at the served 24×24 geometry. Control and
variant differ in **exactly the three `min` lines** (verified by diff).

- Artifacts: `policies/e001-a2-s6.ckpolicy` (`8030b94d…`),
  `policies/e002-m0-g998-s1.ckpolicy` (`1cb3fdac…`).
- Worlds: `configs/{control,scarce}-24x24.toml`, both derived from the
  geometry screen's 24×24 config (served config with the two policy
  seats neutralized and the `[rl.policy.*]` blocks dropped).
- Shape: `--seeds 340001..340010 --ticks 20000 --roster both`.
- 2 artifacts × 2 worlds = 4 sweeps.

The control re-runs on this fresh seed band rather than reusing the
geometry screen's 330k numbers, so both arms are seed-matched. These are
exploratory screens outside the exp-002 prereg; the evaluate-once ledger
governs registered candidate evaluations, not these.

**Seed disjointness**: 340_001–340_010 is unused. Training ≥ 1e6;
in-training probes 40_001–40_003; exp-002 shapes 100k/200k/300k/310k/
320k; exp-001 collection 400k/500k; geometry screen 330k.

## Pass criteria (all must hold on the scarce world)

1. **Welfare bounds PASS in all runs**, both artifacts.
2. **Zero guardrail incidents**: `max_low_streak` 0, `low_share` 0.00%,
   `floor_touches` 0, `fallback_count` 0, `max_distress_age` 0, in every
   run including baselines. Same F-010 tripwire; same outright fail.
3. **Direction holds**: each artifact's AllSubject delta positive in
   ≥ 9 of 10 seeds.
4. **No collapse in delta**: scarce mean AllSubject delta ≥ control mean
   − 0.010 (margin as in the geometry screen).
5. **No material welfare erosion (new, and the one that matters here)**:
   scarce mean AllSubject **subject team welfare** ≥ control mean
   − 0.005 absolute. Delta alone is insufficient for this change:
   scarcity moves the baseline too, so a flat delta could mask everyone
   being worse off. Margin is ≈ 5× the observed seed-to-seed spread in
   subject welfare.
6. **Instrument sane**: `needs_driven` baseline on the *control* world
   lands in the registered 0.906–0.908 band.

Baseline welfare on the scarce world is **reported, not gated** — a
sparser world legitimately lowering the scripted baseline is the knob
working, not a failure.

## Also recorded (not pass/fail)

- Realized element counts on both worlds, measured by generating each
  world through the Python binding, to confirm 26 → 21.
- **Prediction, for exp-003's benefit**: fewer water tiles should lower
  the in-water share, since wading is largely accidental traversal.
  Not measured here (that needs the `dial_resolution` instrument, a
  different shape); flagged so it can be checked deliberately rather
  than discovered.

## Cited findings

- **F-010** — roster-OOD fragility; the tripwire this screen watches.
- **F-014** — the post-024 world search found **scarcity now hurts or
  does nothing** on cooperative signal (it was a pre-024 winner via
  F-005's scarcity×tempo). Two notches of scarcity were searched and
  did not beat the served world. As with geometry, a welfare pass here
  says nothing about the signal axis, where the evidence already leans
  against this change.
- **F-009** — a measurement's horizon bounds the failures it can detect.

## Verdict rule

All six hold → the sparser world is safe for the deployed pair, and the
choice is a product one (visual calm vs F-014's signal evidence vs the
`--fresh` reset that any world change forces). Any failure → keep the
current budget, or take the declutter into exp-003's family where it can
be trained for rather than screened.
