# Quickstart: validating camera mode

How to run the feature and check it against the spec's success criteria. Details
of the maths live in [data-model.md](./data-model.md); the boundary it must not
break lives in [contracts/camera.md](./contracts/camera.md).

---

## Prerequisites

The inert control must be present. It was built on `client-camera-notes` and is
deliberately unmerged, since a button that does nothing should not reach
production. Merge that branch in before starting, or the toggle has no seat.

```sh
git merge origin/client-camera-notes     # brings #camera-toggle + .camera-chip
```

## Run

```sh
cargo run                                # server + client on the configured port
```

Roster size is set in `cloudkitty.toml`. The spec requires validation at three
sizes (FR-022), so keep three configs or edit between runs — 3, 4 and 5 kitties,
which are prefixes of the same authored list.

## Automated checks

```sh
node client/test-motion.mjs              # 163 checks today
node client/test-meadow.mjs              # 78 checks today
```

Extend these two rather than adding a harness. Both eval the plain scripts into
one shared scope and assert against a mock context that throws on non-finite
draw arguments, which is what catches a transform that produces `NaN` at some
zoom. New checks belong roughly as:

| Harness | Covers |
|---|---|
| `test-motion.mjs` | frame geometry and the clamp, anchor choice, hysteresis, easing with a synthetic `dt`, the follow lifecycle table, the inverse transform round-tripping against the forward one |
| `test-meadow.mjs` | ground bakes at `bakeTile`, pond cache invalidates on a tile change, drift field still receives world dimensions |

The round-trip check is the highest-value new one: assert
`toWorld(forward(p)) === p` across the zoom range, which is what stops the two
transforms drifting apart.

---

## Validating against the success criteria

Automated where it can be, by eye where the criterion is a judgement. Marked
accordingly, since pretending a taste call is a test is how a gate stops meaning
anything.

| Criterion | How |
|---|---|
| **SC-001** apparent size | Measure a kitty at nominal and at the ceiling against the whole-world view on the same display. At least 1.3× at the widest, about 2× at nominal. |
| **SC-002** never cuts | Watch a full session at 5 kitties, including a group scattering to the ceiling and regathering. Automatable in part: assert no frame changes `aim` or `across` by more than the easing rate allows. |
| **SC-003** frame rate | Record sustained fps with camera mode on and off on the same display. Within 10%. **The one most likely to fail**, and the ground cache is why — see below. |
| **SC-004** off is unchanged | Compare the off state against a build without the feature. Pixel-identical is the bar. |
| **SC-005** aim rests on a kitty | Assert in the harness: the anchor id is always a kitty in the roster, never a computed midpoint. |
| **SC-006** anchor is not restless | 10 minutes at 5 kitties, count anchor changes. At most 3 a minute. |
| **SC-007** restore before first paint | Reload with camera mode on and a followed kitty. The first painted frame is already framed correctly — the meadow paints nothing until a world state exists, so there is no default position to travel from. |
| **SC-008** one action to follow | From the whole-world view, click a kitty. Camera mode on and following, in one action. |
| **SC-009** reduced motion | Set the OS preference. No easing at any zoom or anchor change. Verify the camera still tracks on served ticks — the rAF loop is not running in this state. |
| **SC-010** 3, 4, 5 kitties | **Owner judgement**, at each roster size independently. The 3-kitty case decides whether 10 tiles is the right floor; the 5-kitty case exercises the hysteresis. |
| **SC-011** view only | Two browsers on the same world, one zoomed, one not. Same positions, activities and needs at the same tick. |
| **SC-012** decoration is stable | Screenshot the same ground tiles at several zooms and with camera mode off. Identical decoration, tile for tile. |
| **SC-013** release without a moving target | At the zoom ceiling on a phone, release a followed kitty by clicking away from the kitties. One action, no need to hit her. |
| **SC-014** keyboard | Tab to the camera control, operate it with the keyboard alone, confirm a visible focus state. |

---

## Where this is most likely to go wrong

**Watch the ground cache first.** If SC-003 fails, the cause is almost certainly
a rebake happening per frame rather than per palette step. `render.js:507`
records a prior incident in this exact code where a guard mismatched every frame
and rebaked the whole ground at 60fps. Instrument the bake count over a full
world day and assert it is bounded before trusting a frame-rate reading — a
count is diagnostic where an fps number is only a symptom.

**Check the ponds at two zooms.** The pond cache keys on water tile positions
and not on the tile it was built at. Zoom in, zoom out, and confirm the
shorelines match the water rather than the previous zoom's geometry.

**Test the phone at the ceiling.** It is the worst case for every interaction
number in the feature: a kitty is roughly 23px, moving, possibly overlapped.
SC-013 exists because of it.

**Do not verify the deploy from the deploy report.** Fetch `anim.js` and
`render.js` from the live hosts and confirm the bytes, as with every previous
client change.
