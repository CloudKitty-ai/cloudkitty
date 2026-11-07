# Arc binding and venv (DECLARATION.md §13 step 1; spec 068 adopted, §12 call 6b)

Built 2026-11-06 from main HEAD after the declaration commit, never
touching the Gen 2 lab venv (`../exp-006-character-gen/.venv`,
ENGINE_COMMIT b5aaa8cd, the trunk's), the mini-friend arc venv
(`../minifriend-phase1-2026-10-22/.venv`, a2e8d044) or the needy arc's
(`../needy-set-2026-10-28/.venv`, 5928b7ca, the heads' and the gate's).
Pinned at build; NEVER rebuilt while an arm runs (068 FR-006 refuses a
snapshot across commits, so a rebuilt venv mid-arc would silently void
g0b). If g0 fails on this binding, the trunk's own venv is the fallback
and the 068 reads wait (DECLARATION §13 step 1).

| item | value |
|---|---|
| venv | `experiments/minifriend-phase2-2026-11-06/.venv` (gitignored) |
| interpreter | `/opt/homebrew/opt/python@3.14/bin/python3.14`, Python 3.14.3 (the lab venv's own interpreter) |
| packages | numpy 2.5.2, torch 2.13.0 (pinned to the lab and arc venvs'), maturin 1.x |
| engine source | main HEAD `226509ec1d66c95518993fdc21cb5e64f228f336` (= origin/main at build, the declaration commit; `crates/` clean; ≥ deff48c0, spec 068's merge) |
| `cloudkitty.ENGINE_COMMIT` | `226509ec1d66c95518993fdc21cb5e64f228f336` |
| schemas | observation 6, global state 2 (the trunk's) |
| 068 surface | `ParallelEnv.snapshot / restore / fork / override / tick_records` present |
| wheel | `wheels/cloudkitty-0.3.0-cp39-abi3-macosx_11_0_arm64.whl` (gitignored; rebuildable from the command below) |
| wheel sha256 | `e260cd2838f7c849c230bb4fb632b518782067f934a5095459f11b899c64c29a` |
| rustc | 1.97.1 (8bab26f4f 2026-07-14) |

Build (a wheel, installed into the arc venv; `maturin develop` was not
used, so nothing was written into the shared crate tree):

```sh
A=experiments/minifriend-phase2-2026-11-06
uv venv --python /opt/homebrew/opt/python@3.14/bin/python3.14 $A/.venv
uv pip install --python $A/.venv/bin/python3 "numpy==2.5.2" "torch==2.13.0" "maturin>=1.5,<2"
VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/maturin build --release -m crates/cloudkitty-py/Cargo.toml -i $A/.venv/bin/python3 --out $A/wheels
uv pip install --python $A/.venv/bin/python3 $A/wheels/*.whl
```

Run everything on it as `VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/python3 -B …`.

## Engine delta since the needy arc's binding (`git log 5928b7ca..226509ec -- crates/`)

- Spec 068, the World Branch API (PR #491, merge deff48c0): d32e4747
  (engine half: `Episode::identity / snapshot / restore / override_next`,
  `Provenance::Overridden*`, `DealtSeeds` serde, vectorized per-world
  replies), c0ebb824 (guard G11 rework), fe30f8d8 (Python half:
  `ParallelEnv.snapshot / restore / fork / override / tick_records`,
  `ENGINE_COMMIT`), 7c4f1459 (review fixes: identity normalisation,
  malformed-restore refusal, GIL released in snapshot / fork /
  override). The ordinary `reset` / `step` path is not in the diff's
  intent; g0 below is the check, not this sentence.
- 4782fe0f, 6f45223e (log-capture test rigs), a3613ab8, 9dd940a1
  (plugin_e2e test deadlines): test files only.

## g0 — the binding reproduces the trunk's worlds (DECLARATION §9)

**RESULT 2026-11-06: PASS on every check** (`test_phase2.py g0a g0b
g0c`, this venv): (a) trunk-s1's last dumped probe (`probe-u2599.npz`,
seed 40,001, 2,000 ticks × 5 seats) replayed by its recorded actions
gives the dumped observation and mask streams EXACTLY; (b) on all three
probe worlds, `snapshot()` at tick 999 then `restore()` — and `fork()` +
`restore()` — reproduce the straight replay's tail exactly; (c) the
recorded g2-s1 uniform leg row on world 905001 at 20×20 (cert battery)
re-run by `cert_harness_fog.run_one` on this binding reproduces every
column (mean_happiness per seat, nash to 1e-16, max_distress_age 77,
dist_ticks, low_share, floor_touches). Reds for g0a / g0b: RED
CONFIRMED (the wrong seed; a reset in place of restore / on the fork).
So the post-068 engine's ordinary path is the trunk's, and 068's
snapshot / restore / fork may be cited (§12 call 6b's condition met).
What g0 checks: (a) trunk-s1's last dumped probe
(`artifacts/ppo-g2-trunk-s1/probe-u<N>.npz`, seed 40,001) replayed by
its recorded actions on this binding reproduces the dumped observation
stream byte-for-byte; (b) the recorded g2-s1 uniform leg at 20×20 on
world 905001 (cert battery `results-raw/g2-s1/legs/size20/`) re-run
with the trunk's final policy reproduces the recorded row's team
happiness and distress columns. g0b: `snapshot` → `restore` on three
recorded worlds equals a fresh `reset` + replay (the state stream and
the observations), before any 068 read is cited.
