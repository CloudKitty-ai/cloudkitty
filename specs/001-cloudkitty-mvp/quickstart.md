# Quickstart & Validation: CloudKitty MVP

**Date**: 2026-07-18 | **Plan**: [plan.md](./plan.md)

How to run CloudKitty and verify, end-to-end, that the implementation satisfies the
spec's acceptance criteria. Wire shapes: [contracts/http-api.md](./contracts/http-api.md).

## Prerequisites

- Rust stable toolchain (`rustup default stable`), edition 2021+
- A modern browser
- No other services, databases, or build tools required

## Run it

```bash
# from repo root — starts the server with the shipped default config
cargo run

# variants
cargo run -- --fresh                 # ignore any existing snapshot.json
cargo run -- --config my.toml        # alternate config file
```

Expected: startup log line with bind address (default `http://127.0.0.1:8090`),
world generated (or resumed from `snapshot.json`), tick loop running at 800 ms.

Open `http://127.0.0.1:8090` → the viewer shows a 32×32 grid, ≥2 kitties, and
water/chow/bug/sunbeam elements.

## Validation scenarios

### V1. Living world (spec US1 / SC-001)

Watch the viewer for ~10 minutes at defaults. Confirm each kitty is seen moving,
eating, drinking, sleeping (ZZZ overlay; faster in sunbeams), playing, grooming,
and meowing (speech bubbles); happiness indicators respond; purring occurs when
happy.

### V2. Constitution invariants (US2 / SC-002) — CI gate

```bash
cargo test --workspace                  # everything
cargo test -p cloudkitty-core --test invariants_proptest   # just the gate
```

Expected: proptest drives randomized configs/behaviors (including adversarial) for
≥10,000 ticks headless; zero violations of: population ≥ 2, no kitty removed, needs
∈ [0,100], happiness ≥ floor, safeguard guarantee, edge-triggered distress. Any
failure prints a reproducible seed (persisted in `proptest-regressions/`).

### V3. Behavior variation (US3 / SC-005)

Default config assigns `needs_driven` and `playful` to different kitties. Watch (or
run the dedicated unit test comparing 1,000-tick action histories): the playful
kitty plays/chases ≥50% more often.

### V4. Restart persistence (US4 / SC-003)

```bash
cargo run                    # let it run ≥100 ticks (or Ctrl-C for final save)
# Ctrl-C  → "snapshot saved" log
cargo run                    # resumes: same positions, needs, elements, tick, RNG
cargo run -- --fresh         # discards snapshot, new world
```

Also covered by the save/restore determinism test: mid-run snapshot → resumed run's
world hash equals uninterrupted run's hash at the same tick.

### V5. Determinism (SC-004)

```bash
cargo test -p cloudkitty-core determinism
```

Two worlds, same seed/config, N ticks → identical serialized state. 100% stable.

### V6. Config shaping & rejection (US5 / SC-006)

```bash
cargo run -- --config bad.toml    # e.g. one kitty, or chow max > floor(area/32)
```

Expected: non-zero exit; error names the field, offending value, and allowed range
(e.g. `config error: [[kitty]] roster has 1 kitty; the constitution requires at
least 2`). Valid edits (tick_ms, world size, element min/max) visibly change the
simulation on next start.

### V7. Greeble invisibility (US6 / SC-007)

```bash
curl -s localhost:8090/world | grep -c greeble    # ≥1 when a greeble is alive
```

Viewer shows kitties chasing empty tiles; pressing `g` in the viewer reveals
greebles. The server integration test asserts greebles in the payload and ≥2 WS
frames with increasing ticks.

### V8. Live updates (SC-008)

Open two browser tabs — both update every tick. Kill and reopen a tab: it repaints
from `GET /world` and resumes live updates; the simulation never notices.

## Troubleshooting

| Symptom | Check |
|---------|-------|
| refuses to start, mentions snapshot | snapshot failed validation — read the error; `--fresh` to discard deliberately |
| kitties idle a lot | needs may be low (content cats idle); check `GET /kitties` need values |
| nothing renders | browser console; confirm `GET /world` returns JSON and `/ws` upgrades |
| port in use | set a different bind port in `cloudkitty.toml` |
