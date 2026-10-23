# Arc binding and venv (DECLARATION.md §Welfare, choice (c); run order step 1)

Built 2026-10-22 from main HEAD, never touching the Gen 2 lab venv
(`../exp-006-character-gen/.venv`, binding e3bcc79a / ENGINE_COMMIT
b5aaa8cd, held fixed by deviations entry 5).

| item | value |
|---|---|
| venv | `experiments/minifriend-phase1-2026-10-22/.venv` (gitignored) |
| interpreter | `/opt/homebrew/opt/python@3.14/bin/python3.14`, Python 3.14.3 (the lab venv's own interpreter) |
| packages | numpy 2.5.2, torch 2.13.0 (pinned to the lab venv's), maturin 1.x |
| engine source | main HEAD `a2e8d0447146f2486f7c6c6e0adbb75f742f1a00` (= origin/main at build; `crates/` clean) |
| `cloudkitty.ENGINE_COMMIT` | `a2e8d0447146f2486f7c6c6e0adbb75f742f1a00` |
| wheel | `wheels/cloudkitty-0.3.0-cp39-abi3-macosx_11_0_arm64.whl` (gitignored with the venv; rebuildable from the command below) |
| wheel sha256 | `c618554b3d003a6ee86d508c8e25d1479085f69b96cd67403e1a2cbe3b4cd251` |
| rustc | 1.97.1 (8bab26f4f 2026-07-14) |

Build (a wheel, installed into the arc venv; `maturin develop` was NOT
used, so nothing was written into the shared crate tree):

```sh
A=experiments/minifriend-phase1-2026-10-22
uv venv --python /opt/homebrew/opt/python@3.14/bin/python3.14 $A/.venv
uv pip install --python $A/.venv/bin/python3 "numpy==2.5.2" "torch==2.13.0" "maturin>=1.5,<2"
VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/maturin build --release -m crates/cloudkitty-py/Cargo.toml -i $A/.venv/bin/python3 --out $A/wheels
uv pip install --python $A/.venv/bin/python3 $A/wheels/*.whl
```

## Engine delta since the certified binding (`git log b5aaa8cd..a2e8d044 -- crates/`)

- a945fccf, f9a080f1, b3d135b0, c9a68e8b, 2be38173, f407e480 — spec 065
  `[initial_needs]` (PR #462, main 5fb27cfb): the config surface
  (`config/mod.rs`, `validate.rs`), the resolve law (`init_needs.rs`),
  and the one engine hook in `world.rs`, gated on
  `init_needs::active(config)` (the section present); every other
  touched file is a test or a struct-literal field (`initial_needs:
  None`).
- 26645f90 — the RL shipped-config sweep's symlink skip (a test file
  under `cloudkitty-rl/tests/` and nothing in the engine).

So with no `[initial_needs]` section the engine path is the certified
one; the declaration's empirical check (L's first world byte-equal to
the certified rot2 battery row on the same seed: team happiness and
distress ticks) runs at step 2 before anything else is collected.

Step-1 smoke on this binding: the collector's save-obs guard
(`test_save_obs_keeps_the_start_of_tick_observation`, g2-s1, seed
905001, 5 ticks) passes here as in the lab venv.
