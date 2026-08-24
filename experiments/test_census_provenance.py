"""F-028 guard: the census header must be able to say "dirty".

The finding's re-verify clause is literal — "check the stamp against a
deliberate dirty-tree run" — so that is what this does, in a throwaway git
repo rather than by dirtying the real one.

Three properties, in the order they matter:

  1. a modified tree stamps `git_dirty: True` AND names the path;
  2. a clean tree stamps False;
  3. a tree git cannot read stamps None — never False. "Unknown" read as
     "clean" is the failure F-028 is about, one layer down.

Run with OLD=1 to see it red against the pre-patch header (commit + config
sha, no dirty field), which is the exact shape that left F-028
unanswerable.
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from census_provenance import stamp  # noqa: E402

OLD = os.environ.get("OLD") == "1"


def legacy_stamp(tool_file, repo=None, extra=None):
    """cert_harness6.provenance as it stood until 2026-08-23."""
    head = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    return {"git_head": head, "config_sha256": "n/a"}


take = legacy_stamp if OLD else stamp
failures = []


def check(name, cond, detail=""):
    print(f"{'ok ' if cond else 'RED'} {name}{(' — ' + detail) if detail else ''}")
    if not cond:
        failures.append(name)


with tempfile.TemporaryDirectory() as tmp:
    repo = Path(tmp) / "repo"
    repo.mkdir()
    for cmd in (["init", "-q"], ["config", "user.email", "t@t"],
                ["config", "user.name", "t"]):
        subprocess.run(["git", "-C", str(repo), *cmd], check=True)
    tool = repo / "census_tool.py"
    tool.write_text("# pretend instrument\n")
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", "seed"],
                   check=True)

    clean = take(tool, repo=repo)
    check("clean tree stamps not-dirty", clean.get("git_dirty") is False,
          f"git_dirty={clean.get('git_dirty')!r}")

    tool.write_text("# pretend instrument\nUNCOMMITTED = True\n")
    dirty = take(tool, repo=repo)
    check("dirty tree stamps dirty", dirty.get("git_dirty") is True,
          f"git_dirty={dirty.get('git_dirty')!r}")
    check("dirty tree names the path",
          bool(dirty.get("git_dirty_paths"))
          and "census_tool.py" in " ".join(dirty["git_dirty_paths"]),
          f"paths={dirty.get('git_dirty_paths')!r}")
    check("tool sha follows the edit",
          clean.get("tool_sha256") != dirty.get("tool_sha256"))

    nogit = Path(tmp) / "plain"
    nogit.mkdir()
    (nogit / "t.py").write_text("x\n")
    unknown = take(nogit / "t.py", repo=nogit)
    check("unreadable tree stamps unknown, NOT clean",
          unknown.get("git_dirty") is None,
          f"git_dirty={unknown.get('git_dirty')!r}")

mode = "OLD (pre-patch header)" if OLD else "patched header"
if failures:
    print(f"\n{mode}: {len(failures)} red — {', '.join(failures)}")
    sys.exit(1)
print(f"\n{mode}: census header OK")
print(json.dumps(stamp(__file__), indent=1))
