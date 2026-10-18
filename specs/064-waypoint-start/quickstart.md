# Quickstart: validating waypoint start-index

- **Flag-off byte-identity (SC-001)**: `cargo test` workspace-wide,
  zero re-cuts; bc-collect size100 seed 993001 byte-compare against the
  pre-change baseline (all arrays identical, meta delta = engine_commit
  only).
- **Seeding law (SC-002)**: `cargo test -p cloudkitty-core --lib
  waypoint_start` — staged disagreement worlds, tie-break, flag-off
  id-law pins; each assertion mutate-red first.
- **062 composition (SC-003)**: starts-knob world, flag on: every drawn
  cat's index equals the nearest waypoint to its drawn tile; 062 draw
  goldens green untouched.
- **Determinism (SC-004)**: same seed+config flag-on twice →
  byte-equal worlds (rides the existing determinism suite shape).
- **Flag-on smoke (SC-005)**: scratch size100 toml with the flag on
  (scratchpad only, never under experiments/), bc-collect 1×2000;
  completes, diverges from flag-off.
- **Gate**: `cargo fmt && cargo clippy --all-targets && cargo test`,
  then CI incl. the shipped-config sweep and jscpd ratchet (3.5; stage
  new tests on the shared `test_support` builders, never fresh clones).
