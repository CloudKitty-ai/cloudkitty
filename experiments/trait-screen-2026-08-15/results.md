# Trait exchange rates, stage 1: scripted marginal cost curves

**2026-08-15** (ROADMAP v2 phase 0). 6 needs × factors {0.5, 0.75,
1.5, 2.0}× default, Miso carrying, trait-flat base (Pumpkin's
override removed), all-scripted, 10 paired seeds × 20k vs control.
Raw: `results-raw/screen.json`. Control: carrier 90.96, team 90.91.

## Carrier happiness delta vs trait-flat (the cost curves)

| need (default) | 0.5× | 0.75× | 1.5× | 2× | ~cost/unit-rate (raising) |
|---|---|---|---|---|---|
| cuddle (0.4) | **+0.76** | +0.29 | −0.58 | **−1.20** | **~3.0 — priciest** |
| eat (0.4) | +0.71 | +0.28 | −0.50 | −1.03 | ~2.6 |
| sleep (0.3) | +0.62 | +0.23 | −0.49 | −0.85 | ~2.8 |
| play (0.4) | +0.55 | +0.24 | −0.46 | −0.79 | ~2.0 |
| drink (0.4) | +0.58 | +0.21 | −0.36 | −0.75 | ~1.9 |
| bath (0.2) | +0.32 | +0.15 | −0.31 | −0.53 | ~2.6 |

Team deltas ≈ carrier/4 throughout (dilution + mild contention
externality on eat). **Zero distress in every cell** — the whole
[0.5×, 2×] envelope is constitution-safe scripted-side. Curves are
mildly convex (buying down gains more per unit than raising costs).

## The surprise: cuddle is the priciest axis (scripted company)

Not eat. Cuddle relief requires a willing adjacent partner, and
scripted company cosleeps rarely (7.5% of sleep) — a high-cuddle cat
among scripted cats waits for service that seldom comes. **This is
exactly the rate stage 2 will move most**: the deployed world
cosleeps 87% of sleep, so cuddle-rise should be far cheaper in
policy company. Clementine's design (cuddle 0.7) MUST wait for the
stage-2 bracket — the scripted number would over-compensate her.

## Provisional balanced vectors (stage-1 rates; verify directly, and
re-derive after stage 2)

- **Pumpkin rebalance**: eat 0.8 (−1.03) + sleep 0.15 (+0.62) +
  bath 0.10 (+0.32) ≈ net −0.09 — "snacky, naps light, always
  tidy." Inside the parity band pending direct verification.
- **Clementine sketch** (stage-1 rates only): cuddle 0.7 (≈ −0.88
  interpolated) + play 0.2 (+0.55) + drink 0.3 (+0.21) ≈ −0.12 —
  "affectionate, mellow, light drinker." EXPECTED TO CHANGE at
  stage 2 (see above).

Next: stage 2 (same sweep bracketed under current policies — cuddle
and bath are the axes to watch), then direct verification of chosen
vectors (additivity is a hypothesis), then the exchange table
freezes into the phase-1 design inputs. Scope stamps: engine
412d00e2…, served 20×20 geometry, scripted company; all rates mortal
on any of those moving.
