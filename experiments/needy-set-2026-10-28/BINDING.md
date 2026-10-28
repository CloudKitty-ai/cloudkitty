# Arc binding and venv (DECLARATION.md §11 step 2; the fresh venv the needy-set kickoff requires)

Built 2026-10-28 from main HEAD, never touching the Gen 2 lab venv
(`../exp-006-character-gen/.venv`, ENGINE_COMMIT b5aaa8cd) or the
mini-friend arc venv (`../minifriend-phase1-2026-10-22/.venv`,
a2e8d044); both predate specs 066 and 067 and refuse a needy config.

| item | value |
|---|---|
| venv | `experiments/needy-set-2026-10-28/.venv` (gitignored) |
| interpreter | `/opt/homebrew/opt/python@3.14/bin/python3.14`, Python 3.14.3 (the lab venv's own interpreter) |
| packages | numpy 2.5.2, torch 2.13.0 (pinned to the lab and arc venvs'), maturin 1.x |
| engine source | main HEAD `5928b7ca7653797f949cb50c651f71311ac23f75` (= origin/main at build; `crates/` clean) |
| `cloudkitty.ENGINE_COMMIT` | `5928b7ca7653797f949cb50c651f71311ac23f75` |
| `ParallelEnv.needy` | present (spec 067 FR-012) |
| wheel | `wheels/cloudkitty-0.3.0-cp39-abi3-macosx_11_0_arm64.whl` (gitignored; rebuildable from the command below) |
| wheel sha256 | `282f682d41fab14a69f76728274b68110134f1b208fcbdc6667dadbbae46080a` |
| rustc | 1.97.1 (8bab26f4f 2026-07-14) |

Build (a wheel, installed into the arc venv; `maturin develop` was not
used, so nothing was written into the shared crate tree):

```sh
A=experiments/needy-set-2026-10-28
uv venv --python /opt/homebrew/opt/python@3.14/bin/python3.14 $A/.venv
uv pip install --python $A/.venv/bin/python3 "numpy==2.5.2" "torch==2.13.0" "maturin>=1.5,<2"
VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/maturin build --release -m crates/cloudkitty-py/Cargo.toml -i $A/.venv/bin/python3 --out $A/wheels
uv pip install --python $A/.venv/bin/python3 $A/wheels/*.whl
```

## Engine delta since the mini-friend arc binding (`git log a2e8d044..5928b7ca -- crates/`)

- Spec 066, the welfare-hazard guard (PR #469, main 3ba039c4):
  7902d6c1, 2b6f7cb8, f5975994, 97947d9a, 36fe46dd, 8b8150ae, d7828dcb,
  47890aef. A config with no `[welfare_hazard]` table and no hazard
  mode active takes the inert path (its world-identity pin: a
  pre-feature config and the same config with an empty acknowledgement
  generate byte-identical worlds).
- Spec 067, the needy presets (PR #471, main 90429f0c): daab1e98,
  6defd2f0, 2d8d952d, 7d6110bd, 07b8f546, fb47e31f, 8feb7ea6, efb3fb0e,
  80a4c76e, eb3098e4, 63728c61, 65e0a8ac, d9d50bba, ad951004. With no
  needy seat the engine is byte-identical on every readable surface
  (FR-002, SC-001; the preset-trace goldens of daab1e98 pinned
  through the feature).
- b1f60a4a (PR #470): `crates/cloudkitty-py/examples/bench.py` only.

So with no needy seat and no hazard table the engine path is the
certified one. The declaration's empirical check (n3: rot2 on L seed
905001 for 2,000 ticks, every array equal to the first 2,000 ticks of
Phase 1's recorded stream) runs at step 2 after her ruling; it is a
covered run (10,000 covered cat-ticks) and waits for her word.
