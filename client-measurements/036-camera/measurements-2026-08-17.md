# Camera mode: what was measured, headless (2026-08-17)

Against the live served world on the 036 branch, using the shipped
`Camera` class rather than a model of it. Nothing here needed a browser.

## SC-006 — anchor changes per minute (bar: <= 3)

Three samples, and they disagree enough that one is not a verdict:

| window | ceiling bound | anchor changes/min | visible/min |
|---|---|---|---|
| 5.0 min | not recorded | 7.60 | not recorded |
| 2.5 min | 84.1% | 2.40 | 1.60 |
| **9.5 min** | 43.1% | **5.79** | **2.42** |

**The criterion does not say which quantity it means.** Below the ceiling
the aim is the centre of mass, so an anchor change moves nothing and
cannot read as restless. On the purpose clause ("reads as deliberate
rather than restless") the visible rate is the one that matters and the
9.5-minute sample passes at 2.42. Read literally, 5.79 fails.

It is marginal either way: at the 84%-bound spread seen in the 2.5-minute
window, the visible rate scales to roughly 4.9/min and fails.

## Hysteresis sweep (376 recorded ticks, 64% bound, replayed)

| hysteresis | anchor changes/min | visible/min |
|---|---|---|
| **1.5 (shipped)** | 4.20 | **3.00** |
| 2.0 | 2.40 | 1.40 |
| 2.5 | 2.00 | 1.00 |
| 3.0 | 1.20 | 0.80 |
| 4.0 | 0.80 | 0.40 |

The shipped value landed exactly ON the bar with no margin. **Raised to
2.0 by the owner, 2026-08-18**, which takes the LITERAL count to 2.40/min
and the visible count to 1.40/min. Her reasoning is worth keeping: an
invisible anchor change today becomes a visible one the moment something
makes the anchor drive the aim more often, and that regression would
arrive with no obvious cause. So SC-006 is held against all changes, not
only the ones that currently show.

## How often the ceiling binds

43% over 9.5 minutes, 64% and 84% over shorter windows. An earlier
57-tick sample showed 0% and I generalised from it that "the ceiling
never binds" -- that was wrong. The clowder gathers and scatters, so the
anchor is load-bearing far more often than that sample suggested.

## Camera stillness

The aim moves >1px on 60% of ticks, so the camera is still 40% of the
time. Earlier deadzone modelling predicted 78% still, and the two are NOT
comparable: that measured the TARGET with no easing, this measures the
eased aim. The deadzone stops the target chasing; the easing tail still
creeps toward it.

**A second lever exists if more stillness is wanted**: snap the aim to
its goal once it is within a small epsilon, which kills the tail without
touching the deadzone or the rates.

## Bake counts (SC-003's diagnostic half)

Across a full zoom sweep with panning, in `test-meadow.mjs`:

- ground bakes: **1**
- pond layer builds: **1**
- distinct bake tiles: **1**

Keyed to the live zoom instead (the naive implementation): 121 rebakes
and 77 distinct tiles. So the per-frame ground cost is one `drawImage`,
which is what SC-003 needs. **The frame-rate half still needs a browser.**

## FR-022 roster sweep

900 states across 3-, 4- and 5-kitty rosters on deterministic walks. The
zoom floor, the ceiling, finite aim, the world clamp (FR-029) and a real
anchor hold at every one. SC-010's aesthetic judgement still needs the
owner's eye.

## Containment, with the centre-of-mass aim (2026-08-18)

301 ticks. While the FIT governs, **100%** of ticks hold every kitty, with
a worst overhang of 0.00 tiles. While the CEILING binds, 11.4% hold
everyone — which is FR-005 working, not failing: past the ceiling the
camera stops fitting and lets the wanderer go.

This is what sent SC-005 back to the owner, and she reworded it to the
thing that actually matters: never a frame with NOBODY in it. That now
holds by construction (the aim is a kitty whenever the ceiling binds, and
the clamp can only push the frame to the world's edge, not past her) and
is asserted across all 900 swept roster states.

## SC-014 — keyboard (2026-08-18, owner)

Passes. With macOS keyboard navigation ON: the camera control is reachable
by Tab, the focus ring is visible, and Space and Enter both toggle it.
Also verified alongside the per-card `?` and the card expand/collapse.

**With keyboard navigation OFF, Safari reaches no button on the page at
all** — not the camera control, not the theme toggle, not expand/collapse.
The one thing it does reach is the About card, which is a
`<details>`/`<summary>` rather than a `<button>`. That is Safari's default
and it is identical before and after 036; nothing here introduced it, and
the markup is a real `<button type="button">` with no tabindex override,
`aria-pressed`, `aria-label` and a `:focus-visible` outline.

## Invisible bowls: what has already been ruled out (2026-08-18)

Owner reported sporadic invisible entities including food, and "only one
food bowl visible on the entire map, even disabling camera". **No drawing
fault was reproducible.** Against the live world, with 6 chow served:

| suspect | finding |
|---|---|
| not served | 6 chow in `/world` |
| dropped before drawing | all 6 reach `drawElement` in a full frame |
| faded out | alpha 1.00 for every bowl across 51 ticks |
| hidden under cover | 0 cover pieces over any bowl tile |
| mid-crossfade black | `props.js` uses no hex-only helpers |
| `spriteOrder` filtering | pure sort, drops nothing |

Do not re-run these. Start from what they leave standing.

**Two pre-existing explanations fit without any bug.** A bowl draws at 66%
of a tile — about 20px with the camera off, 41px with it on — which is the
"too small and hard to see" item written up in the v3 plan's Phase 5 and
never built; camera mode doubles it, so the off state can read as a
regression when it is the old baseline. And a bowl despawns the tick its
last serving goes (BACKLOG ~line 179), so bowls wink out and respawn
constantly: their ids ran 4586 to 4663 in about two minutes here.

**What would prove a real bug**: an EMPTY tile where `/world` says a bowl
is. Fetch `/world`, take the chow positions, and look at those exact
tiles with the camera off.

### Round two: reload fixes it (owner, 2026-08-18)

New facts: a reload clears it, it happens with the camera both on and
off, and bugs and some water go missing alongside the bowls.

Camera-independent plus reload-fixable rules out the camera and points at
long-lived client state. Two more suspects fell:

- **The fade bookkeeping is sound.** `newElementIds` is cleared outright
  on a discontinuity (so everything draws at alpha 1) and recomputed on
  every other push. There is no path that leaves it stale.
- **No pacing mismatch.** The served tick measures 800ms against a
  `tickMsFallback` of 800ms, so `progress` cannot be stuck low and new
  elements cannot be trapped part-way through their fade.

**What that leaves is the state pipeline, not the drawing.** If states
stop arriving or stop being promoted, everything that SPAWNED since never
appears — new bowls, new bugs, newly-spawned water — while what is
already on screen stays put. A reload re-fetches and re-subscribes. This
area has stalled before (#196, the tile-boundary stall).

**The one question to ask before reloading next time: is the tick counter
still advancing, and are the cats still moving?**

- Tick frozen → the stream stalled; not a drawing bug, camera innocent.
- Tick advancing but entities missing → a real render/alpha bug, and a
  far narrower target than anything above.

Nothing measurable from outside the browser separates those two.
