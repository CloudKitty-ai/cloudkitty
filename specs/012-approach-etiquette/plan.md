# Implementation Plan: Approach Etiquette ("Wait for me!")

**Branch**: `009-orthogonal-interactions` (shared batch branch) | **Date**: 2026-07-20 | **Spec**: [spec.md](./spec.md)

## Summary

One new word and one manner. `MessageKind::WaitForMe` joins the vocabulary
(wire `wait_for_me`, base cooldown class, viewer text in the shared
`MEOW_TEXT` map). A guard in the two kitty-approach paths — the cuddle walk
in `needs_driven::pursue` and the kitty-target chase in
`selection::play_action_with` — makes the higher-id kitty of a pair at
exactly Manhattan 2 propose `Meow { WaitForMe }` on even world ticks instead
of stepping. The lower id closes the corner; mutual dances resolve in ≤ 2
ticks; passive-partner approaches lose at most one tick (parity alternation
is the progress guarantee). No engine, config, or snapshot-schema changes.

## Technical Context

**Language/Version**: Rust + the vanilla JS viewer map. **Dependencies**:
none new. **Storage**: none — the new kind appears in `recent_meows` and
cooldown maps additively; old snapshots never mention it and load unchanged.
**Testing**: vocabulary units, yield-guard units, a new
`tests/approach_etiquette.rs` regression built from the verified probe
(meows-available, meows-on-cooldown, play-chase variants), full suite.
**Constraints**: determinism (no RNG in the rule); Article IV (proposals
only). **Scale/Scope**: meow.rs, needs_driven.rs, selection.rs,
client/render.js, one new test file.

## Constitution Check

*PASS pre- and post-design.*

| Article | Verdict |
|---------|---------|
| I | ✅ Removes a relief *delay* (cuddle/play landed late); welfare suite re-run. |
| II / III | ✅ Untouched. |
| IV | ✅ Pure proposal-side manners; the engine validates a Meow like any other. |
| V | ✅ Deterministic: id order + tick parity; no draws added or removed. |
| VI | ✅ Spec first; no new constants (base meow cooldown reused — a deliberate no-new-config decision, spec Assumptions); tests amended with the change. |

## Project Structure

```text
specs/012-approach-etiquette/     spec, plan, research, data-model,
                                  contracts/wait-for-me-contract.md,
                                  quickstart, tasks
crates/cloudkitty-core/src/
├── meow.rs                       # WaitForMe: variant, ALL, related_need None, text
└── behavior/
    ├── needs_driven.rs           # yield guard in the cuddle arm
    └── selection.rs              # yield guard in play_action_with (kitty chase);
                                  # shared should_wait_for(ctx, friend_id, pos) helper
crates/cloudkitty-core/tests/approach_etiquette.rs   # the pinned dance regressions
client/render.js                  # MEOW_TEXT: wait_for_me
```

## Phase 0/1 artifacts

[research.md](./research.md) · [data-model.md](./data-model.md) ·
[contracts/wait-for-me-contract.md](./contracts/wait-for-me-contract.md) ·
[quickstart.md](./quickstart.md)
