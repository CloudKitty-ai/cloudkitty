# Seed-band ledger

One row per claimed world-seed band. Claim your band here, in the
same PR that first uses it, before any run burns a seed. Bands never
overlap; a band stays claimed forever (even burned or historical
bands, so nothing collides with old evidence).

This ledger was reconstructed from committed docs on 2026-08-18 and
may be incomplete for pre-exp-005 work. When claiming anywhere near
an old experiment's numbers, grep the preregs and results docs
before trusting a gap here, then add what you find.

| band | owner | purpose |
|---|---|---|
| 1–1000 | legacy kitty-eval | small-seed evals (`--seeds 1,2,3` era); treat as burned |
| 800001–800010 | exp-003 | sampled-selection eval seeds |
| 820001–820030 | exp-005 | fingerprint probe 820001–010; eval band to 030 |
| 840001–840450 | exp-004 re-baseline | class-credit batches A/B/C, 028 engine (F-004) |
| 850001–866000 | exp-004 | dataset v4 collection (850001 + ci×1000 + r) |
| 870001–870030 | battery convention | shared eval band (eval 870001+; trait screen anchor) |
| 875001–875450 | exp-006 | class-credit batches A/B/C, post-wall stamp |
| 880001–880030 | battery convention | shared stress band (stress 880001+) |
| 900001 | bc-collect | smoke seed, burned |
| 910001–928000 | exp-006 | dataset v5 cell B spread (910001 + ci×1000 + r, 18 configs) |
| 940001–958000 | exp-006 | dataset v5 cell A pinned (same structure) |
| 970001–970100 | exp-006 | anchor demonstrations (100 rollouts) |
| 985001–985010 | exp-006 | fingerprint probe band (post-wall instrument) |
| 1000000+ | training | per-run PPO/BC training seeds; each prereg declares its sub-band |
