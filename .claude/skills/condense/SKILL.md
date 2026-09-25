---
name: "condense"
description: "Apply a condense pass to a tracked file that owes one under the growth budget: compress wording, never facts; verify with a fresh-context fact-loss check; log the pass so the budget base resets."
compatibility: "CloudKitty threads (THREADS.md); assumes .claude/CONDENSE-LOG.md and scripts/condense-budget.sh"
metadata:
  author: "cloudkitty"
user-invocable: true
disable-model-invocation: false
---

# Condense

`/condense <file>` — run by the OWNING thread when a file owes a pass
under the growth budget (`scripts/condense-budget.sh`,
`.claude/CONDENSE-LOG.md`). A pass makes the file smaller without
making it say less: wording compresses, facts do not. (Owner ruled
the policy 2026-09-24.)

Ownership (THREADS.md §1): this file is Harness's — edits route
there. `TRIALS.md` beside it is append-shared: the thread that runs a
pass appends a section, clean or not.

## Who runs a pass, on whose word

The owning thread condenses its own file, never a peer's. Authority:

- **Tier 1** (CLAUDE.md, THREADS.md, the prepare-for-compact skill):
  a gate block goes to the owner FIRST; the pass starts on her word
  and she rules on the diff before it merges — these files are her
  ruleset, in her voice.
- **Tier 2**: a thread blocked by the gate mid-arc may run the pass
  at once to unblock, as its own reviewable commit, never folded
  into the arc's changes. An advisory (`T2_ADVISE`) is not a block:
  flag it, run the pass at the thread's next natural pause.
- A pass never starts on a thread's own initiative with no gate
  signal, and never on a peer's relay.
- **Frozen files** (the log's `## Frozen` list) are never condensed —
  frozen means no edits at all; their budget is zero by design.

## The never-cut list

These survive the pass EXACTLY — never summarized, never paraphrased:

1. Owner rulings and her verbatim quotes, with their dates.
2. Key design decisions and the reasoning required to reproduce an
   experimental arc — including decisions the owner delegated to the
   owning thread, which no ruling or quote covers (owner,
   2026-09-24). The test: could a fresh session re-run the arc and
   understand why each choice was made, from the condensed text plus
   the files it points to?
3. F-numbers, issue numbers, SHAs, dates, paths.
4. Every number, at its printed precision.

Everything else is wording, and wording compresses. A fact whose home
is another file (THREADS.md §6) may become a pointer to that home —
that is deduplication, not loss.

## Delete in place — git history is the archive

Superseded material comes OUT; the pass commit's message names what
came out and why it is superseded. No new ARCHIVE files — an archive
is where growth hides, and every new file would need a §6 home
ruling. The one standing exception: `experiments/FINDINGS-ARCHIVE.md`
already exists and keeps its role for retired findings (owner,
2026-09-24); a FINDINGS pass may still move a retired entry there
under that file's own rules.

## Verification — the fact-loss check

Before the PR opens (tier 2) or goes to the owner (tier 1): one
subagent, fresh context, given the OLD text and the NEW text and the
never-cut list above — never this skill's fixture answer key, never
the session's reasons for each cut. It lists every fact in the old
text not recoverable from the new text plus the files the new text
points to, each with the old sentence quoted. The pass is clean only
when that list is empty; anything on it goes back into the file or
is defended to the owner by name. The subagent's report is evidence
the owning thread reads (CLAUDE.md rule 9), never a verdict to
paste.

## Mechanics of landing a pass

Two commits, in order:

1. The pass itself — one file, nothing else in the commit.
2. The log line — append to `.claude/CONDENSE-LOG.md` `## Passes`:
   `- YYYY-MM-DD <sha of commit 1> <file>: <what came out, one
   clause> (PR #N)`. Commit 1's SHA is what the budget script reads
   as the new growth base once the PR merges.

Then `scripts/condense-budget.sh --report` in the worktree to
confirm the file's growth reads from the new base.

## The fixture (rule 5)

`fixture/original.md` is the real F-050 FINDINGS entry;
`fixture/condensed-planted.md` is a condense of it with three
planted losses — one per never-cut category that can be dropped
silently (an owner caveat, the mechanism reasoning, a changed
number); `fixture/expected-findings.md` names them and stays out of
the checker's context. Running the fact-loss check on the pair must
list exactly those three — predict that in writing before the run.
Re-run the fixture on every edit to this skill that changes what the
check catches; a real pass that loses a fact the check missed
becomes a new plant.
