# Implementation Plan: Held-Out Evaluation Suite

**Branch**: `017-eval-suite` | **Date**: 2026-07-24 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/017-eval-suite/spec.md`

## Summary

Extend `kitty-eval` with a `--suite` mode that scores one subject across a
manifest of committed, frozen exam configs — four v1 exams (scale, scarcity,
heterogeneity, mixed-roster) living in `evals/v1/` — in addition to, never
instead of, default-world certification. The mixed-roster exam runs three
composition-cell configs (guest / half-and-half / host, expressed with the
`policy:candidate` seat placeholder) against an all-scripted baseline and
renders the suite's only verdict: the guest-welfare-differential pass shape,
anchored to that baseline. Freeze is enforced by SHA-256 hashes recorded in
the manifest and verified both at suite startup and by a CI test.

The load-bearing simplification (research.md R5): `EvalRequest` with
`subject: None` already runs a config's roster verbatim, so composition
cells need no roster-rewriting machinery — a cell is just a frozen config
run as-is, with `policy:candidate` bound in the `BehaviorRegistry` at
invocation. The harness core gains only a per-tick observer hook (for duet
participation) and a mechanical `candidate → needs_driven` rewrite for the
all-scripted baseline. Everything else is a new `suite` module beside the
existing harness, plus the exam files themselves.

## Technical Context

**Language/Version**: Rust, stable toolchain, 2021 edition (existing
workspace — no change)

**Primary Dependencies**: none new. `serde`/`toml` (config + manifest
parsing) and `sha2` (freeze hashes) are already dependencies of
`cloudkitty-rl`; `sha2` is the same hasher the policy artifact loader uses.

**Storage**: committed TOML files (`evals/v1/*.toml` + `manifest.toml`);
JSON report output via the existing `--json` flag. No databases, no runtime
persistence — episodes remain ephemeral.

**Testing**: `cargo test --workspace` (existing CI gate). New guarding
tests land in `crates/cloudkitty-rl/tests/eval_suite.rs` plus unit tests in
the new `suite` module.

**Target Platform**: same as `kitty-eval` today — developer machines
(macOS) and CI (ubuntu-latest). Headless only; the server is untouched.

**Project Type**: CLI extension + library module in the existing
`cloudkitty-rl` crate, plus committed data files.

**Performance Goals**: a full v1 suite run with a built-in subject
completes in single-digit minutes on the reference machine (dominated by
the scale exam's 2.25× tile count and 8-kitty roster; per-exam
seeds/ticks are frozen in each exam's own `[rl.eval]` block, so cost is a
landing-time decision, not a runtime surprise).

**Constraints**: byte-identical JSON across repeat runs (SC-002); the
existing single-config invocation byte-compatible in report and exit codes
(SC-004); exit codes 2 (fallback) and 3 (determinism) keep their meaning,
with new exit 4 for a mixed-roster verdict failure — mechanical failures
take precedence over verdict failures.

**Scale/Scope**: one new module (`suite.rs`, orchestration + report +
verdict), one CLI flag branch in `kitty-eval.rs`, two small additive hooks
in `harness.rs`, seven committed TOML files, one new test file. The
engine, bindings, episode/vector machinery, reward, and welfare modules
are untouched (the welfare module is shared with the CI gate — additive
suite metrics live suite-side, not in `WelfareReport`).

## Constitution Check

*GATE: evaluated against constitution v1.2.0 — PASS, pre- and post-design.*

- **Article I (no suffering)**: no engine change. Every exam config passes
  the same `Config::validate()` as a served world; the safeguard spawner
  and need clamps are active in every exam run. The scarcity exam sits at
  the validation floor *because* the floor is lawful — guarding test 5
  (exam lawfulness smoke runs) demonstrates it, and the property-based
  invariant suite is untouched.
- **Article II (no death)**: untouched. Exams vary world shape only.
- **Article III (never alone)**: every exam config passes the ≥ 2 kitty
  validation; the smallest exam roster is 4.
- **Article IV (engine is the law)**: no behavior or dispatch changes. The
  `policy:candidate` binding is a `BehaviorRegistry` registration — the
  same mechanism `kitty-eval` uses for artifacts today. Fallback accounting
  and its exit-2 doctrine extend unchanged to every exam run.
- **Article V (server-authoritative, deterministic)**: headless, budgetless
  runs throughout; the existing per-mode determinism self-check extends
  per-exam and per-cell. The server and served world are untouched.
- **Article VI (spec-first, test-guarded, no magic numbers)**: spec merged
  before this plan; the eight guarding tests named in the spec map to
  concrete tests (quickstart.md); every constant lives in committed config —
  exam numbers in the exam TOMLs (with in-file rationale, FR-005),
  seeds/ticks in each exam's `[rl.eval]`, verdict thresholds and hashes in
  the manifest with derivation comments.

No violations; Complexity Tracking is empty.

## Project Structure

### Documentation (this feature)

```text
specs/017-eval-suite/
├── plan.md              # This file
├── research.md          # Phase 0: decisions R1–R11
├── data-model.md        # Phase 1: manifest/report/verdict entities
├── quickstart.md        # Phase 1: validation guide
├── contracts/
│   ├── suite-cli.md     # invocation, exit codes, report schemas
│   ├── suite-manifest.md# manifest TOML schema + freeze doctrine
│   └── exam-configs.md  # the four exam worlds: full TOML designs
└── tasks.md             # Phase 2 (/speckit-tasks — not created here)
```

### Source Code (repository root)

```text
evals/
└── v1/
    ├── manifest.toml            # suite version, members, hashes, verdict constants
    ├── scale.toml               # 48×48, 8 kitties
    ├── scarcity.toml            # default geometry, minimums at the validation floor
    ├── heterogeneity.toml       # 5 kitties, extreme lawful trait spread
    ├── mixed-roster-guest.toml  # 28×28/6: 1 candidate + 5 scripted
    ├── mixed-roster-half.toml   # 28×28/6: 3 candidate + 3 scripted
    └── mixed-roster-host.toml   # 28×28/6: 5 candidate + 1 scripted (playful)

crates/cloudkitty-rl/
├── src/
│   ├── suite.rs                 # NEW: manifest, orchestration, metrics, verdict, report
│   ├── harness.rs               # +run_one_with (per-tick observer); +unbind helper
│   └── bin/kitty-eval.rs        # +--suite flag branch; exit code 4
└── tests/
    └── eval_suite.rs            # NEW: guarding tests 1–8 (incl. the freeze-hash CI guard)
```

**Structure Decision**: everything lands in `cloudkitty-rl` beside the
harness it extends — the suite is evaluation-layer by definition (spec
FR-014 forbids engine/bindings changes). Exam data is repository-root
`evals/<version>/` per the owner-confirmed location; the freeze-hash CI
guard lives with the other harness tests so `cargo test --workspace` (the
existing required gate) enforces immutability with no CI-workflow changes.

## Complexity Tracking

No constitutional violations to justify.
