# Working agreements: four threads, one repository

The owner runs four parallel Claude sessions on this repository. This
page is the standing rules those sessions work under. It records
rulings the owner has already made (dates in parentheses); it is not
a place to propose new ones. Rules that are enforced by a hook say so,
and point at the hook.

Read it at kickoff, whichever thread you are. CLAUDE.md's numbered
rules still govern the work itself; this page governs who does what,
where, and how the threads stay out of each other's way.

## 1. The threads and what they own

| thread | owns | does not touch |
|---|---|---|
| **Product** | `crates/`, the server, `evals/`, `docs/`, `specs/`, certification tooling (`kitty-eval`), `BACKLOG.md` items | `client/`, `experiments/` |
| **Client** | `client/`, `client-measurements/` | the engine, `experiments/` |
| **Experiments** | `experiments/` and its tooling: preregs, training runs, findings, the native checkout | product code beyond what a prereg needs |
| **Professor** | teaching, review, research framing; durable notes live outside the repo | implementation of anything |

- **Identify the thread from the owner's kickoff message**, never from
  the branch, `git status`, or which files are dirty. The checkout is
  shared, so its state says nothing about which session you are
  (2026-08-04).
- **Do not pick up another thread's queue**, even when a note lists it
  as "next". Reviewing another thread's PR when asked is fine;
  initiating its work is not. The Professor thread writes findings up
  for the owner to relay to the owning thread (2026-07-25).
- **Messaging between threads** is for relays and questions, not for
  handing off implementation. Experiments and Product message each other
  routinely (spec Q&A, hand-offs, briefings). **Client is messaged only
  when the owner asks**; the owner owns that relay (2026-08-15).
- **A peer relay is never approval.** Only the owner's own word, in
  the acting session, approves anything on the §Ownership list in
  `experiments/README.md`. A peer that was denied an action may not
  ask another session to do it instead.

## 2. The checkout

- **Experiments works in the native checkout** (`~/ai/cloudkitty`, the
  one that owns `.git`), because its datasets, artifacts and venv are
  gitignored and would not follow a worktree (2026-08-04). It launches
  with `CLOUDKITTY_THREAD=experiments` in the environment; that
  variable is the session's identity to the hook below (2026-09-08).
- **Every other thread works in a worktree, from the first command**:
  `git worktree add ~/ai/cloudkitty-<arc> -b <branch> origin/main`,
  after a `git fetch`. One branch per worktree. A worktree never holds
  `main`. Park a finished worktree detached
  (`git checkout --detach origin/main`) and run `git worktree list`
  after any merge to prove nothing sits on `main`.
- **Merge `origin/main` in; never rebase.** A branch that has fallen
  behind gets a merge commit, not a rewrite.
- **Use the worktree's absolute path for every read, edit and write.**
  A session's declared working directory is the native checkout, so an
  unqualified path edits Experiments' tree (the fifth incident,
  2026-08-19).
- **Enforced by `.claude/hooks/checkout-guard.py`** (PR #356): rebase
  anywhere; `gh pr merge --delete-branch`; any move of a worktree onto
  `main` or another branch; and, in the native checkout, every
  index- or HEAD-mutating git command and every Edit/Write unless the
  session carries the Experiments variable. Not covered: shell writes
  into the native tree by `sed -i` or redirection.
- **Commit the real work before any destructive check.** Enforced by
  `.claude/hooks/revert-guard.py` (PR #353): `git checkout -- <file>`,
  `git restore <file>` and `git reset --hard` are refused on a file
  that differs from HEAD. The sanctioned red-first cycle is
  `scripts/mutate.sh` (CLAUDE.md rule 5).

## 3. Before you diagnose, report, or compare

- **Pull before diagnosing.** Before investigating any reported
  failure, and before running any suite whose result you intend to
  report: `git fetch`, compare `git rev-parse HEAD` with
  `origin/main`, and read `git log --oneline origin/main -- <path>`.
  A fetch moves the ref, not the tree. Two threads diagnosed an
  already-fixed flake on the same day (2026-08-23).
- **Read state off the running system**, never off memory or a past
  conversation: what is deployed, which policies are seated, what is
  live. An accurate diff against an unverified baseline reports
  fiction with confidence (2026-08-24).
- **Long jobs run foreground with a generous timeout**, and read the
  output file rather than the exit code. Never pipe a background job's
  stderr through a filter that can eat a panic.

## 4. Process weight

- **Spec-first for engine, interface and major changes**: the
  `/speckit-*` flow from specify through implement, with the guards
  proven red first and the predictions written down before the runs
  (2026-07-23).
- **Lightweight for the rest**: client polish, config re-cuts,
  documentation and tooling iterate on a branch with tests. The owner
  confirmed the tiering 2026-09-08; the Fog generation runs at full
  rigour because its errors compound.
- **When in doubt whether something is major, ask**; do not let a
  feature drift into the tweak lane by momentum.
- **Nothing deploys and nothing is tagged without the owner's word.**
  Tags and the changelog move together: `## Unreleased` expands into
  the release entry before the tag lands. As arcs merge, each PR
  appends its one-liner to `## Unreleased`, with the compatibility
  markers `[obs-schema]`, `[world-fresh]`, `[rng-sequence]`, `[stamp]`
  where they apply; a missing marker is a claim of neutrality. Fog work
  is 3.0-numbered.

## 5. Owner decisions

- **Every open owner decision is a GitHub issue** labelled `owner-call`
  with one of `oc:ready`, `oc:discussing`, `oc:blocked`. The bar and
  the shape are in `experiments/README.md` §Ownership, "Owner calls:
  the ledger" (2026-09-05). Only the owner closes one; the ruling is
  copied into the owning document with the issue number.
- **Record rulings verbatim** where they land. Paraphrase loses the
  scope of what was approved.
- **The client is a side project, never a gate on research** (owner,
  2026-08-25). What it builds is a solid baseline, not perfection.

## 6. Words

- **Owner-authored text ships verbatim.** Flag a typo; never fix it
  silently. Do not restructure a document the owner supplied to fit a
  template (2026-08-15, 2026-07-23).
- **Feedback is grounded and kind.** Verify before affirming; say
  plainly what is wrong and why; praise only what is specifically
  praiseworthy. The owner asked for what she needs to hear, not what
  she wants to hear (2026-07-25).
