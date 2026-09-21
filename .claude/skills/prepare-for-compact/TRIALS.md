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

## Trial 3 — Experiments thread, Fable, 2026-09-21

First run on the skill at 6e12ec6, the version with the consumer side
written. State carried: tier 6 of the beam-world screen collected and
first-read, write-up owed; three declaration and guard SHAs; a
five-item read command; poisoned raw dirs; four owner rulings by
quote; one promise to the owner ("Full write-up follows"). The skill
ran twice before the compact (once by the thread, once invoked by the
owner); the second run changed only the stamp.

Resume went in the skill's order. Freshness stamp passed: origin/main
still 6e12ec6, stamp 18:12Z equal to the file's mtime. Every exact
string re-verified against git and the filesystem: the four SHAs
resolve to the commits the anchor names, both done markers match the
log tails byte for byte, the raw and poisoned paths exist, no driver
process alive. The anchor's next-action line and the summary's next
step agreed word for word, because the summary quoted the anchor. No
gaps found. Zero items were summary-only.

Two things this trial could not test:

- **The training-shaped card never ran live.** stage6 and the meow
  legs both finished hours before the compact, so the card on file
  read `None running` and the alive-vs-dead test, the re-arm line and
  the child-kill order were not exercised.
- **Step 5 was not exercised.** Nothing arrived between the report and
  the compact. The owner's ask ("Report on skill efficacy?") landed
  after the compact and was answerable from the anchor's authorization
  line ("the compact trial here").

Confirmed again: the summary's injected git-status block was stale
(its "recent commits" ended at 945933a, weeks behind). The anchor's
"never trust a SHA written here" rule and the fetch-first resume order
are what caught it. One reading note: the memory system's `modified`
field on the anchor read 08:23Z while the body stamp read 18:12Z; the
body stamp was right (mtime agrees) and the frontmatter field lags,
which is the noise SKILL.md already names.

**Patched by**: nothing. A live training card and a step-5 arrival
remain untested; the next Experiments compact with a driver running is
the trial for those.
