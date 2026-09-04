#!/usr/bin/env python3
"""Complete a CloudKitty config to 3.0 form (spec 049 FR-034, research R14).

3.0 configs state every section explicitly (FR-030): a missing section is
a load error naming it. This tool brings a pre-3.0 TOML forward by
inserting what it lacks, taken verbatim from a complete defaults file
(``config-3.0-defaults.toml`` beside this script -- the serialised
``Config::default()`` -- or ``--defaults PATH``), and never touching a key
the file already states. Comments and ordering of the existing text are
preserved: the tool appends sections and inserts keys; it does not rewrite.

What it does, per file:

* every top-level table in the defaults that the file lacks is appended,
  with its nested tables, exactly as the defaults text spells it;
* ``--require KEY=VALUE`` (e.g. ``meow.digest_window_ticks=30``): if the
  named section exists but lacks the key, the key is inserted right after
  the section header (a value for a section that is absent arrives with
  the appended section instead);
* ``--set KEY=VALUE`` (e.g. ``vision.radius=40``): overrides a value INSIDE
  an appended section (used for the arc-temporary world-covering radius);
  never changes a key the file already had.

``--check`` reports what would change and exits 1 if anything would.
Round-trip safety: the result is re-parsed with ``tomllib`` and must contain
every key of the input unchanged.

    python3 experiments/tools/complete_config_3.py [--check] \\
        [--require meow.digest_window_ticks=30] [--set vision.radius=40] \\
        FILE...
"""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
HEADER_RE = re.compile(r"^\s*\[\[?([A-Za-z0-9_.-]+)\]\]?\s*(#.*)?$")
FOREIGN_TABLES = {"rl", "plugins", "watchdog"}


def parse_kv(items: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for item in items:
        if "=" not in item:
            sys.exit(f"expected SECTION.KEY=VALUE, got {item!r}")
        key, value = item.split("=", 1)
        out[key.strip()] = value.strip()
    return out


def sections_of(text: str) -> list[tuple[str, int, int]]:
    """(header name, first line index, end line index exclusive) per header,
    in file order. The preamble before the first header is not a section."""
    lines = text.split("\n")
    heads = [(m.group(1), i) for i, l in enumerate(lines) if (m := HEADER_RE.match(l))]
    out = []
    for n, (name, start) in enumerate(heads):
        end = heads[n + 1][1] if n + 1 < len(heads) else len(lines)
        out.append((name, start, end))
    return out


def top_level(name: str) -> str:
    return name.split(".", 1)[0]


def defaults_blocks(defaults_text: str) -> dict[str, str]:
    """Top-level table name -> the verbatim text of that table and every
    nested table under it, in the defaults file's order."""
    lines = defaults_text.split("\n")
    blocks: dict[str, list[str]] = {}
    for name, start, end in sections_of(defaults_text):
        blocks.setdefault(top_level(name), []).extend(lines[start:end])
    return {k: "\n".join(v).rstrip("\n") + "\n" for k, v in blocks.items()}


def apply_sets(block: str, table: str, sets: dict[str, str]) -> str:
    for key, value in sets.items():
        sect, _, k = key.rpartition(".")
        if sect != table:
            continue
        pattern = re.compile(rf"^(\s*{re.escape(k)}\s*=\s*)(.*?)(\s*(#.*)?)$", re.M)
        block, n = pattern.subn(rf"\g<1>{value}\g<3>", block, count=1)
        if n != 1:
            sys.exit(f"--set {key}: key not present in the defaults block for [{table}]")
    return block


def complete(text: str, defaults_text: str, require: dict[str, str], sets: dict[str, str]) -> tuple[str, list[str]]:
    changes: list[str] = []
    lines = text.split("\n")
    present = {name for name, _, _ in sections_of(text)}
    present_top = {top_level(n) for n in present}
    parsed = tomllib.loads(text)

    # 1. required keys inside sections the file already has
    for key, value in require.items():
        sect, _, k = key.rpartition(".")
        if sect not in present:
            continue  # arrives with the appended section (or is not a table in this file)
        node = parsed
        for part in sect.split("."):
            node = node.get(part, {}) if isinstance(node, dict) else {}
        if isinstance(node, dict) and k in node:
            continue
        # insert after the LAST header line of that exact section name
        # (a section may not repeat, but be safe)
        idx = max(i for i, l in enumerate(lines) if (m := HEADER_RE.match(l)) and m.group(1) == sect)
        lines.insert(idx + 1, f"{k} = {value}")
        changes.append(f"insert [{sect}] {k} = {value}")

    # 2. missing top-level tables, appended verbatim from the defaults --
    #    placed before the first foreign table ([rl], [plugins], [watchdog])
    #    so engine law stays together, at EOF otherwise. The roster
    #    ([[kitty]]) is never appended: every world config states its own.
    blocks = defaults_blocks(defaults_text)
    insert_at = len(lines)
    for name, start, _ in sections_of("\n".join(lines)):
        if top_level(name) in FOREIGN_TABLES:
            insert_at = start
            break
    appended: list[str] = []
    for table, block in blocks.items():
        if table in present_top or table == "kitty":
            continue
        block = apply_sets(block, table, sets)
        appended.extend(block.rstrip("\n").split("\n"))
        appended.append("")
        changes.append(f"append [{table}]")
    if appended:
        if insert_at > 0 and lines[insert_at - 1].strip():
            appended.insert(0, "")
        lines[insert_at:insert_at] = appended

    out = "\n".join(lines)
    if not out.endswith("\n"):
        out += "\n"
    return out, changes


def check_roundtrip(before: str, after: str) -> None:
    a = tomllib.loads(before)
    b = tomllib.loads(after)

    def contained(x, y, path="") -> None:
        if isinstance(x, dict):
            for k, v in x.items():
                if k not in y:
                    sys.exit(f"round-trip lost {path}{k}")
                contained(v, y[k], f"{path}{k}.")
        elif x != y:
            sys.exit(f"round-trip changed {path[:-1]}: {x!r} -> {y!r}")

    contained(a, b)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+", type=Path)
    ap.add_argument("--defaults", type=Path, default=HERE / "config-3.0-defaults.toml")
    ap.add_argument("--require", action="append", default=[], metavar="SECTION.KEY=VALUE")
    ap.add_argument("--set", action="append", default=[], metavar="SECTION.KEY=VALUE")
    ap.add_argument("--check", action="store_true", help="report, change nothing, exit 1 if anything would change")
    args = ap.parse_args()

    defaults_text = args.defaults.read_text()
    tomllib.loads(defaults_text)  # the defaults must themselves parse
    require = parse_kv(args.require)
    sets = parse_kv(args.set)

    would_change = 0
    for path in args.files:
        before = path.read_text()
        after, changes = complete(before, defaults_text, require, sets)
        if not changes:
            continue
        would_change += 1
        check_roundtrip(before, after)
        print(f"{path}: " + "; ".join(changes))
        if not args.check:
            path.write_text(after)
    if args.check and would_change:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
