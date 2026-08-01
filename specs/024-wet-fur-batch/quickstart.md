# Quickstart: validating the wet-fur batch

Prerequisites: stable Rust toolchain, repo root, batch implemented.

## The whole bar

```bash
cargo test --workspace            # everything, including the new guards
cargo clippy --workspace --all-targets -- -D warnings
cargo fmt --all -- --check
```

## Item-by-item validation

**Wet fur** (charge law + guard):

```bash
# Unit + property coverage of the charge, ceiling, trait scaling:
cargo test -p cloudkitty-core advance_needs water
# The executable guard (load-time arithmetic + swim-forever property):
cargo test -p cloudkitty-core --test water_safeguard
# Config contract: defaults fill, hostile values rejected naming the field:
cargo test -p cloudkitty-core config:: -- water
# Every shipped config still parses + validates (incl. frozen exams):
cargo test -p cloudkitty-core --test shipped_configs
```

Expected: a cat lounging in a pond accrues bath to the ceiling and stops;
no Bath distress event exists in any swim-forever world; a config whose
ceiling+gain arithmetic crowds the safeguard is rejected at load naming
`[water] bath_gain_ceiling`.

**Chase sidestep**:

```bash
cargo test -p cloudkitty-core chase
cargo test -p cloudkitty-core --test joint_action_parity   # draw-shape + parity stay green
```

Expected: the blocked-lane fixture advances without a stall; same seed →
identical sidesteps; mirrored two-chaser fixture decorrelates; boxed-in
fixture stalls exactly as before with the patience clock governing.

**Equivalence guardrail**:

```bash
cargo test -p cloudkitty-rl --test welfare_validate_equivalence
```

Expected: full matrix agreement, including the reconciled eat-side
(stocked chow) and the pinned cuddle doctrine (busy neighbor = relief).

## The comparability break (one-time, deliberate)

```bash
# Regenerate the values golden ONCE, with justification in the PR:
UPDATE_GOLDENS=1 cargo test -p cloudkitty-rl --test run_json_golden
# Re-clear the constitutional long-run bars on the new dynamics:
cargo test -p cloudkitty-rl --test welfare_longrun
cargo test -p cloudkitty-core --test welfare_longrun
cargo test -p cloudkitty-core --test stuck_state_regression
# The stamp that marks the break (shown in any report header):
cargo run -p cloudkitty-rl --bin kitty-eval -- --brain needs_driven --ticks 500
```

Expected: `engine_defaults_sha256` differs from the pre-batch value
(b0865884…) — that is the designed mark; the world identity stamp is
unchanged (config untouched).

## What must NOT have changed

```bash
cargo test -p cloudkitty-rl --test eval_suite      # frozen exams: hashes still verify
cd crates/cloudkitty-py && maturin develop --release && python -m pytest tests/
```

Expected: exam freeze guard green (no exam file edited); Python surface
untouched (obs 182 / menu 40 / same API); two-process reproducibility
green. A pre-batch `snapshot.json` (same world shape) resumes cleanly.
