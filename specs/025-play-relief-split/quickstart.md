# Quickstart: Validating Per-Target Play Relief

Runnable proof that spec 025 landed correctly. Prerequisites: the
workspace toolchain (stable Rust); run everything from the repo root.
Long verifications run foreground with generous timeouts (house
practice).

## 1. The whole gate

```sh
cargo test --workspace
```

Expected: green, including the new routing and guard tests, the
regenerated golden, and `welfare_longrun`.

## 2. Routing values (US1)

```sh
cargo test -p cloudkitty-core --lib action
```

Expected: the play-routing tests assert one serviced tick moves the
play need by exactly 25 (bug), 35 (greeble), 20 each (duet, both
parties + partner stamp), 10 (solo), and 10 for a target that expired
mid-scene (the despawn fallback) — per
[contracts/play-relief-split.md](contracts/play-relief-split.md).

## 3. Guards (US2)

```sh
cargo test -p cloudkitty-core --lib config
```

Expected: rejection tests for each strict-ordering boundary (including
equality) and the duet ceiling, each error naming its keys and values,
the ceiling error teaching the duet economics; the defaults (10/20/25/35)
and the served config's values pass. See the validation table in
[data-model.md](data-model.md).

## 4. Back-compat (US3)

```sh
cargo test -p cloudkitty-core --lib config
git diff --stat main -- '*.toml' evals/
```

Expected: the old-shape-config test parses a today's-keys-only TOML
with the new fields defaulting in; the diff shows **no** `.toml`
changes outside test fixtures and **no** `evals/` changes (frozen
exams and hash pins untouched, served `cloudkitty.toml` unedited).

## 5. The break's visible mark

```sh
UPDATE_GOLDENS=1 cargo test -p cloudkitty-rl --test harness_policy
cargo test -p cloudkitty-rl
```

Expected: `run-json.golden.json` regenerates once (values golden),
then the suite is green with the new `engine_defaults_sha256` — the
stamp moves by construction (it hashes compiled defaults) and no
in-repo pin needs editing.

## 6. Stability that must NOT move

```sh
cargo test -p cloudkitty-core --test welfare_longrun
cargo test -p cloudkitty-rl --lib
[ -d crates/cloudkitty-server/tests/python ] && python -m pytest crates/cloudkitty-server/tests/python  # only if the surface exists; a present-but-failing surface must fail
```

Expected: welfare floors hold (more margin is fine; loosening is not),
observation dim 182 and codec 40 assertions green, snapshot loading
tests green.

## 7. Eyes-on (optional)

```sh
cargo run -p cloudkitty-server &
# open the client, watch a greeble scene end faster than a bug scene
```

Play scenes service faster in proportion to the gradient; duets remain
the visibly social choice. Kill the server after; the served deployment
is not touched by this spec.
