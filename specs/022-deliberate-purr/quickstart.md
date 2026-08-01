# Quickstart: Deliberate Purring & the Quiet Motor (spec 022)

Validation guide — proves the feature end-to-end. Implementation detail
lives in [plan.md](plan.md) / [tasks.md](tasks.md); semantics in
[contracts/deliberate-purr.md](contracts/deliberate-purr.md).

## Prerequisites

- Workspace toolchain (`cargo`), repo root as CWD.
- No new dependencies, services, or env vars.

## Build & gates

```bash
cargo build --workspace
cargo test -p cloudkitty-core          # engine: purr semantics, config, determinism
cargo test -p cloudkitty-rl            # SC-005: shapes/harness pass UNCHANGED
cargo clippy --workspace -- -D warnings
cargo fmt --check
```

Expected: all green. Any `cloudkitty-rl` failure is a stop-the-line signal —
this spec must not move observation/menu/mask shapes.

## Targeted proof points

```bash
# Purr semantics (names per contract tests 1–8)
cargo test -p cloudkitty-core purr

# Config: retired knob rejected loudly
cargo test -p cloudkitty-core config -- retired

# Determinism incl. mid-purr save/restore + legacy-snapshot convention
cargo test -p cloudkitty-core determinism
```

The SC-004 occupancy test (±2pp of ≈30.8% over ≥20k ticks) runs in the
core suite; it is long-running — run it foreground with a generous timeout,
per house practice.

## Manual smoke (optional, viewer-level)

```bash
cargo run -p cloudkitty-server    # serves ./cloudkitty.toml
# open the client
```

Expect: kitties visibly purring roughly as often as ever (card shows
"· purring 💕"), but **no** "purrrr" bubbles in the meadow except when a
policy kitty deliberately purrs — with built-ins only, effectively silent.
Set `announce_probability = 1.0` temporarily and bubbles return on every
purr start.

## Certification note

`kitty-eval` bare runs load the updated `cloudkitty.toml`; the world stamp's
`config_sha256` and `engine_defaults_sha256` both change — expected and
self-describing (issue #76). No byte-comparison against pre-022 reports is
valid (RNG stream shift, stated in the spec); certification numbers are
re-established by the batch recert after 022+023 land together.
