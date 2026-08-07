# optE 20×20 — all six criteria pass; it beats the world it replaces

Run 2026-08-07 against [criteria.md](criteria.md), committed (`a17d8a3`)
before any eval on the 800k band executed. Artifact `e003-m0-g998-s3`
(`756aa680…`), 30 seeds × 20k, engine `cba976da…`.

**optE = 20×20, water 7, chow 6, bug 3, sunbeam 4, greeble 1** — 21
standing tiles, one chow more than the optD the previous screen found
wanting.

## Verdict: PASS, 6/6 — and optE is better than the 24×24 on every gated measure

| criterion | control 24×24 | optE 20×20 | |
|---|---|---|---|
| **A** deployed composition, seeds with a threshold crossing | **1/30** | **0/30** | **PASS** |
| **B** all-subject stress: incident runs / worst distress | 2/60 · 107 | 1/60 · **6** | PASS |
| **C** subject welfare [all-subject] | 0.9468 | **0.9471** | PASS (+0.0003) |
| **D** paired delta positive | 30/30 | **30/30** | PASS |
| **E** `needs_driven` baseline (control) | **0.9047** | — | PASS (0.9039–0.9054) |
| **F** water band, B per world | 84.5% of B | **79.0% of B** | PASS |

Welfare on the mixed roster: 0.9150 → **0.9170**. Zero `floor_touches`
and zero fallbacks everywhere, both worlds.

## A — the criterion that decides shipping

Measured on the composition that actually runs: the policy at Miso and
Kittybear beside scripted Biscuit (playful) and Pumpkin (needs_driven).
Neither `--roster` flag constructs this, which is why the previous
screen missed it.

**optE: 0 of 30 seeds show any need crossing 90. The control: 1 of 30**
(a 36-tick streak, cuddle 36 / drink 9). optE is not merely acceptable
here — it is cleaner than the world it replaces.

The control's single crossing being **cuddle**, not eat, is worth
noting: with only two policy cats among two scripted ones, the
contention that dominated the all-subject failures disappears and what
surfaces instead is a social need. It is one seed and 36 ticks; recorded,
not interpreted.

## The chow tile was the whole story

Against the previous screen's optD (chow 5), on comparable bands:

| | incident runs | worst distress | welfare [all] |
|---|---|---|---|
| optD, chow 5 | 9/60 | 239 | 0.9441 |
| **optE, chow 6** | **1/60** | **6** | **0.9471** |

One tile. The eat-driven contention criteria.md named in advance as
risk 1 was exactly one chow tile deep, and closing it moved optE past
the 24×24 control rather than merely level with it.

## F — the relative band paid off again

| world | scripted `B` in-water | policy in-water | policy as % of B |
|---|---|---|---|
| control 24×24 (8 water) | 3.435% | 2.902% | 84.5% |
| **optE 20×20 (7 water)** | **4.180%** | **3.304%** | **79.0%** |

**The registered prediction was right and, on its own, misleading.**
In-water rises in absolute terms — 2.902% → 3.304%, +14% — because 7
tiles in 400 is denser water than 8 in 576. An absolute threshold would
have flagged that as a regression.

But `B` rises *more* (+22%), so the policy's position **improves**: from
84.5% of its world's scripted baseline to 79.0%. Lounging is flat
(0.708% → 0.725%) against a baseline that rose from 1.500% to 1.831%.

That is the second time the relative construction has saved a correct
answer from an absolute one — the first was the 11-tile lake retrofit.
Water use measured against the world's own scripted ladder transfers
across worlds; measured against a remembered number it does not.

## Also recorded

**Mean Chebyshev steps to the nearest element** (the walk a cat makes):

| | control 24×24 | optE 20×20 | |
|---|---|---|---|
| water | 4.85 | 4.25 | −12% |
| chow | 3.36 | 3.77 | **+12%** |
| bug | 5.64 | 5.96 | +6% |
| sunbeam | 4.39 | 4.02 | −8% |

Chow is farther in optE despite the extra tile, because these are
*generated* worlds and the control's eight tiles happen to sit well.
It costs nothing measurable: optE's welfare and distress are both
better. Worth remembering that this measure tracked welfare better than
element density did, but neither is a substitute for measuring welfare.

**Element density is a visual metric, not a welfare one.** optE is 5.25%
element density against the control's 4.51% — 16% "busier" by the
arithmetic that has framed this whole discussion — and the cats are
demonstrably better off in it. Density predicts how a world *looks*;
it does not predict how the cats *fare*.

Realized counts, both worlds, with lakes present: control water 8, chow
8, bug 4, sunbeam 5, greeble 1; optE water 7, chow 6, bug 3, sunbeam 4,
greeble 1.

## Recommendation: ship it

All six criteria pass, and optE is better than the served world on the
deployed composition, on welfare in both rosters, on worst-case distress
and on relative water use.

**A `--fresh` is required** — geometry and element changes invalidate the
snapshot. That costs the current world's history and restarts the soak
clock, and it retires the 11-tile lake-retrofit artifact the live world
carries, returning the served world to a canonical generation.

## Regeneration

```
S=$(python3 -c "print(','.join(str(800000+i) for i in range(1,31)))")
D=experiments/screens/geometry-20x20-optE-2026-08-07
for w in control-24x24 opte-20x20; do
  ./target/release/kitty-eval --artifact policies/e003-m0-g998-s3.ckpolicy \
    --config $D/configs/$w.toml --seeds "$S" --ticks 20000 --roster both \
    --json $D/seeds/$w.json
done
# criterion A (deployed composition) and F (water band) drivers are in the
# commit message; per-seed data under seeds/.
```

Seed band 800_001–800_030, disjoint from all others.
