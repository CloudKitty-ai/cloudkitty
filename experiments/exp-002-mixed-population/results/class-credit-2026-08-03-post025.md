# Class-conditioned credit on the exp-002 family base (post-025)

**Date**: 2026-08-03 · **Engine**: main @ `0fd551d` (spec 025
per-target play relief) · **World**: the frozen family base
(`family/base.toml`) · **Recipe**: identical to the
[post-024 measurement](class-credit-2026-08-02.md) it supersedes —
1,000 samples per class, 150 worlds (seeds 11001–11150), 1,200-tick
traces, probe-seed 42, cluster-robust per F-004 (+150-world
addendum). Run as the registered post-025 re-baseline (handoff
2026-08-02; prediction registered before the spec landed).

| Substituted class | dr sig ticks (fp≈60) | S(.998) | S(.998) post-024 | mass ≤400 | peak |
|---|---|---|---|---|---|
| all actions | 30 (**sub-floor**) | 0.0099 | 0.0387 | 0.20 | k=1182 (trace edge) |
| groom/sleep/rest | 46 | 0.0399 | 0.0334 | 0.80 | @ k=0 |
| eat/drink | 68 | 0.0709 | 0.0333 | 0.59 | 0.0087 @ k=0 |
| play/chase | **43** | **0.0245** | 0.0039 | 0.27 | 0.0026 @ **k=301** |

## Findings

1. **The registered prediction is CONFIRMED.** The falsifiable point
   of spec 025 (handoff + census doc, registered 2026-08-02 before
   the change landed): the play/chase class rises off its 0.1× floor.
   It did — S(.998) 0.0039 → 0.0245 (6.3×), significant ticks 8 → 43,
   real contiguous bands where before there were none, band peak
   k=301 — *inside* γ=0.998's horizon. Substituting one play decision
   now moves team reward because "which play" carries a value
   gradient (bug 25 / greeble 35 / duet 2×20). The change did what it
   was shipped to do.
2. **The pooled all-action batch went sub-floor — by dilution, not
   signal loss.** Every class rose while "all" fell (0.0387 →
   0.0099, 30 sig ticks < fp≈60). Verified mechanism: play/chase
   decision points are the most abundant in the pool (decision-point
   density 0.71) with the smallest per-tick amplitude (+0.0003 vs
   eat/drink's +0.0087, all classes positive-signed — not
   cancellation), so the pooled per-tick mean sinks under the 2·SE
   bar. Consequence for method: **the "vs all" ratio framing is
   retired**; class-conditioned absolute S values are the comparable
   quantities. Pooled all-action probes understate credit whenever
   class amplitudes are heterogeneous (F-015).
3. **Eat/drink credit doubled** (0.0333 → 0.0709). Interpretation
   (unregistered, flagged as such): faster play servicing returns
   cats to the chow/water queues sooner, sharpening consumption
   contention. Whatever the mechanism, eat/drink is now the largest
   single credit channel; §10.1 diagnostics keep it on the watchlist
   **and play/chase re-enters** (it was dropped when sub-floor).
4. **The §3 dormant-γ trigger outcome stands.** Late bands persist
   past k≈500 in the class batches (eat/drink 693–726 and 974–978,
   gsr 778–780, play/chase through 601; all-action edge band
   1178–1184). The F-9985 follow-up cell (registered 2026-08-02 on
   the k=948 peak) remains justified; nothing un-fires.

## Companion re-baseline measurements (same day, same engine)

- **Water calibration re-run** (10 seeds × 20k, served world,
  `results/water-calibration-2026-08-03-post025/`): frozen seats
  lounging 4.14% / in-water 9.21% (post-024: 4.22% / 9.42%),
  scripted 0.31% / 1.63% (0.32% / 1.65%), mean Nash 0.8966 (0.8964).
  The water economy is untouched by 025; §9.1's absolute thresholds
  (1.0% / 3.0%) and anchors carry over.
- **Chase census re-check** (10 seeds × 20k, both worlds):
  needs_driven 6.2/8.2 chase-ticks-per-catch (bug/greeble), playful
  2.4/7.1 — pre-025 within noise (5.9/9.0, 2.4/6.9); duet starts
  within 1%; solo play still zero. The no-behavior-layer-magnitude-
  reader fact held: scripted choice structure did not move.
- **Dataset v2 recollected** on `0fd551d` (registered commands,
  prereg §5): 60 rollouts, 1,908,182 decisions (was 1,907,967),
  drop/mismatch 0.69%/0.13%, s6 half carries 774 channel-row
  decisions (was 777).
- **Scripted welfare anchor** (kitty-eval, served world, 3 seeds ×
  20k): team welfare 0.906–0.908, up from the 0.88–0.90 band —
  faster play servicing raises happiness, the direction the handoff
  predicted. Welfare bounds gain margin.
- **Meow-listening anchor re-measured** (digest-zeroing probe, s6 as
  Miso in scripted company, 10 seeds × 20k — the pre-024 8.18% had
  lapsed): flips **13.26% of heard** (11.79–15.17% per seed, 10/10
  consistent) on a much quieter channel (audibility 62.4% → 10.7%).
  Listening functional; H3's ≥3% threshold anchored with margin. See
  the meow-listening doc's post-025 addendum.

## Reproduce

```
# four batches: all + three --only-action classes; --seeds takes a
# comma list (seq 11001 11150 | paste -sd, -)
./experiments/tools/twin-probe/target/release/twin-probe \
  --config experiments/exp-002-mixed-population/family/base.toml \
  --samples 1000 --trace-len 1200 --seeds <11001..11150 comma list> \
  --probe-seed 42 --quiet [--only-action groom,sleep,rest | eat,drink | play,chase] \
  --out experiments/exp-001-bc-mappo/raw/twin-probe-fambase-<class>-post025-w11001.jsonl
# analysis: search.py channel_metrics, GAMMAS (0.995, 0.998, 0.9985, 1.0)
# calibration rerun: trainer/.venv/bin/python trainer/water_calibration.py \
#   water-calibration-2026-08-03-post025   (argv[1] = archive label)
```
