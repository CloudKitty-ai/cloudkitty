# Arm 0 official certification run (2026-07-30)

Closes the handoff's queue item 5: the pre-registered Arm 0 — uniform
over legal actions — run through the **real deploy chain** for the first
time, unblocked by `kitty-eval --sample` (issue #70, PR #71). The interim
floor had come from the Python surface; this is the official record.

**Setup**: all-zero artifact (constant logits + masked softmax sampling =
uniform over legal actions), regenerated at repo state a7357f0 via
`zero-artifact`; sha256
`0d26083ddf0173c47030d07b24170329ae46caad1a12e3ca7f64abdef1cce9a7`.
Certification protocol per prereg §8: default world, seeds 1–10,
20,000 ticks, both roster modes.

```
cargo build --release --bin kitty-eval
cargo build --release --manifest-path experiments/tools/artifact-tools/Cargo.toml
experiments/tools/artifact-tools/target/release/zero-artifact \
  experiments/exp-001-bc-mappo/artifacts/arm0-zero.ckpolicy
./target/release/kitty-eval \
  --artifact experiments/exp-001-bc-mappo/artifacts/arm0-zero.ckpolicy \
  --sample --seeds 1,2,3,4,5,6,7,8,9,10 --ticks 20000 --roster both
```

## Results

- **Exit 0. Zero fallbacks in all 20 subject runs** (`fallback_count: 0`
  per run; the exit-2 gate never fired). Determinism self-check passed.
- Every line of the report and the JSON carries `selection: sampled` —
  the #70 "never ambiguous" doctrine, observed working end-to-end on its
  first official use.
- Paired Nash-welfare aggregates vs `needs_driven` (identical seeds):

| Roster | Arm 0 range (10 seeds) | Aggregate Δ |
|---|---|---|
| AllSubject | 0.5526 – 0.5661 | **−0.3465** |
| Mixed | 0.7367 – 0.7566 | **−0.1572** |

- **Welfare bounds: violated, massively, in every seed** (low-happiness
  streaks, unresolved distress up to 15,631 ticks). This is the expected
  and *intended* reading — a uniform-random cat is a bad cat.
  Certification is a must-pass gate for candidate arms; for Arm 0 the run
  is the floor's official measurement plus the plumbing proof, not a pass
  attempt.

## Reading

- **The floor is now official**: ≈0.55 AllSubject / ≈0.75 Mixed Nash
  aggregate. The interim Python-surface estimate (≈0.57 team reward on
  the default world) sits right where the official number landed —
  different instrument, same story; the Python detour was a faithful
  stand-in.
- The Mixed floor (0.75) is much higher than AllSubject (0.55):
  four-fifths of a Mixed roster is competent scripted cats, so the
  subject's chaos is diluted — a reminder that Mixed deltas compress all
  effects (clone: −0.02 Mixed vs −0.15 AllSubject; same compression).
- Baseline runs: `needs_driven` 0.9034–0.9072, zero bound violations —
  the gap Arm 2 plays in is 0.55 → 0.90 AllSubject, with Arm 1 (clone,
  greedy) at 0.75 AllSubject / 0.88 Mixed
  ([bc-clone-2026-07-29.md](bc-clone-2026-07-29.md)).
- Sampling determinism held: fixed seeds → reproducible run (the
  self-check re-runs and compares; it passed on the sampled path).

Arm 0 and Arm 1 are now both on the record. Remaining before Arm 2:
the PPO trainer (§7.4).
