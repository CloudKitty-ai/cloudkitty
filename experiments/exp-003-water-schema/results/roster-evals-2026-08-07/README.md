# Per-run roster evals, exp-003's nine candidates (2026-08-07)

Byte copies of the gitignored working set
(`experiments/exp-003-water-schema/artifacts/eval/*--shape-{iii,roster3,roster5}.json`),
committed 2026-08-08 because the §9.2 respecification proposal in
`experiments/exp-004-design-inputs.md` (§3) cites their full per-run
`max_distress_age` / `floor_touches` distributions — the grid doc's
tables only carry the worst-case summaries. Produced by the 2026-08-07
grid evaluation (`trainer/run_eval.py`); exp-002's counterpart set is
already committed at
`experiments/exp-002-mixed-population/results/eval-2026-08-03/`.

`gate_check.py` re-runs the settled gate (owner, 2026-08-08: incident
bar 225 with rate `max(1, floor(0.05n))` per shape / `low_share` > 5%
backstop / any floor-touch) against both cohorts and prints the fail
list the design-inputs doc quotes. Its exp-002
count reads 23, not 22: the extra row is `s6-reference`, the frozen
exp-001 anchor evaluated alongside the grid (it passes; it is not a
candidate).
