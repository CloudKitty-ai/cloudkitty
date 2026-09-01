# Redden list: spec 046 (refusal stamp)

Every rule-5 cycle for this feature. A row is complete only when the
injected bug produced the *predicted* red and the revert restored green.

**Suite counts** (READ THE COUNT):
- Pre-branch baseline (origin/main 0df1e7f, no 046 code): **774 passed / 0 failed** (64 suites, `cargo test --workspace`, 2026-09-01)
- Post-implementation (T020): **787 passed / 0 failed** (64 suites; +13 vs baseline, none lost)
- T020 golden note: the pinned digest hashes the SERIALIZED WORLD, which now carries the additive `refusal_log` — it cannot pass unregenerated (the 041 precedent in the module doc regenerated for the same reason). Continuity witness run before regenerating: 10k-tick world JSON with the `refusal_log` key stripped digests to EXACTLY the 041 pin `7b361b2a…` (full JSON: `04102fe4…`, the new pin). Dynamics, RNG, and every sibling field byte-identical.
- Close-out (T025): **787 passed / 0 failed** (64 suites) after `cargo fmt` + CI-exact clippy clean (`cargo clippy --workspace --all-targets -- -D warnings`). Baseline 774 → 787: +13 new assertions, nothing lost.
- Post-T026: **788 / 0**. Post review-medium fixes (findings 2/4/6/7/8, 2026-09-01): **790 passed / 0 failed** (64 suites; +2 = strip witness + ring-window test), fmt + CI-exact clippy clean. Golden regenerated a second time (`8e184e6d…`): the 4,000→6,000 default moves the serialized ring's `capacity` integer only — the in-tree strip witness stayed green across the change.
- Post findings 3+5 (owner-ruled, 2026-09-01): **792 passed / 0 failed** (64 suites; +2 = sibling re-stamp test + publish-reuse test), fmt + CI-exact clippy clean.

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
| 10 | `the_refusal_ring_honors_configured_retention` (world.rs) | `World::generate` hardcodes `RefusalLog::new(1000)` | Ring keeps all 5: `[0,1,2,3,4]` vs `[2,3,4]` | Exactly that | ✓ reverted |
| 11 | `default_retention_covers_the_baseline_window` (config/mod.rs) | Default shrunk 4000 → 3000 | Floor assertion reds naming 3000 | "refusal_retention default 3000 < 3,500: the >=15k-tick baseline window ... no longer fits" | ✓ reverted, 2 passed |
| 12 | Stamp guard line + `refusal_retention_explicit_default_equals_absent` (config/mod.rs) | Deleted the field's `skip_serializing_if` attribute | Stamp-guard line reds ("leaked into the stamp"); equality test reds too | Both: "refusal_retention leaked into the stamp: {...refusal_retention:4000...}" + equality panic | ✓ attribute restored, 2 passed |
| 13 | `a_pre_046_save_resumes_with_the_configured_refusal_capacity` (persist.rs — moved from tasks.md's snapshot_resume.rs: core tests cannot import the server crate) | (no injection — T018 written before T019's re-stamp existed; the pre-implementation state IS the bug) | Defaulted ring degrades to capacity 1: `left: 1, right: 3` | Exactly that | ✓ green at T019's re-stamp, persist suite 13 passed |
| 14 | `a_mid_window_save_resumes_with_its_refusal_events_intact` (persist.rs, convergence T026) | Load-path re-stamp hardcoded `set_capacity(1)` | Reloaded ring trimmed to the newest single event — verbatim assertion reds | Exactly that: left held only `{kitty_id:1, Purr, tick:2}` vs 3 saved | ✓ reverted, persist suite 14 passed; close-out suite 788/0 |
| 15 | `golden_strip_witness_refusal_ring_is_the_only_delta` (evolution_golden.rs, review-medium F6) | Spurious RNG draw at the recording site (a dynamics move hiding under the ring) | Strip digest ≠ pre-046 pin (full golden reds too; only the strip assertion names WHY) | Exactly that: strip `b8980886…` vs pin `7b361b2a…`, full also red | ✓ reverted, 2 passed |
| 16 | `default_ring_covers_the_baseline_window_under_absorbed_load` (config/mod.rs, review-medium F2) | (no injection — the shipped 4,000 default IS the bug, T018 pattern) | Window < 15,000 (review predicted ~10.5k) | "covers only 10425 ticks (capacity 4000, taxed 1586, absorbed 2414)" — review's counts reproduced exactly | ✓ green at the 6,000 raise |
| 17 | `default_retention_covers_the_baseline_window` re-derived floor (config/mod.rs) | Default shrunk 6000 → 5000 | Floor assertion reds naming 5000; window test reds too | Both: "default 5000 < 5,700" + "covers only 13231 ticks (capacity 5000)" | ✓ reverted, 3 passed (incl. explicit-default equality now spelled via the default fn) |
| 18 | Capacity envelope, both layers (sim_task.rs + server_integration.rs, review-medium F4) | `Published::from_world` hardcodes `refusal_capacity: 0` | Unit test reds at "the ring's own bound"; integration reds at "the served capacity is the configured retention" | Exactly both | ✓ reverted |
| 19 | Typed endpoint test (server_integration.rs, review-medium F8 — this test's first redden row) | `#[serde(rename = "entries")]` on the envelope's `events` field | First-poll "always an events list" assertion reds on the drifted key | Exactly that: `{"capacity":6000,"entries":[]}` in the panic message | ✓ reverted, 15 passed |
| 20 | `a_retention_edit_reaches_every_ring_on_resume` (persist.rs, review-medium F3) | (no injection — the missing sibling re-stamps ARE the bug, T018 pattern) | Siblings keep persisted capacity; refusal alone re-stamped | Exactly that: `left: (1000, 1000, 6007) / right: (1007, 1007, 6007)` | ✓ green at the two sibling `set_capacity` calls, persist suite 15 passed |
| 21 | `the_refusal_window_allocation_is_reused_until_the_ring_changes`, rotation arm (sim_task.rs, review-medium F5) | Witness dead-coded to length-only (tick comparison dropped) | Rotation arm reds ("length alone is not the witness"); quiet arm stays green | Exactly that, sim_task.rs:311 | ✓ reverted |
| 22 | Same test, quiet-tick arm | Reuse arm dead-coded (`if false && …` — always rebuild) | Quiet-arm `Arc::ptr_eq` reds ("an unchanged ring reuses") | Exactly that, sim_task.rs:304 | ✓ reverted, 5 passed |

**T021 no-honest-red caveat** (rule 6): the rl crate reads neither
`EventsConfig` nor `refusal_log` — grep over `crates/cloudkitty-rl/src`
finds no `.events`/refusal read (its distress references are snapshot
kitty state and `thresholds.distress`); the mask derives from
`World::from_snapshot`, whose rings are documented fresh bookkeeping.
The one rl-side surface 046 could move, `engine_defaults_sha256`, is
guarded by cycle 12's stamp test. A mask test here would have no honest
red, so none was written.

**Review note (code-review low, 2026-09-01)**: finding 3 flagged
`World::from_snapshot` installing `RefusalLog::default()` — no change
needed: `from_snapshot` is the rule-evaluation view, documented "fresh
bookkeeping (empty logs, zero-seeded RNG)", and the sibling distress and
activity logs use `::default()` there identically. It is not a resume
path; the resume path is `persist::load_and_validate`, which re-stamps.
Findings 1–2 (re-stamp not yet wired) were the in-flight T019, closed the
same session.

## Notes

**T022 live emit-proof (2026-09-01)**: bounded boot of the 046 build
(`perl -e 'alarm 14; exec @ARGV'`, shipped `cloudkitty.toml` with bind
127.0.0.1:18946 + tick_ms 50, fresh scratch snapshot, run from the
worktree root so policy artifacts resolve). First poll of
`GET /events/refusal` at ~tick 170:

```json
[{"kitty_id":4,"proposed":{"action":"sleep","with":3},"tick":16,"absorbed":true},
 {"kitty_id":1,"proposed":{"action":"sleep","with":4},"tick":17,"absorbed":true},
 {"kitty_id":5,"proposed":{"action":"groom","target":2},"tick":35,"absorbed":false},
 {"kitty_id":3,"proposed":{"action":"eat"},"tick":45,"absorbed":true},
 {"kitty_id":2,"proposed":{"action":"play","target":"kitty","id":5},"tick":45,"absorbed":true},
 {"kitty_id":5,"proposed":{"action":"play","target":"kitty","id":2},"tick":45,"absorbed":true}]
```

Both flag values live; partnered proposals carry `with`/`target`
verbatim; ticks non-decreasing.
