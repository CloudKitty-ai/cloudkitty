# Quickstart: validating the rest sibling

Validation guide per commit and end-to-end. References:
[data-model.md](data-model.md), [contracts/](contracts/),
research.md D9 (the sorted redden list — read it before running
anything; rule 6).

## Prerequisites

- Workspace toolchain (pinned by `rust-toolchain.toml`; `rustup`
  honors it automatically).
- `cargo test --workspace` green on the base commit before starting.

## Commit 1 — the split is a provable no-op

```sh
cargo test --workspace
```

Expected: the migrated tests pass (classic-value assertions now name
the new dials); the golden evolution digest is **unchanged** — same
seed + config + ticks, byte-identical world state, run ×3 (house
practice, SC-001).

Deprecated-key check (SC-002):

```sh
cargo test -p cloudkitty-core config          # inert-key + nan-table + strictness guards
```

Expected (as amended by the owner's 2026-08-28 loud-retirement
ruling, commit 4): a config carrying `cuddle_relief` FAILS validation
with an error naming the key and both split dials; an unknown key is
still rejected; every committed toml (migrated) loads.

## Commit 2 — the sibling shape, before any price moves

```sh
cargo test -p cloudkitty-core action events
```

Expected green (each guard was shown red first — predictions in D9):

- rest toward a **busy** adjacent friend validates legal; toward a
  non-adjacent kitty resolves to idle
- the partner is never bound and never stamped; its clock is
  untouched
- tier resolves per serviced tick off the shared predicate; a
  mid-scene settle flips drip → mutual on that tick
- with `rest_drip_relief = 0.0` (this commit's value) a busy-partner
  scene pays **nothing**; a mutual scene pays `rest_mutual_relief`
  to both
- counters accumulate per tier; `mutual_ticks + drip_ticks ≤ span`,
  shortfall = solo ticks (drive red via a wandered partner)
- a pre-change snapshot carrying a bound duet resumes as two
  synchronized resters paying mutual
- a serialized `ActivityEnd` with zero counters is byte-identical to
  today's JSON (contract §Shape)

## Commit 3 — the reprice is config-only

```sh
git diff HEAD~1 -- cloudkitty.toml   # the whole commit: values + comments
cargo test --workspace
```

Expected: no `.rs` changes in the diff; values match
[contracts/relief-dials.md](contracts/relief-dials.md) §Served 2.x;
per-scene delivery arithmetic guards pass (each rider < need 5.1 per
minimum scene from a single slot; drip < mutual per activity).

## End-to-end (pre-merge, this branch)

1. `cargo test --workspace` — full suite, then re-read the D9
   must-red list and confirm every entry actually went red in its
   commit (running is not reading).
2. Boot a local server; on a scripted-seat world confirm the first
   rest scenes appear and `/events/activity` rows show the counters
   ([contract](contracts/activity-event-tier.md) example shape).
3. Article I–V property suites green (constitution gate).

## Post-merge (owner's word; Experiments runs the measurements)

Deploy is a 2.x restart (world continues). Soak reads: welfare
watchdog quiet, incumbents at the pre-declared **zero** rest scenes;
scripted seats are the demand read. Acceptance (SC-003…SC-007):
Experiments' pre/post censuses on F-029-corrected instruments,
scenes-not-relief-events, both tiers emit-proven via the counters,
re-baseline before any certification bar.
