# Implementation Plan: evals/v3 — the four wide exams re-cut at roster 5

**Branch**: `051-evals-v3` | **Date**: 2026-09-05 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/051-evals-v3/spec.md` (3 user stories, 12 FRs (FR-012 ruled in 2026-09-05), 8 SCs; owner ruled the rosters 2026-09-04; three clarifications 2026-09-05; the plan-time correction in §Problem).

## Summary

A new frozen suite directory `evals/v3` beside the untouched `evals/v2`: `scale` and the three `mixed-roster` cells re-cut at roster 5 (the v2 seats 1–5, `playful` at seat 2, compositions 1+4 / 2+3 / 4+1), `scarcity` and `heterogeneity` carried with re-cut headers, a manifest with fresh hashes and the same derived thresholds (11 / 10 / 6, sign-test k 10). Every test that reached v2 through the one helper in `eval_suite.rs` retargets to v3; v2 joins the sweep exclusions and the sweep guard flips; the usage string, README, `docs/rl-training.md`, the 017 manifest contract and CHANGELOG point at v3.

**The plan-time finding (research R1)** reshapes the guard, not the deliverable: the wide v2 exams do not refuse a served-width mind — the suite binds the subject against compiled-default observation config and the friend-row builder truncates a wider roster silently, so the oracle artifact scored all six v2 exams blind to 3 of 7 friends on `scale`. v3 at roster 5 is still the fix (every roster now fits 4 slots). The standing guard therefore asserts roster fit (roster ≤ slots + 1) for every v3 exam and runs a served-width fixture through the load path plus a short scored run; pointed at v2 it goes red on exactly the four wide exams. FR-012, the suite refusing a policy subject that cannot seat an exam's roster, is the loud failure everyone believed existed — one check at the subject seam, ruled IN by the owner 2026-09-05.

## Technical Context

**Language/Version**: Rust, toolchain pinned by `rust-toolchain.toml` (no change). TOML exam files. No Python change.

**Primary Dependencies**: `cloudkitty-rl` only — `evals/v3/*` (new files), `tests/eval_suite.rs` (retarget + one new guard), `tests/shipped_configs_rl.rs` (the sweep assertion), `src/bin/kitty-eval.rs` (usage string), and `src/suite.rs` (FR-012). `cloudkitty-core`, `cloudkitty-server`, `cloudkitty-py`: no change.

**Storage**: none. No snapshot, wire, artifact or schema move. Six new committed TOMLs plus a manifest.

**Testing**: `cargo test --workspace --no-fail-fast` via `scratchpad/cycle.sh LABEL` (repoint the script to `~/ai/cloudkitty-evals` first; baseline re-read at cycle 0 — main moved to 30eb469 after the branch point, merge `origin/main` in before cycle 0), fmt + clippy CI-exact, red-first per CLAUDE.md rule 5 recorded in `redden-list.md`.

**Target Platform**: unchanged. Nothing deploys; the suite is read by the step-7 seating smoke.

**Project Type**: Rust workspace; config-file deliverable with test retargeting.

**Performance Goals**: the new guard adds a roster-fit assertion (no ticks) plus six load-and-short-run passes at a few hundred ticks each — single-digit seconds against the ~80 s suite. The exams' own 10-seed × 20,000-tick schedule is never run in CI (Clarification Q1).

**Constraints**: `evals/v2` byte-untouched (spec 017 FR-012; the 049 §s1 lesson); manifest hashes written LAST over final bytes; `sign_test*` keys above `[verdict.least_happy_threshold]`; the carried exams' parsed configs equal v2's; no test weakened; `experiments/` untouched.

**Scale/Scope**: 7 new files under `evals/v3/`, 2 test files edited (one new test function), 1 usage string, 1 exclusions line, 4 docs/records (README, rl-training, 017 contract, CHANGELOG), 1 annotation in the 049 spec, the redden list; plus one ~15-line check in `suite.rs` with its unit test (FR-012).

## Constitution Check

*GATE: evaluated pre-Phase-0 and re-checked post-design — PASS, no violations.*

- **Article I–III**: every v3 exam is a lawful world under the same validation as the served config; the safeguard spawner is active in exam runs (spec 017 FR-006); rosters 4 and 5 satisfy Article III; the invariant-asserted run guard (FR-005) covers each file. PASS.
- **Article IV**: the suite still only seats advisors; FR-012 refuses a subject at binding time, before any proposal — a loader-level refusal, not a rule change. PASS.
- **Article V**: no draw order or tick order touched; the exams are configs; determinism guards (two runs identical JSON) retarget unchanged. PASS.
- **Article VI**: spec-first; the suite version is frozen by hash and guarded in CI; thresholds derive from the manifest by the existing tests, never folklore. PASS.

**Complexity Tracking**: no violations to justify.

## Project Structure

### Documentation (this feature)

```text
specs/051-evals-v3/
├── spec.md              # 3 US / 12 FRs (FR-012 ruled in) / 8 SCs; §Clarifications 2026-09-05; plan-time correction
├── plan.md              # This file
├── research.md          # Phase 0: R1 the finding, R2–R9 design decisions
├── data-model.md        # Phase 1: suite version, exam, roster width, record suite
├── quickstart.md        # Phase 1: validation guide (guards, the red-first runs, the full-horizon invocation)
├── contracts/
│   └── evals-v3.md      # the seven files' identity, the manifest constants, the guard, the pointers
├── checklists/requirements.md
├── redden-list.md       # implementation-time red-first record (house standard)
└── tasks.md             # Phase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
evals/v3/                          # NEW, frozen at landing (hashes last)
├── manifest.toml                  # version eval-suite-v3; thresholds guest 11 / half 10 / host 6; k 10;
│                                  #   comment: the plan-time finding + why roster 5
├── scale.toml                     # 48×48, v2 ids 1–5 at corners + centre, elements unscaled, kitty_slots 4
├── mixed-roster-guest.toml        # 28×28, v2 seats 1–5; 1 candidate (id 1) + playful (2) + 3 needs_driven
├── mixed-roster-half.toml         #   2 candidates (1, 3) + playful (2) + 2 needs_driven (4, 5)
├── mixed-roster-host.toml         #   4 candidates (1, 3, 4, 5) + playful (2)
├── scarcity.toml                  # carried: header re-cut, body values identical, stale notes corrected if any
└── heterogeneity.toml             # carried: same

crates/cloudkitty-rl/
├── tests/eval_suite.rs            # evals_v2() → evals_v3() (one helper) + V2_EXAM_FILES → V3_EXAM_FILES;
│                                  #   NEW a_served_width_mind_sits_every_exam (roster fit + load + short run);
│                                  #   NEW carried_exams_parse_equal_to_v2 (scarcity/heterogeneity vs evals/v2);
│                                  #   distinctness guard += served geometry/roster axis
├── tests/shipped_configs_rl.rs    # "frozen exams are in the sweep" → evals/v3 (must go red when v2 is excluded)
├── src/bin/kitty-eval.rs          # usage string → evals/v3
└── src/suite.rs                   # FR-012 (ruled in): roster-fit refusal at the policy-subject seam + unit test

config-sweep-exclusions.txt        # += evals/v2 (the 2026-09-03 3.0 cut; four wide exams predate the roster-width ruling)
README.md                          # repo map + example → evals/v3
docs/rl-training.md                # example → v3; the two stale "a new evals/v2" sentences corrected
specs/017-eval-suite/contracts/suite-manifest.md   # evolution note names v3 as current
specs/049-fog-gen1/spec.md         # one annotation at §the 3.0 wall: v2 → v3 for Gen 1 certification (spec 051)
CHANGELOG.md                       # Unreleased one-liner (no compatibility marker: nothing trained or saved moves)
```

**Structure Decision**: a config-file deliverable inside the existing suite layout (`evals/<version>/`), guarded by the existing test file. No new crate, module or binary. The one engine touch (FR-012) lives where the suite already binds subjects.

## Phase 0 → research.md; Phase 1 → data-model.md, contracts/evals-v3.md, quickstart.md

See the sibling files. Post-design constitution re-check: PASS (nothing in Phase 1 introduced a mechanic; the exams are worlds the constitution already governs).
