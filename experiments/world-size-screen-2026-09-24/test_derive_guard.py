"""Guard for the derived world-size configs. python -B test_derive_guard.py

Independent of derive_configs.py's own table: the expected sizes and
element counts are parsed from the FROZEN PREREG.md table, and each
derived toml is deep-diffed against anchor-b3 — exactly world.width,
world.height and the five element min/max pairs may differ, and they
must equal the prereg's numbers.
"""
import re
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "fog-gen1-cert" / "anchor-b3.toml"
ELEMENTS = ("water", "chow", "bug", "greeble", "sunbeam")


def prereg_table():
    rows = {}
    for line in (HERE / "PREREG.md").read_text().splitlines():
        m = re.match(r"\| (size[\w-]+)\.toml \| (\d+)×\d+ \| [\d/]+ \| (.+) \|$", line.strip())
        if not m:
            continue
        name, size, rest = m.group(1), int(m.group(2)), m.group(3)
        pairs = [tuple(int(x) for x in cell.strip().split("/")) for cell in rest.split("|")]
        assert len(pairs) == 5, (name, pairs)
        rows[name] = (size, dict(zip(ELEMENTS, pairs)))
    assert len(rows) == 7, sorted(rows)
    return rows


def deep_diff(a, b, path=""):
    diffs = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            diffs += deep_diff(a.get(k), b.get(k), f"{path}.{k}".lstrip("."))
    elif a != b:
        diffs.append(path)
    return diffs


def main():
    src = tomllib.loads(SRC.read_text())
    allowed = {"world.width", "world.height"} | {
        f"elements.{el}.{k}" for el in ELEMENTS for k in ("min", "max")}
    for name, (size, counts) in prereg_table().items():
        doc = tomllib.loads((HERE / f"{name}.toml").read_text())
        extra = sorted(set(deep_diff(src, doc)) - allowed)
        assert not extra, f"{name}: keys moved beyond the declared set: {extra}"
        assert doc["world"]["width"] == size and doc["world"]["height"] == size, \
            f"{name}: size {doc['world']['width']}x{doc['world']['height']} != {size}"
        for el in ELEMENTS:
            got = (doc["elements"][el]["min"], doc["elements"][el]["max"])
            assert got == counts[el], f"{name} {el}: {got} != prereg {counts[el]}"
        cap = (size * size) // 32
        for el in ELEMENTS:
            assert doc["elements"][el]["max"] <= cap, f"{name} {el}: max over the engine cap {cap}"
    print("ok: 7 configs match the frozen prereg table; only declared keys moved")


if __name__ == "__main__":
    main()
