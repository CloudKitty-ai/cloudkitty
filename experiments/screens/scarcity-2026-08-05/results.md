# Scarcity screen: the declutter passes, and it isn't free

Run 2026-08-05 against [criteria.md](criteria.md), committed (`ff6866d`)
before any eval executed. **All six criteria pass** for both deployed
artifacts — but unlike the geometry screen, this one costs measurable
welfare, and it spends most of the margin it was given.

## Setup

`kitty-eval --artifact policies/<a>.ckpolicy --config
configs/{control,scarce}-24x24.toml --seeds 340001–340010 --ticks 20000
--roster both`, engine defaults `12bf386241…`. Control and variant
differ in exactly three lines: `water.min` 8→6, `chow.min` 8→6,
`bug.min` 4→3.

**Declutter confirmed empirically** (generated through the Python
binding, seed 340001):

| world | total | water | chow | bug | sunbeam | greeble |
|---|---|---|---|---|---|---|
| control | **26** | 8 | 8 | 4 | 5 | 1 |
| scarce | **21** | 6 | 6 | 3 | 5 | 1 |

19% fewer standing element tiles, exactly as the `ensure_minimums`
reading predicted.

## Result: six for six, with a real cost

| artifact | world | roster | mean Δ | positive | subject welfare | baseline welfare |
|---|---|---|---|---|---|---|
| `e001-a2-s6` | control | AllSubject | +0.0440 | 10/10 | 0.9505 | 0.9066 |
| `e001-a2-s6` | scarce | AllSubject | **+0.0424** | 10/10 | **0.9467** | **0.9043** |
| `e001-a2-s6` | control | Mixed | +0.0121 | 10/10 | 0.9187 | 0.9066 |
| `e001-a2-s6` | scarce | Mixed | +0.0118 | 10/10 | 0.9161 | 0.9043 |
| `e002-m0-g998-s1` | control | AllSubject | +0.0473 | 10/10 | 0.9539 | 0.9066 |
| `e002-m0-g998-s1` | scarce | AllSubject | **+0.0458** | 10/10 | **0.9502** | **0.9043** |
| `e002-m0-g998-s1` | control | Mixed | +0.0105 | 10/10 | 0.9170 | 0.9066 |
| `e002-m0-g998-s1` | scarce | Mixed | +0.0102 | 10/10 | 0.9145 | 0.9043 |

1. **Welfare bounds PASS** in all runs, both artifacts, both worlds.
2. **Zero guardrail incidents** across all 120 runs including baselines:
   `max_low_streak` 0, `low_share` 0.00%, `floor_touches` 0,
   `fallback_count` 0, `max_distress_age` 0. No cat was ever in trouble.
3. **Direction holds**: 80/80 paired seed comparisons positive.
4. **Delta holds**: −0.0015 for both artifacts, inside the −0.010 margin.
5. **Welfare erosion −0.0038** for both artifacts, inside the −0.005
   margin — but at **76% of the allowance**, the closest call in either
   screen.
6. **Instrument sane**: control baseline 0.9066, inside 0.906–0.908.

## Reading

**The cost is small, consistent, and shared.** Everything drops together
— scripted baseline −0.0022, policy subject −0.0038 — so the policies'
*advantage* is nearly intact (−0.0015) while everyone is slightly less
happy. That is exactly the shape the engine predicts: `spawn::safeguard`
spawns food and water on demand past any configured maximum, so nobody
starves, and the cost surfaces as extra travel rather than distress. The
guardrails confirm it — not one incident in 120 runs.

**It is, however, ten times the geometry effect.** For scale: 24×24 →
22×22 moved subject welfare by +0.0015 (upward); this moves it −0.0038.
Geometry between family sizes is a non-event; the element budget is a
live knob that actually does something. If you want the visual change
that costs the least, geometry is nearly free and this is not.

**The size of the ask matters.** −0.0038 landing at 76% of a margin I
set before seeing data is a pass, not a comfortable one. A deeper cut
(min 4, say) has no screen behind it and should not be assumed to scale
linearly — the safeguard starts carrying more of the load, and the
F-009 caveat applies: 20k ticks bounds what this can see.

**And, as with geometry, the signal axis says the opposite.** F-014
searched scarcity two notches on the post-024 engine and found it
**hurts or does nothing** for cooperative credit — it was a pre-024
winner (F-005's scarcity×tempo) and is not one now. This screen says the
cats stay well on a sparser world; F-014 says the world gets no better
as an instrument, and plausibly worse. Both stand.

## Prediction logged for exp-003

Fewer water tiles should lower the in-water share, since wading is
largely accidental traversal. Not measured here — that needs the
`dial_resolution` instrument, a different shape. Flagged so it gets
checked deliberately rather than discovered: if the declutter ships,
the winner's 5.14% in-water anchor moves and exp-003's baseline moves
with it.

## Recommendation

Shippable, and it's a genuine product call rather than a safety one.
The cats are provably fine. What you're buying is visual calm; what
you're paying is about four thousandths of welfare, a `--fresh` world
reset, and a set of re-measured anchors — against F-014's evidence that
scarcity doesn't help the world's signal.

If it were only about clutter, the cheapest honest answer is that the
five sunbeams and one greeble are untouched here and the declutter is
carried entirely by food, water, and bugs. Worth deciding whether the
*visual* clutter you dislike is actually the chow and water tiles, or
something a client-side rendering change addresses better — the same
question the geometry screen raised.

## Regeneration

```
S=$(python3 -c "print(','.join(str(340000+i) for i in range(1,11)))")
for art in e001-a2-s6 e002-m0-g998-s1; do for w in control scarce; do
  ./target/release/kitty-eval --artifact policies/$art.ckpolicy \
    --config experiments/screens/scarcity-2026-08-05/configs/$w-24x24.toml \
    --seeds "$S" --ticks 20000 --roster both \
    --json experiments/screens/scarcity-2026-08-05/seeds/$art--$w.json
done; done
```

Artifact sha256 `8030b94d…` / `1cb3fdac…`, both unchanged. Per-seed JSON
under `seeds/`. Seed band 340_001–340_010, disjoint from all others.
