"""Owner 2026-11-09 ("I'd like to dig into that and see if we can figure out why that's happening"): why does the act arm
diverge from its trunk MORE where the head is LEAST confident (R-5, P44 reversed)? Dump-only over recorded legs (one
replay per world, the row fence and read_r5's act fence both armed); zero collection, no world served.
Two reads:
  (A) SHADOW — the no-head arm's leg with a B15 OnlineHeads stepped as a shadow over the SAME observations: its
      policy never saw the head, so if its divergence from the trunk still rises with the shadow head's entropy, the
      pattern is about situations (what the head is unsure about is also where retraining moved the policy), not
      about how the act arm uses its head.
  (B) UNCERTAINTY — the act15 arm's leg: divergence binned by the TRUNK's own action entropy (policy uncertainty),
      and the 3x3 table head-entropy tercile x trunk-entropy tercile, to see whether head entropy is a proxy for
      policy uncertainty.
  (C) MENU — divergence by the size of the legal menu, and the head-entropy terciles on FREE-CHOICE ticks only: a tick
      with one legal action cannot diverge, and if those ticks fall unevenly across head-entropy terciles the R-5
      ordering is a composition effect. Fence: forced-choice rows carry zero divergence (replay / mask alignment).
    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B diag_r5_counterfactual.py <seating> <size> <A|B> [--seeds ...] --out reads/r5cf/<name>.json [--md]
"""
import argparse, json, sys
from pathlib import Path
import numpy as np, torch
A = Path(__file__).resolve().parent
sys.path.insert(0, str(A))
import p2_common as C, replay as RP, heads_online as HO, graft as G, read_r5 as R5

N_ACT = R5.N_ACT


def ent(logits, mask):
    """Action entropy in nats over the legal menu (0 when one action is legal)."""
    if mask.sum() <= 1:
        return 0.0
    z = np.where(mask, logits, -np.inf); z = z - z.max()
    p = np.exp(z); p /= p.sum()
    p = p[p > 0]
    return float(-(p * np.log(p)).sum())


def run(seating, size, mode, seeds=None):
    rows, header = RP.leg_rows(seating, size, None)
    actors, trunks, shadows = {}, {}, {}
    for i, spec in enumerate(header["seats"]):
        if spec.startswith("p2:"):
            actor, ck = HO.actor_from_artifact(C.ARTS / spec.split(":", 1)[1] / "policy-final.pt", n_obs=1)
            actors[i] = actor
            trunks[i], _ = G.load_trunk(ck["trunk_seed"])
            shadows[i] = HO.OnlineHeads("act15", 1)
    out = {"regime": [], "ent_head": [], "ent_trunk": [], "ent_arm": [], "differ": [], "live": [], "n_legal": []}
    ties = 0
    for seed in (sorted(rows) if seeds is None else seeds):
        for a in actors.values(): a.reset()
        for s in shadows.values(): s.reset()
        for rec in RP.replay(RP.acts_path(seating, size, seed, None), C.LEG_TOML[size], want_obs=True, check_row=rows[seed]):
            obs, mask = rec["obs"], rec["mask"]
            for i, actor in actors.items():
                o = obs[i:i + 1]
                x, cells = actor.widen(o)
                sh = shadows[i].step(o) if mode == "A" else cells
                with torch.no_grad():
                    la = actor.policy(torch.from_numpy(x))[0, :N_ACT].numpy()
                    lt = trunks[i](torch.from_numpy(o))[0, :N_ACT].numpy()
                m = mask[i, :N_ACT]
                a_rec, tied = R5.fence_act(np.where(m, la, -np.inf), int(rec["acts"][i, 0]), rec["tick"], i)
                ties += int(tied)
                a_tr = int(np.where(m, lt, -np.inf).argmax())
                differ = a_rec != a_tr
                blk = o[0, C.SELF_BLOCK:C.SELF_BLOCK + C.N_ROWS * C.KITTY_W].reshape(C.N_ROWS, C.KITTY_W)
                st = HO.row_states(blk)
                et, ea = ent(lt, m), ent(la, m)
                for r in range(C.N_ROWS):
                    out["regime"].append(int(st[r])); out["ent_head"].append(float(sh[0, r, R5.ENT_COL]))
                    out["ent_trunk"].append(et); out["ent_arm"].append(ea); out["differ"].append(bool(differ)); out["live"].append(int(st[r]) != 2); out["n_legal"].append(int(m.sum()))
        print("world", seed, "done", flush=True)
    d = {k: np.asarray(v) for k, v in out.items()}
    res = {"seating": seating, "size": size, "mode": mode, "worlds": len(rows) if seeds is None else len(seeds), "ties": ties,
           "tick_divergence_live_rows": float(d["differ"][d["live"]].mean())}
    # within-regime terciles of the (shadow) head entropy — read_r5's own binning
    res["by_head_entropy"] = R5.bin_divergence(d["regime"], d["ent_head"], d["differ"], has_head=True)
    res["within_regime_low_gt_high_head"] = R5.within_regime_ordering(res["by_head_entropy"])
    # terciles of the trunk's own action entropy, live rows, per regime
    res["by_trunk_entropy"] = R5.bin_divergence(d["regime"], d["ent_trunk"], d["differ"], has_head=True)
    res["within_regime_low_gt_high_trunk"] = R5.within_regime_ordering(res["by_trunk_entropy"])
    # divergence by the size of the legal menu (live rows), and the head-entropy terciles restricted to free-choice ticks
    live = d["live"]
    nl = d["n_legal"]
    bands = [(1, 1), (2, 3), (4, 6), (7, 12), (13, 99)]
    res["by_n_legal"] = {f"{lo}-{hi}": {"n": int(((nl >= lo) & (nl <= hi) & live).sum()),
                                        "divergence": (float(d["differ"][(nl >= lo) & (nl <= hi) & live].mean()) if ((nl >= lo) & (nl <= hi) & live).any() else None),
                                        "mean_head_entropy": (float(d["ent_head"][(nl >= lo) & (nl <= hi) & live].mean()) if ((nl >= lo) & (nl <= hi) & live).any() else None)} for lo, hi in bands}
    free = live & (nl >= 2)
    res["by_head_entropy_free_choice"] = R5.bin_divergence(d["regime"][free], d["ent_head"][free], d["differ"][free], has_head=True)
    res["within_regime_low_gt_high_head_free_choice"] = R5.within_regime_ordering(res["by_head_entropy_free_choice"])
    res["share_forced_choice_live_rows"] = float((nl[live] <= 1).mean())
    forced = live & (nl <= 1)
    assert forced.any() and not d["differ"][forced].any(), "forced-choice rows must not diverge (one legal action for arm and trunk alike)"
    # 3x3: head tercile x trunk tercile, live rows pooled over regimes
    eh, etr, df = d["ent_head"][live], d["ent_trunk"][live], d["differ"][live]
    qh, qt = np.quantile(eh, [1 / 3, 2 / 3]), np.quantile(etr, [1 / 3, 2 / 3])
    th, tt = np.digitize(eh, qh), np.digitize(etr, qt)
    grid = [[{"n": int(((th == a) & (tt == b)).sum()), "divergence": (float(df[(th == a) & (tt == b)].mean()) if ((th == a) & (tt == b)).any() else None)} for b in range(3)] for a in range(3)]
    res["grid_head_x_trunk"] = {"rows": "head entropy tercile low/mid/high", "cols": "trunk entropy tercile low/mid/high", "cells": grid}
    rk = lambda v: np.argsort(np.argsort(v))
    res["spearman_head_vs_trunk_entropy"] = float(np.corrcoef(rk(eh), rk(etr))[0, 1])
    res["spearman_head_vs_arm_entropy"] = float(np.corrcoef(rk(eh), rk(d["ent_arm"][live]))[0, 1])
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("seating"); ap.add_argument("size", type=int); ap.add_argument("mode", choices=["A", "B"])
    ap.add_argument("--seeds", default=None); ap.add_argument("--out", type=Path, required=True); ap.add_argument("--md", action="store_true")
    a = ap.parse_args()
    seeds = [int(s) for s in a.seeds.split(",")] if a.seeds else None
    res = run(a.seating, a.size, a.mode, seeds)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps({k: v for k, v in res.items() if k not in ("by_head_entropy", "by_trunk_entropy")}, indent=1))
    for k in ("by_head_entropy", "by_head_entropy_free_choice", "by_trunk_entropy"):
        print(k, json.dumps({r: {t: ((round(c["divergence"], 3) if c["divergence"] is not None else None), c["n"]) for t, c in b.items() if isinstance(c, dict) and "divergence" in c} for r, b in res[k].items()}))
    if a.md:
        L = [f"# R-5 counterfactual — {res['seating']} {res['size']}×{res['size']}, mode {res['mode']} ({res['worlds']} worlds; ties {res['ties']})", "",
             f"tick divergence on live rows {res['tick_divergence_live_rows']:.3f}; forced-choice share of live rows {res['share_forced_choice_live_rows']:.3f}; "
             f"Spearman head entropy ~ trunk action entropy {res['spearman_head_vs_trunk_entropy']:.3f}, ~ arm action entropy {res['spearman_head_vs_arm_entropy']:.3f}", ""]
        for k, title in (("by_head_entropy", "divergence by head-entropy tercile, all live rows (read_r5's binning)"), ("by_head_entropy_free_choice", "the same on FREE-CHOICE ticks only"), ("by_trunk_entropy", "divergence by the TRUNK's action-entropy tercile")):
            L += [f"## {title}", "", "| regime | low | mid | high |", "|---|---|---|---|"]
            for r, b in res[k].items():
                cells = [f"{b[t]['divergence']:.3f} ({b[t]['n']})" if b[t]['divergence'] is not None else f"— ({b[t]['n']})" for t in ("low", "mid", "high")]
                L.append(f"| {r} | " + " | ".join(cells) + " |")
            L.append("")
        L += ["## divergence by legal-menu size (live rows)", "", "| legal actions | n | divergence | mean head entropy |", "|---|---|---|---|"]
        for k, v in res["by_n_legal"].items():
            L.append(f"| {k} | {v['n']} | {('%.3f' % v['divergence']) if v['divergence'] is not None else '—'} | {('%.3f' % v['mean_head_entropy']) if v['mean_head_entropy'] is not None else '—'} |")
        L += ["", "## head-entropy tercile (rows) × trunk-entropy tercile (cols), live rows", "", "| head \\ trunk | low | mid | high |", "|---|---|---|---|"]
        for i, row in enumerate(res["grid_head_x_trunk"]["cells"]):
            L.append(f"| {('low', 'mid', 'high')[i]} | " + " | ".join(f"{c['divergence']:.3f} ({c['n']})" if c['divergence'] is not None else f"— ({c['n']})" for c in row) + " |")
        a.out.with_suffix(".md").write_text("\n".join(L) + "\n")
