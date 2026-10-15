# Implementation Plan: Stuck Detector at Decoding

**Branch**: `product/stuck-detector` | **Date**: 2026-10-14 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/061-stuck-detector/spec.md`
(four clarifications recorded across sessions 2026-10-13/14, checklist
16/16; confinement and relief rules replay-verified in
`verification-2026-10-13.md`, including the 2026-10-15 governing-need
re-run; cross-artifact analysis remediated 2026-10-15).

## Summary

A serving-side guard for mind-class seats: per seat, track the verified
stuck signature (confined to Manhattan radius 1 of a window anchor for N
consecutive ticks while one need accumulates N armed scene-free ticks,
scene ticks pausing the streak and a relieving scene clearing it). On a
completed signature, substitute that seat's next proposal with the
scripted brain's decision for one tick. Three-state enablement
(`"off"` / `"observe"` / `"enforce"`), shipped off.

Technical approach (details in [research.md](research.md)): the server
has no per-seat decode step to intercept — `World::tick` runs decisions
and application back to back — so the detector is split in two, both
halves in a new `crates/cloudkitty-server/src/stuck.rs`:

1. **Observer** (the watchdog's pattern): after each tick, read `&World`
   (the post-tick world is the start-of-tick snapshot of the next tick),
   advance per-seat signature state, and compute the set of seats that
   fire on the next tick. Timing-independent by construction: no state
   lives in the decision path.
2. **Guard wrapper** (the `SeatClassed` pattern): a `Behavior` wrapper
   around every mind-class seat's registered behavior — wrapped in ALL
   modes, off included (the wrapper forwards when it has nothing to do,
   so the off-mode inertness tests exercise the real code path, not a
   vacuous absence). On a tick its seat is in the fire set, it calls
   the inner advisor (capturing the proposal that is replaced, per
   FR-011), then — in enforce — returns `Teacher::NEEDS_DRIVEN`'s
   decision for the same context instead; in observe it returns the
   inner decision untouched. Either way it records the fire with full
   attribution. If the inner advisor's `try_decide` yields no proposal
   on a fire tick, the record says so ("none") and observe returns
   `None` so the engine's own fallback runs as ever.

The engine is untouched except one config passthrough: a
`#[serde(default, skip_serializing)]` foreign-table field for
`[stuck_detector]` beside the existing `watchdog` one
(`deny_unknown_fields` rejects unknown tables otherwise);
`skip_serializing` keeps `engine_defaults_sha256` unchanged.

## Technical Context

**Language/Version**: Rust, workspace-pinned toolchain (no new root
`.toml` — the toolchain-pin trap of adding one is avoided; the only
config edits are to existing files).

**Primary Dependencies**: existing workspace crates only —
`cloudkitty-core` (Behavior trait, `Teacher::NEEDS_DRIVEN`, Kitty/World
state), `cloudkitty-server` (watchdog pattern, registry, API),
`cloudkitty-rl` (policy seats are the wrapped minds). serde/toml/tracing
already in tree. **No new dependencies.**

**Storage**: in-memory detector state; fires as structured tracing lines
plus a bounded in-memory ring readable over the status API; config in
the server's one TOML file (`[stuck_detector]` table).

**Testing**: `cargo test` (unit in `stuck.rs`, integration in
`crates/cloudkitty-server/tests/`), red-first via
`scripts/mutate.sh --expect`; determinism via the
`cloudkitty-core/tests/determinism.rs` fingerprint pattern;
non-interference via the watchdog's watched-vs-unwatched 2000-tick
byte-identity template (`watchdog.rs:465`).

**Target Platform**: the served server (`cloudkitty-server`), plus
budgetless runs built on its wrapped registry. The detector is
invisible to the python lab/corpus paths (`cloudkitty-py`,
`kitty-eval`, `bc-collect` depend only on core + rl), so the SC-001
F-044 reproduction and the SC-002 paired soak run through the server
test harness (`start_server_with` / a wrapped registry constructed in
`cloudkitty-server` tests, budgetless), and the corpus INVESTIGATE
consumer reads the SERVED world's fire records (the serving logs and
`/stuck`), which is where Gen 2 corpus-time stuck reads live.

**Project Type**: feature inside an existing multi-crate Rust workspace;
one new server module plus wiring.

**Performance Goals**: per-tick bookkeeping is O(seats × needs) over 5
seats and 6 needs — unmeasurable against a tick; no allocation on the
no-fire path beyond map upkeep.

**Constraints**: engine rules, tick constitution, and
`engine_defaults_sha256` unchanged (FR-006, Assumptions); no new
randomness and master-RNG isolation by type (FR-008); scripted seats
never wrapped (FR-003); certified Gen 1 served default = off (FR-009).
Two accepted served-path residuals, both invisible on budgetless runs:
a bench (wall-clock event) can delay a fire's delivery by one tick
(the bench fallback applies the scripted brain anyway), and observe
mode spends record-computation time inside the seat's decision budget
(off-vs-observe byte-identity is exact budgetless; FR-010 states the
scoping).

**Scale/Scope**: 5 seats, 6 needs, windows in the tens of ticks; ring
buffer bounded (default 256 fires); fire rate on healthy behavior
measured at zero-to-rare (425k cat-ticks replayed, one real episode).

## Constitution Check

*GATE: evaluated before Phase 0; re-evaluated after Phase 1 design —
both pass, no violations to justify.*

- **Article I (no suffering)**: PASS. The detector adds no negative
  state; it guards access to relief (a stuck cat is one its own policy
  cut off from a visible resource). Fires are interventions on
  proposals, never a punishment mechanic. The armed-line default (75)
  is the safeguard threshold, where Article I already guarantees a
  reachable resource exists — so a confined, armed cat is by
  construction refusing reachable relief.
- **Article II (no death)**: PASS. No removal path is touched.
- **Article III (never alone)**: PASS. Untouched.
- **Article IV (engine is the law)**: PASS — and load-bearing. The
  guard lives entirely on the advisor side: the wrapper is itself an
  untrusted advisor from the engine's view, and its substitute (the
  default built-in needs-based behavior's decision — Article IV's own
  named fallback) is validated like any proposal. A refused substitute
  resolves through the ordinary refusal path. No engine rule changes.
- **Article V (server-authoritative, deterministic)**: PASS. The master
  `SimRng` lives in `World` and is unreachable from the wrapper by
  type; the substitute draws only from the per-decision stream that is
  discarded after the decision, so no-substitution ticks (off,
  observe-only, no fire) leave the RNG sequence untouched and replays
  reproduce identical fire sequences for deterministic seats (FR-008,
  SC-004). Tick order is untouched. The core config gains only a
  serialization-skipped passthrough field, so the defaults stamp is
  unchanged (guarded by the existing foreign-table leak test, which the
  plan extends).
- **Article VI (spec-first, test-guarded)**: PASS. This spec precedes
  the code; window, armed line, confinement radius, and mode are all
  configuration with documented defaults set from measured data
  (research.md) — no detector constant is hard-coded; every FR maps to
  a named test surface (quickstart.md).

**Post-design re-check (after Phase 1)**: unchanged — the data model and
contracts introduce no engine-side state, no new RNG, no unconfigured
constants. No Complexity Tracking entries.

## Project Structure

### Documentation (this feature)

```text
specs/061-stuck-detector/
├── spec.md                      # Feature spec (clarified, verified)
├── verification-2026-10-13.md   # Clarify-gate false-positive read
├── stuck_rule_replay.py         # Reproducible verification instrument
├── stuck-rule-fires.json        # Fire dump under the FR-002 gate
├── checklists/requirements.md   # 16/16
├── plan.md                      # This file
├── research.md                  # Phase 0 decisions
├── data-model.md                # Phase 1 entities
├── quickstart.md                # Phase 1 validation guide
├── contracts/
│   └── stuck-detector.md        # Config table, status surface, log rows
└── tasks.md                     # /speckit-tasks output (not this command)
```

### Source Code (repository root)

```text
crates/cloudkitty-server/src/
├── stuck.rs          # NEW: StuckConfig, StuckDetector (observer),
│                     #      StuckGuard (Behavior wrapper), StuckStatus,
│                     #      FireRecord + unit tests
├── lib.rs            # wire: wrap policy seats (~:189) and mind-class
│                     #       plugins (~:332) in StuckGuard; /stuck route
├── sim_task.rs       # wire: detector.observe(&world) beside the
│                     #       watchdog observe; fire log lines
├── api.rs            # wire: AppState + get_stuck handler
├── settings.rs       # wire: [stuck_detector] rows in /settings
└── main.rs           # wire: StuckConfig::from_toml_str in load_config

crates/cloudkitty-core/src/
└── config/mod.rs     # ONLY core edit: stuck_detector foreign-table
                      # passthrough beside watchdog + Default impl +
                      # extend the foreign-table leak test

crates/cloudkitty-server/tests/
├── server_integration.rs    # /stuck endpoint + end-to-end fire shapes
└── stuck_determinism.rs     # NEW: replay/fire-sequence determinism

crates/cloudkitty-core/tests/determinism.rs  # pattern reference only
experiments/tools/complete_config_3.py       # FOREIGN_TABLES += stuck_detector
CHANGELOG.md                                 # Unreleased entry
specs/061-stuck-detector/test-sort.md        # rule-6 guard sort (lives with the spec)
```

**Structure Decision**: one new module in `cloudkitty-server` beside
`watchdog.rs`, whose config/observe/status pattern it copies; wiring
edits only in the five named server files; a single passthrough field in
core config. No new crate, no new binary, no engine-module edits.

## Complexity Tracking

No constitution violations; table intentionally empty.
