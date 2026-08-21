# Implementation Plan: Camera shot picker

**Branch**: `038-camera-shot-picker` | **Date**: 2026-08-21 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/038-camera-shot-picker/spec.md`

## Summary

The camera stops being a tracker and becomes a shot picker: it decides a shot
(the most kitties whose groups share the frame), holds it in literal stillness,
and moves only in discrete, eased episodes — a gentle correction when a member
presses the frame, a widen to admit a neighbouring group, a rare fast pan when
a strictly bigger far group persists 15 ticks.

**The whole change lives inside the `Camera` class.** Its external contract —
`update(world, view, { aspect, cssWidth })` in, `left/top/across` out — is
untouched, so `render.js` needs no changes: the letterbox, the ground bake and
the draw offset all read the same three numbers they read today. What changes
is how the class computes them: `targetFor`'s fit-everyone + anchor logic gives
way to shot selection, and `update`'s continuous exponential easing gives way
to latched, duration-based episodes that end in an exact snap. `limitsFor` —
the 037 bounds derivation — is not touched at all.

Two structural splits carry the design:

- **Decide on ticks, move on frames.** Grammar decisions (groups, rivals,
  dwell evidence, membership) run once per world tick; motion runs per frame
  against drawn positions. Dwells are tick counts by definition, and the split
  is what makes the grammar testable without driving an animation loop.
- **Motion is episodes, not pursuit.** A move latches its goal at start, eases
  over a fixed duration, snaps exactly on arrival, and returns to rest. The
  easing tail — the measured cause of "too active" — is structurally
  impossible, not merely damped.

## Technical Context

**Language/Version**: Browser JavaScript, ES2020+, plain scripts, no build
step. Fixed load order `cat.js → cat-v2.js → props.js → meadow.js →
render.js → anim.js → app.js`.

**Primary Dependencies**: None. The camera is a plain class in `anim.js`;
grouping is O(n²) on a roster of 3–5.

**Storage**: None added. 036's two persisted keys (camera mode, follow id) are
untouched.

**Testing**: `node client/test-motion.mjs` (239 checks) — extend it; no new
harness. The three verified fixtures from
`client-measurements/camera-aim/shot-survival.mjs` (near-widen, far-pan,
break) port into it as drives of the REAL `Camera`, joined by overflow
centre-hold, solo-follow, mid-pan commit, and snap-to-rest cases. Every new
assertion is mutation-verified (house rule 5).

**Target Platform**: Evergreen desktop and mobile browsers; phone is the
primary consumption path. The binding viewport constraint is unchanged from
037.

**Project Type**: Static client for a server-authoritative simulation.
View-only.

**Performance Goals**: No regression against 036 SC-003 (frame rate within 10%
of camera-off). The tick-time decision work is a handful of distance
comparisons on ≤5 kitties; frame-time work SHRINKS (a resting camera skips
easing arithmetic).

**Constraints**: Client-only; deployable `--client-only` inside the phase-1
wall window. `limitsFor` and every 037 dial stay exactly as shipped
(spec 038 Out of Scope).

**Scale/Scope**: One file changes (`client/anim.js`: the `Camera` class and
`VIEW.camera` dials), one harness extends (`client/test-motion.mjs`), one lab
page gains a card if dial-judging needs it (`gallery-v2.html` — optional,
owner-driven). `render.js` is expected to carry zero diff; if the pan profile
turns out to need a still-frame hint, that is the one permitted touch and it
must be flagged in the PR.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Article | Bearing | Verdict |
|---|---|---|
| I — Kitties cannot suffer | No needs or welfare logic touched. | Not engaged |
| II — Kitties cannot die | No lifecycle touched. | Not engaged |
| III — Kitties cannot be alone | Roster untouched. (The grammar's minimum-two is a VIEW rule about framing, not a world rule.) | Not engaged |
| IV — Engine is law | No behaviors. | Not engaged |
| **V — Client is a pure view** | The shot picker reads the drawn view and world snapshot, writes nothing back, sends nothing. Two viewers at different shots see the same world (036 FR-021 carried forward as 038 FR-001). | **PASS** |
| VI — Spec-first, test-guarded | Spec written and clarified (3 owner Q&A) before this plan. All new constants live in `VIEW.camera` with documented defaults, never magic numbers. Every grammar rule lands with a mutation-verified check in the existing harness. | **PASS** |

**Post-Phase-1 re-check**: unchanged — the data model adds view-side entities
only (Group, Shot, Episode), none persisted, none serialized, none sent.

No violations. Complexity Tracking omitted.

## Project Structure

### Documentation (this feature)

```text
specs/038-camera-shot-picker/
├── spec.md              # Clarified spec (3 sessions recorded)
├── plan.md              # This file
├── research.md          # Phase 0: 13 decisions with rationale
├── data-model.md        # Phase 1: Group / Shot / Episode / Evidence
├── quickstart.md        # Phase 1: harness + local-world validation guide
├── contracts/
│   └── shot-grammar.md  # Phase 1: the grammar as a testable contract
└── tasks.md             # Phase 2 (/speckit-tasks — not created here)
```

### Source Code (repository root)

```text
client/
├── anim.js              # THE change: Camera class internals + VIEW.camera dials
├── test-motion.mjs      # Harness: grammar fixtures + motion episode checks
├── render.js            # Expected ZERO diff (reads left/top/across as today)
└── gallery-v2.html      # Optional: a dial card if live judging wants one

client-measurements/
└── camera-aim/          # Reference model (shot-survival.mjs) — lands via
                         # PR #279 (open); reused for dial calibration, never
                         # shipped to the page. Merge #279 before this branch.
```

**Structure Decision**: single-file feature inside the established client
layout. The camera stays one class in `anim.js` beside its dials, per the
037 precedent; the reference simulation stays in `client-measurements/` and
never ships to the page.
