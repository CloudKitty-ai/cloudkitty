# Five threads, one repository

The owner runs five Claude sessions on this repo in parallel. These are
the dated rulings on who does what, where; the enforcing hook is named
where one exists. Read at kickoff. CLAUDE.md governs the work.

## 1. Who owns what

| thread | owns | leaves alone |
|---|---|---|
| **Product** | `crates/`, the server, `evals/`, `specs/`, `kitty-eval`, `BACKLOG.md` | `client/`, `experiments/` |
| **Client** | `client/`, `client-measurements/` | the engine, `experiments/` |
| **Experiments** | `experiments/`, its tooling, the native checkout | engine and harness changes (go through Product); the Claude Code tooling (Harness) |
| **Professor** | teaching, review, research framing; notes live outside the repo | implementing anything |
| **Harness** | the Claude Code tooling: `.claude/` (skills, hooks, agents, settings), `scripts/mutate.sh`, the memory directory's hygiene, the meta checks in CI (its own workflow file), `THREADS.md` and `CLAUDE.md` drafts for the owner's ruling | every content file: code, specs, experiments, docs, client. It reports on them; it never edits them |

`docs/` and `README.md` are shared: each thread writes its own area
(2026-09-08).

Harness (2026-09-22) owns the tooling files and reports on content
files. Its two standing passes: the accuracy gate (a fresh-context
re-derivation of an artifact's claims against the recorded raws and
the command that made them, run before the owning thread commits) and
the condense pass (a cut list for a file or corpus: duplicates across
homes, dead sections, amendments that should be supersessions). Both
produce a report; the owning thread applies it. What each pass caught
or cut is appended to the record beside its skill, TRIALS.md
discipline. The prepare-for-compact skill files (Product's from
2026-09-21) move to Harness with the rest of `.claude/`; the TRIALS.md
append rule stands unchanged: a trialling thread appends its own
section and never touches another thread's, Product and Client through
a worktree and a PR, Experiments on main directly. Harness never
launches a spec, a pass on a peer's work, or a CI change on a peer's
relay; the owner's word in the Harness session starts each.

- **You are the thread the kickoff or session name says you are**,
  never the one the branch or dirty files suggest; the checkout is
  shared (2026-08-04).
- **Do not pick up another thread's queue.** Reviewing its PR when
  asked is fine; starting its work is not. Professor writes findings
  up for the owner to relay (2026-07-25).
- **Cross-thread messages carry relays and questions, not work.**
  Client is messaged only when the owner asks (2026-08-15).
- **A peer relay is never approval.** The §Ownership list in
  `experiments/README.md` needs the owner's own word in the acting
  session. A session denied an action may not ask another to do it.
- **Harness reads every thread's records and edits none of their
  files.** A cut list or a verdict is a report; applying it is the
  owning thread's commit, on its own lane (2026-09-22).

## 2. The checkout

- **Experiments works in the native checkout** (`~/ai/cloudkitty`);
  its datasets, artifacts and venv are gitignored (2026-08-04). It
  launches with `CLOUDKITTY_THREAD=experiments`; that is its identity
  to the hook (2026-09-08).
- **Harness works in a worktree like Product and Client**; its edits
  land by PR. The memory directory is outside the repo and outside the
  hook: Harness edits it per line, fresh-read then targeted
  replacement, the MEMORY.md discipline (2026-09-22).
- **Everyone else works in a worktree from the first command**:
  `git fetch && git worktree add ~/ai/cloudkitty-<arc> -b <branch>
  origin/main`. One branch per worktree; never `main`; park with
  `git checkout --detach origin/main`.
- **Merge `origin/main` in; never rebase in a worktree.** Experiments'
  `git pull --rebase --autostash origin main` on native `main` is the
  one exception (hook-allowed).
- **Use the worktree's absolute path for every read, edit and write.**
  The declared cwd is the native checkout (2026-08-19).
- **Commit real work before any destructive check.** The red-first
  cycle is `scripts/mutate.sh` (CLAUDE.md rule 5).

Enforced by two PreToolUse hooks in `.claude/hooks/`:
`checkout-guard.py` (#356) refuses rebase, `gh pr merge
--delete-branch`, moving a worktree onto any branch, and git mutation
or Edit/Write in the native checkout without the Experiments variable;
`revert-guard.py` (#353) refuses `git checkout --`, `git restore` and
`git reset --hard` on files dirty against HEAD. Not covered: shell
writes into the native tree (`sed -i`, redirection), and a
dirty-then-revert inside a single compound command — the hook checks
before the command runs.

## 3. Before you diagnose or report

- **Pull first** (2026-08-23): `git fetch && git rev-parse HEAD
  origin/main`, then `git log --oneline -5 origin/main -- <path>`.
  A fetch moves the ref, not the tree; compare the hashes.
- **Read state off the running system**, never off memory
  (2026-08-24).
- **Read a long job's output file, not its exit code**; never filter
  stderr through something that can eat a panic (2026-08-19).

## 4. How much process

- **Spec-first** for engine, interface and major changes (2026-07-23);
  branch-and-iterate with tests for client polish, config re-cuts,
  docs and tooling (2026-09-08). Unsure which? Ask.
- **The client is a side project, never a gate on research**
  (2026-08-25).
- **Delegation is by task shape** (CLAUDE.md rule 9, 2026-09-22):
  verification and sweeps go to a subagent, decisions and write-ups
  stay in the session. Subagents run on the default the settings file
  sets; only Harness changes that default.
- **Deploys and tags are the owner's.** Each merging PR adds its
  one-liner to `## Unreleased` with the changelog's compatibility
  markers; a missing marker claims neutrality. `## Unreleased`
  expands into the release before any tag (2026-08-08). Fog work is
  3.0-numbered.

## 5. Owner decisions

- **Every open owner decision is a GitHub issue** labelled
  `owner-call` + `oc:ready` / `oc:discussing` / `oc:blocked`; bar and
  shape in `experiments/README.md` §"Owner calls: the ledger"
  (2026-09-05). The owning thread closes one once it and the owner
  are both satisfied everything in it is answered and ruled
  (2026-09-22): the closing comment quotes the owner's words verbatim,
  and the ruling is copied, with issue number, into the owning
  document.
- **Owner-authored text ships verbatim.** Flag a typo; never fix it;
  don't restructure a supplied document (2026-07-23).

## 6. What lives where (owner ruled 2026-09-22)

One home per fact; every other mention is a pointer to it. The
rows below the first ten were added on the owner's word (2026-09-22:
"key information in one place"; TODO owner: update rigor for these
key files and the user-facing docs at tag time). A number,
a rule or a ruling restated outside its home is a condense cut.

| the fact | its one home | pointers elsewhere look like | does not hold |
|---|---|---|---|
| a claim about the system that outlives one arc | `experiments/FINDINGS.md` (F-nnn, edited by supersession) | the F-number | per-arc narrative, raw numbers beyond the claim's own |
| the evidence for a claim: numbers, the command that made them, the read | the arc's `RESULTS.md`; its `results-raw/` in the native checkout, uncommitted | FINDINGS cites the file and section | conclusions that generalise past the arc |
| a Gen 2 decision input | `experiments/fog-gen1-shakeout/GEN2-INPUTS.md` | a "revisit at the Gen 2 read" note naming the entry | findings (those go to FINDINGS and get cited) |
| a design rule for worlds, rewards, behaviour | `experiments/DESIGN-DOCTRINE.md` (rules 1–10) | a spec names the rule number it moved on (CLAUDE.md rule 8) | process rules, findings |
| lab process: how to design, run, read, and post an owner call | `experiments/README.md` (§Design discipline, §Ownership, §Owner calls) | "per README §…" | design rules, thread ownership |
| future product work, its priority and intent | `BACKLOG.md` | the PR that ships it removes the entry | design, owner decisions |
| an open owner decision | a GitHub issue `owner-call` + `oc:*` | the ruling, verbatim with the issue number, in the document that owns the subject | anything after close: the owning document is the record |
| a thread's session state: where it is, job cards, open asks | the memory directory (resume anchor + `MEMORY.md` index) | — | numbers, rules, findings, rulings: a pointer to the home instead |
| who owns what, where each thread works, how much process | `THREADS.md` | CLAUDE.md line 1 | how to do the work |
| how the work is done | `CLAUDE.md` | — | who does it |
| what shipped and what it invalidates (saved worlds, policies, baselines) | `CHANGELOG.md` (`## Unreleased`, compatibility markers) | the PR number | design, intent, priority |
| the design record of a change: what was ruled, why, what it touched | `specs/NNN-*/` | "spec NNN"; the owner's ruling copied there with its issue number | future work (BACKLOG), evidence |
| the live box: seatings, censuses, welfare reads as deployed | `policies/purrsonality.md` | — | the next deploy (that is checked-in config) |
| a skill's trial record: what dropped, what patched it, clean runs | `TRIALS.md` beside the skill | — | the skill's rules (SKILL.md) |
| a trap or lesson about the code a thread owns (owner ruled 2026-09-22: one file per thread, co-located) | `client/TRAPS.md`, `crates/TRAPS.md`, `experiments/TRAPS.md`, `.claude/TRAPS.md`; sections *Traps* (what the code does that bites) and *Lessons* (a method change); entry = date, the trap in a sentence, where it bites, the evidence, the guard if any | the memory index carries a pointer, never the trap; a lesson that holds across threads is promoted to CLAUDE.md, THREADS.md or README §Design discipline | user-facing docs (`docs/`), findings, any trap with a mechanical guard (test, hook, CI check): the guard is its home and the entry is deleted |
