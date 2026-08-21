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

1. **Follow pin** — `followId` set: subject = her chain; skip step 6
   only — admissions (step 5) still apply, so her companions join the
   shot; far rivals never steal a follow (spec FR-014). A FRESH pin acts
   now: it replaces any in-flight episode, a committed pan included
   (owner ruling 2026-08-21), and drops company that no longer fits; an
   ONGOING follow sheds companions per step 3's dwell.
2. **Membership follow** — shot = union of chains holding shot members.
3. **Shed** — if that union no longer fits, sustained `shedDwellTicks`
   consecutive ticks: keep the maximal-count fitting subset (incumbency
   tiebreak), one `shed` episode. Whole-shot overflow (nothing droppable)
   banks NO dwell, and a shed that cannot RESTORE fit never fires — the
   licence to shed is restoring fit; otherwise the overflow centre-hold
   governs (2026-08-21, both clauses). One `shedGate` owns the clock for
   group and follow mode alike.
4. **Break** — if the shot (group mode) holds <2: re-pick maximal-count
   window (ties prefer overlap with the dying shot, then lowest id —
   "ties keep the incumbent" applies here too; amended 2026-08-21, the
   first cut said lowest-id while the code preferred the incumbent);
   closest-pair fallback when no window ≥2.
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
  (FR-013) — with ONE exception: a viewer follow change redirects
  immediately (owner ruling 2026-08-21). Other episodes RE-LATCH through a
  hysteresis: a fresh goal ≥ `relatchTiles` from the latched one starts a
  NEW episode from the current frame (position-continuous by
  construction); sub-threshold drift lets the episode complete and step
  again from rest (re-amended 2026-08-21, high review — a mutated
  in-flight goal was a single-frame cut past the aim-lead pin).
- **Decisions read the DRAWN world**: still frames make no decisions and
  run no hold — a still view publishes served positions. Exemptions where
  served IS drawn: reduced motion, and the never-decided first paint
  (SC-009).
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
  (STRICT-majority continuation, research D5 — amended 2026-08-21: an
  exact half is not a continuation, so an even split restarts BOTH
  clocks; > half survives).
- Persistence thresholds are read from `nearDwellTicks`/`farDwellTicks`
  ONLY at the two comparison sites (the 032 seam).
- A chain is consumed by its first (best) match: a dwelling rival that
  splits hands its evidence clock to ONE heir (2026-08-21).
- An empty roster with the camera on eases home to the whole-world view in
  one episode; returning kitties re-enter through the cold-start pick
  (2026-08-21).

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
