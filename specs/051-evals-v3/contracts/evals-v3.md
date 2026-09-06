# Contract: eval-suite-v3 (spec 051)

The suite manifest contract is spec 017's (`specs/017-eval-suite/contracts/suite-manifest.md`); this file states what v3 pins on top of it and what consumers may rely on.

## Identity

- Directory `evals/v3/`, `version = "eval-suite-v3"`, seven files, frozen at landing. Any byte change to an exam fails CI and suite startup. Evolution = `evals/v4` alongside.
- Held-out doctrine (spec 017 FR-007) applies: results against v3 are void if any v3 exam world appeared in training. The v3 worlds are 48×48 × 5 cats (`scale`), 28×28 × 5 cats (mixed-roster), 32×32 × 4 (`scarcity`), 32×32 × 5 (`heterogeneity`). Experiments confirmed 2026-09-05 that none is in a training or prereg family.

## What a consumer may rely on

1. **A served-width mind sits every exam.** Every v3 roster is ≤ 5, so a policy bound at the compiled default 4 kitty slots (408 floats) sees every friend on every exam. This is the property v2 lacked (research R1): v2's wide exams scored a served-width mind with friends silently dropped from its observation.
2. **The six designs are the v1/v2 designs.** `scale` keeps the dilution question (2.25× the default area, default element counts) and drops the crowd; the mixed-roster cells keep the 28×28 composition hold-out with `playful` at seat 2 in every cell; `scarcity` and `heterogeneity` are carried with identical values.
3. **Verdict constants** are derived, not chosen: guest 11 (unattainable, stated), half 10, host 6 at ten seeds and tail 0.01; sign-test k 10 at tail 0.001, mode `warn`, tighten-only via `--enforce sign-test`.
4. **v2 and v1 are records.** Bytes never move; v1 is excluded from the shipped-config sweep (it no longer loads), v2 stays in it while its bytes load (owner ruling 2026-09-05, review finding 1); `kitty-eval --suite evals/v2` still runs (and, with FR-012, refuses a served-width policy subject on its four wide exams instead of scoring a truncated view).

## Invocation

```bash
kitty-eval --suite evals/v3 (--brain NAME | --artifact PATH [--sample]) [--enforce sign-test] [--json out.json]
```

Exit codes and report stamping unchanged (spec 017). FR-012: a `--artifact` subject whose slot count cannot seat an exam's roster is refused before any tick with a message naming the exam, the roster and the slots (exit 1, as any load failure).

## Guards (all in `crates/cloudkitty-rl/tests/eval_suite.rs` unless noted)

| Guard | Property | Seen red by |
|---|---|---|
| `a_served_width_mind_sits_every_exam` (new) | roster ≤ default slots + 1 for every exam; served-width fixture loads and completes 200 ticks on each | pointing the function at `evals/v2` once (4 of 6 red) — recorded, not kept |
| `carried_exams_parse_equal_to_v2` (new) | `scarcity`, `heterogeneity` parse equal to v2 | one value changed in the v3 draft |
| freeze guard (retargeted) | sha256 of every file = manifest | one byte edited in a v3 file |
| threshold / sign-test derivations (retargeted) | manifest numbers = rule | scratch manifest with `guest = 10` |
| distinctness (retargeted, + axis) | no exam byte-equals served/training; no exam at (20, 20, 5) | served config copied into the list |
| `shipped_configs_rl.rs` sweep assertion (flipped) | `evals/v3` in the sweep | pointed at a directory that does not exist → red (the v2 exclusion was dropped by ruling) |
| FR-012 unit test | 6-cat scratch exam refuses a 4-slot policy subject; scores a built-in | unchanged engine scores instead of refusing |

## Pointers moved to v3

`kitty-eval` usage string; `README.md` repo map and example; `docs/rl-training.md` example and the two stale "a new evals/v2" sentences; `specs/017-eval-suite/contracts/suite-manifest.md` evolution note; one annotation in `specs/049-fog-gen1/spec.md` (§the 3.0 wall); `CHANGELOG.md` Unreleased; `config-sweep-exclusions.txt` (+ `evals/v2`). BACKLOG's P1 entry is removed on merge per its own convention.
