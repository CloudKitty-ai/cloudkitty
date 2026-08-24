#!/usr/bin/env python3
"""The census header F-028 asked for: enough to re-create the instrument.

F-028 (2026-08-21): every chase-census raw from that afternoon failed
byte-reproduction from committed sources, and the surviving explanation —
uncommitted working-tree state in the instrument worktree — was
*uninspectable after the fact*. The finding is not "someone was careless";
it is that a raw which cannot be re-attributed converts a noise-flagged
pass into an unanswerable question. The practice adopted: a census raw
carries its engine commit, its working-tree dirty state, and its tool
source sha, **stamped by the tool itself, not the operator's notes**.

`stamp()` is that header. The dirty flag is the load-bearing field — the
one fact the old headers could not express and the one that would have
answered F-028 — so it names the modified paths rather than just setting
a boolean, and a stamp that cannot reach git says so instead of quietly
reporting clean.

Live censuses need a second half: the instrument's own repo says nothing
about what the BOX is running. `served()` stamps the world on the other
end of the wire — its config hash, its roster and per-seat behaviors, its
tick — so a live raw is attributable to a served world rather than only to
the laptop that sampled it.

Used by attn-cert-2026-08-14/{live_census,pose_census}.py and, through
cert_harness6.provenance, by the exp-006 lab family.
"""

import hashlib
import json
import subprocess
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _git(*args, repo=None):
    try:
        r = subprocess.run(["git", "-C", str(repo or REPO), *args],
                           capture_output=True, text=True, timeout=15)
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:
        return None


def toolchain_pin(repo=None):
    """The pinned channel from rust-toolchain.toml, or None if unpinned."""
    p = (repo or REPO) / "rust-toolchain.toml"
    try:
        for line in p.read_text().splitlines():
            s = line.strip()
            if s.startswith("channel"):
                return s.split("=", 1)[1].strip().strip('"\'')
    except OSError:
        return None
    return None


def binding_identity(module):
    """sha256 of the compiled artifacts behind an imported binding.

    The lab stamp's `rustc -V` comes from PATH at run time, which is not
    necessarily the compiler that built the extension being imported (a
    binding built before a toolchain roll keeps running afterwards —
    Product flagged this 2026-08-23). The compiled bytes are the fact that
    cannot drift from what actually ran, so they are stamped alongside.
    """
    try:
        d = Path(module.__file__).parent
        return [{"name": p.name,
                 "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                 "mtime_utc": datetime.fromtimestamp(
                     p.stat().st_mtime, timezone.utc).isoformat(
                         timespec="seconds")}
                for p in sorted(d.glob("*.so"))] or None
    except Exception:
        return None


def stamp(tool_file, repo=None, extra=None):
    """The instrument's own identity, at the moment it ran.

    `tool_file` is the running tool's path (pass `__file__`). Returns a
    dict safe to nest under "provenance" in any raw. Every field is
    None-able: a stamp that could not be taken must read as unknown, never
    as clean.
    """
    head = _git("rev-parse", "HEAD", repo=repo)
    porcelain = _git("status", "--porcelain", repo=repo)
    # Split on the status code, never on a column offset: `_git` strips the
    # output, which eats the LEADING SPACE of a ` M path` line and shifts
    # every tracked-file path by one character (untracked `?? path` lines
    # have no leading space, so the bug hid on a tree with only new files —
    # test_census_provenance.py caught it on the first run).
    dirty_paths = [ln.strip().split(maxsplit=1)[1]
                   for ln in (porcelain or "").splitlines()
                   if len(ln.strip().split(maxsplit=1)) > 1]
    src = Path(tool_file).resolve()
    out = {
        "git_head": head,
        # THE F-028 FIELD. None = could not be determined (no git, timeout)
        # and must not be read as "clean".
        "git_dirty": None if porcelain is None else bool(dirty_paths),
        "git_dirty_paths": dirty_paths[:40] or None,
        "git_dirty_count": None if porcelain is None else len(dirty_paths),
        "tool": src.name,
        "tool_sha256": hashlib.sha256(src.read_bytes()).hexdigest(),
        # What the repo says the compiler must be (rust-toolchain.toml,
        # landed 2026-08-23). Recorded next to the `rustc` the lab stamp
        # takes from PATH so the two can be compared after the fact — a
        # pin nobody checks is another operator's note.
        "toolchain_pin": toolchain_pin(repo),
        "stamped_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    if extra:
        out.update(extra)
    return out


def served(base, timeout=15):
    """Identity of the world on the other end of the wire, or None.

    A live raw's engine commit is not the instrument's commit — the box
    builds its own. What IS recoverable over the REST surface is the world
    it is serving: the validated config it booted with (hashed), the roster
    and the behavior string seated at each id, and the tick reached. That
    is what makes a live census re-attributable to a deploy.
    """
    def get(path):
        with urllib.request.urlopen(f"{base}{path}", timeout=timeout) as r:
            return json.load(r)

    try:
        cfg, kitties, world = get("/config"), get("/kitties"), get("/world")
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}
    blob = json.dumps(cfg, sort_keys=True, separators=(",", ":")).encode()
    return {
        "base": base,
        "config_sha256": hashlib.sha256(blob).hexdigest(),
        "world": {k: cfg.get("world", {}).get(k)
                  for k in ("width", "height", "tick_ms", "seed")},
        "tick": world.get("tick"),
        "roster": [{"id": k["id"], "name": k["name"],
                    "behavior": k.get("behavior")} for k in kitties],
    }


if __name__ == "__main__":  # a quick look at what the header will say
    print(json.dumps(stamp(__file__), indent=1))
