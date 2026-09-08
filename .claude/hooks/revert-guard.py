#!/usr/bin/env python3
"""PreToolUse hook (Bash): refuse `git checkout -- <file>` / `git restore <file>`
on a tracked file that holds uncommitted changes.

Why: those commands restore to HEAD. They cannot tell a throwaway mutation
from unlanded implementation sitting in the same file, and have wiped
uncommitted work five times (see CLAUDE.md rule 5: commit first, or keep a
copy). Non-destructive reverts stay open: `git apply -R <patch>` reverses
only the patch; `git stash push -- <file>` keeps the content in the stash.

Contract: reads the hook JSON on stdin, exits 2 with the reason on stderr
to block, exits 0 to allow. Any parse failure allows (fail-open) so a
broken hook never locks the session; the guard is a net, not a wall.
"""
import json
import os
import shlex
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gitcmd import git_calls  # noqa: E402


def dirty(repo, path):
    """True if <path> (a file or a directory, tracked) differs from HEAD."""
    r = subprocess.run(
        ["git", "-C", repo, "diff", "--quiet", "HEAD", "--", path],
        capture_output=True,
    )
    # exit 1 means "differs"; git also exits 1 (with a message) when HEAD
    # is unreachable, e.g. not a repo. That is not dirt: fail open, the
    # checkout itself will fail there and nothing can be lost.
    return r.returncode == 1 and not r.stderr


def targets(sub, args):
    """The worktree paths this invocation would overwrite, or []."""
    try:
        toks = shlex.split(args)
    except ValueError:
        toks = args.split()
    if sub == "restore":
        staged = any(t in ("--staged", "-S") for t in toks)
        worktree = any(t in ("--worktree", "-W") for t in toks)
        if staged and not worktree:
            return []  # index only; the worktree copy survives
        out, skip = [], False
        for t in toks:
            if skip:
                skip = False
                continue
            if t in ("-s", "--source"):
                skip = True
                continue
            if t.startswith("-") and t != "--":
                continue
            if t != "--":
                out.append(t)
        return out
    if sub == "reset":
        # `reset --hard` / `--merge` rewrite every tracked file in the tree
        return ["."] if any(t in ("--hard", "--merge") for t in toks) else []
    # checkout
    if "--" in toks:
        return toks[toks.index("--") + 1 :]
    if any(t in ("-b", "-B", "--orphan") for t in toks):
        return []  # branch creation never overwrites paths
    if any(t in ("-f", "--force") for t in toks):
        return ["."]  # a forced branch switch discards every local change
    # `git checkout <thing>`: a branch is safe, a path is not. Let git say
    # which by checking each non-flag token as a path.
    return [t for t in toks if not t.startswith("-")]


def main():
    try:
        data = json.load(sys.stdin)
        cmd = data.get("tool_input", {}).get("command", "")
        repo = data.get("cwd") or "."
    except Exception:
        return 0
    for r, sub, args in git_calls(cmd, repo):
        if sub not in ("checkout", "restore", "reset"):
            continue
        for path in targets(sub, args):
            if dirty(r, path):
                sys.stderr.write(
                    f"revert-guard: `git {sub}` would overwrite uncommitted "
                    f"changes in `{path}`. That command restores to HEAD and "
                    "cannot separate a throwaway patch from unlanded work "
                    "(five incidents; CLAUDE.md rule 5). Commit the real work "
                    "first, or revert the throwaway non-destructively: "
                    "`git apply -R <patch>` or `git stash push -- <file>`.\n"
                )
                return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
