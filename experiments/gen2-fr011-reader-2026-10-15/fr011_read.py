#!/usr/bin/env python3
"""FR-011 served-world reader — the corpus INVESTIGATE row's consumer.

Reads a SERVING LOG (the server's stdout, where the fmt subscriber
writes) and extracts every stuck-detector fire record: target
`cloudkitty_server::stuck`, message "stuck fire" (WARN, enforce) or
"stuck fire (observe-only)" (INFO, observe), flattened to the contract
field names — specs/061-stuck-detector/contracts/stuck-detector.md §3.
Never a bc-collect column: fires exist only on the served world
(Product's 061 review, item 10a).

Why the enforce tick list matters (their item 9): on an enforce-mode
fire tick the applied action is the scripted brain's substitute, but
the tick is stamped Provenance::PolicyMade — any battery or provenance
read over a served stretch must treat exactly those (kitty, tick)
pairs as scripted turns. `enforce_fire_ticks` per kitty is that
correction list.

Parsing law (what the shipped formatter actually emits, verified on
captured serving logs — the contract §3 prose example differs in value
shapes):
  - ANSI escape sequences are present even when piped; stripped first.
  - Values are the emit site's Display/Debug renderings: `name` and
    `armed_need` unquoted, `mode` quoted, an absent message is empty,
    and action values may contain SPACES AND BRACES
    (`substitute=Sleep { with: Some(3) }`) — so fields are parsed by
    the contract's fixed key order, each value running to the next
    key's anchor, never by whitespace split.
  - A line carrying the target and a fire message that fails the
    field parse is a HARD ERROR naming the line — a half-read record
    is a silent undercount of scripted turns.
  - WARN must carry mode="enforce" and INFO mode="observe"; a
    mismatch is a hard error (the level/mode pairing is contract §3).

Usage:
  fr011_read.py [label=]serving.log [[label=]more.log ...] \
      --out fires.json [--md]

Non-monotonic ticks within one log (a restart, two boots captured into
one file) are legal and flagged per log as `ticks_nonmonotonic`; the
records keep file order.
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

# Contract §3, in emit order. A rename or reorder upstream is a
# breaking change and takes a spec touch — this list IS the contract.
FIELDS = [
    "kitty", "name", "tick", "mode", "window", "anchor_x", "anchor_y",
    "confined_span", "armed_need", "need_value", "proposal_replaced",
    "replaced_message", "substitute", "substitute_message",
]
INT_FIELDS = {"kitty", "tick", "window", "anchor_x", "anchor_y",
              "confined_span"}

ANSI = re.compile(r"\x1b\[[0-9;]*m")
FIRE = re.compile(
    r"^\S+\s+(WARN|INFO)\s+cloudkitty_server::stuck:\s+"
    r"stuck fire(?: \(observe-only\))?\s+(?=kitty=)"
)
TARGET = "cloudkitty_server::stuck"


def parse_fire_line(line, where):
    """One fire line -> dict of the 14 contract fields, or SystemExit."""
    m = FIRE.match(line)
    if m is None:
        raise SystemExit(
            f"{where}: a {TARGET} fire line did not match the line shape "
            f"(contract §3): {line!r}")
    level, rest = m.group(1), line[m.end():].rstrip("\n")
    record = {}
    pos = 0
    for i, key in enumerate(FIELDS):
        anchor = f"{key}="
        if not rest.startswith(anchor, pos):
            raise SystemExit(
                f"{where}: contract field {key!r} missing or out of order "
                f"at {rest[pos:pos + 40]!r} — a half-read fire record "
                f"undercounts scripted turns; refusing")
        start = pos + len(anchor)
        if i + 1 < len(FIELDS):
            nxt = rest.find(f" {FIELDS[i + 1]}=", start)
            if nxt < 0:
                raise SystemExit(
                    f"{where}: contract field {FIELDS[i + 1]!r} missing "
                    f"after {key!r}: {rest[start:start + 60]!r}")
            value, pos = rest[start:nxt], nxt + 1
        else:
            value = rest[start:]
        record[key] = value
    for key in INT_FIELDS:
        record[key] = int(record[key])
    record["need_value"] = float(record["need_value"])
    record["mode"] = record["mode"].strip('"')
    expected = {"WARN": "enforce", "INFO": "observe"}[level]
    if record["mode"] != expected:
        raise SystemExit(
            f"{where}: level {level} with mode={record['mode']!r} — the "
            f"contract pairs WARN/enforce and INFO/observe; refusing")
    return record


def read_log(path):
    records = []
    for n, raw in enumerate(Path(path).read_text().splitlines(), 1):
        line = ANSI.sub("", raw)
        if TARGET not in line or "stuck fire" not in line:
            continue
        records.append(parse_fire_line(line, f"{path}:{n}"))
    return records


def summarize(records):
    by_mode = Counter(r["mode"] for r in records)
    per_kitty = {}
    for r in records:
        k = per_kitty.setdefault(r["kitty"], {
            "name": r["name"], "enforce_fires": 0, "observe_fires": 0,
            "enforce_fire_ticks": [], "observe_fire_ticks": [],
            "armed_need": Counter(), "substitute_heads": Counter(),
            "max_need_value": 0.0, "max_confined_span": 0,
        })
        k[f"{r['mode']}_fires"] += 1
        k[f"{r['mode']}_fire_ticks"].append(r["tick"])
        k["armed_need"][r["armed_need"]] += 1
        k["substitute_heads"][r["substitute"].split(" ")[0]] += 1
        k["max_need_value"] = max(k["max_need_value"], r["need_value"])
        k["max_confined_span"] = max(k["max_confined_span"],
                                     r["confined_span"])
    for k in per_kitty.values():
        k["enforce_fire_ticks"].sort()
        k["observe_fire_ticks"].sort()
        k["armed_need"] = dict(k["armed_need"].most_common())
        k["substitute_heads"] = dict(k["substitute_heads"].most_common())
    ticks = [r["tick"] for r in records]
    return {
        "fires": {"total": len(records),
                  "enforce": by_mode.get("enforce", 0),
                  "observe": by_mode.get("observe", 0)},
        "ticks_nonmonotonic": any(b < a for a, b in zip(ticks, ticks[1:])),
        "per_kitty": {str(k): v for k, v in sorted(per_kitty.items())},
    }


def investigate_rows(logs):
    rows = []
    for label, summary in logs.items():
        for kid, k in summary["per_kitty"].items():
            rows.append({
                "log": label, "kitty": int(kid), "name": k["name"],
                "enforce_fires": k["enforce_fires"],
                "observe_fires": k["observe_fires"],
                "first_fire_tick": min(k["enforce_fire_ticks"]
                                       + k["observe_fire_ticks"]),
                "last_fire_tick": max(k["enforce_fire_ticks"]
                                      + k["observe_fire_ticks"]),
                "top_armed_need": next(iter(k["armed_need"])),
                "max_need_value": k["max_need_value"],
                "max_confined_span": k["max_confined_span"],
            })
    return rows


def markdown(rows):
    cols = ["log", "kitty", "name", "enforce_fires", "observe_fires",
            "first_fire_tick", "last_fire_tick", "top_armed_need",
            "max_need_value", "max_confined_span"]
    out = ["| " + " | ".join(cols) + " |",
           "|" + "---|" * len(cols)]
    for r in rows:
        out.append("| " + " | ".join(str(r[c]) for c in cols) + " |")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("logs", nargs="+", metavar="[label=]serving.log")
    ap.add_argument("--out", required=True)
    ap.add_argument("--md", action="store_true")
    args = ap.parse_args(argv)
    logs = {}
    for spec in args.logs:
        label, _, path = spec.rpartition("=")
        path = path or spec
        label = label or Path(path).stem
        if label in logs:
            raise SystemExit(f"duplicate log label {label!r}")
        logs[label] = summarize(read_log(path))
        logs[label]["path"] = str(path)
    result = {"contract":
              "specs/061-stuck-detector/contracts/stuck-detector.md §3",
              "logs": logs, "investigate_rows": investigate_rows(logs)}
    Path(args.out).write_text(json.dumps(result, indent=1) + "\n")
    if args.md:
        print(markdown(result["investigate_rows"]))
    for label, s in logs.items():
        print(f"{label}: {s['fires']['total']} fires "
              f"(enforce {s['fires']['enforce']}, "
              f"observe {s['fires']['observe']})", file=sys.stderr)
    return result


if __name__ == "__main__":
    main()
