# Research: Vector Props — Retire the Remaining Emoji

**Date**: 2026-07-20 | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

Eight decisions (R1–R8). Grounded in the shipped 005 client — `cat.js`'s
drawing conventions, `anim.js`'s `VIEW`/phase machinery, `render.js`'s
emoji call sites — and the 2026-07-20 style conversation recorded in
BACKLOG.md and the 007 spec.

## R1 — A sibling file, one shared vocabulary

**Decision**: props live in a new `client/props.js`, loaded after `cat.js`
and before `render.js`. Classic scripts share top-level lexical scope, so
props reuse `cat.js`'s `TAU` and `OUTLINE_W` and read `VIEW` at draw time
(load order is irrelevant for call-time lookups). Same conventions
throughout: unit-box geometry (0..1, scaled by `size`), outline-first
(fill + `OUTLINE_W` stroke in a shade tone), a `phase` parameter, and the
cats' `fine = size >= 44` detail threshold.

**Rationale**: cats and props are judged and revised at separate gates —
separate files keep each revision loop single-file — while shared
conventions and constants keep them literally one drawing hand (FR-001).

**Alternatives considered**: growing `cat.js` (one gate's revisions churn
the other's approved file); a generic `drawProp(kind, opts)` dispatcher
(props have too-different options — servings vs. colorway vs. need — so
named functions `drawBowl`/`drawButterfly`/`drawGreebleWisp`/`drawSleepZs`
/`drawHeart`/`drawNeedIcon` are the honest API).

## R2 — Butterfly identity mirrors cat identity

**Decision**: `BUTTERFLY_COLORWAYS` — three curated entries (soft lavender,
pale lemon, peachy-white; wing fill + wing shade + body ink) — and
`butterflyColorwayFor(elementId) = BUTTERFLY_COLORWAYS[id % 3]`.

**Rationale**: element ids are allocated monotonically and are stable for
the element's lifetime, exactly the property kitty ids gave `appearanceFor`
— so each butterfly is *that* butterfly until it expires (FR-005, SC-003).
The three hues are deliberately absent from the existing world palette so
butterflies read as the meadow's color accents.

**Alternatives considered**: random colorway per session (breaks reload
stability, SC-003); one fixed color (loses the each-one-is-someone charm
the cats established).

## R3 — The airborne read: bob + detached shadow, phase from the view layer

**Decision**: the butterfly draws at a hover offset (`bobAmp · sin` of its
phase) above a small ground shadow that does *not* bob; wings flap by
scaling wing width on a faster cycle of the same phase. The phase comes
from a new `view.propPhaseFor(el)` in `anim.js` — wall-clock cycle seeded
by element id (mirroring `motionFor`'s per-kitty seeding), returning 0 for
still frames. Agitation: `render.js` derives an `agitatedIds` set once per
frame from served data — every `kitty.pursuit.target` that names an
element — and passes `agitated: true` to those butterflies, which
multiplies the flap rate by the named panic multiplier (FR-006).

**Rationale**: the gap between critter and shadow is what sells "flying"
at 22px, and a hovering flutterer forgives the engine's one-tile hops in a
way a crawler never could. Phase stays in `anim.js` so reduced-motion and
discontinuity handling remain centralized (the 005 rule); agitation is a
pure function of the newest served state, recomputed per frame, no store.

**Alternatives considered**: easing butterfly positions between ticks
(elements deliberately don't glide — 005 R4 — and a flutter-hop reads
fine); tracking agitation as a beat in the one-shot store (it is sustained
served state, not a transition — the pursuit-face precedent applies).

## R4 — The bowl: the mound is the meter

**Decision**: `drawBowl(ctx, {servings, size, x, y})` — squat terracotta
trapezoid with a darker rim band, kibble drawn as a mound of dots whose
count/height maps the served serving count (visual clamp at 5, matching
today's meter clamp); `servings = 0` draws the empty bowl. The separate
white-track meter in `render.js` is deleted; a tiny fish decal appears at
`fine` sizes only.

**Rationale**: FR-004 verbatim — the data display and the drawing become
one thing, which is both cuter and more honest than a bar next to a
fish-cake.

**Alternatives considered**: keeping the meter under the new bowl (two
displays of one number — rejected); mound height as a continuous fill
(dot-count reads better at 22px and matches "servings" being discrete).

## R5 — Overlays and icons: one ink, reuse aggressively

**Decision**: `drawSleepZs` (three rounded Z strokes, staggered, drifting
up and fading on phase; a static ladder at phase 0), `drawHeart` (plump
heart, blush fill, dark outline, one highlight; scale pulses on phase),
and `drawNeedIcon(need)` dispatching to mini-props in one ink weight: the
bowl (drawn by `drawBowl` at icon scale with a fixed mound), a water drop,
the Zs, a yarn ball (circle, two wrap arcs, trailing thread), the heart,
and a three-bubble soap cluster for bath. `render.js`'s `NEED_ICONS` emoji
map and the `emoji()` helper are deleted once all call sites are swapped
(FR-010's zero-emoji sweep is grep-able: no `fillText` of emoji remains on
the canvas path).

**Rationale**: reuse makes consistency free (the thought-bubble bowl *is*
the world bowl), and deleting the emoji helper turns FR-010 from a visual
claim into a structural one.

**Alternatives considered**: a tub icon for bath (mud at 15px — the spec
already settled on bubbles); keeping `emoji()` around "just in case" (dead
code invites regressions of FR-010).

## R6 — The greeble wisp: not-quite-there, decided at the gate

**Decision**: `drawGreebleWisp(ctx, {face, phase, ...})` — teardrop blob
with a wavy skirt, hollow eyes, slow bob on phase, drawn with a softer,
slightly dashed outline (`setLineDash` with a named pattern, reset after)
— rendered only under the existing `showGreebles` flag at the existing
0.55 alpha. `face` is `'blank' | 'grin'`; **the gallery renders both side
by side** and the gate records the winner (spec's one open question,
FR-003), after which the loser remains available as a parameter but
unused.

**Rationale**: the one thing in the world that is deliberately
not-quite-there deserves the one outline treatment nothing else uses; the
face is taste, and taste gets decided where taste is judged.

**Alternatives considered**: deciding the face in the spec (the gallery
exists precisely so looks are judged rendered, not described).

## R7 — Tunables and palette placement

**Decision**: animation numbers join the frozen `VIEW` in `anim.js` under
a `props` sub-object (flap period, panic multiplier, bob amplitude, heart
pulse period, Z drift period/rise — plus nothing inline anywhere); colors
live in a named `PROPS` palette block in `props.js` (terracotta pair, the
three butterfly colorways, ink, blush, soap blue), mirroring how
`PALETTES` lives with the cats.

**Rationale**: FR-012 says tunables live in "the established tunables
home" — that is `VIEW`; palettes are data-of-the-drawing and live beside
the drawings, exactly the split 005 shipped.

**Alternatives considered**: a separate `PROP_TUNABLES` in `props.js`
(splits the Article VI audit surface across files for no gain).

## R8 — Verification without new machinery

**Decision**: the 005 three-tier pattern reused verbatim: the gallery gate
(now including the greeble-face decision and the same-hand judgement
beside the cat portraits), quickstart visual checks per story (bowl
ordering, butterfly distinguishability/stability, panic flap, reduced
motion, and an explicit zero-emoji sweep), and headless node harnesses:
every prop × state × size × phase through the mock-ctx (exception and
non-finite guard), `butterflyColorwayFor` stability/distinctness, and a
structural grep that the canvas path contains no emoji glyph or `emoji()`
call. The Rust suite must pass untouched and `git diff crates/
cloudkitty.toml` must be empty (SC-007) — checked in quickstart and tasks.

**Rationale**: acceptance is visual by nature; the automatable core is the
derivation logic and the draw-path safety, same as 005 — no new toolchain
for a feature this shape (the standing decision from 005 R10).

**Alternatives considered**: pixel-snapshot tests (flaky cross-platform;
the gallery gives humans the same signal reliably — unchanged verdict).
