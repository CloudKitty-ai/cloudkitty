#!/usr/bin/env python3
"""Free-register baseline (PREREG.md): emission census and listener uptake
for mew / chirp / purr on a probe-format trace that carries the message
head (obs, tick, kitty, act, msg, seed; `add_msg.py` supplies msg).

    free_register_read.py TRACE_NPZ [--window 10] [--digest 30] [--out JSON]

Uptake: event = (S says w at t, listener L != S), split by whether L sees
S at t. Outcomes over t+1..t+window: approach (Euclidean distance to S
falls >= 2, where the distance at t is >= 2), a proposal targeting S,
echo (L says w), any speech. Control rows = (L, t') with no other cat
saying w in [t' - digest + 1, t' + window], keyed by (L, S, sees, L's
activity class); ratio = observed / sum of matched control rates.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "attn-oracle-2026-08-15"))
import obs_layout_v5 as L  # noqa: E402

W = 20.0
KITTY_BASE = dict(L.WIDTHS)["self"]
KITTY_W = L.KITTY_W
ACTIVITY = ["idle", "rest", "sleep", "eat", "drink", "play", "groom"]
# Menu 39 (obs_layout_v5): the kitty-targeted entries, four slots each.
KITTY_TARGET_BASES = [5, 10, 15, 25, 34]  # RestWith, SleepWith, GroomKitty, ChaseKitty, PlayKitty
WORDS = ["mew", "chirp", "purr", "want_cuddle", "want_play"]


def head_index(word):
    """Message-head index of a word: Silent is 0, kinds follow HEAD_KINDS."""
    return L.HEAD_KINDS.index(word) + 1


def rows_by_seed(z):
    out = {}
    for s in np.unique(z["seed"]):
        m = z["seed"] == s
        order = np.lexsort((z["kitty"][m], z["tick"][m]))
        out[int(s)] = {k: z[k][m][order] for k in z.files}
    return out


def per_tick(rows):
    """Per-tick arrays with the kitty axis in id order: ids, pos[T,K,2],
    said[T,K] (head index), actcls[T,K], present[T,L,S] (L sees S),
    target[T,K] (kitty-axis index the row's action targets, else -1),
    top[T,K] (top need, 0..1)."""
    ticks, kitties, obs, act, msg = rows["tick"], rows["kitty"], rows["obs"], rows["act"], rows["msg"]
    ids = np.unique(kitties)
    uticks = np.unique(ticks)
    K, T = len(ids), len(uticks)
    tix = {t: n for n, t in enumerate(uticks)}
    kix = {k: n for n, k in enumerate(ids)}
    pos = np.zeros((T, K, 2))
    said = np.zeros((T, K), int)
    actcls = np.zeros((T, K), int)
    top = np.zeros((T, K))
    present = np.zeros((T, K, K), bool)
    target = np.full((T, K), -1, int)
    for r in range(len(ticks)):
        t, i = tix[ticks[r]], kix[kitties[r]]
        row = obs[r]
        pos[t, i] = np.round(row[L.SELF_POS:L.SELF_POS + 2] * W)
        said[t, i] = msg[r]
        actcls[t, i] = int(np.argmax(row[L.SELF_ACTIVITY:L.SELF_ACTIVITY + 7]))
        top[t, i] = float(row[L.SELF_NEEDS:L.SELF_NEEDS + 6].max())
        others = [k for k in ids if k != kitties[r]]  # slot k = k-th other kitty by id (partb/phase2 convention)
        for slot, oid in enumerate(others):
            if row[KITTY_BASE + slot * KITTY_W + L.ROW_PRESENT] > 0:
                present[t, i, kix[oid]] = True
        a = int(act[r])
        for base in KITTY_TARGET_BASES:
            if base <= a < base + 4 and a - base < len(others):
                target[t, i] = kix[others[a - base]]
    return ids, pos, said, actcls, present, target, top


def window_outcomes(pos, said, target, window):
    """Outcomes over t+1..t+window for every (t, L, S), t < T - window:
    d0[t,L,S], approach[t,L,S], eligible[t,L,S], proposal[t,L,S],
    speech[t,L]; echo needs the word and is computed per word."""
    T, K = said.shape
    Tv = T - window
    d = np.linalg.norm(pos[:, :, None, :] - pos[:, None, :, :], axis=-1)
    dmin = np.full((Tv, K, K), np.inf)
    proposal = np.zeros((Tv, K, K), bool)
    speech = np.zeros((Tv, K), bool)
    for u in range(1, window + 1):
        dmin = np.minimum(dmin, d[u:u + Tv])
        proposal |= target[u:u + Tv][:, :, None] == np.arange(K)[None, None, :]
        speech |= said[u:u + Tv] != 0
    d0 = d[:Tv]
    return d0, (d0 - dmin >= 2.0), (d0 >= 2.0), proposal, speech


def echo_outcome(said, w, window):
    T, K = said.shape
    Tv = T - window
    out = np.zeros((Tv, K), bool)
    for u in range(1, window + 1):
        out |= said[u:u + Tv] == w
    return out


def word_masks(said, w, window, digest):
    """(event[t,L,S], control[t,L,S]) for word w, t < T - window."""
    T, K = said.shape
    Tv = T - window
    is_w = said == w
    # any other cat said w in [t - digest + 1, t + window]
    tainted = np.zeros((Tv, K), bool)
    for t in range(Tv):
        lo, hi = max(0, t - digest + 1), min(T, t + window + 1)
        spoke = is_w[lo:hi].any(axis=0)  # per cat
        tainted[t] = spoke.sum() - spoke > 0  # some cat other than L
    off = ~np.eye(K, dtype=bool)[None]
    event = is_w[:Tv][:, None, :] & off
    control = ~tainted[:, :, None] & off
    return event, control


def ratio_read(event, control, outcome, eligible, present, actcls):
    """observed / expected for one outcome[t,L,S] (bool), matched on key
    (L, S, sees, activity). Returns dict with observed, expected, events,
    dropped (events whose key has no control row)."""
    Tv, K, _ = event.shape
    Lax = np.arange(K)[None, :, None]
    Sax = np.arange(K)[None, None, :]
    key = ((Lax * K + Sax) * 2 + present[:Tv].astype(int)) * 7 + actcls[:Tv][:, :, None]
    key = np.broadcast_to(key, event.shape)
    nkeys = K * K * 2 * 7
    cm = control & eligible
    c_n = np.bincount(key[cm], minlength=nkeys)
    c_hit = np.bincount(key[cm & outcome], minlength=nkeys)
    rate = np.where(c_n > 0, c_hit / np.maximum(c_n, 1), np.nan)
    em = event & eligible
    ek = key[em]
    has = c_n[ek] > 0
    observed = int((outcome[em] & has).sum())
    expected = float(np.nansum(rate[ek][has]))
    return {"events": int(has.sum()), "dropped": int((~has).sum()), "observed": observed, "expected": expected,
            "ratio": (observed / expected) if expected > 0 else None}


def read_seed(rows, window, digest):
    ids, pos, said, actcls, present, target, top = per_tick(rows)
    T, K = said.shape
    Tv = T - window
    d0, approach, eligible, proposal, speech = window_outcomes(pos, said, target, window)
    allT = np.ones_like(approach)
    out = {"emission": {}, "uptake": {}, "rows": int(T * K), "all_rows_top_need_mean": float(top.mean())}
    for word in WORDS:
        w = head_index(word)
        m = said == w
        out["emission"][word] = {
            "per_seat_per_1k": [round(1000 * m[:, i].mean(), 2) for i in range(K)],
            "activity_mix": {a: round(float((actcls[m] == j).mean()), 3) if m.any() else None for j, a in enumerate(ACTIVITY)},
            "top_need_mean": float(top[m].mean()) if m.any() else None,
            "n": int(m.sum()),
        }
        event, control = word_masks(said, w, window, digest)
        echo = echo_outcome(said, w, window)
        out["uptake"][word] = {}
        for vis_name, vis in (("visible", present[:Tv]), ("unseen", ~present[:Tv])):
            ev = event & vis
            ct = control & vis
            out["uptake"][word][vis_name] = {
                "approach": ratio_read(ev, ct, approach, eligible, present, actcls),
                "proposal_to_speaker": ratio_read(ev, ct, proposal, allT, present, actcls),
                "echo": ratio_read(ev, ct, np.broadcast_to(echo[:, :, None], ev.shape), allT, present, actcls),
                "any_speech": ratio_read(ev, ct, np.broadcast_to(speech[:, :, None], ev.shape), allT, present, actcls),
            }
    return out


def pool(per_seed):
    """Pooled observed/expected over seeds, per-seed ratio lists, band reading."""
    seeds = sorted(per_seed)
    res = {"seeds": seeds, "emission": {}, "uptake": {}}
    for word in WORDS:
        n = sum(per_seed[s]["emission"][word]["n"] for s in seeds)
        rows = sum(per_seed[s]["rows"] for s in seeds)
        res["emission"][word] = {"per_1k": round(1000 * n / rows, 2), "n": n,
                                 "per_seat_per_1k": np.mean([per_seed[s]["emission"][word]["per_seat_per_1k"] for s in seeds], axis=0).round(2).tolist()}
        res["uptake"][word] = {}
        for vis in ("visible", "unseen"):
            res["uptake"][word][vis] = {}
            for oc in ("approach", "proposal_to_speaker", "echo", "any_speech"):
                rs = [per_seed[s]["uptake"][word][vis][oc] for s in seeds]
                obs_, exp_ = sum(r["observed"] for r in rs), sum(r["expected"] for r in rs)
                per = [r["ratio"] for r in rs]
                res["uptake"][word][vis][oc] = {"events": sum(r["events"] for r in rs), "dropped": sum(r["dropped"] for r in rs),
                                                "observed": obs_, "expected": round(exp_, 2),
                                                "ratio": round(obs_ / exp_, 3) if exp_ > 0 else None,
                                                "per_seed": [round(p, 3) if p is not None else None for p in per]}
    return res


def band(res):
    """PREREG reading per word: INERT / LEANING / ACTIVE off approach and
    proposal on both visibility classes."""
    out = {}
    for word in WORDS:
        verdict = "INERT"
        for vis in ("visible", "unseen"):
            for oc in ("approach", "proposal_to_speaker"):
                r = res["uptake"][word][vis][oc]
                if r["ratio"] is None:
                    verdict = "UNREAD"
                    continue
                if 0.8 <= r["ratio"] <= 1.25:
                    continue
                per = [p for p in r["per_seed"] if p is not None]
                one_side = len(per) == 5 and (all(p > 1 for p in per) or all(p < 1 for p in per))
                verdict = "ACTIVE" if one_side else ("LEANING" if verdict != "ACTIVE" else verdict)
        out[word] = verdict
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("trace", type=Path)
    ap.add_argument("--window", type=int, default=10)
    ap.add_argument("--digest", type=int, default=30)
    ap.add_argument("--out", type=Path, default=None)
    a = ap.parse_args()
    z = np.load(a.trace)
    per_seed = {s: read_seed(rows, a.window, a.digest) for s, rows in rows_by_seed(z).items()}
    res = pool(per_seed)
    res["reading"] = band(res)
    res["per_seed"] = {str(s): v for s, v in per_seed.items()}
    res["params"] = {"window": a.window, "digest": a.digest, "trace": str(a.trace)}
    print(f"== emission per 1k decisions (seats in id order); rows {sum(v['rows'] for v in per_seed.values())}")
    for word in WORDS:
        e = res["emission"][word]
        print(f"  {word:12s} {e['per_1k']:7.2f}  by seat {e['per_seat_per_1k']}  n {e['n']}")
    print("== uptake ratio observed/expected (events; per-seed)")
    for word in WORDS:
        for vis in ("visible", "unseen"):
            cells = []
            for oc in ("approach", "proposal_to_speaker", "echo", "any_speech"):
                r = res["uptake"][word][vis][oc]
                cells.append(f"{oc[:8]} {r['ratio'] if r['ratio'] is not None else 'n/a'} ({r['observed']}/{r['expected']}, n {r['events']})")
            print(f"  {word:12s} {vis:8s} " + "  ".join(cells))
        print(f"  {word:12s} -> {res['reading'][word]}")
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        json.dump(res, open(a.out, "w"), indent=1)
        print("wrote", a.out)


if __name__ == "__main__":
    main()
