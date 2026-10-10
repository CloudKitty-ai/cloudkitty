# Quickstart: validating the Gen 2 observation schema (spec 058)

Validation scenarios proving the bump end to end. Details live in
`contracts/observation-v6.md` and `data-model.md`; this file is the
run guide.

## Prerequisites

- Worktree on `product/schema-bump`, Rust toolchain per
  `rust-toolchain.toml`.
- For the Python-surface checks: `maturin develop` into a venv with
  `VIRTUAL_ENV` set (census-header memory: maturin needs it).

## Scenarios

1. **Layout pins** — `cargo test -p cloudkitty-rl schema_six_pins`:
   every contract offset asserted literally; the v5 oracle
   (`schema_five_pins`) still passes untouched.
2. **Size invariance (SC-001)** —
   `cargo test -p cloudkitty-rl size_invariance`: same relative scene
   encoded at 20×20 and 100×100 yields identical spatial cells.
3. **Leak audit (SC-002)** — `cargo test -p cloudkitty-rl row_visibility`:
   randomized friend states; the row carries bath and never the other
   five needs/happiness (layout enumeration + property encode).
4. **Column map (SC-003)** —
   `cargo test -p cloudkitty-rl schema_map`: v5 lookups equal the
   schema-five pins; v6 lookups equal the v6 pins; unknown
   version/name errors. Python: import `cloudkitty`, assert
   `COLUMN_MAPS[5]` spot values and `ACTION_MENU["play_critter_0"]`-
   style names resolve.
5. **Dirt reserve inertness (SC-004)** — property test: both cells
   0.0 over randomized worlds; no write path to the reserve range.
6. **No clock (SC-005)** — stationary-world property: encodings
   identical across ticks modulo scene-age/staleness cells.
7. **Version gates (SC-006)** — load a v5-pinned artifact against v6:
   refused with the version error; the served Gen 1 path still loads
   v5.
8. **FR-001a overshoot pin** — seen friend dx=2, dy=3 at radius 4
   encodes Manhattan 5 unclamped; heard row at radius + window
   likewise.
9. **Full suites** — `cargo test --workspace` and the config sweeps
   (new toml keys: comfort_slack, per-kitty consent_line/favourite —
   the sweep loads every experiments toml; expect green only after
   defaults are in place).
10. **Vocabulary flags (FR-017)** —
    `cargo test -p cloudkitty-rl vocabulary_flags`: layout identity
    with trill/ekekek armed.

Every new assertion lands red-first through `scripts/mutate.sh
--expect <prediction>` (CLAUDE.md rule 5); predictions stated per
test in the tasks.
