# Implementation Plan: Graphics Refresh — Vector Cats & Animation

**Branch**: `005-graphics-refresh` | **Date**: 2026-07-19 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/005-graphics-refresh/spec.md`

## Summary

Replace the viewer's emoji cats with procedural vector cats and bring the
world to life: per-kitty stable identity (fur, pattern, eyes, facing), smooth
easing between served states, action/idle animations, expressive beats driven
by data the server already sends, and ambient polish. All work lands in
`client/` — **zero engine or server changes** (research confirmed the tick
interval is already served via `/config` as `world.tick_ms`). The one real
risk — a procedural cat that reads as clip-art — is retired first by a
static portrait gallery (US1) with an explicit approval gate before anything
builds on the look. Technically: a shared drawing module (`cat.js`) consumed
by both a standalone gallery page and the live renderer; a presentational
animation layer (`anim.js`) that owns the requestAnimationFrame clock, the
two-newest-states pair, discontinuity snapping, and derived beats; and a
rework of `render.js` to draw interpolated frames instead of raw snapshots.
Reduced motion falls back to the pre-refresh per-tick behavior; hidden tabs
do no work.

## Technical Context

**Language/Version**: Vanilla JavaScript (ES2020+, browser-native; no
transpiler), HTML5 Canvas 2D. Matches the existing viewer exactly.

**Primary Dependencies**: none — the client is dependency-free static files
served by the existing `ServeDir` fallback, and stays that way. No npm, no
bundler, no framework.

**Storage**: n/a (presentational state lives in page memory; nothing
persists, nothing is sent to the server).

**Testing**: The Rust suite remains the CI gate and is untouched. Client
correctness splits into (a) the US1 gallery — the human acceptance gate for
the look, revisitable at any time, (b) a quickstart of scripted visual checks
per story against a live world, and (c) pure presentational functions
(palette derivation, discontinuity detection, beat derivation) kept
dependency-free and DOM-free so they are inspectable and later unit-testable;
introducing a JS test toolchain is explicitly out of scope (no new build
infrastructure for a static-file client).

**Target Platform**: modern desktop browsers (the development machine's
browser per SC-006's "typical laptop"); retina-aware canvas as today.

**Project Type**: web client (static files in `client/`, served by the
existing cloudkitty-server; the gallery page also opens directly from disk
with no server at all).

**Performance Goals**: SC-006 — sustained smooth animation (<1% dropped
frames over a minute) at default world size (32×32, 720px canvas); zero
animation work while the tab is hidden; static ground pre-rendered to an
offscreen layer so the per-frame cost is elements + cats + effects only.

**Constraints**: pure view (Article V) — every pixel is a function of the two
newest served states plus a local wall-clock; never predicts, never
extrapolates past the newest state, never sends anything; all tunables named
(Article VI); fully functional against a server serving no new fields
(FR-018 — trivially met: no new fields exist); `prefers-reduced-motion`
reproduces pre-refresh motion behavior exactly.

**Scale/Scope**: ~4 files touched (`index.html`, `app.js`, `render.js`, plus
panel CSS in `index.html`), ~3 files added (`cat.js`, `anim.js`,
`gallery.html`); 3 kitties / ~17 elements / 32×32 world; six user stories
with a hard human gate after the first.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Article I (Kitties Cannot Suffer)** — PASS. No simulation contact. The
  viewer's new beats *narrate* served welfare signals (relief, distress age)
  and add no mechanic. The long-distress thought bubble uses the same served
  `viewer.distress_patience_ticks` the panel cue already uses — caring, not
  alarming, one bubble at most.
- **Article II (Cannot Die)** — PASS. Untouched.
- **Article III (Cannot Be Alone)** — PASS. Untouched.
- **Article IV (Engine Is the Law)** — PASS. The viewer proposes nothing and
  remains read-only; no behavior surface is touched.
- **Article V (Server-Authoritative, Deterministic)** — PASS, and it is this
  feature's central design constraint. The interpolated frame is a blend
  *between two states the server already sent* at a progress given by the
  local clock and the served tick interval; beats are derived from served
  fields or from differences between consecutive served states; the newest
  served state always wins over an in-flight animation (FR-019). Nothing is
  predicted, computed forward, or sent back. Determinism of the simulation is
  untouched; identical served states produce identical logical renderings
  (poses, palettes, beats), with only sub-tick easing phase varying by wall
  clock — exactly the spec's stated boundary.
- **Article VI (Spec-First, Test-Guarded)** — PASS. This plan follows the
  spec; every new visual tunable is a named constant in one place
  (`VIEW` tunables object), server-owned values come from `/config` with
  named stand-ins (tick interval, distress patience — both already served);
  the property suite and CI gate are untouched. The US1 approval gate is
  itself a spec-mandated artifact (FR-002) and is recorded in
  [gallery-approval.md](./gallery-approval.md) when judged.

*Post-design re-check (after Phase 1)*: PASS — the design below adds no
server surface, no simulation contact, and no unnamed tunables. Complexity
Tracking stays empty.

## Project Structure

### Documentation (this feature)

```text
specs/005-graphics-refresh/
├── plan.md              # This file
├── research.md          # Phase 0 output (R1–R10)
├── data-model.md        # Phase 1 output (presentational entities)
├── quickstart.md        # Phase 1 output (visual validation guide)
├── gallery-approval.md  # US1 gate record — created by the approval task
├── contracts/
│   └── viewer-contract.md  # served-data ↔ visual mapping; pure-view rules
└── tasks.md             # Phase 2 (/speckit-tasks — not created here)
```

### Source Code (repository root)

```text
client/
├── index.html      # script tags for new modules; reduced-motion CSS note;
│                   # panel styles untouched (cards keep emoji for now)
├── cat.js          # NEW — the shared drawing vocabulary: PALETTES (curated,
│                   # per-kitty-id), POSES (named parameter sets), drawCat(ctx,
│                   # pose, appearance, facing, size, phase), plaything/bubble
│                   # glyph helpers. No DOM access beyond the ctx argument; no
│                   # fetches. The single source both gallery and live view use
│                   # (FR-001 "never a copy").
├── gallery.html    # NEW — US1 portrait gallery: every palette × every pose at
│                   # tile size (22px) and inspection size (88px). Standalone:
│                   # loads cat.js, needs no server, opens from disk.
├── anim.js         # NEW — the presentational layer: state-pair store
│                   # (prev/curr + arrival time), rAF loop, progress/easing,
│                   # discontinuity detection (snap rules), per-kitty beat
│                   # store (one-shots, facing memory), reduced-motion and
│                   # visibilitychange handling, VIEW tunables object.
├── render.js       # REWORKED — draws an interpolated frame: ground layer
│                   # cached offscreen; elements (with juice); vector cats via
│                   # cat.js at eased positions with pose/beat overlays;
│                   # bubbles (speech + thought). Greeble rule and `g` toggle
│                   # unchanged.
└── app.js          # EXTENDED — WS frames feed anim.js instead of drawing
│                   # directly; /config fetch also reads world.tick_ms; panel
│                   # rendering unchanged.

crates/            # UNTOUCHED — no engine or server changes in this feature
cloudkitty.toml    # UNTOUCHED
```

**Structure Decision**: keep the existing no-build static-file client and add
two modules plus the gallery page beside it. `cat.js` isolates everything the
US1 gate judges (geometry + palettes) so revision loops touch one file;
`anim.js` isolates everything Article V scrutiny cares about (what may move
when, and why) so the pure-view argument is auditable in one place.

## The US1 gate (sequencing constraint for /speckit-tasks)

US1 (gallery) is built first and ends in a **human approval checkpoint**:
Elizabeth judges the look against the "cuter than the emoji" bar. The
decision — approved, revise, or fall back (pixel sprites /
emoji-faces-on-vector-bodies) — is recorded in `gallery-approval.md`
(FR-002). US2–US6 must not start until that record says approved. Revision
loops before approval touch only `cat.js` and the gallery (acceptance
scenario 3 of US1).

## Complexity Tracking

No constitution violations to justify — table intentionally empty.
