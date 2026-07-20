# Quickstart: Validating Vector Props

**Date**: 2026-07-20 | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

Acceptance is visual (research R8), gated like 005: gallery first, then
scripted checks against a live world. Contract:
[contracts/props-contract.md](./contracts/props-contract.md) · model:
[data-model.md](./data-model.md).

## Prerequisites

```bash
export PATH="$HOME/.cargo/bin:$PATH"   # cargo is not on the default PATH
cargo test --workspace                 # must stay green: zero engine changes
```

A live world (never the owner's real snapshot; note the 4-kitty roster
needs `--fresh` over any 3-kitty save):

```bash
cargo run -p cloudkitty-server -- --snapshot /tmp/props-demo.json --fresh
```

## 1. US1 — the props gallery gate (SC-001, FR-002/003)

```bash
open client/gallery.html        # no server needed
```

Expected: a props section with every prop × state at 22px and 88px — bowl
at 5/3/1/0 servings, three butterfly colorways at two flap positions (plus
an agitated sample), **both greeble faces side by side** at in-world
translucency, Zs, heart, all six thought icons — within visual reach of
the cat portraits. Judge:

- [ ] Same drawing hand as the approved cats, at 22px
- [ ] Bowl levels orderable at a glance; empty bowl reads as empty, not missing
- [ ] The three butterflies distinguishable unlabeled
- [ ] Each thought icon legible at bubble scale
- [ ] Greeble face chosen: blank or grin

Record the outcome (face decision included) in `gallery-approval.md`.
**Nothing past this line replaces a live emoji until it says approved.**
Revision loop: edit `client/props.js`, reload the gallery.

## 2. US2 — bowl and butterfly live (SC-002/003/004)

Open the live viewer:

- [ ] Chow reads as a terracotta bowl; watch a meal — the mound shrinks
      bite by bite; no meter bar remains
- [ ] Two bowls at different servings orderable from across the map
- [ ] Butterflies hover with a detached shadow; wings flap; tile hops read
      as flight
- [ ] Panel covered: tell two butterflies apart by color; reload — colors
      identical; restart the server — identical again
- [ ] Watch a chase begin (panel: "chasing a bug 🐛" — prose emoji is out
      of scope): the hunted butterfly's flap visibly quickens within a
      tick, calms when the chase ends
- [ ] DevTools reduced-motion emulation: butterflies and bowls static,
      kibble level and colorways fully readable

## 3. US3 — overlays, wisp, icons (SC-005/006)

- [ ] Press `g`: the wisp appears at the familiar translucency with its
      softly dashed outline and slow bob; press again — gone; default
      state on a fresh load is hidden, exactly as ever
- [ ] A sleeping kitty: drawn Zs drift and fade (static ladder under
      reduced motion)
- [ ] A cuddling pair: the drawn heart pulses softly between them
- [ ] Wait out (or induce) a long want for several needs: each thought
      bubble shows its drawn icon — bowl, drop, Zs, yarn, heart, soap
      bubbles
- [ ] Solo play still conjures the golden star, and it reads imaginary —
      never mistakable for a butterfly
- [ ] The zero-emoji sweep: watch every activity and beat with the toggle
      on and off — no platform emoji anywhere on the canvas; structurally,
      `grep -n "emoji(" client/render.js` finds no canvas call sites

## 4. Hygiene and closing checks (SC-006/007)

- [ ] One minute at default world size: no perceptible stutter (props are
      cheaper than the text glyphs they replaced)
- [ ] `git diff --stat crates/ cloudkitty.toml` → empty (zero engine or
      server changes)

```bash
cargo fmt --all -- --check
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace
```

Expected: green and untouched — the Rust suite's only job here is to prove
nothing outside the client moved.
