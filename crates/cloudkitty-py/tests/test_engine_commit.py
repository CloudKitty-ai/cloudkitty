"""ENGINE_COMMIT is a real build identity (owner kickoff 2026-10-16).

The cert harnesses stamp ``binding_engine = getattr(cloudkitty,
"ENGINE_COMMIT", None)``; from the binding's birth until this attribute
existed, that stamp was always None. These pins keep a packaging or module
regression from silently reverting to that from-birth failure mode.
"""

import re
import subprocess

import cloudkitty
import pytest


def test_engine_commit_is_present_and_shaped_like_a_build_identity():
    commit = cloudkitty.ENGINE_COMMIT
    assert isinstance(commit, str)
    assert re.fullmatch(r"[0-9a-f]{40}(-dirty)?|unknown", commit), commit


def test_engine_commit_is_not_the_unknown_fallback_on_a_repo_build():
    # CI and local dev both build inside the git checkout, so the fallback
    # firing here means the build script lost git, not that git was absent.
    assert cloudkitty.ENGINE_COMMIT != "unknown"


def test_engine_commit_matches_the_checked_out_head():
    # The staleness guard (PR #452 review, finding 4): a binding rebuilt
    # after a commit must carry the NEW commit — the rerun-if watches in
    # build.rs are what this pins. Shape alone would let a stale stamp
    # pass forever. Skipped only where git itself is unavailable (the
    # "unknown" path, pinned separately above).
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True
    )
    if head.returncode != 0:
        pytest.skip("git unavailable: no HEAD to compare against")
    assert cloudkitty.ENGINE_COMMIT.removesuffix("-dirty") == head.stdout.strip()
