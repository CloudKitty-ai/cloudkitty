# Quickstart: validating the shot picker

## Prerequisites

- Node (any recent); no build step, no dependencies.
- For live judging: the debug server binary and `cloudkitty.toml` (seats
  five including Clementine).

## 1. Harness (every grammar rule, headless)

```sh
node client/test-motion.mjs
node client/test-meadow.mjs   # must stay green — regression guard
```

Expected: all checks pass, including the eight contract fixtures
(contracts/shot-grammar.md §5). Any new assertion was mutation-verified
during implementation; re-verification recipe lives beside each check.

## 2. Reference model cross-check (dial calibration)

```sh
node client-measurements/camera-aim/shot-survival.mjs \
     client-measurements/camera-aim/sample.jsonl
```

Expected: event rates consistent with the SC bars (pan ≈0/min, widen
≤1.7/min, ≥2 framed 100%). Re-run after any dial change; if a proposed dial
value moves a rate past its SC bar here, it will fail live too — cheaper to
learn it in the model. (Requires PR #279 merged; the sample is local-only.)

## 3. Live validation (local five-kitty world)

```sh
target/debug/cloudkitty-server --config cloudkitty.toml \
  --client <worktree>/client \
  --snapshot <scratchpad>/snapshot.json --fresh
# then open http://127.0.0.1:8090, camera mode ON
```

Watch for, in order (spec SCs):

1. **Stillness** (SC-001): at rest the frame is pixel-still; every move is a
   discrete episode with a visible reason; nothing trails off.
2. **Min-two** (SC-002): never fewer than two kitties framed in group mode.
3. **Deliberateness** (SC-003): re-frames feel occasional; a pan reads as
   one committed move.
4. **Size** (SC-004): kitties visibly larger than the pinned-wide camera;
   frame well off the ceiling most of the time.
5. **Follow** (SC-006): click Clementine — her group frames; solitary
   follow shows her alone; release re-enters group grammar eased.
6. **Reduced motion** (SC-008): toggle OS setting — every move instant.
7. **Phone** (SC-010): overflow framing reads as deliberate; camera does
   not chase half-visible edge kitties.

Night check: a sleeping pile should produce minutes of perfect stillness.

## 4. Acceptance measurement (SC numbers)

Sample a served session with `client-measurements/camera-aim/camera-sample.mjs`
and replay through the harness's event counters (task-phase tooling) to
report: rest %, events/min, pans/min, at-ceiling %, ≥2-framed %, mean framed
— against the SC-001…SC-005 bars.
