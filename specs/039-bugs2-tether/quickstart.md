# Quickstart: validating the roam-cell tether

Runnable scenarios proving the spec's claims end-to-end. Contract
details: [contracts/roam-config.md](contracts/roam-config.md); design
decisions: [research.md](research.md).

## Prerequisites

- The workspace builds: `cargo build --workspace`
- For scenario 5: any pre-039 world save (`snapshot.json` from the
  served box or a local run on main)

## 1. Confinement (spec SC-001)

```sh
cargo test -p cloudkitty-core roam
```

Expected: partition property tests (every tile exactly one cell, on
20×20 and 26×26 and a world smaller than one cell) and the
confinement property run (seeded worlds, tether on, every bug tracked
over full lifetimes across ≥10 seeds — zero tiles outside the birth
cell) all pass. Rule-6 red check: invert the cell predicate locally
and confirm the confinement test — that test, not a neighbor — fails.

## 2. Inertness (spec SC-002)

```sh
cargo test -p cloudkitty-core golden_evolution
```

Expected: with `roam_cell` unconfigured, a 10,000-tick seeded run
reproduces the world-state digest pinned from main @ 87236c5
bit-for-bit. This is the proof that merging the capability changes
nothing until a config asks for it.

## 3. Cadence and draw preservation (spec SC-003, FR-003)

```sh
cargo test -p cloudkitty-core cadence
```

Expected: over a seeded tethered run, every bug attempts a move
exactly on its every-other-tick schedule; steps lost to the cell
boundary are counted and the attempt count matches the schedule —
no redraws, no compensation.

## 4. Validation refusals (US3 scenario 3)

```sh
cargo test -p cloudkitty-core roam_cell_validation
```

Expected: `roam_cell = 0` and `= 1` refuse at load naming
"[elements.bug] roam_cell" and the value; `roam_cell` on a non-bug
table refuses naming that table; `= 2` and world-sized values load.

## 5. Old-save adoption (FR-007 edge case)

```sh
# boot the post-039 binary with the served package against a pre-039 save
cargo run --release -p cloudkitty-server -- --config cloudkitty.toml
```

Expected: the save loads with no migration (fingerprint unmoved);
existing bugs finish their current ttl countdowns and are tethered
from load position; respawns are born with lifetime 600 inside their
spawn cells. Verify by watching `/world` for a few hundred ticks
(bugs stay in their cells; `g` in the viewer shows greebles still
roaming).

## 6. Full suite + lint (gate for handoff)

```sh
cargo test --workspace --release && cargo clippy --workspace --release --all-targets
```

Expected: zero failures, clippy clean at `-D warnings`. The pinned
`engine_defaults_sha256` test passing is the stamp-neutrality proof
(research D5).

## 7. Handoff: the economics gate (spec SC-004 — Experiments runs it)

When 1–6 pass, ping Experiments with the branch head. They run the
pre-registered chase-census acceptance grid against a build of this
branch (arms incl. 3×3 and ttl variants, skill rows, both
geometries; census tool with expiry-abandon tagging landed at their
e39079e). Bars: unskilled bug EV > 10; skilled EV inside the
opportunistic corridor; ruin ≤ ~1% at ttl 600. The pre-registered
cell-size rule (largest cell clearing bar 1) must land on the shipped
size. **The PR opens for merge only after this grid passes and the
phase-1 --fresh has run on the box.**

## 8. Definition of done (spec SC-005 — after merge, before "shipped")

Experiments re-banks on the post-change world: fresh scripted +
playful anchors, the purrsonality zero-play baseline, the
tail-benchmark divergence note, and the F-026 fog confound note.
Then the exp-006a sequence resumes on the new world.
