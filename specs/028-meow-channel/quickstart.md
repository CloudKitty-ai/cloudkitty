# Quickstart: validating spec 028

Runnable end-to-end checks that the batch works. Prereqs: Rust toolchain, and
for the binding checks a venv with the cloudkitty-py dev install. Long runs
foreground (house rule).

## 1. The whole workspace is green

```sh
cargo test --workspace
```

Expect: all suites pass, including the extended mask-oracle property suite
(activity + message heads), determinism suites, and the new named tests below.

## 2. The structural guarantees, by name

```sh
cargo test -p cloudkitty-rl silent_is_never_masked
cargo test -p cloudkitty-rl the_mask_is_a_pure_oracle          # extended: both heads
cargo test -p cloudkitty-core announce_arming                  # hysteresis edge tests
cargo test -p cloudkitty-core a_pre_028_world_resumes_and_runs # committed fixture
cargo test -p cloudkitty-core the_retired_courtesy_trio_is_rejected_loudly
cargo test -p cloudkitty-rl distress_census_matches_the_instrument_convention
```

(Exact test names may vary at implementation; each guarantee must have a named
test — the list above is the acceptance checklist shape.)

## 3. Determinism including messages (SC-004)

```sh
cargo test -p cloudkitty-core --test determinism
cargo test -p cloudkitty-rl --test encoding_determinism
cargo test -p cloudkitty-rl --test mixed_control
```

Same seed + config → identical worlds including `recent_meows` and intensities.

## 4. Demonstrators use the channel (SC-001/002/003)

```sh
cargo run -p cloudkitty-rl --bin kitty-eval -- --config cloudkitty.toml \
  --seeds 1..10 --ticks 20000 --roster scripted
```

Expect in the report: nonzero GroomKitty activity (baseline was 0 in 800k),
announcements present, distress census block present. Cosleep share vs the
5.6% baseline is Experiments' measurement (their instruments, new engine) —
the engine-side check is that `Sleep { with: Some(_) }` decisions occur when
cuddle is real.

## 5. The wall behaves as promised (SC-006)

```sh
# a pre-028 artifact refuses loudly:
cargo run -p cloudkitty-rl --bin kitty-eval -- \
  --artifact policies/s6.ckpolicy --config cloudkitty.toml ; echo "exit: $?"
# expect: artifact_version / schema mismatch error, exit 1

# a config with a retired key refuses loudly:
#   add `courtesy_ticks = 10` under [meow] in a scratch copy, then:
cargo run -p cloudkitty-server -- --config /tmp/scratch.toml
# expect: '[meow] courtesy_ticks … retired by spec 028 …', nonzero exit
```

## 6. Python binding (mandatory rebuild + conformance)

```sh
cd crates/cloudkitty-py && maturin develop && pytest tests/
```

Expect: PettingZoo conformance green with `MultiDiscrete([34, 9])`; schema
constants report observation 3 / action 2 / mask 2; `recent_meows` returns
snake_case wire names.

## 7. The stamp, recorded not triaged

```sh
cargo test -p cloudkitty-rl the_engine_defaults_stamp_is_stable_and_well_formed
# then print the new stamp (throwaway test or kitty-eval json) and record it in
# the CHANGELOG Unreleased entry with markers [obs-schema] [rng-sequence] [stamp]
```

## 8. What NOT to run from here

- `update.sh` against the live box — **deploy is gated** until the policy seats
  are re-parked or a generation-3 artifact certifies (spec Rollout Notes).
- The re-baseline — Experiments runs it once, after merge, before the prereg
  freeze (§4 ordering).
