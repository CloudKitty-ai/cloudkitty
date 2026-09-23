# Condense log

The reset points for the growth budget in `scripts/condense-budget.sh`
(THREADS.md §1, Harness; owner ruled 2026-09-22). The budget is
accumulation since the last pass, never a stamp: net lines added to
each tier's files from the SHA on the last pass line to the commit
under test.

Append rule: the PR that applies a condense pass appends its own line,
whichever thread owns the file; the commit that freezes a tracker
appends the frozen line. Harness edits the rest.

Tiers and budgets (net lines since the last pass):

- tier 1, blocking past +80: `CLAUDE.md`, `THREADS.md`,
  `.claude/skills/prepare-for-compact/SKILL.md`
- tier 2, advisory past +800, blocking past +2000:
  `experiments/FINDINGS.md`, `experiments/DESIGN-DOCTRINE.md`,
  `experiments/ROADMAP.md`, `experiments/README.md`,
  `experiments/fog-gen1-shakeout/GEN2-INPUTS.md`, `BACKLOG.md`,
  `policies/purrsonality.md`, the skill `TRIALS.md`, and each
  thread's `TRAPS.md` once it exists
- tier 3, report only: every other markdown file under `experiments/`
- outside the budget: `CHANGELOG.md` (a human record; growth is not a
  concern), `specs/`, `docs/`
- frozen: budget zero, blocking, from the SHA on its line

## Passes

One line each: `- <date> <origin/main sha> <what> (PR #n)`. The script
reads the SHA on the last line.

- 2026-09-22 b50fc2c budgets set; no pass applied (PR #TBD)

## Frozen

One line each: `- <path> @ <sha of the freezing commit>`.
- experiments/fog-gen1-timeline-2026-08-26.md @ 48af87d
