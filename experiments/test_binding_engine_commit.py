#!/usr/bin/env python3
"""Guard: the lab binding's ENGINE_COMMIT is real and well-formed.

Every harness engine-identity stamp reads
getattr(cloudkitty, "ENGINE_COMMIT", None), and from the attribute's
birth (#452, d92a01b6) back to the first stamp site that default was
what every stamp carried: None, silently, for weeks. This guard makes
that regression loud — a packaging or build.rs change that drops the
attribute (or ships a malformed one) fails here, not in a None-valued
stamp nobody reads until an audit.

Shape, per #452 + its hardening 66a8eb6d: 40 lowercase hex, optional
"-dirty" (ENGINE-scoped: uncommitted changes under crates/ or the
workspace manifests; a FAILED dirty probe also stamps -dirty, never
clean — so -dirty is always acceptable here). "unknown" means git was
unavailable at build; a lab rebind always happens inside this repo, so
unknown is a broken probe and FAILS this guard.

Freshness is deliberately NOT asserted: the binding legitimately lags
main between rebuilds (the census-header staleness discipline owns
that question). When the stamp's commit exists locally and differs
from HEAD, the run prints the lag as information.

Run: experiments/exp-006-character-gen/.venv/bin/python -B <this file>
"""
import re
import subprocess
import sys
from pathlib import Path

ENGINE_RE = re.compile(r"^[0-9a-f]{40}(-dirty)?$")


def validate_engine_commit(value):
    """Return the list of problems with a stamp value; [] = well-formed."""
    problems = []
    if value is None:
        problems.append(
            "ENGINE_COMMIT is None — the getattr default; the attribute "
            "is missing from the binding (the from-birth regression)")
        return problems
    if not isinstance(value, str):
        problems.append(f"ENGINE_COMMIT is {type(value).__name__}, not str")
        return problems
    if value == "unknown":
        problems.append(
            "ENGINE_COMMIT is 'unknown' — git was unavailable at build; "
            "a lab rebind inside this repo must never produce it")
        return problems
    if not ENGINE_RE.fullmatch(value):
        problems.append(
            f"ENGINE_COMMIT {value!r} is not 40-hex with optional -dirty")
    return problems


def test_live_binding_attribute_is_well_formed():
    import cloudkitty
    value = getattr(cloudkitty, "ENGINE_COMMIT", None)
    problems = validate_engine_commit(value)
    assert problems == [], problems
    # Information, never an assert: does the stamp's commit exist here,
    # and does the binding lag HEAD?
    sha = value.removesuffix("-dirty")
    repo = Path(__file__).resolve().parents[1]
    known = subprocess.run(
        ["git", "-C", str(repo), "cat-file", "-e", f"{sha}^{{commit}}"],
        capture_output=True).returncode == 0
    head = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        capture_output=True, text=True).stdout.strip()
    print(f"  binding engine {value}"
          f"{' (unknown to this repo!)' if not known else ''}"
          f"{' — LAGS HEAD ' + head[:12] if known and sha != head else ''}")


def test_the_from_birth_bug_is_named():
    problems = validate_engine_commit(None)
    assert len(problems) == 1 and "getattr default" in problems[0], problems


def test_unknown_fails_in_repo():
    problems = validate_engine_commit("unknown")
    assert len(problems) == 1 and "unavailable at build" in problems[0]


def test_malformed_shapes_fail():
    for bad in ("d92a01b", "d92a01b6852fc6d4b28369ae00fe2444d285136g",
                "D92A01B6852FC6D4B28369AE00FE2444D285136C",
                "d92a01b6852fc6d4b28369ae00fe2444d285136c-DIRTY",
                "-dirty", "", 42):
        problems = validate_engine_commit(bad)
        assert problems, f"accepted malformed stamp {bad!r}"


def test_well_formed_shapes_pass():
    for good in ("d92a01b6852fc6d4b28369ae00fe2444d285136c",
                 "d92a01b6852fc6d4b28369ae00fe2444d285136c-dirty"):
        assert validate_engine_commit(good) == [], good


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok {name}")
    print(f"{sum(1 for n in globals() if n.startswith('test_'))} passed")
