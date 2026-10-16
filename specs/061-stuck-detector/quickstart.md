# Quickstart: validating the Stuck Detector

Runnable scenarios proving the feature end to end. Shapes reference
[contracts/stuck-detector.md](contracts/stuck-detector.md) and
[data-model.md](data-model.md); rule-5 red cycles run through
`scripts/mutate.sh --expect <prediction>` as always.

## Prerequisites

- Workspace builds: `cargo test -p cloudkitty-server -p cloudkitty-core`
  green at the branch base.
- For scenario 5 only: the native checkout's raws (the verification
  replay reads recorded traces; everything else is self-contained).

## 1. The F-044 loop breaks (US1, SC-001)

Unit/integration: drive a world with a doctored mind-class advisor that
dithers between two adjacent tiles while `eat` sits above the armed
line — STATE-DEPENDENT: it dithers only while standing on its two home
tiles and walks toward the bowl from anywhere else, so one scripted
step genuinely frees it (an unconditional ditherer would re-loop on
the next tick and make "the loop breaks" unfalsifiable). With
`mode = "enforce"`, `window = 30`:

- assert the fire lands on the EXACT tick the observe convention
  predicts (an equality derived from the sim-task observe points, not
  a ≥ bound — a late fire must fail);
- assert the applied action on the fire tick is the scripted brain's,
  not the dither, and the seat leaves the home tiles within one window
  plus one tick of signature completion (SC-001's bound, both sides);
- assert no fire on consecutive ticks (FR-007: the post-fire reset);
- boxed-in arm: the same fixture walled in → the substitute resolves
  through the ordinary proposal path to a safe outcome and the fire is
  still recorded; refused-substitute arm: a substitute invalid at
  apply time resolves as any refused proposal, no retry in-tick (the
  spec's edge cases, on record as tests);
- shared-instance arm: two seats naming the same wrapped behavior,
  both stuck → each fires on its own window with its own record.

Negative arms in the same test file: needs below the line (US1/AC2) and
a relieving scene in progress (US1/AC3) never fire.

## 2. Full attribution (US2, SC-003)

Force one fire (scenario 1 harness); read the tracing event and the
`/stuck` `recent` entry; assert every contract field present and
correct, including `proposal_replaced` equal to the doctored advisor's
known output. Integration: `GET /stuck` through
`start_server_with` (`server_integration.rs:130` pattern) shows the
per-seat count without log reading (US2/AC2).

## 3. Non-interference: off and observe change nothing (US3, SC-002 arm)

The watchdog byte-identity template (`watchdog.rs:465`), budgetless
(the served-path budget residuals are documented, not tested here):

- **off**: run paired worlds — detector constructed-and-off (mind seats
  wrapped, forwarding) vs absent — 2000 ticks, assert serde_json
  byte-identity of final worlds. The wrapping makes this a real test of
  the forwarding path, not a vacuous absence-vs-absence pairing.
- **observe**: same pairing with `mode = "observe"` on a world that
  fires (scenario 1 shape): assert world byte-identity (applied
  decisions unchanged, master RNG untouched) while the fire record
  exists — the FR-008 extension made testable.

## 4. Determinism replay (US3/AC2, SC-004)

The `determinism.rs` fingerprint pattern, budgetless: two runs, same
seed/config, `mode = "enforce"`, a deterministic firing seat; assert
identical world fingerprints AND identical fire-record sequences end to
end (tick, seat, replaced, substitute).

## 5. The measured-rule anchor (SC-002 screen)

Already on record: `python3 specs/061-stuck-detector/stuck_rule_replay.py`
from the native checkout root reproduces the verification table under
the implementation relief rule (`--relief governing`, the default;
`--relief value-fell` reproduces the original clarify-gate rule — the
two tables are identical, `verification-2026-10-13.md` re-run section):
zero false positives over 425k healthy cat-ticks at the shipped
defaults. The implementation-time SC-002 declared read is the paired
observe/off soak at battery time, through the server harness — the
python lab paths never see the detector (doctrine rule 10: a declared
number, never a pass bar); this replay is the screen that sized the
defaults.

## 6. Boundary and config guards (FR-003, FR-010, SC-005)

- A scripted-class seat in a firing-shaped loop: assert no tracking
  entry, no fire, absence from every status collection (not-wrapped by
  construction, asserted anyway).
- Config: absent table = documented defaults; unknown key, `window = 1`,
  `armed_line = 0`, `radius = 0`, bad mode each fail at load with the
  key named.
- Foreign-table leak test extended: `engine_defaults_sha256` identical
  with and without the `[stuck_detector]` field present in core config.
- `/settings` pinned-key test covers the new rows.

## Expected outcome summary

| Scenario | Proves | Red-first bug to stage |
|---|---|---|
| 1 | loop breaks, stand-down | skip the substitution; fire every tick |
| 2 | full attribution | drop one record field |
| 3 | off/observe inert | mutate world state in observe path |
| 4 | reproducible fires | inject wall-clock into fire choice |
| 5 | rule matches measurement | `--strict-gate` masks the real episode |
| 6 | boundary + config | wrap a scripted seat; accept window = 1 |
