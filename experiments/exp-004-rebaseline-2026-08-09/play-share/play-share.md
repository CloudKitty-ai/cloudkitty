# The play/chase "halving": investigated, refuted — batch noise at the detection floor

**2026-08-09.** The owner asked whether the lake explains play/chase's
apparent drop (0.0245 on 2026-08-03 → 0.0125 in yesterday's re-verify).
Per the freshly re-derived F-004 discipline, step one was replication
before mechanism-hunting — and step one ended the investigation.

## The replication (identical config, disjoint 150-world bands)

play/chase, v5 base, recipe verbatim:

| batch | worlds | S(.998) | S(.998)≤600 | sig ticks |
|---|---|---|---|---|
| A (840001–150, from the re-verify) | 150 | 0.0125 | 0.0098 | 35 |
| B (840151–300, this run) | 150 | **0.0390** | **0.0290** | 74 |
| pooled A+B (cluster-robust, 300 worlds) | 300 | 0.0099 | 0.0064 | 46 |

- **The "halving" does not replicate**: disjoint bands on the identical
  config swing **3.1×**, straddling the old 0.0245. There is no drop to
  explain; the 2026-08-03 → 2026-08-09 comparison was one noisy batch
  against another. (The old 0.0245 was itself a single 150-world batch
  and, with today's knowledge, carried the same noise.)
- **Pooling makes it dissolve, not sharpen**: at 300 world-clusters the
  per-tick SE shrinks but significant ticks *drop* to 46 (fp ≈ 60) with
  the peak in the k>1100 tail — the two bands' significant ticks do not
  align. play/chase's per-tick amplitude sits at or below the 2·SE
  detection floor at these batch sizes on this engine. The honest §10.1
  statement is not "play/chase credit halved" but **"play/chase credit
  is below reliable measurement at standard probe batch sizes"**.

## The toggle cells (run before the replication verdict was in)

Three single-toggle cells on band A — lakeless (water 3–4), edge_penalty
0, pre-pin dials 15/15/15 — produced S(.998)≤600 of 0.0126 / 0.0267 /
0.0046 against band A's 0.0098. **None of these differences are
interpretable**: they are within the 3× swing the identical-config
replication just demonstrated, and a config change re-deals the world,
so same-seed cells are not paired. Recorded as underpowered, no claims
made or implied. (Configs kept in this directory; raw traces in
`raw/play-share/`.) The lake hypothesis is neither supported nor
refuted — it is **unnecessary**.

## Consequences folded into FINDINGS

- **F-015 addendum corrected**: the "play/chase halved" direction is
  withdrawn as a batch artifact; the class enters §10.1 as
  floor-level/unrankable rather than diminished.
- **F-004 addendum gains class-dependence**: the 150-world +
  S(.998)≤600 bar was derived on eat/drink (per-tick amplitude ~0.009,
  replicates 1.24×) and does NOT transfer to floor-amplitude classes
  (play/chase ~0.002, swings 3.1×). Probe claims about small-amplitude
  classes need disjoint-band agreement before they are claims at all —
  which is F-004's original lesson, third time it has cashed out.

## Regeneration

```
# replication batch (identical base, band B):
twin-probe --config experiments/exp-004-meow-channel/family/base.toml \
  --seeds 840151..840300 --samples 1000 --t-min 100 --t-max 1100 \
  --trace-len 1200 --probe-seed 42 --only-action play,chase --out pc-B.jsonl
# toggle cells: pc-lakeless.toml / pc-edge0.toml / pc-dials15.toml on band A
# analysis: channel_metrics (search.py), pooled variant in pc-pooled-300w.json
```
