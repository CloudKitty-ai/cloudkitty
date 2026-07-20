# Implementation Plan: Vector Props — Retire the Remaining Emoji

**Branch**: `props-style-direction` | **Date**: 2026-07-20 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/007-vector-props/spec.md`

## Summary

Replace every platform emoji on the world canvas with parametric props drawn
in the cats' own vocabulary: a terracotta bowl whose drawn kibble mound *is*
the servings display, butterflies with stable per-individual colorways and
an airborne hover-and-shadow treatment (panic-flapping under served
pursuit), a not-quite-there greeble wisp behind the unchanged `g` toggle,
drifting drawn Zs, a heartbeat heart, and six one-ink thought icons.
Technically: one new `client/props.js` sharing `cat.js`'s drawing
conventions and consumed by both the gallery (which gains a props section
and a second approval gate, greeble face included) and `render.js` (whose
emoji call sites are swapped out); prop animation tunables join the frozen
`VIEW` object. Zero engine or server changes — every visual derives from
fields every current server already serves. This is 005's architecture
exercised, not extended: no new pipelines, no new state stores.

## Technical Context

**Language/Version**: Vanilla JavaScript (ES2020+, browser-native, no build
step), HTML5 Canvas 2D — identical to the shipped 005 client.

**Primary Dependencies**: none. Plain scripts; `props.js` uses the same
global-lexical-scope sharing the existing files use (top-level `const`s in
classic scripts are visible to later scripts), so it reuses `cat.js`'s
`TAU`/`OUTLINE_W` conventions and reads `VIEW` at draw time.

**Storage**: n/a — props render served state; nothing persists.

**Testing**: the 005 three-tier pattern: (1) the gallery gate as the human
acceptance test for the look, (2) quickstart visual checks per story, (3)
headless node sweeps over every prop × state × size × phase combination via
the mock-ctx harness (exceptions and non-finite coordinates), plus the Rust
suite staying green with an empty `crates/` diff as an explicit check.

**Target Platform**: modern desktop browsers, retina-aware, as 005.

**Project Type**: web client (static files, served by the existing
fallback; gallery works from `file://`).

**Performance Goals**: no regression to 005's SC-006 (smooth animation at
default world size). Props are a handful of path fills per element — strictly
cheaper than the emoji text-rendering they replace in most cases; the only
additions (shadow ellipse, second wing pass) are O(elements).

**Constraints**: pure view (Article V) — prop states come from served fields
(`servings`, element `id`, `pursuit`, `activity`), agitation derives from
served pursuit only; named palette + named tunables (Article VI, FR-012);
reduced-motion stills every prop animation while keeping state readable
(FR-013); greeble secrecy byte-identical in behavior (FR-007); the
imaginary plaything stays the star (FR-011); zero engine/server diff
(FR-014).

**Scale/Scope**: 1 new file (`client/props.js`), 3 extended
(`client/gallery.html`, `client/render.js`, `client/index.html` script
tag), ~6 `VIEW` tunable additions in `client/anim.js`; 3 user stories with
a human gate after the first.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Articles I–III** — PASS. No simulation contact; kitty welfare, lifecycle
  and company are untouched.
- **Article IV** — PASS. Nothing proposes; the viewer stays read-only.
- **Article V** — PASS. Every prop is a presentational function of served
  fields plus the local animation clock 005 already established: the bowl
  shows served `servings`; the butterfly's colorway is a pure function of
  its served id, its agitation a pure function of served `pursuit` targets;
  overlays key off served `activity`. Nothing is predicted, invented, or
  sent back. The one design rule carried from 005: motion phases come from
  the view layer so reduced-motion/discontinuity handling stays centralized.
- **Article VI** — PASS. Prop colors live in one curated named palette
  (`PROPS` block, mirroring `PALETTES`); every animation number (flap
  period, panic multiplier, bob amplitude, pulse period, Z drift) is a
  named `VIEW` entry; the fine/coarse detail threshold reuses the cats'
  named rule. Spec-first: this plan follows the 007 spec; the props
  approval (greeble face included) is recorded in
  [gallery-approval.md](./gallery-approval.md) at the US1 gate (FR-003).

*Post-design re-check (after Phase 1)*: PASS — the design below adds no
wire surface, no simulation contact, no unnamed values. Complexity Tracking
stays empty.

## Project Structure

### Documentation (this feature)

```text
specs/007-vector-props/
├── plan.md              # This file
├── research.md          # Phase 0 output (R1–R8)
├── data-model.md        # Phase 1 output (props, palette, state mapping)
├── quickstart.md        # Phase 1 output (visual validation guide)
├── gallery-approval.md  # US1 gate record — created by the approval task
├── contracts/
│   └── props-contract.md   # served-data ↔ prop mapping; unchanged rules
└── tasks.md             # Phase 2 (/speckit-tasks — not created here)
```

### Source Code (repository root)

```text
client/
├── props.js        # NEW — the prop vocabulary: PROPS palette (named,
│                   # world-adjacent hues), BUTTERFLY_COLORWAYS,
│                   # butterflyColorwayFor(id), and the draw family:
│                   # drawBowl (servings-scaled mound), drawButterfly
│                   # (colorway, flap phase, agitated, hover+shadow),
│                   # drawGreebleWisp (both face variants for the gallery),
│                   # drawSleepZs, drawHeart, drawNeedIcon(need). Same
│                   # unit-box + outline conventions as cat.js; no DOM
│                   # beyond ctx, no fetches.
├── gallery.html    # EXTENDED — props section: every prop × state at 22px
│                   # and 88px (bowl 5/3/1/0, three colorways × two flap
│                   # poses, BOTH greeble faces side by side for the gate
│                   # decision, Zs, heart, six thought icons).
├── render.js       # SWAPPED — emoji call sites replaced by prop draws:
│                   # chow (mound replaces the meter), bug → butterfly
│                   # (with agitated-ids set derived per frame from served
│                   # pursuits), greeble → wisp (same toggle, same alpha),
│                   # 💤 → drawSleepZs, 💗 → drawHeart, NEED_ICONS →
│                   # drawNeedIcon; the emoji() helper is deleted (FR-010).
├── anim.js         # EXTENDED — VIEW gains the prop tunables (flap/bob/
│                   # pulse/drift periods, panic multiplier); viewAt gains
│                   # propPhaseFor(el) (wall-clock phase seeded by element
│                   # id, 0 when still) beside the existing motion methods.
└── index.html      # script tag for props.js (after cat.js, before
                    # render.js)

crates/            # UNTOUCHED — an explicit quickstart/tasks check
cloudkitty.toml    # UNTOUCHED
```

**Structure Decision**: a sibling `props.js` rather than growing `cat.js` —
cats and props are judged and revised separately (two gates, one file
each), while the shared global-scope conventions keep them one visual
vocabulary. All Article V-sensitive timing stays in `anim.js` where 005 put
it.

## The US1 gate (sequencing constraint for /speckit-tasks)

US1 (props gallery) is built first and ends in a **human approval
checkpoint**: Elizabeth judges the props against the cats — same hand, cute
at 22px — and decides the greeble's face (blank vs. tiny grin; the gallery
shows both). The outcome is recorded in `gallery-approval.md` (FR-003).
US2–US3 must not start until that record says approved. Revision loops
touch only `props.js` and the gallery.

## Complexity Tracking

No constitution violations to justify — table intentionally empty.
