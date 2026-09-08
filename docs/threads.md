# Four threads, one repository

The owner runs four Claude sessions on this repo in parallel. These are
the dated rulings on who does what, where; the enforcing hook is named
where one exists. Read at kickoff. CLAUDE.md governs the work.

## 1. Who owns what

| thread | owns | leaves alone |
|---|---|---|
| **Product** | `crates/`, the server, `evals/`, `specs/`, `kitty-eval`, `BACKLOG.md` | `client/`, `experiments/` |
| **Client** | `client/`, `client-measurements/` | the engine, `experiments/` |
| **Experiments** | `experiments/`, its tooling, the native checkout | engine and harness changes (go through Product) |
| **Professor** | teaching, review, research framing; notes live outside the repo | implementing anything |

`docs/` and `README.md` are shared: each thread writes its own area
(2026-09-08).

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

## 2. The checkout

- **Experiments works in the native checkout** (`~/ai/cloudkitty`);
  its datasets, artifacts and venv are gitignored (2026-08-04). It
  launches with `CLOUDKITTY_THREAD=experiments`; that is its identity
  to the hook (2026-09-08).
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
- **Long jobs run foreground.** Read the output file, not the exit
  code; never filter stderr through something that can eat a panic
  (2026-08-19).

## 4. How much process

- **Spec-first** for engine, interface and major changes (2026-07-23);
  branch-and-iterate with tests for client polish, config re-cuts,
  docs and tooling (2026-09-08). Unsure which? Ask.
- **The client is a side project, never a gate on research**
  (2026-08-25).
- **Deploys and tags are the owner's.** Each merging PR adds its
  one-liner to `## Unreleased` with the changelog's compatibility
  markers; a missing marker claims neutrality. `## Unreleased`
  expands into the release before any tag (2026-08-08). Fog work is
  3.0-numbered.

## 5. Owner decisions

- **Every open owner decision is a GitHub issue** labelled
  `owner-call` + `oc:ready` / `oc:discussing` / `oc:blocked`; bar and
  shape in `experiments/README.md` §"Owner calls: the ledger"
  (2026-09-05). Only the owner closes one; the ruling is copied
  verbatim, with issue number, into the owning document.
- **Owner-authored text ships verbatim.** Flag a typo; never fix it;
  don't restructure a supplied document (2026-07-23).
