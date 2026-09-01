# Tasks: Waterline Contagion (price, not law)

**Input**: Design documents from `/specs/044-waterline-contagion/`

**Prerequisites**: plan.md, spec.md, research.md (D1–D7), data-model.md, contracts/config-surface.md, quickstart.md

**Tests**: Included — the spec's acceptance is test-shaped (SC-001..SC-006) and Constitution Article VI requires every FR to land with a CI guard. House red-first rule applies (CLAUDE.md 5/6): every new assertion is proven red via the exact bug it catches, recorded in `specs/044-waterline-contagion/redden-list.md`, then reverted to green.

**Organization**: Two-commit delivery (plan Structure Decision): US1 + US3 = commit 1 (config surface inert, validation), US2 = commit 2 (charge path + armed tests). US3 is sequenced *before* US2 because the widened budget is pure validator work that belongs in the inert commit; the stories remain independently testable.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

- [ ] T001 Baseline: in `~/ai/cloudkitty-waterline`, run `cargo test --workspace` and record the exact pass count (expected 737+/0 at a2e93f8) plus the default-config stamp value in specs/044-waterline-contagion/redden-list.md (header note); confirm `git status` clean
- [ ] T002 Create specs/044-waterline-contagion/redden-list.md with the 043-style table: assertion | injected bug | predicted failure | observed red | restored green

## Phase 2: Foundational

*(No shared scaffolding beyond Setup — the config field itself is US1's first task; nothing blocks story start.)*

**Checkpoint**: baseline counts recorded — story work can begin.

---

## Phase 3: User Story 1 — Inert launch (Priority: P1) 🎯 MVP

**Goal**: `[water] contagion_factor` exists, defaults to 0.0, is rejected when nonsensical, and provably changes nothing: stamp, golden, determinism all byte-identical.

**Independent Test**: quickstart §1 — full workspace suite green with zero modified existing tests; stamp guard asserts the factor stays out of the default serialization.

### Tests for User Story 1 (red-first)

- [ ] T003 [US1] Extend the default-serialization stamp guard in crates/cloudkitty-core/src/config/mod.rs (sibling of `roam_cell_stays_out_of_the_default_serialization`, mod.rs:2494): a default `Config`'s TOML round-trip contains no `contagion_factor` key AND an explicit `contagion_factor = 0.0` also serializes without the key (identity-skip). Written against the not-yet-existing field → first red is a compile fail; after T005, prove the real red by removing `skip_serializing_if` (predict: key appears), record in redden-list, restore
- [ ] T004 [P] [US1] Add validator unit tests beside `validate_water`'s existing ones in crates/cloudkitty-core/src/config/validate.rs: negative factor rejected, NaN/∞ rejected, and both rejected EVEN when `bath_gain = 0.0` (bounds precede the early return, FR-010); factor absent/0.0/1.0 all accepted on the default config. Red-first: run before T005/T006 → compile fail; after, inject bounds-check-after-early-return (predict: the gain-0 case goes green wrongly), record, restore

### Implementation for User Story 1

- [ ] T005 [US1] Add `contagion_factor: f32` to `WaterConfig` in crates/cloudkitty-core/src/config/mod.rs (~line 148): `#[serde(default, skip_serializing_if = "f32_is_zero")]` reusing `f32_is_zero` (mod.rs:1022); doc comment in house voice covering the mechanism, 0.0 = off, 1.0 = Gen 1 ruling, dry-member-only, own-activity rule (contracts/config-surface.md is the source)
- [ ] T006 [US1] In `validate_water` (crates/cloudkitty-core/src/config/validate.rs:569): add the finite-and-non-negative bounds check for `contagion_factor` BEFORE the `gain == 0.0` early return, with an actionable ConfigError naming `[water] contagion_factor` (FR-010; budget widening deferred to US3/T012)
- [ ] T007 [US1] Prove inertness: `cargo test --workspace` — full suite green including `evolution_golden` (unregenerated), `determinism`, both stamp guards; READ THE COUNT (T001 baseline + new tests only, zero modified existing tests); record in redden-list header
- [ ] T008 [US1] Commit 1a (config surface): `git add` the two source files + spec artifacts touched so far; commit "spec 044 commit 1: [water] contagion_factor — inert config surface + bounds validation"

**Checkpoint**: US1 shippable alone — the knob exists, validated, provably inert.

---

## Phase 4: User Story 3 — The headroom budget still cannot be broken (Priority: P3, sequenced into commit 1)

**Goal**: `validate_water`'s budget re-stated as `ceiling + max(1, factor) × gain × max_ratio < safeguard`; served config + both sweeps pass unchanged.

**Independent Test**: quickstart §3–4 — boundary matrix from contracts/config-surface.md flips exactly at the widened line; `shipped_configs` + `shipped_configs_rl` green with no config edits.

### Tests for User Story 3 (red-first)

- [ ] T009 [US3] Budget boundary tests in crates/cloudkitty-core/src/config/validate.rs: (a) a config valid under the old budget stays valid at factor 1.0 (bit-identical check, FR-011); (b) factor > 1.0 pushing `ceiling + factor×gain×max_ratio` to ≥ safeguard is rejected, error names the keys and remedies; (c) the same factor with enough headroom is accepted; (d) rejection blames the correct max-ratio cat (reuse the existing heterogeneity-style fixture idiom). Red-first: written before T012 → (b) goes green only after widening lands; inject `max(1.0, factor)` → `1.0` (predict: (b) green wrongly = vacuous), record, restore

### Implementation for User Story 3

- [ ] T010 [US3] Widen the budget in `validate_water` (crates/cloudkitty-core/src/config/validate.rs:600-632): `max_charge = gain * max_ratio * factor.max(1.0)`; extend the error text with the contagion remedy (lower the factor) while keeping the existing remedies verbatim
- [ ] T011 [US3] Re-run the sweeps: `cargo test --test shipped_configs` and `cargo test -p cloudkitty-rl --test shipped_configs_rl` — green with zero config edits (FR-011, SC-006); record counts in redden-list header
- [ ] T012 [US3] Complete commit 1: full `cargo test --workspace`, READ THE COUNT, then amend/squash into T008's commit so ONE inert config-surface commit lands (the plan's two-commit shape; 1a is unpushed, so amending is safe)

**Checkpoint**: commit 1 complete — config surface + full validation, still byte-inert.

---

## Phase 5: User Story 2 — The dry partner pays the wet-fur price (Priority: P2)

**Goal**: the charge itself: pre-loop `wet_ids`/`contagious` sets, else-if arm beside occupancy, all spec acceptance scenarios pinned in-tree.

**Independent Test**: quickstart §2 — `cargo test --test waterline_contagion` covers per-kind accrual, exemption, gate, nothing-cases, armed determinism.

### Tests for User Story 2 (red-first — write the file first, watch every assertion fail honestly)

- [ ] T013 [US2] Create crates/cloudkitty-core/tests/waterline_contagion.rs with the harness: a small generated world with one permanent water tile (reuse the `water_safeguard.rs` pinned-world idiom), helpers to place two cats adjacent, set activities directly, tick once, and read bath deltas; plus a `charge(config, id)` = `contagion_factor × bath_gain × bath_ratio(id)` expectation helper
- [ ] T014 [US2] Accrual tests, one per paired kind (FR-003, SC-002): dry cat Resting{with_friend}, Sleeping{with_friend}, Playing{kitty target}, Grooming{target} beside a wet partner accrues `ambient + charge` to tolerance. Red-first: file runs before T018 → all four fail with no-accrual (predict exact expected-vs-actual), record, keep red until T018
- [ ] T015 [US2] Exemption + gate tests (FR-004, FR-005, SC-003): wet member's rise is exactly occupancy (never + contagion); dry member at/above ceiling accrues ambient only; overshoot bounded by one scaled charge just under the ceiling
- [ ] T016 [US2] Nothing-case tests (spec edge cases + clarified Option A): both-dry, both-wet, critter-play target, idle groomee of a wet groomer (asymmetric reference — THE Option A pin), solo activities; each accrues ambient only
- [ ] T017 [US2] Armed determinism test (FR-008, SC-005): two same-seed runs at factor 1.0 for 500 ticks produce identical serialized streams; and an explicit `contagion_factor = 0.0` config run is byte-identical to a default (key-absent) config run over the same span (pins spec US1 scenario 2: explicit zero ≡ absent, everywhere)

### Implementation for User Story 2

- [ ] T018 [US2] Implement the charge in `World::advance_needs` (crates/cloudkitty-core/src/world.rs:870-916) per research D2/D3: pre-loop `wet_ids`/`contagious` BTreeSets collected only when `contagion_factor > 0.0 && bath_gain > 0.0`; `else if` arm after the occupancy `if`, sharing the pre-charge ceiling gate, charging `contagion_factor * bath_gain * bath_ratio(id)`; house-voice comment stating the own-activity rule and the no-double-pay invariant
- [ ] T019 [US2] Run `cargo test --test waterline_contagion` — all green; complete every redden-list row for T014–T017 (each assertion's observed red + restored green); spot-inject one bug per category if any assertion never went honestly red (e.g. charge the wet member too → exemption test reds; drop the `!on_water` guard → both-wet test reds)
- [ ] T020 [US2] Full inertness re-proof after touching world.rs: `cargo test --workspace` — `evolution_golden` still unregenerated, `determinism` green, stamp unmoved, READ THE COUNT
- [ ] T021 [US2] Commit 2: "spec 044 commit 2: the contagion charge — pre-loop sets + else-if arm + gate-zero-style armed suite"

**Checkpoint**: all three stories functional; both commits match the plan's delivery shape.

---

## Phase 6: Polish & Cross-Cutting

- [ ] T022 [P] CHANGELOG.md: one line under `## Unreleased` (house changelog practice — marker style, arc one-liner)
- [ ] T023 [P] Verify the redden-list is complete in specs/044-waterline-contagion/redden-list.md: every assertion added in T003/T004/T009/T014–T017 has an honest red row (injected bug, predicted failure, observed, restored); fix any vacuous row per CLAUDE.md rule 6
- [ ] T024 Walk quickstart.md end-to-end exactly as written (§1–§4) and confirm every expectation line; fix quickstart if reality differs (never weaken a criterion)
- [ ] T025 Final gate: `cargo test --workspace` + `cargo clippy --workspace --all-targets` + `cargo fmt --all --check` (043 lesson: CI enforces `is_multiple_of`-class lints and doc-comment list rules — no doc line opening with `+`/`-`/`*`); READ THE COUNT; commit any polish as "spec 044 polish"

---

## Dependencies & Execution Order

- **Setup (T001–T002)** → everything.
- **US1 (T003–T008)**: T003/T004 written first (red = compile fail), T005 → T006 → T007 → T008. T004 parallel with T003 (different files).
- **US3 (T009–T012)**: after T006 (needs the field + bounds); T009 before T010 (red-first).
- **US2 (T013–T021)**: after commit 1 (needs the validated field); T013 → T014 → T015 → T016 → T017 sequentially (one file, independent test fns); T018 after all US2 tests exist and are red; T019 → T020 → T021.
- **Polish (T022–T025)**: after US2. T022/T023 parallel.

### Independent test criteria

- **US1**: workspace suite green, stamp guard extended, golden/determinism untouched — knob shippable inert with no charge path at all.
- **US3**: validator boundary matrix green + both sweeps green — budget correct even if US2 never landed.
- **US2**: `waterline_contagion.rs` green — behavior correct given US1's field and US3's budget.

### MVP scope

US1 alone (commit 1a) is a shippable MVP: the knob exists, validated, inert. US3 completes commit 1; US2 delivers the mechanism.

## Notes

- Same-file tasks (T005/T006, T010; T014–T017) are sequenced, not [P], except where marked.
- Every commit message follows the house style; GPG signing works (stale-lock fix banked in memory if it recurs).
- Worktree `~/ai/cloudkitty-waterline` only; never the main checkout.
