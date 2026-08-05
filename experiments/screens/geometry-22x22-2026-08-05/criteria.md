# Geometry screen: 22×22 — criteria, fixed before the run (2026-08-05)

Exploratory screen, not a certification. Registered here **before any
eval ran**, following the precedent of
[geometry-screen-24x24-2026-07-31.md](../../exp-001-bc-mappo/results/geometry-screen-24x24-2026-07-31.md).
Nothing below may be edited once results exist; the outcome goes in
`results.md` beside this file.

## Question

The owner is considering shrinking the served world for on-screen
visibility. 20×20 sits outside the training family (variants span
22/24/26) and is therefore extrapolation; 22×22 is inside it. **Can the
currently deployed pair — `e001-a2-s6` (Miso) and `e002-m0-g998-s1`
(Kittybear) — hold their seats on a 22×22 served world?**

## What this screen does NOT answer

- **Cooperative signal.** F-014 already measured that axis and found
  **size22 sub-floor** at 150-world power, against the served 24×24's
  0.0896 — the strongest replication record any world holds here. That
  is scripted dynamics with policy seats neutralized, and it is a
  *world-affordance* result, not a welfare result; but it means a pass
  here must not be read as "22×22 is as good a world." It would mean
  only that the cats stay well on it.
- **Certification.** §8's world is whatever `cloudkitty.toml` says. This
  screen measures a hypothetical.
- Trained-policy probe dynamics, unmeasured as always (F-009: a
  measurement's horizon bounds the failures it can detect; 20k ticks
  cannot see the long-horizon modes of F-010).

## Cited findings

- **F-010** (active) — roster-OOD fragility: an exp-001 policy can
  collapse into idle catatonia when the world stops matching training.
  Geometry is a different axis than roster, but it is the same class of
  risk and the reason this screen exists.
- **F-014** (active) — the served world wins the knob search as it
  stands; size22 sub-floor. Scope note above.
- **F-009** (active) — horizon bounds detectable failure.

## Design

Paired, single-variable. Both geometries run **in this same batch on
the current engine**, so the 24×24 arm is a control rather than a
historical reference (the engine has moved since 2026-07-31: stamp
`12bf386241…`).

- Artifacts: `policies/e001-a2-s6.ckpolicy` (`8030b94d…`) and
  `policies/e002-m0-g998-s1.ckpolicy` (`1cb3fdac…`).
- Worlds: `configs/cloudkitty-{22x22,24x24}-screen.toml`, generated from
  the served `cloudkitty.toml`, differing from each other in **exactly**
  `width`/`height` and from the served config in **exactly** the two
  policy seats (reverted to `needs_driven`) and the two `[rl.policy.*]`
  blocks (dropped) — kitty-eval seats the subject itself.
- Shape: `--seeds 330001..330010 --ticks 20000 --roster both`
  (certification shape; both roster modes).
- 2 artifacts × 2 geometries = 4 sweeps × 10 seeds × 2 rosters.

**Seed disjointness**: band 330_001–330_010 is unused. Training episode
seeds are ≥1e6; in-training probes 40_001–40_003; exp-002 eval shapes
hold 100k (i), 200k (ii/H3), 300k (iii), 310k (roster3), 320k
(roster5); exp-001 rollout collection used 400k/500k bands. 330k
touches none of them.

## Pass criteria (all must hold at 22×22)

1. **Welfare bounds PASS in all 20 runs** (10 seeds × 2 rosters), for
   both artifacts — kitty-eval's own gate.
2. **Zero guardrail incidents**: `max_low_streak` 0, `low_share` 0.00%,
   `floor_touches` 0, `fallback_count` 0, in every run. Any nonzero
   value fails the screen outright — this is the F-010 tripwire.
3. **Direction holds**: each artifact's AllSubject delta positive in
   ≥ 9 of 10 seeds.
4. **No collapse**: for each artifact, mean AllSubject delta at 22×22
   ≥ (mean at 24×24 in this batch) − 0.010. Rationale for the margin:
   the observed 32×32 → 24×24 geometry effect was +0.0032 with a
   seed-to-seed range of roughly ±0.0015, so 0.010 is ~3× the largest
   geometry effect on record and comfortably outside noise, while still
   catching a real erosion.
5. **Instrument sanity**: the `needs_driven` baseline anchor at 24×24
   lands in the 0.906–0.908 band recorded post-025. Outside it, the
   screen is void and the instrument is the suspect, not the geometry.

## Verdict rule

All five hold → 22×22 is safe for the deployed pair, and the decision
becomes a product one (visibility gained vs F-014's signal cost vs the
`--fresh` world reset a geometry change forces). Any failure → 22×22 is
not a drop-in; the clean route is putting the target geometry into
exp-003's family, which retrains from scratch anyway.

**Not a deployment authorization either way.** A geometry change
invalidates the snapshot and requires `--fresh` (per c77fb97's deploy
note), which resets the live world and the soak clock.
