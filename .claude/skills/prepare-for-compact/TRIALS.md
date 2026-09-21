# Trial record

What each live trial of /prepare-for-compact dropped, and which change
patched it. Edits to SKILL.md check themselves against this file: the
skill is shaped by what actually failed, not what plausibly could.

This file is append-shared (THREADS.md §1, 2026-09-21): the thread
that delivers a gap report appends its own section and never touches
another thread's. Product and Client append through a worktree and a
PR; Experiments appends on main directly. A trial that drops nothing
still gets a section; a clean run is evidence too.

## Trial 1 — Product thread, Fable, 2026-09-20

First real compact after PR #402 merged the skill. The post-compact
session resumed from the anchor alone and reported one summary-only
item:

- **The owner's question sent after the compact-ready report.** She
  asked "Do I need to manually run the skill, or is letting a thread
  know to prepare for compact enough?" between the report and the
  /compact; the compact fired before the answer went out. The anchor
  said `Unsent messages: None` and was frozen before the question
  existed. Only the auto-summary carried it.

Everything else held: trial protocol, owner quotes, PR/SHA/comment
IDs, banked items, authorization state. Confirmed live: the summary's
injected git-status block was stale (pre-merge commits) — the
untrusted rule in the anchor's exact-strings section paid.

**Patched by**: PR #403 (step 5, Late arrivals) — a message landing
in the report→compact window makes the session not-ready until it is
answered or anchored.

## Trial 2 — Client thread, Opus, 2026-09-21

Heavier state: eight commits on a branch, two non-CI local suites,
seven scratchpad items, a live server port. The code plane held
completely — HEAD and commit order exact, suite counts (380, 94)
verbatim with SHA, four mutation reds and both vacuous-guard
incidents with failure strings, three banked owner calls, scratchpad
inventory intact. Five gaps, every one a dialogue obligation:

1. That a gap report was owed at all (the owner's ask was not a code
   task, so no bucket carried it).
2. The definition of the gap report (her wording).
3. That the ask was a re-ask, and how round 1 had been answered.
4. The session's own unanswered question to the owner (a shot.mjs
   relocation offer) — `Unsent messages: None` was wrong about it.
5. Minor: port 8795 was held by a foreign PID (91446), recorded
   nowhere.

**Patched by**: PR #404 — bucket 3 counts no-code obligations as
in-flight state; anchor section "Open with the owner" (asks verbatim
with re-ask history, asked-not-answered questions); server cards
record port ownership; the compact-ready report re-states questions
awaiting the owner's answer so she can close them before compacting.

## Design review — Experiments, 2026-09-21 (not a trial)

Feedback on the merged skill at 52971b1, before their first real run:
the consumer side was unwritten (nothing durable told the post-compact
session to read the anchor before the summary's "next step" — both
trials passed only because the summary happened to repeat the
mandate); the dialogue ledger had no peers entry; job cards restored
the job but not its monitor; and this record did not exist.

**Landed as**: the "After the compact" section, the "Open with peers"
ledger line, the watch re-arm card line, the `## Resume` section at
the top of MEMORY.md, and this file.

Experiments' first real run — with the stage6 overnight job as the
training-shaped card — is the next trial.
