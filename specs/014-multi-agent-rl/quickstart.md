# Quickstart: Validating Multi-Agent RL Readiness

Runnable end-to-end scenarios proving each slice works, in the phasing
order the spec assumes (seam → encodings → reward/episodes → Python →
evaluation → deployment). Contracts referenced, not duplicated.

## Prerequisites

- Rust toolchain (workspace edition 2021), `cargo test` green on `main`.
- For the Python surface only: Python ≥ 3.9, `pip install maturin`.
- No GPU, no ML runtime, no network access needed anywhere.

## 1. The seam: golden parity (US1 / SC-001)

```bash
cargo test -p cloudkitty-core golden_parity
```

**Expect**: a behavior-driven run and a joint-action run fed the same
collected proposals serialize byte-identically over ≥ 5,000 ticks on the
default world, RNG state included. Also run the degradation test
(absent + malformed proposals → those kitties idle, invariants hold):

```bash
cargo test -p cloudkitty-core joint_action
```

## 2. Encodings: determinism, totality, mask oracle (US2)

```bash
cargo test -p cloudkitty-rl
```

**Expect**: encoder determinism (same snapshot → identical vector), codec
totality both directions (proptest), the mask's pure-oracle property test
(mask verdict == engine verdict for every menu entry, no carve-outs), and
the never-all-zero property across randomized rosters and activities —
including the named crowded-continuation constructions (crowded duet,
co-sleep, groom, and a default-population critter cluster around an
ongoing play) that exercise target-priority slot ordering
([contracts/encodings.md](contracts/encodings.md)).

## 3. The Python surface: rollouts reproduce (US2 / SC-002, SC-003)

```bash
cd crates/cloudkitty-py && maturin develop --release
python -m pytest tests/  # smoke: shapes, bounds, bookkeeping
python examples/random_rollout.py --seed 7
```

**Expect**: a random-policy rollout with documented shapes and bounds;
terminations all false, truncation exactly at the horizon; rewards one
team scalar. Reproducibility: run `random_rollout.py --seed 7` in two
separate processes — observation/mask/global-state/reward streams
bit-identical. Throughput: `python examples/bench.py` reports ≥ 5,000
steps/s single-threaded on the default world and near-linear scaling to
8 vectorized workers, with the measurement method printed alongside.

## 4. Evaluation harness: baseline the built-ins (US3)

```bash
cargo run -p cloudkitty-rl --bin kitty-eval -- --brain needs_driven
cargo run -p cloudkitty-rl --bin kitty-eval -- --brain playful
```

**Expect**: the welfare scorecard ([contracts/evaluation-harness.md](contracts/evaluation-harness.md))
matching the CI welfare suite's numbers for the same seeds; the paired
same-seed comparison stable across repeat runs. This is valuable before
any training exists — it is the bar a policy must clear.

## 5. A trained policy clears the bar (US2+US3 / SC-004)

Train with any PettingZoo-compatible cooperative trainer (the reference
script under `docs/` is documentation, not a supported surface), export
to the artifact format ([contracts/policy-artifact.md](contracts/policy-artifact.md)), then:

```bash
cargo run -p cloudkitty-rl --bin kitty-eval -- --artifact policies/trained.ckpolicy
```

**Expect**: both roster modes scored; every welfare bound met; welfare
aggregate ≥ the `needs_driven` baseline on ≥ 10 paired seeds; least-happy
kitty no worse than baseline's; **zero fallback-taken decisions** (a
nonzero count exits nonzero by design).

## 6. Deployment: a kitty gets a trained mind (US4 / SC-005, SC-006)

Add to `cloudkitty.toml` ([contracts/policy-artifact.md](contracts/policy-artifact.md)):

```toml
[kitties.pumpkin]
behavior = "policy:trained"

[rl.policy.trained]
artifact = "policies/trained.ckpolicy"
```

```bash
cargo run -p cloudkitty-server   # boots; logs schema versions + content hash
cargo test                       # full CI suite with the policy kitty rostered
```

**Expect**: startup validates and hash-logs the artifact before any tick;
a corrupted artifact fails startup naming `[rl.policy.trained].artifact`;
the viewer shows nothing unusual; the entire existing suite (welfare,
determinism, invariants, fairness) passes with the policy kitty present.

## 7. Constitutional cleanliness (SC-006)

```bash
grep -ri "reward" crates/cloudkitty-core/src/   # expect: no matches
```

The constitution stays at v1.1.0; every new constant lives in
configuration with documented defaults (`[rl.*]` blocks).
