# Redden list: spec 046 (refusal stamp)

Every rule-5 cycle for this feature. A row is complete only when the
injected bug produced the *predicted* red and the revert restored green.

**Suite counts** (READ THE COUNT):
- Pre-branch baseline (origin/main 0df1e7f, no 046 code): **774 passed / 0 failed** (64 suites, `cargo test --workspace`, 2026-09-01)
- Post-implementation (T020): TBD
- Close-out (T025): TBD

| # | Assertion (test) | Injected bug | Predicted failure | Observed red | Restored green |
|---|------------------|--------------|-------------------|--------------|----------------|
| 1 | `set_capacity_trims_oldest_first_and_floors_at_one` (events.rs) | `set_capacity` trims with `pop_back` (newest) instead of `pop_front` | Shrink assertion: kept ticks `[0,1,2]` not `[2,3,4]` | Exactly that: `left: [0, 1, 2] / right: [2, 3, 4]`, "shrinking the ring keeps the newest events" | ✓ reverted, 1 passed |
| 2 | `refusal_retention_zero_is_rejected_and_one_accepted` (config/mod.rs) | Deleted the `[events] refusal_retention` row from `validate_events` | `unwrap_err()` panics on `Ok` — validation silently accepts 0 | Exactly that: `called Result::unwrap_err() on an Ok value` | ✓ row restored, 1 passed |
| 3 | `a_refused_proposal_is_stamped_with_kitty_proposal_and_tick` (world.rs) | Recording predicate inverted to `validated == proposal` | Refusals never match (validated=Idle ≠ proposal) → ring empty, first assertion `left: 0, right: 2` | Exactly that: "two refusals, two events: []" left 0 right 2 | ✓ predicate restored, 1 passed |
| 4 | `duration_enforcement_decides_the_absorbed_flag_never_the_refusal` (world.rs) | Hardcoded `absorbed: false` at the recording site | Arm (b) red at the `events[0].absorbed` assertion | Red at world.rs:2877 = that assertion ("the scene continued") | ✓ flag expression restored, 1 passed |
| — | Same two tests, pre-implementation | (no injection — T009 not yet written) | Both red on empty ring | `left: 0, right: 2` and `left: 0, right: 1` | ✓ green at T009 |
| 5 | `a_refused_partnered_proposal_carries_the_asked_partner` (world.rs) | Recording site swapped to `proposed: enforced` | Target lost — event carries Idle, verbatim assertion reds | Exactly that: `left: Idle / right: Play { target: Some(Kitty { id: 2 }) }` | ✓ reverted, 2 passed |
| 6 | `both_tick_drivers_stamp_identical_refusal_streams` parity arm (joint_action_parity.rs) | Spurious seam-only `refusal_log.record` in `tick_with_proposals_seeded` | Joint stream gains an extra event → byte-inequality | "refusal streams diverged" | ✓ reverted |
| 7 | Same test, non-empty (vacuity) arm | Recording predicate dead-coded (`if false && ...`) | Non-empty assertion reds | "500 built-in ticks must produce at least one refusal, or this parity check is vacuous" | ✓ reverted, suite 6 passed |
| 8 | `a_refusal_event_serializes_the_proposal_verbatim` (events.rs) | `#[serde(skip_serializing_if = "Not::not")]` on `absorbed` (the FR-008 trap) | Pinned-JSON assertion reds — key absent at `false` | Exactly that: left string lacks `"absorbed":false` | ✓ reverted, 1 passed |
| 9 | `published_refusals_are_the_ring_verbatim_and_a_fresh_world_serves_none` (sim_task.rs) | `Published::from_world` wired to `Arc::new(Vec::new())` (always-empty serve — the F-029 zero trap) | Red at "the refusal was published" | Exactly that, sim_task.rs:226 | ✓ reverted, 1 passed |

## Notes

(live emit-proof payload lands here at T022)
