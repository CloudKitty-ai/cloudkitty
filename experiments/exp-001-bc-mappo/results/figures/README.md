# results/figures — exp-001 figure gallery

Rendered by `make_figures.py` from the committed snapshots in `data/`;
`generate_data.py` (re)builds `data/` from the gitignored raw sources
(`artifacts/`, `raw/`) plus deterministic descriptive replays. The
certification JSONs in `data/` are kitty-eval outputs preserved
verbatim — never regenerate them (evaluate-once); everything else in
`data/` is re-derivable.

Batch of 2026-08-01 (current engine post-022/023, served world 24×24):

| Figure | Shows | Data |
|---|---|---|
| `seed-lottery.png` | Training curves for all 15 MAPPO runs (Arm 2 BC-warm-started ×9, Arm 3 scratch ×6); certified winners s3/s4/s6 bold; identical settings diverge by seed, scratch plateaus below baseline | `data/training-curves.npz` (from `artifacts/arm*/metrics.jsonl`) |
| `certification-ladder.png` | All-subject welfare per rung: uniform floor 0.559 → BC clone 0.785 (pre-022-engine anchors) → the six-strong certified pool ≈0.95 (R2 γ=.998 + O1 γ=.995, same world stamp) vs scripted baseline 0.907 | `data/arm0-cert.json`, `data/clone-report30.json`, `data/r2-s{3,4,6}.json`, `data/o1-g0p995-s{1,2,3}.json` |
| `occupancy.png` | 24×24 position density per kitty × 0/1/2 policy seats; wall-hugging playful patrol, agents' den spots | `data/traj-*.npz` |
| `pairing-three-arm.png` | Partner-tick matrices vs seats + team-Nash gradient 0.8698→0.8857→0.8977; agents pair more, choose partners, bond with each other | `data/pair-partner-*.npy` |
| `meow-raster.png` | Every emitted meow, seed 1, three arms; seating s3 retires Kittybear's WaitForMe spam; s3's FollowMe is bursty (see pair-screen correction 2026-08-01) | `data/traj-*.npz` |
| `bc-label-distribution.png` | bc-v1's 1.78M labels over the 40-action menu; meow labels near-absent (92; FollowMe/WantPlay/Purr zero); partner-grooming also zero-labeled → RL-emergent in deployment | `data/bc-label-hist.npz` |
| `roster-ood-streaks.png` | R3 per-run worst low-happiness streaks: s3 20/20 clean, s6 mild (39), s4 recurring (365) — the ranking behind the second-seat pick (F-010 screen) | `data/r3-s{3,4,6}.json` |
| `meow-listening-flip.png` | The digest-zeroing probe: 8.18% of digest-active decisions flip when s6 is deafened; hearing pulls toward play, silence toward sleep/groom | `data/meow-listening-summary.npz` (from `artifacts/arm2-g0p998-s6/meow-probe-seed*.npz`) |
| `collapse-portrait.png` | F-008's canonical failure: s2 seed 8 on the compiled world — onset t≈1541, permanent low-welfare attractor | `data/collapse-s2-seed8.npz` |
| `clone-training.png` | Arm 1 BC curves (64 epochs, best 61, top-1 0.802) + per-class accuracy vs support | `data/clone-metrics.json` |
| `critic-ev.png` | Critic pretrain explained variance per γ (best 0.506 / 0.442) | `data/critic-0p99{5,8}-stats.json` |

The three-arm replays (`traj`, `pair-partner`) are descriptive
re-reads: baseline and Seating B reproduce the registered pair-screen
trajectories (per-seed Nash matches
[pair-screen-2026-07-31.md](../pair-screen-2026-07-31.md) exactly);
the all-scripted control arm is a 2026-08-01 descriptive addition,
not part of the registered screen.

Pre-existing figures (`class-conditioned-credit.png`,
`frozen-world-channels.png`, `world-search-pareto.png`) predate this
batch; their generator scripts were not preserved — cited from
[frozen-world-addendum-2026-07-27.md](../frozen-world-addendum-2026-07-27.md).
