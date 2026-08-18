# Quickstart: validating camera zoom targets

Arithmetic lives in [data-model.md](./data-model.md); the boundary is in
[contracts/zoom.md](./contracts/zoom.md).

## Run

```sh
cargo run                      # server + client
node client/test-motion.mjs    # 206 checks today
node client/test-meadow.mjs    # 85
```

## The thing that makes this feature cheap to test

Almost every criterion is **arithmetic on `cssWidth`**, so it can be swept
headlessly across the whole viewport range without a browser — drive the real
`Camera` with a stubbed `cssWidth` and assert the band, the range and the
clamps at every size. That is a far stronger test than any single window can
give, and it is how the 3.5× spread was measured in the first place.

Reserve the browser for what only it can answer: whether 100px is the right
target, and whether detail actually holds at the widest.

| criterion | how |
|---|---|
| **SC-001** size band ≤ 2× | Sweep `cssWidth` from 340 to 1200; the largest floor tile over the smallest is under 2. Expect ~1.76. |
| **SC-002** fine at both ends | At every swept width, `floorPx` and `ceilingPx` both clear 44. |
| **SC-003** no flicker | Follows from SC-002 by construction; confirm in a browser at a 640px map, which is the viewport that used to straddle the threshold. |
| **SC-004** constant range | At every swept width where neither clamp binds, `ceilingTiles / floorTiles` is equal within 1%. |
| **SC-005** minimum tiles | At every swept width, the floor frames at least `minTiles`. |
| **SC-006** always crops | At every swept width, `ceilingTiles < world.width`. **Expect this to bind at 1000 and 1200 on today's 20-tile world** — that is the Fog dependency, not a bug. |
| **SC-007** camera off unchanged | 036's identity checks still pass, and the off path never reads the new dials. |
| **SC-008** dial pixel effect | Sweep and compare `aimDeadzoneTiles × tile`. Constant where the target is reachable; **fails at the small end as the criterion is currently scoped** — see research R5. |
| **SC-009** no jump on resize | Sweep `cssWidth` in 1px steps across the point where `minTiles` starts binding; `across` must be continuous. |

## Watch for

**The `bound` predicate reading a different ceiling from the fit.** They are
computed from the same pair or the anchor takes over at a width the camera never
reaches. Cheap to assert, invisible to the eye.

**The bake.** `test-meadow.mjs` already checks the ground bakes once across a
zoom sweep; it must still bake once, and its tile should now be display
independent. If the bake count moves, the tile stopped being the floor tile.

**Resize continuity at the clamp boundary**, which is the one place `across` can
change governing rule mid-session. 036's FR-008 forbids cuts and the easing
covers it, but the target it eases toward must not jump.

**Do not verify the deploy from the deploy report.** Fetch `anim.js` and
`render.js` from the live hosts and confirm the bytes.
