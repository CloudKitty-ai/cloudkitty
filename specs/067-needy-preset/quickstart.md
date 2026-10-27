# Quickstart: Needy Behaviour Preset (spec 067)

Validation scenarios proving the feature end-to-end. Scratch configs
live in the session scratchpad, never under the repo tree (a needy seat
outside `experiments/` reddens both config sweeps by spec 066).

## Prerequisites

- Worktree `~/ai/cloudkitty-needy-preset` on the feature branch;
  `cargo build --workspace` green; the binding built for the pytest.
- Baseline pins recorded on the base commit: `engine_defaults_sha256`,
  `Config::default()` JSON, a 300-tick serialized world at a fixed seed
  for `cloudkitty.toml`, and a 200-decision trace per existing preset.

## 1. Inert when absent (SC-001, FR-002)

- `cargo test --workspace`: green, zero golden/pin/fixture diffs.
- Stamp and default JSON equal the baseline; no `needy` key.
- The 300-tick world and the three preset traces equal the baseline
  byte for byte.

## 2. The instrument (SC-003, US1)

Scratch config: `cloudkitty.toml` + one kitty `behavior = "needy"` +
`[welfare_hazard] acknowledged = ["needy"]`, fixed seed, default
`[needy]` (or a short-horizon `[needy]` with small gaps for the test).
Run the first ten episodes through the engine and assert, per tick:

| check | expected |
|-------|----------|
| onset/release ticks | equal the schedule the law computes from the seed |
| masked needs between onset and release | non-decreasing apart from engine floors; the kitty's applied actions never carry a masked governing need |
| unmasked needs | serviced (applied actions include their relief at the teacher's rate) |
| a friend adjacent proposing Rest/Sleep/Groom toward the needy kitty every tick | resolved to Idle while the relief need is masked; accepted after release |
| `needy_hold` variant | no level release; every release `by_limit` at onset + hold_ticks |
| two needy seats | two schedules; changing one kitty's id changes only its own |

## 3. Determinism and stream isolation (SC-002)

- Generate twice at one seed: identical `Kitty.needy` sequences.
- Add a needy seat to a roster: every OTHER kitty's dealt decision
  seeds and the master `World.rng` state after 300 ticks equal the
  no-needy run's (the sub-stream consumed nothing shared).

## 4. Observability (SC-005, FR-012)

- Snapshot: a needy kitty's entry carries `needy` (phase, masked
  names, ordinal); every other kitty's entry is byte-identical to
  pre-feature.
- Binding: `env.needy()` returns `[]` on a plain config and one tuple
  per needy seat whose fields agree with the schedule each step.

## 5. Hazard (SC-006, US3)

Spec 066's seven validation shapes with `needy` and `needy_hold`; both
seated → the line to add is `acknowledged = ["needy", "needy_hold"]`
(with a raised distressed start: `["initial_needs", "needy", "needy_hold"]`).
Sweep self-tests gain a needy file (refused outside `experiments/`,
passes inside when acknowledged). Server: refusal without the switch,
boot line / `GET /config` / settings row naming the modes with it.

## 6. Teacher eligibility (SC-007, US5)

- `registry.teaches("needs_driven" | "playful" | "teacher") == Some(true)`,
  `teaches("needy" | "needy_hold") == Some(false)`, unknown → `None`.
- The collector on a roster with one needy seat: zero rows for that
  seat, one log line naming it, every other seat as today (Experiments'
  lane; run on their consent in this PR or recorded as owed).

## 7. Rule-5 ledger (filled in by tasks)

Every assertion above goes red first via `scripts/mutate.sh --expect`.
Expected hand-rolled items: none (every red here is a code mutation).
Candidate mutations the tasks must include: the verdict skipping the
partner clause; `available_friend_in` ignoring the mask; the release
check reading `>` instead of `>=`; `needy_hold` honouring the level;
the sub-stream seeded without the kitty id; the ordinal not
incrementing; the advance step placed before `advance_needs`; the
masked view leaking into `Teacher` (D12 trace); `teaches()` defaulting
false; the mix length check hard-coding 6 (FR-016: the test builds the
expected message from `NeedKind::ALL.len()`).
