# Quickstart: validating Relief Memory Margin (spec 050)

Run from the worktree root (`~/ai/cloudkitty-relief`, branch `050-relief-memory-margin`). Long jobs run in the foreground (`scratchpad/cycle.sh LABEL` for the whole suite). Commit before any mutate-then-revert cycle; write predictions before each run and re-read counts into `redden-list.md`.

## 0. Baseline

```
cargo fmt --all -- --check && cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace --no-fail-fast 2>&1 | tail -5
```

Expected at cycle 0: the merged-049 count (884 / 0 / 6 ignored at main `75e97d1`; re-read here — main has moved to `9e0ab5e`).

## 1. The predicate and its fixture (SC-001, SC-002, SC-006)

```
cargo test -p cloudkitty-core --lib meow::
```

Expected: the axis-aligned `r + 1` fixture asserts `!visible_from` (outside the disc), then drink / eat / play read **legal at margin 0, silent at margin 1, silent absent**; water in view silent at 0 / 1 / 8 / absent; cuddle / bath / sleep verdicts identical across margins. Red-first: on the engine before the predicate change, the margin-0 arm fails with "remembered relief silences" — recorded in `redden-list.md` cycle 1.

## 2. The property (SC-003, A14)

```
cargo test -p cloudkitty-core --test meow_law_fog
```

Expected: `the_law_holds_over_random_worlds` untouched and green (key absent); the new reach property green, its oracle computing reach from position, memory tile, radius and margin. Red-first: the new property against the unchanged engine reddens on the first drawn `Some(margin)` case with an out-of-reach slot.

## 3. The served roster (SC-004)

```
cargo test -p cloudkitty-core --test relief_memory_margin -- --nocapture
```

Expected: `want_drink` calls > 0 over 20,000 ticks on the served `cloudkitty.toml` verbatim (reading 2026-09-05: 23, ~1.2 per 1,000, first at tick 1,610; F-040's ~12 per 1,000 is the anchor config's rate); with the test-only floor 0.01, `here_water` replies (`reply == true`) > 0 (reading: 273). Red-first: with the key forced absent, drink = 0 at every horizon.

## 4. The stream re-pin and the SC-004b control (FR-009, R5)

```
cargo test -p cloudkitty-core --test fog_continuity
```

Expected BEFORE re-recording: `reply_floor_unset_is_byte_identical` red at the first `want_drink` row (tick recorded); `world_covering_radius_diverges_only_by_the_named_causes` green (r = 40 keeps every tile in reach). Then, once:

```
cargo test -p cloudkitty-core --test fog_continuity -- --ignored record_preladder
cargo test -p cloudkitty-core --test fog_continuity
```

Expected: green; the doc comment names spec 050 and the divergence tick.

## 5. Served welfare readings (SC-007)

```
cargo test -p cloudkitty-rl --test welfare_longrun -- --ignored served_world_fog_r5 --nocapture
```

Expected: numbers printed for r = 5 and r = 64 (0 / 0 before 050); written into the gate's comment beside the pin. Readings, not gates (owner, 2026-09-04).

## 6. The served diff and the stamp (SC-005)

```
git diff origin/main -- cloudkitty.toml
cargo test -p cloudkitty-core --lib config::tests::roam_cell_stays_out_of_the_default_serialization
```

Expected: the TOML diff is exactly `relief_memory_margin = 0` plus its comment block and the amended `[meow]` head comment; the stamp test asserts the key is absent from the default serialization (red if the skip attribute is removed).

## 7. Records

Check `specs/049-fog-gen1/contracts/meow-law-v5.md` (table rows for eat / drink / play), `config-3.0-migration.md` (new-keys row), `docs/meows.md` (law paragraph), `CHANGELOG.md` (Unreleased one-liner). `evals/v2` untouched (`git status` shows no file under `evals/`).

## 8. Whole suite, then PR on the owner's go

```
scratchpad/cycle.sh final
```

Expected: baseline + the new guards, 0 failed, 6 ignored; fmt + clippy clean. After merge: ping Experiments (R8).
