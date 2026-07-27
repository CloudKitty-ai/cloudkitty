# Tasks: Config Restructure — Table-Driven Validation, Navigable Layout

**Input**: Design documents from `/specs/020-config-restructure/`

**Prerequisites**: plan.md, spec.md (incl. the 2026-07-26 FR-004 amendment), research.md (D1–D5), data-model.md, quickstart.md

**Tests**: No new landed tests — the bar is the existing suite with zero assertion changes (FR-007) plus the enumerated rejection-path sweep (FR-008, throwaway harness deleted before landing per the standing goldens ruling). The sweep harness is the feature's principal verification instrument and is built first.

**Organization**: By user story, and the priority order happily *is* the safe execution order: tables fold inside the existing file (US1), the catch-all dissolves (US2), and the file splits last (US3) — so `mod.rs`/`defaults.rs`/`validate.rs` are born with final content and every checkpoint diffs cleanly.

## Format: `[ID] [P?] [Story?] Description`

## Phase 1: Setup

**Purpose**: The verification instrument every story checkpoints against.

- [ ] T001 Author the throwaway sweep harness as `crates/cloudkitty-core/examples/config_sweep.rs` (per research D4): for every rejection rule in baseline `config.rs`, one minimal TOML mutation of the default config that trips exactly that rule; output sorted `rule\tmessage` lines. Coverage bar: rule count matches the `ConfigError::invalid` site count (~46 at `33f69df`); any rule untrippable via parseable TOML is enumerated with a reason. Cross-check the inventory against the existing unit tests' invalid-config cases. (Working-tree only — never committed; deleted at T010.)

---

## Phase 2: Foundational

**Purpose**: Freeze the baseline before any code moves.

- [ ] T002 Create a worktree at `33f69df` under the job tmp dir, copy `config_sweep.rs` in (uncommitted), run it there and in the branch tree, confirm the two outputs are identical (they must be — no code has changed yet), and store the baseline output as `$CLAUDE_JOB_DIR/tmp/ck-020-verify/base-sweep.txt`. Record the rule count.

**Checkpoint**: instrument proven self-consistent; story work can begin.

---

## Phase 3: User Story 1 — Adding a bounded field costs one row (P1) 🎯 MVP

**Goal**: Every mechanical bound guard is a table row carrying its exact message; no if/return guard copies remain.

**Independent Test**: sweep diff vs baseline byte-identical; workspace green; the quickstart §4 walkthrough shows one row suffices.

- [ ] T003 [US1] Fold the mechanical guards in `crates/cloudkitty-core/src/config.rs` into per-cluster table loops (research D2): the ~13 zero/at-least guards (baseline 1072–1176 region) plus any other same-shape clusters across the section validators (survey the whole file — the two existing loops at 1089–1101 and 1110–1127 are the pattern). Every row carries `(field, rendered_value, expected)` with the exact baseline message — rationale parentheticals included, byte-for-byte; clusters already sharing one message keep the shared-message form. Relational/branching rules (min>max, range checks with `is_nan`, capacity logic) stay as-is (FR-002 moves them later; they are never table rows).
- [ ] T004 [US1] Checkpoint: `cargo test --workspace` green; rerun the sweep in the branch tree and `diff` against `base-sweep.txt` — byte-identical required before proceeding.
- [ ] T005 [US1] Run the quickstart §4 walkthrough: throwaway bounded field (struct field + default fn + one table row), out-of-bounds TOML rejects with a cluster-consistent message, in-bounds accepts, revert; record in quickstart; clean tree (FR-009: nothing lands).

**Checkpoint**: US1 delivered — the recurring per-field toll is one row.

---

## Phase 4: User Story 2 — Validators match the config's structure (P2)

**Goal**: The 170-line catch-all is gone; six honestly-named section validators, called in the documented sequence.

**Independent Test**: sweep diff byte-identical for every single-fault path; multi-fault spot-assertions match the data-model.md sequence.

- [ ] T006 [US2] Dissolve `validate_behavior` in `crates/cloudkitty-core/src/config.rs` into `validate_behavior` (now `[behavior]` only), `validate_purr`, `validate_actions`, `validate_viewer`, `validate_events`, `validate_persistence` — rules moved verbatim in their within-section order; `validate()`'s call list becomes the data-model.md sequence (the catch-all expanded in its slot by its own first-occurrence order). Confirm the 8–12 tail order against the actual catch-all and correct data-model.md's listing if the file says otherwise (the rule is the file's order, the listing is its record).
- [ ] T007 [US2] Checkpoint: workspace green; sweep diff vs baseline byte-identical (single-fault paths — the sweep only ever trips one rule per case, so the diff must be empty); separately construct 2–3 multi-fault configs spanning the old interleave (e.g. `[purr] min_ticks = 0` + `[behavior] sunbeam_reach = 0`) and assert the reported message follows the documented sequence; record both in quickstart §2.

**Checkpoint**: US2 delivered — sections are the map.

---

## Phase 5: User Story 3 — Defaults and validation each have a home (P3)

**Goal**: `config.rs` becomes `config/{mod,defaults,validate}.rs` with the public surface byte-compatible.

**Independent Test**: diff outside the config module empty; tests module moved content-untouched; serde spot-set passes.

- [ ] T008 [US3] Split per plan: `crates/cloudkitty-core/src/config/mod.rs` (types, `ConfigError`, `validate()` entry, the `#[cfg(test)]` module byte-unmodified), `config/defaults.rs` (the ~20 `default_*` fns, `pub(super)`, bodies unchanged; serde attributes become `default = "defaults::default_x"`), `config/validate.rs` (all section validators + table loops, `pub(super)`). Delete `config.rs`. No other file changes anywhere.
- [ ] T009 [US3] Checkpoint: `cargo test --workspace` green; quickstart §1 (diff vs `33f69df` outside the config module is empty; the test region moved without modification — compare against `git show 33f69df:…/config.rs`); quickstart §3 serde spot-set (config tests named, `Config::default()` debug-print diffed between trees); final sweep diff byte-identical.

**Checkpoint**: all three stories delivered.

---

## Phase 6: Polish & Final Verification

- [ ] T010 Final: quickstart §5 review sweep (zero guard copies; no validator crosses its section; catch-all gone; three files contain exactly what data-model.md says); `cargo fmt --all` + `cargo clippy --workspace --all-targets -- -D warnings`; fill every quickstart "Record" block; delete `examples/config_sweep.rs` from the branch tree and remove the baseline worktree; mark BACKLOG "Refactoring targets" item 3 shipped; mark all tasks `[X]` here.

---

## Dependencies & Execution Order

- T001 → T002 (harness before baseline capture) → everything.
- US1 (T003→T005), US2 (T006→T007), US3 (T008→T009) strictly sequential — one file (then one module) throughout; the story order is the safe layering (tables inside the file, dissolve, split last).
- T010 last.

### Parallel Opportunities

None, honestly — a single-file-then-single-module refactor with checkpoint discipline. The sweep harness (T001) is the only independent artifact and everything depends on it.

## Implementation Strategy

US1 is the MVP: the one-row property is the payoff that compounds with
every future tunable, and it lands even in the unsplit file. Each story
ends at a sweep-verified checkpoint, so stopping after any story leaves
the tree green and strictly better. The sweep runs at every checkpoint
(T002 self-consistency, T004, T007, T009) — the enumerated instrument is
cheap once built, so it runs often.
