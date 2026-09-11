# Tasks: Groom-other reprice — cuddle relief scales with delivered bath relief

**Input**: Design documents from `/specs/054-groom-reprice/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/groom-pricing.md, quickstart.md

**Tests**: Included — house law (CLAUDE.md rule 5): every assertion added or re-pointed is verified red via `scripts/mutate.sh --expect <prediction>`; changed-behavior guards sorted red/green before running (rule 6).

**Organization**: Tasks grouped by user story. US1 = the payment (P1), US2 = calibration/farm closure (P2), US3 = one curve every reader + observability + docs (P3).

## Phase 1: Setup

- [ ] T001 Create `specs/054-groom-reprice/redden-list.md` with the cycle-0 baseline (full `cargo test --workspace` pass/fail/ignored counts on the clean branch) and the predicted-red ledger skeleton (one row per assertion this arc adds or re-points)

## Phase 2: Foundational (blocking all stories — the dials and THE curve)

- [ ] T002 Add `default_groom_cuddle_floor` (0.25), `default_groom_cuddle_slope` (3.5), `default_groom_cuddle_ceiling` (2.0) in `crates/cloudkitty-core/src/config/defaults.rs`
- [ ] T003 In `crates/cloudkitty-core/src/config/mod.rs` `ActionEffects`: add the three dial fields (serde defaults from T002, normal serialization, doc comments carrying the calibration intent — floor = drip tier, ceiling = ¼ rest_mutual per party); convert `groom_cuddle_relief` to the recognised-but-inert legacy field (`#[serde(default, skip_serializing)]`, doc comment naming the ForeignTable precedent and spec 054); update the `Default` impl
- [ ] T004 Implement `ActionEffects::groom_cuddle_pay(&self, delivered_bath: f32) -> f32` in `crates/cloudkitty-core/src/config/mod.rs`: clamp by `groom_relief`, normalize, `min(ceiling, floor + slope * x)` — add/mul/min only (FR-002a), with a doc comment stating the one-definition-every-reader rule (FR-008)
- [ ] T005 Add dial validation in `crates/cloudkitty-core/src/config/validate.rs`: the three dials join the finite-and-non-negative sweep, plus `groom_cuddle_ceiling >= groom_cuddle_floor` and slope ≥ 0 ordering errors with clear messages; the legacy key is NOT validated (ignored)
- [ ] T006 Unit tests in `crates/cloudkitty-core/src/config/mod.rs` (tests module): exact anchors c(0)=0.25, c(0.10)=0.60, c(0.25)=1.125, c(0.5)=2.0, c(1)=2.0 (SC-002); strict monotonicity below saturation, constant after; delivered clamp (bath > groom_relief → x=1); legacy key deserializes-but-never-serializes (a serialized default `Config` contains no `groom_cuddle_relief`); validation rejections (negative slope, ceiling < floor)
- [ ] T007 Mutate-verify every T006 assertion via `scripts/mutate.sh --expect`: mutate floor/slope/ceiling defaults, drop the `min` clamp, un-skip the legacy serialization — predict each red count and log rows in `specs/054-groom-reprice/redden-list.md`

**Checkpoint**: the curve exists, validated and pinned — no reader wired yet; world behavior unchanged.

## Phase 3: User Story 1 — Grooming pays for the cleaning it actually delivers (P1)

**Goal**: The effect body pays c(delivered fraction) per groomed tick, kitty-directed only.

**Independent Test**: quickstart §2 — a driven two-kitty scene shows per-tick pay equal to c(x) at every tick, including the decay as the target cleans.

- [ ] T008 [US1] Rewire the `Grooming { target: Some(friend) }` arm in `crates/cloudkitty-core/src/action.rs` `apply_activity_effects` (~L783–796): read the target's bath BEFORE `lower_need`, compute `delivered = bath_before.min(effects.groom_relief)`, apply the target's bath relief unchanged, pay the groomer `effects.groom_cuddle_pay(delivered)`; solo arm untouched
- [ ] T009 [US1] Sort the existing changed-behavior guards in `crates/cloudkitty-core/src/action.rs` tests (rule 6): every test pinning flat groomer pay (e.g. the ~L2809 duet-ignores-the-dial test and any flat 15.0/4.0 pay assertions) must go red for the predicted reason, then be re-pointed at curve values; kept behavior (groomee relief, solo groom, cosleep isolation) stays green — log predictions in `specs/054-groom-reprice/redden-list.md`
- [ ] T010 [US1] Integration test `groom_scene_pay` in `crates/cloudkitty-core/src/action.rs` tests (or the existing scene-test module): full-dirt target pays exactly 2.0; half-dirt pays exactly 2.0 (saturation); bath-7 target pays c(0.35); clean target pays exactly 0.25; pay decays tick-over-tick as the target cleans (US1 scenario 4); solo groom pays nothing
- [ ] T011 [US1] Mutate-verify the scene tests via `scripts/mutate.sh --expect`: mutate the delivered computation (drop the `.min`, read bath AFTER lower_need) and the pay call — predict which scene assertions redden; log in redden-list

**Checkpoint**: US1 delivers the reprice end-to-end; US2/US3 refine and propagate.

## Phase 4: User Story 2 — The relief farm closes; charm grooming survives (P2)

**Goal**: The calibrations hold as tested invariants at anchor values.

**Independent Test**: quickstart §1+§2 economics — route ordering groom-clean (0.25) = drip (0.25) < mutual rest (8.0 each); above-floor income bounded by opening dirt.

- [ ] T012 [P] [US2] Calibration tests in `crates/cloudkitty-core/src/config/mod.rs` tests: floor equals the anchor drip tier exactly (0.25, rule 1 strict); ceiling per party = rest_mutual anchor (8.0) / 4 exactly (rule 2, SC-004), asserted against the anchor values as literals with a comment naming the invariant-not-the-number rule (spec Assumptions)
- [ ] T013 [US2] Farm-closure scene test in `crates/cloudkitty-core/src/action.rs` tests: repeated grooming of a clean target accumulates exactly floor-per-tick (never above); a dirty-then-clean scene's cumulative above-floor income ≤ `opening_bath`-worth of delivered relief (SC-003/FR-006)
- [ ] T014 [US2] Mutate-verify T012/T013 via `scripts/mutate.sh --expect` (raise the floor above drip; break the per-tick delivered cap) — log in redden-list

## Phase 5: User Story 3 — One curve, every reader (P3)

**Goal**: The scripted seam, key settings, shipped configs, and docs all follow the curve; no reader of the flat price remains.

**Independent Test**: quickstart §3–§5 — seam sensitivity tracks the curve dials; `/settings` lists the three dials; every shipped TOML loads.

- [ ] T015 [US3] Re-point the groom-response seam in `crates/cloudkitty-core/src/behavior/needs_driven.rs` (~L418): scene value's groomer term becomes `ctx.config.actions.groom_cuddle_pay(emitter.needs.get(NeedKind::Bath))`; update the seam's doc comment (045 seam 3 wording) to the curve basis
- [ ] T016 [US3] Sort and re-point the 045 pinned sensitivity tests in `crates/cloudkitty-core/src/behavior/needs_driven.rs` (~L1859–1901): net-positive/net-negative/decline-bar-tracks-the-dial cases go red for predicted reasons, then re-point (the "generous" case now cranks slope/ceiling); gate-off (option_a) case stays green — predictions logged in redden-list
- [ ] T017 [US3] Replace the key-settings entry in `crates/cloudkitty-server/src/settings.rs`: `actions.groom_cuddle_relief` out, `actions.groom_cuddle_floor`/`_slope`/`_ceiling` in (value + default + presence-based source each); update the key-name goldens 19→21 (two-seat) and 18→20 (minimal) plus the L434/L481/L585/L621 pinned lines — each golden red-first with the predicted count
- [ ] T018 [US3] Re-point `crates/cloudkitty-core/tests/shipped_configs.rs` (~L119–131): retire the served-2.0 flat-pin assertion (it goes red when T019 scrubs the toml — predicted); replace with assertions that the served config carries no `groom_cuddle_relief` and inherits the three curve defaults, and that every `evals/v2/*.toml` and `evals/v3/*.toml` still loads byte-unchanged with the legacy key present (SC-006)
- [ ] T019 [P] [US3] Scrub `groom_cuddle_relief` from `cloudkitty.toml` (the pinned 2.0 line and any comment referencing it) and `training.toml` (the 15.0 line); pin no new dials — engine defaults serve (research R8)
- [ ] T020 [P] [US3] Update `docs/cuddle-relief-semantics.md`: replace the flat groom-other price with the curve (formula, dial table with defaults, delivered-relief basis, floor-=-drip and 4×-dominance calibrations, legacy-key note) per contracts/groom-pricing.md
- [ ] T021 [P] [US3] Add the CHANGELOG.md Unreleased entry (3.0-numbered behavior change): groom-other cuddle relief repriced to the delivered-relief ramp; flat dial retired to a legacy no-op key; lands with the Gen 1 reseat
- [ ] T022 [US3] Mutate-verify the seam and settings re-points via `scripts/mutate.sh --expect` (seam falls back to a flat constant; settings drops one dial entry) — log in redden-list

## Phase 6: Polish & cross-cutting

- [ ] T023 Full-suite verification: `cargo test --workspace` green; confirm schema-5 (408-float) assertions untouched (SC-005) and record the `/config` + stamp delta (serialize defaults pre/post, diff = exactly the declared dial delta, SC-007) in `specs/054-groom-reprice/redden-list.md`
- [ ] T024 Walk `specs/054-groom-reprice/quickstart.md` §1–§6 end-to-end on the finished branch; fix any drift between quickstart claims and reality (edit quickstart only if it, not the code, is wrong)
- [ ] T025 Finalize `specs/054-groom-reprice/redden-list.md` (final counts, every ledger row resolved), then open the PR with the spec-054 summary and the FR-013 banner: **CI to green, MERGE HELD for the owner's reseat sequencing** — do not merge

## Dependencies

- Phase 2 blocks everything (the curve and dials are the shared model).
- US1 (Phase 3) blocks US2's scene tests (T013 drives scenes through the new payment) and US3's seam/test re-points (T016/T018 assert against curve values).
- T012 depends only on Phase 2 (curve units) — can run parallel to Phase 3.
- T019 before T018's final green (the shipped-config assertions read the scrubbed tomls); T017 independent of T015/T016 (different crates).
- Phase 6 last; T025 strictly last.

## Parallel examples

- After Phase 2: T012 [P] (curve calibration units) alongside T008 (effect rewire).
- Within US3: T019/T020/T21 [P] (tomls, docs, changelog — disjoint files) while T015–T017 proceed sequentially per file.

## Implementation strategy

MVP = Phase 2 + US1 (the reprice paying correctly in-engine), then US2's invariant pins, then US3's propagation. Each phase ends with its mutate cycle before the next (no tree edits while mutate.sh runs; `--no-fail-fast` under it; scoped probes read only 12 log lines). The redden-list is the running argument: every assertion either began red for its predicted reason or is listed with why not (rule 6 vacuous-guard reporting).
