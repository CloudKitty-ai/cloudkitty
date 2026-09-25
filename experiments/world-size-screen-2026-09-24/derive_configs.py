"""Derive the world-size screen's seven configs from anchor-b3
(PREREG.md, frozen 2026-09-24): only world.width, world.height and the
five element min/max pairs move; every other byte of the source file
survives verbatim. Each derived config is tomllib-parsed, deep-diffed
against the source (exactly the declared keys may differ), loaded once
in ParallelEnv, and its SHA-256 printed.
"""
import hashlib
import re
import sys
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "fog-gen1-cert" / "anchor-b3.toml"

# The PREREG table, verbatim: name -> (size, {element: (min, max)})
CONFIGS = {
    "size28": (28, {"water": (14, 18), "chow": (12, 16), "bug": (6, 14), "greeble": (2, 6), "sunbeam": (8, 10)}),
    "size40": (40, {"water": (28, 36), "chow": (24, 32), "bug": (12, 28), "greeble": (4, 12), "sunbeam": (16, 20)}),
    "size100": (100, {"water": (175, 225), "chow": (150, 200), "bug": (75, 175), "greeble": (25, 75), "sunbeam": (100, 125)}),
    "size40-d2": (40, {"water": (14, 18), "chow": (12, 16), "bug": (6, 14), "greeble": (2, 6), "sunbeam": (8, 10)}),
    "size40-d4": (40, {"water": (7, 9), "chow": (6, 8), "bug": (3, 7), "greeble": (1, 3), "sunbeam": (4, 5)}),
    "size100-d2": (100, {"water": (88, 113), "chow": (75, 100), "bug": (38, 88), "greeble": (13, 38), "sunbeam": (50, 63)}),
    "size100-d4": (100, {"water": (44, 56), "chow": (38, 50), "bug": (19, 44), "greeble": (6, 19), "sunbeam": (25, 31)}),
}
ELEMENTS = ("water", "chow", "bug", "greeble", "sunbeam")


def patch(text, size, counts):
    out, section = [], None
    for line in text.splitlines(keepends=True):
        header = re.match(r"\[([\w.]+)\]", line.strip())
        if header:
            section = header.group(1)
        m = re.match(r"^(width|height|min|max)\s*=\s*\d+\s*$", line.strip())
        if m:
            key = m.group(1)
            if section == "world" and key in ("width", "height"):
                line = f"{key} = {size}\n"
            elif section and section.startswith("elements.") and key in ("min", "max"):
                el = section.split(".", 1)[1]
                if el in counts:
                    line = f"{key} = {counts[el][key == 'max']}\n"
        out.append(line)
    return "".join(out)


def deep_diff(a, b, path=""):
    diffs = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            diffs += deep_diff(a.get(k), b.get(k), f"{path}.{k}".lstrip("."))
    elif a != b:
        diffs.append(path)
    return diffs


def main():
    import cloudkitty
    src_text = SRC.read_text()
    src = tomllib.loads(src_text)
    for name, (size, counts) in CONFIGS.items():
        text = patch(src_text, size, counts)
        dst = HERE / f"{name}.toml"
        dst.write_text(text)
        doc = tomllib.loads(text)
        allowed = {"world.width", "world.height"} | {
            f"elements.{el}.{k}" for el in ELEMENTS for k in ("min", "max")}
        diffs = set(deep_diff(src, doc))
        assert diffs <= allowed, (name, sorted(diffs - allowed))
        assert doc["world"]["width"] == doc["world"]["height"] == size, name
        for el in ELEMENTS:
            assert (doc["elements"][el]["min"], doc["elements"][el]["max"]) == counts[el], (name, el)
        env = cloudkitty.ParallelEnv(str(dst), horizon=4)
        env.reset(seed=1)
        sha = hashlib.sha256(dst.read_bytes()).hexdigest()
        print(f"{name}.toml sha256 {sha}")


if __name__ == "__main__":
    main()
