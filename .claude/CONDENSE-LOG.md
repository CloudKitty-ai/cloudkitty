# Condense log

The reset points for the growth budget in `scripts/condense-budget.sh`
(THREADS.md §1, Harness; owner ruled 2026-09-22, per-tier bases
2026-09-25). The budget is accumulation since the last pass, never a
stamp: net lines added to each tier's files from that tier's base to
the commit under test. A tier's base is the newest pass line naming a
file in that tier; a line naming no tiered file (the founding line)
resets every tier.

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
  `client/BACKLOG.md` (owner 2026-09-28: "Client backlog same tier
  as main backlog"),
  `policies/purrsonality.md`, and each thread's `TRAPS.md` once it
  exists
- skill `TRIALS.md` files: unmetered during shakeout, frozen at its
  close (owner ruled 2026-09-25; the condense SKILL.md §TRIALS
  lifetime carries the rule)
- tier 3, report only: every other markdown file under `experiments/`
- outside the budget: `CHANGELOG.md` (a human record; growth is not a
  concern), `specs/`, `docs/`
- frozen: budget zero, blocking, from the SHA on its line

## Passes

One line each: `- <date> <hash> <file>: <what> (PR #n)`. The hash on
a new line is the condensed file's blob hash (`git rev-parse
HEAD:<file>` at the pass commit) — it names content, so it survives
any merge style (owner ruled 2026-09-25); a commit SHA also resolves,
which keeps the founding line valid.

- 2026-09-22 b50fc2c budgets set; no pass applied (PR #411)
- 2026-09-28 ea29098dfa24 BACKLOG.md: viewer entries split out to client/BACKLOG.md, −1502 lines (PR #435; logged by #437 so the split is not a −1500 tier-2 credit that hides real growth. Whether client/BACKLOG.md joins tier 2 is an open owner call)
- 2026-09-28 0c0db2642601 THREADS.md: accuracy-gate definition and the hook inventory deduped to their homes (hooks README new, §6 row); wording tightened; residual +49 of THREADS' growth is kept rulings, re-baselined under the owner's ruling on the diff (PR #439)
- 2026-10-28 67b66f1c7534 experiments/FINDINGS.md: three moves on the owner's rulings of 2026-10-28 — (1) a wording pass, −41; (2) the Gen 1-cold split: 19 active pre-fog entries no Gen 2 arc cites moved verbatim to experiments/FINDINGS-COLD.md (stubs + tagged index rows stay; status unchanged; the cold file is TIER 2 by her ruling, its scripts/condense-budget.sh entry is Harness's, pending in their lane, so until then the cold file is unmetered and this line resets the tier past the move); (3) the §6 pass: 16 number-dense entries brought to the claim shape, numbers whose home is the cited RESULTS pointed to, F-064..F-070 given one-sentence headings; FINDINGS 3,748 → 2,353 lines, 259 → 166 KB; residual growth kept: none in FINDINGS (net −501 against the old base 4a9349bb; the cold file holds moved text, not growth); the reset also swallows .claude/TRAPS.md +56, DESIGN-DOCTRINE +59, GEN2-INPUTS +42, README +7, BACKLOG −17 (PR #482)

## Frozen

One line each: `- <path> @ <sha of the freezing commit>`.
- experiments/fog-gen1-timeline-2026-08-26.md @ 48af87d
- .claude/skills/condense/TRIALS.md @ 347c50f9
