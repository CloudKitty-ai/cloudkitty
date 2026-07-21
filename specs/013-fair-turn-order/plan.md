# Implementation Plan: Fair Turn Order

**Branch**: `013-fair-turn-order` | **Date**: 2026-07-20 | **Spec**: [spec.md](./spec.md)

## Summary

A constitutional amendment and a five-line mechanism. Article V clause (2)
now guarantees fairness as a principle (v1.1.0, amended in this change);
the engine honors it with a Fisher–Yates shuffle of the gathered decisions,
drawn from the world RNG at the top of the apply phase — n−1 draws per tick,
state-independent, serialized with the RNG so replays and save/restore are
exact. Decision gathering stays id-ordered (stream assignment, no
advantage). A new property test guards the clause per Article VI.

## Research (folded, three decisions)

- **R1 — Shuffle the decisions vector, not the kitty vector**: the kitty
  Vec's id order is load-bearing elsewhere (stream assignment, purr phase,
  serialization stability); the *decisions* list is the thing whose order
  confers advantage. Shuffling it touches exactly the surface the
  constitution now governs.
- **R2 — Fisher–Yates from the world RNG**: uniform over permutations,
  fixed draw count (n−1 `gen_range` draws; kitty count is constant), no new
  RNG, no config. Rejected: per-tick rotation (fair-ish but correlated —
  neighbors in id space stay neighbors in turn space); hashing tick+id
  (a second randomness source outside the single-RNG rule).
- **R3 — Guard with first-slot occupancy**: over N drawn orders, each of k
  kitties should lead ~N/k times; bound at > 6σ so the test is deaf to noise
  and deadly to bias (id order fails instantly at 0 or N). Plus the existing
  replay/save-restore suites for FR-002, unchanged.

## Constitution Check

*PASS pre- and post-design — this change IS the amendment ceremony.*

| Article | Verdict |
|---------|---------|
| I–III | ✅ Untouched; welfare suite re-run (SC-003). |
| IV | ✅ Validation/apply semantics per kitty unchanged; only their order varies. |
| V (as amended) | ✅ The clause this change ratifies: fair, reproducible turn order from the single seeded RNG. Determinism suites re-verify. |
| VI | ✅ Constitution v1.1.0 + spec + guarding property test in one change (Governance clause). |

## Structure

```text
.specify/memory/constitution.md        # Article V clause (2), v1.1.0, sync report
specs/013-fair-turn-order/             # spec, checklist, plan, tasks
crates/cloudkitty-core/src/world.rs    # shuffle at the top of the apply phase;
                                       # module-doc + phase comments updated
crates/cloudkitty-core/tests/turn_order_fairness.rs   # the Article VI guard
README.md                              # Article V row: "fair turn order" wording
```
