# experiments/ — the lab notebook

Research artifacts for training and studying CloudKitty policies live here,
separated from the product codebase on purpose.

## The governance rule

- `crates/` (and `client/`, the server, `evals/`) are **product**:
  constitution-guarded, spec-first (Article VI), welfare-gated in CI.
- `experiments/` is **trainer territory** (the carve-out spec 014's research
  R11 established: training configs and tooling remain the trainer's). No
  specs required, no constitutional CI gates, free to iterate.
- **The dependency arrow points one way.** Code here may depend on
  `crates/`; nothing in `crates/`, the server, or the client may ever
  import from `experiments/`.

Certification assets are product, not experiments — `evals/<version>/`,
`kitty-eval`, and `docs/rl-training.md` stay where they are. Exam-suite
configs are frozen and versioned; nothing here may train on them.

## Layout

- `PIPELINE.md` — the policy pipeline as default doctrine: stages,
  gates (§9.2 stress / §9.3 welfare), seed-band ledger, certification
  battery, seating and soak protocol, with diagrams. Preregs
  re-register the gates per experiment and, once frozen, win over it.
- `FINDINGS.md` — the findings register: distilled, generalizable
  conclusions with statuses, scope, evidence links, and standing
  re-verification triggers. Pre-registrations MUST cite the F-ids they
  rely on. Read it before designing any experiment or training run.
- `tools/` — shared across experiments: the twin probe, config generators,
  analysis scripts. One directory per tool.
- `exp-NNN-slug/` — one directory per experiment, holding everything that
  experiment produced: `prereg.md` (frozen at first run; deviations go in
  its appendix), `figures/`, `results/`, and a manifest tying each result
  to code commit + config hash + artifact hash + seeds.
- Raw outputs (JSONL traces, rollout dumps) live in `raw/` subdirectories,
  which are gitignored. Commit pre-registrations, manifests, and final
  figures; never commit bulk data or build output.

## Measurement discipline (promoted findings)

Operating defaults graduated from the findings register; the F-ids are
the provenance and carry the evidence and history. These bind every
measurement in this directory — screens, probes, preregs.

- **Cluster by world; replicate on disjoint worlds (F-004).** Any
  across-sample statistic over rollout-derived traces uses
  cluster-robust per-world means (`tools/world-search/search.py`'s
  `channel_metrics` is the reference implementation); ranking
  differences under ~2× must replicate on disjoint worlds before anyone
  acts on them. The minimum world count is engine-dependent and lives
  in F-004's entry, not here — re-derive it after engine changes.
- **Declare what the instrument holds fixed (F-009).** Every
  criteria.md / prereg measurement section states the dimensions its
  instrument holds fixed — **horizon, world, roster, seed band,
  selection mode** — and the claim inherits those bounds. A zero on one
  seed band is a property of policy × world × band, not of the policy.
  When a shorter or cheaper instrument is used for economy, record what
  it cannot see and gate the decision on the full-length instrument.
- **Measure social behavior in the deployment composition (F-012).**
  Solo and homogeneous probes under-count company-dependent behavior;
  the lesson has since re-confirmed at the dial level (F-023: channel
  dials are listener-population properties) and the welfare level
  (F-025: cultured policies' welfare tracks their audience). Any
  channel-use, welfare, or certification claim names the composition it
  was measured in, and selection/certification measurements run in the
  composition that will actually be seated.

## Design discipline

Working rules for designing and running anything here. Relocated from
the retired `experiment-design` skill (2026-08-19) after a blind A/B
spot-check kept only what measurably earned its place. The lifecycle,
the prereg checklist, and the verdict grammar need no restating: the
preregs and results docs in this directory are their canonical
examples — pattern-match the newest frozen prereg rather than working
from memory.

- **The running system's state is read off the running system.** The
  live state is banked in `policies/purrsonality.md` (seatings,
  censuses, welfare reads); when the box itself is out of reach, that
  file is the ground truth — never checked-in config, which describes
  the *next* deploy, not the current one. During a freeze window the
  two diverge by design, and a design built on the wrong one measures
  a world that is not running.
- **Code claims are verified against the code.** A claim about code
  behavior is verified against the code before it bears load in a
  design. A doc, an older prereg, or memory of the code is a lead, not
  a verification. A design that cites a file it has not read says so.
- **Reading order under a budget:** the object a design makes claims
  about — the trainer, the config, the instrument source, the live
  register — outranks a third process document read for style.
- **Named steps are not plans.** "QA per house practice" pins nothing.
  A design carries the instantiated rule — the counted expectation,
  the declared band, the numbered threshold — or explicitly defers it
  to a named document and owner. This includes quick diagnostics: any
  instrument output that feeds a decision gets counted against its
  expectation before the comparison, not just collection campaigns.
  Read the counts, not the exit codes: a pipeline that "completed"
  proves nothing about what it wrote.
- **Commit working code before destructive checks or long runs.** If a
  mutation loop ran, re-run the suite and read the count.

## Ownership

Record the owner's rulings verbatim wherever they land — design-inputs
doc, prereg, deviation, register entry. Paraphrase loses the exact
scope of what was approved, which is the part that gets litigated
later.

The owner's direct word, in the acting session, is required for:
prereg freeze, production seating, changing any gate or budget, and
widening scope. These hold regardless of reversibility. CLAUDE.md rule
1 licenses proceeding on reversible assumptions; it does not reach
this list, and a budget you could set back afterward is still a budget
change.

A registered measurement that turns out vacuous or ambiguous gets
reported with options and a recommendation; it is the owner's fork to
resolve. Peer sessions relay information and requests, never approval.

Blocked on an owner decision with no owner reachable: the run halts
where it is, and the session writes up the fork with its
recommendation. It does not pick the branch that keeps the run alive —
that branch will always look like the reasonable one at the time,
which is exactly why the decision is the owner's.

## Build relationship

Rust tools here are standalone cargo packages (each carries its own empty
`[workspace]` table) that path-depend on `crates/`. They are deliberately
**not** workspace members: product CI never builds research code, and
`cargo test --workspace` stays exactly as fast and as green as the product
makes it. The non-blocking `experiments` CI job builds `tools/` so engine
API drift gets noticed without ever gating a product change.
