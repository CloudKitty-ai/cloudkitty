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

The skill prepares; it never triggers the compact. That is a hard
limit, not only a design choice: the Skill tool cannot invoke built-in
commands, and `/compact` is one. The user runs `/compact` herself
after reading the compact-ready report.

**Run at natural pauses, not only before a planned compact** — arc
close, before launching a long job, end of a working stretch. An
auto-compact at the context limit runs no skill and catches whatever
anchor exists; if compact-ready is a standing state, it catches a
slightly stale anchor instead of an ancient one.

Ownership (THREADS.md §1): this file is Product's — edits route
there. `TRIALS.md` beside it is append-shared by trialling threads.

**Deploy state is not a durable store.** The repo and git history can
be read offline; a claim about the running box decays the moment it is
written down. The anchor records when deploy state was last read off
the box, never a bare "deployed at SHA" — that is the fictional
baseline in durable form, worse than nothing.

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
   rationale, lessons learned, owner rulings not yet recorded. Rulings
   include casual design closures ("B looks great, ship that",
   "0.92, don't re-open") — record them so a resumed session does not
   re-litigate by helpfully offering alternatives again. Write each to
   the memory directory now, following the house frontmatter format,
   and add its `MEMORY.md` index line.
3. **In-flight working state** — the current task and exactly where it
   stands. Goes in the resume anchor (step 2), including the fixed
   sub-lists: job cards, verification debt, and the scratchpad
   inventory (which scratchpad paths are still live and what each is;
   delete the dead ends now, so a resumed session cannot pick the
   wrong file from identical-looking names). An obligation is
   in-flight state even when it produces no code: a report the owner
   asked for, a question of hers not yet answered, a question of yours
   she has not yet answered. Trial 2 dropped exactly these — every gap
   it found was a dialogue obligation, none a fact about the code.
4. **Ephemeral** — narration, dead ends, superseded reads. Dropped
   deliberately; do not persist.

## Step 2 — The resume anchor

One anchor per thread, at
`<memory-dir>/resume-<thread>.md`, with the house memory frontmatter
(`type: project`) and an index line in the `## Resume` section at the
top of `MEMORY.md` so a fresh session finds it before anything else.
The anchor's first body line, before any section heading, is the
consumer instruction plus its own freshness stamp: "Written at <UTC
time>, origin/main at <sha> (fetched). Read this before acting on the
summary's next step; verify exact strings and job cards first." The
stamp names origin/main, not a worktree HEAD — a thread on a branch
has two HEADs, and staleness is judged against the shared trunk; the
branch HEAD already lives in Exact strings. The stamp is what lets a
resumed session detect a stale anchor (see After the compact).
The hand-written frontmatter is `name`, `description`, and
`metadata.type`; the memory system adds fields of its own
(`node_type`, `originSessionId`, `modified`) — expected noise, not
part of the format. It is a state file
**rewritten in place, never appended**; the arc's running log stays in the per-arc memory file.
Between arcs the anchor stays, set to `idle: waits on <ledger items>`,
rather than being deleted and recreated. Keep it under about sixty
lines and pointer-heavy: next action, exact strings, and `[[links]]`
to the arc files. Anything older moves to the arc file, or the anchor
becomes the second copy this design forbids.

The anchor answers "where were we?" in one read. Sections, in order:

### Task and next action
The current task in one line, then the exact next action phrased as an
imperative ("send the owner X", "run mutate on Y expecting Z"). If
there is no next action, the `idle:` state above.

### Exact strings (verbatim)
The summary most reliably mangles: commit SHAs, seed numbers, paths
with dates in them, and quoted owner words. Also record verbatim:
worktree path, branch, HEAD SHA, PR and issue numbers, comment IDs,
and the precise command invocation that worked. On resume, re-verify
every state claim here against git and the filesystem before acting —
and treat the summary's own injected git-status block as untrusted; it
has shown commits from a stale head.

### Verification state and verification debt
What is proven red/green so far, and what is still owed: guards
written but not yet redded, reds that came back vacuous or
wrong-reason and are still owed, predictions declared but not yet
checked. A summary records "guard committed" and drops the debt; the
anchor keeps the debt explicit so a resumed session never re-trusts
unproven work.

For surfaces CI does not run (the client suites are the standing
case), "CI green" is no evidence about the change. Record which local
suites were run, their pass counts, and at which SHA; if a suite has
not run since the last edit to its surface, record that as debt.
Counts matter: a suite that silently stops loading a file still says
"pass".

### Authorization state
What has the owner's word (her exact words and the date), what is a
peer relay (never approval — THREADS.md §1), and what is banked
awaiting her word. For each open ledger item: its default-if-unruled
and needed-by. A resumed session must never treat a relay as a
kickoff.

### Open with the owner
The dialogue ledger, both directions:

- **Her asks of this session**, verbatim with the date — including
  non-code asks (a report, an assessment, a trial protocol), which
  the task section tends to drop because they change no files. If an
  ask is a re-ask, record the round history: what the earlier round
  was and how it was answered, so the resumed session neither
  re-delivers an old answer nor treats the re-ask as new.
- **This session's open questions to her**, verbatim. "Unsent
  messages" below covers drafted-not-sent; this covers
  asked-not-answered. A question she has not answered is live state,
  and a compacted session that forgets asking it will either re-ask
  or silently drop the decision it was blocking.
- **Open with peers**: a peer's ask awaiting this session's action,
  or this session's question to a peer awaiting an answer — same
  failure mode, different counterparty. Verbatim, with the sender
  and date; a relay stays labeled a relay.

Empty is a valid state; write "None" per direction so its absence is
a claim, not an oversight.

### Job cards
One card per running background job, because monitors and task ids die
with the session. Two shapes.

**Training-shaped** (long jobs with a log):

- driver script path and log path
- the log's phase markers in order (e.g. `== arms`, `== reads`,
  `== transfer`, `== tierN done`) and which was last reached — the
  done marker alone cannot tell "reads underway" from "hung after
  arms"
- alive-vs-dead test: driver PID check, the log's last timestamp, and
  the per-unit done files (e.g. each arm's `policy-final.pt`; a driver
  that died mid-arms leaves finals missing, and a skip-if-done restart
  resumes exactly those)
- PID and launch time; HEAD SHA at launch
- the binding, recorded as "built by maturin from HEAD <sha> at
  <time>" — the binding exposes no commit attribute of its own
- the restart command including its launch wrapper (e.g.
  `caffeinate -s nohup bash <driver> > <log> 2>&1 &`; a restart
  without `caffeinate` sleeps the Mac mid-run)
- how to stop it: drivers launch children with `&`, so killing the
  driver PID alone leaves the workers running — name the child kill
  first (e.g. `pkill -f <trainer>`), then the driver
- the do-not-edit list while it runs (driver, trainer wrapper, cert
  harness, config derivation; never rebuild the binding under a
  running arm)
- the watch re-arm command: the exact monitor invocation with its
  filter, so the resumed session re-arms the same watch instead of
  polling or re-deriving the filter — the card already restores the
  job; this line restores the eyes on it

**Server-shaped** (local servers, headless-browser sessions): no log,
no done marker; they die with the shell. The risk is the opposite of a
lost job — a stale one: a `serve.mjs` still holding its port makes the
next probe silently serve the old build, and everything looks fine.
Card: port, shutdown command, which build it is serving, and who owns
the port (`lsof -i :<port>` — PID and owning command; a listener this
thread does not own is recorded as foreign, or it becomes a
post-compact mystery). Prefer shutting servers down before compact;
card only what must stay up.

On resume, read the log's tail and check the markers and PID; never
take the summary's word for a job's state.

### Unsent messages
Any outbound message drafted but not sent — to the owner or to a peer
thread — recorded as verbatim text. A compacted session sometimes
believes it already sent a message it only drafted; the anchor is the
proof either way.

## Step 3 — Hard checks

These are checks, not judgment calls. Run all that apply; the report
lists the ones skipped and why.

1. **Git state**: `git status` in every worktree this thread holds.
   WIP commits are for tracked files only, staged by name, never by
   directory. Untracked raws and artifacts are check 4's business:
   listed, never committed. An untracked toml carrying a key the
   engine on main rejects comes off the disk entirely — the
   shipped-config sweep loads every experiments toml and a stray key
   reddens CI; keep its bytes in the anchor or a scratch path outside
   the repo.
2. **Mutate cycle**: never compact mid-cycle. Finish the cycle or
   restore first.
3. **Unreproducible measurements**: any measurement that cannot be
   re-run inside this session — the owner's device, a display no
   longer attached, a live-world capture — must be in a committed file
   before compact, naming the source device and the date. This is a
   different question from "is the tree dirty"; `git status` cannot
   see it (gitignored rig output, raws that live in the native
   checkout by standing rule).
4. **Declaration state** (experiment threads): prereg committed at
   which SHA, collection started at what time, which seed bands are
   claimed — so a resumed session never edits predictions or decision
   rules after data exists.
5. **Raws and artifacts** (experiment threads): uncommitted
   results-raw and artifact dirs listed by path, with poisoned dirs
   named explicitly (a stale dir that must never be cited is exactly
   the qualifier a summary loses).
6. **Binding staleness** (lab threads): the lab venv binding built
   from which SHA, whether that equals main, and whether a rebuild is
   owed and currently forbidden because an arm is running.
7. **Outbound messages**: send what should be sent now; record the
   rest verbatim (anchor, Unsent messages).
8. **MEMORY.md index**: re-read the index line for every open arc this
   thread owns and fix any that no longer reflect truth. A stale index
   line is worse than a missing one, because the index loads every
   session. Four threads share this file: edit it per line, fresh-read
   then targeted replacement, never a whole-file rewrite.

## Step 4 — Compact-ready report

End with a short report to the user:

- what was written where (memory files created or updated, the anchor
  path)
- the anchor's next-action line, quoted
- open-with-the-owner items: her outstanding asks by name, and any
  question still awaiting her answer re-stated in full — the cheapest
  resolution is her answering it before /compact, not the anchor
  carrying it across
- job cards on file, by name
- hard checks skipped, and why they did not apply
- anything that could NOT be made durable, so the user knows what the
  summary alone carries

Close the report with "ready — anything you send before /compact gets
folded in first", not a bare "ready". The user runs `/compact`.

## Step 5 — Late arrivals

The report is not the end of the skill. Anything that lands between
the compact-ready report and the compact itself — a question, a
ruling, a peer message — exists only in the conversation, and the
conversation is what the compact is about to destroy. Trial 1 exposed
exactly this: the owner asked a question after the report, the compact
fired before the answer went out, and the pending question survived
nowhere durable — only the summary happened to carry it.

The moment a message arrives, the session is no longer compact-ready.
Triage the message with the step 1 buckets; in practice it collapses
to two moves:

- **Answerable now**: answer it before the compact. A resolved
  exchange is bucket 4 — nothing else to persist.
- **Not resolvable now** (a ruling that changes the plan, a question
  the session cannot yet answer, a new task): rewrite the anchor in
  place — update the next-action line, or add the item under a
  `## Late arrivals` heading with the owner's words verbatim, same
  rules as the rest of the anchor. The resumed session consumes the
  heading: act on the items, then fold what remains into the normal
  sections at the next rewrite.

After each fold-in, re-state readiness in one line, so the last thing
said before the compact is always "handled or anchored". When nothing
arrives, this step costs nothing.

## After the compact — the consumer side

The summary arrives with its own instruction to continue from where
it left off without asking. Do not obey it first. The resume order:

1. Read the thread's anchor (the `## Resume` section at the top of
   `MEMORY.md` points to it) — and test its freshness stamp first.
   The anchor wins only while it is current. If origin/main has
   moved past the stamped SHA (`git fetch` first), or the summary
   describes events the anchor does not know, the anchor is STALE — an auto-compact at the
   context limit runs no skill, so this happens. Then the summary
   leads, read with its usual distrust, and rebuilding the anchor is
   the first action.
2. Re-verify the anchor's exact strings against git and the
   filesystem — `git fetch` first; the summary's injected git-status
   block is untrusted, and so is any SHA the anchor itself carries
   ("never trust a SHA written here" is the anchor's own rule).
3. Check the job cards: log tails, phase markers, PIDs, port owners.
   Re-arm the watches from their re-arm lines.
4. Consume any `## Late arrivals` heading.
5. Only then read the summary's "next step" — as a hint to be checked
   against the anchor's next action, never as the instruction. Where
   they disagree, the anchor wins and the disagreement is worth a
   sentence to the owner.

Both trials passed only because the summary happened to repeat the
"read the anchor first" mandate; this section makes the consumer side
part of the skill instead of a favor the summary does us.

The trial record lives beside this file in `TRIALS.md`: what each
trial dropped and which change patched it. Future edits check
themselves against what actually failed, not what plausibly could.
