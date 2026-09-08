#!/usr/bin/env python3
"""PreToolUse hook (Bash, Edit, Write, MultiEdit): the shared-checkout rules.

Four Claude threads share one repository. Experiments works in the native
checkout (the one that owns .git); Product and Client work in linked
worktrees and must never hold `main`. Five recorded incidents (memory:
shared-checkout-branch-hazard) came from the same few commands; this hook
refuses them at the command:

  everywhere in this repo family
    git rebase                         merge origin/main IN instead. This
                                       is for worktree branches; on native
                                       main the flow is `git pull --rebase`
                                       (the only writer to main, landing
                                       local commits over a merged PR),
                                       which is not `git rebase` and must
                                       stay open (pinned in the test)
    gh pr merge ... --delete-branch    the flag checks out the default
                                       branch in the worktree you ran it
                                       from; delete with git push --delete
  in a linked worktree
    git checkout/switch to main, -b/-B/-c/-C, or any branch name
                                       one branch per worktree; only
                                       --detach and path checkouts pass
  in the native checkout, unless CLOUDKITTY_THREAD=experiments
    git add/rm/mv/commit/checkout/switch/restore/merge/rebase/pull/reset/
    stash/cherry-pick/revert/apply/am/clean
                                       and Edit/Write of any file there:
                                       that tree is Experiments'; a session
                                       whose declared cwd is the native
                                       checkout edits it by accident

Identity is the CLOUDKITTY_THREAD environment variable, inherited from the
terminal that launched the session (`CLOUDKITTY_THREAD=experiments claude`).
Exit 2 blocks with the reason on stderr; parse failure fails open.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gitcmd import git, git_calls, native_root, repo_shape, tokens  # noqa: E402

NATIVE_MUTATORS = {
    "add", "rm", "mv", "commit", "checkout", "switch", "restore", "merge",
    "rebase", "pull", "reset", "stash", "cherry-pick", "revert", "apply",
    "am", "clean",
}
HINT = (
    "If this session IS Experiments, launch it with CLOUDKITTY_THREAD=experiments "
    "in the environment; every other thread works in a worktree "
    "(git worktree add ~/ai/cloudkitty-<arc> -b <branch> origin/main)."
)


def is_experiments():
    return os.environ.get("CLOUDKITTY_THREAD", "").lower() == "experiments"


def names_branch(d, tok):
    rc, _, _ = git(d, "rev-parse", "--verify", "--quiet", f"refs/heads/{tok}")
    if rc == 0:
        return True
    rc, _, _ = git(d, "rev-parse", "--verify", "--quiet", f"refs/remotes/{tok}")
    return rc == 0


def worktree_branch_move(d, sub, toks):
    """Reason text if `git checkout/switch <toks>` would move this worktree
    onto a branch, else None."""
    if "--" in toks:
        return None  # path checkout: revert-guard's business
    if any(t in ("--detach", "-d") for t in toks) and not any(t in ("-b", "-B") for t in toks):
        return None
    if any(t in ("-b", "-B", "-c", "-C", "--orphan") for t in toks):
        return f"`git {sub}` would create a branch in this worktree"
    for t in toks:
        if t.startswith("-"):
            continue
        if t == "main" or names_branch(d, t):
            return f"`git {sub} {t}` would put this worktree on branch `{t}`"
    return None


def deny(msg):
    sys.stderr.write(f"checkout-guard: {msg}\n")
    return 2


def check_bash(cmd, cwd, native):
    if "gh pr merge" in cmd and any(f in tokens(cmd) for f in ("--delete-branch", "-d")):
        return deny(
            "`gh pr merge --delete-branch` checks out the default branch in the "
            "worktree it runs from (incident 3). Merge without the flag, then "
            "`git push origin --delete <branch>`."
        )
    for d, sub, args in git_calls(cmd, cwd):
        top, common = repo_shape(d)
        if top is None or os.path.dirname(common) != native:
            continue  # not this repo family
        toks = tokens(args)
        if sub == "rebase":
            return deny("`git rebase` is off in this repo: merge origin/main IN (rule: merge, never rebase).")
        if top == native:
            if sub in NATIVE_MUTATORS and not is_experiments():
                return deny(
                    f"`git {sub}` in the native checkout {native}. That tree is "
                    f"Experiments'; branch and index state there is shared by every "
                    f"session (incidents 1, 2, 5). {HINT}"
                )
        else:
            if sub in ("checkout", "switch"):
                why = worktree_branch_move(d, sub, toks)
                if why:
                    return deny(
                        f"{why} (one branch per worktree; a worktree must never hold "
                        f"main — incidents 3, 4). Park with `git checkout --detach "
                        f"origin/main`; a second branch gets its own worktree."
                    )
    return 0


def check_edit(path, native):
    if not path or is_experiments():
        return 0
    path = os.path.realpath(os.path.expanduser(path))
    top, _ = repo_shape(os.path.dirname(path))
    if top == native:
        return deny(
            f"editing {path} inside the native checkout {native}, which is "
            f"Experiments' tree. A session whose declared cwd is the native "
            f"checkout edits it by accident (incident 5); use the worktree's "
            f"absolute path. {HINT}"
        )
    return 0


def main():
    try:
        data = json.load(sys.stdin)
        tool = data.get("tool_name", "")
        inp = data.get("tool_input", {})
        cwd = data.get("cwd") or os.getcwd()
        project = os.environ.get("CLAUDE_PROJECT_DIR") or cwd
        native = native_root(project)
    except Exception:
        return 0
    if native is None:
        return 0
    if tool == "Bash":
        return check_bash(inp.get("command", ""), cwd, native)
    if tool in ("Edit", "Write", "MultiEdit"):
        return check_edit(inp.get("file_path", ""), native)
    return 0


if __name__ == "__main__":
    sys.exit(main())
