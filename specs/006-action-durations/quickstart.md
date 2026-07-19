# Quickstart: Validating Action Durations

**Date**: 2026-07-19 | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

How to prove the feature works end-to-end. Contracts:
[behavior-delta.md](./contracts/behavior-delta.md) ·
[http-api-delta.md](./contracts/http-api-delta.md) · model:
[data-model.md](./data-model.md).

## Prerequisites

```bash
export PATH="$HOME/.cargo/bin:$PATH"   # cargo is not on the default PATH
cd /path/to/cloudkitty
```

## 1. The whole suite (CI parity)

```bash
cargo fmt --all -- --check
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace
```

Expected: green, including the new `activity_durations` suite and the
re-baselined `welfare_longrun` bounds (which must be ≥ the 004 bounds by
construction — the test constants assert it).

## 2. Duration guarantees (SC-001, SC-002, SC-004)

```bash
cargo test -p cloudkitty-core --test activity_durations
```

Expected assertions over a 20,000-tick default-config run:

- every activity instance lasts ≥ its configured min and ≤ its max
  (only documented counterpart-loss ends may fall short);
- no activity survives past the first tick where its min is met and its
  need is 0;
- every one of the six activity kinds is observed lasting ≥ 2 ticks.

## 3. Determinism and persistence (SC-005, SC-006)

Covered in the same suite plus `invariants_proptest`:

```bash
cargo test -p cloudkitty-core --test invariants_proptest
```

- same seed + config → identical 5k-tick activity timelines;
- a snapshot saved mid-meal resumes to the identical subsequent states;
- a pre-006-shaped snapshot (no `activity_clock`, in-progress `Sleeping`)
  is **refused** by strict load validation with the standard clear error —
  no heal paths (backwards compatibility waived 2026-07-19).

## 4. Welfare improvement (SC-003)

```bash
cargo test -p cloudkitty-core --test welfare_longrun
cargo test -p cloudkitty-core --test stuck_state_regression
```

Expected: bounds tightened vs. 004 (means up, low-happiness time down —
the exact re-baselined numbers are recorded in the test constants with the
004 floors asserted beside them); the frozen 004 stuck-state fixtures still
recover at least as fast as before.

## 5. See it with your own eyes (SC-004, SC-007)

```bash
cargo run -p cloudkitty-server   # serves the unchanged client
# open http://localhost:<port>
```

Watch a kitty reach a bowl: the panel's "doing" line reads "eating 🍥" for
2–3 consecutive ticks (not one flicker), then the kitty moves on. Naps and
cuddles visibly last. The viewer is the shipped, unmodified one — that it
narrates multi-tick scenes correctly *is* the SC-007 check. For the wire:

```bash
curl -s localhost:<port>/world  | jq '.kitties[0] | {activity, activity_clock, last_action}'
curl -s localhost:<port>/config | jq '.actions.durations'
```

Expected: `activity.state` values from the new set during scenes,
`activity_clock` present only mid-activity, durations echoed with the
documented defaults.

## 6. Config validation (FR-002)

```bash
# In a scratch copy of cloudkitty.toml set: [actions.durations] eat = { min = 0, max = 5 }
cargo run -p cloudkitty-server -- --config /tmp/bad.toml
```

Expected: startup rejection naming `[actions.durations] eat.min`, the value
`0`, and the allowed range (min ≥ 1, min ≤ max). Setting every bound to
`min = 1, max = 1` must boot and lawfully reproduce pre-006 instant
actions.

## 7. Old worlds are refused cleanly, fresh worlds run

Pre-006 saves are not supported (owner decision, 2026-07-19). With a
pre-006 `snapshot.json` present (never modify or commit the owner's file):

```bash
cargo run -p cloudkitty-server
```

Expected: if the old snapshot happens to satisfy strict validation (e.g.,
every kitty idle at save time) it loads and runs; otherwise the server
refuses it with the standard clear error suggesting `--fresh` — never a
silent misload. A fresh world then boots and runs lawfully under the new
duration rules.
