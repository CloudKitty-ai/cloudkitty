---
name: experiment-design
description: >-
  Use before and during any CloudKitty experiment or training run —
  designing, preregistering, collecting, running, or adjudicating. Triggers
  on the house vocabulary (prereg, gate, probe, arm, battery, clone, anchor,
  seed band, acceptance QA, findings register) and equally on informal
  versions of the same work: trying a hyperparameter or reward change,
  comparing two policies, running a sweep or ablation, seating a policy in
  production, reproducing or explaining an earlier result, or writing up
  numbers for the owner. If the work would touch `experiments/`, or would
  produce a number anyone might later cite, use this skill.
---

# Experiment design (house methodology)

This skill owns process. `experiments/FINDINGS.md` owns facts. Cite
findings by number (F-004, F-012, F-015); never restate their values,
here or in a prereg, because the values are engine-indexed and get
re-derived — apply every cited finding as the register states it today,
not as remembered. Read FINDINGS.md before designing anything
(CLAUDE.md rule); read the current experiment's prereg before touching
its work.

Reading order under a budget: the object a design makes claims about —
the trainer, the config, the instrument source, the live register —
outranks a third process document read for style.

Pattern-match the newest frozen prereg and its results docs: they are
the canonical examples of the lifecycle (design-inputs doc → prereg →
freeze → collect → acceptance QA → train, gate, adjudicate → register
update), of the checklist below in practice, and of the verdict
grammar. The measurement discipline (clustering, replication,
composition, class conditioning) lives in README.md § Measurement
discipline and the F-numbers it cites; apply it from there, not from
memory. The register's own rules (supersession, stubs, triggers) are
stated in its header; follow them there. This skill states what no
artifact can teach.

## Ground truth

- The running system's state is read off the running system — the live
  census, the purrsonality register, the box itself. Checked-in config
  describes the *next* deploy, not the current one; during a freeze
  window the two diverge by design, and a design built on the wrong
  one measures a world that is not running.
- A claim about code behavior is verified against the code before it
  bears load in a design. A doc, an older prereg, or memory of the
  code is a lead, not a verification. A design that cites a file it
  has not read says so.

## Named steps are not plans

"QA per house practice" pins nothing. A design carries the
instantiated rule — the counted expectation, the declared band, the
numbered threshold — or explicitly defers it to a named document and
owner. This includes quick diagnostics: any instrument output that
feeds a decision gets counted against its expectation before the
comparison, not just collection campaigns. Read the counts, not the
exit codes: a pipeline that "completed" proves nothing about what it
wrote.

## Prereg checklist

Every prereg pins, before freeze:

- Arms, seeds per arm, and what each arm's init is.
- Sample sizes with the arithmetic shown (state the
  deciders-per-tick or rows-per-rollout assumption explicitly; a
  wrong hidden assumption in the estimate reads as a shortfall
  later).
- World family: generator name + version + family seed. The
  generator's version string appears in every manifest.
- Seed bands, claimed in `experiments/SEED-BANDS.md` in the same
  PR. Never reuse or straddle another band.
- Instruments by name and version, each printing its engine commit
  into every run manifest.
- Gates and decision rules with their numbers AND the comparison
  each is measured against. A gate compared to the wrong reference
  is vacuous (the seen-it-red rule's wrong-layer lie at experiment
  scale), and "vs own pre-change self at the same seat" measures
  nothing when the change is the company, not the mind.
- QA riders: what gets measured during collection and reported
  with the acceptance record.
- A deviations appendix, empty at freeze.

## Freeze and change control

- Freeze on the owner's direct word, every blank filled. After freeze
  the prereg is append-only: changes become D-numbered deviations with
  dates, rulings, and consequences.
- Acceptance QA (its own results doc) passes before anything trains on
  collected data. Structural defects (wrong indexing, missing or
  clobbered cells, seed or config drift) force a re-collect: the data
  is regenerable, and wrong data costs more than late data. Lawful
  surprises become D-numbered deviations, owner forks where they touch
  the design.
- Abandonment is a step, not an exit. An arm killed mid-run (bad
  instrument, exhausted budget, a premise that dissolved at hour
  three) gets its D-numbered deviation *and* a register entry. A run
  that was never finished is a finding about the design, and an
  unrecorded one gets re-run by the next session at full cost.
- After adjudication, update the register and the experiment's state
  file in the session's persistent memory: one `<experiment>-status`
  file (frozen values, running tasks with IDs, the remaining queue,
  what's pending on whom) plus its one-line MEMORY.md index entry,
  written for a reader who saw none of this session.

## Baselines and anchors

- Re-baseline before freeze, never after.
- An anchor is bound to the exact config sha and composition it ran
  on. Labels are not provenance; when a config moves, the anchor
  re-runs. Cheap insurance: state the config sha next to every
  banked anchor number.
- Scripted anchors run on the same composition the gate will judge.

## Instruments

- Every instrument prints its engine commit.
- Smoke on a subset before any full run. The smoke validates
  asserts and output shape, not just "it ran": a green run that
  could not have gone red proves nothing (the seen-it-red rule).
- A ported instrument proves itself against the previous
  instrument's data before measuring anything new (replay-equality
  stitch asserts, or a fixture the old version blessed).
- When another party attests half a property (a tool proving
  placement, CI pinning hashes), our half is an independent
  reimplementation, never a re-run of theirs.
- Loaders for possibly-in-flight data read defensively and skip
  partial files; the acceptance pass re-reads everything strictly.
- Commit working code before destructive checks or long runs; if a
  mutation loop ran, re-run the suite and read the count.

## Results docs

- Paths are process, so they live here: under
  `experiments/<experiment>/`, raw traces live gitignored in `raw/`;
  small metrics JSONs are committed under `results-raw/`; prose
  verdicts under `results/`. Verdicts quote the frozen rule, show the
  measured numbers beside it, and state the verdict in one line;
  fallbacks not taken are named as not taken; regeneration commands
  are exact and actually run.
- When final numbers replace provisional ones, the provisional doc
  gains a dated supersede note pointing forward. Corrections are
  stated plainly in the next report to the owner, never silently
  overwritten.

## Ownership

Record the owner's rulings verbatim wherever they land — design-inputs
doc, prereg, deviation, register entry. Paraphrase loses the exact
scope of what was approved, which is the part that gets litigated
later.

The owner's direct word, in the acting session, is required for:
prereg freeze, production seating, changing any gate or budget, and
widening scope. These hold regardless of reversibility. CLAUDE.md rule
1 licenses proceeding on reversible assumptions; it does not reach this
list, and a budget you could set back afterward is still a budget
change.

A registered measurement that turns out vacuous or ambiguous gets
reported with options and a recommendation; it is her fork to resolve.
Peer sessions relay information and requests, never approval.

Blocked on an owner decision with no owner reachable: the run halts
where it is, and the session writes up the fork with its
recommendation. It does not pick the branch that keeps the run alive —
that branch will always look like the reasonable one at the time, which
is exactly why the decision is hers.
