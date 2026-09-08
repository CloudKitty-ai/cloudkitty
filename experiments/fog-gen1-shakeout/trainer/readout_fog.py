#!/usr/bin/env python3
"""Fog Gen 1 BC clone readout: the pre-declared bars on the held-out
rollouts (PREREG Part A, owner ruled).

  1. reply-here opportunity-use >= 0.50 per kind, read as the clone's
     masked-softmax mass on the here-word (the expectation of a sampled
     read; owner ruled 2026-09-08, #348: "0.5 is a reasonable
     threshold"). An opportunity is a held-out row where the here-word
     is legal and the source did not say a want (here-word-screen V4).
     A reply opportunity is one where the engine trace shows an audible
     want of the matching kind from another kitty, stamped at or above
     the listener floor (the responder's own predicate); the rest are
     ambient. Ambient use, the source's own use and the argmax read are
     reported beside it, not gated (the scripted rate is a teacher
     rate, #348).
  2. msg@1 >= 0.80 on rows where the source said a here-word.
  3. want emission per kind within +-15% of the source, kinds with
     >= 100 source rows only; thinner kinds are reported, not judged.

Needs --trace rollouts: the reply/ambient split reads trace.jsonl.
Writes <out>.json next to the printed tables. Run from the repo root
with the exp-006 venv.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(HERE.parent))
sys.path.insert(2, str(HERE.parents[1] / "attn-oracle-2026-08-15"))

from data_fog import HERE_MSG, MSG_NAMES, WANT, _is_val, load_rollout  # noqa: E402
from model_v5 import EntityPolicyV5  # noqa: E402
from obs_layout_v5 import N_ACT, WANT_FOR_HERE  # noqa: E402
from schema_check import audible, load_trace  # noqa: E402

USE_BAR, HERE_TOP1_BAR, WANT_TOL, WANT_MIN_ROWS = 0.50, 0.80, 0.15, 100


def load_clone(path):
    ck = torch.load(path, weights_only=False)
    model = EntityPolicyV5(**ck["hyper"])
    model.load_state_dict(ck["state_dict"])
    model.eval()
    return model


def msg_probs(model, obs, mask_msg, batch=8192):
    """Masked softmax over the message head, per row."""
    out = []
    with torch.no_grad():
        for i in range(0, obs.shape[0], batch):
            logits = model(torch.from_numpy(obs[i:i + batch]))[:, N_ACT:]
            legal = torch.from_numpy(mask_msg[i:i + batch])
            logits = logits.masked_fill(~legal, float("-inf"))
            out.append(torch.softmax(logits, 1).numpy())
    return np.concatenate(out)


def predict_msg(model, obs, mask_msg, batch=8192):
    """Masked argmax over the message head, as two_head_loss reports it."""
    return msg_probs(model, obs, mask_msg, batch).argmax(1)


def reply_flags(tr, tick, kitty):
    """Per here kind, per decision row: an audible want of
    WANT_FOR_HERE[kind] from another kitty, stamped at or above the
    listener floor, sits in the pre-decision snapshot of that tick (the
    scripted responder's own candidate predicate, behavior/mod.rs
    `reply_candidate`; schema_check A8). Floor unset = the responder
    never replies, so no row is a reply opportunity (owner 2026-09-08:
    a want under the floor is nobody's to answer, it reads as ambient)."""
    snap_at = {l["tick"]: l["snapshot"] for l in tr.lines}
    window = tr.window
    floor = tr.cfg["behavior"].get("reply_intensity_floor")
    flags = {kind: np.zeros(len(tick), bool) for kind in HERE_MSG.values()}
    if floor is None:
        return flags
    cache = {}
    for i, (t, k) in enumerate(zip(tick.tolist(), kitty.tolist())):
        if (t, k) not in cache:
            heard = {m["kind"] for m in snap_at[t]["recent_meows"]
                     if m["kitty_id"] != k and m["intensity"] >= floor
                     and audible(m, t, window)}
            cache[(t, k)] = {kind: WANT_FOR_HERE[kind] in heard
                             for kind in flags}
        for kind, hit in cache[(t, k)].items():
            flags[kind][i] = hit
    return flags


def readout(rollouts, model):
    obs = np.concatenate([r.obs for r in rollouts])
    mask_msg = np.concatenate([r.mask_msg for r in rollouts]).astype(bool)
    label_msg = np.concatenate([r.label_msg for r in rollouts])
    probs = msg_probs(model, obs, mask_msg)
    pred = probs.argmax(1)
    n = len(label_msg)
    not_want = ~np.isin(label_msg, WANT)
    per_rollout = [reply_flags(load_trace(r.path), r.tick, r.kitty)
                   for r in rollouts]

    use = {}
    for idx, kind in HERE_MSG.items():
        opp = mask_msg[:, idx] & not_want
        reply = np.concatenate([f[kind] for f in per_rollout])
        row = {}
        for split, sel in (("reply", opp & reply), ("ambient", opp & ~reply)):
            m = int(sel.sum())
            row[split] = {"n": m,
                          "use": float(probs[sel, idx].mean()) if m else None,
                          "argmax_use": float((pred[sel] == idx).mean()) if m else None,
                          "source_use": float((label_msg[sel] == idx).mean())
                          if m else None}
        use[kind] = row

    here_rows = np.isin(label_msg, list(HERE_MSG))
    here_top1 = float((pred[here_rows] == label_msg[here_rows]).mean())

    want = {}
    for idx in WANT:
        src, prd = int((label_msg == idx).sum()), int((pred == idx).sum())
        want[MSG_NAMES[idx]] = {
            "source": src, "pred": prd,
            "ratio": prd / src if src else None,
            "judged": src >= WANT_MIN_ROWS}

    per_1k = {MSG_NAMES[i]: {"source": 1000 * int((label_msg == i).sum()) / n,
                             "pred": 1000 * int((pred == i).sum()) / n}
              for i in range(len(MSG_NAMES))}

    bars = {}
    for kind, row in use.items():
        u = row["reply"]["use"]
        bars[f"reply-{kind}"] = (u is not None and u >= USE_BAR)
    bars["msg@1|here"] = here_top1 >= HERE_TOP1_BAR
    for k, w in want.items():
        if w["judged"]:
            bars[f"want-{k}"] = abs(w["ratio"] - 1.0) <= WANT_TOL
    return {"rows": n, "here_rows": int(here_rows.sum()),
            "opportunity_use": use, "msg_top1_here": here_top1,
            "want_emission": want, "per_1000_rows": per_1k, "bars": bars,
            "pass": all(bars.values())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clone", type=Path, required=True)
    ap.add_argument("--data-root", type=Path, required=True)
    ap.add_argument("--rollouts", nargs="*", default=None,
                    help="dir names to read; default = the held-out split")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    dirs = sorted(p for p in args.data_root.iterdir() if (p / "meta.json").exists())
    if args.rollouts:
        dirs = [d for d in dirs if d.name in set(args.rollouts)]
    else:
        val = [d for d in dirs if _is_val(d.name)]
        dirs = val or dirs[-1:]
    assert dirs, "no rollouts selected"
    rollouts = [load_rollout(d) for d in dirs]
    for r, d in zip(rollouts, dirs):
        r.path = d
        r.kitty = np.load(d / "kitty.npy")   # decision-row speaker ids
        assert r.kitty.shape == r.tick.shape, d
    res = readout(rollouts, load_clone(args.clone))
    res["clone"] = str(args.clone)
    res["rollouts"] = [d.name for d in dirs]

    print(f"clone {args.clone.name} on {', '.join(d.name for d in dirs)}: "
          f"{res['rows']} rows, {res['here_rows']} here rows")
    print(f"{'here kind':<14}{'split':<9}{'n':>7}{'p-use':>7}{'argmax':>8}{'source':>8}")
    for kind, row in res["opportunity_use"].items():
        for split in ("reply", "ambient"):
            c = row[split]
            f = lambda v: "  n/a" if v is None else f"{v:.3f}"
            print(f"{kind:<14}{split:<9}{c['n']:>7}{f(c['use']):>7}"
                  f"{f(c['argmax_use']):>8}{f(c['source_use']):>8}"
                  + ("  (thin)" if c["n"] < WANT_MIN_ROWS else "")
                  + ("" if split == "reply" else "  (informational)"))
    print(f"msg@1 on here rows: {res['msg_top1_here']:.3f}")
    print(f"{'want kind':<14}{'source':>7}{'pred':>7}{'ratio':>7}")
    for k, w in res["want_emission"].items():
        ratio = "  n/a" if w["ratio"] is None else f"{w['ratio']:.3f}"
        print(f"{k:<14}{w['source']:>7}{w['pred']:>7}{ratio:>7}"
              + ("" if w["judged"] else "  (unjudged, < 100 source rows)"))
    misses = [k for k, ok in res["bars"].items() if not ok]
    print("bars: " + ("PASS" if res["pass"] else "MISS " + ", ".join(misses)))

    out = args.out or (args.clone.parent / f"{args.clone.stem}-readout.json")
    out.write_text(json.dumps(res, indent=2) + "\n")
    print(f"-> {out}")


if __name__ == "__main__":
    main()
