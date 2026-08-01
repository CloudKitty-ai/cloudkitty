# Quickstart: Retire the Engine-Enforced Meow Cooldown (spec 023)

Validation guide. Semantics: [contracts/meow-channel.md](contracts/meow-channel.md).
Sequenced after spec 022's implementation on the shared branch.

## Build & gates

```bash
cargo build --workspace
cargo test -p cloudkitty-core          # emission, courtesy, config rename
cargo test -p cloudkitty-rl            # SC-004 gate: passes UNCHANGED
cargo clippy --workspace -- -D warnings
cargo fmt --check
```

## Targeted proof points

```bash
# The swallow is gone; repeats emit and stamp
cargo test -p cloudkitty-core meow

# Courtesy: spacing invariant incl. the approach-dance (long-running —
# foreground, generous timeout, per house practice)
cargo test -p cloudkitty-core spacing

# Config: renamed keys, retired keys rejected, partial table default-fills
cargo test -p cloudkitty-core config -- meow
```

## Manual smoke (optional)

Run the server on the updated `cloudkitty.toml`: built-in kitties meow as
occasionally as ever (courtesy), but a persistently urgent kitty repeats
every 5 ticks instead of going dark for 5 of every 15 — watch a hungry cat
near empty bowls keep saying so. An approach dance shows "Wait for me!" at
most once per 10 ticks, never every other tick.

## Certification note

Same posture as 022: config hash and engine-defaults stamp change; no
byte-comparison validity across the change; the batch recert re-establishes
all numbers after 022+023 land together. Hand Experiments the FINDINGS echo
of the reward-structure dependency (FR-011) at PR time.
