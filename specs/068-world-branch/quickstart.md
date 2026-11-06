# Quickstart: validating the World Branch API (spec 068)

Prerequisites: a worktree on `product/068-world-branch`; `cargo` from
`rust-toolchain.toml`; a Python venv with `maturin pytest numpy` (never
the native checkout's `.venv`). Run every command from the worktree root.

## 1. Rust guards

```sh
cargo test -p cloudkitty-rl --test branch
cargo test -p cloudkitty-core   # DealtSeeds serde + Provenance additions compile against every core suite
```

Expected: every test in `branch.rs` green AFTER each guard has been seen
red with `scripts/mutate.sh --expect <first assertion>` (tasks.md lists
the mutant and the prediction per guard).

## 2. Python guards

```sh
VIRTUAL_ENV=$PWD/.venv maturin develop --release
pytest crates/cloudkitty-py/tests/test_branch.py -v
pytest crates/cloudkitty-py/tests -v        # the existing suites, unchanged
```

## 3. Byte-identity without the API (FR-015 / SC-007)

```sh
cargo test --workspace            # goldens, pins, fixtures, run-json golden, schema pins
python -c "import cloudkitty as c; print(c.OBSERVATION_SCHEMA_VERSION, c.MASK_SCHEMA_VERSION, c.ACTION_SCHEMA_VERSION)"
```

Expected: no golden or pin re-cut in the diff; the three schema versions
equal their pre-feature values; `cargo run -p cloudkitty-server -- --help`
untouched (server crate not in the diff).

## 4. The branch, by hand (US1 + US2)

```python
import cloudkitty, numpy as np
env = cloudkitty.ParallelEnv(horizon=5000)
obs, infos = env.reset(seed=7)
for _ in range(300):
    env.step({a: [34, 0] for a in env.possible_agents})   # idle, silent
snap = env.snapshot()

seeds_at_snapshot = {a: env.tick_records()[a]["decision_seed"] for a in env.possible_agents}
twin = cloudkitty.ParallelEnv(horizon=5000)                 # never reset
obs_t, infos_t = twin.restore(snap)
assert all(infos_t[a]["decision_seed"] is not None for a in twin.possible_agents)  # FR-004: equal to the original's next seeds (test_branch.py compares them)
for _ in range(200):
    s1 = env.step({a: [34, 0] for a in env.possible_agents})
    s2 = twin.step({a: [34, 0] for a in twin.possible_agents})
    assert all(np.array_equal(s1[0][a], s2[0][a]) for a in s1[0])

# A scripted friend (a seat not in possible_agents): name a legal act for one tick, read the mark.
env = cloudkitty.ParallelEnv(horizon=5000, control={"kitty_2": "needs_driven"})
env.reset(seed=7)
env.override("kitty_2", action=0)
env.step({a: [34, 0] for a in env.possible_agents})
rec = env.tick_records()["kitty_2"]
assert rec["provenance"] == "overridden_act"
env.step({a: [34, 0] for a in env.possible_agents})
assert env.tick_records()["kitty_2"]["provenance"] == "policy"
```

## 5. Refusals (US5)

```python
other = cloudkitty.ParallelEnv(horizon=5000, control={"kitty_2": "external"})
try:
    other.restore(snap)
except ValueError as e:
    assert "control differs" in str(e)
try:
    env.restore(b"not a snapshot")
except ValueError as e:
    assert "not a snapshot" in str(e)
```

## 6. SC-006 measurement (record the numbers here when run)

```python
import time, cloudkitty
env = cloudkitty.ParallelEnv(horizon=20000)
env.reset(seed=1)
acts = {a: [34, 0] for a in env.possible_agents}
t0 = time.perf_counter()
for _ in range(10_000): env.step(acts)
replay = time.perf_counter() - t0
snap = env.snapshot()
t0 = time.perf_counter()
env.restore(snap); env.step(acts)
branch = time.perf_counter() - t0
print(f"replay 10k: {replay:.3f}s  restore+step: {branch*1e3:.2f}ms  ratio {branch/replay:.4f}")
```

| Machine | replay 10,000 ticks | restore + 1 step | ratio | bar |
|---------|---------------------|------------------|-------|-----|
| (fill at implementation) | | | | < 0.01 |

The CI assertion in `test_branch.py` uses a loose 0.1 so a slow runner
cannot flake it; the 0.01 bar is read here on the reference machine.

## 7. Done when

- Sections 1–3 green, section 4–5 behave as written, section 6's table
  filled with a ratio under 0.01.
- `gh pr view --json files` shows only Product-lane paths plus the shared
  `docs/howto-rl.md` and `CHANGELOG.md`.
