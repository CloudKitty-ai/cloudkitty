# Research: Held-Out Evaluation Suite (spec 017)

Phase 0 decisions. Each entry: Decision / Rationale / Alternatives
considered. All NEEDS CLARIFICATION items from the Technical Context are
resolved here (there were none outstanding — the spec's Clarifications
settled mode, location, verdict doctrine, and seat binding; this file
settles mechanics).

## R1 — Suite orchestration lives in a new `suite` module behind a `--suite` flag

**Decision**: `kitty-eval --suite evals/v1 (--artifact PATH | --brain NAME)
[--json out.json]`. The flag names the suite *directory*; the manifest is
`manifest.toml` inside it. `--suite` is mutually exclusive with `--config`,
`--seeds`, `--ticks`, and `--roster` — a suite is a fixed instrument, and
its per-exam seeds/ticks are frozen in each exam's own `[rl.eval]` block.
Orchestration, metrics, verdict, and report types live in a new
`crates/cloudkitty-rl/src/suite.rs`; `kitty-eval.rs` gains one branch.

**Rationale**: the spec's Clarifications chose the mode over a wrapper; a
module keeps the binary thin and the machinery unit-testable. Rejecting
`--seeds`/`--ticks` under `--suite` keeps exam identity frozen —
exploratory runs still have a first-class escape hatch: point `--config` at
any exam file directly (the existing single-config path, unchanged).

**Alternatives considered**: manifest path as the flag value (directory is
friendlier and leaves the manifest name as a convention); allowing CLI
seed overrides with a "non-canonical" marker in the report (complexity to
support a use the single-config path already serves).

## R2 — Freeze is a manifest of SHA-256 hashes, verified twice

**Decision**: `manifest.toml` records, per member file, its SHA-256 (the
same `sha2` hasher the policy artifact loader already uses). Verification
happens (a) at suite startup — a mismatch is a usage/validation failure
(exit 1) naming the file — and (b) in CI, by a plain `cargo test` in
`tests/eval_suite.rs` that walks every `evals/*/manifest.toml`, recomputes
hashes, and asserts equality. Landing a suite version = committing the
exam files plus the manifest carrying their hashes.

**Rationale**: SC-003 demands the freeze be demonstrated by test, not
policy. Putting the guard in the workspace test suite makes the existing
required CI gate enforce it with zero workflow changes. Runtime
verification additionally protects local runs from accidentally-edited
working copies producing quietly non-canonical scores.

**Alternatives considered**: git-history enforcement in CI (fragile,
workflow-coupled); hashing the whole directory (a per-file hash names the
offending file, which the guarding test and exit-1 message both want).

## R3 — Composition cells are three frozen sibling files

**Decision**: the mixed-roster exam is three configs —
`mixed-roster-{guest,half,host}.toml` — identical except the `behavior`
field of each `[[kitty]]` entry. A guarding test parses all three and
asserts they are equal in every respect *except* behaviors (geometry,
positions, needs, elements, reward — all identical), so the cells can
never drift apart.

**Rationale**: the owner's seat-binding convention says composition lives
in the config (`behavior = "policy:candidate"` marks a seat). Three files
express three compositions exactly, stay human-readable, and freeze under
R2 like any exam. The drift risk of near-identical siblings is closed by
test, not by a generator.

**Alternatives considered**: one config plus seat lists in the manifest
(splits composition across two files, diluting the convention); runtime
seat rewriting from cell specs (reintroduces the roster-rewrite machinery
R5 avoids and makes the frozen file not what actually runs).

## R4 — Candidate binding is a registry registration; the baseline is a mechanical rewrite

**Decision**: at suite invocation the harness registers the subject under
the exact name `policy:candidate` in the `BehaviorRegistry` — for
`--artifact`, the loaded `PolicyBehavior` (same validation as today); for
`--brain`, the named built-in's `Arc` under the alias. The all-scripted
baseline for each cell is derived mechanically: clone the cell config and
rewrite every `behavior == "policy:candidate"` to `"needs_driven"`,
leaving scripted seats (including `playful`) untouched.

**Rationale**: registry names are plain strings and `kitty-eval` already
registers artifacts under computed names (`policy:{path}`), so binding is
one `register` call — no engine or config change. Deriving the baseline
mechanically makes baseline-vs-cell drift impossible; a fourth committed
baseline file could disagree with its cells. The `--brain` alias is what
makes SC-007 (exam executable with no trained artifact) true, and
`playful`-as-candidate is the machinery's own independent test. Outside a
suite run the placeholder stays an ordinary policy name that fails loudly
at startup — `Config::validate()` does not check behavior names;
`validate_behavior_names(known)` is registry-aware, verified in
`cloudkitty-core/src/config.rs:1251`.

**Alternatives considered**: binding via a synthetic `[rl.policy.candidate]`
config entry (couples the frozen file to artifact paths — exactly what the
convention forbids); a committed all-scripted fourth file (drift risk, R3).

## R5 — Cells run through the existing harness with `subject: None`

**Decision**: composition cells reuse `run_one` exactly as it stands:
`EvalRequest { subject: None, .. }` already runs the config's roster
verbatim (`harness.rs:37` — "None scores the config's own roster
unchanged"). No `RosterMode` extension, no roster rewriting, no new run
path. Standard exams (scale, scarcity, heterogeneity) reuse the existing
subject/roster/baseline flow unchanged, per exam config.

**Rationale**: the harness was built with this door open. One runner
remains the single implementation of an evaluation run (the same DRY
doctrine as spec 014 FR-002); the suite composes it rather than forking it.

**Alternatives considered**: `RosterMode::Seats(Vec<KittyId>)` (dead
weight — the config already expresses seats via the placeholder).

## R6 — Metrics: an observer hook, and suite-side accumulation

**Decision**: `harness.rs` gains
`run_one_with(request, observer: impl FnMut(&World))`, called once per
tick after the tick completes; `run_one` delegates with a no-op observer
(behavior byte-identical, SC-004). The suite uses the observer to
accumulate, per kitty: duet-participation ticks (ticks where
`Kitty::partner()` is `Some` — `kitty.rs:110`), reported as a share of the
run. Guest-welfare differentials come from data the harness already
reports: per-kitty `mean_happiness` in `WelfareReport.kitties`, cell vs
all-scripted baseline, paired per seed then averaged. Least-happy identity
counts come from the same per-kitty means. Nothing is added to
`WelfareReport` itself — it is shared with the constitutional CI gate and
stays untouched.

**Rationale**: the spec's secondary reads ride existing recorded state; the
observer is the smallest additive hook that exposes it without a second
run loop or a change to the shared welfare module.

**Alternatives considered**: extending `WelfareReport` (touches the CI
gate's surface for a suite-only need); duplicating the run loop in
`suite.rs` (two implementations of "an evaluation run").

## R7 — Verdict operationalization

**Decision**: the mixed-roster verdict (spec FR-010) evaluates, per cell,
over the exam's frozen seed set:

1. **Aggregate check**: seed-mean `team_welfare` of the cell ≥ seed-mean
   `team_welfare` of its all-scripted baseline (paired per seed; per-seed
   deltas reported).
2. **Differential check**: the cell's guest-welfare differential — mean
   over seeds and over *scripted* kitties of (cell `mean_happiness` −
   baseline `mean_happiness`) — must be ≥ `-differential_tolerance`
   (manifest constant, default `0.0`; per-kitty differentials all
   reported).
3. **Identity check**: the count of seeds in which the least-happy kitty
   is a scripted (out-group) member must be < the cell's
   `least_happy_threshold` (manifest constant): the smallest k with
   P(Binomial(n_seeds, out_group_share) ≥ k) ≤ `tail_probability` (a
   manifest constant, default 0.01). For v1's 10 seeds:
   guest (share 5/6) → 11, i.e. unattainable — the check cannot bind where
   chance alone makes the out-group least-happy most days; half (share
   3/6) → 10; host (share 1/6) → 6. Thresholds are stored in the manifest
   with this derivation in a comment, and a unit test recomputes them from
   the rule.

A failed check fails the exam; a negative host-cell differential with a
passing aggregate check is additionally reported as the named
**exploitation signature** (cell, kitty, differential). Duet-participation
shares are report-only in v1 — a diagnostic, not a gate.

**Rationale**: deterministic, closed-form, no statistics dependency; the
binomial rule honors "beyond what seed noise explains" while keeping every
number a committed constant. Tolerance defaults to exactly the spec's
`≥ 0`.

**Alternatives considered**: permutation tests (nondeterministic or
seed-hungry, and a dependency); gating on duet shares (the owner listed
them as secondary reads).

## R8 — Exit codes: 4 for verdict failure; mechanical failures dominate

**Decision**: exit 0 success; 1 usage/validation (including manifest hash
mismatch and exam validation failure); 2 any fallback-taken decision; 3
determinism self-check failure; **4 mixed-roster verdict failure** (new).
Precedence 1 > 2 > 3 > 4: a run that both takes a fallback and fails the
verdict exits 2 — a mechanical failure means the scores behind the verdict
aren't trustworthy anyway. Codes 2 and 3 keep their exact single-config
meanings (SC-004).

**Rationale**: scripting and CI want "measured and failed the exam"
distinguishable from "the measurement itself broke". The spec's
scores-not-bounds doctrine is preserved: exit 4 is anchored to the exam's
own baseline, never to the bar's bounds.

**Alternatives considered**: exit 0 with verdict only in the report
(US3 scenario 2 says the exam *fails*; an unscriptable verdict is a
verdict nobody automates).

## R9 — Determinism self-checks extend per exam and per cell

**Decision**: the existing first-seed re-run self-check runs per roster
mode per standard exam, and per cell (plus the baseline) for the
mixed-roster exam. Any disagreement → exit 3, naming the exam/cell.

**Rationale**: mixed-composition dispatch is a distinct code path by the
same argument that made per-mode self-checks worth having (spec 014 second
review).

## R10 — Exam world designs

**Decision**: full TOML designs in `contracts/exam-configs.md`, summarized:

- **scale.toml** — 48×48, 8 kitties (canon five + Mochi, Marmalade,
  Noodle), default rates, default element counts *not* scaled to the
  2.25× area: dilution and travel distance are the axis, and the safeguard
  guarantees relief. Differs from `cloudkitty48.toml` (which serves 4).
- **scarcity.toml** — default 32×32 geometry and canon roster; every
  element minimum at the validation floor (`hard_min`: greeble 0, all
  others 1; `config.rs:365`), maxima at floor+1. Contention is the axis.
- **heterogeneity.toml** — 32×32, 5 kitties, full per-kitty `[kitty.needs]`
  profiles spanning ≈0.05 to 2.0 (a 40× spread, vs. no overrides in the
  default world and a 2× top override in training.toml). Lawful (rates
  ≥ 0) and fully observable (trait encoding is `rate /
  reference_need_rate` = rate/1.0, clamped at 4.0 — nothing clips).
- **mixed-roster-{guest,half,host}.toml** — 28×28, 6 kitties (canon five +
  Mochi), default rates and near-default elements; seats per cell: guest =
  1 candidate + 4 needs_driven + 1 playful; half = 3 candidate +
  2 needs_driven + 1 playful; host = 5 candidate + 1 playful. The host
  cell's lone scripted cat is `playful` deliberately — maximum convention
  distance in the strongest probe.

Every exam pins `[rl.reward]` (p = 0.0, ε = 0.01, level) and `[rl.eval]`
(the 10 fixed CI seeds, 20,000 ticks) explicitly, so the frozen file fully
determines the measurement.

**Rationale**: each design differs from both `cloudkitty.toml` and
`training.toml` on its named axis (SC-005) and carries in-file rationale
(FR-005). Kitty names stay in the meadow's register; the owner can rename
in review without touching any number.

## R11 — Suite human report suppresses the bounds verdict on exam worlds

**Decision**: in suite mode, the per-run "welfare bounds: PASS/VIOLATED"
line is replaced by the welfare panel alone; bound values appear only in
the JSON under a `reference_bounds` key explicitly labeled as calibrated
to the default world. The single-config report is untouched.

**Rationale**: spec FR-003 — a scarcity-floor world lawfully scoring under
bounds calibrated elsewhere must not read as failing. The exam's meaning
is the paired delta; the report's shape should say so.

**Alternatives considered**: printing the verdict with a caveat (a caveat
next to a "VIOLATED" all-caps line loses to the all-caps line every time).
