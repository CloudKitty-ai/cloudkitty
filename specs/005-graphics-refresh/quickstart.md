# Quickstart: Validating the Graphics Refresh

**Date**: 2026-07-19 | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

How to prove the feature works, story by story. This feature's acceptance is
visual by design (R10): the gallery gate, then scripted checks against a
live world. Contract: [contracts/viewer-contract.md](./contracts/viewer-contract.md) ·
model: [data-model.md](./data-model.md).

## Prerequisites

```bash
export PATH="$HOME/.cargo/bin:$PATH"   # cargo is not on the default PATH
cargo test --workspace                 # must stay green: zero engine changes
```

A world to watch (never the owner's live `snapshot.json`):

```bash
cargo run -p cloudkitty-server -- --snapshot /tmp/graphics-demo.json --fresh
# open the printed http://127.0.0.1:<port>
```

## 1. US1 — the gallery gate (SC-001, FR-001/002)

```bash
open client/gallery.html        # no server needed — straight from disk
```

Expected: every palette × every pose (idle, walking, pounce, eating,
drinking, grooming, loaf, sleep-curl) at 22px and 88px; a separate unlabeled
row of the three default kitties. Judge:

- [ ] Cuter than the emoji it replaces, *at 22px* (not only enlarged)
- [ ] The three defaults distinguishable at a glance, unlabeled
- [ ] Each pose readable without a caption

Record the outcome in `gallery-approval.md` (approved / revise / fallback).
**Nothing past this line is built or validated until that file says
approved.** Revision loop: edit `PALETTES`/`POSES` in `client/cat.js`,
reload the gallery — minutes, no other file.

## 2. US2 — identity in the live world (SC-003)

Open the live viewer. Cover the panel:

- [ ] Identify each kitty by fur alone; reload — appearances identical
- [ ] Restart the server (same config): appearances identical again
- [ ] A kitty that walked west faces left, and still faces left after stopping
- [ ] Press `g`: greebles appear/disappear exactly as before

## 3. US3 — gliding (SC-002)

- [ ] Walking cats visibly traverse tiles; no teleporting during normal play
- [ ] Kill the server mid-walk, restart it: on reconnect the view *snaps* —
      no cat slides across the map
- [ ] Hide the tab ~10 s, return: current state within one tick, no replay
- [ ] DevTools → Rendering → emulate `prefers-reduced-motion`: motion returns
      to per-tick snapping (the pre-refresh look), nothing else lost

## 4. US4 — actions and idle life (SC-004)

Watch until each occurs (the 006 duration minimums guarantee every action
holds ≥ 2 ticks; the panel's "doing" line is ground truth):

- [ ] Pounce (play/chase) shows wind-up + squash-and-stretch
- [ ] Eat / drink / groom / loaf each read distinctly without the panel
- [ ] Falling asleep is a curl transition; *staying* asleep is a held curl
      with soft breathing — the transition does not replay
- [ ] An idle cat flicks/twitches/blinks over a minute, and never appears
      to eat, walk, or act
- [ ] Under reduced motion: static pose per state, correct at every moment

## 5. US5 — served drama (SC-005)

Each beat, checked both ways — appears when its condition holds (panel as
ground truth), and never otherwise:

- [ ] Solo play ("pouncing at nothing"): an imaginary sparkle/butterfly that
      resembles no real element and vanishes when the play ends
- [ ] A hopeless chase given up (watch a greeble chase; `g` helps): brief
      sit + ear-droop beat
- [ ] Mid-pursuit: focused eyes for the pursuit's duration
- [ ] A meal/drink landing: brief relief sparkle at the kitty
- [ ] A long-wanted need (panel shows "has been wanting … for a while"):
      one thought bubble with that need's icon, gone when relieved
- [ ] A kitty with none of the above: no beats at all

## 6. US6 — ambient and juice (SC-006 partial)

- [ ] Water shimmer, sunbeam pulse + motes, occasional grass sway, drifting
      cloud shadows — noticeable when looked for, ignorable otherwise,
      never obscuring a cat or element
- [ ] Chow bowl at 5 vs 2 servings reads clearly different; empties as eaten
- [ ] Speech bubbles pop in; over-cat happiness bars ease
- [ ] Reduced motion: ambient gone entirely, juice becomes instant

## 7. Performance and hygiene (SC-006)

- [ ] One minute at default world size: no perceptible stutter (spot-check
      with the browser's FPS meter; expect <1% dropped frames)
- [ ] Hidden tab: performance profile shows no rAF work while hidden

## 8. Older servers (SC-008, FR-018)

No server change shipped with this feature, so any running server *is* a
pre-005 server. Still verify the stand-ins:

- [ ] Block `/config` (DevTools request blocking), reload: viewer runs on
      named fallbacks (800 ms easing, patience 60), console shows no errors

## 9. The suite (CI parity — nothing moved)

```bash
cargo fmt --all -- --check
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace
```

Expected: green and diff-free against this feature — `crates/` and
`cloudkitty.toml` are untouched.
