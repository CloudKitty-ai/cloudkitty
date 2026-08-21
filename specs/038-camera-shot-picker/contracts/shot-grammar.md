# Contract: the shot grammar

The camera's externally observable behaviour, stated as invariants the
harness enforces. `client/test-motion.mjs` drives the real `Camera` through
synthetic worlds; every clause below lands with a mutation-verified check.

## 1. The frozen interface

- `camera.update(world, view, { aspect, cssWidth })` → sets
  `left`, `top`, `across`. Nothing in `render.js` changes meaning: draw
  offset is `left/top`, tile is `cssWidth/across`, letterbox reads
  `camera.on`, ground bake keys on `limitsFor`'s floor.
- `limitsFor` is byte-identical to 037's shipped derivation.
- Camera OFF is the whole-world view with no easing — same numbers,
  same path as today (036 FR-002 / SC-007 continuity).

## 2. Decision order (once per world tick, camera on)

1. **Follow pin** — `followId` set: subject = her chain; skip 5–6.
2. **Membership follow** — shot = union of chains holding shot members.
3. **Shed** — if that union no longer fits: keep the maximal-count fitting
   subset (incumbency tiebreak), one `shed` episode.
4. **Break** — if the shot (group mode) holds <2: re-pick maximal-count
   window (lowest-id tiebreak); closest-pair fallback when no window ≥2.
5. **Admission** — disjoint chain with `nearTicks ≥ nearDwellTicks` whose
   union with the shot fits: admit, one `widen` episode.
6. **Pan** — disjoint chain with `count > |shot|`, not admissible, and
   `farTicks ≥ farDwellTicks`: shot := that chain, one committed `pan`.
7. **Equal never dethrones**: no rule fires on `count == |shot|`.

## 3. Motion invariants

- **At REST the camera is bit-still**: `left`, `top`, `across` identical
  across consecutive frames, however long rest lasts. (SC-001's teeth.)
- **Every episode ends in an exact snap**: on arrival the camera's numbers
  EQUAL the latched goal — no residual easing, no epsilon drift after.
- **Pan commits**: once begun, decision steps 2–6 do not run until arrival
  (FR-013). All other episodes may re-latch on a fresh trigger.
- **Hold triggers**: fitting shot — any member's drawn position outside the
  inner `safeZoneFrac` rect starts a `correction`; overflow shot — bbox
  centre drifting > `aimDeadzoneTiles` from aim does (FR-007a). Members
  half-out of an overflow frame trigger NOTHING (the camera never chases).
- **Reduced motion**: every episode arrives instantly. **Still frames**:
  no episode progress, no decisions (same moment drawn again).

## 4. Grammar invariants

- ≥2 kitties in the shot whenever any pair could share the widest frame
  (group mode); a follow may frame one (clarified 2026-08-21).
- The shot is maximal-count-or-tied among windows that fit (SC-005's bar).
- Chains carry evidence; exact-membership churn does NOT reset dwell
  (majority-overlap continuation, research D5).
- Persistence thresholds are read from `nearDwellTicks`/`farDwellTicks`
  ONLY at the two comparison sites (the 032 seam).

## 5. Harness fixtures (ported from shot-survival.mjs, plus new)

| Case | Predicted observable |
|---|---|
| near-widen | widen fires on the 5th qualifying tick, not the 4th/6th |
| far-pan | pan fires on the 15th tick; camera moves on the fast profile; equal-size never fires |
| break | shot <2 → re-frame; jump classified only by geometry |
| overflow centre-hold | members exit frame, camera still; centre drifts past deadzone, one correction |
| solo-follow | followed loner framed alone at the floor; no widen toward others |
| mid-pan commit | destination dissolves mid-pan; goal unchanged until arrival |
| snap-to-rest | after any episode: N consecutive frames, identical camera numbers |
| chain churn | rival swaps one member mid-dwell; counter continues (D5) |

Each is introduced with its exact counter-bug (off-by-one dwell, missing
snap, per-frame re-latch, exact-set keying) and must go red before it counts
(house rule 5/6).
