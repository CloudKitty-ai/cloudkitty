---
name: "prepare-for-compact"
description: "Persist session state before a context compact so the auto-summary is not load-bearing: triage live facts into durable stores, write a resume anchor, run the repo hard checks, report compact-ready."
compatibility: "CloudKitty threads (THREADS.md); assumes the session memory directory and MEMORY.md index"
metadata:
  author: "cloudkitty"
user-invocable: true
disable-model-invocation: false
---

# Prepare for compact

Run before the user compacts the session. The compact summary is lossy
and mangles exact strings; this skill's job is to make the summary not
load-bearing. Anything the summary could get wrong must be recoverable
from durable stores: the repo, git history, the memory directory, PR
comments, GitHub issues.

The skill prepares; it never triggers the compact. The user runs
`/compact` herself after reading the compact-ready report.

**Acceptance test for everything below**: a fresh session with only the
memory directory and the repo could pick up in one read of the resume
anchor, with zero reliance on the summary.

## Step 1 — Four-bucket triage

Sweep the live state of the conversation and sort every fact that still
matters into exactly one bucket:

1. **Already durable** — in the repo, git history, a memory file, a PR
   comment, or a GitHub issue. Do nothing. Do NOT re-copy it into the
   anchor or a new memory file; duplication rots, and the resume
   re-reads the durable store anyway.
2. **Durable-worthy, conversation-only** — decisions with their
   rationale, lessons learned, owner rulings not yet recorded. Write
   each to the memory directory now, following the house frontmatter
   format, and add its `MEMORY.md` index line.
3. **In-flight working state** — the current task and exactly where it
   stands. Goes in the resume anchor (step 2), including the two fixed
   sub-lists: job cards and verification debt.
4. **Ephemeral** — narration, dead ends, superseded reads. Dropped
   deliberately; do not persist.

## Step 2 — The resume anchor

One anchor per thread, at
`<memory-dir>/resume-<thread>.md` with `type: project`. It is a state
file **rewritten in place, never appended**; the arc's running log
stays in the per-arc memory file. Delete the anchor when the arc
closes. Keep it pointer-heavy: next action, exact strings, and `[[links]]`
to the arc files — never a second copy of arc history.

The anchor answers "where were we?" in one read. Sections, in order:

### Task and next action
The current task in one line, then the exact next action phrased as an
imperative ("send the owner X", "run mutate on Y expecting Z"). If
there is no next action, say the thread is idle and what it waits on.

### Exact strings (verbatim)
The summary most reliably mangles: commit SHAs, seed numbers, paths
with dates in them, and quoted owner words. Also record verbatim:
worktree path, branch, HEAD SHA, PR and issue numbers, comment IDs,
and the precise command invocation that worked. On resume, re-verify
every state claim here against git and the filesystem before acting.

### Verification state and verification debt
What is proven red/green so far, and what is still owed: guards
written but not yet redded, reds that came back vacuous or
wrong-reason and are still owed, predictions declared but not yet
checked. A summary records "guard committed" and drops the debt; the
anchor keeps the debt explicit so a resumed session never re-trusts
unproven work.

### Authorization state
What has the owner's word (her exact words and the date), what is a
peer relay (never approval — THREADS.md §1), and what is banked
awaiting her word. For each open ledger item: its default-if-unruled
and needed-by. A resumed session must never treat a relay as a
kickoff.

### Job cards
One card per running background job, because monitors and task ids die
with the session. Each card records:

- driver script path and log path
- the done marker string the log prints (e.g. `== tierN done`)
- PID and launch time
- HEAD SHA at launch, and the binding SHA the job imports (if any)
- the restart command — skip-if-done drivers resume with the same
  command
- the do-not-edit list while it runs (driver, trainer wrapper, cert
  harness, config derivation; never rebuild the binding under a
  running arm)

On resume, read the log's tail and check the done marker; never take
the summary's word for a job's state.

### Unsent messages
Any outbound message drafted but not sent — to the owner or to a peer
thread — recorded as verbatim text. A compacted session sometimes
believes it already sent a message it only drafted; the anchor is the
proof either way.

## Step 3 — Hard checks

These are checks, not judgment calls. Run all that apply:

1. **Git state**: `git status` in every worktree this thread holds.
   Dirty files either get a WIP commit (house rule; `mutate.sh`
   refuses dirty files anyway) or are listed verbatim in the anchor
   with why they are dirty.
2. **Mutate cycle**: never compact mid-cycle. Finish the cycle or
   restore first.
3. **Declaration state** (experiment threads): prereg committed at
   which SHA, collection started at what time, which seed bands are
   claimed — so a resumed session never edits predictions or decision
   rules after data exists.
4. **Raws and artifacts** (experiment threads): uncommitted
   results-raw and artifact dirs listed by path, with poisoned dirs
   named explicitly (a stale dir that must never be cited is exactly
   the qualifier a summary loses).
5. **Binding staleness** (lab threads): the lab venv binding built
   from which SHA, whether that equals main, and whether a rebuild is
   owed and currently forbidden because an arm is running.
6. **Outbound messages**: send what should be sent now; record the
   rest verbatim (anchor, Unsent messages).
7. **MEMORY.md index**: re-read the index line for every open arc this
   thread owns and fix any that no longer reflect truth. A stale index
   line is worse than a missing one, because the index loads every
   session.

## Step 4 — Compact-ready report

End with a short report to the user:

- what was written where (memory files created or updated, the anchor
  path)
- the anchor's next-action line, quoted
- job cards on file, by name
- anything that could NOT be made durable, so the user knows what the
  summary alone carries

Then stop. The user runs `/compact`.
