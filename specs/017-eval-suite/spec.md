# Feature Specification: Held-Out Evaluation Suite

**Feature Branch**: `017-eval-suite`

**Created**: 2026-07-24

**Status**: Draft

**Input**: Owner-directed follow-on from the 2026-07-24 RL advisory session:
extend the evaluation story so the harness can score a policy across a suite
of committed, frozen exam configs **in addition to** — never instead of —
default-world certification. The settled decisions carried into this spec:
the default world is not toughened (it is the product, and the constitutional
CI gate is calibrated there); the measurement need is met by held-out exams
instead; objective semantics (Nash reward, p = 0, ε = 0.01, full constitution
during training) are untouchable; the config-family generator is trainer-layer
tooling and expressly **not** part of this feature.

## One bar, many exams

The repository's evaluation doctrine is deliberately narrow: `kitty-eval`
certifies on the **default world only** — "the training world is a gym, not
the bar." That narrowness is a strength (the bar is the product, and its
welfare bounds are calibrated to it) and a blind spot: a single world cannot
discriminate between two policies that both clear it, and a policy trained on
one gym can overfit that gym's geometry without anyone noticing until the
served meadow feels subtly wrong.

The remedy is the discipline every trained model already lives by, applied to
worlds: **train / validate / test**. The training world is the gym. The
default world is the bar. This feature adds the exam room — a small suite of
fixed, committed, versioned worlds the policy never trains on, each built to
probe one axis the gym and the bar share no leverage over: scale, scarcity,
trait heterogeneity, and partner composition. Exams never import the bar's
verdicts: the default world remains the sole certification bar, and nothing
in this feature implies its calibrated welfare bounds apply to worlds they
were never calibrated for. What an exam measures is relative — the policy
against a scripted baseline, paired seed by seed, on ground neither has
seen; where an exam renders a verdict of its own (the mixed-roster exam's
pass shape, FR-010), that verdict is anchored to the same scripted baseline,
never to the bar's bounds.

Frozen means frozen. A landed suite version is immutable — its files
mechanically guarded against edits — because an exam that shifts under a
policy's feet measures nothing. When an exam saturates (every policy aces
it), it is not sharpened; a new suite version lands *alongside*, and the old
version stays runnable and reported so results remain comparable across the
project's whole history.

## Clarifications

### Session 2026-07-24

- Q: Is suite support a `kitty-eval` mode or a thin wrapper invoking it per
  config? → A: A `kitty-eval` mode. The harness already accepts `--config`,
  and every per-exam obligation (roster modes, paired baseline, fallback
  accounting, determinism self-check, JSON report) is machinery the binary
  already owns; a wrapper would re-implement report aggregation and exit
  semantics outside the tested surface. One binary, one report shape.
- Q: Where do exam configs live — the repo-root convention
  (`cloudkitty*.toml`) or a dedicated directory? → A: A dedicated `evals/`
  directory, one subdirectory per suite version (e.g., `evals/v1/`), with
  the manifest beside the exams. The root convention is for served worlds; a
  suite version is four-plus files with a freeze boundary, and a directory
  *is* that boundary. **Confirmed by the owner, 2026-07-24.**
- Q: Do exams carry pass/fail thresholds of their own? → A: No absolute
  welfare bounds, ever — those belong to the bar. Three of the four v1 exams
  report scores and paired baseline deltas only; the mixed-roster exam alone
  renders a verdict, and that verdict is *relative*, anchored to its own
  all-scripted baseline (FR-010) — a comparison, not a bound. Mechanical
  failures (config invalid, fallback taken, determinism broken) fail any
  exam.
- Q: How does a frozen exam config name a policy seat, when exams must be
  committed before any particular artifact exists? → A: Seat-binding
  convention (owner-specified, 2026-07-24): exam configs mark policy seats
  with the placeholder `behavior = "policy:candidate"`, and the harness
  binds `candidate` to whatever artifact is under test at invocation
  (FR-011). Composition is expressed precisely and frozen; no frozen file
  ever names an artifact — coupling the suite to one experiment is exactly
  the retrofit this convention exists to avoid.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A researcher scores a policy across the whole suite in one invocation (Priority: P1)

A researcher points the evaluation harness at a policy artifact and a suite
version and gets back, in one run: a per-exam scorecard (the same welfare
panel and paired `needs_driven` comparison a single-config run produces
today, on that exam's world) and a suite-level summary across exams. The
default-world certification path is untouched — the suite is an additional
question, asked the same way.

**Why this priority**: this is the mechanism everything else rides on, and it
is independently valuable the day it lands — even before any v1 exam exists,
it can sweep a policy across any set of lawful configs, which is exactly the
measurement gap the advisory session identified.

**Independent Test**: run the suite mode with `needs_driven` as the subject
over a directory of known configs; every exam's numbers must equal a
standalone harness run on that config with the same seeds, and the summary
must aggregate exactly those numbers.

**Acceptance Scenarios**:

1. **Given** a policy artifact and a named suite version, **When** the suite
   run is invoked, **Then** every exam in the suite is scored — standard
   exams in both roster modes, the mixed-roster exam by its composition
   cells, all paired against `needs_driven` on the same seeds — and the
   report presents each exam's scorecard plus a suite summary, in both human
   and JSON forms.
2. **Given** a suite containing an exam config that fails engine validation,
   **When** the suite run starts, **Then** the run fails before any scoring,
   naming the exam file and the offending field — no exam is silently
   skipped.
3. **Given** a policy whose inference panics on one exam, **When** the suite
   runs, **Then** the run reports which exam, which kitty, and the fallback
   count, and exits with the same failure code a single-config fallback
   produces today — the fallback's welfare is never reported as the
   policy's, on any world.
4. **Given** the same artifact and suite version run twice, **When** the two
   JSON reports are compared, **Then** they are identical.

---

### User Story 2 - The v1 exams probe what the gym and the bar cannot (Priority: P2)

An owner reads the committed v1 suite and finds three to four small worlds,
each documented with the one question it asks: a **scale exam** (a much
larger meadow and roster — does cooperation survive distance and crowds?), a
**scarcity exam** (element minimums at the lawful floor — does yielding
survive genuine contention?), a **heterogeneity exam** (an extreme lawful
trait spread — does fairness survive kitties with wildly different
metabolisms?), and a **mixed-roster exam** (compositions of policy and
scripted kitties seen in neither training nor certification — does
cooperation survive partners who don't share the policy's conventions? US3
gives this exam its full design). Every exam is a lawful world: validation
passes, the safeguard spawner runs, Article I holds — scarcity means walking
and yielding, never suffering.

**Why this priority**: the suite mode without discriminating content is an
empty exam room. The exams are the instrument.

**Independent Test**: each committed exam config passes engine validation and
sustains a multi-thousand-tick `needs_driven` run with zero invariant
violations; each differs from both the default world and the training world
on its named axis, verifiable by reading the configs.

**Acceptance Scenarios**:

1. **Given** the v1 suite, **When** its configs are validated and run
   headlessly under `needs_driven`, **Then** every exam constructs, runs its
   full horizon, and asserts every constitutional invariant throughout.
2. **Given** the v1 exams and the two non-exam worlds (default and
   training), **When** their configs are compared, **Then** each exam
   differs from both on its named axis, and no exam file is identical to any
   config a trainer trains on or the bar certifies on.
3. **Given** a reader of the suite directory, **When** they open any exam,
   **Then** the file itself documents what the exam probes and why its
   numbers are what they are.

---

### User Story 3 - A researcher catches a policy majority exploiting a scripted minority (Priority: P2)

A researcher scores a policy on the mixed-roster exam and reads three
composition cells — the policy as **guest** (one policy kitty among scripted
cats), **half-and-half**, and the policy as **host** (a policy majority with
one scripted cat) — each paired against an all-scripted run of the same
config and seeds. The report's discriminating number is the
**guest-welfare differential**: the scripted kitties' happiness with policy
neighbors versus with scripted neighbors. Positive means policy neighbors
make a scripted cat's life *better* — genuine cooperative surplus. Negative
in the host cell, under a healthy team Nash, is the exploitation signature:
a trained team cooperating beautifully with copies of itself while
structurally out-competing the one cat that doesn't anticipate its moves —
always first to the contested bowl, never conscripting the outsider into
duets, treating its meows as noise.

**Why this priority**: the Nash score counts the whole roster, scripted
kitties included, so this exploitation mode keeps team welfare respectable
while the scripted cat becomes the permanent least-happy member — and no
other metric in the suite catches it. Certification's existing mixed mode is
the *weak* direction (one policy kitty among scripted cats — the policy is
the guest); this exam probes the *strong* direction, the policy majority
hosting. It is the suite's held-out stress test for what the multi-agent
literature calls ad-hoc teamwork (Stone et al., 2010) and zero-shot
coordination: agents trained together develop implicit conventions — who
yields, who initiates duets, how meows get used — and cooperative
performance can collapse when a partner doesn't speak the dialect (the
fragility Hu et al.'s Other-Play (2020) documents; the engine mediates most
coordination here, so the milder form is what's live).

**Independent Test**: bind the candidate seat to a built-in brain (`playful`
is a genuinely different convention) and run the exam: all three cells and
the all-scripted baseline run on paired seeds, the report carries per-cell
aggregates, guest-welfare differentials, least-happy identity counts, and
duet-participation shares, and a verdict is rendered — no trained artifact
required.

**Acceptance Scenarios**:

1. **Given** a subject and the mixed-roster exam, **When** it is scored,
   **Then** all three composition cells and the all-scripted baseline run on
   paired seeds, and the report presents per-cell team aggregates, the
   guest-welfare differential per scripted kitty, least-happy identity
   counts per cell, and per-kitty duet-participation shares.
2. **Given** a host cell whose scripted kitty's differential is negative
   while the cell's team aggregate is healthy, **When** the verdict is
   rendered, **Then** the exam fails and the report names the exploitation
   signature explicitly — which cell, which kitty, what differential.
3. **Given** the candidate seat bound to a built-in behavior, **When** the
   exam runs, **Then** it completes end-to-end and renders a verdict — the
   machinery never requires a trained artifact.
4. **Given** two different artifacts scored against the same frozen exam,
   **When** both runs complete, **Then** no committed file differed between
   them — the artifact is bound at invocation, never named in the config.

---

### User Story 4 - Results stay comparable for the life of the project (Priority: P3)

A researcher comparing this month's policy against last quarter's runs both
against `eval-suite-v1` and trusts the comparison, because v1 is bit-for-bit
the suite it was the day it landed. When v1 saturates, `eval-suite-v2` lands
alongside it; reports name the suite version they were produced by; v1
remains runnable and reported.

**Why this priority**: freezing is what makes an exam an instrument rather
than a moving target — but it only matters once there are results worth
comparing across time.

**Independent Test**: modify any landed exam file in a working copy and run
the guard suite: the modification is detected and fails loudly.

**Acceptance Scenarios**:

1. **Given** a landed suite version, **When** any of its exam files is
   edited, **Then** an automated guard fails, naming the file — the freeze
   is enforced by machinery, not by convention.
2. **Given** two suite versions side by side, **When** either is invoked by
   name, **Then** it runs exactly its own exams and its report names the
   version.
3. **Given** a suite report, **When** it is read later, **Then** the suite
   version and every exam's identity are recorded in it.

---

### Edge Cases

- **An exam config that fails validation**: the suite run fails at startup,
  before any scoring, naming the exam file and field — the same loud-failure
  doctrine as server startup. A suite never silently runs a subset.
- **Default-world bounds on exam worlds**: the long-run welfare bounds
  (mean ≥ 70, streak limits, zero floor touches…) are calibrated to the
  default world. Exam scorecards MUST NOT present them as a pass/fail
  verdict — a scarcity-floor world may lawfully score below them while the
  policy is doing everything right. The exam's meaning is the paired
  baseline delta.
- **Roster size varies across exams**: the observation schema is
  roster-independent by design (spec 014); a policy artifact runs unmodified
  on a 4-kitty bar, a 5-kitty gym, and an 8-kitty scale exam. No exam may
  require a schema change.
- **A trainer trains on an exam**: mechanically undetectable — held-out is a
  doctrine, not a lock. The suite states it plainly: results claimed against
  a suite version are void if any of its exams appeared in training. The
  mechanical guarantee this feature *can* give is distinctness: no exam file
  equals a training or certification config.
- **Mixed roster mode on exam worlds**: the deployment-reality mode (one
  policy kitty among `needs_driven`) runs per **standard** exam exactly as
  on the default world — both roster modes are part of every standard exam's
  scorecard. The mixed-roster exam does not repeat them: its composition
  cells *subsume* roster variation — the guest cell **is** the
  deployment-reality composition, probed at richer compositions besides —
  with their own baseline and verdict (US3), not a rerun of certification's
  mode.
- **The exploitation signature**: a negative guest-welfare differential in
  the host cell under a healthy team Nash — team welfare respectable, the
  scripted cat permanently least-happy. No other metric in the suite catches
  it; the differential exists for exactly this case (FR-010).
- **The `policy:candidate` placeholder outside a suite run**: it is an
  ordinary policy behavior name. A served config using it without a
  configured `candidate` policy fails at startup naming the field, exactly
  like any unconfigured policy today — the placeholder is a harness-side
  binding convention, not a new engine concept.
- **Fallback or determinism failure mid-suite**: the run fails with the
  established exit semantics (fallback-taken and determinism-self-check
  failures are distinct, nonzero, and unchanged from single-config runs);
  the report says which exam produced the failure.
- **A saturated exam**: never edited, never retired from its version. A new
  suite version lands alongside; the old one stays runnable so historical
  results keep their meaning.
- **An empty or missing suite**: invoking a suite version that does not
  exist or contains no exams is a usage error, not an empty success.

## Requirements *(mandatory)*

### Functional Requirements

**The suite mode (US1)**

- **FR-001**: The evaluation harness MUST offer a suite mode that scores one
  subject (behavior name or policy artifact) across every exam in a named
  suite version, **in addition to** the existing single-config invocation,
  which MUST remain unchanged in behavior, report shape, and exit semantics.
  The default world remains the sole certification bar; suite output is
  measurement, and no suite result substitutes for default-world
  certification.
- **FR-002**: Each exam MUST be scored with the full per-config obligations
  the harness already owns — the paired same-seed `needs_driven` baseline
  comparison, fallback accounting (a nonzero fallback count fails the run),
  and the determinism self-check — on the budgetless headless path, per the
  standing doctrine (spec 014 FR-017). Standard exams additionally run both
  roster modes for a policy subject, exactly as certification does; the
  mixed-roster exam runs its composition cells instead (FR-008) — the cells
  subsume roster variation, the guest cell being the deployment-reality
  composition.
- **FR-003**: The suite report MUST present, per exam: the full long-run
  welfare panel the single-config report presents (mean happiness,
  low-happiness streaks and share, floor touches, pinned streaks, distress
  age), the configured team-welfare aggregate with the plain mean and the
  least-happy kitty's mean beside it, and the paired baseline deltas — plus
  a suite-level summary across exams. Human and JSON forms both. Exam
  scorecards MUST NOT present the default world's calibrated welfare bounds
  as a pass/fail verdict on exam worlds; where bound values are shown at
  all, they are labeled as reference context.
- **FR-004**: A suite run MUST fail before any scoring if any member exam
  fails engine validation, naming the exam file and offending field; and
  MUST fail with the established distinct exit semantics on fallback-taken
  decisions and determinism self-check failures, naming the exam that
  produced the failure. A suite run never silently skips an exam.

**The exams (US2)**

- **FR-005**: Suite v1 MUST comprise four committed exam configs covering
  these axes: **scale** (a world at least twice the default's tile
  count with a roster larger than any the policy trained with — the session
  recommendation is 48×48 with 8 kitties), **scarcity** (element minimums at
  the lawful floor the engine's own validation permits), **heterogeneity**
  (an extreme but lawful per-kitty trait spread), and **mixed-roster**
  (held-out compositions of policy and scripted seats — designed in full by
  FR-008 through FR-011). Exact TOML contents are plan-phase deliverables;
  each exam MUST document, in the file itself, what it probes and why its
  numbers are chosen.
- **FR-006**: Every exam MUST be a lawful world: it passes the same
  validation as any served config, and the full constitution — the safeguard
  spawner included — is active during exam runs. Scarcity and scale are
  expressed only through lawful configuration; no exam may relax an
  invariant to become hard.
- **FR-007**: No exam file may be identical to any config used for training
  or certification (the mechanical face of the held-out doctrine), and the
  suite's documentation MUST state the doctrine itself: results against a
  suite version are void if its exams were trained on.

**The mixed-roster exam (US3)**

- **FR-008**: The mixed-roster exam MUST hold out *composition*, not merely
  configuration: a geometry and roster that are neither the bar's nor the
  gym's (the session design: 28×28, roster of 6), scored as three
  composition cells on paired seeds — **guest** (one policy seat among
  scripted kitties), **half-and-half**, and **host** (a policy majority with
  a scripted minority). The scripted contingent MUST include at least one
  `playful` partner alongside `needs_driven`: `playful` follows a genuinely
  different convention (ignores needs below its comfort threshold, chases
  critters, conscripts playmates aggressively), and a policy robust only to
  `needs_driven` partners has demonstrated one memorized partner model, not
  partner-generality.
- **FR-009**: For the mixed-roster exam the harness MUST also run the
  **all-scripted baseline** — the same config and seeds with every seat
  scripted — and report, per cell: the **guest-welfare differential** (each
  scripted kitty's happiness with policy neighbors versus with scripted
  neighbors), least-happy identity counts (whether the least-happy kitty is
  systematically the out-group member — identity, not just value), and
  per-kitty duet-participation shares (derivable from the engine's recorded
  activity state; the plan derives them from per-tick partner observation —
  the same measure).
- **FR-010**: The mixed-roster exam's verdict MUST be anchored to its own
  all-scripted baseline, never to the default world's bounds. It passes
  when: no cell's paired team aggregate falls below the all-scripted
  baseline; the guest-welfare differential is ≥ 0 in every cell; and
  least-happy identity is not concentrated on the out-group beyond what seed
  noise explains. A negative host-cell differential under a healthy team
  aggregate is the exploitation signature this exam exists to catch, and the
  report MUST name it explicitly — cell, kitty, differential — when it
  appears.
- **FR-011**: Frozen exam configs MUST express policy seats
  artifact-agnostically: a policy seat is marked with the placeholder
  `behavior = "policy:candidate"`, and the harness binds `candidate` to the
  artifact under test at invocation. Composition is precise and frozen; no
  frozen file ever names an artifact. Outside a suite run, the placeholder
  resolves like any policy name — a config naming an unconfigured policy
  fails loudly at startup, exactly as today.

**Freeze and versioning (US4)**

- **FR-012**: A landed suite version is immutable: its exam files MUST be
  mechanically guarded (content identity recorded at landing and verified in
  CI) so that any edit to a landed exam fails loudly. Evolution happens only
  by landing a new suite version alongside; prior versions remain runnable
  and invocable by name.
- **FR-013**: Every suite report MUST record the suite version and the
  identity of each exam scored, so any result can be tied to exactly the
  worlds that produced it.

**Scope guard**

- **FR-014**: This feature MUST NOT change the engine, the bindings'
  training surface, the served world's semantics, the reward's objective
  semantics (Nash, p = 0, ε = 0.01, level mode — untouchable per the
  session's settled decisions), the default world's config, or the
  constitution; every new constant it introduces MUST live in configuration
  or the suite manifest with documented defaults (Article VI). The
  config-family generator remains trainer-layer tooling outside this
  feature's scope.

### Key Entities

- **Exam**: one committed, frozen world config plus its in-file rationale —
  a single question asked of every policy, identical for all time within its
  suite version.
- **Suite Version**: a named, immutable set of exams (`eval-suite-v1`, …);
  the unit of freezing, invocation, and historical comparability.
- **Suite Manifest**: the record of a suite version's membership and each
  exam's content identity — what the freeze guard verifies and reports cite.
- **Exam Scorecard**: one exam's results — welfare panel, team aggregate
  with plain mean and least-happy beside it, roster modes (standard exams)
  or composition cells (mixed-roster), paired baseline deltas, fallback and
  determinism accounting.
- **Composition Cell**: one seat arrangement of the mixed-roster exam —
  guest, half-and-half, or host — scored on paired seeds against the
  all-scripted baseline of the same config and seeds.
- **Guest-Welfare Differential**: a scripted kitty's happiness with policy
  neighbors minus its happiness with scripted neighbors, per cell — the
  mixed-roster exam's discriminating metric, positive when policy neighbors
  create cooperative surplus for a cat outside their conventions.
- **Candidate Seat**: a policy seat in a frozen exam config, marked
  `policy:candidate` and bound to the artifact under test at invocation —
  composition frozen, artifact free.
- **Suite Report**: the scorecards plus the cross-exam summary, stamped with
  the suite version; human and JSON forms.

## Constitutional compliance *(Articles I–VI)*

- **Article I (no suffering)**: exams are lawful worlds — validation,
  need clamps, the happiness floor, and the safeguard spawner all active.
  The scarcity exam's floor-level minimums are precisely the point at which
  the safeguard doctrine carries the weight: scarcity means kitties walk
  farther and yield more, never that relief stops existing. No exam may
  configure suffering into existence, because no lawful config can.
- **Article II (no death)**: untouched. Exams change world shape, never
  mechanics; no removal path exists to configure.
- **Article III (never alone)**: every exam passes the ≥ 2 kitty validation
  like any config; the scale and mixed-roster exams *grow* rosters.
- **Article IV (engine is the law)**: the suite scores through the same
  validate-everything harness path as today; fallback accounting keeps
  headless dispatch honest on every world, and a fallback-taken run fails
  rather than laundering the fallback's welfare into the policy's score.
- **Article V (server-authoritative, deterministic)**: suite runs are
  headless and budgetless like all evaluation; per-exam determinism
  self-checks extend the existing guarantee to every exam world; the served
  world and its server are untouched.
- **Article VI (spec-first, test-guarded, no magic numbers)**: this spec
  precedes all code; the guarding tests are named below and join CI; exam
  numbers live in committed config files whose in-file documentation is
  required (FR-005), and suite membership lives in the manifest — nothing
  hard-coded.

**Guarding tests (Article VI)**:

1. Suite-equals-parts: a suite run on `needs_driven` reproduces, exam by
   exam, the numbers of standalone single-config runs on the same seeds.
2. Freeze guard: any edit to a landed exam file fails CI, naming the file
   (SC-003).
3. Loud validation: a deliberately invalid exam config fails the suite run
   before scoring, naming file and field.
4. Report reproducibility: two suite runs of the same subject and version
   produce identical JSON.
5. Exam lawfulness: every v1 exam constructs and sustains a
   multi-thousand-tick invariant-asserted run.
6. Single-config compatibility: the existing `kitty-eval` invocation's
   behavior and exit codes are unchanged (existing harness tests keep
   passing, unmodified).
7. Mixed-roster machinery: with the candidate seat bound to a built-in
   brain, the exam runs all three cells plus the all-scripted baseline and
   renders a verdict; a constructed run whose host-cell differential is
   negative under a healthy team aggregate renders the exploitation-
   signature failure naming cell, kitty, and differential.
8. Seat binding: the same frozen mixed-roster config scores two different
   subjects with no committed file changing between runs.

**Amendment required: none.** The constitution stands at v1.2.0 and this
feature changes nothing in it.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: One invocation scores a subject across every exam in a named
  suite version and produces the per-exam scorecards and suite summary; with
  `needs_driven` as subject, every exam's numbers equal a standalone run on
  that config with the same seeds — zero aggregation drift.
- **SC-002**: Two suite runs of the same subject against the same suite
  version produce byte-identical JSON reports.
- **SC-003**: Modifying any landed exam file causes an automated failure
  naming the file — demonstrated by test, not policy.
- **SC-004**: The existing single-config evaluation path is byte-compatible:
  its report shape and exit codes are unchanged and its existing guarding
  tests pass unmodified.
- **SC-005**: Each v1 exam verifiably differs from both the default world
  and the training world on its named axis by inspection of the committed
  configs: the scale exam has ≥ 2× the default's tiles and a roster larger
  than training's; the scarcity exam's minimums sit at the validation
  floor; the heterogeneity exam's trait spread exceeds both other worlds';
  the mixed-roster exam's geometry, roster size, and composition cells
  appear in neither training nor certification.
- **SC-006**: Constitutional cleanliness — the constitution, engine, and
  default world config are untouched; zero new constants exist outside
  configuration or the suite manifest.
- **SC-007**: The mixed-roster exam is executable without any trained
  artifact: binding the candidate seat to a built-in brain produces the
  full three-cell report — differentials, least-happy identity counts,
  duet-participation shares — and a verdict, reproducibly (per SC-002).

## Assumptions

- **The suite lives beside the harness**: suite scoring is an extension of
  the existing evaluation binary (per the Clarifications), not a new
  surface; the work lands in the RL crate's harness layer.
- **Exam contents are plan-phase**: this spec fixes the axes, lawfulness,
  distinctness, and documentation requirements; the exact TOML numbers are
  designed in the plan and frozen at landing.
- **The mixed-roster exam is fair because training includes mixed-control
  episodes**: the training recipe deliberately exposes the policy to
  scripted partners in general — just never these compositions, this
  geometry, or these seeds. **Held-out refers to the configs, not the
  concept.** If a future experiment drops mixed-control training, this exam
  is expected to fail first and loudest — which is precisely the
  early-warning role a held-out suite member exists to play, not a defect
  in the exam.
- **No absolute exam-level bounds in v1**: three exams produce scores and
  paired deltas only; the mixed-roster exam's verdict is relative to its
  own all-scripted baseline (Clarifications, FR-010). The default world
  remains the only absolute bar.
- **Location confirmed**: exam configs live in a dedicated
  `evals/<version>/` directory with the manifest beside them
  (owner-confirmed, 2026-07-24).
- **Ask B resolved — no bindings change**: VectorEnv constructs N worlds
  from one config, and its batch geometry (observation length, agent set,
  state length) is derived from that config — per-world heterogeneous
  configs inside one batch would be incoherent for mixed rosters anyway. A
  trainer wanting a config family runs one VectorEnv per member. No
  bindings extension is specified, matching the session's
  "only if demonstrably painful" bar.
- **Ask C resolved — the generator is not spec-worthy**: config-family
  generation is trainer-layer tooling (R11 explicitly leaves training
  configs to the trainer), validated by construction against the engine.
  At most it earns a future section in `docs/rl-training.md`; it appears
  in this spec only as this exclusion.
- **Spec-only pass**: this document is the deliverable of the current pass;
  planning and task breakdown follow the standard spec-kit flow after owner
  review.
