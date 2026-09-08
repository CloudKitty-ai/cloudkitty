# Four threads, one repository

The owner runs four Claude sessions on this repo in parallel. These are
the rules they work under: rulings the owner has already made, dated,
with the enforcing hook named where one exists. Read it at kickoff.
CLAUDE.md governs the work; this page governs who does what, where.

## 1. Who owns what

| thread | owns | leaves alone |
|---|---|---|
| **Product** | `crates/`, the server, `evals/`, `specs/`, `kitty-eval`, `BACKLOG.md` | `client/`, `experiments/` |
| **Client** | `client/`, `client-measurements/` | the engine, `experiments/` |
| **Experiments** | `experiments/`, its tooling, the native checkout | engine and harness changes (those go through Product) |
| **Professor** | teaching, review, research framing; notes live outside the repo | implementing anything |

`docs/` and `README.md` are shared: each thread writes its own area
(2026-09-08).

- **You are the thread the kickoff message or the session name says
  you are**, never the one the branch or the dirty files suggest; the
  checkout is shared (2026-08-04).
- **Do not pick up another thread's queue.** Reviewing its PR when
  asked is fine; starting its work is not. Professor writes findings up
  for the owner to relay (2026-07-25).
- **Messages between threads carry relays and questions, not work.**
  Product and Experiments message each other routinely. Client is
  messaged only when the owner asks (2026-08-15).
- **A peer relay is never approval.** The §Ownership list in
  `experiments/README.md` needs the owner's own word in the acting
  session. A session denied an action may not ask another to do it.

## 2. The checkout

- **Experiments works in the native checkout** (`~/ai/cloudkitty`, the
  one that owns `.git`) because its datasets, artifacts and venv are
  gitignored (2026-08-04). It launches with
  `CLOUDKITTY_THREAD=experiments` in the environment; that is its
  identity to the hook (2026-09-08).
- **Everyone else works in a worktree from the first command**:
  `git fetch && git worktree add ~/ai/cloudkitty-<arc> -b <branch>
  origin/main`. One branch per worktree; a worktree never holds `main`;
  park it with `git checkout --detach origin/main` when done.
- **Merge `origin/main` in; never rebase.**
- **Use the worktree's absolute path for every read, edit and write.**
  The session's declared cwd is the native checkout, so a bare path
  edits Experiments' tree (2026-08-19).
- **Commit real work before any destructive check.** The red-first
  cycle is `scripts/mutate.sh` (CLAUDE.md rule 5).

Enforced at the command by two PreToolUse hooks in `.claude/hooks/`:
`checkout-guard.py` (#356) refuses rebase, `gh pr merge
--delete-branch`, any move of a worktree onto `main` or another branch,
and git mutation or Edit/Write in the native checkout without the
Experiments variable; `revert-guard.py` (#353) refuses `git checkout
--`, `git restore` and `git reset --hard` on a file that differs from
HEAD. Not covered: shell writes into the native tree (`sed -i`,
redirection).

## 3. Before you diagnose, report or compare

- **Pull before diagnosing** (2026-08-23). Before investigating any
  reported failure or running a suite you intend to report:

  ```
  git fetch && git rev-parse HEAD origin/main
  git log --oneline -5 origin/main -- <path>
  ```

  A fetch moves the ref, not the tree; compare the hashes.
- **Read state off the running system**, not memory: what is deployed,
  what is seated, what is live. A correct diff against an unverified
  baseline reports fiction with confidence (2026-08-24).
- **Read a long job's output file, not its exit code**; never filter a
  background job's stderr through something that can eat a panic
  (2026-08-19).

## 4. How much process

- **Spec-first** (`/speckit-*`, guards proven red, predictions written
  before runs) for engine, interface and major changes (2026-07-23).
  **Branch-and-iterate with tests** for client polish, config re-cuts,
  docs and tooling (2026-09-08). Unsure which? Ask.
- **The client is a side project, never a gate on research**; it
  builds a solid baseline, not perfection (2026-08-25).
- **Deploys and tags are the owner's.** A tag and its changelog entry
  land together: `## Unreleased` expands into the release before the
  tag. Each merging PR adds its one-liner to `## Unreleased` with the
  compatibility markers the changelog header defines; a missing marker
  claims neutrality (2026-08-08). Fog work is 3.0-numbered.

## 5. Owner decisions and owner words

- **Every open owner decision is a GitHub issue** labelled `owner-call`
  plus `oc:ready` / `oc:discussing` / `oc:blocked`; bar and shape in
  `experiments/README.md` §"Owner calls: the ledger" (2026-09-05). Only
  the owner closes one; the ruling is copied, verbatim and with the
  issue number, into the document that owns it.
- **Owner-authored text ships verbatim.** Flag a typo; never fix it.
  Do not restructure a document the owner supplied (2026-07-23).
- **Feedback is grounded and kind.** Verify before affirming; say what
  is wrong and why; praise only what earns it (2026-07-25).
