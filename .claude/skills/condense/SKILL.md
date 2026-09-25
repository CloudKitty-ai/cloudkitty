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
- **Tier 2**: self-serve on either gate signal (owner, 2026-09-24:
  "self serve is fine for t2 advisory"). A thread blocked mid-arc
  runs the pass at once to unblock; an advisory (`T2_ADVISE`) is
  flagged and run at the thread's next natural pause. Either way the
  pass is its own reviewable commit, never folded into the arc's
  changes.
- A pass never starts on a thread's own initiative with no gate
  signal, and never on a peer's relay.
- **Frozen files** (the log's `## Frozen` list) are never condensed —
  frozen means no edits at all; their budget is zero by design.

## The never-cut list

These survive the pass EXACTLY — never summarized, never paraphrased:

1. Owner rulings and her verbatim quotes, with their dates.
2. In the owner's words (2026-09-24): "key design decisions and
   reasoning required to reproduce experimental arcs (I delegate
   some of that to Experiments and it wouldn't be covered under
   owner rulings/verbatim quotes)". The test: could a fresh session
   re-run the arc and understand why each choice was made, from the
   condensed text plus the files it points to?
3. F-numbers, issue numbers, SHAs, dates, paths.
4. Every number, at its printed precision.

Everything else is wording, and wording compresses. "Exactly" means
exactly in the fact's home: a fact whose §6 home is another file may
become a pointer to that home — that is deduplication, not loss, and
under §6 a ruling restated outside its home is itself a condense
cut.

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
subagent, fresh context, run in the NATIVE checkout (it judges
recoverability by following the new text's pointers, and a worktree
may be missing what they lead to). It gets the OLD document body and
the NEW document body — fixture or scaffolding comments stripped —
and the never-cut list above; never this skill's fixture answer key,
never the session's reasons for each cut. It lists every fact in the
old text not recoverable from the new text plus the files the new
text points to, each with the old sentence quoted. The pass is clean
only when that list is empty; anything on it goes back into the file
or is defended to the owner by name. The subagent's report is
evidence the owning thread reads (CLAUDE.md rule 9), never a verdict
to paste.

## Mechanics of landing a pass

The base is GLOBAL: the budget script measures every tier from the
one SHA on the log's last pass line, so any pass resets every
file's counter, not just the condensed file's. Two consequences,
both mandatory:

- Run `scripts/condense-budget.sh --report` BEFORE the pass. If any
  tier 1 file shows nonzero growth the pass would wipe, name it and
  its count in the pass PR's body — the owner sees what the reset
  swallows instead of losing the block silently.
- **The pass PR merges with a MERGE COMMIT, never squash or rebase.**
  The log names a branch commit; squash or rebase discards it, the
  base stops being an ancestor of HEAD, and every later PR's gate
  exits 3 repo-wide.

The landing order:

1. Commit the pass — one file, nothing else in the commit.
2. Run the fact-loss check (above); a loss means amending commit 1
   and re-checking.
3. Open the PR (tier 1: take the diff to the owner first).
4. Commit the log line — append to `.claude/CONDENSE-LOG.md`
   `## Passes`: `- YYYY-MM-DD <sha> <file>: <what came out, one
   clause> (PR #N)`, where `<sha>` is the LAST commit in the PR that
   touches the condensed file. If review changes the pass after
   this, the fix and the updated log SHA land in one commit.

After merge, `scripts/condense-budget.sh --report` on main confirms
growth reads from the new base.

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
