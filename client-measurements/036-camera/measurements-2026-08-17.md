# Camera mode: what was measured, headless (2026-08-17)

Against the live served world on the 036 branch, using the shipped
`Camera` class rather than a model of it. Nothing here needed a browser.

## SC-006 — anchor changes per minute (bar: <= 3)

Three samples, and they disagree enough that one is not a verdict:

| window | ceiling bound | anchor changes/min | visible/min |
|---|---|---|---|
| 5.0 min | not recorded | 7.60 | not recorded |
| 2.5 min | 84.1% | 2.40 | 1.60 |
| **9.5 min** | 43.1% | **5.79** | **2.42** |

**The criterion does not say which quantity it means.** Below the ceiling
the aim is the centre of mass, so an anchor change moves nothing and
cannot read as restless. On the purpose clause ("reads as deliberate
rather than restless") the visible rate is the one that matters and the
9.5-minute sample passes at 2.42. Read literally, 5.79 fails.

It is marginal either way: at the 84%-bound spread seen in the 2.5-minute
window, the visible rate scales to roughly 4.9/min and fails.

## Hysteresis sweep (376 recorded ticks, 64% bound, replayed)

| hysteresis | anchor changes/min | visible/min |
|---|---|---|
| **1.5 (shipped)** | 4.20 | **3.00** |
| 2.0 | 2.40 | 1.40 |
| 2.5 | 2.00 | 1.00 |
| 3.0 | 1.20 | 0.80 |
| 4.0 | 0.80 | 0.40 |

The shipped value landed exactly ON the bar with no margin. **Raised to
2.0 by the owner, 2026-08-18**, which takes the LITERAL count to 2.40/min
and the visible count to 1.40/min. Her reasoning is worth keeping: an
invisible anchor change today becomes a visible one the moment something
makes the anchor drive the aim more often, and that regression would
arrive with no obvious cause. So SC-006 is held against all changes, not
only the ones that currently show.

## How often the ceiling binds

43% over 9.5 minutes, 64% and 84% over shorter windows. An earlier
57-tick sample showed 0% and I generalised from it that "the ceiling
never binds" -- that was wrong. The clowder gathers and scatters, so the
anchor is load-bearing far more often than that sample suggested.

## Camera stillness

The aim moves >1px on 60% of ticks, so the camera is still 40% of the
time. Earlier deadzone modelling predicted 78% still, and the two are NOT
comparable: that measured the TARGET with no easing, this measures the
eased aim. The deadzone stops the target chasing; the easing tail still
creeps toward it.

**A second lever exists if more stillness is wanted**: snap the aim to
its goal once it is within a small epsilon, which kills the tail without
touching the deadzone or the rates.

## Bake counts (SC-003's diagnostic half)

Across a full zoom sweep with panning, in `test-meadow.mjs`:

- ground bakes: **1**
- pond layer builds: **1**
- distinct bake tiles: **1**

Keyed to the live zoom instead (the naive implementation): 121 rebakes
and 77 distinct tiles. So the per-frame ground cost is one `drawImage`,
which is what SC-003 needs. **The frame-rate half still needs a browser.**

## FR-022 roster sweep

900 states across 3-, 4- and 5-kitty rosters on deterministic walks. The
zoom floor, the ceiling, finite aim, the world clamp (FR-029) and a real
anchor hold at every one. SC-010's aesthetic judgement still needs the
owner's eye.

## Containment, with the centre-of-mass aim (2026-08-18)

301 ticks. While the FIT governs, **100%** of ticks hold every kitty, with
a worst overhang of 0.00 tiles. While the CEILING binds, 11.4% hold
everyone — which is FR-005 working, not failing: past the ceiling the
camera stops fitting and lets the wanderer go.

This is what sent SC-005 back to the owner, and she reworded it to the
thing that actually matters: never a frame with NOBODY in it. That now
holds by construction (the aim is a kitty whenever the ceiling binds, and
the clamp can only push the frame to the world's edge, not past her) and
is asserted across all 900 swept roster states.
