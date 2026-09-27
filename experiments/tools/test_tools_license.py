"""Guard: every cargo package under experiments/tools/ declares a
license (PR #420 report-only finding, fixed 2026-09-27 at 3b77e97).

These crates are deliberately standalone (empty [workspace] tables,
outside the product workspace), so nothing inherits the repo's
Apache-2.0 — a new crate ships license-less unless its author adds
the line, and archive bundles (evidence-archive-ruling-2026-09-27.md)
may carry these tools or their outputs outside the repo.

Run from the repo root: python3 -B experiments/tools/test_tools_license.py
"""
import tomllib
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
tomls = sorted(TOOLS.glob("*/Cargo.toml"))
assert tomls, "no tool crates found — the glob or the layout moved"
missing = []
for t in tomls:
    with t.open("rb") as f:
        pkg = tomllib.load(f).get("package", {})
    if "license" not in pkg and "license-file" not in pkg:
        missing.append(str(t))
assert not missing, f"tool crates without a license declaration: {missing}"
print(f"test_tools_license ok ({len(tomls)} crates, all licensed)")
