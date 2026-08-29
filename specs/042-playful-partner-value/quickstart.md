# Quickstart: validating Playful 2.0

Per-commit validation. References: [data-model.md](data-model.md),
[contracts/behavior-dials.md](contracts/behavior-dials.md),
research.md D9 (the test strategy — read before running; rule 6).

## Prerequisites

- `cargo test --workspace` green at the branch base (e489d4b lineage).
- Note the golden evolution digest pin (`7b361b2a…`): it must stay
  GREEN through this whole feature — a red golden here means the
  inert-launch claim failed (HALT), the opposite of 041's commit-2
  expectation.

## Commit 1 — the config surface

```sh
cargo test -p cloudkitty-core config
cargo test --workspace
```

Expected: nan/negativity guards for all twelve dials pass (each shown
red before its validate.rs entry); both shipped-config sweeps green
(no keys added to any toml); the defaults-stamp tests green with the
stamp UNMOVED (skip-at-identity — compare `engine_defaults_sha256`
before/after the commit: identical).

## Commit 2 — the behavior rewiring

```sh
cargo test -p cloudkitty-core behavior
cargo test --workspace
```

Expected green, each new guard red-first per research D9:

- identity guard: all-defaults pick equals today's on a staged mixed
  field (friends + critters + distance ties)
- value/eligibility/threshold/wait/seriousness/appeal guards, one per
  dial, including the D2 admission rule (busy adjacent friend NOT
  picked at defaults) and the busy-adjacent → `play_solo` fallback
- comfort-weight guards in both directions + all-1.0 identity
- golden evolution digest ×3 GREEN (byte-identical launch, SC-001)
- full selection/playful/etiquette battery green at defaults

## End-to-end (pre-merge)

1. `cargo test --workspace` — full suite; re-read D9's red-first list
   and confirm every guard was seen red (running is not reading).
2. Golden digest ×3 green; `engine_defaults_sha256` unmoved.
3. Scratch config with real weights (e.g. `w_value = 1.0`,
   `t_partner = 20`, `comfort_weight.eat = 1.5`): boot a local
   server, watch a playful seat redirect toward a high-need friend
   and get serious on a food peak — a smoke look, not a census.

## Post-merge

Experiments' joint comfort × score × weights campaign prices the
dials (their lane); `family-11-r5` before any roster decision;
owner pins demo/served values.
