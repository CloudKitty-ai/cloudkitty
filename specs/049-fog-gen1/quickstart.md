# Quickstart: validating Fog Gen 1 (spec 049)

Run everything from the worktree root (`~/ai/cloudkitty-fog`, branch `049-fog-gen1`). Long jobs run in the foreground. Commit before any mutate-then-revert cycle; record predictions and re-read counts in `redden-list.md`.

## 0. Prerequisites

- Pinned toolchain via `rust-toolchain.toml` (`rustc -V` must match the pin).
- Python 3.11 venv with `maturin`, `pytest`, `numpy` for §5; the exp-006 venv (`experiments/exp-006-character-gen/.venv`) for §6.

## 1. Build and the whole suite

```
cargo fmt --all -- --check && cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace --no-fail-fast 2>&1 | tail -30
```

Expected at arc end: green, with the count = baseline (recorded at cycle 0) + the new guards listed in `redden-list.md`; fmt and clippy CI-exact clean.

## 2. The schema pins (SC-001)

```
cargo test -p cloudkitty-rl --test schema_five_pins
```

Expected: `observation_len` 404, `kitty_slots` 4, menu 39, kitty-pointer 20, logit budget 55, observation schema 5, action 3, mask 3 — every assertion literal against [contracts/observation-v5.md](contracts/observation-v5.md).

## 3. Visibility, memory, mask equivalence (SC-002, SC-003, R2)

```
cargo test -p cloudkitty-core --test fog_visibility
cargo test -p cloudkitty-core --test fog_memory
cargo test -p cloudkitty-rl --test mask_oracle
```

Expected: property runs green (random worlds and radii 2–40); the mask on the fog view equals the mask on the full snapshot for every menu entry.

## 4. Meow law, stamps, scripted ladder (SC-010, SC-011, US7, US8)

```
cargo test -p cloudkitty-core --test meow_law_fog
cargo test -p cloudkitty-core say_surface_grounding
cargo test -p cloudkitty-core -- reply_ladder
```

Expected: no want legal with known relief or off the top need (social kinds: illegal exactly while an idle friend is in view; a friend that is only heard, or visible but asleep / mid-scene, never silences the word); no here legal without adjacency or (audible matching want ∧ visible referent); every `reply = 1` has both; no same-tick reply; floor unset ⇒ message stream byte-identical to the no-reply engine.

## 5. Actions identical at a world-covering radius (SC-004, FR-024)

```
cargo test -p cloudkitty-core --test fog_continuity -- world_covering_radius_reproduces_pre_fog_actions
```

Expected: 20,000 ticks, served roster all-scripted, `[vision] radius` = 40, reply floor unset, `announce_here` 0 → action stream identical to the pre-fog stream captured at the branch base (`tests/fixtures/prefog-actions-20k.digest`); message stream differs only by wants the new law silences (asserted per row).

## 6. Blind first-sight and welfare smoke (SC-005, SC-012)

```
cargo test -p cloudkitty-core --test fog_exploration -- first_sight_within_one_crossing
cargo test -p cloudkitty-core --test welfare_longrun -- --ignored fog_r5_20k
```

Expected: every seeded blind trial sights a bowl within 40 ticks; the r = 5 run completes 20,000 ticks with zero invariant failures, printing distress-event and watchdog counts (recorded for the step-5 prereg, not gated).

## 7. Config strictness, sweeps, exams (SC-007)

```
cargo test -p cloudkitty-core --test shipped_configs
cargo test -p cloudkitty-rl --test shipped_configs_rl
cargo test -p cloudkitty-core config:: -- missing_section_is_named retired_key_is_unknown
cargo run -p cloudkitty-rl --bin kitty-eval -- --suite evals/v2 --dry-run
```

Expected: every in-scope TOML loads complete through both surfaces or is listed in `config-sweep-exclusions.txt`; `evals/v2` present in both sweeps; each missing section and each retired key refused by name; the v2 manifest hashes verify.

## 8. Artifact refusal and boot (SC-008, FR-011)

```
cargo test -p cloudkitty-rl --test artifact_v3_reject -- schema_four_artifact_is_refused
cargo test -p cloudkitty-server --test policy_v3_kitty
cargo test -p cloudkitty-server -- roster_above_slots_plus_one_is_refused
```

Expected: a schema-4 `.ckpolicy` fails to load naming observation schema found 4 / expected 5, before any tick; a six-cat roster with `kitty_slots` 4 is refused at boot naming both numbers.

Plugin wire (SC-013):

```
cargo test -p cloudkitty-core -- plugin_e2e
```

Expected: the request the plugin receives carries `v: 3` and a fogged `world`; a plugin that refuses the version falls back to the built-in with the tick loop untouched.

## 9. Determinism and save/restore (SC-006)

```
cargo test -p cloudkitty-core --test determinism
cargo test -p cloudkitty-core --test snapshot_resume
```

Expected: same seed + config + ticks → identical world including memory and `explore_heading`; a mid-run save/restore continues byte-identically.

## 10. Python surface (CI parity)

```
cd crates/cloudkitty-py && maturin develop --release && pytest tests -v
```

Expected: `observation_space` shape (404,), `OBSERVATION_SCHEMA_VERSION` 5, two-process reproducibility green, PettingZoo conformance green.

## 11. Binding continuity (SC-009)

```
experiments/exp-006-character-gen/.venv/bin/python experiments/exp-006-character-gen/binding_continuity.py --rebaseline --config cloudkitty.toml --seating all-scripted
experiments/exp-006-character-gen/.venv/bin/python experiments/exp-006-character-gen/binding_continuity.py
```

Expected: a new 3.0 reference record committed alongside; the second run passes against it.

## 12. Goldens (end of arc only)

Regenerate the evolution golden, the strip witness and the run_json golden from ONE run after every behavioural task landed; paste the justification into each file's doctrine comment; confirm the defaults-stamp diff shows only the new keys.
