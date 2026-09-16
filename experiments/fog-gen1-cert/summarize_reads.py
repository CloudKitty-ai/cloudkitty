#!/usr/bin/env python3
"""Step-7 read table: one row per (arm, probe index) from the existing
instruments' JSON (partb_read, phase2_read) and the trainer's probe lines.

    summarize_reads.py [--at 2599,2899,final] [--arms a,b,...]

Rates are per 1k decisions (30k rows per probe: 3 worlds x 2k ticks x 5
cats) unless the column says otherwise. Matched reads (PREREG §"Matched
reads") take the earlier plateau's index for a pair; this table prints
every index so the pairing is done by eye against the declared pairs.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "fog-gen1-shakeout" / "trainer"))
sys.path.insert(0, "/Users/elizabethkelly/ai/cloudkitty/experiments/attn-oracle-2026-08-15")
from data_fog import ACTION_NAMES  # noqa: E402
import obs_layout_v5 as L  # noqa: E402

CERT = Path(__file__).resolve().parent
READS = CERT / "results-raw" / "reads"
ARTS = CERT / "artifacts"
SLOTS = ["cand-s1", "cand-s2", "cand-s3", "cand-s4", "cand-s5", "cand-s6", "cand-s7",
         "twin-off", "plain-s1", "plain-s2", "flat-s1", "flat-s2", "flat-s3",
         "dose-lo-s1", "dose-lo-s2", "dose-hi-s1", "dose-hi-s2",
         "beam10-s1", "beam10-s2", "beam15-s1"]
GROOM_OTHER = [i for i, n in enumerate(ACTION_NAMES) if n.startswith("GroomKitty")]
GROOM_SELF = [i for i, n in enumerate(ACTION_NAMES) if n == "GroomSelf"]
PLAY_KITTY = [i for i, n in enumerate(ACTION_NAMES) if n.startswith("PlayKitty")]
MSG = ["silent"] + L.HEAD_KINDS  # msg_census layout: 16 = silent + 15 heads


def probe_lines(slot):
    out = {}
    for line in (ARTS / f"ppo-fog-{slot}" / "metrics.jsonl").open():
        if '"probe": true' in line:
            r = json.loads(line)
            out[r["update"]] = r
    return out


def final_index(slot):
    return max(int(p.name.split("-u")[1][:-4]) for p in (ARTS / f"ppo-fog-{slot}").glob("probe-u*.npz"))


def row(slot, u):
    pb = json.load((READS / f"partb-{slot}-u{u}.json").open())
    p2 = json.load((READS / f"phase2-{slot}-u{u}.json").open())
    pl = probe_lines(slot)[u]
    n = sum(sum(w["menu"]["chosen"]) for w in pb)
    chosen = [sum(w["menu"]["chosen"][i] for w in pb) for i in range(len(ACTION_NAMES))]
    msgs = [sum(w["msg_census"][i] for w in pb) for i in range(len(MSG))]
    k = 1000.0 / n
    m = lambda name: msgs[MSG.index(name)] * k  # noqa: E731
    return {
        "arm": slot, "u": u, "ticks_M": pl["ticks"] / 1e6,
        "nash": pl["nash"],
        "distress/1k": sum(w["distress_episodes_per_1k"] for w in pb) / len(pb),
        "wd": sum(w["watchdog_entries"] for w in pb),
        "max_age": max(w["max_distress_age"] for w in pb),
        "groom_other/1k": sum(chosen[i] for i in GROOM_OTHER) * k,
        "groom_self/1k": sum(chosen[i] for i in GROOM_SELF) * k,
        "play_kitty/1k": sum(chosen[i] for i in PLAY_KITTY) * k,
        "meow/1k": (n - msgs[0]) * k,
        "here/1k": sum(m(h) for h in L.HERE_KINDS),
        "want_cuddle/1k": m("want_cuddle"),
        "chirp+purr/1k": m("chirp") + m("purr"),
        "friend_in_view": sum(w["friend_in_view_share"] for w in pb) / len(pb),
        "beam_opp": sum(w["cosleep"]["beam_opportunity_ticks"] for w in p2),
        "beam_closed": sum(w["cosleep"]["closed"] for w in p2),
        "cuddle_approach": sum(w["want_cuddle"]["approaches"] for w in p2),
        "cuddle_unseen": sum(w["want_cuddle"]["unseen_speaker_events"] for w in p2),
    }


FMT = {"ticks_M": "{:.1f}", "nash": "{:.4f}", "distress/1k": "{:.2f}", "friend_in_view": "{:.3f}"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--at", default="2599,2899,final")
    ap.add_argument("--arms", default=",".join(SLOTS))
    ap.add_argument("--json", type=Path, default=None)
    a = ap.parse_args()
    rows = []
    for slot in a.arms.split(","):
        fin = final_index(slot)
        seen = set()
        for tok in a.at.split(","):
            u = fin if tok == "final" else int(tok)
            if u in seen or not (READS / f"partb-{slot}-u{u}.json").exists():
                continue
            seen.add(u)
            r = row(slot, u)
            r["final"] = u == fin
            rows.append(r)
    cols = [c for c in rows[0] if c != "final"]
    print("| " + " | ".join(cols) + " |")
    print("|" + "---|" * len(cols))
    for r in rows:
        cells = []
        for c in cols:
            v = r[c]
            s = FMT.get(c, "{:.1f}" if isinstance(v, float) else "{}").format(v)
            if c == "u" and r["final"]:
                s += "*"
            cells.append(s)
        print("| " + " | ".join(cells) + " |")
    print("\n`u*` = the arm's final probe (its plateau).")
    if a.json:
        a.json.write_text(json.dumps(rows, indent=1) + "\n")


if __name__ == "__main__":
    main()
