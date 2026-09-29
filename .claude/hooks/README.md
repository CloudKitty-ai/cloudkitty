# The shared-checkout hooks — the enforcement inventory

The one home for WHAT the hooks refuse and what they cannot see
(owner's word 2026-09-28, PR #439; THREADS §2 keeps ownership and
review governance and points here). Each hook's docstring carries
its rules' full detail; self-tests sit beside each hook
(`test-*.sh`).

PreToolUse, wired in `.claude/settings.json`:

- `checkout-guard.py` (#356) refuses: `git rebase` anywhere in the
  repo family; `gh pr merge --delete-branch`; `git reset` onto
  `origin/main` or `origin/HEAD`, with or without a `~N`/`^` suffix
  (incident 6 — every mode in a linked worktree, the squash idiom
  `--soft`/`--mixed`/bare in the native checkout, `--hard` staying
  open there as Experiments' sync hatch; path-form resets pass);
  moving a worktree onto any branch; and git mutation or Edit/Write
  in the native checkout without `CLOUDKITTY_THREAD=experiments`.
- `revert-guard.py` (#353) refuses `git checkout --`, `git restore`
  and `git reset --hard` on files dirty against HEAD.

SessionStart runs `scripts/condense-budget.sh --owed` (#437): the
condense-owed nudge, silent when nothing is owed.

Not covered: shell writes into the native tree (`sed -i`,
redirection), and a dirty-then-revert inside a single compound
command — a hook checks before the command runs.
