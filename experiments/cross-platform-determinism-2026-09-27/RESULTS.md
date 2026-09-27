# Cross-platform determinism check — results

Collected 2026-09-27 under `DECLARATION.md` (committed 4610198
before collection). Machines: A = the lab Mac (arm64,
macOS-26.6, python 3.14.3, torch 2.13.0); B = the
serving box (x86_64, Linux 6.8.0-124, python 3.12.3, torch
2.13.0+cpu, 2 cores), running in a throwaway clone at 4610198 with a
maturin-built binding (setup record, not in the raws — the reports'
binding fields are null; consistent with the identical layer-1 sha) —
engine crates code-identical to the lab binding's befe5f0 (only
license and workspace-version metadata moved between them; no .rs
change). Neither report records the
BLAS backend. Both sides torch single-threaded during every forward
(`torch.set_num_threads(1)` in layers 2/3 and `load_model`; the
reports' `torch_threads` field is the pre-set default — 6 and 2 —
recorded before that call). Raws: `results-raw/report-mac.json`,
`report-x86.json` and their `.logits.npz` side files (gitignored);
the observation fixture is tracked (`fixture-obs.npz`, obs sha
c9bc8082beeb7112…, asserted equal by the comparer before any
layer-2/3 comparison; layer 1 does not use the fixture).

## The comparison (compare output, verbatim; the two machine-tuple
header lines omitted)

```
LAYER 1 (engine trajectory): BITWISE EQUAL
LAYER 2 (policy forward): logits differ; argmax agreement 1.0000 (0 of 1000 rows flip)
  logits max abs diff 1.574e-05, mean abs diff 6.304e-07
LAYER 3 (end-to-end greedy):
  seed 900401: action stream BITWISE EQUAL; team hap 92.1593 vs 92.1593
  seed 900402: action stream BITWISE EQUAL; team hap 92.2628 vs 92.2628
  seed 900403: action stream BITWISE EQUAL; team hap 92.2263 vs 92.2263
  seed 900404: action stream BITWISE EQUAL; team hap 92.1499 vs 92.1499
  seed 900405: action stream BITWISE EQUAL; team hap 92.3367 vs 92.3367
  5-seed means: A 92.2270 ± 0.0690 | B 92.2270 ± 0.0690 | delta of means +0.0000
```

## The reading

- **The Rust engine is bitwise-portable** across arm64/x86 on this
  run: 5,000 scripted ticks with state and element streams hashed
  per tick, identical — the libm concern did not reach the
  trajectory.
- **The policy forward drifts at BLAS scale** (max 1.6e-05 across
  1,000 rows) **without one argmax flip** — and in the greedy
  end-to-end legs, zero flips across five 5,000-tick trajectories
  (≈250,000 head-argmax decisions), so every action stream and
  every happiness value reproduced exactly.
- **The measured statement for the archive label** (replacing the
  a-priori one): greedy EVALUATION reproduces bitwise across these
  two tuples, with a measured argmax-flip rate of zero at n ≈
  250,000 decisions — an empirical rate, not a guarantee; a logit
  gap under 1.6e-05 at a decision boundary could still flip.
  TRAINING remains tuple-bound and unmeasured (sampling, gradient
  reduction order, thread interleaving are the divergence sources
  this check deliberately excluded). Scope: one checkpoint
  (cand-s2) in all seats, one world, these seeds, matched torch and
  numpy versions — torch/numpy version skew was deliberately
  excluded and is NOT covered by this result; Python itself
  differed (3.14.3 vs 3.12.3, part of the tuple per the
  DECLARATION) and the one sub-bitwise drift below is Python-side.
- One sub-bitwise drift did reach the statistical tier:
  `nash_state_mean` on seed 900401 differs by 1 ulp between the
  reports (0.9211869706292487 vs …86) — Python-side exp/log
  reduction, not the engine or the action streams. Statistical-tier
  scalars are reproduced to rounding, not guaranteed bitwise.
- Consequence for the 2026-09-27 evidence-archive ruling: greedy
  eval of this checkpoint (cand-s2), occupying all five seats with
  the observation clock zeroed, on the package world, seeds
  900401–900405 × 5,000 ticks, reproduced bitwise across these two
  tuples at matched library versions — an empirical per-decision
  flip rate of zero at n ≈ 250,000, not a guarantee; carrying that
  rate to other seeds or horizons of the same setup is an
  inference from the rate, not a measurement, and other
  checkpoints/worlds/eval modes (mixed rosters, an unzeroed clock)
  are unmeasured (a checkpoint with argmax margins under 1.6e-05
  could flip). Within that measured scope
  the platform tuple's bitwise tier binds retraining rather than the
  archived greedy reads; archived reads outside it keep the tuple as
  their reproducibility condition until measured.

## Regeneration

### Collect

`determinism_check.py run` on each machine (the DECLARATION's
method; the server side ran in /root/detcheck with
/root/detcheck-venv, to be cleaned after this doc lands). Never run
by the gate.

### Read

Runtime: under 5 seconds. No environment variables required.

```
cd /Users/elizabethkelly/ai/cloudkitty
experiments/exp-006-character-gen/.venv/bin/python experiments/cross-platform-determinism-2026-09-27/determinism_check.py compare \
  experiments/cross-platform-determinism-2026-09-27/results-raw/report-mac.json \
  experiments/cross-platform-determinism-2026-09-27/results-raw/report-x86.json
```

GATE: PASS round 4 of 4, 2026-09-28 — arithmetic 16, threshold 2,
characterisation 21 (1 WEAK reported: the flip-risk sentence, edited
would→could per the verifier's own grading after the pass),
undecidable 4, provenance 9; raw-dir hash 5eab5f83e8672870.
