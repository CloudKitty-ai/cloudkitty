# Continuity Baseline: spec 043 `announce_here`

Pinned at branch base `69e65eb` (origin/main; = 836ed3d + the
waterline-ruling doc commit), worktree `~/ai/cloudkitty-announce`,
branch `043-announce-here`, 2026-08-30, before any code change.

## Branch-base witnesses (T002)

| Witness | Result |
|---|---|
| `cargo test -p cloudkitty-core --lib roam_cell_stays_out_of_the_default_serialization` | ok — 1 passed |
| `cargo test -p cloudkitty-core --test evolution_golden` | ok — 1 passed (pin `7b361b2a5582d33efd96d8d64ef5be73d890c76e9d9751e57453e37f44ec17ad`, unregenerated) |
| `cargo test --workspace` | ok — **725 passed, 0 failed** across all targets |

The stamp (`engine_defaults_sha256`) is the sha256 of the default
Config's serialized JSON; the guard above is its CI witness. The golden
pin is the 10,000-tick default-world digest. Both must read identically
at commit 1 (T008) and at the final proof (T021).

## Commit-1 witnesses (T008)

| Witness | Result |
|---|---|
| stamp guard (with the new `announce_here` key) | ok — green, key absent from default serialization |
| `evolution_golden` | ok — pin `7b361b2a…` unregenerated |
| `cargo test --workspace` | ok — **728 passed, 0 failed** (725 baseline + 3 new: 2 config guards + the `HERE_KINDS` order pin) |

## Final proof (T021)

| Witness | Result |
|---|---|
| stamp guard, `announce_here` in its key list | ok — green (in the workspace run below) |
| `evolution_golden` | ok — pin `7b361b2a…` green, **unregenerated** |
| `cargo test --workspace` | ok — **737 passed, 0 failed** (725 baseline + 12 new: 2 config guards, HERE_KINDS pin, 6 behavior guards, 3 gate-zero tests) |
| Existing tests modified | **zero** — `git diff` against branch base shows the only deletion in tracked test-bearing files is the one replaced return line in `announce()` itself |

US2 acceptance 1–3 satisfied: the launch is byte-identical, proven by
the standing witnesses unmodified.
