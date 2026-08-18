---
name: experiment-design
description: Use when designing, preregistering, running, or adjudicating a CloudKitty experiment: preregs, gates, probes, datasets, baselines, clones, PPO arms, batteries, results docs, and findings-register updates.
---

# Experiment design (house methodology)

This skill owns process. `experiments/FINDINGS.md` owns facts.
Cite findings by number (F-004, F-012, F-015); never restate their
values here or in a prereg, because the values are engine-indexed
and get re-derived. Read FINDINGS.md before designing anything
(CLAUDE.md rule); read the current experiment's prereg before
touching its work.

## Lifecycle

1. Design-inputs doc: options and tradeoffs per decision, written
   for the owner to rule on. Record her rulings verbatim.
2. Prereg draft against the checklist below.
3. Freeze on the owner's direct word, every blank filled. After
   freeze the prereg is append-only: changes become D-numbered
   deviations with dates, rulings, and consequences.
4. Collect, then acceptance QA (its own results doc) before
   anything trains on the data.
5. Train, gate, adjudicate. Verdict docs quote the frozen rule they
   apply.
6. Update the register (new findings, fired-trigger annotations)
   and the session memory state file.

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
  is vacuous: "vs own pre-change self at the same seat" measures
  nothing when the change is the company, not the mind.
- QA riders: what gets measured during collection and reported
  with the acceptance record.
- A deviations appendix, empty at freeze.

## Statistics discipline

- Apply the current F-004 bar (world counts, truncated statistic)
  as the register states it today, not as remembered.
- No ranking, verdict, or status update leaves the analysis on a
  single batch. Disjoint-band replication first; this includes
  informal reporting to the owner, where a batch-A excursion
  narrated early reads as a result.
- Class-conditioned probes per F-015; pooled all-action reads are
  dilution, not signal.
- Measure in the deployment composition (F-012). A number measured
  in the wrong company describes a world that will not be served.
- Read the counts, not the exit codes. A pipeline that "completed"
  proves nothing about what it wrote; count output rows or dirs
  against the registered expectation.

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
  asserts and output shape, not just "it ran".
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

## Verdicts and results docs

- Quote the frozen rule, show the measured numbers beside it, state
  the verdict in one line. Fallbacks not taken are named as not
  taken.
- Exact regeneration commands, actually run, including any platform
  traps they hit.
- Raw traces live gitignored under `raw/`; small metrics JSONs are
  committed under `results-raw/`; prose verdicts under `results/`.
- When final numbers replace provisional ones, the provisional doc
  gains a dated supersede note pointing forward. Corrections are
  stated plainly in the next report to the owner, never silently
  overwritten.

## Register hygiene

- A new finding carries: evidence links, implications, what would
  invalidate it, and re-verify-when triggers.
- When a trigger fires, annotate the finding in place, dated, with
  a link to the re-measurement. Withdrawn claims stay visible with
  their withdrawal; the register records the excursion as well as
  the correction.

## Ownership

The owner's direct word, in the acting session, is required for:
prereg freeze, production seating, changing any gate or budget, and
widening scope. A registered measurement that turns out vacuous or
ambiguous gets reported with options and a recommendation; it is
her fork to resolve. Peer sessions relay information and requests,
never approval.
