# Served-world re-measurement: all three winners certify clean (2026-07-30, deviation 31)

Owner decision (deviation 31 / 2026-07-30d): §8's "default world" means
`cloudkitty.toml` — the served world, where the kitties actually live.
The compiled 3-kitty default every prior certification ran on was an
accident (see [collapse-forensics-2026-07-30.md](collapse-forensics-2026-07-30.md)).
Winners-first scope, fixed before any served-world number was seen:
arm2-g0p998-s3 (20M) and s4/s6 (40M), certified once and reported once
each, `--config cloudkitty.toml`, everything else per §8.

## Results — first certification passes of the experiment

| Run | Cert (§8, seeds 1–10) | AllSubject Δ (30 seeds) | min Δ | Mixed Δ | Wilcoxon (both rosters) |
|---|---|---|---|---|---|
| s3 (20M) | **PASS** 20/20 bounds, 0 violations | **+0.0406** | +0.0384 | +0.0107 | 30/30, W=0, p=1.9e-09, r_rb=+1.00 |
| s4 (40M) | **PASS** 20/20 bounds, 0 violations | **+0.0418** | +0.0404 | +0.0108 | 30/30, W=0, p=1.9e-09, r_rb=+1.00 |
| s6 (40M) | **PASS** 20/20 bounds, 0 violations | **+0.0418** | +0.0401 | +0.0110 | 30/30, W=0, p=1.9e-09, r_rb=+1.00 |

Guardrail detail, all three artifacts: **max distress age 0 in every
one of the 60 certification runs** (limit 150), longest-low 0 (limit
20), low-share 0.00%, zero fallbacks. Not a single distress tick or
low-happiness excursion in 1.2M certification-evaluated ticks. The
`needs_driven` served-world anchor: 0.9020 (range 0.9004–0.9032).

## Reading

- **§9 decision rule 1 is triggered for the first time**: Arm 2 >
  baseline on the primary endpoint *and* guardrails pass → the
  deployment-soak gate (§9.1) is now reachable. Which artifact (if any)
  goes to soak is the owner's call; on these numbers s4 and s6 are
  statistically indistinguishable and s3 is marginally behind.
- **The effect size roughly doubles on the intended world**: +0.041 vs
  the compiled world's +0.0138–0.0212. The *minimum* per-seed delta
  (+0.038) exceeds the best compiled-world *mean*. Consistent with the
  trainer having annealed to exactly this world.
- **The "universal guardrail failure" and the "distress-latency
  residual" were compiled-world phenomena** — stress responses of
  policies fed the empty-slot roster-OOD input, not properties of the
  policies where they'd deploy. exp-002's residual-latency target
  dissolves on the served world (nothing to reduce: distress age is 0);
  the roster-OOD fragility target stands and is now the clear primary.
- The compiled-world record stands unreplaced, reinterpreted per
  deviation 31 as an out-of-roster robustness screen — on which 3/9
  seeds still fail catastrophically. Both measurements are true; they
  answer different questions.

## Open per deviation 31

Whether to re-measure the remaining artifacts (Arm 2 s1/s2/s5 + γ=.995
runs, clone, Arm 0 anchors) on the served world — owner decides on
these results. The case for: complete arm-level ladder on the intended
world (clone/Arm 0 anchors re-based). The case against: no decision
hangs on them; the compiled-world paired comparisons already settled
H0a/H0b and Arm 3.

## Regeneration

```
S10=1,2,3,4,5,6,7,8,9,10 ; S30=$(seq 1 30 | paste -sd, -)
for R in arm2-g0p998-s3 arm2-g0p998-s4 arm2-g0p998-s6; do
  A=experiments/exp-001-bc-mappo/artifacts/$R
  ./target/release/kitty-eval --artifact $A/arm2.ckpolicy --config cloudkitty.toml \
      --seeds $S10 --ticks 20000 --roster both --json $A/certification-served.json
  ./target/release/kitty-eval --artifact $A/arm2.ckpolicy --config cloudkitty.toml \
      --seeds $S30 --ticks 20000 --roster both --json $A/report30-served.json
done
# Wilcoxon: scipy.stats.wilcoxon on the paired[].delta rows per roster
```

Artifact sha256 unchanged (s3 in arm2 record; s4 `cc709513…`, s6
`8030b94d…`). Raw outputs: `artifacts/arm2-g0p998-s{3,4,6}/
{certification,report30}-served.{json,txt}` (gitignored, machine-local).
