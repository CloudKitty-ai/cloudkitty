# Quickstart: Randomized Starts — validation guide

Prerequisites: this worktree (`~/ai/cloudkitty-randomized-starts`), workspace
toolchain. All commands from the worktree root.

## 1. Build + full gate (SC-004's local half)

```sh
cargo test --workspace
cargo clippy --all-targets -- -D warnings     # house rule: --all-targets
cargo test -p cloudkitty-rl --test shipped_configs_rl   # sweep green, no pin re-cut
```

Expected: all green with ZERO changes to goldens, pins, or shipped configs in
the diff (`git status` shows only this feature's files).

## 2. The law, end to end (US1 / SC-001 / SC-002)

```sh
cargo test -p cloudkitty-core starts
```

Expected: the starts suite covers — same seed twice = identical positions;
roster file-order reorder = identical positions per id; many-seed sweep with
every start in-bounds, unique, lawfully categorized (independent in-test
classifier using coverage_read.py's geometry), realized shares within binomial
tolerance; category exhaustion fails naming category and counts; golden
vectors (`contracts/golden-draws.json`) byte-stable.

## 3. Stream isolation (US2 / SC-003)

```sh
cargo test -p cloudkitty-core --test starts_baseline_identity
```

Expected: knob-on world vs knob-off world with explicit starts set to the
drawn ones, same seed, full horizon: byte-equal snapshots every tick, element
history included. (Rule 5 red for this guard: make the draw consume one
master-stream u64 via mutate.sh — the test must go red on first element
divergence.)

## 4. Config surface (FR-001/002/006/008)

```sh
cargo test -p cloudkitty-core config
```

Expected: `[starts]` parse + validation errors per
contracts/config-surface.md §3 (share bounds, corner ≤ edge, <3×3 rejection,
missing-coordinate errors naming the kitty); a knob-off config missing x/y
rejected; mixed explicit+drawn config legal with pinned tiles occupied.

## 5. Provenance (US3 / SC-006, cross-lane)

```sh
# bc-collect is a standalone workspace: run it from its own directory,
# and configs are named with --config (not positional).
cd experiments/tools/bc-collect
cargo run --release -- --config <share-enabled.toml> --rollouts 2 --ticks 50 --out-dir /tmp/bc-test
python3 - <<'EOF'
import json; m = json.load(open('/tmp/bc-test/config-00-rollout-00/meta.json'))
assert m['engine_commit'] and m['starts_law_version'] == 1
assert all(s['category'] in ('corner','edge_ring','interior') for s in m['starts'])
EOF
```

Keep the share-enabled toml OUTSIDE experiments/ (scratch dir): the
shipped-config sweep loads every experiments toml, and a stray knob-on
file would join the sweep's surface.

Expected: `engine_commit` a real SHA (not "unknown") on a clean build;
`starts` echo present, kitty-id order; the engine-side test additionally pins
echo == tick-0 readback.

## 6. Independent reproduction (SC-005)

A port (Python, per Experiments' acceptance checks) implements
contracts/draw-law-v1.md from prose + ChaCha8 and validates against
`contracts/golden-draws.json`. Engine-side responsibility here: the golden
file is emitted by a test from the real engine (recorded payloads, never
hand-written) and asserted byte-stable in CI.

## Scope notes

- Serving a knob-on config is NOT validated here: the served config keeps the
  knob off (spec doctrine check, rule 8) — turning it on served is a separate
  deploy ruling.
- bc-collect-level byte-equality and corpus-scale share checks are
  Experiments' acceptance runs (their requirements note §Acceptance), on top
  of the engine tests above.
