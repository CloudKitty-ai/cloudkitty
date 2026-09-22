# Quickstart: validating spec 057

Prerequisites: the worktree at `~/ai/cloudkitty-teacher-sleep`, Rust
toolchain per the repo pin, Python venv only if running the cert leg.

## 1. Unit fixtures (stories 1–3, edge cases)

```sh
cargo test -p cloudkitty-core sleep_floor -- --nocapture
```

(All 057 fixtures carry the `sleep_floor_` name prefix — tasks
T003–T006 and T009 — so this filter matches exactly the new pile.)

Expected: the new fixtures pass — worthless nap loses, at/under-floor
skip, warm options keep full pressure, floor-0 branch untouched.

## 2. Floor-0 byte equivalence (P1)

```sh
cargo test -p cloudkitty-core          # includes the 056 floor-0 regression pin
```

Cert leg (exact match, validation (a) of the 006 protocol):

```sh
kitty-eval --brain needs_driven --config evals/anchor-b3.toml
```

Expected: identical output to the same command on main (SC-001); any
diff is a P1 failure.

## 3. The mutate red (SC-005)

```sh
scripts/mutate.sh --expect "floor-15 fixture goes red; floor-0 pin stays green" \
  crates/cloudkitty-core/src/behavior/selection.rs
```

Mutation: pressure binding back to the raw need. Predict the exact
failing test before running (CLAUDE.md rule 5).

## 4. Experiments' legs (read on their harness, not here)

Tier 5 comparator, 30 × 20k on the floor-15 count-6 package world
(`cert_harness_fog.py scripted eval --config shallow-15.toml`):
sleep share falls from 0.118 toward 0.088; naps begun at/under floor
with no warm option = 0; welfare within seed spread (86.2, 0/150);
placement reported beside 0.341/0.458 (SC-002..004).
