# Quickstart: Welfare-Hazard Acknowledgement Guard (spec 066)

Validation scenarios proving the feature end-to-end. Scratch configs
live in the session scratchpad, never under the repo tree: both
shipped-config sweeps load every tracked toml, and a stray hazardous
file outside `experiments/` is exactly what FR-005 reddens.

## Prerequisites

- Worktree `~/ai/cloudkitty-welfare-hazard` on the feature branch;
  `cargo build --workspace` green.
- A passing base config to copy (`cloudkitty.toml`).

## 1. Inert when absent (SC-001, FR-002)

- `cargo test --workspace`: green, zero golden/pin/fixture diffs in
  the PR beyond the seven appends.
- `engine_defaults_sha256` before and after the change: equal. No test
  pins the value (`the_engine_defaults_stamp_is_stable_and_well_formed`
  checks only length, hex and self-equality), so T001 records it on
  the base commit and T010 compares after; both values go in the PR.
- `World::generate` at a fixed seed with and without the section:
  identical serialized worlds (T009).
- Serialize `Config::default()` to JSON: no `welfare_hazard` key.

## 2. The five failure shapes and the two legal ones (SC-002)

Scratch toml = base config plus `[initial_needs] cuddle = 92.0`.

| variant | expected result |
|---------|-----------------|
| no `[welfare_hazard]` | error names `initial_needs`, `[initial_needs].cuddle = 92`, and the line to add |
| `acknowledged = ["initial_needs"]` | loads; same world as spec 065 generates (fixed seed, compare needs at tick 0) |
| `acknowledged = ["initial_need"]` | error: unknown name |
| `acknowledged = ["initial_needs", "initial_needs"]` | error: duplicate |
| base config (no initial_needs) + `acknowledged = ["initial_needs"]` | error: stale |
| `[initial_needs] cuddle = 0.0`, no acknowledgement | loads (nothing to acknowledge) |
| `[initial_needs] cuddle = 0.0` + `acknowledged = ["initial_needs"]` | error: stale |

Partial (two active, one acknowledged) is exercised by the pure
function's unit test with a synthetic two-mode set.

Drive each through `cloudkitty_rl::config::load_configs_from_str` (the
Python environment's path) and through the server (`cloudkitty-server
-c <scratch>`): same error text on both.

## 3. The sweeps (SC-003, FR-005)

- The in-file self-tests in both sweeps: a hazardous toml under
  `<scratch>/specs/` fails by name; the same bytes under
  `<scratch>/experiments/` with an exact acknowledgement pass; without
  it fail at load.
- `cargo test -p cloudkitty-core --test shipped_configs` and
  `cargo test -p cloudkitty-rl --test shipped_configs_rl` on the
  branch with the seven appends in place: green. Before the appends
  (validator landed, files not yet migrated) both sweeps are RED; each
  panics on the FIRST failing file, so "exactly the seven" is read by
  appending one file at a time and re-running the core sweep after
  each: seven runs, seven distinct failing paths, green on the eighth
  (T013, T017, T020). This is FR-009's reason, and the rule-5 red for
  the migration.

## 4. The server (SC-004, FR-006, FR-007)

Scratch acknowledged config with a scratch `snapshot_path`:

```sh
cargo run -p cloudkitty-server -- -c <scratch>.toml --fresh
# exit non-zero; message names initial_needs and --allow-welfare-hazard;
# no snapshot or .bak file appears under the scratch path
cargo run -p cloudkitty-server -- -c <scratch>.toml --fresh --allow-welfare-hazard
# boots; the log carries ONE line "welfare-hazardous world served on purpose";
curl -s localhost:<port>/config | jq .welfare_hazard
# → {"acknowledged": ["initial_needs"]}
curl -s -H 'Accept: text/plain' localhost:<port>/settings | tail -1
# → welfare_hazard.acknowledged = ["initial_needs"] [toml]
cargo run -p cloudkitty-server -- -c cloudkitty.toml --allow-welfare-hazard
# boots as today; no welfare_hazard line, row or key
```

The in-crate unit tests cover the same four states on `gate`,
`log_boot` and `settings::build` without a listener.

## 5. Fingerprint (SC-005)

Unit test: a config with and without the section fingerprint equal.
For the seven migrated files: `Config::fingerprint()` before and after
the append, equal (a one-line check in the PR body).

## 6. The migration (FR-009)

```sh
for f in experiments/minifriend-phase1-2026-10-22/g2leg-20-{W,G}.toml \
         experiments/minifriend-phase1b-2026-10-23/g2leg-20-P{1..5}.toml; do
  printf '\n[welfare_hazard]\nacknowledged = ["initial_needs"]\n' >> "$f"
done
```

Then, read-only, for each file: strip everything from the trailing
`\n[welfare_hazard]\n` and sha256 the remainder; compare with the
pre-retrofit hash in `experiments/gen2-deviations.md` entry 14. The
branch base ad16a681 predates 304221b1, so entry 14 is NOT on the
branch: read it with `git show origin/main:experiments/gen2-deviations.md`
after a `git fetch` (never reset the branch onto moved main). All
seven equal, or the append shape is wrong. `git diff --stat` shows
exactly seven files, +3 lines each.

## 7. Rule-5 ledger (filled in by tasks)

Every assertion above goes red first via `scripts/mutate.sh --expect`;
the sweep self-tests red by mutating the helper, not the tree. The PR
body carries the ledger (test, mutation, predicted and observed red).
