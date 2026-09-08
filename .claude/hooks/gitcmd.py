"""Shared parsing for the git hooks: find every git invocation in a Bash
command string and the directory it runs in (follows `cd` segments and
`git -C`), plus repo-shape helpers. Imported by revert-guard.py and
checkout-guard.py; not a hook itself."""
import os
import re
import shlex
import subprocess

GIT_RE = re.compile(
    r"\bgit\b((?:\s+-C\s+\S+|\s+-c\s+\S+|\s+--no-pager)*)\s+([a-z-]+)\b([^;&|\n]*)"
)
SEG_RE = re.compile(r"&&|\|\||;|\n")
CD_RE = re.compile(r"^\s*cd(?:\s+(\S+))?\s*$")
# a heredoc body is data, not commands: `cat > f <<'EOF' ... EOF`
HEREDOC_RE = re.compile(
    r"<<-?\s*(['\"]?)(\w+)\1[^\n]*\n.*?\n[ \t]*\2[ \t]*(?=\n|$)", re.S
)


def strip_heredocs(cmd):
    """Drop every heredoc body, keeping the line that opens it."""
    return HEREDOC_RE.sub(lambda m: m.group(0).split("\n", 1)[0], cmd)


def git_calls(cmd, cwd):
    """Yield (dir, subcommand, arg-string) for each git call in `cmd`."""
    for seg in SEG_RE.split(strip_heredocs(cmd)):
        cd = CD_RE.match(seg)
        if cd:
            d = os.path.expanduser(cd.group(1) or "~").strip("'\"")
            cwd = d if os.path.isabs(d) else os.path.join(cwd, d)
            continue
        m = GIT_RE.search(seg)
        if not m:
            continue
        pre, sub, args = m.group(1), m.group(2), m.group(3)
        c = re.search(r"-C\s+(\S+)", pre)
        d = os.path.expanduser(c.group(1).strip("'\"")) if c else cwd
        if not os.path.isabs(d):
            d = os.path.join(cwd, d)
        yield d, sub, args


def tokens(args):
    try:
        return shlex.split(args)
    except ValueError:
        return args.split()


def git(d, *argv):
    r = subprocess.run(["git", "-C", d, *argv], capture_output=True, text=True)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def repo_shape(d):
    """(toplevel, common_dir) as real paths, or (None, None) outside a repo."""
    rc, top, _ = git(d, "rev-parse", "--show-toplevel")
    if rc != 0 or not top:
        return None, None
    rc, common, _ = git(d, "rev-parse", "--git-common-dir")
    if rc != 0:
        return None, None
    if not os.path.isabs(common):
        common = os.path.join(d, common)
    return os.path.realpath(top), os.path.realpath(common)


def native_root(project_dir):
    """The checkout that owns the project's .git (worktrees link to it)."""
    _, common = repo_shape(project_dir)
    return os.path.dirname(common) if common else None
