#!/usr/bin/env python3
"""Step-7 declared reads the shakeout instruments do not carry
(PREREG.md §"Rule 10 declaration" and §"Re-verifies"):

  beam   in-beam share of sleeping cat-ticks (the beam screen's primary
         read; finding 7's baseline was policy 5-10% vs anchor 29%)
  duets  play duets per 1k world ticks, and the consent-breach share:
         duet starts where a member was conscripted (play not its top
         need at t-1) while carrying a non-play need over the consent
         line (30) (the consent-transfer pair's read)
  e1     the comfort sweep's E1 shape: Biscuit's share of cat-ticks with
         a need >= 30 (eat/drink/sleep/cuddle) against the pooled roster
  groom  groom latency vs bath: per (observer, friend) spell where the
         friend is visible and dirty (bath >= 20), ticks from the
         spell's start to the first groom of that friend, censored at
         the spell's end (legality is reported beside, not required:
         legal means adjacent, so latency-to-legal is zero by construction) (the flat-vs-cand re-verify's
         second read; groom_cells.py carries the first)

    step7_reads.py PROBE_NPZ_OR_TRACE_DIR [...] [--json OUT]

Rows are per decision (probe .npz: obs/mask/tick/kitty/act/seed; trace
dir: obs/mask/tick/kitty/label .npy, one world). Kitty rows are by id,
ascending, excluding self (A15), as groom_cells.py reads them. The
activity one-hot order is the engine's (`observe.rs` push_activity):
Idle 0, Resting 1, Sleeping 2, Eating 3, Drinking 4, Playing 5,
Grooming 6; a duet is Playing with the partner flag set.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, "/Users/elizabethkelly/ai/cloudkitty/experiments/attn-oracle-2026-08-15")
import obs_layout_v5 as L  # noqa: E402

KB = dict(L.WIDTHS)["self"]
KW = L.KITTY_W
IDS = [1, 2, 3, 4, 5]
NAMES = {1: "Miso", 2: "Biscuit", 3: "Pumpkin", 4: "Kittybear", 5: "Clem"}
ACT_SLEEP, ACT_PLAY, ACT_GROOM = 2, 5, 6
CONSENT = np.float32(0.30)  # consent_line 30 / 100, compared in the observation's f32 (30.0 is AT the line, not over it)
DIRTY = 0.20         # announce threshold 20 / 100
E1_LINE = 0.30       # the comfort sweep's "polls >= 30"
E1_NEEDS = ["eat", "drink", "sleep", "cuddle"]
NON_PLAY = [i for i, n in enumerate(L.NEED_KINDS) if n != "play"]
PLAY = L.NEED_KINDS.index("play")
GROOM_MENU = 15      # GroomKitty index for row k is GROOM_MENU + k (groom_cells.py)


def load_rows(path):
    p = Path(path)
    if p.is_dir():
        return {"obs": np.load(p / "obs.npy").astype(np.float32),
                "mask": np.load(p / "mask.npy").astype(bool),
                "tick": np.load(p / "tick.npy").astype(np.int64),
                "kitty": np.load(p / "kitty.npy").astype(np.int64),
                "act": np.load(p / "label.npy").astype(np.int64),
                "seed": np.zeros(len(np.load(p / "tick.npy")), np.int64)}
    z = np.load(p)
    return {"obs": z["obs"].astype(np.float32), "mask": z["mask"][:, :L.N_ACT].astype(bool),
            "tick": z["tick"].astype(np.int64), "kitty": z["kitty"].astype(np.int64),
            "act": z["act"].astype(np.int64), "seed": z["seed"].astype(np.int64)}


def _self(rows):
    o = rows["obs"]
    act = o[:, L.SELF_ACTIVITY:L.SELF_ACTIVITY + 7].argmax(1)
    partnered = o[:, L.SELF_PARTNERED] > 0.5
    in_beam = o[:, L.SELF_IN_SUNBEAM] > 0.5
    needs = o[:, L.SELF_NEEDS:L.SELF_NEEDS + 6]
    return act, partnered, in_beam, needs


def beam_sleep_share(rows):
    """Per seat and pooled: sleeping cat-ticks, and the share of them on a sunbeam."""
    act, _, in_beam, _ = _self(rows)
    sleeping = act == ACT_SLEEP
    out = {}
    for k in IDS:
        sel = rows["kitty"] == k
        n = int((sleeping & sel).sum())
        out[NAMES[k]] = {"sleep_ticks": n,
                         "in_beam_share": float((sleeping & sel & in_beam).sum() / n) if n else None}
    n = int(sleeping.sum())
    out["pooled"] = {"sleep_ticks": n,
                     "in_beam_share": float((sleeping & in_beam).sum() / n) if n else None}
    return out


def _world_ticks(rows):
    return len(set(zip(rows["seed"].tolist(), rows["tick"].tolist())))


def duet_starts(rows):
    """Duet starts as (seed, tick, a, b) pairs with each member's max non-play
    need at the start tick. A start is a cat-tick that is a partnered
    Playing tick whose previous tick for that cat was not (or was with
    another partner); the pair is de-duplicated so each duet counts once."""
    act, partnered, _, needs = _self(rows)
    o = rows["obs"]
    duet = (act == ACT_PLAY) & partnered
    starts = {}
    for k in IDS:
        sel = np.flatnonzero(rows["kitty"] == k)
        order = sel[np.lexsort((rows["tick"][sel], rows["seed"][sel]))]
        prev_duet, prev_partner, prev_key, prev_needs = False, None, None, None
        for r in order:
            key = (int(rows["seed"][r]), int(rows["tick"][r]))
            partner = None
            if duet[r]:
                others = [j for j in IDS if j != k]
                for slot, j in enumerate(others):
                    b = KB + slot * KW
                    if o[r, b + L.ROW_PRESENT] > 0.5 and o[r, b + L.ROW_IS_TARGET] > 0.5:
                        partner = j
                consecutive = prev_key is not None and prev_key[0] == key[0] and prev_key[1] == key[1] - 1
                if partner is not None and not (consecutive and prev_duet and prev_partner == partner):
                    pair = (key[0], key[1], min(k, partner), max(k, partner))
                    # snapshots are post-apply: the need that was conscripted
                    # is the one at t-1 (groom-target/post-apply trap, 2026-08)
                    at = prev_needs if consecutive and prev_needs is not None else needs[r]
                    # a member is CONSCRIPTED when play was not its top need:
                    # the gate (spec 047, strict >) refuses a friend whose
                    # non-play need is over the line; the proposer's own
                    # needs are not the gate's business
                    non_play = float(at[NON_PLAY].max())
                    starts.setdefault(pair, {})[k] = non_play if non_play > float(at[PLAY]) else 0.0
            prev_duet, prev_partner, prev_key, prev_needs = bool(duet[r]), partner, key, needs[r]
    return starts


def duets(rows):
    starts = duet_starts(rows)
    per_1k = 1000.0 * len(starts) / max(1, _world_ticks(rows))
    over = [p for p, m in starts.items() if any(v > CONSENT for v in m.values())]
    needy = {}
    for p in over:
        for k, v in starts[p].items():
            if v > CONSENT:
                needy[NAMES[k]] = needy.get(NAMES[k], 0) + 1
    biscuit = [p for p in starts if 2 in p[2:]]
    return {"duets": len(starts), "duets_per_1k_ticks": per_1k,
            "consent_breaches": len(over),
            "consent_breach_share": len(over) / len(starts) if starts else None,
            "needy_member": needy,
            "biscuit_duets": len(biscuit),
            "biscuit_breach_share": (sum(1 for p in biscuit if p in set(over)) / len(biscuit)) if biscuit else None}


def e1(rows):
    """Biscuit's share of cat-ticks with need >= 30 vs the other four pooled, per need."""
    _, _, _, needs = _self(rows)
    out = {}
    for name in E1_NEEDS:
        i = L.NEED_KINDS.index(name)
        hi = needs[:, i] >= E1_LINE
        b = rows["kitty"] == 2
        out[name] = {"biscuit": float(hi[b].mean()), "roster": float(hi[~b].mean()),
                     "gap": float(hi[b].mean() - hi[~b].mean())}
    return out


def groom_latency(rows):
    """Spells of (observer i, friend row k) present & dirty & groom-legal;
    latency to the first GroomKitty(k) inside the spell, censored at its end."""
    o, m, act = rows["obs"], rows["mask"], rows["act"]
    lat, censored, spells = [], 0, 0
    legal_any, dirty_any = [0], [0]
    for k in IDS:
        sel = np.flatnonzero(rows["kitty"] == k)
        order = sel[np.lexsort((rows["tick"][sel], rows["seed"][sel]))]
        others = [j for j in IDS if j != k]
        for slot, _j in enumerate(others):
            b = KB + slot * KW
            cond = (o[order, b + L.ROW_PRESENT] > 0.5) & (o[order, b + L.ROW_NEEDS + 5] >= DIRTY)
            legal_any[0] += int((cond & m[order, GROOM_MENU + slot]).sum())
            dirty_any[0] += int(cond.sum())
            groomed = act[order] == GROOM_MENU + slot
            keys = list(zip(rows["seed"][order].tolist(), rows["tick"][order].tolist()))
            # state: None = off; int = open spell (start index); CLOSED =
            # groomed, stays closed until the condition breaks (a groom scene
            # runs several ticks with the friend still dirty; that is one spell)
            CLOSED = -1
            start = None
            for idx in range(len(order) + 1):
                on = idx < len(order) and cond[idx]
                contiguous = (0 < idx < len(order) and keys[idx][0] == keys[idx - 1][0]
                              and keys[idx][1] == keys[idx - 1][1] + 1)
                if not on or not contiguous:
                    if start is not None and start != CLOSED:
                        censored += 1
                    start = None
                if on and start is None:
                    start = idx
                    spells += 1
                if on and start not in (None, CLOSED) and groomed[idx]:
                    lat.append(idx - start)
                    start = CLOSED
    return {"spells": spells, "groomed": len(lat), "censored": censored,
            "dirty_visible_rows": dirty_any[0], "legal_share_of_dirty_visible": legal_any[0] / dirty_any[0] if dirty_any[0] else None,
            "groomed_share": len(lat) / spells if spells else None,
            "latency_median": float(np.median(lat)) if lat else None,
            "latency_mean": float(np.mean(lat)) if lat else None}


def read(path):
    rows = load_rows(path)
    return {"source": str(path), "rows": int(len(rows["tick"])), "world_ticks": _world_ticks(rows),
            "beam": beam_sleep_share(rows), "duets": duets(rows), "e1": e1(rows),
            "groom": groom_latency(rows)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sources", nargs="+")
    ap.add_argument("--json", type=Path, default=None)
    a = ap.parse_args()
    out = [read(s) for s in a.sources]
    for r in out:
        b, d, g = r["beam"]["pooled"], r["duets"], r["groom"]
        print(f"{Path(r['source']).name}: beam {b['in_beam_share']} of {b['sleep_ticks']} sleep ticks | "
              f"duets {d['duets']} ({d['duets_per_1k_ticks']:.1f}/1k ticks) breach {d['consent_breach_share']} | "
              f"groom spells {g['spells']} groomed {g['groomed_share']} lat med {g['latency_median']} | "
              f"E1 gaps " + " ".join(f"{k} {v['gap']:+.3f}" for k, v in r["e1"].items()))
    if a.json:
        a.json.write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
