# Quickstart: validating the lab DecisionRequest surface (spec 055)

## Prerequisites

Workspace toolchain; for the Python half, the lab venv with
`VIRTUAL_ENV` set before `maturin develop` (house gotcha: without it
the build lands in the repo-root venv).

## The targeted suites

```bash
cargo test -p cloudkitty-core behavior      # constructor + wire shape
cargo test -p cloudkitty-server --test http_plugin   # kept pile: 18 tests
cargo test -p cloudkitty-rl decision_request # byte test, no-consume, errors
cargo test --workspace
```

## The mutation cycle (rule 5)

Per plan.md's ledger, each via `scripts/mutate.sh --expect`:
perturb `for_context` → the byte test reds; draw the render seed from a
stored stream → the no-consume trajectory test reds; placeholder on
unknown id → the error test reds.

## Seeing it by hand

```python
env = ParallelEnv(...); obs, infos = env.reset(seed=7)
line = env.decision_request(2)
req = json.loads(line)
assert req["kitty_id"] == 2 and req["v"] == 3
env.decision_request(99)   # ValueError naming kitty 99
```

Call it twice for the same kitty: identical bytes. Run the same episode
with and without calls: identical trajectory (that is FR-005, and the
suite pins it).

## Acceptance (Experiments, on the branch)

Handover list: the byte-comparison test with its mutate red; the seed
handled as the spec says (rendered, not consumed — documented in
contracts/render-surface.md); one sentence in docs/plugins.md; config
sweeps untouched (no new key). Ping them at mergeable — their first lab
read (screen scale, 5 seeds × 5000 ticks, tier 2 package world) runs
the day the surface lands.
