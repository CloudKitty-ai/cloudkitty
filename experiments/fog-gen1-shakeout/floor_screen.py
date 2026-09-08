#!/usr/bin/env python3
"""Fog Gen 1 speaker-floor screen readout (#352, PREREG Part C):
welfare and communication over `[meow] announce_threshold` at the
pinned radius, read off bc-collect --trace rollouts.

    floor_screen.py ROLLOUT_DIR [ROLLOUT_DIR ...] [--out FILE]

Welfare per rollout comes from radius_screen.screen (watchdog entries,
distress episodes, safeguard crossings, need maxima, blind spans,
dispersion, friend-in-view), fed through a tap that also accumulates
the communication measures in the same pass (rates per 1,000 ticks):
  wants            emissions per kind, deduplicated on
                   (kitty_id, kind, tick) since recent_meows persists
                   a meow for the audible window
  heard share      share of want meows at or above the listener floor
                   (`[behavior] reply_intensity_floor`); a want under
                   the floor is nobody's to answer (owner 2026-09-08)
  informativeness  P(intensity >= 0.5 | want heard), the ruled
                   P(need >= 50 | want heard) bar, per kind and pooled
  reply rate       of heard wants of the four answerable kinds
                   (WANT_FOR_HERE), the share answered: a reply=true
                   here-word of the matching kind from another kitty
                   within the audible window after the want
  here-words       ambient (reply=false) and reply emissions per 1k

Streams trace.jsonl; thresholds, floors and the window come from the
recorded config, the radius from meta.json. Run from the repo root
with the exp-006 venv.
"""
import argparse
import bisect
import json
import sys
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(HERE.parent / "attn-oracle-2026-08-15"))

from obs_layout_v5 import WANT_FOR_HERE  # noqa: E402
from radius_screen import screen, stream_snapshots  # noqa: E402
from schema_check import audible  # noqa: E402

HERE_FOR_WANT = {w: h for h, w in WANT_FOR_HERE.items()}
INFORMATIVE = 0.5


class CommsTap:
    """Iterator pass-through that collects each meow once."""

    def __init__(self, snapshots):
        self.snapshots = snapshots
        self.seen = set()
        self.wants = []          # want_* meow dicts
        self.here_ambient = 0
        self.here_replies = {}   # here kind -> [tick, ...] (reply=true)

    def __iter__(self):
        for snap in self.snapshots:
            for m in snap["recent_meows"]:
                key = (m["kitty_id"], m["kind"], m["tick"])
                if key in self.seen:
                    continue
                self.seen.add(key)
                if m["kind"].startswith("want_"):
                    self.wants.append(m)
                elif m["kind"] in WANT_FOR_HERE:
                    if m["reply"]:
                        self.here_replies.setdefault(m["kind"], []).append(
                            (m["tick"], m["kitty_id"]))
                    else:
                        self.here_ambient += 1
            yield snap


def answered(want, here_replies, window):
    """A matching reply=true here-word from another kitty lands in
    (tick, tick+window)."""
    entries = here_replies.get(HERE_FOR_WANT[want["kind"]], [])
    i = bisect.bisect_right(entries, (want["tick"], float("inf")))
    while i < len(entries) and audible(want, entries[i][0], window):
        if entries[i][1] != want["kitty_id"]:
            return True
        i += 1
    return False


def comms(tap, floor, window, n):
    per_k = 1000.0 / n
    for ticks in tap.here_replies.values():
        ticks.sort()
    heard = [w for w in tap.wants if w["intensity"] >= floor]
    answerable = [w for w in heard if w["kind"] in HERE_FOR_WANT]
    hits = sum(answered(w, tap.here_replies, window) for w in answerable)
    by_kind = {}
    for w in tap.wants:
        by_kind.setdefault(w["kind"], []).append(w["intensity"])
    out = {
        "listener_floor": floor,
        "wants_per_1k": len(tap.wants) * per_k,
        "heard_share": len(heard) / len(tap.wants) if tap.wants else 0.0,
        "informative_heard": (sum(w["intensity"] >= INFORMATIVE
                                  for w in heard) / len(heard)
                              if heard else 0.0),
        "reply_rate": hits / len(answerable) if answerable else 0.0,
        "answerable_heard": len(answerable),
        "here_reply_per_1k": sum(len(t) for t in tap.here_replies.values())
        * per_k,
        "here_ambient_per_1k": tap.here_ambient * per_k,
        "want_kinds": {
            k: {"per_1k": len(v) * per_k,
                "heard_share": sum(x >= floor for x in v) / len(v),
                "informative_heard": (sum(x >= INFORMATIVE for x in v
                                          if x >= floor)
                                      / max(sum(x >= floor for x in v), 1))}
            for k, v in sorted(by_kind.items())},
    }
    return out


def read_rollout(d):
    d = Path(d)
    meta = json.loads((d / "meta.json").read_text())
    assert meta.get("trace"), f"{d} was not recorded with --trace"
    with open(meta["config"], "rb") as f:
        cfg = tomllib.load(f)
    floor = cfg["behavior"]["reply_intensity_floor"]
    window = cfg["meow"]["recent_window_ticks"]
    announce = cfg["meow"]["announce_threshold"]
    tap = CommsTap(stream_snapshots(d))
    res = screen(iter(tap), int(meta["vision_radius"]),
                 cfg["thresholds"]["distress"], cfg["thresholds"]["safeguard"],
                 announce)
    res["comms"] = comms(tap, floor, window, res["ticks"])
    res.update({"floor": announce, "rollout": str(d),
                "world_seed": meta["world_seed"], "config": meta["config"],
                "config_sha256": meta["config_sha256"]})
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rollouts", nargs="+", type=Path)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    rows = [read_rollout(d) for d in args.rollouts]
    print(f"{'floor':>6}{'seed':>8}{'wd':>4}{'dist/1k':>8}{'sg-eat':>7}"
          f"{'sg-drk':>7}{'want/1k':>8}{'heard':>7}{'info':>6}{'reply':>7}"
          f"{'hr/1k':>7}{'ha/1k':>7}{'blindH':>7}")
    for x in rows:
        c = x["comms"]
        print(f"{x['floor']:>6.0f}{x['world_seed']:>8}{x['watchdog_entries']:>4}"
              f"{x['distress_episodes_per_1k']:>8.2f}"
              f"{x['safeguard_crossings_per_1k']['eat']:>7.2f}"
              f"{x['safeguard_crossings_per_1k']['drink']:>7.2f}"
              f"{c['wants_per_1k']:>8.1f}{c['heard_share']:>7.3f}"
              f"{c['informative_heard']:>6.3f}{c['reply_rate']:>7.3f}"
              f"{c['here_reply_per_1k']:>7.1f}{c['here_ambient_per_1k']:>7.1f}"
              f"{x['blind_eat']['cat_ticks_per_1k']:>7.1f}")
    if args.out:
        args.out.write_text(json.dumps(rows, indent=2) + "\n")
        print(f"-> {args.out}")


if __name__ == "__main__":
    main()
