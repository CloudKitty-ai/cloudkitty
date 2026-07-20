# Quickstart: Validating the Meadow

**Date**: 2026-07-20 | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

Acceptance is visual (research R8), judged live — the ground only reads in
context, so the live viewer is this feature's gallery. Contract:
[contracts/meadow-contract.md](./contracts/meadow-contract.md) · model:
[data-model.md](./data-model.md).

## Prerequisites

```bash
export PATH="$HOME/.cargo/bin:$PATH"   # cargo is not on the default PATH
cargo test --workspace                 # must stay green: zero engine changes
```

Two live demo worlds (never the owner's real snapshot):

```bash
# default size (32×32 per cloudkitty.toml)
cargo run -p cloudkitty-server -- --snapshot /tmp/meadow-demo.json --fresh

# a larger world (≥4× area) for SC-002: a temp config copy with [world]
# width/height raised to 64 -- the real cloudkitty.toml stays untouched
sed 's/^width = 32/width = 64/; s/^height = 32/height = 64/' cloudkitty.toml \
  > /tmp/meadow-big.toml
cargo run -p cloudkitty-server -- --config /tmp/meadow-big.toml \
  --snapshot /tmp/meadow-demo-big.json --fresh
```

## 1. US1 — the organic meadow (SC-001/SC-002, FR-001/002/003/004)

- [ ] The ground reads as meadow: ≥3 close grass tones, sparse tufts/clover/
      flowers, no alternating-square pattern anywhere
- [ ] Reload twice: every tone and every scatter mark in identical places
- [ ] Restart the server (same world): still identical
- [ ] Press `l`: grid lines appear over the meadow; press again: gone;
      fresh load starts hidden; footer hints the key
- [ ] On the larger world, pan everywhere: no repeated patch, no diagonal
      banding, density looks uniform per screen area

## 2. US2 — ponds (SC-003, FR-005/006)

- [ ] Adjacent water renders as one pond: no internal tile seams at any
      junction (convex, concave, diagonal neighbors)
- [ ] A single water tile is a small rounded pool
- [ ] A large-enough pond carries one lily pad; it stays put across reloads
- [ ] Shimmer still plays on pond surfaces; a spawning/expiring water tile
      still fades in/bows out
- [ ] Watch a drink: the kitty stops on the same tile as before — shoreline
      is visual only
- [ ] A pond touching the world boundary meets the edge frame cleanly

## 3. US3 — the world edge (FR-007)

- [ ] Default world: fringe frames all four sides and corners
- [ ] Larger world: same, scaled to its bounds
- [ ] A kitty walking the outermost tiles stays fully legible — the frame
      never covers a resident or prop

## 4. US4 — sunbeams as light (FR-008)

- [ ] Each sunbeam is a soft radial glow bleeding past its tile — no hard
      square edge
- [ ] Pulse and dust motes play over the glow exactly as before
- [ ] Two adjacent beams blend without banding or blow-out
- [ ] DevTools reduced-motion emulation: the glow holds still, plainly
      readable as a sunbeam; a napping kitty reads clearly on it

## 5. US5 — worn paths (FR-009)

- [ ] Fresh load: nothing visible; footer lists `p` beside the `g` and `l`
      hints
- [ ] Press `p`, let kitties walk: trails appear along their actual routes,
      darken with repetition, fade over minutes
- [ ] Toggle off/on: hidden instantly, back instantly — including passage
      accumulated while hidden
- [ ] Reload: trails gone, accumulation restarts
- [ ] Kill and restart the server mid-watch (a discontinuity): trails clear

## 6. Legibility, hygiene, closing (SC-004/005/006/007)

- [ ] Legibility sweep: every kitty and prop locatable within two seconds
      against the new ground; thought bubbles, speech bubbles, happiness
      bars, butterflies, bowls all read instantly
- [ ] All three toggles (`g`, `l`, `p`) independent, correct defaults,
      footer hints present
- [ ] One minute at default size with every layer on: no perceptible
      stutter
- [ ] `git diff --stat crates/ cloudkitty.toml` → empty

```bash
cargo fmt --all -- --check
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace
node client/test-meadow.mjs   # or the harness path tasks establishes
```

Expected: Rust green and untouched; headless harness green (hash
determinism, pond grouping/shoreline cases, path memory
accumulate/decay/clear, draw sweeps with the non-finite guard).

## 7. The FR-014 checkpoint (SC-008)

Judged by Elizabeth in the live viewer on both demo worlds, all layers on
and off, before push/PR. Revisions loop through `client/meadow.js` (and its
palette/tunables) only. Record the outcome — approved look, revision rounds,
any layer decisions — in `meadow-approval.md`. **Nothing ships as the
default view until it says approved.**
