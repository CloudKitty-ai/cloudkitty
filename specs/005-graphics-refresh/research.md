# Research: Graphics Refresh — Vector Cats & Animation

**Date**: 2026-07-19 | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

Ten decisions (R1–R10) resolving every open question in the plan's Technical
Context. Grounded in the shipped client (`client/render.js`, `client/app.js`,
`client/index.html` — a dependency-free canvas viewer, emoji glyphs, redraw
per WebSocket frame) and the shipped server surface (`GET /config` serves the
whole `Config`, `GET /world` + `/ws` serve `WorldSnapshot`s).

## R1 — Cat body plan: chibi side-profile, parametric, outline-first

**Decision**: One `drawCat(ctx, {pose, appearance, facing, size, phase})`
drawing a *chibi-proportioned side-profile* cat from parametric primitives:
rounded body blob (bezier), oversized head (~equal to body), triangle ears
with inner-ear fill, bezier tail, dot-and-line face (eyes, tiny muzzle,
whiskers), soft dark outline around every filled shape. Facing = horizontal
mirror (left/right only; north/south reuse the nearest horizontal facing).
`phase` (0..1, wall-clock derived) drives within-pose motion (breathing,
tail sway) and is ignored by static poses.

**Rationale**: At 22px a cat is ~16 usable pixels: only big shapes read.
Chibi ratios and heavy outlines are how tiny game sprites stay legible; the
current emoji succeed for exactly that reason. Side profile gives walking,
pouncing, eating and the sleeping curl a natural silhouette — the poses that
matter — where a front-facing cat would need perspective tricks. Horizontal
mirroring halves the pose work and matches an 8-direction world well enough
(diagonals resolve to their horizontal component; pure N/S keeps prior
facing).

**Alternatives considered**: front-facing mascot style (cuter face, but
walking/pouncing read poorly and facing means redrawing, not mirroring);
4-way facing (double the geometry for marginal gain at 22px — deferred, the
`facing` parameter can grow values later); SVG elements instead of canvas
paths (fights the existing canvas renderer and the interpolation loop;
canvas keeps one drawing pipeline).

## R2 — Identity: a curated palette table indexed by kitty id

**Decision**: `PALETTES` — a hand-curated table of ≥ 6 cat colorways (e.g.
orange tabby, calico, tuxedo, grey shorthair, seal-point, black), each
`{furBase, furShade, pattern: {kind, color}, eyeColor, noseColor}` with
`pattern.kind ∈ {solid, tabby-stripes, patches, tuxedo-mask, point-mask}`.
A kitty's appearance is `PALETTES[kitty.id % PALETTES.length]` — pure,
stable, and identical across frames, reloads and restarts (FR-003, SC-003).
The first three entries are tuned to be maximally distinct (the default
kitties). The lookup lives behind `appearanceFor(kittyId)` so served
appearance data (the P2 "Age / fur / eye stats" backlog item) can override
it later without callers changing.

**Rationale**: Hash-derived colors (HSL from id) cannot guarantee the
aesthetic floor or pairwise distinctness — a curated table guarantees both
by construction and is exactly what the gallery iterates on. Id is the only
stable identity on the wire today (spec assumption), and `id % len` matches
how the emoji renderer already picks faces (`KITTY_FACES[kitty.id % ...]`).

**Alternatives considered**: hashing id → HSL (free variety, uncontrollable
cuteness, near-collisions possible — rejected on the clip-art risk this
feature exists to manage); name-based hashing (names are user-editable
config; ids are the engine's identity).

## R3 — The interpolation clock: two-state pair + wall-clock progress

**Decision**: `anim.js` keeps `{prev, curr, currArrivedAt, generation}`.
Each WS frame shifts `curr → prev` and stamps `currArrivedAt =
performance.now()`. A `requestAnimationFrame` loop renders
`progress = min(1, (now − currArrivedAt) / tickMs)` — an ease applied to
kitty positions (`lerp(prev.pos, curr.pos, ease(progress))`) and bar values.
Progress **clamps at 1** and waits: the viewer never extrapolates past the
newest served state (FR-005, Article V). `tickMs` comes from the already-
served `config.world.tick_ms` with named stand-in `VIEW.tickMsFallback =
800` (the shipped default), fetched exactly like `distress_patience_ticks`
is today.

**Rationale**: Two states and a clamp is the smallest structure that
satisfies "ease between the two most recent served states, never predict."
The server already serves the tick interval — **no server change is needed
at all** (the spec's assumption anticipated adding one; research says it
already exists at `config.world.tick_ms`), which makes FR-018/SC-008
trivially true: every server is a "pre-005 server."

**Alternatives considered**: adding `viewer.tick_ms` to the served
`[viewer]` section (redundant copy of `world.tick_ms`; a second source of
truth to drift — rejected); measuring inter-frame arrival times instead of
reading config (jittery under network noise; config is authoritative);
keeping N>2 states for smoothing (buffering = latency = showing older state;
FR-019 says newest wins).

## R4 — Discontinuity rule: snap, never slide

**Decision**: A frame pair is **discontinuous** — rendered by snapping to
`curr` with no easing and a cleared beat store — when any of: it is the
first paint; the WS reconnected or the page returned from hidden
(`generation` bumps on both); `curr.tick !== prev.tick + 1`; the kitty
roster (id set) changed; or an individual kitty moved more than 1 tile in
either axis (kitties step at most one tile per tick, so anything larger is
not motion). Elements never ease position (they don't move smoothly in the
sim except critters stepping 1–2 tiles; critters get the same ≤1-tile rule,
greebles ≤2). Spawned/expired elements fade in/out briefly but never glide
(edge case list).

**Rationale**: Every discontinuity in the spec's edge-case list reduces to
"this pair is not two consecutive states of one continuous world," which is
detectable from the pair alone plus a generation counter — no timers, no
heuristics.

**Alternatives considered**: easing across gaps with a speed cap (cats
sliding across the map after a reconnect is exactly the artifact the spec
forbids); tracking per-kitty continuity instead of per-pair (needed anyway
for the >1-tile rule; both are used).

## R5 — Poses and beats: derive on frame arrival, play on the local clock

**Decision**: Pose selection is a pure function of the served kitty
(`activity.state`, `last_action`, position delta): walking (moved),
pouncing (play/chase applied), eating, drinking, grooming, resting loaf,
sleeping curl, sitting/idle. **Beats** — short one-shots — are derived once
per frame *arrival* by diffing `prev → curr` (never per rAF): new entry in
`abandoned_chases` → sad beat; need dropped ≥ `VIEW.reliefSparkleDrop`
(named tunable, default 15) → relief sparkle; `last_action` is targetless
play → imaginary plaything during the pounce; `pursuit` present → focused
eyes (a sustained overlay, not a one-shot); longest `distress_since` age ≥
served patience → thought bubble (sustained, at most one). Each one-shot is
`{kind, t0: now, duration}` in a per-kitty beat store, cleared on
discontinuity.

**Layering rule (edge case "two beats at once")**, documented in the
contract: base pose ← action animation ← eye/expression overlay ← at most
one one-shot particle (newest wins) ← bubbles (speech, then thought,
vertically stacked). Nothing flickers because each layer slot holds one
occupant.

**Rationale**: Diff-on-arrival keeps beat derivation deterministic per
served pair (Article V's "identical served states → identical logical
renderings") and cheap (once per tick, not per frame). The sustained
overlays (pursuit face, thought bubble) are direct functions of `curr`
alone, so they need no store at all.

**Alternatives considered**: deriving beats inside the rAF loop (re-derives
and can double-fire; rejected); consuming the new `/events/activity`
endpoint for finished-scene beats (attractive later — "ate for 4 ticks" —
but no US needs it, FR-018 wants no new served data required, and 006's
duration minimums already make actions watchable; recorded as an explicit
non-dependency for a future dramatization pass).

## R6 — Reduced motion and hidden tabs

**Decision**: `matchMedia('(prefers-reduced-motion: reduce)')`, re-checked
live via its `change` event. When reduced: the rAF loop never runs; each WS
frame draws once, statically (positions snapped, static poses, no idle/
ambient motion, no one-shot particles; sustained *informational* cues —
thought bubble, pursuit face — still render, and speech bubbles appear
without pop-in), and the panel's CSS bar transitions are disabled via a
`reduced-motion` class. This is motion-equivalent to the pre-refresh viewer
(FR-015/SC-007) while keeping all state information visible. Hidden tab:
`visibilitychange` cancels the rAF loop entirely; on return, bump
`generation` (forcing a snap) and resume (FR-016). The WS stays open either
way — frames still update `latestWorld` cheaply so return is instant.

**Rationale**: The spec pins reduced motion to "behaviorally equivalent to
the pre-refresh viewer," which is precisely draw-once-per-frame — the code
path already exists and stays exercised. Keeping the socket alive while
hidden costs one JSON parse per tick and buys instant, snap-correct return.

**Alternatives considered**: closing the WS while hidden (reconnect churn
and a stale first paint on return; parsing one frame per 800ms is cheaper);
honoring reduced motion only for ambient effects (fails SC-007's
motion-equivalence).

## R7 — Rendering pipeline: cached ground, one draw path

**Decision**: `render.js` draws an **InterpolatedFrame** (the blend anim.js
computes) through one path used by both animated and reduced/static modes
(static mode is simply progress = 1, phase = 0, beats off). The checkerboard
ground + grid is rendered once per resize into an offscreen canvas and
blitted per frame; ambient effects (water shimmer, sunbeam pulse + motes,
grass sway, cloud shadows — each behind its own named toggle in `VIEW`,
FR-013) draw above the blit. Element juice: chow kibble level scales with
`servings` (the pip row today becomes a visible fill level), speech bubbles
get a pop-in ease, over-cat happiness bars ease toward served values —
capped by the same progress clock, never CSS timers, so FR-019's
"newest state wins" holds everywhere.

**Rationale**: 1024 `fillRect`s per rAF is the only real per-frame fat in
the current draw; caching it makes SC-006 comfortable without touching
anything else. One draw path for both modes means reduced motion cannot
drift from the animated view's correctness.

**Alternatives considered**: layered DOM/CSS animation for effects (splits
the scene across two systems and fights canvas z-order); WebGL (absurd for
32×32 tiles); dirty-rect partial redraws (complexity without need at this
canvas size).

## R8 — The gallery: standalone, same drawing code, approval artifact

**Decision**: `client/gallery.html` renders every `PALETTES` entry × every
pose in `POSES`, each at world tile size (22px) *and* inspection size
(88px), plus a "the three defaults, side by side, unlabeled" row for the
distinguishability check (US1 acceptance 2). It loads `cat.js` via a plain
`<script>` — the very object the live renderer uses (FR-001 "never a
copy") — and needs no server: it opens from disk and is also served at
`/gallery.html` by the existing static fallback with zero server changes.
The gate outcome is recorded in `specs/005-graphics-refresh/
gallery-approval.md`: approved / revised-N-times / fallback chosen (FR-002).

**Rationale**: The gallery is the cheap-to-reject risk retirement the spec
demands; standalone means judging costs a double-click, and sharing `cat.js`
means what is approved is literally what ships.

**Alternatives considered**: a `?gallery` mode inside `index.html` (couples
the gate to the live app and to a running server); screenshots in the repo
(dead artifacts; the gallery is live and re-runnable at every revision).

## R9 — Tunables: one named `VIEW` object; server-owned values from /config

**Decision**: All new client tunables live in one frozen `VIEW` object in
`anim.js` (durations, easing curves, idle-motion frequency, beat durations,
particle sizes, ambient amplitudes + per-effect enable flags,
`reliefSparkleDrop`, `tickMsFallback`, `distressPatienceFallback = 60`).
Nothing inline (FR-017, Article VI). Server-owned values and their client
stand-ins: `config.world.tick_ms` → easing duration;
`config.viewer.distress_patience_ticks` → thought-bubble threshold (same
fetch that exists today). No new server config keys — the `[viewer]`
section is unchanged.

**Rationale**: The existing pattern (`distressPatienceTicks` stand-in in
`app.js`) generalizes; one object is greppable and the gallery can expose
sliders over it later without hunting constants.

**Alternatives considered**: adding `[viewer]` keys for animation timing
(server ownership belongs to values the *simulation* owns — tick interval,
patience; pounce squash amplitude is presentation and would bloat the config
surface for nothing).

## R10 — Verification strategy without a JS toolchain

**Decision**: Three tiers. (1) **The gallery gate** — the human acceptance
test for the look, re-runnable per revision. (2) **Quickstart visual
checks** — a scripted per-story checklist against a live world (and
DevTools emulation for reduced motion), covering SC-002…SC-008; frozen
states for SC-005's beat conditions come from watching the live world with
the panel as ground truth, plus the `g` toggle where relevant. (3)
**Structure for future tests** — palette distinctness, pose completeness,
discontinuity and beat derivation are pure, DOM-free functions exported
from `cat.js`/`anim.js`, so a later JS test harness can assert them without
refactoring; adding that harness now (npm/node in CI) is explicitly out of
scope for a dependency-free static client. The Rust CI gate is untouched
and keeps guarding Articles I–III.

**Rationale**: The feature's acceptance criteria are visual by nature; the
constitution's test mandate covers the simulation (unchanged). The honest
risk is regression in pure derivation logic, which is why that logic is
quarantined into pure functions — testable the day a harness is justified.

**Alternatives considered**: adding node + a test runner to CI now (new
toolchain for ~5 pure functions on a no-build client — deferred until the
client grows real logic mass); pixel-snapshot testing (flaky across
platforms/fonts; the gallery gives humans the same signal reliably).
